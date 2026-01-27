#!/usr/bin/env python3
"""
Universal Error Checker for Pipeline Stages

This script allows non-coders to check if a stage has any errors in the logs.

Usage:
    python3 check_errors.py STAGE_NUMBER [--run-id RUN_ID]

Examples:
    python3 check_errors.py 5           # Check stage 5 errors
    python3 check_errors.py 5 --run-id abc123  # Check stage 5 errors for specific run
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Find project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def check_errors(stage_number: int, run_id: str = None) -> bool:
    """Check for errors in logs for a specific stage.

    Args:
        stage_number: The stage number to check (e.g., 5 for stage 5)
        run_id: Optional run ID to filter errors

    Returns:
        True if no errors found, False if errors found
    """
    print("=" * 70)
    print(f"CHECKING ERRORS FOR STAGE {stage_number}")
    print("=" * 70)
    print("\nThis script checks if there are any errors in the logs.")
    print("You don't need to know how to code - just run this and read the results.\n")

    # Define log locations to check
    log_locations = [
        project_root / "logs" / "central.log",
        project_root / "logs" / "pipeline.log",
        project_root / "logs" / f"stage_{stage_number}.log",
    ]

    errors_found = []
    files_checked = 0

    for log_path in log_locations:
        if log_path.exists():
            files_checked += 1
            print(f"Checking: {log_path.name}...")

            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()

                # Look for errors related to this stage
                stage_pattern = f"stage_{stage_number}"
                stage_pattern_alt = f"stage{stage_number}"

                for line_num, line in enumerate(lines[-5000:], 1):  # Check last 5000 lines
                    line_lower = line.lower()

                    # Check if this line is about our stage
                    is_stage_related = (
                        stage_pattern in line_lower or
                        stage_pattern_alt in line_lower
                    )

                    # Check if run_id matches (if specified)
                    if run_id and run_id not in line:
                        continue

                    # Check for error patterns
                    if is_stage_related and any(err in line_lower for err in ['error', 'exception', 'failed', 'traceback']):
                        # Skip false positives
                        if 'error_count' in line_lower or 'no errors' in line_lower:
                            continue
                        errors_found.append({
                            'file': log_path.name,
                            'line': line.strip()[:200],  # Truncate long lines
                        })
            except Exception as e:
                print(f"   ⚠️  Could not read {log_path.name}: {e}")

    # Report results
    print("\n" + "-" * 70)

    if files_checked == 0:
        print("⚠️  No log files found to check.")
        print("\nWhat this means: Either no pipeline has run yet, or logs are in a different location.")
        print("What to do: Run the pipeline first, then check for errors.")
        return True  # Not an error condition

    if not errors_found:
        print(f"✅ NO ERRORS FOUND for Stage {stage_number}")
        print(f"\n   Checked {files_checked} log file(s)")
        if run_id:
            print(f"   Filtered by run_id: {run_id}")
        print("\nThe stage appears to have run successfully!")
        return True
    else:
        print(f"❌ FOUND {len(errors_found)} ERROR(S) for Stage {stage_number}")
        print("\n" + "-" * 70)

        # Show unique errors (deduplicated)
        unique_errors = []
        seen = set()
        for err in errors_found:
            key = err['line'][:100]
            if key not in seen:
                seen.add(key)
                unique_errors.append(err)

        print(f"\nShowing {min(len(unique_errors), 5)} unique error(s):\n")

        for i, err in enumerate(unique_errors[:5], 1):
            print(f"{i}. [{err['file']}]")
            print(f"   {err['line']}")
            print()

        if len(unique_errors) > 5:
            print(f"   ... and {len(unique_errors) - 5} more unique error(s)")

        print("\n" + "-" * 70)
        print("\nWhat to do next:")
        print(f"  1. Read the error messages above")
        print(f"  2. If the error is clear, fix the issue and re-run Stage {stage_number}")
        print(f"  3. If you need help, share these error messages with support")
        print(f"  4. After fixing, run this check again to confirm errors are resolved")

        return False


def main():
    parser = argparse.ArgumentParser(
        description="Check for errors in pipeline stage logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 check_errors.py 5           # Check stage 5 errors
    python3 check_errors.py 5 --run-id abc123  # Check specific run
        """
    )
    parser.add_argument(
        "stage",
        type=int,
        help="Stage number to check (e.g., 5 for stage 5)"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Filter errors by specific run ID (optional)"
    )

    args = parser.parse_args()

    success = check_errors(args.stage, args.run_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
