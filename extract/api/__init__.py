"""API client module for LLM interactions.

This module provides a direct API client for making LLM calls without
dependency on external libraries like prompter. This approach is:
- More modular and portable
- Easier to test and debug
- More control over retry logic and error handling
- Industry standard approach
"""

from .client import DirectAPIClient, APIConfig
from .retry import RetryConfig, with_retry

__all__ = [
    'DirectAPIClient',
    'APIConfig',
    'RetryConfig',
    'with_retry',
]
