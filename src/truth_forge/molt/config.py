"""Molt Configuration Module.

Provides dataclasses for molt configuration, loaded from molt.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SourceMapping:
    """Mapping from source to destination for document molt."""

    name: str
    source: Path
    destination: Path
    archive: Path
    patterns: list[str] = field(default_factory=lambda: ["*.md", "**/*.md"])
    exclude: list[str] = field(default_factory=lambda: ["**/archive/**", "**/.git/**"])


@dataclass
class ArchiveSettings:
    """Settings for archive creation."""

    date_format: str = "%Y_%m_%d"
    index_file: str = "INDEX.md"
    preserve_structure: bool = True


@dataclass
class StubSettings:
    """Settings for stub file creation."""

    template: str = field(
        default_factory=lambda: """# {title}

> **MOVED**: This document has been molted to truth_forge.
>
> **New Location**: [{dest_name}]({dest_path})
>
> **Archive**: [{archive_name}]({archive_path})
>
> **Molted On**: {date}
"""
    )
    max_lines: int = 20


@dataclass
class VerificationSettings:
    """Settings for verification checks."""

    max_stub_lines: int = 20
    required_markers: list[str] = field(
        default_factory=lambda: [
            "**MOVED**",
            "**New Location**",
            "**Archive**",
            "**Molted On**",
        ]
    )


@dataclass
class TrackingSettings:
    """Settings for molt history tracking."""

    enabled: bool = True
    history_file: Path = field(default_factory=lambda: Path(".molt/history.jsonl"))


@dataclass
class MoltConfig:
    """Main configuration for molt operations."""

    organism_name: str
    organism_type: str
    sources: list[SourceMapping]
    archive_settings: ArchiveSettings = field(default_factory=ArchiveSettings)
    stub_settings: StubSettings = field(default_factory=StubSettings)
    verification_settings: VerificationSettings = field(default_factory=VerificationSettings)
    tracking_settings: TrackingSettings = field(default_factory=TrackingSettings)

    def validate(self) -> list[str]:
        """Validate the configuration.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        if not self.organism_name:
            errors.append("organism.name is required")

        if self.organism_type not in ("genesis", "offspring"):
            errors.append(
                f"organism.type must be 'genesis' or 'offspring', got '{self.organism_type}'"
            )

        if not self.sources:
            errors.append("At least one source mapping is required")

        return errors

    @classmethod
    def from_yaml(cls, config_path: Path) -> MoltConfig:
        """Load configuration from a YAML file.

        Args:
            config_path: Path to the molt.yaml file.

        Returns:
            MoltConfig instance.

        Raises:
            FileNotFoundError: If config file doesn't exist.
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path) as f:
            data = yaml.safe_load(f)

        # Parse organism settings
        organism = data.get("organism", {})
        organism_name = organism.get("name", "")
        organism_type = organism.get("type", "offspring")

        # Parse source mappings
        sources: list[SourceMapping] = []
        base_path = config_path.parent

        for src in data.get("sources", []):
            sources.append(
                SourceMapping(
                    name=src.get("name", ""),
                    source=base_path / src.get("source", ""),
                    destination=base_path / src.get("destination", ""),
                    archive=base_path / src.get("archive", "archive"),
                    patterns=src.get("patterns", ["*.md", "**/*.md"]),
                    exclude=src.get("exclude", ["**/archive/**", "**/.git/**"]),
                )
            )

        # Parse optional settings
        archive_data = data.get("archive", {})
        archive_settings = ArchiveSettings(
            date_format=archive_data.get("date_format", "%Y_%m_%d"),
            index_file=archive_data.get("index_file", "INDEX.md"),
            preserve_structure=archive_data.get("preserve_structure", True),
        )

        stub_data = data.get("stub", {})
        stub_settings = StubSettings(
            template=stub_data.get("template", StubSettings().template),
            max_lines=stub_data.get("max_lines", 20),
        )

        verification_data = data.get("verification", {})
        verification_settings = VerificationSettings(
            max_stub_lines=verification_data.get("max_stub_lines", 20),
            required_markers=verification_data.get(
                "required_markers",
                ["**MOVED**", "**New Location**", "**Archive**", "**Molted On**"],
            ),
        )

        tracking_data = data.get("tracking", {})
        tracking_settings = TrackingSettings(
            enabled=tracking_data.get("enabled", True),
            history_file=Path(tracking_data.get("history_file", ".molt/history.jsonl")),
        )

        return cls(
            organism_name=organism_name,
            organism_type=organism_type,
            sources=sources,
            archive_settings=archive_settings,
            stub_settings=stub_settings,
            verification_settings=verification_settings,
            tracking_settings=tracking_settings,
        )

    @classmethod
    def find_config(cls, start_path: Path) -> Path | None:
        """Find molt.yaml by searching up the directory tree.

        Args:
            start_path: Directory to start searching from.

        Returns:
            Path to molt.yaml if found, None otherwise.
        """
        current = start_path.resolve()

        while current != current.parent:
            config_path = current / "molt.yaml"
            if config_path.exists():
                return config_path
            current = current.parent

        return None
