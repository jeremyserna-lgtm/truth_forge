#!/usr/bin/env python3
"""Stage 12: Topic Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Topic Extractor) → HOLD₂ (claude_code_stage_12)

Extracts topics and keywords from L5 message entities using KeyBERT.
Enables topic-based filtering, clustering, and analysis.

🧠 STAGE FIVE GROUNDING
This stage exists to extract semantic topics from message content.

Structure: Read L5 messages → Extract keywords/topics → Store → Write
Purpose: Enable topic-based discovery and organization
Boundaries: Topic extraction only, no clustering or categorization
Control: Consistent keyword extraction, diversity settings

⚠️ WHAT THIS STAGE CANNOT SEE
- Topic hierarchies (not computed here)
- Cross-message topic evolution
- Topic relevance to user goals
- Domain-specific topic ontologies

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message text content
- Heat (processing): KeyBERT keyword extraction
- Meaning (output): Ranked topic keywords with scores
- Care (delivery): All messages processed, consistent extraction

Usage:
    python claude_code_stage_12.py [--batch-size N] [--top-n N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 12: Topic Extraction - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Topic Extractor) → HOLD₂ (claude_code_stage_12)

Extracts topics and keywords from L5 message entities using KeyBERT.
Enables topic-based filtering, clustering, and analysis.

🧠 STAGE FIVE GROUNDING
This stage exists to extract semantic topics from message content.

Structure: Read L5 messages → Extract keywords/topics → Store → Write
Purpose: Enable topic-based discovery and organization
Boundaries: Topic extraction only, no clustering or categorization
Control: Consistent keyword extraction, diversity settings

⚠️ WHAT THIS STAGE CANNOT SEE
- Topic hierarchies (not computed here)
- Cross-message topic evolution
- Topic relevance to user goals
- Domain-specific topic ontologies

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message text content
- Heat (processing): KeyBERT keyword extraction
- Meaning (output): Ranked topic keywords with scores
- Care (delivery): All messages processed, consistent extraction

Usage:
    python claude_code_stage_12.py [--batch-size N] [--top-n N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_12.claude_code_stage_12.py"

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

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
    TABLE_STAGE_12,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_7_TABLE = get_full_table_id(TABLE_STAGE_7)
STAGE_12_TABLE = get_full_table_id(TABLE_STAGE_12)

# Topic extraction configuration
DEFAULT_TOP_N = 10
KEYBERT_MODEL = "all-MiniLM-L6-v2"

TOPIC_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("extraction_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("keywords", "STRING"),  # JSON array of keywords
    bigquery.SchemaField("keywords_with_scores", "STRING"),  # JSON array of [keyword, score]
    bigquery.SchemaField("top_keyword", "STRING"),
    bigquery.SchemaField("top_keyword_score", "FLOAT"),
    bigquery.SchemaField("keyword_count", "INTEGER"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_12_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 12 topics table."""
    table_ref = bigquery.Table(STAGE_12_TABLE, schema=TOPIC_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["entity_id", "top_keyword"]
    return client.create_table(table_ref, exists_ok=True)


def get_keybert_model():
    """Initialize KeyBERT model."""
    try:
        from keybert import KeyBERT

        return KeyBERT(model=KEYBERT_MODEL)
    except ImportError:
        logger.error("keybert package not installed")
        raise


def extract_keywords(
    kw_model,
    text: str,
    top_n: int,
) -> list[tuple[str, float]]:
    """Extract keywords from text using KeyBERT."""
    if not text or len(text.strip()) < 20:
        return []

    try:
        keywords = kw_model.extract_keywords(
            text,
            keyphrase_ngram_range=(1, 3),
            stop_words="english",
            use_maxsum=True,
            nr_candidates=20,
            top_n=top_n,
            diversity=0.5,
        )
        return keywords
    except Exception as e:
        logger.warning(f"Keyword extraction failed: {e}")
        return []


def process_topics(
    bq_client: bigquery.Client,
    run_id: str,
    batch_size: int,
    top_n: int,
    dry_run: bool,
) -> dict[str, int]:
    """Process topic extraction for all messages."""
    created_at = datetime.now(UTC).isoformat()

    # Get messages for topic extraction
    query = f"""
    SELECT entity_id, text, session_id, content_date
    FROM `{STAGE_7_TABLE}`
    WHERE text IS NOT NULL AND LENGTH(TRIM(text)) > 20
    ORDER BY session_id, entity_id
    """

    messages = list(bq_client.query(query).result())
    logger.info(f"Found {len(messages)} messages for topic extraction")

    if dry_run:
        return {
            "input_messages": len(messages),
            "topics_extracted": 0,
            "dry_run": True,
        }

    kw_model = get_keybert_model()

    records_to_insert = []
    total_extracted = 0

    for msg in messages:
        keywords = extract_keywords(kw_model, msg.text, top_n)

        if keywords:
            top_kw, top_score = keywords[0]
            keywords_list = [kw for kw, _ in keywords]
            keywords_with_scores = [[kw, round(score, 4)] for kw, score in keywords]
        else:
            top_kw, top_score = None, None
            keywords_list = []
            keywords_with_scores = []

        record = {
            "entity_id": msg.entity_id,
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "extraction_model": KEYBERT_MODEL,
            "keywords": json.dumps(keywords_list),
            "keywords_with_scores": json.dumps(keywords_with_scores),
            "top_keyword": top_kw,
            "top_keyword_score": top_score,
            "keyword_count": len(keywords),
            "session_id": msg.session_id,
            "content_date": msg.content_date,
            "created_at": created_at,
            "run_id": run_id,
        }
        records_to_insert.append(record)
        total_extracted += 1

        # Insert in batches
        if len(records_to_insert) >= batch_size:
            errors = bq_client.insert_rows_json(STAGE_12_TABLE, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

    # Insert remaining
    if records_to_insert:
        errors = bq_client.insert_rows_json(STAGE_12_TABLE, records_to_insert)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")

    return {
        "input_messages": len(messages),
        "topics_extracted": total_extracted,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 12: Topic extraction")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=12, stage_name="topics", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_7)
            if not args.dry_run:
                create_stage_12_table(bq_client)

            stats = process_topics(bq_client, run_id, args.batch_size, args.top_n, args.dry_run)
            tracker.update_progress(items_processed=stats["topics_extracted"])

            print(f"\nSTAGE 12 COMPLETE: {stats['topics_extracted']} topics extracted")
            print(f"Model: {KEYBERT_MODEL}")
            print(f"Top-N keywords: {args.top_n}")
            return 0

        except Exception as e:
            logger.error(f"Stage 12 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_12_topics")
            return 1


if __name__ == "__main__":
    sys.exit(main())
