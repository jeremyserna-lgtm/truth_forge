#!/usr/bin/env python3
"""
Universal Rollback Script for Claude Code Pipeline

This script allows non-coders to safely rollback any stage's data.

Usage:
    python3 rollback.py --stage STAGE_NUMBER --run-id RUN_ID [--confirm]

Examples:
    # Rollback Stage 7 data for a specific run
    python3 pipelines/claude_code/scripts/shared/rollback.py --stage 7 --run-id run_2026_01_23

    # Rollback with automatic confirmation (no prompt)
    python3 pipelines/claude_code/scripts/shared/rollback.py --stage 7 --run-id run_2026_01_23 --confirm

What it does:
  - Deletes all data from the specified stage table for the given run_id
  - Provides clear, non-technical feedback
  - Requires confirmation before deleting
  - Works for any stage (0-16)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add shared module to path
shared_path = Path(__file__).parent.parent
sys.path.insert(0, str(shared_path))

from google.cloud import bigquery
from google.cloud.bigquery import ScalarQueryParameter

# Stage descriptions for user-friendly output
STAGE_DESCRIPTIONS = {
    0: "Raw Import",
    1: "Conversation Parsing",
    2: "Message Extraction",
    3: "Gate Validation",
    4: "Deduplication",
    5: "L8 Conversation + L7 Compaction Segment Creation",
    6: "L6 Turn Creation",
    7: "L5 Message Creation",
    8: "L4 Sentence Creation",
    9: "L3 Span Creation (NER)",
    10: "L2 Word Creation (Atomic Level)",
    11: "Parent Linking",
    12: "Count Rollups",
    13: "Validation",
    14: "Entity Promotion",
    15: "Final Validation",
    16: "Final Destination (entity_unified)",
}


def validate_stage(stage: int) -> int:
    """Validate stage number is in valid range."""
    if not 0 <= stage <= 16:
        raise ValueError(f"Stage must be 0-16, got {stage}")
    return stage


def validate_run_id(run_id: str) -> str:
    """Validate run_id is not empty and is a reasonable format."""
    if not run_id or not run_id.strip():
        raise ValueError("Run ID cannot be empty")

    run_id = run_id.strip()

    # Basic sanity check - run_id should be alphanumeric with underscores/dashes
    import re
    if not re.match(r'^[a-zA-Z0-9_\-]+$', run_id):
        raise ValueError(f"Run ID contains invalid characters: {run_id}")

    return run_id


def get_table_for_stage(stage: int) -> str:
    """Get the fully qualified table ID for a stage."""
    try:
        from shared.constants import get_stage_table, get_full_table_id
        table_name = get_stage_table(stage)
        return get_full_table_id(table_name)
    except ImportError:
        # Fallback if imports fail
        project_id = "flash-clover-464719-g1"
        dataset_id = "spine"
        if stage == 16:
            table_name = "entity_unified"
        else:
            table_name = f"claude_code_stage_{stage}"
        return f"{project_id}.{dataset_id}.{table_name}"


def get_bigquery_client():
    """Get BigQuery client."""
    try:
        from truth_forge.core.bigquery_client import get_bigquery_client as get_bq
        return get_bq().client
    except ImportError:
        try:
            from src.services.central_services.core.bigquery_client import get_bigquery_client as get_bq
            return get_bq().client
        except ImportError:
            # Fallback to direct client creation
            return bigquery.Client()


def rollback_stage(stage: int, run_id: str, confirm: bool = False) -> bool:
    """Rollback stage data for a specific run_id.

    Args:
        stage: Stage number (0-16)
        run_id: Run ID to rollback
        confirm: If True, skip confirmation prompt

    Returns:
        True if rollback successful, False otherwise
    """
    stage_desc = STAGE_DESCRIPTIONS.get(stage, f"Stage {stage}")

    print("=" * 70)
    print(f"ROLLBACK STAGE {stage} - {stage_desc}")
    print("=" * 70)
    print(f"\nThis script will delete Stage {stage} data for a specific run.")
    print("You don't need to know how to code - just follow the prompts.\n")

    # Validate inputs
    try:
        validated_stage = validate_stage(stage)
    except ValueError as e:
        print(f"Error: Invalid stage number")
        print(f"   Problem: {e}")
        print("\n   What this means: The stage number you provided is not valid.")
        print("   What to do: Use a stage number between 0 and 16.")
        return False

    try:
        validated_run_id = validate_run_id(run_id)
    except ValueError as e:
        print(f"Error: Invalid run ID")
        print(f"   Problem: {e}")
        print("\n   What this means: The run ID you provided is not valid.")
        print("   What to do: Check the run ID and try again.")
        return False

    # Connect to BigQuery
    try:
        client = get_bigquery_client()
    except Exception as e:
        print(f"Error: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot connect to the database.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # Get table ID
    table_id = get_table_for_stage(validated_stage)

    # Check if table exists
    print(f"Checking table: {table_id}")
    try:
        client.get_table(table_id)
    except Exception as e:
        print(f"Error: Table does not exist")
        print(f"   Table: {table_id}")
        print("\n   What this means: Stage {stage} hasn't been run yet, or the table was deleted.")
        print("   What to do: Nothing to rollback - the table doesn't exist.")
        return True  # Not really an error, just nothing to do

    # Check how many records will be deleted
    print(f"\nChecking how many records will be deleted...")
    try:
        count_query = f"""
        SELECT COUNT(*) as cnt
        FROM `{table_id}`
        WHERE run_id = @run_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("run_id", "STRING", validated_run_id)
            ]
        )
        count_result = list(client.query(count_query, job_config=job_config).result())[0]
        record_count = count_result.cnt

        if record_count == 0:
            print(f"   No records found for run_id: {validated_run_id}")
            print("   What this means: There's nothing to rollback for this run.")
            print("   What to do: The run may not have completed, or data was already deleted.")
            return True

        print(f"   Found {record_count:,} records that will be deleted")
    except Exception as e:
        print(f"   Error checking record count: {e}")
        print("   What this means: Cannot determine how many records will be deleted.")
        print("   What to do: Check your BigQuery connection and try again.")
        return False

    # Confirm deletion
    if not confirm:
        print(f"\nWARNING: This will delete {record_count:,} records from Stage {stage}")
        print(f"   Table: {table_id}")
        print(f"   Run ID: {validated_run_id}")
        print(f"   Stage: {stage_desc}")
        response = input("\n   Type 'yes' to confirm deletion: ")
        if response.lower() != 'yes':
            print("\n   Rollback cancelled.")
            return False

    # Perform deletion
    print(f"\nDeleting records...")
    try:
        delete_query = f"""
        DELETE FROM `{table_id}`
        WHERE run_id = @run_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("run_id", "STRING", validated_run_id)
            ]
        )
        job = client.query(delete_query, job_config=job_config)
        job.result()  # Wait for completion

        if job.errors:
            print(f"   Error during deletion: {job.errors}")
            print("   What this means: The deletion operation failed.")
            print("   What to do: Check the error details and try again.")
            return False

        print(f"   Successfully deleted {record_count:,} records")
        print(f"\nROLLBACK COMPLETE")
        print("=" * 70)
        print(f"Stage {stage} ({stage_desc}) data for run_id '{validated_run_id}' has been deleted.")
        print("\nWhat this means: The data from this run has been removed.")
        print(f"What to do: You can now re-run Stage {stage} if needed.")
        return True

    except Exception as e:
        print(f"   Error during deletion: {e}")
        print("   What this means: The deletion operation failed.")
        print("   What to do: Check the error details and try again.")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rollback any stage's data for a specific run_id",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Rollback Stage 7 (L5 Message Creation)
    python3 rollback.py --stage 7 --run-id run_2026_01_23

    # Rollback Stage 10 (L2 Word Creation) with confirmation
    python3 rollback.py --stage 10 --run-id run_2026_01_23 --confirm

Stage Descriptions:
    0:  Raw Import
    1:  Conversation Parsing
    2:  Message Extraction
    3:  Gate Validation
    4:  Deduplication
    5:  L8 Conversation + L7 Compaction Segment Creation
    6:  L6 Turn Creation
    7:  L5 Message Creation
    8:  L4 Sentence Creation
    9:  L3 Span Creation (NER)
    10: L2 Word Creation (Atomic Level)
    11: Parent Linking
    12: Count Rollups
    13: Validation
    14: Entity Promotion
    15: Final Validation
    16: Final Destination (entity_unified)
        """
    )
    parser.add_argument(
        "--stage",
        type=int,
        required=True,
        help="Stage number to rollback (0-16)"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        required=True,
        help="Run ID to rollback (required)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution)"
    )

    args = parser.parse_args()

    success = rollback_stage(args.stage, args.run_id, args.confirm)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
