# Stage 4 Data Loss - Root Cause Analysis

**Date**: 2026-01-27  
**Issue**: Stage 4 has only 8 rows when Stage 3 has 226,972 rows (99.996% data loss)

## Root Cause - CONFIRMED

### The Problem

Stage 4 uses `CREATE OR REPLACE TABLE` which **completely replaces** the table on each run. When Stage 4 was executed with a different `run_id` that only had 8 rows in Stage 3, it replaced all previous data.

### Evidence

**Stage 3 Data:**
- Total rows: 226,972
- Run IDs: 
  - `run_60885139`: 127,472 rows
  - `run_e9b8a6d2`: 99,500 rows
- All required fields present (no NULLs in critical fields)

**Stage 4 Data:**
- Total rows: 8
- Run ID: `run_9ee6effe` (different from Stage 3 run_ids)
- Only 8 rows from a test run or different data source

### Code Analysis

**Current Stage 4 Implementation:**
```sql
CREATE OR REPLACE TABLE `{STAGE_4_TABLE}` AS
SELECT ...
FROM `{STAGE_3_TABLE}`
-- NO WHERE CLAUSE - processes ALL data
```

**Issues:**
1. `CREATE OR REPLACE` replaces entire table (not incremental)
2. No `run_id` filtering when reading from Stage 3
3. If run with different run_id context, only processes that run's data
4. Previous data is lost on each run

## Impact

- **Data Loss**: 226,964 rows (99.996%)
- **Blocking**: Cannot proceed with stages 5-8 without Stage 4 data
- **Risk**: High - design flaw allows data loss on any re-run

## Recommended Fix

### Option 1: Add run_id Filtering (RECOMMENDED)

Modify `process_staging` to filter by run_id:

```python
def process_staging(
    client: bigquery.Client,
    run_id: str,
    dry_run: bool,
) -> dict[str, int]:
    # ... existing code ...
    
    staging_query = f"""
    CREATE OR REPLACE TABLE `{STAGE_4_TABLE}` AS
    SELECT
        ...
    FROM `{STAGE_3_TABLE}`
    WHERE run_id = '{run_id}'  -- ADD THIS FILTER
    """
```

**Pros:**
- Prevents processing data from other runs
- Maintains data integrity
- Clear intent

**Cons:**
- Only processes current run's data
- May need to handle multiple runs differently

### Option 2: Change to INSERT with Deduplication

Change from `CREATE OR REPLACE` to `INSERT` with run_id tracking:

```python
# Delete existing data for this run_id first
delete_query = f"""
DELETE FROM `{STAGE_4_TABLE}`
WHERE run_id = '{run_id}'
"""

# Then insert new data
insert_query = f"""
INSERT INTO `{STAGE_4_TABLE}`
SELECT ... FROM `{STAGE_3_TABLE}`
WHERE run_id = '{run_id}'
"""
```

**Pros:**
- Preserves data from other runs
- Allows incremental processing
- Better for multi-run scenarios

**Cons:**
- More complex logic
- Requires DELETE before INSERT

### Option 3: Process All Current Data (Quick Fix)

Simply re-run Stage 4 to process all current Stage 3 data:

```bash
python pipelines/adapters/claude_code/scripts/stage_4/claude_code_stage_4.py
```

This will restore 226,972 rows but doesn't fix the underlying issue.

## Immediate Action Plan

1. **Short-term**: Re-run Stage 4 to restore data (Option 3)
2. **Long-term**: Implement run_id filtering (Option 1 or 2)
3. **Verification**: Run `assess_pipeline_state.py` to confirm data restored
4. **Testing**: Add test to prevent this issue in future

## Prevention

Add validation to Stage 4:
- Check input row count vs output row count
- Warn if output is significantly less than input
- Fail if data loss exceeds threshold (e.g., >10%)
