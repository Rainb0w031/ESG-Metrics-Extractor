"""
Metrics - Modular ESG Analysis Pipeline

A modular implementation of the ESG (Environmental, Social, Governance) 
analysis pipeline for PDF reports.

## Pipeline Steps

### Step 1: PDF Extraction (extract/)
Extract text and analyze content from PDF reports.

```python
from extract.pipeline import PDFExtractor, LLMPDFExtractor, ESGExtractor
```

### Step 2: LLM ESG Analysis (analyse/)
Analyze extracted text using LLM for ESG categorization.

```python
from analyse.core import ESGLLMAnalyzer
from analyse.processors import DirectAnalyzer, ParallelProcessor
```

### Step 3: Dashboard Conversion (convert/)
Convert comprehensive analysis to dashboard format.

```python
from convert.pipeline import DashboardConverter
```

### Step 4: Dashboard Integration (integrate/)
Integrate individual dashboards into categorized dashboard.

```python
from integrate.pipeline import DashboardIntegrator
```

## Quick Start

```python
# Full pipeline
from extract.pipeline import LLMPDFExtractor
from analyse.core import ESGLLMAnalyzer
from convert.pipeline import DashboardConverter

# Step 1: Extract from PDF
extractor = LLMPDFExtractor()
extracted = extractor.extract("report.pdf")

# Step 2: Analyze with LLM
analyzer = ESGLLMAnalyzer()
analysis = analyzer.analyze(extracted)

# Step 3: Convert to dashboard
converter = DashboardConverter()
result = converter.convert(
    input_file="analysis.json",
    output_file="dashboard.json",
    company="Company",
    year="2024"
)

# Step 4: Integrate into categorized dashboard
from integrate.pipeline import DashboardIntegrator

integrator = DashboardIntegrator()
result = integrator.integrate(
    dashboard_file="dashboard.json",
    company="Company",
    year="2024"
)
```
"""

__version__ = "1.0.0"
