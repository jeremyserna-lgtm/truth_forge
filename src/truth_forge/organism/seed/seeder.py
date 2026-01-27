"""Project Seeder - Create New Organisms.

MOLT LINEAGE:
- Source: Truth_Engine/src/truth_forge/seed/seed_project.py
- Version: 2.0.0
- Date: 2026-01-26

Creates new projects (organisms) from the truth_forge nucleus.

BIOLOGICAL METAPHOR:
- ProjectSeeder = Cell division machinery
- seed() = Mitosis
- Template = DNA to be replicated

Example:
    seeder = ProjectSeeder()
    lineage = seeder.seed(
        name="my_project",
        target_dir=Path.home() / "projects" / "my_project",
    )
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, ClassVar

from truth_forge.core.paths import PROJECT_ROOT
from truth_forge.organism.seed.federation import Lineage


logger = logging.getLogger(__name__)


@dataclass
class SeedConfig:
    """Configuration for seeding a new project.

    Attributes:
        name: Project name
        target_dir: Where to create the project
        parent_id: Parent organism ID
        template: Template to use
        include_framework: Whether to include framework reference
        include_tests: Whether to include test scaffolding
        metadata: Additional metadata
    """

    name: str
    target_dir: Path | None = None
    parent_id: str = "truth_forge"
    template: str = "standard"
    include_framework: bool = True
    include_tests: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class ProjectSeeder:
    """Creates new organisms from the truth_forge nucleus.

    The seeder handles:
    1. Creating directory structure
    2. Setting up pyproject.toml
    3. Creating initial modules
    4. Establishing lineage tracking
    5. Registering with federation

    BIOLOGICAL METAPHOR:
    - ProjectSeeder = Cell division apparatus
    - seed() = Mitosis trigger
    - Lineage = Genetic inheritance

    Example:
        seeder = ProjectSeeder()

        # Seed a new project
        lineage = seeder.seed(SeedConfig(
            name="my_project",
            target_dir=Path.home() / "projects" / "my_project",
        ))

        print(f"Created {lineage.organism_id} at generation {lineage.generation}")
    """

    # Standard directories to create
    STANDARD_DIRS: ClassVar[list[str]] = [
        ".agent",
        ".claude/commands",
        ".claude/rules",
        ".claude/skills",
        ".seed",
        "src",
        "tests/unit",
        "tests/integration",
        "tests/fixtures",
        "data/local",
        "data/staging",
        "config/base",
        "config/local",
        "docs",
    ]

    def __init__(self) -> None:
        """Initialize the project seeder."""
        self._seeded_projects: list[Lineage] = []
        logger.info("ProjectSeeder initialized")

    def seed(self, config: SeedConfig) -> Lineage:
        """Seed a new project.

        Args:
            config: Seeding configuration.

        Returns:
            Lineage information for the new project.

        Raises:
            FileExistsError: If target directory already exists.
            ValueError: If configuration is invalid.
        """
        # Validate
        if not config.name:
            raise ValueError("Project name is required")

        # Determine target directory
        target_dir = config.target_dir
        if target_dir is None:
            target_dir = Path.home() / "projects" / config.name
        target_dir = Path(target_dir)

        # Check if exists
        if target_dir.exists():
            raise FileExistsError(f"Target directory already exists: {target_dir}")

        logger.info("Seeding project", extra={"name": config.name, "target": str(target_dir)})

        # Create directory structure
        self._create_directories(target_dir, config)

        # Create pyproject.toml
        self._create_pyproject(target_dir, config)

        # Create initial modules
        self._create_modules(target_dir, config)

        # Create lineage file
        lineage = self._create_lineage(target_dir, config)

        # Create CLAUDE.md
        self._create_claude_md(target_dir, config)

        # Track
        self._seeded_projects.append(lineage)

        logger.info(
            "Project seeded successfully",
            extra={
                "organism_id": lineage.organism_id,
                "generation": lineage.generation,
            },
        )

        return lineage

    def _create_directories(self, target_dir: Path, config: SeedConfig) -> None:
        """Create standard directory structure.

        Args:
            target_dir: Root directory for the project.
            config: Seeding configuration.
        """
        for dir_path in self.STANDARD_DIRS:
            (target_dir / dir_path).mkdir(parents=True, exist_ok=True)

        # Create src/{name} package
        src_pkg = target_dir / "src" / config.name.replace("-", "_")
        src_pkg.mkdir(parents=True, exist_ok=True)

    def _create_pyproject(self, target_dir: Path, config: SeedConfig) -> None:
        """Create pyproject.toml.

        Args:
            target_dir: Root directory for the project.
            config: Seeding configuration.
        """
        pkg_name = config.name.replace("-", "_")

        content = f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{config.name}"
version = "0.1.0"
description = "Seeded from truth_forge"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    "mypy>=1.0",
    "pytest>=8.0",
    "pytest-cov>=4.0",
    "ruff>=0.4",
]

[tool.hatch.build.targets.wheel]
packages = ["src/{pkg_name}"]

[tool.mypy]
strict = true
python_version = "3.12"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "RUF"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=src/{pkg_name} --cov-report=term-missing"
'''

        (target_dir / "pyproject.toml").write_text(content)

    def _create_modules(self, target_dir: Path, config: SeedConfig) -> None:
        """Create initial Python modules.

        Args:
            target_dir: Root directory for the project.
            config: Seeding configuration.
        """
        pkg_name = config.name.replace("-", "_")
        pkg_dir = target_dir / "src" / pkg_name

        # Create __init__.py
        init_content = f'''"""
{config.name} - Seeded from truth_forge.

