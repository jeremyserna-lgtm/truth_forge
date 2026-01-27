"""Base enrichment class for all enrichment scripts.

THE PATTERN:
- HOLD₁: entity_unified entities needing enrichment
- AGENT: BaseEnrichment (abstract base class)
- HOLD₂: Enriched data ready for entity_enrichments

All enrichment scripts extend this base class to ensure consistent
CLI, query building, batch processing, and write patterns.
"""

from __future__ import annotations

import argparse
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from pipelines.enrichment.config import (
    BQ_DATASET_ID,
    BQ_PROJECT_ID,
    DEFAULT_BATCH_SIZE,
    DEFAULT_WRITE_BATCH_SIZE,
    ENRICHMENTS_TABLE,
    ENTITY_UNIFIED_TABLE,
    MIN_TEXT_LENGTH,
    STAGING_ENRICHMENTS_TABLE,
    get_bigquery_client,
)
from pipelines.enrichment.dlq import DeadLetterQueue
from pipelines.enrichment.utils import format_progress


logger = logging.getLogger(__name__)


@dataclass
class EnrichmentRunResult:
    """Result of an enrichment run with success/failure counts."""

    processed: int
    written: int
    failed: int
    dlq_count: int


class BaseEnrichment(ABC):
    """Base class for all enrichment scripts.

    Provides unified CLI, BigQuery integration, and write patterns.
    """

    ENRICHMENT_NAME: ClassVar[str] = "base"
    COLUMNS_OWNED: ClassVar[list[str]] = []
    REQUIRES_EMBEDDING: ClassVar[bool] = False

    def __init__(self) -> None:
        """Initialize enrichment script."""
        self.client = get_bigquery_client()
        self.args = self.parse_args()
        self._setup_logging()
        self._dlq = DeadLetterQueue(
            Path.cwd() / "dlq",
            f"enrichment_{self.ENRICHMENT_NAME}",
        )

    def _setup_logging(self) -> None:
        """Setup logging based on verbosity."""
        level = logging.DEBUG if self.args.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments.

        Returns:
            Parsed arguments namespace.
        """
        parser = argparse.ArgumentParser(
            description=f"Enrichment: {self.ENRICHMENT_NAME}",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument(
            "--mode",
            choices=["null-only", "overwrite", "append"],
            default="null-only",
            help="Write mode: null-only (default), overwrite, append",
        )
        parser.add_argument(
            "--level",
            type=str,
            default="5,8",
            help="Entity levels to process (comma-separated, e.g., '5,8')",
        )
        parser.add_argument(
            "--source",
            type=str,
            help="Filter by source_platform (e.g., claude_code, claude_web)",
        )
        parser.add_argument(
            "--entity-ids",
            type=str,
            help="File containing specific entity IDs to process (one per line)",
        )
        parser.add_argument("--limit", type=int, default=0, help="Max entities (0 = all)")
        parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
        parser.add_argument(
            "--batch-size",
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help=f"Processing batch size (default: {DEFAULT_BATCH_SIZE})",
        )
        parser.add_argument(
            "--write-batch-size",
            type=int,
            default=DEFAULT_WRITE_BATCH_SIZE,
            help=f"Write batch size (default: {DEFAULT_WRITE_BATCH_SIZE})",
        )
        parser.add_argument("--dry-run", action="store_true", help="No writes")
        parser.add_argument("--verbose", action="store_true", help="Verbose logging")
        parser.add_argument("--progress", action="store_true", help="Progress updates")
        parser.add_argument(
            "--staging",
            action="store_true",
            default=True,
            help="Write to staging (default)",
        )
        parser.add_argument("--production", action="store_true", help="Write to production")
        parser.add_argument("--table-suffix", type=str, default="", help="Table suffix")
        parser.add_argument(
            "--use-existing-embedding",
            action="store_true",
            help="Use existing sentence_embedding (Group C)",
        )
        return parser.parse_args()

    def build_query(self) -> str:
        """Build query to find entities needing enrichment.

        Returns:
            SQL query string.
        """
        level_strs = self.args.level.split(",")
        levels = [int(lev.strip()) for lev in level_strs]
        select_fields = [
            "e.entity_id",
            "e.text",
            "e.level",
            "e.source_platform",
            "e.entity_type",
            "e.conversation_id",
            "e.message_id",
        ]
        if self.REQUIRES_EMBEDDING and self.args.use_existing_embedding:
            select_fields.append("s.sentence_embedding")
        level_list = ", ".join(str(lev) for lev in levels)
        query = f"""
        SELECT {", ".join(select_fields)}
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENTITY_UNIFIED_TABLE}` e
        LEFT JOIN `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}` s
            ON e.entity_id = s.entity_id
        WHERE e.level IN ({level_list})
          AND e.text IS NOT NULL
          AND LENGTH(e.text) > {MIN_TEXT_LENGTH}
        """
        if self.args.mode == "null-only":
            if self.COLUMNS_OWNED:
                null_checks = " OR ".join(f"s.{col} IS NULL" for col in self.COLUMNS_OWNED)
                query += f" AND (s.entity_id IS NULL OR {null_checks})"
            else:
                query += " AND s.entity_id IS NULL"
        if self.args.source:
            query += f" AND e.source_platform = '{self.args.source}'"
        if self.args.entity_ids:
            p = Path(self.args.entity_ids)
            if p.exists():
                ids = [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]
                if ids:
                    query += " AND e.entity_id IN (" + ", ".join(f"'{i}'" for i in ids) + ")"
        query += " ORDER BY e.level DESC, COALESCE(e.created_at, e.ingestion_timestamp, CURRENT_TIMESTAMP()) DESC"
        if self.args.limit > 0:
            query += f" LIMIT {self.args.limit}"
        if self.args.offset > 0:
            query += f" OFFSET {self.args.offset}"
        return query

    @abstractmethod
    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute enrichment for a single text.

        Args:
            text: Text content to enrich.
            existing_embedding: Existing sentence embedding if available.

        Returns:
            Dict with enrichment data (keys match COLUMNS_OWNED).
        """
        ...

    def get_target_table(self) -> str:
        """Target table ID from args.

        Returns:
            Full table ID (project.dataset.table).
        """
        table_name = ENRICHMENTS_TABLE if self.args.production else STAGING_ENRICHMENTS_TABLE
        if self.args.table_suffix:
            table_name += self.args.table_suffix
        return f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{table_name}"

    def _query_bq(self, query: str) -> list[Any]:
        """Run BigQuery query with retry."""
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential,
        )

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
            reraise=True,
        )
        def _run() -> list[Any]:
            job = self.client.query(query)
            return list(job.result())

        return _run()

    def write_batch(self, enriched: list[dict[str, Any]]) -> int:
        """Write enriched batch to BigQuery.

        Args:
            enriched: List of enrichment dicts.

        Returns:
            Number of rows written.
        """
        if not enriched:
            return 0
        table_id = self.get_target_table()
        try:
            return self._write_batch_merge(table_id, enriched)
        except Exception as e:
            logger.error(
                "write_batch_failed",
                extra={
                    "enrichment": self.ENRICHMENT_NAME,
                    "table": table_id,
                    "batch_size": len(enriched),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            return 0

    def _write_batch_merge(self, table_id: str, enriched: list[dict[str, Any]]) -> int:
        """Write batch via insert_rows_json (idempotent via null-only mode)."""
        if not enriched:
            return 0
        rows_to_insert: list[dict[str, Any]] = []
        for row in enriched:
            eid = row.get("entity_id")
            if not eid:
                continue
            insert_row: dict[str, Any] = {"entity_id": eid}
            for col in self.COLUMNS_OWNED:
                insert_row[col] = row.get(col)
            insert_row[f"{self.ENRICHMENT_NAME}_enriched_at"] = datetime.utcnow()
            rows_to_insert.append(insert_row)
        if not rows_to_insert:
            return 0
        from tenacity import (
            retry,
            retry_if_exception_type,
            stop_after_attempt,
            wait_exponential,
        )

        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError)),
            reraise=True,
        )
        def _insert() -> list[dict[str, Any]]:
            table_ref = self.client.get_table(table_id)
            return self.client.insert_rows_json(table_ref, rows_to_insert, skip_invalid_rows=True)

        errors = _insert()
        n_err = len(errors) if errors else 0
        if n_err:
            logger.warning(
                "insert_rows_partial_errors",
                extra={
                    "enrichment": self.ENRICHMENT_NAME,
                    "batch_size": len(rows_to_insert),
                    "error_count": n_err,
                },
            )
        return len(rows_to_insert) - n_err

    def run(self) -> None:
        """Main execution flow. Uses DLQ for failed records."""
        query = self.build_query()
        if self.args.dry_run:
            self._dry_run(query)
            return
        try:
            results = self._query_bq(query)
        except Exception as e:
            logger.error(
                "enrichment_query_failed",
                extra={
                    "enrichment": self.ENRICHMENT_NAME,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
                exc_info=True,
            )
            return
        if not results:
            logger.info(
                "enrichment_nothing_to_process",
                extra={"enrichment": self.ENRICHMENT_NAME},
            )
            return
        total = len(results)
        enriched: list[dict[str, Any]] = []
        written = 0
        failed = 0
        stage = f"enrichment_{self.ENRICHMENT_NAME}"

        for i, row in enumerate(results):
            try:
                text = getattr(row, "text", None) or (
                    row.get("text") if isinstance(row, dict) else ""
                )
                if not text:
                    continue
                existing_emb: list[float] | None = None
                if (
                    self.REQUIRES_EMBEDDING
                    and self.args.use_existing_embedding
                    and hasattr(row, "sentence_embedding")
                ):
                    emb = getattr(row, "sentence_embedding", None)
                    existing_emb = emb if isinstance(emb, list) else None
                out = self.compute_enrichment(text, existing_emb)
                eid = getattr(row, "entity_id", None) or (
                    row.get("entity_id") if isinstance(row, dict) else None
                )
                out["entity_id"] = eid
                enriched.append(out)

                if len(enriched) >= self.args.write_batch_size:
                    w = self.write_batch(enriched)
                    written += w
                    enriched = []
                    logger.info(
                        "enrichment_batch_written",
                        extra={
                            "enrichment": self.ENRICHMENT_NAME,
                            "written": w,
                            "progress": format_progress(i + 1, total),
                        },
                    )
                if self.args.progress and (i + 1) % 100 == 0:
                    logger.info(
                        "enrichment_progress",
                        extra={
                            "enrichment": self.ENRICHMENT_NAME,
                            "current": i + 1,
                            "total": total,
                        },
                    )
            except Exception as e:
                failed += 1
                rec: dict[str, Any] = {
                    "entity_id": getattr(row, "entity_id", None)
                    or (row.get("entity_id") if isinstance(row, dict) else None),
                    "text_preview": (text[:200] if text else ""),
                }
                self._dlq.send(rec, e, stage, attempt_count=1)
                logger.error(
                    "enrichment_record_failed",
                    extra={
                        "enrichment": self.ENRICHMENT_NAME,
                        "entity_id": rec.get("entity_id"),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )

        if enriched:
            w = self.write_batch(enriched)
            written += w
        dlq_count = self._dlq.count()
        logger.info(
            "enrichment_complete",
            extra={
                "enrichment": self.ENRICHMENT_NAME,
                "processed": total,
                "written": written,
                "failed": failed,
                "dlq_count": dlq_count,
            },
        )

    def _dry_run(self, query: str) -> None:
        """Log dry-run query and optional count."""
        logger.info(
            "enrichment_dry_run",
            extra={"enrichment": self.ENRICHMENT_NAME, "query_preview": query[:500]},
        )
        count_q = query.replace(
            "SELECT " + query.split("SELECT ")[1].split(" FROM")[0],
            "SELECT COUNT(*) as cnt",
            1,
        )
        try:
            rows = self._query_bq(count_q)
            cnt = getattr(rows[0], "cnt", None) or (rows[0][0] if rows else 0)
            logger.info(
                "enrichment_dry_run_count",
                extra={"enrichment": self.ENRICHMENT_NAME, "would_process": cnt},
            )
        except Exception as e:
            logger.warning(
                "enrichment_dry_run_count_failed",
                extra={
                    "enrichment": self.ENRICHMENT_NAME,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )
