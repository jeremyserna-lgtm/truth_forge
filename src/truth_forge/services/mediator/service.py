"""Service Mediator.

A central, resilient event router for inter-service communication.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from truth_forge.services.base import BaseService
from truth_forge.services.factory import get_service, register_service


@register_service()
class ServiceMediator(BaseService):
    """A service for mediating communication between other services."""

    service_name = "mediator"

    def on_startup(self) -> None:
        """Initialize the service and its routing table."""
        # Routes can return Event from inhale() or None from other handlers
        self.routes: dict[str, Callable[[dict[str, Any]], Any]] = {
            "knowledge.process": lambda data: get_service("knowledge").inhale(data),
            "governance.record": lambda data: get_service("governance").inhale(data),
        }

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a record by publishing it as an event."""
        topic = record.get("topic")
        data = record.get("data")
        if not topic or not data:
            raise ValueError("Mediator process record must have 'topic' and 'data'.")
        self.publish(topic, data)
        return record

    def publish(self, topic: str, data: dict[str, Any]) -> None:
        """Publish an event to a topic, routing it to the appropriate service."""
        if topic in self.routes:
            try:
                self.routes[topic](data)
                self.logger.info("event_published", topic=topic)
            except Exception as e:
                self.logger.error("event_publish_failed", topic=topic, error=str(e))
                self._write_error_signal({"topic": topic, "data": data}, e)
        else:
            self.logger.warning("no_route_for_topic", topic=topic)

    def create_schema(self) -> str:
        """Create the schema for the mediator service."""
        return """
            CREATE TABLE IF NOT EXISTS mediator_records (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
