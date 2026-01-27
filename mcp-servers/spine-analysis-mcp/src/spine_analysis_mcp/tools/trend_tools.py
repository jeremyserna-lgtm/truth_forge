"""Trend Tools - Temporal and volume trend analysis."""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all trend analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    analyze_temporal_trends_tool = Tool(
        name="analyze_temporal_trends",
        description="Analyze trends over time (entity creation, activity, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "Metric to analyze: 'entity_creation', 'activity'",
                    "default": "entity_creation",
                },
                "time_range": {"type": "string", "default": "last_90_days"},
                "granularity": {
                    "type": "string",
                    "description": "Time granularity: 'daily', 'weekly', 'monthly'",
                    "default": "daily",
                },
                "group_by": {
                    "type": "string",
                    "description": "Group by: 'source_system', 'level', 'domain'",
                },
            },
        },
    )

    def handle_analyze_temporal_trends(arguments: dict[str, Any]) -> str:
        """Handle analyze_temporal_trends tool."""
        try:
            client = get_bigquery_client()
            metric = arguments.get("metric", "entity_creation")
            granularity = arguments.get("granularity", "daily")
            group_by = arguments.get("group_by")

            # Build date truncation
            date_trunc = {
                "daily": "DATE(created_at)",
                "weekly": "DATE_TRUNC(DATE(created_at), WEEK)",
                "monthly": "DATE_TRUNC(DATE(created_at), MONTH)",
            }.get(granularity, "DATE(created_at)")

            group_by_clause = ""
            if group_by:
                group_by_clause = f", {group_by}"

            group_by_select = ""
            if group_by == "source_system":
                group_by_select = ", source_platform as source_system"
            elif group_by:
                group_by_select = f", {group_by}"

            query = f"""
            SELECT 
                {date_trunc} as period,
                COUNT(*) as count
                {group_by_select}
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
            GROUP BY period {group_by_clause}
            ORDER BY period DESC
            LIMIT 100
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Temporal Trends Analysis", ""]
            lines.append(f"**Metric**: {metric}")
            lines.append(f"**Granularity**: {granularity}")
            if group_by:
                lines.append(f"**Group By**: {group_by}")
            lines.append("")

            for row in results[:30]:
                period = str(row.period)
                count = row.count
                group_value = getattr(row, group_by, "") if group_by else ""
                if group_value:
                    lines.append(f"- **{period}** ({group_value}): {count:,}")
                else:
                    lines.append(f"- **{period}**: {count:,}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_temporal_trends failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((analyze_temporal_trends_tool, handle_analyze_temporal_trends))

    return tools
