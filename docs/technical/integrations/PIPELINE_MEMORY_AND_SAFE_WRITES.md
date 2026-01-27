# Pipeline Memory Management and Safe Writes

## Overview

All pipelines must follow efficient memory rules and use safe writes that persist beyond errors.

## Memory Management Rules

### 1. Incremental Writes (REQUIRED)

**Rule:** Never accumulate all records in memory. Write incrementally after each batch.

```python
# ✅ CORRECT: Write after each batch
for batch in batches:
    outputs = process_batch(batch)
    write_to_hold2(outputs)  # Write immediately
    del outputs  # Clear memory
    gc.collect()  # Force cleanup for large batches

# ❌ WRONG: Accumulating all in memory
all_outputs = []
for batch in batches:
    outputs = process_batch(batch)
    all_outputs.extend(outputs)  # Memory grows!
write_to_hold2(all_outputs)  # Only at end
```

### 2. Memory Cleaning (REQUIRED)

**Rule:** Explicitly clear batches from memory after writing.

```python
# After each batch write:
del batch_outputs
batch = []
if batch_size >= 1000:
    import gc
    gc.collect()  # Force garbage collection
```

### 3. Constant Memory Usage

**Rule:** Only one batch should be in memory at a time.

- Process batch → Write → Clear → Next batch
- Memory usage should remain constant regardless of dataset size
- Can process datasets of any size without out-of-memory errors

## Safe Write Rules

### 1. Atomic Writes (REQUIRED)

**Rule:** All file writes must be atomic (write to temp, then rename).

```python
from src.services.central_services.core.safe_writes import safe_append_jsonl

# ✅ CORRECT: Atomic write
written = safe_append_jsonl(
    file_path="output.jsonl",
    records=batch_outputs,
    dedupe_key="content"
)

# ❌ WRONG: Direct write (not atomic)
with open("output.jsonl", "a") as f:
    for record in batch_outputs:
        f.write(json.dumps(record) + "\n")
```

### 2. Error Recovery (REQUIRED)

**Rule:** Writes must persist even if pipeline crashes mid-execution.

- Atomic writes ensure partial writes don't corrupt files
- Checkpoint files allow resuming from last successful batch
- Original files are preserved if write fails

### 3. Transaction Safety (REQUIRED for DuckDB)

**Rule:** Use safe transactions for DuckDB writes.

```python
from src.services.central_services.core.safe_writes import safe_duckdb_transaction

# ✅ CORRECT: Safe transaction
with safe_duckdb_transaction(db_path) as conn:
    conn.execute("INSERT INTO ...")
    # Commits on success, rolls back on error

# ❌ WRONG: Direct connection (no transaction safety)
conn = duckdb.connect(db_path)
conn.execute("INSERT INTO ...")  # No rollback on error
```

## Implementation Pattern

### PrimitivePattern (Automatic)

If using `PrimitivePattern`, safe writes are automatic:

```python
pattern = PrimitivePattern.from_paths(
    input_path="hold1.jsonl",
    output_path="hold2.jsonl",
    agent=my_agent,
    batch_size=1000,  # Process in batches
)

result = pattern.execute()
# ✅ Automatically:
# - Writes incrementally after each batch
# - Uses atomic writes
# - Clears memory after each batch
# - Safe DuckDB transactions
```

### Custom Pipelines

For custom pipelines, follow this pattern:

```python
from src.services.central_services.core.safe_writes import (
    safe_append_jsonl,
    safe_duckdb_transaction,
    create_checkpoint,
    load_checkpoint,
)

# Load checkpoint (if resuming)
checkpoint = load_checkpoint("checkpoint.json")
start_batch = checkpoint.get("last_batch", 0) if checkpoint else 0

batch = []
batch_num = start_batch

for record in input_records:
    batch.append(record)

    if len(batch) >= batch_size:
        # Process batch
        outputs = process_batch(batch)

        # Safe atomic write
        written = safe_append_jsonl(
            "output.jsonl",
            outputs,
            dedupe_key="content"
        )

        # Safe DuckDB write
        with safe_duckdb_transaction("output.duckdb") as conn:
            write_to_duckdb(conn, outputs)

        # Create checkpoint
        create_checkpoint("checkpoint.json", {
            "last_batch": batch_num,
            "records_written": written,
        })

        # Memory cleanup
        del outputs
        batch = []
        batch_num += 1

        if batch_size >= 1000:
            import gc
            gc.collect()
```

