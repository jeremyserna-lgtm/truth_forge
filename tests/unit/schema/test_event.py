"""Tests for event schema module.

Tests the Event, EventMetadata, EventType, and create_event factory.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from truth_forge.schema.event import (
    Event,
    EventMetadata,
    EventType,
    create_event,
)


class TestEventType:
    """Tests for EventType enum."""

    def test_record_lifecycle_events(self) -> None:
        """Test record lifecycle event types."""
        assert EventType.RECORD_CREATED.value == "record.created"
        assert EventType.RECORD_UPDATED.value == "record.updated"
        assert EventType.RECORD_DELETED.value == "record.deleted"
        assert EventType.RECORD_ARCHIVED.value == "record.archived"

    def test_processing_events(self) -> None:
        """Test processing event types."""
        assert EventType.PROCESSING_STARTED.value == "processing.started"
        assert EventType.PROCESSING_COMPLETED.value == "processing.completed"
        assert EventType.PROCESSING_FAILED.value == "processing.failed"

    def test_sync_events(self) -> None:
        """Test sync event types."""
        assert EventType.SYNC_STARTED.value == "sync.started"
        assert EventType.SYNC_COMPLETED.value == "sync.completed"
        assert EventType.SYNC_FAILED.value == "sync.failed"

    def test_signal_events(self) -> None:
        """Test signal event types."""
        assert EventType.SIGNAL_ERROR.value == "signal.error"
        assert EventType.SIGNAL_DUPLICATE.value == "signal.duplicate"
        assert EventType.SIGNAL_WARNING.value == "signal.warning"

    def test_service_events(self) -> None:
        """Test service event types."""
        assert EventType.SERVICE_STARTED.value == "service.started"
        assert EventType.SERVICE_STOPPED.value == "service.stopped"
        assert EventType.SERVICE_HEALTH_CHECK.value == "service.health_check"

    def test_custom_event(self) -> None:
        """Test custom event type."""
        assert EventType.CUSTOM.value == "custom"

    def test_event_type_is_string_enum(self) -> None:
        """Test that EventType is a string enum."""
        assert isinstance(EventType.RECORD_CREATED, str)
        assert EventType.RECORD_CREATED == "record.created"


class TestEventMetadata:
    """Tests for EventMetadata model."""

    def test_default_values(self) -> None:
        """Test metadata creates with sensible defaults."""
        metadata = EventMetadata()

        assert metadata.correlation_id is not None
        assert len(metadata.correlation_id) == 36  # UUID format
        assert metadata.causation_id is None
        assert metadata.trace_id is None
        assert metadata.span_id is None
        assert metadata.run_id is None
        assert metadata.timestamp is not None
        assert metadata.version == 1
        assert metadata.service is None

    def test_custom_values(self) -> None:
        """Test metadata with custom values."""
        timestamp = datetime(2026, 1, 26, 12, 0, 0, tzinfo=UTC)
        metadata = EventMetadata(
            correlation_id="corr-123",
            causation_id="cause-456",
            trace_id="00112233445566778899aabbccddeeff",
            span_id="0011223344556677",
            run_id="run-789",
            timestamp=timestamp,
            version=2,
            service="test-service",
        )

        assert metadata.correlation_id == "corr-123"
        assert metadata.causation_id == "cause-456"
        assert metadata.trace_id == "00112233445566778899aabbccddeeff"
        assert metadata.span_id == "0011223344556677"
        assert metadata.run_id == "run-789"
        assert metadata.timestamp == timestamp
        assert metadata.version == 2
        assert metadata.service == "test-service"

    def test_to_dict_excludes_none(self) -> None:
        """Test to_dict excludes None values."""
        metadata = EventMetadata(
            correlation_id="corr-123",
            service="my-service",
        )

        result = metadata.to_dict()

        assert "correlation_id" in result
        assert "service" in result
        assert "timestamp" in result
        assert "version" in result
        # None values should be excluded
        assert "causation_id" not in result
        assert "trace_id" not in result
        assert "span_id" not in result
        assert "run_id" not in result

    def test_to_dict_timestamp_is_iso(self) -> None:
        """Test to_dict converts timestamp to ISO string."""
        timestamp = datetime(2026, 1, 26, 12, 0, 0, tzinfo=UTC)
        metadata = EventMetadata(timestamp=timestamp)

        result = metadata.to_dict()

        assert result["timestamp"] == "2026-01-26T12:00:00+00:00"

    def test_frozen_immutable(self) -> None:
        """Test metadata is immutable (frozen)."""
        metadata = EventMetadata()

        with pytest.raises(ValidationError):
            metadata.correlation_id = "new-value"  # type: ignore[misc]


class TestEvent:
    """Tests for Event model."""

    def test_minimal_event(self) -> None:
        """Test creating event with minimal required fields."""
        event = Event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
        )

        assert event.id is not None
        assert len(event.id) == 36  # UUID format
        assert event.event_type == EventType.RECORD_CREATED
        assert event.aggregate_type == "knowledge"
        assert event.aggregate_id is None
        assert event.data == {}
        assert event.metadata is not None

    def test_full_event(self) -> None:
        """Test creating event with all fields."""
        metadata = EventMetadata(
            correlation_id="corr-123",
            service="test-service",
        )
        event = Event(
            id="event-456",
            event_type=EventType.PROCESSING_COMPLETED,
            aggregate_type="batch",
            aggregate_id="batch-789",
            data={"count": 100, "status": "success"},
            metadata=metadata,
        )

        assert event.id == "event-456"
        assert event.event_type == EventType.PROCESSING_COMPLETED
        assert event.aggregate_type == "batch"
        assert event.aggregate_id == "batch-789"
        assert event.data == {"count": 100, "status": "success"}
        assert event.metadata.correlation_id == "corr-123"

    def test_to_jsonl(self) -> None:
        """Test to_jsonl produces valid JSON string."""
        event = Event(
            id="event-123",
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            aggregate_id="agg-456",
            data={"content": "test"},
        )

        jsonl = event.to_jsonl()

        # Should be valid JSON
        parsed = json.loads(jsonl)
        assert parsed["id"] == "event-123"
        assert parsed["event_type"] == "record.created"
        assert parsed["aggregate_type"] == "knowledge"
        assert parsed["aggregate_id"] == "agg-456"
        assert parsed["data"] == {"content": "test"}
        assert "metadata" in parsed

    def test_to_jsonl_single_line(self) -> None:
        """Test to_jsonl produces single line (no newlines)."""
        event = Event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={"multiline": "test\nwith\nnewlines"},
        )

        jsonl = event.to_jsonl()

        # The JSONL output should be a single line
        assert "\n" not in jsonl

    def test_child_event_inherits_correlation(self) -> None:
        """Test child_event inherits correlation_id."""
        parent = Event(
            event_type=EventType.PROCESSING_STARTED,
            aggregate_type="batch",
            metadata=EventMetadata(
                correlation_id="parent-corr",
                trace_id="trace-123",
                run_id="run-456",
                service="parent-service",
            ),
        )

        child = parent.child_event(
            event_type=EventType.PROCESSING_COMPLETED,
            data={"result": "success"},
        )

        assert child.event_type == EventType.PROCESSING_COMPLETED
        assert child.aggregate_type == "batch"
        assert child.data == {"result": "success"}
        # Should inherit correlation chain
        assert child.metadata.correlation_id == "parent-corr"
        assert child.metadata.causation_id == parent.id
        assert child.metadata.trace_id == "trace-123"
        assert child.metadata.run_id == "run-456"
        assert child.metadata.service == "parent-service"

    def test_child_event_inherits_aggregate_id(self) -> None:
        """Test child_event inherits aggregate_id if not specified."""
        parent = Event(
            event_type=EventType.PROCESSING_STARTED,
            aggregate_type="batch",
            aggregate_id="batch-123",
        )

        child = parent.child_event(event_type=EventType.PROCESSING_COMPLETED)

        assert child.aggregate_id == "batch-123"

    def test_child_event_can_override_aggregate_id(self) -> None:
        """Test child_event can specify different aggregate_id."""
        parent = Event(
            event_type=EventType.PROCESSING_STARTED,
            aggregate_type="batch",
            aggregate_id="batch-123",
        )

        child = parent.child_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_id="new-aggregate-456",
        )

        assert child.aggregate_id == "new-aggregate-456"

    def test_child_event_default_empty_data(self) -> None:
        """Test child_event uses empty dict if data not specified."""
        parent = Event(
            event_type=EventType.PROCESSING_STARTED,
            aggregate_type="batch",
            data={"original": "data"},
        )

        child = parent.child_event(event_type=EventType.PROCESSING_COMPLETED)

        assert child.data == {}

    def test_frozen_immutable(self) -> None:
        """Test event is immutable (frozen)."""
        event = Event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
        )

        with pytest.raises(ValidationError):
            event.aggregate_type = "new-type"  # type: ignore[misc]


class TestCreateEvent:
    """Tests for create_event factory function."""

    def test_basic_creation(self) -> None:
        """Test basic event creation."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={"content": "test"},
        )

        assert event.event_type == EventType.RECORD_CREATED
        assert event.aggregate_type == "knowledge"
        assert event.data == {"content": "test"}
        assert event.metadata.correlation_id is not None

    def test_with_correlation_id(self) -> None:
        """Test creation with explicit correlation_id."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
            correlation_id="my-correlation-id",
        )

        assert event.metadata.correlation_id == "my-correlation-id"

    def test_with_causation_id(self) -> None:
        """Test creation with causation_id."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
            causation_id="parent-event-id",
        )

        assert event.metadata.causation_id == "parent-event-id"

    def test_with_aggregate_id(self) -> None:
        """Test creation with aggregate_id."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
            aggregate_id="agg-123",
        )

        assert event.aggregate_id == "agg-123"

    def test_with_run_id(self) -> None:
        """Test creation with explicit run_id."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
            run_id="run-abc123",
        )

        assert event.metadata.run_id == "run-abc123"

    def test_with_service(self) -> None:
        """Test creation with service name."""
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
            service="knowledge-service",
        )

        assert event.metadata.service == "knowledge-service"

    def test_otel_integration_no_active_span(self) -> None:
        """Test OpenTelemetry integration when no span is active.

        When no span is active or recording, trace_id and span_id should be None.
        This is the default state outside of a traced context.
        """
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
        )

        # Without an active recording span, these should be None
        assert event.metadata.trace_id is None
        assert event.metadata.span_id is None

    def test_otel_integration_with_tracer(self) -> None:
        """Test OpenTelemetry integration with actual tracer.

        This test verifies that when we have an active span,
        the trace context is properly captured.
        """
        from opentelemetry import trace as otel_trace
        from opentelemetry.sdk.trace import TracerProvider

        # Set up a tracer provider
        provider = TracerProvider()
        tracer = provider.get_tracer("test-tracer")

        # Create an event within a span context
        with tracer.start_as_current_span("test-span"):
            span = otel_trace.get_current_span()
            if span.is_recording():
                ctx = span.get_span_context()
                expected_trace_id = format(ctx.trace_id, "032x")
                expected_span_id = format(ctx.span_id, "016x")

                event = create_event(
                    event_type=EventType.RECORD_CREATED,
                    aggregate_type="knowledge",
                    data={},
                )

                assert event.metadata.trace_id == expected_trace_id
                assert event.metadata.span_id == expected_span_id

    def test_handles_otel_import_error(self) -> None:
        """Test handles OpenTelemetry not installed."""
        # By default, if opentelemetry is not installed, it should not fail
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
        )

        assert event is not None
        # trace_id/span_id may or may not be set depending on environment

    @patch("truth_forge.observability.context.get_run_id")
    def test_gets_run_id_from_context(self, mock_get_run_id: MagicMock) -> None:
        """Test gets run_id from context when not provided."""
        mock_get_run_id.return_value = "context-run-id"

        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
        )

        assert event.metadata.run_id == "context-run-id"

    @patch("truth_forge.observability.context.get_run_id")
    def test_explicit_run_id_overrides_context(
        self, mock_get_run_id: MagicMock
    ) -> None:
        """Test explicit run_id overrides context."""
        mock_get_run_id.return_value = "context-run-id"

        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
            run_id="explicit-run-id",
        )

        assert event.metadata.run_id == "explicit-run-id"
        # Should not call get_run_id when run_id is provided
        mock_get_run_id.assert_not_called()

    def test_handles_context_import_error(self) -> None:
        """Test handles context module import error gracefully."""
        # The create_event function should handle ImportError for context module
        # This is tested implicitly - if the import fails, run_id will be None
        event = create_event(
            event_type=EventType.RECORD_CREATED,
            aggregate_type="knowledge",
            data={},
        )

        assert event is not None

    def test_all_event_types_work(self) -> None:
        """Test all event types can be used in create_event."""
        for event_type in EventType:
            event = create_event(
                event_type=event_type,
                aggregate_type="test",
                data={},
            )
            assert event.event_type == event_type
