"""Configuration classes for PDF extraction."""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class PDFReaderConfig:
    """Configuration for PDF reading."""
    preferred_method: str = 'auto'  # 'auto', 'pypdf2', 'pymupdf', 'pdfplumber'
    fallback_methods: List[str] = field(default_factory=lambda: ['pymupdf', 'pdfplumber', 'pypdf2'])
    extract_metadata: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        valid_methods = {'auto', 'pypdf2', 'pymupdf', 'pdfplumber'}
        if self.preferred_method not in valid_methods:
            raise ValueError(f"Invalid preferred_method: {self.preferred_method}. Must be one of {valid_methods}")


@dataclass
class ChunkingConfig:
    """Configuration for text chunking."""
    chunk_size: int = 512  # Maximum tokens per chunk
    min_length: int = 32   # Minimum chunk length
    overlap: int = 0       # Overlap between chunks
    tokenizer_model: str = 'cl100k_base'  # Tokenizer to use
    
    def __post_init__(self):
        """Validate configuration."""
        if self.chunk_size < self.min_length:
            raise ValueError(f"chunk_size ({self.chunk_size}) must be >= min_length ({self.min_length})")
        if self.overlap < 0:
            raise ValueError(f"overlap must be >= 0, got {self.overlap}")


@dataclass
class ClassificationConfig:
    """Configuration for text classification."""
    confidence_threshold: float = 0.6
    use_advanced_heuristics: bool = True
    custom_role_patterns: Dict[str, List[str]] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration."""
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(f"confidence_threshold must be between 0.0 and 1.0, got {self.confidence_threshold}")


@dataclass
class SegmentationConfig:
    """Configuration for segmentation."""
    use_llm_enhancement: bool = False
    batch_size: int = 5
    batch_delay: float = 1.0  # seconds
    enable_caching: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if self.batch_size < 1:
            raise ValueError(f"batch_size must be >= 1, got {self.batch_size}")
        if self.batch_delay < 0:
            raise ValueError(f"batch_delay must be >= 0, got {self.batch_delay}")


@dataclass
class ESGConfig:
    """Configuration for ESG analysis."""
    enable_esg_analysis: bool = True
    extract_metrics: bool = True
    calculate_statistics: bool = True
    enhance_importance: bool = True
    custom_keywords: Dict[str, List[str]] = field(default_factory=dict)
    
    # ESG categories to analyze
    categories: List[str] = field(default_factory=lambda: ['environmental', 'social', 'governance'])


@dataclass
class ValidationConfig:
    """Configuration for validation."""
    min_page_chars: int = 50
    min_segment_chars: int = 10
    enable_auto_retry: bool = True
    max_retry_attempts: int = 3
    
    def __post_init__(self):
        """Validate configuration."""
        if self.min_page_chars < 0:
            raise ValueError(f"min_page_chars must be >= 0, got {self.min_page_chars}")
        if self.min_segment_chars < 0:
            raise ValueError(f"min_segment_chars must be >= 0, got {self.min_segment_chars}")


@dataclass
class ExtractionConfig:
    """Main configuration for PDF extraction pipeline."""
    pdf_reader: PDFReaderConfig = field(default_factory=PDFReaderConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    classification: ClassificationConfig = field(default_factory=ClassificationConfig)
    segmentation: SegmentationConfig = field(default_factory=SegmentationConfig)
    esg: ESGConfig = field(default_factory=ESGConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    
    # LLM configuration (if using LLM enhancement)
    llm_model: str = 'dashscope+qwen-max'
    llm_temperature: float = 0.2
    llm_max_tokens: int = 4096
    llm_timeout: int = 120
    
    # Output configuration
    output_format: str = 'json'  # 'json', 'jsonl'
    include_original_text: bool = True
    include_metadata: bool = True
    
    def __post_init__(self):
        """Validate configuration."""
        if not 0.0 <= self.llm_temperature <= 2.0:
            raise ValueError(f"llm_temperature must be between 0.0 and 2.0, got {self.llm_temperature}")
        if self.llm_max_tokens < 1:
            raise ValueError(f"llm_max_tokens must be >= 1, got {self.llm_max_tokens}")
        if self.output_format not in {'json', 'jsonl'}:
            raise ValueError(f"output_format must be 'json' or 'jsonl', got {self.output_format}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'pdf_reader': {
                'preferred_method': self.pdf_reader.preferred_method,
                'fallback_methods': self.pdf_reader.fallback_methods,
                'extract_metadata': self.pdf_reader.extract_metadata
            },
            'chunking': {
                'chunk_size': self.chunking.chunk_size,
                'min_length': self.chunking.min_length,
                'overlap': self.chunking.overlap,
                'tokenizer_model': self.chunking.tokenizer_model
            },
            'classification': {
                'confidence_threshold': self.classification.confidence_threshold,
                'use_advanced_heuristics': self.classification.use_advanced_heuristics
            },
            'segmentation': {
                'use_llm_enhancement': self.segmentation.use_llm_enhancement,
                'batch_size': self.segmentation.batch_size,
                'batch_delay': self.segmentation.batch_delay
            },
            'esg': {
                'enable_esg_analysis': self.esg.enable_esg_analysis,
                'extract_metrics': self.esg.extract_metrics,
                'categories': self.esg.categories
            },
            'validation': {
                'min_page_chars': self.validation.min_page_chars,
                'enable_auto_retry': self.validation.enable_auto_retry
            },
            'llm': {
                'model': self.llm_model,
                'temperature': self.llm_temperature,
                'max_tokens': self.llm_max_tokens
            },
            'output': {
                'format': self.output_format,
                'include_original_text': self.include_original_text,
                'include_metadata': self.include_metadata
            }
        }

