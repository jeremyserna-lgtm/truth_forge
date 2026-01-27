"""Concept Tools - Deep concept exploration and mapping."""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, DEFAULT_LIMIT, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all concept exploration tools."""
    tools: list[tuple[Tool, Any]] = []

    explore_concept_tool = Tool(
        name="explore_concept",
        description="Deep dive into a specific concept, finding all mentions and context",
        inputSchema={
            "type": "object",
            "properties": {
                "concept": {
                    "type": "string",
                    "description": "Concept to explore (search term)",
                },
                "limit": {"type": "integer", "default": DEFAULT_LIMIT},
                "include_context": {
                    "type": "boolean",
                    "description": "Include surrounding context",
                    "default": True,
                },
            },
        },
    )

    def handle_explore_concept(arguments: dict[str, Any]) -> str:
        """Handle explore_concept tool."""
        try:
            client = get_bigquery_client()
            concept = arguments.get("concept", "")
            limit = arguments.get("limit", DEFAULT_LIMIT)

            if not concept:
                return "Error: 'concept' parameter is required"

            query = f"""
            SELECT 
                entity_id,
                level,
                entity_type,
                source_system,
                domain,
                text,
                created_at
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity`
            WHERE LOWER(text) LIKE LOWER('%{concept}%')
            ORDER BY created_at DESC
            LIMIT {limit}
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Concept Exploration: {concept}", ""]
            lines.append(f"**Found**: {len(results)} mentions\n")

            for i, row in enumerate(results[:20], 1):
                lines.append(f"## Mention {i}")
                lines.append(f"- **Entity ID**: {row.entity_id}")
                lines.append(f"- **Level**: L{row.level}")
                lines.append(f"- **Source**: {row.source_system}")
                lines.append(f"- **Created**: {row.created_at}")
                text_preview = str(row.text)[:300] if row.text else "N/A"
                lines.append(f"- **Text**: {text_preview}...")
                lines.append("")

            if len(results) > 20:
                lines.append(f"\n... and {len(results) - 20} more mentions")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"explore_concept failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((explore_concept_tool, handle_explore_concept))

    return tools
