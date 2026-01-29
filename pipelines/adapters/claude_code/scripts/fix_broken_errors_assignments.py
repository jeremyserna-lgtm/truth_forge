#!/usr/bin/env python3
"""Fix broken errors = # assignments in stage files."""
import re
import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent

def fix_file(file_path: Path) -> bool:
    """Fix broken errors assignments."""
    content = file_path.read_text(encoding="utf-8")
    original = content
    
    # Pattern: errors = # Use MERGE...
    pattern = r'errors\s*=\s*#\s*Use MERGE to prevent duplicates\s+from shared import merge_rows_to_table\s+from shared_validation import validate_table_id\s+validated_table = validate_table_id\(STAGE_\d+_TABLE\)\s+try:\s+merge_rows_to_table\([^)]+\)\s+except Exception as e:\s+logger\.warning\(f"MERGE failed, using direct insert: \{e\}"\)\s+bq_client\.insert_rows_json\(validated_table, [^)]+\)'
    
    # Simpler: find the pattern and replace
    # Find: errors = # Use MERGE... (multiline)
    multiline_pattern = r'errors\s*=\s*#\s*Use MERGE to prevent duplicates.*?bq_client\.insert_rows_json\(validated_table, [^)]+\)'
    
    replacement = '''# Use MERGE to prevent duplicates
            from shared import merge_rows_to_table
            from shared_validation import validate_table_id
            validated_table = validate_table_id(STAGE_X_TABLE)
            try:
                merge_rows_to_table(
                    client=bq_client,
                    table_id=validated_table,
                    rows=records_to_insert,
                    match_key="entity_id"
                )
                errors = []
            except Exception as e:
                logger.warning(f"MERGE failed, using direct insert: {e}")
                errors = bq_client.insert_rows_json(validated_table, records_to_insert)'''
    
    # Actually, let's do a simpler find-replace
    # Find the table variable first
    table_match = re.search(r'STAGE_(\d+)_TABLE', content)
    if table_match:
        stage_num = table_match.group(1)
        table_var = f"STAGE_{stage_num}_TABLE"
        
        # Replace the broken pattern
        broken = rf'errors\s*=\s*#\s*Use MERGE to prevent duplicates\s+from shared import merge_rows_to_table\s+from shared_validation import validate_table_id\s+validated_table = validate_table_id\({table_var}\)\s+try:\s+merge_rows_to_table\([^)]+\)\s+except Exception as e:\s+logger\.warning\(f"MERGE failed, using direct insert: \{e\}"\)\s+bq_client\.insert_rows_json\(validated_table, records_to_insert\)'
        
        fixed = f'''# Use MERGE to prevent duplicates
            from shared import merge_rows_to_table
            from shared_validation import validate_table_id
            validated_table = validate_table_id({table_var})
            try:
                merge_rows_to_table(
                    client=bq_client,
                    table_id=validated_table,
                    rows=records_to_insert,
                    match_key="entity_id"
                )
                errors = []
            except Exception as e:
                logger.warning(f"MERGE failed, using direct insert: {{e}}")
                errors = bq_client.insert_rows_json(validated_table, records_to_insert)'''
        
        content = re.sub(broken, fixed, content, flags=re.MULTILINE | re.DOTALL)
    
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False

# Fix stages 10-13
for stage in [10, 11, 12, 13]:
    stage_file = scripts_dir / f"stage_{stage}" / f"claude_code_stage_{stage}.py"
    if stage_file.exists():
        if fix_file(stage_file):
            print(f"✅ Fixed Stage {stage}")
        else:
            # Manual fix needed
            print(f"⚠️  Stage {stage} needs manual fix")
