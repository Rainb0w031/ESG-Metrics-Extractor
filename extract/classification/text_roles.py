"""Text role definitions and descriptions."""

from typing import Dict

# Single source of truth for text role definitions
TEXT_ROLES: Dict[str, str] = {
    'headline': 'Main titles, chapter titles, section headers',
    'subheadline': 'Subsection headers, minor titles',
    'content': 'Main body text, paragraphs, descriptions',
    'caption': 'Figure captions, table captions, image descriptions',
    'footnote': 'Footnotes, endnotes, references',
    'list_item': 'Bullet points, numbered lists, list items',
    'table_content': 'Table data, tabular information',
    'metadata': 'Page numbers, dates, document metadata',
    'quote': 'Quotations, highlighted text, callouts',
    'code': 'Code snippets, technical specifications',
    'formula': 'Mathematical formulas, equations',
    'contact_info': 'Contact information, addresses, phone numbers',
    'disclaimer': 'Legal disclaimers, terms, conditions',
    'executive_summary': 'Executive summaries, key findings',
    'methodology': 'Methodology sections, procedures',
    'results': 'Results sections, findings, data',
    'conclusion': 'Conclusions, recommendations',
    'appendix': 'Appendix content, supplementary information'
}


# Role-specific patterns for classification
ROLE_PATTERNS = {
    'headline': {
        'indicators': ['CHAPTER', 'SECTION', 'PART', 'APPENDIX'],
        'max_length': 100,
        'must_be_uppercase_or_short': True
    },
    'list_item': {
        'start_chars': ['•', '-', '*', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.']
    },
    'caption': {
        'keywords': ['figure', 'table', 'image', 'photo', 'chart', 'graph']
    },
    'contact_info': {
        'keywords': ['contact', 'phone', 'email', 'address', '@', 'www.']
    },
    'footnote': {
        'start_patterns': ['note:', 'footnote', 'reference'],
        'keywords': ['footnote', 'endnote', 'reference']
    },
    'disclaimer': {
        'keywords': ['disclaimer', 'terms', 'conditions', 'copyright', 'all rights reserved']
    },
    'executive_summary': {
        'keywords': ['executive summary', 'key findings', 'summary']
    },
    'methodology': {
        'keywords': ['methodology', 'method', 'procedure', 'approach']
    },
    'results': {
        'keywords': ['results', 'findings', 'data', 'analysis']
    }
}


# Importance indicators
HIGH_IMPORTANCE_INDICATORS = [
    'sustainability', 'carbon', 'emissions', 'renewable', 'energy',
    'climate', 'net-zero', 'target', 'goal', 'commitment',
    'diversity', 'inclusion', 'human rights', 'community',
    'governance', 'board', 'leadership', 'ethics', 'compliance',
    'key findings', 'summary', 'conclusion', 'recommendation',
    'performance', 'metrics', 'data', 'results', 'achievement'
]

LOW_IMPORTANCE_INDICATORS = [
    'page', 'copyright', 'all rights reserved', 'disclaimer',
    'terms and conditions', 'footnote', 'endnote', 'reference',
    'appendix', 'glossary', 'index', 'table of contents'
]

# ESG-specific keywords for importance boosting
ESG_KEYWORDS = [
    'environmental', 'social', 'governance', 'esg',
    'sustainability', 'responsibility', 'impact', 'stakeholder'
]


def get_role_description(role: str) -> str:
    """
    Get description for a text role.
    
    Args:
        role: Role name
        
    Returns:
        Role description
    """
    return TEXT_ROLES.get(role, f"Unknown role: {role}")


def get_all_roles() -> Dict[str, str]:
    """Get all available text roles and their descriptions."""
    return TEXT_ROLES.copy()

