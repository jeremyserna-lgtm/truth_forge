"""Tests for enrichment Dead Letter Queue."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from pipelines.enrichment.dlq import DeadLetterQueue


class TestDeadLetterQueue:
    """Tests for DeadLetterQueue."""

    def test_send_writes_jsonl(self) -> None:
        """Send writes one JSON line per record."""
        with TemporaryDirectory() as tmp:
            dlq = DeadLetterQueue(Path(tmp), "test_pipeline")
            dlq.send(
                {"entity_id": "e1", "text_preview": "abc"},
                ValueError("test error"),
                "stage_a",
                attempt_count=1,
            )
            assert dlq.count() == 1
            lines = Path(dlq._dlq_file).read_text().strip().split("\n")
            assert len(lines) == 1
            rec = json.loads(lines[0])
            assert rec["record_id"] == "e1"
            assert rec["error_type"] == "ValueError"
            assert rec["pipeline_stage"] == "stage_a"

    def test_count_empty(self) -> None:
        """Count is 0 when no records sent."""
        with TemporaryDirectory() as tmp:
            dlq = DeadLetterQueue(Path(tmp), "other")
            assert dlq.count() == 0

    def test_send_multiple(self) -> None:
        """Multiple sends append lines."""
        with TemporaryDirectory() as tmp:
            dlq = DeadLetterQueue(Path(tmp), "multi")
            dlq.send({"id": "1"}, ValueError("e1"), "s1")
            dlq.send({"id": "2"}, RuntimeError("e2"), "s2")
            assert dlq.count() == 2
