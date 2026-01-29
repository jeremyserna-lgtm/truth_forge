#!/usr/bin/env python3
"""Run Stages 1 and 2 to refresh data and ensure no duplicates.

This script runs Stage 1 (Extraction) and Stage 2 (Cleaning) to refresh
the pipeline data and ensure duplicates are properly marked.

Usage:
    python run_stages_1_2.py [--source-dir PATH] [--batch-size N] [--dry-run]
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

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

def clear_stage_tables(client: bigquery.Client) -> None:
    """Clear stage 1 and 2 tables to ensure fresh data."""
    stage_1_table = get_full_table_id(TABLE_STAGE_1)
    stage_2_table = get_full_table_id(TABLE_STAGE_2)
    
    print("Clearing existing data from Stage 1 and Stage 2 tables...")
    
    try:
        # Delete all rows from stage 1
        delete_query_1 = f"DELETE FROM `{stage_1_table}` WHERE TRUE"
        job1 = client.query(delete_query_1)
        job1.result()
        print(f"  ✓ Cleared {stage_1_table}")
    except Exception as e:
        print(f"  ⚠ Could not clear Stage 1: {e}")
    
    try:
        # Delete all rows from stage 2
        delete_query_2 = f"DELETE FROM `{stage_2_table}` WHERE TRUE"
        job2 = client.query(delete_query_2)
        job2.result()
        print(f"  ✓ Cleared {stage_2_table}")
    except Exception as e:
        print(f"  ⚠ Could not clear Stage 2: {e}")

def run_stage_1(source_dir: Path, batch_size: int, dry_run: bool) -> int:
    """Run Stage 1: Extraction."""
    print("\n" + "=" * 80)
    print("RUNNING STAGE 1: EXTRACTION")
    print("=" * 80)
    
    cmd = [
        sys.executable,
        str(scripts_dir / "stage_1" / "claude_code_stage_1.py"),
        "--source-dir", str(source_dir),
        "--batch-size", str(batch_size),
    ]
    
    if dry_run:
        cmd.append("--dry-run")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode

def run_stage_2(batch_size: int, dry_run: bool) -> int:
    """Run Stage 2: Cleaning."""
    print("\n" + "=" * 80)
    print("RUNNING STAGE 2: CLEANING")
    print("=" * 80)
    
    cmd = [
        sys.executable,
        str(scripts_dir / "stage_2" / "claude_code_stage_2.py"),
        "--batch-size", str(batch_size),
    ]
    
    if dry_run:
        cmd.append("--dry-run")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode

def check_duplicates(client: bigquery.Client) -> None:
    """Check for duplicates in Stage 2."""
    stage_2_table = get_full_table_id(TABLE_STAGE_2)
    
    print("\n" + "=" * 80)
    print("CHECKING FOR DUPLICATES")
    print("=" * 80)
    
    query = f"""
    SELECT
        COUNT(*) as total_rows,
        COUNTIF(is_duplicate = TRUE) as duplicate_count,
        COUNTIF(is_duplicate = FALSE OR is_duplicate IS NULL) as unique_count
    FROM `{stage_2_table}`
    """
    
    try:
        result = list(client.query(query).result())[0]
        print(f"Total rows: {result.total_rows:,}")
        print(f"Unique rows: {result.unique_count:,}")
        print(f"Duplicate rows: {result.duplicate_count:,}")
        
        if result.duplicate_count > 0:
            print(f"\n⚠️  WARNING: {result.duplicate_count:,} duplicate rows found!")
            print("   Duplicates are marked with is_duplicate=TRUE")
            print("   Stage 3 will filter these out (WHERE NOT is_duplicate)")
        else:
            print("\n✅ No duplicates found - all rows are unique!")
    except Exception as e:
        print(f"❌ Error checking duplicates: {e}")

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Stages 1 and 2 to refresh data and ensure no duplicates"
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path.home() / ".claude" / "projects",
        help="Source directory for JSONL files",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for processing",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (don't write to BigQuery)",
    )
    parser.add_argument(
        "--clear-first",
        action="store_true",
        help="Clear existing data from Stage 1 and 2 tables before running",
    )
    
    args = parser.parse_args()
    
    # Get BigQuery client
    client = bigquery.Client(project=PROJECT_ID)
    
    # Clear tables if requested
    if args.clear_first and not args.dry_run:
        clear_stage_tables(client)
    
    # Run Stage 1
    stage_1_result = run_stage_1(args.source_dir, args.batch_size, args.dry_run)
    if stage_1_result != 0:
        print(f"\n❌ Stage 1 failed with exit code {stage_1_result}")
        return stage_1_result
    
    # Run Stage 2
    stage_2_result = run_stage_2(args.batch_size, args.dry_run)
    if stage_2_result != 0:
        print(f"\n❌ Stage 2 failed with exit code {stage_2_result}")
        return stage_2_result
    
    # Check for duplicates
    if not args.dry_run:
        check_duplicates(client)
    
    print("\n" + "=" * 80)
    print("✅ STAGES 1 AND 2 COMPLETE")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
