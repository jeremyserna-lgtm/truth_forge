#!/usr/bin/env python3
"""Create rollback scripts for all stages."""
from pathlib import Path

ROLLBACK_SCRIPT_TEMPLATE = '''#!/usr/bin/env python3
"""
Rollback Script for Stage {stage_num}

This script allows non-coders to safely rollback Stage {stage_num} data.

Usage:
    python3 rollback_stage_{stage_num}.py --run-id RUN_ID [--confirm]

What it does:
  - Deletes all data from stage_{stage_num} table for the specified run_id
  - Provides clear, non-technical feedback
  - Requires confirmation before deleting
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from src.services.central_services.core.bigquery_client import get_bigquery_client
from shared.constants import get_full_table_id, TABLE_STAGE_{stage_num}
from shared_validation import validate_table_id, validate_run_id
from google.cloud.bigquery import ScalarQueryParameter

def rollback_stage_{stage_num}(run_id: str, confirm: bool = False) -> bool:
    """Rollback Stage {stage_num} data for a specific run_id.
    
    Args:
        run_id: Run ID to rollback
        confirm: If True, skip confirmation prompt
        
    Returns:
        True if rollback successful, False otherwise
    """
    print("="*70)
    print("ROLLBACK STAGE {stage_num}")
    print("="*70)
    print("\\nThis script will delete Stage {stage_num} data for a specific run.")
    print("You don't need to know how to code - just follow the prompts.\\n")
    
    # Validate run_id
    try:
        validated_run_id = validate_run_id(run_id)
    except ValueError as e:
        print(f"❌ ERROR: Invalid run ID")
        print(f"   Problem: {{e}}")
        print("\\n   What this means: The run ID you provided is not valid.")
        print("   What to do: Check the run ID and try again.")
        return False
    
    try:
        client = get_bigquery_client().client
    except Exception as e:
        print(f"❌ ERROR: Could not connect to BigQuery")
        print(f"   Problem: {{e}}")
        print("\\n   What this means: The system cannot connect to the database.")
        print("   What to do: Check your BigQuery credentials and try again.")
        return False
    
    stage_table = get_full_table_id(TABLE_STAGE_{stage_num})
    validated_table = validate_table_id(stage_table)
    
    # Check how many records will be deleted
    print(f"\\nChecking how many records will be deleted...")
    try:
        count_query = f"""
        SELECT COUNT(*) as cnt
        FROM `{{validated_table}}`
        WHERE run_id = @run_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("run_id", "STRING", validated_run_id)
            ]
        )
        count_result = list(client.query(count_query, job_config=job_config).result())[0]
        record_count = count_result.cnt
        
        if record_count == 0:
            print(f"   ℹ️  No records found for run_id: {{validated_run_id}}")
            print("   What this means: There's nothing to rollback for this run.")
            print("   What to do: The run may not have completed, or data was already deleted.")
            return True
        
        print(f"   ⚠️  Found {{record_count:,}} records that will be deleted")
    except Exception as e:
        print(f"   ❌ Error checking record count: {{e}}")
        print("   What this means: Cannot determine how many records will be deleted.")
        print("   What to do: Check your BigQuery connection and try again.")
        return False
    
    # Confirm deletion
    if not confirm:
        print(f"\\n⚠️  WARNING: This will delete {{record_count:,}} records from Stage {stage_num}")
        print(f"   Run ID: {{validated_run_id}}")
        response = input("\\n   Type 'yes' to confirm deletion: ")
        if response.lower() != 'yes':
            print("\\n   Rollback cancelled.")
            return False
    
    # Perform deletion
    print(f"\\nDeleting records...")
    try:
        delete_query = f"""
        DELETE FROM `{{validated_table}}`
        WHERE run_id = @run_id
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("run_id", "STRING", validated_run_id)
            ]
        )
        job = client.query(delete_query, job_config=job_config)
        job.result()  # Wait for completion
        
        if job.errors:
            print(f"   ❌ Error during deletion: {{job.errors}}")
            print("   What this means: The deletion operation failed.")
            print("   What to do: Check the error details and try again, or contact support.")
            return False
        
        print(f"   ✅ Successfully deleted {{record_count:,}} records")
        print(f"\\n✅ ROLLBACK COMPLETE")
        print("="*70)
        print(f"Stage {stage_num} data for run_id '{{validated_run_id}}' has been deleted.")
        print("\\nWhat this means: The data from this run has been removed.")
        print("What to do: You can now re-run Stage {stage_num} if needed.")
        return True
        
    except Exception as e:
        print(f"   ❌ Error during deletion: {{e}}")
        print("   What this means: The deletion operation failed.")
        print("   What to do: Check the error details and try again, or contact support.")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Rollback Stage {stage_num} data for a specific run_id"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        required=True,
        help="Run ID to rollback (required)"
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution)"
    )
    
    args = parser.parse_args()
    
    success = rollback_stage_{stage_num}(args.run_id, args.confirm)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
'''

def main():
    """Create rollback scripts for all stages."""
    scripts_dir = Path(__file__).parent
    
    print("Creating rollback scripts for all stages...")
    
    for stage_num in range(17):
        stage_dir = scripts_dir / f"stage_{stage_num}"
        rollback_script = stage_dir / f"rollback_stage_{stage_num}.py"
        
        if rollback_script.exists():
            print(f"  Stage {stage_num}: Already exists, skipping")
            continue
        
        # Generate script content
        content = ROLLBACK_SCRIPT_TEMPLATE.format(stage_num=stage_num)
        
        # Write script
        rollback_script.write_text(content)
        rollback_script.chmod(0o755)  # Make executable
        print(f"  Stage {stage_num}: Created {rollback_script.name}")
    
    print("\n✅ All rollback scripts created!")

if __name__ == "__main__":
    main()
