"""
Parallel LLM processor for ESG analysis.

Matches the reference implementation's process_chunks_with_llm() with
ThreadPoolExecutor for parallel processing.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from loguru import logger

from .base_processor import ProcessorConfig


@dataclass
class ParallelConfig:
    """Configuration for parallel processing."""
    max_workers: int = 4  # Match reference implementation
    show_progress: bool = True
    show_eta: bool = True
    
    # Inherited from ProcessorConfig
    max_retries: int = 3
    retry_delay: float = 2.0
    timeout: int = 120


class ParallelProcessor:
    """
    Parallel processor for LLM analysis.
    
    Matches the reference implementation's process_chunks_with_llm() method
    using ThreadPoolExecutor for parallel processing.
    
    Features:
    - Configurable worker count (default 4)
    - Progress tracking with ETA
    - Automatic result merging
    - Comprehensive error handling
    - Timing statistics
    """
    
    def __init__(self, 
                 process_func: Callable[[str, str], Optional[Dict[str, Any]]],
                 config: ParallelConfig = None):
        """
        Initialize parallel processor.
        
        Args:
            process_func: Function to process a single prompt (prompt, analysis_type) -> result
            config: Parallel processing configuration
        """
        self.process_func = process_func
        self.config = config or ParallelConfig()
        
        logger.info(f"Parallel processor initialized with {self.config.max_workers} workers")
    
    def process_chunks(self,
                       prompts: List[str],
                       analysis_type: str,
                       merge_func: Callable[[Dict, Dict, str], Dict] = None) -> Dict[str, Any]:
        """
        Process multiple prompts in parallel.
        
        Matches the reference implementation's process_chunks_with_llm().
        
        Args:
            prompts: List of prompts to process
            analysis_type: Type of analysis (Environmental, Social, Governance)
            merge_func: Function to merge results (existing, new, analysis_type) -> merged
            
        Returns:
            Combined results from all chunks
        """
        total_chunks = len(prompts)
        
        if total_chunks == 0:
            logger.warning("No prompts to process")
            return {}
        
        # Adjust workers based on chunk count
        max_workers = min(self.config.max_workers, total_chunks)
        
        logger.info(f"[PARALLEL] Processing {analysis_type} with {total_chunks} chunks using {max_workers} workers")
        
        # Track progress
        start_time = time.time()
        completed_chunks = 0
        successful_chunks = 0
        combined_results = {}
        
        def process_single_chunk(chunk_index: int, prompt: str):
            """Process a single chunk - designed for parallel execution."""
            chunk_num = chunk_index + 1
            
            try:
                result = self.process_func(prompt, analysis_type)
                
                if result is not None:
                    return chunk_index, result, None
                else:
                    return chunk_index, None, f"Processing returned None for chunk {chunk_num}"
                    
            except Exception as e:
                return chunk_index, None, f"Exception in chunk {chunk_num}: {e}"
        
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_chunk = {
                executor.submit(process_single_chunk, i, prompt): i 
                for i, prompt in enumerate(prompts)
            }
            
            # Process completed tasks as they finish
            for future in as_completed(future_to_chunk):
                chunk_index = future_to_chunk[future]
                chunk_num = chunk_index + 1
                completed_chunks += 1
                
                # Calculate progress
                elapsed = time.time() - start_time
                progress_pct = (completed_chunks / total_chunks) * 100
                
                # Estimate remaining time
                if completed_chunks > 0:
                    remaining = (elapsed / completed_chunks) * (total_chunks - completed_chunks)
                else:
                    remaining = 0
                
                try:
                    chunk_index, chunk_result, error = future.result()
                    
                    if error:
                        if self.config.show_progress:
                            logger.warning(
                                f"[{completed_chunks}/{total_chunks}] ({progress_pct:.1f}%) "
                                f"FAILED: {error}"
                            )
                    else:
                        # Merge results if merge function provided
                        if merge_func and chunk_result:
                            combined_results = merge_func(combined_results, chunk_result, analysis_type)
                        elif chunk_result:
                            # Simple dict update if no merge function
                            if not combined_results:
                                combined_results = chunk_result
                            else:
                                combined_results.update(chunk_result)
                        
                        successful_chunks += 1
                        
                        if self.config.show_progress:
                            eta_str = f"ETA: {remaining/60:.1f}min" if self.config.show_eta else ""
                            logger.info(
                                f"[{completed_chunks}/{total_chunks}] ({progress_pct:.1f}%) "
                                f"SUCCESS: Chunk {chunk_num} | {eta_str}"
                            )
                
                except Exception as e:
                    logger.error(
                        f"[{completed_chunks}/{total_chunks}] EXCEPTION: Chunk {chunk_num} - {e}"
                    )
        
        # Final statistics
        elapsed_total = time.time() - start_time
        
        logger.info(
            f"\n[COMPLETE] {analysis_type}: {successful_chunks}/{total_chunks} chunks "
            f"successful in {elapsed_total/60:.1f} minutes ({elapsed_total:.1f}s)"
        )
        
        if elapsed_total > 0:
            logger.info(
                f"   Speed: {successful_chunks/(elapsed_total/60):.1f} chunks/min | "
                f"Efficiency: {successful_chunks/total_chunks*100:.1f}%"
            )
        
        return combined_results
    
    def process_all_categories(self,
                                prompt_builder_func: Callable[[List[str], int, int, str, str], str],
                                chunks: List[List[str]],
                                year: str,
                                merge_func: Callable[[Dict, Dict, str], Dict] = None) -> Dict[str, Any]:
        """
        Process all ESG categories (Environmental, Social, Governance).
        
        Args:
            prompt_builder_func: Function to build prompts (chunk, chunk_num, total, year, category) -> prompt
            chunks: List of text chunks
            year: Report year
            merge_func: Function to merge results
            
        Returns:
            Combined results for all categories
        """
        all_results = {}
        categories = ["Environmental", "Social", "Governance"]
        
        for category in categories:
            logger.info(f"\n{'='*60}")
            logger.info(f"PROCESSING: {category} data...")
            logger.info(f"{'='*60}")
            
            # Build prompts for this category
            prompts = [
                prompt_builder_func(chunk, i+1, len(chunks), year, category)
                for i, chunk in enumerate(chunks)
            ]
            
            # Process in parallel
            category_results = self.process_chunks(prompts, category, merge_func)
            
            # Add to all results
            category_key = f"{category.lower()}_comprehensive_analysis"
            all_results[category_key] = category_results
        
        return all_results


class ProgressTracker:
    """
    Progress tracker for long-running operations.
    
    Provides:
    - Real-time progress updates
    - ETA calculations
    - Timing statistics
    """
    
    def __init__(self, total: int, description: str = "Processing"):
        """
        Initialize progress tracker.
        
        Args:
            total: Total items to process
            description: Description for logging
        """
        self.total = total
        self.description = description
        self.completed = 0
        self.successful = 0
        self.start_time = None
    
    def start(self):
        """Start tracking."""
        self.start_time = time.time()
        logger.info(f"{self.description}: Starting {self.total} items...")
    
    def update(self, success: bool = True, message: str = ""):
        """
        Update progress.
        
        Args:
            success: Whether the item was successful
            message: Optional message to log
        """
        self.completed += 1
        if success:
            self.successful += 1
        
        elapsed = time.time() - self.start_time
        progress_pct = (self.completed / self.total) * 100
        remaining = (elapsed / self.completed) * (self.total - self.completed) if self.completed > 0 else 0
        
        status = "SUCCESS" if success else "FAILED"
        logger.info(
            f"[{self.completed}/{self.total}] ({progress_pct:.1f}%) {status}"
            f"{': ' + message if message else ''} | ETA: {remaining/60:.1f}min"
        )
    
    def finish(self) -> Dict[str, Any]:
        """
        Finish tracking and return statistics.
        
        Returns:
            Statistics dictionary
        """
        elapsed = time.time() - self.start_time
        
        stats = {
            "total": self.total,
            "completed": self.completed,
            "successful": self.successful,
            "failed": self.completed - self.successful,
            "elapsed_seconds": elapsed,
            "elapsed_minutes": elapsed / 60,
            "success_rate": self.successful / self.total if self.total > 0 else 0,
            "items_per_minute": self.completed / (elapsed / 60) if elapsed > 0 else 0
        }
        
        logger.info(
            f"\n{self.description} COMPLETE: {self.successful}/{self.total} successful "
            f"in {elapsed/60:.1f} minutes"
        )
        logger.info(
            f"   Speed: {stats['items_per_minute']:.1f} items/min | "
            f"Efficiency: {stats['success_rate']*100:.1f}%"
        )
        
        return stats
