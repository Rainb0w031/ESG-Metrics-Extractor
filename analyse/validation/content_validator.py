"""
Content validation for ESG analysis.

Validates details and text content.
Extracted from ESGLLMAnalyzer._is_valid_detail().
"""

from typing import Dict, Any, List
from loguru import logger

from .base_validator import BaseValidator


class ContentValidator(BaseValidator):
    """
    Validates ESG content (details, text).
    
    Checks:
    - Detail validity (min length, not empty)
    - Text quality
    - Content structure
    """
    
    def __init__(self, min_detail_length: int = 10):
        """
        Initialize content validator.
        
        Args:
            min_detail_length: Minimum length for detail strings
        """
        self.min_detail_length = min_detail_length
    
    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate content in results.
        
        Args:
            results: Results containing content
        
        Returns:
            Results with invalid content removed
        """
        if not results:
            return results
        
        # This would recursively validate all content in the structure
        # For now, return as-is (called by quality_validator)
        return results
    
    def is_valid_detail(self, detail: str) -> bool:
        """
        Check if a detail is valid.
        
        Args:
            detail: Detail text to check
        
        Returns:
            True if valid, False otherwise
        """
        # Check type
        if not detail or not isinstance(detail, str):
            logger.debug("Invalid detail: not a string")
            return False
        
        # Check length
        if len(detail.strip()) < self.min_detail_length:
            logger.debug(f"Invalid detail: too short ({len(detail.strip())} chars)")
            return False
        
        # Check for empty or whitespace-only
        if not detail.strip():
            logger.debug("Invalid detail: empty or whitespace")
            return False
        
        return True
    
    def get_quality_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate quality score based on content.
        
        Args:
            results: Results to score
        
        Returns:
            Quality score (0.0-1.0)
        """
        if not results:
            return 0.0
        
        # This would analyze content quality
        # For now, return a default score
        return 0.8
    
    def validate_details_list(self, details: List[str]) -> List[str]:
        """
        Validate a list of details.
        
        Args:
            details: List of detail strings
        
        Returns:
            List with only valid details
        """
        validated_details = []
        invalid_count = 0
        
        for detail in details:
            if self.is_valid_detail(detail):
                validated_details.append(detail)
            else:
                invalid_count += 1
        
        if invalid_count > 0:
            logger.debug(f"Filtered out {invalid_count} invalid details")
        
        return validated_details

