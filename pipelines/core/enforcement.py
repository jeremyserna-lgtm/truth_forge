"""Universal pipeline enforcement module.

This module provides decorators, context managers, and utilities for
enforcing data protection rules across ALL pipelines.

MUST be imported before any BigQuery writes.

Per DATA PROTECTION LAWS:
- NO DATA PASSES WITHOUT VALIDATION
- NO EXCEPTIONS

Usage:
    from pipelines.core.enforcement import (
        enforce_before_write,
        EnforcementGate,
        require_enforcement,
    )

    @enforce_before_write
    def write_to_bigquery(records: list[dict]) -> int:
        # Enforcement runs automatically before write
        ...

    with EnforcementGate("stage_5") as gate:
        records = gate.validate_input(input_records)
        processed = process(records)
        gate.validate_output(processed)

Author: Claude (Opus 4.5)
Date: 2026-02-02
"""
from __future__ import annotations

import functools
import logging
from typing import Any, Callable, TypeVar

# Import runtime protection (auto-activates)
from pipelines.core.runtime_protection import activate_protection, is_protection_active

# Import enforcement rules from llm_refinery
from pipelines.llm_refinery.enforcement import (
    ALLOWED_PIPELINE,
    ALL_COLUMNS,
    BIGQUERY_SCHEMA,
    EnforcementError,
    EnforcementLevel,
    EnforcementResult,
    EnforcementViolation,
    LEVEL_TO_TYPE,
    REQUIRED_COLUMNS,
    VALID_LEVELS,
    enforce_batch,
    enforce_batch_or_raise,
    enforce_or_raise,
    enforce_record,
    generate_enforcement_report,
    post_process_hook,
    pre_write_hook,
)


logger = logging.getLogger(__name__)


# Re-export everything for convenience
__all__ = [
    # Constants
    "ALLOWED_PIPELINE",
    "ALL_COLUMNS",
    "BIGQUERY_SCHEMA",
    "LEVEL_TO_TYPE",
    "REQUIRED_COLUMNS",
    "VALID_LEVELS",
    # Types
    "EnforcementError",
    "EnforcementLevel",
    "EnforcementResult",
    "EnforcementViolation",
    # Functions
    "enforce_batch",
    "enforce_batch_or_raise",
    "enforce_or_raise",
    "enforce_record",
    "generate_enforcement_report",
    "post_process_hook",
    "pre_write_hook",
    # New utilities
    "enforce_before_write",
    "EnforcementGate",
    "require_enforcement",
    "with_dlq",
]


T = TypeVar("T")


# Ensure protection is active
activate_protection()


