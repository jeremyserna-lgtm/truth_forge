#!/usr/bin/env python3
"""Stage 5: L1 Token Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Tokenizer) → HOLD₂ (claude_code_stage_5)

Creates Level 1 token entities from message content using spaCy tokenization.
Tokens are the atomic unit of the SPINE hierarchy.

🧠 STAGE FIVE GROUNDING
This stage exists to create L1 token entities from message text.

Structure: Read messages → Tokenize with spaCy → Generate token entities → Write
Purpose: Create atomic token entities for linguistic analysis
Boundaries: Tokenization only, no semantic analysis
Control: Batch processing, NLP model initialization per worker

⚠️ WHAT THIS STAGE CANNOT SEE
- Token semantics or meaning
- Cross-message relationships
- Sentence boundaries (handled in Stage 6)
- Future analysis requirements

🔥 THE FURNACE PRINCIPLE
- Truth (input): Message text from staged data
- Heat (processing): spaCy tokenization, POS tagging, lemmatization
- Meaning (output): L1 token entities with linguistic features
- Care (delivery): Complete token coverage, NLP annotations

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 5 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 5 creates L1 tokens (lowest level of SPINE hierarchy)
- Tokens enable word-level analysis and search
- Creates foundation for sentence and message aggregation

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Parallel processing for efficiency

Usage:
    python claude_code_stage_5.py [--batch-size N] [--workers N] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 5: L1 Token Creation - Claude Code Pipeline

HOLD₁ (claude_code_stage_4) → AGENT (Tokenizer) → HOLD₂ (claude_code_stage_5)

Creates Level 1 token entities from message content using spaCy tokenization.
Tokens are the atomic unit of the SPINE hierarchy.

🧠 STAGE FIVE GROUNDING
This stage exists to create L1 token entities from message text.

Structure: Read messages → Tokenize with spaCy → Generate token entities → Write
Purpose: Create atomic token entities for linguistic analysis
Boundaries: Tokenization only, no semantic analysis
Control: Batch processing, NLP model initialization per worker

⚠️ WHAT THIS STAGE CANNOT SEE
- Token semantics or meaning
- Cross-message relationships
- Sentence boundaries (handled in Stage 6)
- Future analysis requirements

🔥 THE FURNACE PRINCIPLE
- Truth (input): Message text from staged data
- Heat (processing): spaCy tokenization, POS tagging, lemmatization
- Meaning (output): L1 token entities with linguistic features
- Care (delivery): Complete token coverage, NLP annotations

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows Stage 5 of the Universal Pipeline Pattern for claude_code.

RATIONALE:
----------
- Stage 5 creates L1 tokens (lowest level of SPINE hierarchy)
- Tokens enable word-level analysis and search
- Creates foundation for sentence and message aggregation

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Parallel processing for efficiency

Usage:
    python claude_code_stage_5.py [--batch-size N] [--workers N] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_5.claude_code_stage_5.py"

import argparse
import hashlib
import sys
from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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
    LEVEL_TOKEN,
    PIPELINE_NAME,
    SOURCE_NAME,
    TABLE_STAGE_4,
    TABLE_STAGE_5,
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
STAGE_4_TABLE = get_full_table_id(TABLE_STAGE_4)
STAGE_5_TABLE = get_full_table_id(TABLE_STAGE_5)

# Token table schema
TOKEN_SCHEMA = [
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("parent_id", "STRING", mode="REQUIRED"),  # L5 message entity_id
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("text", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("token_index", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("lemma", "STRING"),
    bigquery.SchemaField("pos", "STRING"),
    bigquery.SchemaField("tag", "STRING"),
    bigquery.SchemaField("dep", "STRING"),
    bigquery.SchemaField("is_stop", "BOOLEAN"),
    bigquery.SchemaField("is_alpha", "BOOLEAN"),
    bigquery.SchemaField("is_punct", "BOOLEAN"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_5_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 5 (tokens) table."""
    table_ref = bigquery.Table(STAGE_5_TABLE, schema=TOKEN_SCHEMA)

    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="content_date",
    )
    table_ref.clustering_fields = ["parent_id", "session_id"]

    try:
        table = client.create_table(table_ref, exists_ok=True)
        logger.info(f"Stage 5 table ready: {STAGE_5_TABLE}")
        return table
    except Exception as e:
        require_diagnostic_on_error(e, "create_stage_5_table")
        raise


def generate_token_id(parent_id: str, token_index: int) -> str:
    """Generate deterministic token entity_id."""
    content = f"L1:{parent_id}:{token_index}"
    return hashlib.sha256(content.encode()).hexdigest()[:32]


