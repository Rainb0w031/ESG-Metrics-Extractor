"""
API Connection Test - Tests LLM API connectivity using modularized extract/api module.

Usage:
    1. Copy .env.example to .env
    2. Add your API key to .env
    3. Run: python test_api_connection.py
"""

import sys
from pathlib import Path

# Add metrics to path
sys.path.insert(0, str(Path(__file__).parent))

from extract.api import DirectAPIClient, APIConfig


def test_api_connection():
    """Test API connection using DirectAPIClient."""
    print("=" * 60)
    print("API CONNECTION TEST")
    print("=" * 60)
    
    # Load config from environment/.env
    config = APIConfig.from_env()
    
    # Show config (hide API key)
    print(f"\nConfiguration:")
    print(f"  API Base: {config.api_base}")
    print(f"  Model: {config.model}")
    print(f"  API Key: {'[SET]' if config.api_key else '[NOT SET]'}")
    
    if not config.api_key:
        print("\n[ERROR] No API key found!")
        print("Please set one of these in .env file:")
        print("  - DEEPSEEK_API_KEY (for DeepSeek)")
        print("  - LLM_API_KEY (generic)")
        print("  - DASHSCOPE_API_KEY (for Qwen)")
        print("\nCopy .env.example to .env and add your key.")
        return False
    
    # Create client
    client = DirectAPIClient(config)
    
    # Test simple message
    print(f"\nSending test message...")
    messages = [
        {"role": "user", "content": "Hello! Please respond with exactly: 'API connection successful!'"}
    ]
    
    response = client.chat(messages)
    
    if response:
        text = client.extract_text(response)
        print(f"\n[OK] Response received:")
        print(f"  {text}")
        print("\n" + "=" * 60)
        print("API CONNECTION TEST: PASSED")
        print("=" * 60)
        return True
    else:
        print("\n[ERROR] No response received")
        print("\n" + "=" * 60)
        print("API CONNECTION TEST: FAILED")
        print("=" * 60)
        return False


def test_json_response():
    """Test JSON response parsing."""
    print("\n" + "=" * 60)
    print("JSON RESPONSE TEST")
    print("=" * 60)
    
    config = APIConfig.from_env()
    if not config.api_key:
        print("[SKIP] No API key configured")
        return False
    
    client = DirectAPIClient(config)
    
    messages = [
        {"role": "user", "content": 'Return this JSON: {"status": "ok", "message": "test"}'}
    ]
    
    print("Requesting JSON response...")
    result = client.chat_json(messages)
    
    if result and isinstance(result, dict):
        print(f"\n[OK] JSON parsed successfully:")
        print(f"  {result}")
        return True
    else:
        print("\n[ERROR] JSON parsing failed")
        return False


if __name__ == "__main__":
    success = test_api_connection()
    
    if success:
        test_json_response()
    
    sys.exit(0 if success else 1)
