# Error Handling

**The Standard** | Every failure is anticipated, caught, logged, and recoverable. Never drop data.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Requirement | Rule |
|-------------|------|
| Try/Catch | Every external call wrapped |
| Specific Exceptions | Catch specific, not generic |
| Context | Include operation context in errors |
| Recovery | Define recovery path or fail gracefully |
| Logging | All errors logged with structured data |
| User-Facing | Never expose internal details |
| Retry | Transient failures retry with exponential backoff |
| Dead Letter Queue | Failed records quarantined, never dropped |
| Batch Isolation | One record failure doesn't kill the batch |

---

## WHY (Theory)

### The Fail-Safe Pillar

From 06_LAW: *"Assume every component will fail."*

Errors are not exceptions—they are expectations. Every external call can fail. Every file can be missing. Every network can timeout. The question is not *if* failure happens, but *when* and *how we respond*.

Unhandled errors waste Jeremy's time debugging. Poorly handled errors hide root causes. Good error handling makes failures visible, recoverable, and educational.

---

## WHAT (Specification)

### Requirements

#### MUST (Required)

1. **Wrap all external calls** — Database, API, file I/O, network operations.

2. **Catch specific exceptions** — Never bare `except:` or `except Exception:` without re-raising.

3. **Include context** — Error messages must include what operation failed and relevant identifiers.

4. **Log before handling** — Log the error with full context before attempting recovery.

5. **Define recovery or fail gracefully** — Either recover automatically or fail in a way that doesn't corrupt state.

6. **Preserve stack traces** — Use `raise ... from` or log the original traceback.

#### SHOULD (Recommended)

1. **Use custom exception classes** — For domain-specific errors.
2. **Implement retry with backoff** — For transient failures.
3. **Use circuit breakers** — For external service calls.
4. **Provide error codes** — For programmatic error handling.

#### MUST NOT (Prohibited)

1. **Silent failures** — Never catch and ignore without logging.
2. **Generic catches without re-raise** — `except Exception: pass` is forbidden.
3. **Expose internal details to users** — Stack traces, file paths, credentials.
4. **Swallow and continue** — If state may be corrupted, fail loudly.

---

## HOW (Reference)

### The Pattern

```python
from src.core.logging import LOG_EVENT
from src.core.exceptions import TruthEngineError

def process_data(document_id: str) -> dict:
    """Process document with proper error handling."""
    try:
        # Attempt the operation
        result = external_service.fetch(document_id)
        return transform(result)

    except ConnectionError as e:
        # Log with context
        LOG_EVENT(
            event="external_service_connection_failed",
            document_id=document_id,
            error=str(e),
            severity="ERROR"
        )
        # Retry or fail gracefully
        raise TruthEngineError(
            f"Failed to fetch document {document_id}: connection error"
        ) from e

    except ValidationError as e:
        # Log and provide recovery path
        LOG_EVENT(
            event="document_validation_failed",
            document_id=document_id,
            error=str(e),
            severity="WARNING"
        )
        # Return safe default or skip
        return {"status": "skipped", "reason": str(e)}

    except Exception as e:
        # Unexpected error - log everything, re-raise
        LOG_EVENT(
            event="unexpected_error",
            document_id=document_id,
            error=str(e),
            traceback=traceback.format_exc(),
            severity="CRITICAL"
        )
        raise  # Re-raise unexpected errors
```

### Custom Exception Hierarchy

```python
# src/core/exceptions.py

class TruthEngineError(Exception):
    """Base exception for all Truth Engine errors."""
    pass

class ConfigurationError(TruthEngineError):
    """Configuration is missing or invalid."""
    pass

class ValidationError(TruthEngineError):
    """Data validation failed."""
    pass

class ExternalServiceError(TruthEngineError):
    """External service call failed."""
    pass

class CostLimitExceeded(TruthEngineError):
    """Operation would exceed cost budget."""
    pass

class IdempotencyViolation(TruthEngineError):
    """Operation is not idempotent as required."""
    pass
```

### Retry Pattern

Use `tenacity` for retry logic. Choose the right strategy based on the failure type.

#### Basic Retry with Exponential Backoff

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

#### Backoff Strategy Comparison

| Strategy | Use Case | Example |
|----------|----------|---------|
| **Exponential** | Rate limits, API throttling | `wait_exponential(min=1, max=60)` |
| **Fixed** | Consistent delay needed | `wait_fixed(5)` |
| **Random** | Avoid thundering herd | `wait_random(min=1, max=5)` |
| **Exponential + Jitter** | Best for distributed systems | `wait_exponential(max=60) + wait_random(0, 2)` |

#### Retry with Structured Logging

