"""
Test suite for the integrate module (Step 4: Dashboard Integration).

Tests all modularized components:
- Core models and configuration
- Duplicate detection
- Dashboard integration
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all modules can be imported."""
    print("\n=== Testing Imports ===")
    
    try:
        from integrate import (
            IntegrationMetadata, DashboardEntry, IntegrationConfig,
            DuplicateDetector, MetricSignature,
            DashboardIntegrator
        )
        print("[OK] All main imports successful")
        
        from integrate.core import IntegrationMetadata, DashboardEntry, IntegrationConfig
        print("[OK] Core module imports successful")
        
        from integrate.deduplication import DuplicateDetector, MetricSignature
        print("[OK] Deduplication module imports successful")
        
        from integrate.pipeline import DashboardIntegrator
        print("[OK] Pipeline module imports successful")
        
        return True
        
    except ImportError as e:
        print(f"[FAIL] Import error: {e}")
        return False


def test_models():
    """Test core data models."""
    print("\n=== Testing Core Models ===")
    
    from integrate.core.models import (
        IntegrationMetadata, DashboardEntry, CategorizedDashboard
    )
    
    # Test IntegrationMetadata
    metadata = IntegrationMetadata(
        total_metrics_processed=100
    )
    
    assert metadata.integration_date != ""
    assert metadata.total_metrics_processed == 100
    assert 'cleaning_date' in metadata.duplicate_cleaning
    print("[OK] IntegrationMetadata model works correctly")
    
    # Test to_dict/from_dict
    meta_dict = metadata.to_dict()
    restored = IntegrationMetadata.from_dict(meta_dict)
    assert restored.total_metrics_processed == 100
    print("[OK] IntegrationMetadata serialization works")
    
    # Test DashboardEntry
    entry = DashboardEntry(
        company="Amazon",
        year="2024",
        file_path="test.json",
        metrics=[{'metric_name': 'Test', 'value': '100'}]
    )
    
    assert entry.key == "Amazon_2024"
    assert entry.metrics_count == 1
    print("[OK] DashboardEntry model works correctly")
    
    # Test CategorizedDashboard
    dashboard = CategorizedDashboard()
    dashboard.add_entry(entry)
    
    assert dashboard.total_entries == 1
    assert dashboard.total_metrics == 1
    assert dashboard.get_entry("Amazon", "2024") is not None
    print("[OK] CategorizedDashboard model works correctly")
    
    return True


def test_config():
    """Test configuration."""
    print("\n=== Testing Configuration ===")
    
    from integrate.core.config import IntegrationConfig
    
    # Test default config
    config = IntegrationConfig()
    assert config.clean_duplicates == True
    assert config.replace_existing == True
    assert len(config.signature_fields) == 8
    print("[OK] Default IntegrationConfig works")
    
    # Test custom config
    custom = IntegrationConfig(
        categorized_dashboard_path="custom/path.json",
        clean_duplicates=False
    )
    assert custom.clean_duplicates == False
    # Path separator may vary by OS
    path_str = str(custom.get_dashboard_path())
    assert "custom" in path_str and "path.json" in path_str
    print("[OK] Custom IntegrationConfig works")
    
    return True


def test_metric_signature():
    """Test metric signature creation."""
    print("\n=== Testing Metric Signature ===")
    
    from integrate.deduplication.duplicate_detector import MetricSignature
    
    # Test signature creation
    metric = {
        'metric_name': 'Carbon Emissions',
        'value': '1000',
        'unit': 'tons',
        'company': 'Amazon',
        'year': '2024',
        'category': 'E - environmental',
        'type': 'environmental',
        'area': 'E'
    }
    
    sig = MetricSignature.from_metric(metric)
    
    assert sig.metric_name == 'Carbon Emissions'
    assert sig.value == '1000'
    assert sig.company == 'Amazon'
    print("[OK] MetricSignature.from_metric works")
    
    # Test string representation
    sig_str = str(sig)
    assert 'carbon emissions' in sig_str
    assert 'amazon' in sig_str
    print(f"[OK] Signature string: {sig_str[:50]}...")
    
    # Test equality
    sig2 = MetricSignature.from_metric(metric)
    assert sig == sig2
    print("[OK] MetricSignature equality works")
    
    # Test hash (for set operations)
    sig_set = {sig, sig2}
    assert len(sig_set) == 1  # Should be same signature
    print("[OK] MetricSignature hashing works")
    
    return True


