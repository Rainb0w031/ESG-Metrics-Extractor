"""Abstract base class for PDF readers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any
from ..core.base import BasePDFReader
from ..core.models import PageData


class PDFReaderBase(BasePDFReader):
    """Base implementation with common utilities."""
    
    def __init__(self, extract_metadata: bool = True):
        """
        Initialize PDF reader.
        
        Args:
            extract_metadata: Whether to extract PDF metadata
        """
        self.extract_metadata = extract_metadata
    
    def _create_page_data(self, page_number: int, text: str, method: str, 
                         error: str = None) -> Dict[str, Any]:
        """
        Create standardized page data dictionary.
        
        Args:
            page_number: Page number
            text: Extracted text
            method: Extraction method
            error: Optional error message
            
        Returns:
            Page data dictionary
        """
        return {
            'page_number': page_number,
            'text': text,
            'extraction_method': method,
            'error': error
        }
    
    def _create_metadata(self, raw_metadata: Dict[str, Any], num_pages: int) -> Dict[str, Any]:
        """
        Create standardized metadata dictionary.
        
        Args:
            raw_metadata: Raw metadata from PDF
            num_pages: Number of pages
            
        Returns:
            Standardized metadata
        """
        return {
            'title': raw_metadata.get('title', raw_metadata.get('Title', '')),
            'author': raw_metadata.get('author', raw_metadata.get('Author', '')),
            'subject': raw_metadata.get('subject', raw_metadata.get('Subject', '')),
            'creator': raw_metadata.get('creator', raw_metadata.get('Creator', '')),
            'producer': raw_metadata.get('producer', raw_metadata.get('Producer', '')),
            'num_pages': num_pages
        }
    
    def _create_result(self, pages: List[Dict[str, Any]], metadata: Dict[str, Any], 
                      success: bool, error: str = None) -> Dict[str, Any]:
        """
        Create standardized result dictionary.
        
        Args:
            pages: List of page data
            metadata: PDF metadata
            success: Whether extraction succeeded
            error: Optional error message
            
        Returns:
            Result dictionary
        """
        return {
            'pages': pages,
            'metadata': metadata,
            'extraction_method': self.get_method_name(),
            'success': success,
            'error': error
        }

