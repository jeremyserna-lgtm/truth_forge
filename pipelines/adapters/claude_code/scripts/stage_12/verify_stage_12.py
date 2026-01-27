#!/usr/bin/env python3
"""
Verification Script for Stage 12

This script allows non-coders to verify that Stage 12 is working correctly.

Usage:
    python3 verify_stage_12.py [--run-id RUN_ID]

What it checks:
  - Count columns populated
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
from shared.constants import get_full_table_id, TABLE_STAGE_5, TABLE_STAGE_12
from shared_validation import validate_table_id, validate_run_id

def verify_stage_12(run_id: str = None) -> bool:
    """Verify Stage 12 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 12 - Count Rollups")
    print("="*70)
    print("\nThis script checks if Stage 12 worked correctly.")
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
        print("\n   What this means: The system cannot check if Stage 12 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # FIX: Validate table IDs for SQL injection protection
    validated_stage_5 = validate_table_id(get_full_table_id(TABLE_STAGE_5))

    # Build parameterized query configuration for run_id filtering
    # SECURITY: Using parameterized queries to prevent SQL injection
    query_params = []
    where_clause = ""
    job_config = None

    if validated_run_id:
        where_clause = "WHERE run_id = @run_id"
        query_params = [ScalarQueryParameter("run_id", "STRING", validated_run_id)]
        job_config = QueryJobConfig(query_parameters=query_params)

    # Check 1: Count columns populated (check L8 conversations have counts)
    print("\n1. Checking if count columns are populated...")

    try:
        # SECURITY: Using parameterized query with job_config and validated table
        query = f"""
        SELECT
            COUNT(*) as total_l8,
            COUNTIF(l6_count IS NOT NULL) as has_l6_count,
            COUNTIF(l5_count IS NOT NULL) as has_l5_count,
            COUNTIF(l2_count IS NOT NULL) as has_l2_count
        FROM `{validated_stage_5}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]
        
        if result.has_l6_count == 0:
            print("   ⚠️  No L8 conversations have l6_count populated")
            print("   What this means: Stage 12 may not have run yet.")
            print("   What to do: Run Stage 12 to populate count columns.")
            all_checks_passed = False
        else:
            print(f"   ✅ {result.has_l6_count:,} L8 conversations have count columns populated")
            print(f"   ✅ l5_count: {result.has_l5_count:,}, l2_count: {result.has_l2_count:,}")
    except Exception as e:
        if "l6_count" in str(e).lower():
            print("   ⚠️  Count columns may not exist yet")
            print("   What this means: Stage 12 hasn't run or count columns weren't created.")
            print("   What to do: Run Stage 12 to populate count columns.")
        else:
            print(f"   ❌ Error checking count columns: {e}")
            all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 12 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 12 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 12"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_12(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
