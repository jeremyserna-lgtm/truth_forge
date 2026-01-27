"""Molt Tracking Module.

Provides history tracking for molt operations.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from truth_forge.molt.engine import MoltResult  # noqa: TC001


@dataclass
class MoltRecord:
    """Record of a single molt operation."""

    timestamp: str
    source_name: str
    source_path: str
    destination_path: str
    archive_path: str
    files_found: int = 0
    files_migrated: int = 0
    files_archived: int = 0
    stubs_created: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    dry_run: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert record to dictionary.

        Returns:
            Dictionary representation.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MoltRecord:
        """Create record from dictionary.

        Args:
            data: Dictionary representation.

        Returns:
            MoltRecord instance.
        """
        return cls(
            timestamp=data["timestamp"],
            source_name=data["source_name"],
            source_path=data["source_path"],
            destination_path=data["destination_path"],
            archive_path=data["archive_path"],
            files_found=data.get("files_found", 0),
            files_migrated=data.get("files_migrated", 0),
            files_archived=data.get("files_archived", 0),
            stubs_created=data.get("stubs_created", 0),
            skipped=data.get("skipped", 0),
            errors=data.get("errors", []),
            dry_run=data.get("dry_run", False),
        )


class MoltTracker:
    """Tracker for molt operation history."""

    def __init__(self, history_file: Path) -> None:
        """Initialize the tracker.

        Args:
            history_file: Path to the history JSONL file.
        """
        self.history_file = history_file

    def record(
        self,
        result: MoltResult,
        source_path: Path,
        destination_path: Path,
        archive_path: Path,
        dry_run: bool = False,
    ) -> MoltRecord:
        """Record a molt operation.

        Args:
            result: Result of the molt operation.
            source_path: Source directory path.
            destination_path: Destination directory path.
            archive_path: Archive directory path.
            dry_run: Whether this was a dry run.

        Returns:
            The recorded MoltRecord.
        """
        record = MoltRecord(
            timestamp=datetime.now(UTC).isoformat(),
            source_name=result.source_name,
            source_path=str(source_path),
            destination_path=str(destination_path),
            archive_path=str(archive_path),
            files_found=result.files_found,
            files_migrated=result.files_migrated,
            files_archived=result.files_archived,
            stubs_created=result.stubs_created,
            skipped=result.skipped,
            errors=result.errors,
            dry_run=dry_run,
        )

        self._append_record(record)
        return record

    def get_history(self) -> list[MoltRecord]:
        """Get all molt history records.

        Returns:
            List of all recorded operations.
        """
        if not self.history_file.exists():
            return []

        records: list[MoltRecord] = []
        with open(self.history_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    records.append(MoltRecord.from_dict(data))

        return records

    def get_source_history(self, source_name: str) -> list[MoltRecord]:
        """Get history for a specific source.

        Args:
            source_name: Name of the source.

        Returns:
            List of records for the specified source.
        """
        return [r for r in self.get_history() if r.source_name == source_name]

    def get_summary(self) -> dict[str, Any]:
        """Get summary statistics across all operations.

        Returns:
            Dictionary with summary statistics.
        """
        history = self.get_history()

        total_operations = len(history)
        executed = [r for r in history if not r.dry_run]
        dry_runs = [r for r in history if r.dry_run]

        # Only count stats from executed operations (not dry runs)
        total_files_archived = sum(r.files_archived for r in executed)
        total_stubs_created = sum(r.stubs_created for r in executed)
        total_errors = sum(len(r.errors) for r in executed)

        return {
            "total_operations": total_operations,
            "executed_operations": len(executed),
            "dry_runs": len(dry_runs),
            "total_files_archived": total_files_archived,
            "total_stubs_created": total_stubs_created,
            "total_errors": total_errors,
        }

    def _append_record(self, record: MoltRecord) -> None:
        """Append a record to the history file.

        Args:
            record: Record to append.
        """
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.history_file, "a") as f:
            f.write(json.dumps(record.to_dict()) + "\n")
