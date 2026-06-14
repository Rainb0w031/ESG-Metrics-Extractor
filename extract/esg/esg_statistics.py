"""ESG statistics calculation."""

from typing import Dict, Any


class ESGStatisticsCalculator:
    """Calculates ESG statistics from structured content."""
    
    @staticmethod
    def calculate_statistics(structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate ESG statistics across entire document.
        
        Args:
            structured_content: Structured PDF content
            
        Returns:
            Dictionary with ESG statistics
        """
        category_counts = {'environmental': 0, 'social': 0, 'governance': 0}
        total_metrics = 0
        relevance_scores = []
        
        # Analyze all segments
        for page in structured_content.get('pages', []):
            for segment in page.get('text_segments', []):
                # Count ESG categories
                esg_categories = segment.get('esg_categories', [])
                for category in esg_categories:
                    if category in category_counts:
                        category_counts[category] += 1
                
                # Count metrics
                esg_metrics = segment.get('esg_metrics', [])
                total_metrics += len(esg_metrics)
                
                # Collect relevance scores
                relevance_score = segment.get('esg_relevance_score', 0)
                if relevance_score > 0:
                    relevance_scores.append(relevance_score)
        
        # Calculate average relevance
        average_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        return {
            'category_counts': category_counts,
            'total_metrics': total_metrics,
            'average_relevance': average_relevance,
            'total_esg_segments': sum(category_counts.values())
        }
    
    @staticmethod
    def calculate_importance_distribution(structured_content: Dict[str, Any]) -> Dict[str, int]:
        """
        Calculate importance distribution across document.
        
        Args:
            structured_content: Structured PDF content
            
        Returns:
            Dictionary with importance counts
        """
        importance_stats = {'high': 0, 'medium': 0, 'low': 0}
        
        for page in structured_content.get('pages', []):
            for segment in page.get('text_segments', []):
                importance = segment.get('importance', 'medium')
                if importance in importance_stats:
                    importance_stats[importance] += 1
        
        return importance_stats

