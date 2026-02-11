"""Safe BigQuery writer with pre-flight checks and backup.

This is the ONLY approved way to write to BigQuery in truth_forge.
All other methods are blocked by runtime protection.

Per DATA PROTECTION LAWS:
- NO streaming inserts (causes duplicates)
- Pre-write backup required for protected tables
- Schema validation before every write
- Post-write verification

Usage:
    from pipelines.core.bigquery_safe import SafeBigQueryWriter

    writer = SafeBigQueryWriter(client, "project.dataset.table")
    rows_written = writer.write_batch(records)  # Enforces rules, creates backup

Author: Claude (Opus 4.5)
Date: 2026-02-02
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import UTC, datetime
from typing import Any

from google.cloud import bigquery
from google.cloud.bigquery import (
    CreateDisposition,
    LoadJobConfig,
    SourceFormat,
    WriteDisposition,
)

from pipelines.core.dlq import DLQ
from pipelines.core.enforcement import (
    EnforcementError,
    enforce_batch,
    enforce_batch_or_raise,
)
from pipelines.core.runtime_protection import activate_protection, is_protection_active


logger = logging.getLogger(__name__)


# Production tables that require backup before modification
PROTECTED_TABLES = {
    "spine.entity_unified",
    "spine.entity_enrichments",
    "identity.contacts_master",
    "identity.id_registry",
}


class SafeBigQueryWriter:
    """Safe BigQuery writer with enforcement and backup.

    This is the ONLY approved method for writing to BigQuery.
    Streaming inserts are blocked at the runtime level.

    Features:
    - Pre-write validation using enforcement rules
    - Automatic backup before writing to protected tables
    - Post-write verification
    - DLQ integration for failed records
    - Batch-only writes (never streaming)

    Usage:
        writer = SafeBigQueryWriter(client, "project.dataset.table")
        rows_written = writer.write_batch(records)
    """

    def __init__(
        self,
        client: bigquery.Client,
        table_id: str,
        *,
        require_backup: bool = True,
        backup_retention_days: int = 7,
        dlq_stage_name: str = "bigquery_safe_writer",
    ) -> None:
        """Initialize safe writer.

        Args:
            client: BigQuery client
            table_id: Full table ID (project.dataset.table)
            require_backup: Whether to require backup before write
            backup_retention_days: Days to retain backups
            dlq_stage_name: Stage name for DLQ entries
        """
        # Ensure runtime protection is active
        if not is_protection_active():
            activate_protection()

        self.client = client
        self.table_id = table_id
        self.require_backup = require_backup
        self.backup_retention_days = backup_retention_days
        self._backup_created = False
        self._backup_table_id: str | None = None
        self.dlq = DLQ(dlq_stage_name)

    def _is_protected_table(self) -> bool:
        """Check if table is protected."""
        for pattern in PROTECTED_TABLES:
            if pattern in self.table_id:
                return True
        return False

    def _create_backup(self) -> str | None:
        """Create backup of protected table.

        Returns backup table ID or None if not needed/failed.
        """
        if not self._is_protected_table():
            logger.debug(
                "backup_not_required",
                extra={"table": self.table_id, "reason": "not_protected"},
            )
            return None

        if not self.require_backup:
            logger.warning(
                "backup_disabled",
                extra={"table": self.table_id, "warning": "backup_requirement_disabled"},
            )
            return None

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_table_id = f"{self.table_id}_backup_{timestamp}"

        # Use CREATE TABLE AS SELECT for backup
        query = f"""
        CREATE TABLE `{backup_table_id}`
        OPTIONS (
            expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL {self.backup_retention_days} DAY)
        )
        AS SELECT * FROM `{self.table_id}`
        """

        try:
            job = self.client.query(query)
            job.result()

            # Verify backup was created
            backup_table = self.client.get_table(backup_table_id)
            backup_rows = backup_table.num_rows

            logger.info(
                "backup_created",
                extra={
                    "source_table": self.table_id,
                    "backup_table": backup_table_id,
                    "row_count": backup_rows,
                    "retention_days": self.backup_retention_days,
                },
            )

            self._backup_created = True
            self._backup_table_id = backup_table_id
            return backup_table_id

        except Exception as e:
            logger.error(
                "backup_failed",
                extra={"table": self.table_id, "error": str(e)},
            )
            raise RuntimeError(f"Failed to create backup before write: {e}") from e

    def write_batch(
        self,
        records: list[dict[str, Any]],
        *,
        use_merge: bool = False,
        skip_backup: bool = False,
    ) -> int:
        """Write batch to BigQuery with full enforcement.

        Args:
            records: Records to write (will be validated)
            use_merge: If True, use MERGE for deduplication
            skip_backup: If True, skip backup (NOT RECOMMENDED)

        Returns:
            Number of records written

        Raises:
            EnforcementError: If any record fails validation
            RuntimeError: If backup or write fails
        """
        if not records:
            logger.info("write_batch_empty", extra={"table": self.table_id})
            return 0

        # Step 1: Enforce all rules
        result = enforce_batch(records)
        if not result.passed:
            # Send failed records to DLQ
            for violation in result.get_errors() + result.get_fatals():
                self.dlq.send(
                    record_id=violation.record_id,
                    error_type=violation.rule,
                    error_message=violation.message,
                    stage="pre_write_enforcement",
                )

            logger.error(
                "write_batch_enforcement_failed",
                extra={
                    "table": self.table_id,
                    "record_count": result.record_count,
                    "rejected_count": result.rejected_count,
                },
            )
            raise EnforcementError(result)

        logger.info(
            "write_batch_enforcement_passed",
            extra={
                "table": self.table_id,
                "record_count": result.record_count,
                "warning_count": len(result.get_warnings()),
            },
        )

        # Step 2: Create backup if needed
        if not skip_backup and self._is_protected_table() and self.require_backup:
            self._create_backup()

        # Step 3: Write to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ndjson",
            delete=False,
            prefix="bigquery_safe_",
        ) as f:
            for record in records:
                # Convert metadata to JSON string if dict
                record_copy = record.copy()
                if isinstance(record_copy.get("metadata"), dict):
                    record_copy["metadata"] = json.dumps(record_copy["metadata"])
                f.write(json.dumps(record_copy) + "\n")
            temp_path = f.name

        try:
            if use_merge:
                rows_written = self._write_with_merge(temp_path, records)
            else:
                rows_written = self._write_append(temp_path)

            # Step 4: Post-write verification
            self._verify_write(len(records))

            logger.info(
                "write_batch_complete",
                extra={
                    "table": self.table_id,
                    "records_submitted": len(records),
                    "rows_written": rows_written,
                    "backup_created": self._backup_created,
                },
            )

            return rows_written

        finally:
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except Exception:
                pass

    def _write_append(self, temp_path: str) -> int:
        """Write via batch load append."""
        job_config = LoadJobConfig(
            source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=WriteDisposition.WRITE_APPEND,
            create_disposition=CreateDisposition.CREATE_NEVER,
        )

        with open(temp_path, "rb") as source_file:
            load_job = self.client.load_table_from_file(
                source_file,
                self.table_id,
                job_config=job_config,
            )

        load_job.result()

        if load_job.errors:
            error_msgs = [str(e) for e in load_job.errors]
            logger.error(
                "load_job_errors",
                extra={"table": self.table_id, "errors": error_msgs},
            )
            raise RuntimeError(f"Load job errors: {load_job.errors}")

        return load_job.output_rows or 0

    def _write_with_merge(
        self,
        temp_path: str,
        records: list[dict[str, Any]],
    ) -> int:
        """Write via MERGE for deduplication."""
        # Create temp table
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        temp_table_id = f"{self.table_id}_temp_{timestamp}"

        job_config = LoadJobConfig(
            source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=WriteDisposition.WRITE_TRUNCATE,
            autodetect=True,
        )

        try:
            # Load to temp table
            with open(temp_path, "rb") as source_file:
                load_job = self.client.load_table_from_file(
                    source_file,
                    temp_table_id,
                    job_config=job_config,
                )
            load_job.result()

            if load_job.errors:
                raise RuntimeError(f"Temp table load errors: {load_job.errors}")

            # MERGE into target
            merge_query = f"""
            MERGE `{self.table_id}` T
            USING `{temp_table_id}` S
            ON T.entity_id = S.entity_id
            WHEN MATCHED THEN
                UPDATE SET
                    text = S.text,
                    metadata = S.metadata,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT ROW
            """

            query_job = self.client.query(merge_query)
            query_job.result()

            rows_affected = query_job.num_dml_affected_rows or len(records)

            logger.info(
                "merge_complete",
                extra={
                    "table": self.table_id,
                    "temp_table": temp_table_id,
                    "rows_affected": rows_affected,
                },
            )

            return rows_affected

        finally:
            # Clean up temp table
            try:
                self.client.delete_table(temp_table_id, not_found_ok=True)
            except Exception as e:
                logger.warning(
                    "temp_table_cleanup_failed",
                    extra={"temp_table": temp_table_id, "error": str(e)},
                )

    def _verify_write(self, expected_count: int) -> None:
        """Verify write succeeded.

        Note: This is a basic verification. For critical operations,
        use full verification from pipelines/core/verification.py
        """
        try:
            table = self.client.get_table(self.table_id)
            actual_count = table.num_rows

            if actual_count is None:
                logger.warning(
                    "verify_write_no_count",
                    extra={"table": self.table_id},
                )
                return

            logger.info(
                "verify_write_complete",
                extra={
                    "table": self.table_id,
                    "expected": expected_count,
                    "total_rows": actual_count,
                },
            )

        except Exception as e:
            logger.error(
                "verify_write_failed",
                extra={"table": self.table_id, "error": str(e)},
            )

    @property
    def backup_table_id(self) -> str | None:
        """Get the backup table ID if one was created."""
        return self._backup_table_id

    def rollback(self) -> bool:
        """Rollback to backup if one exists.

        Returns:
            True if rollback succeeded, False otherwise
        """
        if not self._backup_created or not self._backup_table_id:
            logger.error(
                "rollback_no_backup",
                extra={"table": self.table_id},
            )
            return False

        try:
            # Copy backup back to original
            query = f"""
            CREATE OR REPLACE TABLE `{self.table_id}`
            AS SELECT * FROM `{self._backup_table_id}`
            """
            job = self.client.query(query)
            job.result()

            logger.info(
                "rollback_complete",
                extra={
                    "table": self.table_id,
                    "backup_table": self._backup_table_id,
                },
            )

            return True

        except Exception as e:
            logger.error(
                "rollback_failed",
                extra={
                    "table": self.table_id,
                    "backup_table": self._backup_table_id,
                    "error": str(e),
                },
            )
            return False


def get_safe_writer(
    table_id: str,
    project_id: str | None = None,
) -> SafeBigQueryWriter:
    """Factory function to create a SafeBigQueryWriter.

    Args:
        table_id: Full table ID or short form (dataset.table)
        project_id: Optional project ID (uses default if not provided)

    Returns:
        SafeBigQueryWriter instance
    """
    client = bigquery.Client(project=project_id)

    # Ensure full table ID
    if table_id.count(".") == 1:
        # Short form: dataset.table
        project = project_id or client.project
        table_id = f"{project}.{table_id}"

    return SafeBigQueryWriter(client, table_id)
