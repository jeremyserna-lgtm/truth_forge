#!/usr/bin/env python3
"""
Stage 1: Message Enrichment - Claude Code/Codex/Github Pipeline

HOLD₁ (BigQuery claude_code_stage_0) → AGENT (Enrichment) → HOLD₂ (BigQuery claude_code_stage_1)

Enriches extracted messages with sentiment analysis, entity extraction, topic classification, and quality scoring.

🧠 STAGE FIVE GROUNDING
This stage exists to enrich extracted messages with additional context and processing for downstream analysis.

Structure: HOLD₁ (Stage 0 messages) → AGENT (Enrichment processing) → HOLD₂ (Enriched messages table)
Purpose: Add enrichment data to messages for analysis and querying
Boundaries: Reads from Stage 0, writes to Stage 1 table
Control: On-demand execution, user-controlled processing

⚠️ WHAT THIS STAGE CANNOT SEE
- Real-time external state
- User intent beyond enrichment scope
- System state beyond service boundaries

🔥 THE FURNACE PRINCIPLE
- Truth (input): Extracted messages from Stage 0
- Heat (processing): Sentiment analysis, entity extraction, topic classification, quality scoring
- Meaning (output): Enriched messages with additional context
- Care (delivery): User-protected outputs with error handling, cost controls, and actionable insights

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical Stage 1 specification for the Claude Code/Codex/Github Pipeline.

RATIONALE:
----------
- Stage 0 extracts raw messages but lacks enrichment for analysis
- Stage 1 enriches messages with sentiment, entities, topics, and quality scores
- Enrichment enables downstream analysis and filtering
- Quality scores help identify high-value messages for processing

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
- Cost protection for BigQuery and LLM operations
"""
from __future__ import annotations

