"""PDF Extraction Pipeline Orchestrator.

This module provides complete extraction pipelines that compose all the
modular components into unified workflows, matching the reference
implementation's UltraRobustPDFContentExtractor class.
"""

import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..core.config import ExtractionConfig, PDFReaderConfig
from ..core.base import BaseExtractor
from ..readers import PDFReaderFactory
from ..chunking.text_chunker import TextChunker, ChunkConfig, clean_text_content
from ..llm.role_analyzer import LLMRoleAnalyzer, LLMAnalysisConfig
from ..classification import RoleClassifier, ImportanceAnalyzer
from ..segmentation import BasicSegmenter
from ..esg import ESGContentAnalyzer, ESGStatisticsCalculator
from ..validation import PageValidator
from ..api.client import APIConfig


@dataclass
class ExtractorConfig:
    """Configuration for the PDF extractor."""
    # PDF reading
    pdf_reader_config: PDFReaderConfig = field(default_factory=PDFReaderConfig)
    
    # LLM configuration
    use_llm: bool = True
    api_config: Optional[APIConfig] = None
    
    # Chunking
    chunk_config: ChunkConfig = field(default_factory=ChunkConfig)
    
    # Processing
    batch_delay: float = 1.0
    max_retries: int = 3
    
    # ESG analysis
    enable_esg_analysis: bool = True
    
    # Validation
    min_page_chars: int = 50
    
    # Output
    include_original_text: bool = True


