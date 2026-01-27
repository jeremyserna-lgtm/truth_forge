"""Tests for observability setup module.

Tests OpenTelemetry setup and instrumentation.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import truth_forge.observability.setup as obs_setup
from truth_forge.observability.setup import (
    get_logger,
    get_meter,
    get_tracer,
    setup_observability,
    shutdown_observability,
)


class TestSetupObservability:
    """Tests for setup_observability function."""

    def setup_method(self) -> None:
        """Reset module state before each test."""
        obs_setup._initialized = False
        obs_setup._service_name = "truth-forge"

    def teardown_method(self) -> None:
        """Clean up after each test."""
        obs_setup._initialized = False

    @patch("truth_forge.observability.setup._setup_tracing")
    @patch("truth_forge.observability.setup._setup_metrics")
    @patch("truth_forge.observability.setup._setup_logging")
    def test_setup_initializes_all_components(
        self,
        mock_logging: MagicMock,
        mock_metrics: MagicMock,
        mock_tracing: MagicMock,
    ) -> None:
        """Test setup_observability initializes all components."""
        setup_observability(service_name="test-service")

        mock_tracing.assert_called_once()
        mock_metrics.assert_called_once()
        mock_logging.assert_called_once()
        assert obs_setup._initialized is True
        assert obs_setup._service_name == "test-service"

    @patch("truth_forge.observability.setup._setup_tracing")
    @patch("truth_forge.observability.setup._setup_metrics")
    @patch("truth_forge.observability.setup._setup_logging")
    def test_setup_only_runs_once(
        self,
        mock_logging: MagicMock,
        mock_metrics: MagicMock,
        mock_tracing: MagicMock,
    ) -> None:
        """Test setup_observability is idempotent."""
        setup_observability(service_name="test-service")
        setup_observability(service_name="another-service")

        # Should only be called once
        assert mock_tracing.call_count == 1
        assert obs_setup._service_name == "test-service"

    @patch("truth_forge.observability.setup._setup_tracing")
    @patch("truth_forge.observability.setup._setup_metrics")
    @patch("truth_forge.observability.setup._setup_logging")
    @patch.dict("os.environ", {"ENVIRONMENT": "production"})
    def test_setup_reads_environment_from_env_var(
        self,
        mock_logging: MagicMock,
        mock_metrics: MagicMock,
        mock_tracing: MagicMock,
    ) -> None:
        """Test setup uses ENVIRONMENT env var if not provided."""
        setup_observability()

        # Resource should be created with production environment
        mock_tracing.assert_called_once()

    @patch("truth_forge.observability.setup._setup_tracing")
    @patch("truth_forge.observability.setup._setup_metrics")
    @patch("truth_forge.observability.setup._setup_logging")
    def test_setup_with_custom_log_level(
        self,
        mock_logging: MagicMock,
        mock_metrics: MagicMock,
        mock_tracing: MagicMock,
    ) -> None:
        """Test setup with custom log level."""
        setup_observability(log_level="DEBUG")

        mock_logging.assert_called_once_with("DEBUG")


class TestSetupTracing:
    """Tests for _setup_tracing function."""

    def setup_method(self) -> None:
        """Reset module state before each test."""
        obs_setup._initialized = False

    def teardown_method(self) -> None:
        """Clean up after each test."""
        obs_setup._initialized = False

    @patch("truth_forge.observability.setup.trace.set_tracer_provider")
    @patch("truth_forge.observability.setup.TracerProvider")
    @patch("truth_forge.observability.setup.BatchSpanProcessor")
    @patch("truth_forge.observability.setup.ConsoleSpanExporter")
    def test_setup_tracing_with_console_export(
        self,
        mock_console_exporter: MagicMock,
        mock_processor: MagicMock,
        mock_provider_class: MagicMock,
        mock_set_provider: MagicMock,
    ) -> None:
        """Test tracing setup with console export enabled."""
        from opentelemetry.sdk.resources import Resource

        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider

        resource = Resource.create({"service.name": "test"})
        obs_setup._setup_tracing(resource, otlp_endpoint=None, console_export=True)

        mock_provider.add_span_processor.assert_called_once()
        mock_set_provider.assert_called_once_with(mock_provider)

    @patch("truth_forge.observability.setup.trace.set_tracer_provider")
    @patch("truth_forge.observability.setup.TracerProvider")
    def test_setup_tracing_without_console_export(
        self,
        mock_provider_class: MagicMock,
        mock_set_provider: MagicMock,
    ) -> None:
        """Test tracing setup without console export."""
        from opentelemetry.sdk.resources import Resource

        mock_provider = MagicMock()
        mock_provider_class.return_value = mock_provider

        resource = Resource.create({"service.name": "test"})
        obs_setup._setup_tracing(resource, otlp_endpoint=None, console_export=False)

        # No processor should be added when console_export is False
        mock_provider.add_span_processor.assert_not_called()


class TestSetupMetrics:
    """Tests for _setup_metrics function."""

    def setup_method(self) -> None:
        """Reset module state before each test."""
        obs_setup._initialized = False

    def teardown_method(self) -> None:
        """Clean up after each test."""
        obs_setup._initialized = False

    @patch("truth_forge.observability.setup.metrics.set_meter_provider")
    @patch("truth_forge.observability.setup.MeterProvider")
    def test_setup_metrics_without_otlp(
        self,
        mock_provider_class: MagicMock,
        mock_set_provider: MagicMock,
    ) -> None:
        """Test metrics setup without OTLP endpoint."""
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create({"service.name": "test"})
        obs_setup._setup_metrics(resource, otlp_endpoint=None)

        mock_provider_class.assert_called_once()
        mock_set_provider.assert_called_once()


class TestSetupLogging:
    """Tests for _setup_logging function."""

    @patch("truth_forge.observability.setup.structlog.configure")
    def test_setup_logging_configures_structlog(
        self,
        mock_configure: MagicMock,
    ) -> None:
        """Test logging setup configures structlog."""
        obs_setup._setup_logging("INFO")

        mock_configure.assert_called_once()


class TestShutdownObservability:
    """Tests for shutdown_observability function."""

    def setup_method(self) -> None:
        """Reset module state before each test."""
        obs_setup._initialized = False

    def teardown_method(self) -> None:
        """Clean up after each test."""
        obs_setup._initialized = False

    def test_shutdown_when_not_initialized(self) -> None:
        """Test shutdown does nothing when not initialized."""
        obs_setup._initialized = False
        shutdown_observability()
        # Should not raise

    @patch("truth_forge.observability.setup.trace.get_tracer_provider")
    @patch("truth_forge.observability.setup.metrics.get_meter_provider")
    def test_shutdown_calls_provider_shutdown(
        self,
        mock_meter_provider: MagicMock,
        mock_tracer_provider: MagicMock,
    ) -> None:
        """Test shutdown calls shutdown on providers."""
        obs_setup._initialized = True

        mock_tracer = MagicMock()
        mock_meter = MagicMock()
        mock_tracer_provider.return_value = mock_tracer
        mock_meter_provider.return_value = mock_meter

        shutdown_observability()

        mock_tracer.shutdown.assert_called_once()
        mock_meter.shutdown.assert_called_once()
        assert obs_setup._initialized is False


class TestGetTracer:
    """Tests for get_tracer function."""

    @patch("truth_forge.observability.setup.trace.get_tracer")
    def test_get_tracer_returns_tracer(self, mock_get_tracer: MagicMock) -> None:
        """Test get_tracer returns a tracer."""
        mock_tracer = MagicMock()
        mock_get_tracer.return_value = mock_tracer

        result = get_tracer("test_module")

        mock_get_tracer.assert_called_once_with("test_module")
        assert result is mock_tracer


class TestGetMeter:
    """Tests for get_meter function."""

    @patch("truth_forge.observability.setup.metrics.get_meter")
    def test_get_meter_returns_meter(self, mock_get_meter: MagicMock) -> None:
        """Test get_meter returns a meter."""
        mock_meter = MagicMock()
        mock_get_meter.return_value = mock_meter

        result = get_meter("test_module")

        mock_get_meter.assert_called_once_with("test_module")
        assert result is mock_meter


class TestGetLogger:
    """Tests for get_logger function."""

    @patch("truth_forge.observability.setup.structlog.get_logger")
    def test_get_logger_returns_logger(self, mock_get_logger: MagicMock) -> None:
        """Test get_logger returns a logger."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        result = get_logger("test_module")

        mock_get_logger.assert_called_once_with("test_module")
        assert result is mock_logger


