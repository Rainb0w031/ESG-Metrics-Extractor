"""
Configuration management for the Metrics ESG processing pipeline.
Extends prompter's configuration with ESG-specific settings.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
# Use uv to load environment variables from prompter project's .env file
# Run with: uv run --env-file ../prompter-main/.env python script.py

class MetricsConfig:
    """Configuration class for Metrics ESG processing pipeline."""
    
    def __init__(self):
        # Base paths
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.output_dir = self.project_root / "output"
        self.logs_dir = self.project_root / "logs"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # LLM Configuration (inherited from prompter)
        self.llm_provider = os.getenv("LLM_PROVIDER", "dashscope")
        self.llm_model = os.getenv("LLM_MODEL", "dashscope+qwen-max")
        self.llm_endpoint = os.getenv("LLM_ENDPOINT", "https://dashscope.aliyuncs.com/api/v1")
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        
        # ESG Processing Configuration
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "40"))
        self.max_chunks_per_analysis = os.getenv("MAX_CHUNKS_PER_ANALYSIS")
        self.temperature = float(os.getenv("TEMPERATURE", "0.2"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4096"))
        self.timeout = int(os.getenv("TIMEOUT", "120"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        
        # PDF Processing Configuration
        self.pdf_max_text_length = int(os.getenv("PDF_MAX_TEXT_LENGTH", "800"))  # Increased from 500
        self.pdf_chunk_size = int(os.getenv("PDF_CHUNK_SIZE", "512"))  # Increased from 320
        self.pdf_min_length = int(os.getenv("PDF_MIN_LENGTH", "32"))  # Increased from 24
        
        # Dashboard Configuration
        self.dashboard_company = os.getenv("DASHBOARD_COMPANY", "Amazon")
        self.dashboard_year = os.getenv("DASHBOARD_YEAR", "2023")
        
        # Logging Configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = self.logs_dir / "metrics.log"
        
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration for prompter integration."""
        return {
            "provider": self.llm_provider,
            "model": self.llm_model,
            "endpoint": self.llm_endpoint,
            "api_key": self.llm_api_key,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }
    
    def get_pdf_config(self) -> Dict[str, Any]:
        """Get PDF processing configuration."""
        return {
            "max_text_length": self.pdf_max_text_length,
            "chunk_size": self.pdf_chunk_size,
            "min_length": self.pdf_min_length
        }
    
    def get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration."""
        return {
            "company": self.dashboard_company,
            "year": self.dashboard_year
        }

# Global configuration instance
metrics_config = MetricsConfig() 