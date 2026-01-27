"""Tests for observability context module.

Tests correlation context management and ID propagation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import truth_forge.observability.context as ctx_module
from truth_forge.observability.context import (
    CorrelationContext,
    get_causation_id,
    get_correlation_id,
    get_run_id,
    get_trace_id,
    set_causation_id,
    set_correlation_id,
    set_run_id,
)


class TestCorrelationContext:
    """Tests for CorrelationContext dataclass."""

    def test_default_values(self) -> None:
        """Test default correlation context values."""
        ctx = CorrelationContext()

        assert ctx.correlation_id is not None
        assert len(ctx.correlation_id) == 36  # UUID format
        assert ctx.trace_id is None
        assert ctx.span_id is None
        assert ctx.run_id is None
        assert ctx.causation_id is None
        assert ctx.timestamp is not None

    def test_custom_values(self) -> None:
        """Test custom correlation context values."""
        ctx = CorrelationContext(
            correlation_id="test-corr-id",
            trace_id="test-trace-id",
            span_id="test-span-id",
            run_id="test-run-id",
            causation_id="test-cause-id",
        )

        assert ctx.correlation_id == "test-corr-id"
        assert ctx.trace_id == "test-trace-id"
        assert ctx.span_id == "test-span-id"
        assert ctx.run_id == "test-run-id"
        assert ctx.causation_id == "test-cause-id"

    @patch("truth_forge.observability.context.trace.get_current_span")
    def test_current_without_span(self, mock_get_span: MagicMock) -> None:
        """Test current() when no span is recording."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        mock_get_span.return_value = mock_span

        # Clear context vars
        ctx_module._correlation_id.set(None)
        ctx_module._run_id.set(None)
        ctx_module._causation_id.set(None)

        ctx = CorrelationContext.current()

        assert ctx.correlation_id is not None
        assert ctx.trace_id is None
        assert ctx.span_id is None

    @patch("truth_forge.observability.context.trace.get_current_span")
    def test_current_with_span(self, mock_get_span: MagicMock) -> None:
        """Test current() when span is recording."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_ctx = MagicMock()
        mock_ctx.trace_id = 12345678901234567890
        mock_ctx.span_id = 9876543210
        mock_span.get_span_context.return_value = mock_ctx
        mock_get_span.return_value = mock_span

        ctx = CorrelationContext.current()

        assert ctx.trace_id is not None
        assert ctx.span_id is not None

    @patch("truth_forge.observability.context.trace.get_current_span")
    def test_current_uses_context_vars(self, mock_get_span: MagicMock) -> None:
        """Test current() reads from context vars."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        mock_get_span.return_value = mock_span

        # Set context vars
        ctx_module._correlation_id.set("my-corr-id")
        ctx_module._run_id.set("my-run-id")
        ctx_module._causation_id.set("my-cause-id")

        try:
            ctx = CorrelationContext.current()

            assert ctx.correlation_id == "my-corr-id"
            assert ctx.run_id == "my-run-id"
            assert ctx.causation_id == "my-cause-id"
        finally:
            # Clean up
            ctx_module._correlation_id.set(None)
            ctx_module._run_id.set(None)
            ctx_module._causation_id.set(None)

    def test_to_dict_minimal(self) -> None:
        """Test to_dict with minimal fields."""
        ctx = CorrelationContext(
            correlation_id="test-id",
            timestamp="2026-01-26T00:00:00Z",
        )

        result = ctx.to_dict()

        assert result["correlation_id"] == "test-id"
        assert result["timestamp"] == "2026-01-26T00:00:00Z"
        assert "trace_id" not in result
        assert "span_id" not in result
        assert "run_id" not in result
        assert "causation_id" not in result

    def test_to_dict_full(self) -> None:
        """Test to_dict with all fields."""
        ctx = CorrelationContext(
            correlation_id="test-id",
            trace_id="trace-123",
            span_id="span-456",
            run_id="run-789",
            causation_id="cause-abc",
            timestamp="2026-01-26T00:00:00Z",
        )

        result = ctx.to_dict()

        assert result["correlation_id"] == "test-id"
        assert result["trace_id"] == "trace-123"
        assert result["span_id"] == "span-456"
        assert result["run_id"] == "run-789"
        assert result["causation_id"] == "cause-abc"

    def test_child_default(self) -> None:
        """Test child() with default causation."""
        parent = CorrelationContext(
            correlation_id="parent-id",
            trace_id="trace-123",
            span_id="span-456",
            run_id="run-789",
        )

        child = parent.child()

        assert child.correlation_id == "parent-id"  # Inherited
        assert child.trace_id == "trace-123"
        assert child.span_id == "span-456"
        assert child.run_id == "run-789"
        assert child.causation_id == "parent-id"  # Default to parent correlation

    def test_child_custom_causation(self) -> None:
        """Test child() with custom causation."""
        parent = CorrelationContext(correlation_id="parent-id")

        child = parent.child(causation_id="custom-cause")

        assert child.causation_id == "custom-cause"


