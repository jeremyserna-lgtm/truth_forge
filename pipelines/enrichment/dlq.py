"""Dead Letter Queue for enrichment pipeline.

THE PATTERN:
- HOLD₁: Failed records
- AGENT: DLQ (quarantine, never drop)
- HOLD₂: Recoverable failure log

Per framework/standards/error_handling: never lose data in batch processing.
"""

from __future__ import annotations

import json
import logging
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)


class DeadLetterQueue:
    """Quarantine for failed enrichment records. Never lose data."""

    def __init__(self, dlq_path: Path | str, pipeline_name: str) -> None:
        """Initialize DLQ.

        Args:
            dlq_path: Directory or path prefix for DLQ file.
            pipeline_name: Pipeline/stage name for context.
        """
        self._path = Path(dlq_path)
        self._pipeline_name = pipeline_name
        self._dlq_file = self._path / f"{pipeline_name}_dlq.jsonl"
        self._dlq_file.parent.mkdir(parents=True, exist_ok=True)

    def send(
        self,
        record: dict[str, Any],
        error: BaseException,
        stage: str,
        attempt_count: int = 1,
    ) -> None:
        """Send a failed record to the DLQ.

        Args:
            record: Original record that failed.
            error: Exception raised during processing.
            stage: Pipeline stage name for context.
            attempt_count: Number of processing attempts.
        """
        now = datetime.now(UTC).isoformat()
        dlq_record: dict[str, Any] = {
            "original_record": record,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "pipeline_stage": stage,
            "attempt_count": attempt_count,
            "first_failure": now,
            "last_failure": now,
            "record_id": record.get("entity_id") or record.get("id"),
            "dlq_timestamp": now,
        }
        try:
            with open(self._dlq_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(dlq_record, default=str) + "\n")
            logger.warning(
                "dlq_send",
                extra={
                    "record_id": dlq_record.get("record_id"),
                    "stage": stage,
                    "error_type": type(error).__name__,
                    "dlq_file": str(self._dlq_file),
                },
            )
        except OSError as e:
            logger.error(
                "dlq_write_failed",
                extra={
                    "record_id": dlq_record.get("record_id"),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            raise

    def count(self) -> int:
        """Count records in DLQ.

        Returns:
            Number of lines (records) in the DLQ file.
        """
        if not self._dlq_file.exists():
            return 0
        with open(self._dlq_file, encoding="utf-8") as f:
            return sum(1 for _ in f)
