"""Query Tools - Basic data access and exploration.

THE PATTERN:
- HOLD₁: Query parameters (filters, limits)
- AGENT: BigQuery queries
- HOLD₂: Query results (formatted data)
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import (
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    DEFAULT_LIMIT,
    ENTITY_TABLE,
    MAX_LIMIT,
    get_bigquery_client,
)

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all query tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Query entities
    query_entities_tool = Tool(
        name="query_entities",
        description="Query entities from the spine dataset with filters",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum entities to return",
                    "default": DEFAULT_LIMIT,
                    "minimum": 1,
                    "maximum": MAX_LIMIT,
                },
                "level": {
                    "type": "integer",
                    "description": "Spine level (1-12), optional",
                    "minimum": 1,
                    "maximum": 12,
                },
                "entity_type": {
                    "type": "string",
                    "description": "Filter by entity type",
                },
                "source_system": {
                    "type": "string",
                    "description": "Filter by source system (claude_code, claude_web, gemini_web, codex, cursor)",
                },
                "domain": {
                    "type": "string",
                    "description": "Filter by domain",
                },
            },
        },
    )

    def handle_query_entities(arguments: dict[str, Any]) -> str:
        """Handle query_entities tool."""
        try:
            client = get_bigquery_client()
            limit = min(arguments.get("limit", DEFAULT_LIMIT), MAX_LIMIT)

            query = f"""
            SELECT 
                entity_id,
                level,
                entity_type,
                source_platform as source_system,
                created_at,
                text
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE 1=1
            """

            if arguments.get("level"):
                query += f" AND level = {arguments['level']}"
            if arguments.get("entity_type"):
                query += f" AND entity_type = '{arguments['entity_type']}'"
            if arguments.get("source_system"):
                query += f" AND source_platform = '{arguments['source_system']}'"

            query += f" ORDER BY created_at DESC LIMIT {limit}"

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Entity Query Results", ""]
            lines.append(f"**Found**: {len(results)} entities\n")

            for i, row in enumerate(results[:20], 1):
                lines.append(f"## Entity {i}")
                lines.append(f"- **ID**: {row.entity_id}")
                lines.append(f"- **Level**: L{row.level}")
                lines.append(f"- **Type**: {row.entity_type}")
                lines.append(f"- **Source**: {row.source_system}")
                lines.append(f"- **Created**: {row.created_at}")
                text_preview = str(row.text)[:200] if row.text else "N/A"
                lines.append(f"- **Text**: {text_preview}...")
                lines.append("")

            if len(results) > 20:
                lines.append(f"\n... and {len(results) - 20} more entities")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"query_entities failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((query_entities_tool, handle_query_entities))

    # Query documents
    query_documents_tool = Tool(
        name="query_documents",
        description="Query document metadata and content",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "default": DEFAULT_LIMIT,
                    "minimum": 1,
                    "maximum": MAX_LIMIT,
                },
                "content_type": {"type": "string"},
                "domain": {"type": "string"},
                "include_content": {
                    "type": "boolean",
                    "description": "Include full document content",
                    "default": False,
                },
            },
        },
    )

    def handle_query_documents(arguments: dict[str, Any]) -> str:
        """Handle query_documents tool."""
        try:
            client = get_bigquery_client()
            limit = min(arguments.get("limit", DEFAULT_LIMIT), MAX_LIMIT)
            include_content = arguments.get("include_content", False)

            select_fields = "document_id, filename, filepath, content_type, domain, created_at, word_count"
            if include_content:
                select_fields += ", text"

            query = f"""
            SELECT {select_fields}
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.document`
            WHERE 1=1
            """

            if arguments.get("content_type"):
                query += f" AND content_type = '{arguments['content_type']}'"
            if arguments.get("domain"):
                query += f" AND domain = '{arguments['domain']}'"

            query += f" ORDER BY created_at DESC LIMIT {limit}"

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Document Query Results", ""]
            lines.append(f"**Found**: {len(results)} documents\n")

            for i, row in enumerate(results[:10], 1):
                lines.append(f"## Document {i}")
                lines.append(f"- **ID**: {row.document_id}")
                lines.append(f"- **Filename**: {row.filename}")
                lines.append(f"- **Type**: {row.content_type}")
                lines.append(f"- **Domain**: {row.domain}")
                lines.append(f"- **Words**: {row.word_count}")
                lines.append(f"- **Created**: {row.created_at}")
                if include_content and hasattr(row, "text"):
                    content_preview = str(row.text)[:500] if row.text else "N/A"
                    lines.append(f"- **Content**: {content_preview}...")
                lines.append("")

            if len(results) > 10:
                lines.append(f"\n... and {len(results) - 10} more documents")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"query_documents failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((query_documents_tool, handle_query_documents))

    # Get table statistics
    get_table_stats_tool = Tool(
        name="get_table_stats",
        description="Get statistics for spine dataset tables",
        inputSchema={
            "type": "object",
            "properties": {
                "table_name": {
                    "type": "string",
                    "description": "Table name (optional, defaults to 'entity')",
                },
            },
        },
    )

    def handle_get_table_stats(arguments: dict[str, Any]) -> str:
        """Handle get_table_stats tool."""
        try:
            client = get_bigquery_client()
            table_name = arguments.get("table_name", "entity")
            dataset_ref = client.dataset(BQ_DATASET_ID)
            table_ref = dataset_ref.table(table_name)

            try:
                table = client.get_table(table_ref)
                num_rows = table.num_rows
                num_bytes = table.num_bytes

                lines = [f"# Table Statistics: {table_name}", ""]
                lines.append(f"- **Rows**: {num_rows:,}")
                lines.append(f"- **Size**: {num_bytes / (1024 * 1024):.2f} MB")
                lines.append(f"- **Schema Fields**: {len(table.schema)}")
                lines.append("")

                # Get level distribution if entity table
                if table_name == ENTITY_TABLE or table_name == "entity":
                    query = f"""
                    SELECT level, COUNT(*) as count
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    GROUP BY level
                    ORDER BY level
                    """
                    query_job = client.query(query)
                    results = list(query_job.result())

                    lines.append("## Level Distribution")
                    for row in results:
                        lines.append(f"- **L{row.level}**: {row.count:,} entities")

                return "\n".join(lines)

            except Exception as e:
                return f"Error accessing table {table_name}: {e!s}"

        except Exception as e:
            logger.error(f"get_table_stats failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((get_table_stats_tool, handle_get_table_stats))

    return tools
