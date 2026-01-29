# Truth_Engine vs Truth_Forge Pipeline Comparison

**Date**: 2026-01-27  
**Critical Finding**: **BOTH pipelines have the SAME schema mismatch problem**

---

## Key Finding

**Both Truth_Engine and Truth_Forge have IDENTICAL schema definitions for `entity_unified`** - and **BOTH are WRONG**. Neither matches the actual BigQuery table schema.

---

## Differences Between Pipelines

### 1. **Import Structure**

**Truth_Engine**:
```python
from src.services.central_services.core import get_logger, get_current_run_id
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error
```

**Truth_Forge**:
```python
from shared.logging_bridge import get_logger, get_current_run_id
# Fallback implementations for missing central_services
def get_bigquery_client(): ...
def PipelineTracker(*args, **kwargs): ...
def require_diagnostic_on_error(error, context): ...
```

**Difference**: Truth_Forge uses fallback implementations, Truth_Engine uses central services directly.

---

### 2. **SQL Injection Prevention**

**Truth_Engine**:
- ❌ **NO SQL injection validation**
- Direct table ID usage: `FROM `{STAGE_15_TABLE}``
- Direct table ID usage: `FROM `{ENTITY_UNIFIED_TABLE}``

**Truth_Forge**:
- ✅ **HAS SQL injection validation**
- Uses `validate_table_id()` before queries
- Validated table IDs: `FROM `{validated_stage_15_table}``

**Difference**: Truth_Forge has security hardening, Truth_Engine does not.

---

### 3. **Data Persistence Pattern**

**Truth_Engine**:
```python
# Direct insert - no duplicate prevention
errors = bq_client.insert_rows_json(ENTITY_UNIFIED_TABLE, records_to_insert)
```

**Truth_Forge**:
```python
# Idempotent merge with fallback
merge_rows_to_table(
    client=bq_client,
    table_id=validated_entity_unified_table,
    rows=records_to_insert,
    match_key="entity_id"
)
```

**Difference**: Truth_Forge uses idempotent merge, Truth_Engine uses direct insert.

---

### 4. **DateTime Handling**

**Truth_Engine**:
```python
promoted_at = datetime.now(timezone.utc).isoformat()
```

**Truth_Forge**:
```python
promoted_at = datetime.now(UTC).isoformat()
```

**Difference**: Minor - both use UTC, different import style.

---

### 5. **Type Hints**

**Truth_Engine**:
```python
) -> Dict[str, Any]:
```

**Truth_Forge**:
```python
) -> dict[str, Any]:
```

**Difference**: Truth_Forge uses lowercase `dict` (Python 3.9+), Truth_Engine uses `Dict` (typing).

---

## CRITICAL: Schema Mismatch (BOTH PIPELINES)

**Both pipelines define the SAME incorrect schema:**

```python
ENTITY_UNIFIED_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),  # ❌ Doesn't exist in actual table
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("text", "STRING"),
    bigquery.SchemaField("role", "STRING"),  # ❌ Doesn't exist
    bigquery.SchemaField("message_type", "STRING"),  # ❌ Doesn't exist
    # ... 28 more fields that don't exist in actual table
]
```

**Actual BigQuery table has:**
- `entity_id`, `level`, `entity_type`, `entity_mode`, `parent_id`
- `source_ids` (REPEATED), `conversation_id`, `turn_id`, `message_id`, `sentence_id`, `span_id`, `word_id`
- `text`, `source_pipeline`, `source_file`, `source_file_path`, `source_system`
- `metadata` (JSON), `created_at`, `updated_at`, `ingestion_job_id`, `ingestion_timestamp`
- `validation_status`, `source_message_timestamp`, `persona`, `content_date`, `canonical_form`
- `l7_count`, `l6_count`, `l5_count`, `l4_count`, `l3_count`, `l2_count`

---

## Why It's "Always Out of Order"

The schema mismatch means:
1. **Stage 16 tries to create table with wrong schema** → BigQuery ignores it (table already exists with different schema)
2. **Stage 16 tries to insert data** → **FAILS** because fields don't match
3. **Pipeline appears to run** but **no data actually gets written**

This is why you've had to do the pipeline "so many times" - the data never actually makes it to the final table because the schemas don't match.

---

## Summary

| Aspect | Truth_Engine | Truth_Forge |
|--------|--------------|-------------|
| **Schema Definition** | ❌ Wrong (36 fields, doesn't match) | ❌ Wrong (36 fields, doesn't match) |
| **SQL Injection Prevention** | ❌ None | ✅ Has validation |
| **Data Persistence** | ❌ Direct insert (no idempotency) | ✅ Merge with fallback |
| **Error Handling** | Basic | Enhanced |
| **Central Services** | ✅ Uses directly | ⚠️ Fallback implementations |

**Bottom Line**: Truth_Forge has better code quality (security, idempotency), but **BOTH have the same fundamental problem** - the schema doesn't match the actual table.

---

## Required Fix

**Both pipelines need to be updated to match the actual BigQuery schema:**

1. Remove fields that don't exist (source_name, role, message_type, etc.)
2. Add fields that do exist (entity_type, entity_mode, conversation_id, turn_id, etc.)
3. Map enrichment data to `metadata` JSON field
4. Derive hierarchical IDs from entity hierarchy

---

**The schema mismatch is the root cause of why the pipeline keeps failing.**
