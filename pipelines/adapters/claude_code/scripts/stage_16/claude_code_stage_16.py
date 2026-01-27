#!/usr/bin/env python3
"""Stage 16: Promotion to entity_unified - Claude Code Pipeline

HOLD₁ (claude_code_stage_15) → AGENT (Promoter) → HOLD₂ (spine.entity_unified)

Final stage: Promotes validated entities to the production entity_unified table.
Only entities that passed validation (status = PASSED or WARNING) are promoted.

🧠 STAGE FIVE GROUNDING
This stage exists to move validated entities into the unified production table.

Structure: Read validated entities → Filter passed → Transform to unified schema → Insert
Purpose: Complete the pipeline by promoting entities to production
Boundaries: Schema transformation and insertion only
Control: Idempotent promotion, duplicate prevention, audit trail

⚠️ WHAT THIS STAGE CANNOT SEE
- How entities will be queried
- Downstream analytics dependencies
- User access patterns
- Entity lifecycle after promotion

🔥 THE FURNACE PRINCIPLE
- Truth (input): Validated entities with PASSED/WARNING status
- Heat (processing): Schema transformation, deduplication
- Meaning (output): Production-ready entities in entity_unified
- Care (delivery): Complete promotion, no duplicates, audit logged

Usage:
    python claude_code_stage_16.py [--dry-run] [--include-warnings]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 16: Promotion to entity_unified - Claude Code Pipeline

HOLD₁ (claude_code_stage_15) → AGENT (Promoter) → HOLD₂ (spine.entity_unified)

Final stage: Promotes validated entities to the production entity_unified table.
Only entities that passed validation (status = PASSED or WARNING) are promoted.

🧠 STAGE FIVE GROUNDING
This stage exists to move validated entities into the unified production table.

Structure: Read validated entities → Filter passed → Transform to unified schema → Insert
Purpose: Complete the pipeline by promoting entities to production
Boundaries: Schema transformation and insertion only
Control: Idempotent promotion, duplicate prevention, audit trail

⚠️ WHAT THIS STAGE CANNOT SEE
- How entities will be queried
- Downstream analytics dependencies
- User access patterns
- Entity lifecycle after promotion

🔥 THE FURNACE PRINCIPLE
- Truth (input): Validated entities with PASSED/WARNING status
- Heat (processing): Schema transformation, deduplication
- Meaning (output): Production-ready entities in entity_unified
- Care (delivery): Complete promotion, no duplicates, audit logged

Usage:
    python claude_code_stage_16.py [--dry-run] [--include-warnings]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_16.claude_code_stage_16.py"

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
    TABLE_ENTITY_UNIFIED,
    TABLE_STAGE_15,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_15_TABLE = get_full_table_id(TABLE_STAGE_15)
ENTITY_UNIFIED_TABLE = get_full_table_id(TABLE_ENTITY_UNIFIED)

# Entity unified schema (production)
ENTITY_UNIFIED_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING"),
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
    bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
    bigquery.SchemaField("embedding_model", "STRING"),
    bigquery.SchemaField("embedding_dimension", "INTEGER"),
    bigquery.SchemaField("primary_emotion", "STRING"),
    bigquery.SchemaField("primary_emotion_score", "FLOAT"),
    bigquery.SchemaField("emotions_detected", "STRING"),
    bigquery.SchemaField("keywords", "STRING"),
    bigquery.SchemaField("top_keyword", "STRING"),
    bigquery.SchemaField("keyword_count", "INTEGER"),
    bigquery.SchemaField("intent", "STRING"),
    bigquery.SchemaField("task_type", "STRING"),
    bigquery.SchemaField("code_languages", "STRING"),
    bigquery.SchemaField("complexity", "STRING"),
    bigquery.SchemaField("has_code_block", "BOOLEAN"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
    bigquery.SchemaField("fingerprint", "STRING"),
    bigquery.SchemaField("validation_status", "STRING"),
    bigquery.SchemaField("validation_score", "FLOAT"),
    bigquery.SchemaField("promoted_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def ensure_entity_unified_table(client: bigquery.Client) -> bigquery.Table:
    """Ensure entity_unified table exists with proper schema."""
    table_ref = bigquery.Table(ENTITY_UNIFIED_TABLE, schema=ENTITY_UNIFIED_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["source_pipeline", "session_id", "level"]
    return client.create_table(table_ref, exists_ok=True)


def get_existing_entity_ids(bq_client: bigquery.Client) -> set:
    """Get existing entity_ids from entity_unified for this source."""
    query = f"""
    SELECT DISTINCT entity_id
    FROM `{ENTITY_UNIFIED_TABLE}`
    WHERE source_pipeline = '{PIPELINE_NAME}'
    """
    try:
        results = bq_client.query(query).result()
        return {row.entity_id for row in results}
    except Exception:
        # Table might not exist yet
        return set()


def promote_entities(
    bq_client: bigquery.Client,
    run_id: str,
    include_warnings: bool,
    dry_run: bool,
) -> dict[str, Any]:
    """Promote validated entities to entity_unified."""
    promoted_at = datetime.now(UTC).isoformat()

    # Build filter for validation status
    if include_warnings:
        status_filter = "validation_status IN ('PASSED', 'WARNING')"
    else:
        status_filter = "validation_status = 'PASSED'"

    # Get entities to promote
    query = f"""
    SELECT *
    FROM `{STAGE_15_TABLE}`
    WHERE {status_filter}
    ORDER BY session_id, message_index
    """

    entities = list(bq_client.query(query).result())
    logger.info(f"Found {len(entities)} entities eligible for promotion")

    if dry_run:
        return {
            "eligible_entities": len(entities),
            "promoted_entities": 0,
            "skipped_duplicates": 0,
            "dry_run": True,
        }

    # Get existing IDs to avoid duplicates
    existing_ids = get_existing_entity_ids(bq_client)
    logger.info(f"Found {len(existing_ids)} existing entities from this pipeline")

    # Prepare records for promotion
    records_to_insert = []
    skipped = 0

    for entity in entities:
        entity_dict = dict(entity)
        entity_id = entity_dict.get("entity_id")

        # Skip duplicates
        if entity_id in existing_ids:
            skipped += 1
            continue

        record = {
            "entity_id": entity_id,
            "parent_id": entity_dict.get("parent_id"),
            "source_name": entity_dict.get("source_name"),
            "source_pipeline": entity_dict.get("source_pipeline"),
            "level": entity_dict.get("level"),
            "text": entity_dict.get("text"),
            "role": entity_dict.get("role"),
            "message_type": entity_dict.get("message_type"),
            "message_index": entity_dict.get("message_index"),
            "word_count": entity_dict.get("word_count"),
            "char_count": entity_dict.get("char_count"),
            "model": entity_dict.get("model"),
            "cost_usd": entity_dict.get("cost_usd"),
            "tool_name": entity_dict.get("tool_name"),
            "embedding": list(entity_dict.get("embedding", []))
            if entity_dict.get("embedding")
            else None,
            "embedding_model": entity_dict.get("embedding_model"),
            "embedding_dimension": entity_dict.get("embedding_dimension"),
            "primary_emotion": entity_dict.get("primary_emotion"),
            "primary_emotion_score": entity_dict.get("primary_emotion_score"),
            "emotions_detected": entity_dict.get("emotions_detected"),
            "keywords": entity_dict.get("keywords"),
            "top_keyword": entity_dict.get("top_keyword"),
            "keyword_count": entity_dict.get("keyword_count"),
            "intent": entity_dict.get("intent"),
            "task_type": entity_dict.get("task_type"),
            "code_languages": entity_dict.get("code_languages"),
            "complexity": entity_dict.get("complexity"),
            "has_code_block": entity_dict.get("has_code_block"),
            "session_id": entity_dict.get("session_id"),
            "content_date": entity_dict.get("content_date"),
            "timestamp_utc": entity_dict.get("timestamp_utc"),
            "fingerprint": entity_dict.get("fingerprint"),
            "validation_status": entity_dict.get("validation_status"),
            "validation_score": entity_dict.get("validation_score"),
            "promoted_at": promoted_at,
            "run_id": run_id,
        }
        records_to_insert.append(record)

        # Insert in batches
        if len(records_to_insert) >= 1000:
            errors = bq_client.insert_rows_json(ENTITY_UNIFIED_TABLE, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

    # Insert remaining
    if records_to_insert:
        errors = bq_client.insert_rows_json(ENTITY_UNIFIED_TABLE, records_to_insert)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")

    promoted = len(entities) - skipped

    return {
        "eligible_entities": len(entities),
        "promoted_entities": promoted,
        "skipped_duplicates": skipped,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 16: Promote to entity_unified")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--include-warnings", action="store_true", help="Also promote entities with WARNING status"
    )
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=16, stage_name="promotion", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_15)

            if not args.dry_run:
                ensure_entity_unified_table(bq_client)

            stats = promote_entities(bq_client, run_id, args.include_warnings, args.dry_run)
            tracker.update_progress(items_processed=stats["promoted_entities"])

            print(f"\n{'=' * 60}")
            print("STAGE 16 COMPLETE: PROMOTION TO ENTITY_UNIFIED")
            print(f"{'=' * 60}")
            print(f"Eligible entities: {stats['eligible_entities']}")
            print(f"Promoted entities: {stats['promoted_entities']}")
            print(f"Skipped (duplicates): {stats['skipped_duplicates']}")
            print(f"Target table: {ENTITY_UNIFIED_TABLE}")
            print(f"Include warnings: {args.include_warnings}")
            print(f"{'=' * 60}")

            logger.info(
                f"Pipeline complete: {stats['promoted_entities']} entities promoted to entity_unified",
                extra={
                    "run_id": run_id,
                    "promoted": stats["promoted_entities"],
                    "skipped": stats["skipped_duplicates"],
                },
            )

            return 0

        except Exception as e:
            logger.error(f"Stage 16 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_16_promotion")
            return 1


if __name__ == "__main__":
    sys.exit(main())
