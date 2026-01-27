#!/usr/bin/env python3
"""Stage 6: L3 Sentence Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Sentence Detector) → HOLD₂ (claude_code_stage_6)

Creates Level 3 sentence entities from message content using spaCy sentence detection.

🧠 STAGE FIVE GROUNDING
This stage exists to create L3 sentence entities from message text.

Structure: Read messages → Detect sentences → Generate sentence entities → Write
Purpose: Create sentence-level entities for semantic analysis
Boundaries: Sentence detection only, no sentiment or topic analysis
Control: Batch processing, consistent sentence boundary detection

⚠️ WHAT THIS STAGE CANNOT SEE
- Sentence semantics or meaning
- Cross-message sentence continuity
- Sentiment (handled in Stage 11)
- Topics (handled in Stage 12)

🔥 THE FURNACE PRINCIPLE
- Truth (input): Message text from staged data
- Heat (processing): spaCy sentence detection
- Meaning (output): L3 sentence entities with boundaries
- Care (delivery): Complete sentence coverage, position tracking

Usage:
    python claude_code_stage_6.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 6: L3 Sentence Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Sentence Detector) → HOLD₂ (claude_code_stage_6)

Creates Level 3 sentence entities from message content using spaCy sentence detection.

🧠 STAGE FIVE GROUNDING
This stage exists to create L3 sentence entities from message text.

Structure: Read messages → Detect sentences → Generate sentence entities → Write
Purpose: Create sentence-level entities for semantic analysis
Boundaries: Sentence detection only, no sentiment or topic analysis
Control: Batch processing, consistent sentence boundary detection

⚠️ WHAT THIS STAGE CANNOT SEE
- Sentence semantics or meaning
- Cross-message sentence continuity
- Sentiment (handled in Stage 11)
- Topics (handled in Stage 12)

🔥 THE FURNACE PRINCIPLE
- Truth (input): Message text from staged data
- Heat (processing): spaCy sentence detection
- Meaning (output): L3 sentence entities with boundaries
- Care (delivery): Complete sentence coverage, position tracking

Usage:
    python claude_code_stage_6.py [--batch-size N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_6.claude_code_stage_6.py"

import argparse
import hashlib
import sys
from collections.abc import Generator
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
    LEVEL_SENTENCE,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_4,
    TABLE_STAGE_6,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_4_TABLE = get_full_table_id(TABLE_STAGE_4)
STAGE_6_TABLE = get_full_table_id(TABLE_STAGE_6)

SENTENCE_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("text", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("sentence_index", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("start_char", "INTEGER"),
    bigquery.SchemaField("end_char", "INTEGER"),
    bigquery.SchemaField("word_count", "INTEGER"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_6_table(client: bigquery.Client) -> bigquery.Table:
    table_ref = bigquery.Table(STAGE_6_TABLE, schema=SENTENCE_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["parent_id", "session_id"]
    return client.create_table(table_ref, exists_ok=True)


def generate_sentence_id(parent_id: str, sentence_index: int) -> str:
    return hashlib.sha256(f"L3:{parent_id}:{sentence_index}".encode()).hexdigest()[:32]


def detect_sentences(
    message: dict[str, Any], nlp, run_id: str, created_at: str
) -> Generator[dict, None, None]:
    text = message.get("text") or ""
    if not text.strip():
        return

    parent_id = message["entity_id"]
    doc = nlp(text)

    for idx, sent in enumerate(doc.sents):
        yield {
            "entity_id": generate_sentence_id(parent_id, idx),
            "parent_id": parent_id,
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "level": LEVEL_SENTENCE,
            "text": sent.text,
            "sentence_index": idx,
            "start_char": sent.start_char,
            "end_char": sent.end_char,
            "word_count": len(sent.text.split()),
            "session_id": message.get("session_id"),
            "content_date": message.get("content_date"),
            "created_at": created_at,
            "run_id": run_id,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 6: Create L3 sentence entities")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=6, stage_name="l3_sentences", run_id=run_id
    ) as tracker:
        try:
            import spacy

            nlp = spacy.load("en_core_web_sm")

            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_4)
            if not args.dry_run:
                create_stage_6_table(bq_client)

            created_at = datetime.now(UTC).isoformat()
            query = f"SELECT entity_id, text, session_id, content_date FROM `{STAGE_4_TABLE}` WHERE text IS NOT NULL"
            messages = list(bq_client.query(query).result())

            batch, total = [], 0
            for msg in messages:
                for sent in detect_sentences(dict(msg), nlp, run_id, created_at):
                    batch.append(sent)
                    if len(batch) >= args.batch_size:
                        if not args.dry_run:
                            bq_client.insert_rows_json(STAGE_6_TABLE, batch)
                        total += len(batch)
                        batch = []

            if batch and not args.dry_run:
                bq_client.insert_rows_json(STAGE_6_TABLE, batch)
                total += len(batch)

            tracker.update_progress(items_processed=total)
            print(f"\nSTAGE 6 COMPLETE: {total} sentences created")
            return 0

        except Exception as e:
            logger.error(f"Stage 6 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_6_sentences")
            return 1


if __name__ == "__main__":
    sys.exit(main())
