# Logging

**The Standard** | Every significant event is captured with structured, searchable, actionable data.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Format | Structured JSON for machine parsing |
| Levels | DEBUG, INFO, WARNING, ERROR, CRITICAL (use correctly) |
| Context | Include correlation_id, operation, actor, timestamp |
| Sensitive Data | Never log credentials, PII, or secrets |
| Retention | Define retention policy per log category |
| Performance | Async logging for high-throughput paths |

---

## WHY (Theory)

### The Observability Imperative

From 06_LAW: *"Every action, every state change, every decision must be observable."*

Logs are the primary mechanism for observability. Without proper logging:
- Debugging becomes archaeology
- Incidents become mysteries
- Audits become impossible
- Costs become invisible

### The Cost Connection

Every log line has a cost (storage, processing, attention). Every missing log line has a cost (debugging time, incident duration, compliance risk). The standard optimizes this tradeoff.

---

## WHAT (Specification)

### Log Levels

| Level | Use When | Example |
|-------|----------|---------|
| DEBUG | Development tracing, verbose details | `DEBUG: Cache lookup key=user_123` |
| INFO | Normal operations, business events | `INFO: Order processed order_id=456` |
| WARNING | Recoverable issues, degraded state | `WARNING: Rate limit at 80%` |
| ERROR | Failures requiring attention | `ERROR: Payment failed reason=declined` |
| CRITICAL | System-wide failures, data loss risk | `CRITICAL: Database connection pool exhausted` |

### MUST (Required)

1. **Structured Format** — All logs MUST be structured JSON in production.

```python
# ✅ Correct
logger.info("Order processed", extra={
    "order_id": order.id,
    "customer_id": customer.id,
    "total": order.total,
    "correlation_id": ctx.correlation_id
})

# ❌ Wrong
logger.info(f"Order {order.id} processed for customer {customer.id}")
```

2. **Correlation IDs** — Every request MUST have a correlation_id that flows through all operations.

```python
class CorrelationContext:
    _correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
        'correlation_id', default=None
    )

    @classmethod
    def get(cls) -> str:
        return cls._correlation_id.get() or str(uuid.uuid4())

    @classmethod
    def set(cls, correlation_id: str) -> contextvars.Token:
        return cls._correlation_id.set(correlation_id)
```

3. **No Sensitive Data** — Logs MUST NOT contain:
   - Passwords, API keys, tokens
   - Credit card numbers, SSNs
   - Personal health information
   - Any data subject to compliance (PCI, HIPAA, GDPR)

```python
# ✅ Correct
logger.info("User authenticated", extra={"user_id": user.id})

# ❌ Wrong - exposes password
logger.debug(f"Login attempt: {username}:{password}")
```

4. **Timestamp Standard** — All timestamps MUST be ISO 8601 UTC.

```python
{
    "timestamp": "2025-01-18T14:30:00.000Z",
    "level": "INFO",
    "message": "Event occurred"
}
```

5. **Error Context** — ERROR and CRITICAL logs MUST include:
   - Exception type and message
   - Stack trace (in development) or error reference (in production)
   - Operation context
   - Recovery action taken or recommended

```python
try:
    process_payment(order)
except PaymentError as e:
    logger.error(
        "Payment processing failed",
        extra={
            "order_id": order.id,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "recovery": "Queued for retry",
            "correlation_id": ctx.correlation_id
        },
        exc_info=True  # Include traceback in dev
    )
```

### SHOULD (Recommended)

1. **Rate Limiting** — High-frequency logs SHOULD be rate-limited or sampled.

```python
@rate_limited_log(max_per_minute=100)
def log_cache_miss(key: str):
    logger.debug("Cache miss", extra={"key": key})
```

2. **Log Aggregation** — Logs SHOULD flow to centralized aggregation (ELK, Datadog, etc.).

3. **Metric Extraction** — Key log events SHOULD emit corresponding metrics.

4. **Request/Response Logging** — API boundaries SHOULD log sanitized request/response pairs.

### MAY (Optional)

1. **Trace Context** — Include OpenTelemetry trace_id and span_id for distributed tracing.
2. **Log Sampling** — Sample verbose logs in high-throughput scenarios.
3. **Dynamic Log Levels** — Allow runtime log level adjustment.

### MUST NOT (Prohibited)

1. **Never Log Then Throw** — Don't log an error and then re-throw without handling.
2. **Never Log Passwords** — Even "masked" passwords (e.g., `p***d`) leak length.
3. **Never Use Print** — `print()` is not logging; it's unstructured noise.
4. **Never Block on Logging** — Production logging must not block the main thread.

---

## HOW (Reference)

### Standard Logger Configuration

```python
# logging_config.py
import logging
import logging.config
import json
from datetime import datetime, timezone

class StructuredFormatter(logging.Formatter):
    """JSON formatter with standard fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields
        if hasattr(record, 'correlation_id'):
            log_entry['correlation_id'] = record.correlation_id

        # Add any extra fields passed to the logger
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and not key.startswith('_'):
                log_entry[key] = value

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "()": StructuredFormatter
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",  # Human-readable for dev
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "structured",  # JSON for production
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
}

def configure_logging():
    """Initialize logging with standard configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
```

### Context-Aware Logger

