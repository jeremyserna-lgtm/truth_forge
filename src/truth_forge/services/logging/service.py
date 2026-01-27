"""Logging Service.

Captures log records and sends them to the KnowledgeService for processing.
"""

from __future__ import annotations

import logging
from typing import Any, cast

from truth_forge.services.base import BaseService, MediatorProtocol
from truth_forge.services.factory import get_service, register_service


@register_service()
class LoggingService(BaseService):
    """A service for capturing and processing log records."""

    service_name = "logging"
    mediator: MediatorProtocol  # Type annotation for the mediator

    def on_startup(self) -> None:
        """Initialize the service."""
        self.mediator = cast("MediatorProtocol", get_service("mediator"))

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a log record by sending it to the KnowledgeService."""
        self.mediator.publish("knowledge.process", record)
        return record

    def create_schema(self) -> str:
        """Create the schema for the logging service."""
        return """
            CREATE TABLE IF NOT EXISTS logging_records (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """


class KnowledgeServiceHandler(logging.Handler):
    """A logging handler that sends records to the KnowledgeService."""

    def __init__(self, level: int = logging.NOTSET) -> None:
        super().__init__(level)
        self.logging_service = get_service("logging")

    def emit(self, record: logging.LogRecord) -> None:
        """Send a log record to the KnowledgeService."""
        log_entry = {
            "content": self.format(record),
            "source": record.name,
            "level": record.levelname,
            "timestamp": record.created,
        }
        self.logging_service.inhale(log_entry)
