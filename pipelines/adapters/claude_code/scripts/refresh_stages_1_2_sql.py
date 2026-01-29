#!/usr/bin/env python3
"""Refresh Stages 1 and 2 using direct BigQuery SQL.

This script refreshes Stage 2 data from Stage 1, ensuring duplicates are marked.
Since Stage 1 uses INSERT (which may create duplicates), we refresh Stage 2
which uses CREATE OR REPLACE and marks duplicates properly.

Usage:
    python refresh_stages_1_2_sql.py [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path
from datetime import UTC, datetime

# Add paths
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from google.cloud import bigquery
from shared.constants import (
    PROJECT_ID,
    DATASET_ID,
    TABLE_STAGE_1,
    TABLE_STAGE_2,
    get_full_table_id,
)

def refresh_stage_2(client: bigquery.Client, dry_run: bool = False) -> dict:
    """Refresh Stage 2 by reprocessing Stage 1 data with duplicate marking."""
    stage_1_table = get_full_table_id(TABLE_STAGE_1)
    stage_2_table = get_full_table_id(TABLE_STAGE_2)
    
    cleaned_at = datetime.now(UTC).isoformat()
    
    # Get current run_id from Stage 1 (use most recent)
    run_id_query = f"""
    SELECT run_id
    FROM `{stage_1_table}`
    ORDER BY extracted_at DESC
    LIMIT 1
    """
    
    try:
        run_id_result = list(client.query(run_id_query).result())
        if run_id_result:
            run_id = run_id_result[0].run_id
        else:
            run_id = f"run_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    except Exception:
        run_id = f"run_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    
    # SQL-based cleaning transformation (same as Stage 2)
    cleaning_query = f"""
    CREATE OR REPLACE TABLE `{stage_2_table}` AS
    WITH cleaned AS (
        SELECT
            extraction_id,
            session_id,
            message_index,
            message_type,
            role,
            content,
            -- Clean content
            TRIM(REGEXP_REPLACE(content, r'\\s+', ' ')) AS content_cleaned,
            LENGTH(TRIM(REGEXP_REPLACE(content, r'\\s+', ' '))) AS content_length,
            ARRAY_LENGTH(SPLIT(TRIM(REGEXP_REPLACE(content, r'\\s+', ' ')), ' ')) AS word_count,
            timestamp,
            -- Normalize to UTC
            timestamp AS timestamp_utc,
            model,
            cost_usd,
            tool_name,
            tool_input,
            tool_output,
            source_file,
            content_date,
            fingerprint,
            -- Mark duplicates (same fingerprint = duplicate)
            ROW_NUMBER() OVER (PARTITION BY fingerprint ORDER BY extracted_at) > 1 AS is_duplicate,
            extracted_at,
            TIMESTAMP('{cleaned_at}') AS cleaned_at,
            '{run_id}' AS run_id
        FROM `{stage_1_table}`
    )
    SELECT * FROM cleaned
    """
    
    if dry_run:
        # Count what would be processed
        count_query = f"SELECT COUNT(*) as cnt FROM `{stage_1_table}`"
        result = client.query(count_query).result()
        row = next(iter(result))
        return {
            "input_rows": row.cnt,
            "output_rows": row.cnt,
            "dry_run": True,
        }
    
    print(f"Refreshing Stage 2 from Stage 1...")
    print(f"  Source: {stage_1_table}")
    print(f"  Target: {stage_2_table}")
    print(f"  Run ID: {run_id}")
    
    # Execute cleaning
    job = client.query(cleaning_query)
    job.result()  # Wait for completion
    
    # Get statistics
    stats_query = f"""
    SELECT
        COUNT(*) as total_rows,
        COUNTIF(is_duplicate = TRUE) as duplicate_count,
        COUNTIF(is_duplicate = FALSE OR is_duplicate IS NULL) as unique_count
    FROM `{stage_2_table}`
    """
    result = client.query(stats_query).result()
    row = next(iter(result))
    
    return {
        "input_rows": row.total_rows,
        "output_rows": row.total_rows,
        "duplicates": row.duplicate_count,
        "unique": row.unique_count,
        "dry_run": False,
    }

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Refresh Stage 2 data from Stage 1 with duplicate marking"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without writing",
    )
    
    args = parser.parse_args()
    
    # Get BigQuery client
    client = bigquery.Client(project=PROJECT_ID)
    
    print("=" * 80)
    print("REFRESHING STAGE 2 DATA")
    print("=" * 80)
    print()
    
    # Check Stage 1 data
    stage_1_table = get_full_table_id(TABLE_STAGE_1)
    count_query = f"SELECT COUNT(*) as cnt FROM `{stage_1_table}`"
    try:
        count_result = list(client.query(count_query).result())[0]
        print(f"Stage 1 has {count_result.cnt:,} rows")
    except Exception as e:
        print(f"❌ Error checking Stage 1: {e}")
        return 1
    
    if count_result.cnt == 0:
        print("⚠️  Stage 1 is empty - nothing to refresh!")
        print("   Run Stage 1 first to extract data from JSONL files")
        return 1
    
    # Refresh Stage 2
    stats = refresh_stage_2(client, args.dry_run)
    
    print()
    print("=" * 80)
    if args.dry_run:
        print("DRY RUN RESULTS")
    else:
        print("STAGE 2 REFRESH COMPLETE")
    print("=" * 80)
    print(f"Input rows: {stats['input_rows']:,}")
    print(f"Output rows: {stats['output_rows']:,}")
    print(f"Unique rows: {stats.get('unique', stats['output_rows']):,}")
    print(f"Duplicate rows: {stats.get('duplicates', 0):,}")
    
    if stats.get('duplicates', 0) > 0:
        print()
        print(f"⚠️  WARNING: {stats['duplicates']:,} duplicate rows found!")
        print("   Duplicates are marked with is_duplicate=TRUE")
        print("   Stage 3 will filter these out (WHERE NOT is_duplicate)")
    else:
        print()
        print("✅ No duplicates found - all rows are unique!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
