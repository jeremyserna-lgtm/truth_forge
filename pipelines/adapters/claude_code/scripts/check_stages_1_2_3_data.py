#!/usr/bin/env python3
"""Check data in Stages 1, 2, and 3 tables.

Shows row counts, sample data, and run_id distribution.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from google.cloud import bigquery
from shared import (
    TABLE_STAGE_1,
    TABLE_STAGE_2,
    TABLE_STAGE_3,
    get_full_table_id,
)

def get_bigquery_client():
    """Get BigQuery client."""
    return bigquery.Client()

def check_table_data(client: bigquery.Client, table_id: str, stage_name: str) -> None:
    """Check data in a table."""
    print(f"\n{'=' * 80}")
    print(f"STAGE {stage_name}: {table_id}")
    print("=" * 80)
    
    # Check if table exists
    try:
        table = client.get_table(table_id)
        print(f"✅ Table exists")
        print(f"   Schema: {len(table.schema)} fields")
        print(f"   Created: {table.created}")
        print(f"   Modified: {table.modified}")
    except Exception as e:
        print(f"❌ Table does not exist: {e}")
        return
    
    # Get row count
    count_query = f"SELECT COUNT(*) as cnt FROM `{table_id}`"
    try:
        result = client.query(count_query).result()
        row = next(iter(result))
        total_rows = row.cnt
        print(f"   Total rows: {total_rows:,}")
    except Exception as e:
        print(f"❌ Error counting rows: {e}")
        return
    
    if total_rows == 0:
        print("   ⚠️  Table is empty")
        return
    
    # Get run_id distribution
    run_id_query = f"""
    SELECT 
        run_id,
        COUNT(*) as row_count,
        MIN(extracted_at) as first_extracted,
        MAX(extracted_at) as last_extracted
    FROM `{table_id}`
    GROUP BY run_id
    ORDER BY first_extracted DESC
    LIMIT 10
    """
    
    try:
        result = client.query(run_id_query).result()
        run_ids = list(result)
        print(f"\n   Run IDs (top 10):")
        for r in run_ids:
            print(f"      - {r.run_id}: {r.row_count:,} rows (from {r.first_extracted} to {r.last_extracted})")
    except Exception as e:
        print(f"   ⚠️  Could not get run_id distribution: {e}")
    
    # Get sample data
    sample_query = f"""
    SELECT *
    FROM `{table_id}`
    ORDER BY extracted_at DESC
    LIMIT 3
    """
    
    try:
        result = client.query(sample_query).result()
        samples = list(result)
        if samples:
            print(f"\n   Sample rows (most recent 3):")
            for i, row in enumerate(samples, 1):
                row_dict = dict(row)
                # Show key fields
                key_fields = {}
                for field in ['extraction_id', 'session_id', 'message_index', 'fingerprint', 'run_id', 'extracted_at']:
                    if field in row_dict:
                        key_fields[field] = row_dict[field]
                print(f"      Row {i}: {key_fields}")
    except Exception as e:
        print(f"   ⚠️  Could not get sample data: {e}")

def main():
    """Main execution."""
    client = get_bigquery_client()
    
    stage_1_table = get_full_table_id(TABLE_STAGE_1)
    stage_2_table = get_full_table_id(TABLE_STAGE_2)
    stage_3_table = get_full_table_id(TABLE_STAGE_3)
    
    print("=" * 80)
    print("STAGES 1, 2, 3 DATA ASSESSMENT")
    print("=" * 80)
    
    check_table_data(client, stage_1_table, "1 (Extraction)")
    check_table_data(client, stage_2_table, "2 (Cleaning)")
    check_table_data(client, stage_3_table, "3 (Identity Generation)")
    
    print(f"\n{'=' * 80}")
    print("ASSESSMENT COMPLETE")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
