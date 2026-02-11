# SYSTEM Contract

## The Sentence

**A SYSTEM reads from JSONL, transforms through a script, and writes to DuckDB.**

---

## The Three Files

Every system consists of exactly three files:

| File | Extension | Purpose |
|------|-----------|---------|
| Input | `.jsonl` | Append-only capture (Hold 1) |
| Bridge | `.py` | Transformation logic (Agent) |
| Output | `.duckdb` | Queryable result (Hold 2) |

---

## Required Structure

```
{system_name}/
├── {name}.jsonl           # Input
├── {name}.py              # System (the bridge)
├── {name}.duckdb          # Output
└── README.md              # Documentation
```

---

## Required Imports

```python
#!/usr/bin/env python3
"""
{System Name} - {Brief description}

The Bridge: {input}.jsonl -> {output}.duckdb
"""
import json
from pathlib import Path

import duckdb

from architect_central_services import (
    get_logger,
    get_current_run_id,
    track_cost,
    write_event,
)

logger = get_logger(__name__)
```

---

## Required Events

| Event | When | Content |
|-------|------|---------|
| `system.started` | Script begins | `{run_id, input_path, output_path}` |
| `system.record_processed` | Each record (optional) | `{record_id}` |
| `system.completed` | Script ends | `{run_id, records_processed, duration}` |
| `system.failed` | On error | `{run_id, error}` |

---

## Template

```python
#!/usr/bin/env python3
"""
{System Name}

The Bridge: {name}.jsonl -> {name}.duckdb -> (optional) BigQuery
"""
import json
import time
from pathlib import Path

import duckdb

from architect_central_services import (
    get_logger,
    get_current_run_id,
    get_bigquery_client,
    track_cost,
    write_event,
)

logger = get_logger(__name__)

# Configuration
SYSTEM_NAME = "{name}"
INPUT_PATH = Path(__file__).parent / f"{SYSTEM_NAME}.jsonl"
OUTPUT_PATH = Path(__file__).parent / f"{SYSTEM_NAME}.duckdb"


def ensure_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create output table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id TEXT PRIMARY KEY,
            content TEXT,
            created_at TIMESTAMP,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def transform(record: dict) -> dict:
    """Transform a single record. The logic lives here."""
    # Your transformation logic
    return {
        "id": record.get("id"),
        "content": record.get("content"),
        "created_at": record.get("created_at"),
    }


def bridge(
    input_path: Path,
    output_path: Path,
    sync_to_cloud: bool = False,
    bigquery_table: str = None,
) -> int:
    """
    The Bridge: JSONL -> DuckDB -> (optional) BigQuery

    Args:
        input_path: Path to .jsonl file
        output_path: Path to .duckdb file
        sync_to_cloud: Whether to sync to BigQuery
        bigquery_table: BigQuery table ID (required if sync_to_cloud=True)

    Returns: Number of records processed
    """
    run_id = get_current_run_id()
    start_time = time.time()

    # Log start
    write_event(
        source=SYSTEM_NAME,
        event_type="system.started",
        content={"run_id": run_id, "input": str(input_path), "output": str(output_path)}
    )

    # Connect to DuckDB
    conn = duckdb.connect(str(output_path))
    ensure_schema(conn)

    # Process input
    records_processed = 0
    all_transformed = []  # For BigQuery sync

    if not input_path.exists():
        logger.warning(f"Input file not found: {input_path}")
        return 0

    with open(input_path, "r") as f:
        for line in f:
            if not line.strip():
                continue

            try:
                record = json.loads(line)
                transformed = transform(record)

                # Upsert to DuckDB (always - free)
                conn.execute("""
                    INSERT OR REPLACE INTO {table_name} (id, content, created_at)
                    VALUES (?, ?, ?)
                """, [transformed["id"], transformed["content"], transformed["created_at"]])

                records_processed += 1

                if sync_to_cloud:
                    all_transformed.append(transformed)

            except Exception as e:
                logger.error(f"Failed to process record: {e}")
                write_event(
                    source=SYSTEM_NAME,
                    event_type="system.record_failed",
                    content={"error": str(e), "line": line[:100]}
                )

    conn.close()

    # Sync to BigQuery (optional - costs money)
    if sync_to_cloud and all_transformed and bigquery_table:
        client = get_bigquery_client()
        job = client.load_table_from_json(all_transformed, bigquery_table)
        job.result()
        logger.info(f"Synced {len(all_transformed)} records to BigQuery")

    # Log completion
    duration = time.time() - start_time
    write_event(
        source=SYSTEM_NAME,
        event_type="system.completed",
        content={
            "run_id": run_id,
            "records_processed": records_processed,
            "synced_to_cloud": sync_to_cloud,
            "duration": duration,
        }
    )

    logger.info(f"Processed {records_processed} records in {duration:.2f}s")
    return records_processed


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="Sync to BigQuery")
    args = parser.parse_args()

    bridge(INPUT_PATH, OUTPUT_PATH, sync_to_cloud=args.sync, bigquery_table="{dataset}.{table}")
```

---

## Checklist

Before considering a SYSTEM complete:

- [ ] Three files exist: `.jsonl`, `.py`, `.duckdb`
- [ ] Script uses central services imports
- [ ] Script writes `system.started` and `system.completed` events
- [ ] Script handles missing input file gracefully
- [ ] Script is idempotent (can run multiple times safely)
- [ ] DuckDB schema is created if not exists
- [ ] README.md documents what the system does
- [ ] Script follows cost protection (no unbounded queries)

---

## Relationship to Other Contracts

| Contract | Relationship |
|----------|--------------|
| SCRIPT | A SYSTEM contains a script; the script IS the bridge |
| PIPELINE_STAGE | A pipeline stage is a SYSTEM with specific naming |
| SERVICE | A service may wrap a SYSTEM to provide an API |

---

## The Recovery Property

A SYSTEM is always recoverable:

1. Delete `.duckdb`
2. Run `.py`
3. Output rebuilt from `.jsonl`

**The JSONL is the source of truth. Everything else derives from it.**

---

*A SYSTEM is three files. JSONL captures. Script transforms. DuckDB queries.*
