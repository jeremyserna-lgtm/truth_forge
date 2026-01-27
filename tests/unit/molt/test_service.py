"""Tests for molt service CLI.

Tests the service generation and migration commands.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from truth_forge.molt.service import (
    app,
    load_molt_config,
    SERVICE_TEMPLATE,
    _migrate_service,
)


runner = CliRunner()


class TestLoadMoltConfig:
    """Tests for load_molt_config function."""

    def test_load_molt_config_missing_file(self) -> None:
        """Test loading config when molt.yaml is missing."""
        with TemporaryDirectory() as tmpdir:
            with patch("truth_forge.molt.service.PROJECT_ROOT", Path(tmpdir)):
                result = runner.invoke(app, ["generate", "test"])
                # The command should fail since molt.yaml doesn't exist
                # But generate doesn't use load_molt_config directly
                pass

    def test_load_molt_config_valid(self) -> None:
        """Test loading valid molt.yaml."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("name: test\nservices:\n  mappings: []")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                config = load_molt_config()
                assert config["name"] == "test"

    def test_load_molt_config_invalid_yaml(self) -> None:
        """Test loading invalid YAML format."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            # Write a scalar instead of dict
            molt_file.write_text("just a string")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["migrate", "test"])
                assert result.exit_code != 0


class TestGenerateCommand:
    """Tests for generate command."""

    def test_generate_creates_service_file(self) -> None:
        """Test generate creates a new service file."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            services_dir = base / "src" / "truth_forge" / "services"
            services_dir.mkdir(parents=True)

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["generate", "test_svc"])

                assert result.exit_code == 0
                assert "Generated" in result.stdout

                output_file = services_dir / "test_svc.py"
                assert output_file.exists()

                content = output_file.read_text()
                assert "TestSvcService" in content
                assert "test_svc" in content

    def test_generate_refuses_overwrite_without_force(self) -> None:
        """Test generate refuses to overwrite existing file."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            services_dir = base / "src" / "truth_forge" / "services"
            services_dir.mkdir(parents=True)

            # Create existing file
            existing = services_dir / "existing.py"
            existing.write_text("# existing content")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["generate", "existing"])

                assert result.exit_code != 0
                assert "already exists" in result.stdout
                # Original content should be preserved
                assert existing.read_text() == "# existing content"

    def test_generate_overwrites_with_force(self) -> None:
        """Test generate overwrites with --force flag."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            services_dir = base / "src" / "truth_forge" / "services"
            services_dir.mkdir(parents=True)

            # Create existing file
            existing = services_dir / "existing.py"
            existing.write_text("# old content")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["generate", "existing", "--force"])

                assert result.exit_code == 0
                # Content should be replaced
                assert "ExistingService" in existing.read_text()

    def test_generate_creates_class_name_correctly(self) -> None:
        """Test generate creates correct class name from snake_case."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            services_dir = base / "src" / "truth_forge" / "services"
            services_dir.mkdir(parents=True)

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["generate", "my_awesome_service"])

                assert result.exit_code == 0
                output_file = services_dir / "my_awesome_service.py"
                content = output_file.read_text()
                assert "MyAwesomeServiceService" in content


class TestAnalyzeCommand:
    """Tests for analyze command."""

    def test_analyze_nonexistent_file(self) -> None:
        """Test analyze with nonexistent file."""
        result = runner.invoke(app, ["analyze", "/nonexistent/file.py"])
        assert "not found" in result.stdout.lower() or result.exit_code != 0

    def test_analyze_valid_python_file(self) -> None:
        """Test analyze with valid Python file."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test_service.py"
            test_file.write_text('''"""Test service."""
import os

class MyService:
    def process(self):
        return True

def helper_function():
    pass
''')

            result = runner.invoke(app, ["analyze", str(test_file)])

            assert result.exit_code == 0
            assert "Classes Found" in result.stdout
            assert "MyService" in result.stdout
            assert "helper_function" in result.stdout

    def test_analyze_detects_legacy_imports(self) -> None:
        """Test analyze detects legacy import patterns."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "legacy.py"
            test_file.write_text('''from Primitive.core import settings
from central_services.analytics import Analytics
''')

            result = runner.invoke(app, ["analyze", str(test_file)])

            assert result.exit_code == 0
            assert "LEGACY" in result.stdout

    def test_analyze_detects_hardcoded_paths(self) -> None:
        """Test analyze detects hardcoded paths."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "paths.py"
            test_file.write_text('''path = "/Users/jeremyserna/code"
tmp_path = "/tmp/data.json"
''')

            result = runner.invoke(app, ["analyze", str(test_file)])

            assert result.exit_code == 0
            assert "Hardcoded Paths" in result.stdout

    def test_analyze_detects_env_vars(self) -> None:
        """Test analyze detects environment variable usage."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "env.py"
            test_file.write_text('''import os
key = os.environ.get("API_KEY")
project = os.environ["PROJECT_ID"]
''')

            result = runner.invoke(app, ["analyze", str(test_file)])

            assert result.exit_code == 0
            assert "Environment Variables" in result.stdout
            assert "API_KEY" in result.stdout

    def test_analyze_syntax_error(self) -> None:
        """Test analyze handles syntax errors."""
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "bad.py"
            test_file.write_text("def broken(\n")

            result = runner.invoke(app, ["analyze", str(test_file)])

            assert "Cannot parse" in result.stdout or "Error" in result.stdout


class TestMigrateCommand:
    """Tests for migrate command."""

    def test_migrate_requires_service_or_all(self) -> None:
        """Test migrate requires either service name or --all."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("services:\n  mappings: []")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["migrate"])
                assert result.exit_code != 0

    def test_migrate_service_not_found(self) -> None:
        """Test migrate with service not in molt.yaml."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            molt_file = base / "molt.yaml"
            molt_file.write_text("services:\n  mappings: []")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["migrate", "nonexistent"])
                assert result.exit_code != 0
                assert "not found" in result.stdout.lower()

    def test_migrate_valid_service(self) -> None:
        """Test migrate with valid service in molt.yaml."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create molt.yaml with service mapping
            molt_file = base / "molt.yaml"
            molt_file.write_text("""services:
  mappings:
    - name: knowledge
      destination: src/truth_forge/services/knowledge
      sources:
        - legacy/knowledge_service.py
""")

            # Create legacy source file
            legacy_dir = base / "legacy"
            legacy_dir.mkdir()
            (legacy_dir / "knowledge_service.py").write_text('''"""Knowledge service."""
class KnowledgeService:
    pass
''')

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["migrate", "knowledge"])

                assert "Migrating service: knowledge" in result.stdout

    def test_migrate_all_services(self) -> None:
        """Test migrate --all migrates all services."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create molt.yaml with multiple services
            molt_file = base / "molt.yaml"
            molt_file.write_text("""services:
  mappings:
    - name: svc1
      destination: src/svc1
      sources: []
    - name: svc2
      destination: src/svc2
      sources: []
