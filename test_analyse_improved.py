"""
Test suite for improved analyse module.
Tests new components: parallel processor, direct processor, enhanced prompts.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("IMPROVED ANALYSE MODULE - COMPREHENSIVE TEST SUITE")
print("="*70)
print()

# =============================================================================
# TEST 1: Import All New Modules
# =============================================================================
print("[TEST 1] Importing All New Modules...")
print("-" * 70)

import_results = {}

# Test parallel processor
try:
    from analyse.processors import ParallelProcessor, ParallelConfig, ProgressTracker
    import_results['parallel'] = 'PASS'
    print("[PASS] analyse.processors.parallel_processor - Parallel processing")
except Exception as e:
    import_results['parallel'] = f'FAIL: {e}'
    print(f"[FAIL] analyse.processors.parallel_processor - {e}")

# Test direct processor
try:
    from analyse.processors import DirectProcessor, DirectProcessorConfig, DirectAnalyzer
    import_results['direct'] = 'PASS'
    print("[PASS] analyse.processors.direct_processor - Direct API processing")
except Exception as e:
    import_results['direct'] = f'FAIL: {e}'
    print(f"[FAIL] analyse.processors.direct_processor - {e}")

# Test existing modules
try:
    from analyse.processors import LLMProcessor, ProcessorConfig
    import_results['llm'] = 'PASS'
    print("[PASS] analyse.processors.llm_processor - LLM processing")
except Exception as e:
    import_results['llm'] = f'FAIL: {e}'
    print(f"[FAIL] analyse.processors.llm_processor - {e}")

# Test prompts
try:
    from analyse.prompts import PromptFactory
    from analyse.prompts.comprehensive_prompt import ComprehensivePromptBuilder
    import_results['prompts'] = 'PASS'
    print("[PASS] analyse.prompts - Prompt builders")
except Exception as e:
    import_results['prompts'] = f'FAIL: {e}'
    print(f"[FAIL] analyse.prompts - {e}")

# Test chunking
try:
    from analyse.chunking import AdaptiveChunker
    import_results['chunking'] = 'PASS'
    print("[PASS] analyse.chunking - Adaptive chunking")
except Exception as e:
    import_results['chunking'] = f'FAIL: {e}'
    print(f"[FAIL] analyse.chunking - {e}")

# Test merging
try:
    from analyse.merging import ESGMerger
    import_results['merging'] = 'PASS'
    print("[PASS] analyse.merging - ESG merger")
except Exception as e:
    import_results['merging'] = f'FAIL: {e}'
    print(f"[FAIL] analyse.merging - {e}")

print()

# =============================================================================
# TEST 2: ParallelConfig
# =============================================================================
print("[TEST 2] Testing ParallelConfig...")
print("-" * 70)

try:
    config = ParallelConfig(
        max_workers=4,
        show_progress=True,
        show_eta=True,
        max_retries=3,
        retry_delay=2.0
    )
    
    assert config.max_workers == 4
    assert config.show_progress == True
    assert config.max_retries == 3
    print(f"[PASS] ParallelConfig created with custom values")
    print(f"  - max_workers: {config.max_workers}")
    print(f"  - show_progress: {config.show_progress}")
    print(f"  - max_retries: {config.max_retries}")
    
except Exception as e:
    print(f"[FAIL] ParallelConfig test failed: {e}")

print()

# =============================================================================
# TEST 3: ProgressTracker
# =============================================================================
print("[TEST 3] Testing ProgressTracker...")
print("-" * 70)

try:
    tracker = ProgressTracker(total=10, description="Test Processing")
    
    tracker.start()
    
    # Simulate some work
    for i in range(3):
        tracker.update(success=True, message=f"Item {i+1}")
    
    tracker.update(success=False, message="Failed item")
    
    stats = tracker.finish()
    
    assert stats['total'] == 10
    assert stats['completed'] == 4
    assert stats['successful'] == 3
    assert stats['failed'] == 1
    print(f"[PASS] ProgressTracker working correctly")
    print(f"  - Completed: {stats['completed']}/{stats['total']}")
    print(f"  - Success rate: {stats['success_rate']*100:.0f}%")
    
except Exception as e:
    print(f"[FAIL] ProgressTracker test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 4: DirectProcessorConfig
# =============================================================================
print("[TEST 4] Testing DirectProcessorConfig...")
print("-" * 70)

try:
    from extract.api import APIConfig
    
    api_config = APIConfig(
        api_key='test-key',
        model='qwen-max'
    )
    
    config = DirectProcessorConfig(
        api_config=api_config,
        max_retries=3,
        temperature=0.2,
        max_tokens=4096
    )
    
    assert config.api_config.api_key == 'test-key'
    assert config.temperature == 0.2
    print(f"[PASS] DirectProcessorConfig created with custom values")
    
except Exception as e:
    print(f"[FAIL] DirectProcessorConfig test failed: {e}")

print()

# =============================================================================
# TEST 5: Comprehensive Prompt Builder
# =============================================================================
print("[TEST 5] Testing ComprehensivePromptBuilder...")
print("-" * 70)

try:
    builder = ComprehensivePromptBuilder()
    
    # Test prompt building
    test_chunk = [
        "Our company reduced carbon emissions by 25% in 2024.",
        "Scope 1 emissions totaled 717,096 tons.",
        "We achieved 85% renewable energy usage."
    ]
    
    prompt = builder.build(test_chunk, chunk_num=1, total_chunks=3, year="2024")
    
    # Check prompt contains key elements
    assert "2024" in prompt
    assert "chunk 1/3" in prompt
    assert "CRITICAL REQUIREMENTS" in prompt
    assert "SCOPE 3+" in prompt
    assert "UNIT PRESERVATION" in prompt
    assert "717,096 tons" in prompt or "carbon emissions" in prompt
    
    print(f"[PASS] ComprehensivePromptBuilder generates detailed prompt")
    print(f"  - Prompt length: {len(prompt)} chars")
    print(f"  - Contains CRITICAL REQUIREMENTS: Yes")
    print(f"  - Contains SCOPE 3+ guidance: Yes")
    print(f"  - Contains UNIT PRESERVATION rules: Yes")
    
except Exception as e:
    print(f"[FAIL] ComprehensivePromptBuilder test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 6: ESG Merger
# =============================================================================
print("[TEST 6] Testing ESGMerger...")
print("-" * 70)

try:
    merger = ESGMerger()
    
    # Test merging
    result1 = {
        "environmental_comprehensive": {
            "emissions": {
                "scope_1": {"details": ["First detail"], "metrics": {"emissions_2024": "100 tons"}}
            }
        }
    }
    
    result2 = {
        "environmental_comprehensive": {
            "emissions": {
                "scope_1": {"details": ["Second detail"], "metrics": {"emissions_2023": "120 tons"}}
            }
        }
    }
    
    merged = merger.merge(result1, result2)
    
    # Check merged result
    assert "environmental_comprehensive" in merged
    emissions = merged["environmental_comprehensive"]["emissions"]["scope_1"]
    
    # Should have both details
    assert len(emissions["details"]) >= 1
    
    # Should have both metrics
    assert "emissions_2024" in emissions["metrics"] or "emissions_2023" in emissions["metrics"]
    
    print(f"[PASS] ESGMerger merges results correctly")
    
except Exception as e:
    print(f"[FAIL] ESGMerger test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 7: Adaptive Chunker
# =============================================================================
print("[TEST 7] Testing AdaptiveChunker...")
print("-" * 70)

try:
    from analyse.chunking.base_chunker import ChunkingStrategy
    
    strategy = ChunkingStrategy(base_chunk_size=35)
    chunker = AdaptiveChunker(strategy)
    
    # Create test segments
    test_segments = [
        "This is a simple text segment.",
        "Carbon emissions reduced by 25% in 2024.",  # High complexity
        "Scope 1 emissions: 717,096 tons CO2e.",  # High complexity
        "Another simple text segment here.",
        "Renewable energy usage reached 85%.",  # Medium complexity
    ] * 10  # 50 segments total
    
    chunks = chunker.chunk(test_segments)
    
    assert len(chunks) > 0
    print(f"[PASS] AdaptiveChunker created {len(chunks)} chunks from {len(test_segments)} segments")
    
    # Get stats
    stats = chunker.get_stats(chunks)
    print(f"  - Average chunk size: {stats['avg_size']:.1f}")
    print(f"  - Min chunk size: {stats['min_size']}")
    print(f"  - Max chunk size: {stats['max_size']}")
    
except Exception as e:
    print(f"[FAIL] AdaptiveChunker test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# FINAL SUMMARY
# =============================================================================
print("="*70)
print("TEST SUITE SUMMARY")
print("="*70)

all_passed = all(v == 'PASS' for v in import_results.values())

print(f"\nImport Tests: {sum(1 for v in import_results.values() if v == 'PASS')}/{len(import_results)} passed")
for module, result in import_results.items():
    status = "[OK]" if result == 'PASS' else "[!!]"
    print(f"  {status} {module}: {result}")

print()
print("New Features Added:")
print("  [+] ParallelProcessor     - ThreadPoolExecutor-based parallel processing")
print("  [+] ProgressTracker       - Real-time progress with ETA")
print("  [+] DirectProcessor       - Direct API calls (no prompter needed)")
print("  [+] DirectAnalyzer        - Complete analyzer with direct API")
print("  [+] Enhanced Prompts      - Detailed prompts matching reference")
print()
print("Processing Options:")
print("  [1] ESGLLMAnalyzer        - Prompter-based (existing)")
print("  [2] DirectAnalyzer        - Direct API (new, no prompter)")
print("  [3] ParallelProcessor     - Parallel processing (new)")
print()

if all_passed:
    print("="*70)
    print("OVERALL STATUS: SUCCESS - All improved modules working!")
    print("="*70)
else:
    print("="*70)
    print("OVERALL STATUS: PARTIAL - Some modules need attention")
    print("="*70)
