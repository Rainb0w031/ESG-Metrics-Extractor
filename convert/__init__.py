"""
Dashboard Conversion Module - Step 3 of ESG Pipeline

Converts comprehensive ESG analysis to dashboard format with:
- Metric extraction from nested JSON structures
- Value cleaning and unit separation
- LLM-enhanced metric names
- Category generation
- Importance analysis using double materiality
- Parallel processing for efficiency

## Architecture

```
convert/
├── core/           # Models and configuration
├── extraction/     # Metric extraction from analysis
├── cleaning/       # Value cleaning and unit separation
├── enhancement/    # LLM-based enhancements
└── pipeline/       # DashboardConverter orchestrator
```

## Usage

```python
from convert.pipeline import DashboardConverter

converter = DashboardConverter()
result = converter.convert(
    input_file="comprehensive_analysis.json",
    output_file="dashboard.json",
    company="Amazon",
    year="2024"
)
```
"""

__version__ = "1.0.0"

# Core
from .core.models import Metric, DashboardData, ValidationIssue
from .core.config import ConversionConfig

# Extraction
from .extraction import MetricExtractor

# Cleaning
from .cleaning import ValueCleaner

# Validation
from .validation import (
    UnitValidator,
    CalculationValidator,
    ScopeDetector,
    MetricValidator,
)

# Enhancement
from .enhancement import (
    NameEnhancer,
    CategoryGenerator,
    ImportanceAnalyzer,
    CombinedProcessor,
)

# Pipeline
from .pipeline import DashboardConverter

__all__ = [
    # Core
    'Metric',
    'DashboardData',
    'ValidationIssue',
    'ConversionConfig',
    # Extraction
    'MetricExtractor',
    # Cleaning
    'ValueCleaner',
    # Validation
    'UnitValidator',
    'CalculationValidator',
    'ScopeDetector',
    'MetricValidator',
    # Enhancement
    'NameEnhancer',
    'CategoryGenerator',
    'ImportanceAnalyzer',
    'CombinedProcessor',
    # Pipeline
    'DashboardConverter',
]
