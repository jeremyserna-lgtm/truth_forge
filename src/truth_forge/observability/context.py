"""Correlation context management.

Provides context propagation for:
- Correlation IDs (request tracking across services)
- Run IDs (batch/pipeline run tracking)
- Trace IDs (OpenTelemetry distributed tracing)

Aligns with HOLD pattern event schema for full traceability.
"""

from __future__ import annotations

import hashlib
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace


# Context variables for cross-cutting concerns
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_run_id: ContextVar[str | None] = ContextVar("run_id", default=None)
_causation_id: ContextVar[str | None] = ContextVar("causation_id", default=None)


@dataclass
class CorrelationContext:
    """Container for all correlation identifiers.

    Used in HOLD pattern events for full traceability:
    - correlation_id: Links related events across services
    - trace_id: OpenTelemetry distributed trace
    - span_id: Current span in the trace
    - run_id: Pipeline/batch run identifier
    - causation_id: ID of the event that caused this one

    Example:
        >>> ctx = CorrelationContext.current()
        >>> event = {
        ...     "id": str(uuid.uuid4()),
        ...     "data": {...},
        ...     "correlation": ctx.to_dict(),
        ... }
    """

    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trace_id: str | None = None
    span_id: str | None = None
    run_id: str | None = None
    causation_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def current(cls) -> CorrelationContext:
        """Get current correlation context from context vars and OpenTelemetry.

        Returns:
            CorrelationContext populated with current values.
        """
        # Get OpenTelemetry trace context
        span = trace.get_current_span()
        trace_id = None
        span_id = None

        if span.is_recording():
            ctx = span.get_span_context()
            trace_id = format(ctx.trace_id, "032x")
            span_id = format(ctx.span_id, "016x")

        return cls(
            correlation_id=_correlation_id.get() or str(uuid.uuid4()),
            trace_id=trace_id,
            span_id=span_id,
            run_id=_run_id.get(),
            causation_id=_causation_id.get(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for event embedding.

        Returns:
            Dictionary with non-None values only.
        """
        result: dict[str, Any] = {
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
        }
        if self.trace_id:
            result["trace_id"] = self.trace_id
        if self.span_id:
            result["span_id"] = self.span_id
        if self.run_id:
            result["run_id"] = self.run_id
        if self.causation_id:
            result["causation_id"] = self.causation_id
        return result

    def child(self, causation_id: str | None = None) -> CorrelationContext:
        """Create child context with this context as causation.

        Args:
            causation_id: Override causation ID (defaults to this correlation_id).

        Returns:
            New CorrelationContext with causation chain.
        """
        return CorrelationContext(
            correlation_id=self.correlation_id,  # Inherit correlation
            trace_id=self.trace_id,
            span_id=self.span_id,
            run_id=self.run_id,
            causation_id=causation_id or self.correlation_id,
        )


def get_correlation_id() -> str | None:
    """Get current correlation ID from context."""
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID in current context.

    Args:
        correlation_id: UUID string for request/operation tracking.
    """
    _correlation_id.set(correlation_id)


def get_run_id() -> str | None:
    """Get current run ID from context."""
    return _run_id.get()


def set_run_id(run_id: str | None = None) -> str:
    """Set or generate run ID in current context.

    Args:
        run_id: Explicit run ID or None to generate one.

    Returns:
        The run ID that was set.
    """
    if run_id is None:
        # Generate run ID: run_{timestamp_hash}
        timestamp = datetime.now(UTC).isoformat()
        hash_input = f"{timestamp}-{uuid.uuid4()}"
        short_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        run_id = f"run_{short_hash}"

    _run_id.set(run_id)
    return run_id


def get_trace_id() -> str | None:
    """Get current OpenTelemetry trace ID.

    Returns:
        32-character hex trace ID or None if no active span.
    """
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        return format(ctx.trace_id, "032x")
    return None


def get_causation_id() -> str | None:
    """Get current causation ID from context."""
    return _causation_id.get()


def set_causation_id(causation_id: str) -> None:
    """Set causation ID in current context.

    Args:
        causation_id: ID of the event that caused the current operation.
    """
    _causation_id.set(causation_id)
