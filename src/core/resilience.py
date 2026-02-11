"""
Resilience — Truth Forge Core
Retry logic, circuit breaker, and fault tolerance patterns.
"""

import time
import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Tuple
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, skip calls
    HALF_OPEN = "half_open" # Testing recovery


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading failures.
    Essential for federation resilience — if one organ fails,
    the others must continue operating.
    """
    
    def __init__(self, failure_threshold: int = 5, 
                 recovery_timeout: float = 60.0,
                 name: str = "default"):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.state = CircuitState.CLOSED
        self.logger = logging.getLogger(f"truth_forge.resilience.{name}")
        
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.logger.info(f"Circuit {self.name}: HALF_OPEN (testing recovery)")
            else:
                raise CircuitBreakerOpen(f"Circuit {self.name} is OPEN")
        
        try:
            result = func(*args, **kwargs)
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.logger.info(f"Circuit {self.name}: CLOSED (recovered)")
            return result
        except Exception as e:
            self._record_failure()
            raise
    
    def _record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.error(
                f"Circuit {self.name}: OPEN (failures: {self.failure_count})")


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open."""
    pass


def retry(max_attempts: int = 3, 
          delay: float = 1.0, 
          backoff: float = 2.0,
          exceptions: Tuple[Type[Exception], ...] = (Exception,)):
    """
    Decorator for retry with exponential backoff.
    
    Usage:
        @retry(max_attempts=3, delay=1.0)
        def flaky_operation():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger("truth_forge.resilience.retry")
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(
                        f"{func.__name__} attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay:.1f}s")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator
