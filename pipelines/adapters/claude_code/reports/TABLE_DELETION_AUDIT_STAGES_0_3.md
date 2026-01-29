# Table Deletion Audit - Stages 0, 1, 2, 3

**Date**: 2026-01-27  
**Purpose**: Verify that stages 0-3 do not remove or clear tables when they complete

## Summary

✅ **All stages are SAFE** - No operations that remove or clear entire tables

## Detailed Analysis

### Stage 0: Assessment (Read-Only)

**Status**: ✅ **SAFE** - Does not write to BigQuery at all

**Operations**:
- Reads JSONL session files from source directory
- Creates assessment report (JSON file)
- Creates discovery manifest file
- **No BigQuery operations**
- **No table writes**
- **No table deletions**

**Conclusion**: Stage 0 is completely safe - it's read-only and doesn't touch BigQuery tables.

---

### Stage 1: Extraction

**Status**: ✅ **SAFE** - Only inserts data, never deletes

**Operations**:
- Creates table if it doesn't exist (`create_stage_1_table`)
- Uses `merge_rows_to_table()` for idempotent inserts
- **No DELETE operations**
- **No DROP TABLE**
- **No TRUNCATE**

**Code Pattern**:
```python
# Only uses merge_rows_to_table (idempotent insert/update)
merge_rows_to_table(
    client=client,
    table_id=validated_table,
    rows=records,
    match_key="fingerprint"
)
```

**Conclusion**: Stage 1 only adds data - never removes it. Safe for re-runs.

---

### Stage 2: Cleaning

**Status**: ✅ **SAFE** - Only deletes data for current run_id (intentional for idempotency)

**Operations**:
- **DELETE FROM table WHERE run_id = '{validated_run_id}'** - Only deletes current run's data
- Then INSERTs cleaned data for current run
- **No DROP TABLE**
- **No TRUNCATE**
- **No DELETE without WHERE clause**

**Code Pattern**:
```python
# First delete existing data for THIS run_id only
delete_query = f"""
DELETE FROM `{validated_stage_2_table}`
WHERE run_id = '{validated_run_id}'
"""

# Then insert new cleaned data for THIS run_id
cleaning_query = f"""
INSERT INTO `{validated_stage_2_table}`
SELECT ... FROM `{validated_stage_1_table}`
WHERE run_id = '{validated_run_id}'
"""
```

**Why This Is Safe**:
- Only affects data for the current `run_id`
- Preserves data from other runs
- This is intentional for idempotency (allows re-running Stage 2 without duplicates)
- **Does NOT delete all data** - only current run's data

**Conclusion**: Stage 2 is safe - it only deletes data for the current run_id, preserving all other runs.

---

### Stage 3: Identity Generation

**Status**: ✅ **SAFE** - Only inserts data, never deletes

**Operations**:
- Uses `merge_rows_to_table()` for idempotent inserts
- **No DELETE operations**
- **No DROP TABLE**
- **No TRUNCATE**

**Code Pattern**:
```python
# Only uses merge_rows_to_table (idempotent insert/update)
merge_rows_to_table(
    client=client,
    table_id=validated_stage_3_table,
    rows=records_to_insert,
    match_key="entity_id"
)
```

**Conclusion**: Stage 3 only adds data - never removes it. Safe for re-runs.

---

## Rollback Scripts (Separate from Main Stages)

**Note**: Rollback scripts (`rollback_stage_X.py`) are separate utilities that:
- Only run when explicitly called by the user
- Delete data for a specific `run_id` only
- Require confirmation before deletion
- Are NOT called by the main stage scripts

**These are safe** because:
- They're separate scripts, not part of the main pipeline
- They require explicit user action
- They only delete specific run_ids (not all data)

---

## Why Stages 1 and 2 Are Empty

Based on the audit, the empty tables are NOT caused by the stage scripts themselves. Possible reasons:

1. **Stages 1 and 2 were never run** - Data was loaded directly into Stage 3
2. **Rollback scripts were used** - Someone explicitly ran rollback scripts to clear data
3. **Manual deletion** - Data was manually deleted from BigQuery
4. **Different run_id** - Data exists but with a different run_id than expected

**The stage scripts themselves do NOT clear tables automatically.**

---

## Recommendations

1. ✅ **No changes needed** - All stages are safe
2. **To populate Stages 1 and 2**: Re-run stages 1 and 2 to populate them from source files
3. **To verify data**: Check if data exists with different run_ids

---

## Conclusion

✅ **All stages (0, 1, 2, 3) are SAFE**

- **Stage 0**: Read-only, no BigQuery operations
- **Stage 1**: Only inserts data (idempotent)
- **Stage 2**: Only deletes current run_id's data (intentional for idempotency)
- **Stage 3**: Only inserts data (idempotent)

**No stages remove or clear entire tables when they complete.**
