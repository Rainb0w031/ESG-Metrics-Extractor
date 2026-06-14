"""Configuration for dashboard integration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class IntegrationConfig:
    """Configuration for dashboard integration pipeline."""
    
    # Default categorized dashboard path
    categorized_dashboard_path: str = "dashboard/llm_enhanced_esg_data_categorized.json"
    
    # Duplicate handling
    clean_duplicates: bool = True
    replace_existing: bool = True
    
    # Signature fields for duplicate detection
    signature_fields: tuple = (
        'metric_name',
        'value',
        'unit',
        'company',
        'year',
        'category',
        'type',
        'area'
    )
    
    # Create directories if they don't exist
    auto_create_dirs: bool = True
    
    def get_dashboard_path(self) -> Path:
        """Get the dashboard path as Path object."""
        return Path(self.categorized_dashboard_path)
