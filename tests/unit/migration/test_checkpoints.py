"""Tests for migration checkpoints module.

Tests the checkpoint validation functions.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.migration.checkpoints import (
    CheckpointResult,
    VALIDATORS,
    _check_command,
    _check_directory_exists,
    _check_file_exists,
    _check_import,
    validate_all_checkpoints,
    validate_checkpoint,
)


class TestCheckpointResult:
    """Tests for CheckpointResult dataclass."""

    def test_ok_status(self) -> None:
        """Test ok property with ok status."""
        result = CheckpointResult(phase=0, status="ok")
        assert result.ok is True
        assert result.failed is False

    def test_fail_status(self) -> None:
        """Test failed property with fail status."""
        result = CheckpointResult(phase=0, status="fail", issues=["error"])
        assert result.ok is False
        assert result.failed is True

    def test_warning_status(self) -> None:
        """Test warning status is neither ok nor failed."""
        result = CheckpointResult(phase=0, status="warning", warnings=["warn"])
        assert result.ok is False
        assert result.failed is False

    def test_default_lists(self) -> None:
        """Test default empty lists."""
        result = CheckpointResult(phase=0, status="ok")
        assert result.issues == []
        assert result.warnings == []


class TestCheckHelpers:
    """Tests for helper check functions."""

    def test_check_directory_exists_success(self) -> None:
        """Test _check_directory_exists when directory exists."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            result = _check_directory_exists(path, "test_dir")
            assert result is None

    def test_check_directory_exists_missing(self) -> None:
        """Test _check_directory_exists when directory is missing."""
        path = Path("/nonexistent/path/12345")
        result = _check_directory_exists(path, "test_dir")
        assert result is not None
        assert "Missing directory" in result

    def test_check_directory_exists_is_file(self) -> None:
        """Test _check_directory_exists when path is a file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "file.txt"
            file_path.write_text("content")
            result = _check_directory_exists(file_path, "test_dir")
            assert result is not None
            assert "Not a directory" in result

    def test_check_file_exists_success(self) -> None:
        """Test _check_file_exists when file exists."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            file_path.write_text("content")
            result = _check_file_exists(file_path, "test_file")
            assert result is None

    def test_check_file_exists_missing(self) -> None:
        """Test _check_file_exists when file is missing."""
        path = Path("/nonexistent/file.txt")
        result = _check_file_exists(path, "test_file")
        assert result is not None
        assert "Missing file" in result

    def test_check_file_exists_is_directory(self) -> None:
        """Test _check_file_exists when path is a directory."""
        with TemporaryDirectory() as tmpdir:
            result = _check_file_exists(Path(tmpdir), "test_file")
            assert result is not None
            assert "Not a file" in result

    def test_check_import_success(self) -> None:
        """Test _check_import with valid module."""
        result = _check_import("os")
        assert result is None

    def test_check_import_failure(self) -> None:
        """Test _check_import with invalid module."""
        result = _check_import("nonexistent_module_12345")
        assert result is not None
        assert "Import failed" in result

    @patch("subprocess.run")
    def test_check_command_success(self, mock_run: MagicMock) -> None:
        """Test _check_command when command succeeds."""
        mock_run.return_value = MagicMock(returncode=0)
        result = _check_command(["echo", "test"], "test command")
        assert result is None

    @patch("subprocess.run")
    def test_check_command_failure(self, mock_run: MagicMock) -> None:
        """Test _check_command when command fails."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error message")
        result = _check_command(["false"], "test command")
        assert result is not None
        assert "Command failed" in result

    @patch("subprocess.run")
    def test_check_command_exception(self, mock_run: MagicMock) -> None:
        """Test _check_command when exception occurs."""
        mock_run.side_effect = Exception("subprocess error")
        result = _check_command(["cmd"], "test command")
        assert result is not None
        assert "Command error" in result


class TestValidatePhase0:
    """Tests for validate_phase_0 function."""

    def test_validate_phase_0_all_exists(self) -> None:
        """Test validate_phase_0 when everything exists."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create all required directories
            src_tf = base / "src" / "truth_forge"
            src_tf.mkdir(parents=True)
            data_dir = base / "data"
            data_dir.mkdir()
            services_dir = base / "data" / "services"
            services_dir.mkdir()
            framework_dir = base / "framework"
            (framework_dir / "standards").mkdir(parents=True)

            # Create pyproject.toml with valid TOML
            pyproject = base / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"')

            # Patch paths at the point where they're imported
            with patch("truth_forge.core.paths.PROJECT_ROOT", base), patch(
                "truth_forge.core.paths.DATA_ROOT", data_dir
            ), patch("truth_forge.core.paths.SERVICES_ROOT", services_dir), patch(
                "truth_forge.core.paths.FRAMEWORK_ROOT", framework_dir
            ):
                from truth_forge.migration.checkpoints import validate_phase_0

                result = validate_phase_0()
                # May have warnings but should not fail if structure exists
                assert isinstance(result, CheckpointResult)
                assert result.phase == 0


class TestValidateCheckpoint:
    """Tests for validate_checkpoint function."""

    def test_validate_checkpoint_with_validator(self) -> None:
        """Test validate_checkpoint with existing validator."""
        # Create a mock validator that returns success
        mock_result = CheckpointResult(phase=0, status="ok")

        # Patch VALIDATORS dict to use our mock
        with patch.dict(VALIDATORS, {0: lambda: mock_result}):
            result = validate_checkpoint(0)
            assert result.phase == 0
            assert result.status == "ok"

    def test_validate_checkpoint_no_validator(self) -> None:
        """Test validate_checkpoint for phase without specific validator."""
        # Phase 99 doesn't have a specific validator
        result = validate_checkpoint(99)
        assert result.phase == 99
        assert result.status == "ok"
        assert any("No specific validator" in w for w in result.warnings)


class TestValidateAllCheckpoints:
    """Tests for validate_all_checkpoints function."""

    def test_validate_all_checkpoints(self) -> None:
        """Test validate_all_checkpoints runs validators for phases."""
        mock_result = CheckpointResult(phase=0, status="ok")

        # Patch validate_checkpoint to return mocked results
        with patch(
            "truth_forge.migration.checkpoints.validate_checkpoint",
            return_value=mock_result,
        ):
            results = validate_all_checkpoints(2)

            assert isinstance(results, list)


class TestValidatorsRegistry:
    """Tests for VALIDATORS registry."""

    def test_validators_registry_exists(self) -> None:
        """Test that VALIDATORS registry is populated."""
        assert isinstance(VALIDATORS, dict)
        assert 0 in VALIDATORS  # Phase 0
        assert 1 in VALIDATORS  # Phase 1
        assert 2 in VALIDATORS  # Phase 2

    def test_validators_are_callable(self) -> None:
        """Test that all validators are callable."""
        for phase, validator in VALIDATORS.items():
            assert callable(validator), f"Validator for phase {phase} is not callable"
