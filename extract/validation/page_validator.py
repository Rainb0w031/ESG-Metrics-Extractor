"""Page-level validation."""

from typing import Dict, List, Any
from ..core.base import BaseValidator


class PageValidator(BaseValidator):
    """Validates extracted pages for quality and completeness."""
    
    def __init__(self, min_page_chars: int = 50):
        """
        Initialize page validator.
        
        Args:
            min_page_chars: Minimum characters for valid page
        """
        self.min_page_chars = min_page_chars
        self.validation_results = []
    
    def validate(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single page.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            Validation result
        """
        page_num = page_data.get('page_number', 0)
        is_valid = True
        issues = []
        
        # Check for errors
        if page_data.get('error'):
            is_valid = False
            issues.append(f"Extraction error: {page_data['error']}")
        
        # Check for empty content
        if not page_data.get('text_segments'):
            is_valid = False
            issues.append("No text segments found")
        
        # Check text length
        original_text = page_data.get('original_text', '')
        if len(original_text) < self.min_page_chars:
            is_valid = False
            issues.append(f"Insufficient text content ({len(original_text)} chars < {self.min_page_chars})")
        
        result = {
            'page_number': page_num,
            'is_valid': is_valid,
            'issues': issues,
            'char_count': len(original_text),
            'segment_count': len(page_data.get('text_segments', []))
        }
        
        self.validation_results.append(result)
        return result
    
    def validate_all(self, structured_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Validate all pages in structured content.
        
        Args:
            structured_content: Structured PDF content
            
        Returns:
            List of validation results
        """
        self.validation_results = []
        
        for page in structured_content.get('pages', []):
            self.validate(page)
        
        return self.validation_results
    
    def get_failed_pages(self) -> List[int]:
        """Get list of page numbers that failed validation."""
        return [r['page_number'] for r in self.validation_results if not r['is_valid']]
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Get comprehensive validation report.
        
        Returns:
            Validation report dictionary
        """
        if not self.validation_results:
            return {'error': 'No validation results available'}
        
        failed_pages = self.get_failed_pages()
        
        return {
            'total_pages': len(self.validation_results),
            'valid_pages': len([r for r in self.validation_results if r['is_valid']]),
            'failed_pages': failed_pages,
            'validation_rate': (len(self.validation_results) - len(failed_pages)) / len(self.validation_results),
            'issues_summary': self._summarize_issues()
        }
    
    def _summarize_issues(self) -> Dict[str, int]:
        """Summarize common issues across all validations."""
        issue_counts = {}
        
        for result in self.validation_results:
            for issue in result['issues']:
                # Extract issue type
                issue_type = issue.split(':')[0] if ':' in issue else issue
                issue_counts[issue_type] = issue_counts.get(issue_type, 0) + 1
        
        return issue_counts

