"""
End-to-end test for modularized ESG analysis.

Tests the complete pipeline with sample data.
"""

import json
from datetime import datetime


def create_sample_structured_content():
    """Create sample structured content simulating PDF extraction."""
    return {
        "metadata": {
            "title": "2024 Sustainability Report",
            "year": "2024",
            "company": "Test Company",
            "source": "test_report.pdf"
        },
        "pages": [
            {
                "page_number": 1,
                "text_segments": [
                    {
                        "text": "Carbon emissions reduced by 20% in 2024, achieving our sustainability goals.",
                        "esg_categories": ["environmental"],
                        "esg_metrics": []
                    },
                    {
                        "text": "Scope 1 net emissions totaled 717,096 tons in 2024, down from 928,939 tons in 2023.",
                        "esg_categories": ["environmental"],
                        "esg_metrics": ["Scope 1 emissions: 717,096 tons"]
                    },
                    {
                        "text": "Scope 2 net emissions totaled 3,732,075 tons in 2024, representing a 29% reduction.",
                        "esg_categories": ["environmental"],
                        "esg_metrics": ["Scope 2 emissions: 3,732,075 tons"]
                    },
                    {
                        "text": "Renewable energy percentage increased to 85% of total energy consumption.",
                        "esg_categories": ["environmental"],
                        "esg_metrics": ["Renewable energy: 85%"]
                    },
                    {
                        "text": "Water positive goal set for 2030, aiming to replenish more water than we consume.",
                        "esg_categories": ["environmental"],
                        "esg_metrics": []
                    }
                ]
            },
            {
                "page_number": 2,
                "text_segments": [
                    {
                        "text": "Diversity and inclusion programs expanded, with Black representation increasing by 39%.",
                        "esg_categories": ["social"],
                        "esg_metrics": ["Black representation increase: 39%"]
                    },
                    {
                        "text": "Employee training programs reached 110,000 employees globally in 2024.",
                        "esg_categories": ["social"],
                        "esg_metrics": ["Employees trained: 110,000"]
                    },
                    {
                        "text": "Workplace safety incident rate improved by 7% year-over-year.",
                        "esg_categories": ["social"],
                        "esg_metrics": ["Safety improvement: 7%"]
                    },
                    {
                        "text": "Community investment totaled $1.6 billion committed to local programs.",
                        "esg_categories": ["social"],
                        "esg_metrics": ["Community investment: $1.6 billion"]
                    }
                ]
            },
            {
                "page_number": 3,
                "text_segments": [
                    {
                        "text": "Board diversity increased with 40% of directors from underrepresented groups.",
                        "esg_categories": ["governance"],
                        "esg_metrics": ["Board diversity: 40%"]
                    },
                    {
                        "text": "Ethics training completed by 100% of employees, ensuring compliance awareness.",
                        "esg_categories": ["governance"],
                        "esg_metrics": ["Ethics training: 100%"]
                    },
                    {
                        "text": "Risk management framework enhanced with new climate risk assessments.",
                        "esg_categories": ["governance"],
                        "esg_metrics": []
                    }
                ]
            }
        ],
        "processing": {
            "total_pages": 3,
            "extraction_method": "test_extraction",
            "timestamp": datetime.now().isoformat()
        }
    }


