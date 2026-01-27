"""Pattern Tools - Pattern detection, anomalies, and recurring sequences.

THE PATTERN:
- HOLD₁: Pattern criteria, thresholds
- AGENT: Pattern detection queries
- HOLD₂: Detected patterns and anomalies
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, DEFAULT_LIMIT, ENTITY_TABLE, get_bigquery_client

logger = logging.getLogger(__name__)


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all pattern detection tools."""
    tools: list[tuple[Tool, Any]] = []

    # Detect patterns
    detect_patterns_tool = Tool(
        name="detect_patterns",
        description="Detect patterns in entity data (recurring text, sequences, etc.)",
        inputSchema={
            "type": "object",
            "properties": {
                "pattern_type": {
                    "type": "string",
                    "description": "recurring_text, sequence, frequency",
                    "default": "recurring_text",
                },
                "min_frequency": {
                    "type": "integer",
                    "description": "Minimum occurrences to be considered a pattern",
                    "default": 5,
                },
                "level": {
                    "type": "integer",
                    "description": "Filter by spine level (optional)",
                },
            },
        },
    )

    def handle_detect_patterns(arguments: dict[str, Any]) -> str:
        """Handle detect_patterns tool."""
        try:
            client = get_bigquery_client()
            pattern_type = arguments.get("pattern_type", "recurring_text")
            min_freq = arguments.get("min_frequency", 5)
            level = arguments.get("level")

            level_filter = f" AND level = {level}" if level else ""

            if pattern_type == "recurring_text":
                # Find common text patterns (simplified - look for common prefixes)
                query = f"""
                SELECT 
                    SUBSTR(text, 1, 50) as text_pattern,
                    COUNT(*) as frequency,
                    COUNT(DISTINCT source_platform) as source_count
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE text IS NOT NULL {level_filter}
                GROUP BY text_pattern
                HAVING COUNT(*) >= {min_freq}
                ORDER BY frequency DESC
                LIMIT 50
                """
            elif pattern_type == "frequency":
                # Frequency patterns by entity type
                query = f"""
                SELECT 
                    entity_type,
                    COUNT(*) as frequency,
                    COUNT(DISTINCT source_platform) as source_count
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
                WHERE 1=1 {level_filter}
                GROUP BY entity_type
                HAVING COUNT(*) >= {min_freq}
                ORDER BY frequency DESC
                LIMIT 50
                """
            else:
                return f"Error: Unknown pattern_type: {pattern_type}"

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Pattern Detection: {pattern_type}", ""]
            lines.append(f"**Min Frequency**: {min_freq}")
            lines.append(f"**Found**: {len(results)} patterns\n")

            for i, row in enumerate(results[:30], 1):
                lines.append(f"## Pattern {i}")
                if pattern_type == "recurring_text":
                    lines.append(f"- **Text Pattern**: {row.text_pattern}...")
                else:
                    lines.append(f"- **Entity Type**: {row.entity_type}")
                lines.append(f"- **Frequency**: {row.frequency:,}")
                lines.append(f"- **Sources**: {row.source_count}")
                lines.append("")

            if len(results) > 30:
                lines.append(f"\n... and {len(results) - 30} more patterns")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"detect_patterns failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((detect_patterns_tool, handle_detect_patterns))

    # Identify pattern anomalies
    identify_pattern_anomalies_tool = Tool(
        name="identify_pattern_anomalies",
        description="Identify unusual pattern occurrences (outliers, breaks in patterns)",
        inputSchema={
            "type": "object",
            "properties": {
                "anomaly_type": {
                    "type": "string",
                    "description": "statistical, temporal, frequency",
                    "default": "statistical",
                },
                "sensitivity": {
                    "type": "number",
                    "description": "Sensitivity (higher = more anomalies detected)",
                    "default": 2.0,
                },
            },
        },
    )

    def handle_identify_pattern_anomalies(arguments: dict[str, Any]) -> str:
        """Handle identify_pattern_anomalies tool."""
        try:
            client = get_bigquery_client()
            anomaly_type = arguments.get("anomaly_type", "statistical")
            sensitivity = arguments.get("sensitivity", 2.0)

            if anomaly_type == "statistical":
                # Find entities with unusual characteristics
                query = f"""
                WITH stats AS (
                    SELECT 
                        AVG(LENGTH(text)) as avg_length,
                        STDDEV(LENGTH(text)) as stddev_length
                    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity`
                    WHERE text IS NOT NULL
                )
                SELECT 
                    e.entity_id,
                    e.level,
                    e.source_platform as source_system,
                    LENGTH(e.text) as text_length,
                    s.avg_length,
                    s.stddev_length,
                    ABS(LENGTH(e.text) - s.avg_length) / NULLIF(s.stddev_length, 0) as z_score
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}` e
                CROSS JOIN stats s
                WHERE e.text IS NOT NULL
                  AND ABS(LENGTH(e.text) - s.avg_length) / NULLIF(s.stddev_length, 0) >= {sensitivity}
                ORDER BY z_score DESC
                LIMIT 50
                """
            else:
                return f"Error: Unknown anomaly_type: {anomaly_type}"

            query_job = client.query(query)
            results = list(query_job.result())

            lines = [f"# Pattern Anomalies: {anomaly_type}", ""]
            lines.append(f"**Sensitivity**: {sensitivity} standard deviations")
            lines.append(f"**Found**: {len(results)} anomalies\n")

            for i, row in enumerate(results[:20], 1):
                lines.append(f"## Anomaly {i}")
                lines.append(f"- **Entity ID**: {row.entity_id}")
                lines.append(f"- **Level**: L{row.level}")
                lines.append(f"- **Source**: {row.source_system}")
                lines.append(f"- **Text Length**: {row.text_length:,}")
                lines.append(f"- **Average**: {row.avg_length:.1f}")
                lines.append(f"- **Z-Score**: {row.z_score:.2f}")
                lines.append("")

            if len(results) > 20:
                lines.append(f"\n... and {len(results) - 20} more anomalies")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"identify_pattern_anomalies failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((identify_pattern_anomalies_tool, handle_identify_pattern_anomalies))

    # Find repeating patterns
    find_repeating_patterns_tool = Tool(
        name="find_repeating_patterns",
        description="Find repeating sequences or patterns in entity data",
        inputSchema={
            "type": "object",
            "properties": {
                "sequence_length": {
                    "type": "integer",
                    "description": "Length of sequence to look for",
                    "default": 3,
                },
                "min_repetitions": {
                    "type": "integer",
                    "description": "Minimum number of repetitions",
                    "default": 2,
                },
            },
        },
    )

    def handle_find_repeating_patterns(arguments: dict[str, Any]) -> str:
        """Handle find_repeating_patterns tool."""
        try:
            client = get_bigquery_client()
            seq_length = arguments.get("sequence_length", 3)
            min_reps = arguments.get("min_repetitions", 2)

            # Simplified: find entities that appear in sequences
            query = f"""
            SELECT 
                entity_type,
                source_platform as source_system,
                COUNT(*) as frequency
            FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_TABLE}`
            GROUP BY entity_type, source_platform
            HAVING COUNT(*) >= {min_reps * seq_length}
            ORDER BY frequency DESC
            LIMIT 30
            """

            query_job = client.query(query)
            results = list(query_job.result())

            lines = ["# Repeating Patterns", ""]
            lines.append(f"**Sequence Length**: {seq_length}")
            lines.append(f"**Min Repetitions**: {min_reps}")
            lines.append(f"**Found**: {len(results)} potential patterns\n")

            for i, row in enumerate(results, 1):
                lines.append(f"## Pattern {i}")
                lines.append(f"- **Entity Type**: {row.entity_type}")
                lines.append(f"- **Source**: {row.source_system}")
                lines.append(f"- **Frequency**: {row.frequency:,}")
                lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"find_repeating_patterns failed: {e}", exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((find_repeating_patterns_tool, handle_find_repeating_patterns))

    return tools
