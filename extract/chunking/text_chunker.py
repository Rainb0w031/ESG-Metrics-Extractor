"""Text chunking utilities.

This module provides text chunking functionality matching the reference
implementation's _chunk_text_content() method.
"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ChunkConfig:
    """Configuration for text chunking."""
    max_chars_per_chunk: int = 320
    max_chunks_per_page: int = 20
    min_chunk_length: int = 50
    preserve_sentences: bool = True
    
    def __post_init__(self):
        if self.max_chars_per_chunk < self.min_chunk_length:
            raise ValueError(
                f"max_chars_per_chunk ({self.max_chars_per_chunk}) must be >= "
                f"min_chunk_length ({self.min_chunk_length})"
            )


class TextChunker:
    """
    Text chunker for splitting content into manageable pieces.
    
    Matches the reference implementation's _chunk_text_content() method.
    
    Features:
    - Sentence-based splitting for natural boundaries
    - Configurable chunk size limits
    - Automatic merging of small chunks
    - Page-aware chunk limits
    """
    
    def __init__(self, config: Optional[ChunkConfig] = None):
        """
        Initialize text chunker.
        
        Args:
            config: Chunk configuration. Uses defaults if None.
        """
        self.config = config or ChunkConfig()
    
    def chunk_text(self, text: str, page_number: int = 1) -> List[str]:
        """
        Split text into chunks.
        
        Args:
            text: Text content to chunk
            page_number: Page number (for logging)
            
        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # If text is short enough, return as single chunk
        if len(text) <= self.config.max_chars_per_chunk:
            return [text] if len(text) >= self.config.min_chunk_length else []
        
        # Split by sentences
        if self.config.preserve_sentences:
            chunks = self._split_by_sentences(text)
        else:
            chunks = self._split_by_length(text)
        
        # Limit number of chunks per page
        if len(chunks) > self.config.max_chunks_per_page:
            chunks = self._merge_chunks(chunks, self.config.max_chunks_per_page)
        
        # Filter out empty chunks
        chunks = [c.strip() for c in chunks if c.strip()]
        
        return chunks
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text by sentences while respecting chunk size limits.
        
        Args:
            text: Text to split
            
        Returns:
            List of chunks
        """
        # Split by sentence boundaries
        sentences = self._extract_sentences(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed limit
            if len(current_chunk) + len(sentence) <= self.config.max_chars_per_chunk:
                current_chunk += sentence + " "
            else:
                # Save current chunk and start new one
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                    if len(chunks) >= self.config.max_chunks_per_page:
                        break
                current_chunk = sentence + " "
        
        # Add final chunk
        if current_chunk.strip() and len(chunks) < self.config.max_chunks_per_page:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text.
        
        Args:
            text: Text to extract sentences from
            
        Returns:
            List of sentences
        """
        # Split by common sentence endings
        # This handles ., !, ? followed by space and capital letter or end
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])$'
        sentences = re.split(sentence_pattern, text)
        
        # If regex didn't split well, fall back to simple period split
        if len(sentences) <= 1 and len(text) > self.config.max_chars_per_chunk:
            sentences = text.split('. ')
            sentences = [s + '.' if not s.endswith('.') else s for s in sentences]
        
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_by_length(self, text: str) -> List[str]:
        """
        Split text by character length.
        
        Args:
            text: Text to split
            
        Returns:
            List of chunks
        """
        chunks = []
        
        for i in range(0, len(text), self.config.max_chars_per_chunk):
            chunk = text[i:i + self.config.max_chars_per_chunk]
            if chunk.strip():
                chunks.append(chunk.strip())
                if len(chunks) >= self.config.max_chunks_per_page:
                    break
        
        return chunks
    
    def _merge_chunks(self, chunks: List[str], target_count: int) -> List[str]:
        """
        Merge chunks to reduce total count.
        
        Args:
            chunks: List of chunks to merge
            target_count: Target number of chunks
            
        Returns:
            Merged chunks
        """
        if len(chunks) <= target_count:
            return chunks
        
        # Calculate how many chunks to merge together
        merge_factor = len(chunks) // target_count + 1
        
        merged = []
        for i in range(0, len(chunks), merge_factor):
            batch = chunks[i:i + merge_factor]
            merged_chunk = " ".join(batch)
            merged.append(merged_chunk)
            
            if len(merged) >= target_count:
                break
        
        return merged
    
    def chunk_page_text(self, page_text: str, page_number: int) -> List[dict]:
        """
        Chunk page text and return with metadata.
        
        Args:
            page_text: Text content of the page
            page_number: Page number
            
        Returns:
            List of chunk dictionaries with metadata
        """
        chunks = self.chunk_text(page_text, page_number)
        
        return [
            {
                'text': chunk,
                'page_number': page_number,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'char_count': len(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]


def clean_text_content(text: str) -> str:
    """
    Clean text content before chunking.
    
    Matches the reference implementation's _clean_text_content() method.
    
    Args:
        text: Raw text content
        
    Returns:
        Cleaned text content
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Remove excessive punctuation
    text = re.sub(r'\.{4,}', '...', text)
    text = re.sub(r'-{3,}', '--', text)
    
    return text.strip()
