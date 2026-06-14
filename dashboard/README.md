# ESG Dashboard

Flask web app for exploring, visualizing, and comparing the ESG metrics produced by
the modular `metrics/` pipeline (Step 4 output).

## Data Source

The dashboard reads `llm_enhanced_esg_data_categorized.json` in this folder. That file
is produced/updated by the pipeline's integration step (`metrics/run_pipeline.py`),
which converts each processed report into dashboard-ready, categorized metrics.

To add a new report, run the pipeline; the integration step merges the new company/year
entry into `llm_enhanced_esg_data_categorized.json`.

## Quick Start

Run from the `metrics/` project (the dashboard imports `extract.api` for API config):

```bash
# from metrics/
pip install -r dashboard/requirements.txt
python dashboard/app.py
```

Then open:

- Home:          http://localhost:5000
- Exploration:   http://localhost:5000/exploration
- Visualization: http://localhost:5000/visualization
- Benchmarking:  http://localhost:5000/benchmarking

## API Configuration

The dynamic comparison feature (`dynamic_comparison_analyzer.py`) calls an LLM using the
same configuration as the rest of the project via `extract.api.APIConfig.from_env()`.
Configure it through the project `.env` (DeepSeek by default):

```
DEEPSEEK_API_KEY=sk-...
LLM_API_BASE=https://api.deepseek.com/chat/completions
LLM_MODEL=deepseek-v4-pro
```

No API keys are hardcoded. Never commit `.env`.

## Structure

```
dashboard/
├── app.py                                   # Flask application
├── dynamic_comparison_analyzer.py           # LLM-powered report comparison
├── llm_enhanced_esg_data_categorized.json   # Dashboard data (pipeline output)
├── comprehensive_conversion_results.json    # Unit-conversion data (/api/unit_conversion_results)
├── comparison_analysis/                     # Cached LLM comparison results
├── templates/                               # base, index, exploration, visualization, benchmarking
└── requirements.txt
```

## Technology Stack

- Backend: Flask (Python)
- Frontend: Bootstrap 5, jQuery, Plotly.js
- Data: Pandas, JSON
- LLM: configured via `extract.api` (DeepSeek by default)
