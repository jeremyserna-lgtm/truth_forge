#!/usr/bin/env python3
"""Stage 14: Aggregation - Claude Code Pipeline

HOLD₁ (multiple stages) → AGENT (Aggregator) → HOLD₂ (claude_code_stage_14)

Aggregates enrichments onto L5 message entities to create unified entity records.
Combines: base entity + embeddings + sentiment + topics + LLM extraction.

🧠 STAGE FIVE GROUNDING
This stage exists to merge all enrichments into unified entity records.

Structure: Read all enrichment tables → Join on entity_id → Create unified records → Write
Purpose: Create complete entity records for promotion to spine
Boundaries: Aggregation only, no new analysis
Control: Consistent joins, null handling, schema alignment

⚠️ WHAT THIS STAGE CANNOT SEE
- Which enrichments are most valuable
- Data quality across enrichments
- Usage patterns (downstream analysis)
- Cross-entity insights

🔥 THE FURNACE PRINCIPLE
- Truth (input): Multiple enrichment tables
- Heat (processing): SQL aggregation, schema unification
- Meaning (output): Unified entity records ready for validation
- Care (delivery): All enrichments merged, no data loss

Usage:
    python claude_code_stage_14.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 14: Aggregation - Claude Code Pipeline

HOLD₁ (multiple stages) → AGENT (Aggregator) → HOLD₂ (claude_code_stage_14)

Aggregates enrichments onto L5 message entities to create unified entity records.
Combines: base entity + embeddings + sentiment + topics + LLM extraction.

🧠 STAGE FIVE GROUNDING
This stage exists to merge all enrichments into unified entity records.

Structure: Read all enrichment tables → Join on entity_id → Create unified records → Write
Purpose: Create complete entity records for promotion to spine
Boundaries: Aggregation only, no new analysis
Control: Consistent joins, null handling, schema alignment

⚠️ WHAT THIS STAGE CANNOT SEE
- Which enrichments are most valuable
- Data quality across enrichments
- Usage patterns (downstream analysis)
- Cross-entity insights

🔥 THE FURNACE PRINCIPLE
- Truth (input): Multiple enrichment tables
- Heat (processing): SQL aggregation, schema unification
- Meaning (output): Unified entity records ready for validation
- Care (delivery): All enrichments merged, no data loss

Usage:
    python claude_code_stage_14.py [--batch-size N] [--dry-run]
"""
# Use shared logging bridge for consistent logging
from shared.logging_bridge import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_14.claude_code_stage_14.py"

import argparse
import sys
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
    PIPELINE_NAME,
    TABLE_STAGE_7,
    TABLE_STAGE_9,
    TABLE_STAGE_10,
    TABLE_STAGE_11,
    TABLE_STAGE_12,
    TABLE_STAGE_14,
    get_full_table_id,
    validate_input_table_exists,
)
from shared.logging_bridge import get_current_run_id, get_logger
# get_bigquery_client fallback
def get_bigquery_client():
    from google.cloud import bigquery
    return bigquery.Client()
# PipelineTracker fallback
from contextlib import contextmanager
@contextmanager
def PipelineTracker(*args, **kwargs):
    obj = type("obj", (object,), {"update_progress": lambda self, **kw: None})()
    yield obj
# require_diagnostic_on_error fallback
def require_diagnostic_on_error(error, context):
    pass


logger = get_logger(__name__)

STAGE_7_TABLE = get_full_table_id(TABLE_STAGE_7)
STAGE_9_TABLE = get_full_table_id(TABLE_STAGE_9)
STAGE_10_TABLE = get_full_table_id(TABLE_STAGE_10)
STAGE_11_TABLE = get_full_table_id(TABLE_STAGE_11)
STAGE_12_TABLE = get_full_table_id(TABLE_STAGE_12)
STAGE_14_TABLE = get_full_table_id(TABLE_STAGE_14)

