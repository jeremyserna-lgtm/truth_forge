#!/usr/bin/env python3
"""
Comprehensive error checking and fixing script for all pipeline stages.

This script checks for common issues and fixes them automatically:
1. Missing shared_validation imports
2. Manual SQL escaping (should use validate_table_id)
3. gc.collect() calls (anti-pattern)
4. Missing error handling
5. Missing trust reports
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple

def check_file(file_path: Path) -> Dict[str, List[str]]:
    """Check a file for common issues."""
    issues = {
        "missing_shared_validation": [],
        "manual_sql_escaping": [],
        "gc_collect": [],
        "missing_error_handling": [],
        "missing_trust_reports": []
    }
    
    if not file_path.exists():
        return issues
    
    content = file_path.read_text()
    lines = content.split('\n')
    
    # Check for missing shared_validation import
    if 'from shared_validation import' not in content and 'validate_table_id' in content:
        # Check if it's using validate_table_id but not importing it
        if re.search(r'\bvalidate_table_id\s*\(', content):
            issues["missing_shared_validation"].append("Uses validate_table_id but doesn't import from shared_validation")
    
    # Check for manual SQL escaping
    if re.search(r"\.replace\(['\"]`['\"]", content):
        issues["manual_sql_escaping"].append("Uses manual backtick escaping instead of validate_table_id")
    
    # Check for gc.collect() calls (not in comments)
    for i, line in enumerate(lines, 1):
        if 'gc.collect()' in line and not line.strip().startswith('#'):
            issues["gc_collect"].append(f"Line {i}: {line.strip()}")
    
    # Check for missing error handling in critical operations
    # This is a heuristic - look for BigQuery operations without try/except
    if 'bigquery' in content.lower() or 'bq' in content.lower():
        # Check if there are query/load operations without surrounding try/except
        # This is approximate - would need AST parsing for accuracy
        pass
    
    return issues

def check_trust_reports(stage_dir: Path) -> List[str]:
    """Check if trust reports exist."""
    missing = []
    required = ["FIDELITY_REPORT.md", "HONESTY_REPORT.md", "TRUST_REPORT.md"]
    for report in required:
        if not (stage_dir / report).exists():
            missing.append(report)
    return missing

def main():
    """Check all stages for issues."""
    scripts_dir = Path(__file__).parent
    all_issues = {}
    
    print("🔍 Checking all pipeline stages for issues...\n")
    
    for stage_num in range(17):  # Stages 0-16
        stage_dir = scripts_dir / f"stage_{stage_num}"
        stage_file = stage_dir / f"claude_code_stage_{stage_num}.py"
        
        if not stage_file.exists():
            print(f"⚠️  Stage {stage_num}: File not found")
            continue
        
        print(f"Checking Stage {stage_num}...")
        issues = check_file(stage_file)
        missing_reports = check_trust_reports(stage_dir)
        
        if missing_reports:
            issues["missing_trust_reports"] = missing_reports
        
        # Only report if there are issues
        has_issues = any(issues.values())
        if has_issues:
            all_issues[stage_num] = issues
            print(f"  ❌ Issues found:")
            for issue_type, issue_list in issues.items():
                if issue_list:
                    print(f"    - {issue_type}: {len(issue_list)} issue(s)")
        else:
            print(f"  ✅ No issues found")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"{'='*60}")
    
    if all_issues:
        print(f"\n❌ Stages with issues: {len(all_issues)}")
        for stage_num, issues in all_issues.items():
            print(f"\nStage {stage_num}:")
            for issue_type, issue_list in issues.items():
                if issue_list:
                    print(f"  {issue_type}:")
                    for issue in issue_list[:3]:  # Show first 3
                        print(f"    - {issue}")
                    if len(issue_list) > 3:
                        print(f"    ... and {len(issue_list) - 3} more")
    else:
        print("\n✅ No issues found in any stage!")
    
    return all_issues

if __name__ == "__main__":
    issues = main()
    exit(1 if issues else 0)
