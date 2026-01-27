#!/usr/bin/env python3
"""
Stage 6: Write to entity_unified (Final Destination) - Claude Code/Codex/Github Pipeline

HOLD₁ (BigQuery claude_code_stage_5) → AGENT (Unify & Write) → HOLD₂ (BigQuery entity_unified)

Writes processed messages to entity_unified table as the final destination.
This is the last stage where all processed messages are unified into the central entity table.

🧠 STAGE FIVE GROUNDING
This stage exists to write processed messages to entity_unified, the central destination for all processed entities.

Structure: Read Stage 5 → Transform to entity_unified format → Write to entity_unified (sequential flow)
Purpose: Write all processed messages to entity_unified (final destination)
Boundaries: Only writes to entity_unified, uses entity_unified schema
Control: Validates input exists, uses entity_unified schema, tracks write statistics

⚠️ WHAT THIS STAGE CANNOT SEE
- Message content meaning or context beyond what's in Stage 5
- Relationships between entities beyond what's in Stage 5
- Future processing needs beyond entity_unified storage

🔥 THE FURNACE PRINCIPLE
- Truth (input): Processed messages from Stage 5 (ready for storage)
- Heat (processing): Transform to entity_unified format, write to BigQuery
- Meaning (output): Messages stored in entity_unified (final destination)
- Care (delivery): Data with complete processing history ready for TruthService

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical final stage specification for the Claude Code/Codex/Github Pipeline.

RATIONALE:
----------
- Stage 5 has ready messages with all processing complete
- Stage 6 writes these to entity_unified (final destination)
- entity_unified is the central table where all processed entities are stored
- This completes the pipeline: source → processing → entity_unified

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses entity_unified schema for consistency
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
"""
from __future__ import annotations

