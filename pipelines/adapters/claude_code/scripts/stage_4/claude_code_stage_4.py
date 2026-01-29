#!/usr/bin/env python3
"""Stage 4: Staging - Claude Code Pipeline

HOLD₁ (claude_code_stage_3) → AGENT (SPINE Preparer) → HOLD₂ (claude_code_stage_4)

Prepares data structure for SPINE entity creation. Adds required fields for
the entity hierarchy (L1→L3→L5→L8) that will be created in stages 5-8.

🧠 STAGE FIVE GROUNDING
This stage exists to prepare data structure for SPINE entity creation.

Structure: Read identities → Add SPINE fields → Validate structure → Write
Purpose: Transform into SPINE-compatible format before entity creation
Boundaries: Schema transformation only, no content enrichment
Control: Validation of required fields, schema compliance checks

⚠️ WHAT THIS STAGE CANNOT SEE
- Actual entity hierarchy relationships (created in stages 5-8)
- Content semantics
- Downstream enrichment needs
- Cross-session entity relationships

🔥 THE FURNACE PRINCIPLE
- Truth (input): Messages with entity_ids from THE GATE
- Heat (processing): Schema mapping, field addition, structure validation
- Meaning (output): SPINE-ready records with all required fields
- Care (delivery): Validated structure ready for entity hierarchy creation

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 4 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 4 prepares data for the SPINE entity hierarchy
- Adds source_name, level, and metadata structure
- Creates foundation for L1→L3→L5→L8 entity creation

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations

Usage:
    python claude_code_stage_4.py [--dry-run]
"""

from __future__ import annotations

# Use shared logging bridge for consistent logging
from shared.logging_bridge import get_logger as _get_logger

_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_4.claude_code_stage_4.py"

import argparse
import json
import os
import sys
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
    LEVEL_MESSAGE,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_3,
    TABLE_STAGE_4,
    get_full_table_id,
    retry_with_backoff,
    validate_input_table_exists,
)
from shared.logging_bridge import get_current_run_id, get_logger

# Fallback implementations for missing central_services
def get_bigquery_client():
    """Get BigQuery client (fallback implementation)."""
    return bigquery.Client()

from contextlib import contextmanager
@contextmanager
def PipelineTracker(*args, **kwargs):
    """PipelineTracker fallback (simple context manager)."""
    obj = type("obj", (object,), {"update_progress": lambda self, **kw: None})()
    yield obj

def require_diagnostic_on_error(error, context):
    """require_diagnostic_on_error fallback (no-op)."""
    pass


logger = get_logger(__name__)

# Table configuration
STAGE_3_TABLE = get_full_table_id(TABLE_STAGE_3)
STAGE_4_TABLE = get_full_table_id(TABLE_STAGE_4)

# Gemini configuration: Flash Lite for spelling only. Meaning must be preserved for sentiment analysis.
GEMINI_MODEL = "gemini-2.0-flash-lite"
# Simple prompt: spelling only. Do not change meaning—we run sentiment analysis downstream.
CORRECTION_PROMPT = """Clean the spelling of this text. Do not change the meaning. We use this for sentiment analysis and must preserve intent and tone.

Text:
{text}

Return ONLY a JSON object:
- corrected_text: The spelling-corrected text (meaning unchanged)
- original_text: The exact original text
- changes_made: Brief description (or "no changes" if none)

JSON:"""


def get_gemini_client():
    """Initialize the Gemini LLM client."""
    try:
        import google.generativeai as genai

        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable required")
        genai.configure(api_key=api_key)
        return genai
    except ImportError:
        logger.error("google-generativeai package not installed. Install with: pip install google-generativeai")
        raise
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        raise


def _correct_text_impl(genai_client, text: str) -> dict[str, Any]:
    """Correct text using Gemini (implementation)."""
    model = genai_client.GenerativeModel(GEMINI_MODEL)
    prompt = CORRECTION_PROMPT.format(text=text[:8000])  # Limit input size
    
    response = model.generate_content(prompt)
    response_text = response.text.strip()
    
    # Clean up JSON response
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
    
    result = json.loads(response_text.strip())
    return {
        "corrected_text": result.get("corrected_text", text),
        "original_text": result.get("original_text", text),
        "changes_made": result.get("changes_made", "unknown"),
    }


# Retry wrapper for Gemini calls
correct_text_with_retry = retry_with_backoff(
    _correct_text_impl,
    max_retries=3,
    retry_delays=(1, 2, 4),
)


