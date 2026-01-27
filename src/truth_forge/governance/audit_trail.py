"""Audit Trail - Operation Recording and Compliance.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/governance/audit_trail.py
- Version: 2.0.0
- Date: 2026-01-26

Every operation in the cell is recorded for:
- Traceability (who did what, when)
- Compliance (prove operations followed THE_PATTERN)
- Debugging (understand what happened)
- Learning (patterns of behavior over time)

The audit trail is append-only and immutable - it is itself a HOLD2.

BIOLOGICAL METAPHOR:
- AuditTrail = Cellular memory
- AuditRecord = Memory trace
- Categories = Memory types (procedural, semantic, episodic)
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from truth_forge.core.paths import DATA_ROOT


logger = logging.getLogger(__name__)


def _generate_run_id() -> str:
    """Generate a unique run ID.

    Returns:
        A run ID string.
    """
    return f"run_{uuid4().hex[:12]}"


# Module-level run ID (single run context)
_CURRENT_RUN_ID: str | None = None


def get_current_run_id() -> str:
    """Get or create the current run ID.

    Returns:
        Current run ID for this session.
    """
    global _CURRENT_RUN_ID
    if _CURRENT_RUN_ID is None:
        _CURRENT_RUN_ID = _generate_run_id()
    return _CURRENT_RUN_ID


class AuditLevel(Enum):
    """Severity/importance of audit records."""

    DEBUG = "debug"  # Detailed tracing
    INFO = "info"  # Normal operations
    WARNING = "warning"  # Potential issues
    ERROR = "error"  # Failed operations
    CRITICAL = "critical"  # System integrity issues
    VIOLATION = "violation"  # Policy violations


class AuditCategory(Enum):
    """Categories of auditable events."""

    HOLD_OPERATION = "hold_operation"  # HOLD1/HOLD2 access
    AGENT_ACTION = "agent_action"  # Agent transformation
    GOVERNANCE = "governance"  # Policy enforcement
    COST = "cost"  # Resource consumption
    FEDERATION = "federation"  # Colony communication
    SYSTEM = "system"  # System-level events


@dataclass
class AuditRecord:
    """A single audit trail entry."""

    # Identity
    audit_id: str = field(default_factory=lambda: f"audit_{uuid4().hex[:12]}")
    run_id: str = field(default_factory=get_current_run_id)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Classification
    level: AuditLevel = AuditLevel.INFO
    category: AuditCategory = AuditCategory.SYSTEM

    # Event details
    operation: str = ""
    component: str = ""
    target: str | None = None

    # Outcome
    success: bool = True
    error_message: str | None = None

    # Context
    context: dict[str, Any] = field(default_factory=dict)

    # Metadata
    source_file: str | None = None
    source_line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation.
        """
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        d["level"] = self.level.value
        d["category"] = self.category.value
        return d

    def to_json(self) -> str:
        """Convert to JSON string.

        Returns:
            JSON string representation.
        """
        return json.dumps(self.to_dict())


