#!/usr/bin/env python3
"""
Verification Script for Stage 0

This script allows non-coders to verify that Stage 0 is working correctly.

Usage:
    python3 verify_stage_0.py

What it checks:
  1. Manifest file exists (discovery_manifest.json)
  2. go_no_go decision is GO
  3. Files were discovered (file count > 0)
  4. Messages were found (message count > 0)

If any check fails, you'll get:
  - A clear description of what went wrong
  - What that means in plain English
  - What you should do to fix it
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
_script_dir = Path(__file__).parent
_scripts_dir = _script_dir.parent
_pipeline_dir = _scripts_dir.parent
_project_root = _pipeline_dir.parent.parent

sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_scripts_dir))

# Import centralized constant for manifest path
from shared.constants import DEFAULT_MANIFEST_PATH as _DEFAULT_MANIFEST_PATH_STR

# Convert to Path for this script (constants stores as string for JSON compatibility)
DEFAULT_MANIFEST_PATH = _project_root / _DEFAULT_MANIFEST_PATH_STR


def verify_stage_0(manifest_path: Path = None) -> bool:
    """Verify Stage 0 is working correctly.

    Args:
        manifest_path: Path to the discovery manifest. Defaults to staging/discovery_manifest.json

    Returns:
        True if all checks pass, False otherwise
    """
    print("=" * 70)
    print("VERIFYING STAGE 0: Assessment & Discovery")
    print("=" * 70)
    print("\nThis script checks if Stage 0 worked correctly.")
    print("You don't need to know how to code - just run this and read the results.\n")

    all_checks_passed = True
    manifest_path = manifest_path or DEFAULT_MANIFEST_PATH
    manifest = None  # Will be loaded in check 1

    # Check 1: Manifest exists
    print("1. Checking: Discovery manifest exists...")
    print(f"   Looking for: {manifest_path}")

    if not manifest_path.exists():
        print("   ❌ FAILED: Manifest file not found")
        print("")
        print("   What this means:")
        print("     Stage 0 hasn't run yet, or it failed before creating a manifest.")
        print("     The manifest is Stage 0's output - it lists everything discovered.")
        print("")
        print("   What to do:")
        print("     1. Run Stage 0 first:")
        print("        python3 pipelines/claude_code/scripts/stage_0/claude_code_stage_0.py")
        print("     2. Check if it completed without errors")
        print("     3. Run this verification script again")
        return False

    # Load manifest
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        print("   ✅ PASSED: Manifest file found and readable")
    except json.JSONDecodeError as e:
        print(f"   ❌ FAILED: Manifest file is corrupted (invalid JSON)")
        print("")
        print("   What this means:")
        print("     The manifest file exists but is damaged or incomplete.")
        print("     This usually means Stage 0 was interrupted while writing.")
        print("")
        print("   What to do:")
        print("     1. Delete the corrupted manifest file")
        print("     2. Run Stage 0 again")
        print("     3. Make sure Stage 0 completes fully before stopping it")
        print(f"\n   Technical error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ FAILED: Could not read manifest file")
        print(f"\n   Technical error: {e}")
        return False

    # Check 2: go_no_go is GO
    print("\n2. Checking: Assessment result is GO...")

    go_no_go = manifest.get("go_no_go", "UNKNOWN")

    if go_no_go.startswith("GO"):
        print(f"   ✅ PASSED: Result is '{go_no_go}'")
    elif go_no_go.startswith("CAUTION"):
        print(f"   ⚠️ WARNING: Result is '{go_no_go}'")
        print("")
        print("   What this means:")
        print("     Stage 0 found the data, but there were some issues (like parse errors).")
        print("     The pipeline can still proceed, but you should review the issues.")
        print("")
        print("   What to do:")
        print("     1. Look at the recommendations in the manifest")
        print("     2. Decide if the issues are acceptable")
        print("     3. You can proceed to Stage 1 if you choose")
        # CAUTION is not a failure, but we note it
    else:
        print(f"   ❌ FAILED: Result is '{go_no_go}'")
        print("")
        print("   What this means:")
        print("     Stage 0 determined the source data isn't ready for processing.")
        print("     Common reasons: no files found, no messages found, too many errors.")
        print("")
        print("   What to do:")
        print("     1. Check the 'recommendations' in the manifest for specific issues")
        print("     2. Fix the underlying problem (source directory, file format, etc.)")
        print("     3. Run Stage 0 again")
        all_checks_passed = False

    # Check 3: Files were discovered
    print("\n3. Checking: Source files were discovered...")

    discovery = manifest.get("discovery", {})
    files_processed = discovery.get("files_processed", 0)

    if files_processed > 0:
        print(f"   ✅ PASSED: Found {files_processed} JSONL file(s)")

        # Show files per folder breakdown
        files_per_folder = discovery.get("files_per_folder", {})
        if files_per_folder:
            print("   Breakdown by folder:")
            for folder, info in list(files_per_folder.items())[:5]:
                count = info.get("file_count", 0) if isinstance(info, dict) else info
                print(f"     - {folder or '.'}: {count} file(s)")
            if len(files_per_folder) > 5:
                print(f"     ... and {len(files_per_folder) - 5} more folders")
    else:
        print("   ❌ FAILED: No JSONL files found")
        print("")
        print("   What this means:")
        print("     Stage 0 couldn't find any JSONL files in the source directory.")
        print("     Either the directory is empty or the files have a different extension.")
        print("")
        print("   What to do:")
        print("     1. Check that your source directory contains .jsonl files")
        source_path = manifest.get("source", {}).get("path", "unknown")
        print(f"     2. Source directory used: {source_path}")
        print("     3. If files are elsewhere, run Stage 0 with --source-dir <path>")
        all_checks_passed = False

    # Check 4: Messages were found
    print("\n4. Checking: Messages were found in files...")

    messages_processed = discovery.get("messages_processed", 0)

    if messages_processed > 0:
        print(f"   ✅ PASSED: Found {messages_processed:,} messages")

        # Show counts breakdown
        counts = discovery.get("counts", {})
        if counts:
            thinking = counts.get("thinking_blocks", 0)
            text = counts.get("text_blocks", 0)
            tool_calls = counts.get("tool_calls", 0)
            tool_results = counts.get("tool_results", 0)

            print("   Message breakdown:")
            if thinking > 0:
                print(f"     - Thinking blocks: {thinking:,} (AI's internal reasoning)")
            if text > 0:
                print(f"     - Text blocks: {text:,} (visible responses)")
            if tool_calls > 0:
                print(f"     - Tool calls: {tool_calls:,} (when AI used tools)")
            if tool_results > 0:
                print(f"     - Tool results: {tool_results:,} (tool outputs)")
    else:
        print("   ❌ FAILED: No messages found")
        print("")
        print("   What this means:")
        print("     Stage 0 found files, but they appear to be empty or malformed.")
        print("     Each line in a JSONL file should be a valid JSON message.")
        print("")
        print("   What to do:")
        print("     1. Check one of the source files manually")
        print("     2. Make sure each line is valid JSON")
        print("     3. Check for encoding issues (should be UTF-8)")
        all_checks_passed = False

    # Check 5: Show date range if available
    print("\n5. Checking: Temporal coverage...")

    date_range = discovery.get("date_range", {})
    earliest = date_range.get("earliest")
    latest = date_range.get("latest")

    if earliest and latest:
        # Try to format nicely
        try:
            earliest_short = earliest[:10] if len(earliest) >= 10 else earliest
            latest_short = latest[:10] if len(latest) >= 10 else latest
            print(f"   ✅ PASSED: Data covers {earliest_short} to {latest_short}")
        except:
            print(f"   ✅ PASSED: Date range found")
    else:
        print("   ⚠️ INFO: No timestamp data found")
        print("     (This is okay - timestamps are optional)")

    # Summary
    print("\n" + "=" * 70)

    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 0 completed successfully!")
        print("=" * 70)
        print("\nWhat this means:")
        print("  Stage 0 discovered your source data and it's ready for processing.")
        print("")
        print("What to do next:")
        print("  Run Stage 1 to extract and parse the data:")
        print("    python3 pipelines/claude_code/scripts/stage_1/claude_code_stage_1.py")
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("=" * 70)
        print("\nWhat to do:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each failed check")
        print("  3. Fix the issues")
        print("  4. Run Stage 0 again if needed")
        print("  5. Run this verification script again to confirm fixes")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Stage 0: Check if assessment completed correctly",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 verify_stage_0.py                    # Check default manifest location
  python3 verify_stage_0.py --manifest /path   # Check specific manifest file

This verification script checks:
  - Discovery manifest exists and is valid JSON
  - Assessment result is GO (data is ready)
  - Files were discovered
  - Messages were found

If any check fails, you'll get clear instructions on what to do.
        """
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=f"Path to discovery manifest (default: {DEFAULT_MANIFEST_PATH})"
    )

    args = parser.parse_args()

    manifest_path = args.manifest or DEFAULT_MANIFEST_PATH

    success = verify_stage_0(manifest_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
