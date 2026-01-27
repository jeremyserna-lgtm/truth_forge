"""Coverage monitoring - Track enrichment coverage over time.

THE PATTERN:
- HOLD₁: entity_enrichments table state
- AGENT: Coverage analysis queries
- HOLD₂: Coverage reports and gap identification

Purpose: Track enrichment coverage over time and report gaps for prioritization.
"""

from __future__ import annotations

import argparse
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from pipelines.enrichment.config import (
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    ENRICHMENTS_TABLE,
    ENTITY_UNIFIED_TABLE,
    get_bigquery_client,
)


logger = logging.getLogger(__name__)


def get_entity_coverage() -> dict[str, Any]:
    """Get entity-level coverage statistics.

    Returns:
        Dictionary with coverage metrics
    """
    client = get_bigquery_client()

    query = f"""
    WITH total AS (
        SELECT COUNT(DISTINCT entity_id) as total_entities
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_UNIFIED_TABLE}`
    ),
    enriched AS (
        SELECT COUNT(DISTINCT entity_id) as enriched_entities
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
    )
    SELECT 
        t.total_entities,
        e.enriched_entities,
        e.enriched_entities / t.total_entities * 100 as coverage_pct
    FROM total t
    CROSS JOIN enriched e
    """

    result = list(client.query(query).result())
    if result:
        row = result[0]
        return {
            "total_entities": row.total_entities,
            "enriched_entities": row.enriched_entities,
            "coverage_pct": row.coverage_pct,
        }
    return {}


def get_coverage_by_level() -> list[dict[str, Any]]:
    """Get coverage statistics by spine level.

    Returns:
        List of dictionaries with level coverage
    """
    client = get_bigquery_client()

    query = f"""
    WITH total_by_level AS (
        SELECT level, COUNT(DISTINCT entity_id) as total
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_UNIFIED_TABLE}`
        GROUP BY level
    ),
    enriched_by_level AS (
        SELECT level, COUNT(DISTINCT entity_id) as enriched
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
        GROUP BY level
    )
    SELECT 
        t.level,
        t.total,
        COALESCE(e.enriched, 0) as enriched,
        COALESCE(e.enriched, 0) / t.total * 100 as coverage_pct
    FROM total_by_level t
    LEFT JOIN enriched_by_level e ON t.level = e.level
    ORDER BY t.level
    """

    results = list(client.query(query).result())
    return [
        {
            "level": row.level,
            "total": row.total,
            "enriched": row.enriched,
            "coverage_pct": row.coverage_pct,
        }
        for row in results
    ]


def get_coverage_by_source() -> list[dict[str, Any]]:
    """Get coverage statistics by source platform.

    Returns:
        List of dictionaries with source coverage
    """
    client = get_bigquery_client()

    query = f"""
    WITH total_by_source AS (
        SELECT source_platform, COUNT(DISTINCT entity_id) as total
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_UNIFIED_TABLE}`
        WHERE source_platform IS NOT NULL
        GROUP BY source_platform
    ),
    enriched_by_source AS (
        SELECT source_platform, COUNT(DISTINCT entity_id) as enriched
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
        WHERE source_platform IS NOT NULL
        GROUP BY source_platform
    )
    SELECT 
        t.source_platform,
        t.total,
        COALESCE(e.enriched, 0) as enriched,
        COALESCE(e.enriched, 0) / t.total * 100 as coverage_pct
    FROM total_by_source t
    LEFT JOIN enriched_by_source e ON t.source_platform = e.source_platform
    ORDER BY t.total DESC
    """

    results = list(client.query(query).result())
    return [
        {
            "source_platform": row.source_platform,
            "total": row.total,
            "enriched": row.enriched,
            "coverage_pct": row.coverage_pct,
        }
        for row in results
    ]


def get_column_coverage() -> list[dict[str, Any]]:
    """Get coverage statistics for enrichment columns.

    Returns:
        List of dictionaries with column coverage
    """
    client = get_bigquery_client()

    # Get table schema to know columns
    table_ref = client.get_table(f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}")
    columns = [field.name for field in table_ref.schema]

    # Build coverage query for key enrichment columns
    key_columns = [
        "textblob_polarity",
        "textstat_flesch_reading_ease",
        "nrclx_emotions",
        "goemotions_scores",
        "roberta_hate_label",
        "keybert_top_keyword",
        "bertopic_topic_id",
        "cluster_id",
        "primary_category",
        "is_claim",
        "resonance_group_id",
    ]

    # Filter to columns that exist
    existing_columns = [col for col in key_columns if col in columns]

    if not existing_columns:
        return []

    coverage_queries = []
    for col in existing_columns:
        coverage_queries.append(f"COUNTIF({col} IS NOT NULL) as {col.replace('.', '_')}_count")

    query = f"""
    SELECT 
        COUNT(*) as total_rows,
        {", ".join(coverage_queries)}
    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
    """

    result = list(client.query(query).result())
    if not result:
        return []

    row = result[0]
    total = row.total_rows

    coverage_data = []
    for col in existing_columns:
        count_attr = f"{col.replace('.', '_')}_count"
        count = getattr(row, count_attr, 0)
        pct = (count / total * 100) if total > 0 else 0

        coverage_data.append(
            {
                "column": col,
                "non_null_count": count,
                "coverage_pct": pct,
                "status": (
                    "excellent"
                    if pct >= 80
                    else "good"
                    if pct >= 50
                    else "partial"
                    if pct >= 20
                    else "low"
                ),
            }
        )

    return sorted(coverage_data, key=lambda x: x["coverage_pct"], reverse=True)


