"""Standardized Event Schema for HOLD Pattern.

Implements Event Sourcing schema per RESEARCH_FINDINGS.md:
- Append-only events in HOLD₁
- Full correlation/causation tracking
- Immutable event records

This schema is used across all services for consistent event handling.

Example JSONL record in hold1/:
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "event_type": "record.created",
        "aggregate_type": "knowledge",
        "aggregate_id": "123e4567-e89b-12d3-a456-426614174000",
        "data": {"content": "...", "source": "..."},
        "metadata": {
            "correlation_id": "...",
            "causation_id": "...",
            "trace_id": "...",
            "span_id": "...",
            "run_id": "run_abc123",
            "timestamp": "2026-01-26T12:00:00Z",
            "version": 1,
            "service": "knowledge-service"
        }
    }
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    """Standard event types for HOLD pattern.

    Follow past-tense naming convention for events
    (events describe what happened, not what should happen).
    """

    # Record lifecycle
    RECORD_CREATED = "record.created"
    RECORD_UPDATED = "record.updated"
    RECORD_DELETED = "record.deleted"
    RECORD_ARCHIVED = "record.archived"

    # Processing events
    PROCESSING_STARTED = "processing.started"
    PROCESSING_COMPLETED = "processing.completed"
    PROCESSING_FAILED = "processing.failed"

    # Sync events (HOLD₁ → HOLD₂)
    SYNC_STARTED = "sync.started"
    SYNC_COMPLETED = "sync.completed"
    SYNC_FAILED = "sync.failed"

    # Signal events (errors, duplicates)
    SIGNAL_ERROR = "signal.error"
    SIGNAL_DUPLICATE = "signal.duplicate"
    SIGNAL_WARNING = "signal.warning"

    # Service events
    SERVICE_STARTED = "service.started"
    SERVICE_STOPPED = "service.stopped"
    SERVICE_HEALTH_CHECK = "service.health_check"

    # Custom (for service-specific events)
    CUSTOM = "custom"


class EventMetadata(BaseModel):
    """Event metadata for traceability and correlation.

    Provides full audit trail and distributed tracing integration.
    """

    model_config = ConfigDict(frozen=True)

    # Correlation chain (per Event Sourcing best practices)
    correlation_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Links related events across services",
    )
    causation_id: str | None = Field(
        default=None,
        description="ID of the event that caused this one",
    )

    # OpenTelemetry integration
    trace_id: str | None = Field(
        default=None,
        description="OpenTelemetry trace ID (32-char hex)",
    )
    span_id: str | None = Field(
        default=None,
        description="OpenTelemetry span ID (16-char hex)",
    )

    # Run tracking (pipeline/batch context)
    run_id: str | None = Field(
        default=None,
        description="Pipeline or batch run identifier",
    )

    # Temporal
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred (UTC)",
    )

    # Schema versioning
    version: int = Field(
        default=1,
        description="Event schema version for evolution",
    )

    # Source attribution
    service: str | None = Field(
        default=None,
        description="Service that emitted this event",
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict, excluding None values."""
        data = self.model_dump()
        # Convert datetime to ISO string
        data["timestamp"] = self.timestamp.isoformat()
        # Remove None values for cleaner JSONL
        return {k: v for k, v in data.items() if v is not None}


