"""
Structure-only test suite for modularized ESG analysis.

Tests component structure without requiring LLM access or external dependencies.
"""


def test_chunker_import():
    """Test AdaptiveChunker can be imported."""
    print("\n" + "="*60)
    print("TEST: AdaptiveChunker Import")
    print("="*60)
    
    try:
        from metrics.analyse.chunking.adaptive_chunker import AdaptiveChunker
        print("[PASS] AdaptiveChunker imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_duplicate_detector_import():
    """Test DuplicateDetector can be imported."""
    print("\n" + "="*60)
    print("TEST: DuplicateDetector Import")
    print("="*60)
    
    try:
        from metrics.analyse.merging.duplicate_detector import DuplicateDetector
        print("[PASS] DuplicateDetector imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_merger_import():
    """Test ESGMerger can be imported."""
    print("\n" + "="*60)
    print("TEST: ESGMerger Import")
    print("="*60)
    
    try:
        from metrics.analyse.merging.esg_merger import ESGMerger
        print("[PASS] ESGMerger imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_validator_import():
    """Test QualityValidator can be imported."""
    print("\n" + "="*60)
    print("TEST: QualityValidator Import")
    print("="*60)
    
    try:
        from metrics.analyse.validation.quality_validator import QualityValidator
        print("[PASS] QualityValidator imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_prompt_factory_import():
    """Test PromptFactory can be imported."""
    print("\n" + "="*60)
    print("TEST: PromptFactory Import")
    print("="*60)
    
    try:
        from metrics.analyse.prompts.base_prompt import PromptFactory
        print("[PASS] PromptFactory imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        return False


def test_duplicate_detection():
    """Test DuplicateDetector functionality."""
    print("\n" + "="*60)
    print("TEST: DuplicateDetector Functionality")
    print("="*60)
    
    try:
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
        
        print("[PASS] DuplicateDetector works correctly")
        return True
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all structure tests."""
    print("\n" + "="*60)
    print("MODULARIZED ESG ANALYSIS STRUCTURE TEST SUITE")
    print("="*60)
    
    tests = [
        test_chunker_import,
        test_duplicate_detector_import,
        test_merger_import,
        test_validator_import,
        test_prompt_factory_import,
        test_duplicate_detection
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    passed = sum(results)
    total = len(results)
    
    print("\n" + "="*60)
    if passed == total:
        print(f"[SUCCESS] ALL {total} TESTS PASSED")
    else:
        print(f"[PARTIAL] {passed}/{total} TESTS PASSED")
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)

