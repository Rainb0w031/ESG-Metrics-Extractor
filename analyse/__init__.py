"""
ESG Analysis Module - High-Quality LLM Analysis for ESG Content

This module provides modular, testable components for analyzing ESG reports with LLM.
Maintains all quality standards from the reference implementation while improving maintainability.

## Architecture

```
analyse/
├── core/           # Base classes, config, models
├── chunking/       # Adaptive text chunking
├── processors/     # LLM processing (sequential, parallel, direct API)
├── merging/        # Result merging & deduplication
├── validation/     # Quality validation
├── prompts/        # Prompt templates & builders
└── pipeline/       # ESGLLMAnalyzer orchestrator
```

## Public API

### Option 1: Prompter-based (requires prompter library)
```python
from analyse.pipeline.esg_analyzer import ESGLLMAnalyzer
from analyse.core.config import AnalysisConfig

analyzer = ESGLLMAnalyzer(which_model="qwen-max")
results = analyzer.analyze_comprehensive(structured_content, "comprehensive")
```

### Option 2: Direct API (no prompter dependency)
```python
from analyse.processors import DirectAnalyzer, DirectProcessorConfig

analyzer = DirectAnalyzer()
results = analyzer.analyze_with_prompts(prompts, "Environmental", parallel=True)
```

### Option 3: Parallel processing
```python
from analyse.processors import ParallelProcessor, ParallelConfig

processor = ParallelProcessor(process_func, ParallelConfig(max_workers=4))
results = processor.process_chunks(prompts, "Environmental", merge_func)
```
"""

__version__ = "2.0.0"

# Note: Don't import here to avoid circular dependencies and prompter requirement
# Import directly from submodules as needed:
#   from analyse.pipeline.esg_analyzer import ESGLLMAnalyzer  (requires prompter)
#   from analyse.processors import DirectAnalyzer  (no prompter needed)
#   from analyse.processors import ParallelProcessor  (for parallel processing)
#   from analyse.core.config import AnalysisConfig
#   from analyse.chunking.adaptive_chunker import AdaptiveChunker
#   etc.

__all__ = []

