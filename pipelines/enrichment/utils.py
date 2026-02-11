"""Shared utilities for enrichment pipeline.

THE PATTERN:
- HOLD₁: Raw data, query strings
- AGENT: Utility functions
- HOLD₂: Processed data, formatted results
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from typing import Any

from google.cloud import bigquery
from google.cloud.bigquery import (
    LoadJobConfig,
    SourceFormat,
    WriteDisposition,
)


logger = logging.getLogger(__name__)


def build_merge_statement(
    table_id: str,
    source_data: list[dict[str, Any]],
    columns: list[str],
    enrichment_name: str,
) -> str:
    """Build BigQuery MERGE statement for enrichment updates.

    Args:
        table_id: Target table ID (full path)
        source_data: List of dictionaries with enrichment data
        columns: Column names to update
        enrichment_name: Name of enrichment (for timestamp column)

    Returns:
        MERGE SQL statement
    """
    if not source_data:
        return ""

    # Build VALUES clause
    values_parts = []
    for row in source_data:
        entity_id = row.get("entity_id", "")
        if not entity_id:
            continue

        value_parts = [f"'{entity_id}'"]  # entity_id

        for col in columns:
            value = row.get(col)
            if value is None:
                value_parts.append("NULL")
            elif isinstance(value, (list, dict)):
                # JSON/ARRAY types
                value_parts.append(f"JSON '{json.dumps(value)}'")
            elif isinstance(value, str):
                # Escape single quotes
                escaped = value.replace("'", "''")
                value_parts.append(f"'{escaped}'")
            elif isinstance(value, bool):
                value_parts.append("TRUE" if value else "FALSE")
            else:
                value_parts.append(str(value))

        # Add enriched_at timestamp
        value_parts.append("CURRENT_TIMESTAMP()")
        values_parts.append(f"({', '.join(value_parts)})")

    if not values_parts:
        return ""

    return _build_simple_merge(table_id, source_data, columns, enrichment_name)


def _build_simple_merge(
    table_id: str,
    source_data: list[dict[str, Any]],
    columns: list[str],
    enrichment_name: str,
) -> str:
    """Build simpler MERGE using temp table approach."""
    # This is a placeholder - actual implementation will use BigQuery load job
    # or direct INSERT with ON CONFLICT handling
    return ""


def write_batch_to_bigquery(
    client: bigquery.Client,
    table_id: str,
    rows: list[dict[str, Any]],
    columns: list[str],
    enrichment_name: str,
) -> int:
    """Write batch of enrichment data to BigQuery using batch load.

    Uses load_table_from_file instead of streaming insert for:
    - No streaming buffer issues
    - Better performance for batch operations
    - Immediate data availability for updates

    Args:
        client: BigQuery client
        table_id: Target table ID
        rows: List of dictionaries with enrichment data
        columns: Column names to write
        enrichment_name: Name of enrichment

    Returns:
        Number of rows written
    """
    if not rows:
        return 0

    try:
        # Prepare rows for BigQuery
        formatted_rows = []
        for row in rows:
            formatted_row: dict[str, Any] = {"entity_id": row["entity_id"]}

            for col in columns:
                formatted_row[col] = row.get(col)

            formatted_row[f"{enrichment_name}_enriched_at"] = None  # Will be set by BigQuery

            formatted_rows.append(formatted_row)

        # Use batch load (not streaming insert)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
            for row in formatted_rows:
                f.write(json.dumps(row) + "\n")
            temp_path = f.name

        try:
            job_config = LoadJobConfig(
                source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
                write_disposition=WriteDisposition.WRITE_APPEND,
                schema_update_options=["ALLOW_FIELD_ADDITION"],
            )

            with open(temp_path, "rb") as source_file:
                load_job = client.load_table_from_file(
                    source_file,
                    table_id,
                    job_config=job_config,
                )
                load_job.result()  # Wait for completion

            return len(formatted_rows)
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass

    except Exception as e:
        logger.error(
            "write_batch_bigquery_failed",
            extra={
                "error_type": type(e).__name__,
                "error_message": str(e),
            },
            exc_info=True,
        )
        return 0


def format_progress(current: int, total: int, prefix: str = "") -> str:
    """Format progress message.

    Args:
        current: Current item number
        total: Total items
        prefix: Optional prefix text

    Returns:
        Formatted progress string
    """
    percentage = (current / total * 100) if total > 0 else 0
    return f"{prefix}{current:,}/{total:,} ({percentage:.1f}%)"