def enforce_before_write(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that enforces all rules before any BigQuery write.

    Automatically finds records in function arguments and validates them.
    Raises EnforcementError if any record fails validation.

    Usage:
        @enforce_before_write
        def write_to_bigquery(records: list[dict]) -> int:
            # Enforcement runs automatically before the function executes
            ...

    Args:
        func: Function that writes data to BigQuery

    Returns:
        Wrapped function with enforcement
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        # Ensure runtime protection is active
        if not is_protection_active():
            activate_protection()

        # Find records in args or kwargs
        records = None
        for arg in args:
            if isinstance(arg, list) and arg and isinstance(arg[0], dict):
                records = arg
                break
        if records is None:
            records = kwargs.get("records", kwargs.get("rows", kwargs.get("data")))

        if records:
            result = enforce_batch(records)
            if not result.passed:
                logger.error(
                    "enforcement_failed_before_write",
                    extra={
                        "function": func.__name__,
                        "record_count": result.record_count,
                        "rejected_count": result.rejected_count,
                        "fatal_count": len(result.get_fatals()),
                        "error_count": len(result.get_errors()),
                    },
                )
                raise EnforcementError(result)

            logger.info(
                "enforcement_passed_before_write",
                extra={
                    "function": func.__name__,
                    "record_count": result.record_count,
                    "warning_count": len(result.get_warnings()),
                },
            )

        return func(*args, **kwargs)

    return wrapper


class EnforcementGate:
    """Context manager for enforcement at HOLD→AGENT→HOLD boundaries.

    Validates records at stage entry and exit points.
    Raises EnforcementError if any validation fails.

    Usage:
        with EnforcementGate("stage_5") as gate:
            records = gate.validate_input(input_records)
            processed = process(records)
            gate.validate_output(processed)  # Raises if invalid
    """

    def __init__(self, stage_name: str) -> None:
        """Initialize enforcement gate.

        Args:
            stage_name: Name of the stage (for logging)
        """
        self.stage_name = stage_name
        self._input_result: EnforcementResult | None = None
        self._output_result: EnforcementResult | None = None
        self._input_count = 0
        self._output_count = 0

    def __enter__(self) -> "EnforcementGate":
        # Ensure runtime protection is active
        if not is_protection_active():
            activate_protection()

        logger.info(
            "enforcement_gate_entered",
            extra={"stage": self.stage_name},
        )
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        if exc_type is not None:
            logger.error(
                "enforcement_gate_exception",
                extra={
                    "stage": self.stage_name,
                    "error_type": exc_type.__name__ if exc_type else None,
                    "error": str(exc_val),
                },
            )
        else:
            logger.info(
                "enforcement_gate_exited",
                extra={
                    "stage": self.stage_name,
                    "input_count": self._input_count,
                    "output_count": self._output_count,
                },
            )
        return False  # Don't suppress exceptions

    def validate_input(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate records entering this stage.

        Args:
            records: Records to validate

        Returns:
            Same records (validated)

        Raises:
            EnforcementError: If any record fails validation
        """
        self._input_count = len(records)
        self._input_result = enforce_batch(records)

        if not self._input_result.passed:
            logger.error(
                "enforcement_gate_input_failed",
                extra={
                    "stage": self.stage_name,
                    "record_count": self._input_result.record_count,
                    "rejected_count": self._input_result.rejected_count,
                },
            )
            raise EnforcementError(self._input_result)

        logger.info(
            "enforcement_gate_input_passed",
            extra={
                "stage": self.stage_name,
                "record_count": self._input_count,
            },
        )
        return records

    def validate_output(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Validate records leaving this stage.

        Args:
            records: Records to validate

        Returns:
            Same records (validated)

        Raises:
            EnforcementError: If any record fails validation
        """
        self._output_count = len(records)
        self._output_result = enforce_batch(records)

        if not self._output_result.passed:
            logger.error(
                "enforcement_gate_output_failed",
                extra={
                    "stage": self.stage_name,
                    "record_count": self._output_result.record_count,
                    "rejected_count": self._output_result.rejected_count,
                },
            )
            raise EnforcementError(self._output_result)

        logger.info(
            "enforcement_gate_output_passed",
            extra={
                "stage": self.stage_name,
                "record_count": self._output_count,
            },
        )
        return records

    @property
    def input_result(self) -> EnforcementResult | None:
        """Get the input validation result."""
        return self._input_result

    @property
    def output_result(self) -> EnforcementResult | None:
        """Get the output validation result."""
        return self._output_result


def require_enforcement(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator that ensures runtime protection is active before function runs.

    Use this on any function that touches BigQuery.

    Usage:
        @require_enforcement
        def process_records(records):
            # Runtime protection guaranteed to be active
            ...
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        if not is_protection_active():
            activate_protection()
            logger.info(
                "enforcement_auto_activated",
                extra={"function": func.__name__},
            )
        return func(*args, **kwargs)

    return wrapper


def with_dlq(stage_name: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that adds DLQ (Dead Letter Queue) handling to a function.

    Failed records are sent to DLQ instead of being lost.

    Usage:
        @with_dlq("stage_5")
        def process_batch(records):
            # Failed records automatically go to DLQ
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except EnforcementError as e:
                # Send to DLQ
                from pipelines.core.dlq import DLQ

                dlq = DLQ(stage_name)
                for violation in e.result.violations:
                    if violation.level in (EnforcementLevel.FATAL, EnforcementLevel.ERROR):
                        dlq.send(
                            record_id=violation.record_id or "unknown",
                            error_type=violation.rule,
                            error_message=violation.message,
                            stage=stage_name,
                        )

                logger.error(
                    "records_sent_to_dlq",
                    extra={
                        "stage": stage_name,
                        "count": e.result.rejected_count,
                    },
                )
                raise

        return wrapper

    return decorator