#!/usr/bin/env python3
"""
Stage 1: Message Enrichment - Claude Code/Codex/Github Pipeline

HOLD₁ (BigQuery claude_code_stage_0) → AGENT (Enrichment) → HOLD₂ (BigQuery claude_code_stage_1)

Enriches extracted messages with sentiment analysis, entity extraction, topic classification, and quality scoring.

🧠 STAGE FIVE GROUNDING
This stage exists to enrich extracted messages with additional context and processing for downstream analysis.

Structure: HOLD₁ (Stage 0 messages) → AGENT (Enrichment processing) → HOLD₂ (Enriched messages table)
Purpose: Add enrichment data to messages for analysis and querying
Boundaries: Reads from Stage 0, writes to Stage 1 table
Control: On-demand execution, user-controlled processing

⚠️ WHAT THIS STAGE CANNOT SEE
- Real-time external state
- User intent beyond enrichment scope
- System state beyond service boundaries

🔥 THE FURNACE PRINCIPLE
- Truth (input): Extracted messages from Stage 0
- Heat (processing): Sentiment analysis, entity extraction, topic classification, quality scoring
- Meaning (output): Enriched messages with additional context
- Care (delivery): User-protected outputs with error handling, cost controls, and actionable insights

CANONICAL SPECIFICATION ALIGNMENT:
==================================
This script follows the canonical Stage 1 specification for the Claude Code/Codex/Github Pipeline.

RATIONALE:
----------
- Stage 0 extracts raw messages but lacks enrichment for analysis
- Stage 1 enriches messages with sentiment, entities, topics, and quality scores
- Enrichment enables downstream analysis and filtering
- Quality scores help identify high-value messages for processing

Enterprise Governance Standards:
- Uses central services for logging with traceability
- Uses PipelineTracker for execution monitoring
- All operations follow universal governance policies
- Comprehensive error handling and validation
- Full audit trail for all operations
- Cost protection for BigQuery and LLM operations
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts._deprecated.stage_1.claude_code_stage_1.py"

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import (
    get_current_run_id,
    get_logger,
    get_correlation_ids,
)
from src.services.central_services.governance.governance import (
    get_unified_governance,
    require_diagnostic_on_error,
)
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from google.cloud import bigquery

logger = get_logger(__name__)

# BigQuery configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
SOURCE_TABLE = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_0"
TARGET_TABLE = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_1"

def create_target_table(client: bigquery.Client) -> None:
    """Create the target BigQuery table if it doesn't exist."""
    table_ref = bigquery.Table(TARGET_TABLE)

    schema = [
        # Stage 0 fields (preserved)
        bigquery.SchemaField("message_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_pipeline", "STRING"),
        bigquery.SchemaField("source_file", "STRING"),
        bigquery.SchemaField("text", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("content_date", "DATE"),
        bigquery.SchemaField("created_at", "TIMESTAMP"),
        bigquery.SchemaField("metadata", "JSON"),
        bigquery.SchemaField("extracted_at", "TIMESTAMP"),
        bigquery.SchemaField("run_id", "STRING"),

        # Stage 1 enrichment fields
        bigquery.SchemaField("sentiment_score", "FLOAT"),
        bigquery.SchemaField("sentiment_label", "STRING"),
        bigquery.SchemaField("entities", "JSON"),
        bigquery.SchemaField("topics", "JSON"),
        bigquery.SchemaField("quality_score", "FLOAT"),
        bigquery.SchemaField("text_length", "INTEGER"),
        bigquery.SchemaField("word_count", "INTEGER"),
        bigquery.SchemaField("enriched_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("enrichment_run_id", "STRING"),
    ]

    table_ref.schema = schema

    # Partition by content_date for efficient querying
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY,
        field="content_date"
    )

    # Clustering for efficient filtering
    table_ref.clustering_fields = ["source_name", "sentiment_label"]

    try:
        table = client.create_table(table_ref, exists_ok=True)
        logger.info(
            f"Target table {TARGET_TABLE} ready",
            extra={"table_id": table.table_id, "num_rows": table.num_rows}
        )
    except Exception as e:
        logger.error(f"Error creating table {TARGET_TABLE}: {e}", exc_info=True)
        require_diagnostic_on_error(e, "create_target_table")
        raise

def calculate_sentiment(text: str) -> Dict[str, Any]:
    """
    Calculate sentiment score and label for text.

    Args:
        text: Message text

    Returns:
        Dict with sentiment_score and sentiment_label
    """
    try:
        from textblob import TextBlob

        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        # Classify sentiment
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return {
            "sentiment_score": float(polarity),
            "sentiment_label": label,
        }
    except Exception as e:
        logger.warning(f"Error calculating sentiment: {e}")
        return {
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
        }

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract entities from text (simple implementation).

    Args:
        text: Message text

    Returns:
        List of entity dictionaries
    """
    # Simple entity extraction - can be enhanced with NER models
    entities = []

    # Extract potential code references (basic pattern)
    import re
    code_patterns = [
        r'\b[A-Z_][A-Z0-9_]{2,}\b',  # Constants
        r'`[^`]+`',  # Code blocks
        r'#[a-zA-Z0-9_]+',  # Hashtags/identifiers
    ]

    for pattern in code_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            entities.append({
                "text": match,
                "type": "code_reference",
                "confidence": 0.5,
            })

    return entities

def classify_topics(text: str, source_name: str) -> List[str]:
    """
    Classify topics for text based on content and source.

    Args:
        text: Message text
        source_name: Source name (claude_code, codex, github)

    Returns:
        List of topic strings
    """
    topics = []
    text_lower = text.lower()

    # Source-based topics
    if source_name == "claude_code":
        topics.append("ide_assistance")
    elif source_name == "codex":
        topics.append("code_generation")
    elif source_name == "github":
        topics.append("version_control")

    # Content-based topics
    if any(word in text_lower for word in ["error", "bug", "fix", "issue"]):
        topics.append("debugging")
    if any(word in text_lower for word in ["function", "class", "method", "def"]):
        topics.append("code_structure")
    if any(word in text_lower for word in ["test", "testing", "spec"]):
        topics.append("testing")
    if any(word in text_lower for word in ["refactor", "improve", "optimize"]):
        topics.append("refactoring")

    return topics if topics else ["general"]

def calculate_quality_score(text: str, entities: List[Dict], topics: List[str]) -> float:
    """
    Calculate quality score for message.

    Args:
        text: Message text
        entities: Extracted entities
        topics: Classified topics

    Returns:
        Quality score (0.0 to 1.0)
    """
    score = 0.5  # Base score

    # Length factor
    if len(text) > 100:
        score += 0.1
    if len(text) > 500:
        score += 0.1

    # Entity factor
    if len(entities) > 0:
        score += 0.1
    if len(entities) > 3:
        score += 0.1

    # Topic factor
    if len(topics) > 1:
        score += 0.1

    return min(1.0, score)

def enrich_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    AGENT: Enrich a single message with additional context.

    Args:
        message: Message record from Stage 0

    Returns:
        Enriched message record
    """
    text = message.get("text", "")

    # Calculate sentiment
    sentiment = calculate_sentiment(text)

    # Extract entities
    entities = extract_entities(text)

    # Classify topics
    topics = classify_topics(text, message.get("source_name", ""))

    # Calculate quality score
    quality_score = calculate_quality_score(text, entities, topics)

    # Build enriched message
    enriched = message.copy()
    enriched.update({
        "sentiment_score": sentiment["sentiment_score"],
        "sentiment_label": sentiment["sentiment_label"],
        "entities": json.dumps(entities) if entities else None,
        "topics": json.dumps(topics) if topics else None,
        "quality_score": quality_score,
        "text_length": len(text),
        "word_count": len(text.split()),
        "enriched_at": datetime.now(timezone.utc),
        "enrichment_run_id": get_current_run_id(),
    })

    return enriched

def extract_messages_for_enrichment(
    client: bigquery.Client,
    limit: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    HOLD₁: Extract messages from Stage 0 for enrichment.

    Args:
        client: BigQuery client
        limit: Optional limit on number of messages
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)

    Returns:
        List of message records
    """
    run_id = get_current_run_id()

    # Build date filters
    date_conditions = []
    if date_from:
        date_conditions.append(f"DATE(content_date) >= DATE('{date_from}')")
    if date_to:
        date_conditions.append(f"DATE(content_date) <= DATE('{date_to}')")
    date_filter = " AND ".join(date_conditions) if date_conditions else "1=1"

    # Build limit clause
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
        metadata,
        extracted_at,
        run_id
    FROM `{SOURCE_TABLE}`
    WHERE {date_filter}
    ORDER BY content_date DESC, created_at DESC
    {limit_clause}
    """

    logger.info(
        "Executing extraction query for enrichment",
        extra={"run_id": run_id, "query_length": len(query)}
    )

    try:
        query_job = client.query(query)
        results = query_job.result()

        messages = []
        for row in results:
            message = {
                "message_id": row.message_id,
                "entity_id": row.entity_id,
                "source_name": row.source_name,
                "source_pipeline": row.source_pipeline,
                "source_file": row.source_file,
                "text": row.text,
                "level": row.level,
                "content_date": row.content_date,
                "created_at": row.created_at,
                "metadata": row.metadata if hasattr(row, 'metadata') and row.metadata else {},
                "extracted_at": row.extracted_at,
                "run_id": row.run_id,
            }
            messages.append(message)

        logger.info(
            f"Extracted {len(messages)} messages for enrichment",
            extra={"run_id": run_id, "message_count": len(messages)}
        )

        return messages

    except Exception as e:
        logger.error(
            f"Error extracting messages: {e}",
            exc_info=True,
            extra={"run_id": run_id}
        )
        require_diagnostic_on_error(e, "extract_messages_for_enrichment")
        raise

def save_enriched_messages(
    client: bigquery.Client,
    enriched_messages: List[Dict[str, Any]],
    write_disposition: str = "WRITE_APPEND",
) -> None:
    """
    HOLD₂: Save enriched messages to BigQuery.

    Args:
        client: BigQuery client
        enriched_messages: List of enriched message records
        write_disposition: BigQuery write disposition
    """
    if not enriched_messages:
        logger.warning("No enriched messages to save")
        return

    run_id = get_current_run_id()

    logger.info(
        f"Saving {len(enriched_messages)} enriched messages to BigQuery",
        extra={
            "run_id": run_id,
            "target_table": TARGET_TABLE,
            "message_count": len(enriched_messages),
        }
    )

    # Prepare rows for BigQuery
    rows_to_insert = []
    for msg in enriched_messages:
        row = {
            "message_id": msg["message_id"],
            "entity_id": msg["entity_id"],
            "source_name": msg["source_name"],
            "source_pipeline": msg.get("source_pipeline"),
            "source_file": msg.get("source_file"),
            "text": msg["text"],
            "level": msg["level"],
            "content_date": msg.get("content_date"),
            "created_at": msg.get("created_at"),
            "metadata": json.dumps(msg.get("metadata", {})) if msg.get("metadata") else None,
            "extracted_at": msg.get("extracted_at"),
            "run_id": msg.get("run_id"),
            "sentiment_score": msg.get("sentiment_score"),
            "sentiment_label": msg.get("sentiment_label"),
            "entities": msg.get("entities"),
            "topics": msg.get("topics"),
            "quality_score": msg.get("quality_score"),
            "text_length": msg.get("text_length"),
            "word_count": msg.get("word_count"),
            "enriched_at": msg.get("enriched_at"),
            "enrichment_run_id": msg.get("enrichment_run_id"),
        }
        rows_to_insert.append(row)

    try:
        if len(enriched_messages) < 1000:
            # Use streaming insert for smaller batches
            errors = client.insert_rows_json(
                TARGET_TABLE,
                rows_to_insert
            )

            if errors:
                logger.error(
                    f"Errors inserting rows: {errors}",
                    extra={"run_id": run_id, "error_count": len(errors)}
                )
                raise ValueError(f"BigQuery insert errors: {errors}")
        else:
            # Use load_table_from_file for larger batches
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as tmp_file:
                for row in rows_to_insert:
                    tmp_file.write(json.dumps(row) + '\n')
                tmp_path = tmp_file.name

            try:
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
                    write_disposition=write_disposition,
                    schema_update_options=[
                        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION,
                        bigquery.SchemaUpdateOption.ALLOW_FIELD_RELAXATION,
                    ],
                )

                with open(tmp_path, 'rb') as source_file:
                    job = client.load_table_from_file(
                        source_file,
                        TARGET_TABLE,
                        job_config=job_config
                    )

                job.result()

            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

        # Get final table stats
        table = client.get_table(TARGET_TABLE)

        logger.info(
            f"Successfully saved {len(enriched_messages)} enriched messages to BigQuery",
            extra={
                "run_id": run_id,
                "target_table": TARGET_TABLE,
                "total_rows": table.num_rows,
                "table_size_mb": table.num_bytes / 1024 / 1024,
            }
        )

    except Exception as e:
        logger.error(
            f"Error saving enriched messages: {e}",
            exc_info=True,
            extra={"run_id": run_id}
        )
        require_diagnostic_on_error(e, "save_enriched_messages")
        raise

