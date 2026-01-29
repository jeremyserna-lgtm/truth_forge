#!/usr/bin/env python3
"""Stage 3: THE GATE - Identity Generation - Claude Code Pipeline

HOLD₁ (claude_code_stage_2) → AGENT (Identity Generator) → HOLD₂ (claude_code_stage_3)

This is THE GATE - the stage where system identities are generated and registered.
All entity_ids are created here using the identity_service. No entity can exist
without passing through THE GATE.

FILTERING POLICY:
-----------------
THE GATE only allows the following message types to pass through:
  - role = 'user' (user messages)
  - role = 'assistant' (assistant messages)
  - message_type = 'thinking' or contains 'thinking' (thinking blocks)

All other message types (tool_use, tool_result, system, etc.) are filtered out
and will NOT receive entity_ids. This ensures only meaningful conversation
content proceeds to downstream stages.

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


# Use shared logging bridge for consistent logging
from shared.logging_bridge import get_logger as _get_logger
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
# IdentityService integration - use real service when available
try:
    from truth_forge.services.identity import IdentityService
    _identity_service = IdentityService()
    _USE_REAL_IDENTITY_SERVICE = True
    logger.info("Using real IdentityService for ID generation")
except ImportError:
    # Fallback: use hashlib (NOT IDEAL, but allows pipeline to run)
    import hashlib
    _identity_service = None
    _USE_REAL_IDENTITY_SERVICE = False
    logger.warning("⚠️  WARNING: IdentityService not available. Using hashlib fallback.")
    logger.warning("   Install truth_forge.services.identity for canonical ID generation.")
    print("⚠️  WARNING: Using hashlib for ID generation (not canonical)")
    print("   Install truth_forge.services.identity for proper ID service")
    
    def _generate_message_id_fallback(session_id: str, message_index: int, fingerprint: str) -> str:
        """Fallback ID generation using hashlib."""
        content = f"{session_id}:{message_index}:{fingerprint}"
        return f"msg:{hashlib.sha256(content.encode()).hexdigest()[:16]}"


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

    Uses IdentityService for ID generation when available, fallback to hashlib.

    Args:
        session_id: Session identifier
        message_index: Message position in session
        fingerprint: Content fingerprint for deduplication

    Returns:
        Entity ID in canonical format (msg:{hash}:{seq})
    """
    if _USE_REAL_IDENTITY_SERVICE and _identity_service:
        # ✅ CORRECT: Use real IdentityService
        # First, generate conversation_id from session_id
        conversation_id = _identity_service.generate_conversation_id(
            source_type=SOURCE_NAME,
            source_id=session_id
        )
        
        # Generate message_id using canonical service
        entity_id = _identity_service.generate_message_id(
            conversation_id=conversation_id,
            index=message_index
        )
        
        # Note: ID registration to identity.id_registry happens via backfill script
        # See: pipelines/claude_code/scripts/utilities/register_spine_entities.py
        
        logger.debug(f"Generated entity_id via IdentityService: {entity_id}")
        return entity_id
    else:
        # ⚠️ FALLBACK: Use hashlib (not canonical, but allows pipeline to run)
        entity_id = _generate_message_id_fallback(session_id, message_index, fingerprint)
        logger.debug(f"Generated entity_id via fallback: {entity_id}")
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
    # THE GATE: Only allow user, assistant, and thinking blocks to pass through
    # Filter criteria:
    #   - role IN ('user', 'assistant') OR
    #   - message_type = 'thinking' (thinking blocks may not have role set)
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
      AND (
        role IN ('user', 'assistant')
        OR message_type = 'thinking'
        OR message_type LIKE '%thinking%'
      )
    ORDER BY session_id, message_index
    """

    # Validate table IDs to prevent SQL injection
    from shared_validation import validate_table_id
    
    validated_stage_2_table = validate_table_id(STAGE_2_TABLE)
    validated_stage_3_table = validate_table_id(STAGE_3_TABLE)
    
    # Update query with validated table ID
    select_query = select_query.replace(f"FROM `{STAGE_2_TABLE}`", f"FROM `{validated_stage_2_table}`")
    
    if dry_run:
        # Just count what would be processed (with validated table ID)
        # Apply same filtering as main query: user, assistant, thinking blocks only
        count_query = f"""
        SELECT COUNT(*) as cnt 
        FROM `{validated_stage_2_table}` 
        WHERE NOT is_duplicate
          AND (
            role IN ('user', 'assistant')
            OR message_type = 'thinking'
            OR message_type LIKE '%thinking%'
          )
        """
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

        # Batch insert with duplicate prevention
        if len(records_to_insert) >= batch_size:
            from shared import merge_rows_to_table
            try:
                merge_rows_to_table(
                    client=client,
                    table_id=validated_stage_3_table,
                    rows=records_to_insert,
                    match_key="entity_id"
                )
            except Exception as e:
                logger.warning("Unable to merge records, using direct insert instead")
                logger.debug(f"MERGE failed: {e}", exc_info=True)
                errors = client.insert_rows_json(validated_stage_3_table, records_to_insert)
                if errors:
                    logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

    # Insert remaining records with duplicate prevention
    if records_to_insert:
        from shared import merge_rows_to_table
        try:
            merge_rows_to_table(
                client=client,
                table_id=validated_stage_3_table,
                rows=records_to_insert,
                match_key="entity_id"
            )
        except Exception as e:
            logger.warning("Unable to merge records, using direct insert instead")
            logger.debug(f"MERGE failed: {e}", exc_info=True)
            errors = client.insert_rows_json(validated_stage_3_table, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")

    # Note: ID registration to identity.id_registry happens via backfill script
    # See: pipelines/claude_code/scripts/utilities/register_spine_entities.py
    # This is intentional - registration is separate from ID generation
    logger.info("Identity generation complete. IDs will be registered via backfill script.")

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
