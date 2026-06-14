"""
Dashboard Integration Module - Step 4 of ESG Pipeline

Integrates individual dashboard files into a categorized dashboard with:
- Multi-company, multi-year support
- Duplicate detection and removal
- Integration metadata tracking
- Automatic dashboard management

## Architecture

```
integrate/
├── core/              # Models and configuration
├── deduplication/     # Duplicate detection
└── pipeline/          # DashboardIntegrator orchestrator
```

## Usage

```python
from integrate.pipeline import DashboardIntegrator

integrator = DashboardIntegrator()
result = integrator.integrate(
    dashboard_file="company_2024_dashboard.json",
    company="Amazon",
    year="2024"
)
```
"""

__version__ = "1.0.0"

# Core
from .core.models import IntegrationMetadata, DashboardEntry
from .core.config import IntegrationConfig

# Deduplication
from .deduplication import DuplicateDetector, MetricSignature

# Pipeline
from .pipeline import DashboardIntegrator

__all__ = [
    # Core
    'IntegrationMetadata',
    'DashboardEntry',
    'IntegrationConfig',
    # Deduplication
    'DuplicateDetector',
    'MetricSignature',
    # Pipeline
    'DashboardIntegrator',
]