class Event(BaseModel):
    """Canonical event structure for HOLD pattern.

    This is the standard format for all events written to hold1/.
    Events are immutable once created.

    Attributes:
        id: Unique event identifier (UUID v4).
        event_type: Type of event (from EventType enum).
        aggregate_type: Type of aggregate this event relates to.
        aggregate_id: ID of the aggregate this event relates to.
        data: Event payload (domain-specific data).
        metadata: Correlation, tracing, and audit metadata.
    """

    model_config = ConfigDict(frozen=True)

    # Identity
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier",
    )

    # Event classification
    event_type: EventType = Field(
        description="Type of event that occurred",
    )
    aggregate_type: str = Field(
        description="Type of aggregate (e.g., 'knowledge', 'identity')",
    )
    aggregate_id: str | None = Field(
        default=None,
        description="ID of the aggregate this event relates to",
    )

    # Payload
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Event payload with domain-specific data",
    )

    # Metadata
    metadata: EventMetadata = Field(
        default_factory=EventMetadata,
        description="Correlation and audit metadata",
    )

    def to_jsonl(self) -> str:
        """Convert to JSONL-compatible string (single line JSON).

        Returns:
            JSON string suitable for appending to JSONL file.
        """
        import json

        data = self.model_dump()
        # Convert enums to strings
        data["event_type"] = self.event_type.value
        # Convert metadata
        data["metadata"] = self.metadata.to_dict()
        return json.dumps(data, default=str)

    def child_event(
        self,
        event_type: EventType,
        data: dict[str, Any] | None = None,
        aggregate_id: str | None = None,
    ) -> Event:
        """Create a child event with causation chain.

        The new event inherits correlation_id and sets this event's
        id as its causation_id.

        Args:
            event_type: Type of the child event.
            data: Optional new payload.
            aggregate_id: Optional new aggregate ID.

        Returns:
            New Event with proper causation chain.
        """
        return Event(
            event_type=event_type,
            aggregate_type=self.aggregate_type,
            aggregate_id=aggregate_id or self.aggregate_id,
            data=data or {},
            metadata=EventMetadata(
                correlation_id=self.metadata.correlation_id,
                causation_id=self.id,
                trace_id=self.metadata.trace_id,
                span_id=self.metadata.span_id,
                run_id=self.metadata.run_id,
                service=self.metadata.service,
            ),
        )


# Type variable for generic event creation
T = TypeVar("T", bound=dict[str, Any])


def create_event(
    event_type: EventType,
    aggregate_type: str,
    data: dict[str, Any],
    aggregate_id: str | None = None,
    correlation_id: str | None = None,
    causation_id: str | None = None,
    run_id: str | None = None,
    service: str | None = None,
) -> Event:
    """Factory function for creating events with proper metadata.

    Automatically captures OpenTelemetry trace context if available.

    Args:
        event_type: Type of event.
        aggregate_type: Type of aggregate (e.g., 'knowledge').
        data: Event payload.
        aggregate_id: Optional aggregate identifier.
        correlation_id: Optional correlation ID (generates if None).
        causation_id: Optional causation ID.
        run_id: Optional run/batch identifier.
        service: Optional service name.

    Returns:
        Properly constructed Event with full metadata.

    Example:
        >>> event = create_event(
        ...     event_type=EventType.RECORD_CREATED,
        ...     aggregate_type="knowledge",
        ...     data={"content": "...", "source": "web"},
        ...     service="knowledge-service",
        ... )
        >>> # Write to hold1/
        >>> with open(intake_file, "a") as f:
        ...     f.write(event.to_jsonl() + "\\n")
    """
    # Try to get trace context from OpenTelemetry
    trace_id = None
    span_id = None
    try:
        from opentelemetry import trace as otel_trace

        span = otel_trace.get_current_span()
        if span.is_recording():
            ctx = span.get_span_context()
            trace_id = format(ctx.trace_id, "032x")
            span_id = format(ctx.span_id, "016x")
    except ImportError:
        pass  # OpenTelemetry not available

    # Try to get run_id from context if not provided
    if run_id is None:
        try:
            from truth_forge.observability.context import get_run_id

            run_id = get_run_id()
        except ImportError:
            pass

    metadata = EventMetadata(
        correlation_id=correlation_id or str(uuid.uuid4()),
        causation_id=causation_id,
        trace_id=trace_id,
        span_id=span_id,
        run_id=run_id,
        service=service,
    )

    return Event(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        data=data,
        metadata=metadata,
    )
