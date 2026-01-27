#!/usr/bin/env python3
"""Stage 8: L8 Conversation Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Conversation Aggregator) → HOLD₂ (claude_code_stage_8)

Creates Level 8 conversation entities (sessions) by aggregating L5 messages.
This completes the SPINE hierarchy: L1→L3→L5→L8.

🧠 STAGE FIVE GROUNDING
This stage exists to create L8 conversation/session entities from message groups.

Structure: Read L5 messages → Aggregate by session → Create conversation entities → Write
Purpose: Create session-level SPINE entities with aggregated statistics
Boundaries: Conversation entity creation only, aggregation stats
Control: Proper session grouping, complete message coverage

⚠️ WHAT THIS STAGE CANNOT SEE
- Individual message content (aggregated only)
- Downstream enrichment (embeddings, sentiment)
- Cross-session relationships
- User intents or goals

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message entities grouped by session
- Heat (processing): Statistical aggregation, session metadata extraction
- Meaning (output): L8 conversation entities with session-level statistics
- Care (delivery): All sessions represented, accurate aggregations

Usage:
    python claude_code_stage_8.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 8: L8 Conversation Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Conversation Aggregator) → HOLD₂ (claude_code_stage_8)

Creates Level 8 conversation entities (sessions) by aggregating L5 messages.
This completes the SPINE hierarchy: L1→L3→L5→L8.

🧠 STAGE FIVE GROUNDING
This stage exists to create L8 conversation/session entities from message groups.

Structure: Read L5 messages → Aggregate by session → Create conversation entities → Write
Purpose: Create session-level SPINE entities with aggregated statistics
Boundaries: Conversation entity creation only, aggregation stats
Control: Proper session grouping, complete message coverage

⚠️ WHAT THIS STAGE CANNOT SEE
- Individual message content (aggregated only)
- Downstream enrichment (embeddings, sentiment)
- Cross-session relationships
- User intents or goals

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message entities grouped by session
- Heat (processing): Statistical aggregation, session metadata extraction
- Meaning (output): L8 conversation entities with session-level statistics
- Care (delivery): All sessions represented, accurate aggregations

Usage:
    python claude_code_stage_8.py [--batch-size N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_8.claude_code_stage_8.py"

import argparse
import hashlib
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
    LEVEL_CONVERSATION,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_7,
    TABLE_STAGE_8,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_7_TABLE = get_full_table_id(TABLE_STAGE_7)
STAGE_8_TABLE = get_full_table_id(TABLE_STAGE_8)

CONVERSATION_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING"),  # Could be user_id in future
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("message_count", "INTEGER"),
    bigquery.SchemaField("user_message_count", "INTEGER"),
    bigquery.SchemaField("assistant_message_count", "INTEGER"),
    bigquery.SchemaField("tool_use_count", "INTEGER"),
    bigquery.SchemaField("total_word_count", "INTEGER"),
    bigquery.SchemaField("total_char_count", "INTEGER"),
    bigquery.SchemaField("total_cost_usd", "FLOAT"),
    bigquery.SchemaField("models_used", "STRING"),  # JSON array
    bigquery.SchemaField("tools_used", "STRING"),  # JSON array
    bigquery.SchemaField("first_message_at", "TIMESTAMP"),
    bigquery.SchemaField("last_message_at", "TIMESTAMP"),
    bigquery.SchemaField("duration_seconds", "INTEGER"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_8_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 8 table."""
    table_ref = bigquery.Table(STAGE_8_TABLE, schema=CONVERSATION_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["session_id"]
    return client.create_table(table_ref, exists_ok=True)


def generate_conversation_id(session_id: str) -> str:
    """Generate deterministic conversation entity_id."""
    return hashlib.sha256(f"L8:{SOURCE_NAME}:{session_id}".encode()).hexdigest()[:32]


def create_conversation_entities(
    client: bigquery.Client, run_id: str, created_at: str
) -> Generator[dict, None, None]:
    """Aggregate L5 messages into L8 conversation entities."""
    query = f"""
    SELECT
        session_id,
        COUNT(*) as message_count,
        COUNTIF(role = 'user') as user_message_count,
        COUNTIF(role = 'assistant') as assistant_message_count,
        COUNTIF(tool_name IS NOT NULL) as tool_use_count,
        SUM(COALESCE(word_count, 0)) as total_word_count,
        SUM(COALESCE(char_count, 0)) as total_char_count,
        SUM(COALESCE(cost_usd, 0)) as total_cost_usd,
        TO_JSON_STRING(ARRAY_AGG(DISTINCT model IGNORE NULLS)) as models_used,
        TO_JSON_STRING(ARRAY_AGG(DISTINCT tool_name IGNORE NULLS)) as tools_used,
        MIN(timestamp_utc) as first_message_at,
        MAX(timestamp_utc) as last_message_at,
        MIN(content_date) as content_date
    FROM `{STAGE_7_TABLE}`
    GROUP BY session_id
    """

    for row in client.query(query).result():
        duration = None
        if row.first_message_at and row.last_message_at:
            duration = int((row.last_message_at - row.first_message_at).total_seconds())

        yield {
            "entity_id": generate_conversation_id(row.session_id),
            "parent_id": None,  # Could be user_id
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "level": LEVEL_CONVERSATION,
            "session_id": row.session_id,
            "message_count": row.message_count,
            "user_message_count": row.user_message_count,
            "assistant_message_count": row.assistant_message_count,
            "tool_use_count": row.tool_use_count,
            "total_word_count": row.total_word_count,
            "total_char_count": row.total_char_count,
            "total_cost_usd": float(row.total_cost_usd) if row.total_cost_usd else 0.0,
            "models_used": row.models_used,
            "tools_used": row.tools_used,
            "first_message_at": row.first_message_at.isoformat() if row.first_message_at else None,
            "last_message_at": row.last_message_at.isoformat() if row.last_message_at else None,
            "duration_seconds": duration,
            "content_date": row.content_date,
            "created_at": created_at,
            "run_id": run_id,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 8: Create L8 conversation entities")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=8, stage_name="l8_conversations", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_7)
            if not args.dry_run:
                create_stage_8_table(bq_client)

            created_at = datetime.now(UTC).isoformat()
            batch, total = [], 0

            for entity in create_conversation_entities(bq_client, run_id, created_at):
                batch.append(entity)
                if len(batch) >= args.batch_size:
                    if not args.dry_run:
                        bq_client.insert_rows_json(STAGE_8_TABLE, batch)
                    total += len(batch)
                    batch = []

            if batch and not args.dry_run:
                bq_client.insert_rows_json(STAGE_8_TABLE, batch)
                total += len(batch)

            tracker.update_progress(items_processed=total)
            print(f"\nSTAGE 8 COMPLETE: {total} L8 conversation entities created")
            return 0

        except Exception as e:
            logger.error(f"Stage 8 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_8_conversations")
            return 1


if __name__ == "__main__":
    sys.exit(main())
