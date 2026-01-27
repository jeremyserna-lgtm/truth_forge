"""Tests for CLI main module.

Tests the command-line interface for truth_forge.
"""

from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

import pytest

from truth_forge.cli.main import create_parser, cmd_status, cmd_seed, cmd_govern, main


class TestCreateParser:
    """Tests for create_parser function."""

    def test_creates_parser(self) -> None:
        """Test parser is created."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "truth_forge"

    def test_parser_has_verbose_flag(self) -> None:
        """Test parser has verbose flag."""
        parser = create_parser()
        args = parser.parse_args(["--verbose", "status"])
        assert args.verbose is True

    def test_parser_has_json_flag(self) -> None:
        """Test parser has json flag."""
        parser = create_parser()
        args = parser.parse_args(["--json", "status"])
        assert args.json is True

    def test_parser_has_status_command(self) -> None:
        """Test parser has status command."""
        parser = create_parser()
        args = parser.parse_args(["status"])
        assert args.command == "status"

    def test_parser_has_seed_command(self) -> None:
        """Test parser has seed command."""
        parser = create_parser()
        args = parser.parse_args(["seed", "test_project"])
        assert args.command == "seed"
        assert args.name == "test_project"

    def test_parser_has_govern_command(self) -> None:
        """Test parser has govern command."""
        parser = create_parser()
        args = parser.parse_args(["govern"])
        assert args.command == "govern"

    def test_status_detailed_flag(self) -> None:
        """Test status --detailed flag."""
        parser = create_parser()
        args = parser.parse_args(["status", "--detailed"])
        assert args.detailed is True

    def test_seed_target_flag(self) -> None:
        """Test seed --target flag."""
        parser = create_parser()
        args = parser.parse_args(["seed", "test", "--target", "/tmp"])
        # target is parsed as Path
        assert args.target == Path("/tmp")


class TestCmdStatus:
    """Tests for cmd_status function."""

    def test_returns_zero_on_success(self) -> None:
        """Test status command returns 0."""
        parser = create_parser()
        args = parser.parse_args(["status"])
        result = cmd_status(args)
        assert result == 0

    def test_json_output(self) -> None:
        """Test status command with JSON output."""
        parser = create_parser()
        args = parser.parse_args(["--json", "status"])

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cmd_status(args)
            output = mock_stdout.getvalue()

        assert result == 0
        # Output should be valid JSON
        data = json.loads(output)
        assert "project_root" in data


class TestMain:
    """Tests for main function."""

    def test_no_command_exits_zero(self) -> None:
        """Test main with no command exits with 0 (shows help)."""
        with pytest.raises(SystemExit) as exc_info:
            main([])
        assert exc_info.value.code == 0

    def test_status_command_exits_zero(self) -> None:
        """Test main with status command exits with 0."""
        with patch("sys.stdout", new_callable=StringIO):
            with pytest.raises(SystemExit) as exc_info:
                main(["status"])
        assert exc_info.value.code == 0

    def test_verbose_enables_logging(self) -> None:
        """Test verbose flag enables debug logging."""
        with patch("sys.stdout", new_callable=StringIO):
            with patch("logging.basicConfig") as mock_logging:
                with pytest.raises(SystemExit):
                    main(["--verbose", "status"])
                mock_logging.assert_called_once()
                call_args = mock_logging.call_args
                assert call_args[1]["level"] == 10  # DEBUG level

    def test_unknown_command_exits_one(self) -> None:
        """Test main with unknown command exits with 1."""
        parser = create_parser()
        # Mock the commands dict to simulate unknown command
        with patch("sys.stderr", new_callable=StringIO):
            with patch("truth_forge.cli.main.create_parser") as mock_parser:
                mock_args = MagicMock()
                mock_args.command = "unknown_command"
                mock_args.verbose = False
                mock_parser.return_value.parse_args.return_value = mock_args

                with pytest.raises(SystemExit) as exc_info:
                    main([])
                assert exc_info.value.code == 1


class TestCmdStatusDetailed:
    """Tests for cmd_status detailed mode."""

    def test_detailed_counts_files(self) -> None:
        """Test status --detailed counts source and test files."""
        parser = create_parser()
        args = parser.parse_args(["status", "--detailed"])

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cmd_status(args)
            output = mock_stdout.getvalue()

        assert result == 0
        assert "Source files:" in output
        assert "Test files:" in output

    def test_detailed_json_includes_counts(self) -> None:
        """Test status --detailed --json includes file counts."""
        parser = create_parser()
        args = parser.parse_args(["--json", "status", "--detailed"])

        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            result = cmd_status(args)
            output = mock_stdout.getvalue()

        assert result == 0
        data = json.loads(output)
        assert "source_files" in data
        assert "test_files" in data


class TestCmdSeed:
    """Tests for cmd_seed function."""

    def test_seed_success(self) -> None:
        """Test seed command succeeds."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            parser = create_parser()
            args = parser.parse_args(["seed", "test_project", "--target", str(target)])

            # Mock the seeder to avoid actual file creation
            mock_lineage = MagicMock()
            mock_lineage.organism_id = "test-organism-123"
            mock_lineage.parent_id = "parent-id"
            mock_lineage.generation = 1

            # Patch at source since imports happen inside function
            with patch("truth_forge.organism.seed.ProjectSeeder") as mock_seeder_class:
                mock_seeder = MagicMock()
                mock_seeder.seed.return_value = mock_lineage
                mock_seeder_class.return_value = mock_seeder

                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = cmd_seed(args)
                    output = mock_stdout.getvalue()

            assert result == 0
            assert "test-organism-123" in output
            assert "parent-id" in output

    def test_seed_json_output(self) -> None:
        """Test seed command with JSON output."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            parser = create_parser()
            args = parser.parse_args(["--json", "seed", "test_project", "--target", str(target)])

            mock_lineage = MagicMock()
            mock_lineage.organism_id = "test-organism-123"
            mock_lineage.parent_id = "parent-id"
            mock_lineage.generation = 1

            with patch("truth_forge.organism.seed.ProjectSeeder") as mock_seeder_class:
                mock_seeder = MagicMock()
                mock_seeder.seed.return_value = mock_lineage
                mock_seeder_class.return_value = mock_seeder

                with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                    result = cmd_seed(args)
                    output = mock_stdout.getvalue()

            assert result == 0
            data = json.loads(output)
            assert data["organism_id"] == "test-organism-123"

    def test_seed_default_target(self) -> None:
        """Test seed command uses default target when not specified."""
        parser = create_parser()
        args = parser.parse_args(["seed", "my_project"])

        mock_lineage = MagicMock()
        mock_lineage.organism_id = "test-org"
        mock_lineage.parent_id = "parent"
        mock_lineage.generation = 1

        with patch("truth_forge.organism.seed.ProjectSeeder") as mock_seeder_class:
            mock_seeder = MagicMock()
            mock_seeder.seed.return_value = mock_lineage
            mock_seeder_class.return_value = mock_seeder

            with patch("sys.stdout", new_callable=StringIO):
                result = cmd_seed(args)

        assert result == 0
        # Verify seeder was called with default target (~/projects/my_project)
        call_args = mock_seeder.seed.call_args[0][0]
        assert call_args.name == "my_project"
        assert "projects" in str(call_args.target_dir)

    def test_seed_file_exists_error(self) -> None:
        """Test seed command handles FileExistsError."""
        parser = create_parser()
        args = parser.parse_args(["seed", "existing_project"])

        with patch("truth_forge.organism.seed.ProjectSeeder") as mock_seeder_class:
            mock_seeder = MagicMock()
            mock_seeder.seed.side_effect = FileExistsError("Directory already exists")
            mock_seeder_class.return_value = mock_seeder

            with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
                result = cmd_seed(args)

            assert result == 1
            assert "already exists" in mock_stderr.getvalue()


class TestCmdGovern:
    """Tests for cmd_govern function."""

    def test_govern_default_status(self) -> None:
        """Test govern command shows default status."""
        parser = create_parser()
        args = parser.parse_args(["govern"])

        # Patch at source since imports happen inside function
        with patch("truth_forge.governance.UnifiedGovernance") as mock_gov_class:
            mock_gov = MagicMock()
            mock_gov_class.return_value = mock_gov

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cmd_govern(args)
                output = mock_stdout.getvalue()

        assert result == 0
        assert "Governance Status" in output
        assert "Isolation Enabled" in output

    def test_govern_status_json(self) -> None:
        """Test govern command with JSON output."""
        parser = create_parser()
        args = parser.parse_args(["--json", "govern"])

        with patch("truth_forge.governance.UnifiedGovernance") as mock_gov_class:
            mock_gov = MagicMock()
            mock_gov_class.return_value = mock_gov

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cmd_govern(args)
                output = mock_stdout.getvalue()

        assert result == 0
        data = json.loads(output)
        assert data["isolation_enabled"] is True
        assert data["cost_tracking_enabled"] is True

    def test_govern_violations(self) -> None:
        """Test govern --violations shows violations."""
        parser = create_parser()
        args = parser.parse_args(["govern", "--violations"])

        mock_violation = MagicMock()
        mock_violation.timestamp.isoformat.return_value = "2026-01-26T12:00:00"
        mock_violation.operation = "TEST_OP"
        mock_violation.error_message = "Test error"

        with patch("truth_forge.governance.UnifiedGovernance") as mock_gov_class:
            mock_gov = MagicMock()
            mock_gov.audit_trail.get_violations.return_value = [mock_violation]
            mock_gov_class.return_value = mock_gov

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cmd_govern(args)
                output = mock_stdout.getvalue()

        assert result == 0
        assert "Recent Violations" in output
        assert "TEST_OP" in output
        assert "Test error" in output

    def test_govern_violations_empty(self) -> None:
        """Test govern --violations with no violations."""
        parser = create_parser()
        args = parser.parse_args(["govern", "--violations"])

        with patch("truth_forge.governance.UnifiedGovernance") as mock_gov_class:
            mock_gov = MagicMock()
            mock_gov.audit_trail.get_violations.return_value = []
            mock_gov_class.return_value = mock_gov

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cmd_govern(args)
                output = mock_stdout.getvalue()

        assert result == 0
        assert "No violations recorded" in output

    def test_govern_violations_json(self) -> None:
        """Test govern --violations with JSON output."""
        parser = create_parser()
        args = parser.parse_args(["--json", "govern", "--violations"])

        mock_violation = MagicMock()
        mock_violation.to_dict.return_value = {"operation": "TEST_OP", "message": "error"}

        with patch("truth_forge.governance.UnifiedGovernance") as mock_gov_class:
            mock_gov = MagicMock()
            mock_gov.audit_trail.get_violations.return_value = [mock_violation]
            mock_gov_class.return_value = mock_gov

            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                result = cmd_govern(args)
                output = mock_stdout.getvalue()

        assert result == 0
        data = json.loads(output)
        assert len(data) == 1
        assert data[0]["operation"] == "TEST_OP"
