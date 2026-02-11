# Data Enforcement Rules (MANDATORY)

**Per DATA PROTECTION LAWS: These rules are NON-NEGOTIABLE.**

## YOU MUST NOT

### 1. NEVER use streaming inserts

**Streaming inserts caused 8.9 MILLION duplicate rows.**

```python
# WRONG - FORBIDDEN
client.insert_rows_json(table, rows)
client.insert_rows(table, rows)

# RIGHT - REQUIRED
from pipelines.core.bigquery_safe import SafeBigQueryWriter

writer = SafeBigQueryWriter(client, table_id)
writer.write_batch(records)
```

### 2. NEVER run pipelines without validation

```bash
# WRONG - FORBIDDEN
python pipeline.py
python pipeline.py --skip-validation

# RIGHT - REQUIRED
python pipeline.py --dry-run  # Test first
python pipeline.py            # Validation is mandatory
```

### 3. NEVER hardcode source_pipeline values

```python
# WRONG - FORBIDDEN
source_pipeline = "my_custom_pipeline"
source_pipeline = "test"

# RIGHT - REQUIRED
from pipelines.llm_refinery.enforcement import ALLOWED_PIPELINE
source_pipeline = ALLOWED_PIPELINE  # Always "llm_refinery"
```

### 4. NEVER delete production data without backup

```sql
-- WRONG - FORBIDDEN
DELETE FROM spine.entity_unified WHERE ...

-- RIGHT - REQUIRED
-- 1. Create backup first
CREATE TABLE spine.entity_unified_backup_20260202
AS SELECT * FROM spine.entity_unified;

-- 2. Verify backup has expected rows
SELECT COUNT(*) FROM spine.entity_unified_backup_20260202;

-- 3. Only then proceed with delete
DELETE FROM spine.entity_unified WHERE ...
```

### 5. NEVER use WRITE_TRUNCATE on production tables

```python
# WRONG - FORBIDDEN
job_config = LoadJobConfig(
    write_disposition=WriteDisposition.WRITE_TRUNCATE,  # DESTROYS DATA
)
client.load_table_from_file(f, "spine.entity_unified", job_config=job_config)

# RIGHT - REQUIRED
job_config = LoadJobConfig(
    write_disposition=WriteDisposition.WRITE_APPEND,  # Adds to existing
)
```

### 6. NEVER write silent exception handlers

```python
# WRONG - FORBIDDEN
except Exception:
    pass

except Exception as e:
    continue  # Error swallowed

# RIGHT - REQUIRED
except Exception as e:
    logger.error("operation_failed", extra={"error": str(e)})
    raise

# OR with DLQ
except Exception as e:
    dlq.send(record=record, error_type="PROCESSING_ERROR", error_message=str(e))
    continue  # OK because error is captured
```

### 7. NEVER return None on error

```python
# WRONG - FORBIDDEN
def process_record(record):
    try:
        return do_work(record)
    except Exception:
        return None  # Silent failure

# RIGHT - REQUIRED
def process_record(record):
    try:
        return do_work(record)
    except Exception as e:
        logger.error("process_failed", extra={"error": str(e)})
        raise ProcessingError(f"Failed to process: {e}") from e
```

## YOU MUST

### 1. Import enforcement before BigQuery writes

```python
from pipelines.core.enforcement import enforce_before_write

@enforce_before_write
def write_to_bigquery(records: list[dict]) -> int:
    # Enforcement runs automatically
    ...
```

### 2. Use SafeBigQueryWriter for all writes

```python
from pipelines.core.bigquery_safe import SafeBigQueryWriter

writer = SafeBigQueryWriter(client, "spine.entity_unified")
writer.write_batch(records)  # Creates backup, validates, writes
```

### 3. Verify parent chains

Every entity must have valid parent references:

```
L8 (conversation) → parent_id = NULL
L7 (topic_segment) → parent_id = L8 entity_id
L6 (turn) → parent_id = L7 entity_id
L5 (message) → parent_id = L6 entity_id
L4 (sentence) → parent_id = L5 entity_id
L3 (span) → parent_id = L4 entity_id
L2 (word) → parent_id = L3 entity_id
```

### 4. Use structured logging

```python
# WRONG - FORBIDDEN in production code
print(f"Processed {count} records")

# RIGHT - REQUIRED
logger.info("records_processed", extra={"count": count})
```

### 5. Use DLQ for batch operations

```python
from pipelines.core.dlq import DLQ

dlq = DLQ("my_stage")

for record in records:
    try:
        process(record)
    except Exception as e:
        dlq.send(
            record=record,
            error_type="PROCESSING_ERROR",
            error_message=str(e),
        )
        continue  # OK - error captured in DLQ
```

## Verification

Before any data operation, verify:

```bash
# Run ALL checks
mypy src/ pipelines/ --strict && \
ruff check src/ pipelines/ && \
ruff format --check src/ pipelines/ && \
pytest tests/ -v --cov=src --cov=pipelines --cov-fail-under=90

# If ANY fail, you are NOT done.
```

## Cost of Violation

Past violations have caused:
- December 2025: Corrupted entity_enrichments
- January-February 2026: 8.9 MILLION duplicate rows
- February 2026: Broken parent chains, orphan entities

**THESE RULES EXIST TO PREVENT DATA DESTRUCTION.**
