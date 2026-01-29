#!/usr/bin/env python3
"""Fix Duplicate Prevention Across All Stages

This script replaces insert_rows_json with merge_rows_to_table
to prevent duplicates when re-running stages.

Usage:
    python fix_all_duplicate_prevention.py [--stage N] [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Add paths
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

# Match keys for each stage
STAGE_MATCH_KEYS = {
    3: "entity_id",
    5: "entity_id",  # token entity_id
    6: "sentence_id",
    7: "entity_id",  # message entity_id
    8: "conversation_id",
    9: "entity_id",  # embedding entity_id
    10: "entity_id",  # extraction entity_id
    11: "entity_id",  # sentiment entity_id
    12: "entity_id",  # topic entity_id
    13: "relationship_id",
    14: "entity_id",  # aggregated entity_id
    15: "entity_id",  # validated entity_id
    16: "entity_id",  # promoted entity_id
}

def fix_stage_duplicate_prevention(stage_num: int, dry_run: bool = False) -> bool:
    """Fix duplicate prevention for a specific stage."""
    stage_file = scripts_dir / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
    
    if stage_num not in STAGE_MATCH_KEYS:
        return False
    
    if not stage_file.exists():
        print(f"⚠️  Stage {stage_num} file not found")
        return False
    
    content = stage_file.read_text(encoding="utf-8")
    original = content
    
    match_key = STAGE_MATCH_KEYS[stage_num]
    table_var = f"STAGE_{stage_num}_TABLE"
    
    # Pattern 1: Replace insert_rows_json with merge_rows_to_table
    # Find patterns like: errors = client.insert_rows_json(STAGE_X_TABLE, batch)
    pattern1 = rf'errors\s*=\s*client\.insert_rows_json\(\s*{table_var}\s*,\s*([^)]+)\)'
    
    replacement1 = f'''# Use MERGE to prevent duplicates
                from shared import merge_rows_to_table
                from shared_validation import validate_table_id
                validated_table = validate_table_id({table_var})
                try:
                    merge_rows_to_table(
                        client=client,
                        table_id=validated_table,
                        rows=\\1,
                        match_key="{match_key}"
                    )
                    errors = []
                except Exception as e:
                    logger.warning(f"MERGE failed, using direct insert: {{e}}")
                    errors = client.insert_rows_json(validated_table, \\1)'''
    
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Direct insert_rows_json calls without error assignment
    pattern2 = rf'client\.insert_rows_json\(\s*{table_var}\s*,\s*([^)]+)\)'
    
    replacement2 = f'''# Use MERGE to prevent duplicates
                from shared import merge_rows_to_table
                from shared_validation import validate_table_id
                validated_table = validate_table_id({table_var})
                try:
                    merge_rows_to_table(
                        client=client,
                        table_id=validated_table,
                        rows=\\1,
                        match_key="{match_key}"
                    )
                except Exception as e:
                    logger.warning(f"MERGE failed, using direct insert: {{e}}")
                    client.insert_rows_json(validated_table, \\1)'''
    
    content = re.sub(pattern2, replacement2, content)
    
    # Also add table ID validation for queries
    # Find queries using table variables
    query_pattern = rf'FROM\s+`\{{' + table_var + r'\}\}`'
    if re.search(query_pattern, content):
        # Add validation before queries
        content = re.sub(
            rf'(\w+)\s*=\s*f"""\s*SELECT',
            rf'from shared_validation import validate_table_id\nvalidated_{table_var.lower()} = validate_table_id({table_var})\n\\1 = f"""SELECT',
            content,
            count=1
        )
        # Replace table references in queries
        validated_var_name = f"validated_{table_var.lower()}"
        content = re.sub(
            rf'`\{{' + table_var + r'\}\}`',
            rf'`{{' + validated_var_name + r'}}`',
            content
        )
    
    if content != original:
        if not dry_run:
            stage_file.write_text(content, encoding="utf-8")
        print(f"✅ Fixed Stage {stage_num} duplicate prevention (match_key: {match_key})")
        return True
    else:
        print(f"ℹ️  Stage {stage_num} - no duplicate prevention fixes needed")
        return False

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix duplicate prevention across all stages")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    parser.add_argument("--stage", type=int, help="Fix specific stage only")
    
    args = parser.parse_args()
    
    fixed_count = 0
    
    if args.stage is not None:
        if fix_stage_duplicate_prevention(args.stage, args.dry_run):
            fixed_count = 1
    else:
        for stage_num in STAGE_MATCH_KEYS.keys():
            if fix_stage_duplicate_prevention(stage_num, args.dry_run):
                fixed_count += 1
    
    print(f"\n{'=' * 80}")
    print(f"Fixed {fixed_count} stage(s)")
    if args.dry_run:
        print("⚠️  DRY RUN - No changes were made")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
