"""Tests for migration transform module.

Tests import and code transformation functions.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from truth_forge.migration.transform import (
    CODE_TRANSFORMATIONS,
    ENV_TRANSFORMATIONS,
    IMPORT_TRANSFORMATIONS,
    PATH_TRANSFORMATIONS,
    REQUIRED_IMPORTS,
    TransformResult,
    add_required_imports,
    apply_transformations,
    generate_migration_report,
    transform_directory,
    transform_file,
)


class TestTransformResult:
    """Tests for TransformResult dataclass."""

    def test_was_modified_true(self) -> None:
        """Test was_modified when content differs."""
        result = TransformResult(
            file_path=Path("test.py"),
            original_content="old",
            transformed_content="new",
        )
        assert result.was_modified is True

    def test_was_modified_false(self) -> None:
        """Test was_modified when content is the same."""
        result = TransformResult(
            file_path=Path("test.py"),
            original_content="same",
            transformed_content="same",
        )
        assert result.was_modified is False

    def test_change_count(self) -> None:
        """Test change_count property."""
        result = TransformResult(
            file_path=Path("test.py"),
            original_content="",
            transformed_content="",
            changes=["change1", "change2", "change3"],
        )
        assert result.change_count == 3

    def test_default_lists(self) -> None:
        """Test default empty lists."""
        result = TransformResult(
            file_path=Path("test.py"),
            original_content="",
            transformed_content="",
        )
        assert result.changes == []
        assert result.errors == []


class TestApplyTransformations:
    """Tests for apply_transformations function."""

    def test_no_matches(self) -> None:
        """Test apply_transformations with no matching patterns."""
        content = "print('hello world')"
        transformations: list[tuple[str, str, str]] = [
            (r"nonexistent", "replacement", "test"),
        ]

        result, changes = apply_transformations(content, transformations)
        assert result == content
        assert changes == []

    def test_single_match(self) -> None:
        """Test apply_transformations with single match."""
        content = "from Primitive.core import foo"
        transformations: list[tuple[str, str, str]] = [
            (r"from Primitive\.core", "from truth_forge.core", "test transform"),
        ]

        result, changes = apply_transformations(content, transformations)
        assert "from truth_forge.core" in result
        assert len(changes) == 1
        assert "1 occurrence" in changes[0]

    def test_multiple_matches(self) -> None:
        """Test apply_transformations with multiple matches."""
        content = """from Primitive.core import foo
