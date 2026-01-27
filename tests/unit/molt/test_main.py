"""Tests for molt __main__ module.

Tests the main CLI entry point.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from truth_forge.molt.__main__ import app, status, history


runner = CliRunner()


class TestStatusCommand:
    """Tests for status command."""

    def test_status_shows_header(self) -> None:
        """Test status command shows header."""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "MOLT" in result.stdout
        assert "Migration" in result.stdout or "Transformation" in result.stdout

    def test_status_shows_commands(self) -> None:
        """Test status command shows available commands."""
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "service" in result.stdout.lower()
        assert "code" in result.stdout.lower()
        assert "verify" in result.stdout.lower()


class TestHistoryCommand:
    """Tests for history command."""

    def test_history_shows_header(self) -> None:
        """Test history command shows header."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_dir = base / ".molt"
            molt_dir.mkdir()
            (molt_dir / "history.jsonl").write_text("")

            # Patch at the source module since imports happen inside function
            with patch("truth_forge.core.paths.PROJECT_ROOT", base):
                result = runner.invoke(app, ["history"])
                assert "MOLT HISTORY" in result.stdout

    def test_history_shows_summary(self) -> None:
        """Test history command shows summary statistics."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_dir = base / ".molt"
            molt_dir.mkdir()
            (molt_dir / "history.jsonl").write_text("")

            with patch("truth_forge.core.paths.PROJECT_ROOT", base):
                result = runner.invoke(app, ["history"])
                assert "Total operations" in result.stdout


class TestMainEntry:
    """Tests for main entry point."""

    def test_help_shows_subcommands(self) -> None:
        """Test --help shows available subcommands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "service" in result.stdout
        assert "code" in result.stdout
        assert "verify" in result.stdout

    def test_service_subcommand_exists(self) -> None:
        """Test service subcommand is available."""
        result = runner.invoke(app, ["service", "--help"])
        assert result.exit_code == 0
        assert "generate" in result.stdout

    def test_code_subcommand_exists(self) -> None:
        """Test code subcommand is available."""
        result = runner.invoke(app, ["code", "--help"])
        assert result.exit_code == 0
        assert "transform" in result.stdout

    def test_verify_subcommand_exists(self) -> None:
        """Test verify subcommand is available."""
        result = runner.invoke(app, ["verify", "--help"])
        assert result.exit_code == 0
        assert "types" in result.stdout
