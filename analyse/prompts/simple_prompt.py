"""
Simplified ESG analysis prompt builder.

Maintains quality while being concise enough for reliable JSON output.
Key simplifications:
- Flat JSON structure (not deeply nested)
- 6 core rules instead of 27
- ~400 tokens instead of 2000+
- Still does full E/S/G categorization
"""

from typing import List, Union
from .base_prompt import BasePromptBuilder


class SimplePromptBuilder(BasePromptBuilder):
    """
    Simplified prompt builder for reliable JSON extraction.
    
    Design principles:
    - Short, focused prompt = reliable JSON output
    - Essential rules only (unit preservation, completeness)
    - Flat structure = easier for LLM to generate
    - Still extracts comprehensive ESG data
    """
    
    def build(self, chunk: Union[List[str], str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """
        Build simplified ESG analysis prompt.
        
        Args:
            chunk: Text content (list of segments or string)
            chunk_num: Current chunk number
            total_chunks: Total chunks
            year: Report year
        
        Returns:
            Complete prompt string
        """
        if isinstance(chunk, list):
            chunk_text = "\n".join(chunk)
        else:
            chunk_text = chunk
        
        return f"""Extract ESG metrics from this {year} sustainability report text (chunk {chunk_num}/{total_chunks}).

RULES:
1. Extract EVERY number, percentage, and metric you find
2. Preserve exact units - never convert (e.g., "million tons" stays "million tons")
3. Include year in metric names (e.g., "carbon_emissions_2024")
4. Categorize each metric as Environmental (E), Social (S), or Governance (G)
5. Include relevant text snippets as context in details
6. Return ONLY valid JSON, no other text

OUTPUT FORMAT:
{{
  "environmental": {{
    "metrics": {{
      "scope_1_emissions_2024": "717,096 tons",
      "renewable_energy_percentage_2024": "85%"
    }},
    "details": ["Original text snippet about emissions...", "Another relevant snippet..."]
  }},
  "social": {{
    "metrics": {{
      "employee_count_2024": "1.5 million",
      "diversity_percentage_2024": "45%"
    }},
    "details": ["Text about employees...", "Text about diversity..."]
  }},
  "governance": {{
    "metrics": {{
      "board_independence_2024": "80%"
    }},
    "details": ["Text about board governance..."]
  }}
}}

CATEGORIZATION GUIDE:
- Environmental (E): emissions, carbon, energy, water, waste, climate, renewable, recycling, biodiversity
- Social (S): employees, diversity, safety, health, community, training, human rights, labor, benefits
- Governance (G): board, compliance, ethics, risk, audit, transparency, executive, shareholders

TEXT TO ANALYZE:
{chunk_text}

JSON:"""


class SimpleComprehensivePromptBuilder(BasePromptBuilder):
    """
    Balanced prompt - more detail than Simple but less than full Comprehensive.
    
    Use this when you need more structured output but still want reliability.
    """
    
    def build(self, chunk: Union[List[str], str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """Build balanced ESG analysis prompt."""
        if isinstance(chunk, list):
            chunk_text = "\n".join(chunk)
        else:
            chunk_text = chunk
        
        return f"""You are an ESG analyst extracting data from a {year} sustainability report (chunk {chunk_num}/{total_chunks}).

CRITICAL RULES:
1. Extract ALL numbers, percentages, metrics, goals, and targets
2. PRESERVE EXACT UNITS - never convert:
   - "million tons" stays "million tons" (not "tons")
   - "gigatons" stays "gigatons" (not "tons")  
   - "tons per million RMB" stays exactly as written
3. Include year suffix in metric names: "emissions_2024", "target_2030"
4. Extract both current values AND future targets/goals
5. Include original text snippets as supporting details
6. Return ONLY valid JSON - no markdown, no explanations

OUTPUT STRUCTURE:
{{
  "environmental": {{
    "emissions": {{
      "metrics": {{"scope_1_2024": "value", "scope_2_2024": "value", "scope_3_2024": "value"}},
      "details": ["relevant text..."]
    }},
    "energy": {{
      "metrics": {{"renewable_percentage_2024": "value"}},
      "details": ["relevant text..."]
    }},
    "water": {{"metrics": {{}}, "details": []}},
    "waste": {{"metrics": {{}}, "details": []}},
    "other": {{"metrics": {{}}, "details": []}}
  }},
  "social": {{
    "workforce": {{"metrics": {{}}, "details": []}},
    "diversity": {{"metrics": {{}}, "details": []}},
    "safety": {{"metrics": {{}}, "details": []}},
    "community": {{"metrics": {{}}, "details": []}},
    "other": {{"metrics": {{}}, "details": []}}
  }},
  "governance": {{
    "board": {{"metrics": {{}}, "details": []}},
    "ethics": {{"metrics": {{}}, "details": []}},
    "risk": {{"metrics": {{}}, "details": []}},
    "other": {{"metrics": {{}}, "details": []}}
  }}
}}

EXAMPLES:
- "reduced emissions by 15% to 51 million tons" → {{"emissions_reduction_2024": "15%", "total_emissions_2024": "51 million tons"}}
- "goal: net zero by 2040" → {{"net_zero_target_year": "2040"}}
- "1.5 million employees globally" → {{"employee_count_2024": "1.5 million"}}

TEXT:
{chunk_text}

JSON:"""
