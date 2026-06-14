"""ESG keyword definitions and patterns."""

from typing import Dict, List
import re

# ESG keyword categories
ESG_KEYWORDS: Dict[str, List[str]] = {
    'environmental': [
        'sustainability', 'environmental', 'carbon', 'emissions', 'renewable',
        'energy', 'water', 'waste', 'biodiversity', 'climate', 'greenhouse',
        'recycling', 'pollution', 'conservation', 'ecosystem'
    ],
    'social': [
        'social', 'community', 'diversity', 'inclusion', 'human rights',
        'labor', 'employee', 'health', 'safety', 'wellbeing', 'stakeholder',
        'supply chain', 'responsible', 'ethical', 'fair trade'
    ],
    'governance': [
        'governance', 'board', 'leadership', 'ethics', 'compliance',
        'transparency', 'risk', 'management', 'corporate', 'structure',
        'policy', 'regulation', 'oversight', 'accountability'
    ]
}

# ESG metrics patterns
ESG_METRIC_KEYWORDS = [
    'carbon footprint', 'energy consumption', 'water usage', 'waste reduction',
    'employee satisfaction', 'diversity ratio', 'safety incidents',
    'board diversity', 'executive compensation', 'compliance rate',
    'carbon emissions'
]

# Regex patterns for extracting metric values
METRIC_PATTERNS = [
    # Pattern: "metric reduced/increased/improved/decreased by X%"
    r'(carbon emissions|energy consumption|water usage|waste|diversity ratio|safety incidents|board diversity|compliance rate) (reduced|increased|improved|decreased) by (\d+)%',
    # Pattern: "metric: X%"
    r'(carbon emissions|energy consumption|water usage|waste|diversity ratio|safety incidents|board diversity|compliance rate): (\d+)%',
    # Pattern: "X% reduction/increase in metric"
    r'(\d+)% (reduction|increase) in (carbon emissions|energy consumption|water usage|waste)',
]


def get_esg_category_keywords(category: str) -> List[str]:
    """
    Get keywords for a specific ESG category.
    
    Args:
        category: ESG category ('environmental', 'social', 'governance')
        
    Returns:
        List of keywords for that category
    """
    return ESG_KEYWORDS.get(category, [])


def get_all_esg_keywords() -> Dict[str, List[str]]:
    """Get all ESG keywords organized by category."""
    return ESG_KEYWORDS.copy()


def extract_metric_patterns(text: str) -> List[str]:
    """
    Extract ESG metric patterns from text.
    
    Args:
        text: Text to analyze
        
    Returns:
        List of extracted metric patterns
    """
    text_lower = text.lower()
    found_metrics = []
    
    # Try each regex pattern
    for pattern in METRIC_PATTERNS:
        matches = re.findall(pattern, text_lower)
        if matches:
            for match in matches:
                # Reconstruct the full metric phrase
                if isinstance(match, tuple):
                    metric_phrase = ' '.join(str(m) for m in match if m)
                    found_metrics.append(metric_phrase)
    
    # Also check for simple keyword matches
    for metric in ESG_METRIC_KEYWORDS:
        if metric in text_lower:
            found_metrics.append(metric)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_metrics = []
    for metric in found_metrics:
        if metric not in seen:
            seen.add(metric)
            unique_metrics.append(metric)
    
    return unique_metrics

