"""Unit tests for base service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.base import BaseService, ServiceState
from truth_forge.services.factory import ServiceFactory


@pytest.fixture
def mock_mediator() -> MagicMock:
    """Mock mediator service for tests that use inhale/sync."""
    mediator = MagicMock()
    mediator.service_name = "mediator"
    mediator.publish = MagicMock()
    return mediator


@pytest.fixture(autouse=True)
def clean_factory() -> Any:
    """Clean factory before and after each test."""
    ServiceFactory.clear()
    yield
    ServiceFactory.clear()


@pytest.fixture
def temp_services_dir(tmp_path: Path) -> Path:
    """Create temporary services directory structure.

    Patches SERVICES_ROOT directly since it's computed at import time.
    """
    services_dir = tmp_path / "services"
    services_dir.mkdir(parents=True)
    return services_dir


class ConcreteTestService(BaseService):
    """Concrete test service for testing BaseService."""

    service_name = "test_service"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process record by adding processed flag."""
        record["processed"] = True
        return record


class TestBaseServiceInit:
    """Tests for BaseService initialization."""

    def test_requires_service_name(self) -> None:
        """Test that service_name is required."""

        class NoNameService(BaseService):
            def process(self, record: dict[str, Any]) -> dict[str, Any]:
                return record

        with pytest.raises(ValueError, match="must define 'service_name'"):
            NoNameService()

    def test_initializes_with_service_name(self, temp_services_dir: Path) -> None:
        """Test initialization with valid service_name."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()

            assert service.service_name == "test_service"
            assert service.state == ServiceState.READY

    def test_creates_hold_directories(self, temp_services_dir: Path) -> None:
        """Test that HOLD directories are created."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()

            # Check paths were set
            assert "hold1" in service._paths
            assert "hold2" in service._paths
            assert "staging" in service._paths


class TestBaseServiceInhale:
    """Tests for BaseService.inhale()."""

    def test_inhale_creates_event(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test inhale creates event with proper structure."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            event = service.inhale({"content": "test data"})

            assert event.id is not None
            assert event.aggregate_type == "test_service"
            assert event.data["content"] == "test data"

    def test_inhale_writes_to_hold1(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test inhale writes to HOLD₁ (intake file)."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            service.inhale({"content": "test data"})

            intake_file = service._paths["hold1"] / "test_service_intake.jsonl"
            assert intake_file.exists()

            with open(intake_file) as f:
                lines = f.readlines()

            assert len(lines) == 1
            record = json.loads(lines[0])
            assert record["data"]["content"] == "test data"

    def test_inhale_appends_multiple_records(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test multiple inhale calls append to same file."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            service.inhale({"content": "first"})
            service.inhale({"content": "second"})
            service.inhale({"content": "third"})

            intake_file = service._paths["hold1"] / "test_service_intake.jsonl"
            with open(intake_file) as f:
                lines = f.readlines()

            assert len(lines) == 3


class TestBaseServiceSync:
    """Tests for BaseService.sync()."""

    def test_sync_empty_hold1(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test sync with no intake file."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            stats = service.sync()

            assert stats["processed"] == 0
            assert stats["failed"] == 0

    def test_sync_processes_records(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test sync processes records through AGENT."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()

            # Add records to HOLD₁
            service.inhale({"content": "record1"})
            service.inhale({"content": "record2"})

            # Sync HOLD₁ → HOLD₂
            stats = service.sync()

            assert stats["processed"] == 2
            assert stats["failed"] == 0

    def test_sync_handles_invalid_json(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test sync handles invalid JSON gracefully."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()

            # Create intake file with invalid JSON
            intake_file = service._paths["hold1"] / "test_service_intake.jsonl"
            with open(intake_file, "w") as f:
                f.write("not valid json\n")
                f.write('{"data": {"content": "valid"}}\n')

            stats = service.sync()

            assert stats["failed"] == 1
            assert stats["processed"] == 1

    def test_sync_writes_to_duckdb(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test sync writes processed records to DuckDB."""
        import duckdb

        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            service.inhale({"content": "test"})
            service.sync()

            # Verify record in DuckDB
            duckdb_file = service._paths["hold2"] / f"{service.service_name}.duckdb"
            conn = duckdb.connect(str(duckdb_file), read_only=True)
            try:
                result = conn.execute(
                    f"SELECT COUNT(*) FROM {service.service_name}_records"
                ).fetchone()
                assert result is not None
                assert result[0] == 1
            finally:
                conn.close()


class TestBaseServiceErrorHandling:
    """Tests for BaseService error handling."""

    def test_write_error_signal_creates_dlq(self, temp_services_dir: Path) -> None:
        """Test error signal writes to DLQ."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()
            service._write_error_signal(
                {"content": "failed record"}, ValueError("Test error")
            )

            dlq_file = service._paths["staging"] / f"{service.service_name}_dlq.jsonl"
            assert dlq_file.exists()

            with open(dlq_file) as f:
                record = json.loads(f.readline())

            assert "Test error" in record["data"]["error"]
            assert record["data"]["original_record"]["content"] == "failed record"


class TestBaseServiceExhale:
    """Tests for BaseService.exhale()."""

    def test_exhale_creates_event(self, temp_services_dir: Path) -> None:
        """Test exhale creates event."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()
            event = service.exhale({"result": "processed data"})

            assert event.id is not None
            assert event.data["result"] == "processed data"

    def test_exhale_writes_to_staging(self, temp_services_dir: Path) -> None:
        """Test exhale writes to staging."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()
            service.exhale({"result": "test"})

            staging_file = (
                service._paths["staging"] / f"{service.service_name}_staged.jsonl"
            )
            assert staging_file.exists()


class TestBaseServiceLifecycle:
    """Tests for BaseService lifecycle."""

    def test_shutdown(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test shutdown changes state."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            assert service.state == ServiceState.READY

            service.shutdown()

            assert service.state == ServiceState.STOPPED

    def test_health_check(self, temp_services_dir: Path) -> None:
        """Test health check returns status."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()
            health = service.health_check()

            assert isinstance(health, dict)
            assert "service" in health


class TestBaseServiceIteration:
    """Tests for BaseService iteration."""

    def test_iter_hold1_empty(self, temp_services_dir: Path) -> None:
        """Test iterating empty HOLD₁."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()
            records = list(service.iter_hold1())

            assert records == []

    def test_iter_hold1_with_records(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test iterating HOLD₁ with records."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()
            service.inhale({"content": "first"})
            service.inhale({"content": "second"})

            records = list(service.iter_hold1())

            assert len(records) == 2

    def test_transaction_context_manager(
        self, temp_services_dir: Path, mock_mediator: MagicMock
    ) -> None:
        """Test transaction context manager."""
        with (
            patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir),
            patch("truth_forge.services.factory.get_service", return_value=mock_mediator),
        ):
            service = ConcreteTestService()

            with service.transaction():
                service.inhale({"content": "in transaction"})

            intake_file = service._paths["hold1"] / "test_service_intake.jsonl"
            assert intake_file.exists()


class TestBaseServiceRepr:
    """Tests for BaseService representation."""

    def test_repr(self, temp_services_dir: Path) -> None:
        """Test string representation."""
        with patch("truth_forge.core.paths.SERVICES_ROOT", temp_services_dir):
            service = ConcreteTestService()
            repr_str = repr(service)

            assert "ConcreteTestService" in repr_str
            assert "test_service" in repr_str
            assert "ready" in repr_str
