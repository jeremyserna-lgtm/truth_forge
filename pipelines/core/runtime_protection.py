"""Runtime protection - patches BigQuery client to block streaming inserts.

This module MUST be imported early in any pipeline execution.
It monkey-patches the BigQuery client to prevent streaming inserts.

Per DATA PROTECTION LAWS:
- Streaming inserts cause duplicates (8.9 MILLION duplicates in Jan-Feb 2026)
- Use load_table_from_file() with LoadJobConfig instead
- This module makes streaming inserts IMPOSSIBLE at runtime

Usage:
    # At the top of any pipeline entry point:
    from pipelines.core.runtime_protection import activate_protection
    activate_protection()

    # Or just import the module (auto-activates):
    import pipelines.core.runtime_protection

Example:
    >>> from pipelines.core.runtime_protection import activate_protection
    >>> activate_protection()
    >>>
    >>> from google.cloud import bigquery
    >>> client = bigquery.Client()
    >>> client.insert_rows_json(table, rows)  # Raises RuntimeError
    RuntimeError: BLOCKED: Streaming insert (insert_rows_json) is forbidden.
"""
from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar


logger = logging.getLogger(__name__)


_PROTECTION_ACTIVE = False
_ORIGINAL_INSERT_ROWS_JSON: Callable[..., Any] | None = None
_ORIGINAL_INSERT_ROWS: Callable[..., Any] | None = None


T = TypeVar("T")


def _blocked_streaming_insert(*args: Any, **kwargs: Any) -> None:
    """Replacement function that always raises.

    This is patched onto bigquery.Client.insert_rows_json to prevent
    any streaming insert operations.
    """
    raise RuntimeError(
        "BLOCKED: Streaming insert (insert_rows_json) is FORBIDDEN.\n"
        "\n"
        "Per DATA PROTECTION LAWS:\n"
        "- Streaming inserts caused 8.9 MILLION duplicate rows\n"
        "- Use load_table_from_file() with LoadJobConfig instead\n"
        "\n"
        "Example of correct pattern:\n"
        "    job_config = LoadJobConfig(\n"
        "        source_format=SourceFormat.NEWLINE_DELIMITED_JSON,\n"
        "        write_disposition=WriteDisposition.WRITE_APPEND,\n"
        "    )\n"
        "    client.load_table_from_file(source_file, table_id, job_config=job_config)\n"
        "\n"
        "See: CLAUDE.md DATA PROTECTION LAWS"
    )


def _blocked_insert_rows(*args: Any, **kwargs: Any) -> None:
    """Replacement function that always raises.

    This is patched onto bigquery.Client.insert_rows to prevent
    any streaming insert operations.
    """
    raise RuntimeError(
        "BLOCKED: Streaming insert (insert_rows) is FORBIDDEN.\n"
        "\n"
        "Per DATA PROTECTION LAWS:\n"
        "- Streaming inserts caused 8.9 MILLION duplicate rows\n"
        "- Use load_table_from_file() with LoadJobConfig instead\n"
        "\n"
        "See: CLAUDE.md DATA PROTECTION LAWS"
    )


def activate_protection() -> None:
    """Activate runtime protection by patching BigQuery client.

    MUST be called before any BigQuery operations.
    Once activated, any attempt to use streaming inserts will raise RuntimeError.

    This function is idempotent - calling it multiple times is safe.
    """
    global _PROTECTION_ACTIVE, _ORIGINAL_INSERT_ROWS_JSON, _ORIGINAL_INSERT_ROWS

    if _PROTECTION_ACTIVE:
        logger.debug("runtime_protection_already_active")
        return

    try:
        from google.cloud import bigquery
    except ImportError:
        logger.warning(
            "runtime_protection_bigquery_not_installed",
            extra={"message": "google-cloud-bigquery not installed, protection not needed"},
        )
        return

    # Save original methods (for potential restoration in tests)
    _ORIGINAL_INSERT_ROWS_JSON = bigquery.Client.insert_rows_json
    _ORIGINAL_INSERT_ROWS = bigquery.Client.insert_rows

    # Patch streaming insert methods
    bigquery.Client.insert_rows_json = _blocked_streaming_insert  # type: ignore[method-assign]
    bigquery.Client.insert_rows = _blocked_insert_rows  # type: ignore[method-assign]

    _PROTECTION_ACTIVE = True
    logger.info(
        "runtime_protection_activated",
        extra={
            "patched_methods": ["insert_rows_json", "insert_rows"],
            "protection": "streaming_inserts_blocked",
        },
    )


def deactivate_protection() -> None:
    """Deactivate runtime protection (for testing only).

    WARNING: Only use this in test fixtures. Never in production code.
    """
    global _PROTECTION_ACTIVE, _ORIGINAL_INSERT_ROWS_JSON, _ORIGINAL_INSERT_ROWS

    if not _PROTECTION_ACTIVE:
        return

    try:
        from google.cloud import bigquery
    except ImportError:
        return

    if _ORIGINAL_INSERT_ROWS_JSON is not None:
        bigquery.Client.insert_rows_json = _ORIGINAL_INSERT_ROWS_JSON  # type: ignore[method-assign]
    if _ORIGINAL_INSERT_ROWS is not None:
        bigquery.Client.insert_rows = _ORIGINAL_INSERT_ROWS  # type: ignore[method-assign]

    _PROTECTION_ACTIVE = False
    logger.warning(
        "runtime_protection_deactivated",
        extra={"warning": "Protection disabled - only valid in test fixtures"},
    )


def is_protection_active() -> bool:
    """Check if runtime protection is active.

    Returns:
        True if streaming inserts are blocked, False otherwise.
    """
    return _PROTECTION_ACTIVE


class ProtectionContext:
    """Context manager for temporarily disabling protection (tests only).

    Usage:
        # In test fixtures ONLY:
        with ProtectionContext(enabled=False):
            # Streaming inserts allowed here
            client.insert_rows_json(table, rows)
        # Protection re-enabled automatically
    """

    def __init__(self, enabled: bool = True) -> None:
        """Initialize protection context.

        Args:
            enabled: If True (default), ensure protection is active.
                    If False, temporarily disable protection.
        """
        self._enabled = enabled
        self._was_active = False

    def __enter__(self) -> "ProtectionContext":
        self._was_active = is_protection_active()

        if self._enabled:
            activate_protection()
        else:
            deactivate_protection()

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        # Restore previous state
        if self._was_active:
            activate_protection()
        else:
            deactivate_protection()

        return False


def require_protection(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that ensures protection is active before function runs.

    Usage:
        @require_protection
        def write_to_bigquery(records):
            # Protection guaranteed to be active here
            ...
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        if not is_protection_active():
            activate_protection()
            logger.info(
                "protection_auto_activated",
                extra={"function": func.__name__},
            )
        return func(*args, **kwargs)

    return wrapper


# Auto-activate on import
# This ensures protection is always active when this module is imported
activate_protection()
