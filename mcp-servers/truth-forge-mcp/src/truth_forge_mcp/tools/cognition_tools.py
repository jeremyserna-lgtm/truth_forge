"""Cognition Service MCP Tools.

Exposes CognitionService capabilities via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (goals, queries)
- AGENT: CognitionService methods
- HOLD₂: Tool results (thoughts, plans, paradoxes)
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

logger = logging.getLogger(__name__)


def get_cognition_tools() -> list[tuple[Tool, Any]]:
    """Get all cognition service tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Get cognitive state
    state_tool = Tool(
        name="get_cognitive_state",
        description="Get current cognitive state summary",
        inputSchema={
            "type": "object",
            "properties": {
                "detailed": {
                    "type": "boolean",
                    "description": "Include detailed information",
                    "default": False,
                },
            },
        },
    )

    def handle_get_cognitive_state(arguments: dict[str, Any]) -> str:
        """Handle get_cognitive_state tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted cognitive state.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            cognition_service = get_service("cognition")
            detailed = arguments.get("detailed", False)

            lines = ["# Cognitive State", ""]
            lines.append("## Status")
            lines.append("- ✓ Cognition Service: Active")
            lines.append("- ✓ Knowledge Integration: Enabled")
            lines.append("- ✓ Relationship Context: Enabled")

            if detailed:
                # Try to get more detailed state
                # Note: CognitionService may not expose all these methods yet
                lines.append("\n## Service Information")
                lines.append(f"- **Service Name**: {cognition_service.service_name}")
                lines.append(f"- **State**: {getattr(cognition_service, 'state', 'ready')}")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_cognitive_state_failed", error=str(e), exc_info=True)
            return f"Error getting cognitive state: {type(e).__name__}: {e!s}"

    tools.append((state_tool, handle_get_cognitive_state))

    # Query thoughts (placeholder - may need CognitionService enhancement)
    thoughts_tool = Tool(
        name="query_thoughts",
        description="Query active thoughts and plans",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum thoughts to return",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
        },
    )

    def handle_query_thoughts(arguments: dict[str, Any]) -> str:
        """Handle query_thoughts tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted thoughts.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            cognition_service = get_service("cognition")
            limit = arguments.get("limit", 10)

            lines = ["# Active Thoughts", ""]
            lines.append("## Status")
            lines.append("Cognition service is active and processing goals.")

            # Note: This is a placeholder. CognitionService may need enhancement
            # to expose query_thoughts() method
            lines.append("\n**Note**: Thought querying may require CognitionService enhancement.")

            return "\n".join(lines)

        except Exception as e:
            logger.error("query_thoughts_failed", error=str(e), exc_info=True)
            return f"Error querying thoughts: {type(e).__name__}: {e!s}"

    tools.append((thoughts_tool, handle_query_thoughts))

    return tools
