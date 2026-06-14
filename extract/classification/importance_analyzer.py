"""Text importance analysis - eliminates code duplication."""

from typing import Optional
from ..core.base import BaseClassifier
from .text_roles import (
    HIGH_IMPORTANCE_INDICATORS,
    LOW_IMPORTANCE_INDICATORS,
    ESG_KEYWORDS
)


class ImportanceAnalyzer(BaseClassifier):
    """
    Analyzes text importance (high, medium, low).
    
    This class consolidates the duplicated importance analysis logic from
    BaseExtractor and SegmentCreator into a single implementation.
    """
    
    def classify_role(self, text: str) -> str:
        """Not used - importance analyzer doesn't classify roles."""
        from .role_classifier import RoleClassifier
        classifier = RoleClassifier()
        return classifier.classify_role(text)
    
    def analyze_importance(self, text: str, role: str, position: str,
                          segment_num: Optional[int] = None,
                          total_segments: Optional[int] = None) -> str:
        """
        Analyze the importance level of text.
        
        Args:
            text: Text content to analyze
            role: Text role classification
            position: Position in document ('start', 'middle', 'end')
            segment_num: Optional segment number on page
            total_segments: Optional total segments on page
            
        Returns:
            Importance level ('high', 'medium', 'low')
        """
        if not text or len(text.strip()) == 0:
            return 'low'
        
        text_lower = text.lower().strip()
        text_length = len(text)
        
        # Base importance from role
        if role in ['headline', 'subheadline', 'executive_summary']:
            return 'high'
        elif role in ['footnote', 'metadata', 'disclaimer']:
            return 'low'
        
        # Position-based importance (first and last segments often more important)
        if segment_num is not None and total_segments is not None:
            if (segment_num == 1 or segment_num == total_segments) and text_length > 50:
                return 'high'
        
        # Content-based importance analysis
        
        # Check for high importance indicators
        if self._has_high_importance_content(text_lower):
            return 'high'
        
        # Check for low importance indicators
        if self._has_low_importance_content(text_lower):
            return 'low'
        
        # Length-based importance
        if text_length > 200:
            return 'high'
        elif text_length < 30:
            return 'low'
        
        # ESG-specific importance boost
        if self._has_esg_keywords(text_lower):
            return 'high'
        
        # Default to medium for balanced content
        return 'medium'
    
    def _has_high_importance_content(self, text_lower: str) -> bool:
        """Check if text contains high importance indicators."""
        return any(indicator in text_lower for indicator in HIGH_IMPORTANCE_INDICATORS)
    
    def _has_low_importance_content(self, text_lower: str) -> bool:
        """Check if text contains low importance indicators."""
        return any(indicator in text_lower for indicator in LOW_IMPORTANCE_INDICATORS)
    
    def _has_esg_keywords(self, text_lower: str) -> bool:
        """Check if text contains ESG keywords."""
        return any(keyword in text_lower for keyword in ESG_KEYWORDS)
    
    def get_importance_score(self, text: str, role: str, position: str) -> float:
        """
        Get numeric importance score (0.0 to 1.0).
        
        Args:
            text: Text content
            role: Text role
            position: Position in document
            
        Returns:
            Importance score (0.0 = lowest, 1.0 = highest)
        """
        importance = self.analyze_importance(text, role, position)
        
        importance_scores = {
            'low': 0.3,
            'medium': 0.6,
            'high': 0.9
        }
        
        return importance_scores.get(importance, 0.6)
    
    def create_context_description(self, text: str, role: str, page_num: int) -> str:
        """
        Create a context description for a text segment.
        
        Args:
            text: Text content
            role: Text role
            page_num: Page number
            
        Returns:
            Context description
        """
        text_lower = text.lower()
        
        if role == 'headline':
            return f"Main section header on page {page_num}"
        elif role == 'subheadline':
            return f"Subsection header on page {page_num}"
        elif role == 'content':
            # Check for ESG-specific content
            if any(word in text_lower for word in ['sustainability', 'environmental', 'carbon', 'emissions']):
                return f"Environmental content on page {page_num}"
            elif any(word in text_lower for word in ['social', 'community', 'diversity', 'inclusion']):
                return f"Social responsibility content on page {page_num}"
            elif any(word in text_lower for word in ['governance', 'board', 'leadership', 'ethics']):
                return f"Governance content on page {page_num}"
            else:
                return f"General content on page {page_num}"
        elif role == 'caption':
            return f"Figure or table caption on page {page_num}"
        elif role == 'footnote':
            return f"Footnote or reference on page {page_num}"
        elif role == 'list_item':
            return f"List item on page {page_num}"
        elif role == 'table_content':
            return f"Table data on page {page_num}"
        else:
            return f"{role} content on page {page_num}"

