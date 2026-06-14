"""
Configuration classes for ESG analysis.

Standalone configuration that doesn't require external dependencies.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


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
    
    # Adaptive chunking specific
    base_chunk_size_adaptive: int = 35
    """Base chunk size for adaptive chunking"""
    
    high_complexity_chunk_size: int = 20
    """Chunk size for high complexity segments"""
    
    medium_complexity_chunk_size: int = 25
    """Chunk size for medium complexity segments"""
    
    max_chunks_to_merge: int = 50
    """Threshold for merging small chunks"""
    
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

