"""
Environmental ESG analysis prompt builder.

Builds prompts for environmental-only ESG analysis.
Extracted from ESGLLMAnalyzer._create_environmental_analysis_prompt().
"""

from typing import List
from .base_prompt import BasePromptBuilder


class EnvironmentalPromptBuilder(BasePromptBuilder):
    """
    Builds prompts for environmental ESG analysis.
    
    Focuses only on environmental dimension:
    - Emissions (Scope 1, 2, 3, 3+)
    - Energy
    - Water
    - Waste
    - Transportation
    - Buildings
    - Supply chain
    - Climate pledge
    - Biodiversity
    """
    
    def build(self, chunk: List[str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """
        Build environmental ESG analysis prompt.
        
        Args:
            chunk: List of text segments
            chunk_num: Current chunk number
            total_chunks: Total chunks
            year: Report year
        
        Returns:
            Complete prompt string
        """
        chunk_text = "\n".join(chunk)
        
        return f"""You are an expert ESG analyst specializing in Environmental (E) data extraction and categorization. 
Analyze the following text content chunk from the {year} Sustainability Report (chunk {chunk_num}/{total_chunks}) and extract ALL environmental information. 
Provide a comprehensive, detailed categorization of environmental data including both quantitative metrics and qualitative information.

CRITICAL REQUIREMENTS:
1. EXTRACT ALL NUMBERS, PERCENTAGES, AND SPECIFIC METRICS from the text
2. Populate 'metrics' objects with actual numerical values
3. Preserve exact numbers and units as mentioned in the text
4. CRITICAL: DO NOT CONVERT UNITS - preserve original units exactly
5. CRITICAL: Preserve compound units exactly (e.g., 'tons per million RMB')
6. Extract all emissions, energy, water, waste, and transportation metrics
7. Include year suffixes for all metrics (e.g., '_2024')
8. Distinguish between Scope 3 and Scope 3+ emissions

RESPOND WITH VALID JSON ONLY containing environmental_comprehensive structure.

TEXT TO ANALYZE:
{chunk_text}

RESPOND WITH VALID JSON ONLY:"""

