"""Abstract base classes for PDF extraction."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional
from .models import PageData, SegmentData, ExtractionResult
from .config import ExtractionConfig


class BasePDFReader(ABC):
    """Abstract base class for PDF readers."""
    
    @abstractmethod
    def read(self, file_path: Path) -> Dict[str, Any]:
        """
        Read PDF and extract text.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with:
                - pages: List of PageData objects
                - metadata: PDF metadata
                - success: bool
                - error: Optional error message
        """
        pass
    
    @abstractmethod
    def get_method_name(self) -> str:
        """Get the name of this reading method."""
        pass


class BaseClassifier(ABC):
    """Abstract base class for text classification."""
    
    @abstractmethod
    def classify_role(self, text: str) -> str:
        """
        Classify the role of a text segment.
        
        Args:
            text: Text to classify
            
        Returns:
            Role string (e.g., 'headline', 'content', etc.)
        """
        pass
    
    @abstractmethod
    def analyze_importance(self, text: str, role: str, position: str) -> str:
        """
        Analyze the importance of a text segment.
        
        Args:
            text: Text content
            role: Text role
            position: Position in document
            
        Returns:
            Importance level ('high', 'medium', 'low')
        """
        pass


class BaseSegmenter(ABC):
    """Abstract base class for segment creation."""
    
    @abstractmethod
    def create_segment(self, text: str, page_num: int, segment_num: int, 
                      total_segments: int) -> Dict[str, Any]:
        """
        Create a segment from text.
        
        Args:
            text: Text content
            page_num: Page number
            segment_num: Segment number on the page
            total_segments: Total segments on the page
            
        Returns:
            Segment dictionary
        """
        pass


class BaseExtractor(ABC):
    """Abstract base class for PDF extractors."""
    
    def __init__(self, config: Optional[ExtractionConfig] = None):
        """
        Initialize extractor.
        
        Args:
            config: Extraction configuration
        """
        self.config = config or ExtractionConfig()
    
    @abstractmethod
    def extract(self, pdf_path: Path, output_path: Optional[Path] = None) -> ExtractionResult:
        """
        Extract content from PDF.
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional output path for results
            
        Returns:
            ExtractionResult object
        """
        pass
    
    @abstractmethod
    def extract_text(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract raw text from PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text data
        """
        pass
    
    @abstractmethod
    def process_pages(self, text_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process extracted text into structured segments.
        
        Args:
            text_data: Raw extracted text data
            
        Returns:
            List of processed pages
        """
        pass
    
    def validate_extraction(self, result: ExtractionResult) -> Dict[str, Any]:
        """
        Validate extraction result.
        
        Args:
            result: Extraction result to validate
            
        Returns:
            Validation report
        """
        validation = {
            'total_pages': len(result.pages),
            'pages_with_content': sum(1 for page in result.pages 
                                     if page.get('text_segments')),
            'total_segments': sum(len(page.get('text_segments', [])) 
                                for page in result.pages),
            'is_valid': True,
            'issues': []
        }
        
        # Check for empty pages
        empty_pages = [page['page_number'] for page in result.pages 
                      if not page.get('text_segments')]
        if empty_pages:
            validation['issues'].append(f"Empty pages: {empty_pages}")
        
        # Check minimum content
        if validation['total_segments'] < 10:
            validation['issues'].append("Very few segments extracted")
            validation['is_valid'] = False
        
        return validation


class BaseESGAnalyzer(ABC):
    """Abstract base class for ESG analysis."""
    
    @abstractmethod
    def analyze_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze ESG content in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            ESG analysis results
        """
        pass
    
    @abstractmethod
    def extract_metrics(self, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract ESG metrics from structured content.
        
        Args:
            structured_content: Structured PDF content
            
        Returns:
            ESG metrics
        """
        pass


class BaseValidator(ABC):
    """Abstract base class for validation."""
    
    @abstractmethod
    def validate(self, data: Any) -> Dict[str, Any]:
        """
        Validate data.
        
        Args:
            data: Data to validate
            
        Returns:
            Validation result
        """
        pass
    
    @abstractmethod
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Get comprehensive validation report.
        
        Returns:
            Validation report
        """
        pass

