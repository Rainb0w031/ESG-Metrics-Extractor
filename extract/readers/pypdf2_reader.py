"""PyPDF2-based PDF reader implementation."""

from pathlib import Path
from typing import Dict, List, Any
import PyPDF2
from .base_reader import PDFReaderBase


class PyPDF2Reader(PDFReaderBase):
    """PDF reader using PyPDF2 library."""
    
    def get_method_name(self) -> str:
        """Get the name of this reading method."""
        return 'pypdf2'
    
    def read(self, file_path: Path) -> Dict[str, Any]:
        """
        Read PDF using PyPDF2.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with pages, metadata, success status
        """
        pages = []
        metadata = {}
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                if self.extract_metadata and pdf_reader.metadata:
                    metadata = self._create_metadata({
                        'Title': pdf_reader.metadata.get('/Title', ''),
                        'Author': pdf_reader.metadata.get('/Author', ''),
                        'Subject': pdf_reader.metadata.get('/Subject', ''),
                        'Creator': pdf_reader.metadata.get('/Creator', ''),
                        'Producer': pdf_reader.metadata.get('/Producer', ''),
                    }, len(pdf_reader.pages))
                else:
                    metadata = {'num_pages': len(pdf_reader.pages)}
                
                # Extract text from each page
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        text = page.extract_text()
                        pages.append(self._create_page_data(
                            page_number=page_num,
                            text=text,
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
                error=f"PyPDF2 extraction failed: {str(e)}"
            )

