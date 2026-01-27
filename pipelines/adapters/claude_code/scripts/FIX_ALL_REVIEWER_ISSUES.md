# Fix All Reviewer Issues - Comprehensive Plan

## Issues to Fix

### 1. Verification Scripts ✅ CREATED (Need to improve)
- ✅ Created templates for all 17 stages
- ⏳ Need to implement actual checks (not just TODOs)

### 2. SQL Injection - Parameterized Queries (CRITICAL)
**Problem**: Reviewers say `validate_table_id()` alone isn't enough. Need parameterized queries for VALUES.

**Solution**: 
- Keep `validate_table_id()` for table names (BigQuery doesn't support parameterized table names)
- Use `QueryJobConfig` with `query_parameters` for all VALUE parameters (run_id, entity_id, etc.)
- Example from Stage 9:
```python
count_query = f"SELECT COUNT(*) as cnt FROM `{validated_table}` WHERE run_id = @run_id"
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("run_id", "STRING", run_id)
    ]
)
count_result = client.query(count_query, job_config=job_config).result()
```

**Stages Affected**: All stages with WHERE clauses using values

### 3. Memory/Scalability (HIGH)
**Problem**: Stages 6-10 load entire datasets into memory

**Solution**:
- Stage 6: Already has streaming (lines 564-600) - but reviewers still complain
- Need to verify no memory accumulation
- Use BigQuery iterators, process row-by-row
- Don't accumulate lists in memory

**Stages Affected**: 6, 7, 8, 9, 10

### 4. Error Handling - Non-Coder Friendly (HIGH)
**Problem**: Error messages are technical, require coding knowledge

**Solution**:
- Create user-friendly error messages
- Explain what went wrong in plain language
- Provide actionable steps for non-coders

**Stages Affected**: All 17 stages

### 5. Turn Boundary Logic (MEDIUM)
**Problem**: Stage 6 turn pairing algorithm doesn't match documented definition

**Solution**: Review algorithm and fix to match specification

**Stages Affected**: Stage 6

## Implementation Order

1. ✅ Create verification scripts (templates done, need to implement checks)
2. Fix SQL injection (add parameterized queries for values)
3. Fix memory issues (verify streaming, remove accumulation)
4. Improve error messages (non-coder friendly)
5. Fix turn boundary logic (Stage 6)
