#!/usr/bin/env python3
"""
Rollback Script for Stage 0

This script allows non-coders to safely rollback Stage 0 output.

Usage:
    python3 rollback_stage_0.py [--confirm]

What it does:
  - Removes the discovery manifest file
  - Shows you what will be deleted before deleting
  - Requires confirmation before deleting (unless --confirm is used)

Stage 0 only creates a manifest file - it doesn't write to BigQuery.
This is the safest rollback: just delete one file and re-run.
"""

import argparse
import sys
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


def rollback_stage_0(manifest_path: Path = None, confirm: bool = False) -> bool:
    """Rollback Stage 0 by removing the discovery manifest.

    Args:
        manifest_path: Path to the manifest file. Defaults to staging/discovery_manifest.json
        confirm: If True, skip confirmation prompt

    Returns:
        True if rollback successful (or nothing to rollback), False on error
    """
    print("=" * 70)
    print("ROLLBACK STAGE 0: Discovery")
    print("=" * 70)
    print("\nThis script will remove the Stage 0 discovery manifest.")
    print("You don't need to know how to code - just follow the prompts.\n")

    manifest_path = manifest_path or DEFAULT_MANIFEST_PATH

    # Check if manifest exists
    print(f"1. Checking: Does manifest exist?")
    print(f"   Looking for: {manifest_path}")

    if not manifest_path.exists():
        print("   ℹ️ Manifest file not found")
        print("")
        print("   What this means:")
        print("     Stage 0 hasn't run yet, or the manifest was already deleted.")
        print("     There's nothing to rollback.")
        print("")
        print("   What to do:")
        print("     You can run Stage 0 fresh whenever you're ready.")
        return True

    # Get file info
    try:
        file_size = manifest_path.stat().st_size
        print(f"   ✅ Found manifest file ({file_size:,} bytes)")
    except Exception as e:
        print(f"   ❌ Error reading file info: {e}")
        return False

    # Confirm deletion
    if not confirm:
        print(f"\n⚠️ WARNING: This will delete the discovery manifest file")
        print(f"   Path: {manifest_path}")
        print("")
        print("   What this means:")
        print("     - Stage 0's discovery results will be removed")
        print("     - Downstream stages won't be able to proceed until Stage 0 runs again")
        print("     - No source data is affected (Stage 0 only reads, never modifies)")
        print("")
        response = input("   Type 'yes' to confirm deletion: ")
        if response.lower() != "yes":
            print("\n   Rollback cancelled.")
            return False

    # Perform deletion
    print("\n2. Deleting manifest file...")
    try:
        manifest_path.unlink()
        print(f"   ✅ Successfully deleted: {manifest_path.name}")
    except PermissionError:
        print(f"   ❌ Permission denied")
        print("")
        print("   What this means:")
        print("     You don't have permission to delete this file.")
        print("")
        print("   What to do:")
        print("     1. Check file permissions")
        print("     2. Try running with appropriate permissions")
        return False
    except Exception as e:
        print(f"   ❌ Error deleting file: {e}")
        return False

    print("")
    print("=" * 70)
    print("✅ ROLLBACK COMPLETE")
    print("=" * 70)
    print("")
    print("What happened:")
    print("  - The discovery manifest was deleted")
    print("  - No source data was affected (Stage 0 only reads source files)")
    print("")
    print("What to do next:")
    print("  - Run Stage 0 again when you're ready:")
    print("    python3 pipelines/claude_code/scripts/stage_0/claude_code_stage_0.py")
    return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rollback Stage 0 by removing the discovery manifest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
What Stage 0 does:
  Stage 0 reads source files and creates a discovery manifest.
  It NEVER modifies source data - it only reads.

What rollback does:
  Removes the manifest file so Stage 0 can be re-run fresh.
  This is completely safe - no data is lost.

Examples:
  python3 rollback_stage_0.py                 # Delete manifest (with confirmation)
  python3 rollback_stage_0.py --confirm       # Delete manifest (no confirmation)
        """,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help=f"Path to manifest file (default: {DEFAULT_MANIFEST_PATH})",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution)",
    )

    args = parser.parse_args()

    manifest_path = args.manifest or DEFAULT_MANIFEST_PATH

    success = rollback_stage_0(manifest_path, args.confirm)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
