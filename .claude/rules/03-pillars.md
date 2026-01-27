# the four pillars

**06_LAW. these are non-negotiable.**

## the pillars

| pillar | meaning | implication |
|--------|---------|-------------|
| **Fail-Safe** | every failure anticipated, caught, recoverable | DLQ pattern, retry logic |
| **No Magic** | everything explicit, no hidden behavior | no implicit configs, no magic strings |
| **Observability** | every action traceable, every state visible | structured logging, metrics |
| **Idempotency** | same input → same output | deterministic processing |

## Fail-Safe in practice

```python
# CORRECT - failure is visible, data preserved
try:
    result = process_record(record)
except Exception as e:
    dlq.send(record=record, error=e, stage="processing")
    logger.error("Processing failed", extra={"record_id": record.id, "error": str(e)})
    continue  # batch continues

# WRONG - silent loss
except Exception:
    pass
```

## No Magic in practice

```python
# CORRECT - explicit
config = Config(
    batch_size=1000,
    timeout_seconds=30,
    retry_count=3
)

# WRONG - hidden defaults
config = Config()  # what are the values?
```

## Observability in practice

```python
# CORRECT - structured, queryable
logger.info("Batch processed", extra={
    "batch_id": batch.id,
    "record_count": len(records),
    "duration_ms": elapsed,
    "success_rate": successes / total
})

# WRONG - unstructured
logger.info(f"Processed {count} records in {elapsed}ms")
```

## Idempotency in practice

```python
# CORRECT - same input, same output
def process_record(record: Record) -> Result:
    # uses only record data, no external state
    return Result(value=record.value * 2)

# WRONG - depends on mutable state
def process_record(record: Record) -> Result:
    return Result(value=record.value * self.multiplier)  # multiplier can change
```
