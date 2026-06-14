"""
Value cleaning and unit separation.

Separates numeric values from units while preserving original values.
"""

import re
from typing import Dict, List, Any
from loguru import logger


class ValueCleaner:
    """
    Cleans metric values by separating numeric values from units.
    
    Features:
    - Preserves original values
    - Extracts numeric values (including ranges)
    - Separates units properly
    - No unit conversion (preserves integrity)
    """
    
    # Pattern for numeric values (including ranges, commas, decimals)
    NUMERIC_PATTERN = r'(\d+(?:,\d+)*(?:\.\d+)?(?:-\d+(?:,\d+)*(?:\.\d+)?)?)'
    
    def clean_metrics(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean all metrics by separating values and units.
        
        Args:
            metrics: List of metric dictionaries
            
        Returns:
            List of cleaned metric dictionaries
        """
        cleaned = []
        total = len(metrics)
        
        logger.info(f"Cleaning {total} metrics - separating values and units...")
        
        for i, metric in enumerate(metrics):
            if i % 50 == 0 and i > 0:
                logger.debug(f"Progress: {i}/{total} metrics cleaned")
            
            cleaned_metric = self.clean_metric(metric)
            cleaned.append(cleaned_metric)
        
        logger.info(f"Cleaned {total} metrics - values and units separated")
        return cleaned
    
    def clean_metric(self, metric: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single metric.
        
        Args:
            metric: Metric dictionary
            
        Returns:
            Cleaned metric dictionary
        """
        cleaned = metric.copy()
        value = metric.get('value', '')
        
        if not isinstance(value, str):
            value = str(value) if value is not None else ''
        
        if not value:
            return cleaned
        
        # Store original value with unit
        cleaned['original_value_with_unit'] = value
        
        # Extract numeric value and unit
        numeric_match = re.search(self.NUMERIC_PATTERN, value)
        
        if numeric_match:
            numeric_value = numeric_match.group(1)
            # Remove commas for consistency
            numeric_value = numeric_value.replace(',', '')
            cleaned['value'] = numeric_value
            
            # Extract unit from remaining part
            unit_part = value.replace(numeric_match.group(0), '').strip()
            unit_part = self._clean_unit(unit_part)
            
            cleaned['unit'] = unit_part if unit_part else None
        else:
            # No numeric value found, keep original
            cleaned['unit'] = None
        
        cleaned['unit_conversion_applied'] = False
        
        return cleaned
    
    def _clean_unit(self, unit_part: str) -> str:
        """
        Clean the unit string.
        
        Args:
            unit_part: Raw unit string
            
        Returns:
            Cleaned unit string
        """
        if not unit_part:
            return ""
        
        # Remove leading/trailing separators
        unit_part = re.sub(r'^[\s,.-]+', '', unit_part)
        unit_part = re.sub(r'[\s,.-]+$', '', unit_part)
        
        return unit_part.strip()


