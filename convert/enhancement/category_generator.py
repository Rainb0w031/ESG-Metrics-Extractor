"""LLM-based category generation."""

import re
import json
from typing import Dict, List, Any, Optional
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import DirectAPIClient, APIConfig
from .prompts import get_category_generation_prompt


class CategoryGenerator:
    """
    Generates ESG categories using LLM.
    
    Assigns detailed categories with specific subcategories
    for dashboard filtering and analysis.
    """
    
    def __init__(self, api_client: Optional[DirectAPIClient] = None, config: Optional[APIConfig] = None):
        """
        Initialize the generator.
        
        Args:
            api_client: Optional pre-configured API client
            config: Optional API configuration
        """
        if api_client:
            self.client = api_client
        else:
            config = config or APIConfig.from_env()
            self.client = DirectAPIClient(config)
    
    def categorize_batch(self, metrics: List[Dict[str, Any]], company: str, year: str) -> List[Dict[str, Any]]:
        """
        Generate categories for a batch of metrics.
        
        Args:
            metrics: List of metric dictionaries
            company: Company name
            year: Report year
            
        Returns:
            List of metrics with categories
        """
        # Prepare metrics text for prompt
        metrics_text = "\n".join([
            f"- {metric.get('metric_name', 'Unknown')} (Current: {metric.get('category', 'None')})"
            for metric in metrics
        ])
        
        prompt = get_category_generation_prompt(metrics_text, company, year)
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert ESG analyst."},
                {"role": "user", "content": prompt}
            ]
            
            result = self.client.chat_json(messages, max_tokens=2000)
            
            if result and 'categorized_metrics' in result:
                return self._apply_categories(metrics, result['categorized_metrics'])
            
        except Exception as e:
            logger.warning(f"Category generation failed: {e}")
        
        return metrics
    
    def _apply_categories(self, 
                          metrics: List[Dict[str, Any]], 
                          categories: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Apply categories to metrics.
        
        Args:
            metrics: Original metrics
            categories: List of {metric_name, category}
            
        Returns:
            Metrics with categories applied
        """
        categorized = []
        category_map = {
            c.get('metric_name'): c.get('category')
            for c in categories
        }
        
        for metric in metrics:
            cat_metric = metric.copy()
            metric_name = metric.get('metric_name')
            
            if metric_name in category_map:
                new_category = category_map[metric_name]
                cat_metric['category'] = new_category
                cat_metric['type'] = self._determine_type(new_category)
                cat_metric['area'] = self._determine_area(new_category)
            
            categorized.append(cat_metric)
        
        return categorized
    
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
