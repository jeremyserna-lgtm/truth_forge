#!/usr/bin/env python3
"""
Validation Script for Claude Code/Codex/Github Pipeline

Validates pipeline stages and data quality.
"""
from __future__ import annotations

#!/usr/bin/env python3
"""
Validation Script for Claude Code/Codex/Github Pipeline

Validates pipeline stages and data quality.
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.validation.validate_claude_code_pipeline.py"

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from google.cloud import bigquery

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
STAGE_0_TABLE = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_0"
STAGE_1_TABLE = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_1"

def validate_stage_0(client: bigquery.Client) -> Dict[str, Any]:
    """Validate Stage 0 data."""
    logger.info("Validating Stage 0")

    query = f"""
    SELECT
        COUNT(*) as total_messages,
        COUNT(DISTINCT source_name) as unique_sources,
        COUNT(DISTINCT DATE(content_date)) as unique_dates,
        MIN(content_date) as earliest_date,
        MAX(content_date) as latest_date,
        COUNT(DISTINCT message_id) as unique_messages
    FROM `{STAGE_0_TABLE}`
    """

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        if results:
            row = results[0]
            return {
                "valid": True,
                "total_messages": row.total_messages,
                "unique_sources": row.unique_sources,
                "unique_dates": row.unique_dates,
                "earliest_date": str(row.earliest_date) if row.earliest_date else None,
                "latest_date": str(row.latest_date) if row.latest_date else None,
                "unique_messages": row.unique_messages,
            }
        else:
            return {"valid": False, "error": "No data in Stage 0"}

    except Exception as e:
        logger.error(f"Error validating Stage 0: {e}", exc_info=True)
        return {"valid": False, "error": str(e)}

def validate_stage_1(client: bigquery.Client) -> Dict[str, Any]:
    """Validate Stage 1 data."""
    logger.info("Validating Stage 1")

    query = f"""
    SELECT
        COUNT(*) as total_messages,
        COUNT(DISTINCT source_name) as unique_sources,
        AVG(sentiment_score) as avg_sentiment,
        AVG(quality_score) as avg_quality,
        COUNT(DISTINCT sentiment_label) as unique_sentiments,
        COUNT(DISTINCT message_id) as unique_messages
    FROM `{STAGE_1_TABLE}`
    """

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        if results:
            row = results[0]
            return {
                "valid": True,
                "total_messages": row.total_messages,
                "unique_sources": row.unique_sources,
                "avg_sentiment": float(row.avg_sentiment) if row.avg_sentiment else None,
                "avg_quality": float(row.avg_quality) if row.avg_quality else None,
                "unique_sentiments": row.unique_sentiments,
                "unique_messages": row.unique_messages,
            }
        else:
            return {"valid": False, "error": "No data in Stage 1"}

    except Exception as e:
        logger.error(f"Error validating Stage 1: {e}", exc_info=True)
        return {"valid": False, "error": str(e)}

def validate_pipeline_integrity(client: bigquery.Client) -> Dict[str, Any]:
    """Validate pipeline integrity between stages."""
    logger.info("Validating pipeline integrity")

    query = f"""
    SELECT
        COUNT(DISTINCT s0.message_id) as stage_0_count,
        COUNT(DISTINCT s1.message_id) as stage_1_count,
        COUNT(DISTINCT CASE WHEN s1.message_id IS NOT NULL THEN s0.message_id END) as enriched_count
    FROM `{STAGE_0_TABLE}` s0
    LEFT JOIN `{STAGE_1_TABLE}` s1
        ON s0.message_id = s1.message_id
    """

    try:
        query_job = client.query(query)
        results = list(query_job.result())

        if results:
            row = results[0]
            enrichment_rate = (
                float(row.enriched_count) / float(row.stage_0_count)
                if row.stage_0_count > 0
                else 0.0
            )

            return {
                "valid": True,
                "stage_0_count": row.stage_0_count,
                "stage_1_count": row.stage_1_count,
                "enriched_count": row.enriched_count,
                "enrichment_rate": enrichment_rate,
            }
        else:
            return {"valid": False, "error": "No data for integrity check"}

    except Exception as e:
        logger.error(f"Error validating pipeline integrity: {e}", exc_info=True)
        return {"valid": False, "error": str(e)}

def main():
    """Main validation function."""
    import json

    run_id = get_current_run_id()

    logger.info(
        "Starting pipeline validation",
        extra={"run_id": run_id}
    )

    try:
        # Get BigQuery client
        client = get_bigquery_client()
        if hasattr(client, 'client'):
            bq_client = client.client
        else:
            bq_client = client

        # Validate stages
        stage_0_results = validate_stage_0(bq_client)
        stage_1_results = validate_stage_1(bq_client)
        integrity_results = validate_pipeline_integrity(bq_client)

        # Print results
        print("\n" + "="*60)
        print("Pipeline Validation Results")
        print("="*60)

        print("\nStage 0 (Extraction):")
        print(json.dumps(stage_0_results, indent=2))

        print("\nStage 1 (Enrichment):")
        print(json.dumps(stage_1_results, indent=2))

        print("\nPipeline Integrity:")
        print(json.dumps(integrity_results, indent=2))

        # Overall validation
        all_valid = (
            stage_0_results.get("valid", False) and
            stage_1_results.get("valid", False) and
            integrity_results.get("valid", False)
        )

        print("\n" + "="*60)
        if all_valid:
            print("✅ Pipeline validation PASSED")
        else:
            print("❌ Pipeline validation FAILED")
        print("="*60)

        return 0 if all_valid else 1

    except Exception as e:
        logger.error(
            f"Error in pipeline validation: {e}",
            exc_info=True,
            extra={"run_id": run_id}
        )
        return 1

if __name__ == "__main__":
    exit(main())
