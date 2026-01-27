"""Tests for mediator service module.

Tests the service mediator for inter-service communication.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.mediator.service import ServiceMediator


class TestServiceMediator:
    """Tests for ServiceMediator class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert ServiceMediator.service_name == "mediator"

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.mediator.service.get_service")
    def test_on_startup_creates_routes(
        self, mock_get_service: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Test on_startup creates routing table."""
        service = ServiceMediator.__new__(ServiceMediator)
        service.on_startup()

        assert "knowledge.process" in service.routes
        assert "governance.record" in service.routes

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    def test_process_missing_topic(self, mock_logger: MagicMock) -> None:
        """Test process raises for missing topic."""
        service = ServiceMediator.__new__(ServiceMediator)
        service.routes = {}

        record = {"data": {"key": "value"}}

        with pytest.raises(ValueError) as exc_info:
            service.process(record)

        assert "topic" in str(exc_info.value)

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    def test_process_missing_data(self, mock_logger: MagicMock) -> None:
        """Test process raises for missing data."""
        service = ServiceMediator.__new__(ServiceMediator)
        service.routes = {}

        record = {"topic": "test.topic"}

        with pytest.raises(ValueError) as exc_info:
            service.process(record)

        assert "data" in str(exc_info.value)

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    def test_process_valid_record(self, mock_logger: MagicMock) -> None:
        """Test process with valid record."""
        service = ServiceMediator.__new__(ServiceMediator)
        service._write_error_signal = MagicMock()

        mock_handler = MagicMock()
        service.routes = {"test.topic": mock_handler}

        record = {"topic": "test.topic", "data": {"key": "value"}}
        result = service.process(record)

        assert result == record
        mock_handler.assert_called_once_with({"key": "value"})

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    def test_publish_routes_to_handler(self, mock_logger: MagicMock) -> None:
        """Test publish routes data to correct handler."""
        service = ServiceMediator.__new__(ServiceMediator)
        service._write_error_signal = MagicMock()

        mock_handler = MagicMock()
        service.routes = {"my.topic": mock_handler}

        service.publish("my.topic", {"message": "test"})

        mock_handler.assert_called_once_with({"message": "test"})
        mock_logger.info.assert_called()

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    def test_publish_no_route(self, mock_logger: MagicMock) -> None:
        """Test publish logs warning when no route found."""
        service = ServiceMediator.__new__(ServiceMediator)
        service._write_error_signal = MagicMock()
        service.routes = {}

        service.publish("unknown.topic", {"data": "test"})

        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert call_args[0][0] == "no_route_for_topic"

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    def test_publish_handler_error(self, mock_logger: MagicMock) -> None:
        """Test publish handles handler errors."""
        service = ServiceMediator.__new__(ServiceMediator)
        service._write_error_signal = MagicMock()

        mock_handler = MagicMock()
        mock_handler.side_effect = RuntimeError("Handler failed")
        service.routes = {"error.topic": mock_handler}

        service.publish("error.topic", {"data": "test"})

        mock_logger.error.assert_called()
        service._write_error_signal.assert_called_once()

    def test_create_schema(self) -> None:
        """Test create_schema returns valid SQL."""
        service = ServiceMediator.__new__(ServiceMediator)
        schema = service.create_schema()

        assert "CREATE TABLE IF NOT EXISTS" in schema
        assert "mediator_records" in schema
        assert "id VARCHAR PRIMARY KEY" in schema
        assert "data JSON NOT NULL" in schema

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.mediator.service.get_service")
    def test_routes_call_knowledge_service(
        self, mock_get_service: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Test knowledge.process route calls knowledge service."""
        mock_knowledge = MagicMock()
        mock_get_service.return_value = mock_knowledge

        service = ServiceMediator.__new__(ServiceMediator)
        service.on_startup()

        # Call the route handler
        service.routes["knowledge.process"]({"content": "test"})

        mock_get_service.assert_called_with("knowledge")
        mock_knowledge.inhale.assert_called_once_with({"content": "test"})

    @patch.object(ServiceMediator, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.mediator.service.get_service")
    def test_routes_call_governance_service(
        self, mock_get_service: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Test governance.record route calls governance service."""
        mock_governance = MagicMock()
        mock_get_service.return_value = mock_governance

        service = ServiceMediator.__new__(ServiceMediator)
        service.on_startup()

        # Call the route handler
        service.routes["governance.record"]({"event": "test"})

        mock_get_service.assert_called_with("governance")
        mock_governance.inhale.assert_called_once_with({"event": "test"})

