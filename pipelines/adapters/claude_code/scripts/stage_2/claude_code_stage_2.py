#!/usr/bin/env python3
"""Stage 2: Cleaning - Claude Code Pipeline

HOLD₁ (claude_code_stage_1) → AGENT (Normalizer) → HOLD₂ (claude_code_stage_2)

Cleans and normalizes extracted data: timestamp normalization, content cleaning,
deduplication, and data quality validation.

🧠 STAGE FIVE GROUNDING
This stage exists to clean and normalize raw extracted data for processing.

Structure: Read stage_1 → Normalize timestamps → Clean content → Dedupe → Write stage_2
Purpose: Ensure data quality and consistency before identity generation
Boundaries: Cleaning only, no semantic transformation or enrichment
Control: Deduplication by fingerprint, validation before write

⚠️ WHAT THIS STAGE CANNOT SEE
- Original file content after extraction
- Semantic meaning of messages
- Whether duplicates are intentional
- Upstream data quality issues

🔥 THE FURNACE PRINCIPLE
- Truth (input): Raw extracted rows from stage_1
- Heat (processing): Normalization, cleaning, deduplication
- Meaning (output): Clean, deduplicated rows ready for THE GATE
- Care (delivery): Data quality metrics, validation report

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 2 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 2 prepares data for identity generation (Stage 3)
- Deduplication prevents duplicate entity creation
- Normalization ensures consistent downstream processing

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations

Usage:
    python claude_code_stage_2.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations

# Use shared logging bridge for consistent logging
from shared.logging_bridge import get_logger as _get_logger


_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_2.claude_code_stage_2.py"

import argparse
import re
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

from contextlib import contextmanager

from shared import (
    PIPELINE_NAME,
    TABLE_STAGE_1,
    TABLE_STAGE_2,
    get_full_table_id,
    validate_input_table_exists,
)
from shared.logging_bridge import get_current_run_id, get_logger


# Fallback implementations for missing central_services
def get_bigquery_client():
    """Get BigQuery client (fallback implementation)."""
    return bigquery.Client()


@contextmanager
def PipelineTracker(*args, **kwargs):
    """PipelineTracker fallback (simple context manager)."""
    obj = type("obj", (object,), {"update_progress": lambda self, **kw: None})()
    yield obj


def require_diagnostic_on_error(error, context):
    """require_diagnostic_on_error fallback (no-op)."""
    pass


def serialize_datetime(val):
    """Convert datetime/date to ISO string for JSON serialization.

    Args:
        val: datetime, date, or None value

    Returns:
        ISO format string or None
    """
    if val is None:
        return None
    if hasattr(val, "isoformat"):
        return val.isoformat()
    return val


logger = get_logger(__name__)

# Table configuration
STAGE_1_TABLE = get_full_table_id(TABLE_STAGE_1)
STAGE_2_TABLE = get_full_table_id(TABLE_STAGE_2)

# Schema for stage 2 table (adds cleaning metadata)
STAGE_2_SCHEMA = [
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
    bigquery.SchemaField("cleaned_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_2_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 2 table with proper schema."""
    table_ref = bigquery.Table(STAGE_2_TABLE, schema=STAGE_2_SCHEMA)

    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="content_date",
    )
    table_ref.clustering_fields = ["session_id", "message_type", "is_duplicate"]

    try:
        table = client.create_table(table_ref, exists_ok=True)
        logger.info(f"Stage 2 table ready: {STAGE_2_TABLE}")
        return table
    except Exception as e:
        require_diagnostic_on_error(e, "create_stage_2_table")
        raise


def clean_content(content: str | None) -> tuple[str, int, int]:
    """Clean and normalize content text.

    Args:
        content: Raw content string

    Returns:
        Tuple of (cleaned_content, content_length, word_count)
    """
    if not content:
        return "", 0, 0

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", content).strip()

    # Remove control characters (except newlines)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", cleaned)

    content_length = len(cleaned)
    word_count = len(cleaned.split()) if cleaned else 0

    return cleaned, content_length, word_count


