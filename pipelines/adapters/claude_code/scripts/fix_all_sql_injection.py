#!/usr/bin/env python3
"""Fix SQL Injection Vulnerabilities Across All Stages

This script adds validate_table_id() calls to all SQL queries
to prevent SQL injection vulnerabilities.

Usage:
    python fix_all_sql_injection.py [--stage N] [--dry-run]
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

def fix_stage_sql_injection(stage_num: int, dry_run: bool = False) -> bool:
    """Fix SQL injection vulnerabilities for a specific stage."""
    stage_file = scripts_dir / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
    
    if not stage_file.exists():
        print(f"⚠️  Stage {stage_num} file not found")
        return False
    
    content = stage_file.read_text(encoding="utf-8")
    original = content
    
    # Add import if not present
    if "from shared_validation import validate_table_id" not in content:
        # Find last import statement
        import_pattern = r'(from\s+shared[^\n]+\n)'
        matches = list(re.finditer(import_pattern, content))
        if matches:
            last_import = matches[-1]
            insert_pos = last_import.end()
            content = content[:insert_pos] + "from shared_validation import validate_table_id, validate_run_id\n" + content[insert_pos:]
        else:
            # Add after path setup
            path_setup_pattern = r'(sys\.path\.insert\(0[^\n]+\n)'
            matches = list(re.finditer(path_setup_pattern, content))
            if matches:
                last_path = matches[-1]
                insert_pos = last_path.end()
                content = content[:insert_pos] + "\nfrom shared_validation import validate_table_id, validate_run_id\n" + content[insert_pos:]
    
    # Fix table ID variables - find all STAGE_X_TABLE usages
    table_vars = re.findall(r'STAGE_\d+_TABLE', content)
    for table_var in set(table_vars):
        # Get the stage number
        stage_match = re.search(r'STAGE_(\d+)_TABLE', table_var)
        if stage_match:
            stage_n = stage_match.group(1)
            
            # Validate table ID before first use
            # Find where table is first used in a query
            query_pattern = rf'`\{{{table_var}\}\}`'
            if re.search(query_pattern, content):
                # Add validation before first query
                first_query = re.search(rf'(\w+)\s*=\s*f"""\s*SELECT.*?`\{{{table_var}\}\}`', content, re.DOTALL)
                if first_query:
                    # Add validation before this query
                    validated_var = f"validated_{table_var.lower()}"
                    # Check if already validated
                    if validated_var not in content:
                        insert_pos = first_query.start()
                        validation_line = f"    {validated_var} = validate_table_id({table_var})\n    "
                        content = content[:insert_pos] + validation_line + content[insert_pos:]
                        # Replace all uses of {table_var} with {validated_var}
                        content = re.sub(
                            rf'`\{{{table_var}\}\}`',
                            rf'`{{{validated_var}}}`',
                            content
                        )
    
    # Fix timestamp interpolations
    # Pattern: TIMESTAMP('{variable}')
    timestamp_pattern = r"TIMESTAMP\('\{([^}]+)\}'\)"
    matches = list(re.finditer(timestamp_pattern, content))
    for match in reversed(matches):  # Reverse to maintain positions
        var_name = match.group(1)
        # Validate timestamp string (basic check)
        validation_code = f"""    # Validate timestamp to prevent SQL injection
    if any(danger in {var_name} for danger in ['--', ';', '/*', '*/']):
        raise ValueError("Invalid timestamp: potential SQL injection")
    """
        # Insert validation before the query
        query_start = content.rfind('f"""', 0, match.start())
        if query_start != -1:
            # Find the function start
            func_start = content.rfind('def ', 0, query_start)
            if func_start != -1:
                # Find the first line of the function body
                first_line = content.find('\n', query_start) + 1
                if first_line > 0 and validation_code not in content[func_start:first_line]:
                    content = content[:first_line] + validation_code + content[first_line:]
    
    # Fix run_id interpolations in WHERE clauses
    # Pattern: WHERE run_id = '{run_id}'
    run_id_pattern = r"WHERE\s+run_id\s*=\s*'\{run_id\}'"
    if re.search(run_id_pattern, content):
        # Add validation for run_id
        if 'validated_run_id = validate_run_id(run_id)' not in content:
            # Find first use of run_id in WHERE clause
            first_where = re.search(run_id_pattern, content)
            if first_where:
                # Find function start
                func_start = content.rfind('def ', 0, first_where.start())
                if func_start != -1:
                    # Find function body start
                    body_start = content.find(':', func_start) + 1
                    body_line = content.find('\n', body_start) + 1
                    if body_line > 0:
                        validation = "    from shared_validation import validate_run_id\n    validated_run_id = validate_run_id(run_id)\n"
                        if validation not in content[func_start:body_line + 100]:
                            content = content[:body_line] + validation + content[body_line:]
                            # Replace run_id with validated_run_id
                            content = re.sub(
                                r"run_id\s*=\s*'\{run_id\}'",
                                r"run_id = '{validated_run_id}'",
                                content
                            )
    
    if content != original:
        if not dry_run:
            stage_file.write_text(content, encoding="utf-8")
        print(f"✅ Fixed Stage {stage_num} SQL injection vulnerabilities")
        return True
    else:
        print(f"ℹ️  Stage {stage_num} - no SQL injection fixes needed")
        return False

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix SQL injection across all stages")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed")
    parser.add_argument("--stage", type=int, help="Fix specific stage only")
    
    args = parser.parse_args()
    
    fixed_count = 0
    
    if args.stage is not None:
        if fix_stage_sql_injection(args.stage, args.dry_run):
            fixed_count = 1
    else:
        for stage_num in range(17):
            if fix_stage_sql_injection(stage_num, args.dry_run):
                fixed_count += 1
    
    print(f"\n{'=' * 80}")
    print(f"Fixed {fixed_count} stage(s)")
    if args.dry_run:
        print("⚠️  DRY RUN - No changes were made")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
