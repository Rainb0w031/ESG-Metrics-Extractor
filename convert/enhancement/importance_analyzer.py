"""LLM-based importance analysis using double materiality."""

import re
from typing import Dict, List, Any, Optional
from loguru import logger

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import DirectAPIClient, APIConfig
from .prompts import get_importance_analysis_prompt


class ImportanceAnalyzer:
    """
    Analyzes metric importance using LLM with double materiality assessment.
    
    Features:
    - Financial materiality (impact on company value)
    - Impact materiality (impact on society/environment)
    - Comprehensive reasoning
    """
    
    def __init__(self, api_client: Optional[DirectAPIClient] = None, config: Optional[APIConfig] = None):
        """
        Initialize the analyzer.
        
        Args:
            api_client: Optional pre-configured API client
            config: Optional API configuration
        """
        if api_client:
            self.client = api_client
        else:
            config = config or APIConfig.from_env()
            self.client = DirectAPIClient(config)
    
    def analyze_batch(self, metrics: List[Dict[str, Any]], company: str, year: str) -> List[Dict[str, Any]]:
        """
        Analyze importance for a batch of metrics.
        
        Args:
            metrics: List of metric dictionaries
            company: Company name
            year: Report year
            
        Returns:
            List of metrics with importance analysis
        """
        # Prepare metrics text
        metrics_text = []
        for i, metric in enumerate(metrics):
            info = f"Metric {i+1}: {metric['metric_name']}\n"
            info += f"Value: {metric['value']} {metric.get('unit', '')}\n"
            info += f"Category: {metric['category']}\n"
            info += f"Subcategory: {metric.get('subcategory', '')}\n"
            if metric.get('details'):
                info += f"Context: {' '.join(metric['details'][:2])}\n"
            info += "---\n"
            metrics_text.append(info)
        
        combined_text = "\n".join(metrics_text)
        prompt = get_importance_analysis_prompt(combined_text, company, year, len(metrics))
        
        # Initialize with defaults
        enhanced = []
        for metric in metrics:
            enhanced_metric = metric.copy()
            enhanced_metric['importance'] = 'Medium'
            enhanced_metric['importance_reasoning'] = 'Analysis unavailable'
            enhanced.append(enhanced_metric)
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert ESG analyst with deep knowledge of sustainability metrics and corporate reporting."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat(messages, max_tokens=3000)
            
            if response:
                self._parse_importance_response(enhanced, response)
            
        except Exception as e:
            logger.warning(f"Importance analysis failed: {e}")
        
        return enhanced
    
    def _parse_importance_response(self, metrics: List[Dict[str, Any]], response: str):
        """
        Parse LLM response and update metrics.
        
        Args:
            metrics: Metrics to update (modified in place)
            response: LLM response text
        """
        for i, metric in enumerate(metrics):
            patterns = [
                f"Metric {i+1}:",
                f"Metric {i+1} :",
                f"Metric {i+1}.",
            ]
            
            found = False
            for pattern in patterns:
                if pattern in response:
                    lines = response.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line.startswith(pattern):
                            remaining = line[len(pattern):].strip()
                            
                            if ' - ' in remaining:
                                importance_part, reasoning = remaining.split(' - ', 1)
                            else:
                                importance_part = remaining
                                reasoning = ""
                            
                            importance_part = importance_part.strip()
                            
                            if importance_part.lower() in ['high', 'medium', 'low']:
                                metric['importance'] = importance_part.capitalize()
                                metric['importance_reasoning'] = reasoning.strip()
                                found = True
                                break
                    
                    if found:
                        break
            
            if not found:
                # Try fallback detection
                if 'high' in response.lower():
                    metric['importance'] = 'High'
                elif 'low' in response.lower():
                    metric['importance'] = 'Low'
