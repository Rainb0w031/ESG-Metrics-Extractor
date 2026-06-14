"""
Governance ESG analysis prompt builder.

Builds prompts for governance-only ESG analysis.
"""

from typing import List
from .base_prompt import BasePromptBuilder


class GovernancePromptBuilder(BasePromptBuilder):
    """
    Builds prompts for governance ESG analysis.
    
    Focuses only on governance dimension:
    - Board Governance
    - Risk Management
    - Ethics & Compliance
    - Transparency & Disclosure
    """
    
    def build(self, chunk: List[str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """Build governance ESG analysis prompt."""
        chunk_text = "\n".join(chunk)
        
        return f"""You are an expert ESG analyst specializing in Governance (G) data extraction and categorization. 
Analyze the following text content chunk from the {year} Sustainability Report (chunk {chunk_num}/{total_chunks}) and extract ALL governance information. 

CRITICAL REQUIREMENTS:
1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS
2. Include board composition, risk management, and ethics metrics
3. Preserve exact numbers
4. Include year suffixes for metrics
5. Extract both current state and improvement targets

RESPOND WITH VALID JSON ONLY containing governance_comprehensive structure.

TEXT TO ANALYZE:
{chunk_text}

RESPOND WITH VALID JSON ONLY:"""