def tokenize_message(
    message: dict[str, Any],
    nlp,
    run_id: str,
    created_at: str,
) -> Generator[dict[str, Any], None, None]:
    """Tokenize a message and yield token records.

    Args:
        message: Message record from stage 4
        nlp: spaCy NLP model
        run_id: Current run ID
        created_at: Creation timestamp

    Yields:
        Token records
    """
    text = message.get("text") or ""
    if not text.strip():
        return

    parent_id = message["entity_id"]
    session_id = message.get("session_id")
    content_date = message.get("content_date")

    doc = nlp(text)

    for idx, token in enumerate(doc):
        token_id = generate_token_id(parent_id, idx)

        yield {
            "entity_id": token_id,
            "parent_id": parent_id,
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "level": LEVEL_TOKEN,
            "text": token.text,
            "token_index": idx,
            "lemma": token.lemma_,
            "pos": token.pos_,
            "tag": token.tag_,
            "dep": token.dep_,
            "is_stop": token.is_stop,
            "is_alpha": token.is_alpha,
            "is_punct": token.is_punct,
            "session_id": session_id,
            "content_date": content_date,
            "created_at": created_at,
            "run_id": run_id,
        }


def process_tokenization(
    client: bigquery.Client,
    run_id: str,
    batch_size: int,
    dry_run: bool,
) -> dict[str, int]:
    """Process tokenization for all messages.

    Args:
        client: BigQuery client
        run_id: Current run ID
        batch_size: Batch size for inserts
        dry_run: If True, don't write results

    Returns:
        Processing statistics
    """
    # Load spaCy model
    try:
        import spacy

        nlp = spacy.load("en_core_web_sm")
    except Exception as e:
        logger.error(f"Failed to load spaCy model: {e}")
        raise

    created_at = datetime.now(UTC).isoformat()

    # Fetch messages from stage 4
    query = f"""
    SELECT entity_id, text, session_id, content_date
    FROM `{STAGE_4_TABLE}`
    WHERE text IS NOT NULL AND TRIM(text) != ''
    """

    if dry_run:
        count_query = f"SELECT COUNT(*) as cnt FROM `{STAGE_4_TABLE}` WHERE text IS NOT NULL"
        result = client.query(count_query).result()
        row = next(iter(result))
        return {"messages_processed": row.cnt, "tokens_created": 0, "dry_run": True}

    logger.info("Fetching messages for tokenization...")
    query_job = client.query(query)
    messages = list(query_job.result())

    logger.info(f"Processing {len(messages)} messages...")

    tokens_batch = []
    total_tokens = 0

    for msg in messages:
        msg_dict = dict(msg)

        for token_record in tokenize_message(msg_dict, nlp, run_id, created_at):
            tokens_batch.append(token_record)

            if len(tokens_batch) >= batch_size:
                errors = client.insert_rows_json(STAGE_5_TABLE, tokens_batch)
                if errors:
                    logger.warning(f"Insert errors: {errors[:3]}")
                total_tokens += len(tokens_batch)
                tokens_batch = []

    # Insert remaining tokens
    if tokens_batch:
        errors = client.insert_rows_json(STAGE_5_TABLE, tokens_batch)
        if errors:
            logger.warning(f"Insert errors: {errors[:3]}")
        total_tokens += len(tokens_batch)

    return {
        "messages_processed": len(messages),
        "tokens_created": total_tokens,
        "dry_run": False,
    }


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Stage 5: Create L1 token entities")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Batch size for inserts (default: 5000)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count records but don't create tokens",
    )

    args = parser.parse_args()
    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME,
        stage=5,
        stage_name="l1_tokens",
        run_id=run_id,
        metadata={"batch_size": args.batch_size, "dry_run": args.dry_run},
    ) as tracker:
        try:
            logger.info("Starting Stage 5: L1 Token Creation", extra={"run_id": run_id})

            client = get_bigquery_client()
            if hasattr(client, "client"):
                bq_client = client.client
            else:
                bq_client = client

            validate_input_table_exists(bq_client, TABLE_STAGE_4)

            if not args.dry_run:
                create_stage_5_table(bq_client)

            stats = process_tokenization(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats["tokens_created"])

            logger.info(
                f"Stage 5 complete: {stats['tokens_created']} tokens created",
                extra={"run_id": run_id, **stats},
            )

            print(f"\n{'=' * 60}")
            print("STAGE 5 COMPLETE: L1 Token Creation")
            print(f"{'=' * 60}")
            print(f"Messages processed: {stats['messages_processed']}")
            print(f"Tokens created: {stats['tokens_created']}")
            print(f"Target table: {STAGE_5_TABLE}")
            print(f"Dry run: {args.dry_run}")

            return 0

        except Exception as e:
            logger.error(f"Stage 5 failed: {e}", exc_info=True, extra={"run_id": run_id})
            require_diagnostic_on_error(e, "stage_5_tokens")
            tracker.update_progress(items_failed=1)
            return 1


if __name__ == "__main__":
    sys.exit(main())
