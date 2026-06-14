"""
Base chunking interface for text chunking strategies.

Defines the abstract interface that all chunking strategies must implement.
"""

from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass


@dataclass
class ChunkingStrategy:
    """
    Configuration for chunking strategy.
    
    Controls how text segments are divided into processable chunks.
    """
    
    base_chunk_size: int = 40
    """Base number of segments per chunk"""
    
    max_chunk_size: int = 60
    """Maximum number of segments per chunk"""
    
    min_chunk_size: int = 20
    """Minimum number of segments per chunk"""
    
    adaptive: bool = True
    """Enable adaptive chunking based on content complexity"""
    
    merge_small_chunks: bool = True
    """Merge small chunks if total exceeds threshold"""
    
    max_chunks_threshold: int = 50
    """Maximum chunks before merging is triggered"""
    
    def __post_init__(self):
        """Validate configuration."""
        if self.min_chunk_size > self.base_chunk_size:
            raise ValueError("min_chunk_size cannot exceed base_chunk_size")
        if self.base_chunk_size > self.max_chunk_size:
            raise ValueError("base_chunk_size cannot exceed max_chunk_size")


class BaseChunker(ABC):
    """
    Abstract base for text chunking strategies.
    
    Chunking strategies determine how text segments are grouped
    for processing by the LLM. Different strategies may optimize
    for different goals (speed, accuracy, context preservation, etc.)
    """
    
    def __init__(self, strategy: ChunkingStrategy = None):
        """
        Initialize chunker with strategy.
        
        Args:
            strategy: Chunking strategy configuration
        """
        self.strategy = strategy or ChunkingStrategy()
    
    @abstractmethod
    def chunk(self, text_segments: List[str]) -> List[List[str]]:
        """
        Chunk text segments into manageable pieces.
        
        Args:
            text_segments: List of text segments to chunk
        
        Returns:
            List of chunks, where each chunk is a list of text segments
        """
        pass
    
    def get_stats(self, chunks: List[List[str]]) -> dict:
        """
        Get statistics about the chunks.
        
        Args:
            chunks: List of chunks
        
        Returns:
            Dict with statistics (total_chunks, avg_size, min_size, max_size)
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_size": 0,
                "min_size": 0,
                "max_size": 0
            }
        
        sizes = [len(chunk) for chunk in chunks]
        return {
            "total_chunks": len(chunks),
            "avg_size": sum(sizes) / len(sizes),
            "min_size": min(sizes),
            "max_size": max(sizes)
        }

