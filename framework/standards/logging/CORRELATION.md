# Correlation IDs

**Every request MUST have a correlation_id that flows through all operations.**

---

## Implementation

```python
import contextvars
import uuid
from functools import wraps
from typing import Any, Callable
import logging

correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    'correlation_id', default=None
)

class ContextLogger(logging.LoggerAdapter):
    """Logger that automatically includes correlation context."""

    def process(self, msg: str, kwargs: dict) -> tuple[str, dict]:
        extra = kwargs.get('extra', {})
        extra['correlation_id'] = correlation_id_var.get() or 'no-correlation'
        kwargs['extra'] = extra
        return msg, kwargs


def get_logger(name: str) -> ContextLogger:
    """Get a context-aware logger."""
    return ContextLogger(logging.getLogger(name), {})


def with_correlation_id(func: Callable) -> Callable:
    """Decorator to set correlation ID for a request/operation."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        correlation_id = kwargs.pop('correlation_id', None) or str(uuid.uuid4())
        token = correlation_id_var.set(correlation_id)
        try:
            return func(*args, **kwargs)
        finally:
            correlation_id_var.reset(token)
    return wrapper
```

---

## Usage

```python
from context_logger import get_logger, with_correlation_id

logger = get_logger(__name__)

@with_correlation_id
def process_order(order_id: str) -> dict:
    logger.info("Starting order processing", extra={"order_id": order_id})

    try:
        order = fetch_order(order_id)
        logger.debug("Order fetched", extra={
            "order_id": order_id,
            "items": len(order.items)
        })

        result = validate_and_process(order)
        logger.info("Order processed successfully", extra={
            "order_id": order_id,
            "total": result.total
        })
        return result

    except Exception as e:
        logger.error("Order processing failed", extra={
            "order_id": order_id,
            "error_type": type(e).__name__
        }, exc_info=True)
        raise
```

---

## Why Correlation IDs Matter

- **Distributed tracing**: Follow a request across services
- **Debugging**: Find all logs for a single operation
- **Audit**: Track who did what when
- **Alerting**: Group related errors

---

## UP

[logging/INDEX.md](INDEX.md)
