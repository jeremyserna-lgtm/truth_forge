"""BigQuery Export API Endpoint

This serverless function handles direct export of validated entities to BigQuery.
It follows the DATA PROTECTION LAWS established in the truth_forge project.

Per DATA PROTECTION LAWS:
- Uses batch load (never streaming)
- Creates backup before write
- Validates schema alignment
- Reports all errors

Author: Claude (Opus 4.5)
Date: 2026-02-02
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Target table
TABLE_ID = "flash-clover-464719-g1.spine.entity_unified"


def validate_entity(entity: dict[str, Any], index: int) -> list[str]:
    """Validate a single entity against the schema.

    Returns list of error messages (empty if valid).
    """
    errors = []

    # Required fields
    required_fields = [
        "entity_id", "level", "entity_type", "entity_mode",
        "conversation_id", "text", "source_pipeline", "source_system",
        "content_date", "created_at", "updated_at", "ingestion_timestamp",
        "ingestion_job_id", "validation_status"
    ]

    for field in required_fields:
        if field not in entity or entity[field] is None:
            errors.append(f"Entity {index}: Missing required field '{field}'")

    # Validate level
    if "level" in entity:
        level = entity["level"]
        if level not in [2, 3, 4, 5, 6, 7, 8]:
            errors.append(f"Entity {index}: Invalid level {level} (must be 2-8)")

    # Validate entity_id format
    if "entity_id" in entity:
        entity_id = entity["entity_id"]
        if not isinstance(entity_id, str) or ":" not in entity_id:
            errors.append(f"Entity {index}: Invalid entity_id format '{entity_id}'")

    # Validate validation_status
    if "validation_status" in entity:
        status = entity["validation_status"]
        if status not in ["PASSED", "WARNING", "FAILED"]:
            errors.append(f"Entity {index}: Invalid validation_status '{status}'")

    # Validate parent_id for non-L8 entities
    if "level" in entity and entity["level"] < 8:
        if "parent_id" not in entity or entity["parent_id"] is None:
            errors.append(f"Entity {index}: Non-L8 entity missing parent_id")

    return errors


def validate_batch(entities: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Validate a batch of entities.

    Returns (is_valid, error_messages).
    """
    all_errors = []

    for i, entity in enumerate(entities):
        errors = validate_entity(entity, i)
        all_errors.extend(errors)

    # Check for duplicate entity_ids
    entity_ids = [e.get("entity_id") for e in entities if e.get("entity_id")]
    duplicates = set([x for x in entity_ids if entity_ids.count(x) > 1])
    if duplicates:
        all_errors.append(f"Duplicate entity_ids found: {list(duplicates)[:5]}...")

    return len(all_errors) == 0, all_errors


def write_to_bigquery(entities: list[dict[str, Any]]) -> dict[str, Any]:
    """Write entities to BigQuery using batch load.

    Returns result dict with success status and details.
    """
    try:
        from google.cloud import bigquery
        from google.cloud.bigquery import (
            LoadJobConfig,
            SourceFormat,
            WriteDisposition,
            CreateDisposition,
        )
    except ImportError:
        return {
            "success": False,
            "error": "google-cloud-bigquery not installed",
            "rows_written": 0,
        }

    try:
        client = bigquery.Client()

        # Create backup first (DATA PROTECTION LAWS)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_table_id = f"{TABLE_ID}_backup_{timestamp}"

        backup_query = f"""
        CREATE TABLE `{backup_table_id}`
        OPTIONS (expiration_timestamp = TIMESTAMP_ADD(CURRENT_TIMESTAMP(), INTERVAL 7 DAY))
        AS SELECT * FROM `{TABLE_ID}`
        """

        logger.info(f"Creating backup: {backup_table_id}")
        backup_job = client.query(backup_query)
        backup_job.result()

        # Verify backup
        backup_table = client.get_table(backup_table_id)
        backup_rows = backup_table.num_rows
        logger.info(f"Backup created with {backup_rows} rows")

        # Write entities to temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ndjson",
            delete=False,
            prefix="bq_export_",
        ) as f:
            for entity in entities:
                # Convert metadata dict to JSON string
                entity_copy = entity.copy()
                if isinstance(entity_copy.get("metadata"), dict):
                    entity_copy["metadata"] = json.dumps(entity_copy["metadata"])
                f.write(json.dumps(entity_copy) + "\n")
            temp_path = f.name

        # Configure batch load job
        job_config = LoadJobConfig(
            source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=WriteDisposition.WRITE_APPEND,
            create_disposition=CreateDisposition.CREATE_NEVER,
        )

        # Execute batch load
        with open(temp_path, "rb") as source_file:
            load_job = client.load_table_from_file(
                source_file,
                TABLE_ID,
                job_config=job_config,
            )

        load_job.result()

        if load_job.errors:
            return {
                "success": False,
                "error": f"Load job errors: {load_job.errors}",
                "rows_written": 0,
                "backup_table": backup_table_id,
            }

        rows_written = load_job.output_rows or len(entities)

        # Cleanup temp file
        try:
            os.unlink(temp_path)
        except Exception:
            pass

        return {
            "success": True,
            "rows_written": rows_written,
            "backup_table": backup_table_id,
            "backup_rows": backup_rows,
            "table": TABLE_ID,
        }

    except Exception as e:
        logger.error(f"BigQuery write failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "rows_written": 0,
        }


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        """Handle POST request to export entities."""
        # CORS headers
        self.send_header("Access-Control-Allow-Origin", "*")

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))

            entities = data.get("entities", [])
            dry_run = data.get("dry_run", False)

            if not entities:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "No entities provided",
                }).encode())
                return

            logger.info(f"Received {len(entities)} entities (dry_run={dry_run})")

            # Validate batch
            is_valid, errors = validate_batch(entities)

            if not is_valid:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Validation failed",
                    "validation_errors": errors[:20],  # Limit error count
                    "total_errors": len(errors),
                }).encode())
                return

            # If dry run, just return validation success
            if dry_run:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "dry_run": True,
                    "validated_entities": len(entities),
                    "message": "Validation passed. Ready for export.",
                }).encode())
                return

            # Write to BigQuery
            result = write_to_bigquery(entities)

            if result["success"]:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())

        except json.JSONDecodeError as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": f"Invalid JSON: {e}",
            }).encode())

        except Exception as e:
            logger.error(f"Handler error: {e}")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": False,
                "error": f"Server error: {e}",
            }).encode())