## Benefits

### Memory Efficiency
- **Constant memory usage:** Only one batch in memory at a time
- **Scalable:** Can process datasets of any size
- **No OOM errors:** Memory is freed after each batch

### Data Safety
- **Atomic writes:** Partial writes don't corrupt files
- **Error recovery:** Can resume from checkpoints
- **No data loss:** Original files preserved on errors

### Performance
- **Progress visibility:** Files grow incrementally (can monitor)
- **Faster recovery:** Resume from last checkpoint
- **Efficient I/O:** Batch writes are more efficient

## Checklist

When implementing a pipeline, ensure:

- [ ] Writes are incremental (after each batch)
- [ ] Memory is cleared after each batch (`del`, `gc.collect()`)
- [ ] Uses `safe_append_jsonl()` for JSONL writes
- [ ] Uses `safe_duckdb_transaction()` for DuckDB writes
- [ ] Checkpoint files created for error recovery
- [ ] Constant memory usage (only one batch in memory)
- [ ] No accumulation of all records in memory

## Examples

### Example 1: PrimitivePattern (Recommended)

```python
# ✅ All safety built-in
pattern = PrimitivePattern.from_paths(
    input_path="input.jsonl",
    output_path="output.jsonl",
    agent=my_agent,
    batch_size=1000,
)
result = pattern.execute()
```

### Example 2: Custom Pipeline

```python
# ✅ Manual implementation with safe writes
from src.services.central_services.core.safe_writes import (
    safe_append_jsonl,
    safe_duckdb_transaction,
)

batch = []
for record in input_records:
    batch.append(record)
    if len(batch) >= 1000:
        outputs = process(batch)

        # Safe atomic write
        safe_append_jsonl("output.jsonl", outputs)

        # Safe DuckDB write
        with safe_duckdb_transaction("output.duckdb") as conn:
            write_to_db(conn, outputs)

        # Memory cleanup
        del outputs
        batch = []
        gc.collect()
```

## Migration Guide

### Updating Existing Pipelines

1. **Replace direct file writes:**
   ```python
   # Old
   with open("output.jsonl", "a") as f:
       f.write(json.dumps(record) + "\n")

   # New
   safe_append_jsonl("output.jsonl", [record])
   ```

2. **Add incremental writes:**
   ```python
   # Old
   all_outputs = []
   for batch in batches:
       all_outputs.extend(process(batch))
   write_all(all_outputs)

   # New
   for batch in batches:
       outputs = process(batch)
       safe_append_jsonl("output.jsonl", outputs)
       del outputs
   ```

3. **Use safe DuckDB transactions:**
   ```python
   # Old
   conn = duckdb.connect("db.duckdb")
   conn.execute("INSERT ...")

   # New
   with safe_duckdb_transaction("db.duckdb") as conn:
       conn.execute("INSERT ...")
   ```

## HOLD Persistence Pattern

### HOLD₂ Persists Until BigQuery Confirmation

**Rule:** HOLD₂ data persists until BigQuery write is confirmed.

- HOLD₂ files are NEVER automatically deleted
- BigQuery verification confirms write succeeded
- HOLD₂ serves as backup until manual cleanup
- Data persists beyond errors

See: `docs/HOLD_PERSISTENCE_PATTERN.md` for complete details.

## Resources

- **Safe Write Utilities:** `src/services/central_services/core/safe_writes.py`
- **PrimitivePattern:** `src/services/central_services/primitive_pattern/pattern.py`
- **HOLD Persistence:** `docs/HOLD_PERSISTENCE_PATTERN.md`
- **Examples:** See `pipelines/gemini_web/scripts/stage_4/` for reference implementation
