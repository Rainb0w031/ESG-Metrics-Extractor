"""Retry utilities for API calls."""

import time
import functools
from dataclasses import dataclass
from typing import Callable, TypeVar, Optional, Any

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for adding retry logic to functions.
    
    Args:
        config: Retry configuration. Uses defaults if None.
        
    Returns:
        Decorated function with retry logic
    
    Usage:
        @with_retry(RetryConfig(max_retries=5))
        def my_api_call():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            last_exception = None
            
            for attempt in range(config.max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result is not None:
                        return result
                    
                except Exception as e:
                    last_exception = e
                    print(f"[WARNING] Attempt {attempt + 1} failed: {e}")
                
                if attempt < config.max_retries - 1:
                    delay = config.get_delay(attempt)
                    print(f"[INFO] Retrying in {delay:.1f}s...")
                    time.sleep(delay)
            
            if last_exception:
                print(f"[ERROR] All {config.max_retries} attempts failed. Last error: {last_exception}")
            
            return None
        
        return wrapper
    
    return decorator


class RetryableOperation:
    """
    Context manager for retryable operations.
    
    Usage:
        with RetryableOperation(config) as op:
            for attempt in op:
                result = some_operation()
                if result:
                    op.success(result)
                    break
    """
    
    def __init__(self, config: Optional[RetryConfig] = None):
        """Initialize with retry configuration."""
        self.config = config or RetryConfig()
        self.attempts = 0
        self.result = None
        self._success = False
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def __iter__(self):
        """Iterate through retry attempts."""
        for attempt in range(self.config.max_retries):
            self.attempts = attempt + 1
            yield attempt
            
            if self._success:
                break
            
            if attempt < self.config.max_retries - 1:
                delay = self.config.get_delay(attempt)
                time.sleep(delay)
    
    def success(self, result: Any):
        """Mark operation as successful."""
        self._success = True
        self.result = result
    
    def is_successful(self) -> bool:
        """Check if operation succeeded."""
        return self._success
