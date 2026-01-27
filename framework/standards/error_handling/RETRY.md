# Retry Pattern

**Transient failures retry with exponential backoff using tenacity.**

---

## Basic Retry

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
def call_external_api(request: dict) -> dict:
    """Call external API with automatic retry."""
    response = api_client.post(request)
    response.raise_for_status()
    return response.json()
```

---

## Backoff Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|
| **Exponential** | Rate limits, API throttling | `wait_exponential(min=1, max=60)` |
| **Fixed** | Consistent delay needed | `wait_fixed(5)` |
| **Random** | Avoid thundering herd | `wait_random(min=1, max=5)` |
| **Exponential + Jitter** | Best for distributed | `wait_exponential(max=60) + wait_random(0, 2)` |

---

## Retry with Structured Logging

```python
from tenacity import retry, stop_after_attempt, wait_exponential, RetryCallState

def log_retry_attempt(retry_state: RetryCallState) -> None:
    """Log each retry attempt with structured data."""
    logger.warning(
        "retry_attempt",
        extra={
            "attempt": retry_state.attempt_number,
            "wait_seconds": retry_state.next_action.sleep if retry_state.next_action else 0,
            "function": retry_state.fn.__name__ if retry_state.fn else "unknown",
            "exception": str(retry_state.outcome.exception()) if retry_state.outcome else None,
        },
    )

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=30),
    before_sleep=log_retry_attempt,
    reraise=True,
)
def resilient_operation(record_id: str) -> dict:
    """Operation with logged retries."""
    ...
```

---

## When NOT to Retry

| Exception Type | Retry? | Reason |
|----------------|--------|--------|
| `ConnectionError` | Yes | Transient network issue |
| `TimeoutError` | Yes | Temporary overload |
| `RateLimitError` | Yes | Back off and retry |
| `ValidationError` | **No** | Bad data won't become good |
| `AuthenticationError` | **No** | Credentials won't fix themselves |
| `NotFoundError` | **No** | Resource doesn't exist |

---

## UP

[error_handling/INDEX.md](INDEX.md)