from Primitive.core import bar
from Primitive.core import baz"""
        transformations: list[tuple[str, str, str]] = [
            (r"from Primitive\.core", "from truth_forge.core", "test transform"),
        ]

        result, changes = apply_transformations(content, transformations)
        assert result.count("from truth_forge.core") == 3
        assert "3 occurrence" in changes[0]


class TestImportTransformations:
    """Tests for IMPORT_TRANSFORMATIONS patterns."""

    def test_primitive_core_import(self) -> None:
        """Test Primitive.core import transformation."""
        content = "from Primitive.core.settings import settings"
        result, _ = apply_transformations(content, IMPORT_TRANSFORMATIONS)
        assert "from truth_forge.core.settings import" in result

    def test_primitive_services_import(self) -> None:
        """Test Primitive.services import transformation."""
        content = "from Primitive.services.identity import IdentityService"
        result, _ = apply_transformations(content, IMPORT_TRANSFORMATIONS)
        assert "from truth_forge.services.identity import" in result

    def test_src_services_import(self) -> None:
        """Test src.services import transformation."""
        content = "from src.services.knowledge import Knowledge"
        result, _ = apply_transformations(content, IMPORT_TRANSFORMATIONS)
        assert "from truth_forge.services.knowledge import" in result

    def test_central_services_import(self) -> None:
        """Test central_services import transformation."""
        content = "from central_services.analytics import Analytics"
        result, _ = apply_transformations(content, IMPORT_TRANSFORMATIONS)
        assert "from truth_forge.services.analytics import" in result

    def test_truth_engine_import(self) -> None:
        """Test Truth_Engine import transformation."""
        content = "from Truth_Engine.gateway import Gateway"
        result, _ = apply_transformations(content, IMPORT_TRANSFORMATIONS)
        assert "from truth_forge.gateway import" in result


class TestPathTransformations:
    """Tests for PATH_TRANSFORMATIONS patterns."""

    def test_hardcoded_truth_engine_path(self) -> None:
        """Test hardcoded Truth_Engine path transformation."""
        content = 'path = "/Users/jeremyserna/Truth_Engine"'
        result, _ = apply_transformations(content, PATH_TRANSFORMATIONS)
        assert "PROJECT_ROOT" in result

    def test_hardcoded_truth_forge_path(self) -> None:
        """Test hardcoded truth_forge path transformation."""
        content = 'path = "/Users/jeremyserna/truth_forge"'
        result, _ = apply_transformations(content, PATH_TRANSFORMATIONS)
        assert "PROJECT_ROOT" in result

    def test_path_home_truth_engine(self) -> None:
        """Test Path.home() / 'Truth_Engine' transformation."""
        content = "path = Path.home() / 'Truth_Engine'"
        result, _ = apply_transformations(content, PATH_TRANSFORMATIONS)
        assert "PROJECT_ROOT" in result


class TestEnvTransformations:
    """Tests for ENV_TRANSFORMATIONS patterns."""

    def test_gcp_project_env(self) -> None:
        """Test GCP_PROJECT env var transformation."""
        content = 'project = os.environ.get("GCP_PROJECT")'
        result, _ = apply_transformations(content, ENV_TRANSFORMATIONS)
        assert "settings.gcp_project" in result

    def test_gemini_api_key_env(self) -> None:
        """Test GEMINI_API_KEY env var transformation."""
        # The pattern expects os.environ.get(...) with parentheses
        content = 'key = os.environ.get("GEMINI_API_KEY")'
        result, _ = apply_transformations(content, ENV_TRANSFORMATIONS)
        assert "settings.effective_gemini_key" in result

    def test_anthropic_api_key_env(self) -> None:
        """Test ANTHROPIC_API_KEY env var transformation."""
        content = 'key = os.environ.get("ANTHROPIC_API_KEY", "")'
        result, _ = apply_transformations(content, ENV_TRANSFORMATIONS)
        assert "settings.anthropic_api_key" in result


class TestCodeTransformations:
    """Tests for CODE_TRANSFORMATIONS patterns."""

    def test_silent_exception_handler(self) -> None:
        """Test silent exception handler transformation."""
        content = """try:
    do_something()
except Exception:
    pass"""
        result, changes = apply_transformations(content, CODE_TRANSFORMATIONS)
        assert "logger.error" in result
        assert "MIGRATION" in result
        assert len(changes) > 0


class TestAddRequiredImports:
    """Tests for add_required_imports function."""

    def test_adds_missing_import(self) -> None:
        """Test adding missing import."""
        content = """import os

path = PROJECT_ROOT / "file.py"
"""
        result = add_required_imports(content, ["PROJECT_ROOT used"])
        assert "from truth_forge.core.paths import PROJECT_ROOT" in result

    def test_no_duplicate_imports(self) -> None:
        """Test doesn't add duplicate imports."""
        content = """from truth_forge.core.paths import PROJECT_ROOT

path = PROJECT_ROOT / "file.py"
"""
        result = add_required_imports(content, ["PROJECT_ROOT used"])
        assert result.count("PROJECT_ROOT") == 2  # Import and usage

    def test_no_imports_needed(self) -> None:
        """Test no change when no imports needed."""
        content = "print('hello')"
        result = add_required_imports(content, [])
        assert result == content


