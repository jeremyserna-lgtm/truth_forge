#!/usr/bin/env python3
"""
Verification Script for Stage 7

This script allows non-coders to verify that Stage 7 is working correctly.

Usage:
    python3 verify_stage_7.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - L5 Message entities created correctly
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from google.cloud.bigquery import ScalarQueryParameter, QueryJobConfig
from src.services.central_services.core.bigquery_client import get_bigquery_client
from shared.constants import get_full_table_id, TABLE_STAGE_7, TABLE_STAGE_6
from shared_validation import validate_table_id, validate_run_id

def verify_stage_7(run_id: str = None) -> bool:
    """Verify Stage 7 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 7")
    print("="*70)
    print("\nThis script checks if Stage 7 worked correctly.")
    print("You don't need to know how to code - just run this and read the results.\n")

    all_checks_passed = True

    # FIX: Validate run_id if provided (security)
    validated_run_id = None
    if run_id:
        try:
            validated_run_id = validate_run_id(run_id)
            print(f"📋 Verifying specific run: {validated_run_id}")
        except ValueError as e:
            print(f"❌ ERROR: Invalid run ID")
            print(f"   Problem: {e}")
            print("\n   What this means: The run ID you provided is not valid.")
            print("   What to do: Check the run ID and try again.")
            return False
    else:
        print("📋 No --run-id specified. Verifying ALL data in the table.")
        print("   (For a specific run, use: --run-id YOUR_RUN_ID)")

    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot check if Stage 7 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # FIX: Validate table ID for SQL injection protection
    stage_table = get_full_table_id(TABLE_STAGE_7)
    validated_table = validate_table_id(stage_table)
    stage_6_table = get_full_table_id(TABLE_STAGE_6)
    validated_stage_6 = validate_table_id(stage_6_table)

    # Build parameterized query configuration for run_id filtering
    # SECURITY: Using parameterized queries to prevent SQL injection
    query_params = []
    where_clause = ""
    job_config = None

    if validated_run_id:
        # Use parameterized query to prevent SQL injection
        where_clause = "WHERE run_id = @run_id"
        query_params = [ScalarQueryParameter("run_id", "STRING", validated_run_id)]
        job_config = QueryJobConfig(query_parameters=query_params)
    
    # Check 1: Table exists and has data (for specified run_id if provided)
    print("\n1. Checking if the table exists and has data...")
    try:
        table = client.get_table(validated_table)
        print(f"   ✅ Table exists")

        # Count records (filtered by run_id if provided)
        # SECURITY: Using parameterized query with job_config
        count_query = f"SELECT COUNT(*) as cnt FROM `{validated_table}` {where_clause}"
        result = list(client.query(count_query, job_config=job_config).result())[0]
        row_count = result.cnt

        if validated_run_id:
            print(f"   Records for run_id '{validated_run_id}': {row_count:,}")
        else:
            print(f"   Total records in table: {row_count:,}")

        if row_count == 0:
            if validated_run_id:
                print(f"   ❌ FAILED: No records found for run_id '{validated_run_id}'")
                print("   What this means: The specified run either failed, produced no data, or the ID is incorrect.")
                print("   What to do:")
                print("      1. Check if Stage 7 ran successfully for this run_id")
                print("      2. Verify the run_id is correct")
                print("      3. Check Stage 7 logs for errors")
            else:
                print("   ⚠️  WARNING: Table exists but has no data")
                print("   What this means: Stage 7 ran but didn't create any records.")
                print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
        else:
            print(f"   ✅ Found {row_count:,} records to verify")
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 7 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 7 first, then check for errors.")
        return False


    # Check 2: L5 Message entities have correct level
    print("\n2. Checking that all records are Level 5 entities (L5 Messages)...")
    try:
        # SECURITY: Using parameterized query with job_config and validated_table
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(level = 5) as level_5_count,
            COUNTIF(level != 5) as wrong_level_count
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.wrong_level_count > 0:
            print(f"   ❌ Found {result.wrong_level_count} records with wrong level")
            print("   What this means: Some records are not Level 5 (Message) as they should be.")
            print("   What to do: This is a data corruption issue - contact support.")
            all_checks_passed = False
        else:
            print(f"   ✅ All {result.total:,} records are Level 5 (Message) entities")
    except Exception as e:
        print(f"   ❌ Error checking levels: {e}")
        all_checks_passed = False

    # Check 3: Parent links are valid (point to L6 turns)
    print("\n3. Checking that message parent links point to valid turns...")
    try:
        # SECURITY: Using parameterized query with job_config and validated tables
        query = f"""
        SELECT
            COUNT(*) as total_messages,
            COUNTIF(parent_id IS NULL) as null_parents,
            COUNTIF(parent_id NOT IN (SELECT entity_id FROM `{validated_stage_6}`)) as orphaned_messages
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.null_parents > 0:
            print(f"   ❌ Found {result.null_parents} messages with no parent")
            print("   What this means: Some messages don't know which turn they belong to.")
            print("   What to do: This is a data quality issue - run Stage 7 again.")
            all_checks_passed = False
        elif result.orphaned_messages > 0:
            print(f"   ❌ Found {result.orphaned_messages} messages pointing to non-existent turns")
            print("   What this means: Some messages reference turns that don't exist.")
            print("   What to do: Run Stage 6 first to create turns, then run Stage 7.")
            all_checks_passed = False
        else:
            print(f"   ✅ All {result.total_messages:,} messages have valid parent links")
    except Exception as e:
        print(f"   ❌ Error checking parent links: {e}")
        all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 7 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 7 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 7"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_7(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
