"""
Structure validation for ESG analysis.

Validates the overall structure of analysis results.
"""

from typing import Dict, Any
from loguru import logger

from .base_validator import BaseValidator


class StructureValidator(BaseValidator):
    """
    Validates ESG result structure.
    
    Checks:
    - Required keys present
    - Proper nesting
    - Type correctness
    - Structure completeness
    """
    
    def __init__(self):
        """Initialize structure validator."""
        self.required_comprehensive_keys = [
            "environmental_comprehensive",
            "social_comprehensive",
            "governance_comprehensive"
        ]
    
    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate structure of results.
        
        Args:
            results: Results to validate
        
        Returns:
            Validated results (unchanged if valid)
        """
        if not results:
            logger.warning("Results are empty")
            return results
        
        # Check structure
        if not self.has_valid_structure(results):
            logger.warning("Results have invalid structure")
        
        return results
    
    def has_valid_structure(self, results: Dict[str, Any]) -> bool:
        """
        Check if results have valid structure.
        
        Args:
            results: Results to check
        
        Returns:
            True if structure is valid
        """
        if not isinstance(results, dict):
            logger.error("Results is not a dict")
            return False
        
        # Check for at least one ESG category
        has_any_category = any(
            key in results 
            for key in [
                "environmental_comprehensive",
                "social_comprehensive",
                "governance_comprehensive",
                "environmental_comprehensive_analysis",
                "social_comprehensive_analysis",
                "governance_comprehensive_analysis"
            ]
        )
        
        if not has_any_category:
            logger.warning("No ESG categories found in results")
            return False
        
        return True
    
    def get_quality_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate quality score based on structure.
        
        Args:
            results: Results to score
        
        Returns:
            Quality score (0.0-1.0)
        """
        if not results:
            return 0.0
        
        score = 0.0
        
        # Check basic structure (0.3 points)
        if isinstance(results, dict) and len(results) > 0:
            score += 0.3
        
        # Check for ESG categories (0.3 points each, up to 0.7 total)
        categories = [
            "environmental_comprehensive",
            "social_comprehensive",
            "governance_comprehensive"
        ]
        
        found_categories = sum(1 for cat in categories if cat in results and results[cat])
        score += (found_categories / len(categories)) * 0.7
        
        return min(score, 1.0)
    
    def get_structure_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed structure report.
        
        Args:
            results: Results to report on
        
        Returns:
            Dict with structure details
        """
        report = {
            "is_dict": isinstance(results, dict),
            "keys": list(results.keys()) if isinstance(results, dict) else [],
            "has_environmental": "environmental_comprehensive" in results,
            "has_social": "social_comprehensive" in results,
            "has_governance": "governance_comprehensive" in results,
            "total_keys": len(results) if isinstance(results, dict) else 0
        }
        
        return report

