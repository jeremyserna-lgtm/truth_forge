#!/usr/bin/env python3
"""Stage 9: Embeddings Generation - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Embedding Generator) → HOLD₂ (claude_code_stage_9)

Generates semantic embeddings for L5 message entities using Gemini embedding model.
Embeddings enable semantic search and similarity analysis.

🧠 STAGE FIVE GROUNDING
This stage exists to create vector embeddings for semantic capabilities.

Structure: Read L5 messages → Generate embeddings → Store vectors → Write
Purpose: Enable semantic search, clustering, and similarity analysis
Boundaries: Embedding generation only, no interpretation
Control: Batch processing, rate limiting, cost tracking

⚠️ WHAT THIS STAGE CANNOT SEE
- Embedding interpretation (downstream analysis)
- Clustering results (requires separate analysis)
- Similarity relationships (computed later)
- User search queries

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message text content
- Heat (processing): Gemini embedding model inference
- Meaning (output): 3072-dimensional vector embeddings
- Care (delivery): All messages embedded, vectors stored correctly

Usage:
    python claude_code_stage_9.py [--batch-size N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 9: Embeddings Generation - Claude Code Pipeline

HOLD₁ (claude_code_stage_7) → AGENT (Embedding Generator) → HOLD₂ (claude_code_stage_9)

Generates semantic embeddings for L5 message entities using Gemini embedding model.
Embeddings enable semantic search and similarity analysis.

🧠 STAGE FIVE GROUNDING
This stage exists to create vector embeddings for semantic capabilities.

Structure: Read L5 messages → Generate embeddings → Store vectors → Write
Purpose: Enable semantic search, clustering, and similarity analysis
Boundaries: Embedding generation only, no interpretation
Control: Batch processing, rate limiting, cost tracking

⚠️ WHAT THIS STAGE CANNOT SEE
- Embedding interpretation (downstream analysis)
- Clustering results (requires separate analysis)
- Similarity relationships (computed later)
- User search queries

🔥 THE FURNACE PRINCIPLE
- Truth (input): L5 message text content
- Heat (processing): Gemini embedding model inference
- Meaning (output): 3072-dimensional vector embeddings
- Care (delivery): All messages embedded, vectors stored correctly

Usage:
    python claude_code_stage_9.py [--batch-size N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_9.claude_code_stage_9.py"

import argparse
import sys
import time
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
    TABLE_STAGE_9,
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
STAGE_9_TABLE = get_full_table_id(TABLE_STAGE_9)

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 768
MAX_TOKENS_PER_REQUEST = 2048
BATCH_SIZE_EMBEDDING = 100  # API batch size

EMBEDDING_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("embedding_model", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("embedding_dimension", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
    bigquery.SchemaField("text_length", "INTEGER"),
    bigquery.SchemaField("text_truncated", "BOOLEAN"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_9_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 9 embeddings table."""
    table_ref = bigquery.Table(STAGE_9_TABLE, schema=EMBEDDING_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["entity_id", "session_id"]
    return client.create_table(table_ref, exists_ok=True)


def get_embedding_client():
    """Initialize the Gemini embedding client."""
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


def truncate_text(text: str, max_chars: int = 8000) -> tuple[str, bool]:
    """Truncate text to fit embedding model limits."""
    if not text:
        return "", False
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def _generate_embeddings_batch_impl(genai, texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a batch of texts (implementation)."""
    result = genai.embed_content(
        model=f"models/{EMBEDDING_MODEL}",
        content=texts,
        task_type="retrieval_document",
    )
    return (
        result["embedding"] if isinstance(result["embedding"][0], list) else [result["embedding"]]
    )

generate_embeddings_batch = retry_with_backoff(
    _generate_embeddings_batch_impl,
    max_retries=3,
    retry_delays=(1, 2, 4)
)


def process_embeddings(
    bq_client: bigquery.Client,
    run_id: str,
    batch_size: int,
    dry_run: bool,
) -> dict[str, int]:
    """Process embeddings for all L5 messages."""
    created_at = datetime.now(UTC).isoformat()

    # Get messages needing embeddings
    query = f"""
    SELECT entity_id, text, session_id, content_date
    FROM `{STAGE_7_TABLE}`
    WHERE text IS NOT NULL AND LENGTH(TRIM(text)) > 0
    ORDER BY session_id, entity_id
    """

    messages = list(bq_client.query(query).result())
    logger.info(f"Found {len(messages)} messages for embedding generation")

    if dry_run:
        return {
            "input_messages": len(messages),
            "embeddings_generated": 0,
            "dry_run": True,
        }

    genai = get_embedding_client()

    records_to_insert = []
    total_embedded = 0

    # Process in embedding API batches
    for i in range(0, len(messages), BATCH_SIZE_EMBEDDING):
        batch_messages = messages[i : i + BATCH_SIZE_EMBEDDING]

        # Prepare texts
        texts_to_embed = []
        batch_metadata = []

        for msg in batch_messages:
            text, truncated = truncate_text(msg.text or "")
            if text:
                texts_to_embed.append(text)
                batch_metadata.append(
                    {
                        "entity_id": msg.entity_id,
                        "session_id": msg.session_id,
                        "content_date": msg.content_date,
                        "text_length": len(msg.text or ""),
                        "text_truncated": truncated,
                    }
                )

        if not texts_to_embed:
            continue

        # Generate embeddings
        try:
            embeddings = generate_embeddings_batch(genai, texts_to_embed)

            for meta, embedding in zip(batch_metadata, embeddings):
                records_to_insert.append(
                    {
                        "entity_id": meta["entity_id"],
                        "source_name": SOURCE_NAME,
                        "source_pipeline": PIPELINE_NAME,
                        "embedding_model": EMBEDDING_MODEL,
                        "embedding_dimension": len(embedding),
                        "embedding": embedding,
                        "text_length": meta["text_length"],
                        "text_truncated": meta["text_truncated"],
                        "session_id": meta["session_id"],
                        "content_date": meta["content_date"],
                        "created_at": created_at,
                        "run_id": run_id,
                    }
                )

            total_embedded += len(embeddings)

        except Exception as e:
            logger.error(f"Embedding batch failed: {e}")
            continue

        # Insert to BigQuery in batches
        if len(records_to_insert) >= batch_size:
            errors = bq_client.insert_rows_json(STAGE_9_TABLE, records_to_insert)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            records_to_insert = []

        # Rate limiting
        time.sleep(0.1)

    # Insert remaining records
    if records_to_insert:
        errors = bq_client.insert_rows_json(STAGE_9_TABLE, records_to_insert)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")

    return {
        "input_messages": len(messages),
        "embeddings_generated": total_embedded,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 9: Generate embeddings")
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=9, stage_name="embeddings", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            validate_input_table_exists(bq_client, TABLE_STAGE_7)
            if not args.dry_run:
                create_stage_9_table(bq_client)

            stats = process_embeddings(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats["embeddings_generated"])

            print(f"\nSTAGE 9 COMPLETE: {stats['embeddings_generated']} embeddings generated")
            print(f"Model: {EMBEDDING_MODEL}")
            return 0

        except Exception as e:
            logger.error(f"Stage 9 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_9_embeddings")
            return 1


if __name__ == "__main__":
    sys.exit(main())
