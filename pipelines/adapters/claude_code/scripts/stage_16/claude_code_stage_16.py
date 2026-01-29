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

# Use shared logging bridge for consistent logging
from shared.logging_bridge import get_logger as _get_logger


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

# Fallback implementations for missing central_services dependencies
from collections.abc import Generator
from contextlib import contextmanager

from shared import (
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_ENTITY_UNIFIED,
    TABLE_STAGE_15,
    get_full_table_id,
    validate_input_table_exists,
)
from shared.logging_bridge import get_current_run_id, get_logger


def get_bigquery_client() -> bigquery.Client:
    """Get BigQuery client with cost protection when available."""
    try:
        # Try truth_forge.core first
        from truth_forge.core.bigquery_client import get_bigquery_client as get_bq
        client = get_bq()
        logger.info("Using truth_forge.core BigQuery client (with cost protection)")
        if hasattr(client, "client"):
            return client.client  # type: ignore[return-value]
        return client  # type: ignore[return-value]
    except ImportError:
        try:
            # Fallback to central_services
            from src.services.central_services.core.config import get_bigquery_client as get_bq
            client = get_bq()
            logger.info("Using central_services BigQuery client (with cost protection)")
            if hasattr(client, "client"):
                return client.client  # type: ignore[return-value]
            return client  # type: ignore[return-value]
        except ImportError:
            # Final fallback with WARNING
            logger.warning(
                "⚠️  WARNING: Central services not available. Using direct client (NO COST PROTECTION)."
            )
            logger.warning("   Install central services for cost protection and retry logic.")
            print("⚠️  WARNING: Using direct BigQuery client - NO COST PROTECTION")
            print("   Install central services for cost protection and retry logic.")
            return bigquery.Client()


@contextmanager
def PipelineTracker(*args: Any, **kwargs: Any) -> Generator[Any, None, None]:
    """PipelineTracker with real tracking when available."""
    try:
        from src.services.central_services.core.pipeline_tracker import PipelineTracker as RealTracker
        logger.info("Using real PipelineTracker (with progress tracking)")
        with RealTracker(*args, **kwargs) as tracker:
            yield tracker
    except ImportError:
        logger.warning("⚠️  WARNING: PipelineTracker not available. Using no-op fallback.")
        logger.warning("   Install central services for progress tracking.")
        print("⚠️  WARNING: Progress tracking not available")
        obj = type("obj", (object,), {"update_progress": lambda self, **kw: None})()
        yield obj


def require_diagnostic_on_error(error: Exception, context: str) -> None:
    """Require diagnostic on error with real diagnostics when available."""
    try:
        from src.services.central_services.governance.governance import require_diagnostic_on_error as real_diag
        logger.info(f"Using real error diagnostics for: {context}")
        real_diag(error, context)
    except ImportError:
        logger.warning(f"⚠️  WARNING: Error diagnostics not available for: {context}")
        logger.warning("   Install central services for error diagnostics.")
        # Still log error even without diagnostics
        logger.error(
            f"Error in {context}",
            extra={"error": str(error), "context": context},
            exc_info=True
        )
        print(f"⚠️  WARNING: Error diagnostics not available for: {context}")
        print(f"   Error: {str(error)}")


logger = get_logger(__name__)

STAGE_15_TABLE = get_full_table_id(TABLE_STAGE_15)
ENTITY_UNIFIED_TABLE = get_full_table_id(TABLE_ENTITY_UNIFIED)

# Entity unified schema (production) - MATCHES ACTUAL BigQuery TABLE SCHEMA
# This schema must match the actual entity_unified table exactly
ENTITY_UNIFIED_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("level", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("entity_type", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("entity_mode", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("parent_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_ids", "STRING", mode="REPEATED"),
    bigquery.SchemaField("conversation_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("topic_segment_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("turn_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("message_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("sentence_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("span_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("word_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("text", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_file", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_file_path", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_system", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("metadata", "JSON", mode="NULLABLE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("updated_at", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("ingestion_job_id", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("ingestion_timestamp", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("validation_status", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("source_message_timestamp", "TIMESTAMP", mode="NULLABLE"),
    bigquery.SchemaField("persona", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("content_date", "DATE", mode="NULLABLE"),
    bigquery.SchemaField("canonical_form", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("l7_count", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("l6_count", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("l5_count", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("l4_count", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("l3_count", "INTEGER", mode="NULLABLE"),
    bigquery.SchemaField("l2_count", "INTEGER", mode="NULLABLE"),
]


def ensure_entity_unified_table(client: bigquery.Client) -> bigquery.Table:
    """Ensure entity_unified table exists with proper schema."""
    table_ref = bigquery.Table(ENTITY_UNIFIED_TABLE, schema=ENTITY_UNIFIED_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["level", "conversation_id", "entity_id"]
    return client.create_table(table_ref, exists_ok=True)


def get_existing_entity_ids(bq_client: bigquery.Client) -> set[str]:
    """Get existing entity_ids from entity_unified for this source."""
    from shared_validation import validate_table_id

    validated_table = validate_table_id(ENTITY_UNIFIED_TABLE)
    query = f"""
    SELECT DISTINCT entity_id
    FROM `{validated_table}`
    WHERE source_pipeline = '{PIPELINE_NAME}'
    """
    try:
        results = bq_client.query(query).result()
        return {row.entity_id for row in results}
    except Exception as e:
        # ✅ FIXED: Surface error instead of silent suppression
        logger.error(
            "Failed to get existing entity IDs",
            extra={"run_id": get_current_run_id(), "table": validated_table, "error": str(e)},
            exc_info=True
        )
        # SURFACE ERROR TO USER
        print(f"⚠️  WARNING: Failed to get existing entity IDs")
        print(f"   Error: {str(e)}")
        print(f"   Table: {validated_table}")
        print(f"   Returning empty set - may cause duplicates if table exists")
        print(f"   Check logs for technical details")
        
        # Diagnose error
        require_diagnostic_on_error(e, "get_existing_entity_ids")
        
        # Return empty set with warning (allows pipeline to continue)
        return set()


def _derive_entity_type(level: int | None) -> str | None:
    """Derive entity_type from level."""
    if level is None:
        return None
    level_map = {
        2: "word",
        3: "span",
        4: "sentence",
        5: "message",
        6: "turn",
        7: "topic_segment",
        8: "conversation",
    }
    return level_map.get(level)


def _derive_hierarchical_ids(
    entity_id: str | None, level: int | None, parent_id: str | None
) -> dict[str, str | None]:
    """Derive hierarchical IDs based on level and entity_id."""
    result: dict[str, str | None] = {
        "conversation_id": None,
        "topic_segment_id": None,
        "turn_id": None,
        "message_id": None,
        "sentence_id": None,
        "span_id": None,
        "word_id": None,
    }
    
    if level is None or entity_id is None:
        return result
    
    # Map entity_id to appropriate hierarchical ID based on level
    if level == 8:
        result["conversation_id"] = entity_id
    elif level == 7:
        result["topic_segment_id"] = entity_id
    elif level == 6:
        result["turn_id"] = entity_id
    elif level == 5:
        result["message_id"] = entity_id
    elif level == 4:
        result["sentence_id"] = entity_id
    elif level == 3:
        result["span_id"] = entity_id
    elif level == 2:
        result["word_id"] = entity_id
    
    return result


def promote_entities(
    bq_client: bigquery.Client,
    run_id: str,
    include_warnings: bool,
    dry_run: bool,
) -> dict[str, Any]:
    """Promote validated entities to entity_unified with correct schema mapping."""
    import json
    
    now = datetime.now(UTC)
    created_at = now.isoformat()
    ingestion_timestamp = now.isoformat()

    # Validate table IDs to prevent SQL injection
    from shared_validation import validate_table_id

    validated_stage_15_table = validate_table_id(STAGE_15_TABLE)
    validated_entity_unified_table = validate_table_id(ENTITY_UNIFIED_TABLE)

    # Build filter for validation status (safe - no user input)
    if include_warnings:
        status_filter = "validation_status IN ('PASSED', 'WARNING')"
    else:
        status_filter = "validation_status = 'PASSED'"

    # Get entities to promote (with validated table ID)
    query = f"""
    SELECT *
    FROM `{validated_stage_15_table}`
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
        level = entity_dict.get("level")

        # Skip duplicates
        if entity_id in existing_ids:
            skipped += 1
            continue

        # Derive hierarchical IDs
        hierarchical_ids = _derive_hierarchical_ids(
            entity_id, level, entity_dict.get("parent_id")
        )

        # Build metadata JSON with all enrichment data
        metadata_dict = {
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
            "fingerprint": entity_dict.get("fingerprint"),
            "validation_score": entity_dict.get("validation_score"),
            "source_name": entity_dict.get("source_name"),
        }
        # Remove None values for cleaner JSON
        metadata_dict = {k: v for k, v in metadata_dict.items() if v is not None}

        # Get source_file from metadata or entity_dict
        source_file = entity_dict.get("source_file") or metadata_dict.get("source_file")

        # Build record matching actual entity_unified schema
        record = {
            "entity_id": entity_id,
            "level": level,
            "entity_type": _derive_entity_type(level),
            "entity_mode": "active" if entity_dict.get("validation_status") == "PASSED" else "warning",
            "parent_id": entity_dict.get("parent_id"),
            "source_ids": [entity_id] if entity_id else [],  # REPEATED field - array
            "conversation_id": hierarchical_ids["conversation_id"],
            "topic_segment_id": hierarchical_ids["topic_segment_id"],
            "turn_id": hierarchical_ids["turn_id"],
            "message_id": hierarchical_ids["message_id"],
            "sentence_id": hierarchical_ids["sentence_id"],
            "span_id": hierarchical_ids["span_id"],
            "word_id": hierarchical_ids["word_id"],
            "text": entity_dict.get("text"),
            "source_pipeline": entity_dict.get("source_pipeline"),
            "source_file": source_file,
            "source_file_path": source_file,  # Same as source_file for now
            "source_system": SOURCE_NAME,
            "metadata": json.dumps(metadata_dict) if metadata_dict else None,
            "created_at": created_at,
            "updated_at": created_at,
            "ingestion_job_id": run_id,
            "ingestion_timestamp": ingestion_timestamp,
            "validation_status": entity_dict.get("validation_status"),
            "source_message_timestamp": entity_dict.get("timestamp_utc"),
            "persona": None,  # Not available in current pipeline
            "content_date": entity_dict.get("content_date"),
            "canonical_form": None,  # Not available in current pipeline
            "l7_count": entity_dict.get("l7_count"),
            "l6_count": entity_dict.get("l6_count"),
            "l5_count": entity_dict.get("l5_count"),
            "l4_count": entity_dict.get("l4_count"),
            "l3_count": entity_dict.get("l3_count"),
            "l2_count": entity_dict.get("l2_count"),
        }
        records_to_insert.append(record)

        # Insert in batches with duplicate prevention
        if len(records_to_insert) >= 1000:
            from shared import merge_rows_to_table

            try:
                merge_rows_to_table(
                    client=bq_client,
                    table_id=validated_entity_unified_table,
                    rows=records_to_insert,
                    match_key="entity_id",
                )
            except Exception as e:
                # ✅ FIXED: Surface MERGE failure to user
                logger.warning("Unable to merge records, using direct insert instead")
                logger.debug(f"MERGE failed: {e}", exc_info=True)
                
                # SURFACE ERROR TO USER
                print(f"⚠️  WARNING: MERGE operation failed, using direct insert")
                print(f"   Error: {str(e)}")
                print(f"   Records: {len(records_to_insert)}")
                print(f"   This may cause duplicates. Check logs for details.")
                
                # Diagnose error
                require_diagnostic_on_error(e, "merge_rows_to_table_batch")
                
                # Try fallback
                try:
                    errors = bq_client.insert_rows_json(
                        validated_entity_unified_table, records_to_insert
                    )
                    if errors:
                        # ✅ FIXED: Surface insert errors to user
                        error_msg = f"Failed to insert {len(records_to_insert)} entities into production table"
                        logger.error(error_msg)
                        logger.debug(f"Insert errors: {errors[:5]}")
                        
                        # SURFACE INSERT ERRORS TO USER
                        print(f"❌ ERROR: Direct insert failed")
                        print(f"   {error_msg}")
                        print(f"   Errors: {errors[:5]}")
                        print(f"   Check logs for full error details")
                        
                        # Re-raise so user knows
                        raise ValueError(f"Insert failed: {errors[:5]}")
                except Exception as insert_error:
                    # ✅ FIXED: Surface fallback failure
                    print(f"❌ ERROR: Direct insert also failed: {str(insert_error)}")
                    require_diagnostic_on_error(insert_error, "direct_insert_fallback")
                    raise
            records_to_insert = []

    # Insert remaining with duplicate prevention
    if records_to_insert:
        from shared import merge_rows_to_table

        try:
            merge_rows_to_table(
                client=bq_client,
                table_id=validated_entity_unified_table,
                rows=records_to_insert,
                match_key="entity_id",
            )
        except Exception as e:
            # ✅ FIXED: Surface MERGE failure to user
            logger.warning("Unable to merge records, using direct insert instead")
            logger.debug(f"MERGE failed: {e}", exc_info=True)
            
            # SURFACE ERROR TO USER
            print(f"⚠️  WARNING: MERGE operation failed, using direct insert")
            print(f"   Error: {str(e)}")
            print(f"   Records: {len(records_to_insert)}")
            print(f"   This may cause duplicates. Check logs for details.")
            
            # Diagnose error
            require_diagnostic_on_error(e, "merge_rows_to_table_final")
            
            # Try fallback
            try:
                errors = bq_client.insert_rows_json(validated_entity_unified_table, records_to_insert)
                if errors:
                    # ✅ FIXED: Surface insert errors to user
                    error_msg = f"Failed to insert {len(records_to_insert)} entities into production table"
                    logger.error(error_msg)
                    logger.debug(f"Insert errors: {errors[:5]}")
                    
                    # SURFACE INSERT ERRORS TO USER
                    print(f"❌ ERROR: Direct insert failed")
                    print(f"   {error_msg}")
                    print(f"   Errors: {errors[:5]}")
                    print(f"   Check logs for full error details")
                    
                    # Re-raise so user knows
                    raise ValueError(f"Insert failed: {errors[:5]}")
            except Exception as insert_error:
                # ✅ FIXED: Surface fallback failure
                print(f"❌ ERROR: Direct insert also failed: {str(insert_error)}")
                require_diagnostic_on_error(insert_error, "direct_insert_fallback_final")
                raise

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
            logger.error("Failed to promote entities to production table")
            logger.error(f"Error: {e!s}")
            logger.debug(f"Technical details: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_16_promotion")
            return 1


if __name__ == "__main__":
    sys.exit(main())