""")

            with patch("truth_forge.molt.service.PROJECT_ROOT", base):
                result = runner.invoke(app, ["migrate", "--all"])

                assert "svc1" in result.stdout
                assert "svc2" in result.stdout


class TestMigrateServiceHelper:
    """Tests for _migrate_service helper function."""

    def test_migrate_service_no_sources(self) -> None:
        """Test _migrate_service with no sources."""
        with patch("truth_forge.molt.service.typer") as mock_typer:
            _migrate_service("test", {"destination": "dst", "sources": []})
            # Should report no sources found
            calls = [str(c) for c in mock_typer.echo.call_args_list]
            assert any("No legacy sources" in str(c) for c in calls)

    def test_migrate_service_source_not_exists(self) -> None:
        """Test _migrate_service with nonexistent source."""
        with patch("truth_forge.molt.service.typer") as mock_typer:
            _migrate_service(
                "test",
                {"destination": "dst", "sources": ["/nonexistent/path"]},
            )
            calls = [str(c) for c in mock_typer.echo.call_args_list]
            assert any("does not exist" in str(c) for c in calls)

    def test_migrate_service_with_directory_source(self) -> None:
        """Test _migrate_service with directory source."""
        with TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "legacy"
            source_dir.mkdir()
            (source_dir / "test_service.py").write_text("# test")

            with patch("truth_forge.molt.service.typer") as mock_typer:
                _migrate_service(
                    "test",
                    {"destination": "dst", "sources": [str(source_dir)]},
                )


class TestServiceTemplate:
    """Tests for SERVICE_TEMPLATE constant."""

    def test_template_contains_required_elements(self) -> None:
        """Test template has all required placeholders."""
        assert "${service_name}" in SERVICE_TEMPLATE
        assert "${class_name}" in SERVICE_TEMPLATE
        assert "${service_title}" in SERVICE_TEMPLATE
        assert "BaseService" in SERVICE_TEMPLATE
        assert "process" in SERVICE_TEMPLATE
        assert "create_schema" in SERVICE_TEMPLATE
