"""Claude Code Pipeline - Shared Utilities

Common functions used across all pipeline stages.
Includes retry logic, validation, and data utilities.

🧠 STAGE FIVE GROUNDING
This module exists to provide reusable utilities for all stages.

Structure: Define utilities → Export → Use in stages
Purpose: Eliminate code duplication, ensure consistent behavior
Boundaries: Stateless utilities only, no stage-specific logic
Control: All utilities must be idempotent and well-tested

⚠️ WHAT THIS MODULE CANNOT SEE
- Stage execution context
- BigQuery client state
- Runtime errors in calling code

🔥 THE FURNACE PRINCIPLE
- Truth (input): Function arguments
- Heat (processing): Utility logic execution
- Meaning (output): Processed results
- Care (delivery): Consistent, reliable utilities
"""
from __future__ import annotations

# Use logging bridge or fallback
try:
    from .logging_bridge import get_logger as _get_logger
except Exception:
    try:
        from truth_forge.core.structured_logging import get_logger as _get_logger
    except Exception:
        import logging
        logging.basicConfig(level=logging.INFO)
        def _get_logger(name: str):
            return logging.getLogger(name)

_LOGGER = _get_logger(__name__)
script_id = "pipelines.claude_code.scripts.shared.utilities.py"

import hashlib
import time
from functools import wraps
from typing import Any, Callable, List, Optional, Tuple, TypeVar

from google.api_core import exceptions as google_exceptions
from google.cloud import bigquery

from .constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_DELAYS,
    get_full_table_id,
)

T = TypeVar("T")

# =============================================================================
# RETRY LOGIC
# =============================================================================

def is_retryable_error(error: Exception) -> bool:
    """Check if an error is retryable.

    Args:
        error: The exception to check

    Returns:
        True if the error is transient and should be retried
    """
    retryable_types = (
        google_exceptions.ServiceUnavailable,
        google_exceptions.InternalServerError,
        google_exceptions.TooManyRequests,
        google_exceptions.DeadlineExceeded,
        ConnectionError,
        TimeoutError,
    )
    return isinstance(error, retryable_types)

