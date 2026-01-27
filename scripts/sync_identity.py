"""Syncs the local identity registry to BigQuery."""

from __future__ import annotations

import json
import logging

from google.cloud import bigquery

from truth_forge.core.paths import get_intake_file


def sync_identity_to_bigquery(dry_run: bool = False, batch_size: int = 1000) -> int:
    """Sync local JSONL registry to BigQuery (sync layer)."""
    logger = logging.getLogger(__name__)

    jsonl_path = get_intake_file("identity")

    if not jsonl_path.exists():
        logger.info("No local registry file to sync")
        return 0

    records = []
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line.strip())
                records.append(record)
            except json.JSONDecodeError:
                continue

    if not records:
        logger.info("No records to sync")
        return 0

    logger.info(f"Found {len(records):,} records to sync from {jsonl_path}")

    if dry_run:
        logger.info(f"[DRY RUN] Would sync {len(records):,} records to BigQuery")
        return len(records)

    PROJECT_ID = "flash-clover-464719-g1"
    DATASET_ID = "identity"
    TABLE_ID = "id_registry"
    TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    client = bigquery.Client(project=PROJECT_ID)

    synced = 0
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        # ... (rest of the BigQuery sync logic) ...

    logger.info(f"Synced {synced:,} records to BigQuery")
    return synced


if __name__ == "__main__":
    # Add basic CLI to run the sync
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    sync_identity_to_bigquery(dry_run=args.dry_run)
