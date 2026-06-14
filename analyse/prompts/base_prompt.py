"""
Base prompt builder interface and factory.

Provides abstract base for prompt builders and factory for creating them.
"""

from abc import ABC, abstractmethod
from typing import Dict, List
from pathlib import Path
from loguru import logger


class BasePromptBuilder(ABC):
    """
    Abstract base for prompt builders.
    
    Prompt builders construct prompts for LLM analysis by:
    1. Loading template files (requirements, rules, examples)
    2. Composing templates with chunk-specific content
    3. Ensuring all quality standards are maintained
    """
    
    def __init__(self, templates_dir: Path = None):
        """
        Initialize prompt builder.
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir or (Path(__file__).parent / "templates")
        self._load_templates()
    
    def _load_templates(self):
        """Load prompt templates from files."""
        try:
            self.requirements = self._load_template("requirements.txt")
            self.naming_rules = self._load_template("naming_rules.txt")
            self.unit_preservation = self._load_template("unit_preservation.txt")
            self.examples = self._load_template("examples.txt")
            logger.debug(f"Loaded templates from {self.templates_dir}")
        except Exception as e:
            logger.warning(f"Could not load some templates: {e}")
            # Set defaults if templates don't exist yet
            self.requirements = ""
            self.naming_rules = ""
            self.unit_preservation = ""
            self.examples = ""
    
    def _load_template(self, filename: str) -> str:
        """
        Load a template file.
        
        Args:
            filename: Template filename
        
        Returns:
            Template content
        """
        path = self.templates_dir / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        else:
            logger.debug(f"Template not found: {filename}")
            return ""
    
    @abstractmethod
    def build(self, chunk: List[str], chunk_num: int, total_chunks: int, year: str = "2024") -> str:
        """
        Build prompt for a text chunk.
        
        Args:
            chunk: List of text segments in this chunk
            chunk_num: Current chunk number (1-indexed)
            total_chunks: Total number of chunks
            year: Report year
        
        Returns:
            Complete prompt string
        """
        pass
    
    def get_system_message(self, analysis_type: str) -> str:
        """
        Get system message for LLM.
        
        Args:
            analysis_type: Type of analysis
        
        Returns:
            System message string
        """
        return f"You are an expert ESG analyst that only responds with comprehensive, detailed JSON categorizations of {analysis_type.lower()} data. Your response must be valid JSON only."


class PromptFactory:
    """
    Factory for creating prompt builders.
    
    Provides centralized access to different prompt builder types.
    """
    
    @staticmethod
    def get_prompt_builder(analysis_type: str) -> BasePromptBuilder:
        """
        Get appropriate prompt builder for analysis type.
        
        Args:
            analysis_type: Type of analysis ("comprehensive", "environmental", "social", "governance")
        
        Returns:
            Prompt builder instance
        """
        from .comprehensive_prompt import ComprehensivePromptBuilder
        from .environmental_prompt import EnvironmentalPromptBuilder
        from .social_prompt import SocialPromptBuilder
        from .governance_prompt import GovernancePromptBuilder
        
        builders = {
            "comprehensive": ComprehensivePromptBuilder,
            "environmental": EnvironmentalPromptBuilder,
            "social": SocialPromptBuilder,
            "governance": GovernancePromptBuilder
        }
        
        builder_class = builders.get(analysis_type.lower(), ComprehensivePromptBuilder)
        logger.debug(f"Created {builder_class.__name__} for {analysis_type} analysis")
        
        return builder_class()

