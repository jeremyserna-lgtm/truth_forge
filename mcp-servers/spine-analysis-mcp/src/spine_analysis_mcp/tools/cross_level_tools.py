"""Cross-Level Tools - Analyze relationships across spine levels (L1-L12).

THE PATTERN:
- HOLD₁: Level pairs, traversal direction
- AGENT: Cross-level aggregation queries
- HOLD₂: Cross-level analysis results
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_TABLE, RELATIONSHIP_TABLE, SPINE_LEVELS, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all cross-level analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    # Analyze cross-level distribution
    analyze_cross_level_distribution_tool = Tool(
        name="analyze_cross_level_distribution",
        description="Analyze how entities distribute across spine levels",
        inputSchema={
            "type": "object",
            "properties": {
                "group_by": {
                    "type": "string",
                    "description": "source_system, domain, entity_type",
                },
            },
        },
    )

    def handle_analyze_cross_level_distribution(arguments: dict[str, Any]) -> str:
        """Handle analyze_cross_level_distribution tool."""
        try:
            client = get_bigquery_client()
            group_by = arguments.get("group_by")

            group_by_clause = ""
            if group_by:
                group_by_clause = f", {group_by}"

            query = f"""
            SELECT 
                level,
                COUNT(*) as count
                {group_by_clause}
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity`
            GROUP BY level {group_by_clause}
            ORDER BY level
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Cross-Level Distribution", ""]
            if group_by:
                lines.append(f"**Group By**: {group_by}")
            lines.append("")

            # Group by the group_by field if present
            if group_by:
                by_group: dict[str, list[Any]] = {}
                for row in results:
                    group_value = getattr(row, group_by, "unknown")
                    if group_value not in by_group:
                        by_group[group_value] = []
                    by_group[group_value].append(row)

                for group_value in sorted(by_group.keys()):
                    lines.append(f"## {group_by}: {group_value}")
                    for row in by_group[group_value]:
                        level_name = SPINE_LEVELS.get(row.level, f"Level {row.level}")
                        lines.append(f"- **L{row.level}** ({level_name}): {row.count:,}")
                    lines.append("")
            else:
                total = sum(row.count for row in results)
                for row in results:
                    level_name = SPINE_LEVELS.get(row.level, f"Level {row.level}")
                    percentage = (row.count / total * 100) if total > 0 else 0
                    lines.append(f"- **L{row.level}** ({level_name}): {row.count:,} ({percentage:.1f}%)")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_cross_level_distribution failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((analyze_cross_level_distribution_tool, handle_analyze_cross_level_distribution))

    # Find level relationships
    find_level_relationships_tool = Tool(
        name="find_level_relationships",
        description="Find how entities at different levels relate to each other",
        inputSchema={
            "type": "object",
            "properties": {
                "source_level": {
                    "type": "integer",
                    "description": "Source spine level (1-12)",
                    "minimum": 1,
                    "maximum": 12,
                },
                "target_level": {
                    "type": "integer",
                    "description": "Target spine level (1-12)",
                    "minimum": 1,
                    "maximum": 12,
                },
            },
        },
    )

    def handle_find_level_relationships(arguments: dict[str, Any]) -> str:
        """Handle find_level_relationships tool."""
        try:
            client = get_bigquery_client()
            source_level = arguments.get("source_level")
            target_level = arguments.get("target_level")

            if not source_level or not target_level:
                return "Error: Both 'source_level' and 'target_level' are required"

            # Find relationships between entities at these levels
            query = f"""
            SELECT 
                r.relationship_type,
                COUNT(*) as frequency,
                COUNT(DISTINCT r.source_entity_id) as source_count,
                COUNT(DISTINCT r.target_entity_id) as target_count
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{RELATIONSHIP_TABLE}` r
            JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e1
                ON r.source_entity_id = e1.entity_id
            JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e2
                ON r.target_entity_id = e2.entity_id
            WHERE e1.level = {source_level}
              AND e2.level = {target_level}
            GROUP BY r.relationship_type
            ORDER BY frequency DESC
            LIMIT 20
            """

            query_job = client.query(query)
            results = list(query_job.result())

            source_name = SPINE_LEVELS.get(source_level, f"Level {source_level}")
            target_name = SPINE_LEVELS.get(target_level, f"Level {target_level}")

            lines = [f"# Level Relationships: L{source_level} → L{target_level}", ""]
            lines.append(f"**From**: L{source_level} ({source_name})")
            lines.append(f"**To**: L{target_level} ({target_name})")
            lines.append(f"**Found**: {len(results)} relationship types\n")

            for i, row in enumerate(results, 1):
                lines.append(f"## {row.relationship_type}")
                lines.append(f"- **Frequency**: {row.frequency:,}")
                lines.append(f"- **Unique Sources**: {row.source_count:,}")
                lines.append(f"- **Unique Targets**: {row.target_count:,}")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_level_relationships failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_level_relationships_tool, handle_find_level_relationships))

    return tools
