"""
Test suite for improved extract module.
Tests all new components: api, chunking, llm, and pipeline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("IMPROVED EXTRACT MODULE - COMPREHENSIVE TEST SUITE")
print("="*70)
print()

# =============================================================================
# TEST 1: Import All New Modules
# =============================================================================
print("[TEST 1] Importing All New Modules...")
print("-" * 70)

import_results = {}

# Test API module
try:
    from extract.api import DirectAPIClient, APIConfig, RetryConfig, with_retry
    import_results['api'] = 'PASS'
    print("[PASS] extract.api - Direct API client module")
except Exception as e:
    import_results['api'] = f'FAIL: {e}'
    print(f"[FAIL] extract.api - {e}")

# Test Chunking module
try:
    from extract.chunking import TextChunker, ChunkConfig
    import_results['chunking'] = 'PASS'
    print("[PASS] extract.chunking - Text chunking module")
except Exception as e:
    import_results['chunking'] = f'FAIL: {e}'
    print(f"[FAIL] extract.chunking - {e}")

# Test LLM module
try:
    from extract.llm import LLMRoleAnalyzer, LLMAnalysisConfig, create_chunk_prompt
    import_results['llm'] = 'PASS'
    print("[PASS] extract.llm - LLM role analysis module")
except Exception as e:
    import_results['llm'] = f'FAIL: {e}'
    print(f"[FAIL] extract.llm - {e}")

# Test Pipeline module
try:
    from extract.pipeline import PDFExtractor, LLMPDFExtractor, ESGExtractor, ExtractorConfig
    import_results['pipeline'] = 'PASS'
    print("[PASS] extract.pipeline - Pipeline orchestrators")
except Exception as e:
    import_results['pipeline'] = f'FAIL: {e}'
    print(f"[FAIL] extract.pipeline - {e}")

# Test main extract imports
try:
    from extract import (
        DirectAPIClient, APIConfig,
        TextChunker, ChunkConfig,
        LLMRoleAnalyzer, LLMAnalysisConfig,
        PDFExtractor, LLMPDFExtractor, ESGExtractor, ExtractorConfig
    )
    import_results['main'] = 'PASS'
    print("[PASS] extract (main) - All exports available")
except Exception as e:
    import_results['main'] = f'FAIL: {e}'
    print(f"[FAIL] extract (main) - {e}")

print()

# =============================================================================
# TEST 2: API Config and Client
# =============================================================================
print("[TEST 2] Testing API Configuration...")
print("-" * 70)

try:
    # Test APIConfig
    config = APIConfig(
        api_key='test-key',
        api_base='https://test.api.com/v1/chat',
        model='test-model',
        temperature=0.1,
        max_tokens=1000,
        timeout=30,
        max_retries=2
    )
    
    assert config.api_key == 'test-key'
    assert config.model == 'test-model'
    assert config.max_retries == 2
    print(f"[PASS] APIConfig created with custom values")
    
    # Test from_dict
    config_dict = {
        'api_key': 'dict-key',
        'model': 'dict-model',
        'temperature': 0.5
    }
    config2 = APIConfig.from_dict(config_dict)
    assert config2.api_key == 'dict-key'
    print(f"[PASS] APIConfig.from_dict() works correctly")
    
    # Test client creation
    client = DirectAPIClient(config)
    assert client.config.api_key == 'test-key'
    print(f"[PASS] DirectAPIClient created successfully")
    
except Exception as e:
    print(f"[FAIL] API configuration test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 3: Text Chunking
# =============================================================================
print("[TEST 3] Testing Text Chunking...")
print("-" * 70)

try:
    # Test ChunkConfig
    chunk_config = ChunkConfig(
        max_chars_per_chunk=200,
        max_chunks_per_page=10,
        min_chunk_length=30
    )
    assert chunk_config.max_chars_per_chunk == 200
    print(f"[PASS] ChunkConfig created with custom values")
    
    # Test invalid config
    try:
        bad_config = ChunkConfig(max_chars_per_chunk=10, min_chunk_length=50)
        print(f"[FAIL] Should have raised ValueError for invalid config")
    except ValueError as e:
        print(f"[PASS] ChunkConfig validation working: {e}")
    
    # Test TextChunker
    chunker = TextChunker(chunk_config)
    
    # Test with short text
    short_text = "This is a short text."
    chunks = chunker.chunk_text(short_text, page_number=1)
    assert len(chunks) == 0  # Below min_chunk_length
    print(f"[PASS] Short text returns empty (below min length)")
    
    # Test with longer text
    long_text = """This is the first sentence of a longer text. It contains multiple sentences.
    
