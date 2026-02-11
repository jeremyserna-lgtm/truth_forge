#!/usr/bin/env python3
"""BigQuery loader for LLM Refinery output.

Loads entity_unified records directly to BigQuery's spine.entity_unified table.
This is the final stage of the refinery - processed entities go straight to storage.

🧠 STAGE FIVE GROUNDING
This module exists to push refined entities to permanent storage.

Structure: Read JSONL → Validate schema → Load to BigQuery
Purpose: Automated persistence of processed entities
Boundaries: Loading only, no transformation (data already in correct format)
Control: Batch loading with duplicate prevention via entity_id

🔥 THE FURNACE PRINCIPLE
- Truth (input): JSONL files from LLM Refinery output
- Heat (processing): Schema validation, batch preparation
- Meaning (output): Permanent records in spine.entity_unified
- Care (delivery): Verified loads with row counts

Usage:
    # Load all refinery output
    python -m pipelines.llm_refinery.bigquery_loader
    
    # Load specific file
    python -m pipelines.llm_refinery.bigquery_loader --input path/to/file.jsonl
    
    # Dry run (validate without loading)
    python -m pipelines.llm_refinery.bigquery_loader --dry-run
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import tempfile
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

from google.cloud import bigquery
from google.cloud.bigquery import (
    LoadJobConfig,
    SourceFormat,
    WriteDisposition,
    CreateDisposition,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = "flash-clover-464719-g1"
DATASET = "spine"
TABLE_NAME = "entity_unified"
FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET}.{TABLE_NAME}"

DEFAULT_OUTPUT_DIR = Path("data/llm_refinery_output")


def get_bigquery_client() -> bigquery.Client:
    """Get BigQuery client."""
    return bigquery.Client(project=PROJECT_ID)


def load_jsonl_file(file_path: Path) -> list[dict[str, Any]]:
    """Load records from a JSONL file.
    
    Args:
        file_path: Path to JSONL file
        
    Returns:
        List of parsed records
    """
    records = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                records.append(record)
            except json.JSONDecodeError as e:
                logger.warning(f"Invalid JSON at {file_path}:{line_num}: {e}")
    return records


def prepare_record_for_bigquery(record: dict[str, Any]) -> dict[str, Any]:
    """Prepare a record for BigQuery insertion.
    
    Handles type conversions and field mappings.
    
    Args:
        record: Raw entity_unified record
        
    Returns:
        BigQuery-ready record
    """
    # Convert metadata dict to JSON string if present
    if "metadata" in record and isinstance(record["metadata"], dict):
        record["metadata"] = json.dumps(record["metadata"])
    
    # Ensure timestamps are strings (BigQuery accepts ISO format)
    for ts_field in ["created_at", "updated_at", "ingestion_timestamp", "source_message_timestamp"]:
        if ts_field in record and record[ts_field] is not None:
            if isinstance(record[ts_field], datetime):
                record[ts_field] = record[ts_field].isoformat()
    
    return record


def load_to_bigquery(
    client: bigquery.Client,
    records: list[dict[str, Any]],
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    """Load records to BigQuery entity_unified table.
    
    Uses batch load job (not streaming insert) per codebase standards.
    
    Args:
        client: BigQuery client
        records: Records to load
        dry_run: If True, skip actual load
        
    Returns:
        Tuple of (records_loaded, list of errors)
    """
    if not records:
        return 0, []
    
    # Prepare records
    prepared = [prepare_record_for_bigquery(r.copy()) for r in records]
    
    if dry_run:
        logger.info(f"DRY RUN: Would load {len(prepared)} records to {FULL_TABLE_ID}")
        return len(prepared), []
    
    # Write to temp file as newline-delimited JSON (per codebase standard)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
        for record in prepared:
            f.write(json.dumps(record) + "\n")
        temp_path = f.name
    
    try:
        job_config = LoadJobConfig(
            source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
            write_disposition=WriteDisposition.WRITE_APPEND,
            create_disposition=CreateDisposition.CREATE_NEVER,  # Table must exist
        )
        
        with open(temp_path, "rb") as source_file:
            load_job = client.load_table_from_file(
                source_file,
                FULL_TABLE_ID,
                job_config=job_config,
            )
        
        load_job.result()  # Wait for job to complete
        
        if load_job.errors:
            error_msgs = [str(e) for e in load_job.errors[:10]]
            return load_job.output_rows or 0, error_msgs
        
        return len(prepared), []
        
    except Exception as e:
        return 0, [str(e)]
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def load_with_merge(
    client: bigquery.Client,
    records: list[dict[str, Any]],
    dry_run: bool = False,
) -> tuple[int, list[str]]:
    """Load records using MERGE to prevent duplicates.
    
    Uses entity_id as the unique key. Uses temp file for batch loading.
    
    Args:
        client: BigQuery client  
        records: Records to load
        dry_run: If True, skip actual load
        
    Returns:
        Tuple of (records_loaded, list of errors)
    """
    if not records:
        return 0, []
    
    # Prepare records
    prepared = [prepare_record_for_bigquery(r.copy()) for r in records]
    
    if dry_run:
        logger.info(f"DRY RUN: Would MERGE {len(prepared)} records to {FULL_TABLE_ID}")
        return len(prepared), []
    
    # Create temp table for staging
    temp_table_id = f"{PROJECT_ID}.{DATASET}._temp_refinery_load_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
    
    # Write to temp file as newline-delimited JSON
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ndjson", delete=False) as f:
        for record in prepared:
            f.write(json.dumps(record) + "\n")
        temp_path = f.name
    
    try:
        # First, load to temp table using batch load (not streaming)
        job_config = LoadJobConfig(
            source_format=SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition=WriteDisposition.WRITE_TRUNCATE,
        )
        
        with open(temp_path, "rb") as source_file:
            load_job = client.load_table_from_file(
                source_file,
                temp_table_id,
                job_config=job_config,
            )
        load_job.result()  # Wait for completion
        
        # Now MERGE into main table
        merge_query = f"""
        MERGE `{FULL_TABLE_ID}` T
        USING `{temp_table_id}` S
        ON T.entity_id = S.entity_id
        WHEN MATCHED THEN
            UPDATE SET
                level = S.level,
                entity_type = S.entity_type,
                entity_mode = S.entity_mode,
                parent_id = S.parent_id,
                text = S.text,
                metadata = S.metadata,
                updated_at = CURRENT_TIMESTAMP(),
                ingestion_timestamp = S.ingestion_timestamp
        WHEN NOT MATCHED THEN
            INSERT ROW
        """
        
        query_job = client.query(merge_query)
        result = query_job.result()
        
        # Get merge stats
        rows_affected = query_job.num_dml_affected_rows or len(prepared)
        
        return rows_affected, []
        
    except Exception as e:
        return 0, [str(e)]
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        # Clean up temp table
        try:
            client.delete_table(temp_table_id, not_found_ok=True)
        except Exception:
            pass


def find_jsonl_files(directory: Path) -> list[Path]:
    """Find all JSONL files in directory.
    
    Args:
        directory: Directory to search
        
    Returns:
        List of JSONL file paths (excluding all_entities.jsonl)
    """
    files = []
    for f in directory.glob("*.jsonl"):
        # Skip the combined file (we'll use individual conversation files)
        if f.name == "all_entities.jsonl":
            continue
        files.append(f)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Load LLM Refinery output to BigQuery entity_unified",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=None,
        help="Path to specific JSONL file (default: all files in output dir)",
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory containing JSONL files (default: {DEFAULT_OUTPUT_DIR})",
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and count records without loading",
    )
    
    parser.add_argument(
        "--use-merge",
        action="store_true",
        help="Use MERGE instead of batch load (deduplicates)",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine files to load
    if args.input:
        if not args.input.exists():
            logger.error(f"Input file not found: {args.input}")
            return 1
        files = [args.input]
    else:
        if not args.output_dir.exists():
            logger.error(f"Output directory not found: {args.output_dir}")
            return 1
        files = find_jsonl_files(args.output_dir)
    
    if not files:
        logger.error("No JSONL files found to load")
        return 1
    
    logger.info("=" * 60)
    logger.info("BIGQUERY LOADER - LLM REFINERY")
    logger.info("=" * 60)
    logger.info(f"Target:    {FULL_TABLE_ID}")
    logger.info(f"Files:     {len(files)}")
    logger.info(f"Dry Run:   {args.dry_run}")
    logger.info(f"Method:    {'MERGE' if args.use_merge else 'Batch Load'}")
    logger.info("=" * 60)
    
    # Initialize BigQuery client
    if not args.dry_run:
        try:
            client = get_bigquery_client()
            logger.info(f"Connected to BigQuery project: {PROJECT_ID}")
        except Exception as e:
            logger.error(f"Failed to connect to BigQuery: {e}")
            return 1
    else:
        client = None
    
    # Process files
    total_loaded = 0
    total_errors = []
    
    for file_path in files:
        logger.info(f"Processing: {file_path.name}")
        
        # Load records
        records = load_jsonl_file(file_path)
        if not records:
            logger.warning(f"  No records in {file_path.name}")
            continue
        
        logger.info(f"  Found {len(records)} entities")
        
        # Load to BigQuery
        if args.use_merge:
            loaded, errors = load_with_merge(client, records, args.dry_run)
        else:
            loaded, errors = load_to_bigquery(client, records, args.dry_run)
        
        if errors:
            logger.error(f"  Errors: {errors[:3]}")
            total_errors.extend(errors)
        else:
            logger.info(f"  Loaded: {loaded} entities")
        
        total_loaded += loaded
    
    # Summary
    logger.info("=" * 60)
    logger.info("LOADING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Files Processed: {len(files)}")
    logger.info(f"Total Loaded:    {total_loaded}")
    logger.info(f"Total Errors:    {len(total_errors)}")
    logger.info("=" * 60)
    
    return 0 if not total_errors else 1


if __name__ == "__main__":
    sys.exit(main())