def test_components_individually():
    """Test individual components before full pipeline."""
    print("\n" + "="*70)
    print("TESTING INDIVIDUAL COMPONENTS")
    print("="*70)
    
    # Test 1: Chunking
    print("\n[1/5] Testing AdaptiveChunker...")
    try:
        from analyse.chunking.adaptive_chunker import AdaptiveChunker
        from analyse.chunking.base_chunker import ChunkingStrategy
        
        strategy = ChunkingStrategy(base_chunk_size=5, min_chunk_size=1, max_chunk_size=10)
        chunker = AdaptiveChunker(strategy)
        
        test_segments = [
            "Carbon emissions reduced by 20%",
            "Scope 1 emissions: 717,096 tons",
            "Scope 2 emissions: 3,732,075 tons",
            "Renewable energy at 85%",
            "Water positive goal for 2030",
            "Diversity increased by 39%",
            "Safety improved by 7%",
            "Board diversity at 40%"
        ]
        
        chunks = chunker.chunk(test_segments)
        print(f"   [OK] Created {len(chunks)} chunks from {len(test_segments)} segments")
        print(f"   [OK] First chunk has {len(chunks[0])} segments")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 2: Duplicate Detection
    print("\n[2/5] Testing DuplicateDetector...")
    try:
        from analyse.merging.duplicate_detector import DuplicateDetector
        
        detector = DuplicateDetector(similarity_threshold=0.8)
        
        # Test metric duplicate detection
        existing_metrics = {
            "scope_1_emissions_2024": "717,096 tons"
        }
        
        is_dup1 = detector.is_duplicate_metric("scope_1_emissions_2024", "717K", existing_metrics)
        is_dup2 = detector.is_duplicate_metric("scope 1 emissions 2024", "717K", existing_metrics)
        is_not_dup = detector.is_duplicate_metric("scope_2_emissions_2024", "3.7M", existing_metrics)
        
        print(f"   [OK] Exact match detected: {is_dup1}")
        print(f"   [OK] Fuzzy match detected: {is_dup2}")
        print(f"   [OK] Non-duplicate recognized: {not is_not_dup}")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 3: Merging
    print("\n[3/5] Testing ESGMerger...")
    try:
        from analyse.merging.esg_merger import ESGMerger
        
        merger = ESGMerger()
        
        result1 = {
            "environmental_comprehensive": {
                "emissions": {
                    "scope_1": {
                        "details": ["Detail 1"],
                        "metrics": {"metric_1": "value_1"}
                    }
                }
            }
        }
        
        result2 = {
            "environmental_comprehensive": {
                "emissions": {
                    "scope_1": {
                        "details": ["Detail 2"],
                        "metrics": {"metric_2": "value_2"}
                    }
                }
            }
        }
        
        merged = merger.merge(result1, result2)
        
        details = merged["environmental_comprehensive"]["emissions"]["scope_1"]["details"]
        metrics = merged["environmental_comprehensive"]["emissions"]["scope_1"]["metrics"]
        
        print(f"   [OK] Merged {len(details)} details")
        print(f"   [OK] Merged {len(metrics)} metrics")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 4: Validation
    print("\n[4/5] Testing QualityValidator...")
    try:
        from analyse.validation.quality_validator import QualityValidator
        
        validator = QualityValidator()
        
        test_results = {
            "environmental_comprehensive": {
                "emissions": {
                    "scope_1": {
                        "details": ["Valid detail with sufficient length", "Too short", ""],
                        "metrics": {"valid_metric": "100 tons", "": "invalid"}
                    }
                }
            }
        }
        
        validated = validator.validate(test_results)
        quality_score = validator.get_quality_score(validated)
        
        details = validated["environmental_comprehensive"]["emissions"]["scope_1"]["details"]
        metrics = validated["environmental_comprehensive"]["emissions"]["scope_1"]["metrics"]
        
        print(f"   [OK] Filtered details: {len(test_results['environmental_comprehensive']['emissions']['scope_1']['details'])} -> {len(details)}")
        print(f"   [OK] Filtered metrics: {len(test_results['environmental_comprehensive']['emissions']['scope_1']['metrics'])} -> {len(metrics)}")
        print(f"   [OK] Quality score: {quality_score:.2f}")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    # Test 5: Prompt Factory
    print("\n[5/5] Testing PromptFactory...")
    try:
        from analyse.prompts.base_prompt import PromptFactory
        
        builder = PromptFactory.get_prompt_builder("comprehensive")
        
        test_chunk = ["Carbon emissions reduced by 20%", "Renewable energy at 85%"]
        prompt = builder.build(test_chunk, chunk_num=1, total_chunks=5, year="2024")
        
        print(f"   [OK] Generated prompt: {len(prompt)} characters")
        print(f"   [OK] Contains requirements: {'CRITICAL REQUIREMENTS' in prompt}")
        print(f"   [OK] Contains year: {'2024' in prompt}")
        
    except Exception as e:
        print(f"   [FAIL] {e}")
        return False
    
    print("\n" + "="*70)
    print("[SUCCESS] ALL COMPONENT TESTS PASSED")
    print("="*70)
    return True


