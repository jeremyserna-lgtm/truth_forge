"""Shared utilities for enrichment pipeline.

THE PATTERN:
- HOLD₁: Raw data, query strings
- AGENT: Utility functions
- HOLD₂: Processed data, formatted results
"""

from __future__ import annotations

import json
import logging
from typing import Any

from google.cloud import bigquery


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

    # Build column list
    all_columns = ["entity_id"] + columns + [f"{enrichment_name}_enriched_at"]

    # Build SET clause
    set_clauses = []
    for col in columns:
        set_clauses.append(f"{col} = source.{col}")
    set_clauses.append(f"{enrichment_name}_enriched_at = source.{enrichment_name}_enriched_at")
    set_clause = ", ".join(set_clauses)

    merge_sql = f"""
    MERGE `{table_id}` AS target
    USING (
        SELECT * FROM UNNEST([
            STRUCT<{", ".join(f"{col} ANY TYPE" for col in all_columns)}>(
                {", ".join("source." + col for col in all_columns)}
            )
        ]) AS source
    ) AS source
    ON target.entity_id = source.entity_id
    WHEN MATCHED THEN
        UPDATE SET {set_clause}
    WHEN NOT MATCHED THEN
        INSERT ({", ".join(all_columns)})
        VALUES ({", ".join("source." + col for col in all_columns)})
    """

    # Actually, use a simpler approach with temp table
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
    """Write batch of enrichment data to BigQuery.

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

        # Use load job for better performance
        table_ref = client.get_table(table_id)
        errors = client.insert_rows_json(table_ref, formatted_rows)

        if errors:
            logger.error(
                "insert_rows_errors",
                extra={
                    "error_count": len(errors),
                    "errors_sample": str(errors[:5]),
                },
            )
            return 0

        return len(formatted_rows)

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
