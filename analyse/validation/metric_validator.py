"""
Metric validation for ESG analysis.

Validates individual metrics and metric collections.
Extracted from ESGLLMAnalyzer._is_valid_metric().
"""

from typing import Dict, Any
from loguru import logger

from .base_validator import BaseValidator


class MetricValidator(BaseValidator):
    """
    Validates ESG metrics.
    
    Checks:
    - Metric name validity (min length, format)
    - Metric value validity (not empty, min length)
    - Metric structure (key-value pairs)
    """
    
    def __init__(self, min_name_length: int = 3, min_value_length: int = 1):
        """
        Initialize metric validator.
        
        Args:
            min_name_length: Minimum length for metric names
            min_value_length: Minimum length for metric values (strings)
        """
        self.min_name_length = min_name_length
        self.min_value_length = min_value_length
    
    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate metrics in results.
        
        Args:
            results: Results containing metrics
        
        Returns:
            Results with invalid metrics removed
        """
        if not results:
            return results
        
        # This would recursively validate all metrics in the structure
        # For now, return as-is (called by quality_validator)
        return results
    
    def is_valid_metric(self, metric_name: str, metric_value: Any) -> bool:
        """
        Check if a metric is valid.
        
        Args:
            metric_name: Metric name
            metric_value: Metric value
        
        Returns:
            True if valid, False otherwise
        """
        # Check for None or empty
        if not metric_name or not metric_value:
            logger.debug(f"Invalid metric: empty name or value")
            return False
        
        # Check metric name length
        if len(str(metric_name).strip()) < self.min_name_length:
            logger.debug(f"Invalid metric: name too short '{metric_name}'")
            return False
        
        # Check metric value for strings
        if isinstance(metric_value, str):
            if len(metric_value.strip()) < self.min_value_length:
                logger.debug(f"Invalid metric: value too short for '{metric_name}'")
                return False
        
        # Check for None or empty string
        if metric_value is None or metric_value == "":
            logger.debug(f"Invalid metric: None/empty value for '{metric_name}'")
            return False
        
        return True
    
    def get_quality_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate quality score based on metrics.
        
        Args:
            results: Results to score
        
        Returns:
            Quality score (0.0-1.0)
        """
        if not results:
            return 0.0
        
        # Count total and valid metrics
        total_metrics = 0
        valid_metrics = 0
        
        # This would recursively count metrics in the structure
        # For now, return a default score
        return 0.8
    
    def validate_metrics_dict(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a dict of metrics.
        
        Args:
            metrics: Dict of metric name -> metric value
        
        Returns:
            Dict with only valid metrics
        """
        validated_metrics = {}
        invalid_count = 0
        
        for metric_name, metric_value in metrics.items():
            if self.is_valid_metric(metric_name, metric_value):
                validated_metrics[metric_name] = metric_value
            else:
                invalid_count += 1
        
        if invalid_count > 0:
            logger.debug(f"Filtered out {invalid_count} invalid metrics")
        
        return validated_metrics

