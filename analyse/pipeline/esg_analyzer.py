"""
Integrated ESG LLM Analyzer.

Main analyzer that orchestrates all modularized components for ESG analysis.
Simplified and maintainable version of the original ESGLLMAnalyzer.
"""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
from loguru import logger

from prompter.prompt import BasePromptModel

from ..core.config import AnalysisConfig
from ..chunking.adaptive_chunker import AdaptiveChunker
from ..prompts.base_prompt import PromptFactory
from ..processors.llm_processor import LLMProcessor, ProcessorConfig
from ..merging.esg_merger import ESGMerger
from ..validation.quality_validator import QualityValidator


class ESGLLMAnalyzer(BasePromptModel):
    """
    Integrated ESG LLM Analyzer.
    
    Orchestrates:
    - AdaptiveChunker: Splits text into manageable chunks
    - PromptFactory: Creates analysis prompts
    - LLMProcessor: Processes chunks with LLM
    - ESGMerger: Merges results from chunks
    - QualityValidator: Validates and cleans results
    
    Maintains quality standards from reference implementation:
    - Comprehensive metrics extraction
    - Unit preservation
    - Duplicate detection
    - Result validation
    - Extensive logging
    """
    
    def __init__(self,
                 which_model: str = "qwen-max",
                 analysis_config: AnalysisConfig = None,
                 processor_config: ProcessorConfig = None,
                 system_prompt: str = None):
        """
        Initialize ESG LLM Analyzer.
        
        Args:
            which_model: Model identifier for prompter
            analysis_config: Analysis configuration
            processor_config: Processor configuration
            system_prompt: System prompt for LLM (optional)
        """
        # Initialize BasePromptModel (provides .chat() method)
        if system_prompt is None:
            system_prompt = "You are an expert ESG analyst specializing in comprehensive Environmental, Social, and Governance data extraction and categorization."
        
        super().__init__(which_model=which_model, system_prompt=system_prompt)
        
        # Store configs
        self.analysis_config = analysis_config or AnalysisConfig()
        self.processor_config = processor_config or ProcessorConfig()
        
        # Initialize components
        # Create ChunkingStrategy from AnalysisConfig
        from ..chunking.base_chunker import ChunkingStrategy
        chunking_strategy = ChunkingStrategy(
            base_chunk_size=self.analysis_config.chunk_size,
            max_chunk_size=self.analysis_config.max_chunk_size,
            min_chunk_size=self.analysis_config.min_chunk_size,
            adaptive=self.analysis_config.enable_adaptive_chunking,
            merge_small_chunks=True,
            max_chunks_threshold=self.analysis_config.max_chunks_to_merge
        )
        self.chunker = AdaptiveChunker(chunking_strategy)
        self.processor = LLMProcessor(self, self.processor_config)  # Pass self for .chat() access
        self.merger = ESGMerger()
        self.validator = QualityValidator()
        
        logger.info(f"ESG LLM Analyzer initialized (model={which_model})")
    
    def analyze_comprehensive(self,
                             structured_content: Dict[str, Any],
                             analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze structured content with comprehensive ESG analysis.
        
        Main analysis method that orchestrates the entire pipeline:
        1. Extract and chunk text segments
        2. Build prompts for each chunk
        3. Process chunks with LLM
        4. Merge results
        5. Validate and clean
        6. Add metadata
        
        Args:
            structured_content: Structured PDF content from extraction
            analysis_type: Type of analysis ("comprehensive", "environmental", "social", "governance")
        
        Returns:
            Comprehensive ESG analysis results
        """
        logger.info(f"Starting {analysis_type} ESG analysis...")
        
        # Extract year
        year = self._extract_year_from_content(structured_content)
        logger.info(f"Report year: {year}")
        
        # Step 1: Extract text segments
        text_segments = self._extract_text_segments(structured_content)
        logger.info(f"Extracted {len(text_segments)} text segments")
        
        if not text_segments:
            logger.warning("No text segments found")
            return self._create_empty_result(year)
        
        # Step 2: Chunk text segments
        chunks = self.chunker.chunk(text_segments)
        logger.info(f"Created {len(chunks)} chunks for analysis")
        
        # Step 3: Build prompts and process chunks
        prompt_builder = PromptFactory.get_prompt_builder(analysis_type)
        chunk_results = []
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"Processing chunk {i}/{len(chunks)}...")
            
            # Build prompt
            prompt = prompt_builder.build(chunk, i, len(chunks), year)
            
            # Process with LLM
            result = self.processor.process(prompt, analysis_type)
            chunk_results.append(result)
        
        # Step 4: Merge results
        logger.info("Merging chunk results...")
        merged_results = self.merger.merge_all(chunk_results, analysis_type)
        
        # Step 5: Validate and clean
        logger.info("Validating results...")
        validated_results = self.validator.validate(merged_results)
        
        # Step 6: Add metadata
        final_result = self._create_final_result(
            validated_results,
            year,
            structured_content,
            analysis_type
        )
        
        # Log quality score
        quality_score = self.validator.get_quality_score(final_result)
        logger.info(f"Analysis complete! Quality score: {quality_score:.2f}")
        
        return final_result
    
    def _extract_text_segments(self, structured_content: Dict[str, Any]) -> List[str]:
        """
        Extract text segments from structured content.
        
        Args:
            structured_content: Structured PDF content
        
        Returns:
            List of text segments
        """
        text_segments = []
        
        # Extract from pages
        pages = structured_content.get('pages', [])
        for page in pages:
            segments = page.get('text_segments', [])
            for segment in segments:
                # Get text
                if isinstance(segment, dict):
                    text = segment.get('text', '')
                else:
                    text = str(segment)
                
                if text and text.strip():
                    text_segments.append(text.strip())
        
        return text_segments
    
    def _extract_year_from_content(self, structured_content: Dict[str, Any]) -> str:
        """
        Extract report year from structured content.
        
        Args:
            structured_content: Structured content
        
        Returns:
            Year string
        """
        # Try metadata
        metadata = structured_content.get('metadata', {})
        if 'year' in metadata:
            return str(metadata['year'])
        
        # Try title
        title = metadata.get('title', '')
        import re
        years = re.findall(r'\b(20\d{2})\b', title)
        if years:
            return years[0]
        
        # Default to current year
        return str(datetime.now().year)
    
    def _create_empty_result(self, year: str) -> Dict[str, Any]:
        """
        Create empty result structure.
        
        Args:
            year: Report year
        
        Returns:
            Empty result dict
        """
        return {
            "environmental_comprehensive_analysis": {},
            "social_comprehensive_analysis": {},
            "governance_comprehensive_analysis": {},
            "analysis_metadata": {
                "status": "no_content",
                "year": year,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _create_final_result(self,
                            validated_results: Dict[str, Any],
                            year: str,
                            structured_content: Dict[str, Any],
                            analysis_type: str) -> Dict[str, Any]:
        """
        Create final result with metadata.
        
        Args:
            validated_results: Validated analysis results
            year: Report year
            structured_content: Original structured content
            analysis_type: Type of analysis
        
        Returns:
            Final result dict
        """
        # Map categories to _analysis suffix keys
        result = {}
        
        if "environmental_comprehensive" in validated_results:
            result["environmental_comprehensive_analysis"] = validated_results["environmental_comprehensive"]
        
        if "social_comprehensive" in validated_results:
            result["social_comprehensive_analysis"] = validated_results["social_comprehensive"]
        
        if "governance_comprehensive" in validated_results:
            result["governance_comprehensive_analysis"] = validated_results["governance_comprehensive"]
        
        # Add metadata
        result["analysis_metadata"] = {
            "total_text_segments_analyzed": self._count_text_segments(structured_content),
            "segments_used_in_analysis": self._count_text_segments(structured_content),
            "analysis_type": f"{analysis_type}_esg_categorization",
            "extraction_method": "all_text_content_inclusion",
            "esg_areas_analyzed": self._get_analyzed_areas(analysis_type),
            "year": year,
            "timestamp": datetime.now().isoformat(),
            "model_used": self.which_model,
            "status": "completed",
            "quality_score": self.validator.get_quality_score(validated_results)
        }
        
        return result
    
    def _count_text_segments(self, structured_content: Dict[str, Any]) -> int:
        """Count total text segments."""
        count = 0
        pages = structured_content.get('pages', [])
        for page in pages:
            segments = page.get('text_segments', [])
            count += len(segments)
        return count
    
    def _get_analyzed_areas(self, analysis_type: str) -> List[str]:
        """Get list of analyzed ESG areas."""
        if analysis_type == "comprehensive":
            return ["environmental", "social", "governance"]
        elif analysis_type in ["environmental", "social", "governance"]:
            return [analysis_type]
        else:
            return ["environmental", "social", "governance"]

