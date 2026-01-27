#!/usr/bin/env python3
"""
Verification Script for Stage 3

This script allows non-coders to verify that Stage 3 is working correctly.

Usage:
    python3 verify_stage_3.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - Entity IDs generated
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from src.services.central_services.core.bigquery_client import get_bigquery_client
from shared.constants import get_full_table_id, TABLE_STAGE_3
from shared_validation import validate_table_id, validate_run_id

def verify_stage_3(run_id: str = None) -> bool:
    """Verify Stage 3 is working correctly.

    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 3")
    print("="*70)
    print("\nThis script checks if Stage 3 worked correctly.")
    print("You don't need to know how to code - just run this and read the results.\n")

    all_checks_passed = True

    # FIX: Validate run_id if provided to prevent injection attacks
    validated_run_id = None
    if run_id:
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
        print("\n   What this means: The system cannot check if Stage 3 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False
    

    stage_table = get_full_table_id(TABLE_STAGE_3)
    # FIX: Validate table ID to prevent SQL injection
    validated_table = validate_table_id(stage_table)

    # Check 1: Table exists and has data
    print("\n1. Checking if the table exists and has data...")
    try:
        table = client.get_table(validated_table)
        row_count = table.num_rows
        print(f"   ✅ Table exists")
        print(f"   ✅ Table has {row_count:,} records")
        
        if row_count == 0:
            print("   ⚠️  WARNING: Table exists but has no data")
            print("   What this means: Stage 3 ran but didn't create any records.")
            print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 3 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 3 first, then check for errors.")
        return False


    # Check 2: Entity IDs generated and valid (run_id-aware to avoid false positives on re-runs)
    print("\n2. Checking if entity IDs were generated...")
    try:
        # FIX: Make query run_id-aware to avoid false positives when pipeline is re-run
        # Only check entity_ids for the specific run_id if provided, otherwise check all
        if validated_run_id:
            # Use parameterized query for run_id to prevent SQL injection
            from google.cloud.bigquery import ScalarQueryParameter
            query = f"""
            SELECT 
                COUNT(*) as total,
                COUNTIF(entity_id IS NULL) as null_entity_ids,
                COUNTIF(entity_id = '') as empty_entity_ids,
                COUNT(DISTINCT entity_id) as unique_entity_ids
            FROM `{validated_table}`
            WHERE run_id = @run_id
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("run_id", "STRING", validated_run_id)
                ]
            )
            result = list(client.query(query, job_config=job_config).result())[0]
        else:
            # Check all records (for initial verification)
            query = f"""
            SELECT 
                COUNT(*) as total,
                COUNTIF(entity_id IS NULL) as null_entity_ids,
                COUNTIF(entity_id = '') as empty_entity_ids,
                COUNT(DISTINCT entity_id) as unique_entity_ids
            FROM `{validated_table}`
            """
            result = list(client.query(query).result())[0]
        
        if result.null_entity_ids > 0 or result.empty_entity_ids > 0:
            print(f"   ❌ Found {result.null_entity_ids + result.empty_entity_ids} records without entity IDs")
            print("   What this means: Some records don't have entity IDs assigned.")
            print("   What to do: This is a critical error - re-run Stage 3.")
            all_checks_passed = False
        elif result.total != result.unique_entity_ids:
            # FIX: Only warn if checking specific run_id, otherwise duplicates across runs are expected
            if validated_run_id:
                print(f"   ⚠️  Found duplicate entity IDs within this run")
                print(f"   What this means: {result.total - result.unique_entity_ids} records share entity IDs in the same run.")
                print("   What to do: This is a data quality issue - contact support.")
                all_checks_passed = False
            else:
                print(f"   ℹ️  Note: Found {result.total - result.unique_entity_ids} duplicate entity IDs across all runs")
                print("   What this means: This is normal if the pipeline was re-run on the same data.")
                print("   What to do: Use --run-id to check a specific run, or this is expected behavior.")
        else:
            print(f"   ✅ All {result.total:,} records have unique entity IDs")
    except Exception as e:
        print(f"   ❌ Error checking entity IDs: {e}")
        all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 3 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 3 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 3"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_3(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
