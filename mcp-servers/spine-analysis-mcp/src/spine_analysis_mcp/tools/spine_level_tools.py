"""Spine Level Tools - L1-L12 hierarchical analysis."""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_TABLE, SPINE_LEVELS, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all spine level analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    analyze_spine_level_tool = Tool(
        name="analyze_spine_level",
        description="Analyze entities at a specific spine level (1-12)",
        inputSchema={
            "type": "object",
            "properties": {
                "level": {
                    "type": "integer",
                    "description": "Spine level (1-12)",
                    "minimum": 1,
                    "maximum": 12,
                },
                "include_statistics": {"type": "boolean", "default": True},
            },
        },
    )

    def handle_analyze_spine_level(arguments: dict[str, Any]) -> str:
        """Handle analyze_spine_level tool."""
        try:
            client = get_bigquery_client()
            level = arguments.get("level")

            if not level or level < 1 or level > 12:
                return "Error: 'level' must be between 1 and 12"

            level_name = SPINE_LEVELS.get(level, f"Level {level}")

            query = f"""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT source_platform) as source_count,
                COUNT(DISTINCT entity_type) as domain_count
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE level = {level}
            """

            query_job = client.query(query)
            result = list(query_job.result())[0]

            lines = [f"# Spine Level Analysis: L{level} ({level_name})", ""]
            lines.append(f"- **Total Entities**: {result.total:,}")
            lines.append(f"- **Unique Sources**: {result.source_count}")
            lines.append(f"- **Unique Domains**: {result.domain_count}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_spine_level failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((analyze_spine_level_tool, handle_analyze_spine_level))

    return tools
