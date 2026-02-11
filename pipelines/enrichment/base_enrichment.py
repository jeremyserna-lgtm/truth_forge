"""Base enrichment class for all enrichment scripts.

THE PATTERN:
- HOLD₁: entity_unified entities needing enrichment
- AGENT: BaseEnrichment (abstract base class)
- HOLD₂: Enriched data ready for entity_enrichments

All enrichment scripts extend this base class to ensure consistent
CLI, query building, batch processing, and write patterns.

ROBUSTNESS FEATURES:
- Streaming pagination (never loads full dataset into memory)
- Checkpoint/resume capability
- Memory management with explicit gc
- Resource monitoring
"""

from __future__ import annotations

import argparse
import gc
import json
import logging
import os
import resource
import signal
import tempfile
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Iterator, cast

from google.cloud.bigquery import (
    LoadJobConfig,
    SourceFormat,
    WriteDisposition,
)

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


# Memory limit: 4GB default, configurable via env
MAX_MEMORY_MB = int(os.getenv("ENRICHMENT_MAX_MEMORY_MB", "4096"))
# Page size for streaming queries
STREAM_PAGE_SIZE = int(os.getenv("ENRICHMENT_STREAM_PAGE_SIZE", "5000"))


@dataclass
class Checkpoint:
    """Checkpoint state for resumable processing."""

    enrichment_name: str
    levels: list[int]
    mode: str
    last_offset: int = 0
    processed_count: int = 0
    written_count: int = 0
    failed_count: int = 0
    started_at: str = ""
    updated_at: str = ""
    completed: bool = False
    last_entity_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Checkpoint":
        """Create from dict."""
        return cls(**data)


@dataclass
class EnrichmentRunResult:
    """Result of an enrichment run with success/failure counts."""

    processed: int
    written: int
    failed: int
    dlq_count: int


def get_memory_usage_mb() -> float:
    """Get current memory usage in MB."""
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_maxrss / 1024 / 1024  # Convert to MB (macOS reports in bytes)


def check_memory_pressure() -> bool:
    """Check if memory usage is approaching limit."""
    usage_mb = get_memory_usage_mb()
    if usage_mb > MAX_MEMORY_MB * 0.8:
        logger.warning(
            "memory_pressure_high",
            extra={"usage_mb": round(usage_mb, 1), "limit_mb": MAX_MEMORY_MB},
        )
        return True
    return False


