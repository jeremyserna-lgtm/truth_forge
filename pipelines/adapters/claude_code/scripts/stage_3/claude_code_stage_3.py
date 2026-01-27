#!/usr/bin/env python3
"""Stage 3: THE GATE - Identity Generation - Claude Code Pipeline

HOLD₁ (claude_code_stage_2) → AGENT (Identity Generator) → HOLD₂ (claude_code_stage_3)

This is THE GATE - the stage where system identities are generated and registered.
All entity_ids are created here using the identity_service. No entity can exist
without passing through THE GATE.

🧠 STAGE FIVE GROUNDING
This stage exists to generate and register stable entity_ids for all messages.

Structure: Read cleaned data → Generate entity_ids → Register with identity_service → Write
Purpose: Create stable, deduplicated identities for all entities in the pipeline
Boundaries: Identity generation only, no content transformation
Control: identity_service for all ID operations, validation of uniqueness

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether entity already exists in entity_unified (checked at Stage 16)
- Downstream enrichment requirements
- Cross-pipeline entity matches
- Future identity requirements

🔥 THE FURNACE PRINCIPLE
- Truth (input): Cleaned messages without stable system IDs
- Heat (processing): Deterministic ID generation, registry synchronization
- Meaning (output): Messages with registered entity_ids ready for SPINE creation
- Care (delivery): IDs are stable, deterministic, deduplicated, and registered

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 3 (THE GATE) of the Universal Pipeline Pattern.

RATIONALE:
----------
- THE GATE is where identities are born
- All entity_ids must be generated via identity_service
- Enables deduplication across pipeline runs
- Creates foundation for entity relationships

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses identity_service for all ID generation (MANDATORY)
- All operations follow universal governance policies
- Full audit trail for all ID registrations

Usage:
    python claude_code_stage_3.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_3.claude_code_stage_3.py"

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

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
    SOURCE_NAME,
    TABLE_STAGE_2,
    TABLE_STAGE_3,
    get_full_table_id,
    validate_gate_no_null_identity,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import (
    require_diagnostic_on_error,
)
from src.services.central_services.identity_service.service import (
    generate_message_id_from_guid,
    register_id,
    sync_to_bigquery,
)


logger = get_logger(__name__)


def serialize_datetime(val):
    """Convert datetime/date to ISO string for JSON serialization."""
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return val


# Table configuration
STAGE_2_TABLE = get_full_table_id(TABLE_STAGE_2)
STAGE_3_TABLE = get_full_table_id(TABLE_STAGE_3)

# Schema for stage 3 table (adds entity_id)
STAGE_3_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),  # THE GATE output
    bigquery.SchemaField("extraction_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("message_index", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("message_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("role", "STRING"),
    bigquery.SchemaField("content", "STRING"),
    bigquery.SchemaField("content_cleaned", "STRING"),
    bigquery.SchemaField("content_length", "INTEGER"),
    bigquery.SchemaField("word_count", "INTEGER"),
    bigquery.SchemaField("timestamp", "TIMESTAMP"),
    bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("cost_usd", "FLOAT"),
    bigquery.SchemaField("tool_name", "STRING"),
    bigquery.SchemaField("tool_input", "STRING"),
    bigquery.SchemaField("tool_output", "STRING"),
    bigquery.SchemaField("source_file", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("fingerprint", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("is_duplicate", "BOOLEAN"),
    bigquery.SchemaField("extracted_at", "TIMESTAMP"),
    bigquery.SchemaField("cleaned_at", "TIMESTAMP"),
    bigquery.SchemaField("identity_created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_3_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 3 table with proper schema."""
    table_ref = bigquery.Table(STAGE_3_TABLE, schema=STAGE_3_SCHEMA)

    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="content_date",
    )
    table_ref.clustering_fields = ["entity_id", "session_id"]

    try:
        table = client.create_table(table_ref, exists_ok=True)
        logger.info(f"Stage 3 table ready: {STAGE_3_TABLE}")
        return table
    except Exception as e:
        require_diagnostic_on_error(e, "create_stage_3_table")
        raise


def generate_entity_id(session_id: str, message_index: int, fingerprint: str) -> str:
    """Generate deterministic entity_id for Claude Code message.

    Uses identity_service for ID generation and registration.

    Args:
        session_id: Session identifier
        message_index: Message position in session
        fingerprint: Content fingerprint for deduplication

    Returns:
        32-character entity_id
    """
    # Create GUID from stable components
    guid = f"{SOURCE_NAME}:{session_id}:{message_index}:{fingerprint[:12]}"

    # Generate via identity_service
    entity_id = generate_message_id_from_guid(guid, message_index)

    # Register with central registry
    register_id(
        id_str=entity_id,
        metadata={
            "entity_type": f"{SOURCE_NAME}_message",
            "generation_method": "guid_based",
            "context_data": {
                "pipeline": PIPELINE_NAME,
                "session_id": session_id,
                "message_index": message_index,
                "fingerprint": fingerprint,
            },
            "stable": True,
            "first_requestor": f"{PIPELINE_NAME}_stage_3",
        },
    )

    return entity_id


