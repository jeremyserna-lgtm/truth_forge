#!/usr/bin/env python3
"""Stage 1: Extraction - Claude Code Pipeline

HOLD₁ (JSONL session files) → AGENT (Parser) → HOLD₂ (BigQuery claude_code_stage_1)

Extracts structured message data from raw Claude Code JSONL exports and loads
into BigQuery staging table for downstream processing.

🧠 STAGE FIVE GROUNDING
This stage exists to parse raw Claude Code exports into structured BigQuery rows.

Structure: Read JSONL → Parse messages → Validate → Load to BigQuery
Purpose: Transform raw exports into queryable structured data
Boundaries: Extraction only, no enrichment or transformation
Control: Batch processing with checkpoints, validates before write

⚠️ WHAT THIS STAGE CANNOT SEE
- Message semantics or intent
- Relationships between messages
- Whether sessions are complete
- Future schema requirements

🔥 THE FURNACE PRINCIPLE
- Truth (input): Raw JSONL session files from Claude Code
- Heat (processing): JSON parsing, schema mapping, batch loading
- Meaning (output): Structured rows in BigQuery ready for processing
- Care (delivery): Validated data with full audit trail

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 1 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 1 extracts raw data with minimal transformation
- Creates foundation for downstream processing
- Enables parallel processing of multiple source files

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations

Usage:
    python claude_code_stage_1.py [--source-dir PATH] [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 1: Extraction - Claude Code Pipeline

HOLD₁ (JSONL session files) → AGENT (Parser) → HOLD₂ (BigQuery claude_code_stage_1)

Extracts structured message data from raw Claude Code JSONL exports and loads
into BigQuery staging table for downstream processing.

🧠 STAGE FIVE GROUNDING
This stage exists to parse raw Claude Code exports into structured BigQuery rows.

Structure: Read JSONL → Parse messages → Validate → Load to BigQuery
Purpose: Transform raw exports into queryable structured data
Boundaries: Extraction only, no enrichment or transformation
Control: Batch processing with checkpoints, validates before write

⚠️ WHAT THIS STAGE CANNOT SEE
- Message semantics or intent
- Relationships between messages
- Whether sessions are complete
- Future schema requirements

🔥 THE FURNACE PRINCIPLE
- Truth (input): Raw JSONL session files from Claude Code
- Heat (processing): JSON parsing, schema mapping, batch loading
- Meaning (output): Structured rows in BigQuery ready for processing
- Care (delivery): Validated data with full audit trail

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 1 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 1 extracts raw data with minimal transformation
- Creates foundation for downstream processing
- Enables parallel processing of multiple source files

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations

Usage:
    python claude_code_stage_1.py [--source-dir PATH] [--batch-size N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_1.claude_code_stage_1.py"

import argparse
import hashlib
import json
import sys
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from google.cloud import bigquery


# Add paths for imports
_script_dir = Path(__file__).parent
_scripts_dir = _script_dir.parent
_pipeline_dir = _scripts_dir.parent
_project_root = _pipeline_dir.parent.parent
_src_path = _project_root / "src"

sys.path.insert(0, str(_scripts_dir))
sys.path.insert(0, str(_src_path))

from shared import (
    PIPELINE_NAME,
    TABLE_STAGE_1,
    get_full_table_id,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import (
    require_diagnostic_on_error,
)


logger = get_logger(__name__)

# Configuration
DEFAULT_SOURCE_DIR = Path.home() / ".claude" / "projects"
DEFAULT_BATCH_SIZE = 1000
STAGE_1_TABLE = get_full_table_id(TABLE_STAGE_1)

# Schema for stage 1 table
STAGE_1_SCHEMA = [
    bigquery.SchemaField("extraction_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("message_index", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("message_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("role", "STRING"),
    bigquery.SchemaField("content", "STRING"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("cost_usd", "FLOAT"),
    bigquery.SchemaField("tool_name", "STRING"),
    bigquery.SchemaField("tool_input", "STRING"),
    bigquery.SchemaField("tool_output", "STRING"),
    bigquery.SchemaField("source_file", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("fingerprint", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("extracted_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_1_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 1 table with proper schema."""
    table_ref = bigquery.Table(STAGE_1_TABLE, schema=STAGE_1_SCHEMA)

    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="content_date",
    )
    table_ref.clustering_fields = ["session_id", "message_type"]

    try:
        table = client.create_table(table_ref, exists_ok=True)
        logger.info(f"Stage 1 table ready: {STAGE_1_TABLE}")
        return table
    except Exception as e:
        require_diagnostic_on_error(e, "create_stage_1_table")
        raise


def discover_session_files(source_dir: Path) -> list[Path]:
    """Discover JSONL files in source directory."""
    if not source_dir.exists():
        logger.warning(f"Source directory does not exist: {source_dir}")
        return []

    return sorted(source_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime)


