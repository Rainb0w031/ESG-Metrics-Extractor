"""Core models and configuration for dashboard integration."""

from .models import IntegrationMetadata, DashboardEntry
from .config import IntegrationConfig

__all__ = [
    'IntegrationMetadata',
    'DashboardEntry',
    'IntegrationConfig',
]