def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delays: Tuple[int, ...] = DEFAULT_RETRY_DELAYS,
    retryable_check: Callable[[Exception], bool] = is_retryable_error,
) -> Callable[..., T]:
    """Decorator for retry with exponential backoff.

    Args:
        func: Function to wrap
        max_retries: Maximum number of retry attempts
        retry_delays: Tuple of delay seconds for each retry
        retryable_check: Function to check if error is retryable

    Returns:
        Wrapped function with retry logic
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        last_error: Optional[Exception] = None

        for attempt in range(max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if not retryable_check(e) or attempt >= max_retries:
                    raise

                delay = retry_delays[min(attempt, len(retry_delays) - 1)]
                time.sleep(delay)

        # Should never reach here, but for type safety
        raise last_error  # type: ignore  # pragma: no cover

    return wrapper

# =============================================================================
# VALIDATION UTILITIES
# =============================================================================

def validate_input_table_exists(
    client: bigquery.Client,
    table_name: str,
    project: Optional[str] = None,
    dataset: Optional[str] = None,
) -> bool:
    """Validate that input table exists and has data.

    Args:
        client: BigQuery client
        table_name: Table name to check
        project: Optional project override
        dataset: Optional dataset override

    Returns:
        True if table exists and has rows

    Raises:
        ValueError: If table doesn't exist or is empty
    """
    table_id = get_full_table_id(table_name, project, dataset)

    try:
        table = client.get_table(table_id)
        if table.num_rows == 0:
            raise ValueError(f"Input table {table_id} exists but is empty")
        return True
    except google_exceptions.NotFound:
        raise ValueError(f"Input table {table_id} does not exist")

def validate_gate_no_null_identity(
    client: bigquery.Client,
    table_name: str,
    id_column: str = "entity_id",
    project: Optional[str] = None,
    dataset: Optional[str] = None,
) -> Tuple[bool, int]:
    """Validate that no rows have null identity (THE GATE check).

    Args:
        client: BigQuery client
        table_name: Table to check
        id_column: Name of identity column
        project: Optional project override
        dataset: Optional dataset override

    Returns:
        Tuple of (is_valid, null_count)

    Raises:
        ValueError: If null identities found
    """
    table_id = get_full_table_id(table_name, project, dataset)

    query = f"""
    SELECT COUNT(*) as null_count
    FROM `{table_id}`
    WHERE {id_column} IS NULL
    """

    result = client.query(query).result()
    row = next(iter(result))
    null_count = row.null_count

    if null_count > 0:
        raise ValueError(
            f"THE GATE VIOLATION: {null_count} rows have null {id_column} in {table_id}"
        )

    return True, null_count

def verify_row_counts(
    client: bigquery.Client,
    source_table: str,
    target_table: str,
    expected_ratio: float = 1.0,
    tolerance: float = 0.01,
    project: Optional[str] = None,
    dataset: Optional[str] = None,
) -> Tuple[int, int, bool]:
    """Verify row counts between source and target tables.

    Args:
        client: BigQuery client
        source_table: Source table name
        target_table: Target table name
        expected_ratio: Expected target/source ratio (1.0 = same count)
        tolerance: Acceptable deviation from expected ratio
        project: Optional project override
        dataset: Optional dataset override

    Returns:
        Tuple of (source_count, target_count, is_valid)
    """
    source_id = get_full_table_id(source_table, project, dataset)
    target_id = get_full_table_id(target_table, project, dataset)

    try:
        source = client.get_table(source_id)
        target = client.get_table(target_id)

        source_count = source.num_rows or 0
        target_count = target.num_rows or 0

        if source_count == 0:
            return source_count, target_count, target_count == 0

        actual_ratio = target_count / source_count
        is_valid = abs(actual_ratio - expected_ratio) <= tolerance

        return source_count, target_count, is_valid

    except google_exceptions.NotFound as e:
        raise ValueError(f"Table not found: {e}")

# =============================================================================
# DATA UTILITIES
# =============================================================================

def create_fingerprint(*args: Any, prefix: str = "") -> str:
    """Create a deterministic fingerprint from input values.

    Args:
        *args: Values to include in fingerprint
        prefix: Optional prefix for the fingerprint

    Returns:
        32-character hex fingerprint
    """
    content = ":".join(str(arg) for arg in args)
    if prefix:
        content = f"{prefix}:{content}"

    return hashlib.sha256(content.encode()).hexdigest()[:32]

def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks of specified size.

    Args:
        lst: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def safe_json_loads(text: str, default: Any = None) -> Any:
    """Safely load JSON, returning default on error.

    Args:
        text: JSON string to parse
        default: Value to return on parse error

    Returns:
        Parsed JSON or default
    """
    import json

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return default


def get_pipeline_hold2_path(stage: int, pipeline_name: str) -> Path:
    """Get path to pipeline HOLD₂ for a specific stage.
    
    Args:
        stage: Stage number (0-16)
        pipeline_name: Pipeline name (e.g., 'claude_code')
    
    Returns:
        Path to pipeline HOLD₂ JSONL file
    """
    from pathlib import Path
    from .constants import PIPELINE_NAME
    
    # Get pipeline directory (scripts/../..)
    scripts_dir = Path(__file__).resolve().parent.parent
    pipeline_dir = scripts_dir.parent
    staging_dir = pipeline_dir / "staging" / "knowledge_atoms" / f"stage_{stage}"
    staging_dir.mkdir(parents=True, exist_ok=True)
    return staging_dir / "hold2.jsonl"

# =============================================================================
# DUPLICATE PREVENTION - MERGE UTILITIES
# =============================================================================

def merge_rows_to_table(
    client: bigquery.Client,
    table_id: str,
    rows: List[dict[str, Any]],
    match_key: str,
    project: Optional[str] = None,
    dataset: Optional[str] = None,
) -> int:
    """Insert or update rows using MERGE to prevent duplicates.
    
    This function uses BigQuery MERGE statement to ensure idempotent inserts.
    If a row with the same match_key exists, it updates; otherwise, it inserts.
    
    Args:
        client: BigQuery client
        table_id: Target table ID (will be validated)
        rows: List of row dictionaries to merge
        match_key: Column name to use for matching (must exist in rows)
        project: Optional project override
        dataset: Optional dataset override
        
    Returns:
        Number of rows merged (inserted or updated)
        
    Raises:
        ValueError: If table_id is invalid, match_key missing, or merge fails
    """
    if not rows:
        return 0
    
    # Validate table_id using shared_validation
    try:
        from shared_validation import validate_table_id
    except ImportError:
        # Fallback validation
        def validate_table_id(tid: str) -> str:
            if not tid or not isinstance(tid, str):
                raise ValueError(f"Invalid table_id: {tid}")
            if any(danger in tid.upper() for danger in ['--', ';', 'DROP', 'DELETE']):
                raise ValueError(f"Invalid table_id: potential SQL injection: {tid}")
            return tid
    
    full_table_id = get_full_table_id(table_id, project, dataset)
    validated_table_id = validate_table_id(full_table_id)
    
    # Validate match_key exists in all rows
    if not all(match_key in row for row in rows):
        raise ValueError(f"match_key '{match_key}' missing from one or more rows")
    
    # Get table schema to build MERGE statement
    try:
        table = client.get_table(validated_table_id)
        schema = table.schema
        field_names = [field.name for field in schema]
    except google_exceptions.NotFound:
        raise ValueError(f"Table {validated_table_id} does not exist")
    
    # For large batches, use temporary table approach
    # For small batches, use direct insert with duplicate checking via MERGE
    
    if len(rows) > 100:
        # Large batch: use temporary table
        import uuid
        temp_table_id = f"{validated_table_id.replace(':', '_')}_temp_{uuid.uuid4().hex[:8]}"
        
        # Create temp table with same schema
        temp_table = bigquery.Table(temp_table_id, schema=schema)
        client.create_table(temp_table, exists_ok=True)
        
        try:
            # Load rows to temp table
            errors = client.insert_rows_json(temp_table_id, rows)
            if errors:
                raise ValueError(f"Failed to load temp table: {errors[:5]}")
            
            # Build MERGE statement
            update_fields = [f.name for f in schema if f.name != match_key]
            insert_fields = [f.name for f in schema]
            
            merge_query = f"""
            MERGE `{validated_table_id}` AS target
            USING `{temp_table_id}` AS source
            ON target.{match_key} = source.{match_key}
            WHEN MATCHED THEN
                UPDATE SET {', '.join(f"{f} = source.{f}" for f in update_fields)}
            WHEN NOT MATCHED THEN
                INSERT ({', '.join(insert_fields)})
                VALUES ({', '.join(f'source.{f}' for f in insert_fields)})
            """
            
            job = client.query(merge_query)
            job.result()
            
            if job.errors:
                raise ValueError(f"MERGE failed: {job.errors[:5]}")
            
            # Clean up temp table
            client.delete_table(temp_table_id, not_found_ok=True)
            
        except Exception as e:
            # Clean up temp table on error
            try:
                client.delete_table(temp_table_id, not_found_ok=True)
            except Exception:
                pass
            raise
    else:
        # Small batch: use DELETE + INSERT pattern for idempotency
        # This prevents duplicates by deleting existing rows first
        
        # Get all match_key values (validate they're safe)
        from shared_validation import validate_entity_id
        match_values = []
        for row in rows:
            match_val = str(row[match_key])
            # Basic validation to prevent injection
            if any(danger in match_val for danger in ['--', ';', '/*', '*/']):
                raise ValueError(f"Invalid match_key value: potential SQL injection")
            match_values.append(match_val)
        
        # Build safe IN clause
        # Escape single quotes for SQL
        safe_values = ', '.join(f"'{v.replace(chr(39), chr(39) + chr(39))}'" for v in match_values)
        
        # Delete existing rows with these match_keys (for this run_id if present)
        if "run_id" in field_names and all("run_id" in row for row in rows):
            run_ids = list(set(row["run_id"] for row in rows))
            if len(run_ids) == 1:
                from shared_validation import validate_run_id
                safe_run_id = validate_run_id(run_ids[0])
                delete_query = f"""
                DELETE FROM `{validated_table_id}`
                WHERE {match_key} IN ({safe_values})
                AND run_id = '{safe_run_id}'
                """
            else:
                # Escape single quotes for SQL
                safe_run_ids = ', '.join(f"'{validate_run_id(rid).replace(chr(39), chr(39) + chr(39))}'" for rid in run_ids)
                delete_query = f"""
                DELETE FROM `{validated_table_id}`
                WHERE {match_key} IN ({safe_values})
                AND run_id IN ({safe_run_ids})
                """
        else:
            delete_query = f"""
            DELETE FROM `{validated_table_id}`
            WHERE {match_key} IN ({safe_values})
            """
        
        # Execute delete
        delete_job = client.query(delete_query)
        delete_job.result()
        
        if delete_job.errors:
            raise ValueError(f"DELETE failed: {delete_job.errors[:5]}")
        
        # Insert new rows
        errors = client.insert_rows_json(validated_table_id, rows)
        if errors:
            raise ValueError(f"Failed to insert rows: {errors[:5]}")
    
    return len(rows)
