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
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_4.claude_code_stage_4.py"

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
    LEVEL_MESSAGE,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_3,
    TABLE_STAGE_4,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import (
    require_diagnostic_on_error,
)


logger = get_logger(__name__)

# Table configuration
STAGE_3_TABLE = get_full_table_id(TABLE_STAGE_3)
STAGE_4_TABLE = get_full_table_id(TABLE_STAGE_4)


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
    """Transform data to SPINE format.

    Args:
        client: BigQuery client
        run_id: Current run ID
        dry_run: If True, don't write results

    Returns:
        Processing statistics
    """
    created_at = datetime.now(UTC).isoformat()

    # SQL transformation to SPINE format
    staging_query = f"""
    CREATE OR REPLACE TABLE `{STAGE_4_TABLE}` AS
    SELECT
        entity_id,
        CAST(NULL AS STRING) AS parent_id,  -- L5 messages have no parent yet
        '{SOURCE_NAME}' AS source_name,
        '{PIPELINE_NAME}' AS source_pipeline,
        {LEVEL_MESSAGE} AS level,  -- L5 = Message level
        content_cleaned AS text,
        session_id,
        message_index,
        message_type,
        role,
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
        TIMESTAMP('{created_at}') AS created_at,
        TO_JSON_STRING(STRUCT(
            session_id,
            message_index,
            message_type,
            role,
            model,
            cost_usd,
            tool_name
        )) AS metadata,
        fingerprint,
        '{run_id}' AS run_id
    FROM `{STAGE_3_TABLE}`
    """

    if dry_run:
        count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_3_TABLE}`"
        result = client.query(count_query).result()
        row = next(iter(result))
        return {"input_rows": row.cnt, "output_rows": row.cnt, "dry_run": True}

    logger.info("Executing SPINE staging transformation...")
    job = client.query(staging_query)
    job.result()

    # Get output count
    count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_4_TABLE}`"
    result = client.query(count_query).result()
    row = next(iter(result))

    return {"input_rows": row.cnt, "output_rows": row.cnt, "dry_run": False}


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
            print("STAGE 4 COMPLETE: Staging")
            print(f"{'=' * 60}")
            print(f"Rows staged: {stats['output_rows']}")
            print(f"Target table: {STAGE_4_TABLE}")
            print(f"Dry run: {args.dry_run}")

            return 0

        except Exception as e:
            logger.error(f"Stage 4 failed: {e}", exc_info=True, extra={"run_id": run_id})
            require_diagnostic_on_error(e, "stage_4_staging")
            tracker.update_progress(items_failed=1)
            return 1


if __name__ == "__main__":
    sys.exit(main())
