#!/usr/bin/env python3
"""
Rollback Script for Stage 9

This script allows non-coders to safely rollback Stage 9 data.

Usage:
    python3 rollback_stage_9.py --run-id RUN_ID [--confirm]

What it does:
  - Deletes all data from stage_9 table for the specified run_id
  - Provides clear, non-technical feedback
  - Requires confirmation before deleting
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from src.services.central_services.core.bigquery_client import get_bigquery_client
from shared.constants import get_full_table_id, TABLE_STAGE_9, TABLE_STAGE_10
from shared_validation import validate_table_id, validate_run_id
from google.cloud.bigquery import ScalarQueryParameter

def list_available_runs() -> bool:
    """List all available run IDs in Stage 9 table.

    This helps non-coders discover what run IDs exist so they can
    choose which one to rollback.

    Returns:
        True if successful, False otherwise
    """
    print("="*70)
    print("AVAILABLE RUN IDs IN STAGE 9")
    print("="*70)
    print("\nThis shows all the run IDs that exist in Stage 9.")
    print("Use these to decide which run to rollback.\n")

    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot list run IDs.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    stage_table = get_full_table_id(TABLE_STAGE_9)
    validated_table = validate_table_id(stage_table)

    try:
        query = f"""
        SELECT
            run_id,
            COUNT(*) as record_count,
            MIN(processed_at) as earliest_record,
            MAX(processed_at) as latest_record
        FROM `{validated_table}`
        GROUP BY run_id
        ORDER BY MAX(processed_at) DESC
        LIMIT 20
        """
        results = list(client.query(query).result())

        if not results:
            print("   ℹ️  No data found in Stage 9 table.")
            print("   What this means: Stage 9 has no runs to rollback.")
            return True

        print(f"Found {len(results)} run(s):\n")
        print("-"*70)
        print(f"{'Run ID':<40} {'Records':>10} {'Latest Record':<20}")
        print("-"*70)

        for row in results:
            latest = row.latest_record.strftime("%Y-%m-%d %H:%M") if row.latest_record else "Unknown"
            print(f"{row.run_id:<40} {row.record_count:>10,} {latest:<20}")

        print("-"*70)
        print("\nTo rollback a specific run, use:")
        print("   python3 rollback_stage_9.py --run-id YOUR_RUN_ID\n")
        return True

    except Exception as e:
        print(f"❌ ERROR: Could not list run IDs")
        print(f"   Problem: {e}")
        print("\n   What this means: There was an error querying the database.")
        print("   What to do: Check your BigQuery connection and try again.")
        return False


def rollback_stage_9(run_id: str, confirm: bool = False) -> bool:
    """Rollback Stage 9 data for a specific run_id.
    
    Args:
        run_id: Run ID to rollback
        confirm: If True, skip confirmation prompt
        
    Returns:
        True if rollback successful, False otherwise
    """
    print("="*70)
    print("ROLLBACK STAGE 9")
    print("="*70)
    print("\nThis script will delete Stage 9 data for a specific run.")
    print("You don't need to know how to code - just follow the prompts.\n")
    
    # Validate run_id
    try:
        validated_run_id = validate_run_id(run_id)
    except ValueError as e:
        print(f"❌ ERROR: Invalid run ID")
        print(f"   Problem: {e}")
        print("\n   What this means: The run ID you provided is not valid.")
        print("   What to do: Check the run ID and try again.")
        return False
    
    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot connect to the database.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False
    
    stage_table = get_full_table_id(TABLE_STAGE_9)
    validated_table = validate_table_id(stage_table)
    
    # Check how many records will be deleted
    print(f"\nChecking how many records will be deleted...")
    try:
        count_query = f"""
        SELECT COUNT(*) as cnt
        FROM `{validated_table}`
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
            print(f"   ℹ️  No records found for run_id: {validated_run_id}")
            print("   What this means: There's nothing to rollback for this run.")
            print("   What to do: The run may not have completed, or data was already deleted.")
            return True
        
        print(f"   ⚠️  Found {record_count:,} records that will be deleted")
    except Exception as e:
        print(f"   ❌ Error checking record count: {e}")
        print("   What this means: Cannot determine how many records will be deleted.")
        print("   What to do: Check your BigQuery connection and try again.")
        return False

    # FIX: Check for downstream dependencies before allowing rollback
    # If Stage 10 has already processed data from this run_id, rolling back Stage 9
    # would create orphaned records in Stage 10 and corrupt the pipeline
    print("\nChecking for data in later stages...")
    stage_10_table = get_full_table_id(TABLE_STAGE_10)
    try:
        validated_stage_10 = validate_table_id(stage_10_table)
        dep_query = f"""
        SELECT COUNT(*) as cnt
        FROM `{validated_stage_10}`
        WHERE run_id = @run_id
        """
        dep_job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("run_id", "STRING", validated_run_id)
            ]
        )
        dep_result = list(client.query(dep_query, job_config=dep_job_config).result())[0]

        if dep_result.cnt > 0:
            print(f"   ❌ CRITICAL WARNING: Found {dep_result.cnt:,} records in Stage 10 from this run!")
            print("\n   " + "="*60)
            print("   ROLLBACK BLOCKED - DOWNSTREAM DATA EXISTS")
            print("   " + "="*60)
            print(f"\n   What this means:")
            print(f"     Stage 10 has already processed {dep_result.cnt:,} records from run '{validated_run_id}'.")
            print(f"     If we delete Stage 9 data now, those Stage 10 records would become")
            print(f"     'orphaned' - their source data would be gone, corrupting the pipeline.")
            print(f"\n   What to do:")
            print(f"     1. First run the Stage 10 rollback for this run_id:")
            print(f"        python3 rollback_stage_10.py --run-id {validated_run_id}")
            print(f"     2. Then come back and run this Stage 9 rollback again.")
            print(f"\n   Why this matters:")
            print(f"     Data pipelines must be rolled back in reverse order (Stage 10, then Stage 9)")
            print(f"     to maintain data integrity. This is like unstacking blocks - you have to")
            print(f"     remove the top ones first.")
            print("\n   Rollback cancelled to prevent data corruption.")
            return False
        else:
            print("   ✅ No downstream data found in Stage 10. It is safe to proceed.")

    except Exception as e:
        # Check if the error is because the table doesn't exist
        if "Not found" in str(e) or "404" in str(e):
            print("   ✅ Stage 10 table does not exist yet. It is safe to proceed.")
        else:
            # FIX: FAIL-SAFE - Never allow bypass of data integrity check
            print(f"   ❌ ERROR: Could not verify if rollback is safe")
            print(f"   Technical details: {e}")
            print("\n   " + "="*60)
            print("   ROLLBACK BLOCKED - SAFETY CHECK FAILED")
            print("   " + "="*60)
            print("\n   What this means:")
            print("     The system cannot verify if Stage 10 has data from this run.")
            print("     Without this verification, rolling back could corrupt the pipeline.")
            print("\n   What to do:")
            print("     1. Check your BigQuery connection and permissions")
            print("     2. Contact support if the problem persists")
            print("     3. Do NOT attempt to manually delete data")
            print("\n   Why no override is allowed:")
            print("     Data integrity must be maintained at all costs. There is no")
            print("     'force' option because accidentally corrupting the pipeline")
            print("     could cause irreversible data loss.")
            print("\n   Rollback cancelled for your protection.")
            return False

    # Confirm deletion
    if not confirm:
        print(f"\n⚠️  WARNING: This will delete {record_count:,} records from Stage 9")
        print(f"   Run ID: {validated_run_id}")
        response = input("\n   Type 'yes' to confirm deletion: ")
        if response.lower() != 'yes':
            print("\n   Rollback cancelled.")
            return False
    
    # Perform deletion
    print(f"\nDeleting records...")
    try:
        delete_query = f"""
        DELETE FROM `{validated_table}`
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
            print(f"   ❌ Error during deletion: {job.errors}")
            print("   What this means: The deletion operation failed.")
            print("   What to do: Check the error details and try again, or contact support.")
            return False
        
        print(f"   ✅ Successfully deleted {record_count:,} records")
        print(f"\n✅ ROLLBACK COMPLETE")
        print("="*70)
        print(f"Stage 9 data for run_id '{validated_run_id}' has been deleted.")
        print("\nWhat this means: The data from this run has been removed.")
        print("What to do: You can now re-run Stage 9 if needed.")
        return True
        
    except Exception as e:
        print(f"   ❌ Error during deletion: {e}")
        print("   What this means: The deletion operation failed.")
        print("   What to do: Check the error details and try again, or contact support.")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rollback Stage 9 data for a specific run_id"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run ID to rollback"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution)"
    )
    parser.add_argument(
        "--list-runs",
        action="store_true",
        help="List all available run IDs (use this first to find your run ID)"
    )

    args = parser.parse_args()

    # Handle --list-runs option
    if args.list_runs:
        success = list_available_runs()
        sys.exit(0 if success else 1)

    # Require --run-id if not listing runs
    if not args.run_id:
        print("❌ ERROR: --run-id is required for rollback")
        print("\n   What this means: You need to specify which run to rollback.")
        print("   What to do:")
        print("      1. First, run: python3 rollback_stage_9.py --list-runs")
        print("      2. Find the run ID you want to rollback")
        print("      3. Run: python3 rollback_stage_9.py --run-id YOUR_RUN_ID")
        sys.exit(1)

    success = rollback_stage_9(args.run_id, args.confirm)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