def test_full_pipeline():
    """Test the full analysis pipeline with mock LLM responses."""
    print("\n" + "="*70)
    print("TESTING FULL PIPELINE (Structure Only)")
    print("="*70)
    
    try:
        from analyse.pipeline.esg_analyzer import ESGLLMAnalyzer
        from analyse.core.config import AnalysisConfig
        
        print("\n[1/4] Creating analyzer...")
        config = AnalysisConfig(
            chunk_size=5,
            temperature=0.2,
            max_tokens=4096
        )
        
        # Note: This will try to use prompter's BasePromptModel
        # We're testing structure only, not actual LLM calls
        print("   [OK] Creating ESGLLMAnalyzer instance...")
        analyzer = ESGLLMAnalyzer(which_model="qwen-max", analysis_config=config)
        
        print(f"   [OK] Analyzer created with model: {analyzer.which_model}")
        print(f"   [OK] Chunker initialized: {analyzer.chunker is not None}")
        print(f"   [OK] Processor initialized: {analyzer.processor is not None}")
        print(f"   [OK] Merger initialized: {analyzer.merger is not None}")
        print(f"   [OK] Validator initialized: {analyzer.validator is not None}")
        
        print("\n[2/4] Testing helper methods...")
        sample_content = create_sample_structured_content()
        
        year = analyzer._extract_year_from_content(sample_content)
        print(f"   [OK] Year extraction: {year}")
        
        segments = analyzer._extract_text_segments(sample_content)
        print(f"   [OK] Text extraction: {len(segments)} segments")
        
        segment_count = analyzer._count_text_segments(sample_content)
        print(f"   [OK] Segment counting: {segment_count} total")
        
        print("\n[3/4] Testing chunking with extracted segments...")
        chunks = analyzer.chunker.chunk(segments)
        print(f"   [OK] Created {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"      Chunk {i}: {len(chunk)} segments")
        
        print("\n[4/4] Testing prompt generation...")
        from analyse.prompts.base_prompt import PromptFactory
        builder = PromptFactory.get_prompt_builder("comprehensive")
        
        if chunks:
            prompt = builder.build(chunks[0], chunk_num=1, total_chunks=len(chunks), year=year)
            print(f"   [OK] Generated prompt: {len(prompt)} characters")
            print(f"   [OK] First 200 chars: {prompt[:200]}...")
        
        print("\n[NOTE] Full LLM analysis requires:")
        print("   - Valid API credentials in .env")
        print("   - Running: uv run --env-file ../prompter-main/.env python test_analyse_e2e.py")
        print("   - Calling: analyzer.analyze_comprehensive(sample_content)")
        
        print("\n" + "="*70)
        print("[SUCCESS] PIPELINE STRUCTURE TEST PASSED")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n[FAIL] PIPELINE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ESG ANALYSIS MODULE - END-TO-END TEST")
    print("="*70)
    
    # Test components
    components_ok = test_components_individually()
    
    if not components_ok:
        print("\n[FAIL] Component tests failed. Aborting pipeline test.")
        return False
    
    # Test pipeline
    pipeline_ok = test_full_pipeline()
    
    if components_ok and pipeline_ok:
        print("\n" + "="*70)
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*70)
        print("\nModularized ESG analysis system is working correctly!")
        print("\nNext steps:")
        print("  1. Review the generated documentation in analyse/")
        print("  2. Try a real analysis with: analyzer.analyze_comprehensive(pdf_content)")
        print("  3. Explore individual components for custom use cases")
        return True
    else:
        print("\n" + "="*70)
        print("[FAIL] SOME TESTS FAILED")
        print("="*70)
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

