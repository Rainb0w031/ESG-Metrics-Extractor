# ESG Analysis Module

Modular, maintainable ESG (Environmental, Social, Governance) analysis system using LLM-based extraction.

## 🎯 Overview

This module provides a comprehensive system for extracting and categorizing ESG information from sustainability reports. It has been refactored from a monolithic script into a modular architecture with clear separation of concerns.

## 📁 Module Structure

```
analyse/
├── core/              # Base classes and interfaces
│   ├── base.py        # BaseAnalyzer, AnalysisConfig
│   └── models.py      # Pydantic models for LLM responses
├── chunking/          # Text chunking strategies
│   ├── base_chunker.py
│   └── adaptive_chunker.py
├── prompts/           # Prompt building system
│   ├── base_prompt.py         # BasePromptBuilder, PromptFactory
│   ├── comprehensive_prompt.py
│   ├── environmental_prompt.py
│   ├── social_prompt.py
│   └── governance_prompt.py
├── processors/        # LLM processing
│   ├── base_processor.py
│   └── llm_processor.py       # LLM calls, retries, response extraction
├── merging/           # Result merging
│   ├── base_merger.py
│   ├── duplicate_detector.py  # Fuzzy matching for duplicates
│   ├── section_merger.py
│   ├── category_merger.py
│   └── esg_merger.py          # Main ESG merger
├── validation/        # Result validation
│   ├── base_validator.py
│   ├── content_validator.py
│   ├── metric_validator.py
│   ├── structure_validator.py
│   └── quality_validator.py   # Orchestrates all validation
├── pipeline/          # Main integration
│   └── esg_analyzer.py        # ESGLLMAnalyzer - main entry point
├── utils/             # Utility functions
└── tests/             # Test suite
    └── test_modularized_analyze.py
```

## 🚀 Quick Start

### Basic Usage

```python
from metrics.analyse.pipeline.esg_analyzer import ESGLLMAnalyzer
from metrics.analyse.core.base import AnalysisConfig

# Create analyzer
config = AnalysisConfig(chunk_size=35, temperature=0.2)
analyzer = ESGLLMAnalyzer(which_model="qwen-max", analysis_config=config)

# Analyze structured content
results = analyzer.analyze_comprehensive(
    structured_content=pdf_content,  # From PDF extraction
    analysis_type="comprehensive"     # or "environmental", "social", "governance"
)

# Access results
environmental = results["environmental_comprehensive_analysis"]
social = results["social_comprehensive_analysis"]
governance = results["governance_comprehensive_analysis"]
metadata = results["analysis_metadata"]
```

### Configuration

```python
from metrics.analyse.core.base import AnalysisConfig
from metrics.analyse.processors.base_processor import ProcessorConfig

# Analysis configuration
analysis_config = AnalysisConfig(
    chunk_size=35,                    # Base chunk size
    base_chunk_size_adaptive=35,      # Adaptive chunking base
    high_complexity_chunk_size=20,    # High complexity chunk size
    max_chunks_to_merge=50,           # Max chunks before merging
    temperature=0.2,                  # LLM temperature
    max_tokens=4096                   # Max response tokens
)

# Processor configuration
processor_config = ProcessorConfig(
    max_retries=3,                    # Max retry attempts
    retry_delay=2.0,                  # Delay between retries
    timeout=120,                      # Request timeout
    temperature=0.2,                  # LLM temperature
    enable_response_validation=True   # Enable validation
)

# Create analyzer with configs
analyzer = ESGLLMAnalyzer(
    which_model="qwen-max",
    analysis_config=analysis_config,
    processor_config=processor_config
)
```

## 🔧 Component Overview

### 1. Chunking (`chunking/`)

**Purpose**: Split large texts into manageable chunks for LLM processing.

**Key Features**:
- Adaptive chunking based on content complexity
- Configurable chunk sizes
- Intelligent merging to avoid too many small chunks

**Usage**:
```python
from metrics.analyse.chunking.adaptive_chunker import AdaptiveChunker

chunker = AdaptiveChunker(config)
chunks = chunker.chunk(text_segments)
```

### 2. Prompts (`prompts/`)

**Purpose**: Build high-quality prompts for different analysis types.

**Key Features**:
- Factory pattern for prompt builders
- Comprehensive requirements embedded
- Unit preservation rules
- Scope 3+ understanding
- Examples and formatting rules

