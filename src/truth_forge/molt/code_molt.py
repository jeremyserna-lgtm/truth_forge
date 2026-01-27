"""Code Molt Module.

Provides code transformation capabilities for migrating legacy code.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TransformRule:
    """A single transformation rule."""

    pattern: str
    replacement: str
    is_regex: bool = False

    def apply(self, content: str) -> tuple[str, int]:
        """Apply the transformation to content.

        Args:
            content: Source content to transform.

        Returns:
            Tuple of (transformed content, number of replacements).
        """
        if self.is_regex:
            result, count = re.subn(self.pattern, self.replacement, content)
            return result, count
        else:
            count = content.count(self.pattern)
            result = content.replace(self.pattern, self.replacement)
            return result, count


@dataclass
class TransformConfig:
    """Configuration for code transformations."""

    import_rules: list[TransformRule] = field(default_factory=list)
    path_rules: list[TransformRule] = field(default_factory=list)
    env_rules: list[TransformRule] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TransformConfig:
        """Create config from dictionary (e.g., from molt.yaml).

        Args:
            data: Dictionary with import/path/env rules.

        Returns:
            TransformConfig instance.
        """
        import_rules: list[TransformRule] = []
        path_rules: list[TransformRule] = []
        env_rules: list[TransformRule] = []

        for rule in data.get("imports", []):
            import_rules.append(
                TransformRule(
                    pattern=rule["from"],
                    replacement=rule["to"],
                    is_regex=rule.get("regex", False),
                )
            )

        for rule in data.get("paths", []):
            path_rules.append(
                TransformRule(
                    pattern=rule["from"],
                    replacement=rule["to"],
                    is_regex=rule.get("regex", False),
                )
            )

        for rule in data.get("env", []):
            env_rules.append(
                TransformRule(
                    pattern=rule["from"],
                    replacement=rule["to"],
                    is_regex=rule.get("regex", False),
                )
            )

        return cls(
            import_rules=import_rules,
            path_rules=path_rules,
            env_rules=env_rules,
        )

    @classmethod
    def default(cls) -> TransformConfig:
        """Get default transformation configuration.

        Returns:
            TransformConfig with standard transformation rules.
        """
        return cls(
            import_rules=[
                TransformRule(
                    pattern=r"from Primitive\.(\w+)",
                    replacement=r"from truth_forge.\1",
                    is_regex=True,
                ),
                TransformRule(
                    pattern=r"from central_services\.(\w+)",
                    replacement=r"from truth_forge.services.\1",
                    is_regex=True,
                ),
                TransformRule(
                    pattern=r"from src\.services\.(\w+)",
                    replacement=r"from truth_forge.services.\1",
                    is_regex=True,
                ),
            ],
            path_rules=[
                TransformRule(
                    pattern="/Users/jeremyserna/Truth_Engine",
                    replacement="PROJECT_ROOT",
                ),
                TransformRule(
                    pattern='Path.home() / "Truth_Engine"',
                    replacement="PROJECT_ROOT",
                ),
            ],
            env_rules=[
                TransformRule(
                    pattern="os.environ['GCP_PROJECT']",
                    replacement="settings.gcp_project",
                ),
            ],
        )


@dataclass
class CodeMoltResult:
    """Result of a code molt operation."""

    source_name: str
    files_found: int = 0
    files_transformed: int = 0
    files_unchanged: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if the operation was successful.

        Returns:
            True if no errors occurred.
        """
        return len(self.errors) == 0


