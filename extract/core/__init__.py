"""Core abstractions and configuration for PDF extraction."""

from .base import (
    BasePDFReader,
    BaseClassifier,
    BaseSegmenter,
    BaseExtractor,
    BaseESGAnalyzer,
    BaseValidator
)
from .config import (
    PDFReaderConfig,
    ChunkingConfig,
    ClassificationConfig,
    SegmentationConfig,
    ESGConfig,
    ValidationConfig,
    ExtractionConfig
)
from .models import (
    PageData,
    SegmentData,
    ProcessedPage,
    ExtractionResult,
    TextSegmentAnalysis,
    LLMAnalysisResponse,
    ESGAnalysisResult
)

__all__ = [
    # Base classes
    'BasePDFReader',
    'BaseClassifier',
    'BaseSegmenter',
    'BaseExtractor',
    'BaseESGAnalyzer',
    'BaseValidator',
    
    # Configuration
    'PDFReaderConfig',
    'ChunkingConfig',
    'ClassificationConfig',
    'SegmentationConfig',
    'ESGConfig',
    'ValidationConfig',
    'ExtractionConfig',
    
    # Models
    'PageData',
    'SegmentData',
    'ProcessedPage',
    'ExtractionResult',
    'TextSegmentAnalysis',
    'LLMAnalysisResponse',
    'ESGAnalysisResult',
]

