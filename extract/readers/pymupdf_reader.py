"""PyMuPDF (fitz) based PDF reader implementation."""

from pathlib import Path
from typing import Dict, List, Any
import fitz  # PyMuPDF
from .base_reader import PDFReaderBase


class PyMuPDFReader(PDFReaderBase):
    """PDF reader using PyMuPDF (fitz) library."""
    
    def get_method_name(self) -> str:
        """Get the name of this reading method."""
        return 'pymupdf'
    
    def read(self, file_path: Path) -> Dict[str, Any]:
        """
        Read PDF using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with pages, metadata, success status
        """
        pages = []
        metadata = {}
        
        try:
            doc = fitz.open(file_path)
            
            # Extract metadata
            if self.extract_metadata:
                raw_metadata = doc.metadata
                metadata = self._create_metadata(raw_metadata, len(doc))
            else:
                metadata = {'num_pages': len(doc)}
            
            # Extract text from each page
            for page_num in range(len(doc)):
                try:
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    pages.append(self._create_page_data(
                        page_number=page_num + 1,
                        text=text,
                        method=self.get_method_name()
                    ))
                except Exception as e:
                    pages.append(self._create_page_data(
                        page_number=page_num + 1,
                        text='',
                        method=self.get_method_name(),
                        error=f"Page extraction failed: {str(e)}"
                    ))
            
            doc.close()
            return self._create_result(pages, metadata, success=True)
            
        except Exception as e:
            return self._create_result(
                pages=[],
                metadata={},
                success=False,
                error=f"PyMuPDF extraction failed: {str(e)}"
            )

