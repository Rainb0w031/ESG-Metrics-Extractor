"""
Duplicate detection for ESG metrics and details.

Uses fuzzy matching to identify duplicate entries during merging.
Extracted from ESGLLMAnalyzer._is_duplicate_metric(), _is_duplicate_detail(), 
and _calculate_text_similarity().
"""

import re
from typing import List, Dict, Any
from loguru import logger


class DuplicateDetector:
    """
    Detects duplicate metrics and details using fuzzy matching.
    
    Features:
    - Exact matching (direct comparison)
    - Fuzzy name matching (handles variations like underscores/spaces)
    - Year suffix handling (metrics with/without year suffixes)
    - Jaccard similarity for text comparison
    - Configurable similarity threshold
    
    This prevents duplicate information from being included when merging
    results from multiple text chunks.
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize duplicate detector.
        
        Args:
            similarity_threshold: Minimum similarity (0.0-1.0) to consider duplicates
        """
        self.similarity_threshold = similarity_threshold
        logger.debug(f"Duplicate detector initialized with threshold={similarity_threshold}")
    
    def is_duplicate_metric(self, metric_name: str, metric_value: Any, 
                           existing_metrics: Dict[str, Any]) -> bool:
        """
        Check if a metric is a duplicate using fuzzy matching.
        
        Checks:
        1. Direct name match
        2. Normalized name match (underscores/spaces)
        3. Name without year suffix match
        
        Args:
            metric_name: Name of the metric to check
            metric_value: Value of the metric (not currently used but available)
            existing_metrics: Dict of existing metrics
        
        Returns:
            True if metric is a duplicate, False otherwise
        """
        # Direct name match
        if metric_name in existing_metrics:
            logger.debug(f"Metric '{metric_name}' is exact duplicate")
            return True
        
        # Fuzzy name matching (handle slight variations)
        metric_name_clean = re.sub(r'[_\s]+', '_', metric_name.lower())
        
        for existing_name in existing_metrics.keys():
            existing_name_clean = re.sub(r'[_\s]+', '_', existing_name.lower())
            
            # Check for very similar names
            if metric_name_clean == existing_name_clean:
                logger.debug(f"Metric '{metric_name}' matches '{existing_name}' (normalized)")
                return True
            
            # Check for name variations (with/without year suffix)
            # This handles cases like 'scope_1_2022' vs 'scope_1_2023' 
            # (both refer to same metric, different years)
            for year in ['_2020', '_2021', '_2022', '_2023', '_2024', '_2025']:
                name_without_year = metric_name_clean.replace(year, '')
                existing_without_year = existing_name_clean.replace(year, '')
                
                if name_without_year and name_without_year == existing_without_year:
                    logger.debug(f"Metric '{metric_name}' matches '{existing_name}' (year variation)")
                    return True
        
        return False
    
    def is_duplicate_detail(self, detail: str, existing_details: List[str]) -> bool:
        """
        Check if a detail is a duplicate using fuzzy matching.
        
        Checks:
        1. Exact match
        2. Normalized match (remove punctuation)
        3. Jaccard similarity for substantial overlap
        
        Args:
            detail: Detail text to check
            existing_details: List of existing detail strings
        
        Returns:
            True if detail is a duplicate, False otherwise
        """
        # Exact match
        if detail in existing_details:
            logger.debug(f"Detail is exact duplicate: '{detail[:50]}...'")
            return True
        
        # Fuzzy matching for similar details
        detail_clean = re.sub(r'[^\w\s]', '', detail.lower()).strip()
        
        for existing_detail in existing_details:
            existing_clean = re.sub(r'[^\w\s]', '', existing_detail.lower()).strip()
            
            # Check for very similar content (exact match after normalization)
            if detail_clean == existing_clean:
                logger.debug(f"Detail matches (normalized): '{detail[:50]}...'")
                return True
            
            # Check for substantial overlap (>80% similarity)
            # Only for longer texts (>20 chars) to avoid false positives
            if len(detail_clean) > 20 and len(existing_clean) > 20:
                similarity = self.calculate_text_similarity(detail_clean, existing_clean)
                if similarity > self.similarity_threshold:
                    logger.debug(f"Detail matches (similarity={similarity:.2f}): '{detail[:50]}...'")
                    return True
        
        return False
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate Jaccard similarity between two text strings.
        
        Jaccard similarity = |intersection| / |union|
        
        This measures how many words are common between two texts
        compared to the total unique words.
        
        Args:
            text1: First text
            text2: Second text
        
        Returns:
            Similarity score (0.0 = no overlap, 1.0 = identical)
        """
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0.0
        
        return similarity
    
    def filter_duplicates(self, items: List[str]) -> List[str]:
        """
        Filter out duplicate items from a list.
        
        Args:
            items: List of items to filter
        
        Returns:
            List with duplicates removed
        """
        unique_items = []
        
        for item in items:
            if not self.is_duplicate_detail(item, unique_items):
                unique_items.append(item)
        
        logger.debug(f"Filtered {len(items)} items → {len(unique_items)} unique items")
        return unique_items
    
    def get_duplicate_stats(self, items: List[str]) -> Dict[str, int]:
        """
        Get statistics about duplicates in a list.
        
        Args:
            items: List of items to analyze
        
        Returns:
            Dict with duplicate statistics
        """
        unique = self.filter_duplicates(items)
        return {
            "total": len(items),
            "unique": len(unique),
            "duplicates": len(items) - len(unique),
            "duplicate_rate": (len(items) - len(unique)) / len(items) if items else 0
        }

