"""Pydantic models for PDF extraction."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PageData(BaseModel):
    """Model for extracted page data."""
    page_number: int = Field(description="Page number in the document")
    text: str = Field(description="Raw extracted text from the page")
    extraction_method: str = Field(description="Method used to extract text")
    error: Optional[str] = Field(default=None, description="Error message if extraction failed")


class SegmentData(BaseModel):
    """Model for a text segment."""
    segment_id: str = Field(description="Unique segment identifier")
    text: str = Field(description="Segment text content")
    role: str = Field(description="Text role classification")
    chunk_index: int = Field(description="Index of this chunk in the page")
    confidence: float = Field(ge=0.0, le=1.0, description="Classification confidence")
    position: str = Field(description="Position in document: start|middle|end")
    importance: str = Field(description="Importance level: high|medium|low")
    context: str = Field(description="Context description")
    
    # Optional ESG-specific fields
    esg_categories: Optional[List[str]] = Field(default=None, description="ESG categories")
    esg_metrics: Optional[List[str]] = Field(default=None, description="ESG metrics found")
    esg_keywords: Optional[List[str]] = Field(default=None, description="ESG keywords found")
    primary_esg_focus: Optional[str] = Field(default=None, description="Primary ESG focus")
    esg_relevance_score: Optional[float] = Field(default=None, description="ESG relevance score")


class ProcessedPage(BaseModel):
    """Model for a processed page with segments."""
    page_number: int = Field(description="Page number")
    text_segments: List[Dict[str, Any]] = Field(description="List of text segments")
    original_text: str = Field(description="Original page text")
    num_segments: int = Field(description="Number of segments")
    page_summary: Optional[str] = Field(default=None, description="Page summary")
    main_topics: Optional[List[str]] = Field(default=None, description="Main topics")
    document_section: Optional[str] = Field(default=None, description="Document section")
    char_count: Optional[int] = Field(default=None, description="Character count")
    word_count: Optional[int] = Field(default=None, description="Word count")
    error: Optional[str] = Field(default=None, description="Error message if any")
    fixed_with_method: Optional[str] = Field(default=None, description="Method used to fix failed page")


class ExtractionResult(BaseModel):
    """Model for complete extraction result."""
    metadata: Dict[str, Any] = Field(description="PDF metadata")
    pages: List[Dict[str, Any]] = Field(description="Processed pages")
    extraction_timestamp: str = Field(description="Timestamp of extraction")
    extraction_method: str = Field(description="Primary extraction method used")
    validation: Optional[Dict[str, Any]] = Field(default=None, description="Validation results")
    processing: Optional[Dict[str, Any]] = Field(default=None, description="Processing configuration")
    esg_analysis: Optional[Dict[str, Any]] = Field(default=None, description="ESG-specific analysis")


class TextSegmentAnalysis(BaseModel):
    """Pydantic model for LLM text segment analysis response."""
    text: str = Field(description="The analyzed text content")
    role: str = Field(description="Text role: headline|subheadline|content|caption|footnote|list_item|table_content|metadata|quote|executive_summary|methodology|results|conclusion|appendix")
    confidence: float = Field(description="Confidence score 0.0-1.0", ge=0.0, le=1.0)
    position: str = Field(description="Position in document: start|middle|end")
    importance: str = Field(description="Importance level: high|medium|low")
    context: str = Field(description="Brief description of what this text represents")


class LLMAnalysisResponse(BaseModel):
    """Pydantic model for complete LLM analysis response."""
    text_segments: List[Dict[str, Any]] = Field(description="List of analyzed text segments")
    main_topics: List[str] = Field(description="Main topics identified in the text")
    esg_metrics: Optional[List[str]] = Field(default=None, description="List of ESG metrics identified")


class ESGAnalysisResult(BaseModel):
    """Model for ESG-specific analysis results."""
    esg_categories: List[str] = Field(description="ESG categories found")
    esg_metrics: List[str] = Field(description="ESG metrics identified")
    esg_keywords: List[str] = Field(description="ESG keywords found")
    primary_esg_focus: Optional[str] = Field(default=None, description="Primary ESG focus area")
    esg_relevance_score: float = Field(description="ESG relevance score", ge=0.0, le=1.0)

