"""Governance Service implementation.

The governance service is the organism's self-observation mechanism.
It records all events (molt, processing, errors, etc.) to provide:
- Complete audit trail
- Queryable history
- Compliance reporting
- Self-awareness (organism can query its own history)

HOLD Pattern:
- HOLD₁: Incoming events (JSONL)
- AGENT: Event enrichment (timestamps, correlation)
- HOLD₂: Queryable event store (DuckDB)
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

import duckdb

from truth_forge.core.paths import get_duckdb_file
from truth_forge.services.base import BaseService
from truth_forge.services.factory import register_service


if TYPE_CHECKING:
    from collections.abc import Callable

# Retry configuration
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 0.1  # seconds


def _with_retry(
    operation: Callable[[], Any],
    operation_name: str,
    max_retries: int = MAX_RETRIES,
) -> Any:
    """Execute operation with exponential backoff retry.

    Args:
        operation: Callable to execute.
        operation_name: Name for logging.
        max_retries: Maximum retry attempts.

    Returns:
        Result of operation.

    Raises:
        Exception: If all retries exhausted.
    """
    last_error: Exception | None = None
    for attempt in range(max_retries):
        try:
            return operation()
        except duckdb.IOException as e:
            last_error = e
            if attempt < max_retries - 1:
                sleep_time = RETRY_BACKOFF_BASE * (2**attempt)
                time.sleep(sleep_time)
            continue
        except Exception:
            raise

    if last_error:
        raise last_error
    raise RuntimeError(f"Retry exhausted for {operation_name}")


@register_service()
class GovernanceService(BaseService):
    """Service for recording and querying organism events.

    The governance service is the organism's "black box" - it records
    everything that happens for audit, debugging, and self-awareness.

    Attributes:
        service_name: "governance"
    """

    service_name = "governance"

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process an incoming event record.

        Enriches the event with governance metadata:
        - Ensures event_id exists
        - Adds governance_processed_at timestamp
        - Validates required fields

        Args:
            record: Event record from HOLD₁.

        Returns:
            Enriched event record for HOLD₂.
        """
        self.logger.debug("processing_event", record_keys=list(record.keys()))

        # Ensure event has an ID
        if "event_id" not in record:
            # Generate ID from content hash
            content_str = str(sorted(record.items()))
            record["event_id"] = hashlib.sha256(content_str.encode()).hexdigest()[:32]
            self.logger.debug("generated_event_id", event_id=record["event_id"])

        # Add governance processing timestamp
        record["governance_processed_at"] = datetime.now(UTC).isoformat()

        # Ensure required fields have defaults
        if "source" not in record:
            record["source"] = "unknown"
        if "event_type" not in record:
            record["event_type"] = "unknown"

        self.logger.debug(
            "event_processed",
            event_id=record["event_id"],
            source=record["source"],
            event_type=record["event_type"],
        )

        return record

    def create_schema(self) -> str:
        """Create governance-specific DuckDB schema.

        Optimized for event querying with indexes on common filters.

        Returns:
            SQL CREATE TABLE statement.
        """
        return """
            CREATE TABLE IF NOT EXISTS governance_records (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                event_id VARCHAR,
                event_type VARCHAR,
                source VARCHAR,
                timestamp TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_governance_event_type
                ON governance_records(event_type);
            CREATE INDEX IF NOT EXISTS idx_governance_source
                ON governance_records(source);
            CREATE INDEX IF NOT EXISTS idx_governance_timestamp
                ON governance_records(timestamp);
        """

    def query_events(
        self,
        event_type: str | None = None,
        source: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Query events from HOLD₂.

        Args:
            event_type: Filter by event type.
            source: Filter by source service.
            limit: Maximum events to return (clamped to 1-10000).

        Returns:
            List of matching events.
        """
        # Sanitize limit to prevent abuse (not SQL injection, but still important)
        safe_limit = max(1, min(limit, 10000))

        self.logger.debug(
            "querying_events",
            event_type=event_type,
            source=source,
            limit=safe_limit,
        )

        duckdb_file = get_duckdb_file(self.service_name)
        if not duckdb_file.exists():
            self.logger.debug("no_duckdb_file", path=str(duckdb_file))
            return []

        def _execute_query() -> list[dict[str, Any]]:
            conn = duckdb.connect(str(duckdb_file), read_only=True)
            try:
                # Build query with all parameters (including limit)
                query = "SELECT data FROM governance_records WHERE 1=1"
                params: list[Any] = []

                if event_type:
                    query += " AND event_type = ?"
                    params.append(event_type)
                if source:
                    query += " AND source = ?"
                    params.append(source)

                # Use parameterized limit to prevent SQL injection
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(safe_limit)

                result = conn.execute(query, params).fetchall()
                events = []
                for row in result:
                    data = row[0]
                    if isinstance(data, str):
                        events.append(json.loads(data))
                    else:
                        events.append(data)
                return events
            finally:
                conn.close()

        events: list[dict[str, Any]] = _with_retry(_execute_query, "query_events")
        self.logger.debug("query_completed", event_count=len(events))
        return events

    def get_event_count(self, source: str | None = None) -> int:
        """Get total event count.

        Args:
            source: Optional filter by source.

        Returns:
            Number of events.
        """
        self.logger.debug("getting_event_count", source=source)

        duckdb_file = get_duckdb_file(self.service_name)
        if not duckdb_file.exists():
            return 0

        def _execute_count() -> int:
            conn = duckdb.connect(str(duckdb_file), read_only=True)
            try:
                if source:
                    result = conn.execute(
                        "SELECT COUNT(*) FROM governance_records WHERE source = ?",
                        [source],
                    ).fetchone()
                else:
                    result = conn.execute("SELECT COUNT(*) FROM governance_records").fetchone()
                return result[0] if result else 0
            except duckdb.CatalogException:
                # Table doesn't exist yet
                return 0
            finally:
                conn.close()

        count: int = _with_retry(_execute_count, "get_event_count")
        self.logger.debug("event_count_retrieved", count=count, source=source)
        return count

    def get_summary(self) -> dict[str, Any]:
        """Get governance summary statistics.

        Returns:
            Summary with event counts by source and type.
        """
        self.logger.debug("getting_summary")

        duckdb_file = get_duckdb_file(self.service_name)
        summary: dict[str, Any] = {
            "total_events": 0,
            "by_source": {},
            "by_type": {},
        }

        if not duckdb_file.exists():
            self.logger.debug("no_duckdb_file_for_summary", path=str(duckdb_file))
            return summary

        def _execute_summary() -> dict[str, Any]:
            conn = duckdb.connect(str(duckdb_file), read_only=True)
            try:
                result_summary: dict[str, Any] = {
                    "total_events": 0,
                    "by_source": {},
                    "by_type": {},
                }

                # Total count
                result = conn.execute("SELECT COUNT(*) FROM governance_records").fetchone()
                result_summary["total_events"] = result[0] if result else 0

                # By source
                results = conn.execute(
                    "SELECT source, COUNT(*) FROM governance_records GROUP BY source"
                ).fetchall()
                result_summary["by_source"] = {row[0]: row[1] for row in results}

                # By type
                results = conn.execute(
                    "SELECT event_type, COUNT(*) FROM governance_records GROUP BY event_type"
                ).fetchall()
                result_summary["by_type"] = {row[0]: row[1] for row in results}

                return result_summary

            except duckdb.CatalogException:
                # Table doesn't exist yet
                return {
                    "total_events": 0,
                    "by_source": {},
                    "by_type": {},
                }
            finally:
                conn.close()

        summary = _with_retry(_execute_summary, "get_summary")
        self.logger.info(
            "summary_retrieved",
            total_events=summary["total_events"],
            source_count=len(summary["by_source"]),
            type_count=len(summary["by_type"]),
        )
        return summary
