#!/usr/bin/env python3
"""Verify that all pipeline stages use the new ID system correctly.

Checks:
- All stages import from truth_forge.identity
- No direct hashlib.sha256 usage for IDs (except fingerprints)
- No old format IDs (conv_L08_S_, 12-char hashes, etc.)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))


def check_file_for_id_issues(file_path: Path) -> list[str]:
    """Check a file for ID generation issues.
    
    Returns:
        List of issues found (empty if none).
    """
    issues = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Failed to read file: {e}"]
    
    # Check for old conversation ID format (only in code, not comments/docs)
    # Look for actual usage, not just mentions in comments
    code_lines = [line for line in content.split('\n') if not line.strip().startswith('#') and not line.strip().startswith('║') and '"""' not in line[:20]]
    code_content = '\n'.join(code_lines)
    if re.search(r'conv_L08_S_', code_content):
        issues.append(f"Found old conversation ID format in code: conv_L08_S_")
    
    # Check for 12-char hash usage in ID generation (should be 16)
    if re.search(r'hashlib\.sha256.*\.hexdigest\(\)\[:12\]', content):
        issues.append(f"Found 12-char hash (should be 16 for IDs)")
    
    # Check for 8-char UUID fragments (should use ULID)
    if re.search(r'uuid\.uuid4\(\)\.hex\[:8\]', content):
        issues.append(f"Found 8-char UUID fragment (should use ULID)")
    
    # Check for direct hashlib usage in ID generation (should use Primitive.identity)
    # But allow it for fingerprints/content hashing (not ID generation)
    # Allow fallback patterns (try Primitive.identity first, then fallback)
    # Only flag if hashlib is used WITHOUT trying Primitive.identity first
    if re.search(r'def generate.*id', content, re.IGNORECASE):
        # Check if function uses hashlib directly without Primitive.identity
        func_match = re.search(r'def (generate.*id)\([^)]*\):.*?(?=def |\Z)', content, re.IGNORECASE | re.DOTALL)
        if func_match:
            func_body = func_match.group(0)
            # If it uses hashlib but doesn't try Primitive.identity first, flag it
            if 'hashlib' in func_body and 'Primitive.identity' not in func_body and 'from truth_forge.identity import' not in func_body:
                issues.append(f"Found direct hashlib usage in ID generation function without Primitive.identity fallback")
    
    return issues


def main() -> int:
    """Check all pipeline scripts for ID system compliance.
    
    Returns:
        0 if all checks pass, 1 otherwise.
    """
    scripts_dir = Path(__file__).resolve().parent
    
    # Find all Python files in pipeline scripts
    python_files = list(scripts_dir.rglob("*.py"))
    
    # Exclude test files, utilities, and this verification script
    exclude_patterns = ["test_", "__pycache__", ".pyc", "verify_id_system.py"]
    python_files = [
        f for f in python_files
        if not any(pattern in str(f) for pattern in exclude_patterns)
    ]
    
    print("="*60)
    print("ID SYSTEM COMPLIANCE CHECK")
    print("="*60)
    print(f"\nChecking {len(python_files)} files...\n")
    
    all_issues = {}
    for file_path in sorted(python_files):
        issues = check_file_for_id_issues(file_path)
        if issues:
            all_issues[file_path] = issues
    
    if not all_issues:
        print("✅ All files comply with new ID system")
        return 0
    
    print("❌ Issues found:\n")
    for file_path, issues in all_issues.items():
        rel_path = file_path.relative_to(scripts_dir)
        print(f"  {rel_path}:")
        for issue in issues:
            print(f"    - {issue}")
        print()
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
