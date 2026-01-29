# Stage 2 Persistence Fix - Enable Step Back

**Date**: 2026-01-27  
**Issue**: Stage 2 was deleting current run_id's data before inserting, preventing ability to step back  
**Fix**: Changed to use idempotent merge pattern like Stages 1 and 3

## Problem

**Before**: Stage 2 used DELETE + INSERT pattern:
```python
# Delete current run_id's data
DELETE FROM stage_2 WHERE run_id = '{run_id}'
# Then insert new data
INSERT INTO stage_2 SELECT ... FROM stage_1 WHERE run_id = '{run_id}'
```

**Issue**: This deletes the current run's data before inserting, which means:
- If you re-run Stage 2, it overwrites that run_id's data
- You cannot "step back" to see previous runs
- Data from previous runs with the same run_id is lost

## Solution

**After**: Stage 2 now uses idempotent merge pattern:
```python
# Query cleaned data
SELECT ... FROM stage_1 WHERE run_id = '{run_id}'
# Then merge (idempotent - preserves all runs)
merge_rows_to_table(
    client=client,
    table_id=stage_2_table,
    rows=cleaned_records,
    match_key="fingerprint"
)
```

**Benefits**:
- ✅ Preserves all runs (can step back)
- ✅ Idempotent (can re-run without issues)
- ✅ Prevents duplicates (uses fingerprint as match_key)
- ✅ Consistent with Stages 1 and 3

## Changes Made

### Modified Function: `process_cleaning()`

**Before**:
- Used `DELETE FROM ... WHERE run_id` + `INSERT INTO ...`
- Deleted current run's data before inserting

**After**:
- Uses `SELECT` to get cleaned data
- Converts to Python records
- Uses `merge_rows_to_table()` with `fingerprint` as match_key
- Processes in batches of 1000 for memory efficiency

## Verification

All stages now use consistent persistence pattern:

| Stage | Pattern | Match Key | Persists All Runs? |
|-------|---------|-----------|-------------------|
| Stage 1 | `merge_rows_to_table()` | `fingerprint` | ✅ Yes |
| Stage 2 | `merge_rows_to_table()` | `fingerprint` | ✅ Yes (fixed) |
| Stage 3 | `merge_rows_to_table()` | `entity_id` | ✅ Yes |

## Impact

✅ **All stages (1, 2, 3) now persist data**  
✅ **Ability to step back preserved**  
✅ **Consistent pattern across all stages**  
✅ **No data loss on re-runs**

## Testing

To verify the fix works:
1. Run Stage 1 → Check table has data
2. Run Stage 2 → Check table has data (should persist)
3. Re-run Stage 2 → Check that data is still there (idempotent)
4. Check that you can query previous runs