def test_duplicate_detector():
    """Test duplicate detection."""
    print("\n=== Testing Duplicate Detector ===")
    
    from integrate.deduplication import DuplicateDetector
    
    detector = DuplicateDetector()
    
    # Test signature creation
    metric = {
        'metric_name': 'Test Metric',
        'value': '100',
        'unit': 'kg',
        'company': 'TestCo',
        'year': '2024',
        'category': 'E',
        'type': 'environmental',
        'area': 'E'
    }
    
    sig = detector.create_signature(metric)
    assert 'test metric' in sig
    assert 'testco' in sig
    print("[OK] create_signature works")
    
    # Test duplicate detection
    metrics = [
        {'metric_name': 'Metric A', 'value': '100', 'unit': 'kg', 'company': 'Co', 'year': '2024', 'category': 'E', 'type': 'e', 'area': 'E'},
        {'metric_name': 'Metric B', 'value': '200', 'unit': 'kg', 'company': 'Co', 'year': '2024', 'category': 'E', 'type': 'e', 'area': 'E'},
        {'metric_name': 'Metric A', 'value': '100', 'unit': 'kg', 'company': 'Co', 'year': '2024', 'category': 'E', 'type': 'e', 'area': 'E'},  # Duplicate
    ]
    
    unique, duplicates = detector.detect_duplicates(metrics, "TestCo_2024")
    
    assert len(unique) == 2
    assert len(duplicates) == 1
    print(f"[OK] detect_duplicates: {len(unique)} unique, {len(duplicates)} duplicates")
    
    # Test summary generation
    summary = detector.get_duplicate_summary(3, 2, duplicates)
    assert summary['original_metrics_count'] == 3
    assert summary['unique_metrics_count'] == 2
    assert summary['duplicates_removed'] == 1
    print("[OK] get_duplicate_summary works")
    
    return True


def test_dashboard_integrator_init():
    """Test DashboardIntegrator initialization."""
    print("\n=== Testing DashboardIntegrator ===")
    
    from integrate.pipeline import DashboardIntegrator
    from integrate.core.config import IntegrationConfig
    
    # Test default initialization
    integrator = DashboardIntegrator()
    assert integrator.config is not None
    assert integrator.duplicate_detector is not None
    print("[OK] DashboardIntegrator initialized with defaults")
    
    # Test with custom config
    config = IntegrationConfig(clean_duplicates=False)
    integrator = DashboardIntegrator(config)
    assert integrator.config.clean_duplicates == False
    print("[OK] DashboardIntegrator initialized with custom config")
    
    return True


def test_integration_result():
    """Test IntegrationResult model."""
    print("\n=== Testing IntegrationResult ===")
    
    from integrate.pipeline.integrator import IntegrationResult
    
    # Test successful result
    result = IntegrationResult(
        success=True,
        entry_key="Amazon_2024",
        metrics_added=100,
        duplicates_removed=5,
        total_entries=10,
        total_metrics=500
    )
    
    assert result.success == True
    assert "Amazon_2024" in str(result)
    assert "100 metrics" in str(result)
    print(f"[OK] Success result: {result}")
    
    # Test failed result
    failed = IntegrationResult(
        success=False,
        message="File not found"
    )
    
    assert failed.success == False
    assert "File not found" in str(failed)
    print(f"[OK] Failed result: {failed}")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Integrate Module Test Suite")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Models", test_models),
        ("Configuration", test_config),
        ("Metric Signature", test_metric_signature),
        ("Duplicate Detector", test_duplicate_detector),
        ("DashboardIntegrator", test_dashboard_integrator_init),
        ("IntegrationResult", test_integration_result),
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
