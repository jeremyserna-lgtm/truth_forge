"""Universal Dead Letter Queue (DLQ) for failed records.

This module ensures NO RECORDS ARE EVER SILENTLY LOST.

Per DATA PROTECTION LAWS:
- Every failed record must be captured with full context
- Failed records can be replayed after fixing issues
- No silent failures allowed

Usage:
    from pipelines.core.dlq import DLQ, DLQEntry

    dlq = DLQ("stage_5")

    # Send failed record to DLQ
    dlq.send(
        record=failed_record,
        error_type="VALIDATION_ERROR",
        error_message="Level out of range",
        stage="stage_5",
    )

    # List failed records
    entries = dlq.list_entries()

    # Replay failed records
    for entry in entries:
        try:
            process(entry.record)
            dlq.mark_resolved(entry.dlq_id)
        except Exception as e:
            dlq.mark_retry(entry.dlq_id)

Author: Claude (Opus 4.5)
Date: 2026-02-02
"""
from __future__ import annotations

import json
import logging
import os
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator


logger = logging.getLogger(__name__)


# Default DLQ directory
DEFAULT_DLQ_DIR = Path.home() / ".truth_engine" / "dlq"


@dataclass
class DLQEntry:
    """A single entry in the Dead Letter Queue."""

    dlq_id: str
    record_id: str | None
    record: dict[str, Any] | None
    error_type: str
    error_message: str
    stage: str
    timestamp: str
    attempt_count: int = 1
    traceback: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, retrying, resolved, dead

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "dlq_id": self.dlq_id,
            "record_id": self.record_id,
            "record": self.record,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "stage": self.stage,
            "timestamp": self.timestamp,
            "attempt_count": self.attempt_count,
            "traceback": self.traceback,
            "metadata": self.metadata,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DLQEntry":
        """Create from dictionary."""
        return cls(
            dlq_id=data["dlq_id"],
            record_id=data.get("record_id"),
            record=data.get("record"),
            error_type=data["error_type"],
            error_message=data["error_message"],
            stage=data["stage"],
            timestamp=data["timestamp"],
            attempt_count=data.get("attempt_count", 1),
            traceback=data.get("traceback"),
            metadata=data.get("metadata", {}),
            status=data.get("status", "pending"),
        )