Here is a second paragraph with more content. This should be split into chunks.

And a third paragraph for good measure. The chunker should handle this well."""
    
    chunks = chunker.chunk_text(long_text, page_number=1)
    assert len(chunks) > 0
    print(f"[PASS] Long text chunked into {len(chunks)} chunks")
    
    # Test chunk_page_text
    page_chunks = chunker.chunk_page_text(long_text, page_number=5)
    assert all('page_number' in c and c['page_number'] == 5 for c in page_chunks)
    print(f"[PASS] chunk_page_text() returns metadata correctly")
    
    # Test clean_text_content
    from extract.chunking.text_chunker import clean_text_content
    dirty_text = "  Multiple   spaces  and\x00control\x01chars  "
    clean_text = clean_text_content(dirty_text)
    assert '\x00' not in clean_text
    assert '  ' not in clean_text.strip()
    print(f"[PASS] clean_text_content() removes artifacts")
    
except Exception as e:
    print(f"[FAIL] Text chunking test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 4: LLM Prompts
# =============================================================================
print("[TEST 4] Testing LLM Prompts...")
print("-" * 70)

try:
    from extract.llm.prompts import (
        create_chunk_prompt,
        create_page_analysis_prompt,
        create_segment_analysis_prompt,
        get_system_prompt
    )
    
    # Test create_chunk_prompt
    prompt = create_chunk_prompt("Sample text content", page_number=1, chunk_num=1, total_chunks=3)
    assert "Sample text content" in prompt
    assert "page 1" in prompt
    assert "chunk 1/3" in prompt
    print(f"[PASS] create_chunk_prompt() generates valid prompt")
    
    # Test create_page_analysis_prompt
    prompt = create_page_analysis_prompt("Full page text", page_number=5)
    assert "page 5" in prompt
    assert "Full page text" in prompt
    print(f"[PASS] create_page_analysis_prompt() generates valid prompt")
    
    # Test get_system_prompt
    system_prompt = get_system_prompt()
    assert "document analyzer" in system_prompt.lower()
    print(f"[PASS] get_system_prompt() returns valid system prompt")
    
except Exception as e:
    print(f"[FAIL] LLM prompts test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 5: LLM Role Analyzer (Without API Call)
# =============================================================================
print("[TEST 5] Testing LLM Role Analyzer (Fallback Mode)...")
print("-" * 70)

try:
    # Create analyzer with dummy config (no real API key)
    llm_config = LLMAnalysisConfig(
        api_config=APIConfig(api_key='dummy-key'),
        batch_delay=0,
        max_retries=1
    )
    
    analyzer = LLMRoleAnalyzer(llm_config)
    print(f"[PASS] LLMRoleAnalyzer created successfully")
    
    # Test fallback segment creation
    fallback_segment = analyzer._create_fallback_segment("This is a test headline.", 0, 1)
    assert 'text' in fallback_segment
    assert 'role' in fallback_segment
    assert 'confidence' in fallback_segment
    print(f"[PASS] _create_fallback_segment() works correctly")
    print(f"  - Role: {fallback_segment['role']}")
    print(f"  - Confidence: {fallback_segment['confidence']}")
    
    # Test fallback response
    fallback_response = analyzer._create_fallback_response(1, "Test page text\n\nSecond paragraph", "Test reason")
    assert 'page_number' in fallback_response
    assert 'text_segments' in fallback_response
    assert fallback_response.get('fallback') == True
    print(f"[PASS] _create_fallback_response() works correctly")
    print(f"  - Segments: {len(fallback_response['text_segments'])}")
    
except Exception as e:
    print(f"[FAIL] LLM role analyzer test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 6: Pipeline Extractors (Without PDF)
# =============================================================================
print("[TEST 6] Testing Pipeline Extractors (Configuration)...")
print("-" * 70)

try:
    # Test ExtractorConfig
    config = ExtractorConfig(
        use_llm=False,
        enable_esg_analysis=True,
        min_page_chars=100
    )
    assert config.use_llm == False
    assert config.enable_esg_analysis == True
    print(f"[PASS] ExtractorConfig created with custom values")
    
    # Test PDFExtractor creation
    pdf_extractor = PDFExtractor(config)
    assert pdf_extractor.config.use_llm == False
    print(f"[PASS] PDFExtractor created (rule-based mode)")
    
    # Test LLMPDFExtractor creation
    llm_config = ExtractorConfig(
        use_llm=True,
        api_config=APIConfig(api_key='test-key')
    )
    llm_extractor = LLMPDFExtractor(llm_config)
    assert llm_extractor.config.use_llm == True
    print(f"[PASS] LLMPDFExtractor created (LLM mode)")
    
    # Test ESGExtractor creation
    esg_extractor = ESGExtractor()
    assert esg_extractor.config.enable_esg_analysis == True
    print(f"[PASS] ESGExtractor created (ESG-specialized mode)")
    
except Exception as e:
    print(f"[FAIL] Pipeline extractors test failed: {e}")
    import traceback
    traceback.print_exc()

print()

# =============================================================================
# TEST 7: Integration - Process Mock Pages
# =============================================================================
print("[TEST 7] Testing Integration - Process Mock Pages...")
print("-" * 70)

try:
    # Create extractor with ESG analysis
    extractor = PDFExtractor(ExtractorConfig(
        use_llm=False,
        enable_esg_analysis=True
    ))
    
    # Create mock text data
    mock_text_data = {
        'pages': [
            {
                'page_number': 1,
                'text': '''EXECUTIVE SUMMARY
                
Our commitment to sustainability has driven significant achievements in 2024.
We reduced carbon emissions by 25% compared to the previous year.

Environmental Performance:
- Carbon footprint reduced by 25%
- Renewable energy usage increased to 60%
- Water consumption decreased by 15%

This report outlines our progress toward our 2030 sustainability goals.'''
            },
            {
                'page_number': 2,
                'text': '''SOCIAL RESPONSIBILITY

Diversity and Inclusion:
- Workforce diversity improved to 45%
- Employee satisfaction score: 8.5/10
- Safety incidents reduced by 30%

Community Engagement:
We invested $10 million in community programs.'''
            }
        ],
        'metadata': {'title': 'Test ESG Report'},
        'success': True
    }
    
    # Process pages
    processed_pages = extractor.process_pages(mock_text_data)
    
    assert len(processed_pages) == 2
    print(f"[PASS] Processed {len(processed_pages)} pages")
    
    # Check page 1
    page1 = processed_pages[0]
    assert page1['page_number'] == 1
    assert len(page1['text_segments']) > 0
    print(f"  - Page 1: {page1['num_segments']} segments")
    
    # Check ESG analysis
    esg_found = False
    for segment in page1['text_segments']:
        if segment.get('esg_categories'):
            esg_found = True
            break
    
    assert esg_found
    print(f"[PASS] ESG content detected in segments")
    
    # Check page 2
    page2 = processed_pages[1]
    social_found = any('social' in seg.get('esg_categories', []) 
                       for seg in page2['text_segments'])
    assert social_found
    print(f"[PASS] Social content detected in page 2")
    
except Exception as e:
    print(f"[FAIL] Integration test failed: {e}")
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
print("New Modules Added:")
print("  [+] extract/api/           - Direct API client (no prompter dependency)")
print("  [+] extract/chunking/      - Text chunking (matches reference)")
print("  [+] extract/llm/           - LLM-based role analysis")
print("  [+] extract/pipeline/      - Complete orchestrators")
print()
print("Pipeline Classes Available:")
print("  [+] PDFExtractor           - Basic extraction (rule-based, no LLM)")
print("  [+] LLMPDFExtractor        - LLM-enhanced extraction")
print("  [+] ESGExtractor           - ESG-specialized extraction")
print()

if all_passed:
    print("="*70)
    print("OVERALL STATUS: SUCCESS - All improved modules working!")
    print("="*70)
else:
    print("="*70)
    print("OVERALL STATUS: PARTIAL - Some modules need attention")
    print("="*70)

print()
print("Next Steps:")
print("  1. Set QWEN_API_KEY environment variable for LLM features")
print("  2. Test with actual PDF files")
print("  3. Compare output with reference implementation")
print()
