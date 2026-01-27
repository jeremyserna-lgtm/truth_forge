"""Observability module - OpenTelemetry integration.

Industry-standard observability with traces, metrics, and structured logs.
See RESEARCH_FINDINGS.md for implementation rationale.

Usage:
    from truth_forge.observability import setup_observability, get_tracer, get_logger

    # Initialize at application startup
    setup_observability(service_name="my-service")

    # Get tracer for distributed tracing
    tracer = get_tracer(__name__)

    # Get structured logger with trace correlation
    logger = get_logger(__name__)

    with tracer.start_as_current_span("my-operation") as span:
        logger.info("Processing started", extra={"item_count": 100})
        # ... do work ...
        span.set_attribute("items.processed", 100)
"""

from truth_forge.observability.context import (
    CorrelationContext,
    get_correlation_id,
    get_run_id,
    get_trace_id,
    set_correlation_id,
    set_run_id,
)
from truth_forge.observability.setup import (
    get_logger,
    get_meter,
    get_tracer,
    setup_observability,
    shutdown_observability,
)


__all__ = [
    # Setup
    "setup_observability",
    "shutdown_observability",
    # Instrumentation
    "get_tracer",
    "get_meter",
    "get_logger",
    # Context
    "CorrelationContext",
    "get_correlation_id",
    "get_run_id",
    "get_trace_id",
    "set_correlation_id",
    "set_run_id",
]
