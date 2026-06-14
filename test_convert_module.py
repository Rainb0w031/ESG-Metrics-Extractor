"""
Test suite for the convert module (Step 3: Dashboard Conversion).

Tests all modularized components:
- Core models and configuration
- Metric extraction
- Value cleaning
- LLM enhancement (mocked)
- Pipeline orchestration
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules can be imported."""
    print("\n=== Testing Imports ===")
    
    try:
        from convert import (
            Metric, DashboardData, ValidationIssue, ConversionConfig,
            MetricExtractor, ValueCleaner,
            NameEnhancer, CategoryGenerator, ImportanceAnalyzer, CombinedProcessor,
            DashboardConverter
        )
        print("[OK] All main imports successful")
        
        from convert.core import Metric, DashboardData, ConversionConfig
        print("[OK] Core module imports successful")
        
        from convert.extraction import MetricExtractor
        print("[OK] Extraction module imports successful")
        
        from convert.cleaning import ValueCleaner
        print("[OK] Cleaning module imports successful")
        
        from convert.validation import (
            UnitValidator, CalculationValidator, ScopeDetector, MetricValidator
        )
        print("[OK] Validation module imports successful")
        
        from convert.enhancement import (
            NameEnhancer, CategoryGenerator, ImportanceAnalyzer, CombinedProcessor
        )
        print("[OK] Enhancement module imports successful")
        
        from convert.pipeline import DashboardConverter
        print("[OK] Pipeline module imports successful")
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_models():
    """Test core data models."""
    print("\n=== Testing Core Models ===")
    
    from convert.core.models import Metric, DashboardData, ValidationIssue
    
    # Test Metric
    metric = Metric(
        metric_name="Carbon Emissions Scope 1",
        value="1000",
        unit="tons CO2e",
        category="E - environmental",
        type="environmental",
        area="E",
        importance="High"
    )
    
    metric_dict = metric.to_dict()
    assert metric_dict['metric_name'] == "Carbon Emissions Scope 1"
    assert metric_dict['value'] == "1000"
    assert metric_dict['importance'] == "High"
    print("[OK] Metric model works correctly")
    
    # Test from_dict
    restored = Metric.from_dict(metric_dict)
    assert restored.metric_name == metric.metric_name
    print("[OK] Metric.from_dict works correctly")
    
    # Test ValidationIssue
    issue = ValidationIssue(
        metric_name="Test Metric",
        issue_type="unit_scale_error",
        severity="critical",
        message="Potential scale error"
    )
    
    issue_dict = issue.to_dict()
    assert issue_dict['severity'] == "critical"
    print("[OK] ValidationIssue model works correctly")
    
    # Test DashboardData
    dashboard = DashboardData(
        company="TestCo",
        year="2024",
        file_path="test.json",
        metrics=[metric_dict]
    )
    
    dashboard_dict = dashboard.to_dict()
    assert dashboard_dict['company'] == "TestCo"
    assert len(dashboard_dict['metrics']) == 1
    print("[OK] DashboardData model works correctly")
    
    return True


def test_config():
    """Test configuration."""
    print("\n=== Testing Configuration ===")
    
    from convert.core.config import ConversionConfig
    
    # Test default config
    config = ConversionConfig()
    assert config.batch_size == 15
    assert config.max_workers == 3
    assert config.enhance_names == True
    print("[OK] Default ConversionConfig works")
    
    # Test custom config
    custom = ConversionConfig(
        batch_size=10,
        max_workers=2,
        enhance_names=False
    )
    assert custom.batch_size == 10
    assert custom.enhance_names == False
    print("[OK] Custom ConversionConfig works")
    
    return True


