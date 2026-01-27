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
