"""Tests for analytics service module.

Tests the AnalyticsService class.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.analytics import AnalyticsService


class TestAnalyticsService:
    """Tests for AnalyticsService class."""

    def test_service_name(self) -> None:
        """Test service name is set correctly."""
        assert AnalyticsService.service_name == "analytics"

    @patch.object(AnalyticsService, "logger", new_callable=lambda: MagicMock())
    def test_process_adds_metadata(self, mock_logger: MagicMock) -> None:
        """Test process adds _processed and _service fields."""
        service = AnalyticsService.__new__(AnalyticsService)

        record: dict[str, Any] = {"id": "123", "data": "test"}
        result = service.process(record)

        assert result["id"] == "123"
        assert result["data"] == "test"
        assert result["_processed"] is True
        assert result["_service"] == "analytics"

    @patch.object(AnalyticsService, "logger", new_callable=lambda: MagicMock())
    def test_process_preserves_original_fields(self, mock_logger: MagicMock) -> None:
        """Test process preserves all original record fields."""
        service = AnalyticsService.__new__(AnalyticsService)

        record: dict[str, Any] = {
            "id": "456",
            "type": "event",
            "value": 100,
            "nested": {"key": "value"},
        }
        result = service.process(record)

        assert result["id"] == "456"
        assert result["type"] == "event"
        assert result["value"] == 100
        assert result["nested"] == {"key": "value"}

    @patch.object(AnalyticsService, "logger", new_callable=lambda: MagicMock())
    def test_process_empty_record(self, mock_logger: MagicMock) -> None:
        """Test process handles empty record."""
        service = AnalyticsService.__new__(AnalyticsService)

        record: dict[str, Any] = {}
        result = service.process(record)

        assert result["_processed"] is True
        assert result["_service"] == "analytics"

    def test_create_schema_returns_valid_sql(self) -> None:
        """Test create_schema returns valid SQL."""
        service = AnalyticsService.__new__(AnalyticsService)

        schema = service.create_schema()

        assert "CREATE TABLE IF NOT EXISTS" in schema
        assert "analytics_records" in schema
        assert "id VARCHAR PRIMARY KEY" in schema
        assert "data JSON NOT NULL" in schema
        assert "created_at TIMESTAMP" in schema

    def test_inherits_from_base_service(self) -> None:
        """Test AnalyticsService inherits from BaseService."""
        from truth_forge.services.base import BaseService

        assert issubclass(AnalyticsService, BaseService)
