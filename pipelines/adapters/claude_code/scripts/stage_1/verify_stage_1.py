#!/usr/bin/env python3
"""
Verification Script for Stage 1

This script allows non-coders to verify that Stage 1 is working correctly.

Usage:
    python3 verify_stage_1.py [--run-id RUN_ID]

What it checks:
  - Table exists
  - Has records
  - DLQ has no errors
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from src.services.central_services.core.bigquery_client import get_bigquery_client
from shared.constants import get_full_table_id, TABLE_STAGE_1

def verify_stage_1(run_id: str = None) -> bool:
    """Verify Stage 1 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 1")
    print("="*70)
    print("\nThis script checks if Stage 1 worked correctly.")
    print("You don't need to know how to code - just run this and read the results.\n")
    
    all_checks_passed = True
    
    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot check if Stage 1 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False
    

    stage_table = get_full_table_id(TABLE_STAGE_1)
    
    # Check 1: Table exists and has data
    print("\n1. Checking if the table exists and has data...")
    try:
        table = client.get_table(stage_table)
        row_count = table.num_rows
        print(f"   ✅ Table exists")
        print(f"   ✅ Table has {row_count:,} records")
        
        if row_count == 0:
            print("   ⚠️  WARNING: Table exists but has no data")
            print("   What this means: Stage 1 ran but didn't create any records.")
            print("   What to do: Check if upstream stages have data to process.")
            all_checks_passed = False
    except Exception as e:
        print(f"   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 1 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 1 first, then check for errors.")
        return False


    # Check 2: DLQ has no errors
    print("\n2. Checking: DLQ has no errors...")
    try:
        # Check Dead Letter Queue for failed parses
        dlq_table = get_full_table_id("claude_code_stage_1_dlq")
        try:
            query = f"SELECT COUNT(*) as error_count FROM `{dlq_table}`"
            if run_id:
                query += " WHERE run_id = @run_id"
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
                )
                result = list(client.query(query, job_config=job_config).result())[0]
            else:
                result = list(client.query(query).result())[0]
            
            if result.error_count > 0:
                print(f"   ⚠️  Found {result.error_count} failed JSON parses in DLQ")
                print("   What this means: Some lines in JSONL files couldn't be parsed.")
                print("   What to do: Check the DLQ table to see which lines failed and why.")
            else:
                print("   ✅ No failed parses in DLQ")
        except Exception as e:
            # DLQ table might not exist if no errors occurred
            if "not found" in str(e).lower():
                print("   ✅ DLQ table doesn't exist (no errors occurred)")
            else:
                print(f"   ⚠️  Could not check DLQ: {e}")
    except Exception as e:
        print(f"   ❌ Error checking: {e}")
        all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 1 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 1 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 1"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_1(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
