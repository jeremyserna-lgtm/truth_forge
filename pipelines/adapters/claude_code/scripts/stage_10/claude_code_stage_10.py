#!/usr/bin/env python3
"""Stage 10: LLM Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (LLM Extractor) → HOLD₂ (claude_code_stage_10)

Uses LLM to extract structured information from messages:
- Intent classification
- Task type detection
- Code language identification
- Question/answer patterns

🧠 STAGE FIVE GROUNDING
This stage exists to extract structured semantic information via LLM.

Structure: Read L5 messages → LLM extraction → Store structured data → Write
Purpose: Enable structured analysis and filtering by intent/task type
Boundaries: Extraction only, no interpretation or recommendations
Control: Cost tracking, rate limiting, batch processing

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether extractions are correct (no ground truth)
- User satisfaction with response
- Long-term patterns (single message scope)
- Downstream usage of extractions

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message content
- Heat (processing): LLM inference for structured extraction
- Meaning (output): Intent, task type, code language classifications
- Care (delivery): Consistent extraction schema, cost-efficient

Usage:
    python claude_code_stage_10.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 10: LLM Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (LLM Extractor) → HOLD₂ (claude_code_stage_10)

Uses LLM to extract structured information from messages:
- Intent classification
- Task type detection
- Code language identification
- Question/answer patterns

🧠 STAGE FIVE GROUNDING
This stage exists to extract structured semantic information via LLM.

Structure: Read L5 messages → LLM extraction → Store structured data → Write
Purpose: Enable structured analysis and filtering by intent/task type
Boundaries: Extraction only, no interpretation or recommendations
Control: Cost tracking, rate limiting, batch processing

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether extractions are correct (no ground truth)
- User satisfaction with response
- Long-term patterns (single message scope)
- Downstream usage of extractions

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message content
- Heat (processing): LLM inference for structured extraction
- Meaning (output): Intent, task type, code language classifications
- Care (delivery): Consistent extraction schema, cost-efficient

Usage:
    python claude_code_stage_10.py [--batch-size N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_10.claude_code_stage_10.py"

import argparse
import json
import sys
import time
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
    SOURCE_NAME,
    TABLE_STAGE_7,
    TABLE_STAGE_10,
    get_full_table_id,
    retry_with_backoff,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_7_TABLE = get_full_table_id(TABLE_STAGE_7)
STAGE_10_TABLE = get_full_table_id(TABLE_STAGE_10)

# LLM configuration
LLM_MODEL = "gemini-2.0-flash"
MAX_INPUT_CHARS = 4000

EXTRACTION_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("llm_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("intent", "STRING"),  # question, instruction, clarification, etc.
    bigquery.SchemaField("task_type", "STRING"),  # coding, debugging, explanation, refactoring
    bigquery.SchemaField("code_languages", "STRING"),  # JSON array
    bigquery.SchemaField("complexity", "STRING"),  # simple, moderate, complex
    bigquery.SchemaField("has_code_block", "BOOLEAN"),
    bigquery.SchemaField("extraction_raw", "STRING"),  # Full JSON response
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_10_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 10 extraction table."""
    table_ref = bigquery.Table(STAGE_10_TABLE, schema=EXTRACTION_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["entity_id", "intent", "task_type"]
    return client.create_table(table_ref, exists_ok=True)


def get_llm_client():
    """Initialize the Gemini LLM client."""
    try:
        import os

        import google.generativeai as genai

        api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        return genai
    except ImportError:
        logger.error("google-generativeai package not installed")
        raise


EXTRACTION_PROMPT = """Analyze this Claude Code message and extract structured information.
Return ONLY a JSON object with these fields:
- intent: one of [question, instruction, clarification, feedback, greeting, other]
- task_type: one of [coding, debugging, explanation, refactoring, testing, documentation, other, null]
- code_languages: array of programming languages mentioned or used (empty array if none)
- complexity: one of [simple, moderate, complex]
- has_code_block: boolean if message contains code

Message:
{text}

JSON response:"""


def _extract_from_message_impl(genai, text: str) -> dict[str, Any]:
    """Extract structured information from a message (implementation)."""
    model = genai.GenerativeModel(LLM_MODEL)

    truncated = text[:MAX_INPUT_CHARS] if len(text) > MAX_INPUT_CHARS else text
    prompt = EXTRACTION_PROMPT.format(text=truncated)

    response = model.generate_content(prompt)
    response_text = response.text.strip()

    # Clean up JSON response
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    return json.loads(response_text.strip())

extract_from_message = retry_with_backoff(
    _extract_from_message_impl,
    max_retries=3,
    retry_delays=(1, 2, 4)
)


def process_extractions(
    bq_client: bigquery.Client,
    run_id: str,
    batch_size: int,
    dry_run: bool,
) -> dict[str, int]:
    """Process LLM extractions for user messages."""
    created_at = datetime.now(UTC).isoformat()

    # Only extract from user messages (not assistant responses)
    query = f"""
    SELECT entity_id, text, session_id, content_date
    FROM `{STAGE_7_TABLE}`
    WHERE role = 'user' AND text IS NOT NULL AND LENGTH(TRIM(text)) > 10
    ORDER BY session_id, entity_id
    """

    messages = list(bq_client.query(query).result())
    logger.info(f"Found {len(messages)} user messages for LLM extraction")

    if dry_run:
        return {
            "input_messages": len(messages),
            "extractions_completed": 0,
            "dry_run": True,
        }

    genai = get_llm_client()

    records_to_insert = []
    total_extracted = 0
    errors_count = 0

    for msg in messages:
        try:
            extraction = extract_from_message(genai, msg.text)

            record = {
                "entity_id": msg.entity_id,
                "source_name": SOURCE_NAME,
                "source_pipeline": PIPELINE_NAME,
                "llm_model": LLM_MODEL,
                "intent": extraction.get("intent"),
                "task_type": extraction.get("task_type"),
                "code_languages": json.dumps(extraction.get("code_languages", [])),
                "complexity": extraction.get("complexity"),
                "has_code_block": extraction.get("has_code_block", False),
                "extraction_raw": json.dumps(extraction),
                "session_id": msg.session_id,
                "content_date": msg.content_date,
                "created_at": created_at,
                "run_id": run_id,
            }
            records_to_insert.append(record)
            total_extracted += 1

        except Exception as e:
            logger.warning(f"Extraction failed for {msg.entity_id}: {e}")
            errors_count += 1
            continue

        # Insert in batches
        if len(records_to_insert) >= batch_size:
            errors = bq_client.insert_rows_json(STAGE_10_TABLE, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

        # Rate limiting
        time.sleep(0.2)

    # Insert remaining records
    if records_to_insert:
        errors = bq_client.insert_rows_json(STAGE_10_TABLE, records_to_insert)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")

    return {
        "input_messages": len(messages),
        "extractions_completed": total_extracted,
        "extraction_errors": errors_count,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 10: LLM extraction")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=10, stage_name="llm_extraction", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_7)
            if not args.dry_run:
                create_stage_10_table(bq_client)

            stats = process_extractions(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats["extractions_completed"])

            print(f"\nSTAGE 10 COMPLETE: {stats['extractions_completed']} extractions completed")
            print(f"Model: {LLM_MODEL}")
            return 0

        except Exception as e:
            logger.error(f"Stage 10 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_10_llm_extraction")
            return 1


if __name__ == "__main__":
    sys.exit(main())
