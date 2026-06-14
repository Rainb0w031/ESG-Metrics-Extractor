"""
Category-level merger for ESG data.

Merges categories (environmental, social, governance) and their sections.
Extracted from ESGLLMAnalyzer._merge_comprehensive_category().
"""

from typing import Dict, Any
from loguru import logger

from .section_merger import SectionMerger
from .duplicate_detector import DuplicateDetector


class CategoryMerger:
    """
    Merges category-level ESG data.
    
    Categories are the top-level ESG dimensions:
    - environmental_comprehensive
    - social_comprehensive
    - governance_comprehensive
    
    Each category contains multiple sections (emissions, energy, diversity, etc.)
    """
    
    def __init__(self, section_merger: SectionMerger = None):
        """
        Initialize category merger.
        
        Args:
            section_merger: Section merger instance
        """
        self.section_merger = section_merger or SectionMerger()
    
    def merge(self, existing_category: Dict[str, Any], new_category: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge a comprehensive ESG category (environmental, social, governance).
        
        Args:
            existing_category: Existing category data
            new_category: New category data to merge
        
        Returns:
            Merged category data
        """
        if not existing_category:
            logger.debug("No existing category, using new category")
            return new_category
        
        if not new_category:
            logger.debug("No new category data, keeping existing")
            return existing_category
        
        merged_category = existing_category.copy()
        
        # Merge each section in the category
        sections_added = 0
        sections_merged = 0
        
        for section_name, section_data in new_category.items():
            if section_name in merged_category:
                # Section exists, merge it
                merged_category[section_name] = self.section_merger.merge(
                    merged_category[section_name], 
                    section_data
                )
                sections_merged += 1
                logger.debug(f"Merged section: {section_name}")
            else:
                # New section, add it
                merged_category[section_name] = section_data
                sections_added += 1
                logger.debug(f"Added new section: {section_name}")
        
        logger.info(f"Category merge: {sections_merged} merged, {sections_added} added")
        
        return merged_category

