# Pipeline Logging

**Logging patterns for batch processing and pipelines.**

---

## Stage Transition Logging

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

---

## Batch Progress Logging

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

---

## Cost Tracking in Logs

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

## Context Binding with structlog

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

## UP

[logging/INDEX.md](INDEX.md)