class PDFExtractor(BaseExtractor):
    """
    Basic PDF extractor using rule-based classification.
    
    No LLM required - fast and reliable for basic extraction.
    
    Features:
    - Multi-method PDF reading with fallback
    - Rule-based text classification
    - Basic segmentation
    - Optional ESG analysis
    - Page validation
    """
    
    def __init__(self, config: Optional[ExtractorConfig] = None):
        """
        Initialize PDF extractor.
        
        Args:
            config: Extractor configuration. Uses defaults if None.
        """
        self.config = config or ExtractorConfig(use_llm=False)
        
        # Initialize components
        self.segmenter = BasicSegmenter()
        self.esg_analyzer = ESGContentAnalyzer() if self.config.enable_esg_analysis else None
        self.validator = PageValidator(min_page_chars=self.config.min_page_chars)
        
        print("[OK] PDFExtractor initialized (rule-based mode)")
    
    def extract(self, pdf_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Extract content from PDF.
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional output path for results
            
        Returns:
            Extraction result dictionary
        """
        print(f"[INFO] Starting PDF extraction: {pdf_path}")
        start_time = time.time()
        
        # Step 1: Read PDF
        text_data = self.extract_text(pdf_path)
        if not text_data['success']:
            return self._create_error_result(f"PDF reading failed: {text_data.get('error')}")
        
        print(f"[OK] PDF read with {len(text_data['pages'])} pages")
        
        # Step 2: Process pages
        processed_pages = self.process_pages(text_data)
        print(f"[OK] Processed {len(processed_pages)} pages")
        
        # Step 3: Validate
        validation = self._validate_result(processed_pages)
        
        # Step 4: ESG analysis
        esg_analysis = None
        if self.config.enable_esg_analysis and self.esg_analyzer:
            esg_analysis = self._run_esg_analysis({'pages': processed_pages})
        
        # Create result
        elapsed_time = time.time() - start_time
        result = {
            'metadata': text_data.get('metadata', {}),
            'pages': processed_pages,
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_method': text_data.get('extraction_method', 'unknown'),
            'validation': validation,
            'processing': {
                'elapsed_seconds': elapsed_time,
                'total_pages': len(processed_pages),
                'use_llm': False,
                'config': {
                    'min_page_chars': self.config.min_page_chars,
                    'enable_esg_analysis': self.config.enable_esg_analysis
                }
            }
        }
        
        if esg_analysis:
            result['esg_analysis'] = esg_analysis
        
        # Save if output path provided
        if output_path:
            self._save_result(result, output_path)
        
        print(f"[OK] Extraction complete in {elapsed_time:.2f}s")
        return result
    
    def extract_text(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract raw text from PDF."""
        return PDFReaderFactory.read_with_fallback(pdf_path, self.config.pdf_reader_config)
    
    def process_pages(self, text_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process extracted text into structured segments."""
        processed_pages = []
        
        for page in text_data.get('pages', []):
            page_number = page.get('page_number', 0)
            page_text = page.get('text', '')
            
            # Split into segments (simple paragraph-based)
            paragraphs = self._split_into_paragraphs(page_text)
            
            # Create segments
            segments = []
            for i, para in enumerate(paragraphs):
                if len(para.strip()) > 10:
                    segment = self.segmenter.create_segment(
                        text=para,
                        page_num=page_number,
                        segment_num=i + 1,
                        total_segments=len(paragraphs)
                    )
                    
                    # Add ESG analysis if enabled
                    if self.esg_analyzer:
                        esg_data = self.esg_analyzer.analyze_content(para)
                        segment.update(esg_data)
                    
                    segments.append(segment)
            
            processed_pages.append({
                'page_number': page_number,
                'text_segments': segments,
                'original_text': page_text if self.config.include_original_text else '',
                'num_segments': len(segments),
                'char_count': len(page_text),
                'word_count': len(page_text.split())
            })
        
        return processed_pages
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs."""
        if '\n\n' in text:
            paragraphs = text.split('\n\n')
        elif '\n' in text:
            paragraphs = text.split('\n')
        else:
            # Split by sentence for very long single blocks
            paragraphs = [text]
        
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _validate_result(self, pages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate extraction result."""
        self.validator.validate_all({'pages': pages})
        return self.validator.get_validation_report()
    
    def _run_esg_analysis(self, structured_content: Dict[str, Any]) -> Dict[str, Any]:
        """Run ESG analysis on structured content."""
        stats = ESGStatisticsCalculator.calculate_statistics(structured_content)
        importance = ESGStatisticsCalculator.calculate_importance_distribution(structured_content)
        metrics = self.esg_analyzer.extract_metrics(structured_content)
        
        return {
            'statistics': stats,
            'importance_distribution': importance,
            'metrics': metrics
        }
    
    def _create_error_result(self, error: str) -> Dict[str, Any]:
        """Create an error result."""
        return {
            'metadata': {},
            'pages': [],
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_method': 'failed',
            'success': False,
            'error': error
        }
    
    def _save_result(self, result: Dict[str, Any], output_path: Path):
        """Save result to file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"[OK] Result saved to: {output_path}")


class LLMPDFExtractor(PDFExtractor):
    """
    LLM-enhanced PDF extractor.
    
    Uses LLM for text role analysis, matching the reference implementation's
    UltraRobustPDFContentExtractor class.
    
    Features:
    - Everything from PDFExtractor
    - LLM-based text role analysis
    - Chunked processing
    - Fallback to rule-based on LLM failure
    - Retry logic with exponential backoff
    """
    
    def __init__(self, config: Optional[ExtractorConfig] = None):
        """
        Initialize LLM PDF extractor.
        
        Args:
            config: Extractor configuration. Uses defaults if None.
        """
        self.config = config or ExtractorConfig(use_llm=True)
        
        # Force LLM mode
        self.config.use_llm = True
        
        # Initialize base components
        self.segmenter = BasicSegmenter()
        self.esg_analyzer = ESGContentAnalyzer() if self.config.enable_esg_analysis else None
        self.validator = PageValidator(min_page_chars=self.config.min_page_chars)
        
        # Initialize LLM components
        llm_config = LLMAnalysisConfig(
            api_config=self.config.api_config or APIConfig.from_env(),
            chunk_config=self.config.chunk_config,
            batch_delay=self.config.batch_delay,
            max_retries=self.config.max_retries
        )
        self.llm_analyzer = LLMRoleAnalyzer(llm_config)
        
        print("[OK] LLMPDFExtractor initialized (LLM-enhanced mode)")
    
    def process_pages(self, text_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process pages using LLM analysis."""
        processed_pages = []
        failed_pages = []
        
        pages = text_data.get('pages', [])
        total_pages = len(pages)
        
        for i, page in enumerate(pages):
            page_number = page.get('page_number', i + 1)
            page_text = page.get('text', '')
            
            print(f"[INFO] Processing page {page_number}/{total_pages}...")
            
            # Skip pages with insufficient content
            if len(page_text.strip()) < self.config.min_page_chars:
                print(f"  [SKIP] Page {page_number}: insufficient content")
                processed_pages.append({
                    'page_number': page_number,
                    'text_segments': [],
                    'original_text': page_text if self.config.include_original_text else '',
                    'num_segments': 0,
                    'error': 'Insufficient content'
                })
                continue
            
            # Analyze with LLM
            try:
                result = self.llm_analyzer.analyze_page(page_text, page_number)
                
                # Check for fallback
                if result.get('fallback'):
                    failed_pages.append(page_number)
                    print(f"  [WARN] Page {page_number} used fallback processing")
                
                # Add ESG analysis if enabled
                if self.esg_analyzer:
                    for segment in result.get('text_segments', []):
                        segment_text = segment.get('text', '')
                        esg_data = self.esg_analyzer.analyze_content(segment_text)
                        segment.update(esg_data)
                
                # Add page metadata
                result['original_text'] = page_text if self.config.include_original_text else ''
                result['num_segments'] = len(result.get('text_segments', []))
                result['char_count'] = len(page_text)
                result['word_count'] = len(page_text.split())
                
                processed_pages.append(result)
                print(f"  [OK] Page {page_number}: {result['num_segments']} segments")
                
            except Exception as e:
                print(f"  [ERROR] Page {page_number} failed: {e}")
                failed_pages.append(page_number)
                
                # Fall back to basic extraction
                basic_result = super()._process_single_page(page_text, page_number)
                basic_result['error'] = str(e)
                basic_result['fallback'] = True
                processed_pages.append(basic_result)
        
        # Report results
        if failed_pages:
            print(f"[WARN] {len(failed_pages)} pages required fallback: {failed_pages}")
        
        return processed_pages
    
    def _process_single_page(self, page_text: str, page_number: int) -> Dict[str, Any]:
        """Process a single page with basic extraction (for fallback)."""
        paragraphs = self._split_into_paragraphs(page_text)
        
        segments = []
        for i, para in enumerate(paragraphs):
            if len(para.strip()) > 10:
                segment = self.segmenter.create_segment(
                    text=para,
                    page_num=page_number,
                    segment_num=i + 1,
                    total_segments=len(paragraphs)
                )
                
                if self.esg_analyzer:
                    esg_data = self.esg_analyzer.analyze_content(para)
                    segment.update(esg_data)
                
                segments.append(segment)
        
        return {
            'page_number': page_number,
            'text_segments': segments,
            'original_text': page_text if self.config.include_original_text else '',
            'num_segments': len(segments),
            'char_count': len(page_text),
            'word_count': len(page_text.split())
        }


class ESGExtractor(LLMPDFExtractor):
    """
    ESG-specialized PDF extractor.
    
    Extends LLMPDFExtractor with ESG-specific features.
    
    Features:
    - Everything from LLMPDFExtractor
    - Enhanced ESG content analysis
    - ESG metric extraction
    - ESG statistics calculation
    - ESG-specific validation
    """
    
    def __init__(self, config: Optional[ExtractorConfig] = None):
        """
        Initialize ESG extractor.
        
        Args:
            config: Extractor configuration. Uses defaults if None.
        """
        # Force ESG analysis on
        if config is None:
            config = ExtractorConfig(use_llm=True, enable_esg_analysis=True)
        else:
            config.enable_esg_analysis = True
        
        super().__init__(config)
        
        print("[OK] ESGExtractor initialized (ESG-specialized mode)")
    
    def extract(self, pdf_path: Path, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Extract content with ESG-specialized analysis.
        
        Args:
            pdf_path: Path to PDF file
            output_path: Optional output path for results
            
        Returns:
            Extraction result with comprehensive ESG analysis
        """
        # Run base extraction
        result = super().extract(pdf_path, output_path=None)  # Don't save yet
        
        # Enhance with ESG-specific analysis
        if result.get('pages'):
            result['esg_summary'] = self._create_esg_summary(result)
        
        # Save if output path provided
        if output_path:
            self._save_result(result, output_path)
        
        return result
    
    def _create_esg_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Create comprehensive ESG summary."""
        esg_analysis = result.get('esg_analysis', {})
        
        # Count ESG segments
        esg_segments = {
            'environmental': 0,
            'social': 0,
            'governance': 0
        }
        
        for page in result.get('pages', []):
            for segment in page.get('text_segments', []):
                for category in segment.get('esg_categories', []):
                    if category in esg_segments:
                        esg_segments[category] += 1
        
        return {
            'total_pages': len(result.get('pages', [])),
            'total_segments': sum(
                len(p.get('text_segments', [])) for p in result.get('pages', [])
            ),
            'esg_segment_counts': esg_segments,
            'statistics': esg_analysis.get('statistics', {}),
            'metrics_summary': esg_analysis.get('metrics', {}).get('summary', {}),
            'extraction_quality': self._assess_quality(result)
        }
    
    def _assess_quality(self, result: Dict[str, Any]) -> str:
        """Assess extraction quality."""
        validation = result.get('validation', {})
        validation_rate = validation.get('validation_rate', 0)
        
        if validation_rate >= 0.95:
            return 'excellent'
        elif validation_rate >= 0.8:
            return 'good'
        elif validation_rate >= 0.6:
            return 'fair'
        else:
            return 'poor'