class BaseEnrichment(ABC):
    """Base class for all enrichment scripts.

    Provides unified CLI, BigQuery integration, and write patterns.
    Now with streaming pagination, checkpoints, and memory management.
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
        self._checkpoint_dir = Path.cwd() / "checkpoints"
        self._checkpoint_dir.mkdir(exist_ok=True)
        self._shutdown_requested = False
        self._setup_signal_handlers()

    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown handlers."""
        def handle_signal(signum: int, _frame: Any) -> None:
            logger.info(
                "shutdown_requested",
                extra={"signal": signum, "enrichment": self.ENRICHMENT_NAME},
            )
            self._shutdown_requested = True

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)

    def _setup_logging(self) -> None:
        """Setup logging based on verbosity."""
        level = logging.DEBUG if self.args.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    def parse_args(self) -> argparse.Namespace:
        """Parse command-line arguments."""
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
            help="Filter by source_system (e.g., claude_code, claude_web)",
        )
        parser.add_argument(
            "--entity-ids",
            type=str,
            help="File containing specific entity IDs to process (one per line)",
        )
        parser.add_argument("--limit", type=int, default=0, help="Max entities (0 = all)")
        parser.add_argument("--offset", type=int, default=0, help="Starting offset")
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
        parser.add_argument(
            "--resume",
            action="store_true",
            help="Resume from last checkpoint",
        )
        parser.add_argument(
            "--no-checkpoint",
            action="store_true",
            help="Disable checkpoint saving",
        )
        parser.add_argument(
            "--page-size",
            type=int,
            default=STREAM_PAGE_SIZE,
            help=f"Stream page size (default: {STREAM_PAGE_SIZE})",
        )
        return parser.parse_args()

    def _get_checkpoint_path(self) -> Path:
        """Get checkpoint file path for this enrichment run."""
        levels_str = self.args.level.replace(",", "_")
        return self._checkpoint_dir / f"{self.ENRICHMENT_NAME}_L{levels_str}.json"

    def _load_checkpoint(self) -> Checkpoint | None:
        """Load checkpoint from disk if exists."""
        path = self._get_checkpoint_path()
        if path.exists():
            try:
                data = json.loads(path.read_text())
                checkpoint = Checkpoint.from_dict(data)
                if not checkpoint.completed:
                    logger.info(
                        "checkpoint_loaded",
                        extra={
                            "enrichment": self.ENRICHMENT_NAME,
                            "offset": checkpoint.last_offset,
                            "processed": checkpoint.processed_count,
                        },
                    )
                    return checkpoint
            except Exception as e:
                logger.warning(
                    "checkpoint_load_failed",
                    extra={"error": str(e)},
                )
        return None

    def _save_checkpoint(self, checkpoint: Checkpoint) -> None:
        """Save checkpoint to disk."""
        if self.args.no_checkpoint:
            return
        checkpoint.updated_at = datetime.utcnow().isoformat()
        path = self._get_checkpoint_path()
        path.write_text(json.dumps(checkpoint.to_dict(), indent=2))

    def _clear_checkpoint(self) -> None:
        """Clear checkpoint file after successful completion."""
        path = self._get_checkpoint_path()
        if path.exists():
            path.unlink()

    def _get_total_count(self) -> int:
        """Get total count of entities to process."""
        level_strs = self.args.level.split(",")
        levels = [int(lev.strip()) for lev in level_strs]
        level_list = ", ".join(str(lev) for lev in levels)

        query = f"""
        SELECT COUNT(*) as cnt
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
            query += f" AND e.source_system = '{self.args.source}'"

        try:
            result = list(self.client.query(query).result())
            return result[0].cnt if result else 0
        except Exception as e:
            logger.warning("count_query_failed", extra={"error": str(e)})
            return 0

    def _build_page_query(self, offset: int, page_size: int) -> str:
        """Build paginated query for streaming."""
        level_strs = self.args.level.split(",")
        levels = [int(lev.strip()) for lev in level_strs]
        select_fields = [
            "e.entity_id",
            "e.text",
            "e.level",
            "e.source_system",
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
            query += f" AND e.source_system = '{self.args.source}'"
        if self.args.entity_ids:
            p = Path(self.args.entity_ids)
            if p.exists():
                ids = [ln.strip() for ln in p.read_text().splitlines() if ln.strip()]
                if ids:
                    query += " AND e.entity_id IN (" + ", ".join(f"'{i}'" for i in ids) + ")"

        query += " ORDER BY e.entity_id"  # Deterministic order for pagination
        query += f" LIMIT {page_size} OFFSET {offset}"
        return query

    def _stream_entities(self, start_offset: int = 0) -> Iterator[tuple[int, Any]]:
        """Stream entities in pages, yielding (offset, row) tuples."""
        page_size = self.args.page_size
        current_offset = start_offset
        total_limit = self.args.limit if self.args.limit > 0 else float("inf")
        yielded = 0

        while yielded < total_limit:
            if self._shutdown_requested:
                logger.info("shutdown_during_stream", extra={"offset": current_offset})
                break

            # Check memory before fetching next page
            if check_memory_pressure():
                logger.info("gc_triggered_by_memory_pressure")
                gc.collect()
                time.sleep(1)  # Brief pause to allow system recovery

            query = self._build_page_query(current_offset, page_size)
            try:
                results = list(self.client.query(query).result())
            except Exception as e:
                logger.error(
                    "page_query_failed",
                    extra={"offset": current_offset, "error": str(e)},
                )
                break

            if not results:
                # No more data
                break

            for row in results:
                if yielded >= total_limit:
                    break
                yield (current_offset + yielded, row)
                yielded += 1

            current_offset += len(results)

            # Force garbage collection after each page
            del results
            gc.collect()

            logger.debug(
                "page_fetched",
                extra={
                    "offset": current_offset,
                    "page_size": page_size,
                    "yielded": yielded,
                },
            )

    @abstractmethod
    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute enrichment for a single text."""
        ...

    def get_target_table(self) -> str:
        """Target table ID from args."""
        table_name = ENRICHMENTS_TABLE if self.args.production else STAGING_ENRICHMENTS_TABLE
        if self.args.table_suffix:
            table_name += self.args.table_suffix
        return f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{table_name}"

    def write_batch(self, enriched: list[dict[str, Any]]) -> int:
        """Write enriched batch to BigQuery."""
        if not enriched:
            return 0
        table_id = self.get_target_table()
        try:
            return self._write_batch_insert(table_id, enriched)
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

    def _write_batch_insert(self, table_id: str, enriched: list[dict[str, Any]]) -> int:
        """Write batch via batch load (not streaming insert).
        
        Uses load_table_from_file with NDJSON temp file for:
        - No streaming buffer issues
        - Better performance for batch operations
        - Immediate data availability for updates
        """
        if not enriched:
            return 0

        rows_to_insert: list[dict[str, Any]] = []
        for row in enriched:
            eid = row.get("entity_id")
            if not eid:
                continue
            insert_row: dict[str, Any] = {"entity_id": eid}
            for col in self.COLUMNS_OWNED:
                val = row.get(col)
                # Handle JSON serialization of complex types
                if isinstance(val, (list, dict)):
                    insert_row[col] = val
                else:
                    insert_row[col] = val
            insert_row[f"{self.ENRICHMENT_NAME}_enriched_at"] = datetime.utcnow().isoformat()
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
        def _batch_load() -> int:
            """Write rows via batch load with temp file."""
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".ndjson", delete=False
            ) as f:
                for row in rows_to_insert:
                    f.write(json.dumps(row) + "\n")
                temp_path = f.name

            try:
                job_config = LoadJobConfig(
                    source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
                    write_disposition=WriteDisposition.WRITE_APPEND,
                    schema_update_options=["ALLOW_FIELD_ADDITION"],
                )

                with open(temp_path, "rb") as source_file:
                    load_job = self.client.load_table_from_file(
                        source_file,
                        table_id,
                        job_config=job_config,
                    )
                    load_job.result()  # Wait for completion

                return len(rows_to_insert)
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        try:
            return _batch_load()
        except Exception as e:
            logger.warning(
                "batch_load_failed",
                extra={
                    "enrichment": self.ENRICHMENT_NAME,
                    "batch_size": len(rows_to_insert),
                    "error": str(e),
                },
            )
            return 0

    def run(self) -> None:
        """Main execution flow with streaming, checkpoints, and memory management."""
        if self.args.dry_run:
            self._dry_run()
            return

        # Load or create checkpoint
        checkpoint: Checkpoint | None = None
        start_offset = self.args.offset

        if self.args.resume:
            checkpoint = self._load_checkpoint()
            if checkpoint:
                start_offset = checkpoint.last_offset
                logger.info(
                    "resuming_from_checkpoint",
                    extra={
                        "offset": start_offset,
                        "previously_processed": checkpoint.processed_count,
                    },
                )

        if checkpoint is None:
            levels = [int(x.strip()) for x in self.args.level.split(",")]
            checkpoint = Checkpoint(
                enrichment_name=self.ENRICHMENT_NAME,
                levels=levels,
                mode=self.args.mode,
                last_offset=start_offset,
                started_at=datetime.utcnow().isoformat(),
            )

        # Get total count for progress reporting
        total_count = self._get_total_count()
        if total_count == 0:
            logger.info(
                "enrichment_nothing_to_process",
                extra={"enrichment": self.ENRICHMENT_NAME},
            )
            return

        logger.info(
            "enrichment_starting",
            extra={
                "enrichment": self.ENRICHMENT_NAME,
                "total_entities": total_count,
                "start_offset": start_offset,
                "page_size": self.args.page_size,
                "target_table": self.get_target_table(),
            },
        )

        enriched: list[dict[str, Any]] = []
        written = checkpoint.written_count
        failed = checkpoint.failed_count
        processed = checkpoint.processed_count
        stage = f"enrichment_{self.ENRICHMENT_NAME}"
        last_checkpoint_save = time.time()
        checkpoint_interval = 60  # Save checkpoint every 60 seconds

        try:
            for offset, row in self._stream_entities(start_offset):
                if self._shutdown_requested:
                    logger.info(
                        "graceful_shutdown",
                        extra={
                            "processed": processed,
                            "written": written,
                            "offset": offset,
                        },
                    )
                    break

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
                    processed += 1

                    # Write batch when full
                    if len(enriched) >= self.args.write_batch_size:
                        w = self.write_batch(enriched)
                        written += w
                        enriched = []
                        gc.collect()  # Clean up after batch write

                        # Update checkpoint
                        checkpoint.last_offset = offset + 1
                        checkpoint.processed_count = processed
                        checkpoint.written_count = written
                        checkpoint.failed_count = failed
                        checkpoint.last_entity_id = eid or ""

                        # Save checkpoint periodically
                        if time.time() - last_checkpoint_save > checkpoint_interval:
                            self._save_checkpoint(checkpoint)
                            last_checkpoint_save = time.time()

                        if self.args.progress:
                            logger.info(
                                "enrichment_progress",
                                extra={
                                    "enrichment": self.ENRICHMENT_NAME,
                                    "processed": processed,
                                    "written": written,
                                    "total": total_count,
                                    "pct": round(processed / total_count * 100, 1),
                                    "memory_mb": round(get_memory_usage_mb(), 1),
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
                    )

            # Write remaining batch
            if enriched:
                w = self.write_batch(enriched)
                written += w

            # Mark complete and clear checkpoint
            checkpoint.completed = True
            checkpoint.processed_count = processed
            checkpoint.written_count = written
            checkpoint.failed_count = failed
            self._save_checkpoint(checkpoint)

            if not self._shutdown_requested:
                self._clear_checkpoint()

        except Exception as e:
            logger.error(
                "enrichment_run_failed",
                extra={
                    "enrichment": self.ENRICHMENT_NAME,
                    "error": str(e),
                    "processed": processed,
                    "written": written,
                },
                exc_info=True,
            )
            # Save checkpoint on failure for resume
            checkpoint.processed_count = processed
            checkpoint.written_count = written
            checkpoint.failed_count = failed
            self._save_checkpoint(checkpoint)
            raise

        dlq_count = self._dlq.count()
        logger.info(
            "enrichment_complete",
            extra={
                "enrichment": self.ENRICHMENT_NAME,
                "processed": processed,
                "written": written,
                "failed": failed,
                "dlq_count": dlq_count,
                "final_memory_mb": round(get_memory_usage_mb(), 1),
            },
        )

    def _dry_run(self) -> None:
        """Log dry-run info with count."""
        total = self._get_total_count()
        logger.info(
            "enrichment_dry_run",
            extra={
                "enrichment": self.ENRICHMENT_NAME,
                "would_process": total,
                "levels": self.args.level,
                "mode": self.args.mode,
                "target_table": self.get_target_table(),
            },
        )
