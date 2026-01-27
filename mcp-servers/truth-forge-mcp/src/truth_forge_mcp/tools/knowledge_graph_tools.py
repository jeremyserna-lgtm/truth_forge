"""Knowledge Graph MCP Tools.

Exposes knowledge graph query capabilities via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (entity_id, relationship_type)
- AGENT: Knowledge graph queries
- HOLD₂: Tool results (nodes, edges, paths)
"""

from __future__ import annotations

import json
import logging
from typing import Any

import duckdb

from mcp.types import Tool

logger = logging.getLogger(__name__)


def get_knowledge_graph_tools() -> list[tuple[Tool, Any]]:
    """Get all knowledge graph tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Get entity relationships
    relationships_tool = Tool(
        name="get_entity_relationships",
        description="Get relationships for an entity",
        inputSchema={
            "type": "object",
            "properties": {
                "entity_id": {
                    "type": "string",
                    "description": "Entity ID",
                },
                "relationship_type": {
                    "type": "string",
                    "description": "Filter by relationship type (optional)",
                },
                "direction": {
                    "type": "string",
                    "description": "Direction: 'outgoing', 'incoming', or 'both'",
                    "enum": ["outgoing", "incoming", "both"],
                    "default": "both",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum relationships to return",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
            "required": ["entity_id"],
        },
    )

    def handle_get_entity_relationships(arguments: dict[str, Any]) -> str:
        """Handle get_entity_relationships tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted relationships.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.core.paths import get_duckdb_file

            entity_id = arguments["entity_id"]
            relationship_type = arguments.get("relationship_type")
            direction = arguments.get("direction", "both")
            limit = arguments.get("limit", 20)

            # Try to find knowledge graph database
            # Check common locations
            kg_db_paths = [
                get_duckdb_file("knowledge_graph"),
                get_duckdb_file("knowledge"),
            ]

            db_path = None
            for path in kg_db_paths:
                if path.exists():
                    db_path = path
                    break

            if not db_path:
                return "# Entity Relationships\n\nKnowledge graph database not found."

            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                # Try to query edges table
                # Knowledge graph may have different schemas
                query = """
                SELECT * FROM edges
                WHERE (subject_id = ? OR object_id = ?)
                """
                params: list[Any] = [entity_id, entity_id]

                if relationship_type:
                    query += " AND predicate = ?"
                    params.append(relationship_type)

                if direction == "outgoing":
                    query = "SELECT * FROM edges WHERE subject_id = ?"
                    params = [entity_id]
                    if relationship_type:
                        query += " AND predicate = ?"
                        params.append(relationship_type)
                elif direction == "incoming":
                    query = "SELECT * FROM edges WHERE object_id = ?"
                    params = [entity_id]
                    if relationship_type:
                        query += " AND predicate = ?"
                        params.append(relationship_type)

                query += f" LIMIT {limit}"

                try:
                    results = conn.execute(query, params).fetchall()
                except Exception as e:
                    logger.debug(
                        "Graph schema not recognized",
                        extra={"entity_id": entity_id, "error": str(e)},
                    )
                    return "# Entity Relationships\n\nGraph schema not recognized. Knowledge graph may use different structure."

                lines = [f"# Entity Relationships: {entity_id}", ""]
                lines.append(f"**Direction**: {direction}")
                if relationship_type:
                    lines.append(f"**Type**: {relationship_type}")
                lines.append("")

                if not results:
                    lines.append("No relationships found.")
                else:
                    lines.append(f"Found {len(results)} relationship(s):\n")
                    for i, row in enumerate(results, 1):
                        # Handle different possible schemas
                        if len(row) >= 3:
                            subject = row[0] if len(row) > 0 else "unknown"
                            predicate = row[1] if len(row) > 1 else "unknown"
                            obj = row[2] if len(row) > 2 else "unknown"

                            lines.append(f"## Relationship {i}")
                            lines.append(f"**Subject**: {subject}")
                            lines.append(f"**Predicate**: {predicate}")
                            lines.append(f"**Object**: {obj}")
                            lines.append("")

            finally:
                conn.close()

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_entity_relationships_failed", error=str(e), exc_info=True)
            return f"Error getting relationships: {type(e).__name__}: {e!s}"

    tools.append((relationships_tool, handle_get_entity_relationships))

    # Get graph stats
    graph_stats_tool = Tool(
        name="get_graph_stats",
        description="Get knowledge graph statistics",
        inputSchema={
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Include detailed breakdowns",
                    "default": False,
                },
            },
        },
    )

    def handle_get_graph_stats(arguments: dict[str, Any]) -> str:
        """Handle get_graph_stats tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted statistics.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.core.paths import get_duckdb_file

            db_path = get_duckdb_file("knowledge_graph")
            if not db_path.exists():
                db_path = get_duckdb_file("knowledge")
                if not db_path.exists():
                    return "# Graph Statistics\n\nKnowledge graph database not found."

            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                lines = ["# Knowledge Graph Statistics", ""]

                # Try to get node count
                try:
                    node_count = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
                    lines.append(f"**Nodes**: {node_count:,}")
                except Exception as e:
                    logger.debug("Could not get node count", extra={"error": str(e)})
                    lines.append("**Nodes**: Schema not recognized")

                # Try to get edge count
                try:
                    edge_count = conn.execute("SELECT COUNT(*) FROM edges").fetchone()[0]
                    lines.append(f"**Edges**: {edge_count:,}")
                except Exception as e:
                    logger.debug("Could not get edge count", extra={"error": str(e)})
                    lines.append("**Edges**: Schema not recognized")

                if arguments.get("detailed"):
                    # Try to get relationship type breakdown
                    try:
                        rel_types = conn.execute(
                            "SELECT predicate, COUNT(*) as count FROM edges GROUP BY predicate ORDER BY count DESC"
                        ).fetchall()
                        if rel_types:
                            lines.append("\n## Relationship Types")
                            for rel_type, count in rel_types[:10]:
                                lines.append(f"- {rel_type}: {count}")
                    except Exception as e:
                        logger.debug("Could not get relationship types", extra={"error": str(e)})

            finally:
                conn.close()

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_graph_stats_failed", error=str(e), exc_info=True)
            return f"Error getting graph stats: {type(e).__name__}: {e!s}"

    tools.append((graph_stats_tool, handle_get_graph_stats))

    return tools