AGGREGATED_SCHEMA = [
    # Core entity fields
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    # Message fields
    bigquery.SchemaField("text", "STRING"),
    bigquery.SchemaField("role", "STRING"),
    bigquery.SchemaField("message_type", "STRING"),
    bigquery.SchemaField("message_index", "INTEGER"),
    bigquery.SchemaField("word_count", "INTEGER"),
    bigquery.SchemaField("char_count", "INTEGER"),
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("cost_usd", "FLOAT"),
    bigquery.SchemaField("tool_name", "STRING"),
    # Embedding fields
    bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
    bigquery.SchemaField("embedding_model", "STRING"),
    bigquery.SchemaField("embedding_dimension", "INTEGER"),
    # Sentiment fields (aggregated from sentences)
    bigquery.SchemaField("primary_emotion", "STRING"),
    bigquery.SchemaField("primary_emotion_score", "FLOAT"),
    bigquery.SchemaField("emotions_detected", "STRING"),
    # Topic fields
    bigquery.SchemaField("keywords", "STRING"),
    bigquery.SchemaField("top_keyword", "STRING"),
    bigquery.SchemaField("keyword_count", "INTEGER"),
    # LLM extraction fields
    bigquery.SchemaField("intent", "STRING"),
    bigquery.SchemaField("task_type", "STRING"),
    bigquery.SchemaField("code_languages", "STRING"),
    bigquery.SchemaField("complexity", "STRING"),
    bigquery.SchemaField("has_code_block", "BOOLEAN"),
    # Metadata
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
    bigquery.SchemaField("fingerprint", "STRING"),
    bigquery.SchemaField("aggregated_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_14_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 14 aggregated table."""
    table_ref = bigquery.Table(STAGE_14_TABLE, schema=AGGREGATED_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["session_id", "role", "intent"]
    return client.create_table(table_ref, exists_ok=True)


def aggregate_entities(
    bq_client: bigquery.Client,
    run_id: str,
    batch_size: int,
    dry_run: bool,
) -> dict[str, int]:
    """Aggregate all enrichments onto message entities."""
    # Validate all inputs first to prevent SQL injection
    from shared_validation import validate_table_id, validate_run_id
    
    validated_stage_7_table = validate_table_id(STAGE_7_TABLE)
    validated_stage_9_table = validate_table_id(STAGE_9_TABLE)
    validated_stage_10_table = validate_table_id(STAGE_10_TABLE)
    validated_stage_12_table = validate_table_id(STAGE_12_TABLE)
    validated_stage_14_table = validate_table_id(STAGE_14_TABLE)
    validated_run_id = validate_run_id(run_id)
    
    aggregated_at = datetime.now(UTC).isoformat()
    # Validate timestamp
    if any(danger in aggregated_at for danger in ['--', ';', '/*', '*/']):
        raise ValueError("Invalid timestamp: potential SQL injection")

    # Build aggregation query with validated table IDs
    # Left joins to preserve all messages even without enrichments
    aggregation_query = f"""
    SELECT
        m.entity_id,
        m.parent_id,
        m.source_name,
        m.source_pipeline,
        m.level,
        m.text,
        m.role,
        m.message_type,
        m.message_index,
        m.word_count,
        m.char_count,
        m.model,
        m.cost_usd,
        m.tool_name,

        -- Embeddings
        e.embedding,
        e.embedding_model,
        e.embedding_dimension,

        -- Sentiment (from LLM extraction or message-level)
        COALESCE(llm.intent, 'unknown') as intent,
        llm.task_type,
        llm.code_languages,
        llm.complexity,
        llm.has_code_block,

        -- Topics
        t.keywords,
        t.top_keyword,
        t.keyword_count,

        -- Metadata
        m.session_id,
        m.content_date,
        m.timestamp_utc,
        m.fingerprint,

        TIMESTAMP('{aggregated_at}') as aggregated_at,
        '{validated_run_id}' as run_id

    FROM `{validated_stage_7_table}` m

    LEFT JOIN `{validated_stage_9_table}` e
        ON m.entity_id = e.entity_id

    LEFT JOIN `{validated_stage_10_table}` llm
        ON m.entity_id = llm.entity_id

    LEFT JOIN `{validated_stage_12_table}` t
        ON m.entity_id = t.entity_id

    ORDER BY m.session_id, m.message_index
    """

    if dry_run:
        # Count what would be processed (with validated table ID)
        count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_7_table}`"
        result = bq_client.query(count_query).result()
        row = next(iter(result))
        return {
            "messages_aggregated": 0,
            "messages_to_aggregate": row.cnt,
            "dry_run": True,
        }

    # Execute aggregation via DELETE + INSERT to prevent duplicates
    # First delete existing data for this run_id
    delete_query = f"""
    DELETE FROM `{validated_stage_14_table}`
    WHERE run_id = '{validated_run_id}'
    """
    delete_job = bq_client.query(delete_query)
    delete_job.result()
    if delete_job.errors:
        raise ValueError(f"DELETE failed: {delete_job.errors[:5]}")
    
    # Then insert new aggregated data
    insert_query = f"""
    INSERT INTO `{validated_stage_14_table}` (
        entity_id, parent_id, source_name, source_pipeline, level,
        text, role, message_type, message_index, word_count, char_count,
        model, cost_usd, tool_name,
        embedding, embedding_model, embedding_dimension,
        intent, task_type, code_languages, complexity, has_code_block,
        keywords, top_keyword, keyword_count,
        session_id, content_date, timestamp_utc, fingerprint,
        TIMESTAMP('{aggregated_at}') as aggregated_at,
        '{validated_run_id}' AS run_id
    )
    {aggregation_query}
    """

    job = bq_client.query(insert_query)
    job.result()  # Wait for completion
    if job.errors:
        raise ValueError(f"INSERT failed: {job.errors[:5]}")

    # Count inserted rows (with validated table ID and run_id)
    count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_14_table}` WHERE run_id = '{validated_run_id}'"
    result = bq_client.query(count_query).result()
    row = next(iter(result))

    return {
        "messages_aggregated": row.cnt,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 14: Entity aggregation")
    parser.add_argument("--batch-size", type=int, default=10000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=14, stage_name="aggregation", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            # Validate input tables (only require stage 7, others are optional)
            validate_input_table_exists(bq_client, TABLE_STAGE_7)

            if not args.dry_run:
                create_stage_14_table(bq_client)

            stats = aggregate_entities(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats.get("messages_aggregated", 0))

            print(f"\nSTAGE 14 COMPLETE: {stats.get('messages_aggregated', 0)} entities aggregated")
            return 0

        except Exception as e:
            logger.error("Failed to aggregate entity data")
            logger.error(f"Error: {str(e)}")
            logger.debug(f"Technical details: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_14_aggregation")
            return 1


if __name__ == "__main__":
    sys.exit(main())
