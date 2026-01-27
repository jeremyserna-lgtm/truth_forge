#!/usr/bin/env python3
"""
Verification Script for Stage 15

This script allows non-coders to verify that Stage 15 is working correctly.

Usage:
    python3 verify_stage_15.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - Validation status assigned
  - Validation scores (if available)

NO CODING KNOWLEDGE REQUIRED:
  - Just run this script
  - Read the results
  - Follow the "What to do" instructions if there are problems
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
from shared.constants import get_full_table_id, TABLE_STAGE_15
from shared_validation import validate_table_id, validate_run_id

def verify_stage_15(run_id: str = None) -> bool:
    """Verify Stage 15 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 15 - Final Validation")
    print("="*70)
    print("\nThis script checks if Stage 15 worked correctly.")
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
        print("\n   What this means: The system cannot check if Stage 15 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # FIX: Validate table ID for SQL injection protection
    stage_table = get_full_table_id(TABLE_STAGE_15)
    validated_table = validate_table_id(stage_table)

    # Build parameterized query configuration for run_id filtering
    # SECURITY: Using parameterized queries to prevent SQL injection
    query_params = []
    where_clause = ""
    job_config = None

    if validated_run_id:
        where_clause = "WHERE run_id = @run_id"
        query_params = [ScalarQueryParameter("run_id", "STRING", validated_run_id)]
        job_config = QueryJobConfig(query_parameters=query_params)

    # Check 1: Table exists and has data
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
                print("      1. Check if Stage 15 ran successfully for this run_id")
                print("      2. Verify the run_id is correct")
                print("      3. Check Stage 15 logs for errors")
            else:
                print("   ⚠️  WARNING: Table exists but has no data")
                print("   What this means: Stage 15 ran but didn't create any records.")
                print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
        else:
            print(f"   ✅ Found {row_count:,} records to verify")
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 15 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 15 first, then check for errors.")
        return False


    # Check 2: Validation status assigned (comprehensive check)
    print("\n2. Checking if validation status was assigned...")
    try:
        # SECURITY: Using parameterized query with validated table and job_config
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(validation_status IS NOT NULL) as has_status,
            COUNTIF(validation_status = 'PASSED') as passed_count,
            COUNTIF(validation_status = 'WARNING') as warning_count,
            COUNTIF(validation_status = 'FAILED') as failed_count,
            COUNT(DISTINCT validation_status) as unique_statuses
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.has_status == 0:
            print("   ⚠️  No records have validation_status assigned")
            print("   What this means: Stage 15 may not have assigned validation statuses.")
            print("   What to do: Check if validation_status field exists, re-run Stage 15 if needed.")
            all_checks_passed = False
        else:
            print(f"   ✅ {result.has_status:,} records have validation status assigned")
            print(f"   ✅ Found {result.unique_statuses} different validation statuses")
            if result.passed_count > 0:
                print(f"      - {result.passed_count:,} records PASSED validation")
            if result.warning_count > 0:
                print(f"      - {result.warning_count:,} records have WARNINGS")
            if result.failed_count > 0:
                print(f"      - ⚠️  {result.failed_count:,} records FAILED validation")
                print("      What this means: Some entities did not pass validation.")
                print("      What to do: Review Stage 15 logs to see why validation failed.")
                all_checks_passed = False
    except Exception as e:
        if "validation_status" in str(e).lower():
            print("   ⚠️  validation_status field may not exist")
            print("   What this means: Stage 15 may not create this field.")
            print("   What to do: Check Stage 15 documentation for expected fields.")
            all_checks_passed = False
        else:
            print(f"   ❌ Error checking validation status: {e}")
            all_checks_passed = False
    
    # Check 3: Validation scores (if score field exists)
    print("\n3. Checking validation scores...")
    try:
        # SECURITY: Using parameterized query with validated table and job_config
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(validation_score IS NOT NULL) as has_score,
            AVG(validation_score) as avg_score,
            MIN(validation_score) as min_score,
            MAX(validation_score) as max_score
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.has_score > 0:
            print(f"   ✅ {result.has_score:,} records have validation scores")
            print(f"   ✅ Average score: {result.avg_score:.1f} (min: {result.min_score}, max: {result.max_score})")
            if result.avg_score < 70:
                print("   ⚠️  Average validation score is below 70")
                print("   What this means: Many entities have low validation scores.")
                print("   What to do: Review Stage 15 logs to see what's causing low scores.")
        else:
            print("   ℹ️  No validation scores found (field may not exist)")
    except Exception as e:
        if "validation_score" in str(e).lower():
            print("   ℹ️  validation_score field may not exist (this is okay)")
        else:
            print(f"   ⚠️  Could not check validation scores: {e}")

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 15 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 15 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 15"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_15(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
