#!/usr/bin/env python3
"""Diagnose Stage 4 Data Loss

This script investigates why Stage 4 has only 8 rows when Stage 3 has 226,972 rows.

Usage:
    python diagnose_stage_4_data_loss.py
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
from shared.constants import (
    PROJECT_ID,
    DATASET_ID,
    TABLE_STAGE_3,
    TABLE_STAGE_4,
    get_full_table_id,
)

def diagnose_data_loss():
    """Diagnose why Stage 4 has so few rows."""
    client = bigquery.Client(project=PROJECT_ID)
    
    stage_3_table = get_full_table_id(TABLE_STAGE_3)
    stage_4_table = get_full_table_id(TABLE_STAGE_4)
    
    print("=" * 80)
    print("STAGE 4 DATA LOSS DIAGNOSIS")
    print("=" * 80)
    print()
    
    # Check if tables exist
    try:
        stage_3 = client.get_table(stage_3_table)
        print(f"✅ Stage 3 table exists: {stage_3_table}")
        print(f"   Total rows: {stage_3.num_rows:,}")
    except Exception as e:
        print(f"❌ Stage 3 table not found: {e}")
        return
    
    try:
        stage_4 = client.get_table(stage_4_table)
        print(f"✅ Stage 4 table exists: {stage_4_table}")
        print(f"   Total rows: {stage_4.num_rows:,}")
    except Exception as e:
        print(f"❌ Stage 4 table not found: {e}")
        return
    
    print()
    print("-" * 80)
    print("ANALYSIS")
    print("-" * 80)
    print()
    
    # Check run_id distribution in stage 3
    print("1. Checking run_id distribution in Stage 3:")
    query = f"""
    SELECT 
        run_id,
        COUNT(*) as count
    FROM `{stage_3_table}`
    GROUP BY run_id
    ORDER BY count DESC
    LIMIT 10
    """
    results = list(client.query(query).result())
    print(f"   Found {len(results)} different run_ids in Stage 3:")
    for row in results:
        print(f"     run_id: {row.run_id} - {row.count:,} rows")
    
    print()
    
    # Check run_id distribution in stage 4
    print("2. Checking run_id distribution in Stage 4:")
    query = f"""
    SELECT 
        run_id,
        COUNT(*) as count
    FROM `{stage_4_table}`
    GROUP BY run_id
    ORDER BY count DESC
    LIMIT 10
    """
    results = list(client.query(query).result())
    print(f"   Found {len(results)} different run_ids in Stage 4:")
    for row in results:
        print(f"     run_id: {row.run_id} - {row.count:,} rows")
    
    print()
    
    # Check schema compatibility
    print("3. Checking schema compatibility:")
    stage_3_schema = {field.name: field.field_type for field in stage_3.schema}
    stage_4_schema = {field.name: field.field_type for field in stage_4.schema}
    
    # Check if required fields exist in stage 3
    required_fields = [
        "entity_id", "content_cleaned", "session_id", "message_index",
        "message_type", "role", "content_length", "word_count"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in stage_3_schema:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   ⚠️  Missing fields in Stage 3: {', '.join(missing_fields)}")
        print("   This could cause data loss if Stage 4 queries these fields")
    else:
        print("   ✅ All required fields exist in Stage 3")
    
    print()
    
    # Check for NULL values in critical fields
    print("4. Checking for NULL values in Stage 3 critical fields:")
    query = f"""
    SELECT 
        COUNT(*) as total,
        COUNTIF(entity_id IS NULL) as null_entity_id,
        COUNTIF(content_cleaned IS NULL) as null_content,
        COUNTIF(session_id IS NULL) as null_session_id,
        COUNTIF(message_index IS NULL) as null_message_index
    FROM `{stage_3_table}`
    """
    result = list(client.query(query).result())[0]
    print(f"   Total rows: {result.total:,}")
    print(f"   NULL entity_id: {result.null_entity_id:,}")
    print(f"   NULL content_cleaned: {result.null_content:,}")
    print(f"   NULL session_id: {result.null_session_id:,}")
    print(f"   NULL message_index: {result.null_message_index:,}")
    
    print()
    
    # Check what's actually in stage 4
    print("5. Sample of Stage 4 data:")
    query = f"""
    SELECT 
        entity_id,
        run_id,
        session_id,
        message_index,
        LENGTH(text) as text_length
    FROM `{stage_4_table}`
    LIMIT 10
    """
    results = list(client.query(query).result())
    if results:
        print(f"   Sample rows:")
        for row in results:
            print(f"     entity_id: {row.entity_id[:20]}... run_id: {row.run_id} session: {row.session_id} idx: {row.message_index} text_len: {row.text_length}")
    else:
        print("   No rows found in Stage 4")
    
    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("Based on the analysis above:")
    print("1. If Stage 4 was run with a different run_id, it would have replaced")
    print("   all previous data (CREATE OR REPLACE TABLE)")
    print("2. Check if Stage 4 needs to filter by run_id when reading from Stage 3")
    print("3. Verify that Stage 4 query can access all required fields from Stage 3")
    print("4. Consider running Stage 4 again with the correct run_id filter")


if __name__ == "__main__":
    diagnose_data_loss()
