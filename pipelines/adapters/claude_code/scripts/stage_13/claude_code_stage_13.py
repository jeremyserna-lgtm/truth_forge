#!/usr/bin/env python3
"""Stage 13: Relationship Detection - Claude Code Pipeline

HOLD₁ (multiple stages) → AGENT (Relationship Builder) → HOLD₂ (claude_code_stage_13)

Detects and creates relationships between entities:
- Message → Sentence (parent-child)
- Conversation → Message (parent-child)
- User → Assistant (turn pairs)
- Topic similarity (cosine similarity)

🧠 STAGE FIVE GROUNDING
This stage exists to create the relationship graph between entities.

Structure: Read entities → Compute relationships → Store edges → Write
Purpose: Enable graph-based analysis and navigation
Boundaries: Relationship creation only, no graph analysis
Control: Consistent edge types, proper entity references

⚠️ WHAT THIS STAGE CANNOT SEE
- Relationship semantics beyond edge type
- Graph metrics (computed downstream)
- Causal relationships
- Temporal dependencies

🔥 THE FURNACE PRINCIPLE
- Truth (input): Entities from multiple stages
- Heat (processing): Relationship detection and similarity computation
- Meaning (output): Entity relationship edges
- Care (delivery): Complete relationship coverage, valid references

Usage:
    python claude_code_stage_13.py [--similarity-threshold F] [--dry-run]
"""

from __future__ import annotations