class AuditTrail:
    """Records and manages audit trail entries.

    The audit trail is the memory of operations - every significant
    action is recorded for compliance, debugging, and learning.

    Storage:
    - In-memory buffer for recent records
    - JSONL file for persistence (append-only)

    Example:
        trail = AuditTrail()

        # Record an operation
        trail.record(
            operation="write",
            component="pattern_executor",
            target="hold2",
            category=AuditCategory.HOLD_OPERATION,
            context={"records": 100}
        )

        # Record a violation
        trail.record_violation(
            operation="direct_hold2_write",
            reason="Attempted to bypass AGENT"
        )

        # Query recent records
        recent = trail.get_recent(limit=100)
    """

    def __init__(
        self,
        storage_path: Path | None = None,
        buffer_size: int = 1000,
        auto_flush: bool = True,
    ) -> None:
        """Initialize audit trail.

        Args:
            storage_path: Path to JSONL file (defaults to data/local/audit/audit_trail.jsonl)
            buffer_size: Max records to keep in memory
            auto_flush: Whether to auto-flush to disk
        """
        if storage_path is None:
            storage_path = DATA_ROOT / "local" / "audit" / "audit_trail.jsonl"

        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.buffer_size = buffer_size
        self.auto_flush = auto_flush
        self._buffer: list[AuditRecord] = []

        logger.info("AuditTrail initialized", extra={"storage_path": str(self.storage_path)})

    def record(
        self,
        operation: str,
        component: str,
        target: str | None = None,
        level: AuditLevel = AuditLevel.INFO,
        category: AuditCategory = AuditCategory.SYSTEM,
        success: bool = True,
        error_message: str | None = None,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> AuditRecord:
        """Record an operation in the audit trail.

        Args:
            operation: What was done
            component: Who did it
            target: What it was done to
            level: Severity level
            category: Event category
            success: Whether operation succeeded
            error_message: Error if failed
            context: Additional context
            **kwargs: Extra fields for context

        Returns:
            The created audit record
        """
        # Merge kwargs into context
        full_context = context or {}
        full_context.update(kwargs)

        audit_record = AuditRecord(
            operation=operation,
            component=component,
            target=target,
            level=level,
            category=category,
            success=success,
            error_message=error_message,
            context=full_context,
        )

        self._add_record(audit_record)
        return audit_record

    def record_success(
        self,
        operation: str,
        component: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Shorthand for recording a successful operation.

        Args:
            operation: What was done
            component: Who did it
            context: Additional context

        Returns:
            The created audit record
        """
        return self.record(
            operation=operation,
            component=component,
            success=True,
            context=context,
        )

    def record_failure(
        self,
        operation: str,
        error_message: str,
        component: str = "unknown",
        context: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Shorthand for recording a failed operation.

        Args:
            operation: What was attempted
            error_message: Why it failed
            component: Who attempted it
            context: Additional context

        Returns:
            The created audit record
        """
        return self.record(
            operation=operation,
            component=component,
            success=False,
            error_message=error_message,
            level=AuditLevel.ERROR,
            context=context,
        )

    def record_violation(
        self,
        operation: str,
        reason: str,
        component: str = "governance",
        context: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Record a policy violation.

        Args:
            operation: What was attempted
            reason: Why it was denied
            component: What enforced the policy
            context: Additional context

        Returns:
            The created audit record
        """
        return self.record(
            operation=operation,
            component=component,
            success=False,
            error_message=reason,
            level=AuditLevel.VIOLATION,
            category=AuditCategory.GOVERNANCE,
            context=context,
        )

    def record_hold_operation(
        self,
        operation: str,
        hold_layer: str,
        component: str,
        records_count: int = 0,
        success: bool = True,
        context: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Record a HOLD layer operation.

        Args:
            operation: What was done
            hold_layer: Which HOLD layer
            component: Who did it
            records_count: Number of records affected
            success: Whether it succeeded
            context: Additional context

        Returns:
            The created audit record
        """
        ctx = context or {}
        ctx["hold_layer"] = hold_layer
        ctx["records_count"] = records_count

        return self.record(
            operation=operation,
            component=component,
            target=hold_layer,
            category=AuditCategory.HOLD_OPERATION,
            success=success,
            context=ctx,
        )

    def record_cost(
        self,
        service: str,
        operation: str,
        cost_usd: float,
        context: dict[str, Any] | None = None,
    ) -> AuditRecord:
        """Record a cost event.

        Args:
            service: Which service incurred the cost
            operation: What operation
            cost_usd: Cost in USD
            context: Additional context

        Returns:
            The created audit record
        """
        ctx = context or {}
        ctx["cost_usd"] = cost_usd

        return self.record(
            operation=operation,
            component=service,
            category=AuditCategory.COST,
            context=ctx,
        )

    def _add_record(self, record: AuditRecord) -> None:
        """Add record to buffer and optionally flush.

        Args:
            record: The audit record to add
        """
        self._buffer.append(record)

        # Log based on level
        log_msg = f"[{record.category.value}] {record.operation}"
        if record.target:
            log_msg += f" -> {record.target}"

        if record.level == AuditLevel.VIOLATION:
            logger.warning(log_msg, extra=record.context)
        elif record.level in (AuditLevel.ERROR, AuditLevel.CRITICAL):
            logger.error(log_msg, extra=record.context)
        else:
            logger.debug(log_msg, extra=record.context)

        # Auto-flush if buffer full
        if self.auto_flush and len(self._buffer) >= self.buffer_size:
            self.flush()

    def flush(self) -> int:
        """Flush buffer to disk.

        Returns:
            Number of records flushed
        """
        if not self._buffer:
            return 0

        count = len(self._buffer)

        with open(self.storage_path, "a", encoding="utf-8") as f:
            for record in self._buffer:
                f.write(record.to_json() + "\n")

        self._buffer.clear()
        logger.debug(
            "Flushed audit records", extra={"count": count, "path": str(self.storage_path)}
        )

        return count

    def get_recent(self, limit: int = 100) -> list[AuditRecord]:
        """Get recent records from buffer.

        Args:
            limit: Max records to return

        Returns:
            List of recent records (newest first)
        """
        return list(reversed(self._buffer[-limit:]))

    def get_violations(self, limit: int = 100) -> list[AuditRecord]:
        """Get recent violations.

        Args:
            limit: Max violations to return

        Returns:
            List of violation records (newest first)
        """
        violations = [r for r in self._buffer if r.level == AuditLevel.VIOLATION]
        return list(reversed(violations[-limit:]))

    def query(
        self,
        category: AuditCategory | None = None,
        level: AuditLevel | None = None,
        component: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> list[AuditRecord]:
        """Query records with filters.

        Args:
            category: Filter by category
            level: Filter by level
            component: Filter by component
            since: Only records after this time
            limit: Max records to return

        Returns:
            Matching records (newest first)
        """
        results: list[AuditRecord] = []

        for record in reversed(self._buffer):
            if len(results) >= limit:
                break

            if category and record.category != category:
                continue
            if level and record.level != level:
                continue
            if component and record.component != component:
                continue
            if since and record.timestamp < since:
                continue

            results.append(record)

        return results

    def __enter__(self) -> AuditTrail:
        """Context manager entry.

        Returns:
            Self for context manager use.
        """
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - flush remaining records."""
        self.flush()


__all__ = [
    "AuditCategory",
    "AuditLevel",
    "AuditRecord",
    "AuditTrail",
    "get_current_run_id",
]
