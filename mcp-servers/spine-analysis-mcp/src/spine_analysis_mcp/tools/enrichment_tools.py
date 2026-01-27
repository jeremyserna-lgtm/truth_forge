"""Enrichment Tools - entity_enrichments coverage and gap analysis.

THE PATTERN:
- HOLD₁: entity_enrichments schema, coverage queries
- AGENT: BigQuery coverage analysis
- HOLD₂: Coverage report, gap summary
"""

from __future__ import annotations

import logging
from typing import Any

from mcp.types import Tool

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, get_bigquery_client

logger = logging.getLogger(__name__)

ENRICHMENTS_TABLE = "entity_enrichments"


def get_tools() -> list[tuple[Tool, Any]]:
    """Get all enrichment analysis tools."""
    tools: list[tuple[Tool, Any]] = []

    get_coverage_tool = Tool(
        name="get_enrichment_coverage",
        description="Report coverage and gaps for spine.entity_enrichments: schema summary, "
        "row counts, entity-level coverage vs entity_unified, and which columns are missing or partial.",
        inputSchema={
            "type": "object",
            "properties": {
                "include_column_details": {
                    "type": "boolean",
                    "description": "Include per-column coverage (slower).",
                    "default": True,
                },
                "max_columns": {
                    "type": "integer",
                    "description": "Max columns to list when include_column_details is true.",
                    "default": 50,
                },
            },
        },
    )

    def handle_get_enrichment_coverage(arguments: dict[str, Any]) -> str:
        try:
            client = get_bigquery_client()
            include_cols = arguments.get("include_column_details", True)
            max_cols = arguments.get("max_columns", 50)

            lines: list[str] = [
                "# Entity Enrichments Coverage Report",
                "",
                "## Summary",
                "",
            ]

            # Table stats
            try:
                table_ref = client.dataset(BQ_DATASET_ID).table(ENRICHMENTS_TABLE)
                table = client.get_table(table_ref)
                rows = table.num_rows
                size_mb = table.num_bytes / (1024 * 1024)
                n_fields = len(table.schema)
            except Exception as e:
                logger.error("get_enrichment_coverage table stats failed: %s", e)
                return f"Error: {type(e).__name__}: {e!s}"

            lines.append(f"- **Table**: `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`")
            lines.append(f"- **Rows**: {rows:,}")
            lines.append(f"- **Size**: {size_mb:.2f} MB")
            lines.append(f"- **Fields**: {n_fields}")
            lines.append("")

            # Entity-level coverage vs entity_unified
            for tbl in ["entity_unified", "entity_production", "entity"]:
                try:
                    q = f"""
                    WITH base AS (
                        SELECT COUNT(DISTINCT entity_id) AS n
                        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{tbl}`
                    ),
                    enr AS (
                        SELECT COUNT(DISTINCT entity_id) AS n
                        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
                    )
                    SELECT base.n AS total_entities, enr.n AS enriched_entities,
                           enr.n / base.n * 100 AS coverage_pct
                    FROM base CROSS JOIN enr
                    """
                    job = client.query(q)
                    res = list(job.result())
                    if res:
                        r = res[0]
                        lines.append("## Entity-Level Coverage")
                        lines.append("")
                        lines.append(f"- **Base table**: `{tbl}`")
                        lines.append(f"- **Total entities**: {r.total_entities:,}")
                        lines.append(f"- **Enriched entities**: {r.enriched_entities:,}")
                        lines.append(f"- **Coverage**: {r.coverage_pct:.2f}%")
                        lines.append("")
                        break
                except Exception:
                    continue
            else:
                lines.append("## Entity-Level Coverage")
                lines.append("")
                lines.append("Could not compute vs entity_unified / entity_production / entity.")
                lines.append("")

            if not include_cols:
                return "\n".join(lines)

            # Per-column coverage (sample of columns to avoid huge query)
            try:
                columns = [f.name for f in table.schema if f.name not in ("entity_id",)]
            except Exception:
                columns = []

            if not columns:
                return "\n".join(lines)

            # Build a single query with COUNTIF for each column (limit columns if many)
            cols_to_check = columns[:max_cols]
            select_parts = [
                f"COUNTIF({c} IS NOT NULL) AS {c.replace('.', '_')}_cnt"
                for c in cols_to_check
            ]
            select_clause = ",\n        ".join(select_parts)

            try:
                q2 = f"""
                SELECT COUNT(*) AS total,
                       {select_clause}
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
                """
                job2 = client.query(q2)
                res2 = list(job2.result())
            except Exception as e:
                logger.warning("get_enrichment_coverage column coverage query failed: %s", e)
                lines.append("## Column Coverage")
                lines.append("")
                lines.append(f"Column-level coverage query failed: {e!s}")
                return "\n".join(lines)

            if not res2:
                return "\n".join(lines)

            row = res2[0]
            total = row.total
            lines.append("## Column Coverage")
            lines.append("")
            lines.append("| Column | Non-Null | Coverage | Status |")
            lines.append("|--------|----------|----------|--------|")

            excellent = []
            partial = []
            low = []

            for c in cols_to_check:
                attr = f"{c.replace('.', '_')}_cnt"
                cnt = getattr(row, attr, 0) or 0
                pct = (cnt / total * 100) if total else 0
                if pct >= 80:
                    status = "Excellent"
                    excellent.append(c)
                elif pct >= 20:
                    status = "Partial"
                    partial.append(c)
                else:
                    status = "Low"
                    low.append(c)
                lines.append(f"| {c} | {cnt:,} | {pct:.1f}% | {status} |")

            if len(columns) > max_cols:
                lines.append(f"| _... and {len(columns) - max_cols} more_ | | | |")
            lines.append("")

            lines.append("## Gaps Summary")
            lines.append("")
            lines.append(f"- **Excellent (≥80%)**: {len(excellent)} columns")
            lines.append(f"- **Partial (20–80%)**: {len(partial)} columns")
            lines.append(f"- **Low (<20%)**: {len(low)} columns")
            lines.append("")
            lines.append("See `docs/technical/enrichment/ENRICHMENT_COVERAGE_GAPS_REPORT.md` for full gap analysis and completion checklist.")
            lines.append("")

            return "\n".join(lines)

        except Exception as e:
            logger.error("get_enrichment_coverage failed: %s", e, exc_info=True)
            return f"Error: {type(e).__name__}: {e!s}"

    tools.append((get_coverage_tool, handle_get_enrichment_coverage))
    return tools
