# HOLD Persistence Pattern

## Overview

**HOLD → AGENT → HOLD always keeps data in HOLD₂ until confirmed written to BigQuery.**

This ensures data safety and provides a backup mechanism.

## Pattern: HOLD₁ → AGENT → HOLD₂ → BigQuery

### Flow

```
1. HOLD₁: Receives data (JSONL/DuckDB)
   └─ Data persists in HOLD₁

2. AGENT: Transforms data
   └─ Processes in batches

3. HOLD₂: Delivers transformed data (JSONL/DuckDB)
   └─ Data persists in HOLD₂ (NEVER auto-deleted)

4. BigQuery: Load from HOLD₂
   └─ Loads data from HOLD₂ JSONL

5. Verification: Confirm BigQuery write
   └─ Verify records exist in BigQuery

6. Confirmation: HOLD₂ remains as backup
   └─ HOLD₂ files persist even after BigQuery load
```

## Rules

### 1. HOLD₂ Never Auto-Deleted

**Rule:** HOLD₂ files are NEVER automatically deleted.

- HOLD₂ JSONL and DuckDB files persist after BigQuery load
- They serve as backup and confirmation source
- Only remove manually after confirming BigQuery write
- HOLD₂ is the source of truth until BigQuery confirms

### 2. BigQuery Verification Required

**Rule:** Always verify BigQuery write before considering data "delivered".

```python
# Load to BigQuery
count = load_jsonl_to_bigquery(client, hold2_jsonl, table_name, schema)

# Verify write
verified = verify_bigquery_write(client, table_name, count, run_id)

if verified:
    print("✅ BigQuery write confirmed - HOLD₂ data verified")
    print("   HOLD₂ files remain as backup (not deleted)")
else:
    print("⚠️  BigQuery verification incomplete - HOLD₂ data preserved")
    print("   HOLD₂ files remain until verification succeeds")
```

### 3. HOLD₂ as Backup

**Rule:** HOLD₂ serves as backup until BigQuery confirmation.

- If BigQuery load fails, data is still in HOLD₂
- Can retry BigQuery load from HOLD₂
- HOLD₂ provides audit trail
- HOLD₂ enables data recovery

## Implementation

### PrimitivePattern (Automatic)

`PrimitivePattern` automatically follows this pattern:

```python
pattern = PrimitivePattern.from_paths(
    input_path="hold1.jsonl",
    output_path="hold2.jsonl",  # Persists after execution
    agent=my_agent,
)

result = pattern.execute()
# HOLD₂ files are written and persist
# They are NOT deleted after execution
```

### Manual Verification

After loading to BigQuery, verify the write:

```python
from scripts.gemini.gemini_web_stage_4 import verify_bigquery_write

# Load to BigQuery
stage4_count = load_jsonl_to_bigquery(
    bq_client,
    hold2_jsonl,
    TABLE_STAGE_4,
    schema,
)

# Verify write
verified = verify_bigquery_write(
    bq_client,
    TABLE_STAGE_4,
    stage4_count,
    run_id,
)

if verified:
    # BigQuery write confirmed
    # HOLD₂ remains as backup (not deleted)
    pass
else:
    # Verification failed - HOLD₂ data preserved
    # Can retry BigQuery load from HOLD₂
    pass
```

## Benefits

### Data Safety
- **No data loss:** HOLD₂ persists until BigQuery confirms
- **Backup available:** Can retry if BigQuery load fails
- **Audit trail:** HOLD₂ provides complete history

### Error Recovery
- **Retry capability:** Can reload from HOLD₂ if BigQuery fails
- **Verification:** Confirms data integrity
- **Recovery:** HOLD₂ enables data recovery

### Traceability
- **Complete history:** HOLD₂ preserves all transformations
- **Audit trail:** Can trace data from HOLD₁ → HOLD₂ → BigQuery
- **Debugging:** HOLD₂ enables debugging and analysis

## File Locations

### HOLD₂ Files
- **JSONL:** `Primitive/staging/{pipeline_name}_stage_{N}/hold2_output.jsonl`
- **DuckDB:** `Primitive/staging/{pipeline_name}_stage_{N}/hold2_output.duckdb`

### Persistence
- Files persist after `pattern.execute()` completes
- Files persist after BigQuery load
- Files persist after verification
- Only remove manually after confirming BigQuery write

## Example: Gemini Web Stage 4

```python
# Execute pattern
result = pattern.execute()
# HOLD₂ files written: hold2_output.jsonl, hold2_output.duckdb

# Load to BigQuery
stage4_count = load_jsonl_to_bigquery(
    bq_client,
    hold2_jsonl,
    TABLE_STAGE_4,
    schema,
)

# Verify write
verified = verify_bigquery_write(
    bq_client,
    TABLE_STAGE_4,
    stage4_count,
    run_id,
)

if verified:
    print("✅ BigQuery write confirmed")
    print("   HOLD₂ files remain as backup")
    # HOLD₂ files are NOT deleted
    # They persist for backup and audit
else:
    print("⚠️  Verification failed - HOLD₂ preserved")
    # Can retry BigQuery load from HOLD₂
```

## Checklist

When implementing a pipeline:

- [ ] HOLD₂ files persist after `pattern.execute()`
- [ ] BigQuery load reads from HOLD₂ (not deletes it)
- [ ] Verification confirms BigQuery write
- [ ] HOLD₂ files remain after verification
- [ ] HOLD₂ serves as backup until manual cleanup
- [ ] Documentation explains HOLD₂ persistence

## Important Notes

1. **HOLD₂ is NOT temporary:** It's a persistent staging area
2. **Never auto-delete:** HOLD₂ files should persist
3. **Verification required:** Always verify BigQuery write
4. **Backup purpose:** HOLD₂ enables recovery and retry
5. **Manual cleanup:** Only remove HOLD₂ after confirming BigQuery write

## Resources

- **PrimitivePattern:** `src/services/central_services/primitive_pattern/pattern.py`
- **Verification:** `scripts/gemini/gemini_web_stage_4.py` - `verify_bigquery_write()`
- **Example:** `pipelines/gemini_web/scripts/stage_4/` for reference implementation