```python
from tenacity import retry, stop_after_attempt, wait_exponential, RetryCallState
from typing import Any

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

#### When NOT to Retry

| Exception Type | Retry? | Reason |
|----------------|--------|--------|
| `ConnectionError` | ✅ Yes | Transient network issue |
| `TimeoutError` | ✅ Yes | Temporary overload |
| `RateLimitError` | ✅ Yes | Back off and retry |
| `ValidationError` | ❌ No | Bad data won't become good |
| `AuthenticationError` | ❌ No | Credentials won't fix themselves |
| `NotFoundError` | ❌ No | Resource doesn't exist |

---

### Dead Letter Queue (DLQ) Pattern

**Never drop data.** Failed records go to a DLQ for later analysis and reprocessing.

#### DLQ Implementation

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any, Dict, Optional

@dataclass
class DeadLetterRecord:
    """A record that failed processing."""
    original_record: Dict[str, Any]
    error_type: str
    error_message: str
    traceback: str
    pipeline_stage: str
    attempt_count: int
    first_failure: str
    last_failure: str
    record_id: Optional[str] = None

class DeadLetterQueue:
    """Quarantine for failed records. Never lose data."""

    def __init__(self, dlq_path: Path, pipeline_name: str) -> None:
        self.dlq_path = dlq_path / f"{pipeline_name}_dlq.jsonl"
        self.dlq_path.parent.mkdir(parents=True, exist_ok=True)

    def send(
        self,
        record: Dict[str, Any],
        error: Exception,
        stage: str,
        attempt_count: int = 1,
    ) -> None:
        """Send a failed record to the DLQ."""
        import traceback

        now = datetime.now(timezone.utc).isoformat()
        dlq_record = {
            "original_record": record,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "pipeline_stage": stage,
            "attempt_count": attempt_count,
            "first_failure": now,
            "last_failure": now,
            "record_id": record.get("entity_id") or record.get("id"),
            "dlq_timestamp": now,
        }

        with open(self.dlq_path, "a") as f:
            f.write(json.dumps(dlq_record) + "\n")

    def count(self) -> int:
        """Count records in DLQ."""
        if not self.dlq_path.exists():
            return 0
        with open(self.dlq_path) as f:
            return sum(1 for _ in f)

    def replay(self, processor_func) -> tuple[int, int]:
        """Attempt to reprocess DLQ records."""
        if not self.dlq_path.exists():
            return 0, 0

        success_count = 0
        failure_count = 0
        remaining = []

        with open(self.dlq_path) as f:
            for line in f:
                dlq_record = json.loads(line)
                try:
                    processor_func(dlq_record["original_record"])
                    success_count += 1
                except Exception:
                    dlq_record["attempt_count"] += 1
                    dlq_record["last_failure"] = datetime.now(timezone.utc).isoformat()
                    remaining.append(dlq_record)
                    failure_count += 1

        # Rewrite DLQ with remaining failures
        with open(self.dlq_path, "w") as f:
            for record in remaining:
                f.write(json.dumps(record) + "\n")

        return success_count, failure_count
```

#### Using DLQ in Batch Processing

```python
def process_batch(
    records: List[Dict[str, Any]],
    dlq: DeadLetterQueue,
    stage: str,
) -> tuple[List[Dict[str, Any]], int, int]:
    """Process batch with DLQ for failures.

    Returns:
        Tuple of (successful_records, success_count, failure_count)
    """
    successful = []
    success_count = 0
    failure_count = 0

    for record in records:
        try:
            result = process_single_record(record)
            successful.append(result)
            success_count += 1
        except ValidationError as e:
            # Non-retryable - send directly to DLQ
            dlq.send(record, e, stage, attempt_count=1)
            failure_count += 1
        except (ConnectionError, TimeoutError) as e:
            # Retryable - try with backoff first
            try:
                result = retry_with_backoff(process_single_record, record)
                successful.append(result)
                success_count += 1
            except Exception as retry_error:
                dlq.send(record, retry_error, stage, attempt_count=4)  # 1 + 3 retries
                failure_count += 1

    return successful, success_count, failure_count
```

#### DLQ Monitoring

```python
def check_dlq_health(dlq: DeadLetterQueue, threshold: int = 100) -> dict:
    """Check DLQ health and alert if threshold exceeded."""
    count = dlq.count()
    status = "healthy" if count < threshold else "warning" if count < threshold * 2 else "critical"

    return {
        "dlq_count": count,
        "threshold": threshold,
        "status": status,
        "requires_attention": count >= threshold,
    }
```

### Batch Error Isolation

One record failure should never kill an entire batch. Isolate failures.

