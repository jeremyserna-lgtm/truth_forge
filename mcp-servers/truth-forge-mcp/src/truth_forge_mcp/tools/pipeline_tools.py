"""Pipeline Status MCP Tools.

Exposes pipeline execution status and monitoring via MCP tools.

THE PATTERN:
- HOLD₁: Tool arguments (pipeline name, stage number)
- AGENT: Pipeline status queries
- HOLD₂: Tool results (status, counts, history)
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

logger = logging.getLogger(__name__)

# Pipeline configuration
BQ_PROJECT_ID = "flash-clover-464719-g1"
BQ_DATASET_ID = "spine"


def get_pipeline_tools() -> list[tuple[Tool, Any]]:
    """Get all pipeline status tools.

    Returns:
        List of (Tool, handler) tuples.
    """
    tools: list[tuple[Tool, Any]] = []

    # Get pipeline status
    pipeline_status_tool = Tool(
        name="get_pipeline_status",
        description="Get current pipeline execution status",
        inputSchema={
            "type": "object",
            "properties": {
                "pipeline_name": {
                    "type": "string",
                    "description": "Pipeline name (e.g., 'claude_code')",
                    "default": "claude_code",
                },
            },
        },
    )

    def handle_get_pipeline_status(arguments: dict[str, Any]) -> str:
        """Handle get_pipeline_status tool.

        Args:
            arguments: Tool arguments containing pipeline_name.

        Returns:
            Markdown-formatted pipeline status.
        """
        try:
            from google.cloud import bigquery

            pipeline_name = arguments.get("pipeline_name", "claude_code")

            client = bigquery.Client(project=BQ_PROJECT_ID)

            # Stage definitions for claude_code pipeline
            stages = [
                (0, "Discovery", None),
                (1, "Extraction", f"{BQ_DATASET_ID}.claude_code_stage_1"),
                (2, "Cleaning", f"{BQ_DATASET_ID}.claude_code_stage_2"),
                (3, "Identity", f"{BQ_DATASET_ID}.claude_code_stage_3"),
                (4, "LLM Correction", f"{BQ_DATASET_ID}.claude_code_stage_4"),
                (5, "L8 Conversations", f"{BQ_DATASET_ID}.claude_code_stage_5"),
                (6, "L6 Turns", f"{BQ_DATASET_ID}.claude_code_stage_6"),
                (7, "L5 Messages", f"{BQ_DATASET_ID}.claude_code_stage_7"),
                (8, "L4 Sentences", f"{BQ_DATASET_ID}.claude_code_stage_8"),
                (9, "L3 Spans", f"{BQ_DATASET_ID}.claude_code_stage_9"),
                (10, "L2 Words", f"{BQ_DATASET_ID}.claude_code_stage_10"),
                (11, "Validation", f"{BQ_DATASET_ID}.claude_code_stage_11"),
                (12, "Denormalization", f"{BQ_DATASET_ID}.claude_code_stage_12"),
                (13, "Pre-Promotion", f"{BQ_DATASET_ID}.claude_code_stage_13"),
                (14, "Promotion", f"{BQ_DATASET_ID}.claude_code_stage_14"),
                (15, "Final Validation", f"{BQ_DATASET_ID}.claude_code_stage_15"),
                (16, "Final", f"{BQ_DATASET_ID}.entity_unified"),
            ]

            lines = [f"# Pipeline Status: {pipeline_name}", ""]

            for stage_num, stage_name, table_name in stages:
                if table_name:
                    try:
                        query = f"SELECT COUNT(*) as count FROM `{BQ_PROJECT_ID}.{table_name}`"
                        result = client.query(query).result()
                        count = next(result).count
                        status = "✓" if count > 0 else "○"
                        lines.append(f"{status} Stage {stage_num}: {stage_name} - {count:,} rows")
                    except Exception as e:
                        logger.debug(
                            "Stage table not found or inaccessible",
                            extra={"stage": stage_num, "table": table_name, "error": str(e)},
                        )
                        lines.append(f"○ Stage {stage_num}: {stage_name} - Table not found")
                else:
                    lines.append(f"○ Stage {stage_num}: {stage_name} - No table")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_pipeline_status_failed", error=str(e), exc_info=True)
            return f"Error getting pipeline status: {type(e).__name__}: {e!s}"

    tools.append((pipeline_status_tool, handle_get_pipeline_status))

    # Get stage status
    stage_status_tool = Tool(
        name="get_stage_status",
        description="Get status of a specific pipeline stage",
        inputSchema={
            "type": "object",
            "properties": {
                "pipeline_name": {
                    "type": "string",
                    "description": "Pipeline name",
                    "default": "claude_code",
                },
                "stage_number": {
                    "type": "integer",
                    "description": "Stage number (0-16)",
                    "minimum": 0,
                    "maximum": 16,
                },
            },
            "required": ["stage_number"],
        },
    )

    def handle_get_stage_status(arguments: dict[str, Any]) -> str:
        """Handle get_stage_status tool.

        Args:
            arguments: Tool arguments.

        Returns:
            Markdown-formatted stage status.
        """
        try:
            from google.cloud import bigquery

            pipeline_name = arguments.get("pipeline_name", "claude_code")
            stage_num = arguments["stage_number"]

            client = bigquery.Client(project=BQ_PROJECT_ID)

            # Map stage to table
            stage_tables = {
                1: f"{BQ_DATASET_ID}.claude_code_stage_1",
                2: f"{BQ_DATASET_ID}.claude_code_stage_2",
                3: f"{BQ_DATASET_ID}.claude_code_stage_3",
                4: f"{BQ_DATASET_ID}.claude_code_stage_4",
                5: f"{BQ_DATASET_ID}.claude_code_stage_5",
                6: f"{BQ_DATASET_ID}.claude_code_stage_6",
                7: f"{BQ_DATASET_ID}.claude_code_stage_7",
                8: f"{BQ_DATASET_ID}.claude_code_stage_8",
                9: f"{BQ_DATASET_ID}.claude_code_stage_9",
                10: f"{BQ_DATASET_ID}.claude_code_stage_10",
                11: f"{BQ_DATASET_ID}.claude_code_stage_11",
                12: f"{BQ_DATASET_ID}.claude_code_stage_12",
                13: f"{BQ_DATASET_ID}.claude_code_stage_13",
                14: f"{BQ_DATASET_ID}.claude_code_stage_14",
                15: f"{BQ_DATASET_ID}.claude_code_stage_15",
                16: f"{BQ_DATASET_ID}.entity_unified",
            }

            lines = [f"# Stage {stage_num} Status: {pipeline_name}", ""]

            if stage_num == 0:
                lines.append("Stage 0: Discovery (manifest file, no BigQuery table)")
                return "\n".join(lines)

            table_name = stage_tables.get(stage_num)
            if not table_name:
                return f"# Stage {stage_num} Status\n\nUnknown stage number."

            try:
                # Get row count
                query = f"SELECT COUNT(*) as count FROM `{BQ_PROJECT_ID}.{table_name}`"
                result = client.query(query).result()
                count = next(result).count

                lines.append(f"**Table**: {table_name}")
                lines.append(f"**Row Count**: {count:,}")
                lines.append(f"**Status**: {'✓ Active' if count > 0 else '○ Empty'}")

                # Get sample data if available
                if count > 0:
                    sample_query = f"SELECT * FROM `{BQ_PROJECT_ID}.{table_name}` LIMIT 5"
                    sample_result = client.query(sample_query).result()
                    sample_rows = list(sample_result)

                    if sample_rows:
                        lines.append("\n## Sample Data")
                        for i, row in enumerate(sample_rows, 1):
                            row_dict = dict(row)
                            entity_id = row_dict.get("entity_id", "N/A")
                            lines.append(f"{i}. Entity ID: {entity_id}")

            except Exception as e:
                lines.append(f"**Error**: {str(e)}")
                lines.append("Table may not exist or be accessible.")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_stage_status_failed", error=str(e), exc_info=True)
            return f"Error getting stage status: {type(e).__name__}: {e!s}"

    tools.append((stage_status_tool, handle_get_stage_status))

    return tools
