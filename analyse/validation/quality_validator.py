"""
Quality validation for ESG analysis.

Main validator that orchestrates all validation strategies.
Extracted from ESGLLMAnalyzer._validate_and_clean_results() and related methods.
"""

from typing import Dict, Any
from loguru import logger

from .base_validator import BaseValidator
from .content_validator import ContentValidator
from .metric_validator import MetricValidator
from .structure_validator import StructureValidator


class QualityValidator(BaseValidator):
    """
    Comprehensive quality validation for ESG results.
    
    Orchestrates:
    - StructureValidator: Validates overall structure
    - ContentValidator: Validates details and text
    - MetricValidator: Validates metrics
    
    Provides:
    - Recursive validation of nested structures
    - Quality scoring
    - Cleaning of invalid data
    """
    
    def __init__(self,
                 structure_validator: StructureValidator = None,
                 content_validator: ContentValidator = None,
                 metric_validator: MetricValidator = None):
        """
        Initialize quality validator.
        
        Args:
            structure_validator: Structure validator instance
            content_validator: Content validator instance
            metric_validator: Metric validator instance
        """
        self.structure_validator = structure_validator or StructureValidator()
        self.content_validator = content_validator or ContentValidator()
        self.metric_validator = metric_validator or MetricValidator()
        
        logger.info("Quality validator initialized")
    
    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean analysis results.
        
        Recursively validates:
        1. Overall structure
        2. Categories (environmental, social, governance)
        3. Sections (emissions, energy, diversity, etc.)
        4. Subsections (scope_1, renewable_energy, etc.)
        5. Details and metrics
        
        Args:
            results: Results to validate
        
        Returns:
            Validated and cleaned results
        """
        if not results:
            logger.warning("Results are empty, cannot validate")
            return results
        
        logger.info("Validating analysis results...")
        
        # Validate structure
        if not self.structure_validator.has_valid_structure(results):
            logger.warning("Results have invalid structure")
        
        # Clean results
        cleaned_results = results.copy()
        
        # Validate and clean comprehensive ESG structure
        for category_key in ["environmental_comprehensive", "social_comprehensive", "governance_comprehensive"]:
            if category_key in cleaned_results:
                logger.debug(f"Validating category: {category_key}")
                cleaned_results[category_key] = self._validate_category(cleaned_results[category_key])
        
        # Also handle alternative keys with _analysis suffix
        for category_key in ["environmental_comprehensive_analysis", "social_comprehensive_analysis", "governance_comprehensive_analysis"]:
            if category_key in cleaned_results:
                logger.debug(f"Validating category: {category_key}")
                cleaned_results[category_key] = self._validate_category(cleaned_results[category_key])
        
        logger.info("Validation complete")
        
        return cleaned_results
    
    def _validate_category(self, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean a category of ESG data.
        
        Args:
            category_data: Category data to validate
        
        Returns:
            Validated category data
        """
        if not category_data:
            return category_data
        
        validated_category = {}
        sections_validated = 0
        sections_cleaned = 0
        
        for section_name, section_data in category_data.items():
            if isinstance(section_data, dict):
                # Dict section: validate recursively
                validated_section = self._validate_section(section_data)
                if validated_section:  # Only include non-empty sections
                    validated_category[section_name] = validated_section
                    sections_validated += 1
            
            elif isinstance(section_data, list):
                # List section: clean empty items
                cleaned_list = [item for item in section_data if item and str(item).strip()]
                if cleaned_list:  # Only include non-empty lists
                    validated_category[section_name] = cleaned_list
                    sections_cleaned += 1
        
        logger.debug(f"Category validation: {sections_validated} dict sections, {sections_cleaned} list sections")
        
        return validated_category
    
    def _validate_section(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean a section of ESG data.
        
        Args:
            section_data: Section data to validate
        
        Returns:
            Validated section data
        """
        if not section_data:
            return section_data
        
        validated_section = {}
        
        for subsection_name, subsection_data in section_data.items():
            if isinstance(subsection_data, dict):
                # Dict subsection: validate recursively
                validated_subsection = self._validate_subsection(subsection_data)
                if validated_subsection:  # Only include non-empty subsections
                    validated_section[subsection_name] = validated_subsection
            
            elif isinstance(subsection_data, list):
                # List subsection: clean empty items
                cleaned_list = [item for item in subsection_data if item and str(item).strip()]
                if cleaned_list:  # Only include non-empty lists
                    validated_section[subsection_name] = cleaned_list
        
        return validated_section
    
    def _validate_subsection(self, subsection_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean a subsection of ESG data.
        
        This is where we validate individual metrics and details.
        
        Args:
            subsection_data: Subsection data to validate
        
        Returns:
            Validated subsection data
        """
        if not subsection_data:
            return subsection_data
        
        validated_subsection = {}
        
        # Validate metrics
        if "metrics" in subsection_data:
            validated_metrics = self.metric_validator.validate_metrics_dict(
                subsection_data["metrics"]
            )
            if validated_metrics:  # Only include if there are valid metrics
                validated_subsection["metrics"] = validated_metrics
        
        # Validate details
        if "details" in subsection_data:
            validated_details = self.content_validator.validate_details_list(
                subsection_data["details"]
            )
            if validated_details:  # Only include if there are valid details
                validated_subsection["details"] = validated_details
        
        return validated_subsection
    
    def get_quality_score(self, results: Dict[str, Any]) -> float:
        """
        Calculate overall quality score.
        
        Combines scores from:
        - Structure (30%)
        - Content (35%)
        - Metrics (35%)
        
        Args:
            results: Results to score
        
        Returns:
            Quality score (0.0-1.0)
        """
        if not results:
            return 0.0
        
        # Get individual scores
        structure_score = self.structure_validator.get_quality_score(results)
        content_score = self.content_validator.get_quality_score(results)
        metric_score = self.metric_validator.get_quality_score(results)
        
        # Weighted average
        total_score = (
            structure_score * 0.30 +
            content_score * 0.35 +
            metric_score * 0.35
        )
        
        logger.info(f"Quality scores: structure={structure_score:.2f}, content={content_score:.2f}, metrics={metric_score:.2f}, total={total_score:.2f}")
        
        return total_score
    
    def get_validation_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive validation report.
        
        Args:
            results: Results to report on
        
        Returns:
            Dict with detailed validation information
        """
        report = {
            "valid": self.is_valid(results),
            "quality_score": self.get_quality_score(results),
            "structure": self.structure_validator.get_structure_report(results),
            "errors": self.get_errors(results),
            "warnings": self.get_warnings(results),
            "statistics": self._get_statistics(results)
        }
        
        return report
    
    def _get_statistics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get statistics about the results.
        
        Args:
            results: Results to analyze
        
        Returns:
            Dict with statistics
        """
        stats = {
            "total_categories": 0,
            "total_sections": 0,
            "total_subsections": 0,
            "total_metrics": 0,
            "total_details": 0
        }
        
        # Count categories
        for category_key in ["environmental_comprehensive", "social_comprehensive", "governance_comprehensive"]:
            if category_key in results and results[category_key]:
                stats["total_categories"] += 1
                
                # Count sections and subsections
                category_data = results[category_key]
                if isinstance(category_data, dict):
                    stats["total_sections"] += len(category_data)
                    
                    for section_data in category_data.values():
                        if isinstance(section_data, dict):
                            stats["total_subsections"] += len(section_data)
                            
                            # Count metrics and details
                            for subsection_data in section_data.values():
                                if isinstance(subsection_data, dict):
                                    if "metrics" in subsection_data:
                                        stats["total_metrics"] += len(subsection_data["metrics"])
                                    if "details" in subsection_data:
                                        stats["total_details"] += len(subsection_data["details"])
        
        return stats

