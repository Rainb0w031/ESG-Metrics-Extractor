# ESG Metrics Pipeline

A modular Python pipeline for extracting and analyzing ESG (Environmental, Social, and Governance) metrics from PDF sustainability reports. This tool processes PDFs through a 4-step pipeline, from raw text extraction to dashboard-ready metrics.

## Features

- **Multi-Library PDF Extraction**: Combines PyPDF2, PyMuPDF (fitz), and pdfplumber with automatic fallback
- **LLM-Powered Analysis**: Uses Qwen-Max via DashScope API for semantic ESG categorization
- **Modular Architecture**: 4 independent steps, each with focused, testable modules
- **Parallel Processing**: Batch processing with configurable workers for LLM calls
- **Duplicate Detection**: Automatic deduplication across metrics and dashboards
- **Comprehensive Validation**: Unit normalization, calculation validation, scope detection

## Pipeline Overview

```
PDF Report → [1. Extract] → [2. Analyze] → [3. Convert] → [4. Integrate] → Dashboard
```

| Step | Module | Description |
|------|--------|-------------|
| 1 | `extract/` | Extract text from PDF with multi-library fallback |
| 2 | `analyse/` | LLM-based ESG content analysis and categorization |
| 3 | `convert/` | Convert analysis to dashboard format with LLM enhancement |
| 4 | `integrate/` | Integrate into categorized multi-company dashboard |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/esg-metrics-pipeline.git
cd esg-metrics-pipeline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
# or with uv:
uv sync
```

### Configuration

Create a `.env` file with your API credentials:

```bash
cp .env.example .env
# Edit .env with your DashScope API key
```

Required environment variables:
```
DASHSCOPE_API_KEY=your-api-key-here
```

### Running the Pipeline

**Full pipeline from PDF:**
```bash
python run_pipeline.py report.pdf --company "Amazon" --year 2022
```

**With custom output directory:**
```bash
python run_pipeline.py report.pdf --company "Amazon" --year 2022 --output-dir ./results
```

**Skip integration (stop after conversion):**
```bash
python run_pipeline.py report.pdf --company "Amazon" --year 2022 --skip-integration
```

**Resume from intermediate step:**
```bash
# Start from existing extraction
python run_pipeline.py report.pdf --company "Amazon" --year 2022 \
    --extraction-file output/amazon_2022_extraction.json

# Start from existing analysis
python run_pipeline.py report.pdf --company "Amazon" --year 2022 \
    --analysis-file output/amazon_2022_analysis.json
```

## Module Usage

### Step 1: PDF Extraction

```python
from extract.pipeline import LLMPDFExtractor, ExtractorConfig
from extract.api import APIConfig

config = ExtractorConfig(
    use_llm=True,
    api_config=APIConfig.from_env(),
    enable_esg_analysis=True
)

extractor = LLMPDFExtractor(config)
result = extractor.extract("report.pdf", "output/extraction.json")
```

### Step 2: LLM ESG Analysis

```python
from analyse.pipeline import ESGLLMAnalyzer
import json

# Load extraction result
with open("output/extraction.json") as f:
    extraction_data = json.load(f)

analyzer = ESGLLMAnalyzer()
result = analyzer.analyze_comprehensive(extraction_data, analysis_type="comprehensive")
```

### Step 3: Dashboard Conversion

```python
from convert.pipeline import DashboardConverter
from convert.core.config import ConversionConfig

config = ConversionConfig(
    batch_size=15,
    max_workers=3,
    enhance_names=True
)

converter = DashboardConverter(config)
result = converter.convert(
    input_file="output/analysis.json",
    output_file="output/dashboard.json",
    company="Amazon",
    year="2022"
)
```

### Step 4: Dashboard Integration

```python
from integrate.pipeline import DashboardIntegrator
from integrate.core.config import IntegrationConfig

config = IntegrationConfig(
    categorized_dashboard_path="dashboard/categorized.json",
    clean_duplicates=True
)