class DLQ:
    """Dead Letter Queue for failed records.

    Stores failed records to JSONL files for later inspection and replay.
    Each stage gets its own DLQ file.
    """

    MAX_RETRIES = 3

    def __init__(
        self,
        stage_name: str,
        dlq_dir: Path | None = None,
    ) -> None:
        """Initialize DLQ.

        Args:
            stage_name: Name of the stage (used for file naming)
            dlq_dir: Directory for DLQ files (default: ~/.truth_engine/dlq)
        """
        self.stage_name = stage_name
        self.dlq_dir = dlq_dir or DEFAULT_DLQ_DIR
        self.dlq_dir.mkdir(parents=True, exist_ok=True)

        # DLQ file path
        self.dlq_file = self.dlq_dir / f"{stage_name}_dlq.jsonl"

        # Index for quick lookup (loaded lazily)
        self._index: dict[str, int] | None = None

    def send(
        self,
        *,
        record: dict[str, Any] | None = None,
        record_id: str | None = None,
        error_type: str,
        error_message: str,
        stage: str | None = None,
        include_traceback: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Send a failed record to DLQ.

        Args:
            record: The failed record (optional if record_id provided)
            record_id: ID of the failed record
            error_type: Type of error (e.g., "VALIDATION_ERROR")
            error_message: Human-readable error message
            stage: Stage name (defaults to self.stage_name)
            include_traceback: Whether to include current traceback
            metadata: Additional metadata

        Returns:
            DLQ entry ID
        """
        dlq_id = str(uuid.uuid4())
        timestamp = datetime.now(UTC).isoformat()

        # Get traceback if requested
        tb = traceback.format_exc() if include_traceback else None

        entry = DLQEntry(
            dlq_id=dlq_id,
            record_id=record_id or (record.get("entity_id") if record else None),
            record=record,
            error_type=error_type,
            error_message=error_message,
            stage=stage or self.stage_name,
            timestamp=timestamp,
            traceback=tb,
            metadata=metadata or {},
            status="pending",
        )

        # Append to DLQ file
        with open(self.dlq_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

        # Invalidate index
        self._index = None

        logger.warning(
            "record_sent_to_dlq",
            extra={
                "dlq_id": dlq_id,
                "record_id": entry.record_id,
                "error_type": error_type,
                "stage": self.stage_name,
            },
        )

        return dlq_id

    def list_entries(
        self,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[DLQEntry]:
        """List DLQ entries.

        Args:
            status: Filter by status (pending, retrying, resolved, dead)
            limit: Maximum entries to return

        Returns:
            List of DLQ entries
        """
        if not self.dlq_file.exists():
            return []

        entries = []
        with open(self.dlq_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = DLQEntry.from_dict(json.loads(line))
                    if status is None or entry.status == status:
                        entries.append(entry)
                        if limit and len(entries) >= limit:
                            break

        return entries

    def iter_entries(self, status: str | None = None) -> Iterator[DLQEntry]:
        """Iterate over DLQ entries.

        Args:
            status: Filter by status

        Yields:
            DLQ entries
        """
        if not self.dlq_file.exists():
            return

        with open(self.dlq_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry = DLQEntry.from_dict(json.loads(line))
                    if status is None or entry.status == status:
                        yield entry

    def get_entry(self, dlq_id: str) -> DLQEntry | None:
        """Get a specific DLQ entry by ID.

        Args:
            dlq_id: DLQ entry ID

        Returns:
            DLQ entry or None if not found
        """
        for entry in self.iter_entries():
            if entry.dlq_id == dlq_id:
                return entry
        return None

    def mark_resolved(self, dlq_id: str) -> bool:
        """Mark a DLQ entry as resolved.

        Args:
            dlq_id: DLQ entry ID

        Returns:
            True if entry was found and updated
        """
        return self._update_status(dlq_id, "resolved")

    def mark_retry(self, dlq_id: str) -> bool:
        """Mark a DLQ entry for retry.

        If max retries exceeded, marks as dead instead.

        Args:
            dlq_id: DLQ entry ID

        Returns:
            True if entry was found and updated
        """
        entry = self.get_entry(dlq_id)
        if entry is None:
            return False

        if entry.attempt_count >= self.MAX_RETRIES:
            logger.error(
                "dlq_entry_max_retries_exceeded",
                extra={
                    "dlq_id": dlq_id,
                    "attempt_count": entry.attempt_count,
                },
            )
            return self._update_status(dlq_id, "dead", increment_attempt=True)

        return self._update_status(dlq_id, "retrying", increment_attempt=True)

    def _update_status(
        self,
        dlq_id: str,
        new_status: str,
        increment_attempt: bool = False,
    ) -> bool:
        """Update status of a DLQ entry.

        Rewrites the file with updated entry.
        """
        if not self.dlq_file.exists():
            return False

        entries = []
        found = False
        with open(self.dlq_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_dict = json.loads(line)
                    if entry_dict.get("dlq_id") == dlq_id:
                        entry_dict["status"] = new_status
                        if increment_attempt:
                            entry_dict["attempt_count"] = entry_dict.get("attempt_count", 1) + 1
                        found = True
                    entries.append(entry_dict)

        if not found:
            return False

        # Rewrite file
        with open(self.dlq_file, "w", encoding="utf-8") as f:
            for entry_dict in entries:
                f.write(json.dumps(entry_dict) + "\n")

        logger.info(
            "dlq_entry_status_updated",
            extra={
                "dlq_id": dlq_id,
                "new_status": new_status,
            },
        )

        return True

    def count(self, status: str | None = None) -> int:
        """Count DLQ entries.

        Args:
            status: Filter by status

        Returns:
            Number of entries
        """
        count = 0
        for _ in self.iter_entries(status):
            count += 1
        return count

    def clear_resolved(self) -> int:
        """Remove all resolved entries from DLQ.

        Returns:
            Number of entries removed
        """
        if not self.dlq_file.exists():
            return 0

        entries = []
        removed = 0
        with open(self.dlq_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    entry_dict = json.loads(line)
                    if entry_dict.get("status") == "resolved":
                        removed += 1
                    else:
                        entries.append(entry_dict)

        # Rewrite file
        with open(self.dlq_file, "w", encoding="utf-8") as f:
            for entry_dict in entries:
                f.write(json.dumps(entry_dict) + "\n")

        logger.info(
            "dlq_resolved_entries_cleared",
            extra={
                "stage": self.stage_name,
                "removed_count": removed,
            },
        )

        return removed


class DLQReplay:
    """Utility for replaying DLQ entries.

    Usage:
        replay = DLQReplay(dlq)
        results = replay.replay_all(processor_function)
    """

    def __init__(self, dlq: DLQ) -> None:
        """Initialize replayer.

        Args:
            dlq: DLQ instance to replay from
        """
        self.dlq = dlq

    def replay_all(
        self,
        processor: Any,
        status: str = "pending",
    ) -> dict[str, int]:
        """Replay all pending DLQ entries through processor.

        Args:
            processor: Function or object with process() method
            status: Status of entries to replay

        Returns:
            Dict with success/failure counts
        """
        results = {"success": 0, "failed": 0, "skipped": 0}

        for entry in self.dlq.iter_entries(status):
            if entry.record is None:
                results["skipped"] += 1
                continue

            try:
                if hasattr(processor, "process"):
                    processor.process(entry.record)
                else:
                    processor(entry.record)

                self.dlq.mark_resolved(entry.dlq_id)
                results["success"] += 1

            except Exception as e:
                logger.warning(
                    "dlq_replay_failed",
                    extra={
                        "dlq_id": entry.dlq_id,
                        "error": str(e),
                    },
                )
                self.dlq.mark_retry(entry.dlq_id)
                results["failed"] += 1

        logger.info(
            "dlq_replay_complete",
            extra={
                "stage": self.dlq.stage_name,
                **results,
            },
        )

        return results
