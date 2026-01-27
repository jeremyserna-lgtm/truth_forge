#!/usr/bin/env python3
"""
Simple Status Checker - For Non-Coders

Run this anytime to see if your pipeline is working.
It checks BigQuery to see if data is actually there.

Usage:
    python check_status.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Add scripts directory to path
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

try:
    from google.cloud import bigquery
    from shared.constants import (
        PROJECT_ID,
        DATASET_ID,
        get_stage_table,
        TABLE_ENTITY_UNIFIED,
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and dependencies are installed.")
    sys.exit(1)


def check_stage(stage_num: int, table_name: str) -> tuple[bool, int]:
    """Check if a stage has data in BigQuery.
    
    Args:
        stage_num: Stage number (1-16)
        table_name: Table name (without project.dataset prefix)
    
    Returns:
        Tuple of (has_data: bool, row_count: int)
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        full_table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        query = f"SELECT COUNT(*) as c FROM `{full_table_id}`"
        result = list(client.query(query).result())
        count = result[0].c if result else 0
        return count > 0, count
    except Exception as e:
        # Table might not exist yet - that's OK
        return False, 0


def check_manifest() -> tuple[bool, Path]:
    """Check if discovery manifest exists.
    
    Returns:
        Tuple of (exists: bool, path: Path)
    """
    # Manifest path: pipelines/claude_code/staging/discovery_manifest.json
    # Relative to project root
    scripts_dir = Path(__file__).resolve().parent
    pipeline_dir = scripts_dir.parent  # pipelines/claude_code
    manifest_path = pipeline_dir / "staging" / "discovery_manifest.json"
    
    return manifest_path.exists(), manifest_path


def main():
    """Main status check function."""
    print("=" * 60)
    print("📊 PIPELINE STATUS CHECKER")
    print("=" * 60)
    print()
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print()
    
    # Stage definitions (0-16)
    stages = [
        (0, "Assessment (Discovery)", None),  # Special: manifest file
        (1, "Extraction", get_stage_table(1)),
        (2, "Cleaning", get_stage_table(2)),
        (3, "THE GATE (Identity)", get_stage_table(3)),
        (4, "Staging + LLM Text Correction", get_stage_table(4)),
        (5, "L8 Conversations", get_stage_table(5)),
        (6, "L6 Turns", get_stage_table(6)),
        (7, "L5 Messages", get_stage_table(7)),
        (8, "L4 Sentences", get_stage_table(8)),
        (9, "L3 Spans (NER)", get_stage_table(9)),
        (10, "L2 Words", get_stage_table(10)),
        (11, "Parent-Child Validation", get_stage_table(11)),
        (12, "Count Denormalization", get_stage_table(12)),
        (13, "Pre-Promotion Validation", get_stage_table(13)),
        (14, "Promotion to entity_unified", get_stage_table(14)),
        (15, "Final Validation", get_stage_table(15)),
        (16, "Final Promotion", TABLE_ENTITY_UNIFIED),  # Special: entity_unified
    ]
    
    for stage_num, stage_name, table_name in stages:
        if stage_num == 0:
            # Check for manifest file
            exists, manifest_path = check_manifest()
            status = "✅" if exists else "⏳"
            print(f"{status} Stage {stage_num}: {stage_name}")
            if exists:
                print(f"   📄 Manifest: {manifest_path}")
            else:
                print(f"   📄 Manifest: Not found (run Stage 0 first)")
        else:
            success, count = check_stage(stage_num, table_name)
            status = "✅" if success else "⏳"
            print(f"{status} Stage {stage_num}: {stage_name}")
            if success:
                print(f"   📊 {count:,} rows in BigQuery")
            else:
                print(f"   📊 No data (stage not run yet)")
        print()
    
    print("=" * 60)
    print("✅ = Working (data is there)")
    print("⏳ = Not run yet (no data)")
    print("=" * 60)
    print()
    print("💡 Tip: Run stages sequentially using:")
    print("   python pipelines/claude_code/scripts/run_pipeline.py")


if __name__ == "__main__":
    main()