def test_metric_extractor():
    """Test metric extraction."""
    print("\n=== Testing Metric Extractor ===")
    
    from convert.extraction import MetricExtractor
    
    extractor = MetricExtractor()
    
    # Test with sample analysis data
    sample_analysis = {
        "environmental_comprehensive_analysis": {
            "emissions": {
                "details": ["Carbon emissions from operations"],
                "metrics": {
                    "scope_1_emissions": "1000 tons CO2e",
                    "scope_2_emissions": "500 tons CO2e"
                }
            }
        },
        "social_comprehensive_analysis": {
            "workforce": {
                "metrics": {
                    "total_employees": "50000"
                }
            }
        }
    }
    
    metrics = extractor.extract(sample_analysis, "TestCo", "2024")
    
    assert len(metrics) == 3
    print(f"[OK] Extracted {len(metrics)} metrics")
    
    # Check that metrics have categories assigned
    for metric in metrics:
        assert 'category' in metric
        assert 'area' in metric
        assert metric['area'] in ['E', 'S', 'G']
    print("[OK] Category assignment works correctly")
    
    # Check details are preserved
    scope1 = [m for m in metrics if 'scope_1' in m['metric_name']][0]
    assert len(scope1['details']) > 0
    print("[OK] Details are preserved")
    
    return True


def test_value_cleaner():
    """Test value cleaning."""
    print("\n=== Testing Value Cleaner ===")
    
    from convert.cleaning.value_cleaner import ValueCleaner
    
    cleaner = ValueCleaner()
    
    # Test single metric cleaning
    test_cases = [
        {
            'input': {'metric_name': 'Test', 'value': '1,000 tons CO2e'},
            'expected_value': '1000',
            'expected_unit': 'tons CO2e'
        },
        {
            'input': {'metric_name': 'Test', 'value': '2.5-3.0 gigatons'},
            'expected_value': '2.5-3.0',
            'expected_unit': 'gigatons'
        },
        {
            'input': {'metric_name': 'Test', 'value': '85%'},
            'expected_value': '85',
            'expected_unit': '%'
        },
        {
            'input': {'metric_name': 'Test', 'value': '50000'},
            'expected_value': '50000',
            'expected_unit': None
        }
    ]
    
    for i, case in enumerate(test_cases):
        cleaned = cleaner.clean_metric(case['input'])
        assert cleaned['value'] == case['expected_value'], f"Case {i}: value mismatch"
        assert cleaned['unit'] == case['expected_unit'], f"Case {i}: unit mismatch"
        print(f"[OK] Test case {i+1}: '{case['input']['value']}' -> value='{cleaned['value']}', unit='{cleaned['unit']}'")
    
    # Test batch cleaning
    metrics = [{'metric_name': 'M1', 'value': '100 kg'}, {'metric_name': 'M2', 'value': '50%'}]
    cleaned = cleaner.clean_metrics(metrics)
    assert len(cleaned) == 2
    assert cleaned[0]['unit'] == 'kg'
    assert cleaned[1]['unit'] == '%'
    print("[OK] Batch cleaning works correctly")
    
    return True


def test_metric_validator():
    """Test comprehensive metric validation."""
    print("\n=== Testing Comprehensive Metric Validator ===")
    
    from convert.validation.validators import (
        UnitValidator, CalculationValidator, ScopeDetector, MetricValidator
    )
    
    # Test UnitValidator
    val, unit = UnitValidator.parse_value_and_unit("3,732,075 tons")
    assert val == 3732075.0
    assert unit == "tons"
    print("[OK] UnitValidator.parse_value_and_unit works")
    
    norm = UnitValidator.normalize_to_tons(33.338, "million tons")
    assert norm == 33338000.0
    print("[OK] UnitValidator.normalize_to_tons works")
    
    # Test CalculationValidator
    result = CalculationValidator.validate_reduction(
        "4,445,238 tons",
        "3,732,075 tons",
        "713,163 tons",
        "Scope 2 Reduction"
    )
    assert result['valid'] == True
    print("[OK] CalculationValidator.validate_reduction works")
    
    # Test ScopeDetector
    scope = ScopeDetector.detect_scope(
        "self-built data centers",
        "Energy Usage"  # No 'total' in metric name
    )
    assert scope['scope'] == 'subset'
    print("[OK] ScopeDetector.detect_scope works (subset)")
    
    scope2 = ScopeDetector.detect_scope(
        "company-wide overall emissions",
        "Global Carbon"
    )
    assert scope2['scope'] == 'total'
    print("[OK] ScopeDetector.detect_scope works (total)")
    
    # Test MetricValidator with scale error
    validator = MetricValidator()
    metrics = [
        {
            'metric_name': 'Large Scale Metric',
            'value': '500000',
            'unit': 'million tons'
        },
        {
            'metric_name': 'Normal Metric',
            'value': '100',
            'unit': 'tons'
        }
    ]
    
    validated, issues = validator.validate_metrics(metrics)
    
    assert len(validated) == 2
    print(f"[OK] MetricValidator validated {len(validated)} metrics")
    
    if issues:
        print(f"[OK] Found {len(issues)} validation issues")
        critical_issues = [i for i in issues if i.get('severity') == 'critical']
        if critical_issues:
            print(f"[OK] Detected critical scale issue: {critical_issues[0]['message'][:50]}...")
    
    return True


