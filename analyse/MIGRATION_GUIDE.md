# Migration Guide: Monolithic → Modular ESG Analysis

This guide helps you migrate from the old monolithic `analyse.py` script to the new modular `analyse/` module.

## 🎯 Quick Comparison

### Old Way (Monolithic)

```python
from metrics.analyse import ESGLLMAnalyzer

# Single class with 1,700+ lines
analyzer = ESGLLMAnalyzer(which_model="qwen-max")
results = analyzer.analyze_comprehensive_esg(structured_content)
```

### New Way (Modular)

```python
from metrics.analyse.pipeline.esg_analyzer import ESGLLMAnalyzer

# Clean orchestration with modular components
analyzer = ESGLLMAnalyzer(which_model="qwen-max")
results = analyzer.analyze_comprehensive(structured_content)
```

## 📋 Step-by-Step Migration

### Step 1: Update Imports

**Old:**
```python
from metrics.analyse import ESGLLMAnalyzer
```

**New:**
```python
from metrics.analyse.pipeline.esg_analyzer import ESGLLMAnalyzer
from metrics.analyse.core.base import AnalysisConfig
```

### Step 2: Update Method Names

The main method name changed:

**Old:**
```python
results = analyzer.analyze_comprehensive_esg(
    structured_content=content,
    year="2024"
)
```

**New:**
```python
results = analyzer.analyze_comprehensive(
    structured_content=content,
    analysis_type="comprehensive"  # or "environmental", "social", "governance"
)
# Year is auto-extracted from content
```

### Step 3: Update Configuration

Configuration is now done via config objects:

**Old:**
```python
# Configuration was hardcoded in __init__
analyzer = ESGLLMAnalyzer(which_model="qwen-max")
```

**New:**
```python
from metrics.analyse.core.base import AnalysisConfig
from metrics.analyse.processors.base_processor import ProcessorConfig

# Explicit configuration
analysis_config = AnalysisConfig(
    chunk_size=35,
    temperature=0.2,
    max_tokens=4096
)

processor_config = ProcessorConfig(
    max_retries=3,
    retry_delay=2.0,
    timeout=120
)

analyzer = ESGLLMAnalyzer(
    which_model="qwen-max",
    analysis_config=analysis_config,
    processor_config=processor_config
)
```

### Step 4: Update Result Access

Result structure is unchanged, but metadata keys differ slightly:

**Old:**
```python
env = results["environmental_comprehensive_analysis"]
metadata = results["analysis_metadata"]
timestamp = metadata["timestamp"]
```

**New:**
```python
# Same structure
env = results["environmental_comprehensive_analysis"]
metadata = results["analysis_metadata"]
timestamp = metadata["timestamp"]

# New: Quality score available
quality_score = metadata["quality_score"]
```

## 🔄 Component Mapping

Here's how the old monolithic class maps to new modules:

| Old Code | New Module | Notes |
|----------|------------|-------|
| `_create_adaptive_text_chunks()` | `chunking/adaptive_chunker.py` | Now `AdaptiveChunker.chunk()` |
| `_process_chunk_with_llm()` | `processors/llm_processor.py` | Now `LLMProcessor.process()` |
| `_extract_response_text()` | `processors/llm_processor.py` | Now `LLMProcessor._extract_response_text()` |
| `_merge_esg_results()` | `merging/esg_merger.py` | Now `ESGMerger.merge()` |
| `_merge_comprehensive_category()` | `merging/category_merger.py` | Now `CategoryMerger.merge()` |
| `_merge_section_data()` | `merging/section_merger.py` | Now `SectionMerger.merge()` |
| `_is_duplicate_metric()` | `merging/duplicate_detector.py` | Now `DuplicateDetector.is_duplicate_metric()` |
| `_is_duplicate_detail()` | `merging/duplicate_detector.py` | Now `DuplicateDetector.is_duplicate_detail()` |
| `_validate_and_clean_results()` | `validation/quality_validator.py` | Now `QualityValidator.validate()` |
| `_is_valid_metric()` | `validation/metric_validator.py` | Now `MetricValidator.is_valid_metric()` |
| `_is_valid_detail()` | `validation/content_validator.py` | Now `ContentValidator.is_valid_detail()` |
| `_create_comprehensive_analysis_prompt()` | `prompts/comprehensive_prompt.py` | Now `ComprehensivePromptBuilder.build()` |

## 🧩 Using Components Independently

One major benefit of the new architecture is that you can use components independently:

### Example 1: Custom Chunking

```python
from metrics.analyse.chunking.adaptive_chunker import AdaptiveChunker
from metrics.analyse.core.base import AnalysisConfig

# Use chunker standalone
config = AnalysisConfig(chunk_size=50)
chunker = AdaptiveChunker(config)

text_segments = ["segment 1", "segment 2", ...]
chunks = chunker.chunk(text_segments)
```

### Example 2: Duplicate Detection

```python
from metrics.analyse.merging.duplicate_detector import DuplicateDetector

# Use duplicate detector standalone
detector = DuplicateDetector(similarity_threshold=0.8)

# Check metrics
is_dup = detector.is_duplicate_metric(
    "scope_1_emissions_2024",
    "717K tons",
    existing_metrics
)

# Filter duplicate details
unique_details = detector.filter_duplicates(all_details)
```

