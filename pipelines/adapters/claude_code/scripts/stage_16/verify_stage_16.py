#!/usr/bin/env python3
"""
Verification Script for Stage 16

This script allows non-coders to verify that Stage 16 is working correctly.

Usage:
    python3 verify_stage_16.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - Entities promoted
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
from shared.constants import get_full_table_id, TABLE_ENTITY_UNIFIED
from shared_validation import validate_table_id, validate_run_id

def verify_stage_16(run_id: str = None) -> bool:
    """Verify Stage 16 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 16 - Promotion to entity_unified")
    print("="*70)
    print("\nThis script checks if Stage 16 worked correctly.")
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
        print("\n   What this means: The system cannot check if Stage 16 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # FIX: Validate table ID for SQL injection protection
    stage_table = get_full_table_id(TABLE_ENTITY_UNIFIED)
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
                print("      1. Check if Stage 16 ran successfully for this run_id")
                print("      2. Verify the run_id is correct")
                print("      3. Check Stage 16 logs for errors")
            else:
                print("   ⚠️  WARNING: Table exists but has no data")
                print("   What this means: Stage 16 ran but didn't create any records.")
                print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
        else:
            print(f"   ✅ Found {row_count:,} records to verify")
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 16 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 16 first, then check for errors.")
        return False


    # Check 2: Entities promoted (check entity_unified has data from all levels)
    print("\n2. Checking if entities were promoted correctly...")
    try:
        # SECURITY: Using parameterized query with validated table and job_config
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNT(DISTINCT level) as unique_levels,
            COUNTIF(level = 8) as l8_count,
            COUNTIF(level = 6) as l6_count,
            COUNTIF(level = 5) as l5_count,
            COUNTIF(level = 4) as l4_count,
            COUNTIF(level = 3) as l3_count,
            COUNTIF(level = 2) as l2_count
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.total == 0:
            print("   ❌ No entities found in entity_unified")
            print("   What this means: Stage 16 didn't promote any entities.")
            print("   What to do: Run Stage 16 to promote validated entities.")
            all_checks_passed = False
        else:
            print(f"   ✅ {result.total:,} entities promoted to entity_unified")
            print(f"   ✅ Entities from {result.unique_levels} different levels")
            if result.l8_count > 0:
                print(f"   ✅ L8: {result.l8_count:,}, L6: {result.l6_count:,}, L5: {result.l5_count:,}")
                print(f"   ✅ L4: {result.l4_count:,}, L3: {result.l3_count:,}, L2: {result.l2_count:,}")
    except Exception as e:
        print(f"   ❌ Error checking promoted entities: {e}")
        all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 16 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 16 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 16"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_16(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
