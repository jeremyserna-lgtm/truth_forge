#!/usr/bin/env python3
"""Stage 7: L5 Message Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Message Finalizer) → HOLD₂ (claude_code_stage_7)

Creates Level 5 message entities from staged data, establishing the primary
entity level for Claude Code conversations.

🧠 STAGE FIVE GROUNDING
This stage exists to create L5 message entities - the primary unit of analysis.

Structure: Read staged data → Create message entities → Write to L5 table
Purpose: Create message-level SPINE entities with full metadata
Boundaries: Message entity creation only, no enrichment
Control: Consistent entity structure, parent-child relationships

⚠️ WHAT THIS STAGE CANNOT SEE
- Sentence-level analysis (handled in Stage 6)
- Embeddings (handled in Stage 9)
- Sentiment (handled in Stage 11)
- Topics (handled in Stage 12)

🔥 THE FURNACE PRINCIPLE
- Truth (input): Staged messages with entity_ids from THE GATE
- Heat (processing): Entity structure normalization
- Meaning (output): L5 message entities in SPINE format
- Care (delivery): Complete message coverage, proper hierarchy

Usage:
    python claude_code_stage_7.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 7: L5 Message Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Message Finalizer) → HOLD₂ (claude_code_stage_7)

Creates Level 5 message entities from staged data, establishing the primary
entity level for Claude Code conversations.

🧠 STAGE FIVE GROUNDING
This stage exists to create L5 message entities - the primary unit of analysis.

Structure: Read staged data → Create message entities → Write to L5 table
Purpose: Create message-level SPINE entities with full metadata
Boundaries: Message entity creation only, no enrichment
Control: Consistent entity structure, parent-child relationships

⚠️ WHAT THIS STAGE CANNOT SEE
- Sentence-level analysis (handled in Stage 6)
- Embeddings (handled in Stage 9)
- Sentiment (handled in Stage 11)
- Topics (handled in Stage 12)

🔥 THE FURNACE PRINCIPLE
- Truth (input): Staged messages with entity_ids from THE GATE
- Heat (processing): Entity structure normalization
- Meaning (output): L5 message entities in SPINE format
- Care (delivery): Complete message coverage, proper hierarchy

Usage:
    python claude_code_stage_7.py [--batch-size N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_7.claude_code_stage_7.py"

import argparse
import sys
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

from google.cloud import bigquery


_script_dir = Path(__file__).parent
_scripts_dir = _script_dir.parent
_pipeline_dir = _scripts_dir.parent
_project_root = _pipeline_dir.parent.parent
_src_path = _project_root / "src"

sys.path.insert(0, str(_scripts_dir))
sys.path.insert(0, str(_src_path))

from shared import (
    LEVEL_MESSAGE,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_4,
    TABLE_STAGE_7,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_4_TABLE = get_full_table_id(TABLE_STAGE_4)
STAGE_7_TABLE = get_full_table_id(TABLE_STAGE_7)

MESSAGE_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING"),  # session_id for conversation grouping
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("text", "STRING"),
    bigquery.SchemaField("role", "STRING"),
    bigquery.SchemaField("message_type", "STRING"),
    bigquery.SchemaField("message_index", "INTEGER"),
    bigquery.SchemaField("word_count", "INTEGER"),
    bigquery.SchemaField("char_count", "INTEGER"),
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("cost_usd", "FLOAT"),
    bigquery.SchemaField("tool_name", "STRING"),
    bigquery.SchemaField("tool_input", "STRING"),
    bigquery.SchemaField("tool_output", "STRING"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
    bigquery.SchemaField("fingerprint", "STRING"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_7_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 7 table."""
    table_ref = bigquery.Table(STAGE_7_TABLE, schema=MESSAGE_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["session_id", "role"]
    return client.create_table(table_ref, exists_ok=True)


def create_message_entities(
    client: bigquery.Client, run_id: str, created_at: str
) -> Generator[dict, None, None]:
    """Generate L5 message entities from staged data."""
    query = f"""
    SELECT
        entity_id,
        session_id,
        message_index,
        message_type,
        role,
        text,
        content_length,
        word_count,
        model,
        cost_usd,
        tool_name,
        tool_input,
        tool_output,
        content_date,
        timestamp_utc,
        fingerprint
    FROM `{STAGE_4_TABLE}`
    ORDER BY session_id, message_index
    """

    for row in client.query(query).result():
        yield {
            "entity_id": row.entity_id,
            "parent_id": row.session_id,  # Messages belong to sessions
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "level": LEVEL_MESSAGE,
            "text": row.text,
            "role": row.role,
            "message_type": row.message_type,
            "message_index": row.message_index,
            "word_count": row.word_count,
            "char_count": row.content_length,
            "model": row.model,
            "cost_usd": row.cost_usd,
            "tool_name": row.tool_name,
            "tool_input": row.tool_input,
            "tool_output": row.tool_output,
            "session_id": row.session_id,
            "content_date": row.content_date,
            "timestamp_utc": row.timestamp_utc,
            "fingerprint": row.fingerprint,
            "created_at": created_at,
            "run_id": run_id,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 7: Create L5 message entities")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=7, stage_name="l5_messages", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_4)
            if not args.dry_run:
                create_stage_7_table(bq_client)

            created_at = datetime.now(UTC).isoformat()
            batch, total = [], 0

            for entity in create_message_entities(bq_client, run_id, created_at):
                batch.append(entity)
                if len(batch) >= args.batch_size:
                    if not args.dry_run:
                        bq_client.insert_rows_json(STAGE_7_TABLE, batch)
                    total += len(batch)
                    batch = []

            if batch and not args.dry_run:
                bq_client.insert_rows_json(STAGE_7_TABLE, batch)
                total += len(batch)

            tracker.update_progress(items_processed=total)
            print(f"\nSTAGE 7 COMPLETE: {total} L5 message entities created")
            return 0

        except Exception as e:
            logger.error(f"Stage 7 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_7_messages")
            return 1


if __name__ == "__main__":
    sys.exit(main())
