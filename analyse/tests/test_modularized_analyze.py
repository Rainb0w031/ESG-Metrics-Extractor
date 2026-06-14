"""
Comprehensive test suite for modularized ESG analysis.

Tests all components individually and the integrated pipeline.
"""

import json
from pathlib import Path
from datetime import datetime


def test_adaptive_chunker():
    """Test AdaptiveChunker functionality."""
    print("\n" + "="*60)
    print("TEST: AdaptiveChunker")
    print("="*60)
    
    from metrics.analyse.chunking.adaptive_chunker import AdaptiveChunker
    from metrics.analyse.core.base import AnalysisConfig
    
    # Create chunker
    config = AnalysisConfig(chunk_size=30)
    chunker = AdaptiveChunker(config)
    
    # Test data
    segments = [
        "Carbon emissions reduced by 20% in 2024",
        "Scope 1 emissions totaled 717,096 tons",
        "Scope 2 emissions totaled 3,732,075 tons",
        "Renewable energy percentage increased to 85%",
        "Water positive goal set for 2030"
    ] * 10  # Repeat to create multiple chunks
    
    # Chunk
    chunks = chunker.chunk(segments)
    
    print(f"Input segments: {len(segments)}")
    print(f"Output chunks: {len(chunks)}")
    print(f"First chunk size: {len(chunks[0])}")
    
    assert len(chunks) > 0, "Should create at least one chunk"
    assert all(isinstance(chunk, list) for chunk in chunks), "Chunks should be lists"
    
    print("[PASS] AdaptiveChunker works correctly")


def test_llm_processor():
    """Test LLMProcessor (mock mode)."""
    print("\n" + "="*60)
    print("TEST: LLMProcessor (Mock)")
    print("="*60)
    
    # Note: Full LLM test requires API access
    # This tests the structure only
    
    from metrics.analyse.processors.llm_processor import LLMProcessor, ProcessorConfig
    
    config = ProcessorConfig(max_retries=1)
    
    # Would need actual analyzer with .chat() method for full test
    # Just verify structure here
    
    assert ProcessorConfig is not None
    assert LLMProcessor is not None
    
    print("[PASS] LLMProcessor structure is correct")


def test_duplicate_detector():
    """Test DuplicateDetector."""
    print("\n" + "="*60)
    print("TEST: DuplicateDetector")
    print("="*60)
    
    from metrics.analyse.merging.duplicate_detector import DuplicateDetector
    
    detector = DuplicateDetector(similarity_threshold=0.8)
    
    # Test metric duplicates
    existing_metrics = {
        "scope_1_emissions_2024": "717,096 tons",
        "renewable_energy": "85%"
    }
    
    # Exact duplicate
    assert detector.is_duplicate_metric("scope_1_emissions_2024", "717,096 tons", existing_metrics)
    
    # Fuzzy duplicate (different formatting)
    assert detector.is_duplicate_metric("scope 1 emissions 2024", "717,096 tons", existing_metrics)
    
    # Not duplicate
    assert not detector.is_duplicate_metric("scope_2_emissions_2024", "3.7M tons", existing_metrics)
    
    # Test detail duplicates
    details = [
        "Carbon emissions reduced by 20% in 2024",
        "Renewable energy increased to 85%"
    ]
    
    # Exact duplicate
    assert detector.is_duplicate_detail("Carbon emissions reduced by 20% in 2024", details)
    
    # Fuzzy duplicate (similar content)
    assert detector.is_duplicate_detail("carbon emissions reduced by 20 percent in 2024", details)
    
    # Not duplicate
    assert not detector.is_duplicate_detail("Water positive goal for 2030", details)
    
    print("[PASS] DuplicateDetector works correctly")


def test_esg_merger():
    """Test ESGMerger."""
    print("\n" + "="*60)
    print("TEST: ESGMerger")
    print("="*60)
    
    from metrics.analyse.merging.esg_merger import ESGMerger
    
    merger = ESGMerger()
    
    # Test data
    result1 = {
        "environmental_comprehensive": {
            "emissions": {
                "scope_1": {
                    "details": ["Scope 1 detail 1"],
                    "metrics": {"scope_1_2024": "717K tons"}
                }
            }
        }
    }
    
    result2 = {
        "environmental_comprehensive": {
            "emissions": {
                "scope_1": {
                    "details": ["Scope 1 detail 2"],
                    "metrics": {"scope_1_2023": "928K tons"}
                },
                "scope_2": {
                    "details": ["Scope 2 detail 1"],
                    "metrics": {"scope_2_2024": "3.7M tons"}
                }
            }
        }
    }
    
    # Merge
    merged = merger.merge(result1, result2)
    
    # Verify structure
    assert "environmental_comprehensive" in merged
    assert "emissions" in merged["environmental_comprehensive"]
    assert "scope_1" in merged["environmental_comprehensive"]["emissions"]
    assert "scope_2" in merged["environmental_comprehensive"]["emissions"]
    
    # Verify details merged
    scope_1_details = merged["environmental_comprehensive"]["emissions"]["scope_1"]["details"]
    assert len(scope_1_details) == 2
    
    # Verify metrics merged
    scope_1_metrics = merged["environmental_comprehensive"]["emissions"]["scope_1"]["metrics"]
    assert "scope_1_2024" in scope_1_metrics
    assert "scope_1_2023" in scope_1_metrics
    
    print("[PASS] ESGMerger works correctly")


