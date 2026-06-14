"""
Base classes and interfaces for ESG analysis.

This module provides abstract base classes and configuration for all analyzers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from prompter.prompt import BasePromptModel


@dataclass
class AnalysisConfig:
    """
    Configuration for analysis operations.
    
    Based on quality standards from quantitative_llm_analysis_clean_fixed.py:
    - chunk_size: 40-60 segments for optimal processing
    - No chunk limits: Process all content
    - Conservative temperature: 0.2 for consistency
    - Generous timeouts: 120s per request
    """
    
    # Chunking configuration
    chunk_size: int = 60
    """Base chunk size (segments per chunk)"""
    
    max_chunks_per_analysis: Optional[int] = None
    """Maximum chunks to process (None = no limit)"""
    
    min_chunk_size: int = 20
    """Minimum chunk size for adaptive chunking"""
    
    max_chunk_size: int = 80
    """Maximum chunk size for adaptive chunking"""
    
    # Processing configuration
    batch_delay: float = 1.0
    """Delay between batches (seconds)"""
    
    max_retries: int = 3
    """Maximum retry attempts for failed requests"""
    
    retry_delay: float = 2.0
    """Delay between retries (seconds)"""
    
    timeout: int = 120
    """Request timeout (seconds)"""
    
    # LLM configuration
    temperature: float = 0.2
    """LLM temperature (0.0-1.0, lower = more deterministic)"""
    
    max_tokens: int = 4096
    """Maximum tokens in LLM response"""
    
    # Quality configuration
    enable_adaptive_chunking: bool = True
    """Enable adaptive chunking based on content complexity"""
    
    enable_duplicate_detection: bool = True
    """Enable duplicate detection during merging"""
    
    enable_validation: bool = True
    """Enable result validation"""
    
    # ESG categories
    esg_categories: Dict[str, list] = field(default_factory=lambda: {
        'environmental': [
            'carbon_emissions', 'renewable_energy', 'water_management', 
            'waste_management', 'biodiversity', 'climate_change', 
            'energy_efficiency', 'sustainable_materials'
        ],
        'social': [
            'employee_health_safety', 'diversity_inclusion', 'community_engagement',
            'human_rights', 'supply_chain_responsibility', 'product_safety',
            'data_privacy', 'labor_practices'
        ],
        'governance': [
            'board_diversity', 'executive_compensation', 'risk_management',
            'compliance', 'transparency', 'stakeholder_engagement',
            'ethics', 'corporate_structure'
        ]
    })
    
    def __post_init__(self):
        """Validate configuration values."""
        if self.chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        if self.min_chunk_size > self.max_chunk_size:
            raise ValueError("min_chunk_size cannot exceed max_chunk_size")
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")


class BaseAnalyzer(BasePromptModel, ABC):
    """
    Abstract base for all ESG analyzers.
    
    Inherits from prompter's BasePromptModel to leverage:
    - LLM interaction capabilities (.chat() method)
    - Configuration management
    - Logging infrastructure
    
    Subclasses must implement:
    - analyze(): Main analysis method
    - get_analysis_type(): Return analysis type identifier
    """
    
    def __init__(self, 
                 which_model: str = None, 
                 system_prompt: str = None,
                 config: AnalysisConfig = None):
        """
        Initialize base analyzer.
        
        Args:
            which_model: LLM model to use (from prompter config)
            system_prompt: System prompt for LLM
            config: Analysis configuration (defaults to AnalysisConfig())
        """
        super().__init__(which_model=which_model, system_prompt=system_prompt)
        self.config = config or AnalysisConfig()
    
    @abstractmethod
    def analyze(self, structured_content: Dict[str, Any], 
                analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze structured content and return results.
        
        Args:
            structured_content: Structured content from PDF extraction
            analysis_type: Type of analysis to perform
                         ("comprehensive", "environmental", "social", "governance")
        
        Returns:
            Dict containing analysis results with structure:
                {
                    "analysis_type": str,
                    "timestamp": str,
                    "year": str,
                    "environmental_comprehensive_analysis": {...},
                    "social_comprehensive_analysis": {...},
                    "governance_comprehensive_analysis": {...},
                    "analysis_metadata": {...}
                }
        """
        pass
    
    @abstractmethod
    def get_analysis_type(self) -> str:
        """
        Return the type of analysis this analyzer performs.
        
        Returns:
            Analysis type string ("comprehensive", "environmental", etc.)
        """
        pass
    
    def _get_default_system_prompt(self) -> str:
        """
        Get default system prompt for ESG analysis.
        
        Can be overridden by subclasses for specialized prompts.
        
        Returns:
            System prompt string
        """
        return """You are an expert ESG (Environmental, Social, and Governance) analyst with deep expertise in:
- Quantitative metrics extraction and analysis
- ESG reporting standards and frameworks
- Corporate sustainability assessment
- Data quality and validation

Your task is to provide comprehensive, accurate, and detailed ESG analysis with:
- Precise quantitative metrics extraction
- Proper categorization of ESG topics
- High confidence scores based on data quality
- Detailed context and explanations
- Structured JSON output following specified schemas

Always prioritize accuracy and completeness over speed."""


class AnalysisStrategy(ABC):
    """
    Abstract base for analysis strategies.
    
    Strategy pattern for different analysis approaches:
    - Comprehensive analysis
    - Environmental-only analysis
    - Social-only analysis
    - Governance-only analysis
    """
    
    @abstractmethod
    def execute(self, text_content: Any, config: AnalysisConfig) -> Dict[str, Any]:
        """Execute the analysis strategy."""
        pass

