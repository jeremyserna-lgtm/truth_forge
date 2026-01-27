"""BigQuery/Entity Query MCP Tools.

Exposes BigQuery entity data access via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (query_type, filters, limits)
- AGENT: BigQuery client queries
- HOLD₂: Tool results (entity data, enrichments, embeddings)
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

logger = logging.getLogger(__name__)

# BigQuery project and dataset configuration
BQ_PROJECT_ID = "flash-clover-464719-g1"
BQ_DATASET_ID = "spine"


def get_bigquery_tools() -> list[tuple[Tool, Any]]:
    """Get all BigQuery/entity query tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Query entities (unified + enrichments + embeddings)
    query_entities_tool = Tool(
        name="query_entities",
        description="Query unified entity data with enrichments and embeddings",
        inputSchema={
            "type": "object",
            "properties": {
                "query_type": {
                    "type": "string",
                    "description": "Query type: 'joined', 'unified', 'enrichments', or 'embeddings'",
                    "enum": ["joined", "unified", "enrichments", "embeddings"],
                    "default": "joined",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum entities to return",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 1000,
                },
                "filters": {
                    "type": "object",
                    "description": "Filters to apply (e.g., source_system, spine_level)",
                    "properties": {
                        "source_system": {"type": "string"},
                        "spine_level": {"type": "integer"},
                    },
                },
            },
        },
    )

    def handle_query_entities(arguments: dict[str, Any]) -> str:
        """Handle query_entities tool.

        Args:
            arguments: Tool arguments containing query_type, filters, and limit.

        Returns:
            Markdown-formatted entity data.
        """
        try:
            from google.cloud import bigquery

            query_type = arguments.get("query_type", "joined")
            limit = arguments.get("limit", 50)
            filters = arguments.get("filters", {})

            client = bigquery.Client(project=BQ_PROJECT_ID)

            # Build query based on type
            if query_type == "joined":
                # Left join of unified + enrichments + embeddings
                query = f"""
                SELECT 
                    e.*,
                    enr.keybert_top_keyword,
                    enr.bertopic_topic_id,
                    enr.goemotions_primary_emotion,
                    enr.roberta_hate_score,
                    emb.enrichment_embedding,
                    emb.core_embedding
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity` e
                LEFT JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.L4_sentences_enriched` enr
                    ON e.entity_id = enr.entity_id
                LEFT JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity_embeddings` emb
                    ON e.entity_id = emb.entity_id
                WHERE 1=1
                """
            elif query_type == "unified":
                query = f"SELECT * FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity` WHERE 1=1"
            elif query_type == "enrichments":
                query = f"SELECT * FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.L4_sentences_enriched` WHERE 1=1"
            elif query_type == "embeddings":
                query = f"SELECT * FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity_embeddings` WHERE 1=1"
            else:
                return f"Error: Unknown query_type: {query_type}"

            # Add filters
            if filters.get("source_system"):
                query += f" AND source_system = '{filters['source_system']}'"
            if filters.get("spine_level") is not None:
                query += f" AND spine_level = {filters['spine_level']}"

            query += f" LIMIT {limit}"

            # Execute query
            query_job = client.query(query)
            results = query_job.result()

            lines = [f"# Entity Query: {query_type}", ""]
            lines.append(f"**Limit**: {limit}")
            if filters:
                lines.append(f"**Filters**: {filters}")
            lines.append("")

            rows = list(results)
            if not rows:
                lines.append("No entities found.")
            else:
                lines.append(f"Found {len(rows)} entity(ies):\n")
                for i, row in enumerate(rows[:10], 1):  # Show first 10
                    row_dict = dict(row)
                    entity_id = row_dict.get("entity_id", "unknown")
                    text = str(row_dict.get("text", ""))[:100]
                    lines.append(f"## Entity {i}: {entity_id}")
                    lines.append(f"**Text**: {text}...")
                    if query_type == "joined":
                        if row_dict.get("keybert_top_keyword"):
                            lines.append(f"**Keyword**: {row_dict['keybert_top_keyword']}")
                        if row_dict.get("goemotions_primary_emotion"):
                            lines.append(f"**Emotion**: {row_dict['goemotions_primary_emotion']}")
                    lines.append("")

                if len(rows) > 10:
                    lines.append(f"\n... and {len(rows) - 10} more entities")

            return "\n".join(lines)

        except Exception as e:
            logger.error("query_entities_failed", error=str(e), exc_info=True)
            return f"Error querying entities: {type(e).__name__}: {e!s}"

    tools.append((query_entities_tool, handle_query_entities))

    # Query enrichments
    query_enrichments_tool = Tool(
        name="query_enrichments",
        description="Query NLP enrichments (sentiment, topics, keywords)",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum enrichments to return",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 1000,
                },
                "emotion": {
                    "type": "string",
                    "description": "Filter by emotion (optional)",
                },
            },
        },
    )

    def handle_query_enrichments(arguments: dict[str, Any]) -> str:
        """Handle query_enrichments tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted enrichments.
        """
        try:
            from google.cloud import bigquery

            limit = arguments.get("limit", 50)
            emotion = arguments.get("emotion")

            client = bigquery.Client(project=BQ_PROJECT_ID)

            query = f"""
            SELECT 
                entity_id,
                keybert_top_keyword,
                bertopic_topic_id,
                goemotions_primary_emotion,
                roberta_hate_score
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.L4_sentences_enriched`
            WHERE 1=1
            """
            if emotion:
                query += f" AND goemotions_primary_emotion = '{emotion}'"
            query += f" LIMIT {limit}"

            query_job = client.query(query)
            results = query_job.result()

            lines = ["# NLP Enrichments", ""]
            if emotion:
                lines.append(f"**Filter**: Emotion = {emotion}")
            lines.append(f"**Limit**: {limit}\n")

            rows = list(results)
            if not rows:
                lines.append("No enrichments found.")
            else:
                lines.append(f"Found {len(rows)} enrichment(s):\n")
                for i, row in enumerate(rows[:10], 1):
                    row_dict = dict(row)
                    lines.append(f"## Enrichment {i}")
                    lines.append(f"**Entity ID**: {row_dict.get('entity_id', 'unknown')}")
                    if row_dict.get("keybert_top_keyword"):
                        lines.append(f"**Keyword**: {row_dict['keybert_top_keyword']}")
                    if row_dict.get("goemotions_primary_emotion"):
                        lines.append(f"**Emotion**: {row_dict['goemotions_primary_emotion']}")
                    if row_dict.get("bertopic_topic_id") is not None:
                        lines.append(f"**Topic ID**: {row_dict['bertopic_topic_id']}")
                    lines.append("")

                if len(rows) > 10:
                    lines.append(f"\n... and {len(rows) - 10} more enrichments")

            return "\n".join(lines)

        except Exception as e:
            logger.error("query_enrichments_failed", error=str(e), exc_info=True)
            return f"Error querying enrichments: {type(e).__name__}: {e!s}"

    tools.append((query_enrichments_tool, handle_query_enrichments))

    return tools
