"""Relationship Tools - Entity relationship analysis and network mapping.

THE PATTERN:
- HOLD₁: Entity IDs, relationship types, depth
- AGENT: Graph traversal queries
- HOLD₂: Relationship networks and paths
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, DEFAULT_LIMIT, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all relationship analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    # Find entity relationships
    find_entity_relationships_tool = Tool(
        name="find_entity_relationships",
        description="Find all relationships for a specific entity",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID to find relationships for",
                },
                "relationship_type": {
                    "type": "string",
                    "description": "Filter by relationship type (optional)",
                },
                "direction": {
                    "type": "string",
                    "description": "Direction: 'outgoing', 'incoming', 'both'",
                    "default": "both",
                },
                "limit": {"type": "integer", "default": DEFAULT_LIMIT},
            },
        },
    )

    def handle_find_entity_relationships(arguments: dict[str, Any]) -> str:
        """Handle find_entity_relationships tool."""
        try:
            client = get_bigquery_client()
            entity_id = arguments.get("entity_id", "")
            relationship_type = arguments.get("relationship_type")
            direction = arguments.get("direction", "both")
            limit = arguments.get("limit", DEFAULT_LIMIT)

            if not entity_id:
                return "Error: 'entity_id' parameter is required"

            # Build query based on direction
            if direction == "outgoing":
                where_clause = f"source_entity_id = '{entity_id}'"
            elif direction == "incoming":
                where_clause = f"target_entity_id = '{entity_id}'"
            else:  # both
                where_clause = f"(source_entity_id = '{entity_id}' OR target_entity_id = '{entity_id}')"

            if relationship_type:
                where_clause += f" AND relationship_type = '{relationship_type}'"

            query = f"""
            SELECT 
                relationship_id,
                source_entity_id,
                source_entity_type,
                target_entity_id,
                target_entity_type,
                relationship_type,
                strength,
                bidirectional,
                created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}`
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT {limit}
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Entity Relationships: {entity_id}", ""]
            lines.append(f"**Direction**: {direction}")
            lines.append(f"**Found**: {len(results)} relationships\n")

            for i, row in enumerate(results[:20], 1):
                lines.append(f"## Relationship {i}")
                if row.source_entity_id == entity_id:
                    lines.append(f"- **From**: {row.source_entity_id} ({row.source_entity_type})")
                    lines.append(f"- **To**: {row.target_entity_id} ({row.target_entity_type})")
                else:
                    lines.append(f"- **From**: {row.source_entity_id} ({row.source_entity_type})")
                    lines.append(f"- **To**: {row.target_entity_id} ({row.target_entity_type})")
                lines.append(f"- **Type**: {row.relationship_type}")
                if row.strength:
                    lines.append(f"- **Strength**: {row.strength:.2f}")
                lines.append(f"- **Bidirectional**: {row.bidirectional}")
                lines.append(f"- **Created**: {row.created_at}")
                lines.append("")

            if len(results) > 20:
                lines.append(f"\n... and {len(results) - 20} more relationships")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_entity_relationships failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_entity_relationships_tool, handle_find_entity_relationships))

    # Map relationship network
    map_relationship_network_tool = Tool(
        name="map_relationship_network",
        description="Map a network of relationships around an entity (multi-hop)",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {"type": "string", "description": "Central entity ID"},
                "max_hops": {
                    "type": "integer",
                    "description": "Maximum number of hops from center",
                    "default": 2,
                    "minimum": 1,
                    "maximum": 5,
                },
                "relationship_types": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by relationship types (optional)",
                },
            },
        },
    )

    def handle_map_relationship_network(arguments: dict[str, Any]) -> str:
        """Handle map_relationship_network tool."""
        try:
            client = get_bigquery_client()
            entity_id = arguments.get("entity_id", "")
            max_hops = min(arguments.get("max_hops", 2), 5)
            relationship_types = arguments.get("relationship_types", [])

            if not entity_id:
                return "Error: 'entity_id' parameter is required"

            # Build recursive CTE for multi-hop traversal
            type_filter = ""
            if relationship_types:
                type_list = ", ".join([f"'{t}'" for t in relationship_types])
                type_filter = f" AND relationship_type IN ({type_list})"

            # For now, do 2-hop query (can be extended)
            query = f"""
            WITH direct AS (
                SELECT 
                    source_entity_id as entity_id,
                    source_entity_type as entity_type,
                    relationship_type,
                    1 as hop
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}`
                WHERE target_entity_id = '{entity_id}' {type_filter}
                
                UNION ALL
                
                SELECT 
                    target_entity_id as entity_id,
                    target_entity_type as entity_type,
                    relationship_type,
                    1 as hop
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}`
                WHERE source_entity_id = '{entity_id}' {type_filter}
            ),
            second_hop AS (
                SELECT DISTINCT
                    CASE 
                        WHEN r.source_entity_id = d.entity_id THEN r.target_entity_id
                        ELSE r.source_entity_id
                    END as entity_id,
                    CASE 
                        WHEN r.source_entity_id = d.entity_id THEN r.target_entity_type
                        ELSE r.source_entity_type
                    END as entity_type,
                    r.relationship_type,
                    2 as hop
                FROM direct d
                JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}` r
                    ON (r.source_entity_id = d.entity_id OR r.target_entity_id = d.entity_id)
                WHERE d.entity_id != '{entity_id}' {type_filter}
            )
            SELECT * FROM direct
            UNION ALL
            SELECT * FROM second_hop
            ORDER BY hop, entity_type, entity_id
            LIMIT 200
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Relationship Network: {entity_id}", ""]
            lines.append(f"**Max Hops**: {max_hops}")
            lines.append(f"**Found**: {len(results)} connected entities\n")

            # Group by hop
            by_hop: dict[int, list[Any]] = {}
            for row in results:
                hop = row.hop
                if hop not in by_hop:
                    by_hop[hop] = []
                by_hop[hop].append(row)

            for hop in sorted(by_hop.keys()):
                lines.append(f"## Hop {hop} ({len(by_hop[hop])} entities)")
                for row in by_hop[hop][:20]:
                    lines.append(f"- **{row.entity_id}** ({row.entity_type}) - {row.relationship_type}")
                if len(by_hop[hop]) > 20:
                    lines.append(f"  ... and {len(by_hop[hop]) - 20} more")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"map_relationship_network failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((map_relationship_network_tool, handle_map_relationship_network))

    # Find relationship paths
    find_relationship_paths_tool = Tool(
        name="find_relationship_paths",
        description="Find paths between two entities",
        inputSchema={
            "type": "object",
            "properties": {
                "source_entity_id": {"type": "string"},
                "target_entity_id": {"type": "string"},
                "max_path_length": {
                    "type": "integer",
                    "default": 3,
                    "minimum": 1,
                    "maximum": 5,
                },
            },
        },
    )

    def handle_find_relationship_paths(arguments: dict[str, Any]) -> str:
        """Handle find_relationship_paths tool."""
        try:
            client = get_bigquery_client()
            source_id = arguments.get("source_entity_id", "")
            target_id = arguments.get("target_entity_id", "")
            max_length = min(arguments.get("max_path_length", 3), 5)

            if not source_id or not target_id:
                return "Error: Both 'source_entity_id' and 'target_entity_id' are required"

            # Find direct path
            query = f"""
            SELECT 
                source_entity_id,
                target_entity_id,
                relationship_type,
                1 as path_length
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}`
            WHERE (source_entity_id = '{source_id}' AND target_entity_id = '{target_id}')
               OR (source_entity_id = '{target_id}' AND target_entity_id = '{source_id}')
            LIMIT 10
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Relationship Paths", ""]
            lines.append(f"**From**: {source_id}")
            lines.append(f"**To**: {target_id}")
            lines.append(f"**Max Length**: {max_length}\n")

            if results:
                lines.append("## Direct Paths (Length 1)")
                for row in results:
                    lines.append(f"- **{row.source_entity_id}** → **{row.target_entity_id}** ({row.relationship_type})")
                lines.append("")
            else:
                lines.append("No direct path found. Use map_relationship_network to explore connections.")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_relationship_paths failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_relationship_paths_tool, handle_find_relationship_paths))

    # Analyze relationship patterns
    analyze_relationship_patterns_tool = Tool(
        name="analyze_relationship_patterns",
        description="Analyze common relationship patterns in the dataset",
        inputSchema={
            "type": "object",
            "properties": {
                "min_frequency": {
                    "type": "integer",
                    "description": "Minimum frequency to include",
                    "default": 10,
                },
            },
        },
    )

    def handle_analyze_relationship_patterns(arguments: dict[str, Any]) -> str:
        """Handle analyze_relationship_patterns tool."""
        try:
            client = get_bigquery_client()
            min_freq = arguments.get("min_frequency", 10)

            query = f"""
            SELECT 
                source_entity_type,
                target_entity_type,
                relationship_type,
                COUNT(*) as frequency,
                AVG(strength) as avg_strength
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}`
            GROUP BY source_entity_type, target_entity_type, relationship_type
            HAVING COUNT(*) >= {min_freq}
            ORDER BY frequency DESC
            LIMIT 50
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Relationship Patterns", ""]
            lines.append(f"**Min Frequency**: {min_freq}")
            lines.append(f"**Found**: {len(results)} patterns\n")

            for i, row in enumerate(results[:30], 1):
                lines.append(f"## Pattern {i}")
                lines.append(f"- **{row.source_entity_type}** → **{row.target_entity_type}**")
                lines.append(f"- **Type**: {row.relationship_type}")
                lines.append(f"- **Frequency**: {row.frequency:,}")
                if row.avg_strength:
                    lines.append(f"- **Avg Strength**: {row.avg_strength:.2f}")
                lines.append("")

            if len(results) > 30:
                lines.append(f"\n... and {len(results) - 30} more patterns")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_relationship_patterns failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((analyze_relationship_patterns_tool, handle_analyze_relationship_patterns))

    return tools
