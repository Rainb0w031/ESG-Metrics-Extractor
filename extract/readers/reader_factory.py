"""Factory for creating PDF readers."""

from pathlib import Path
from typing import Dict, List, Any, Optional
from ..core.base import BasePDFReader
from ..core.config import PDFReaderConfig
from .pypdf2_reader import PyPDF2Reader
from .pymupdf_reader import PyMuPDFReader
from .pdfplumber_reader import PdfplumberReader


class PDFReaderFactory:
    """Factory for creating and managing PDF readers."""
    
    # Registry of available readers
    _readers = {
        'pypdf2': PyPDF2Reader,
        'pymupdf': PyMuPDFReader,
        'pdfplumber': PdfplumberReader
    }
    
    @classmethod
    def create_reader(cls, method: str, extract_metadata: bool = True) -> BasePDFReader:
        """
        Create a PDF reader for the specified method.
        
        Args:
            method: Reader method ('pypdf2', 'pymupdf', 'pdfplumber')
            extract_metadata: Whether to extract metadata
            
        Returns:
            PDF reader instance
            
        Raises:
            ValueError: If method is not recognized
        """
        method = method.lower()
        if method not in cls._readers:
            raise ValueError(
                f"Unknown reader method: {method}. "
                f"Available methods: {list(cls._readers.keys())}"
            )
        
        reader_class = cls._readers[method]
        return reader_class(extract_metadata=extract_metadata)
    
    @classmethod
    def read_with_fallback(cls, file_path: Path, config: PDFReaderConfig) -> Dict[str, Any]:
        """
        Read PDF with automatic fallback to other methods if primary fails.
        
        Args:
            file_path: Path to PDF file
            config: PDF reader configuration
            
        Returns:
            Dictionary with extraction results
        """
        # Determine methods to try
        if config.preferred_method == 'auto':
            methods = config.fallback_methods
        else:
            methods = [config.preferred_method] + [
                m for m in config.fallback_methods 
                if m != config.preferred_method
            ]
        
        last_error = None
        
        # Try each method in order
        for method in methods:
            try:
                reader = cls.create_reader(method, config.extract_metadata)
                result = reader.read(file_path)
                
                if result['success']:
                    print(f"[OK] Text extraction successful using {method}")
                    return result
                else:
                    last_error = result.get('error', 'Unknown error')
                    print(f"[WARN] {method} extraction failed: {last_error}")
                    
            except Exception as e:
                last_error = str(e)
                print(f"[WARN] {method} extraction failed: {e}")
                continue
        
        # All methods failed
        return {
            'pages': [],
            'metadata': {},
            'extraction_method': 'failed',
            'success': False,
            'error': f"All extraction methods failed. Last error: {last_error}"
        }
    
    @classmethod
    def get_available_methods(cls) -> List[str]:
        """Get list of available reader methods."""
        return list(cls._readers.keys())
    
    @classmethod
    def register_reader(cls, method: str, reader_class: type):
        """
        Register a custom PDF reader.
        
        Args:
            method: Method name
            reader_class: Reader class (must inherit from BasePDFReader)
        """
        if not issubclass(reader_class, BasePDFReader):
            raise TypeError(f"{reader_class} must inherit from BasePDFReader")
        
        cls._readers[method.lower()] = reader_class
        print(f"[OK] Registered custom reader: {method}")

