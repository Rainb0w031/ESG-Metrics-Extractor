"""
Combined LLM processing for efficiency.

Performs name enhancement, category generation, and importance analysis
in a single API call per batch, with parallel processing support.
"""

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import DirectAPIClient, APIConfig
from .prompts import get_combined_processing_prompt


@dataclass
class ProcessingConfig:
    """Configuration for combined processing."""
    batch_size: int = 15
    max_workers: int = 3


class ProgressTracker:
    """Tracks processing progress with ETA."""
    
    def __init__(self, total_batches: int, total_items: int):
        self.total_batches = total_batches
        self.total_items = total_items
        self.completed = 0
        self.successful = 0
        self.start_time = None
    
    def start(self):
        """Start tracking."""
        self.start_time = time.time()
    
    def update(self, success: bool = True):
        """Update progress."""
        self.completed += 1
        if success:
            self.successful += 1
    
    def get_progress(self, batch_size: int) -> Dict[str, Any]:
        """Get current progress info."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        progress_pct = (self.completed / self.total_batches) * 100 if self.total_batches > 0 else 0
        
        remaining = 0
        if self.completed > 0:
            remaining = (elapsed / self.completed) * (self.total_batches - self.completed)
        
        items_processed = min(self.completed * batch_size, self.total_items)
        
        return {
            'completed': self.completed,
            'total': self.total_batches,
            'percentage': progress_pct,
            'items_processed': items_processed,
            'total_items': self.total_items,
            'elapsed_seconds': elapsed,
            'remaining_seconds': remaining,
            'success_rate': (self.successful / self.completed * 100) if self.completed > 0 else 0
        }


class CombinedProcessor:
    """
    Processes metrics using combined LLM calls with parallel execution.
    
    Features:
    - Single API call for name + category + importance
    - Parallel batch processing
    - Progress tracking with ETA
    - Fallback handling
    """
    
    def __init__(self, 
                 api_client: Optional[DirectAPIClient] = None, 
                 config: Optional[ProcessingConfig] = None,
                 api_config: Optional[APIConfig] = None):
        """
        Initialize the processor.
        
        Args:
            api_client: Optional pre-configured API client
            config: Processing configuration
            api_config: Optional API configuration
        """
        self.config = config or ProcessingConfig()
        
        if api_client:
            self.client = api_client
        else:
            api_config = api_config or APIConfig.from_env()
            self.client = DirectAPIClient(api_config)
    
    def process_all(self, 
                    metrics: List[Dict[str, Any]], 
                    company: str, 
                    year: str,
                    progress_callback: Optional[Callable] = None) -> List[Dict[str, Any]]:
        """
        Process all metrics with parallel batch processing.
        
        Args:
            metrics: List of metric dictionaries
            company: Company name
            year: Report year
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of processed metrics
        """
        total = len(metrics)
        batch_size = self.config.batch_size
        total_batches = (total + batch_size - 1) // batch_size
        
        logger.info(f"Processing {total} metrics with parallel batch processing...")
        logger.info(f"Using {self.config.max_workers} workers for {total_batches} batches (batch size: {batch_size})")
        
        # Create batches
        batches = []
        for i in range(0, total, batch_size):
            batch_idx = i // batch_size
            batch = metrics[i:i + batch_size]
            batches.append((batch_idx, batch))
        
        # Initialize progress tracker
        tracker = ProgressTracker(total_batches, total)
        tracker.start()
        
        # Process in parallel
        results = [None] * total_batches  # Preserve order
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_batch = {
                executor.submit(self._process_batch_wrapper, batch_idx, batch, company, year): batch_idx
                for batch_idx, batch in batches
            }
            
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                batch_num = batch_idx + 1
                
                try:
                    idx, processed, error = future.result()
                    
                    if error:
                        tracker.update(success=False)
                        logger.warning(f"Batch {batch_num} failed: {error}")
                    else:
                        tracker.update(success=True)
                    
                    results[idx] = processed
                    
                    # Log progress
                    progress = tracker.get_progress(batch_size)
                    logger.info(
                        f"[{progress['completed']}/{progress['total']}] "
                        f"({progress['percentage']:.1f}%) "
                        f"~{progress['items_processed']}/{progress['total_items']} metrics | "
                        f"ETA: {progress['remaining_seconds']/60:.1f}min"
                    )
                    
                    if progress_callback:
                        progress_callback(progress)
                    
                except Exception as e:
                    logger.error(f"Batch {batch_num} exception: {e}")
                    results[batch_idx] = batches[batch_idx][1]  # Use original batch
                    tracker.update(success=False)
        
        # Flatten results
        processed_metrics = []
        for batch_result in results:
            if batch_result:
                processed_metrics.extend(batch_result)
        
        elapsed = tracker.get_progress(batch_size)['elapsed_seconds']
        logger.info(
            f"Processing complete: {tracker.successful}/{tracker.total_batches} batches successful "
            f"in {elapsed/60:.1f} minutes"
        )
        logger.info(f"Speed: {total/(elapsed/60):.1f} metrics/min | Efficiency: {tracker.get_progress(batch_size)['success_rate']:.1f}%")
        
        return processed_metrics
    
    def _process_batch_wrapper(self, 
                               batch_idx: int, 
                               batch: List[Dict[str, Any]], 
                               company: str, 
                               year: str) -> tuple:
        """
        Wrapper for batch processing.
        
        Returns:
            Tuple of (batch_idx, processed_batch, error_message)
        """
        try:
            processed = self.process_batch(batch, company, year)
            return batch_idx, processed, None
        except Exception as e:
            return batch_idx, batch, str(e)
    
    def process_batch(self, 
                      metrics: List[Dict[str, Any]], 
                      company: str, 
                      year: str) -> List[Dict[str, Any]]:
        """
        Process a single batch of metrics.
        
        Args:
            metrics: Batch of metric dictionaries
            company: Company name
            year: Report year
            
        Returns:
            Processed metrics
        """
        # Prepare metrics text
        metrics_text = []
        for i, metric in enumerate(metrics):
            info = f"Metric {i+1}:\n"
            info += f"Original Name: {metric['metric_name']}\n"
            info += f"Value: {metric['value']} {metric.get('unit', '')}\n"
            info += f"Category: {metric['category']}\n"
            info += f"Subcategory: {metric.get('subcategory', '')}\n"
            
            if metric.get('details') and len(metric['details']) > 0:
                info += "Context Details:\n"
                for detail in metric['details'][:3]:
                    info += f"  - {detail}\n"
            
            info += "---\n"
            metrics_text.append(info)
        
        combined_text = "\n".join(metrics_text)
        prompt = get_combined_processing_prompt(combined_text, company, year, len(metrics))
        
        # Initialize with original values
        enhanced = []
        for metric in metrics:
            enhanced_metric = metric.copy()
            if 'details' not in enhanced_metric:
                enhanced_metric['details'] = []
            enhanced.append(enhanced_metric)
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert ESG analyst with deep knowledge of sustainability metrics, corporate reporting, ESG frameworks, and double materiality assessment methodologies."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat(messages, max_tokens=4000)
            
            if response:
                self._parse_combined_response(enhanced, response)
            
        except Exception as e:
            logger.warning(f"Combined processing failed: {e}")
        
        return enhanced
    
    def _parse_combined_response(self, metrics: List[Dict[str, Any]], response: str):
        """
        Parse combined LLM response and update metrics.
        
        Args:
            metrics: Metrics to update (modified in place)
            response: LLM response text
        """
        for idx, metric in enumerate(metrics):
            metric_pattern = f"Metric {idx + 1}:"
            
            if metric_pattern not in response:
                continue
            
            # Extract metric section
            lines = response.split('\n')
            section_lines = []
            in_section = False
            
            for line in lines:
                line = line.strip()
                if line.startswith(metric_pattern):
                    in_section = True
                    continue
                elif line.startswith(f"Metric {idx + 2}:"):
                    break
                elif in_section and line:
                    section_lines.append(line)
            
            # Parse section
            for line in section_lines:
                line_lower = line.lower()
                
                # Enhanced Name
                if "enhanced name:" in line_lower:
                    try:
                        name = line.split(":", 1)[1].strip()
                        if name:
                            metric['metric_name'] = name
                    except:
                        pass
                
                # ESG Category
                elif "esg category:" in line_lower:
                    try:
                        category = line.split(":", 1)[1].strip()
                        if category:
                            metric['category'] = category
                            metric['type'] = self._determine_type(category)
                            metric['area'] = self._determine_area(category)
                    except:
                        pass
                
                # Importance
                elif "importance:" in line_lower:
                    try:
                        importance_part = line.split(":", 1)[1].strip()
                        
                        if " - " in importance_part:
                            level, reasoning = importance_part.split(" - ", 1)
                        else:
                            level = importance_part
                            reasoning = "Based on analysis"
                        
                        level = level.strip()
                        if level.lower() in ['high', 'medium', 'low']:
                            metric['importance'] = level.capitalize()
                            metric['importance_reasoning'] = reasoning.strip()
                    except:
                        pass
    
    def _determine_type(self, category: str) -> str:
        """Determine type from category."""
        if category.startswith('E'):
            return 'environmental'
        elif category.startswith('S'):
            return 'social'
        elif category.startswith('G'):
            return 'governance'
        return 'environmental'
    
    def _determine_area(self, category: str) -> str:
        """Determine area from category."""
        if category.startswith('E'):
            return 'E'
        elif category.startswith('S'):
            return 'S'
        elif category.startswith('G'):
            return 'G'
        return 'E'