class TestTraceContext:
    """Tests for _add_trace_context processor."""

    @patch("truth_forge.observability.setup.trace.get_current_span")
    def test_add_trace_context_when_recording(
        self,
        mock_get_span: MagicMock,
    ) -> None:
        """Test trace context is added when span is recording."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = True
        mock_ctx = MagicMock()
        mock_ctx.trace_id = 123456789
        mock_ctx.span_id = 987654321
        mock_span.get_span_context.return_value = mock_ctx
        mock_get_span.return_value = mock_span

        event_dict: dict[str, str] = {"event": "test"}
        result = obs_setup._add_trace_context(None, "info", event_dict)  # type: ignore[arg-type]

        assert "trace_id" in result
        assert "span_id" in result

    @patch("truth_forge.observability.setup.trace.get_current_span")
    def test_add_trace_context_when_not_recording(
        self,
        mock_get_span: MagicMock,
    ) -> None:
        """Test trace context is not added when span is not recording."""
        mock_span = MagicMock()
        mock_span.is_recording.return_value = False
        mock_get_span.return_value = mock_span

        event_dict: dict[str, str] = {"event": "test"}
        result = obs_setup._add_trace_context(None, "info", event_dict)  # type: ignore[arg-type]

        assert "trace_id" not in result
        assert "span_id" not in result


class TestServiceContext:
    """Tests for _add_service_context processor."""

    def setup_method(self) -> None:
        """Reset module state before each test."""
        obs_setup._service_name = "test-service"

    def test_add_service_context(self) -> None:
        """Test service context is added to log records."""
        event_dict: dict[str, str] = {"event": "test"}
        result = obs_setup._add_service_context(None, "info", event_dict)  # type: ignore[arg-type]

        assert result["service"] == "test-service"

