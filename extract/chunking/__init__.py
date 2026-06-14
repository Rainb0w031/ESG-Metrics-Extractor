"""Text chunking module for PDF content.

This module provides text chunking capabilities matching the reference
implementation's _chunk_text_content() functionality.
"""

from .text_chunker import TextChunker, ChunkConfig

__all__ = [
    'TextChunker',
    'ChunkConfig',
]