def generate_report(output_path: Path | None = None, format: str = "markdown") -> str:
    """Generate coverage report.

    Args:
        output_path: Path to write report (optional)
        format: Report format ("markdown" or "csv")

    Returns:
        Report content as string
    """
    # Get all coverage data
    entity_coverage = get_entity_coverage()
    level_coverage = get_coverage_by_level()
    source_coverage = get_coverage_by_source()
    column_coverage = get_column_coverage()

    if format == "markdown":
        lines = [
            "# Enrichment Coverage Report",
            "",
            f"**Generated**: {datetime.utcnow().isoformat()}",
            "",
            "## Entity-Level Coverage",
            "",
            f"- **Total Entities**: {entity_coverage.get('total_entities', 0):,}",
            f"- **Enriched Entities**: {entity_coverage.get('enriched_entities', 0):,}",
            f"- **Coverage**: {entity_coverage.get('coverage_pct', 0):.2f}%",
            "",
            "## Coverage by Spine Level",
            "",
            "| Level | Total | Enriched | Coverage % |",
            "|-------|-------|----------|------------|",
        ]

        for level_data in level_coverage:
            lines.append(
                f"| L{level_data['level']} | {level_data['total']:,} | {level_data['enriched']:,} | {level_data['coverage_pct']:.2f}% |"
            )

        lines.extend(
            [
                "",
                "## Coverage by Source Platform",
                "",
                "| Source | Total | Enriched | Coverage % |",
                "|--------|-------|----------|------------|",
            ]
        )

        for source_data in source_coverage:
            lines.append(
                f"| {source_data['source_platform']} | {source_data['total']:,} | {source_data['enriched']:,} | {source_data['coverage_pct']:.2f}% |"
            )

        lines.extend(
            [
                "",
                "## Column Coverage",
                "",
                "| Column | Non-Null | Coverage % | Status |",
                "|--------|----------|------------|--------|",
            ]
        )

        for col_data in column_coverage:
            status_emoji = {
                "excellent": "✅",
                "good": "⚠️",
                "partial": "🔶",
                "low": "❌",
            }.get(col_data["status"], "")
            lines.append(
                f"| {col_data['column']} | {col_data['non_null_count']:,} | {col_data['coverage_pct']:.2f}% | {status_emoji} {col_data['status']} |"
            )

        report_content = "\n".join(lines)

    elif format == "csv":
        # CSV format
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Entity coverage
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Entities", entity_coverage.get("total_entities", 0)])
        writer.writerow(["Enriched Entities", entity_coverage.get("enriched_entities", 0)])
        writer.writerow(["Coverage %", entity_coverage.get("coverage_pct", 0)])
        writer.writerow([])

        # Level coverage
        writer.writerow(["Level Coverage"])
        writer.writerow(["Level", "Total", "Enriched", "Coverage %"])
        for level_data in level_coverage:
            writer.writerow(
                [
                    level_data["level"],
                    level_data["total"],
                    level_data["enriched"],
                    level_data["coverage_pct"],
                ]
            )
        writer.writerow([])

        # Source coverage
        writer.writerow(["Source Coverage"])
        writer.writerow(["Source", "Total", "Enriched", "Coverage %"])
        for source_data in source_coverage:
            writer.writerow(
                [
                    source_data["source_platform"],
                    source_data["total"],
                    source_data["enriched"],
                    source_data["coverage_pct"],
                ]
            )
        writer.writerow([])

        # Column coverage
        writer.writerow(["Column Coverage"])
        writer.writerow(["Column", "Non-Null", "Coverage %", "Status"])
        for col_data in column_coverage:
            writer.writerow(
                [
                    col_data["column"],
                    col_data["non_null_count"],
                    col_data["coverage_pct"],
                    col_data["status"],
                ]
            )

        report_content = output.getvalue()

    else:
        raise ValueError(f"Unknown format: {format}")

    # Write to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content, encoding="utf-8")
        logger.info(f"Report written to {output_path}")

    return report_content


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Monitor enrichment coverage and generate reports")
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path for report",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "csv"],
        default="markdown",
        help="Report format (default: markdown)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Generate report
    report = generate_report(args.output, args.format)

    if not args.output:
        print(report)


if __name__ == "__main__":
    main()