#!/usr/bin/env python3
"""Stage 13: Relationship Detection - Claude Code Pipeline

HOLD₁ (multiple stages) → AGENT (Relationship Builder) → HOLD₂ (claude_code_stage_13)

Detects and creates relationships between entities:
- Message → Sentence (parent-child)
- Conversation → Message (parent-child)
- User → Assistant (turn pairs)
- Topic similarity (cosine similarity)

🧠 STAGE FIVE GROUNDING
This stage exists to create the relationship graph between entities.

Structure: Read entities → Compute relationships → Store edges → Write
Purpose: Enable graph-based analysis and navigation
Boundaries: Relationship creation only, no graph analysis
Control: Consistent edge types, proper entity references

⚠️ WHAT THIS STAGE CANNOT SEE
- Relationship semantics beyond edge type
- Graph metrics (computed downstream)
- Causal relationships
- Temporal dependencies

🔥 THE FURNACE PRINCIPLE
- Truth (input): Entities from multiple stages
- Heat (processing): Relationship detection and similarity computation
- Meaning (output): Entity relationship edges
- Care (delivery): Complete relationship coverage, valid references

Usage:
    python claude_code_stage_13.py [--similarity-threshold F] [--dry-run]
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.stage_13.claude_code_stage_13.py"

import argparse
import hashlib
import json
import sys
from collections.abc import Generator
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
    TABLE_STAGE_6,
    TABLE_STAGE_7,
    TABLE_STAGE_8,
    TABLE_STAGE_13,
    get_full_table_id,
    validate_input_table_exists,
)
from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from src.services.central_services.core.pipeline_tracker import PipelineTracker
from src.services.central_services.governance.governance import require_diagnostic_on_error


logger = get_logger(__name__)

STAGE_6_TABLE = get_full_table_id(TABLE_STAGE_6)
STAGE_7_TABLE = get_full_table_id(TABLE_STAGE_7)
STAGE_8_TABLE = get_full_table_id(TABLE_STAGE_8)
STAGE_13_TABLE = get_full_table_id(TABLE_STAGE_13)

# Relationship types
REL_CONTAINS = "contains"
REL_BELONGS_TO = "belongs_to"
REL_FOLLOWS = "follows"
REL_RESPONDS_TO = "responds_to"
REL_SIMILAR_TOPIC = "similar_topic"

RELATIONSHIP_SCHEMA = [
    bigquery.SchemaField("relationship_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("target_entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("relationship_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_level", "INTEGER"),
    bigquery.SchemaField("target_level", "INTEGER"),
    bigquery.SchemaField("weight", "FLOAT"),
    bigquery.SchemaField("metadata", "STRING"),  # JSON
    bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("content_date", "DATE"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


def create_stage_13_table(client: bigquery.Client) -> bigquery.Table:
    """Create or get stage 13 relationships table."""
    table_ref = bigquery.Table(STAGE_13_TABLE, schema=RELATIONSHIP_SCHEMA)
    table_ref.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="content_date"
    )
    table_ref.clustering_fields = ["relationship_type", "source_entity_id"]
    return client.create_table(table_ref, exists_ok=True)


def generate_relationship_id(source_id: str, target_id: str, rel_type: str) -> str:
    """Generate deterministic relationship ID."""
    return hashlib.sha256(f"REL:{source_id}:{target_id}:{rel_type}".encode()).hexdigest()[:32]


def build_parent_child_relationships(
    bq_client: bigquery.Client,
    run_id: str,
    created_at: str,
) -> Generator[dict, None, None]:
    """Build parent-child relationships between entity levels."""

    # Message (L5) contains Sentence (L3)
    query = f"""
    SELECT
        m.entity_id as message_id,
        s.entity_id as sentence_id,
        m.session_id,
        m.content_date
    FROM `{STAGE_7_TABLE}` m
    JOIN `{STAGE_6_TABLE}` s ON m.entity_id = s.parent_id
    """

    for row in bq_client.query(query).result():
        yield {
            "relationship_id": generate_relationship_id(
                row.message_id, row.sentence_id, REL_CONTAINS
            ),
            "source_entity_id": row.message_id,
            "target_entity_id": row.sentence_id,
            "relationship_type": REL_CONTAINS,
            "source_level": 5,
            "target_level": 3,
            "weight": 1.0,
            "metadata": None,
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "session_id": row.session_id,
            "content_date": row.content_date,
            "created_at": created_at,
            "run_id": run_id,
        }

    # Conversation (L8) contains Message (L5)
    query = f"""
    SELECT
        c.entity_id as conversation_id,
        m.entity_id as message_id,
        m.session_id,
        m.content_date
    FROM `{STAGE_8_TABLE}` c
    JOIN `{STAGE_7_TABLE}` m ON c.session_id = m.session_id
    """

    for row in bq_client.query(query).result():
        yield {
            "relationship_id": generate_relationship_id(
                row.conversation_id, row.message_id, REL_CONTAINS
            ),
            "source_entity_id": row.conversation_id,
            "target_entity_id": row.message_id,
            "relationship_type": REL_CONTAINS,
            "source_level": 8,
            "target_level": 5,
            "weight": 1.0,
            "metadata": None,
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "session_id": row.session_id,
            "content_date": row.content_date,
            "created_at": created_at,
            "run_id": run_id,
        }


def build_sequential_relationships(
    bq_client: bigquery.Client,
    run_id: str,
    created_at: str,
) -> Generator[dict, None, None]:
    """Build sequential (follows) relationships between messages."""

    query = f"""
    SELECT
        m1.entity_id as source_id,
        m2.entity_id as target_id,
        m1.role as source_role,
        m2.role as target_role,
        m1.session_id,
        m1.content_date
    FROM `{STAGE_7_TABLE}` m1
    JOIN `{STAGE_7_TABLE}` m2
        ON m1.session_id = m2.session_id
        AND m2.message_index = m1.message_index + 1
    ORDER BY m1.session_id, m1.message_index
    """

    for row in bq_client.query(query).result():
        # Determine relationship type
        if row.source_role == "user" and row.target_role == "assistant":
            rel_type = REL_RESPONDS_TO
        else:
            rel_type = REL_FOLLOWS

        yield {
            "relationship_id": generate_relationship_id(row.source_id, row.target_id, rel_type),
            "source_entity_id": row.source_id,
            "target_entity_id": row.target_id,
            "relationship_type": rel_type,
            "source_level": 5,
            "target_level": 5,
            "weight": 1.0,
            "metadata": json.dumps(
                {
                    "source_role": row.source_role,
                    "target_role": row.target_role,
                }
            ),
            "source_name": SOURCE_NAME,
            "source_pipeline": PIPELINE_NAME,
            "session_id": row.session_id,
            "content_date": row.content_date,
            "created_at": created_at,
            "run_id": run_id,
        }


def process_relationships(
    bq_client: bigquery.Client,
    run_id: str,
    batch_size: int,
    dry_run: bool,
) -> dict[str, int]:
    """Process all relationship types."""
    created_at = datetime.now(UTC).isoformat()

    if dry_run:
        return {
            "parent_child_relationships": 0,
            "sequential_relationships": 0,
            "total_relationships": 0,
            "dry_run": True,
        }

    total = 0
    batch = []

    # Parent-child relationships
    parent_child_count = 0
    for rel in build_parent_child_relationships(bq_client, run_id, created_at):
        batch.append(rel)
        parent_child_count += 1
        if len(batch) >= batch_size:
            errors = bq_client.insert_rows_json(STAGE_13_TABLE, batch)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            total += len(batch)
            batch = []

    # Sequential relationships
    sequential_count = 0
    for rel in build_sequential_relationships(bq_client, run_id, created_at):
        batch.append(rel)
        sequential_count += 1
        if len(batch) >= batch_size:
            errors = bq_client.insert_rows_json(STAGE_13_TABLE, batch)
            if errors:
                logger.error(f"Insert errors: {errors[:5]}")
            total += len(batch)
            batch = []

    # Insert remaining
    if batch:
        errors = bq_client.insert_rows_json(STAGE_13_TABLE, batch)
        if errors:
            logger.error(f"Insert errors: {errors[:5]}")
        total += len(batch)

    return {
        "parent_child_relationships": parent_child_count,
        "sequential_relationships": sequential_count,
        "total_relationships": total,
        "dry_run": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage 13: Relationship detection")
    parser.add_argument("--batch-size", type=int, default=5000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_id = get_current_run_id()

    with PipelineTracker(
        pipeline_name=PIPELINE_NAME, stage=13, stage_name="relationships", run_id=run_id
    ) as tracker:
        try:
            client = get_bigquery_client()
            bq_client = client.client if hasattr(client, "client") else client

            # Validate input tables
            validate_input_table_exists(bq_client, TABLE_STAGE_6)
            validate_input_table_exists(bq_client, TABLE_STAGE_7)
            validate_input_table_exists(bq_client, TABLE_STAGE_8)

            if not args.dry_run:
                create_stage_13_table(bq_client)

            stats = process_relationships(bq_client, run_id, args.batch_size, args.dry_run)
            tracker.update_progress(items_processed=stats["total_relationships"])

            print(f"\nSTAGE 13 COMPLETE: {stats['total_relationships']} relationships created")
            print(f"  Parent-child: {stats['parent_child_relationships']}")
            print(f"  Sequential: {stats['sequential_relationships']}")
            return 0

        except Exception as e:
            logger.error(f"Stage 13 failed: {e}", exc_info=True)
            require_diagnostic_on_error(e, "stage_13_relationships")
            return 1


if __name__ == "__main__":
    sys.exit(main())