integrator = DashboardIntegrator(config)
result = integrator.integrate(
    dashboard_file="output/dashboard.json",
    company="Amazon",
    year="2022"
)
```

## Project Structure

```
metrics/
├── run_pipeline.py          # End-to-end pipeline runner
├── extract/                 # Step 1: PDF Extraction
│   ├── api/                 # Direct API client with retry
│   ├── chunking/            # Text chunking strategies
│   ├── llm/                 # LLM-based role analysis
│   ├── readers/             # PDF reader implementations
│   ├── classification/      # Text role classification
│   ├── segmentation/        # Text segmentation
│   ├── esg/                 # ESG keyword analysis
│   ├── validation/          # Page validation
│   └── pipeline/            # Extraction orchestrator
├── analyse/                 # Step 2: LLM ESG Analysis
│   ├── core/                # Base classes and config
│   ├── chunking/            # Adaptive text chunking
│   ├── processors/          # LLM processors (direct/parallel)
│   ├── prompts/             # ESG analysis prompts
│   ├── merging/             # Result merging with dedup
│   ├── validation/          # Quality validation
│   └── pipeline/            # Analysis orchestrator
├── convert/                 # Step 3: Dashboard Conversion
│   ├── core/                # Data models and config
│   ├── extraction/          # Metric extraction from JSON
│   ├── cleaning/            # Value cleaning and normalization
│   ├── validation/          # Metric validation
│   ├── enhancement/         # LLM-based metric enhancement
│   └── pipeline/            # Conversion orchestrator
├── integrate/               # Step 4: Dashboard Integration
│   ├── core/                # Models and config
│   ├── deduplication/       # Duplicate detection
│   └── pipeline/            # Integration orchestrator
└── tests/                   # Test suites
    ├── test_extract_improved.py
    ├── test_analyse_improved.py
    ├── test_convert_module.py
    └── test_integrate_module.py
```

## Testing

Run all tests:
```bash
python -m pytest test_*.py -v
```

Run individual test suites:
```bash
python -m pytest test_extract_improved.py -v
python -m pytest test_analyse_improved.py -v
python -m pytest test_convert_module.py -v
python -m pytest test_integrate_module.py -v
```

Test API connection:
```bash
python test_api_connection.py
```

## Requirements

- Python 3.11+
- DashScope API key (for Qwen-Max LLM)
- Dependencies: See `pyproject.toml`

Key dependencies:
- `pypdf2`, `pymupdf`, `pdfplumber` - PDF reading
- `requests` - API calls
- `loguru` - Logging
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration

## Output Format

### Dashboard JSON Structure

```json
{
  "company": "Amazon",
  "year": "2022",
  "metrics": [
    {
      "metric_name": "Carbon Emissions Reduction",
      "value": "20",
      "unit": "%",
      "category": "Climate Change",
      "area": "E",
      "importance": {
        "financial_materiality": "High",
        "impact_materiality": "High"
      }
    }
  ],
  "validation_summary": {
    "total_issues": 0
  }
}
```

### Categorized Dashboard Structure

```json
{
  "Amazon_2022": {
    "company": "Amazon",
    "year": "2022",
    "metrics": [...],
    "integration_metadata": {
      "integration_date": "2024-01-15T10:30:00",
      "metrics_processed": 150,
      "duplicate_cleaning": {
        "duplicates_removed": 5
      }
    }
  },
  "Alibaba_2023": {...}
}
```

## Configuration Options

### Pipeline Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `output` | Output directory for intermediate files |
| `--skip-integration` | `false` | Stop after conversion step |
| `--no-llm-extraction` | `false` | Use rule-based extraction |
| `--batch-size` | `15` | LLM processing batch size |
| `--workers` | `3` | Parallel workers for LLM calls |

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DASHSCOPE_API_KEY` | Yes | DashScope API key for Qwen |
| `DASHSCOPE_BASE_URL` | No | API base URL (default: dashscope endpoint) |

## License

MIT License

## Contributing

Contributions welcome! Please read the architecture overview in `ARCHITECTURE_OVERVIEW.md` before contributing.
