#!/usr/bin/env python3
"""
Direct API Client for Qwen LLM
Replaces OpenAI client with direct HTTP requests
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional, List
from config import get_api_config

class DirectAPIClient:
    """Direct API client for making requests to Qwen LLM"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None, model: Optional[str] = None):
        """Initialize the direct API client"""
        # Use config.py for default values
        config = get_api_config('qwen')
        self.api_key = api_key or config['api_key']
        self.api_base = api_base or config['api_base']
        self.model = model or config['model']  # Use model from config
        
        if not self.api_key:
            raise ValueError("QWEN_API_KEY environment variable is required")
    
    def chat_completions_create(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Create a chat completion using direct HTTP request
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to qwen-turbo)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary containing the API response
        """
        url = self.api_base
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Use OpenAI-compatible format
        data = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            print(f"🔄 Making direct API call to {url}")
            print(f"📋 Model: {model or self.model}")
            print(f"📋 Temperature: {temperature}")
            print(f"📋 Max Tokens: {max_tokens}")
            
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
            end_time = time.time()
            
            print(f"⏱️ Response time: {end_time - start_time:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                
                print(f"✅ API call successful")
                return response_data
            else:
                print(f"❌ API call failed with status {response.status_code}")
                print(f"📝 Response: {response.text}")
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Request timed out after {timeout} seconds")
            raise Exception(f"Request timed out after {timeout} seconds")
            
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 Connection error: {e}")
            raise Exception(f"Connection error: {e}")
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise Exception(f"Unexpected error: {e}")
    
    def create_with_retry(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        timeout: int = 60,
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Create chat completion with retry logic
        
        Args:
            messages: List of message dictionaries
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            API response dictionary or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                print(f"🔄 API call attempt {attempt + 1}/{max_retries}...")
                return self.chat_completions_create(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
            except Exception as e:
                print(f"⚠️ API call attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    print(f"❌ All API call attempts failed")
                    return None

def get_direct_client(api_key: Optional[str] = None, api_base: Optional[str] = None) -> DirectAPIClient:
    """Get a direct API client instance"""
    return DirectAPIClient(api_key=api_key, api_base=api_base)

def make_direct_api_call(
    messages: List[Dict[str, str]], 
    model: str = None,
    temperature: float = 0.2,
    max_tokens: int = 2048,
    timeout: int = 60,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Make a direct API call with retry logic
    
    Args:
        messages: List of message dictionaries
        model: Model to use (defaults to config model)
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        
    Returns:
        API response dictionary or None if all retries failed
    """
    # Use model from config if not specified
    if model is None:
        from config import get_model_config
        model_config = get_model_config()
        model = model_config['model']
    
    client = get_direct_client()
    return client.create_with_retry(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
        max_retries=max_retries
    )

def extract_response_text(response: Optional[Dict[str, Any]]) -> Optional[str]:
    """Extract text content from API response"""
    if response and "choices" in response and len(response["choices"]) > 0:
        return response["choices"][0]["message"]["content"]
    return None 