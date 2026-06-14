"""
Adaptive text chunking strategy for ESG analysis.

Adjusts chunk size based on content complexity (metrics density, ESG keywords).
Extracted from ESGLLMAnalyzer._chunk_text_content() and _calculate_segment_complexity().
"""

import re
from typing import List
from loguru import logger

from .base_chunker import BaseChunker, ChunkingStrategy


class AdaptiveChunker(BaseChunker):
    """
    Adaptive chunking based on content complexity.
    
    Features:
    - Analyzes segment complexity (numbers, metrics, ESG keywords)
    - Adjusts chunk size dynamically:
      * High complexity (>5 indicators) → smaller chunks (20 segments)
      * Medium complexity (>2 indicators) → medium chunks (25 segments)
      * Low complexity → base chunk size (35-40 segments)
    - Merges small chunks if total exceeds threshold (50+ chunks)
    
    This ensures:
    - Complex content with many metrics gets more focused analysis
    - Simple content is processed efficiently in larger batches
    - Total chunk count stays manageable
    """
    
    # ESG keywords that indicate complexity
    ESG_KEYWORDS = [
        'emissions', 'carbon', 'energy', 'water', 'waste', 'renewable',
        'diversity', 'inclusion', 'safety', 'health', 'governance',
        'scope', 'target', 'goal', 'commitment', 'reduction', 'increase',
        'percentage', 'million', 'billion', 'tons', 'CO2e', 'MMT'
    ]
    
    def __init__(self, strategy: ChunkingStrategy = None):
        """
        Initialize adaptive chunker.
        
        Args:
            strategy: Chunking strategy configuration
        """
        super().__init__(strategy)
        logger.info(f"Adaptive chunker initialized with base_chunk_size={self.strategy.base_chunk_size}")
    
    def chunk(self, text_segments: List[str]) -> List[List[str]]:
        """
        Chunk text segments using adaptive strategy.
        
        Args:
            text_segments: List of text segments to chunk
        
        Returns:
            List of chunks, where each chunk is a list of text segments
        """
        if not text_segments:
            return []
        
        # Reduce base chunk size for better coverage
        base_chunk_size = min(self.strategy.base_chunk_size, 35)
        chunks = []
        
        # Adaptive chunking based on content complexity
        current_chunk = []
        current_size = 0
        current_complexity = 0
        
        for segment in text_segments:
            # Calculate segment complexity
            segment_complexity = self._calculate_segment_complexity(segment)
            
            # Adjust chunk size based on complexity
            target_chunk_size = base_chunk_size
            
            if segment_complexity > 5:  # High complexity segment
                target_chunk_size = max(self.strategy.min_chunk_size, base_chunk_size - 10)
                logger.debug(f"High complexity segment (score={segment_complexity}), target_size={target_chunk_size}")
            
            elif segment_complexity > 2:  # Medium complexity segment
                target_chunk_size = max(25, base_chunk_size - 5)
                logger.debug(f"Medium complexity segment (score={segment_complexity}), target_size={target_chunk_size}")
            
            # Check if adding this segment would exceed target size
            if current_size >= target_chunk_size and current_chunk:
                chunks.append(current_chunk)
                logger.debug(f"Created chunk {len(chunks)} with {current_size} segments, complexity={current_complexity}")
                current_chunk = []
                current_size = 0
                current_complexity = 0
            
            current_chunk.append(segment)
            current_size += 1
            current_complexity += segment_complexity
        
        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk)
            logger.debug(f"Created final chunk {len(chunks)} with {current_size} segments, complexity={current_complexity}")
        
        # Merge small chunks if we have too many
        if self.strategy.merge_small_chunks and len(chunks) > self.strategy.max_chunks_threshold:
            logger.info(f"Merging chunks: {len(chunks)} chunks exceeds threshold of {self.strategy.max_chunks_threshold}")
            chunks = self._merge_small_chunks(chunks, base_chunk_size)
        
        logger.info(f"Adaptive chunking complete: {len(text_segments)} segments → {len(chunks)} chunks")
        stats = self.get_stats(chunks)
        logger.info(f"Chunk stats: avg={stats['avg_size']:.1f}, min={stats['min_size']}, max={stats['max_size']}")
        
        return chunks
    
    def _calculate_segment_complexity(self, segment: str) -> int:
        """
        Calculate the complexity of a text segment based on ESG content indicators.
        
        Complexity is determined by:
        1. Numbers and percentages (each adds 1 point)
        2. ESG keywords (each adds 1 point)
        
        Args:
            segment: Text segment to analyze
        
        Returns:
            Complexity score (higher = more complex)
        """
        complexity = 0
        
        # Count numbers and percentages
        numbers = re.findall(r'\d+(?:\.\d+)?', segment)
        percentages = re.findall(r'\d+(?:\.\d+)?%', segment)
        complexity += len(numbers) + len(percentages)
        
        # Count ESG keywords
        segment_lower = segment.lower()
        for keyword in self.ESG_KEYWORDS:
            if keyword.lower() in segment_lower:
                complexity += 1
        
        return complexity
    
    def _merge_small_chunks(self, chunks: List[List[str]], base_chunk_size: int) -> List[List[str]]:
        """
        Merge small chunks if total count is too high.
        
        Strategy:
        - Iterate through chunks
        - Combine chunks while staying under 1.5x base_chunk_size
        - Create new chunk when limit would be exceeded
        
        Args:
            chunks: List of chunks to merge
            base_chunk_size: Base chunk size for merging threshold
        
        Returns:
            List of merged chunks
        """
        merged_chunks = []
        current_merged = []
        current_merged_size = 0
        
        for chunk in chunks:
            chunk_size = len(chunk)
            
            # Can we add this chunk to current merged chunk?
            if current_merged_size + chunk_size <= base_chunk_size * 1.5:
                current_merged.extend(chunk)
                current_merged_size += chunk_size
            else:
                # Current merged chunk is full, save it
                if current_merged:
                    merged_chunks.append(current_merged)
                # Start new merged chunk
                current_merged = chunk
                current_merged_size = chunk_size
        
        # Add final merged chunk
        if current_merged:
            merged_chunks.append(current_merged)
        
        logger.info(f"Merged {len(chunks)} chunks → {len(merged_chunks)} chunks")
        return merged_chunks

