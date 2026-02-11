"""Tests for truth_forge.core.paths module.

Tests path resolution, service directory creation, and HOLD path generation.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from truth_forge.core.paths import (
    PROJECT_ROOT,
    PathResolutionError,
    ensure_service_directories,
    get_duckdb_file,
    get_hold1_path,
    get_hold2_path,
    get_intake_file,
    get_legacy_root,
    get_legacy_services_root,
    get_project_root,
    get_service_root,
    get_staging_path,
)


def _mock_roots(tmp_path: Path):
    """Return a combined patch context manager for PROJECT_ROOT and SERVICES_ROOT.

    The service-path functions (get_service_root, get_hold1_path, etc.) use
    the module-level SERVICES_ROOT constant, which is computed from
    PROJECT_ROOT at import time.  Patching PROJECT_ROOT alone has no effect
    on paths that read SERVICES_ROOT.  We must patch both.
    """
    services_root = tmp_path / "data" / "services"
    return patch.multiple(
        "truth_forge.core.paths",
        PROJECT_ROOT=tmp_path,
        SERVICES_ROOT=services_root,
    )


class TestGetProjectRoot:
    """Test project root resolution."""

    def test_resolves_from_env_var(self, tmp_path: Path) -> None:
        """Test resolution from TRUTH_FORGE_ROOT environment variable."""
        # Create a temporary directory with pyproject.toml
        test_root = tmp_path / "test_project"
        test_root.mkdir()
        (test_root / "pyproject.toml").write_text("[project]\nname = 'test'")

        with patch.dict(os.environ, {"TRUTH_FORGE_ROOT": str(test_root)}):
            # Clear cache
            get_project_root.cache_clear()
            result = get_project_root()
            assert result == test_root.resolve()

    def test_resolves_from_file_location(self, tmp_path: Path) -> None:
        """Test resolution by walking up from file location."""
        # Create project structure
        project_root = tmp_path / "project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]\nname = 'test'")
        (project_root / "src" / "truth_forge" / "core").mkdir(parents=True)

        with patch(
            "truth_forge.core.paths.__file__",
            str(project_root / "src" / "truth_forge" / "core" / "paths.py"),
        ):
            with patch.dict(os.environ, {}, clear=True):
                get_project_root.cache_clear()
                result = get_project_root()
                assert result == project_root.resolve()

    def test_resolves_from_cwd(self, tmp_path: Path) -> None:
        """Test resolution from current working directory.

        Must patch both __file__ (so the walk-up-from-file strategy fails)
        and Path.cwd (so the cwd strategy succeeds).
        """
        project_root = tmp_path / "cwd_project"
        project_root.mkdir()
        (project_root / "pyproject.toml").write_text("[project]\nname = 'test'")

        # Point __file__ at a location with no pyproject.toml anywhere above it
        fake_file = tmp_path / "nowhere" / "paths.py"
        (tmp_path / "nowhere").mkdir()

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("truth_forge.core.paths.__file__", str(fake_file)),
            patch("truth_forge.core.paths.Path.cwd", return_value=project_root),
        ):
            get_project_root.cache_clear()
            result = get_project_root()
            assert result == project_root

    def test_raises_error_when_not_found(self) -> None:
        """Test raises PathResolutionError when root cannot be found."""
        with patch.dict(os.environ, {}, clear=True):
            with patch("pathlib.Path.exists", return_value=False):
                get_project_root.cache_clear()
                with pytest.raises(PathResolutionError, match="Cannot determine project root"):
                    get_project_root()


class TestServicePaths:
    """Test service-specific path functions."""

    def test_get_service_root(self, tmp_path: Path) -> None:
        """Test get_service_root returns correct path."""
        with _mock_roots(tmp_path):
            result = get_service_root("knowledge")
            expected = tmp_path / "data" / "services" / "knowledge"
            assert result == expected

    def test_get_hold1_path_directory(self, tmp_path: Path) -> None:
        """Test get_hold1_path returns directory path."""
        with _mock_roots(tmp_path):
            result = get_hold1_path("knowledge")
            expected = tmp_path / "data" / "services" / "knowledge" / "hold1"
            assert result == expected

    def test_get_hold1_path_file(self, tmp_path: Path) -> None:
        """Test get_hold1_path returns file path when filename provided."""
        with _mock_roots(tmp_path):
            result = get_hold1_path("knowledge", "test.jsonl")
            expected = tmp_path / "data" / "services" / "knowledge" / "hold1" / "test.jsonl"
            assert result == expected

    def test_get_hold2_path_directory(self, tmp_path: Path) -> None:
        """Test get_hold2_path returns directory path."""
        with _mock_roots(tmp_path):
            result = get_hold2_path("knowledge")
            expected = tmp_path / "data" / "services" / "knowledge" / "hold2"
            assert result == expected

    def test_get_hold2_path_file(self, tmp_path: Path) -> None:
        """Test get_hold2_path returns file path when filename provided."""
        with _mock_roots(tmp_path):
            result = get_hold2_path("knowledge", "test.duckdb")
            expected = tmp_path / "data" / "services" / "knowledge" / "hold2" / "test.duckdb"
            assert result == expected

    def test_get_staging_path_directory(self, tmp_path: Path) -> None:
        """Test get_staging_path returns directory path."""
        with _mock_roots(tmp_path):
            result = get_staging_path("knowledge")
            expected = tmp_path / "data" / "services" / "knowledge" / "staging"
            assert result == expected

    def test_get_staging_path_file(self, tmp_path: Path) -> None:
        """Test get_staging_path returns file path when filename provided."""
        with _mock_roots(tmp_path):
            result = get_staging_path("knowledge", "test.txt")
            expected = tmp_path / "data" / "services" / "knowledge" / "staging" / "test.txt"
            assert result == expected


class TestStandardPaths:
    """Test standard file path functions."""

    def test_get_intake_file(self, tmp_path: Path) -> None:
        """Test get_intake_file returns correct intake file path."""
        with _mock_roots(tmp_path):
            result = get_intake_file("knowledge")
            expected = (
                tmp_path / "data" / "services" / "knowledge" / "hold1" / "knowledge_intake.jsonl"
            )
            assert result == expected

    def test_get_duckdb_file(self, tmp_path: Path) -> None:
        """Test get_duckdb_file returns correct DuckDB file path."""
        with _mock_roots(tmp_path):
            result = get_duckdb_file("knowledge")
            expected = tmp_path / "data" / "services" / "knowledge" / "hold2" / "knowledge.duckdb"
            assert result == expected


class TestEnsureServiceDirectories:
    """Test ensure_service_directories function."""

    def test_creates_all_directories(self, tmp_path: Path) -> None:
        """Test creates all required service directories."""
        with _mock_roots(tmp_path):
            result = ensure_service_directories("test_service")

            assert "root" in result
            assert "hold1" in result
            assert "hold2" in result
            assert "staging" in result

            # Verify directories exist
            assert result["root"].exists()
            assert result["hold1"].exists()
            assert result["hold2"].exists()
            assert result["staging"].exists()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Test creates parent directories if they don't exist."""
        with _mock_roots(tmp_path):
            ensure_service_directories(str(Path("nested") / "service"))
            service_root = tmp_path / "data" / "services" / "nested" / "service"
            assert service_root.exists()

    def test_idempotent(self, tmp_path: Path) -> None:
        """Test calling twice doesn't raise errors."""
        with _mock_roots(tmp_path):
            result1 = ensure_service_directories("test_service")
            result2 = ensure_service_directories("test_service")

            assert result1 == result2


class TestLegacyPaths:
    """Test legacy path functions."""

    def test_get_legacy_root(self, tmp_path: Path) -> None:
        """Test get_legacy_root returns correct path."""
        with _mock_roots(tmp_path):
            result = get_legacy_root()
            expected = tmp_path / "Truth_Engine"
            assert result == expected

    def test_get_legacy_services_root(self, tmp_path: Path) -> None:
        """Test get_legacy_services_root returns correct path."""
        with _mock_roots(tmp_path):
            result = get_legacy_services_root()
            expected = tmp_path / "Truth_Engine" / "src" / "services" / "central_services"
            assert result == expected


class TestProjectRootConstant:
    """Test PROJECT_ROOT constant."""

    def test_is_path_instance(self) -> None:
        """Test PROJECT_ROOT is a Path instance."""
        assert isinstance(PROJECT_ROOT, Path)

    def test_resolves_to_absolute_path(self) -> None:
        """Test PROJECT_ROOT is an absolute path."""
        assert PROJECT_ROOT.is_absolute()
