"""Pipeline orchestration for PDF extraction.

The pipeline module provides high-level extractors that compose all the modular components
into unified extraction workflows. It's organized in three levels:

1. PDFExtractor: Basic extraction using heuristic segmentation (no LLM)
2. LLMPDFExtractor: LLM-enhanced extraction with advanced segment analysis
3. ESGExtractor: ESG-specialized extraction with domain-specific analysis

Each extractor builds on the previous one, adding more sophisticated capabilities.
"""

from .extractor import PDFExtractor, LLMPDFExtractor, ESGExtractor, ExtractorConfig

__all__ = [
    'PDFExtractor',       # Basic extractor (no LLM)
    'LLMPDFExtractor',    # LLM-enhanced extractor
    'ESGExtractor',       # ESG-specialized extractor
    'ExtractorConfig',    # Configuration
]

