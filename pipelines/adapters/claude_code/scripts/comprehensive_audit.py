#!/usr/bin/env python3
"""Comprehensive Pipeline Audit Tool

Systematically scans all pipeline scripts for:
- SQL injection vulnerabilities
- Security issues
- Import errors
- Duplicate prevention gaps
- Memory/scalability issues
- Error handling problems
- Code quality issues
- Antipatterns

Usage:
    python comprehensive_audit.py [--fix] [--stage N]
"""
from __future__ import annotations

import ast
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Add paths
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

class PipelineAuditor:
    """Comprehensive auditor for pipeline scripts."""
    
    def __init__(self):
        self.issues: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.stage_files: dict[int, Path] = {}
        
    def discover_stage_files(self) -> None:
        """Discover all stage script files."""
        for stage_num in range(17):
            stage_dir = scripts_dir / f"stage_{stage_num}"
            stage_file = stage_dir / f"claude_code_stage_{stage_num}.py"
            if stage_file.exists():
                self.stage_files[stage_num] = stage_file
    
    def audit_file(self, file_path: Path, stage_num: int) -> None:
        """Audit a single file for all issues."""
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            
            # Run all audit checks
            self._check_sql_injection(file_path, content, stage_num)
            self._check_imports(file_path, content, stage_num)
            self._check_duplicate_prevention(file_path, content, stage_num)
            self._check_security(file_path, content, stage_num)
            self._check_memory_issues(file_path, content, stage_num)
            self._check_error_handling(file_path, content, stage_num)
            self._check_code_quality(file_path, content, tree, stage_num)
            
        except Exception as e:
            self.issues["PARSE_ERROR"].append({
                "file": str(file_path),
                "stage": stage_num,
                "severity": "CRITICAL",
                "issue": f"Failed to parse file: {e}",
                "line": 0,
            })
    
    def _check_sql_injection(self, file_path: Path, content: str, stage_num: int) -> None:
        """Check for SQL injection vulnerabilities."""
        lines = content.split("\n")
        
        # Build a map of validated variables
        validated_vars = self._find_validated_variables(content, lines)
        
        # Build a map of system-generated timestamps
        system_timestamps = self._find_system_timestamps(content, lines)
        
        # Pattern 1: f-strings in SQL queries without validation
        sql_patterns = [
            (r'f["\']\s*SELECT.*FROM\s*`\{([^}]+)\}`', "Unvalidated table ID in SELECT"),
            (r'f["\']\s*INSERT.*INTO\s*`\{([^}]+)\}`', "Unvalidated table ID in INSERT"),
            (r'f["\']\s*MERGE\s*`\{([^}]+)\}`', "Unvalidated table ID in MERGE"),
            (r'f["\']\s*CREATE.*TABLE\s*`\{([^}]+)\}`', "Unvalidated table ID in CREATE"),
            (r'f["\']\s*DELETE.*FROM\s*`\{([^}]+)\}`', "Unvalidated table ID in DELETE"),
            (r'WHERE\s+\{([^}]+)\}', "Unvalidated value in WHERE clause"),
            (r'TIMESTAMP\([\'"]\{([^}]+)\}[\'"]\)', "Unvalidated timestamp interpolation"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, issue in sql_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    var_name = match.group(1).strip()
                    
                    # Skip if variable is validated
                    if self._is_variable_safe(var_name, line_num, validated_vars, system_timestamps, lines):
                        continue
                    
                    # Check if validation is used on the same line
                    if "validate_table_id" not in line and "validate_" not in line.lower():
                        self.issues["SQL_INJECTION"].append({
                            "file": str(file_path),
                            "stage": stage_num,
                            "severity": "CRITICAL",
                            "issue": issue,
                            "line": line_num,
                            "code": line.strip(),
                        })
    
    def _find_validated_variables(self, content: str, lines: list[str]) -> dict[str, int]:
        """Find all variables that are validated via validate_table_id or validate_run_id."""
        validated_vars = {}
        
        for line_num, line in enumerate(lines, 1):
            # Pattern: validated_var = validate_table_id(TABLE_VAR)
            # Pattern: validated_var = validate_run_id(run_id)
            match = re.search(r'(\w+)\s*=\s*validate_(table_id|run_id)\(', line)
            if match:
                var_name = match.group(1)
                validated_vars[var_name] = line_num
        
        return validated_vars
    
    def _find_system_timestamps(self, content: str, lines: list[str]) -> dict[str, int]:
        """Find all variables that are system-generated timestamps."""
        system_timestamps = {}
        
        for line_num, line in enumerate(lines, 1):
            # Pattern: timestamp = datetime.now(UTC).isoformat()
            # Pattern: created_at = datetime.now(UTC).isoformat()
            # Pattern: *_at = datetime.now(UTC).isoformat()
            match = re.search(r'(\w+)\s*=\s*datetime\.now\([^)]*\)\.isoformat\(\)', line)
            if match:
                var_name = match.group(1)
                system_timestamps[var_name] = line_num
        
        return system_timestamps
    
    def _is_variable_safe(
        self, 
        var_name: str, 
        line_num: int, 
        validated_vars: dict[str, int],
        system_timestamps: dict[str, int],
        lines: list[str]
    ) -> bool:
        """Check if a variable is safe to use in SQL (validated or system-generated)."""
        # Check if variable is validated
        if var_name in validated_vars:
            # Make sure validation happens before use
            if validated_vars[var_name] < line_num:
                return True
        
        # Check if variable is a system-generated timestamp
        if var_name in system_timestamps:
            if system_timestamps[var_name] < line_num:
                return True
        
        # Check if variable name contains "validated" (common pattern)
        if "validated" in var_name.lower():
            # Check if it's assigned from validate_* function earlier
            for check_line_num in range(max(0, line_num - 50), line_num):
                if check_line_num < len(lines):
                    check_line = lines[check_line_num]
                    if f"{var_name} = validate_" in check_line:
                        return True
        
        # Check if WHERE clause value is hardcoded (not user input)
        # Pattern: status_filter = "validation_status IN ('PASSED', 'WARNING')"
        if line_num > 0 and line_num <= len(lines) and "WHERE" in lines[line_num - 1]:
            # Look backwards for hardcoded string assignment
            for check_line_num in range(max(0, line_num - 20), line_num):
                if check_line_num < len(lines):
                    check_line = lines[check_line_num]
                    # Check if it's a hardcoded string assignment
                    if re.search(rf'{var_name}\s*=\s*["\'][^"\']+["\']', check_line):
                        # Check if it contains SQL keywords (indicating it's SQL, not user input)
                        if any(keyword in check_line.upper() for keyword in ['IN', '=', 'PASSED', 'WARNING', 'VALIDATION_STATUS']):
                            return True
        
        return False
    
    def _check_imports(self, file_path: Path, content: str, stage_num: int) -> None:
        """Check for import errors."""
        lines = content.split("\n")
        
        # Check for problematic import patterns
        import_issues = [
            (r'from\s+src\.services\.central_services', "Missing central_services module"),
            (r'from\s+truth_forge\.core\s+import\s+get_logger', "get_logger not in truth_forge.core"),
            (r'import\s+src\.', "Direct src import without path setup"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, issue in import_issues:
                if re.search(pattern, line):
                    self.issues["IMPORT_ERROR"].append({
                        "file": str(file_path),
                        "stage": stage_num,
                        "severity": "HIGH",
                        "issue": issue,
                        "line": line_num,
                        "code": line.strip(),
                    })
    
    def _check_duplicate_prevention(self, file_path: Path, content: str, stage_num: int) -> None:
        """Check for duplicate prevention mechanisms."""
        # Check if stage uses INSERT without MERGE or duplicate checking
        if "insert_rows_json" in content:
            if "MERGE" not in content and "is_duplicate" not in content:
                # Check if it's Stage 1 (which should check fingerprints)
                if stage_num == 1:
                    if "fingerprint" not in content.lower():
                        self.issues["DUPLICATE_PREVENTION"].append({
                            "file": str(file_path),
                            "stage": stage_num,
                            "severity": "HIGH",
                            "issue": "Stage 1 uses insert_rows_json without fingerprint-based duplicate prevention",
                            "line": 0,
                        })
                else:
                    self.issues["DUPLICATE_PREVENTION"].append({
                        "file": str(file_path),
                        "stage": stage_num,
                        "severity": "HIGH",
                        "issue": f"Stage {stage_num} uses insert_rows_json without MERGE or duplicate prevention",
                        "line": 0,
                    })
        
        # Check if CREATE OR REPLACE is used (which can cause data loss)
        if "CREATE OR REPLACE TABLE" in content:
            if stage_num == 4:  # Known issue
                self.issues["DUPLICATE_PREVENTION"].append({
                    "file": str(file_path),
                    "stage": stage_num,
                    "severity": "CRITICAL",
                    "issue": "Stage 4 uses CREATE OR REPLACE which causes data loss on re-runs",
                    "line": 0,
                })
    
    def _check_security(self, file_path: Path, content: str, stage_num: int) -> None:
        """Check for security vulnerabilities."""
        lines = content.split("\n")
        
        # Path traversal checks
        for line_num, line in enumerate(lines, 1):
            if "os.path" in line or "Path(" in line:
                if "validate_path" not in line and "validate_input_source_dir" not in line:
                    if any(op in line for op in ["join", "resolve", "expanduser"]):
                        if "ALLOW_ANY_SOURCE_DIR" in content:
                            self.issues["SECURITY"].append({
                                "file": str(file_path),
                                "stage": stage_num,
                                "severity": "CRITICAL",
                                "issue": "Path validation bypass via ALLOW_ANY_SOURCE_DIR environment variable",
                                "line": line_num,
                                "code": line.strip(),
                            })
        
        # Subprocess execution without validation
        if "subprocess.run" in content or "subprocess.call" in content:
            if "shlex.quote" not in content and "validate" not in content.lower():
                self.issues["SECURITY"].append({
                    "file": str(file_path),
                    "stage": stage_num,
                    "severity": "HIGH",
                    "issue": "Subprocess execution without input validation",
                    "line": 0,
                })
    
    def _check_memory_issues(self, file_path: Path, content: str, stage_num: int) -> None:
        """Check for memory/scalability issues."""
        # Check for gc.collect() (antipattern)
        if "gc.collect()" in content:
            self.issues["MEMORY"].append({
                "file": str(file_path),
                "stage": stage_num,
                "severity": "MEDIUM",
                "issue": "Uses gc.collect() which is an antipattern - Python GC handles this automatically",
                "line": 0,
            })
        
        # Check for unbounded list accumulation
        if "list(" in content and "query().result()" in content:
            if "page_size" not in content and "LIMIT" not in content:
                self.issues["MEMORY"].append({
                    "file": str(file_path),
                    "stage": stage_num,
                    "severity": "HIGH",
                    "issue": "Potential memory issue: Loading query results into list without pagination",
                    "line": 0,
                })
    
    def _check_error_handling(self, file_path: Path, content: str, stage_num: int) -> None:
        """Check for error handling issues."""
        lines = content.split("\n")
        
        # Check for bare except clauses
        if re.search(r'except\s*:', content):
            self.issues["ERROR_HANDLING"].append({
                "file": str(file_path),
                "stage": stage_num,
                "severity": "MEDIUM",
                "issue": "Bare except clause catches all exceptions including SystemExit",
                "line": 0,
            })
        
        # Check for technical error messages (improved detection)
        # Look for error logging that includes exception objects directly
        error_patterns = [
            (r'logger\.error\(f"[^"]*\{e\}[^"]*"', "Technical error message with exception object"),
            (r'logger\.error\(f"[^"]*\{error\}[^"]*"', "Technical error message with error object"),
            (r'logger\.error\([^,]+,\s*exc_info=True\)', "Error message with stack trace"),
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, issue in error_patterns:
                if re.search(pattern, line):
                    # Check if there's also a user-friendly message nearby
                    # Look in the next few lines for user-friendly alternatives
                    has_user_friendly = False
                    for check_line_num in range(line_num, min(line_num + 5, len(lines))):
                        check_line = lines[check_line_num]
                        # Check for user-friendly patterns
                        if any(phrase in check_line.lower() for phrase in [
                            "failed to", "unable to", "could not", "error:", "what this means"
                        ]):
                            if "exc_info" not in check_line and "{" not in check_line:
                                has_user_friendly = True
                                break
                    
                    if not has_user_friendly:
                        self.issues["ERROR_HANDLING"].append({
                            "file": str(file_path),
                            "stage": stage_num,
                            "severity": "MEDIUM",
                            "issue": issue,
                            "line": line_num,
                            "code": line.strip(),
                        })
                        break
    
    def _check_code_quality(self, file_path: Path, content: str, tree: ast.AST, stage_num: int) -> None:
        """Check for code quality issues and antipatterns."""
        # Check for TODO/FIXME comments
        if "TODO" in content or "FIXME" in content or "XXX" in content:
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                if any(marker in line for marker in ["TODO", "FIXME", "XXX", "HACK"]):
                    self.issues["CODE_QUALITY"].append({
                        "file": str(file_path),
                        "stage": stage_num,
                        "severity": "LOW",
                        "issue": f"Unresolved TODO/FIXME: {line.strip()}",
                        "line": line_num,
                    })
        
        # Check for duplicate code blocks
        # (Simplified - would need more sophisticated analysis)
        
    def generate_report(self) -> str:
        """Generate comprehensive audit report."""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE PIPELINE AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_issues = sum(len(issues) for issues in self.issues.values())
        report.append(f"Total Issues Found: {total_issues}")
        report.append("")
        
        # Issues by category
        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        
        for category in sorted(self.issues.keys()):
            issues = self.issues[category]
            if not issues:
                continue
                
            report.append(f"\n{'=' * 80}")
            report.append(f"{category} ({len(issues)} issues)")
            report.append("=" * 80)
            
            # Group by severity
            by_severity = defaultdict(list)
            for issue in issues:
                by_severity[issue["severity"]].append(issue)
            
            for severity in severity_order:
                if severity not in by_severity:
                    continue
                    
                report.append(f"\n{severity} Severity ({len(by_severity[severity])} issues):")
                report.append("-" * 80)
                
                for issue in by_severity[severity]:
                    report.append(f"  Stage {issue['stage']}: {issue['issue']}")
                    if issue.get("line"):
                        report.append(f"    File: {Path(issue['file']).name}:{issue['line']}")
                    if issue.get("code"):
                        report.append(f"    Code: {issue['code'][:80]}")
                    report.append("")
        
        return "\n".join(report)
    
    def audit_all(self) -> None:
        """Audit all discovered stage files."""
        self.discover_stage_files()
        for stage_num, file_path in self.stage_files.items():
            print(f"Auditing Stage {stage_num}...", file=sys.stderr)
            self.audit_file(file_path, stage_num)

def main():
    """Main execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive pipeline audit")
    parser.add_argument("--stage", type=int, help="Audit specific stage only")
    parser.add_argument("--output", type=Path, help="Output file for report")
    
    args = parser.parse_args()
    
    auditor = PipelineAuditor()
    
    if args.stage is not None:
        stage_file = scripts_dir / f"stage_{args.stage}" / f"claude_code_stage_{args.stage}.py"
        if stage_file.exists():
            auditor.audit_file(stage_file, args.stage)
        else:
            print(f"❌ Stage {args.stage} file not found: {stage_file}")
            return 1
    else:
        auditor.audit_all()
    
    report = auditor.generate_report()
    
    if args.output:
        args.output.write_text(report, encoding="utf-8")
        print(f"✅ Report written to {args.output}")
    else:
        print(report)
    
    # Return exit code based on critical issues
    critical_count = sum(
        len([i for i in issues if i["severity"] == "CRITICAL"])
        for issues in auditor.issues.values()
    )
    
    return 1 if critical_count > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
