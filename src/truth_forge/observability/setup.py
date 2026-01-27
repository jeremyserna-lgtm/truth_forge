"""OpenTelemetry setup and instrumentation.

Provides unified observability with:
- Distributed tracing (traces)
- Metrics collection
- Structured logging with trace correlation

Industry standard per RESEARCH_FINDINGS.md:
- OpenTelemetry for traces/metrics
- structlog for JSON logging
- Automatic trace-log correlation
"""

from __future__ import annotations

import logging
import os
import sys
from typing import TYPE_CHECKING

import structlog
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


if TYPE_CHECKING:
    from opentelemetry.metrics import Meter
    from opentelemetry.trace import Tracer


# Module-level state
_initialized = False
_service_name = "truth-forge"


def setup_observability(
    service_name: str = "truth-forge",
    environment: str | None = None,
    otlp_endpoint: str | None = None,
    log_level: str = "INFO",
    console_export: bool = True,
) -> None:
    """Initialize OpenTelemetry observability stack.

    Args:
        service_name: Name of this service for telemetry attribution.
        environment: Deployment environment (dev, staging, prod).
        otlp_endpoint: OTLP collector endpoint (if None, uses console export).
        log_level: Minimum log level to emit.
        console_export: Whether to export spans to console (useful for dev).

    Example:
        >>> setup_observability(
        ...     service_name="knowledge-service",
        ...     environment="production",
        ...     otlp_endpoint="http://collector:4317",
        ... )
    """
    global _initialized, _service_name

    if _initialized:
        return

    _service_name = service_name
    resolved_environment: str = environment or os.getenv("ENVIRONMENT") or "development"

    # Create resource with service metadata
    resource = Resource.create(
        {
            "service.name": service_name,
            "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
            "deployment.environment": resolved_environment,
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.language": "python",
        }
    )

    # Setup tracing
    _setup_tracing(resource, otlp_endpoint, console_export)

    # Setup metrics
    _setup_metrics(resource, otlp_endpoint)

    # Setup structured logging with trace correlation
    _setup_logging(log_level)

    _initialized = True


def _setup_tracing(
    resource: Resource,
    otlp_endpoint: str | None,
    console_export: bool,
) -> None:
    """Configure distributed tracing with OpenTelemetry."""
    tracer_provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint provided
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        except ImportError:
            pass  # OTLP exporter not installed

    # Add console exporter for development
    if console_export:
        tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(tracer_provider)


def _setup_metrics(resource: Resource, otlp_endpoint: str | None) -> None:
    """Configure metrics collection with OpenTelemetry."""
    meter_provider = MeterProvider(resource=resource)

    # Add OTLP exporter if endpoint provided
    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
                OTLPMetricExporter,
            )
            from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

            otlp_exporter = OTLPMetricExporter(endpoint=otlp_endpoint)
            reader = PeriodicExportingMetricReader(otlp_exporter)
            meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        except ImportError:
            pass  # OTLP exporter not installed

    metrics.set_meter_provider(meter_provider)


def _setup_logging(log_level: str) -> None:
    """Configure structured logging with structlog and trace correlation.

    Logs are emitted as JSON with automatic trace/span ID injection.
    """
    # Configure structlog for JSON output with trace correlation
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            _add_trace_context,
            _add_service_context,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, log_level.upper())),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def _add_trace_context(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Add OpenTelemetry trace context to log records.

    This enables trace-log correlation in observability platforms.
    """
    span = trace.get_current_span()
    if span.is_recording():
        ctx = span.get_span_context()
        event_dict["trace_id"] = format(ctx.trace_id, "032x")
        event_dict["span_id"] = format(ctx.span_id, "016x")
    return event_dict


def _add_service_context(
    logger: structlog.types.WrappedLogger,
    method_name: str,
    event_dict: structlog.types.EventDict,
) -> structlog.types.EventDict:
    """Add service context to log records."""
    event_dict["service"] = _service_name
    return event_dict


def shutdown_observability() -> None:
    """Gracefully shutdown observability providers.

    Call this before application exit to flush pending telemetry.
    """
    global _initialized

    if not _initialized:
        return

    # Shutdown tracer provider
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, "shutdown"):
        tracer_provider.shutdown()

    # Shutdown meter provider
    meter_provider = metrics.get_meter_provider()
    if hasattr(meter_provider, "shutdown"):
        meter_provider.shutdown()

    _initialized = False


def get_tracer(name: str) -> Tracer:
    """Get a tracer for creating spans.

    Args:
        name: Usually __name__ of the calling module.

    Returns:
        OpenTelemetry Tracer instance.

    Example:
        >>> tracer = get_tracer(__name__)
        >>> with tracer.start_as_current_span("process-record") as span:
        ...     span.set_attribute("record.id", record_id)
        ...     # ... process record ...
    """
    return trace.get_tracer(name)


def get_meter(name: str) -> Meter:
    """Get a meter for creating metrics.

    Args:
        name: Usually __name__ of the calling module.

    Returns:
        OpenTelemetry Meter instance.

    Example:
        >>> meter = get_meter(__name__)
        >>> counter = meter.create_counter("records.processed")
        >>> counter.add(1, {"service": "knowledge"})
    """
    return metrics.get_meter(name)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger with trace correlation.

    Args:
        name: Usually __name__ of the calling module.

    Returns:
        structlog BoundLogger with JSON output and trace IDs.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started", item_count=100)
        >>> logger.error("Processing failed", error=str(e), item_id=item_id)
    """
    logger: structlog.stdlib.BoundLogger = structlog.get_logger(name)
    return logger
