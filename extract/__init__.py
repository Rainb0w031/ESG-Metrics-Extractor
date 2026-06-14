"""
PDF Extraction Package - Modular Architecture

This package provides a highly modular PDF extraction system with clear separation of concerns.

## Architecture Overview

```
extract/
├── core/          # Base classes, config, models
├── readers/       # PDF reading implementations (PyPDF2, PyMuPDF, pdfplumber)
├── classification/# Text role and importance classification (rule-based)
├── segmentation/  # Segment creation (basic and LLM-enhanced)
├── esg/           # ESG-specific analysis
├── validation/    # Content validation
├── api/           # Direct API client for LLM calls
├── chunking/      # Text chunking utilities
├── llm/           # LLM-based text analysis
└── pipeline/      # High-level extraction workflows (PDFExtractor, ESGExtractor)
```

## Quick Start

### Complete Extraction Pipeline (Recommended)
```python
from extract.pipeline import PDFExtractor, LLMPDFExtractor, ESGExtractor

# Basic extraction (no LLM)
extractor = PDFExtractor()
result = extractor.extract(pdf_path, output_path)

# LLM-enhanced extraction
extractor = LLMPDFExtractor()
result = extractor.extract(pdf_path, output_path)

# ESG-specialized extraction
extractor = ESGExtractor()
result = extractor.extract(pdf_path, output_path)
```

### Basic PDF Reading
```python
from extract.readers import PDFReaderFactory
from extract.core.config import PDFReaderConfig

config = PDFReaderConfig(preferred_method='auto')
result = PDFReaderFactory.read_with_fallback(pdf_path, config)
```

### Classification
```python
from extract.classification import RoleClassifier, ImportanceAnalyzer

classifier = RoleClassifier()
analyzer = ImportanceAnalyzer()

role = classifier.classify_role(text)
importance = analyzer.analyze_importance(text, role, position)
```

### ESG Analysis
```python
from extract.esg import ESGContentAnalyzer

esg_analyzer = ESGContentAnalyzer()
esg_data = esg_analyzer.analyze_content(text)
metrics = esg_analyzer.extract_metrics(structured_content)
```

### Direct API Calls (for custom LLM workflows)
```python
from extract.api import DirectAPIClient, APIConfig

config = APIConfig.from_env()
client = DirectAPIClient(config)
result = client.chat_json(messages)
```

## Benefits

1. **No Code Duplication**: Single source of truth for classification logic
2. **Easy Testing**: Each component can be tested independently  
3. **Extensibility**: Easy to add new readers, classifiers, or analyzers
4. **Clear Dependencies**: Well-defined interfaces between modules
5. **Maintainability**: Small, focused modules with single responsibilities
6. **Direct API Calls**: More control, no external dependencies beyond requests
7. **Complete Pipeline**: Orchestrators that match reference implementation

## Migration from Old Code

Old extractors (`base_extractor.py`, `prompt_extractor.py`, `esg_extractor.py`) 
remain available for backward compatibility. New code should use the modular structure.

See EXTRACT_MODULARIZATION_PLAN.md for complete documentation.
"""

# Core exports
from .core import (
    ExtractionConfig,
    PageData,
    SegmentData,
    ExtractionResult
)

# Reader exports
from .readers import PDFReaderFactory

# Classification exports
from .classification import RoleClassifier, ImportanceAnalyzer

# Segmentation exports
from .segmentation import BasicSegmenter

# ESG exports
from .esg import ESGContentAnalyzer, ESGStatisticsCalculator

# Validation exports
from .validation import PageValidator

# API exports
from .api import DirectAPIClient, APIConfig

# Chunking exports
from .chunking import TextChunker, ChunkConfig

# LLM exports
from .llm import LLMRoleAnalyzer, LLMAnalysisConfig

# Pipeline exports (orchestrators)
from .pipeline import PDFExtractor, LLMPDFExtractor, ESGExtractor, ExtractorConfig

__version__ = '2.0.0'

__all__ = [
    # Core
    'ExtractionConfig',
    'PageData',
    'SegmentData',
    'ExtractionResult',
    
    # Readers
    'PDFReaderFactory',
    
    # Classification
    'RoleClassifier',
    'ImportanceAnalyzer',
    
    # Segmentation
    'BasicSegmenter',
    
    # ESG
    'ESGContentAnalyzer',
    'ESGStatisticsCalculator',
    
    # Validation
    'PageValidator',
    
    # API
    'DirectAPIClient',
    'APIConfig',
    
    # Chunking
    'TextChunker',
    'ChunkConfig',
    
    # LLM
    'LLMRoleAnalyzer',
    'LLMAnalysisConfig',
    
    # Pipeline (Orchestrators)
    'PDFExtractor',
    'LLMPDFExtractor',
    'ESGExtractor',
    'ExtractorConfig',
]

