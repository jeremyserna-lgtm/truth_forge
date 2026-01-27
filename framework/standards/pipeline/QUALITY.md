# Pipeline Quality

**Quality gates, code standards, and error handling for pipelines.**

**Status**: ACTIVE
**Owner**: Framework
**Parent**: [INDEX.md](INDEX.md)

---

## Quality Gates

### Required Checks

| Gate | Check | Enforcement |
|------|-------|-------------|
| Type hints | All functions typed (PEP 484) | mypy --strict |
| Linting | No violations | ruff check |
| Formatting | Consistent style | ruff format --check |
| Tests | Coverage >80% | pytest --cov |
| Docstrings | All public functions | Review |

### Before Merge

```bash
# All must pass
mypy pipelines/{pipeline}/ --strict
ruff check pipelines/{pipeline}/
ruff format --check pipelines/{pipeline}/
pytest pipelines/{pipeline}/tests/ -v --cov
```

---

## Anti-Patterns

### ❌ Streaming Instead of Batch

```python
# WRONG
for row in client.query(query).result():
    process_and_write(row)

# CORRECT
rows = list(client.query(query).result())
results = [process(r) for r in rows]
write_batch(results)
```

### ❌ Direct Stage-to-Stage

```python
# WRONG
result = stage_2.process(stage_1_data)

# CORRECT
data = read_from_hold_1()
result = process(data)
write_to_hold_2(result)
```

### ❌ Missing Error Handling

```python
# WRONG
def process(data):
    return transform(data)

# CORRECT
def process(data):
    try:
        return transform(data)
    except TransformError as e:
        dlq.send(data, e, "transform")
        raise
```

### ❌ Silent Failures

```python
# WRONG
try:
    process(data)
except Exception:
    pass  # Data lost

# CORRECT
try:
    process(data)
except Exception as e:
    dlq.send(data, e, stage)
    logger.error("Processing failed", extra={"error": str(e)})
```

---

## Error Handling

### Retry with Exponential Backoff

```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    reraise=True,
)
def call_external_api(request: dict) -> dict:
    """Call API with automatic retry."""
    response = api_client.post(request)
    response.raise_for_status()
    return response.json()
```

### Dead Letter Queue

```python
from dataclasses import dataclass
from pathlib import Path
import json

@dataclass
class DLQRecord:
    original_record: dict
    error_type: str
    error_message: str
    stage: str
    timestamp: str

class DeadLetterQueue:
    def __init__(self, path: Path, pipeline: str):
        self.path = path / f"{pipeline}_dlq.jsonl"

    def send(self, record: dict, error: Exception, stage: str) -> None:
        entry = {
            "original_record": record,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stage": stage,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
```

---

## Structured Logging

### Required Pattern

```python
# CORRECT - Structured
logger.info(
    "batch_processed",
    extra={
        "stage": STAGE_NUMBER,
        "batch_size": len(data),
        "success_count": success,
        "failure_count": failure,
    }
)

# WRONG - Unstructured
logger.info(f"Processed {len(data)} records in stage {STAGE_NUMBER}")
```

### Required Fields

| Field | Description | Required |
|-------|-------------|----------|
| stage | Stage number | Yes |
| pipeline | Pipeline name | Yes |
| run_id | Execution run ID | Yes |
| batch_num | Batch number | Recommended |
| record_count | Records processed | Recommended |

---

## Convergence

### Bottom-Up Validation

This document requires:
- [INDEX.md](INDEX.md) - Parent standard
- [code_quality/](../code_quality/) - Code quality rules
- [error_handling/](../error_handling/) - Error handling patterns
- [logging/](../logging/) - Logging standards

### Top-Down Validation

This document is shaped by:
- [06_LAW](../../06_LAW.md) - Fail-Safe, Observability
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE

---

*Type it. Test it. Log it. Never drop data.*
