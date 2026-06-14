"""LLM-based text analysis module.

This module provides LLM-based text role analysis matching the reference
implementation's analyze_text_roles_with_llm() functionality.
"""

from .role_analyzer import LLMRoleAnalyzer, LLMAnalysisConfig
from .prompts import create_chunk_prompt, create_page_analysis_prompt

__all__ = [
    'LLMRoleAnalyzer',
    'LLMAnalysisConfig',
    'create_chunk_prompt',
    'create_page_analysis_prompt',
]
