"""pdfplumber-based PDF reader implementation."""

from pathlib import Path
from typing import Dict, List, Any
import pdfplumber
from .base_reader import PDFReaderBase


class PdfplumberReader(PDFReaderBase):
    """PDF reader using pdfplumber library."""
    
    def get_method_name(self) -> str:
        """Get the name of this reading method."""
        return 'pdfplumber'
    
    def read(self, file_path: Path) -> Dict[str, Any]:
        """
        Read PDF using pdfplumber.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with pages, metadata, success status
        """
        pages = []
        metadata = {}
        
        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                if self.extract_metadata and pdf.metadata:
                    metadata = self._create_metadata(pdf.metadata, len(pdf.pages))
                else:
                    metadata = {'num_pages': len(pdf.pages) if hasattr(pdf, 'pages') else 0}
                
                # Extract text from each page
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        pages.append(self._create_page_data(
                            page_number=page_num,
                            text=text or '',
                            method=self.get_method_name()
                        ))
                    except Exception as e:
                        pages.append(self._create_page_data(
                            page_number=page_num,
                            text='',
                            method=self.get_method_name(),
                            error=f"Page extraction failed: {str(e)}"
                        ))
            
            return self._create_result(pages, metadata, success=True)
            
        except Exception as e:
            return self._create_result(
                pages=[],
                metadata={},
                success=False,
                error=f"pdfplumber extraction failed: {str(e)}"
            )

