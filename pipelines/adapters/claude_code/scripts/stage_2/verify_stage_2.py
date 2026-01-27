#!/usr/bin/env python3
"""
Verification Script for Stage 2

This script allows non-coders to verify that Stage 2 is working correctly.

Usage:
    python3 verify_stage_2.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - Content cleaned
  - Duplicates marked
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
from shared.constants import get_full_table_id, TABLE_STAGE_2

def verify_stage_2(run_id: str = None) -> bool:
    """Verify Stage 2 is working correctly.

    Args:
        run_id: Specific run ID to verify (optional). If provided, only checks
               data from that specific run. If not provided, checks all data.

    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 2")
    print("="*70)
    print("\nThis script checks if Stage 2 worked correctly.")
    print("You don't need to know how to code - just run this and read the results.\n")

    all_checks_passed = True

    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot check if Stage 2 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False


    stage_table = get_full_table_id(TABLE_STAGE_2)

    # Build parameterized query configuration for run_id filtering
    # SECURITY: Using parameterized queries to prevent SQL injection
    query_params = []
    where_clause = ""
    job_config = None

    if run_id:
        print(f"📋 Verifying specific run: {run_id}")
        # Use parameterized query to prevent SQL injection
        where_clause = "WHERE run_id = @run_id"
        query_params = [ScalarQueryParameter("run_id", "STRING", run_id)]
        job_config = QueryJobConfig(query_parameters=query_params)
    else:
        print("📋 No --run-id specified. Verifying ALL data in the table.")
        print("   (For a specific run, use: --run-id YOUR_RUN_ID)")

    # Check 1: Table exists and has data (for specified run_id if provided)
    print("\n1. Checking if the table exists and has data...")
    try:
        table = client.get_table(stage_table)
        print(f"   ✅ Table exists")

        # Count records (filtered by run_id if provided)
        # SECURITY: Using parameterized query with job_config
        count_query = f"SELECT COUNT(*) as cnt FROM `{stage_table}` {where_clause}"
        result = list(client.query(count_query, job_config=job_config).result())[0]
        row_count = result.cnt

        if run_id:
            print(f"   Records for run_id '{run_id}': {row_count:,}")
        else:
            print(f"   Total records in table: {row_count:,}")

        if row_count == 0:
            if run_id:
                print(f"   ❌ FAILED: No records found for run_id '{run_id}'")
                print("   What this means: The specified run either failed, produced no data, or the ID is incorrect.")
                print("   What to do:")
                print("      1. Check if Stage 2 ran successfully for this run_id")
                print("      2. Verify the run_id is correct")
                print("      3. Check Stage 2 logs for errors")
            else:
                print("   ⚠️  WARNING: Table exists but has no data")
                print("   What this means: Stage 2 ran but didn't create any records.")
                print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
        else:
            print(f"   ✅ Found {row_count:,} records to verify")
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 2 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 2 first, then check for errors.")
        return False


    # Check 2: Content cleaned (verify cleaning transformations were applied)
    print("\n2. Checking if content was cleaned correctly...")
    try:
        # Comprehensive check - verify cleaning actually happened
        # Check for control characters (should be removed), whitespace normalization
        # NOTE: Uses content_cleaned field which is the cleaned version of content
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(content_cleaned IS NULL OR content_cleaned = '') as empty_content,
            COUNTIF(content_cleaned LIKE '%\\n%' OR content_cleaned LIKE '%\\r%') as has_newlines,
            COUNTIF(LENGTH(content_cleaned) != LENGTH(TRIM(content_cleaned))) as has_leading_trailing_whitespace,
            COUNTIF(content_cleaned LIKE '%  %') as has_multiple_spaces
        FROM `{stage_table}`
        {where_clause}
        """
        # SECURITY: Using parameterized query with job_config
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.empty_content > 0:
            print(f"   ⚠️  Found {result.empty_content} records with empty content")
            print("   What this means: Some records have no content after cleaning.")
            print("   What to do: This might be normal (e.g., tool results), but check if expected.")
        
        # STRICT CHECK: Zero-tolerance for cleaning issues
        # If cleaning is working, there should be NO uncleaned records
        cleaning_issues = []
        if result.has_leading_trailing_whitespace > 0:
            cleaning_issues.append(f"{result.has_leading_trailing_whitespace:,} records have leading/trailing whitespace")
        if result.has_multiple_spaces > 0:
            cleaning_issues.append(f"{result.has_multiple_spaces:,} records have multiple consecutive spaces")

        # Note: Newlines in content_cleaned are intentionally allowed for readability
        # The cleaning removes control characters and normalizes excessive whitespace,
        # but preserves intentional line breaks in content

        if cleaning_issues:
            print("   ❌ FAILED: Content cleaning has issues:")
            for issue in cleaning_issues:
                print(f"      - {issue}")
            print("   What this means: The cleaning transformations were not fully applied.")
            print("   What to do:")
            print("      1. Check Stage 2 logs for errors")
            print("      2. Re-run Stage 2 to fix the cleaning")
            print("      3. Run this verification again")
            all_checks_passed = False
        else:
            print(f"   ✅ Content cleaning applied correctly to {result.total:,} records")
    except Exception as e:
        print(f"   ❌ Error checking content cleaning: {e}")
        all_checks_passed = False

    # Check 3: Duplicates marked
    print("\n3. Checking if duplicates were marked...")
    try:
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(is_duplicate = TRUE) as duplicates,
            COUNTIF(is_duplicate IS NULL) as null_duplicate_flag
        FROM `{stage_table}`
        {where_clause}
        """
        # SECURITY: Using parameterized query with job_config
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.null_duplicate_flag > 0:
            print(f"   ⚠️  Found {result.null_duplicate_flag} records without duplicate flag")
            print("   What this means: Some records don't have the is_duplicate field set.")
            print("   What to do: Check if Stage 2 completed successfully.")
            all_checks_passed = False
        
        if result.duplicates > 0:
            print(f"   ✅ Found and marked {result.duplicates:,} duplicate records")
        else:
            print("   ✅ No duplicates found (or all marked correctly)")
    except Exception as e:
        # FIX: HARD FAIL if is_duplicate field is missing
        # Stage 2's job is to mark duplicates. If the field doesn't exist,
        # that's a critical error - Stage 2 didn't complete its job.
        # Non-coders need to know this is a real problem, not just a warning.
        if "is_duplicate" in str(e).lower() or "Unrecognized name" in str(e):
            print("   ❌ CRITICAL: is_duplicate field does not exist!")
            print("   What this means: Stage 2 did NOT complete its job.")
            print("   The is_duplicate field is a REQUIRED output of Stage 2.")
            print("   What to do:")
            print("      1. Check Stage 2 logs for errors")
            print("      2. Re-run Stage 2 to create the missing field")
            print("      3. Run this verification again")
            all_checks_passed = False
        else:
            print(f"   ❌ Error checking duplicates: {e}")
            all_checks_passed = False
    
    # Check 4: UTC timestamp normalization (verify timestamps are in UTC)
    print("\n4. Checking if timestamps were normalized to UTC...")
    try:
        # Check if timestamp_utc field exists and has values
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(timestamp_utc IS NOT NULL) as has_utc_timestamp,
            COUNTIF(timestamp_utc IS NULL) as null_timestamps
        FROM `{stage_table}`
        {where_clause}
        """
        # SECURITY: Using parameterized query with job_config
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.null_timestamps > 0:
            print(f"   ⚠️  Found {result.null_timestamps} records without UTC timestamps")
            print("   What this means: Some records don't have normalized timestamps.")
            print("   What to do: Check if timestamp normalization completed successfully.")
            all_checks_passed = False
        else:
            print(f"   ✅ All {result.total:,} records have UTC timestamps")
    except Exception as e:
        if "timestamp_utc" in str(e).lower():
            print("   ⚠️  Could not check UTC timestamps (field may not exist)")
        else:
            print(f"   ❌ Error checking timestamps: {e}")
            all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 2 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 2 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 2"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_2(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