LINEAGE:
- Parent: {config.parent_id}
- Seeded: {datetime.now(UTC).isoformat()}
"""

__version__ = "0.1.0"
'''
        (pkg_dir / "__init__.py").write_text(init_content)

        # Create conftest.py for tests
        conftest = '''"""Test configuration and fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Provide sample test data."""
    return {"key": "value"}
'''
        (target_dir / "tests" / "conftest.py").write_text(conftest)

    def _create_lineage(self, target_dir: Path, config: SeedConfig) -> Lineage:
        """Create lineage tracking file.

        Args:
            target_dir: Root directory for the project.
            config: Seeding configuration.

        Returns:
            Lineage information.
        """
        lineage = Lineage(
            organism_id=config.name,
            parent_id=config.parent_id,
            generation=1,  # First generation from truth_forge
            metadata={
                "template": config.template,
                "seeded_from": str(PROJECT_ROOT),
            },
        )

        # Write to .seed directory
        seed_dir = target_dir / ".seed"
        lineage_file = seed_dir / "lineage.json"
        lineage_file.write_text(json.dumps(lineage.to_dict(), indent=2))

        return lineage

    def _create_claude_md(self, target_dir: Path, config: SeedConfig) -> None:
        """Create CLAUDE.md for the project.

        Args:
            target_dir: Root directory for the project.
            config: Seeding configuration.
        """
        pkg_name = config.name.replace("-", "_")

        content = f"""# {config.name} - Agent Instructions

## Lineage

This project was seeded from truth_forge.

- **Parent**: {config.parent_id}
- **Seeded**: {datetime.now(UTC).strftime("%Y-%m-%d")}

## Code Quality Standards

```bash
# Quick quality check:
.venv/bin/mypy src/ --strict && \\
.venv/bin/ruff check src/ && \\
.venv/bin/ruff format --check src/
```

## The Pattern

```
HOLD1 (input) -> AGENT (process) -> HOLD2 (output)
```

## Key Locations

| Resource | Location |
|----------|----------|
| Source | src/{pkg_name}/ |
| Tests | tests/ |
| Config | config/ |
| Data | data/ |
"""

        (target_dir / "CLAUDE.md").write_text(content)

    def get_seeded_projects(self) -> list[Lineage]:
        """Get list of projects seeded by this instance.

        Returns:
            List of lineage information.
        """
        return self._seeded_projects.copy()


__all__ = [
    "ProjectSeeder",
    "SeedConfig",
]