class TestGetCorrelationId:
    """Tests for get_correlation_id function."""

    def setup_method(self) -> None:
        """Reset context vars before each test."""
        ctx_module._correlation_id.set(None)

    def teardown_method(self) -> None:
        """Clean up context vars after each test."""
        ctx_module._correlation_id.set(None)

    def test_get_when_not_set(self) -> None:
        """Test get_correlation_id returns None when not set."""
        result = get_correlation_id()
        assert result is None

    def test_get_when_set(self) -> None:
        """Test get_correlation_id returns set value."""
        ctx_module._correlation_id.set("test-id")
        result = get_correlation_id()
        assert result == "test-id"


class TestSetCorrelationId:
    """Tests for set_correlation_id function."""

    def teardown_method(self) -> None:
        """Clean up context vars after each test."""
        ctx_module._correlation_id.set(None)

    def test_set_correlation_id(self) -> None:
        """Test set_correlation_id sets the value."""
        set_correlation_id("new-id")
        assert ctx_module._correlation_id.get() == "new-id"


class TestGetRunId:
    """Tests for get_run_id function."""

    def setup_method(self) -> None:
        """Reset context vars before each test."""
        ctx_module._run_id.set(None)

    def teardown_method(self) -> None:
        """Clean up context vars after each test."""
        ctx_module._run_id.set(None)

    def test_get_when_not_set(self) -> None:
        """Test get_run_id returns None when not set."""
        result = get_run_id()
        assert result is None

    def test_get_when_set(self) -> None:
        """Test get_run_id returns set value."""
        ctx_module._run_id.set("run-123")
        result = get_run_id()
        assert result == "run-123"


class TestSetRunId:
    """Tests for set_run_id function."""

    def teardown_method(self) -> None:
        """Clean up context vars after each test."""
        ctx_module._run_id.set(None)

    def test_set_run_id_explicit(self) -> None:
        """Test set_run_id with explicit ID."""
        result = set_run_id("my-run-id")

        assert result == "my-run-id"
        assert ctx_module._run_id.get() == "my-run-id"

    def test_set_run_id_generated(self) -> None:
        """Test set_run_id generates ID when None."""
        result = set_run_id(None)

        assert result.startswith("run_")
        assert len(result) == 12  # run_ + 8 char hash
        assert ctx_module._run_id.get() == result


class TestGetTraceId:
    """Tests for get_trace_id function."""

    @patch("truth_forge.observability.context.trace.get_current_span")
    def test_get_trace_id_with_span(self, mock_get_span: MagicMock) -> None:
        """Test get_trace_id when span is recording."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_ctx = MagicMock()
        mock_ctx.trace_id = 12345678901234567890
        mock_span.get_span_context.return_value = mock_ctx
        mock_get_span.return_value = mock_span

        result = get_trace_id()

        assert result is not None
        assert len(result) == 32  # 32 hex chars

    @patch("truth_forge.observability.context.trace.get_current_span")
    def test_get_trace_id_without_span(self, mock_get_span: MagicMock) -> None:
        """Test get_trace_id when no span is recording."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        mock_get_span.return_value = mock_span

        result = get_trace_id()

        assert result is None


class TestGetCausationId:
    """Tests for get_causation_id function."""

    def setup_method(self) -> None:
        """Reset context vars before each test."""
        ctx_module._causation_id.set(None)

    def teardown_method(self) -> None:
        """Clean up context vars after each test."""
        ctx_module._causation_id.set(None)

    def test_get_when_not_set(self) -> None:
        """Test get_causation_id returns None when not set."""
        result = get_causation_id()
        assert result is None

    def test_get_when_set(self) -> None:
        """Test get_causation_id returns set value."""
        ctx_module._causation_id.set("cause-123")
        result = get_causation_id()
        assert result == "cause-123"


class TestSetCausationId:
    """Tests for set_causation_id function."""

    def teardown_method(self) -> None:
        """Clean up context vars after each test."""
        ctx_module._causation_id.set(None)

    def test_set_causation_id(self) -> None:
        """Test set_causation_id sets the value."""
        set_causation_id("new-cause")
        assert ctx_module._causation_id.get() == "new-cause"

