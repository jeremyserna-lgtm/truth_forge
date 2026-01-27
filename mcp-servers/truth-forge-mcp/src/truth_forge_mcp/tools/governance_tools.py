"""Governance Service MCP Tools.

Exposes GovernanceService capabilities via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (filters, queries)
- AGENT: GovernanceService.query_events()
- HOLD₂: Tool results (event history, statistics)
"""

from __future__ import annotations

import json
import logging
from typing import Any

from mcp.types import Tool

logger = logging.getLogger(__name__)


def get_governance_tools() -> list[tuple[Tool, Any]]:
    """Get all governance service tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Query events
    query_events_tool = Tool(
        name="query_events",
        description="Query event history with filters",
        inputSchema={
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "description": "Filter by event type (optional)",
                },
                "source": {
                    "type": "string",
                    "description": "Filter by source service (optional)",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum events to return",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 1000,
                },
            },
        },
    )

    def handle_query_events(arguments: dict[str, Any]) -> str:
        """Handle query_events tool.

        Args:
            arguments: Tool arguments containing filters.

        Returns:
            Markdown-formatted event list.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            governance_service = get_service("governance")
            event_type = arguments.get("event_type")
            source = arguments.get("source")
            limit = arguments.get("limit", 50)

            events = governance_service.query_events(
                event_type=event_type, source=source, limit=limit
            )

            lines = ["# Event History", ""]
            if event_type:
                lines.append(f"**Event Type**: {event_type}")
            if source:
                lines.append(f"**Source**: {source}")
            lines.append(f"**Limit**: {limit}\n")

            if not events:
                lines.append("No events found.")
            else:
                lines.append(f"Found {len(events)} event(s):\n")
                for i, event in enumerate(events, 1):
                    event_id = event.get("event_id", "unknown")
                    event_type_val = event.get("event_type", "unknown")
                    source_val = event.get("source", "unknown")
                    timestamp = event.get("governance_processed_at", "unknown")

                    lines.append(f"## Event {i}: {event_id}")
                    lines.append(f"- **Type**: {event_type_val}")
                    lines.append(f"- **Source**: {source_val}")
                    lines.append(f"- **Timestamp**: {timestamp}")
                    if event.get("metadata"):
                        lines.append(f"- **Metadata**: {json.dumps(event.get('metadata'), indent=2)}")
                    lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error("query_events_failed", error=str(e), exc_info=True)
            return f"Error querying events: {type(e).__name__}: {e!s}"

    tools.append((query_events_tool, handle_query_events))

    # Get recent events
    recent_events_tool = Tool(
        name="get_recent_events",
        description="Get recent activity summary",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent events",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 100,
                },
            },
        },
    )

    def handle_get_recent_events(arguments: dict[str, Any]) -> str:
        """Handle get_recent_events tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted recent events.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            governance_service = get_service("governance")
            limit = arguments.get("limit", 10)

            events = governance_service.query_events(limit=limit)

            lines = [f"# Recent Events (Last {limit})", ""]

            if not events:
                lines.append("No recent events.")
            else:
                for i, event in enumerate(events, 1):
                    event_type = event.get("event_type", "unknown")
                    source = event.get("source", "unknown")
                    timestamp = event.get("governance_processed_at", "unknown")

                    lines.append(
                        f"{i}. **{event_type}** from {source} at {timestamp}"
                    )

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_recent_events_failed", error=str(e), exc_info=True)
            return f"Error getting recent events: {type(e).__name__}: {e!s}"

    tools.append((recent_events_tool, handle_get_recent_events))

    # Get governance stats
    stats_tool = Tool(
        name="get_governance_stats",
        description="Get governance statistics",
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

    def handle_get_governance_stats(arguments: dict[str, Any]) -> str:
        """Handle get_governance_stats tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted statistics.
        """
        try:
            from truth_forge_mcp.tools._utils import setup_project_path

            setup_project_path()
            from truth_forge.services.factory import get_service

            governance_service = get_service("governance")
            detailed = arguments.get("detailed", False)

            summary = governance_service.get_summary()

            lines = ["# Governance Statistics", ""]
            lines.append(f"**Total Events**: {summary.get('total_events', 0)}")

            if detailed:
                by_source = summary.get("by_source", {})
                if by_source:
                    lines.append("\n## Events by Source")
                    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
                        lines.append(f"- {source}: {count}")

                by_type = summary.get("by_type", {})
                if by_type:
                    lines.append("\n## Events by Type")
                    for event_type, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
                        lines.append(f"- {event_type}: {count}")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_governance_stats_failed", error=str(e), exc_info=True)
            return f"Error getting governance stats: {type(e).__name__}: {e!s}"

    tools.append((stats_tool, handle_get_governance_stats))

    return tools
