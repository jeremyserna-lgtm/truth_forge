"""Temporal Tools - Time-based analysis, cycles, and evolution patterns.

THE PATTERN:
- HOLD₁: Time ranges, granularity, metrics
- AGENT: Temporal aggregation queries
- HOLD₂: Time series and pattern results
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all temporal analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    # Analyze temporal patterns
    analyze_temporal_patterns_tool = Tool(
        name="analyze_temporal_patterns",
        description="Analyze patterns in time (daily cycles, weekly patterns, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range": {"type": "string", "default": "last_90_days"},
                "granularity": {
                    "type": "string",
                    "description": "daily, weekly, monthly, hourly",
                    "default": "daily",
                },
                "metric": {
                    "type": "string",
                    "description": "entity_creation, activity, relationships",
                    "default": "entity_creation",
                },
                "group_by": {
                    "type": "string",
                    "description": "source_system, level, domain",
                },
            },
        },
    )

    def handle_analyze_temporal_patterns(arguments: dict[str, Any]) -> str:
        """Handle analyze_temporal_patterns tool."""
        try:
            client = get_bigquery_client()
            time_range = arguments.get("time_range", "last_90_days")
            granularity = arguments.get("granularity", "daily")
            metric = arguments.get("metric", "entity_creation")
            group_by = arguments.get("group_by")

            # Calculate time filter
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90, "last_365_days": 365}
            days = days_map.get(time_range, 90)
            cutoff_date = datetime.now() - timedelta(days=days)

            # Build date truncation
            date_trunc_map = {
                "hourly": "DATETIME_TRUNC(DATETIME(created_at), HOUR)",
                "daily": "DATE(created_at)",
                "weekly": "DATE_TRUNC(DATE(created_at), WEEK)",
                "monthly": "DATE_TRUNC(DATE(created_at), MONTH)",
            }
            date_trunc = date_trunc_map.get(granularity, "DATE(created_at)")

            group_by_clause = ""
            if group_by:
                group_by_clause = f", {group_by}"

            query = f"""
            SELECT 
                {date_trunc} as period,
                COUNT(*) as count
                {group_by_clause}
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity`
            WHERE created_at >= '{cutoff_date.isoformat()}'
            GROUP BY period {group_by_clause}
            ORDER BY period DESC
            LIMIT 200
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Temporal Patterns Analysis", ""]
            lines.append(f"**Time Range**: {time_range}")
            lines.append(f"**Granularity**: {granularity}")
            lines.append(f"**Metric**: {metric}")
            if group_by:
                lines.append(f"**Group By**: {group_by}")
            lines.append("")

            # Calculate statistics
            if results:
                counts = [row.count for row in results]
                avg_count = sum(counts) / len(counts) if counts else 0
                max_count = max(counts) if counts else 0
                min_count = min(counts) if counts else 0

                lines.append("## Statistics")
                lines.append(f"- **Average**: {avg_count:.1f}")
                lines.append(f"- **Maximum**: {max_count:,}")
                lines.append(f"- **Minimum**: {min_count:,}")
                lines.append("")

            lines.append("## Timeline")
            for row in results[:50]:
                period = str(row.period)
                count = row.count
                group_value = getattr(row, group_by, "") if group_by else ""
                if group_value:
                    lines.append(f"- **{period}** ({group_value}): {count:,}")
                else:
                    lines.append(f"- **{period}**: {count:,}")

            if len(results) > 50:
                lines.append(f"\n... and {len(results) - 50} more periods")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_temporal_patterns failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((analyze_temporal_patterns_tool, handle_analyze_temporal_patterns))

    # Find temporal clusters
    find_temporal_clusters_tool = Tool(
        name="find_temporal_clusters",
        description="Find clusters of activity in time (bursts, quiet periods)",
        inputSchema={
            "type": "object",
            "properties": {
                "time_range": {"type": "string", "default": "last_90_days"},
                "threshold_multiplier": {
                    "type": "number",
                    "description": "Threshold for cluster detection (e.g., 2.0 = 2x average)",
                    "default": 2.0,
                },
            },
        },
    )

    def handle_find_temporal_clusters(arguments: dict[str, Any]) -> str:
        """Handle find_temporal_clusters tool."""
        try:
            client = get_bigquery_client()
            time_range = arguments.get("time_range", "last_90_days")
            threshold = arguments.get("threshold_multiplier", 2.0)

            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days = days_map.get(time_range, 90)
            cutoff_date = datetime.now() - timedelta(days=days)

            query = f"""
            WITH daily_counts AS (
                SELECT 
                    DATE(created_at) as day,
                    COUNT(*) as count
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE created_at >= '{cutoff_date.isoformat()}'
                GROUP BY day
            ),
            stats AS (
                SELECT 
                    AVG(count) as avg_count,
                    STDDEV(count) as stddev_count
                FROM daily_counts
            )
            SELECT 
                dc.day,
                dc.count,
                s.avg_count,
                s.stddev_count,
                (dc.count - s.avg_count) / NULLIF(s.stddev_count, 0) as z_score
            FROM daily_counts dc
            CROSS JOIN stats s
            WHERE dc.count >= s.avg_count * {threshold}
            ORDER BY dc.count DESC
            LIMIT 20
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Temporal Clusters (Activity Bursts)", ""]
            lines.append(f"**Time Range**: {time_range}")
            lines.append(f"**Threshold**: {threshold}x average")
            lines.append(f"**Found**: {len(results)} clusters\n")

            for i, row in enumerate(results, 1):
                lines.append(f"## Cluster {i}")
                lines.append(f"- **Date**: {row.day}")
                lines.append(f"- **Count**: {row.count:,}")
                lines.append(f"- **Average**: {row.avg_count:.1f}")
                if row.z_score:
                    lines.append(f"- **Z-Score**: {row.z_score:.2f} (standard deviations above mean)")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_temporal_clusters failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_temporal_clusters_tool, handle_find_temporal_clusters))

    # Analyze activity cycles
    analyze_activity_cycles_tool = Tool(
        name="analyze_activity_cycles",
        description="Analyze cyclical patterns (day of week, hour of day, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "cycle_type": {
                    "type": "string",
                    "description": "day_of_week, hour_of_day, day_of_month",
                    "default": "day_of_week",
                },
                "time_range": {"type": "string", "default": "last_90_days"},
            },
        },
    )

    def handle_analyze_activity_cycles(arguments: dict[str, Any]) -> str:
        """Handle analyze_activity_cycles tool."""
        try:
            client = get_bigquery_client()
            cycle_type = arguments.get("cycle_type", "day_of_week")
            time_range = arguments.get("time_range", "last_90_days")

            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days = days_map.get(time_range, 90)
            cutoff_date = datetime.now() - timedelta(days=days)

            cycle_map = {
                "day_of_week": "EXTRACT(DAYOFWEEK FROM created_at) as cycle_value, ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][OFFSET(EXTRACT(DAYOFWEEK FROM created_at) - 1)] as cycle_label",
                "hour_of_day": "EXTRACT(HOUR FROM created_at) as cycle_value, CAST(EXTRACT(HOUR FROM created_at) AS STRING) as cycle_label",
                "day_of_month": "EXTRACT(DAY FROM created_at) as cycle_value, CAST(EXTRACT(DAY FROM created_at) AS STRING) as cycle_label",
            }

            cycle_expr = cycle_map.get(cycle_type, cycle_map["day_of_week"])

            query = f"""
            SELECT 
                {cycle_expr},
                COUNT(*) as count
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity`
            WHERE created_at >= '{cutoff_date.isoformat()}'
            GROUP BY cycle_value, cycle_label
            ORDER BY cycle_value
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Activity Cycles: {cycle_type}", ""]
            lines.append(f"**Time Range**: {time_range}\n")

            total = sum(row.count for row in results)
            for row in results:
                percentage = (row.count / total * 100) if total > 0 else 0
                bar_length = int(percentage / 2)  # Scale for display
                bar = "█" * bar_length
                lines.append(f"- **{row.cycle_label}**: {row.count:,} ({percentage:.1f}%) {bar}")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"analyze_activity_cycles failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((analyze_activity_cycles_tool, handle_analyze_activity_cycles))

    # Track temporal evolution
    track_temporal_evolution_tool = Tool(
        name="track_temporal_evolution",
        description="Track how metrics evolve over time periods",
        inputSchema={
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "entity_count, source_diversity, domain_expansion",
                    "default": "entity_count",
                },
                "periods": {
                    "type": "integer",
                    "description": "Number of periods to compare",
                    "default": 4,
                },
                "period_length_days": {
                    "type": "integer",
                    "description": "Days per period",
                    "default": 30,
                },
            },
        },
    )

    def handle_track_temporal_evolution(arguments: dict[str, Any]) -> str:
        """Handle track_temporal_evolution tool."""
        try:
            client = get_bigquery_client()
            metric = arguments.get("metric", "entity_count")
            periods = arguments.get("periods", 4)
            period_days = arguments.get("period_length_days", 30)

            # Build period queries
            period_queries = []
            for i in range(periods):
                start_days = (i + 1) * period_days
                end_days = i * period_days
                start_date = datetime.now() - timedelta(days=start_days)
                end_date = datetime.now() - timedelta(days=end_days)

                if metric == "entity_count":
                    period_query = f"""
                    SELECT 
                        {i} as period_num,
                        '{start_date.date()}' as period_start,
                        '{end_date.date()}' as period_end,
                        COUNT(*) as value
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE created_at >= '{start_date.isoformat()}'
                      AND created_at < '{end_date.isoformat()}'
                    """
                elif metric == "source_diversity":
                    period_query = f"""
                    SELECT 
                        {i} as period_num,
                        '{start_date.date()}' as period_start,
                        '{end_date.date()}' as period_end,
                        COUNT(DISTINCT source_platform) as value
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE created_at >= '{start_date.isoformat()}'
                      AND created_at < '{end_date.isoformat()}'
                    """
                else:  # domain_expansion
                    period_query = f"""
                    SELECT 
                        {i} as period_num,
                        '{start_date.date()}' as period_start,
                        '{end_date.date()}' as period_end,
                        COUNT(DISTINCT entity_type) as value
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                    WHERE created_at >= '{start_date.isoformat()}'
                      AND created_at < '{end_date.isoformat()}'
                    """

                period_queries.append(period_query)

            query = " UNION ALL ".join(period_queries) + " ORDER BY period_num DESC"

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Temporal Evolution: {metric}", ""]
            lines.append(f"**Periods**: {periods}")
            lines.append(f"**Period Length**: {period_days} days\n")

            prev_value = None
            for row in results:
                lines.append(f"## Period {row.period_num + 1}")
                lines.append(f"- **Range**: {row.period_start} to {row.period_end}")
                lines.append(f"- **Value**: {row.value:,}")

                if prev_value is not None:
                    change = row.value - prev_value
                    change_pct = (change / prev_value * 100) if prev_value > 0 else 0
                    direction = "↑" if change > 0 else "↓" if change < 0 else "→"
                    lines.append(f"- **Change**: {direction} {abs(change):,} ({change_pct:+.1f}%)")

                prev_value = row.value
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"track_temporal_evolution failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((track_temporal_evolution_tool, handle_track_temporal_evolution))

    return tools