def test_enhancement_prompts():
    """Test prompt generation."""
    print("\n=== Testing Enhancement Prompts ===")
    
    from convert.enhancement.prompts import (
        get_name_enhancement_prompt,
        get_category_generation_prompt,
        get_importance_analysis_prompt,
        get_combined_processing_prompt
    )
    
    # Test name enhancement prompt
    prompt = get_name_enhancement_prompt("- Test metric", "TestCo", "2024")
    assert "TestCo" in prompt
    assert "2024" in prompt
    assert "enhanced" in prompt.lower()
    print("[OK] Name enhancement prompt generated")
    
    # Test category generation prompt
    prompt = get_category_generation_prompt("- Test metric", "TestCo", "2024")
    assert "category" in prompt.lower()
    print("[OK] Category generation prompt generated")
    
    # Test importance analysis prompt
    prompt = get_importance_analysis_prompt("Metric 1: Test", "TestCo", "2024", 1)
    assert "double materiality" in prompt.lower()
    assert "financial" in prompt.lower()
    assert "impact" in prompt.lower()
    print("[OK] Importance analysis prompt generated")
    
    # Test combined processing prompt
    prompt = get_combined_processing_prompt("Metric 1: Test", "TestCo", "2024", 1)
    assert "enhanced name" in prompt.lower()
    assert "esg category" in prompt.lower()
    assert "importance" in prompt.lower()
    print("[OK] Combined processing prompt generated")
    
    return True


def test_progress_tracker():
    """Test progress tracking."""
    print("\n=== Testing Progress Tracker ===")
    
    from convert.enhancement.combined_processor import ProgressTracker
    
    tracker = ProgressTracker(total_batches=10, total_items=100)
    tracker.start()
    
    # Simulate some progress
    for i in range(5):
        tracker.update(success=True)
    
    tracker.update(success=False)  # One failure
    
    progress = tracker.get_progress(batch_size=10)
    
    assert progress['completed'] == 6
    assert progress['total'] == 10
    assert progress['percentage'] == 60.0
    assert progress['success_rate'] > 80  # 5/6 = 83.3%
    print(f"[OK] Progress: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)")
    print(f"[OK] Success rate: {progress['success_rate']:.1f}%")
    
    return True


def test_dashboard_converter_init():
    """Test DashboardConverter initialization."""
    print("\n=== Testing DashboardConverter ===")
    
    from convert.pipeline import DashboardConverter
    from convert.core.config import ConversionConfig
    
    # Test default initialization
    converter = DashboardConverter()
    assert converter.config is not None
    assert converter.extractor is not None
    assert converter.cleaner is not None
    assert converter.processor is not None
    print("[OK] DashboardConverter initialized with defaults")
    
    # Test with custom config
    config = ConversionConfig(batch_size=5, max_workers=1)
    converter = DashboardConverter(config)
    assert converter.config.batch_size == 5
    print("[OK] DashboardConverter initialized with custom config")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Convert Module Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Models", test_models),
        ("Configuration", test_config),
        ("Metric Extractor", test_metric_extractor),
        ("Value Cleaner", test_value_cleaner),
        ("Metric Validator", test_metric_validator),
        ("Enhancement Prompts", test_enhancement_prompts),
        ("Progress Tracker", test_progress_tracker),
        ("DashboardConverter", test_dashboard_converter_init),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_fn in tests:
        try:
            if test_fn():
                passed += 1
            else:
                failed += 1
                print(f"[FAIL] {name}")
        except Exception as e:
            failed += 1
            print(f"[FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
