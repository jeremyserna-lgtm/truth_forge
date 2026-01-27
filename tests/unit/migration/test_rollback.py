"""Tests for migration rollback module.

Tests backup and rollback functionality.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.migration.rollback import (
    cleanup_old_backups,
    create_backup,
    list_backups,
    rollback_to_backup,
)


class TestCreateBackup:
    """Tests for create_backup function."""

    def test_create_backup_creates_directory(self) -> None:
        """Test create_backup creates backup directory."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create services dir
            services = base / "data" / "services"
            services.mkdir(parents=True)
            (services / "test_service").mkdir()
            (services / "test_service" / "data.json").write_text("{}")

            # Patch at truth_forge.core.paths since imports happen inside the function
            with patch(
                "truth_forge.core.paths.PROJECT_ROOT", base
            ), patch("truth_forge.core.paths.DATA_ROOT", base / "data"):
                result = create_backup("test")

                assert result.exists()
                assert result.is_dir()
                assert (result / "manifest.json").exists()

    def test_create_backup_copies_services(self) -> None:
        """Test create_backup copies services directory."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create services dir with content
            services = base / "data" / "services"
            services.mkdir(parents=True)
            (services / "test.txt").write_text("test content")

            with patch(
                "truth_forge.core.paths.PROJECT_ROOT", base
            ), patch("truth_forge.core.paths.DATA_ROOT", base / "data"):
                result = create_backup("test")

                backup_services = result / "services"
                assert backup_services.exists()
                assert (backup_services / "test.txt").read_text() == "test content"

    def test_create_backup_manifest(self) -> None:
        """Test create_backup creates valid manifest."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            with patch(
                "truth_forge.core.paths.PROJECT_ROOT", base
            ), patch("truth_forge.core.paths.DATA_ROOT", base / "data"):
                result = create_backup("manifest_test")

                manifest_path = result / "manifest.json"
                assert manifest_path.exists()

                manifest = json.loads(manifest_path.read_text())
                assert "name" in manifest
                assert "timestamp" in manifest
                assert "manifest_test" in manifest["name"]


class TestRollbackToBackup:
    """Tests for rollback_to_backup function."""

    def test_rollback_nonexistent_backup(self) -> None:
        """Test rollback fails with nonexistent backup."""
        fake_path = Path("/nonexistent/backup/12345")
        with pytest.raises(ValueError) as exc_info:
            rollback_to_backup(fake_path)
        assert "does not exist" in str(exc_info.value)

    def test_rollback_invalid_backup(self) -> None:
        """Test rollback fails without manifest."""
        with TemporaryDirectory() as tmpdir:
            backup_dir = Path(tmpdir)
            # No manifest.json

            with pytest.raises(ValueError) as exc_info:
                rollback_to_backup(backup_dir)
            assert "missing manifest.json" in str(exc_info.value)

    def test_rollback_restores_services(self) -> None:
        """Test rollback restores services directory."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create backup structure
            backup_dir = base / "backup"
            backup_dir.mkdir()
            (backup_dir / "manifest.json").write_text('{"name": "test"}')

            # Create backup services
            backup_services = backup_dir / "services"
            backup_services.mkdir()
            (backup_services / "restored.txt").write_text("restored content")

            # Create current services (to be replaced)
            current_services = base / "data" / "services"
            current_services.mkdir(parents=True)
            (current_services / "current.txt").write_text("current content")

            with patch(
                "truth_forge.core.paths.PROJECT_ROOT", base
            ), patch("truth_forge.core.paths.DATA_ROOT", base / "data"):
                rollback_to_backup(backup_dir, restore_git=False)

                # Check restored
                assert (current_services / "restored.txt").exists()
                assert (current_services / "restored.txt").read_text() == "restored content"
                # Current file should be gone
                assert not (current_services / "current.txt").exists()


class TestListBackups:
    """Tests for list_backups function."""

    def test_list_backups_empty(self) -> None:
        """Test list_backups when no backups exist."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            with patch("truth_forge.core.paths.PROJECT_ROOT", base):
                result = list_backups()
                assert result == []

    def test_list_backups_with_backups(self) -> None:
        """Test list_backups finds existing backups."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create backups directory with backups
            backups_dir = base / "backups"
            backups_dir.mkdir()

            backup1 = backups_dir / "backup1"
            backup1.mkdir()
            (backup1 / "manifest.json").write_text(
                '{"name": "backup1", "timestamp": "2024-01-01"}'
            )

            backup2 = backups_dir / "backup2"
            backup2.mkdir()
            (backup2 / "manifest.json").write_text(
                '{"name": "backup2", "timestamp": "2024-01-02"}'
            )

            with patch("truth_forge.core.paths.PROJECT_ROOT", base):
                result = list_backups()

                assert len(result) == 2
                names = [b["name"] for b in result]
                assert "backup1" in names
                assert "backup2" in names


class TestCleanupOldBackups:
    """Tests for cleanup_old_backups function."""

    def test_cleanup_no_backups(self) -> None:
        """Test cleanup when no backups exist."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            with patch("truth_forge.core.paths.PROJECT_ROOT", base):
                result = cleanup_old_backups(keep=5)
                assert result == []

    def test_cleanup_removes_old_backups(self) -> None:
        """Test cleanup removes old backups beyond keep limit."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create backups directory with many backups
            backups_dir = base / "backups"
            backups_dir.mkdir()

            import time

            for i in range(10):
                backup = backups_dir / f"backup{i}"
                backup.mkdir()
                (backup / "data.txt").write_text(f"data {i}")
                time.sleep(0.01)  # Ensure different mtime

            with patch("truth_forge.core.paths.PROJECT_ROOT", base):
                result = cleanup_old_backups(keep=3)

                # Should remove 7 old backups
                assert len(result) == 7
                # Should keep 3 newest
                remaining = list(backups_dir.iterdir())
                assert len(remaining) == 3
