"""Stage 1: Extraction - Parse raw JSONL into structured rows.

PATTERN: HOLD1 (raw JSONL) → AGENT (parsing) → HOLD2 (structured JSONL)

Reads raw Claude Code session files and extracts core fields into a
standardized format. Malformed records are routed to DLQ.

Usage:
    stage = ExtractionStage(config)
    result = stage.run()
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pipelines.core.stage import Stage


logger = logging.getLogger(__name__)


class ExtractionStage(Stage):
    """Stage 1: Extract and parse raw JSONL data."""

    STAGE_TYPE = "extraction"

    def __init__(self, config: Any) -> None:
        """Initialize extraction stage.
        
        Args:
            config: Stage configuration.
        """
        super().__init__(config)
        self.dlq_path = Path("dlq/claude_code_stage_1_dlq.jsonl")
        self.dlq_path.parent.mkdir(parents=True, exist_ok=True)
        self.dlq_count = 0

    def read_input(self) -> list[dict[str, Any]]:
        """Read all JSONL files from source directory.
        
        Returns:
            List of raw message records.
        """
        source_path = self.config.extra.get("source_path", "~/.claude-code/sessions")
        source_dir = Path(source_path).expanduser()
        
        if not source_dir.exists():
            logger.warning(f"Source directory does not exist: {source_dir}")
            return []
        
        records = []
        for jsonl_file in source_dir.glob("*.jsonl"):
            logger.info(f"Reading: {jsonl_file.name}")
            
            try:
                with open(jsonl_file, encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        try:
                            record = json.loads(line)
                            record["_source_file"] = str(jsonl_file)
                            record["_source_line"] = line_num
                            records.append(record)
                        except json.JSONDecodeError as e:
                            self._send_to_dlq({
                                "error": "json_decode_error",
                                "message": str(e),
                                "source_file": str(jsonl_file),
                                "line_num": line_num,
                                "raw_line": line[:200],  # First 200 chars
                            })
            except Exception as e:
                logger.error(f"Error reading {jsonl_file}: {e}")
        
        logger.info(f"Loaded {len(records)} records from {source_dir}")
        return records

    def transform(self, record: dict[str, Any]) -> dict[str, Any] | None:
        """Extract core fields from raw record.
        
        Args:
            record: Raw message record.
            
        Returns:
            Structured record with core fields, or None if invalid.
        """
        # Validate required fields
        required_fields = ["session_id", "message_index", "text", "role"]
        missing_fields = [f for f in required_fields if f not in record]
        
        if missing_fields:
            self._send_to_dlq({
                "error": "missing_required_fields",
                "missing_fields": missing_fields,
                "record": record,
            })
            return None
        
        # Extract core fields
        try:
            extracted = {
                "session_id": str(record["session_id"]),
                "message_index": int(record["message_index"]),
                "text": str(record["text"]),
                "role": str(record["role"]),
                "message_type": record.get("message_type", "message"),
                "source_file": record.get("_source_file"),
                "timestamp_utc": record.get("timestamp_utc"),
                "content_date": record.get("content_date"),
                # Preserve additional fields in metadata
                "raw_metadata": {
                    k: v for k, v in record.items()
                    if k not in required_fields 
                    and not k.startswith("_")
                    and k not in ["message_type", "timestamp_utc", "content_date"]
                },
            }
            
            return extracted
        
        except (ValueError, TypeError) as e:
            self._send_to_dlq({
                "error": "field_type_error",
                "message": str(e),
                "record": record,
            })
            return None

    def _send_to_dlq(self, error_record: dict[str, Any]) -> None:
        """Send malformed record to dead letter queue.
        
        Args:
            error_record: Error details and record.
        """
        with open(self.dlq_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(error_record) + "\n")
        self.dlq_count += 1

    def write_output(self, records: list[dict[str, Any]]) -> int:
        """Write extracted records to output file.
        
        Args:
            records: Extracted records.
            
        Returns:
            Number of records written.
        """
        count = super().write_output(records)
        
        if self.dlq_count > 0:
            logger.warning(f"Sent {self.dlq_count} records to DLQ: {self.dlq_path}")
        
        return count


__all__ = ["ExtractionStage"]
