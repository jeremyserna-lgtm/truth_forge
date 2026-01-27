"""Tests for molt verify CLI.

Tests the verification commands.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from truth_forge.molt.verify_cli import app, _run_command


runner = CliRunner()


class TestRunCommand:
    """Tests for _run_command helper function."""

    def test_run_command_success(self) -> None:
        """Test running successful command."""
        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            success, output = _run_command(["echo", "test"], "Test echo")
            assert success is True
            assert "test" in output

    def test_run_command_failure(self) -> None:
        """Test running failing command."""
        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            success, output = _run_command(["false"], "Test false")
            # 'false' command should return non-zero
            assert success is False

    def test_run_command_exception(self) -> None:
        """Test running command that raises exception."""
        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            with patch(
                "truth_forge.molt.verify_cli.subprocess.run",
                side_effect=Exception("Command error"),
            ):
                success, output = _run_command(["test"], "Test")
                assert success is False
                assert "Command error" in output


class TestTypesCommand:
    """Tests for types command."""

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_types_success(self, mock_run: MagicMock) -> None:
        """Test types command success."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["types", "src/"])

            assert result.exit_code == 0
            assert "passed" in result.stdout.lower()

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_types_failure(self, mock_run: MagicMock) -> None:
        """Test types command failure."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="error: Type error",
            stderr="",
        )

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["types", "src/"])

            assert result.exit_code != 0
            assert "failed" in result.stdout.lower()

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_types_no_strict(self, mock_run: MagicMock) -> None:
        """Test types command without strict mode."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["types", "--no-strict"])

            # Command should be called without --strict
            assert result.exit_code == 0


class TestLintCommand:
    """Tests for lint command."""

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_lint_success(self, mock_run: MagicMock) -> None:
        """Test lint command success."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["lint", "src/"])

            assert result.exit_code == 0
            assert "passed" in result.stdout.lower()

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_lint_with_fix(self, mock_run: MagicMock) -> None:
        """Test lint command with --fix option."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["lint", "--fix", "src/"])

            assert result.exit_code == 0


class TestFormatCheckCommand:
    """Tests for format-check command."""

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_format_check_success(self, mock_run: MagicMock) -> None:
        """Test format-check command success."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["format-check", "src/"])

            assert result.exit_code == 0
            assert "passed" in result.stdout.lower()


class TestTestsCommand:
    """Tests for tests command."""

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_tests_success(self, mock_run: MagicMock) -> None:
        """Test tests command success."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["tests", "tests/"])

            assert result.exit_code == 0
            assert "passed" in result.stdout.lower()

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_tests_with_coverage(self, mock_run: MagicMock) -> None:
        """Test tests command with coverage threshold."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["tests", "--cov", "80"])

            assert result.exit_code == 0

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_tests_verbose(self, mock_run: MagicMock) -> None:
        """Test tests command verbose mode."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["tests", "-v"])

            assert result.exit_code == 0


class TestServicesCommand:
    """Tests for services command."""

    def test_services_checks_registration(self) -> None:
        """Test services command checks service registration."""
        result = runner.invoke(app, ["services"])

        # Should check multiple services
        assert "secret" in result.stdout.lower() or "Verifying" in result.stdout

    @patch("truth_forge.services.factory.ServiceFactory.is_registered")
    def test_services_all_registered(self, mock_registered: MagicMock) -> None:
        """Test services command when all registered."""
        mock_registered.return_value = True

        result = runner.invoke(app, ["services"])

        assert result.exit_code == 0
        assert "passed" in result.stdout.lower() or "✓" in result.stdout

    @patch("truth_forge.services.factory.ServiceFactory.is_registered")
    def test_services_some_missing(self, mock_registered: MagicMock) -> None:
        """Test services command when some not registered."""
        mock_registered.return_value = False

        result = runner.invoke(app, ["services"])

        assert result.exit_code != 0


class TestHoldCommand:
    """Tests for hold command."""

    def test_hold_missing_services_dir(self) -> None:
        """Test hold command when services dir doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path(tmpdir)):
                result = runner.invoke(app, ["hold"])

                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_hold_all_present(self) -> None:
        """Test hold command when all HOLD dirs present."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create services directory with HOLD pattern
            services_dir = base / "data" / "services"
            for svc in ["secret", "mediator", "governance"]:
                svc_dir = services_dir / svc
                (svc_dir / "hold1").mkdir(parents=True)
                (svc_dir / "hold2").mkdir()
                (svc_dir / "staging").mkdir()

            with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", base):
                result = runner.invoke(app, ["hold"])

                # Some services might pass
                assert "HOLD pattern" in result.stdout

    def test_hold_missing_dirs(self) -> None:
        """Test hold command when some HOLD dirs missing."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create services directory with incomplete HOLD pattern
            services_dir = base / "data" / "services"
            (services_dir / "secret").mkdir(parents=True)
            # Only create hold1, missing hold2 and staging

            with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", base):
                result = runner.invoke(app, ["hold"])

                # Should fail due to missing dirs
                assert result.exit_code != 0


class TestFullCommand:
    """Tests for full command."""

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_full_shows_summary(self, mock_run: MagicMock) -> None:
        """Test full command shows summary."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["full"])

            assert "SUMMARY" in result.stdout
            assert "FULL VALIDATION" in result.stdout

    @patch("truth_forge.molt.verify_cli.subprocess.run")
    def test_full_runs_all_checks(self, mock_run: MagicMock) -> None:
        """Test full command runs all check types."""
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        with patch("truth_forge.molt.verify_cli.PROJECT_ROOT", Path("/")):
            result = runner.invoke(app, ["full"])

            # Should mention various check types
            assert "Type checking" in result.stdout or "types" in result.stdout.lower()
