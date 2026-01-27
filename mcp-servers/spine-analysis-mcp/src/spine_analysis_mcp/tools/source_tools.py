"""Source Tools - Multi-source data tracking and correlation.

Tracks data from: Claude code/web, Gemini web, Codex, Cursor.

THE PATTERN:
- HOLD₁: Source filters and time ranges
- AGENT: BigQuery queries grouped by source
- HOLD₂: Source analysis results
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import (
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    DATA_SOURCES,
    DEFAULT_LIMIT,
    ENTITY_TABLE,
    get_bigquery_client,
)

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all source tracking tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Track source data
    track_source_data_tool = Tool(
        name="track_source_data",
        description="Track data volume and patterns by source (claude_code, claude_web, gemini_web, codex, cursor)",
        inputSchema={
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of sources to track (optional, defaults to all)",
                },
                "time_range": {
                    "type": "string",
                    "description": "Time range: 'last_7_days', 'last_30_days', 'last_90_days', or 'all'",
                    "default": "last_30_days",
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Metrics to include: 'volume', 'entities', 'domains', 'levels'",
                    "default": ["volume", "entities"],
                },
            },
        },
    )

    def handle_track_source_data(arguments: dict[str, Any]) -> str:
        """Handle track_source_data tool."""
        try:
            client = get_bigquery_client()
            sources = arguments.get("sources", list(DATA_SOURCES.keys()))
            time_range = arguments.get("time_range", "last_30_days")
            metrics = arguments.get("metrics", ["volume", "entities"])

            # Calculate time filter
            time_filter = ""
            if time_range != "all":
                days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
                days = days_map.get(time_range, 30)
                cutoff_date = datetime.now() - timedelta(days=days)
                time_filter = f" AND created_at >= '{cutoff_date.isoformat()}'"

            lines = ["# Source Data Tracking", ""]
            lines.append(f"**Time Range**: {time_range}")
            lines.append(f"**Sources**: {', '.join(sources)}")
            lines.append("")

            # Query each source
            for source in sources:
                if source not in DATA_SOURCES:
                    continue

                lines.append(f"## {source.upper()}")
                lines.append(f"*{DATA_SOURCES[source]}*")
                lines.append("")

                # Volume metric
                if "volume" in metrics:
                    query = f"""
                    SELECT COUNT(*) as count
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE source_platform = '{source}' {time_filter}
                    """
                    query_job = client.query(query)
                    result = list(query_job.result())[0]
                    lines.append(f"- **Total Entities**: {result.count:,}")

                # Entities by level
                if "entities" in metrics:
                    query = f"""
                    SELECT level, COUNT(*) as count
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE source_platform = '{source}' {time_filter}
                    GROUP BY level
                    ORDER BY level
                    """
                    query_job = client.query(query)
                    results = list(query_job.result())

                    if results:
                        lines.append("- **By Level**:")
                        for row in results:
                            lines.append(f"  - L{row.level}: {row.count:,}")

                # Domains (using entity_type as proxy)
                if "domains" in metrics:
                    query = f"""
                    SELECT entity_type as domain, COUNT(*) as count
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE source_platform = '{source}' {time_filter}
                      AND entity_type IS NOT NULL
                    GROUP BY entity_type
                    ORDER BY count DESC
                    LIMIT 10
                    """
                    query_job = client.query(query)
                    results = list(query_job.result())

                    if results:
                        lines.append("- **Top Domains**:")
                        for row in results:
                            lines.append(f"  - {row.domain}: {row.count:,}")

                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"track_source_data failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((track_source_data_tool, handle_track_source_data))

    # Compare sources
    compare_sources_tool = Tool(
        name="compare_sources",
        description="Compare patterns and metrics across different data sources",
        inputSchema={
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sources to compare (defaults to all)",
                },
                "metric": {
                    "type": "string",
                    "description": "Metric to compare: 'volume', 'level_distribution', 'domain_distribution'",
                    "default": "volume",
                },
                "time_range": {
                    "type": "string",
                    "default": "last_30_days",
                },
            },
        },
    )

    def handle_compare_sources(arguments: dict[str, Any]) -> str:
        """Handle compare_sources tool."""
        try:
            client = get_bigquery_client()
            sources = arguments.get("sources", list(DATA_SOURCES.keys()))
            metric = arguments.get("metric", "volume")
            time_range = arguments.get("time_range", "last_30_days")

            # Calculate time filter
            time_filter = ""
            if time_range != "all":
                days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
                days = days_map.get(time_range, 30)
                cutoff_date = datetime.now() - timedelta(days=days)
                time_filter = f" AND created_at >= '{cutoff_date.isoformat()}'"

            lines = ["# Source Comparison", ""]
            lines.append(f"**Metric**: {metric}")
            lines.append(f"**Time Range**: {time_range}")
            lines.append("")

            if metric == "volume":
                query = f"""
                SELECT source_platform as source_system, COUNT(*) as count
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE source_platform IN ({', '.join([f"'{s}'" for s in sources])}) {time_filter}
                GROUP BY source_platform
                ORDER BY count DESC
                """
                query_job = client.query(query)
                results = list(query_job.result())

                lines.append("## Volume Comparison")
                total = sum(row.count for row in results)
                for row in results:
                    percentage = (row.count / total * 100) if total > 0 else 0
                    lines.append(f"- **{row.source_system}**: {row.count:,} ({percentage:.1f}%)")

            elif metric == "level_distribution":
                lines.append("## Level Distribution by Source")
                for source in sources:
                    query = f"""
                    SELECT level, COUNT(*) as count
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE source_platform = '{source}' {time_filter}
                    GROUP BY level
                    ORDER BY level
                    """
                    query_job = client.query(query)
                    results = list(query_job.result())

                    lines.append(f"\n### {source.upper()}")
                    for row in results:
                        lines.append(f"- L{row.level}: {row.count:,}")

            elif metric == "domain_distribution":
                lines.append("## Top Domains by Source")
                for source in sources:
                    query = f"""
                    SELECT domain, COUNT(*) as count
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity`
                    WHERE source_system = '{source}' {time_filter}
                      AND domain IS NOT NULL
                    GROUP BY domain
                    ORDER BY count DESC
                    LIMIT 5
                    """
                    query_job = client.query(query)
                    results = list(query_job.result())

                    lines.append(f"\n### {source.upper()}")
                    for row in results:
                        lines.append(f"- {row.domain}: {row.count:,}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"compare_sources failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((compare_sources_tool, handle_compare_sources))

    # Find cross-source connections
    find_cross_source_connections_tool = Tool(
        name="find_cross_source_connections",
        description="Find entities or concepts that appear across multiple sources",
        inputSchema={
            "type": "object",
            "properties": {
                "min_sources": {
                    "type": "integer",
                    "description": "Minimum number of sources an entity must appear in",
                    "default": 2,
                    "minimum": 2,
                },
                "domain": {
                    "type": "string",
                    "description": "Filter by domain (optional)",
                },
            },
        },
    )

    def handle_find_cross_source_connections(arguments: dict[str, Any]) -> str:
        """Handle find_cross_source_connections tool."""
        try:
            client = get_bigquery_client()
            min_sources = arguments.get("min_sources", 2)
            domain_filter = f" AND domain = '{arguments['domain']}'" if arguments.get("domain") else ""

            # Find entities that appear in multiple sources
            query = f"""
            SELECT 
                entity_id,
                COUNT(DISTINCT source_platform) as source_count,
                STRING_AGG(DISTINCT source_platform, ', ') as sources,
                MAX(created_at) as last_seen
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            WHERE 1=1 {domain_filter}
            GROUP BY entity_id
            HAVING COUNT(DISTINCT source_platform) >= {min_sources}
            ORDER BY source_count DESC, last_seen DESC
            LIMIT 50
            """
            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Cross-Source Connections", ""]
            lines.append(f"**Found**: {len(results)} entities appearing in {min_sources}+ sources")
            lines.append("")

            for i, row in enumerate(results[:20], 1):
                lines.append(f"## Connection {i}")
                lines.append(f"- **Entity ID**: {row.entity_id}")
                lines.append(f"- **Sources**: {row.sources} ({row.source_count} sources)")
                lines.append(f"- **Last Seen**: {row.last_seen}")
                lines.append("")

            if len(results) > 20:
                lines.append(f"\n... and {len(results) - 20} more connections")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_cross_source_connections failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_cross_source_connections_tool, handle_find_cross_source_connections))

    return tools
