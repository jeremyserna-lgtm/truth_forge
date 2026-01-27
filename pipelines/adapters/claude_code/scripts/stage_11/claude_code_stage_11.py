#!/usr/bin/env python3
"""Stage 11: Sentiment Analysis - Claude Code Pipeline

HOLD₁ (claude_code_stage_6) → AGENT (Sentiment Analyzer) → HOLD₂ (claude_code_stage_11)

Performs sentiment analysis on L3 sentence entities using GoEmotions model.
Produces multi-label emotion classifications for each sentence.

🧠 STAGE FIVE GROUNDING
This stage exists to add emotional/sentiment dimensions to text content.

Structure: Read L3 sentences → Run sentiment model → Store classifications → Write
Purpose: Enable emotion-aware analysis and filtering
Boundaries: Sentiment classification only, no interpretation
Control: Batch processing, GPU optimization, consistent labeling

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether sentiment affects user behavior
- Context of surrounding sentences
- Sarcasm or irony (model limitation)
- Cultural/personal sentiment variations

🔥 THE FURNACE PRINCIPLE
- Truth (input): L3 sentence text
- Heat (processing): GoEmotions transformer inference
- Meaning (output): Emotion classifications with confidence scores
- Care (delivery): All sentences analyzed, proper thresholds

Usage:
    python claude_code_stage_11.py [--batch-size N] [--threshold F] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 11: Sentiment Analysis - Claude Code Pipeline

HOLD₁ (claude_code_stage_6) → AGENT (Sentiment Analyzer) → HOLD₂ (claude_code_stage_11)

Performs sentiment analysis on L3 sentence entities using GoEmotions model.
Produces multi-label emotion classifications for each sentence.

🧠 STAGE FIVE GROUNDING
This stage exists to add emotional/sentiment dimensions to text content.

Structure: Read L3 sentences → Run sentiment model → Store classifications → Write
Purpose: Enable emotion-aware analysis and filtering
Boundaries: Sentiment classification only, no interpretation
Control: Batch processing, GPU optimization, consistent labeling

⚠️ WHAT THIS STAGE CANNOT SEE
- Whether sentiment affects user behavior
- Context of surrounding sentences
- Sarcasm or irony (model limitation)
- Cultural/personal sentiment variations

🔥 THE FURNACE PRINCIPLE
- Truth (input): L3 sentence text
- Heat (processing): GoEmotions transformer inference
- Meaning (output): Emotion classifications with confidence scores
- Care (delivery): All sentences analyzed, proper thresholds

Usage:
    python claude_code_stage_11.py [--batch-size N] [--threshold F] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_11.claude_code_stage_11.py"

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
    SOURCE_NAME,
    TABLE_STAGE_6,
    TABLE_STAGE_11,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_6_TABLE = get_full_table_id(TABLE_STAGE_6)
STAGE_11_TABLE = get_full_table_id(TABLE_STAGE_11)

# Sentiment configuration
SENTIMENT_MODEL = "SamLowe/roberta-base-go_emotions"
DEFAULT_THRESHOLD = 0.3

SENTIMENT_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("sentiment_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("primary_emotion", "STRING"),
    bigquery.SchemaField("primary_score", "FLOAT"),
    bigquery.SchemaField("emotions_detected", "STRING"),  # JSON array
    bigquery.SchemaField("all_scores", "STRING"),  # JSON object
    bigquery.SchemaField("threshold_used", "FLOAT"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_11_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 11 sentiment table."""
    table_ref = bigquery.Table(STAGE_11_TABLE, schema=SENTIMENT_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["entity_id", "primary_emotion"]
    return client.create_table(table_ref, exists_ok=True)


def get_sentiment_pipeline():
    """Initialize the sentiment analysis pipeline."""
    try:
        from transformers import pipeline

        return pipeline(
            "text-classification",
            model=SENTIMENT_MODEL,
            top_k=None,
            truncation=True,
            max_length=512,
        )
    except ImportError:
        logger.error("transformers package not installed")
        raise


def process_sentiment_batch(
    classifier,
    texts: list[str],
    threshold: float,
) -> list[dict[str, Any]]:
    """Process a batch of texts through sentiment classifier."""
    results = []

    # Run classifier on batch
    predictions = classifier(texts)

    for pred in predictions:
        # Sort by score
        sorted_preds = sorted(pred, key=lambda x: x["score"], reverse=True)

        # Get primary emotion
        primary = sorted_preds[0]
        primary_emotion = primary["label"]
        primary_score = primary["score"]

        # Get all emotions above threshold
        emotions_detected = [p["label"] for p in sorted_preds if p["score"] >= threshold]

        # All scores as dict
        all_scores = {p["label"]: round(p["score"], 4) for p in sorted_preds}

        results.append(
            {
                "primary_emotion": primary_emotion,
                "primary_score": round(primary_score, 4),
                "emotions_detected": emotions_detected,
                "all_scores": all_scores,
            }
        )

    return results


def process_sentiment(
    bq_client: bigquery.Client,
    run_id: str,
    batch_size: int,
    threshold: float,
    dry_run: bool,
) -> dict[str, int]:
    """Process sentiment analysis for all sentences."""
    created_at = datetime.now(UTC).isoformat()

    # Get sentences for sentiment analysis
    query = f"""
    SELECT entity_id, text, session_id, content_date
    FROM `{STAGE_6_TABLE}`
    WHERE text IS NOT NULL AND LENGTH(TRIM(text)) > 5
    ORDER BY session_id, entity_id
    """

    sentences = list(bq_client.query(query).result())
    logger.info(f"Found {len(sentences)} sentences for sentiment analysis")

    if dry_run:
        return {
            "input_sentences": len(sentences),
            "sentiments_analyzed": 0,
            "dry_run": True,
        }

    classifier = get_sentiment_pipeline()

    records_to_insert = []
    total_analyzed = 0

    # Process in batches for efficiency
    for i in range(0, len(sentences), batch_size):
        batch_sentences = sentences[i : i + batch_size]
        texts = [s.text for s in batch_sentences]

        try:
            sentiment_results = process_sentiment_batch(classifier, texts, threshold)

            for sent, sentiment in zip(batch_sentences, sentiment_results):
                record = {
                    "entity_id": sent.entity_id,
                    "source_name": SOURCE_NAME,
                    "source_pipeline": PIPELINE_NAME,
                    "sentiment_model": SENTIMENT_MODEL,
                    "primary_emotion": sentiment["primary_emotion"],
                    "primary_score": sentiment["primary_score"],
                    "emotions_detected": json.dumps(sentiment["emotions_detected"]),
                    "all_scores": json.dumps(sentiment["all_scores"]),
                    "threshold_used": threshold,
                    "session_id": sent.session_id,
                    "content_date": sent.content_date,
                    "created_at": created_at,
                    "run_id": run_id,
                }
                records_to_insert.append(record)

            total_analyzed += len(batch_sentences)

        except Exception as e:
            logger.error(f"Sentiment batch failed: {e}")
            continue

        # Insert to BigQuery
        if len(records_to_insert) >= 1000:
            errors = bq_client.insert_rows_json(STAGE_11_TABLE, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

    # Insert remaining
    if records_to_insert:
        errors = bq_client.insert_rows_json(STAGE_11_TABLE, records_to_insert)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")

    return {
        "input_sentences": len(sentences),
        "sentiments_analyzed": total_analyzed,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 11: Sentiment analysis")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=11, stage_name="sentiment", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_6)
            if not args.dry_run:
                create_stage_11_table(bq_client)

            stats = process_sentiment(
                bq_client, run_id, args.batch_size, args.threshold, args.dry_run
            )
            tracker.update_progress(items_processed=stats["sentiments_analyzed"])

            print(f"\nSTAGE 11 COMPLETE: {stats['sentiments_analyzed']} sentiments analyzed")
            print(f"Model: {SENTIMENT_MODEL}")
            print(f"Threshold: {args.threshold}")
            return 0

        except Exception as e:
            logger.error(f"Stage 11 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_11_sentiment")
            return 1


if __name__ == "__main__":
    sys.exit(main())