class TestTransformFile:
    """Tests for transform_file function."""

    def test_transform_file_success(self) -> None:
        """Test successful file transformation."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("from Primitive.core import foo")

            result = transform_file(file_path, dry_run=True)

            assert result.was_modified
            assert "truth_forge" in result.transformed_content

    def test_transform_file_dry_run(self) -> None:
        """Test dry run doesn't modify file."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            original = "from Primitive.core import foo"
            file_path.write_text(original)

            transform_file(file_path, dry_run=True)

            # File should be unchanged
            assert file_path.read_text() == original

    def test_transform_file_writes_changes(self) -> None:
        """Test non-dry-run writes changes."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("from Primitive.core import foo")

            transform_file(file_path, dry_run=False)

            # File should be changed
            assert "truth_forge" in file_path.read_text()

    def test_transform_file_unreadable(self) -> None:
        """Test handling of unreadable file."""
        result = transform_file(Path("/nonexistent/file.py"))
        assert len(result.errors) > 0
        assert "Cannot read" in result.errors[0]

    def test_transform_file_no_code_patterns(self) -> None:
        """Test transformation without code patterns."""
        with TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("except Exception:\n    pass")

            result = transform_file(file_path, dry_run=True, include_code_patterns=False)

            # Silent exception pattern should not be changed
            assert "except Exception:\n    pass" in result.transformed_content


class TestTransformDirectory:
    """Tests for transform_directory function."""

    def test_transform_directory_multiple_files(self) -> None:
        """Test transforming multiple files in directory."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create multiple Python files
            (base / "file1.py").write_text("from Primitive.core import foo")
            (base / "file2.py").write_text("from Primitive.services import bar")

            results = transform_directory(base, dry_run=True)

            assert len(results) == 2
            assert all(r.was_modified for r in results)

    def test_transform_directory_excludes_venv(self) -> None:
        """Test transform_directory excludes venv."""
        with TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)

            # Create file in venv
            venv_dir = base / ".venv"
            venv_dir.mkdir()
            (venv_dir / "test.py").write_text("from Primitive.core import foo")

            # Create file outside venv
            (base / "main.py").write_text("from Primitive.core import bar")

            results = transform_directory(base, dry_run=True)

            # Should only find main.py
            file_names = [r.file_path.name for r in results]
            assert "main.py" in file_names
            assert "test.py" not in file_names

    def test_transform_directory_empty(self) -> None:
        """Test transform_directory on empty directory."""
        with TemporaryDirectory() as tmpdir:
            results = transform_directory(Path(tmpdir), dry_run=True)
            assert results == []


class TestGenerateMigrationReport:
    """Tests for generate_migration_report function."""

    def test_report_empty_results(self) -> None:
        """Test report with no results."""
        report = generate_migration_report([])
        # Report uses markdown bold format
        assert "**Files scanned:** 0" in report
        assert "**Files modified:** 0" in report

    def test_report_with_modified_files(self) -> None:
        """Test report with modified files."""
        results = [
            TransformResult(
                file_path=Path("modified.py"),
                original_content="old",
                transformed_content="new",
                changes=["import change: 1 occurrence"],
            ),
        ]
        report = generate_migration_report(results)
        assert "**Files modified:** 1" in report
        assert "modified.py" in report
        assert "import change" in report

    def test_report_with_errors(self) -> None:
        """Test report with errors."""
        results = [
            TransformResult(
                file_path=Path("error.py"),
                original_content="",
                transformed_content="",
                errors=["Cannot read file"],
            ),
        ]
        report = generate_migration_report(results)
        assert "**Files with errors:** 1" in report
        assert "error.py" in report
        assert "Cannot read file" in report


class TestRequiredImports:
    """Tests for REQUIRED_IMPORTS dictionary."""

    def test_required_imports_has_project_root(self) -> None:
        """Test PROJECT_ROOT is in required imports."""
        assert "PROJECT_ROOT" in REQUIRED_IMPORTS
        assert "from truth_forge.core.paths" in REQUIRED_IMPORTS["PROJECT_ROOT"]

    def test_required_imports_has_settings(self) -> None:
        """Test settings is in required imports."""
        assert "settings" in REQUIRED_IMPORTS
        assert "from truth_forge.core.settings" in REQUIRED_IMPORTS["settings"]
