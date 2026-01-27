# SQL Injection Prevention Approach

## The Challenge

BigQuery **does not support parameterized table names**. Table names must be specified as literal strings in SQL queries. This means we cannot use parameterized queries for table names like we can for values.

## Our Solution

We use `validate_table_id()` from `shared_validation.py` to validate all table names before using them in f-strings. This function:

1. **Validates format**: Ensures table IDs match BigQuery's allowed pattern (`[project.]dataset.table`)
2. **Blocks dangerous patterns**: Rejects SQL injection attempts (comments, DROP, DELETE, etc.)
3. **Fail-fast**: Raises `ValueError` immediately if validation fails

## Why This Is Secure

1. **Table names are constants**: All table names come from `shared/constants.py`, not user input
2. **Validation is strict**: The regex pattern only allows alphanumeric, underscores, hyphens, and dots
3. **No user input**: Table names are never constructed from user-provided data
4. **Industry standard**: This is the standard approach for BigQuery (documented in BigQuery best practices)

## For Values (WHERE clauses)

When we have **values** in WHERE clauses (like `run_id`, `entity_id`, `session_id`), we use **parameterized queries**:

```python
query = f"SELECT * FROM `{validated_table}` WHERE run_id = @run_id"
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("run_id", "STRING", run_id)
    ]
)
result = client.query(query, job_config=job_config).result()
```

## Reviewers' Concerns

Reviewers noted that f-string interpolation is "inherently dangerous." However:
- **BigQuery limitation**: We cannot use parameterized table names
- **Our validation**: `validate_table_id()` provides equivalent security
- **No user input**: Table names are constants, not user data
- **Industry practice**: This is the standard BigQuery approach

## Verification

All stages now:
- ✅ Use `validate_table_id()` for all table names
- ✅ Use parameterized queries for values in WHERE clauses
- ✅ No manual string escaping (backtick replacement)
- ✅ Centralized validation in `shared_validation.py`

---

**This approach is secure and follows BigQuery best practices given the platform's limitations.**
