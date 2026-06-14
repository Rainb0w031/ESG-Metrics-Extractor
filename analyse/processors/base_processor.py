"""
Base processor interface for chunk processing.

Defines the abstract interface for processing text chunks with different strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ProcessorConfig:
    """
    Configuration for chunk processors.
    
    Controls retry behavior, timeouts, and LLM parameters.
    """
    
    max_retries: int = 3
    """Maximum retry attempts for failed requests"""
    
    retry_delay: float = 2.0
    """Delay between retries (seconds)"""
    
    timeout: int = 120
    """Request timeout (seconds)"""
    
    temperature: float = 0.2
    """LLM temperature (0.0-1.0, lower = more deterministic)"""
    
    max_tokens: int = 4096
    """Maximum tokens in LLM response"""
    
    enable_response_validation: bool = True
    """Enable JSON response validation"""
    
    enable_retry_on_json_error: bool = True
    """Retry if JSON parsing fails"""
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")
        if self.timeout < 1:
            raise ValueError("timeout must be positive")
        if self.temperature < 0 or self.temperature > 1:
            raise ValueError("temperature must be between 0 and 1")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")


class BaseProcessor(ABC):
    """
    Abstract base for chunk processors.
    
    Processors handle the execution of analysis on text chunks,
    managing LLM calls, retries, and response parsing.
    """
    
    def __init__(self, config: ProcessorConfig = None):
        """
        Initialize processor with configuration.
        
        Args:
            config: Processor configuration
        """
        self.config = config or ProcessorConfig()
    
    @abstractmethod
    def process(self, prompt: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        """
        Process a prompt and return result.
        
        Args:
            prompt: Prompt to process
            analysis_type: Type of analysis being performed
        
        Returns:
            Dict containing processed result, or None if processing failed
        """
        pass
    
    @abstractmethod
    def process_batch(self, prompts: list, analysis_type: str) -> list:
        """
        Process multiple prompts in batch.
        
        Args:
            prompts: List of prompts to process
            analysis_type: Type of analysis being performed
        
        Returns:
            List of results (None for failed items)
        """
        pass
    
    def validate_response(self, response: Any) -> bool:
        """
        Validate that response is well-formed.
        
        Args:
            response: Response to validate
        
        Returns:
            True if valid, False otherwise
        """
        return response is not None