#!/usr/bin/env python3
"""
Stage 6: Write to entity_unified (Final Destination) - Claude Code/Codex/Github Pipeline

HOLD₁ (BigQuery claude_code_stage_5) → AGENT (Unify & Write) → HOLD₂ (BigQuery entity_unified)

Writes processed messages to entity_unified table as the final destination.
This is the last stage where all processed messages are unified into the central entity table.

🧠 STAGE FIVE GROUNDING
This stage exists to write processed messages to entity_unified, the central destination for all processed entities.

Structure: Read Stage 5 → Transform to entity_unified format → Write to entity_unified (sequential flow)
Purpose: Write all processed messages to entity_unified (final destination)
Boundaries: Only writes to entity_unified, uses entity_unified schema
Control: Validates input exists, uses entity_unified schema, tracks write statistics

⚠️ WHAT THIS STAGE CANNOT SEE
- Message content meaning or context beyond what's in Stage 5
- Relationships between entities beyond what's in Stage 5
- Future processing needs beyond entity_unified storage

🔥 THE FURNACE PRINCIPLE
- Truth (input): Processed messages from Stage 5 (ready for storage)
- Heat (processing): Transform to entity_unified format, write to BigQuery
- Meaning (output): Messages stored in entity_unified (final destination)
- Care (delivery): Data with complete processing history ready for TruthService

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical final stage specification for the Claude Code/Codex/Github Pipeline.

RATIONALE:
----------
- Stage 5 has ready messages with all processing complete
- Stage 6 writes these to entity_unified (final destination)
- entity_unified is the central table where all processed entities are stored
- This completes the pipeline: source → processing → entity_unified

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses entity_unified schema for consistency
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts._deprecated.stage_6.claude_code_stage_6.py"

import argparse
import gc
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# pandas is used for DataFrame operations
try:
    import pandas as pd
except ImportError:
    pd = None
from google.cloud import bigquery

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

# 🎓 LEARNING: Central Services Integration
# All stages MUST use central services for logging, governance, and identity
from src.services.central_services.core import (
    get_correlation_ids,
    get_current_run_id,
    get_logger,
)
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import (
    get_unified_governance,
    require_diagnostic_on_error,
)

# Initialize logger (NOT print())
logger = get_logger(__name__)

# Configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
TABLE_STAGE_5 = "claude_code_stage_5"
ENTITY_UNIFIED_TABLE = f"{PROJECT_ID}.{DATASET_ID}.entity_unified"

def write_to_entity_unified(
    run_id: str,
    correlation_ids: dict,
    limit: Optional[int] = None,
) -> dict:
    """Write processed messages from Stage 5 to entity_unified.

    🎓 LEARNING: Final Destination Pattern
    entity_unified is the central destination where all processed entities are stored.
    This stage completes the pipeline by writing all processed messages to this table.

    Args:
        run_id: Current run ID for traceability
        correlation_ids: Correlation IDs for distributed tracing
        limit: Optional limit on number of messages to process

    Returns:
        dict with write stats
    """
    start_time = time.time()
    stats = {
        "status": "in_progress",
        "rows_read": 0,
        "rows_processed": 0,
        "rows_written": 0,
        "errors": 0,
        "duration_seconds": 0,
    }

    governance = get_unified_governance()

    try:
        # Read data from Stage 5
        logger.info(
            f"Reading data from Stage 5: {PROJECT_ID}.{DATASET_ID}.{TABLE_STAGE_5}",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_6",
                "operation": "read_stage_5",
                "project_id": PROJECT_ID,
                "dataset_id": DATASET_ID,
                "table_id": TABLE_STAGE_5,
            },
        )

        # Get BigQuery client - use direct client for compatibility
        from google.cloud import bigquery as bq
        bq_client = bq.Client(project=PROJECT_ID)

        # Build query to read from Stage 5
        limit_clause = f"LIMIT {limit}" if limit else ""

        query = f"""
        SELECT
            entity_id,
            source_name,
            text,
            original_text,
            run_id as stage_5_run_id,
            created_at
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_STAGE_5}`
        ORDER BY created_at DESC
        {limit_clause}
        """

        logger.info(
            "Executing query to read Stage 5 data",
            extra={
                "run_id": run_id,
                "query_length": len(query),
                "limit": limit,
            }
        )

        # Execute query and get results
        try:
            query_job = bq_client.query(query)
            df = query_job.to_dataframe()
            stats["rows_read"] = len(df)
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e):
                logger.warning(
                    f"Stage 5 table does not exist - pipeline will complete with 0 messages: {e}",
                    extra={
                        "run_id": run_id,
                        "correlation_id": correlation_ids.get("correlation_id"),
                    }
                )
                stats["status"] = "success"
                stats["rows_read"] = 0
                stats["rows_processed"] = 0
                stats["rows_written"] = 0
                stats["duration_seconds"] = time.time() - start_time
                return stats
            else:
                raise

        if len(df) == 0:
            logger.warning(
                "No rows found in Stage 5 table - pipeline will complete with 0 messages",
                extra={
                    "run_id": run_id,
                    "correlation_id": correlation_ids.get("correlation_id"),
                }
            )
            stats["status"] = "success"
            stats["rows_processed"] = 0
            stats["rows_written"] = 0
            stats["duration_seconds"] = time.time() - start_time
            return stats

        logger.info(
            f"Read {len(df)} rows from Stage 5",
            extra={
                "run_id": run_id,
                "rows_read": len(df),
            }
        )

        # Transform to entity_unified format
        # entity_unified schema: entity_id, text, level, source_pipeline, source_file, content_date, created_at, metadata
        processed_rows = []
        errors = 0

        for idx, row in df.iterrows():
            try:
                # Get created_at as datetime object
                created_at = row["created_at"]
                if isinstance(created_at, str):
                    try:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    except:
                        created_at = datetime.now(timezone.utc)
                elif not isinstance(created_at, datetime):
                    created_at = datetime.now(timezone.utc)

                # Get content_date
                if hasattr(created_at, "date"):
                    content_date = created_at.date()
                else:
                    content_date = datetime.now(timezone.utc).date()

                # Transform to entity_unified schema
                processed_row = {
                    "entity_id": row["entity_id"],
                    "text": row["text"],
                    "level": 5,  # Message level
                    "source_pipeline": f"claude_code_pipeline",
                    "source_file": f"claude_code_stage_5",
                    "content_date": content_date.isoformat(),
                    "created_at": created_at.isoformat(),
                    "metadata": json.dumps({
                        "source_name": row.get("source_name"),
                        "original_text": row.get("original_text"),
                        "pipeline": "claude_code",
                        "stage_5_run_id": row.get("stage_5_run_id"),
                        "final_run_id": run_id,
                    }),
                }

                processed_rows.append(processed_row)
                stats["rows_processed"] += 1

            except Exception as e:
                errors += 1
                logger.warning(
                    f"Error processing row {idx}: {str(e)}",
                    extra={
                        "run_id": run_id,
                        "correlation_id": correlation_ids.get("correlation_id"),
                        "component": "claude_code_stage_6",
                        "operation": "process_row",
                        "row_index": idx,
                        "error": str(e),
                    },
                    exc_info=True,
                )

        stats["errors"] = errors

        # Clear dataframe from memory
        del df
        gc.collect()

        if not processed_rows:
            raise ValueError("No rows were processed successfully")

        logger.info(
            f"Processed {len(processed_rows)} rows (errors: {errors})",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_6",
                "operation": "write_to_entity_unified",
                "rows_processed": len(processed_rows),
                "errors": errors,
            },
        )

        # Write to entity_unified
        logger.info(
            f"Writing to entity_unified: {ENTITY_UNIFIED_TABLE}",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_6",
                "operation": "write_entity_unified",
                "table": ENTITY_UNIFIED_TABLE,
                "row_count": len(processed_rows),
            },
        )

        # Write using temporary JSONL file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_file:
            for row in processed_rows:
                tmp_file.write(json.dumps(row) + '\n')
            tmp_path = tmp_file.name

        try:
            # Load to entity_unified
            job_config = bigquery.LoadJobConfig(
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                autodetect=True,  # Auto-detect schema
            )

            # Load to entity_unified
            with open(tmp_path, 'rb') as source_file:
                job = bq_client.load_table_from_file(
                    source_file,
                    ENTITY_UNIFIED_TABLE,
                    job_config=job_config,
                )

            job.result()  # Wait for job to complete

            # Clear from memory after write
            stats["rows_written"] = len(processed_rows)
            del processed_rows
            gc.collect()
            stats["status"] = "success"
            stats["duration_seconds"] = time.time() - start_time

            logger.info(
                "Stage 6 write to entity_unified complete",
                extra={
                    "run_id": run_id,
                    "correlation_id": correlation_ids.get("correlation_id"),
                    "component": "claude_code_stage_6",
                    "operation": "write_to_entity_unified",
                    "step": "complete",
                    "rows_written": stats["rows_written"],
                    "duration_seconds": stats["duration_seconds"],
                },
            )

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        return stats

    except Exception as e:
        stats["status"] = "failed"
        stats["duration_seconds"] = time.time() - start_time
        logger.error(
            f"Error in write_to_entity_unified: {e}",
            exc_info=True,
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_6",
                "operation": "write_to_entity_unified",
                "error": str(e),
            },
        )
        require_diagnostic_on_error(e, "write_to_entity_unified")
        raise

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Stage 6: Write to entity_unified (Final Destination)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of messages to process (for testing)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - don't write to entity_unified"
    )

    args = parser.parse_args()

    run_id = get_current_run_id()
    correlation_ids = get_correlation_ids()
    governance = get_unified_governance()

    # Use PipelineTracker for execution monitoring
    with PipelineTracker(
        pipeline_name="claude_code",
        stage=6,
        stage_name="write_to_entity_unified",
        run_id=run_id,
        metadata={
            "limit": args.limit,
            "dry_run": args.dry_run,
        }
    ) as tracker:

        logger.info(
            "Starting Claude Code/Codex/Github Stage 6 write to entity_unified",
            extra={
                "run_id": run_id,
                "limit": args.limit,
                "dry_run": args.dry_run,
                **correlation_ids,
            }
        )

        # Log stage start (governance audit handled by PipelineTracker)
        logger.info(
            "Stage 6 write to entity_unified started",
            extra={
                "run_id": run_id,
                "dry_run": args.dry_run,
            },
        )

        try:
            if args.dry_run:
                logger.info("Dry run - skipping write to entity_unified")
                return 0

            # Write to entity_unified
            stats = write_to_entity_unified(
                run_id=run_id,
                correlation_ids=correlation_ids,
                limit=args.limit,
            )

            tracker.update_progress(
                items_processed=stats["rows_processed"],
                items_failed=stats["errors"]
            )

            logger.info(
                "Stage 6 write to entity_unified completed successfully",
                extra={
                    "run_id": run_id,
                    "stats": stats,
                }
            )

            print("\n" + "="*80)
            print("STAGE 6: WRITE TO ENTITY_UNIFIED COMPLETE")
            print("="*80)
            print(f"Rows Read: {stats['rows_read']:,}")
            print(f"Rows Processed: {stats['rows_processed']:,}")
            print(f"Rows Written: {stats['rows_written']:,}")
            print(f"Errors: {stats['errors']:,}")
            print(f"Duration: {stats['duration_seconds']:.2f}s")
            print("="*80 + "\n")

            return 0

        except Exception as e:
            logger.error(
                f"Error in Stage 6 write to entity_unified: {e}",
                exc_info=True,
                extra={"run_id": run_id}
            )
            tracker.update_progress(items_failed=1)
            require_diagnostic_on_error(e, "main")
            return 1

if __name__ == "__main__":
    exit(main())
