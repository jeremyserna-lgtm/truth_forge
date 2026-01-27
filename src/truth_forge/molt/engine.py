"""Molt Engine Module.

The core engine for document molt operations.
"""

from __future__ import annotations

import fnmatch
import shutil
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from truth_forge.molt.config import MoltConfig, SourceMapping  # noqa: TC001


@dataclass
class MoltResult:
    """Result of a molt operation."""

    source_name: str
    files_found: int = 0
    files_migrated: int = 0
    files_archived: int = 0
    stubs_created: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Check if the molt operation was successful.

        Returns:
            True if no errors and all migrated files were archived.
        """
        if self.errors:
            return False
        # Success if files_archived matches files_migrated
        return self.files_archived == self.files_migrated


class MoltEngine:
    """Engine for document molt operations."""

    def __init__(self, config: MoltConfig) -> None:
        """Initialize the molt engine.

        Args:
            config: Molt configuration.
        """
        self.config = config

    def molt_source(self, source: SourceMapping, dry_run: bool = True) -> MoltResult:
        """Molt a single source.

        Args:
            source: Source mapping to molt.
            dry_run: If True, only simulate the molt.

        Returns:
            Result of the molt operation.
        """
        result = MoltResult(source_name=source.name)

        # Validate source exists
        if not source.source.exists():
            result.errors.append(f"Source directory does not exist: {source.source}")
            return result

        # Find all matching files
        files = self._find_files(source)
        result.files_found = len(files)

        for file_path in files:
            try:
                self._process_file(file_path, source, result, dry_run)
            except Exception as e:
                result.errors.append(f"Error processing {file_path}: {e}")

        return result

    def molt_all(self, dry_run: bool = True) -> dict[str, MoltResult]:
        """Molt all configured sources.

        Args:
            dry_run: If True, only simulate the molt.

        Returns:
            Dictionary mapping source names to results.
        """
        results: dict[str, MoltResult] = {}

        for source in self.config.sources:
            results[source.name] = self.molt_source(source, dry_run)

        return results

    def update_archive_index(self, archive_dir: Path, result: MoltResult) -> None:
        """Update or create the archive index file.

        Args:
            archive_dir: Archive batch directory (e.g., archive/molt_2026_01_26/).
            result: Result of the molt operation.
        """
        index_path = archive_dir.parent / self.config.archive_settings.index_file
        timestamp = datetime.now(UTC).isoformat()

        # Read existing index or create new
        if index_path.exists():
            content = index_path.read_text()
        else:
            content = "# Archive Index\n\nMolt archive history.\n\n| Date | Source | Files |\n|------|--------|-------|\n"

        # Append new entry
        entry = f"| {timestamp} | {result.source_name} | {result.files_archived} |\n"

        # Insert before the last line if there's content, or append
        lines = content.rstrip().split("\n")
        lines.append(entry.rstrip())

        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text("\n".join(lines) + "\n")

    def _find_files(self, source: SourceMapping) -> list[Path]:
        """Find all files matching the source patterns.

        Args:
            source: Source mapping.

        Returns:
            List of matching file paths.
        """
        files: list[Path] = []

        for pattern in source.patterns:
            for file_path in source.source.glob(pattern):
                if file_path.is_file() and not self._is_excluded(file_path, source):
                    files.append(file_path)

        return sorted(set(files))

    def _is_excluded(self, file_path: Path, source: SourceMapping) -> bool:
        """Check if a file should be excluded.

        Args:
            file_path: Path to check.
            source: Source mapping with exclude patterns.

        Returns:
            True if file should be excluded.
        """
        rel_path = str(file_path.relative_to(source.source))
        return any(fnmatch.fnmatch(rel_path, pattern) for pattern in source.exclude)

    def _is_stub(self, file_path: Path) -> bool:
        """Check if a file is already a stub.

        Args:
            file_path: Path to check.

        Returns:
            True if file appears to be a stub.
        """
        try:
            content = file_path.read_text()
            lines = content.split("\n")

            # Check for stub markers
            if len(lines) <= self.config.stub_settings.max_lines:
                for marker in self.config.verification_settings.required_markers:
                    if marker in content:
                        return True

            return False
        except Exception:
            return False

    def _process_file(
        self,
        file_path: Path,
        source: SourceMapping,
        result: MoltResult,
        dry_run: bool,
    ) -> None:
        """Process a single file for molt.

        Args:
            file_path: Path to the file.
            source: Source mapping.
            result: Result object to update.
            dry_run: If True, only simulate.
        """
        # Check if already a stub
        if self._is_stub(file_path):
            result.skipped += 1
            return

        # Calculate destination path
        rel_path = file_path.relative_to(source.source)
        dest_path = source.destination / rel_path

        # Check if destination exists (file has been migrated)
        if not dest_path.exists():
            result.skipped += 1
            return

        result.files_migrated += 1

        if dry_run:
            return

        # Create archive batch directory
        date_str = datetime.now(UTC).strftime(self.config.archive_settings.date_format)
        archive_batch = source.archive / f"molt_{date_str}"

        # Preserve structure in archive if configured
        if self.config.archive_settings.preserve_structure:
            archive_path = archive_batch / rel_path
        else:
            archive_path = archive_batch / file_path.name

        archive_path.parent.mkdir(parents=True, exist_ok=True)

        # Archive original
        shutil.copy2(file_path, archive_path)
        result.files_archived += 1

        # Create stub
        stub_content = self._create_stub(file_path, dest_path, archive_path)
        file_path.write_text(stub_content)
        result.stubs_created += 1

        # Update archive index
        self.update_archive_index(archive_batch, result)

    def _create_stub(self, source_path: Path, dest_path: Path, archive_path: Path) -> str:
        """Create a stub file content.

        Args:
            source_path: Original source file path.
            dest_path: Destination file path.
            archive_path: Archive file path.

        Returns:
            Stub file content.
        """
        title = source_path.stem.replace("_", " ").title()
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")

        # Calculate relative paths
        try:
            dest_rel = dest_path.relative_to(source_path.parent)
        except ValueError:
            dest_rel = dest_path

        try:
            archive_rel = archive_path.relative_to(source_path.parent)
        except ValueError:
            archive_rel = archive_path

        return self.config.stub_settings.template.format(
            title=title,
            dest_name=dest_path.name,
            dest_path=str(dest_rel),
            archive_name=archive_path.name,
            archive_path=str(archive_rel),
            date=date_str,
        )
