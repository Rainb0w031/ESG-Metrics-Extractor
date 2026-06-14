"""
Direct API processor for ESG analysis.

Uses the modularized extract/api module for direct API calls,
providing an alternative to prompter-based processing.
"""

import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from loguru import logger

# Import from extract module
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import DirectAPIClient, APIConfig


@dataclass
class DirectProcessorConfig:
    """Configuration for direct API processor."""
    api_config: APIConfig = None
    max_retries: int = 3
    retry_delay: float = 2.0
    temperature: float = 0.2
    max_tokens: int = 4096
    timeout: int = 120
    
    def __post_init__(self):
        if self.api_config is None:
            self.api_config = APIConfig.from_env()


class DirectProcessor:
    """
    Direct API processor using extract/api module.
    
    Features:
    - Uses DirectAPIClient from extract/api (no prompter dependency)
    - Configurable retry logic
    - Multiple response format support
    - JSON extraction and parsing
    
    This provides an alternative to LLMProcessor for environments
    where prompter is not available or direct API calls are preferred.
    """
    
    def __init__(self, config: DirectProcessorConfig = None):
        """
        Initialize direct processor.
        
        Args:
            config: Processor configuration
        """
        self.config = config or DirectProcessorConfig()
        self.client = DirectAPIClient(self.config.api_config)
        
        logger.info(f"Direct processor initialized (model={self.config.api_config.model})")
    
    def process(self, prompt: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Process prompt with direct API call.
        
        Args:
            prompt: Prompt to process
            analysis_type: Type of analysis
            
        Returns:
            Dict containing analysis result, or None if failed
        """
        messages = [
            {
                "role": "system",
                "content": f"You are an expert ESG analyst that only responds with comprehensive, detailed JSON categorizations of {analysis_type.lower()} data. Your response must be valid JSON only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        for attempt in range(self.config.max_retries):
            try:
                # Make API call
                response = self.client.chat(
                    messages,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens
                )
                
                if response is None:
                    logger.warning(f"Attempt {attempt + 1}: API returned None")
                    continue
                
                # Extract and parse JSON
                result = self.client.extract_json(response)
                
                if result is not None:
                    logger.debug(f"Successfully parsed {analysis_type} JSON")
                    return result
                else:
                    logger.warning(f"Attempt {attempt + 1}: Failed to extract JSON")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}: Exception - {e}")
            
            # Retry delay
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (attempt + 1)
                logger.info(f"Retrying in {delay}s...")
                time.sleep(delay)
        
        logger.error(f"All {self.config.max_retries} attempts failed for {analysis_type}")
        return None
    
    def process_batch(self, prompts: List[str], analysis_type: str) -> List[Optional[Dict[str, Any]]]:
        """
        Process multiple prompts sequentially.
        
        Args:
            prompts: List of prompts
            analysis_type: Type of analysis
            
        Returns:
            List of results (None for failed items)
        """
        results = []
        total = len(prompts)
        
        for i, prompt in enumerate(prompts, 1):
            logger.info(f"Processing batch item {i}/{total}")
            result = self.process(prompt, analysis_type)
            results.append(result)
            
            # Add delay between requests
            if i < total:
                time.sleep(self.config.retry_delay)
        
        success_count = sum(1 for r in results if r is not None)
        logger.info(f"Batch complete: {success_count}/{total} successful")
        
        return results


class DirectAnalyzer:
    """
    Complete ESG analyzer using direct API calls.
    
    Combines DirectProcessor with parallel processing support
    for a prompter-free analysis pipeline.
    """
    
    def __init__(self, config: DirectProcessorConfig = None):
        """
        Initialize analyzer.
        
        Args:
            config: Processor configuration
        """
        self.config = config or DirectProcessorConfig()
        self.processor = DirectProcessor(self.config)
        
        logger.info("Direct ESG analyzer initialized")
    
    def analyze_with_prompts(self,
                             prompts: List[str],
                             analysis_type: str,
                             merge_func=None,
                             parallel: bool = True,
                             max_workers: int = 4) -> Dict[str, Any]:
        """
        Analyze text using provided prompts.
        
        Args:
            prompts: List of prompts to process
            analysis_type: Type of analysis
            merge_func: Function to merge results
            parallel: Use parallel processing
            max_workers: Number of parallel workers
            
        Returns:
            Combined analysis results
        """
        if parallel and len(prompts) > 1:
            # Use parallel processor
            from .parallel_processor import ParallelProcessor, ParallelConfig
            
            parallel_config = ParallelConfig(
                max_workers=max_workers,
                max_retries=self.config.max_retries,
                retry_delay=self.config.retry_delay
            )
            
            parallel_proc = ParallelProcessor(
                process_func=self.processor.process,
                config=parallel_config
            )
            
            return parallel_proc.process_chunks(prompts, analysis_type, merge_func)
        else:
            # Sequential processing
            results = self.processor.process_batch(prompts, analysis_type)
            
            # Merge results
            if merge_func:
                combined = {}
                for result in results:
                    if result:
                        combined = merge_func(combined, result, analysis_type)
                return combined
            else:
                # Return last non-None result
                for result in reversed(results):
                    if result:
                        return result
                return {}
