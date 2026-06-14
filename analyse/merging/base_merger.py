"""
Base merger interface for result merging.

Defines the abstract interface for merging analysis results from multiple chunks.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseMerger(ABC):
    """
    Abstract base for result mergers.
    
    Mergers combine analysis results from multiple text chunks into a single
    comprehensive result, handling duplicates and preserving all unique information.
    """
    
    @abstractmethod
    def merge(self, existing: Dict[str, Any], new: Dict[str, Any], 
              analysis_type: str = None) -> Dict[str, Any]:
        """
        Merge two result dictionaries.
        
        Args:
            existing: Existing accumulated results
            new: New results to merge in
            analysis_type: Optional type hint for merging strategy
        
        Returns:
            Merged results containing both existing and new data
        """
        pass
    
    @abstractmethod
    def merge_all(self, results: List[Dict[str, Any]], analysis_type: str) -> Dict[str, Any]:
        """
        Merge multiple results sequentially.
        
        Args:
            results: List of result dictionaries to merge
            analysis_type: Type of analysis ("comprehensive", "environmental", etc.)
        
        Returns:
            Single merged result dictionary
        """
        pass
    
    def get_merge_stats(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about merging operation.
        
        Args:
            results: List of results that will be merged
        
        Returns:
            Dict with statistics (count, total_items, etc.)
        """
        return {
            "result_count": len(results),
            "non_empty_count": sum(1 for r in results if r),
            "empty_count": sum(1 for r in results if not r)
        }

