"""Unit tests for governance service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from truth_forge.services.factory import ServiceFactory
from truth_forge.services.governance.service import GovernanceService


@pytest.fixture(autouse=True)
def clean_factory() -> Any:
    """Clean factory before and after each test."""
    ServiceFactory.clear()
    yield
    ServiceFactory.clear()


@pytest.fixture
def temp_services_dir(tmp_path: Path) -> Path:
    """Create temporary services directory.

    Patches SERVICES_ROOT directly since it's computed at import time.
    """
    services_dir = tmp_path / "services"
    services_dir.mkdir(parents=True)
    return services_dir


class TestGovernanceService:
    """Tests for GovernanceService class."""

    def test_service_name(self) -> None:
        """Test service_name is set correctly."""
        assert GovernanceService.service_name == "governance"

    def test_process_adds_event_id(self, temp_services_dir: Path) -> None:
        """Test process adds event_id if missing."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            record: dict[str, Any] = {"data": "test"}
            processed = service.process(record)

            assert "event_id" in processed
            assert len(processed["event_id"]) == 32  # SHA256 hex truncated

    def test_process_preserves_event_id(self, temp_services_dir: Path) -> None:
        """Test process preserves existing event_id."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            record: dict[str, Any] = {"event_id": "existing-id", "data": "test"}
            processed = service.process(record)

            assert processed["event_id"] == "existing-id"

    def test_process_adds_governance_timestamp(self, temp_services_dir: Path) -> None:
        """Test process adds governance_processed_at timestamp."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            record: dict[str, Any] = {"data": "test"}
            processed = service.process(record)

            assert "governance_processed_at" in processed
            # ISO format check
            assert "T" in processed["governance_processed_at"]

    def test_process_defaults_source(self, temp_services_dir: Path) -> None:
        """Test process defaults source to unknown."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            record: dict[str, Any] = {"data": "test"}
            processed = service.process(record)

            assert processed["source"] == "unknown"

    def test_process_preserves_source(self, temp_services_dir: Path) -> None:
        """Test process preserves existing source."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            record: dict[str, Any] = {"source": "molt_service", "data": "test"}
            processed = service.process(record)

            assert processed["source"] == "molt_service"

    def test_process_defaults_event_type(self, temp_services_dir: Path) -> None:
        """Test process defaults event_type to unknown."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            record: dict[str, Any] = {"data": "test"}
            processed = service.process(record)

            assert processed["event_type"] == "unknown"

    def test_inhale_creates_event(self, temp_services_dir: Path) -> None:
        """Test inhale creates properly structured event."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            event = service.inhale({"content": "test event"})

            assert event.id is not None
            assert event.aggregate_type == "governance"

    def test_get_event_count_empty(self, temp_services_dir: Path) -> None:
        """Test get_event_count returns 0 when no events."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            count = service.get_event_count()

            assert count == 0

    def test_get_summary_empty(self, temp_services_dir: Path) -> None:
        """Test get_summary returns empty summary when no events."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            summary = service.get_summary()

            assert summary["total_events"] == 0
            assert summary["by_source"] == {}
            assert summary["by_type"] == {}

    def test_create_schema(self, temp_services_dir: Path) -> None:
        """Test create_schema returns valid SQL."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            schema = service.create_schema()

            assert "CREATE TABLE IF NOT EXISTS governance_records" in schema
            assert "id VARCHAR PRIMARY KEY" in schema
            assert "data JSON NOT NULL" in schema
            assert "event_type VARCHAR" in schema
            assert "source VARCHAR" in schema

    def test_query_events_empty(self, temp_services_dir: Path) -> None:
        """Test query_events returns empty list when no events."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = GovernanceService()
            events = service.query_events()

            assert events == []