### Example 3: Validation

```python
from metrics.analyse.validation.quality_validator import QualityValidator

# Use validator standalone
validator = QualityValidator()

# Validate results
validated = validator.validate(raw_results)

# Get quality score
score = validator.get_quality_score(validated)

# Get detailed report
report = validator.get_validation_report(validated)
```

### Example 4: Custom Prompts

```python
from metrics.analyse.prompts.base_prompt import PromptFactory

# Get prompt builder
builder = PromptFactory.get_prompt_builder("environmental")

# Build custom prompt
prompt = builder.build(
    chunk=["text segment 1", "text segment 2"],
    chunk_num=1,
    total_chunks=5,
    year="2024"
)
```

## 🔧 Advanced Customization

### Creating Custom Components

#### Custom Chunker

```python
from metrics.analyse.chunking.base_chunker import BaseChunker

class MyCustomChunker(BaseChunker):
    def chunk(self, text_segments, **kwargs):
        # Your custom chunking logic
        return chunks

# Use it
chunker = MyCustomChunker()
chunks = chunker.chunk(segments)
```

#### Custom Validator

```python
from metrics.analyse.validation.base_validator import BaseValidator

class MyCustomValidator(BaseValidator):
    def validate(self, results):
        # Your custom validation logic
        return validated_results
    
    def get_quality_score(self, results):
        # Your custom scoring logic
        return score

# Use it
validator = MyCustomValidator()
validated = validator.validate(results)
```

#### Custom Prompt Builder

```python
from metrics.analyse.prompts.base_prompt import BasePromptBuilder

class MyCustomPromptBuilder(BasePromptBuilder):
    def build(self, chunk, chunk_num, total_chunks, year="2024"):
        # Your custom prompt building logic
        return prompt

# Use it
builder = MyCustomPromptBuilder()
prompt = builder.build(chunk, 1, 5, "2024")
```

## 🧪 Testing Your Migration

### 1. Run the test suite

```bash
cd metrics
uv run python -m analyse.tests.test_modularized_analyze
```

### 2. Compare outputs

```python
# Old analyzer
from metrics.analyse import ESGLLMAnalyzer as OldAnalyzer

# New analyzer
from metrics.analyse.pipeline.esg_analyzer import ESGLLMAnalyzer as NewAnalyzer

# Run both
old_results = old_analyzer.analyze_comprehensive_esg(content)
new_results = new_analyzer.analyze_comprehensive(content)

# Compare (structure should be identical)
assert old_results.keys() == new_results.keys()
```

### 3. Validate quality

```python
from metrics.analyse.validation.quality_validator import QualityValidator

validator = QualityValidator()

# Get quality scores
old_score = validator.get_quality_score(old_results)
new_score = validator.get_quality_score(new_results)

print(f"Old: {old_score:.2f}, New: {new_score:.2f}")
```

## ⚠️ Breaking Changes

### 1. Method Rename

- `analyze_comprehensive_esg()` → `analyze_comprehensive()`

### 2. Parameter Changes

- `year` parameter removed (now auto-extracted)
- New `analysis_type` parameter added

### 3. Configuration

- Configuration now done via config objects instead of `__init__` params
- More explicit and type-safe

### 4. Imports

- All imports now from `metrics.analyse.*` submodules
- Main entry point: `metrics.analyse.pipeline.esg_analyzer`

## ✅ Verification Checklist

After migration, verify:

- [ ] Imports updated
- [ ] Method names updated  
- [ ] Configuration using config objects
- [ ] Tests passing
- [ ] Output structure unchanged
- [ ] Quality scores comparable
- [ ] Logging works correctly
- [ ] Error handling preserved

## 🆘 Troubleshooting

### Issue: Import errors

**Problem**: `ModuleNotFoundError: No module named 'metrics.analyse.pipeline'`

**Solution**: Ensure all `__init__.py` files exist in subdirectories.

### Issue: Quality score lower

**Problem**: New analyzer produces lower quality scores.

**Solution**: Check configuration - ensure chunk_size, temperature, and other parameters match the old defaults.

### Issue: Different results

**Problem**: Results differ between old and new analyzer.

**Solution**: This is expected due to LLM non-determinism. Ensure:
- Same model used (`which_model`)
- Same temperature
- Same chunk size
- Compare multiple runs to see variance

### Issue: Missing metadata

**Problem**: `quality_score` not in metadata.

**Solution**: This is a new field. Update code to handle both old and new format:

```python
quality_score = metadata.get("quality_score", 0.0)
```

## 📚 Additional Resources

- [Module README](./README.md) - Complete module documentation
- [Test Suite](./tests/test_modularized_analyze.py) - Example usage
- [Reference Implementation](../reports-core-scripts-reference/02-llm-analysis/) - Original script

## 🎓 Next Steps

After migrating:

1. **Run tests** to ensure everything works
2. **Review logs** to understand the new pipeline flow
3. **Explore components** to leverage modularity
4. **Customize** components for your specific needs
5. **Contribute** improvements back to the codebase

Happy migrating! 🚀

