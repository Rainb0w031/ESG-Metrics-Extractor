"""Text role classification - eliminates code duplication."""

from typing import Optional
from ..core.base import BaseClassifier
from .text_roles import ROLE_PATTERNS


class RoleClassifier(BaseClassifier):
    """
    Classifies text segments into roles (headline, content, etc.).
    
    This class consolidates the duplicated classification logic from
    BaseExtractor and SegmentCreator into a single implementation.
    """
    
    def classify_role(self, text: str) -> str:
        """
        Classify the role of a text segment.
        
        Args:
            text: Text to classify
            
        Returns:
            Role string (e.g., 'headline', 'content', 'list_item')
        """
        if not text or len(text.strip()) == 0:
            return 'content'
        
        text_lower = text.lower().strip()
        text_upper = text.upper()
        text_stripped = text.strip()
        
        # Check headline patterns
        if self._is_headline(text, text_upper, text_stripped):
            return 'headline'
        
        # Check list item patterns
        if self._is_list_item(text_stripped):
            return 'list_item'
        
        # Check caption patterns
        if self._is_caption(text_lower):
            return 'caption'
        
        # Check contact info patterns
        if self._is_contact_info(text_lower):
            return 'contact_info'
        
        # Check footnote patterns
        if self._is_footnote(text_lower):
            return 'footnote'
        
        # Check disclaimer patterns
        if self._is_disclaimer(text_lower):
            return 'disclaimer'
        
        # Check executive summary patterns
        if self._is_executive_summary(text_lower):
            return 'executive_summary'
        
        # Check methodology patterns
        if self._is_methodology(text_lower):
            return 'methodology'
        
        # Check results patterns
        if self._is_results(text_lower):
            return 'results'
        
        # Default to content
        return 'content'
    
    def _is_headline(self, text: str, text_upper: str, text_stripped: str) -> bool:
        """Check if text is a headline."""
        patterns = ROLE_PATTERNS['headline']
        
        # Short text that's all uppercase
        if len(text) < patterns['max_length']:
            if text_upper == text:
                return True
            
            # Starts with headline indicators
            if any(text.startswith(ind) for ind in patterns['indicators']):
                return True
            
            # Short text (<=8 words) that's all uppercase
            if len(text.split()) <= 8 and text_upper == text:
                return True
        
        return False
    
    def _is_list_item(self, text_stripped: str) -> bool:
        """Check if text is a list item."""
        start_chars = ROLE_PATTERNS['list_item']['start_chars']
        return any(text_stripped.startswith(char) for char in start_chars)
    
    def _is_caption(self, text_lower: str) -> bool:
        """Check if text is a caption."""
        keywords = ROLE_PATTERNS['caption']['keywords']
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_contact_info(self, text_lower: str) -> bool:
        """Check if text is contact information."""
        keywords = ROLE_PATTERNS['contact_info']['keywords']
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_footnote(self, text_lower: str) -> bool:
        """Check if text is a footnote."""
        patterns = ROLE_PATTERNS['footnote']
        
        # Check start patterns
        if any(text_lower.startswith(pattern) for pattern in patterns['start_patterns']):
            return True
        
        # Check keywords
        if any(keyword in text_lower for keyword in patterns['keywords']):
            return True
        
        return False
    
    def _is_disclaimer(self, text_lower: str) -> bool:
        """Check if text is a disclaimer."""
        keywords = ROLE_PATTERNS['disclaimer']['keywords']
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_executive_summary(self, text_lower: str) -> bool:
        """Check if text is an executive summary."""
        keywords = ROLE_PATTERNS['executive_summary']['keywords']
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_methodology(self, text_lower: str) -> bool:
        """Check if text is methodology."""
        keywords = ROLE_PATTERNS['methodology']['keywords']
        return any(keyword in text_lower for keyword in keywords)
    
    def _is_results(self, text_lower: str) -> bool:
        """Check if text is results."""
        keywords = ROLE_PATTERNS['results']['keywords']
        return any(keyword in text_lower for keyword in keywords)
    
    def analyze_importance(self, text: str, role: str, position: str) -> str:
        """
        Analyze importance - delegate to ImportanceAnalyzer.
        
        This method is here for interface compatibility but delegates
        to the specialized ImportanceAnalyzer class.
        """
        from .importance_analyzer import ImportanceAnalyzer
        analyzer = ImportanceAnalyzer()
        return analyzer.analyze_importance(text, role, position)

