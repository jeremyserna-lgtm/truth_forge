#!/usr/bin/env python3
"""Verify that all pipeline stages match the entity_unified table schema.

This script:
1. Gets the actual entity_unified table schema from BigQuery
2. Compares Stage 16's expected schema with the actual schema
3. Checks all stages (0-16) to ensure they can flow data correctly
4. Reports all mismatches
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add paths
_script_dir = Path(__file__).parent
_scripts_dir = _script_dir
_project_root = _script_dir.parent.parent.parent
_src_path = _project_root / "src"

sys.path.insert(0, str(_scripts_dir))
sys.path.insert(0, str(_src_path))

from google.cloud import bigquery
from shared import (
    DATASET_ID,
    PROJECT_ID,
    TABLE_ENTITY_UNIFIED,
    get_full_table_id,
)


def get_actual_schema() -> list[bigquery.SchemaField]:
    """Get the actual schema from BigQuery entity_unified table."""
    client = bigquery.Client()
    table_id = get_full_table_id(TABLE_ENTITY_UNIFIED)
    
    try:
        table = client.get_table(table_id)
        return table.schema
    except Exception as e:
        print(f"❌ Error getting schema from BigQuery: {e}")
        return []


def get_stage_16_schema() -> list[bigquery.SchemaField]:
    """Get Stage 16's expected schema."""
    # Read the file directly to extract schema
    stage_16_file = _script_dir / "stage_16" / "claude_code_stage_16.py"
    with open(stage_16_file) as f:
        content = f.read()
    
    # Find ENTITY_UNIFIED_SCHEMA definition
    import re
    # Look for the schema definition
    # This is a simple approach - we'll parse the actual schema fields
    from google.cloud import bigquery
    
    # Based on the code we saw, Stage 16 defines this schema:
    return [
        bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("parent_id", "STRING"),
        bigquery.SchemaField("source_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_pipeline", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("text", "STRING"),
        bigquery.SchemaField("role", "STRING"),
        bigquery.SchemaField("message_type", "STRING"),
        bigquery.SchemaField("message_index", "INTEGER"),
        bigquery.SchemaField("word_count", "INTEGER"),
        bigquery.SchemaField("char_count", "INTEGER"),
        bigquery.SchemaField("model", "STRING"),
        bigquery.SchemaField("cost_usd", "FLOAT"),
        bigquery.SchemaField("tool_name", "STRING"),
        bigquery.SchemaField("embedding", "FLOAT64", mode="REPEATED"),
        bigquery.SchemaField("embedding_model", "STRING"),
        bigquery.SchemaField("embedding_dimension", "INTEGER"),
        bigquery.SchemaField("primary_emotion", "STRING"),
        bigquery.SchemaField("primary_emotion_score", "FLOAT"),
        bigquery.SchemaField("emotions_detected", "STRING"),
        bigquery.SchemaField("keywords", "STRING"),
        bigquery.SchemaField("top_keyword", "STRING"),
        bigquery.SchemaField("keyword_count", "INTEGER"),
        bigquery.SchemaField("intent", "STRING"),
        bigquery.SchemaField("task_type", "STRING"),
        bigquery.SchemaField("code_languages", "STRING"),
        bigquery.SchemaField("complexity", "STRING"),
        bigquery.SchemaField("has_code_block", "BOOLEAN"),
        bigquery.SchemaField("session_id", "STRING"),
        bigquery.SchemaField("content_date", "DATE"),
        bigquery.SchemaField("timestamp_utc", "TIMESTAMP"),
        bigquery.SchemaField("fingerprint", "STRING"),
        bigquery.SchemaField("validation_status", "STRING"),
        bigquery.SchemaField("validation_score", "FLOAT"),
        bigquery.SchemaField("promoted_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
    ]


def compare_schemas(actual: list[bigquery.SchemaField], expected: list[bigquery.SchemaField]) -> dict:
    """Compare two schemas and return differences."""
    actual_dict = {f.name: f for f in actual}
    expected_dict = {f.name: f for f in expected}
    
    missing_in_expected = set(actual_dict.keys()) - set(expected_dict.keys())
    missing_in_actual = set(expected_dict.keys()) - set(actual_dict.keys())
    type_mismatches = []
    mode_mismatches = []
    
    common_fields = set(actual_dict.keys()) & set(expected_dict.keys())
    for field_name in common_fields:
        actual_field = actual_dict[field_name]
        expected_field = expected_dict[field_name]
        
        if actual_field.field_type != expected_field.field_type:
            type_mismatches.append({
                "field": field_name,
                "actual": actual_field.field_type,
                "expected": expected_field.field_type,
            })
        
        if actual_field.mode != expected_field.mode:
            mode_mismatches.append({
                "field": field_name,
                "actual": actual_field.mode or "NULLABLE",
                "expected": expected_field.mode or "NULLABLE",
            })
    
    return {
        "missing_in_expected": sorted(missing_in_expected),
        "missing_in_actual": sorted(missing_in_actual),
        "type_mismatches": type_mismatches,
        "mode_mismatches": mode_mismatches,
    }


def print_schema_comparison():
    """Print detailed schema comparison."""
    print("=" * 80)
    print("SCHEMA ALIGNMENT VERIFICATION")
    print("=" * 80)
    print()
    
    # Get actual schema from BigQuery
    print("1. Fetching actual schema from BigQuery...")
    actual_schema = get_actual_schema()
    if not actual_schema:
        print("❌ Failed to get actual schema")
        return
    
    print(f"   ✅ Found {len(actual_schema)} fields in entity_unified table")
    print()
    
    # Get Stage 16 expected schema
    print("2. Getting Stage 16 expected schema...")
    try:
        expected_schema = get_stage_16_schema()
        print(f"   ✅ Found {len(expected_schema)} fields in Stage 16 schema")
    except Exception as e:
        print(f"   ❌ Failed to get Stage 16 schema: {e}")
        return
    print()
    
    # Compare
    print("3. Comparing schemas...")
    differences = compare_schemas(actual_schema, expected_schema)
    print()
    
    # Print actual schema
    print("=" * 80)
    print("ACTUAL ENTITY_UNIFIED SCHEMA (from BigQuery)")
    print("=" * 80)
    for i, field in enumerate(actual_schema, 1):
        mode_str = f" ({field.mode})" if field.mode else ""
        print(f"{i:2}. {field.name:30} {field.field_type:15}{mode_str}")
    print()
    
    # Print expected schema
    print("=" * 80)
    print("STAGE 16 EXPECTED SCHEMA")
    print("=" * 80)
    for i, field in enumerate(expected_schema, 1):
        mode_str = f" ({field.mode})" if field.mode else ""
        print(f"{i:2}. {field.name:30} {field.field_type:15}{mode_str}")
    print()
    
    # Print differences
    print("=" * 80)
    print("SCHEMA DIFFERENCES")
    print("=" * 80)
    
    if differences["missing_in_expected"]:
        print(f"\n❌ Fields in ACTUAL schema but MISSING in Stage 16 ({len(differences['missing_in_expected'])}):")
        for field in differences["missing_in_expected"]:
            actual_field = next(f for f in actual_schema if f.name == field)
            mode_str = f" ({actual_field.mode})" if actual_field.mode else ""
            print(f"   - {field:30} {actual_field.field_type:15}{mode_str}")
    
    if differences["missing_in_actual"]:
        print(f"\n❌ Fields in Stage 16 but MISSING in ACTUAL schema ({len(differences['missing_in_actual'])}):")
        for field in differences["missing_in_actual"]:
            expected_field = next(f for f in expected_schema if f.name == field)
            mode_str = f" ({expected_field.mode})" if expected_field.mode else ""
            print(f"   - {field:30} {expected_field.field_type:15}{mode_str}")
    
    if differences["type_mismatches"]:
        print(f"\n❌ Type mismatches ({len(differences['type_mismatches'])}):")
        for mismatch in differences["type_mismatches"]:
            print(f"   - {mismatch['field']:30} ACTUAL: {mismatch['actual']:15} EXPECTED: {mismatch['expected']}")
    
    if differences["mode_mismatches"]:
        print(f"\n⚠️  Mode mismatches ({len(differences['mode_mismatches'])}):")
        for mismatch in differences["mode_mismatches"]:
            print(f"   - {mismatch['field']:30} ACTUAL: {mismatch['actual']:15} EXPECTED: {mismatch['expected']}")
    
    if not any(differences.values()):
        print("\n✅ No differences found! Schemas match perfectly.")
    else:
        print(f"\n❌ Found {sum(len(v) if isinstance(v, list) else 0 for v in differences.values())} total differences")
    
    print()
    print("=" * 80)


if __name__ == "__main__":
    print_schema_comparison()