class TestGovernanceServiceIntegration:
    """Integration tests for GovernanceService with DuckDB."""

    def test_query_events_with_data(self, tmp_path: Path) -> None:
        """Test query_events returns data from DuckDB."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            # Create DuckDB with test data using unique IDs
            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                id1 = str(uuid.uuid4())
                id2 = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [id1, '{"test": "data1"}', "type1", "source1"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [id2, '{"test": "data2"}', "type2", "source2"],
                )
                conn.commit()
            finally:
                conn.close()

            # Query events
            events = service.query_events()

            assert len(events) == 2

    def test_query_events_with_filter(self, tmp_path: Path) -> None:
        """Test query_events with event_type filter."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{"test": "data1"}', "molt_started", "molt_service"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{"test": "data2"}', "error", "other"],
                )
                conn.commit()
            finally:
                conn.close()

            events = service.query_events(event_type="molt_started")

            assert len(events) == 1
            assert events[0]["test"] == "data1"

    def test_query_events_with_source_filter(self, tmp_path: Path) -> None:
        """Test query_events with source filter."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{"test": "data1"}', "type1", "molt_service"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{"test": "data2"}', "type2", "other"],
                )
                conn.commit()
            finally:
                conn.close()

            events = service.query_events(source="molt_service")

            assert len(events) == 1

    def test_query_events_with_limit(self, tmp_path: Path) -> None:
        """Test query_events respects limit."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                for i in range(10):
                    conn.execute(
                        "INSERT INTO governance_records (id, data, event_type, source) "
                        "VALUES (?, ?, ?, ?)",
                        [str(uuid.uuid4()), f'{{"index": {i}}}', "type", "source"],
                    )
                conn.commit()
            finally:
                conn.close()

            events = service.query_events(limit=3)

            assert len(events) == 3

    def test_get_event_count_with_data(self, tmp_path: Path) -> None:
        """Test get_event_count with actual data."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                for i in range(5):
                    conn.execute(
                        "INSERT INTO governance_records (id, data, event_type, source) "
                        "VALUES (?, ?, ?, ?)",
                        [str(uuid.uuid4()), '{}', "type", "source"],
                    )
                conn.commit()
            finally:
                conn.close()

            count = service.get_event_count()

            assert count == 5

    def test_get_event_count_with_source_filter(self, tmp_path: Path) -> None:
        """Test get_event_count with source filter."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{}', "type", "molt_service"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{}', "type", "molt_service"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{}', "type", "other"],
                )
                conn.commit()
            finally:
                conn.close()

            count = service.get_event_count(source="molt_service")

            assert count == 2

    def test_get_summary_with_data(self, tmp_path: Path) -> None:
        """Test get_summary with actual data."""
        import duckdb
        import uuid

        services_dir = tmp_path / "services"
        services_dir.mkdir(parents=True)

        with patch("truth_forge.core.paths.SERVICES_ROOT", services_dir):
            service = GovernanceService()

            duckdb_file = service._paths["hold2"] / "governance.duckdb"
            conn = duckdb.connect(str(duckdb_file))
            try:
                conn.execute(service.create_schema())
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{}', "molt_started", "molt_service"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{}', "molt_started", "molt_service"],
                )
                conn.execute(
                    "INSERT INTO governance_records (id, data, event_type, source) "
                    "VALUES (?, ?, ?, ?)",
                    [str(uuid.uuid4()), '{}', "error", "other_service"],
                )
                conn.commit()
            finally:
                conn.close()

            summary = service.get_summary()

            assert summary["total_events"] == 3
            assert summary["by_source"]["molt_service"] == 2
            assert summary["by_source"]["other_service"] == 1
            assert summary["by_type"]["molt_started"] == 2
            assert summary["by_type"]["error"] == 1


class TestGovernanceServiceRetry:
    """Tests for retry logic."""

    def test_with_retry_success(self) -> None:
        """Test _with_retry succeeds on first try."""
        from truth_forge.services.governance.service import _with_retry

        call_count = 0

        def operation() -> str:
            nonlocal call_count
            call_count += 1
            return "success"

        result = _with_retry(operation, "test_op")

        assert result == "success"
        assert call_count == 1

    def test_with_retry_retries_on_io_error(self) -> None:
        """Test _with_retry retries on IOException."""
        import duckdb

        from truth_forge.services.governance.service import _with_retry

        call_count = 0

        def operation() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise duckdb.IOException("Transient error")
            return "success"

        result = _with_retry(operation, "test_op", max_retries=3)

        assert result == "success"
        assert call_count == 3

    def test_with_retry_raises_non_io_error(self) -> None:
        """Test _with_retry raises non-IOException immediately."""
        from truth_forge.services.governance.service import _with_retry

        call_count = 0

        def operation() -> str:
            nonlocal call_count
            call_count += 1
            raise ValueError("Not an IO error")

        with pytest.raises(ValueError, match="Not an IO error"):
            _with_retry(operation, "test_op")

        assert call_count == 1


class TestGovernanceServiceRegistration:
    """Tests for governance service factory registration."""

    def test_governance_registered(self) -> None:
        """Test governance service can be registered."""
        from truth_forge.services.factory import ServiceFactory

        # Manually register (since fixture clears factory)
        ServiceFactory.register("governance", GovernanceService)

        assert ServiceFactory.is_registered("governance")

    def test_get_governance_service(self, temp_services_dir: Path) -> None:
        """Test getting governance service via factory."""
        from truth_forge.services.factory import ServiceFactory, get_service

        # Manually register (since fixture clears factory)
        ServiceFactory.register("governance", GovernanceService)

        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = get_service("governance")

            assert isinstance(service, GovernanceService)
            assert service.service_name == "governance"
