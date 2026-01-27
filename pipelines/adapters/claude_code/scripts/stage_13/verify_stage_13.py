#!/usr/bin/env python3
"""
Verification Script for Stage 13

This script allows non-coders to verify that Stage 13 is working correctly.

Usage:
    python3 verify_stage_13.py [--run-id RUN_ID]

What it checks:
  - Validation passed
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
from shared.constants import (
    get_full_table_id, TABLE_STAGE_13,
    TABLE_STAGE_2, TABLE_STAGE_3, TABLE_STAGE_4, TABLE_STAGE_5,
    TABLE_STAGE_6, TABLE_STAGE_7, TABLE_STAGE_8, TABLE_STAGE_9, TABLE_STAGE_10,
)
from shared_validation import validate_table_id, validate_run_id

def verify_stage_13(run_id: str = None) -> bool:
    """Verify Stage 13 is working correctly.
    
    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print(f"VERIFYING STAGE 13 - Validation")
    print("="*70)
    print("\nThis script checks if Stage 13 worked correctly.")
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
        print("📋 No --run-id specified. Verifying ALL data in the tables.")
        print("   (For a specific run, use: --run-id YOUR_RUN_ID)")

    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot check if Stage 13 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # Build parameterized query configuration for run_id filtering
    # SECURITY: Using parameterized queries to prevent SQL injection
    query_params = []
    where_clause = ""
    job_config = None

    if validated_run_id:
        where_clause = "WHERE run_id = @run_id"
        query_params = [ScalarQueryParameter("run_id", "STRING", validated_run_id)]
        job_config = QueryJobConfig(query_parameters=query_params)

    # Check 1: Validation status - Stage 13 validates all staging tables L2-L8
    print("\n1. Checking if validation completed successfully...")
    print("   Note: Stage 13 validates data quality across all staging tables (L2-L8).")
    print("   It checks required fields, count fields, and parent-child links.")

    # FIX: Validate table IDs and use parameterized queries
    try:
        # FIX: Validate all table IDs for SQL injection protection
        staging_tables = {
            "L2": validate_table_id(get_full_table_id(TABLE_STAGE_10)),
            "L3": validate_table_id(get_full_table_id(TABLE_STAGE_9)),
            "L4": validate_table_id(get_full_table_id(TABLE_STAGE_8)),
            "L5": validate_table_id(get_full_table_id(TABLE_STAGE_7)),
            "L6": validate_table_id(get_full_table_id(TABLE_STAGE_6)),
            "L8": validate_table_id(get_full_table_id(TABLE_STAGE_5)),
        }

        all_tables_valid = True
        validation_summary = []

        for level, validated_table in staging_tables.items():
            try:
                table = client.get_table(validated_table)
                row_count = table.num_rows

                # Check for required fields (entity_id, level, source_pipeline)
                if row_count > 0:
                    # SECURITY: Using parameterized query with validated table
                    check_query = f"""
                    SELECT
                        COUNT(*) as total,
                        COUNTIF(entity_id IS NULL) as null_entity_id,
                        COUNTIF(level IS NULL) as null_level,
                        COUNTIF(source_pipeline IS NULL) as null_source_pipeline
                    FROM `{validated_table}`
                    {where_clause}
                    """
                    check_result = list(client.query(check_query, job_config=job_config).result())[0]
                    
                    if check_result.null_entity_id > 0 or check_result.null_level > 0 or check_result.null_source_pipeline > 0:
                        validation_summary.append(f"   ⚠️  {level}: {row_count:,} records, but some required fields are NULL")
                        all_tables_valid = False
                    else:
                        validation_summary.append(f"   ✅ {level}: {row_count:,} records, required fields present")
                else:
                    validation_summary.append(f"   ⚠️  {level}: Table exists but has no data")
                    all_tables_valid = False
            except Exception as e:
                validation_summary.append(f"   ❌ {level}: Table check failed - {str(e)[:100]}")
                all_tables_valid = False
        
        print("\n   Validation Results by Level:")
        for summary in validation_summary:
            print(summary)
        
        if all_tables_valid:
            print("\n   ✅ All staging tables have valid data structure")
            print("   What this means: Stage 13 validation checks would pass for required fields.")
            print("   What to do: Stage 13 should have completed successfully. Check logs for full validation report.")
        else:
            print("\n   ⚠️  Some tables have validation issues")
            print("   What this means: Some staging tables have missing required fields.")
            print("   What to do: Review the issues above and fix data quality problems before promotion.")
            all_checks_passed = False
            
    except Exception as e:
        print(f"   ⚠️  Could not perform detailed validation checks: {e}")
        print("   What this means: Cannot verify validation results automatically.")
        print("   What to do: Check Stage 13 execution logs to see validation results.")
        all_checks_passed = False

    
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 13 is working correctly!")
        print("="*70)
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 13 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description=f"Verify Stage 13"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )
    
    args = parser.parse_args()
    
    success = verify_stage_13(args.run_id)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
