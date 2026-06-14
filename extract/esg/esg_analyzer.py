"""ESG content analysis."""

from typing import Dict, Any, List
from ..core.base import BaseESGAnalyzer
from .esg_keywords import (
    get_all_esg_keywords,
    extract_metric_patterns
)


class ESGContentAnalyzer(BaseESGAnalyzer):
    """Analyzes text content for ESG-specific information."""
    
    def __init__(self):
        """Initialize ESG content analyzer."""
        self.esg_keywords = get_all_esg_keywords()
    
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze ESG content in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with ESG analysis results
        """
        text_lower = text.lower()
        
        esg_categories = []
        esg_keywords_found = []
        
        # Check each ESG category
        for category, keywords in self.esg_keywords.items():
            category_keywords = [kw for kw in keywords if kw in text_lower]
            if category_keywords:
                esg_categories.append(category)
                esg_keywords_found.extend(category_keywords)
        
        # Extract ESG metrics
        esg_metrics = extract_metric_patterns(text)
        
        # Determine primary ESG focus
        primary_esg_focus = self._determine_primary_focus(esg_categories, text_lower)
        
        # Calculate ESG relevance score
        esg_relevance_score = len(esg_keywords_found) / max(len(text.split()), 1)
        
        return {
            'esg_categories': esg_categories,
            'esg_metrics': esg_metrics,
            'esg_keywords': list(set(esg_keywords_found)),
            'primary_esg_focus': primary_esg_focus,
            'esg_relevance_score': min(1.0, esg_relevance_score)  # Cap at 1.0
        }
    
    def _determine_primary_focus(self, esg_categories: List[str], text_lower: str) -> str:
        """
        Determine the primary ESG focus area.
        
        Args:
            esg_categories: List of ESG categories found
            text_lower: Lowercase text
            
        Returns:
            Primary ESG focus or None
        """
        if not esg_categories:
            return None
        
        # Count keyword occurrences for each category
        category_counts = {}
        for category in esg_categories:
            keywords = self.esg_keywords[category]
            count = sum(1 for kw in keywords if kw in text_lower)
            category_counts[category] = count
        
        # Return category with most keywords
        return max(category_counts, key=category_counts.get)
    
    def extract_metrics(self, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract ESG metrics from structured content.
        
        Args:
            structured_content: Structured PDF content
            
        Returns:
            Dictionary with ESG metrics organized by category
        """
        esg_metrics = {
            'environmental_metrics': [],
            'social_metrics': [],
            'governance_metrics': [],
            'summary': {}
        }
        
        # Extract metrics from all segments
        for page in structured_content.get('pages', []):
            for segment in page.get('text_segments', []):
                esg_categories = segment.get('esg_categories', [])
                segment_metrics = segment.get('esg_metrics', [])
                
                # Categorize metrics
                for category in esg_categories:
                    if category == 'environmental':
                        esg_metrics['environmental_metrics'].extend(segment_metrics)
                    elif category == 'social':
                        esg_metrics['social_metrics'].extend(segment_metrics)
                    elif category == 'governance':
                        esg_metrics['governance_metrics'].extend(segment_metrics)
        
        # Remove duplicates
        esg_metrics['environmental_metrics'] = list(set(esg_metrics['environmental_metrics']))
        esg_metrics['social_metrics'] = list(set(esg_metrics['social_metrics']))
        esg_metrics['governance_metrics'] = list(set(esg_metrics['governance_metrics']))
        
        # Generate summary
        esg_metrics['summary'] = {
            'total_environmental_metrics': len(esg_metrics['environmental_metrics']),
            'total_social_metrics': len(esg_metrics['social_metrics']),
            'total_governance_metrics': len(esg_metrics['governance_metrics']),
            'total_esg_metrics': (
                len(esg_metrics['environmental_metrics']) + 
                len(esg_metrics['social_metrics']) + 
                len(esg_metrics['governance_metrics'])
            )
        }
        
        return esg_metrics

