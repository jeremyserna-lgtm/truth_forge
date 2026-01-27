#!/usr/bin/env python3
"""
Verification Script for Stage 9 - L3 Span Creation (Named Entity Recognition)

This script allows non-coders to verify that Stage 9 is working correctly.

Usage:
    python3 verify_stage_9.py [--run-id RUN_ID]

What it checks:
  - Table exists and has data
  - All records are Level 3 (Span/NER) entities
  - All entity types are valid spaCy NER labels
  - All parent IDs reference valid L4 Sentence entities
  - Content is not empty
  - Entity type distribution is reasonable
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
from shared.constants import get_full_table_id, TABLE_STAGE_9, TABLE_STAGE_8
from shared_validation import validate_table_id, validate_run_id

# Valid spaCy NER entity types
VALID_ENTITY_TYPES = {
    "PERSON", "ORG", "GPE", "LOC", "DATE", "TIME", "MONEY", "PERCENT",
    "PRODUCT", "EVENT", "WORK_OF_ART", "LAW", "LANGUAGE", "FAC", "NORP",
    "QUANTITY", "ORDINAL", "CARDINAL"
}


def verify_stage_9(run_id: str = None) -> bool:
    """Verify Stage 9 is working correctly.

    Returns:
        True if all checks pass, False otherwise
    """
    print("="*70)
    print("VERIFYING STAGE 9 - L3 Span Creation (Named Entity Recognition)")
    print("="*70)
    print("\nThis script checks if Stage 9 worked correctly.")
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
        print("❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {e}")
        print("\n   What this means: The system cannot check if Stage 9 worked.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False

    # FIX: Validate table IDs for SQL injection protection
    stage_table = get_full_table_id(TABLE_STAGE_9)
    validated_table = validate_table_id(stage_table)
    input_table = get_full_table_id(TABLE_STAGE_8)
    validated_input = validate_table_id(input_table)

    # Build parameterized query configuration for run_id filtering
    # SECURITY: Using parameterized queries to prevent SQL injection
    query_params = []
    where_clause = ""
    job_config = None

    if validated_run_id:
        where_clause = "WHERE run_id = @run_id"
        query_params = [ScalarQueryParameter("run_id", "STRING", validated_run_id)]
        job_config = QueryJobConfig(query_parameters=query_params)

    # Check 1: Table exists and has data (for specified run_id if provided)
    print("\n1. Checking if the table exists and has data...")
    try:
        table = client.get_table(validated_table)
        print(f"   ✅ Table exists")

        # Count records (filtered by run_id if provided)
        count_query = f"SELECT COUNT(*) as cnt FROM `{validated_table}` {where_clause}"
        result = list(client.query(count_query, job_config=job_config).result())[0]
        row_count = result.cnt

        if validated_run_id:
            print(f"   Records for run_id '{validated_run_id}': {row_count:,}")
        else:
            print(f"   Total records in table: {row_count:,}")

        if row_count == 0:
            if validated_run_id:
                print(f"   ⚠️  WARNING: No records found for run_id '{validated_run_id}'")
                print("   What this means: The specified run either failed, produced no entities, or the ID is incorrect.")
            else:
                print("   ⚠️  WARNING: Table exists but has no data")
                print("   What this means: Stage 9 ran but didn't create any L3 Span entities.")
            print("   Note: This might be normal if input sentences had no named entities.")
        else:
            print(f"   ✅ Found {row_count:,} records to verify")
    except Exception as e:
        print("   ❌ Table does not exist or error occurred")
        print(f"   Problem: {e}")
        print("   What this means: Stage 9 hasn't run yet or failed to create the table.")
        print("   What to do: Run Stage 9 first, then check for errors.")
        return False

    # Check 2: All records are Level 3 (Span/NER) entities
    print("\n2. Checking that all records are Level 3 (Span/NER) entities...")
    try:
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(level = 3) as level_3_count,
            COUNTIF(level != 3) as wrong_level_count
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.wrong_level_count > 0:
            print(f"   ❌ Found {result.wrong_level_count:,} records with wrong level")
            print("   What this means: Some records are not Level 3 (Span/NER) as they should be.")
            print("   What to do: This is a data corruption issue - contact support.")
            all_checks_passed = False
        else:
            print(f"   ✅ All {result.total:,} records are Level 3 (Span/NER) entities")
    except Exception as e:
        print(f"   ❌ Error checking levels: {e}")
        all_checks_passed = False

    # Check 3: All entity types are valid spaCy NER labels
    print("\n3. Checking that all entity types are valid spaCy NER labels...")
    try:
        query = f"""
        SELECT
            entity_type,
            COUNT(*) as count
        FROM `{validated_table}`
        {where_clause}
        GROUP BY entity_type
        ORDER BY count DESC
        """
        results = list(client.query(query, job_config=job_config).result())

        invalid_types = []
        valid_count = 0
        print("   Entity type distribution:")
        for row in results:
            entity_type = row.entity_type
            count = row.count
            if entity_type in VALID_ENTITY_TYPES:
                print(f"      ✅ {entity_type}: {count:,}")
                valid_count += count
            else:
                print(f"      ❌ {entity_type}: {count:,} (INVALID)")
                invalid_types.append(entity_type)

        if invalid_types:
            print(f"\n   ❌ Found invalid entity types: {invalid_types}")
            print("   What this means: Some entities have types not recognized by spaCy.")
            print("   What to do: This may indicate a processing error - contact support.")
            all_checks_passed = False
        else:
            print(f"\n   ✅ All entity types are valid spaCy NER labels")
    except Exception as e:
        print(f"   ❌ Error checking entity types: {e}")
        all_checks_passed = False

    # Check 4: All parent IDs reference valid L4 Sentence entities
    print("\n4. Checking that all parent IDs reference valid L4 Sentence entities...")
    try:
        query = f"""
        SELECT
            COUNT(*) as total_spans,
            COUNTIF(parent_id IS NULL) as null_parents,
            COUNTIF(parent_id NOT IN (SELECT entity_id FROM `{validated_input}`)) as orphaned_spans
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.null_parents > 0:
            print(f"   ❌ Found {result.null_parents} spans with no parent")
            print("   What this means: Some spans don't know which sentence they belong to.")
            print("   What to do: This is a data quality issue - run Stage 9 again.")
            all_checks_passed = False
        elif result.orphaned_spans > 0:
            print(f"   ❌ Found {result.orphaned_spans} spans pointing to non-existent sentences")
            print("   What this means: Some spans reference sentences that don't exist.")
            print("   What to do: Run Stage 8 first to create sentences, then run Stage 9.")
            all_checks_passed = False
        else:
            print(f"   ✅ All {result.total_spans:,} spans have valid parent links")
    except Exception as e:
        print(f"   ❌ Error checking parent IDs: {e}")
        all_checks_passed = False

    # Check 5: Content is not empty
    print("\n5. Checking that all span content is not empty...")
    try:
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(content IS NULL OR TRIM(content) = '') as empty_count
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.empty_count > 0:
            print(f"   ❌ Found {result.empty_count:,} spans with empty content")
            print("   What this means: Some named entities have no text content.")
            print("   What to do: This is a data quality issue - contact support.")
            all_checks_passed = False
        else:
            print(f"   ✅ All {result.total:,} spans have valid content")
    except Exception as e:
        print(f"   ❌ Error checking content: {e}")
        all_checks_passed = False

    # Check 6: Character offsets are valid (start_char < end_char)
    print("\n6. Checking that character offsets are valid...")
    try:
        query = f"""
        SELECT
            COUNT(*) as total,
            COUNTIF(start_char >= end_char) as invalid_offset_count
        FROM `{validated_table}`
        {where_clause}
        """
        result = list(client.query(query, job_config=job_config).result())[0]

        if result.invalid_offset_count > 0:
            print(f"   ❌ Found {result.invalid_offset_count:,} spans with invalid character offsets")
            print("   What this means: Some spans have start_char >= end_char (impossible).")
            print("   What to do: This is a data integrity issue - contact support.")
            all_checks_passed = False
        else:
            print(f"   ✅ All character offsets are valid (start_char < end_char)")
    except Exception as e:
        print(f"   ❌ Error checking offsets: {e}")
        all_checks_passed = False

    # Summary
    print("\n" + "="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Stage 9 is working correctly!")
        print("="*70)
        print("\nStage 9 successfully created L3 Span (Named Entity) entities from")
        print("L4 Sentences using spaCy NER.")
        return True
    else:
        print("❌ SOME CHECKS FAILED - See details above")
        print("="*70)
        print("\nWhat to do next:")
        print("  1. Read the error messages above")
        print("  2. Follow the 'What to do' instructions for each error")
        print("  3. Run Stage 9 again if needed")
        print("  4. Run this verification script again to confirm fixes")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Stage 9 - L3 Span Creation (Named Entity Recognition)"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Specific run ID to verify (optional)"
    )

    args = parser.parse_args()

    success = verify_stage_9(args.run_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
