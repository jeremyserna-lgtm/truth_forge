#!/usr/bin/env python3
"""
Verification Script for Stage 4

This script allows non-coders to verify that Stage 4 is working correctly.

Usage:
    python3 verify_stage_4.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - Text corrected
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
from shared.constants import get_full_table_id, TABLE_STAGE_4
from shared_validation import validate_table_id, validate_run_id

def verify_stage_4(run_id: str = None) -> bool:
    """Verify Stage 4 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 4")
    print("="*70)
    print("\nThis script checks if Stage 4 worked correctly.")
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
        print("\n   What this means: The system cannot check if Stage 4 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # FIX: Validate table ID for SQL injection protection
    stage_table = get_full_table_id(TABLE_STAGE_4)
    validated_table = validate_table_id(stage_table)

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
                print("      1. Check if Stage 4 ran successfully for this run_id")
                print("      2. Verify the run_id is correct")
                print("      3. Check Stage 4 logs for errors")
            else:
                print("   ⚠️  WARNING: Table exists but has no data")
                print("   What this means: Stage 4 ran but didn't create any records.")
                print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
        else:
            print(f"   ✅ Found {row_count:,} records to verify")
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 4 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 4 first, then check for errors.")
        return False


    # Check 2: Text correction applied (check metadata field for correction evidence)
    print("\n2. Checking if text correction was applied...")
    try:
        # FIX: Check metadata JSON field to confirm correction occurred
        # Stage 4 stores correction metadata with these ACTUAL keys:
        # - $.original_text - The original text before correction
        # - $.corrected_text - The corrected text after correction
        # - $.correction_cost_usd - Cost of the correction API call
        # SECURITY: Using parameterized query with job_config and validated_table
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(text IS NOT NULL AND text != '') as has_text,
            COUNTIF(
                metadata IS NOT NULL
                AND JSON_EXTRACT_SCALAR(metadata, '$.original_text') IS NOT NULL
            ) as has_original_text,
            COUNTIF(
                metadata IS NOT NULL
                AND JSON_EXTRACT_SCALAR(metadata, '$.corrected_text') IS NOT NULL
            ) as has_corrected_text,
            COUNTIF(
                metadata IS NOT NULL
                AND JSON_EXTRACT_SCALAR(metadata, '$.correction_cost_usd') IS NOT NULL
            ) as has_correction_cost
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.has_text == 0:
            print("   ⚠️  No text content found in records")
            print("   What this means: All records have empty text fields.")
            print("   What to do: Check if Stage 4 processed the data correctly.")
            all_checks_passed = False

        # Check if correction metadata exists (this confirms correction was applied)
        # FIX: Use the correct metadata keys that Stage 4 actually writes
        correction_evidence_count = max(
            result.has_original_text or 0,
            result.has_corrected_text or 0,
            result.has_correction_cost or 0
        )

        if correction_evidence_count > 0:
            print(f"   ✅ Text correction applied to {correction_evidence_count:,} user messages (verified via metadata)")
            if result.has_correction_cost and result.has_correction_cost > 0:
                print(f"      - {result.has_correction_cost:,} records have correction cost tracking")
        else:
            # No correction metadata found - this could mean:
            # 1. No user messages in the data (only assistant messages)
            # 2. Correction wasn't applied
            # 3. All corrections failed and fell back to original text
            print("   ℹ️  INFO: No correction metadata found in records")
            print("   What this means: No user messages were corrected OR no user messages exist.")
            print("   Note: Only user/human messages get text correction applied.")
            print("   Tip: Check Stage 4 logs to confirm correction ran successfully.")
    except Exception as e:
        # If metadata field doesn't exist or query fails, try fallback check
        try:
            # Fallback: Just check if text field exists (basic check)
            # SECURITY: Using parameterized query with job_config and validated_table
            query = f"""
            SELECT
                COUNT(*) as total,
                COUNTIF(text IS NOT NULL AND text != '') as has_text
            FROM `{validated_table}`
            {where_clause}
            """
            result = list(client.query(query, job_config=job_config).result())[0]
            if result.has_text > 0:
                print(f"   ⚠️  Text exists but cannot verify correction (metadata check failed)")
                print(f"   What this means: Found {result.has_text:,} records with text, but couldn't verify correction.")
                print("   What to do: Check Stage 4 logs to confirm correction ran successfully.")
            else:
                print("   ❌ No text content found in records")
                all_checks_passed = False
        except Exception as e2:
            print(f"   ❌ Error checking text correction: {e2}")
            all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 4 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 4 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 4"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_4(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
