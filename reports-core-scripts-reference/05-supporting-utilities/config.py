"""
Configuration file for ESG Analysis Pipeline
Contains all API keys, URLs, and other configuration settings
"""

import os
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Qwen/DashScope API Configuration
QWEN_API_KEY = os.getenv('QWEN_API_KEY', 'your-qwen-api-key-here')
QWEN_API_BASE = os.getenv('QWEN_API_BASE', 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions')

# Alternative environment variable names for compatibility
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', QWEN_API_KEY)
OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', QWEN_API_BASE)

# SerpAPI for web search functionality
SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY', 'your-serpapi-key-here')

# DashScope specific (for compatibility with existing code)
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', QWEN_API_KEY)

# Model Configuration
# Available models: qwen-turbo, qwen-plus, qwen-max, qwen2.5-72b-instruct, qwen2.5-32b-instruct, qwen2.5-14b-instruct, qwen2.5-7b-instruct
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen-max')  # Change this to switch models

def get_api_config(api_type: str = 'qwen') -> dict:
    """
    Get API configuration for different API types
    
    Args:
        api_type: Type of API ('qwen', 'openai', 'serpapi')
    
    Returns:
        Dictionary with API configuration
    """
    if api_type == 'qwen':
        return {
            'api_key': QWEN_API_KEY,
            'api_base': QWEN_API_BASE,
            'model': QWEN_MODEL
        }
    elif api_type == 'openai':
        return {
            'api_key': OPENAI_API_KEY,
            'api_base': OPENAI_API_BASE,
            'model': QWEN_MODEL
        }
    elif api_type == 'serpapi':
        return {
            'api_key': SERPAPI_API_KEY
        }
    else:
        raise ValueError(f"Unknown API type: {api_type}")

def get_model_config() -> dict:
    """
    Get model-specific configuration
    
    Returns:
        Dictionary with model configuration
    """
    return {
        'model': QWEN_MODEL,
        'temperature': 0.2,
        'max_tokens': 2048,
        'timeout': 60
    }

def validate_api_keys() -> bool:
    """
    Validate that all required API keys are set
    
    Returns:
        True if all keys are valid, False otherwise
    """
    required_keys = [QWEN_API_KEY, SERPAPI_API_KEY]
    return all(key and key != 'your-api-key-here' for key in required_keys) 