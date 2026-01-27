# Batch Error Isolation

**One record failure should never kill an entire batch. Isolate failures.**

---

## Batch Result Pattern

```python
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class BatchResult:
    """Result of batch processing with error isolation."""
    successful: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]
    success_count: int
    failure_count: int
    errors: List[Dict[str, Any]]
```

---

## Isolated Processing

```python
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

---

## Large Dataset Processing

```python
def process_large_dataset(
    records: List[Dict[str, Any]],
    batch_size: int = 1000,
    dlq: DeadLetterQueue = None,
    stage: str = "processing",
) -> Dict[str, Any]:
    """Process large dataset in batches with progress tracking."""
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
        "error_summary": all_errors[:10],  # First 10 errors
        "dlq_count": dlq.count() if dlq else 0,
    }
```

---

## The Rule

**Batch processing MUST:**
1. Isolate failures (one bad record doesn't kill batch)
2. Log progress with structured data
3. Send failures to DLQ
4. Return comprehensive results

---

## UP

[error_handling/INDEX.md](INDEX.md)
