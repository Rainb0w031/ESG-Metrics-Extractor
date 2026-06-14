"""Direct API client for LLM interactions.

This module provides a robust API client with:
- Configurable retry logic with exponential backoff
- Multiple response format support (OpenAI, DashScope)
- JSON extraction and validation
- Comprehensive error handling and logging
- .env file support for secure API key storage

For public projects:
1. Create a .env file (copy from .env.example)
2. Add your API key to .env
3. NEVER commit .env to git (it's in .gitignore)
"""

import json
import os
import time
import requests
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path

from json_repair import repair_json


def _load_dotenv():
    """Load environment variables from .env file if it exists."""
    # Try to find .env file in project root
    current_dir = Path(__file__).parent
    for _ in range(5):  # Search up to 5 levels
        env_file = current_dir / '.env'
        if env_file.exists():
            try:
                # Try using python-dotenv if available
                from dotenv import load_dotenv
                load_dotenv(env_file)
                return True
            except ImportError:
                # Manual loading if dotenv not installed
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key and value and key not in os.environ:
                                os.environ[key] = value
                return True
        current_dir = current_dir.parent
    return False


# Try to load .env on module import
_load_dotenv()


@dataclass
class APIConfig:
    """Configuration for API client.
    
    API keys are loaded in this priority:
    1. Explicit value passed to constructor
    2. Environment variable (DEEPSEEK_API_KEY, LLM_API_KEY, QWEN_API_KEY, or DASHSCOPE_API_KEY)
    3. .env file in project root
    
    Supported providers:
    - DeepSeek: api.deepseek.com (deepseek-chat, deepseek-coder)
    - DashScope/Qwen: dashscope.aliyuncs.com (qwen-max, qwen-plus)
    - OpenAI-compatible: Any OpenAI-compatible endpoint
    
    For public projects, use .env file and add it to .gitignore.
    """
    api_key: str = ''
    api_base: str = 'https://api.deepseek.com/v1/chat/completions'
    model: str = 'deepseek-chat'
    temperature: float = 0.0
    max_tokens: int = 2000
    timeout: int = 60
    
    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 2.0
    
    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Create config from environment variables or .env file."""
        # Check multiple API key environment variables
        api_key = (
            os.getenv('DEEPSEEK_API_KEY') or
            os.getenv('LLM_API_KEY') or
            os.getenv('QWEN_API_KEY') or
            os.getenv('DASHSCOPE_API_KEY') or
            ''
        )
        
        return cls(
            api_key=api_key,
            api_base=os.getenv('LLM_API_BASE', 'https://api.deepseek.com/v1/chat/completions'),
            model=os.getenv('LLM_MODEL', 'deepseek-chat'),
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'APIConfig':
        """Create config from dictionary."""
        return cls(
            api_key=config_dict.get('api_key', ''),
            api_base=config_dict.get('api_base', cls.api_base),
            model=config_dict.get('model', cls.model),
            temperature=config_dict.get('temperature', cls.temperature),
            max_tokens=config_dict.get('max_tokens', cls.max_tokens),
            timeout=config_dict.get('timeout', cls.timeout),
            max_retries=config_dict.get('max_retries', cls.max_retries),
            retry_delay=config_dict.get('retry_delay', cls.retry_delay),
        )


class DirectAPIClient:
    """
    Direct API client for LLM interactions.
    
    Features:
    - Direct HTTP requests (no external dependencies beyond requests)
    - Configurable retry with exponential backoff
    - Multiple response format support
    - JSON extraction and cleaning
    - Comprehensive error handling
    
    Usage:
        client = DirectAPIClient(config)
        response = client.chat(messages)
        text = client.extract_text(response)
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize API client.
        
        Args:
            config: API configuration. If None, loads from environment.
        """
        self.config = config or APIConfig.from_env()
        
        if not self.config.api_key:
            print("[WARNING] No API key configured. Set QWEN_API_KEY or DASHSCOPE_API_KEY environment variable.")
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: Optional[float] = None,
             max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Send chat request to API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            API response dictionary, or None if all retries failed
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.config.temperature,
            "max_tokens": max_tokens if max_tokens is not None else self.config.max_tokens
        }
        
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    self.config.api_base,
                    headers=headers,
                    json=data,
                    timeout=self.config.timeout
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    last_error = f"HTTP {response.status_code}: {response.text[:200]}"
                    print(f"[WARNING] API call failed (attempt {attempt + 1}): {last_error}")
                    
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                print(f"[WARNING] API timeout (attempt {attempt + 1})")
                
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                print(f"[WARNING] Request error (attempt {attempt + 1}): {e}")
                
            except Exception as e:
                last_error = str(e)
                print(f"[WARNING] Unexpected error (attempt {attempt + 1}): {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay * (2 ** attempt)
                print(f"[INFO] Retrying in {delay:.1f}s...")
                time.sleep(delay)
        
        print(f"[ERROR] All {self.config.max_retries} attempts failed. Last error: {last_error}")
        return None
    
    def extract_text(self, response: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract text content from API response.
        
        Supports multiple response formats:
        - OpenAI format: response.choices[0].message.content
        - DashScope format: response.output.choices[0].message.content
        
        Args:
            response: API response dictionary
            
        Returns:
            Extracted text content, or None if extraction failed
        """
        if response is None:
            return None
        
        try:
            # OpenAI-compatible format
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                elif 'content' in choice:
                    return choice['content']
            
            # DashScope format
            if 'output' in response and 'choices' in response['output']:
                choice = response['output']['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
                elif 'content' in choice:
                    return choice['content']
            
            print(f"[ERROR] Could not extract text from response: {list(response.keys())}")
            return None
            
        except Exception as e:
            print(f"[ERROR] Error extracting text: {e}")
            return None
    
    def extract_json(self, response: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON from API response.
        
        Handles:
        - Markdown JSON code blocks (```json ... ```)
        - Extra text around JSON object
        - Multiple JSON objects (returns first)
        - Malformed JSON via json_repair fallback (unescaped quotes, trailing commas, etc.)
        
        Args:
            response: API response dictionary
            
        Returns:
            Parsed JSON dictionary, or None if extraction/parsing failed
        """
        text = self.extract_text(response)
        if text is None:
            return None
        
        # Clean the text
        cleaned_text = self._clean_json_text(text)
        if cleaned_text is None:
            return None
        
        try:
            return json.loads(cleaned_text)
        except json.JSONDecodeError as e:
            # Attempt repair for common LLM JSON issues (unescaped quotes, trailing commas)
            try:
                repaired = repair_json(cleaned_text, return_objects=True)
                if isinstance(repaired, dict):
                    print(f"[INFO] JSON repaired successfully (original error: {e})")
                    return repaired
            except Exception as repair_error:
                print(f"[WARNING] JSON repair failed: {repair_error}")
            
            print(f"[ERROR] JSON parse error: {e}")
            print(f"[DEBUG] Text (first 200 chars): {cleaned_text[:200]}...")
            return None
    
    def _clean_json_text(self, text: str) -> Optional[str]:
        """
        Clean text to extract valid JSON.
        
        Args:
            text: Raw text that may contain JSON
            
        Returns:
            Cleaned JSON string, or None if no valid JSON found
        """
        # Remove markdown JSON code blocks
        if '```json' in text:
            start = text.index('```json') + 7
            end = text.index('```', start) if '```' in text[start:] else len(text)
            text = text[start:end].strip()
        elif '```' in text:
            start = text.index('```') + 3
            end = text.index('```', start) if '```' in text[start:] else len(text)
            text = text[start:end].strip()
        
        # Find JSON object boundaries
        try:
            start = text.index('{')
            end = text.rindex('}') + 1
            return text[start:end]
        except ValueError:
            print("[ERROR] No JSON object found in text")
            return None
    
    def chat_json(self, messages: List[Dict[str, str]], 
                  temperature: Optional[float] = None,
                  max_tokens: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Send chat request and parse JSON response.
        
        Convenience method combining chat() and extract_json().
        
        Args:
            messages: List of message dictionaries
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            
        Returns:
            Parsed JSON dictionary, or None if failed
        """
        response = self.chat(messages, temperature, max_tokens)
        return self.extract_json(response)
    
    def analyze_text(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze text with a prompt and get JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Parsed JSON dictionary, or None if failed
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return self.chat_json(messages)