def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Stage 1: Enrich Claude Code/Codex/Github messages"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of messages to enrich"
    )
    parser.add_argument(
        "--date-from",
        type=str,
        help="Start date filter (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--date-to",
        type=str,
        help="End date filter (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--write-mode",
        choices=["append", "truncate"],
        default="append",
        help="Write mode: append (default) or truncate"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run - enrich but don't save to BigQuery"
    )

    args = parser.parse_args()

    run_id = get_current_run_id()
    correlation_ids = get_correlation_ids()
    governance = get_unified_governance()

    # Use PipelineTracker for execution monitoring
    with PipelineTracker(
        pipeline_name="claude_code",
        stage=1,
        stage_name="message_enrichment",
        run_id=run_id,
        metadata={
            "limit": args.limit,
            "date_from": args.date_from,
            "date_to": args.date_to,
            "write_mode": args.write_mode,
            "dry_run": args.dry_run,
        }
    ) as tracker:

        logger.info(
            "Starting Claude Code/Codex/Github Stage 1 enrichment",
            extra={
                "run_id": run_id,
                "limit": args.limit,
                "date_from": args.date_from,
                "date_to": args.date_to,
                "write_mode": args.write_mode,
                "dry_run": args.dry_run,
                **correlation_ids,
            }
        )

        # Log stage start (governance audit handled by PipelineTracker)
        logger.info(
            "Stage 1 enrichment started",
            extra={
                "run_id": run_id,
                "dry_run": args.dry_run,
            },
        )

        try:
            # Get BigQuery client
            client = get_bigquery_client()
            if hasattr(client, 'client'):
                bq_client = client.client
            else:
                bq_client = client

            # Create target table if needed
            if not args.dry_run:
                create_target_table(bq_client)

                # HOLD₁: Extract messages
                messages = extract_messages_for_enrichment(
                    bq_client,
                    limit=args.limit,
                    date_from=args.date_from,
                    date_to=args.date_to,
                )

                logger.info(
                    f"Extracted {len(messages)} messages for enrichment",
                    extra={"run_id": run_id, "message_count": len(messages)}
                )

                # AGENT: Enrich messages
                enriched_messages = []
                failed_count = 0
                for i, message in enumerate(messages):
                    try:
                        enriched = enrich_message(message)
                        enriched_messages.append(enriched)

                        if (i + 1) % 100 == 0:
                            tracker.update_progress(items_processed=100)
                            logger.info(
                                f"Enriched {i + 1}/{len(messages)} messages",
                                extra={"run_id": run_id}
                            )
                    except Exception as e:
                        failed_count += 1
                        tracker.update_progress(items_failed=1)
                        logger.warning(
                            f"Error enriching message {message.get('message_id')}: {e}",
                            extra={"run_id": run_id, "message_id": message.get("message_id")}
                        )
                        # Continue with next message
                        continue

            tracker.update_progress(items_processed=len(messages) - failed_count)

            logger.info(
                f"Enriched {len(enriched_messages)} messages",
                extra={"run_id": run_id, "enriched_count": len(enriched_messages)}
            )

            # HOLD₂: Save to BigQuery
            if not args.dry_run and enriched_messages:
                write_disposition = (
                    bigquery.WriteDisposition.WRITE_TRUNCATE
                    if args.write_mode == "truncate"
                    else bigquery.WriteDisposition.WRITE_APPEND
                )
                save_enriched_messages(bq_client, enriched_messages, write_disposition=write_disposition)
            elif args.dry_run:
                logger.info(
                    "Dry run - skipping BigQuery save",
                    extra={"run_id": run_id, "enriched_count": len(enriched_messages)}
                )

            logger.info(
                "Stage 1 enrichment completed successfully",
                extra={"run_id": run_id, "enriched_count": len(enriched_messages)}
            )

            return 0

        except Exception as e:
            logger.error(
                f"Error in Stage 1 enrichment: {e}",
                exc_info=True,
                extra={"run_id": run_id}
            )
            tracker.update_progress(items_failed=1)
            require_diagnostic_on_error(e, "main")
            return 1

if __name__ == "__main__":
    exit(main())