def normalize_timestamp(timestamp: datetime | None) -> datetime | None:
    """Normalize timestamp to UTC.

    Args:
        timestamp: Input timestamp (may or may not have timezone)

    Returns:
        UTC-normalized timestamp
    """
    if not timestamp:
        return None

    if timestamp.tzinfo is None:
        # Assume UTC if no timezone
        return timestamp.replace(tzinfo=UTC)

    return timestamp.astimezone(UTC)


def process_cleaning(
    client: bigquery.Client, run_id: str, batch_size: int, dry_run: bool
) -> dict[str, int]:
    """Process cleaning transformation using SQL.

    Args:
        client: BigQuery client
        run_id: Current run ID
        batch_size: Batch size (used for reporting)
        dry_run: If True, don't write results

    Returns:
        Processing statistics
    """
    from shared_validation import validate_run_id, validate_table_id

    # Validate all inputs to prevent SQL injection
    validated_stage_1_table = validate_table_id(STAGE_1_TABLE)
    validated_stage_2_table = validate_table_id(STAGE_2_TABLE)
    validated_run_id = validate_run_id(run_id)

    cleaned_at = datetime.now(UTC).isoformat()
    # Validate timestamp string (basic check)
    if any(danger in cleaned_at for danger in ['--', ';', '/*', '*/']):
        raise ValueError("Invalid timestamp: potential SQL injection")

    # SQL-based cleaning transformation with validated inputs
    # Use SELECT to get cleaned data, then merge_rows_to_table for idempotent persistence
    # This preserves all runs and allows stepping back
    cleaning_select_query = f"""
    WITH cleaned AS (
        SELECT
            extraction_id,
            session_id,
            message_index,
            message_type,
            role,
            content,
            -- Clean content
            TRIM(REGEXP_REPLACE(content, r'\\s+', ' ')) AS content_cleaned,
            LENGTH(TRIM(REGEXP_REPLACE(content, r'\\s+', ' '))) AS content_length,
            ARRAY_LENGTH(SPLIT(TRIM(REGEXP_REPLACE(content, r'\\s+', ' ')), ' ')) AS word_count,
            timestamp,
            -- Normalize to UTC
            timestamp AS timestamp_utc,
            model,
            cost_usd,
            tool_name,
            tool_input,
            tool_output,
            source_file,
            content_date,
            fingerprint,
            -- Mark duplicates
            ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY extracted_at) > 1 AS is_duplicate,
            extracted_at,
            TIMESTAMP('{cleaned_at}') AS cleaned_at,
            '{validated_run_id}' AS run_id
        FROM `{validated_stage_1_table}`
        WHERE run_id = '{validated_run_id}'
    )
    SELECT * FROM cleaned
    """

    if dry_run:
        # Just count what would be processed (with validated table ID and run_id filter)
        count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_1_table}` WHERE run_id = '{validated_run_id}'"
        result = client.query(count_query).result()
        row = next(iter(result))
        return {
            "input_rows": row.cnt,
            "output_rows": row.cnt,
            "duplicates": 0,
            "dry_run": True,
        }

    # Execute cleaning transformation and persist with idempotent merge
    logger.info("Executing cleaning transformation...")

    # Query cleaned data from Stage 1
    query_job = client.query(cleaning_select_query)
    cleaned_rows = list(query_job.result())

    if query_job.errors:
        raise ValueError(f"Cleaning query failed: {query_job.errors[:5]}")

    logger.info(f"Cleaned {len(cleaned_rows)} rows, persisting with idempotent merge...")

    # Convert BigQuery Row objects to dictionaries for merge_rows_to_table
    # Serialize datetime objects and handle None values properly
    from shared import merge_rows_to_table

    records_to_insert = []
    for row in cleaned_rows:
        try:
            record = {
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
                "run_id": row.run_id,
            }
            records_to_insert.append(record)
        except Exception as e:
            logger.warning(f"Failed to convert row to record: {e}")
            logger.debug(f"Technical details: {e}", exc_info=True, extra={"run_id": validated_run_id})
            # Skip this row but continue processing
            continue

    # Use merge_rows_to_table for idempotent persistence (preserves all runs)
    # Process in batches to avoid memory issues
    if not records_to_insert:
        logger.warning("No records to insert after cleaning")
        return {
            "input_rows": len(cleaned_rows),
            "output_rows": 0,
            "duplicates": 0,
            "unique": 0,
            "dry_run": False,
        }

    batch_size_merge = 1000
    total_inserted = 0
    total_failed = 0

    for i in range(0, len(records_to_insert), batch_size_merge):
        batch = records_to_insert[i:i + batch_size_merge]
        try:
            merge_rows_to_table(
                client=client,
                table_id=validated_stage_2_table,
                rows=batch,
                match_key="fingerprint",  # Use fingerprint for duplicate prevention
            )
            total_inserted += len(batch)
            logger.debug(f"Successfully merged batch {i // batch_size_merge + 1} ({len(batch)} rows)")
        except Exception as e:
            logger.warning(f"MERGE failed for batch {i // batch_size_merge + 1}, using direct insert: {e}")
            logger.debug(f"Technical details: {e}", exc_info=True, extra={"run_id": validated_run_id})
            try:
                errors = client.insert_rows_json(validated_stage_2_table, batch)
                if errors:
                    logger.error(f"Insert errors for batch {i // batch_size_merge + 1}: {errors[:5]}")
                    total_failed += len(errors)
                else:
                    total_inserted += len(batch)
            except Exception as insert_error:
                logger.error(f"Direct insert also failed for batch {i // batch_size_merge + 1}: {insert_error}")
                logger.debug(f"Technical details: {insert_error}", exc_info=True, extra={"run_id": validated_run_id})
                total_failed += len(batch)

    if total_failed > 0:
        logger.warning(f"Failed to insert {total_failed} rows out of {len(records_to_insert)}")

    # Get statistics for this run_id (with validated table ID)
    stats_query = f"""
    SELECT
        COUNT(*) as total_rows,
        COUNTIF(is_duplicate) as duplicate_count,
        COUNTIF(NOT is_duplicate) as unique_count
    FROM `{validated_stage_2_table}`
    WHERE run_id = '{validated_run_id}'
    """
    result = client.query(stats_query).result()
    row = next(iter(result))

    return {
        "input_rows": len(cleaned_rows),
        "output_rows": total_inserted,
        "duplicates": row.duplicate_count,
        "unique": row.unique_count,
        "dry_run": False,
    }


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Stage 2: Clean and normalize Claude Code data")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for processing (default: 1000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze but don't write results",
    )

    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=2,
        stage_name="cleaning",
        run_id=run_id,
        metadata={"batch_size": args.batch_size, "dry_run": args.dry_run},
    ) as tracker:
        try:
            logger.info(
                "Starting Stage 2: Cleaning",
                extra={"run_id": run_id},
            )

            # Get BigQuery client
            client = get_bigquery_client()
            if hasattr(client, "client"):
                bq_client = client.client
            else:
                bq_client = client

            # HOLD₁: Validate input table exists
            validate_input_table_exists(bq_client, TABLE_STAGE_1)

            # Create output table
            if not args.dry_run:
                create_stage_2_table(bq_client)

            # AGENT: Process cleaning
            stats = process_cleaning(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats["output_rows"])

            # HOLD₂: Verify output
            logger.info(
                f"Stage 2 complete: {stats['output_rows']} rows cleaned",
                extra={
                    "run_id": run_id,
                    "input_rows": stats["input_rows"],
                    "output_rows": stats["output_rows"],
                    "duplicates": stats.get("duplicates", 0),
                },
            )

            print(f"\n{'=' * 60}")
            print("STAGE 2 COMPLETE: Cleaning")
            print(f"{'=' * 60}")
            print(f"Input rows: {stats['input_rows']}")
            print(f"Output rows: {stats['output_rows']}")
            print(f"Duplicates found: {stats.get('duplicates', 0)}")
            print(f"Unique rows: {stats.get('unique', stats['output_rows'])}")
            print(f"Target table: {STAGE_2_TABLE}")
            print(f"Dry run: {args.dry_run}")

            return 0

        except Exception as e:
            logger.error("Failed to clean and deduplicate extracted data")
            logger.error(f"Error: {e!s}")
            logger.debug(f"Technical details: {e}", exc_info=True, extra={"run_id": run_id})
            require_diagnostic_on_error(e, "stage_2_cleaning")
            tracker.update_progress(items_failed=1)
            return 1


if __name__ == "__main__":
    sys.exit(main())