```python
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

@dataclass
class BatchResult:
    """Result of batch processing with error isolation."""
    successful: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]
    success_count: int
    failure_count: int
    errors: List[Dict[str, Any]]

def process_batch_isolated(
    records: List[Dict[str, Any]],
    processor: callable,
    dlq: DeadLetterQueue,
    stage: str,
) -> BatchResult:
    """Process batch with isolation - one failure doesn't kill the batch.

    Args:
        records: Records to process.
        processor: Function to process single record.
        dlq: Dead letter queue for failed records.
        stage: Pipeline stage name for error context.

    Returns:
        BatchResult with successful records, failed records, and error details.
    """
    successful = []
    failed = []
    errors = []

    for i, record in enumerate(records):
        try:
            result = processor(record)
            successful.append(result)
        except Exception as e:
            # Log with full context
            error_info = {
                "record_index": i,
                "record_id": record.get("entity_id") or record.get("id"),
                "error_type": type(e).__name__,
                "error_message": str(e),
                "stage": stage,
            }
            errors.append(error_info)
            failed.append(record)

            # Send to DLQ - never lose data
            dlq.send(record, e, stage)

    return BatchResult(
        successful=successful,
        failed=failed,
        success_count=len(successful),
        failure_count=len(failed),
        errors=errors,
    )
```

#### Batch Processing with Progress

```python
def process_large_dataset(
    records: List[Dict[str, Any]],
    batch_size: int = 1000,
    dlq: DeadLetterQueue = None,
    stage: str = "processing",
) -> Dict[str, Any]:
    """Process large dataset in batches with progress tracking.

    Returns:
        Summary with total counts and any errors.
    """
    total_success = 0
    total_failure = 0
    all_errors = []

    for batch_num, start in enumerate(range(0, len(records), batch_size)):
        batch = records[start:start + batch_size]

        result = process_batch_isolated(batch, process_record, dlq, stage)

        total_success += result.success_count
        total_failure += result.failure_count
        all_errors.extend(result.errors)

        # Log progress
        logger.info(
            "batch_complete",
            extra={
                "batch_num": batch_num + 1,
                "batch_size": len(batch),
                "batch_success": result.success_count,
                "batch_failure": result.failure_count,
                "total_processed": start + len(batch),
                "total_records": len(records),
            },
        )

    return {
        "total_success": total_success,
        "total_failure": total_failure,
        "success_rate": total_success / len(records) if records else 0,
        "error_summary": all_errors[:10],  # First 10 errors for debugging
        "dlq_count": dlq.count() if dlq else 0,
    }
```

---

### User-Facing Error Messages

```python
# WRONG - Exposes internals
raise Exception(f"SQL error: {sql_query} failed with {db_error}")

# CORRECT - Safe for users
raise UserFacingError(
    message="Unable to save your document. Please try again.",
    error_code="DOC_SAVE_001",
    internal_details=f"SQL: {sql_query}, Error: {db_error}"  # Logged, not shown
)
```

---

## Enforcement

### Automated Checks

| Tool | Check | Severity |
|------|-------|----------|
| pylint | Bare except clauses | error |
| pylint | Too broad exception | warning |
| ruff | B001-B017 (bugbear) | error |
| custom | Missing LOG_EVENT in except blocks | warning |
| custom | Batch processing without DLQ | warning |
| custom | Retry without backoff | warning |

### Code Review Checklist

- [ ] All external calls have try/catch
- [ ] Exceptions are specific, not generic
- [ ] Error messages include context (IDs, operation)
- [ ] LOG_EVENT called before handling
- [ ] No silent failures (catch without action)
- [ ] User-facing errors don't expose internals
- [ ] Transient failures use retry with backoff
- [ ] Batch processing uses DLQ for failures
- [ ] One record failure doesn't kill the batch
- [ ] DLQ monitoring in place for pipelines

---

## Escape Hatch

```python
# standard:disable error-handling-specific-exception - Legacy code migration in progress
try:
    legacy_operation()
except Exception as e:  # noqa: broad-except
    handle_legacy_error(e)
```

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [LOGGING.md](LOGGING.md) | Errors must use structured logging |
| [PIPELINE_STANDARD.md](PIPELINE_STANDARD.md) | Pipeline error handling requirements |
| [CODE_QUALITY.md](CODE_QUALITY.md) | Exception types must be explicit |
| [TESTING.md](TESTING.md) | Error paths must be tested |

---

## Industry Alignment

This standard incorporates best practices from:
- [Tenacity Documentation](https://tenacity.readthedocs.io/) - Retry library
- [AWS Dead Letter Queue Pattern](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Google SRE Book - Error Budgets](https://sre.google/sre-book/embracing-risk/)
- [Real Python: Exceptions and Error Handling](https://realpython.com/python-exceptions/)

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-25 | Added DLQ pattern, retry strategies, batch isolation | Claude |
| 2025-01-XX | Initial standard | Claude |

---

*Every failure anticipated. Every record preserved. Never drop data.*