def parse_session_file(
    file_path: Path,
    run_id: str,
) -> Generator[dict[str, Any], None, None]:
    """Parse JSONL file and yield message records.

    Args:
        file_path: Path to JSONL file
        run_id: Current run ID for traceability

    Yields:
        Message records ready for BigQuery
    """
    session_id = None
    current_model = None
    message_index = 0
    extracted_at = datetime.now(UTC)

    with open(file_path, encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue

            try:
                msg = json.loads(line)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse error in {file_path}:{line_num}: {e}")
                continue

            msg_type = msg.get("type", "unknown")

            # Handle summary message (contains session metadata)
            if msg_type == "summary":
                session_id = msg.get("session_id") or _generate_session_id(file_path)
                current_model = msg.get("model")
                continue

            # Generate session_id if not found in summary
            if session_id is None:
                session_id = _generate_session_id(file_path)

            # Parse timestamp
            timestamp = None
            content_date = None
            if msg.get("timestamp"):
                try:
                    timestamp = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
                    content_date = timestamp.date()
                except (ValueError, AttributeError):
                    pass

            # Determine role
            role = None
            if msg_type == "user":
                role = "user"
            elif msg_type == "assistant":
                role = "assistant"
            elif msg_type == "tool_result":
                role = "tool"

            # Extract content
            content = msg.get("content", "")
            if isinstance(content, dict) or isinstance(content, list):
                content = json.dumps(content)

            # Create fingerprint for deduplication
            fingerprint = hashlib.sha256(
                f"{session_id}:{message_index}:{content[:100] if content else ''}".encode()
            ).hexdigest()[:32]

            # Create extraction ID
            extraction_id = f"ext:{session_id}:{message_index}:{fingerprint[:8]}"

            record = {
                "extraction_id": extraction_id,
                "session_id": session_id,
                "message_index": message_index,
                "message_type": msg_type,
                "role": role,
                "content": content,
                "timestamp": timestamp,
                "model": msg.get("model") or current_model,
                "cost_usd": msg.get("cost_usd"),
                "tool_name": msg.get("name") if msg_type == "tool_use" else None,
                "tool_input": json.dumps(msg.get("input")) if msg.get("input") else None,
                "tool_output": msg.get("output") if msg_type == "tool_result" else None,
                "source_file": str(file_path),
                "content_date": content_date,
                "fingerprint": fingerprint,
                "extracted_at": extracted_at,
                "run_id": run_id,
            }

            message_index += 1
            yield record


def _generate_session_id(file_path: Path) -> str:
    """Generate session ID from file path."""
    return hashlib.sha256(str(file_path).encode()).hexdigest()[:16]


def load_to_bigquery(
    client: bigquery.Client,
    records: list[dict[str, Any]],
    dry_run: bool = False,
) -> int:
    """Load records to BigQuery.

    Args:
        client: BigQuery client
        records: Records to load
        dry_run: If True, skip actual load

    Returns:
        Number of records loaded
    """
    if not records:
        return 0

    if dry_run:
        logger.info(f"DRY RUN: Would load {len(records)} records")
        return len(records)

    errors = client.insert_rows_json(STAGE_1_TABLE, records)

    if errors:
        logger.error(f"BigQuery insert errors: {errors[:5]}")  # Log first 5 errors
        raise ValueError(f"Failed to insert {len(errors)} records")

    return len(records)


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(
        description="Stage 1: Extract Claude Code sessions to BigQuery"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE_DIR,
        help=f"Source directory for JSONL files (default: {DEFAULT_SOURCE_DIR})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"Batch size for BigQuery loads (default: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse files but don't load to BigQuery",
    )
    parser.add_argument(
        "--limit-files",
        type=int,
        default=None,
        help="Limit number of files to process",
    )

    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=1,
        stage_name="extraction",
        run_id=run_id,
        metadata={
            "source_dir": str(args.source_dir),
            "batch_size": args.batch_size,
            "dry_run": args.dry_run,
        },
    ) as tracker:
        try:
            logger.info(
                "Starting Stage 1: Extraction",
                extra={"run_id": run_id, "source_dir": str(args.source_dir)},
            )

            # Get BigQuery client
            client = get_bigquery_client()
            if hasattr(client, "client"):
                bq_client = client.client
            else:
                bq_client = client

            # Create table if needed
            if not args.dry_run:
                create_stage_1_table(bq_client)

            # HOLD₁: Discover source files
            session_files = discover_session_files(args.source_dir)
            if args.limit_files:
                session_files = session_files[: args.limit_files]

            tracker.update_progress(items_total=len(session_files))
            logger.info(f"Found {len(session_files)} session files to process")

            # AGENT: Parse and load
            total_records = 0
            batch = []

            for file_idx, file_path in enumerate(session_files):
                logger.info(f"Processing [{file_idx + 1}/{len(session_files)}]: {file_path.name}")

                for record in parse_session_file(file_path, run_id):
                    batch.append(record)

                    if len(batch) >= args.batch_size:
                        loaded = load_to_bigquery(bq_client, batch, args.dry_run)
                        total_records += loaded
                        batch = []
                        tracker.update_progress(items_processed=total_records)

            # Load remaining batch
            if batch:
                loaded = load_to_bigquery(bq_client, batch, args.dry_run)
                total_records += loaded

            tracker.update_progress(items_processed=total_records)

            # HOLD₂: Verify load
            logger.info(
                f"Stage 1 complete: Extracted {total_records} records from {len(session_files)} files",
                extra={
                    "run_id": run_id,
                    "files_processed": len(session_files),
                    "records_extracted": total_records,
                },
            )

            print(f"\n{'=' * 60}")
            print("STAGE 1 COMPLETE: Extraction")
            print(f"{'=' * 60}")
            print(f"Files processed: {len(session_files)}")
            print(f"Records extracted: {total_records}")
            print(f"Target table: {STAGE_1_TABLE}")
            print(f"Dry run: {args.dry_run}")

            return 0

        except Exception as e:
            logger.error(f"Stage 1 failed: {e}", exc_info=True, extra={"run_id": run_id})
            require_diagnostic_on_error(e, "stage_1_extraction")
            tracker.update_progress(items_failed=1)
            return 1


if __name__ == "__main__":
    sys.exit(main())
