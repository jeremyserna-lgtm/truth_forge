#!/usr/bin/env python3
"""Fix Remaining Stages - Duplicate Prevention and SQL Injection

This script fixes duplicate prevention and SQL injection for stages 8-15.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent

def fix_stage_file(stage_num: int) -> bool:
    """Fix a stage file for duplicate prevention and SQL injection."""
    stage_file = scripts_dir / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
    
    if not stage_file.exists():
        return False
    
    content = stage_file.read_text(encoding="utf-8")
    original = content
    
    table_var = f"STAGE_{stage_num}_TABLE"
    
    # Add imports if needed
    if "from shared_validation import validate_table_id" not in content:
        # Find last import
        import_match = list(re.finditer(r'from\s+shared[^\n]+\n', content))
        if import_match:
            insert_pos = import_match[-1].end()
            content = content[:insert_pos] + "from shared_validation import validate_table_id\n" + content[insert_pos:]
    
    if "from shared import merge_rows_to_table" not in content and "insert_rows_json" in content:
        # Add merge import
        shared_import_match = list(re.finditer(r'from\s+shared\s+import[^\n]+\n', content))
        if shared_import_match:
            insert_pos = shared_import_match[-1].end()
            # Check if merge_rows_to_table already in the import
            if "merge_rows_to_table" not in content[:insert_pos]:
                # Add to existing import or create new
                last_shared = shared_import_match[-1].group(0)
                if last_shared.strip().endswith(")"):
                    # Multi-line import
                    content = content.replace(last_shared, last_shared.rstrip()[:-1] + ", merge_rows_to_table)\n")
                else:
                    # Single line import - add comma and merge_rows_to_table
                    content = content.replace(last_shared, last_shared.rstrip() + ", merge_rows_to_table\n")
    
    # Fix insert_rows_json calls
    # Pattern: bq_client.insert_rows_json(STAGE_X_TABLE, batch)
    pattern1 = rf'bq_client\.insert_rows_json\(\s*{table_var}\s*,\s*([^)]+)\)'
    
    replacement1 = f'''# Use MERGE to prevent duplicates
                        from shared import merge_rows_to_table
                        from shared_validation import validate_table_id
                        validated_table = validate_table_id({table_var})
                        try:
                            merge_rows_to_table(
                                client=bq_client,
                                table_id=validated_table,
                                rows=\\1,
                                match_key="entity_id"
                            )
                        except Exception as e:
                            logger.warning(f"MERGE failed, using direct insert: {{e}}")
                            bq_client.insert_rows_json(validated_table, \\1)'''
    
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern: client.insert_rows_json(STAGE_X_TABLE, batch)
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
                                match_key="entity_id"
                            )
                        except Exception as e:
                            logger.warning(f"MERGE failed, using direct insert: {{e}}")
                            client.insert_rows_json(validated_table, \\1)'''
    
    content = re.sub(pattern2, replacement2, content)
    
    # Pattern: errors = client.insert_rows_json(...)
    pattern3 = rf'errors\s*=\s*client\.insert_rows_json\(\s*{table_var}\s*,\s*([^)]+)\)'
    
    replacement3 = f'''# Use MERGE to prevent duplicates
                        from shared import merge_rows_to_table
                        from shared_validation import validate_table_id
                        validated_table = validate_table_id({table_var})
                        try:
                            merge_rows_to_table(
                                client=client,
                                table_id=validated_table,
                                rows=\\1,
                                match_key="entity_id"
                            )
                            errors = []
                        except Exception as e:
                            logger.warning(f"MERGE failed, using direct insert: {{e}}")
                            errors = client.insert_rows_json(validated_table, \\1)'''
    
    content = re.sub(pattern3, replacement3, content)
    
    # Fix table IDs in queries
    # Find queries using table variables and add validation
    query_patterns = [
        (rf'FROM\s+`\{{' + table_var + r'\}\}`', table_var),
        (rf'INTO\s+`\{{' + table_var + r'\}\}`', table_var),
    ]
    
    for pattern, var in query_patterns:
        if re.search(pattern, content):
            # Add validation before first use
            first_match = re.search(pattern, content)
            if first_match:
                # Find function start
                func_start = content.rfind('def ', 0, first_match.start())
                if func_start != -1:
                    # Find function body
                    colon_pos = content.find(':', func_start)
                    if colon_pos != -1:
                        body_start = content.find('\n', colon_pos) + 1
                        validated_var = f"validated_{var.lower()}"
                        if validated_var not in content[func_start:body_start + 200]:
                            validation = f"    from shared_validation import validate_table_id\n    {validated_var} = validate_table_id({var})\n    "
                            content = content[:body_start] + validation + content[body_start:]
                            # Replace table references
                            content = re.sub(
                                rf'`\{{' + var + r'\}\}`',
                                rf'`{{' + validated_var + r'}}`',
                                content
                            )
    
    if content != original:
        stage_file.write_text(content, encoding="utf-8")
        print(f"✅ Fixed Stage {stage_num}")
        return True
    
    return False

def main():
    """Fix all remaining stages."""
    stages_to_fix = [8, 9, 10, 11, 12, 13, 15]
    
    fixed = 0
    for stage_num in stages_to_fix:
        if fix_stage_file(stage_num):
            fixed += 1
    
    print(f"\n{'=' * 80}")
    print(f"Fixed {fixed} stage(s)")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
