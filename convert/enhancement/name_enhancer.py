"""LLM-based metric name enhancement."""

import re
import json
from typing import Dict, List, Any, Optional
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import DirectAPIClient, APIConfig
from .prompts import get_name_enhancement_prompt


class NameEnhancer:
    """
    Enhances metric names using LLM.
    
    Converts raw metric names to clear, professional descriptions
    suitable for dashboard display.
    """
    
    def __init__(self, api_client: Optional[DirectAPIClient] = None, config: Optional[APIConfig] = None):
        """
        Initialize the enhancer.
        
        Args:
            api_client: Optional pre-configured API client
            config: Optional API configuration
        """
        if api_client:
            self.client = api_client
        else:
            config = config or APIConfig.from_env()
            self.client = DirectAPIClient(config)
    
    def enhance_batch(self, metrics: List[Dict[str, Any]], company: str, year: str) -> List[Dict[str, Any]]:
        """
        Enhance a batch of metric names.
        
        Args:
            metrics: List of metric dictionaries
            company: Company name
            year: Report year
            
        Returns:
            List of metrics with enhanced names
        """
        # Prepare metrics text for prompt
        metrics_text = "\n".join([
            f"- {metric.get('metric_name', 'Unknown')}"
            for metric in metrics
        ])
        
        prompt = get_name_enhancement_prompt(metrics_text, company, year)
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert ESG analyst."},
                {"role": "user", "content": prompt}
            ]
            
            result = self.client.chat_json(messages, max_tokens=2000)
            
            if result and 'enhanced_metrics' in result:
                return self._apply_enhancements(metrics, result['enhanced_metrics'])
            
        except Exception as e:
            logger.warning(f"Name enhancement failed: {e}")
        
        return metrics
    
    def _apply_enhancements(self, 
                            metrics: List[Dict[str, Any]], 
                            enhancements: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Apply enhancements to metrics.
        
        Args:
            metrics: Original metrics
            enhancements: List of {original_name, enhanced_name}
            
        Returns:
            Metrics with enhanced names
        """
        enhanced = []
        enhancement_map = {
            e.get('original_name'): e.get('enhanced_name')
            for e in enhancements
        }
        
        for metric in metrics:
            enhanced_metric = metric.copy()
            original_name = metric.get('metric_name')
            
            if original_name in enhancement_map:
                enhanced_metric['metric_name'] = enhancement_map[original_name]
            
            enhanced.append(enhanced_metric)
        
        return enhanced