class CodeMoltEngine:
    """Engine for code transformation operations."""

    def __init__(self, config: TransformConfig | None = None) -> None:
        """Initialize the code molt engine.

        Args:
            config: Transformation configuration. Uses default if not provided.
        """
        self.config = config or TransformConfig.default()

    def transform_content(self, content: str) -> tuple[str, dict[str, int]]:
        """Transform content using configured rules.

        Args:
            content: Source content to transform.

        Returns:
            Tuple of (transformed content, counts by category).
        """
        counts: dict[str, int] = {"imports": 0, "paths": 0, "env": 0}

        # Apply import rules
        for rule in self.config.import_rules:
            content, count = rule.apply(content)
            counts["imports"] += count

        # Apply path rules
        for rule in self.config.path_rules:
            content, count = rule.apply(content)
            counts["paths"] += count

        # Apply env rules
        for rule in self.config.env_rules:
            content, count = rule.apply(content)
            counts["env"] += count

        return content, counts

    def transform_file(
        self,
        source_file: Path,
        dest_file: Path,
        archive_dir: Path | None = None,
        dry_run: bool = True,
    ) -> tuple[bool, dict[str, int]]:
        """Transform a single file.

        Args:
            source_file: Source file to transform.
            dest_file: Destination file path.
            archive_dir: Optional archive directory for original.
            dry_run: If True, only simulate the transformation.

        Returns:
            Tuple of (was_changed, transformation_counts).
        """
        content = source_file.read_text()
        transformed, counts = self.transform_content(content)

        was_changed = transformed != content

        if was_changed and not dry_run:
            # Archive original if requested
            if archive_dir:
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_file = archive_dir / source_file.name
                shutil.copy2(source_file, archive_file)

            # Write transformed content
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(transformed)

        return was_changed, counts

    def molt_directory(
        self,
        source_dir: Path,
        dest_dir: Path,
        archive_dir: Path | None = None,
        dry_run: bool = True,
        patterns: list[str] | None = None,
    ) -> CodeMoltResult:
        """Transform all Python files in a directory.

        Args:
            source_dir: Source directory.
            dest_dir: Destination directory.
            archive_dir: Optional archive directory.
            dry_run: If True, only simulate.
            patterns: File patterns to match (default: *.py).

        Returns:
            Result of the operation.
        """
        result = CodeMoltResult(source_name=source_dir.name)

        if not source_dir.exists():
            result.errors.append(f"Source directory does not exist: {source_dir}")
            return result

        patterns = patterns or ["**/*.py"]

        for pattern in patterns:
            for source_file in source_dir.glob(pattern):
                if source_file.is_file():
                    result.files_found += 1

                    try:
                        rel_path = source_file.relative_to(source_dir)
                        dest_file = dest_dir / rel_path

                        changed, _ = self.transform_file(
                            source_file=source_file,
                            dest_file=dest_file,
                            archive_dir=archive_dir,
                            dry_run=dry_run,
                        )

                        if changed:
                            result.files_transformed += 1
                        else:
                            result.files_unchanged += 1

                    except Exception as e:
                        result.errors.append(f"Error processing {source_file}: {e}")

        return result

    def molt_phase(
        self,
        phase_config: dict[str, Any],
        base_path: Path,
        dry_run: bool = True,
    ) -> CodeMoltResult:
        """Transform files according to a phase configuration.

        Args:
            phase_config: Phase configuration from molt.yaml.
            base_path: Base path for resolving relative paths.
            dry_run: If True, only simulate.

        Returns:
            Result of the operation.
        """
        phase_name = phase_config.get("name", "unknown")
        result = CodeMoltResult(source_name=f"phase_{phase_name}")

        for source_spec in phase_config.get("sources", []):
            source_path = base_path / source_spec["source"]
            dest_path = base_path / source_spec["destination"]

            if source_path.is_dir():
                dir_result = self.molt_directory(
                    source_dir=source_path,
                    dest_dir=dest_path,
                    dry_run=dry_run,
                )
                result.files_found += dir_result.files_found
                result.files_transformed += dir_result.files_transformed
                result.files_unchanged += dir_result.files_unchanged
                result.errors.extend(dir_result.errors)

            elif source_path.is_file():
                result.files_found += 1
                try:
                    changed, _ = self.transform_file(
                        source_file=source_path,
                        dest_file=dest_path,
                        dry_run=dry_run,
                    )
                    if changed:
                        result.files_transformed += 1
                    else:
                        result.files_unchanged += 1
                except Exception as e:
                    result.errors.append(f"Error processing {source_path}: {e}")

            else:
                result.errors.append(f"Source not found: {source_path}")

        return result
