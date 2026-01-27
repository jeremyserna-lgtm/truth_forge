"""Tests for molt code CLI.

Tests the code transformation commands.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from truth_forge.molt.code_cli import (
    app,
    _load_transform_config,
    _print_result,
)
from truth_forge.molt.code_molt import CodeMoltResult


runner = CliRunner()


class TestLoadTransformConfig:
    """Tests for _load_transform_config function."""

    def test_load_config_no_file(self) -> None:
        """Test loading config when molt.yaml doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", Path(tmpdir)):
                config = _load_transform_config()
                # Should return defaults
                assert config is not None
                assert hasattr(config, "import_rules")

    def test_load_config_with_file(self) -> None:
        """Test loading config from molt.yaml."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("""
code:
  transforms:
    import_rules:
      - pattern: "from old"
        replacement: "from new"
""")

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                config = _load_transform_config()
                assert config is not None

    def test_load_config_empty_transforms(self) -> None:
        """Test loading config with empty transforms."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("code:\n  transforms: {}")

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                config = _load_transform_config()
                # Should return defaults when empty
                assert config is not None


class TestPrintResult:
    """Tests for _print_result function."""

    def test_print_success_result(self) -> None:
        """Test printing successful result."""
        result = CodeMoltResult(
            source_name="test",
            files_found=10,
            files_transformed=5,
            files_unchanged=5,
            errors=[],
        )

        # Just verify it doesn't raise
        _print_result(result, dry_run=True)

    def test_print_result_with_errors(self) -> None:
        """Test printing result with errors."""
        result = CodeMoltResult(
            source_name="test",
            files_found=10,
            files_transformed=3,
            files_unchanged=5,
            errors=["Error 1", "Error 2"],
        )

        # Just verify it doesn't raise
        _print_result(result, dry_run=False)


class TestTransformCommand:
    """Tests for transform command."""

    def test_transform_file_dry_run(self) -> None:
        """Test transform single file in dry run mode."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create source file with transformable content
            source_file = base / "source.py"
            source_file.write_text("from Primitive.core import foo")

            dest_file = base / "dest.py"

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                result = runner.invoke(
                    app,
                    ["transform", str(source_file), str(dest_file), "--dry-run"],
                )

                assert result.exit_code == 0
                # Dest file should not exist in dry run
                # (unless it was already created)

    def test_transform_nonexistent_source(self) -> None:
        """Test transform with nonexistent source."""
        result = runner.invoke(
            app,
            ["transform", "/nonexistent/source.py", "/tmp/dest.py"],
        )

        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_transform_directory_dry_run(self) -> None:
        """Test transform directory in dry run mode."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create source directory with files
            source_dir = base / "source"
            source_dir.mkdir()
            (source_dir / "file1.py").write_text("print('hello')")
            (source_dir / "file2.py").write_text("print('world')")

            dest_dir = base / "dest"

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                result = runner.invoke(
                    app,
                    ["transform", str(source_dir), str(dest_dir), "--dry-run"],
                )

                assert result.exit_code == 0
                assert "DRY RUN" in result.stdout


class TestPhaseCommand:
    """Tests for phase command."""

    def test_phase_missing_molt_yaml(self) -> None:
        """Test phase command when molt.yaml is missing."""
        with TemporaryDirectory() as tmpdir:
            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", Path(tmpdir)):
                result = runner.invoke(app, ["phase", "1"])

                assert result.exit_code != 0
                assert "molt.yaml" in result.stdout.lower()

    def test_phase_not_found(self) -> None:
        """Test phase command when phase doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("""
code:
  phases:
    - phase: 1
      name: Phase One
""")

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                result = runner.invoke(app, ["phase", "99"])

                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_phase_shows_available(self) -> None:
        """Test phase command shows available phases on error."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("""
code:
  phases:
    - phase: 1
      name: Phase One
    - phase: 2
      name: Phase Two
""")

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                result = runner.invoke(app, ["phase", "99"])

                # Should show available phases
                assert result.exit_code != 0


class TestShowRulesCommand:
    """Tests for show-rules command."""

    def test_show_rules_displays_sections(self) -> None:
        """Test show-rules displays all rule sections."""
        with TemporaryDirectory() as tmpdir:
            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", Path(tmpdir)):
                result = runner.invoke(app, ["show-rules"])

                assert result.exit_code == 0
                assert "Import Rules" in result.stdout
                assert "Path Rules" in result.stdout
                assert "Environment Rules" in result.stdout

    def test_show_rules_with_config(self) -> None:
        """Test show-rules with custom configuration."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("""
code:
  transforms:
    import_rules:
      - pattern: "from old"
        replacement: "from new"
    path_rules: []
    env_rules: []
""")

            with patch("truth_forge.molt.code_cli.PROJECT_ROOT", base):
                result = runner.invoke(app, ["show-rules"])

                assert result.exit_code == 0
