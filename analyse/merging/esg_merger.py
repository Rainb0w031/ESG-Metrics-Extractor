"""
ESG-specific result merger.

Main merger that orchestrates category, section, and subsection merging.
Extracted from ESGLLMAnalyzer._merge_esg_results().
"""

from typing import Dict, List, Any
from loguru import logger

from .base_merger import BaseMerger
from .category_merger import CategoryMerger
from .section_merger import SectionMerger
from .duplicate_detector import DuplicateDetector


class ESGMerger(BaseMerger):
    """
    ESG-specific result merger.
    
    Handles merging of ESG analysis results from multiple text chunks,
    supporting:
    - Comprehensive analysis (all three ESG categories)
    - Single-category analysis (environmental, social, or governance)
    
    Orchestrates:
    - CategoryMerger: Merges environmental/social/governance categories
    - SectionMerger: Merges sections within categories
    - DuplicateDetector: Prevents duplicate metrics and details
    """
    
    def __init__(self,
                 category_merger: CategoryMerger = None,
                 section_merger: SectionMerger = None,
                 duplicate_detector: DuplicateDetector = None):
        """
        Initialize ESG merger with dependency injection.
        
        Args:
            category_merger: Category merger instance
            section_merger: Section merger instance
            duplicate_detector: Duplicate detector instance
        """
        # Create instances if not provided
        if duplicate_detector is None:
            duplicate_detector = DuplicateDetector()
        
        if section_merger is None:
            section_merger = SectionMerger(duplicate_detector)
        
        if category_merger is None:
            category_merger = CategoryMerger(section_merger)
        
        self.category_merger = category_merger
        self.section_merger = section_merger
        self.duplicate_detector = duplicate_detector
        
        logger.info("ESG merger initialized")
    
    def merge(self, existing: Dict[str, Any], new: Dict[str, Any], 
              analysis_type: str = None) -> Dict[str, Any]:
        """
        Merge two ESG result dictionaries.
        
        Args:
            existing: Existing accumulated results
            new: New results to merge in
            analysis_type: Optional analysis type hint. If provided, uses this instead
                          of auto-detecting from data structure. This is more reliable
                          when LLM responses have inconsistent structure.
        
        Returns:
            Merged results
        """
        if not existing:
            logger.debug("No existing results, using new results")
            return new if new else {}
        
        if not new:
            logger.debug("No new results, keeping existing")
            return existing
        
        merged_results = existing.copy()
        
        # Detect format from data (more reliable than caller hint)
        detected_type = self._determine_analysis_type(new)
        if existing:
            existing_type = self._determine_analysis_type(existing)
            # Prefer simple format if either side uses it
            if detected_type == "simple" or existing_type == "simple":
                detected_type = "simple"
        
        # Use detected type; fall back to caller hint only if detection is inconclusive
        merge_type = detected_type
        if merge_type == "comprehensive" and analysis_type == "simple":
            merge_type = "simple"
        
        logger.debug(f"Merging with type: {merge_type} (detected={detected_type}, hint={analysis_type})")
        
        if merge_type == "simple":
            merged_results = self._merge_simple(merged_results, new)
        elif merge_type == "comprehensive":
            merged_results = self._merge_comprehensive(merged_results, new)
        elif merge_type in ["environmental", "social", "governance"]:
            merged_results = self._merge_single_category(merged_results, new, merge_type)
        
        return merged_results
    
    def merge_all(self, results: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        """
        Merge multiple results sequentially.
        
        Args:
            results: List of result dictionaries to merge
            analysis_type: Type of analysis
        
        Returns:
            Single merged result dictionary
        """
        if not results:
            logger.warning("No results to merge")
            return {}
        
        # Filter out None/empty results
        valid_results = [r for r in results if r]
        
        if not valid_results:
            logger.warning("All results are empty")
            return {}
        
        logger.info(f"Merging {len(valid_results)} {analysis_type} results...")
        
        # Start with first result
        merged = valid_results[0]
        
        # Merge remaining results sequentially
        for i, result in enumerate(valid_results[1:], 2):
            logger.debug(f"Merging result {i}/{len(valid_results)}...")
            merged = self.merge(merged, result)
        
        logger.info(f"Merge complete: {len(valid_results)} results combined")
        
        return merged
    
    def _determine_analysis_type(self, results: Dict[str, Any]) -> str:
        """
        Determine analysis type from results structure.
        
        Args:
            results: Results dictionary
        
        Returns:
            Analysis type string
        """
        # Check for comprehensive structure (old format with _comprehensive suffix)
        comprehensive_keys = [
            "environmental_comprehensive",
            "social_comprehensive",
            "governance_comprehensive"
        ]
        
        has_comprehensive = any(key in results for key in comprehensive_keys)
        
        if has_comprehensive:
            return "comprehensive"
        
        # Check for simple format (new format without suffix)
        simple_keys = ["environmental", "social", "governance"]
        has_simple = any(key in results for key in simple_keys)
        
        if has_simple:
            return "simple"
        
        # Default to comprehensive
        return "comprehensive"
    
    def _merge_comprehensive(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge comprehensive ESG analysis results.
        
        Args:
            existing: Existing results
            new: New results
        
        Returns:
            Merged results
        """
        merged = existing.copy()
        
        # Merge each ESG category
        for category in ["environmental_comprehensive", "social_comprehensive", "governance_comprehensive"]:
            if category in new:
                if category in merged:
                    # Category exists in both, merge them
                    merged[category] = self.category_merger.merge(
                        merged[category],
                        new[category]
                    )
                    logger.debug(f"Merged category: {category}")
                else:
                    # New category, add it
                    merged[category] = new[category]
                    logger.debug(f"Added new category: {category}")
        
        return merged
    
    def _merge_simple(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge simple format ESG results (without _comprehensive suffix).
        
        Simple format:
        {
            "environmental": {"metrics": {...}, "details": [...]},
            "social": {"metrics": {...}, "details": [...]},
            "governance": {"metrics": {...}, "details": [...]}
        }
        
        Args:
            existing: Existing results
            new: New results
        
        Returns:
            Merged results
        """
        merged = existing.copy()
        
        for category in ["environmental", "social", "governance"]:
            if category in new:
                if category not in merged:
                    merged[category] = new[category]
                else:
                    # Merge metrics
                    if "metrics" in new[category]:
                        if "metrics" not in merged[category]:
                            merged[category]["metrics"] = {}
                        merged[category]["metrics"].update(new[category].get("metrics", {}))
                    
                    # Merge details (deduplicate)
                    if "details" in new[category]:
                        if "details" not in merged[category]:
                            merged[category]["details"] = []
                        existing_details = set(merged[category]["details"])
                        for detail in new[category].get("details", []):
                            if detail not in existing_details:
                                merged[category]["details"].append(detail)
                    
                    # Handle nested subcategories (for SimpleComprehensivePromptBuilder)
                    for key, value in new[category].items():
                        if key not in ["metrics", "details"] and isinstance(value, dict):
                            if key not in merged[category]:
                                merged[category][key] = value
                            else:
                                # Merge nested metrics
                                if "metrics" in value:
                                    if "metrics" not in merged[category][key]:
                                        merged[category][key]["metrics"] = {}
                                    merged[category][key]["metrics"].update(value.get("metrics", {}))
                                # Merge nested details
                                if "details" in value:
                                    if "details" not in merged[category][key]:
                                        merged[category][key]["details"] = []
                                    existing_nested = set(merged[category][key]["details"])
                                    for detail in value.get("details", []):
                                        if detail not in existing_nested:
                                            merged[category][key]["details"].append(detail)
                
                logger.debug(f"Merged simple category: {category}")
        
        return merged
    
    def _merge_single_category(self, existing: Dict[str, Any], new: Dict[str, Any], 
                               analysis_type: str) -> Dict[str, Any]:
        """
        Merge single-category analysis results.
        
        Args:
            existing: Existing results
            new: New results
            analysis_type: Category type (environmental, social, governance)
        
        Returns:
            Merged results
        """
        merged = existing.copy()
        
        # Map analysis type to result key
        category_key_map = {
            "environmental": "environmental_comprehensive",
            "social": "social_comprehensive",
            "governance": "governance_comprehensive"
        }
        
        category_key = category_key_map.get(analysis_type)
        
        if category_key and category_key in new:
            if category_key in merged:
                merged[category_key] = self.category_merger.merge(
                    merged[category_key],
                    new[category_key]
                )
            else:
                merged[category_key] = new[category_key]
        
        return merged

