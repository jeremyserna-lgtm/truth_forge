"""truth_forge - THE GENESIS.

The foundational organism from which all others inherit.

Architecture:
    HOLD₁ (Receiving) → AGENT (Processing) → HOLD₂ (Delivering)

Core Modules:
    - observability: OpenTelemetry tracing, metrics, structured logging
    - schema: Pydantic models for events, records, configuration
    - services: Domain services with HOLD pattern implementation

Usage:
    from truth_forge import __version__
    from truth_forge.observability import setup_observability, get_logger
    from truth_forge.schema import Event, EventType, create_event

Example:
    >>> from truth_forge.observability import setup_observability, get_logger
    >>> setup_observability(service_name="my-service")
    >>> logger = get_logger(__name__)
    >>> logger.info("Application started", version=__version__)
"""

__version__ = "1.0.0"
__author__ = "Jeremy Serna"
__email__ = "jeremy@truth-forge.ai"

# Type stub marker
__all__ = [
    "__author__",
    "__email__",
    "__version__",
]
