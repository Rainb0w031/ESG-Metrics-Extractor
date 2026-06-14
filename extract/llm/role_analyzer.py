"""LLM-based text role analyzer.

This module provides LLM-based text analysis matching the reference
implementation's analyze_text_roles_with_llm() method.
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List

from ..api.client import DirectAPIClient, APIConfig
from ..chunking.text_chunker import TextChunker, ChunkConfig, clean_text_content
from .prompts import create_chunk_prompt, get_system_prompt


@dataclass
class LLMAnalysisConfig:
    """Configuration for LLM-based analysis."""
    # API configuration
    api_config: Optional[APIConfig] = None
    
    # Chunking configuration
    chunk_config: Optional[ChunkConfig] = None
    
    # Processing configuration
    batch_delay: float = 1.0  # Delay between chunks to avoid rate limits
    enable_fallback: bool = True  # Fall back to basic classification on failure
    
    # Retry configuration
    max_retries: int = 3
    
    def __post_init__(self):
        if self.api_config is None:
            self.api_config = APIConfig.from_env()
        if self.chunk_config is None:
            self.chunk_config = ChunkConfig()


class LLMRoleAnalyzer:
    """
    LLM-based text role analyzer.
    
    Matches the reference implementation's analyze_text_roles_with_llm() method.
    
    Features:
    - Chunked processing for large texts
    - Direct API calls with retry logic
    - Fallback response generation
    - Batch processing with delays
    """
    
    def __init__(self, config: Optional[LLMAnalysisConfig] = None):
        """
        Initialize LLM role analyzer.
        
        Args:
            config: Analysis configuration. Uses defaults if None.
        """
        self.config = config or LLMAnalysisConfig()
        self.api_client = DirectAPIClient(self.config.api_config)
        self.chunker = TextChunker(self.config.chunk_config)
    
    def analyze_page(self, page_text: str, page_number: int) -> Dict[str, Any]:
        """
        Analyze a page's text content using LLM.
        
        Matches the reference implementation's analyze_text_roles_with_llm().
        
        Args:
            page_text: Text content of the page
            page_number: Page number
            
        Returns:
            Dictionary with analysis results
        """
        # Clean the text content
        cleaned_text = clean_text_content(page_text)
        
        if not cleaned_text or len(cleaned_text.strip()) < 50:
            return self._create_fallback_response(page_number, page_text, "Insufficient text content")
        
        # Split into chunks
        chunks = self.chunker.chunk_text(cleaned_text, page_number)
        print(f"  Split page {page_number} into {len(chunks)} chunks")
        
        if not chunks:
            return self._create_fallback_response(page_number, page_text, "No valid chunks created")
        
        # Process chunks
        all_segments = []
        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)} for page {page_number}")
            
            # Create prompt for this chunk
            prompt = create_chunk_prompt(chunk, page_number, i + 1, len(chunks))
            
            # Process chunk with retries
            result = self._process_chunk(prompt, page_number, chunk)
            
            if result and isinstance(result, list):
                all_segments.extend(result)
            else:
                # Add fallback segment for failed chunk
                all_segments.append(self._create_fallback_segment(chunk))
            
            # Add delay between chunks (except for last)
            if i < len(chunks) - 1 and self.config.batch_delay > 0:
                time.sleep(self.config.batch_delay)
        
        # Combine all segments
        if all_segments:
            return {
                "page_number": page_number,
                "text_segments": all_segments,
                "page_summary": f"Page {page_number} processed with {len(all_segments)} segments",
                "main_topics": [seg.get("context", "general") for seg in all_segments[:5]],
                "document_section": "content"
            }
        else:
            return self._create_fallback_response(page_number, page_text, "No segments generated")
    
    def _process_chunk(self, prompt: str, page_number: int, chunk_text: str) -> Optional[List[Dict[str, Any]]]:
        """
        Process a single chunk with the LLM.
        
        Args:
            prompt: Prompt for LLM
            page_number: Page number
            chunk_text: Original chunk text
            
        Returns:
            List of segment dictionaries, or None if failed
        """
        for attempt in range(self.config.max_retries):
            try:
                # Make API call
                messages = [
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": prompt}
                ]
                
                result = self.api_client.chat_json(messages)
                
                if result and 'text_segments' in result:
                    return result['text_segments']
                
            except Exception as e:
                print(f"    [WARNING] Chunk processing attempt {attempt + 1} failed: {e}")
            
            if attempt < self.config.max_retries - 1:
                time.sleep(self.config.api_config.retry_delay)
        
        print(f"    [WARNING] All attempts failed, using fallback")
        return None
    
    def _create_fallback_response(self, page_number: int, text: str, reason: str) -> Dict[str, Any]:
        """
        Create a fallback response when LLM analysis fails.
        
        Matches the reference implementation's _create_fallback_response().
        
        Args:
            page_number: Page number
            text: Original text content
            reason: Reason for fallback
            
        Returns:
            Fallback response dictionary
        """
        # Create basic segments from the text
        segments = []
        
        # Split by paragraphs or lines
        paragraphs = text.split('\n\n') if '\n\n' in text else text.split('\n')
        
        for i, para in enumerate(paragraphs[:10]):  # Limit to 10 segments
            para = para.strip()
            if len(para) > 20:  # Only include substantial content
                segments.append(self._create_fallback_segment(para, i, len(paragraphs)))
        
        # If no segments created, create one from entire text
        if not segments and text.strip():
            segments.append(self._create_fallback_segment(text[:500]))
        
        return {
            "page_number": page_number,
            "text_segments": segments,
            "page_summary": f"Page {page_number} - Fallback processing ({reason})",
            "main_topics": ["general"],
            "document_section": "content",
            "error": reason,
            "fallback": True
        }
    
    def _create_fallback_segment(self, text: str, index: int = 0, total: int = 1) -> Dict[str, Any]:
        """
        Create a fallback segment when LLM fails.
        
        Args:
            text: Text content
            index: Segment index
            total: Total segments
            
        Returns:
            Fallback segment dictionary
        """
        # Basic heuristic classification
        text_preview = text[:200] + "..." if len(text) > 200 else text
        text_lower = text.lower()
        
        # Determine role based on simple heuristics
        if len(text) < 50 and text.upper() == text:
            role = "headline"
        elif text.startswith(('-', '*', '•', '1.', '2.')):
            role = "list_item"
        else:
            role = "content"
        
        # Determine importance
        esg_keywords = ['sustainability', 'environmental', 'social', 'governance', 'carbon', 'emissions']
        if any(kw in text_lower for kw in esg_keywords):
            importance = "high"
        elif len(text) > 200:
            importance = "medium"
        else:
            importance = "low"
        
        return {
            "text": text_preview,
            "role": role,
            "confidence": 0.5,
            "position": "start" if index == 0 else ("end" if index == total - 1 else "middle"),
            "importance": importance,
            "context": "Fallback content due to processing error"
        }
    
    def analyze_pages(self, pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple pages.
        
        Args:
            pages: List of page dictionaries with 'text' and 'page_number'
            
        Returns:
            List of analyzed page dictionaries
        """
        results = []
        
        for page in pages:
            page_number = page.get('page_number', 1)
            page_text = page.get('text', '')
            
            print(f"[INFO] Analyzing page {page_number}...")
            
            result = self.analyze_page(page_text, page_number)
            results.append(result)
        
        return results
