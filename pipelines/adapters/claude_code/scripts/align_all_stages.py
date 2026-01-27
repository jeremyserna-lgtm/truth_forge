#!/usr/bin/env python3
"""
Systematic alignment script for stages 7-16.
Applies all alignment patterns from stages 0-6 to stages 7-16.

Alignment patterns:
1. Date/timestamp: Python date/datetime objects (not ISO strings)
2. Metadata: json.dumps() (not str())
3. Memory: gc.collect(), clear objects
4. BigQuery limits: Constants defined
5. Error handling: Enhanced with require_diagnostic_on_error
6. Imports: gc, json added where needed
"""

import os
import re
from pathlib import Path

def check_and_fix_stage(stage_num: int) -> dict:
    """Check a stage file for alignment issues and return findings."""
    stage_file = Path(f"pipelines/claude_code/scripts/stage_{stage_num}/claude_code_stage_{stage_num}.py")
    
    if not stage_file.exists():
        return {"exists": False}
    
    content = stage_file.read_text()
    issues = {
        "exists": True,
        "has_gc_import": "import gc" in content or "from gc import" in content,
        "has_json_import": "import json" in content,
        "has_isoformat": ".isoformat()" in content,
        "has_str_metadata": re.search(r'metadata.*=.*str\(', content) is not None,
        "has_gc_collect": "gc.collect()" in content,
        "has_bq_limits": "BQ_DAILY_LOAD_JOBS_LIMIT" in content or "BQ_DAILY_QUERY_JOBS_LIMIT" in content,
        "has_require_diagnostic": "require_diagnostic_on_error" in content,
        "has_date_objects": re.search(r'created_at\s*=\s*datetime\.now\(timezone\.utc\)(?!\.isoformat)', content) is not None,
        "has_json_dumps": "json.dumps(" in content,
    }
    
    return issues

def main():
    """Check all stages 7-16."""
    print("Checking stages 7-16 for alignment issues...\n")
    
    for stage_num in range(7, 17):
        issues = check_and_fix_stage(stage_num)
        if not issues["exists"]:
            print(f"Stage {stage_num}: File not found")
            continue
        
        print(f"Stage {stage_num}:")
        if not issues["has_gc_import"]:
            print("  ⚠️  Missing: import gc")
        if not issues["has_json_import"]:
            print("  ⚠️  Missing: import json")
        if issues["has_isoformat"]:
            print("  ⚠️  Has: .isoformat() (should use Python objects)")
        if issues["has_str_metadata"]:
            print("  ⚠️  Has: str() for metadata (should use json.dumps())")
        if not issues["has_gc_collect"]:
            print("  ⚠️  Missing: gc.collect() calls")
        if not issues["has_bq_limits"]:
            print("  ⚠️  Missing: BigQuery daily limit constants")
        if not issues["has_require_diagnostic"]:
            print("  ⚠️  Missing: require_diagnostic_on_error")
        if not issues["has_date_objects"]:
            print("  ⚠️  Missing: Python date/datetime objects")
        if not issues["has_json_dumps"] and issues["has_str_metadata"]:
            print("  ⚠️  Missing: json.dumps() for metadata")
        
        if all([
            issues["has_gc_import"],
            issues["has_json_import"],
            not issues["has_isoformat"],
            not issues["has_str_metadata"],
            issues["has_gc_collect"],
            issues["has_bq_limits"],
            issues["has_require_diagnostic"],
        ]):
            print("  ✅ Aligned")
        print()

if __name__ == "__main__":
    main()
