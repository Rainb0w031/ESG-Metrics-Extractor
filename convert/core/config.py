"""Configuration for dashboard conversion."""

from dataclasses import dataclass, field
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from extract.api import APIConfig


@dataclass
class ConversionConfig:
    """Configuration for dashboard conversion pipeline."""
    
    # API configuration
    api_config: Optional[APIConfig] = None
    
    # Processing configuration
    batch_size: int = 15  # Metrics per batch for LLM processing
    max_workers: int = 3  # Parallel workers
    
    # Enhancement options
    enhance_names: bool = True
    generate_categories: bool = True
    analyze_importance: bool = True
    
    # Validation options
    validate_metrics: bool = True
    
    # Cleaning options
    clean_values: bool = True
    preserve_original_values: bool = True
    
    def __post_init__(self):
        if self.api_config is None:
            self.api_config = APIConfig.from_env()
