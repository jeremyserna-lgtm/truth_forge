#!/usr/bin/env python3
"""Stage 15: Final Validation - Claude Code Pipeline

HOLD₁ (claude_code_stage_14) → AGENT (Validator) → HOLD₂ (claude_code_stage_15)

Performs comprehensive validation before promotion to entity_unified:
- Schema compliance validation
- Data quality checks
- Entity integrity verification
- Cross-reference validation

🧠 STAGE FIVE GROUNDING
This stage exists as the final quality gate before production promotion.

Structure: Read aggregated entities → Run validations → Generate report → Write validated
Purpose: Ensure only valid, complete entities reach entity_unified
Boundaries: Validation only, no data transformation
Control: Strict validation rules, clear failure modes

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether data is semantically correct
- User expectations
- Downstream query patterns
- Production usage patterns

🔥 THE FURNACE PRINCIPLE
- Truth (input): Aggregated entities from Stage 14
- Heat (processing): Multi-layer validation checks
- Meaning (output): Validated entities with quality scores
- Care (delivery): Zero invalid entities promoted, clear validation report

Usage:
    python claude_code_stage_15.py [--dry-run] [--strict]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 15: Final Validation - Claude Code Pipeline

HOLD₁ (claude_code_stage_14) → AGENT (Validator) → HOLD₂ (claude_code_stage_15)

Performs comprehensive validation before promotion to entity_unified:
- Schema compliance validation
- Data quality checks
- Entity integrity verification
- Cross-reference validation

🧠 STAGE FIVE GROUNDING
This stage exists as the final quality gate before production promotion.

Structure: Read aggregated entities → Run validations → Generate report → Write validated
Purpose: Ensure only valid, complete entities reach entity_unified
Boundaries: Validation only, no data transformation
Control: Strict validation rules, clear failure modes

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether data is semantically correct
- User expectations
- Downstream query patterns
- Production usage patterns

🔥 THE FURNACE PRINCIPLE
- Truth (input): Aggregated entities from Stage 14
- Heat (processing): Multi-layer validation checks
- Meaning (output): Validated entities with quality scores
- Care (delivery): Zero invalid entities promoted, clear validation report

Usage:
    python claude_code_stage_15.py [--dry-run] [--strict]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_15.claude_code_stage_15.py"

import argparse
import json
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
    TABLE_STAGE_14,
    TABLE_STAGE_15,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_14_TABLE = get_full_table_id(TABLE_STAGE_14)
STAGE_15_TABLE = get_full_table_id(TABLE_STAGE_15)

VALIDATED_SCHEMA = [
    # Core entity fields (same as stage 14)
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
    bigquery.SchemaField("session_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
    bigquery.SchemaField("fingerprint", "STRING"),
    # Validation fields
    bigquery.SchemaField("validation_status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("validation_score", "FLOAT"),
    bigquery.SchemaField("validation_errors", "STRING"),  # JSON array
    bigquery.SchemaField("validation_warnings", "STRING"),  # JSON array
    bigquery.SchemaField("validated_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_15_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 15 validated table."""
    table_ref = bigquery.Table(STAGE_15_TABLE, schema=VALIDATED_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["session_id", "validation_status"]
    return client.create_table(table_ref, exists_ok=True)


def validate_entity(
    entity: dict[str, Any], strict: bool
) -> tuple[str, float, list[str], list[str]]:
    """Validate a single entity and return status, score, errors, warnings."""
    errors = []
    warnings = []
    score = 100.0

    # Required field validation
    if not entity.get("entity_id"):
        errors.append("Missing entity_id")
        score -= 50

    if not entity.get("session_id"):
        errors.append("Missing session_id")
        score -= 30

    if entity.get("level") is None:
        errors.append("Missing level")
        score -= 20

    # Data quality checks
    if entity.get("text") is None or len(str(entity.get("text", ""))) == 0:
        warnings.append("Empty text content")
        score -= 5

    if entity.get("word_count", 0) == 0:
        warnings.append("Zero word count")
        score -= 2

    # Enrichment coverage
    if not entity.get("embedding"):
        warnings.append("Missing embedding")
        score -= 10

    if not entity.get("intent"):
        warnings.append("Missing intent")
        score -= 5

    if not entity.get("keywords"):
        warnings.append("Missing keywords")
        score -= 5

    # Entity ID format validation
    entity_id = entity.get("entity_id", "")
    if len(entity_id) != 32:
        warnings.append(f"Non-standard entity_id length: {len(entity_id)}")
        score -= 5

    # Strict mode additional checks
    if strict:
        if entity.get("timestamp_utc") is None:
            errors.append("Missing timestamp_utc in strict mode")
            score -= 15

        if entity.get("fingerprint") is None:
            errors.append("Missing fingerprint in strict mode")
            score -= 10

    # Determine status
    if errors:
        status = "FAILED"
    elif warnings and score < 70:
        status = "WARNING"
    else:
        status = "PASSED"

    return status, max(0, score), errors, warnings


def run_validation(
    bq_client: bigquery.Client,
    run_id: str,
    strict: bool,
    dry_run: bool,
) -> dict[str, Any]:
    """Run validation on all aggregated entities."""
    validated_at = datetime.now(UTC).isoformat()

    # Get entities from stage 14
    query = f"""
    SELECT * FROM `{STAGE_14_TABLE}`
    ORDER BY session_id, message_index
    """

    entities = list(bq_client.query(query).result())
    logger.info(f"Validating {len(entities)} entities")

    if dry_run:
        # Just run validation without writing
        passed = 0
        warned = 0
        failed = 0

        for entity in entities:
            entity_dict = dict(entity)
            status, score, errors, warnings = validate_entity(entity_dict, strict)
            if status == "PASSED":
                passed += 1
            elif status == "WARNING":
                warned += 1
            else:
                failed += 1

        return {
            "total_entities": len(entities),
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "dry_run": True,
        }

    # Process and write validated entities
    records_to_insert = []
    passed = 0
    warned = 0
    failed = 0

    for entity in entities:
        entity_dict = dict(entity)
        status, score, errors, warnings = validate_entity(entity_dict, strict)

        record = {
            "entity_id": entity_dict.get("entity_id"),
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
            "validation_status": status,
            "validation_score": score,
            "validation_errors": json.dumps(errors) if errors else None,
            "validation_warnings": json.dumps(warnings) if warnings else None,
            "validated_at": validated_at,
            "run_id": run_id,
        }
        records_to_insert.append(record)

        if status == "PASSED":
            passed += 1
        elif status == "WARNING":
            warned += 1
        else:
            failed += 1

        # Insert in batches
        if len(records_to_insert) >= 1000:
            bq_client.insert_rows_json(STAGE_15_TABLE, records_to_insert)
            records_to_insert = []

    # Insert remaining
    if records_to_insert:
        bq_client.insert_rows_json(STAGE_15_TABLE, records_to_insert)

    return {
        "total_entities": len(entities),
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 15: Final validation")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Enable strict validation")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=15, stage_name="validation", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_14)

            if not args.dry_run:
                create_stage_15_table(bq_client)

            stats = run_validation(bq_client, run_id, args.strict, args.dry_run)
            tracker.update_progress(items_processed=stats["total_entities"])

            print("\nSTAGE 15 COMPLETE: Validation Results")
            print(f"  Total entities: {stats['total_entities']}")
            print(f"  Passed: {stats['passed']}")
            print(f"  Warned: {stats['warned']}")
            print(f"  Failed: {stats['failed']}")
            print(f"  Pass rate: {stats['passed'] / max(1, stats['total_entities']) * 100:.1f}%")

            if stats["failed"] > 0 and args.strict:
                logger.error(f"Validation failed: {stats['failed']} entities failed validation")
                return 1

            return 0

        except Exception as e:
            logger.error(f"Stage 15 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_15_validation")
            return 1


if __name__ == "__main__":
    sys.exit(main())
