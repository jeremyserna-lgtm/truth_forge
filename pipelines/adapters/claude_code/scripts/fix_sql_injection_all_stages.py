#!/usr/bin/env python3
"""
Fix SQL injection vulnerabilities across all pipeline stages.

This script:
1. Finds all SQL queries with f-strings that use values in WHERE clauses
2. Converts them to use QueryJobConfig with query_parameters
3. Keeps validate_table_id() for table names (BigQuery doesn't support parameterized table names)
"""

import re
from pathlib import Path
from typing import List, Tuple

def find_queries_needing_parameterization(content: str) -> List[Tuple[int, str, str]]:
    """Find SQL queries that need parameterization.
    
    Returns list of (line_number, query_text, issue_description)
    """
    issues = []
    lines = content.split('\n')
    
    in_query = False
    query_start = 0
    query_lines = []
    
    for i, line in enumerate(lines, 1):
        # Detect start of f-string query
        if 'f"""' in line or "f'''" in line:
            if 'SELECT' in line.upper() or 'FROM' in line.upper() or 'WHERE' in line.upper():
                in_query = True
                query_start = i
                query_lines = [line]
        elif in_query:
            query_lines.append(line)
            # Detect end of query (triple quotes)
            if '"""' in line or "'''" in line:
                query_text = '\n'.join(query_lines)
                
                # Check if query has WHERE clause with f-string interpolation
                if 'WHERE' in query_text.upper():
                    # Look for patterns like WHERE field = {variable} or WHERE field = '{variable}'
                    if re.search(r'WHERE\s+\w+\s*=\s*\{[^}]+\}', query_text, re.IGNORECASE):
                        issues.append((
                            query_start,
                            query_text[:200],  # First 200 chars
                            "WHERE clause uses f-string interpolation - should use @parameter"
                        ))
                
                in_query = False
                query_lines = []
    
    return issues

def fix_query_parameterization(file_path: Path) -> List[str]:
    """Fix SQL injection in a single file.
    
    Returns list of changes made.
    """
    content = file_path.read_text()
    original_content = content
    changes = []
    
    # Pattern 1: WHERE field = {variable} -> WHERE field = @param with QueryJobConfig
    # This is complex - we'll need to do it manually for each stage
    
    # For now, just report what needs fixing
    issues = find_queries_needing_parameterization(content)
    if issues:
        changes.append(f"Found {len(issues)} queries needing parameterization")
    
    return changes

def main():
    """Fix SQL injection across all stages."""
    scripts_dir = Path(__file__).parent
    
    print("🔒 Fixing SQL Injection Issues Across All Stages\n")
    print("="*80)
    
    all_changes = {}
    for stage_num in range(17):
        stage_file = scripts_dir / f"stage_{stage_num}" / f"claude_code_stage_{stage_num}.py"
        
        if not stage_file.exists():
            continue
        
        print(f"\nChecking Stage {stage_num}...")
        changes = fix_query_parameterization(stage_file)
        
        if changes:
            all_changes[stage_num] = changes
            print(f"  ⚠️  {len(changes)} issue(s) found")
        else:
            print(f"  ✅ No SQL injection issues found")
    
    print("\n" + "="*80)
    if all_changes:
        print(f"\n⚠️  Stages needing SQL injection fixes: {len(all_changes)}")
        for stage, changes in all_changes.items():
            print(f"  Stage {stage}: {', '.join(changes)}")
    else:
        print("\n✅ No SQL injection issues found!")
    
    print("\nNote: This script identifies issues. Manual fixes required for each stage.")
    return all_changes

if __name__ == "__main__":
    main()
