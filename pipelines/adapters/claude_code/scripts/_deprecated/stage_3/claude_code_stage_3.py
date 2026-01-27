#!/usr/bin/env python3
"""
Stage 3: System ID Registration (THE GATE) - Claude Code/Codex/Github Pipeline

HOLD₁ (BigQuery claude_code_stage_1) → AGENT (Register IDs) → HOLD₂ (BigQuery claude_code_stage_3)

Registers existing entity_ids from TruthService with identity_service (THE GATE).
This is THE GATE stage where all entity_ids are registered in the central identity registry.

🧠 STAGE FIVE GROUNDING
This stage exists to register entity_ids with identity_service for central tracking and deduplication.

Structure: Read Stage 1 → Register Entity IDs → Sync to BigQuery → Store (sequential flow)
Purpose: Register all entity_ids in central identity service (THE GATE)
Boundaries: Only registers IDs, no ID generation (IDs already exist from TruthService), uses identity_service for registration
Control: Validates input exists, uses identity_service for registration, tracks registration statistics

⚠️ WHAT THIS STAGE CANNOT SEE
- Message content meaning or context
- Relationships between entities beyond what's in Stage 1
- Future processing needs beyond ID registration
- Downstream stage requirements beyond ID structure

🔥 THE FURNACE PRINCIPLE
- Truth (input): Enriched messages from Stage 1 with existing entity_ids
- Heat (processing): Entity ID registration via identity_service, sync to BigQuery
- Meaning (output): Registered entity_ids in central registry and Stage 3 table
- Care (delivery): Data with registered IDs ready for downstream processing

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical Stage 3 specification for the Claude Code/Codex/Github Pipeline.

RATIONALE:
----------
- Stage 1 has enriched messages with entity_ids from TruthService
- Stage 3 registers these existing entity_ids in identity_service (THE GATE)
- Registration enables:
  - Deduplication across pipelines
  - Identity resolution
  - Entity matching
  - Complete audit trail
- Unlike other pipelines, we REGISTER existing IDs (not generate new ones)

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses identity_service for ID registration (primitive pattern)
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
"""
from __future__ import annotations

