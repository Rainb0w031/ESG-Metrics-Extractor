"""
Base validator interface for result validation.

Defines the abstract interface for validating analysis results.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseValidator(ABC):
    """
    Abstract base for result validators.
    
    Validators check analysis results for:
    - Structural correctness
    - Content quality
    - Metric validity
    - Overall quality scores
    """
    
    @abstractmethod
    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean results.
        
        Args:
            results: Results to validate
        
        Returns:
            Validated and cleaned results
        """
        pass
    
    @abstractmethod
    def get_quality_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate quality score for results.
        
        Args:
            results: Results to score
        
        Returns:
            Quality score (0.0-1.0)
        """
        pass
    
    def get_validation_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed validation report.
        
        Args:
            results: Results to report on
        
        Returns:
            Dict with validation details
        """
        return {
            "valid": self.is_valid(results),
            "quality_score": self.get_quality_score(results),
            "errors": self.get_errors(results),
            "warnings": self.get_warnings(results)
        }
    
    def is_valid(self, results: Dict[str, Any]) -> bool:
        """
        Check if results are valid.
        
        Args:
            results: Results to check
        
        Returns:
            True if valid, False otherwise
        """
        return results is not None and len(results) > 0
    
    def get_errors(self, results: Dict[str, Any]) -> list:
        """
        Get validation errors.
        
        Args:
            results: Results to check
        
        Returns:
            List of error messages
        """
        errors = []
        
        if not results:
            errors.append("Results are empty")
        
        return errors
    
    def get_warnings(self, results: Dict[str, Any]) -> list:
        """
        Get validation warnings.
        
        Args:
            results: Results to check
        
        Returns:
            List of warning messages
        """
        return []

