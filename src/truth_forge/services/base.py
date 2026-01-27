"""Base Service class enforcing HOLD pattern.

RISK MITIGATION: Ensures all services follow HOLD₁ → AGENT → HOLD₂ pattern.

All services MUST inherit from BaseService which provides:
- Automatic HOLD directory creation
- inhale() / exhale() / sync() methods
- Event schema enforcement
- Centralized path resolution
- Health check capabilities
- Thread-safe operations

Usage:
    from truth_forge.services.base import BaseService

    class KnowledgeService(BaseService):
        service_name = "knowledge"

        def process(self, record: dict) -> dict:
            # Service-specific processing
            return {"content_hash": hash(record["content"]), **record}

    service = KnowledgeService()
    service.inhale({"content": "...", "source": "web"})
    service.sync()  # Process HOLD₁ → HOLD₂
"""

from __future__ import annotations

import json
import threading
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from enum import Enum
from typing import Any, Protocol, cast

import structlog  # noqa: TC002 - used at runtime

from truth_forge.schema.event import Event, EventType, create_event


class MediatorProtocol(Protocol):
    """Protocol for mediator service to enable type-safe publish calls."""

    def publish(self, topic: str, data: dict[str, Any]) -> None:
        """Publish an event to a topic."""
        ...


class ServiceState(str, Enum):
    """Service lifecycle states."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    STOPPED = "stopped"


class BaseService(ABC):
    """Abstract base class for all truth_forge services.

    Enforces the HOLD pattern:
    - HOLD₁ (hold1/): Append-only intake (JSONL)
    - AGENT (process()): Transform/enrich records
    - HOLD₂ (hold2/): Queryable output (DuckDB)

    Subclasses MUST:
    - Define service_name class attribute
    - Implement process() method

    Subclasses MAY override:
    - on_startup() for initialization logic
    - on_shutdown() for cleanup logic
    - create_schema() for custom DuckDB schema

    Attributes:
        service_name: Unique identifier for this service.
        state: Current lifecycle state.
        logger: Structured logger for this service.
    """

    # Subclasses MUST define this
    service_name: str = ""

    @staticmethod
    def get_logger(name: str) -> structlog.stdlib.BoundLogger:
        """Get a structured logger for a service."""
        from typing import cast

        import structlog

        return cast(
            "structlog.stdlib.BoundLogger",
            structlog.get_logger(service=name),
        )

    def __init__(self) -> None:
        """Initialize service with HOLD directories and logging."""
        if not self.service_name:
            raise ValueError(
                f"{self.__class__.__name__} must define 'service_name' class attribute"
            )

        self._state = ServiceState.CREATED
        self._lock = threading.RLock()
        self._logger = BaseService.get_logger(self.service_name)

        # Initialize HOLD directories BEFORE startup hook
        from truth_forge.core.paths import ensure_service_directories

        self._paths = ensure_service_directories(self.service_name)
        self._state = ServiceState.INITIALIZING

        # Run startup hook
        self.on_startup()
        self._state = ServiceState.READY

        self._logger.info(
            "service_initialized",
            paths={k: str(v) for k, v in self._paths.items()},
        )

    @property
    def state(self) -> ServiceState:
        """Current service state (thread-safe read)."""
        with self._lock:
            return self._state

    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
        """Structured logger for this service."""
        return self._logger

    # =========================================================================
    # HOLD Pattern Methods
    # =========================================================================

    def inhale(
        self,
        data: dict[str, Any],
        event_type: EventType = EventType.RECORD_CREATED,
        aggregate_id: str | None = None,
        correlation_id: str | None = None,
    ) -> Event:
        """Write record to HOLD₁ (intake)."""
        from truth_forge.core.paths import get_intake_file  # Method-level import
        from truth_forge.services.factory import get_service  # Lazy import

        event = create_event(
            event_type=event_type,
            aggregate_type=self.service_name,
            data=data,
            aggregate_id=aggregate_id,
            correlation_id=correlation_id,
            service=self.service_name,
        )

        intake_file = get_intake_file(self.service_name)

        with self._lock, open(intake_file, "a") as f:
            f.write(event.to_jsonl() + "\n")

        # Publish governance event, unless we ARE the governance service
        if self.service_name != "governance":
            mediator = cast("MediatorProtocol", get_service("mediator"))
            mediator.publish("governance.record", event.dict())

        self._logger.debug(
            "record_inhaled",
            event_id=event.id,
            event_type=event_type.value,
        )

        return event

    def exhale(
        self,
        processed_data: dict[str, Any],
        source_event: Event | None = None,
    ) -> Event:
        """Write processed record to staging (pre-HOLD₂)."""
        from truth_forge.core.paths import get_staging_path  # Method-level import

        if source_event:
            event = source_event.child_event(
                event_type=EventType.PROCESSING_COMPLETED,
                data=processed_data,
            )
        else:
            event = create_event(
                event_type=EventType.PROCESSING_COMPLETED,
                aggregate_type=self.service_name,
                data=processed_data,
                service=self.service_name,
            )

        staging_file = get_staging_path(self.service_name, f"{self.service_name}_staged.jsonl")

        with self._lock, open(staging_file, "a") as f:
            f.write(event.to_jsonl() + "\n")

        self._logger.debug(
            "record_exhaled",
            event_id=event.id,
        )

        return event

    @abstractmethod
    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Process a single record (AGENT logic).

        Subclasses MUST implement this method.

        Args:
            record: Input record from HOLD₁.

        Returns:
            Processed record for HOLD₂.

        Raises:
            Exception: If processing fails (will be captured as signal).
        """
        ...

    def sync(self, batch_size: int = 1000) -> dict[str, Any]:
        """Sync HOLD₁ → HOLD₂ through AGENT processing."""
        import time

        from truth_forge.core.paths import get_intake_file  # Method-level import
        from truth_forge.migration.health import verify_hold_sync
        from truth_forge.services.factory import get_service  # Lazy import

        start_time = time.time()
        stats: dict[str, Any] = {
            "processed": 0,
            "failed": 0,
            "errors": [],
        }

        with self._lock:
            self._state = ServiceState.PROCESSING

        mediator = cast("MediatorProtocol", get_service("mediator"))
        mediator.publish(
            "governance.record",
            {
                "event_type": EventType.SYNC_STARTED,
                "service": self.service_name,
            },
        )

        try:
            # Read from HOLD₁
            intake_file = get_intake_file(self.service_name)
            if not intake_file.exists():
                self._logger.info("no_intake_file", path=str(intake_file))
                return stats

            records_to_process = []
            with open(intake_file) as f:
                for line_num, raw_line in enumerate(f, 1):
                    stripped_line = raw_line.strip()
                    if not stripped_line:
                        continue
                    try:
                        record = json.loads(stripped_line)
                        records_to_process.append(record)
                    except json.JSONDecodeError as e:
                        stats["failed"] += 1
                        stats["errors"].append(f"Invalid JSON at line {line_num}: {e}")
                        # Write invalid JSON to DLQ (data preservation)
                        self._write_error_signal(
                            {"_raw_line": raw_line, "_line_number": line_num},
                            ValueError(f"Invalid JSON at line {line_num}: {e}"),
                        )

            # Process through AGENT
            processed_records = []
            for record in records_to_process:
                try:
                    # Extract data from event envelope if present
                    data = record.get("data", record)
                    processed = self.process(data)
                    processed_records.append(processed)
                    stats["processed"] += 1
                except Exception as e:
                    stats["failed"] += 1
                    stats["errors"].append(str(e))
                    # Write error signal
                    self._write_error_signal(record, e)

            # Write to HOLD₂ (DuckDB)
            if processed_records:
                self._write_to_hold2(processed_records)

            stats["duration_seconds"] = time.time() - start_time

            # Verify sync health
            health = verify_hold_sync(self.service_name)
            stats["sync_health"] = health

            self._logger.info(
                "sync_completed",
                **stats,
            )

        finally:
            with self._lock:
                self._state = ServiceState.READY

        return stats

    def _write_to_hold2(self, records: list[dict[str, Any]]) -> None:
        """Write processed records to DuckDB (HOLD₂)."""
        import duckdb

        from truth_forge.core.paths import get_duckdb_file  # Method-level import

        duckdb_file = get_duckdb_file(self.service_name)
        # Sanitize table name to prevent SQL injection
        table_name = f"{self.service_name.replace(chr(34), '').replace(chr(39), '')}_records"

        # Ensure hold2 directory exists
        duckdb_file.parent.mkdir(parents=True, exist_ok=True)

        conn = duckdb.connect(str(duckdb_file))
        try:
            # Create schema if needed
            schema = self.create_schema()
            conn.execute(schema)

            # Use INSERT OR REPLACE for idempotency
            # Records with same id will be updated, not duplicated
            for record in records:
                record_json = json.dumps(record)
                # Extract id if present, otherwise generate from content hash
                record_id = record.get("id") or record.get("aggregate_id")
                if not record_id:
                    import hashlib

                    record_id = hashlib.sha256(record_json.encode()).hexdigest()[:32]

                conn.execute(
                    f"INSERT OR REPLACE INTO {table_name} (id, data) VALUES (?, ?)",
                    [record_id, record_json],
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            self._logger.error(
                "write_to_hold2_failed",
                error=str(e),
                record_count=len(records),
            )
            raise RuntimeError(f"Failed to write {len(records)} records to HOLD₂: {e}") from e
        finally:
            conn.close()

    def _write_error_signal(self, record: dict[str, Any], error: Exception) -> None:
        """Write error signal to DLQ (Dead Letter Queue)."""
        import traceback

        from truth_forge.core.paths import get_staging_path  # Method-level import

        try:
            dlq_file = get_staging_path(self.service_name, f"{self.service_name}_dlq.jsonl")

            # Ensure staging directory exists
            dlq_file.parent.mkdir(parents=True, exist_ok=True)

            signal = create_event(
                event_type=EventType.SIGNAL_ERROR,
                aggregate_type=self.service_name,
                data={
                    "original_record": record,
                    "error": str(error),
                    "traceback": traceback.format_exc(),
                },
                service=self.service_name,
            )

            with open(dlq_file, "a") as f:
                f.write(signal.to_jsonl() + "\n")

            self._logger.error(
                "processing_failed",
                error=str(error),
                event_id=signal.id,
            )
        except Exception as dlq_error:
            # DLQ write failed - log everything we can
            # This is the last-resort fallback - never lose error context
            self._logger.critical(
                "dlq_write_failed",
                dlq_error=str(dlq_error),
                original_error=str(error),
                record_preview=str(record)[:500],  # Truncate large records
            )

    def create_schema(self) -> str:
        """Create DuckDB schema for HOLD₂.

        Override this method for custom schemas. Schema MUST include:
        - id VARCHAR PRIMARY KEY (for idempotent INSERT OR REPLACE)
        - data JSON NOT NULL (record payload)

        Returns:
            SQL CREATE TABLE statement.
        """
        table_name = f"{self.service_name}_records"
        return f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id VARCHAR PRIMARY KEY,
                data JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

    # =========================================================================
    # Lifecycle Hooks
    # =========================================================================

    def on_startup(self) -> None:
        """Called during service initialization.

        Override for custom startup logic.
        """
        pass

    def on_shutdown(self) -> None:
        """Called during service shutdown.

        Override for custom cleanup logic.
        """
        pass

    def shutdown(self) -> None:
        """Gracefully shutdown the service."""
        from truth_forge.services.factory import get_service  # Lazy import

        with self._lock:
            self._state = ServiceState.STOPPED
        self.on_shutdown()

        mediator = cast("MediatorProtocol", get_service("mediator"))
        mediator.publish(
            "governance.record",
            {
                "event_type": EventType.SERVICE_STOPPED,
                "service": self.service_name,
            },
        )
        self._logger.info("service_shutdown")

    # =========================================================================
    # Health Check
    # =========================================================================

    def health_check(self) -> dict[str, Any]:
        """Check service health.

        Returns:
            Health status with checks and issues.
        """
        from truth_forge.migration.health import check_service_health

        return check_service_health(self.service_name)

    # =========================================================================
    # Iteration Support
    # =========================================================================

    def iter_hold1(self) -> Iterator[dict[str, Any]]:
        """Iterate over HOLD₁ records.

        Yields:
            Records from intake file.
        """
        from truth_forge.core.paths import get_intake_file  # Method-level import

        intake_file = get_intake_file(self.service_name)
        if not intake_file.exists():
            return

        with open(intake_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue

    @contextmanager
    def transaction(self) -> Generator[None, None, None]:
        """Context manager for atomic operations.

        Usage:
            with service.transaction():
                service.inhale(record1)
                service.inhale(record2)
                # All or nothing
        """
        with self._lock:
            try:
                yield
            except Exception:
                self._logger.error("transaction_failed")
                raise

    # =========================================================================
    # Representation
    # =========================================================================

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(service_name='{self.service_name}', state={self.state.value})>"
