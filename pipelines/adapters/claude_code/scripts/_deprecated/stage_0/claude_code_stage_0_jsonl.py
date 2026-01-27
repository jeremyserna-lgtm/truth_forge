#!/usr/bin/env python3
"""
Stage 0: Message Extraction from JSONL Files - Claude Code/Codex/Github Pipeline

HOLD₁ (JSONL source files) → AGENT (Message Extractor) → HOLD₂ (BigQuery claude_code_stage_0)

Extracts messages from raw JSONL export files for Claude Code, Codex, and Github sources.
Saves extracted messages to BigQuery for downstream processing.

NOTE: entity_unified is the FINAL DESTINATION (written by final stage), not the source.
This pipeline processes raw source files and writes to entity_unified at the end.
"""
from __future__ import annotations

try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts._deprecated.stage_0.claude_code_stage_0_jsonl.py"

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse

from google.cloud import bigquery

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import (
    get_correlation_ids,
    get_current_run_id,
    get_logger,
)
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import (
    get_unified_governance,
    require_diagnostic_on_error,
)

logger = get_logger(__name__)

# Configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_0"
ENTITY_UNIFIED_TABLE = f"{PROJECT_ID}.{DATASET_ID}.entity_unified"  # Final destination

# Default source file directories
DEFAULT_SOURCE_DIRS = {
    "claude_code": Path.home() / "Truth_Engine" / "data" / "raw" / "claude_code",
    "codex": Path.home() / "Truth_Engine" / "data" / "raw" / "codex",
    "github": Path.home() / "Truth_Engine" / "data" / "raw" / "github",
}

def extract_messages_from_jsonl(
    source_dir: Path,
    source_name: str,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Extract messages from JSONL files in source directory.

    Args:
        source_dir: Directory containing JSONL files
        source_name: Source identifier (claude_code, codex, github)
        limit: Optional limit on number of messages

    Returns:
        List of message records
    """
    messages = []

    if not source_dir.exists():
        logger.warning(f"Source directory does not exist: {source_dir}")
        return messages

    # Find all JSONL files
    jsonl_files = list(source_dir.glob("*.jsonl"))
    if not jsonl_files:
        logger.warning(f"No JSONL files found in {source_dir}")
        return messages

    logger.info(f"Found {len(jsonl_files)} JSONL files in {source_dir}")

    for jsonl_file in jsonl_files:
        try:
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    if limit and len(messages) >= limit:
                        break

                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)

                        # Extract message based on source type
                        # This is a simplified extractor - may need source-specific parsing
                        if "message" in event and "role" in event.get("message", {}):
                            msg = event["message"]
                            role = msg.get("role")
                            content = msg.get("content", "")

                            if role in ["user", "assistant"] and content:
                                message = {
                                    "message_id": event.get("id", f"{source_name}_{jsonl_file.stem}_{line_num}"),
                                    "entity_id": event.get("id", f"{source_name}_{jsonl_file.stem}_{line_num}"),
                                    "source_name": source_name,
                                    "source_pipeline": f"{source_name}_loader",
                                    "source_file": str(jsonl_file),
                                    "text": content if isinstance(content, str) else json.dumps(content),
                                    "level": 5,  # Message level
                                    "content_date": datetime.now(timezone.utc).date(),
                                    "created_at": datetime.now(timezone.utc),
                                    "metadata": json.dumps(event),
                                }
                                messages.append(message)

                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parsing JSON in {jsonl_file}:{line_num}: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error reading {jsonl_file}: {e}", exc_info=True)
            continue

    logger.info(f"Extracted {len(messages)} messages from {source_name}")
    return messages

def _serialize_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Convert message dict into BigQuery-friendly payload."""
    payload = dict(message)
    for key in ("created_at", "content_date"):
        value = payload.get(key)
        if isinstance(value, datetime):
            payload[key] = value.isoformat()
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract JSONL messages and load to BigQuery.")
    parser.add_argument("--source", choices=list(DEFAULT_SOURCE_DIRS.keys()), default="claude_code")
    parser.add_argument("--source-dir", type=Path, help="Override source directory for JSONL files.")
    parser.add_argument("--limit", type=int, help="Maximum number of messages to extract.")
    parser.add_argument("--dry-run", action="store_true", help="Extract and display sample rows without loading.")
    parser.add_argument("--target-table", default=TARGET_TABLE, help="Fully qualified BigQuery table for output.")
    return parser.parse_args()


def main() -> int:
    """Extract JSONL messages and load them into BigQuery."""
    args = _parse_args()
    source_dir = Path(args.source_dir) if args.source_dir else DEFAULT_SOURCE_DIRS[args.source]

    with PipelineTracker(
        pipeline_name="claude_code_stage_0_jsonl",
        stage=0,
        stage_name="jsonl_extraction",
        metadata={"source": args.source, "source_dir": str(source_dir)},
    ) as tracker:
        messages = extract_messages_from_jsonl(source_dir, args.source, limit=args.limit)
        tracker.update_progress(items_processed=len(messages))

        if not messages:
            logger.info("No messages found to process", extra={"source": args.source, "source_dir": str(source_dir)})
            return 0

        if args.dry_run:
            print("\n".join(json.dumps(_serialize_message(m), indent=2, default=str) for m in messages[:5]))
            logger.info("Dry run complete", extra={"count": len(messages)})
            return 0

        client = get_bigquery_client()
        rows = [_serialize_message(m) for m in messages]
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
        job = client.load_table_from_json(rows, args.target_table, job_config=job_config)
        job.result()

        logger.info(
            "Loaded messages to BigQuery",
            extra={"count": len(rows), "table": args.target_table, "source": args.source},
        )

    return 0

if __name__ == "__main__":
    exit(main())