def process_identity_generation(
    client: bigquery.Client,
    run_id: str,
    batch_size: int,
    dry_run: bool,
) -> dict[str, int]:
    """Process identity generation for all messages.

    Args:
        client: BigQuery client
        run_id: Current run ID
        batch_size: Batch size for processing
        dry_run: If True, don't write results

    Returns:
        Processing statistics
    """
    identity_created_at = datetime.now(UTC).isoformat()

    # First, get records that need identity generation
    # Only process non-duplicates from stage 2
    select_query = f"""
    SELECT
        extraction_id,
        session_id,
        message_index,
        message_type,
        role,
        content,
        content_cleaned,
        content_length,
        word_count,
        timestamp,
        timestamp_utc,
        model,
        cost_usd,
        tool_name,
        tool_input,
        tool_output,
        source_file,
        content_date,
        fingerprint,
        is_duplicate,
        extracted_at,
        cleaned_at
    FROM `{STAGE_2_TABLE}`
    WHERE NOT is_duplicate
    ORDER BY session_id, message_index
    """

    if dry_run:
        # Just count what would be processed
        count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_2_TABLE}` WHERE NOT is_duplicate"
        result = client.query(count_query).result()
        row = next(iter(result))
        return {
            "input_rows": row.cnt,
            "ids_generated": row.cnt,
            "ids_registered": 0,
            "dry_run": True,
        }

    logger.info("Fetching records for identity generation...")
    query_job = client.query(select_query)

    # FIX: Stream results with small page_size to avoid "Response too large" error
    # BigQuery has ~21MB response limit per page. With large content fields,
    # we need small pages to stay under the limit.
    logger.info("Streaming records through THE GATE...")

    # Generate entity_ids and prepare records
    records_to_insert = []
    ids_registered = 0
    rows_processed = 0

    # Stream results with page_size=100 to avoid response size limit
    for row in query_job.result(page_size=100):
        # Generate entity_id via identity_service
        entity_id = generate_entity_id(
            session_id=row.session_id,
            message_index=row.message_index,
            fingerprint=row.fingerprint,
        )
        ids_registered += 1
        rows_processed += 1

        record = {
            "entity_id": entity_id,
            "extraction_id": row.extraction_id,
            "session_id": row.session_id,
            "message_index": row.message_index,
            "message_type": row.message_type,
            "role": row.role,
            "content": row.content,
            "content_cleaned": row.content_cleaned,
            "content_length": row.content_length,
            "word_count": row.word_count,
            "timestamp": serialize_datetime(row.timestamp),
            "timestamp_utc": serialize_datetime(row.timestamp_utc),
            "model": row.model,
            "cost_usd": row.cost_usd,
            "tool_name": row.tool_name,
            "tool_input": row.tool_input,
            "tool_output": row.tool_output,
            "source_file": row.source_file,
            "content_date": serialize_datetime(row.content_date),
            "fingerprint": row.fingerprint,
            "is_duplicate": row.is_duplicate,
            "extracted_at": serialize_datetime(row.extracted_at),
            "cleaned_at": serialize_datetime(row.cleaned_at),
            "identity_created_at": identity_created_at,
            "run_id": run_id,
        }
        records_to_insert.append(record)

        # Batch insert
        if len(records_to_insert) >= batch_size:
            errors = client.insert_rows_json(STAGE_3_TABLE, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

    # Insert remaining records
    if records_to_insert:
        errors = client.insert_rows_json(STAGE_3_TABLE, records_to_insert)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")

    # Sync identity registry to BigQuery
    logger.info("Syncing identity registry to BigQuery...")
    try:
        sync_to_bigquery()
    except Exception as e:
        logger.warning(f"Identity sync warning (non-fatal): {e}")

    return {
        "input_rows": rows_processed,
        "ids_generated": rows_processed,
        "ids_registered": ids_registered,
        "dry_run": False,
    }


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Stage 3: THE GATE - Generate entity identities")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for processing (default: 1000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count records but don't generate IDs",
    )

    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=3,
        stage_name="identity_gate",
        run_id=run_id,
        metadata={"batch_size": args.batch_size, "dry_run": args.dry_run},
    ) as tracker:
        try:
            logger.info(
                "Starting Stage 3: THE GATE - Identity Generation",
                extra={"run_id": run_id},
            )

            # Get BigQuery client
            client = get_bigquery_client()
            if hasattr(client, "client"):
                bq_client = client.client
            else:
                bq_client = client

            # HOLD₁: Validate input table exists
            validate_input_table_exists(bq_client, TABLE_STAGE_2)

            # Create output table
            if not args.dry_run:
                create_stage_3_table(bq_client)

            # AGENT: Process identity generation
            stats = process_identity_generation(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats["ids_generated"])

            # HOLD₂: Validate THE GATE - no null entity_ids allowed
            if not args.dry_run:
                validate_gate_no_null_identity(bq_client, TABLE_STAGE_3, "entity_id")

            logger.info(
                f"Stage 3 (THE GATE) complete: {stats['ids_generated']} identities generated",
                extra={
                    "run_id": run_id,
                    "ids_generated": stats["ids_generated"],
                    "ids_registered": stats["ids_registered"],
                },
            )

            print(f"\n{'=' * 60}")
            print("STAGE 3 COMPLETE: THE GATE - Identity Generation")
            print(f"{'=' * 60}")
            print(f"Input rows: {stats['input_rows']}")
            print(f"Entity IDs generated: {stats['ids_generated']}")
            print(f"IDs registered with identity_service: {stats['ids_registered']}")
            print(f"Target table: {STAGE_3_TABLE}")
            print(f"Dry run: {args.dry_run}")

            return 0

        except Exception as e:
            logger.error(
                f"Stage 3 (THE GATE) failed: {e}",
                exc_info=True,
                extra={"run_id": run_id},
            )
            require_diagnostic_on_error(e, "stage_3_identity_gate")
            tracker.update_progress(items_failed=1)
            return 1


if __name__ == "__main__":
    sys.exit(main())
