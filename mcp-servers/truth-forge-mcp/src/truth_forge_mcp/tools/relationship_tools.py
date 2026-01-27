"""Relationship Service MCP Tools.

Exposes RelationshipService capabilities via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (partner_id, interaction_type)
- AGENT: RelationshipService methods
- HOLD₂: Tool results (partnership data, trust levels)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.types import Tool

logger = logging.getLogger(__name__)


def get_relationship_tools() -> list[tuple[Tool, Any]]:
    """Get all relationship service tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Get partnership
    partnership_tool = Tool(
        name="get_partnership",
        description="Get relationship context for an entity/partner",
        inputSchema={
            "type": "object",
            "properties": {
                "partner_id": {
                    "type": "string",
                    "description": "Partner/entity ID",
                },
            },
            "required": ["partner_id"],
        },
    )

    def handle_get_partnership(arguments: dict[str, Any]) -> str:
        """Handle get_partnership tool.

        Args:
            arguments: Tool arguments containing partner_id.

        Returns:
            Markdown-formatted partnership details.
        """
        try:
            from truth_forge.services.factory import get_service

            relationship_service = get_service("relationship")
            partner_id = arguments["partner_id"]

            partnership = relationship_service.get_partnership(partner_id)

            lines = [f"# Partnership: {partner_id}", ""]

            if not partnership:
                lines.append("Partnership not found.")
            else:
                lines.append(f"**Trust Level**: {partnership.get('trust_level', 0.5):.2f}")
                lines.append(f"**Interaction Count**: {partnership.get('interaction_count', 0)}")
                lines.append(
                    f"**Last Interaction**: {partnership.get('last_interaction', 'Never')}"
                )

                if partnership.get("preferences"):
                    lines.append("\n## Preferences")
                    lines.append(f"```json\n{json.dumps(partnership['preferences'], indent=2)}\n```")

                history = partnership.get("history", [])
                if history:
                    lines.append(f"\n## Interaction History ({len(history)} entries)")
                    for i, interaction in enumerate(history[-10:], 1):  # Last 10
                        lines.append(
                            f"{i}. **{interaction.get('type', 'unknown')}** "
                            f"({interaction.get('timestamp', 'unknown')})"
                        )

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_partnership_failed", error=str(e), exc_info=True)
            return f"Error getting partnership: {type(e).__name__}: {e!s}"

    tools.append((partnership_tool, handle_get_partnership))

    # Get trust level
    trust_tool = Tool(
        name="get_trust_level",
        description="Get trust score for an entity",
        inputSchema={
            "type": "object",
            "properties": {
                "partner_id": {
                    "type": "string",
                    "description": "Partner/entity ID",
                },
            },
            "required": ["partner_id"],
        },
    )

    def handle_get_trust_level(arguments: dict[str, Any]) -> str:
        """Handle get_trust_level tool.

        Args:
            arguments: Tool arguments containing partner_id.

        Returns:
            Markdown-formatted trust level.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            relationship_service = get_service("relationship")
            partner_id = arguments["partner_id"]

            partnership = relationship_service.get_partnership(partner_id)

            lines = [f"# Trust Level: {partner_id}", ""]

            if not partnership:
                lines.append("**Trust Level**: 0.50 (default - no interactions)")
                lines.append("\nNo partnership record found. Using default trust level.")
            else:
                trust = partnership.get("trust_level", 0.5)
                lines.append(f"**Trust Level**: {trust:.2f}")

                # Interpret trust level
                if trust >= 0.8:
                    interpretation = "Very High Trust"
                elif trust >= 0.6:
                    interpretation = "High Trust"
                elif trust >= 0.4:
                    interpretation = "Moderate Trust"
                elif trust >= 0.2:
                    interpretation = "Low Trust"
                else:
                    interpretation = "Very Low Trust"

                lines.append(f"**Interpretation**: {interpretation}")
                lines.append(f"**Interactions**: {partnership.get('interaction_count', 0)}")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_trust_level_failed", error=str(e), exc_info=True)
            return f"Error getting trust level: {type(e).__name__}: {e!s}"

    tools.append((trust_tool, handle_get_trust_level))

    # List partnerships
    list_tool = Tool(
        name="list_partnerships",
        description="List all known partnerships",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum partnerships to return",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 100,
                },
                "min_trust": {
                    "type": "number",
                    "description": "Minimum trust level filter",
                    "minimum": 0.0,
                    "maximum": 1.0,
                },
            },
        },
    )

    def handle_list_partnerships(arguments: dict[str, Any]) -> str:
        """Handle list_partnerships tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted partnership list.
        """
        try:
            import duckdb

            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.core.paths import get_duckdb_file

            limit = arguments.get("limit", 20)
            min_trust = arguments.get("min_trust")

            db_path = get_duckdb_file("relationship")
            if not db_path.exists():
                return "# Partnerships\n\nNo partnerships database found."

            conn = duckdb.connect(str(db_path), read_only=True)
            try:
                query = "SELECT id, data FROM relationship_records"
                if min_trust is not None:
                    query += f" WHERE CAST(data->>'trust_level' AS FLOAT) >= {min_trust}"
                query += f" ORDER BY CAST(data->>'trust_level' AS FLOAT) DESC LIMIT {limit}"

                results = conn.execute(query).fetchall()

                lines = ["# Partnerships", ""]
                if not results:
                    lines.append("No partnerships found.")
                else:
                    lines.append(f"Found {len(results)} partnership(s):\n")
                    for partner_id, data_str in results:
                        data = json.loads(data_str) if isinstance(data_str, str) else data_str
                        trust = data.get("trust_level", 0.5)
                        count = data.get("interaction_count", 0)
                        lines.append(
                            f"- **{partner_id}**: Trust {trust:.2f}, {count} interactions"
                        )

                return "\n".join(lines)
            finally:
                conn.close()

        except Exception as e:
            logger.error("list_partnerships_failed", error=str(e), exc_info=True)
            return f"Error listing partnerships: {type(e).__name__}: {e!s}"

    tools.append((list_tool, handle_list_partnerships))

    return tools