```python
# context_logger.py
import logging
import contextvars
import uuid
from functools import wraps
from typing import Any, Callable

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

### Usage Example

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

    except ValidationError as e:
        logger.warning("Order validation failed", extra={
            "order_id": order_id,
            "validation_errors": e.errors
        })
        raise

    except Exception as e:
        logger.error("Order processing failed", extra={
            "order_id": order_id,
            "error_type": type(e).__name__
        }, exc_info=True)
        raise
```

---

### Modern Structured Logging with structlog

For new code, prefer `structlog` which provides better ergonomics for structured logging.

#### Configuration

```python
# structlog_config.py
import structlog
from datetime import datetime, timezone

def configure_structlog(json_logs: bool = True) -> None:
    """Configure structlog for structured logging.

    Args:
        json_logs: True for JSON output (production), False for console (dev).
    """
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        # Production: JSON output
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Development: Colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(10),  # DEBUG level
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
```

#### Context Binding

```python
import structlog

log = structlog.get_logger()

def process_batch(batch_id: str, records: list) -> dict:
    """Process batch with bound context."""
    # Bind context that persists across all log calls
    log_ctx = log.bind(
        batch_id=batch_id,
        record_count=len(records),
        pipeline="ingestion",
    )

    log_ctx.info("batch_started")

    success_count = 0
    failure_count = 0

    for i, record in enumerate(records):
        # Bind per-record context
        record_log = log_ctx.bind(
            record_index=i,
            record_id=record.get("id"),
        )

        try:
            process_record(record)
            success_count += 1
            record_log.debug("record_processed")
        except Exception as e:
            failure_count += 1
            record_log.error("record_failed", error=str(e), exc_info=True)

    log_ctx.info(
        "batch_completed",
        success_count=success_count,
        failure_count=failure_count,
        success_rate=success_count / len(records) if records else 0,
    )

    return {"success": success_count, "failure": failure_count}
```

---

### Pipeline-Specific Logging Patterns

#### Stage Transition Logging

```python
import structlog
from enum import Enum
from typing import Any

class PipelineStage(Enum):
    INGESTION = "ingestion"
    ENTITY_CREATION = "entity_creation"
    ENRICHMENT = "enrichment"
    FINALIZATION = "finalization"

def log_stage_transition(
    stage: PipelineStage,
    batch_id: str,
    record_count: int,
    metrics: dict[str, Any],
) -> None:
    """Log pipeline stage completion with standardized metrics."""
    log = structlog.get_logger()
    log.info(
        "stage_completed",
        stage=stage.value,
        batch_id=batch_id,
        record_count=record_count,
        duration_seconds=metrics.get("duration_seconds"),
        success_count=metrics.get("success_count"),
        failure_count=metrics.get("failure_count"),
        dlq_count=metrics.get("dlq_count", 0),
        throughput_per_second=metrics.get("throughput_per_second"),
    )
```

#### Batch Progress Logging

```python
def log_batch_progress(
    total_records: int,
    processed: int,
    batch_num: int,
    batch_size: int,
    start_time: float,
) -> None:
    """Log batch processing progress at regular intervals."""
    import time

    log = structlog.get_logger()
    elapsed = time.time() - start_time
    rate = processed / elapsed if elapsed > 0 else 0
    remaining = total_records - processed
    eta_seconds = remaining / rate if rate > 0 else 0

    log.info(
        "batch_progress",
        batch_num=batch_num,
        processed=processed,
        total=total_records,
        percent_complete=round(processed / total_records * 100, 1),
        records_per_second=round(rate, 1),
        eta_seconds=round(eta_seconds, 0),
    )
```

#### Cost Tracking in Logs

```python
def log_operation_cost(
    operation: str,
    cost_usd: float,
    details: dict[str, Any],
) -> None:
    """Log operation with cost tracking."""
    log = structlog.get_logger()
    log.info(
        "operation_cost",
        operation=operation,
        cost_usd=round(cost_usd, 4),
        **details,
    )

# Usage
log_operation_cost(
    operation="bigquery_query",
    cost_usd=0.0025,
    details={
        "bytes_processed": 500_000_000,
        "query_type": "batch_insert",
        "table": "knowledge_atoms",
    },
)
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| Custom linter | No `print()` statements | error |
| Custom linter | Structured logging format | warning |
| Log scanner | Sensitive data patterns | error |
| CI pipeline | Log configuration present | error |

### Escape Hatch

For debugging scenarios requiring temporary verbose logging:

```python
# standard:override logging-level - Temporary debug logging for incident #123
logging.getLogger('module').setLevel(logging.DEBUG)
```

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [ERROR_HANDLING.md](ERROR_HANDLING.md) | Error context for logs |
| [SECURITY.md](SECURITY.md) | Sensitive data classification |
| [PIPELINE_STANDARD.md](PIPELINE_STANDARD.md) | Pipeline-specific logging requirements |
| [CODE_QUALITY.md](CODE_QUALITY.md) | Type hints for logging functions |

---

## Industry Alignment

This standard incorporates best practices from:
- [structlog Documentation](https://www.structlog.org/) - Modern structured logging
- [Python Logging HOWTO](https://docs.python.org/3/howto/logging.html) - Standard library patterns
- [12 Factor App: Logs](https://12factor.net/logs) - Log streaming philosophy
- [OpenTelemetry Logging](https://opentelemetry.io/docs/concepts/signals/logs/) - Observability standards

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-25 | Added structlog patterns, pipeline logging, cost tracking | Claude |
| 2025-01-18 | Initial standard | Claude |