**Usage**:
```python
from metrics.analyse.prompts.base_prompt import PromptFactory

builder = PromptFactory.get_prompt_builder("comprehensive")
prompt = builder.build(chunk, chunk_num=1, total_chunks=10, year="2024")
```

### 3. Processing (`processors/`)

**Purpose**: Execute LLM calls with robust error handling.

**Key Features**:
- Automatic retries with exponential backoff
- Multiple response format support (Prompter, OpenAI, DashScope)
- JSON extraction and parsing
- Response cleaning (markdown removal, etc.)
- Comprehensive logging

**Usage**:
```python
from metrics.analyse.processors.llm_processor import LLMProcessor

processor = LLMProcessor(analyzer, config)
result = processor.process(prompt, "comprehensive")
```

### 4. Merging (`merging/`)

**Purpose**: Combine results from multiple chunks without duplicates.

**Key Features**:
- Fuzzy duplicate detection (metrics and details)
- Hierarchical merging (category → section → subsection)
- Jaccard similarity for text comparison
- Year suffix handling
- Preserves all unique information

**Usage**:
```python
from metrics.analyse.merging.esg_merger import ESGMerger

merger = ESGMerger()
merged = merger.merge_all(chunk_results, "comprehensive")
```

### 5. Validation (`validation/`)

**Purpose**: Ensure result quality and consistency.

**Key Features**:
- Structure validation (required keys, types)
- Content validation (detail length, format)
- Metric validation (name/value requirements)
- Quality scoring
- Recursive cleaning of invalid data

**Usage**:
```python
from metrics.analyse.validation.quality_validator import QualityValidator

validator = QualityValidator()
validated = validator.validate(results)
quality_score = validator.get_quality_score(validated)
```

### 6. Pipeline (`pipeline/`)

**Purpose**: Orchestrate all components into a complete analysis pipeline.

**Key Features**:
- Main entry point (`ESGLLMAnalyzer`)
- Inherits from `BasePromptModel` for LLM access
- Complete pipeline: chunk → prompt → process → merge → validate
- Metadata generation
- Comprehensive logging

## 🧪 Testing

Run the test suite:

```bash
cd metrics
uv run python -m analyse.tests.test_modularized_analyze
```

Tests cover:
- ✅ Adaptive chunking
- ✅ Duplicate detection
- ✅ ESG merging
- ✅ Quality validation
- ✅ Prompt building
- ✅ Integrated analyzer structure

## 📊 Quality Standards

This module maintains the high quality standards from the reference implementation:

1. **Comprehensive Extraction**
   - All numbers, percentages, and metrics
   - Quantitative and qualitative data
   - Historical trends and targets
   - Multiple dimensions (region, time, unit)

2. **Unit Preservation**
   - No unit conversions
   - Exact preservation as mentioned in text
   - Compound unit handling (e.g., "tons per million RMB")

3. **Duplicate Detection**
   - Fuzzy matching for similar metrics
   - Text similarity for details
   - Year suffix handling

4. **Validation**
   - Minimum length requirements
   - Content quality checks
   - Structure validation

5. **Scope 3+ Understanding**
   - Distinguishes traditional Scope 3 from Scope 3+
   - Platform ecosystem reductions
   - Enabled and engaged emissions

## 📝 Migration Guide

See [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) for detailed instructions on migrating from the old monolithic script to the new modular system.

## 🎓 Architecture Benefits

### Modularity
- Each component has a single responsibility
- Easy to test in isolation
- Clear interfaces between components

### Maintainability
- Changes localized to specific modules
- No cascading changes
- Clear documentation

### Extensibility
- New chunking strategies: implement `BaseChunker`
- New processors: implement `BaseProcessor`
- New validators: implement `BaseValidator`
- New prompt builders: implement `BasePromptBuilder`

### Testability
- Unit tests for each component
- Integration tests for pipeline
- Mock-friendly design

## 🔍 Logging

All components use `loguru` for comprehensive logging:

```python
from loguru import logger

# Configure logging
logger.add("logs/esg_analysis.log", rotation="1 day", retention="30 days")

# Run analysis (logs automatically)
results = analyzer.analyze_comprehensive(structured_content)
```

## 🤝 Contributing

When adding new features:

1. Follow the existing architecture patterns
2. Implement appropriate base classes
3. Add comprehensive docstrings
4. Write tests
5. Update documentation

## 📄 License

[Your License Here]

