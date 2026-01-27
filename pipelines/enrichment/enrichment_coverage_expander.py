"""Coverage expander - Create enrichment rows for entities missing from entity_enrichments.

THE PATTERN:
- HOLD₁: entity_unified (entities without enrichments)
- AGENT: Coverage expander (creates minimal enrichment rows)
- HOLD₂: entity_enrichments (new enrichment rows created)

Purpose: Systematically expand enrichment coverage from 4.62% to target (e.g., 50%+).
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Any

from pipelines.enrichment.config import (
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    ENRICHMENTS_TABLE,
    ENTITY_UNIFIED_TABLE,
    get_bigquery_client,
)


logger = logging.getLogger(__name__)


def expand_coverage(
    target_coverage: float = 0.50,
    priority_levels: list[int] | None = None,
    priority_sources: list[str] | None = None,
    limit: int = 0,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Expand enrichment coverage by creating minimal enrichment rows.

    Args:
        target_coverage: Target coverage percentage (0.50 = 50%)
        priority_levels: Spine levels to prioritize (default: [8, 5, 4])
        priority_sources: Source platforms to prioritize
        limit: Maximum entities to process (0 = all needed)
        dry_run: If True, only report what would be done

    Returns:
        Dictionary with expansion results
    """
    if priority_levels is None:
        priority_levels = [8, 5, 4]  # Conversations, messages, sentences

    if priority_sources is None:
        priority_sources = ["claude_code", "claude_web", "gemini_web", "codex", "cursor"]

    client = get_bigquery_client()

    # Get current coverage
    coverage_query = f"""
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
        e.enriched_entities / t.total_entities * 100 as current_coverage_pct
    FROM total t
    CROSS JOIN enriched e
    """

    try:
        result = list(client.query(coverage_query).result())
        if not result:
            logger.error("Could not determine current coverage")
            return {"error": "Could not determine current coverage"}

        row = result[0]
        total_entities = row.total_entities
        enriched_entities = row.enriched_entities
        current_coverage = row.current_coverage_pct / 100

        logger.info(
            f"Current coverage: {enriched_entities:,}/{total_entities:,} ({row.current_coverage_pct:.2f}%)"
        )

        # Calculate how many entities needed
        target_entities = int(total_entities * target_coverage)
        needed = target_entities - enriched_entities

        if needed <= 0:
            logger.info(f"Coverage already at or above target ({target_coverage * 100:.1f}%)")
            return {
                "current_coverage": current_coverage,
                "target_coverage": target_coverage,
                "status": "already_met",
            }

        if limit > 0:
            needed = min(needed, limit)

        logger.info(f"Need to create enrichment rows for {needed:,} entities")

    except Exception as e:
        logger.error(f"Error checking coverage: {e}", exc_info=True)
        return {"error": str(e)}

    # Find entities missing enrichments, prioritized
    levels_str = ", ".join(str(lev) for lev in priority_levels)
    sources_str = ", ".join(f"'{s}'" for s in priority_sources)

    entities_query = f"""
    SELECT DISTINCT
        e.entity_id,
        e.text,
        e.level,
        e.source_platform,
        e.entity_type,
        e.conversation_id,
        e.message_id,
        COALESCE(e.created_at, e.ingestion_timestamp, CURRENT_TIMESTAMP()) as priority_date
    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_UNIFIED_TABLE}` e
    LEFT JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}` enr
        ON e.entity_id = enr.entity_id
    WHERE enr.entity_id IS NULL
      AND e.level IN ({levels_str})
      AND e.source_platform IN ({sources_str})
      AND e.text IS NOT NULL
      AND LENGTH(e.text) > 10
    ORDER BY 
        e.level DESC,
        priority_date DESC
    LIMIT {needed}
    """

    if dry_run:
        logger.info(f"DRY RUN - Would execute:\n{entities_query}\n")
        count_query = (
            entities_query.replace(
                "SELECT DISTINCT\n        e.entity_id,",
                "SELECT COUNT(DISTINCT e.entity_id) as count,",
            )
            .replace("ORDER BY", "")
            .replace("LIMIT", "")
        )
        try:
            count_result = list(client.query(count_query).result())
            if count_result:
                count = (
                    count_result[0].count
                    if hasattr(count_result[0], "count")
                    else count_result[0][0]
                )
                logger.info(f"Would process {count:,} entities")
        except Exception as e:
            logger.warning(f"Could not count entities: {e}")

        return {
            "current_coverage": current_coverage,
            "target_coverage": target_coverage,
            "needed": needed,
            "status": "dry_run",
        }

    # Execute query and create enrichment rows
    try:
        query_job = client.query(entities_query)
        results = list(query_job.result())
        logger.info(f"Found {len(results):,} entities to create enrichment rows for")

        if not results:
            return {
                "current_coverage": current_coverage,
                "target_coverage": target_coverage,
                "status": "no_entities_found",
            }

        # Prepare rows for insertion
        rows_to_insert = []
        for row in results:
            enrichment_row: dict[str, Any] = {
                "entity_id": row.entity_id,
                "enrichment_text": row.text[:10000] if row.text else None,  # Limit text length
                "level": row.level,
                "source_platform": row.source_platform,
                "entity_type": row.entity_type,
                "conversation_id": row.conversation_id,
                "message_id": row.message_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            rows_to_insert.append(enrichment_row)

        # Insert to staging first
        staging_table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.staging_entity_enrichments"
        try:
            staging_table = client.get_table(staging_table_id)
        except Exception:
            # Staging table doesn't exist, create it or use production
            logger.warning(f"Staging table not found, using production: {ENRICHMENTS_TABLE}")
            staging_table_id = f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}"
            staging_table = client.get_table(staging_table_id)

        # Insert in batches
        batch_size = 1000
        total_inserted = 0

        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i : i + batch_size]
            errors = client.insert_rows_json(staging_table, batch, skip_invalid_rows=True)

            if errors:
                logger.warning(f"Batch {i // batch_size + 1} had {len(errors)} errors")
                total_inserted += len(batch) - len(errors)
            else:
                total_inserted += len(batch)

            logger.info(
                f"Inserted batch {i // batch_size + 1}: {total_inserted:,}/{len(rows_to_insert):,}"
            )

        logger.info(f"Coverage expansion complete: {total_inserted:,} enrichment rows created")

        return {
            "current_coverage": current_coverage,
            "target_coverage": target_coverage,
            "entities_processed": len(rows_to_insert),
            "entities_inserted": total_inserted,
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Error expanding coverage: {e}", exc_info=True)
        return {"error": str(e), "status": "failed"}


def main() -> None:
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Expand enrichment coverage by creating minimal enrichment rows"
    )
    parser.add_argument(
        "--target-coverage",
        type=float,
        default=0.50,
        help="Target coverage percentage (default: 0.50 = 50%%)",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="8,5,4",
        help="Priority levels (comma-separated, default: 8,5,4)",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Priority source platform (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maximum entities to process (0 = all needed)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
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

    # Parse levels
    priority_levels = [int(lev.strip()) for lev in args.level.split(",")]

    # Parse sources
    priority_sources = None
    if args.source:
        priority_sources = [args.source]

    # Run expansion
    result = expand_coverage(
        target_coverage=args.target_coverage,
        priority_levels=priority_levels,
        priority_sources=priority_sources,
        limit=args.limit,
        dry_run=args.dry_run,
    )

    if "error" in result:
        logger.error(f"Expansion failed: {result['error']}")
        sys.exit(1)

    logger.info(f"Expansion result: {result}")


if __name__ == "__main__":
    main()
