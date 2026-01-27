"""Hold Isolation - HOLD1/HOLD2 Boundary Enforcement.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/governance/hold_isolation.py
- Version: 2.0.0
- Date: 2026-01-26

This module enforces the sacred boundaries of THE_PATTERN:
- HOLD1 (intake) can only be written by external sources
- AGENT transforms HOLD1 -> HOLD2
- HOLD2 (processed) is the output, protected from direct writes

The flow is unidirectional:
    External -> HOLD1 -> AGENT -> HOLD2 -> Consumers

Violations:
- Writing directly to HOLD2 (bypassing AGENT)
- Reading from HOLD1 without AGENT context
- Modifying HOLD2 after creation (immutable)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar


logger = logging.getLogger(__name__)


class HoldLayer(Enum):
    """The two HOLD layers in THE_PATTERN."""

    HOLD1 = "hold1"  # Intake layer (raw, unprocessed)
    HOLD2 = "hold2"  # Output layer (processed, immutable)
    AGENT = "agent"  # Transformation context


class OperationType(Enum):
    """Types of operations on HOLD layers."""

    READ = "read"
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"
    MODIFY = "modify"


@dataclass
class IsolationViolation:
    """Record of a boundary violation."""

    timestamp: datetime
    operation: OperationType
    source: HoldLayer
    target: HoldLayer
    path: Path | None
    reason: str
    context: dict[str, Any] = field(default_factory=dict)


class HoldIsolation:
    """Enforces HOLD1/HOLD2 boundary integrity.

    The membrane around each HOLD layer ensures:
    1. HOLD1 receives external writes only
    2. HOLD2 receives AGENT writes only
    3. HOLD2 is immutable once written
    4. No layer can be bypassed

    BIOLOGICAL METAPHOR:
    - HoldIsolation = Cell membrane
    - HOLD1 = Input receptors
    - HOLD2 = Output secretion
    - AGENT = Internal processing

    Example:
        isolation = HoldIsolation()

        # Check if operation is allowed
        if isolation.check("write", source="external", target="hold1"):
            # Proceed with write
            pass

        # Get violation reason
        allowed, reason = isolation.check_with_reason(...)
    """

    # Valid operation flows
    ALLOWED_FLOWS: ClassVar[dict[tuple[str, OperationType, HoldLayer], bool]] = {
        # (source, operation, target) -> allowed
        ("external", OperationType.WRITE, HoldLayer.HOLD1): True,
        ("external", OperationType.APPEND, HoldLayer.HOLD1): True,
        ("agent", OperationType.READ, HoldLayer.HOLD1): True,
        ("agent", OperationType.WRITE, HoldLayer.HOLD2): True,
        ("agent", OperationType.APPEND, HoldLayer.HOLD2): True,
        ("consumer", OperationType.READ, HoldLayer.HOLD2): True,
        # Explicitly forbidden
        ("external", OperationType.WRITE, HoldLayer.HOLD2): False,  # Bypass
        ("external", OperationType.MODIFY, HoldLayer.HOLD2): False,  # Immutable
        ("agent", OperationType.MODIFY, HoldLayer.HOLD2): False,  # Immutable
        ("consumer", OperationType.WRITE, HoldLayer.HOLD2): False,  # Read-only
    }

    def __init__(self, strict_mode: bool = True) -> None:
        """Initialize isolation enforcer.

        Args:
            strict_mode: If True, unknown flows are denied. If False, warned.
        """
        self.strict_mode = strict_mode
        self.violations: list[IsolationViolation] = []

    def check(
        self,
        operation: str | OperationType,
        source: str,
        target: str | HoldLayer,
        path: Path | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """Check if an operation is allowed.

        Args:
            operation: The operation type (read, write, append, etc.)
            source: Where the operation originates (external, agent, consumer)
            target: The target HOLD layer
            path: Optional path for logging
            context: Additional context for audit

        Returns:
            True if allowed, False if denied
        """
        allowed, _ = self.check_with_reason(operation, source, target, path, context)
        return allowed

    def check_with_reason(
        self,
        operation: str | OperationType,
        source: str,
        target: str | HoldLayer,
        path: Path | None = None,
        context: dict[str, Any] | None = None,
    ) -> tuple[bool, str]:
        """Check operation and return reason if denied.

        Args:
            operation: The operation type
            source: Where the operation originates
            target: The target HOLD layer
            path: Optional path for logging
            context: Additional context for audit

        Returns:
            Tuple of (allowed, reason)
        """
        # Normalize inputs
        if isinstance(operation, str):
            try:
                operation = OperationType(operation.lower())
            except ValueError:
                return False, f"Unknown operation type: {operation}"

        if isinstance(target, str):
            try:
                target = HoldLayer(target.lower())
            except ValueError:
                return False, f"Unknown HOLD layer: {target}"

        source = source.lower()

        # Check allowed flows
        flow_key = (source, operation, target)

        if flow_key in self.ALLOWED_FLOWS:
            if self.ALLOWED_FLOWS[flow_key]:
                logger.debug(
                    "Isolation check passed",
                    extra={
                        "source": source,
                        "operation": operation.value,
                        "target": target.value,
                        "path": str(path) if path else None,
                    },
                )
                return True, "allowed"
            else:
                reason = self._get_violation_reason(source, operation, target)
                self._record_violation(operation, source, target, path, reason, context)
                return False, reason

        # Unknown flow
        if self.strict_mode:
            reason = f"Unknown flow not allowed in strict mode: {source} -> {operation.value} -> {target.value}"
            self._record_violation(operation, source, target, path, reason, context)
            return False, reason
        else:
            logger.warning(
                "Unknown flow allowed (non-strict)",
                extra={
                    "source": source,
                    "operation": operation.value,
                    "target": target.value,
                },
            )
            return True, "allowed (non-strict)"

    def _get_violation_reason(
        self,
        source: str,
        operation: OperationType,
        target: HoldLayer,
    ) -> str:
        """Get human-readable violation reason.

        Args:
            source: Where the operation originates
            operation: The operation type
            target: The target HOLD layer

        Returns:
            Human-readable reason string
        """
        if target == HoldLayer.HOLD2:
            if source == "external":
                return "HOLD2 cannot receive direct external writes - must go through AGENT"
            if operation in (OperationType.MODIFY, OperationType.DELETE):
                return "HOLD2 is immutable - modifications not allowed"
            if source == "consumer":
                return "Consumers can only read from HOLD2"

        if target == HoldLayer.HOLD1:
            if source == "consumer":
                return "Consumers should read from HOLD2, not HOLD1"

        return f"Flow not allowed: {source} -> {operation.value} -> {target.value}"

    def _record_violation(
        self,
        operation: OperationType,
        source: str,
        target: HoldLayer,
        path: Path | None,
        reason: str,
        context: dict[str, Any] | None,
    ) -> None:
        """Record a violation for audit.

        Args:
            operation: The operation type
            source: Where the operation originates
            target: The target HOLD layer
            path: Optional path
            reason: Violation reason
            context: Additional context
        """
        # Determine source layer
        try:
            source_layer = HoldLayer(source)
        except ValueError:
            source_layer = HoldLayer.AGENT

        violation = IsolationViolation(
            timestamp=datetime.now(UTC),
            operation=operation,
            source=source_layer,
            target=target,
            path=path,
            reason=reason,
            context=context or {},
        )
        self.violations.append(violation)

        logger.warning(
            "HOLD isolation violation",
            extra={
                "reason": reason,
                "operation": operation.value,
                "source": source,
                "target": target.value,
                "path": str(path) if path else None,
            },
        )

    def get_violations(self) -> list[IsolationViolation]:
        """Get all recorded violations.

        Returns:
            Copy of violations list
        """
        return self.violations.copy()

    def clear_violations(self) -> int:
        """Clear violations and return count.

        Returns:
            Number of violations cleared
        """
        count = len(self.violations)
        self.violations.clear()
        return count

    def assert_allowed(
        self,
        operation: str | OperationType,
        source: str,
        target: str | HoldLayer,
        path: Path | None = None,
    ) -> None:
        """Assert operation is allowed, raise if not.

        Args:
            operation: The operation type
            source: Where the operation originates
            target: The target HOLD layer
            path: Optional path for logging

        Raises:
            PermissionError: If operation violates isolation
        """
        allowed, reason = self.check_with_reason(operation, source, target, path)
        if not allowed:
            raise PermissionError(f"HOLD isolation violation: {reason}")


__all__ = [
    "HoldIsolation",
    "HoldLayer",
    "IsolationViolation",
    "OperationType",
]