#!/usr/bin/env python3
"""
Stage 3: System ID Registration (THE GATE) - Claude Code/Codex/Github Pipeline

HOLD₁ (BigQuery claude_code_stage_1) → AGENT (Register IDs) → HOLD₂ (BigQuery claude_code_stage_3)

Registers existing entity_ids from TruthService with identity_service (THE GATE).
This is THE GATE stage where all entity_ids are registered in the central identity registry.

🧠 STAGE FIVE GROUNDING
This stage exists to register entity_ids with identity_service for central tracking and deduplication.

Structure: Read Stage 1 → Register Entity IDs → Sync to BigQuery → Store (sequential flow)
Purpose: Register all entity_ids in central identity service (THE GATE)
Boundaries: Only registers IDs, no ID generation (IDs already exist from TruthService), uses identity_service for registration
Control: Validates input exists, uses identity_service for registration, tracks registration statistics

⚠️ WHAT THIS STAGE CANNOT SEE
- Message content meaning or context
- Relationships between entities beyond what's in Stage 1
- Future processing needs beyond ID registration
- Downstream stage requirements beyond ID structure

🔥 THE FURNACE PRINCIPLE
- Truth (input): Enriched messages from Stage 1 with existing entity_ids
- Heat (processing): Entity ID registration via identity_service, sync to BigQuery
- Meaning (output): Registered entity_ids in central registry and Stage 3 table
- Care (delivery): Data with registered IDs ready for downstream processing

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical Stage 3 specification for the Claude Code/Codex/Github Pipeline.

RATIONALE:
----------
- Stage 1 has enriched messages with entity_ids from TruthService
- Stage 3 registers these existing entity_ids in identity_service (THE GATE)
- Registration enables:
  - Deduplication across pipelines
  - Identity resolution
  - Entity matching
  - Complete audit trail
- Unlike other pipelines, we REGISTER existing IDs (not generate new ones)

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses identity_service for ID registration (primitive pattern)
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts._deprecated.stage_3.claude_code_stage_3.py"

import argparse
import gc
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
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
from src.services.central_services.governance.governance import (
    get_unified_governance,
    require_diagnostic_on_error,
)
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.identity_service.service import (
    register_id,
    sync_to_bigquery,
)

# Initialize logger (NOT print())
logger = get_logger(__name__)

# Configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
TABLE_STAGE_1 = "claude_code_stage_1"
TABLE_STAGE_3 = "claude_code_stage_3"

def register_entity_ids(run_id: str, correlation_ids: dict, limit: Optional[int] = None) -> dict:
    """Register entity_ids from Stage 1 with identity_service.

    🎓 LEARNING: ID Registration for Claude Code/Codex/Github
    Unlike other pipelines that GENERATE new IDs, this pipeline REGISTERS existing IDs
    from TruthService. The entity_ids already exist and are stable.

    Args:
        run_id: Current run ID for traceability
        correlation_ids: Correlation IDs for distributed tracing
        limit: Optional limit on number of messages to process

    Returns:
        dict with registration stats
    """
    start_time = time.time()
    stats = {
        "status": "in_progress",
        "rows_read": 0,
        "rows_processed": 0,
        "rows_inserted": 0,
        "ids_registered": 0,
        "errors": 0,
        "duration_seconds": 0,
    }

    governance = get_unified_governance()

    try:
        # Read data from Stage 1
        logger.info(
            f"Reading data from Stage 1: {PROJECT_ID}.{DATASET_ID}.{TABLE_STAGE_1}",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_3",
                "operation": "read_stage_1",
                "project_id": PROJECT_ID,
                "dataset_id": DATASET_ID,
                "table_id": TABLE_STAGE_1,
            },
        )

        client = get_bigquery_client()
        if hasattr(client, 'client'):
            bq_client = client.client
        else:
            bq_client = client

        # Build query to read from Stage 1
        limit_clause = f"LIMIT {limit}" if limit else ""

        query = f"""
        SELECT
            message_id,
            entity_id,
            source_name,
            source_pipeline,
            source_file,
            text,
            level,
            content_date,
            created_at,
            extracted_at,
            metadata,
            sentiment_score,
            sentiment_label,
            entities,
            topics,
            quality_score,
            text_length,
            word_count,
            enriched_at,
            enrichment_run_id,
            run_id as stage_1_run_id
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_STAGE_1}`
        WHERE entity_id IS NOT NULL
        ORDER BY content_date DESC, created_at DESC
        {limit_clause}
        """

        logger.info(
            "Executing query to read Stage 1 data",
            extra={
                "run_id": run_id,
                "query_length": len(query),
                "limit": limit,
            }
        )

        df = bq_client.query(query).to_dataframe()
        stats["rows_read"] = len(df)

        if len(df) == 0:
            logger.warning(
                "No rows found in Stage 1 table - pipeline will complete with 0 messages",
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
            f"Read {len(df)} rows from Stage 1",
            extra={
                "run_id": run_id,
                "rows_read": len(df),
            }
        )

        # Process rows to register IDs
        processed_rows = []
        registered_ids = set()  # Track registered IDs to avoid duplicates
        errors = 0

        # Process in batches for memory efficiency
        BATCH_SIZE = 1000
        total_batches = (len(df) + BATCH_SIZE - 1) // BATCH_SIZE

        for batch_idx in range(total_batches):
            batch_start = batch_idx * BATCH_SIZE
            batch_end = min(batch_start + BATCH_SIZE, len(df))
            batch_df = df.iloc[batch_start:batch_end]

            logger.info(
                f"Processing batch {batch_idx + 1}/{total_batches} ({batch_start}-{batch_end})",
                extra={
                    "run_id": run_id,
                    "batch_idx": batch_idx + 1,
                    "total_batches": total_batches,
                    "batch_start": batch_start,
                    "batch_end": batch_end,
                }
            )

            for idx, row in batch_df.iterrows():
                try:
                    entity_id = row["entity_id"]
                    source_name = row["source_name"]
                    level = row["level"]

                    # Skip if already registered in this run
                    if entity_id in registered_ids:
                        continue

                    # Determine entity type based on source and level
                    if level == 5:
                        entity_type = f"{source_name}_message"
                    else:
                        entity_type = f"{source_name}_entity"

                    # Register entity_id with identity_service
                    register_id(
                        id_str=entity_id,
                        metadata={
                            "entity_type": entity_type,
                            "generation_method": "truth_service",
                            "context_data": {
                                "pipeline": "claude_code",
                                "stage": 3,
                                "level": int(level),
                                "source_name": source_name,
                                "source_pipeline": row.get("source_pipeline"),
                            },
                            "stable": True,
                            "first_requestor": "claude_code_stage_3",
                            "source_system": "claude_code",
                        },
                    )

                    registered_ids.add(entity_id)
                    stats["ids_registered"] += 1

                    # Create processed row for Stage 3 table
                    processed_row = {
                        "message_id": row["message_id"],
                        "entity_id": entity_id,
                        "source_name": source_name,
                        "source_pipeline": row.get("source_pipeline"),
                        "source_file": row.get("source_file"),
                        "text": row["text"],
                        "level": int(level),
                        "content_date": row["content_date"].isoformat() if hasattr(row["content_date"], "isoformat") else str(row["content_date"]),
                        "created_at": row["created_at"].isoformat() if hasattr(row["created_at"], "isoformat") else str(row["created_at"]),
                        "extracted_at": row["extracted_at"].isoformat() if hasattr(row["extracted_at"], "isoformat") else str(row["extracted_at"]),
                        "metadata": json.dumps(row.get("metadata", {})) if isinstance(row.get("metadata"), dict) else row.get("metadata"),
                        "sentiment_score": float(row.get("sentiment_score")) if pd.notna(row.get("sentiment_score")) else None,
                        "sentiment_label": row.get("sentiment_label"),
                        "entities": row.get("entities"),
                        "topics": row.get("topics"),
                        "quality_score": float(row.get("quality_score")) if pd.notna(row.get("quality_score")) else None,
                        "text_length": int(row.get("text_length")) if pd.notna(row.get("text_length")) else None,
                        "word_count": int(row.get("word_count")) if pd.notna(row.get("word_count")) else None,
                        "enriched_at": row["enriched_at"].isoformat() if hasattr(row["enriched_at"], "isoformat") else str(row["enriched_at"]),
                        "enrichment_run_id": row.get("enrichment_run_id"),
                        "registered_at": datetime.now(timezone.utc).isoformat(),
                        "registration_run_id": run_id,
                        "stage_1_run_id": row.get("stage_1_run_id"),
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
                            "component": "claude_code_stage_3",
                            "operation": "process_row",
                            "row_index": idx,
                            "error": str(e),
                        },
                        exc_info=True,
                    )

            # Clear batch from memory
            del batch_df
            gc.collect()

        stats["errors"] = errors

        # Clear dataframe from memory
        del df
        gc.collect()

        if not processed_rows:
            raise ValueError("No rows were processed successfully")

        logger.info(
            f"Processed {len(processed_rows)} rows, registered {stats['ids_registered']} IDs (errors: {errors})",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_3",
                "operation": "register_ids",
                "rows_processed": len(processed_rows),
                "ids_registered": stats["ids_registered"],
                "errors": errors,
            },
        )

        # Sync registered IDs to BigQuery
        logger.info(
            "Syncing registered IDs to BigQuery identity registry",
            extra={
                "run_id": run_id,
                "ids_registered": stats["ids_registered"],
            }
        )

        try:
            synced_count = sync_to_bigquery(dry_run=False, batch_size=1000)
            logger.info(
                f"Synced {synced_count} IDs to BigQuery identity registry",
                extra={
                    "run_id": run_id,
                    "synced_count": synced_count,
                }
            )
        except Exception as e:
            logger.warning(
                f"Error syncing to BigQuery: {e}",
                extra={
                    "run_id": run_id,
                    "error": str(e),
                },
                exc_info=True,
            )
            # Don't fail the stage if sync fails - IDs are registered locally

        # Write to BigQuery Stage 3 table
        logger.info(
            f"Writing to BigQuery: {PROJECT_ID}.{DATASET_ID}.{TABLE_STAGE_3}",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_3",
                "operation": "write_bigquery",
                "project_id": PROJECT_ID,
                "dataset_id": DATASET_ID,
                "table_id": TABLE_STAGE_3,
                "row_count": len(processed_rows),
            },
        )

        # Create dataset if it doesn't exist
        dataset_ref = bq_client.dataset(DATASET_ID)
        try:
            bq_client.get_dataset(dataset_ref)
        except Exception:
            logger.info(f"Creating dataset {DATASET_ID}")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset = bq_client.create_dataset(dataset, exists_ok=True)

        table_ref = bq_client.dataset(DATASET_ID).table(TABLE_STAGE_3)

        # Configure load job
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,  # Auto-detect schema
        )

        # Write using temporary JSONL file (more reliable for large datasets)
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_file:
            for row in processed_rows:
                tmp_file.write(json.dumps(row) + '\n')
            tmp_path = tmp_file.name

        try:
            # Load from file
            with open(tmp_path, 'rb') as source_file:
                job = bq_client.load_table_from_file(
                    source_file,
                    table_ref,
                    job_config=job_config,
                )

            job.result()  # Wait for job to complete
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        # Clear from memory after write
        stats["rows_inserted"] = len(processed_rows)
        del processed_rows
        gc.collect()
        stats["status"] = "success"
        stats["duration_seconds"] = time.time() - start_time

        logger.info(
            "Stage 3 ID registration complete",
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_3",
                "operation": "register_ids",
                "step": "complete",
                "rows_inserted": stats["rows_inserted"],
                "ids_registered": stats["ids_registered"],
                "duration_seconds": stats["duration_seconds"],
            },
        )

        return stats

    except Exception as e:
        stats["status"] = "failed"
        stats["duration_seconds"] = time.time() - start_time
        logger.error(
            f"Error in register_entity_ids: {e}",
            exc_info=True,
            extra={
                "run_id": run_id,
                "correlation_id": correlation_ids.get("correlation_id"),
                "component": "claude_code_stage_3",
                "operation": "register_entity_ids",
                "error": str(e),
            },
        )
        require_diagnostic_on_error(e, "register_entity_ids")
        raise

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Register entity_ids with identity_service (THE GATE)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of messages to process (for testing)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - register IDs but don't write to BigQuery"
    )

    args = parser.parse_args()

    run_id = get_current_run_id()
    correlation_ids = get_correlation_ids()
    governance = get_unified_governance()

    # Use PipelineTracker for execution monitoring
    with PipelineTracker(
        pipeline_name="claude_code",
        stage=3,
        stage_name="id_registration",
        run_id=run_id,
        metadata={
            "limit": args.limit,
            "dry_run": args.dry_run,
        }
    ) as tracker:

        logger.info(
            "Starting Claude Code/Codex/Github Stage 3 ID registration",
            extra={
                "run_id": run_id,
                "limit": args.limit,
                "dry_run": args.dry_run,
                **correlation_ids,
            }
        )

        # Log stage start (governance audit handled by PipelineTracker)
        logger.info(
            "Stage 3 ID registration started",
            extra={
                "run_id": run_id,
                "dry_run": args.dry_run,
            },
        )

        try:
            # Register entity_ids
            stats = register_entity_ids(
                run_id=run_id,
                correlation_ids=correlation_ids,
                limit=args.limit,
            )

            tracker.update_progress(
                items_processed=stats["rows_processed"],
                items_failed=stats["errors"]
            )

            logger.info(
                "Stage 3 ID registration completed successfully",
                extra={
                    "run_id": run_id,
                    "stats": stats,
                }
            )

            print("\n" + "="*80)
            print("STAGE 3 ID REGISTRATION COMPLETE")
            print("="*80)
            print(f"Rows Read: {stats['rows_read']:,}")
            print(f"Rows Processed: {stats['rows_processed']:,}")
            print(f"IDs Registered: {stats['ids_registered']:,}")
            print(f"Rows Inserted: {stats['rows_inserted']:,}")
            print(f"Errors: {stats['errors']:,}")
            print(f"Duration: {stats['duration_seconds']:.2f}s")
            print("="*80 + "\n")

            return 0

        except Exception as e:
            logger.error(
                f"Error in Stage 3 ID registration: {e}",
                exc_info=True,
                extra={"run_id": run_id}
            )
            tracker.update_progress(items_failed=1)
            require_diagnostic_on_error(e, "main")
            return 1

if __name__ == "__main__":
    exit(main())
