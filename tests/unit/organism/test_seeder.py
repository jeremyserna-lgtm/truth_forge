"""Tests for project seeder module.

Tests the project seeding functionality.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from truth_forge.organism.seed.seeder import ProjectSeeder, SeedConfig


class TestSeedConfig:
    """Tests for SeedConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default seed config values."""
        config = SeedConfig(name="test_project")
        assert config.name == "test_project"
        assert config.parent_id == "truth_forge"
        assert config.template == "standard"
        assert config.include_framework is True
        assert config.include_tests is True

    def test_custom_values(self) -> None:
        """Test custom seed config values."""
        config = SeedConfig(
            name="custom_project",
            target_dir=Path("/tmp/custom"),
            parent_id="custom_parent",
            template="minimal",
            include_framework=False,
            include_tests=False,
        )
        assert config.name == "custom_project"
        assert config.target_dir == Path("/tmp/custom")
        assert config.parent_id == "custom_parent"
        assert config.template == "minimal"


class TestProjectSeeder:
    """Tests for ProjectSeeder class."""

    def test_init(self) -> None:
        """Test seeder initialization."""
        seeder = ProjectSeeder()
        assert seeder.get_seeded_projects() == []

    def test_seed_creates_directories(self) -> None:
        """Test seed creates standard directories."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            seeder.seed(config)

            assert (target / ".agent").exists()
            assert (target / ".claude" / "commands").exists()
            assert (target / ".claude" / "rules").exists()
            assert (target / ".seed").exists()
            assert (target / "src").exists()
            assert (target / "tests" / "unit").exists()
            assert (target / "data" / "local").exists()
            assert (target / "config" / "base").exists()

    def test_seed_creates_pyproject(self) -> None:
        """Test seed creates pyproject.toml."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            seeder.seed(config)

            pyproject = target / "pyproject.toml"
            assert pyproject.exists()
            content = pyproject.read_text()
            assert "test_project" in content
            assert "hatchling" in content

    def test_seed_creates_package(self) -> None:
        """Test seed creates Python package."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            seeder.seed(config)

            init_file = target / "src" / "test_project" / "__init__.py"
            assert init_file.exists()
            content = init_file.read_text()
            assert "__version__" in content

    def test_seed_creates_lineage(self) -> None:
        """Test seed creates lineage file."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            lineage = seeder.seed(config)

            lineage_file = target / ".seed" / "lineage.json"
            assert lineage_file.exists()
            assert lineage.organism_id == "test_project"
            assert lineage.parent_id == "truth_forge"
            assert lineage.generation == 1

    def test_seed_creates_claude_md(self) -> None:
        """Test seed creates CLAUDE.md."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            seeder.seed(config)

            claude_md = target / "CLAUDE.md"
            assert claude_md.exists()
            content = claude_md.read_text()
            assert "test_project" in content
            assert "Lineage" in content

    def test_seed_creates_conftest(self) -> None:
        """Test seed creates test conftest."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            seeder.seed(config)

            conftest = target / "tests" / "conftest.py"
            assert conftest.exists()
            content = conftest.read_text()
            assert "pytest" in content

    def test_seed_raises_if_exists(self) -> None:
        """Test seed raises if target exists."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            target.mkdir()

            seeder = ProjectSeeder()
            config = SeedConfig(name="test_project", target_dir=target)

            with pytest.raises(FileExistsError):
                seeder.seed(config)

    def test_seed_raises_if_no_name(self) -> None:
        """Test seed raises if name is empty."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "test_project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="", target_dir=target)

            with pytest.raises(ValueError):
                seeder.seed(config)

    def test_seed_tracks_seeded_projects(self) -> None:
        """Test seeder tracks seeded projects."""
        with TemporaryDirectory() as tmpdir:
            seeder = ProjectSeeder()

            config1 = SeedConfig(
                name="project1",
                target_dir=Path(tmpdir) / "project1",
            )
            config2 = SeedConfig(
                name="project2",
                target_dir=Path(tmpdir) / "project2",
            )

            seeder.seed(config1)
            seeder.seed(config2)

            seeded = seeder.get_seeded_projects()
            assert len(seeded) == 2
            assert seeded[0].organism_id == "project1"
            assert seeded[1].organism_id == "project2"

    def test_seed_handles_hyphenated_names(self) -> None:
        """Test seed handles hyphenated project names."""
        with TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "my-project"
            seeder = ProjectSeeder()
            config = SeedConfig(name="my-project", target_dir=target)

            seeder.seed(config)

            # Package name should use underscores
            init_file = target / "src" / "my_project" / "__init__.py"
            assert init_file.exists()
