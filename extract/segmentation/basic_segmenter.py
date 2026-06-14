"""Basic heuristic-based segmentation."""

from typing import Dict, Any
from ..core.base import BaseSegmenter
from ..classification.role_classifier import RoleClassifier
from ..classification.importance_analyzer import ImportanceAnalyzer


class BasicSegmenter(BaseSegmenter):
    """
    Creates text segments using heuristic-based classification.
    No LLM required - fast and reliable.
    """
    
    def __init__(self):
        """Initialize basic segmenter with classifiers."""
        self.role_classifier = RoleClassifier()
        self.importance_analyzer = ImportanceAnalyzer()
    
    def create_segment(self, text: str, page_num: int, segment_num: int, 
                      total_segments: int) -> Dict[str, Any]:
        """
        Create a segment using heuristic classification.
        
        Args:
            text: Text content
            page_num: Page number
            segment_num: Segment number on the page
            total_segments: Total segments on the page
            
        Returns:
            Segment dictionary
        """
        # Classify role
        role = self.role_classifier.classify_role(text)
        
        # Determine position
        if segment_num == 1:
            position = "start"
        elif segment_num == total_segments:
            position = "end"
        else:
            position = "middle"
        
        # Analyze importance
        importance = self.importance_analyzer.analyze_importance(
            text, role, position, segment_num, total_segments
        )
        
        # Calculate confidence based on text characteristics
        confidence = self._calculate_confidence(text, role)
        
        # Create context description
        context = self.importance_analyzer.create_context_description(text, role, page_num)
        
        return {
            'segment_id': f"page_{page_num}_segment_{segment_num}",
            'text': text,
            'role': role,
            'chunk_index': segment_num - 1,
            'confidence': confidence,
            'position': position,
            'importance': importance,
            'context': context
        }
    
    def _calculate_confidence(self, text: str, role: str) -> float:
        """
        Calculate confidence score for classification.
        
        Args:
            text: Text content
            role: Classified role
            
        Returns:
            Confidence score (0.0-1.0)
        """
        # Base confidence
        confidence = 0.8
        
        # Adjust based on text length
        if len(text) < 20:
            confidence = 0.6  # Less confident for very short text
        elif role == 'content' and len(text) > 100:
            confidence = 0.9  # More confident for substantial content
        
        # Boost confidence for clear structural elements
        if role in ['headline', 'list_item', 'footnote']:
            confidence = min(0.95, confidence + 0.1)
        
        return confidence

