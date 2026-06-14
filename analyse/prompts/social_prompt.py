"""
Social ESG analysis prompt builder.

Builds prompts for social-only ESG analysis.
"""

from typing import List
from .base_prompt import BasePromptBuilder


class SocialPromptBuilder(BasePromptBuilder):
    """
    Builds prompts for social ESG analysis.
    
    Focuses only on social dimension:
    - Diversity & Inclusion
    - Employee Development
    - Health & Safety
    - Compensation & Benefits
    - Community Engagement
    - Human Rights
    """
    
    def build(self, chunk: List[str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """Build social ESG analysis prompt."""
        chunk_text = "\n".join(chunk)
        
        return f"""You are an expert ESG analyst specializing in Social (S) data extraction and categorization. 
Analyze the following text content chunk from the {year} Sustainability Report (chunk {chunk_num}/{total_chunks}) and extract ALL social information. 

CRITICAL REQUIREMENTS:
1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS
2. Include diversity, safety, training, and community metrics
3. Preserve exact numbers and units
4. Include year suffixes for metrics
5. Extract both current performance and targets

RESPOND WITH VALID JSON ONLY containing social_comprehensive structure.

TEXT TO ANALYZE:
{chunk_text}

RESPOND WITH VALID JSON ONLY:"""

