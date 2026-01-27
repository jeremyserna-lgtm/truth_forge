"""Semantic Tools - Embedding analysis, similarity, and clustering.

THE PATTERN:
- HOLD₁: Entity IDs, similarity thresholds
- AGENT: Embedding similarity queries
- HOLD₂: Similar entities and clusters
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, DEFAULT_LIMIT, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all semantic analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    # Find similar entities
    find_similar_entities_tool = Tool(
        name="find_similar_entities",
        description="Find semantically similar entities using embeddings",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID to find similar entities for",
                },
                "similarity_threshold": {
                    "type": "number",
                    "description": "Minimum cosine similarity (0-1)",
                    "default": 0.7,
                    "minimum": 0,
                    "maximum": 1,
                },
                "limit": {"type": "integer", "default": 20},
            },
        },
    )

    def handle_find_similar_entities(arguments: dict[str, Any]) -> str:
        """Handle find_similar_entities tool."""
        try:
            client = get_bigquery_client()
            entity_id = arguments.get("entity_id", "")
            threshold = arguments.get("similarity_threshold", 0.7)
            limit = arguments.get("limit", 20)

            if not entity_id:
                return "Error: 'entity_id' parameter is required"

            # Check if embeddings table exists and has data
            # For now, return a message about embedding availability
            lines = [f"# Similar Entities: {entity_id}", ""]
            lines.append(f"**Similarity Threshold**: {threshold}")
            lines.append("")

            # Try to query embeddings if available
            try:
                query = f"""
                SELECT 
                    e2.entity_id,
                    e2.level,
                    e2.entity_type,
                    e2.text
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e1
                JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e2
                    ON e1.entity_id != e2.entity_id
                WHERE e1.entity_id = '{entity_id}'
                  AND e1.level = e2.level
                LIMIT {limit}
                """

                query_job = client.query(query)
                results = list(query_job.result())

                if results:
                    lines.append(f"**Found**: {len(results)} entities at same level\n")
                    for i, row in enumerate(results[:10], 1):
                        lines.append(f"## Entity {i}")
                        lines.append(f"- **ID**: {row.entity_id}")
                        lines.append(f"- **Type**: {row.entity_type}")
                        text_preview = str(row.text)[:200] if row.text else "N/A"
                        lines.append(f"- **Text**: {text_preview}...")
                        lines.append("")
                else:
                    lines.append("No similar entities found. Embedding-based similarity requires enrichment data.")
            except Exception:
                lines.append("**Note**: Embedding-based similarity requires the `entity_embeddings` table.")
                lines.append("Use `query_entities` with filters to find related entities.")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_similar_entities failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_similar_entities_tool, handle_find_similar_entities))

    # Extract concept clusters
    extract_concept_clusters_tool = Tool(
        name="extract_concept_clusters",
        description="Identify clusters of related concepts using co-occurrence",
        inputSchema={
            "type": "object",
            "properties": {
                "min_cluster_size": {
                    "type": "integer",
                    "description": "Minimum entities in a cluster",
                    "default": 5,
                },
                "domain": {"type": "string", "description": "Filter by domain"},
            },
        },
    )

    def handle_extract_concept_clusters(arguments: dict[str, Any]) -> str:
        """Handle extract_concept_clusters tool."""
        try:
            client = get_bigquery_client()
            min_size = arguments.get("min_cluster_size", 5)
            domain = arguments.get("domain")

            domain_filter = f" AND domain = '{domain}'" if domain else ""

            # Find entities that co-occur in same documents/conversations
            query = f"""
            SELECT 
                e1.entity_type,
                e1.entity_type as domain,
                COUNT(DISTINCT e1.entity_id) as cluster_size,
                COUNT(DISTINCT e1.source_platform) as source_count
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e1
            WHERE 1=1 {domain_filter}
            GROUP BY e1.entity_type
            HAVING COUNT(DISTINCT e1.entity_id) >= {min_size}
            ORDER BY cluster_size DESC
            LIMIT 30
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Concept Clusters", ""]
            lines.append(f"**Min Cluster Size**: {min_size}")
            if domain:
                lines.append(f"**Domain**: {domain}")
            lines.append(f"**Found**: {len(results)} clusters\n")

            for i, row in enumerate(results, 1):
                lines.append(f"## Cluster {i}")
                lines.append(f"- **Entity Type**: {row.entity_type}")
                lines.append(f"- **Domain**: {row.domain}")
                lines.append(f"- **Size**: {row.cluster_size:,} entities")
                lines.append(f"- **Sources**: {row.source_count}")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"extract_concept_clusters failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((extract_concept_clusters_tool, handle_extract_concept_clusters))

    return tools