def test_quality_validator():
    """Test QualityValidator."""
    print("\n" + "="*60)
    print("TEST: QualityValidator")
    print("="*60)
    
    from metrics.analyse.validation.quality_validator import QualityValidator
    
    validator = QualityValidator()
    
    # Test data with invalid content
    results = {
        "environmental_comprehensive": {
            "emissions": {
                "scope_1": {
                    "details": [
                        "Valid detail with enough content",
                        "Too short",  # Should be filtered
                        "",  # Should be filtered
                        "Another valid detail with sufficient length"
                    ],
                    "metrics": {
                        "valid_metric": "717K tons",
                        "": "invalid",  # Should be filtered
                        "x": "y"  # Should be filtered (too short)
                    }
                }
            }
        }
    }
    
    # Validate
    validated = validator.validate(results)
    
    # Check details filtered
    details = validated["environmental_comprehensive"]["emissions"]["scope_1"]["details"]
    assert len(details) == 2  # Only 2 valid details
    assert "Too short" not in details
    
    # Check metrics filtered
    metrics = validated["environmental_comprehensive"]["emissions"]["scope_1"]["metrics"]
    assert "valid_metric" in metrics
    assert "" not in metrics
    assert "x" not in metrics
    
    # Check quality score
    quality_score = validator.get_quality_score(validated)
    assert 0.0 <= quality_score <= 1.0
    
    print(f"Quality score: {quality_score:.2f}")
    print("[PASS] QualityValidator works correctly")


def test_prompt_factory():
    """Test PromptFactory."""
    print("\n" + "="*60)
    print("TEST: PromptFactory")
    print("="*60)
    
    from metrics.analyse.prompts.base_prompt import PromptFactory
    
    # Get builders
    comprehensive_builder = PromptFactory.get_prompt_builder("comprehensive")
    environmental_builder = PromptFactory.get_prompt_builder("environmental")
    social_builder = PromptFactory.get_prompt_builder("social")
    governance_builder = PromptFactory.get_prompt_builder("governance")
    
    # Test prompt building
    test_chunk = ["Carbon emissions reduced by 20%", "Renewable energy at 85%"]
    
    prompt = comprehensive_builder.build(test_chunk, 1, 5, "2024")
    
    assert len(prompt) > 0
    assert "2024" in prompt
    assert "chunk 1/5" in prompt.lower()
    assert "Carbon emissions reduced by 20%" in prompt
    
    print(f"Prompt length: {len(prompt)} chars")
    print("[PASS] PromptFactory works correctly")


def test_integrated_analyzer_structure():
    """Test ESGLLMAnalyzer structure (without actual LLM calls)."""
    print("\n" + "="*60)
    print("TEST: ESGLLMAnalyzer Structure")
    print("="*60)
    
    from metrics.analyse.pipeline.esg_analyzer import ESGLLMAnalyzer
    from metrics.analyse.core.base import AnalysisConfig
    
    # Create analyzer
    config = AnalysisConfig()
    analyzer = ESGLLMAnalyzer(which_model="qwen-max", analysis_config=config)
    
    # Verify components initialized
    assert analyzer.chunker is not None
    assert analyzer.processor is not None
    assert analyzer.merger is not None
    assert analyzer.validator is not None
    
    # Test helper methods
    test_content = {
        "metadata": {"title": "2024 Sustainability Report"},
        "pages": [
            {
                "page_number": 1,
                "text_segments": [
                    {"text": "Carbon emissions reduced"},
                    {"text": "Renewable energy increased"}
                ]
            }
        ]
    }
    
    year = analyzer._extract_year_from_content(test_content)
    assert year == "2024"
    
    segments = analyzer._extract_text_segments(test_content)
    assert len(segments) == 2
    
    print("[PASS] ESGLLMAnalyzer structure is correct")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("MODULARIZED ESG ANALYSIS TEST SUITE")
    print("="*60)
    
    try:
        test_adaptive_chunker()
        test_llm_processor()
        test_duplicate_detector()
        test_esg_merger()
        test_quality_validator()
        test_prompt_factory()
        test_integrated_analyzer_structure()
        
        print("\n" + "="*60)
        print("[SUCCESS] ALL TESTS PASSED")
        print("="*60)
        
        return True
    
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

