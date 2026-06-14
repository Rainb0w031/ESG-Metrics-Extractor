"""
Section-level merger for ESG data.

Merges sections (emissions, energy, water, etc.) and their subsections.
Extracted from ESGLLMAnalyzer._merge_section_data() and _merge_subsection_data().
"""

from typing import Dict, Any
from loguru import logger

from .duplicate_detector import DuplicateDetector


class SectionMerger:
    """
    Merges section-level ESG data.
    
    Sections are major categories like:
    - emissions (with subsections: scope_1, scope_2, scope_3, etc.)
    - energy (with subsections: renewable_energy, energy_efficiency, etc.)
    - water (with subsections: water_use, water_replenishment, etc.)
    
    Each subsection contains:
    - details: List of text descriptions
    - metrics: Dict of quantitative metrics
    """
    
    def __init__(self, duplicate_detector: DuplicateDetector = None):
        """
        Initialize section merger.
        
        Args:
            duplicate_detector: Duplicate detector instance
        """
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
    
    def merge(self, existing_section: Dict[str, Any], new_section: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge section data (like emissions, energy, etc.).
        
        Handles two types of sections:
        1. Dict sections: Contains subsections as nested dicts
        2. List sections: Contains items as a list (strategies, goals)
        
        Args:
            existing_section: Existing section data
            new_section: New section data to merge
        
        Returns:
            Merged section data
        """
        if not existing_section:
            return new_section
        
        if not new_section:
            return existing_section
        
        merged_section = existing_section.copy()
        
        # Handle different section structures
        if isinstance(new_section, dict):
            # Dict-based section: merge each subsection
            for subsection_name, subsection_data in new_section.items():
                if subsection_name in merged_section:
                    # Subsection exists, merge it
                    merged_section[subsection_name] = self.merge_subsection(
                        merged_section[subsection_name], 
                        subsection_data
                    )
                    logger.debug(f"Merged subsection: {subsection_name}")
                else:
                    # New subsection, add it
                    merged_section[subsection_name] = subsection_data
                    logger.debug(f"Added new subsection: {subsection_name}")
        
        elif isinstance(new_section, list):
            # List-based section: extend or replace
            if isinstance(merged_section, list):
                merged_section.extend(new_section)
                logger.debug(f"Extended list section with {len(new_section)} items")
            else:
                merged_section = new_section
                logger.debug(f"Replaced with list section ({len(new_section)} items)")
        
        return merged_section
    
    def merge_subsection(self, existing_subsection: Dict[str, Any], 
                         new_subsection: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge subsection data (like details and metrics) with duplicate detection.
        
        Subsections typically contain:
        - details: List[str] - Text descriptions
        - metrics: Dict[str, str] - Quantitative metrics
        
        Args:
            existing_subsection: Existing subsection data
            new_subsection: New subsection data to merge
        
        Returns:
            Merged subsection data
        """
        if not existing_subsection:
            return new_subsection
        
        if not new_subsection:
            return existing_subsection
        
        merged_subsection = existing_subsection.copy()
        
        # Merge metrics with duplicate detection
        if "metrics" in new_subsection and "metrics" in merged_subsection:
            metrics_added = 0
            metrics_skipped = 0
            
            for metric_name, metric_value in new_subsection["metrics"].items():
                # Check for duplicates using fuzzy matching
                if not self.duplicate_detector.is_duplicate_metric(
                    metric_name, metric_value, merged_subsection["metrics"]
                ):
                    merged_subsection["metrics"][metric_name] = metric_value
                    metrics_added += 1
                else:
                    metrics_skipped += 1
            
            logger.debug(f"Metrics: added {metrics_added}, skipped {metrics_skipped} duplicates")
        
        elif "metrics" in new_subsection:
            merged_subsection["metrics"] = new_subsection["metrics"]
            logger.debug(f"Added {len(new_subsection['metrics'])} new metrics")
        
        # Merge details with duplicate detection
        if "details" in new_subsection and "details" in merged_subsection:
            details_added = 0
            details_skipped = 0
            
            for detail in new_subsection["details"]:
                # Check for duplicates using fuzzy matching
                if not self.duplicate_detector.is_duplicate_detail(
                    detail, merged_subsection["details"]
                ):
                    merged_subsection["details"].append(detail)
                    details_added += 1
                else:
                    details_skipped += 1
            
            logger.debug(f"Details: added {details_added}, skipped {details_skipped} duplicates")
        
        elif "details" in new_subsection:
            merged_subsection["details"] = new_subsection["details"]
            logger.debug(f"Added {len(new_subsection['details'])} new details")
        
        return merged_subsection

