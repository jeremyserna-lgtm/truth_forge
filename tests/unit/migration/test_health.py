"""Tests for migration health check module.

Tests the health check functions for services.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.migration.health import (
    check_all_services_health,
    check_service_health,
    verify_hold_sync,
)


class TestCheckServiceHealth:
    """Tests for check_service_health function."""

    @patch("truth_forge.core.paths.get_hold1_path")
    @patch("truth_forge.core.paths.get_hold2_path")
    @patch("truth_forge.core.paths.get_staging_path")
    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    def test_healthy_service_all_exist(
        self,
        mock_duckdb: MagicMock,
        mock_intake: MagicMock,
        mock_staging: MagicMock,
        mock_hold2: MagicMock,
        mock_hold1: MagicMock,
    ) -> None:
        """Test health check when all paths exist."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create directories
            hold1 = base / "hold1"
            hold2 = base / "hold2"
            staging = base / "staging"
            hold1.mkdir()
            hold2.mkdir()
            staging.mkdir()

            # Create intake file with valid JSON
            intake = base / "intake.jsonl"
            intake.write_text('{"id": 1}\n{"id": 2}\n')

            # Mock the path getters
            mock_hold1.return_value = hold1
            mock_hold2.return_value = hold2
            mock_staging.return_value = staging
            mock_intake.return_value = intake

            # DuckDB doesn't exist yet (warning, not error)
            duckdb_file = base / "data.duckdb"
            mock_duckdb.return_value = duckdb_file

            result = check_service_health("test_service")

            assert result["service"] == "test_service"
            assert result["healthy"] is True
            assert len(result["issues"]) == 0
            assert result["checks"]["hold1_exists"] is True
            assert result["checks"]["hold2_exists"] is True
            assert result["checks"]["intake_valid_lines"] == 2

    @patch("truth_forge.core.paths.get_hold1_path")
    @patch("truth_forge.core.paths.get_hold2_path")
    @patch("truth_forge.core.paths.get_staging_path")
    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    def test_missing_hold1_unhealthy(
        self,
        mock_duckdb: MagicMock,
        mock_intake: MagicMock,
        mock_staging: MagicMock,
        mock_hold2: MagicMock,
        mock_hold1: MagicMock,
    ) -> None:
        """Test health check when hold1 is missing."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # hold1 doesn't exist
            hold1 = base / "hold1"  # Not created
            hold2 = base / "hold2"
            hold2.mkdir()

            mock_hold1.return_value = hold1
            mock_hold2.return_value = hold2
            mock_staging.return_value = base / "staging"
            mock_intake.return_value = base / "intake.jsonl"
            mock_duckdb.return_value = base / "data.duckdb"

            result = check_service_health("test_service")

            assert result["healthy"] is False
            assert any("Missing hold1" in issue for issue in result["issues"])

    @patch("truth_forge.core.paths.get_hold1_path")
    @patch("truth_forge.core.paths.get_hold2_path")
    @patch("truth_forge.core.paths.get_staging_path")
    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    def test_invalid_json_unhealthy(
        self,
        mock_duckdb: MagicMock,
        mock_intake: MagicMock,
        mock_staging: MagicMock,
        mock_hold2: MagicMock,
        mock_hold1: MagicMock,
    ) -> None:
        """Test health check with invalid JSON in intake file."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            hold1 = base / "hold1"
            hold2 = base / "hold2"
            hold1.mkdir()
            hold2.mkdir()

            # Create intake file with invalid JSON
            intake = base / "intake.jsonl"
            intake.write_text('{"id": 1}\ninvalid json line\n{"id": 2}\n')

            mock_hold1.return_value = hold1
            mock_hold2.return_value = hold2
            mock_staging.return_value = base / "staging"
            mock_intake.return_value = intake
            mock_duckdb.return_value = base / "data.duckdb"

            result = check_service_health("test_service")

            assert result["healthy"] is False
            assert result["checks"]["intake_invalid_lines"] == 1
            assert any("Invalid JSON" in issue for issue in result["issues"])

    @patch("truth_forge.core.paths.get_hold1_path")
    @patch("truth_forge.core.paths.get_hold2_path")
    @patch("truth_forge.core.paths.get_staging_path")
    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    @patch("duckdb.connect")
    def test_duckdb_corrupted_directory(
        self,
        mock_connect: MagicMock,
        mock_duckdb: MagicMock,
        mock_intake: MagicMock,
        mock_staging: MagicMock,
        mock_hold2: MagicMock,
        mock_hold1: MagicMock,
    ) -> None:
        """Test health check when DuckDB is a directory (corrupted)."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            hold1 = base / "hold1"
            hold2 = base / "hold2"
            hold1.mkdir()
            hold2.mkdir()

            # Create DuckDB as directory (corrupted state)
            duckdb_path = base / "data.duckdb"
            duckdb_path.mkdir()  # Directory instead of file

            mock_hold1.return_value = hold1
            mock_hold2.return_value = hold2
            mock_staging.return_value = base / "staging"
            mock_intake.return_value = base / "intake.jsonl"
            mock_duckdb.return_value = duckdb_path

            result = check_service_health("test_service")

            assert result["healthy"] is False
            assert any("corrupted" in issue for issue in result["issues"])


class TestCheckAllServicesHealth:
    """Tests for check_all_services_health function."""

    @patch("truth_forge.core.paths.SERVICES_ROOT", new_callable=MagicMock)
    @patch.object(
        __import__("truth_forge.migration.health", fromlist=["check_service_health"]),
        "check_service_health",
    )
    def test_all_services_healthy(
        self, mock_check: MagicMock, mock_root: MagicMock
    ) -> None:
        """Test when all services are healthy."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create all expected service directories
            services = [
                "identity", "knowledge", "analytics", "quality",
                "pipeline", "hold", "run", "builder", "federation",
                "frontmatter", "model_gateway", "stage_awareness",
            ]
            for svc in services:
                (base / svc).mkdir()

            mock_root.__truediv__ = lambda self, x: base / x
            mock_check.return_value = {"service": "test", "healthy": True, "issues": []}

            result = check_all_services_health()

            assert result["services_healthy"] == 12
            assert result["services_unhealthy"] == 0
            assert result["overall_healthy"] is True

    @patch("truth_forge.core.paths.SERVICES_ROOT", new_callable=MagicMock)
    def test_missing_services(self, mock_root: MagicMock) -> None:
        """Test when services are missing."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            # Don't create any service directories

            mock_root.__truediv__ = lambda self, x: base / x

            result = check_all_services_health()

            assert result["services_missing"] == 12
            assert result["overall_healthy"] is False


class TestVerifyHoldSync:
    """Tests for verify_hold_sync function."""

    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    def test_both_empty_ok(
        self, mock_duckdb: MagicMock, mock_intake: MagicMock
    ) -> None:
        """Test sync is OK when both hold1 and hold2 are empty."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Neither file exists
            mock_intake.return_value = base / "intake.jsonl"
            mock_duckdb.return_value = base / "data.duckdb"

            result = verify_hold_sync("test_service")

            assert result["sync_ok"] is True
            assert result["hold1_count"] == 0
            assert result["hold2_count"] == 0

    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    def test_hold1_has_data_hold2_empty_not_ok(
        self, mock_duckdb: MagicMock, mock_intake: MagicMock
    ) -> None:
        """Test sync fails when hold1 has data but hold2 is empty."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create intake with data
            intake = base / "intake.jsonl"
            intake.write_text('{"id": 1}\n{"id": 2}\n')

            mock_intake.return_value = intake
            mock_duckdb.return_value = base / "data.duckdb"  # Doesn't exist

            result = verify_hold_sync("test_service")

            assert result["sync_ok"] is False
            assert result["hold1_count"] == 2
            assert result["hold2_count"] == 0
            assert result["sync_ratio"] == 0.0

    @patch("truth_forge.core.paths.get_intake_file")
    @patch("truth_forge.core.paths.get_duckdb_file")
    @patch("duckdb.connect")
    def test_sync_ratio_above_threshold(
        self,
        mock_connect: MagicMock,
        mock_duckdb: MagicMock,
        mock_intake: MagicMock,
    ) -> None:
        """Test sync is OK when ratio is above 90%."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create intake with 10 lines
            intake = base / "intake.jsonl"
            intake.write_text("\n".join([f'{{"id": {i}}}' for i in range(10)]) + "\n")

            # Create DuckDB file
            duckdb_file = base / "data.duckdb"
            duckdb_file.write_text("")  # Just needs to exist and be a file

            mock_intake.return_value = intake
            mock_duckdb.return_value = duckdb_file

            # Mock DuckDB to return 9 records (90%)
            mock_conn = MagicMock()
            mock_conn.execute.return_value.fetchone.return_value = (9,)
            mock_connect.return_value = mock_conn

            result = verify_hold_sync("test_service")

            assert result["sync_ok"] is True
            assert result["hold1_count"] == 10
            assert result["hold2_count"] == 9
            assert result["sync_ratio"] == 0.9