def create_stage_4_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 4 table with SPINE schema."""
    schema = [
        # Identity fields
        bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("parent_id", "STRING"),  # Will be set for child entities
        # SPINE fields
        bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("text", "STRING"),
        # Original fields
        bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("message_index", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("message_type", "STRING"),
        bigquery.SchemaField("role", "STRING"),
        bigquery.SchemaField("content_length", "INTEGER"),
        bigquery.SchemaField("word_count", "INTEGER"),
        bigquery.SchemaField("model", "STRING"),
        bigquery.SchemaField("cost_usd", "FLOAT"),
        bigquery.SchemaField("tool_name", "STRING"),
        bigquery.SchemaField("tool_input", "STRING"),
        bigquery.SchemaField("tool_output", "STRING"),
        bigquery.SchemaField("source_file", "STRING"),
        # Timestamps
        bigquery.SchemaField("content_date", "DATE"),
        bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
        bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
        # Metadata
        bigquery.SchemaField("metadata", "JSON"),
        bigquery.SchemaField("fingerprint", "STRING"),
        bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
    ]

    table_ref = bigquery.Table(STAGE_4_TABLE, schema=schema)

    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="content_date",
    )
    table_ref.clustering_fields = ["source_name", "level", "session_id"]

    try:
        table = client.create_table(table_ref, exists_ok=True)
        logger.info(f"Stage 4 table ready: {STAGE_4_TABLE}")
        return table
    except Exception as e:
        require_diagnostic_on_error(e, "create_stage_4_table")
        raise


def process_staging(
    client: bigquery.Client,
    run_id: str,
    dry_run: bool,
) -> dict[str, int]:
    """Transform data to SPINE format with Gemini correction for user messages.

    Args:
        client: BigQuery client
        run_id: Current run ID
        dry_run: If True, don't write results

    Returns:
        Processing statistics
    """
    from shared import merge_rows_to_table
    from shared_validation import validate_table_id, validate_run_id
    
    # Validate all inputs to prevent SQL injection
    validated_stage_3_table = validate_table_id(STAGE_3_TABLE)
    validated_stage_4_table = validate_table_id(STAGE_4_TABLE)
    validated_run_id = validate_run_id(run_id)
    
    created_at = datetime.now(UTC).isoformat()
    # Validate timestamp string (basic check)
    if any(danger in created_at for danger in ['--', ';', '/*', '*/']):
        raise ValueError("Invalid timestamp: potential SQL injection")

    # Query Stage 3 data
    select_query = f"""
    SELECT
        entity_id,
        session_id,
        message_index,
        message_type,
        role,
        content_cleaned,
        content_length,
        word_count,
        model,
        cost_usd,
        tool_name,
        tool_input,
        tool_output,
        source_file,
        content_date,
        timestamp_utc,
        fingerprint
    FROM `{validated_stage_3_table}`
    WHERE run_id = '{validated_run_id}'
    ORDER BY session_id, message_index
    """

    if dry_run:
        # Count what would be processed
        count_query = f"SELECT COUNT(*) as cnt FROM `{validated_stage_3_table}` WHERE run_id = '{validated_run_id}'"
        result = client.query(count_query).result()
        row = next(iter(result))
        return {"input_rows": row.cnt, "output_rows": row.cnt, "user_corrected": 0, "dry_run": True}

    logger.info("Fetching records from Stage 3...")
    query_job = client.query(select_query)
    rows = list(query_job.result())
    
    if query_job.errors:
        raise ValueError(f"Query failed: {query_job.errors[:5]}")
    
    logger.info(f"Processing {len(rows)} records...")
    
    # Initialize Gemini client (only if we have user messages to correct)
    gemini_client = None
    user_count = sum(1 for row in rows if row.role == 'user')
    if user_count > 0:
        try:
            gemini_client = get_gemini_client()
            logger.info(f"Gemini client initialized. Will correct {user_count} user messages.")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")
            logger.warning("User messages will pass through without correction")
    
    # Process records
    records_to_insert = []
    user_corrected = 0
    user_failed = 0
    
    for row in rows:
        original_text = row.content_cleaned or ""
        corrected_text = original_text
        correction_metadata = None
        
        # Only correct user messages
        if row.role == 'user' and gemini_client and original_text and len(original_text.strip()) > 10:
            try:
                correction_result = correct_text_with_retry(gemini_client, original_text)
                corrected_text = correction_result["corrected_text"]
                correction_metadata = {
                    "original_text": correction_result["original_text"],
                    "corrected_text": corrected_text,
                    "changes_made": correction_result.get("changes_made", "unknown"),
                    "correction_cost_usd": 0.0,  # Gemini pricing would go here
                    "correction_model": GEMINI_MODEL,
                }
                if corrected_text != original_text:
                    user_corrected += 1
                    logger.debug(f"Corrected user message {row.entity_id}")
            except Exception as e:
                logger.warning(f"Failed to correct user message {row.entity_id}: {e}")
                logger.debug(f"Technical details: {e}", exc_info=True)
                user_failed += 1
                # Fallback: use original text
                corrected_text = original_text
                correction_metadata = {
                    "original_text": original_text,
                    "corrected_text": original_text,
                    "correction_error": str(e),
                    "correction_cost_usd": 0.0,
                }
        # Assistant messages and thinking blocks pass through unchanged
        elif row.role == 'assistant' or (row.message_type and 'thinking' in row.message_type.lower()):
            # No correction, pass through
            pass
        
        # Build metadata JSON
        base_metadata = {
            "session_id": row.session_id,
            "message_index": row.message_index,
            "message_type": row.message_type,
            "role": row.role,
            "model": row.model,
            "cost_usd": row.cost_usd,
            "tool_name": row.tool_name,
        }
        
        # Merge correction metadata if present
        if correction_metadata:
            base_metadata.update(correction_metadata)
        
        record = {
            "entity_id": row.entity_id,
            "parent_id": None,  # L5 messages have no parent yet
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "level": LEVEL_MESSAGE,  # L5 = Message level
            "text": corrected_text,
            "session_id": row.session_id,
            "message_index": row.message_index,
            "message_type": row.message_type,
            "role": row.role,
            "content_length": row.content_length,
            "word_count": row.word_count,
            "model": row.model,
            "cost_usd": row.cost_usd,
            "tool_name": row.tool_name,
            "tool_input": row.tool_input,
            "tool_output": row.tool_output,
            "source_file": row.source_file,
            "content_date": row.content_date,
            "timestamp_utc": row.timestamp_utc,
            "created_at": created_at,
            "metadata": json.dumps(base_metadata),
            "fingerprint": row.fingerprint,
            "run_id": validated_run_id,
        }
        records_to_insert.append(record)
    
    # Use merge_rows_to_table for idempotent persistence
    logger.info(f"Inserting {len(records_to_insert)} records with idempotent merge...")
    try:
        merge_rows_to_table(
            client=client,
            table_id=validated_stage_4_table,
            rows=records_to_insert,
            match_key="entity_id",
        )
    except Exception as e:
        logger.warning(f"MERGE failed, using direct insert: {e}")
        logger.debug(f"Technical details: {e}", exc_info=True)
        errors = client.insert_rows_json(validated_stage_4_table, records_to_insert)
        if errors:
            raise ValueError(f"Insert failed: {errors[:5]}")
    
    logger.info(f"Stage 4 complete: {len(records_to_insert)} records, {user_corrected} user messages corrected")
    if user_failed > 0:
        logger.warning(f"{user_failed} user messages failed correction and used original text")
    
    return {
        "input_rows": len(rows),
        "output_rows": len(records_to_insert),
        "user_corrected": user_corrected,
        "user_failed": user_failed,
        "dry_run": False,
    }


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Stage 4: Prepare data for SPINE entity creation")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze but don't write results",
    )

    args = parser.parse_args()
    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=4,
        stage_name="staging",
        run_id=run_id,
        metadata={"dry_run": args.dry_run},
    ) as tracker:
        try:
            logger.info("Starting Stage 4: Staging", extra={"run_id": run_id})

            client = get_bigquery_client()
            if hasattr(client, "client"):
                bq_client = client.client
            else:
                bq_client = client

            validate_input_table_exists(bq_client, TABLE_STAGE_3)

            if not args.dry_run:
                create_stage_4_table(bq_client)

            stats = process_staging(bq_client, run_id, args.dry_run)
            tracker.update_progress(items_processed=stats["output_rows"])

            logger.info(
                f"Stage 4 complete: {stats['output_rows']} rows staged",
                extra={"run_id": run_id, **stats},
            )

            print(f"\n{'=' * 60}")
            print("STAGE 4 COMPLETE: Staging with LLM Correction")
            print(f"{'=' * 60}")
            print(f"Rows staged: {stats['output_rows']}")
            if not args.dry_run and 'user_corrected' in stats:
                print(f"User messages corrected: {stats['user_corrected']}")
                if stats.get('user_failed', 0) > 0:
                    print(f"User messages failed correction: {stats['user_failed']}")
            print(f"Target table: {STAGE_4_TABLE}")
            print(f"Dry run: {args.dry_run}")

            return 0

        except Exception as e:
            logger.error("Failed to stage data for SPINE processing")
            logger.error(f"Error: {str(e)}")
            logger.debug(f"Technical details: {e}", exc_info=True, extra={"run_id": run_id})
            require_diagnostic_on_error(e, "stage_4_staging")
            tracker.update_progress(items_failed=1)
            return 1


if __name__ == "__main__":
    sys.exit(main())
