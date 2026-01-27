"""Tests for logging service module.

Tests the logging capture and processing service.
"""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.logging.service import KnowledgeServiceHandler, LoggingService


class TestLoggingService:
    """Tests for LoggingService class."""

    def test_service_name(self) -> None:
        """Test service name is set."""
        assert LoggingService.service_name == "logging"

    @patch.object(LoggingService, "logger", new_callable=lambda: MagicMock())
    @patch("truth_forge.services.logging.service.get_service")
    def test_on_startup(self, mock_get_service: MagicMock, mock_logger: MagicMock) -> None:
        """Test on_startup initializes mediator."""
        mock_mediator = MagicMock()
        mock_get_service.return_value = mock_mediator

        service = LoggingService.__new__(LoggingService)
        service.on_startup()

        mock_get_service.assert_called_once_with("mediator")
        assert service.mediator is mock_mediator

    @patch.object(LoggingService, "logger", new_callable=lambda: MagicMock())
    def test_process_publishes_to_mediator(self, mock_logger: MagicMock) -> None:
        """Test process publishes record to mediator."""
        service = LoggingService.__new__(LoggingService)
        mock_mediator = MagicMock()
        service.mediator = mock_mediator

        record = {"message": "Test log", "level": "INFO"}
        result = service.process(record)

        assert result == record
        mock_mediator.publish.assert_called_once_with("knowledge.process", record)

    def test_create_schema(self) -> None:
        """Test create_schema returns valid SQL."""
        service = LoggingService.__new__(LoggingService)
        schema = service.create_schema()

        assert "CREATE TABLE IF NOT EXISTS" in schema
        assert "logging_records" in schema
        assert "id VARCHAR PRIMARY KEY" in schema
        assert "data JSON NOT NULL" in schema


class TestKnowledgeServiceHandler:
    """Tests for KnowledgeServiceHandler class."""

    @patch("truth_forge.services.logging.service.get_service")
    def test_init(self, mock_get_service: MagicMock) -> None:
        """Test handler initialization."""
        mock_logging_service = MagicMock()
        mock_get_service.return_value = mock_logging_service

        handler = KnowledgeServiceHandler()

        mock_get_service.assert_called_once_with("logging")
        assert handler.logging_service is mock_logging_service

    @patch("truth_forge.services.logging.service.get_service")
    def test_init_with_level(self, mock_get_service: MagicMock) -> None:
        """Test handler initialization with custom level."""
        mock_logging_service = MagicMock()
        mock_get_service.return_value = mock_logging_service

        handler = KnowledgeServiceHandler(level=logging.WARNING)

        assert handler.level == logging.WARNING

    @patch("truth_forge.services.logging.service.get_service")
    def test_emit_sends_to_logging_service(self, mock_get_service: MagicMock) -> None:
        """Test emit sends formatted log to logging service."""
        mock_logging_service = MagicMock()
        mock_get_service.return_value = mock_logging_service

        handler = KnowledgeServiceHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))

        # Create a log record
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        mock_logging_service.inhale.assert_called_once()
        call_args = mock_logging_service.inhale.call_args[0][0]
        assert call_args["content"] == "Test message"
        assert call_args["source"] == "test.logger"
        assert call_args["level"] == "INFO"
        assert "timestamp" in call_args

    @patch("truth_forge.services.logging.service.get_service")
    def test_emit_captures_error_level(self, mock_get_service: MagicMock) -> None:
        """Test emit captures error level correctly."""
        mock_logging_service = MagicMock()
        mock_get_service.return_value = mock_logging_service

        handler = KnowledgeServiceHandler()

        record = logging.LogRecord(
            name="error.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        call_args = mock_logging_service.inhale.call_args[0][0]
        assert call_args["level"] == "ERROR"

    @patch("truth_forge.services.logging.service.get_service")
    def test_emit_captures_warning_level(self, mock_get_service: MagicMock) -> None:
        """Test emit captures warning level correctly."""
        mock_logging_service = MagicMock()
        mock_get_service.return_value = mock_logging_service

        handler = KnowledgeServiceHandler()

        record = logging.LogRecord(
            name="warn.logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None,
        )

        handler.emit(record)

        call_args = mock_logging_service.inhale.call_args[0][0]
        assert call_args["level"] == "WARNING"

