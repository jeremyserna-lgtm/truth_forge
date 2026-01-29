#!/usr/bin/env python3
"""Assess claude_code Pipeline State

This script checks which BigQuery tables exist and which have data
to understand the current state of the pipeline.

Usage:
    python assess_pipeline_state.py [--project PROJECT] [--dataset DATASET]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

# Add paths - match pattern used in check_status.py
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Add scripts directory to path
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

# Local imports after path setup
from google.cloud import bigquery
from google.cloud.exceptions import NotFound

try:
    from shared.constants import (
        PROJECT_ID,
        DATASET_ID,
        get_stage_table,
        TABLE_ENTITY_UNIFIED,
    )
    from shared import get_full_table_id
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root and dependencies are installed.")
    sys.exit(1)

# Get BigQuery client
try:
    from src.services.central_services.core.config import get_bigquery_client
    from src.services.central_services.core import get_logger
except ImportError:
    # Fallback: use direct BigQuery client
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name: str):
        return logging.getLogger(name)
    
    def get_bigquery_client():
        return bigquery.Client(project=PROJECT_ID)

logger = get_logger(__name__)

# Stage names for reporting
STAGE_NAMES = {
    0: "Discovery & Assessment",
    1: "Extraction",
    2: "Cleaning",
    3: "Identity Generation",
    4: "Staging",
    5: "Tokenization (L1)",
    6: "Sentence Detection (L3)",
    7: "Message Entities (L5)",
    8: "Conversation Entities (L8)",
    9: "Embeddings",
    10: "LLM Extractions",
    11: "Sentiment Analysis",
    12: "Topic Extraction",
    13: "Relationships",
    14: "Aggregation",
    15: "Validation",
    16: "Promotion",
}


def check_table_state(client: bigquery.Client, table_id: str) -> dict[str, Any]:
    """Check if a table exists and get its row count.
    
    Args:
        client: BigQuery client
        table_id: Full table ID (project.dataset.table)
        
    Returns:
        Dictionary with exists, row_count, and error info
    """
    result = {
        "exists": False,
        "row_count": 0,
        "error": None,
    }
    
    try:
        table = client.get_table(table_id)
        result["exists"] = True
        result["row_count"] = table.num_rows or 0
    except NotFound:
        result["exists"] = False
        result["row_count"] = 0
    except Exception as e:
        result["error"] = str(e)
        result["exists"] = False
    
    return result


def assess_pipeline_state(
    client: bigquery.Client,
    project: str | None = None,
    dataset: str | None = None,
) -> dict[int, dict[str, Any]]:
    """Assess the state of all pipeline stages.
    
    Args:
        client: BigQuery client
        project: Optional project override
        dataset: Optional dataset override
        
    Returns:
        Dictionary mapping stage number to state info
    """
    results: dict[int, dict[str, Any]] = {}
    
    for stage_num in range(17):  # Stages 0-16
        # Get table name using get_stage_table helper
        if stage_num == 16:
            table_name = TABLE_ENTITY_UNIFIED
        else:
            table_name = get_stage_table(stage_num)
        
        table_id = get_full_table_id(table_name, project, dataset)
        
        state = check_table_state(client, table_id)
        state["stage_name"] = STAGE_NAMES[stage_num]
        state["table_id"] = table_id
        state["table_name"] = table_name
        
        results[stage_num] = state
    
    return results


def print_assessment_report(results: dict[int, dict[str, Any]]) -> None:
    """Print a formatted assessment report.
    
    Args:
        results: Results from assess_pipeline_state
    """
    print("\n" + "=" * 80)
    print("CLAUDE_CODE PIPELINE STATE ASSESSMENT")
    print("=" * 80)
    print()
    
    # Summary statistics
    total_stages = len(results)
    existing_tables = sum(1 for r in results.values() if r["exists"])
    tables_with_data = sum(1 for r in results.values() if r["exists"] and r["row_count"] > 0)
    total_rows = sum(r["row_count"] for r in results.values())
    
    print(f"Total Stages: {total_stages}")
    print(f"Tables Exists: {existing_tables}/{total_stages}")
    print(f"Tables With Data: {tables_with_data}/{total_stages}")
    print(f"Total Rows Across All Tables: {total_rows:,}")
    print()
    
    # Detailed stage-by-stage report
    print("-" * 80)
    print(f"{'Stage':<6} {'Name':<30} {'Status':<12} {'Rows':<15} {'Table ID'}")
    print("-" * 80)
    
    for stage_num in sorted(results.keys()):
        state = results[stage_num]
        stage_name = state["stage_name"]
        
        if state["error"]:
            status = f"ERROR: {state['error'][:30]}"
        elif not state["exists"]:
            status = "NOT EXISTS"
        elif state["row_count"] == 0:
            status = "EMPTY"
        else:
            status = "HAS DATA"
        
        row_count_str = f"{state['row_count']:,}" if state["row_count"] > 0 else "0"
        table_id_short = state["table_id"].split(".")[-1] if "." in state["table_id"] else state["table_id"]
        
        print(f"{stage_num:<6} {stage_name:<30} {status:<12} {row_count_str:<15} {table_id_short}")
    
    print("-" * 80)
    print()
    
    # Pipeline progression analysis
    print("PIPELINE PROGRESSION ANALYSIS:")
    print("-" * 80)
    
    # Find the highest consecutive stage with data (starting from 0)
    last_consecutive_stage = -1
    for stage_num in sorted(results.keys()):
        state = results[stage_num]
        if state["exists"] and state["row_count"] > 0:
            last_consecutive_stage = stage_num
        elif stage_num <= last_consecutive_stage + 1:
            # If we hit a gap, stop looking for consecutive stages
            break
    
    # Check if entity_unified has data (stage 16)
    has_entity_unified = results[16]["exists"] and results[16]["row_count"] > 0
    
    # Find all stages with data (for gap analysis)
    stages_with_data = [s for s, r in results.items() if r["exists"] and r["row_count"] > 0 and s != 16]
    
    # Determine if pipeline is complete
    all_stages_complete = (
        has_entity_unified and
        len([s for s in range(17) if results[s]["exists"] and results[s]["row_count"] > 0]) >= 15
    )
    
    if all_stages_complete:
        print(f"✓ Pipeline COMPLETE: All stages executed")
        print(f"  Final stage (entity_unified) has {results[16]['row_count']:,} rows")
    elif has_entity_unified:
        print(f"⚠ Pipeline PARTIAL: entity_unified has {results[16]['row_count']:,} rows")
        print("  BUT intermediate stages (5-15) are missing - data may be from different source")
    elif last_consecutive_stage >= 0:
        print(f"✓ Pipeline has progressed through Stage {last_consecutive_stage}: {STAGE_NAMES[last_consecutive_stage]}")
        print(f"  Stage {last_consecutive_stage} has {results[last_consecutive_stage]['row_count']:,} rows")
        if last_consecutive_stage < 16:
            next_stage = last_consecutive_stage + 1
            print(f"⚠ Next stage to run: Stage {next_stage}: {STAGE_NAMES[next_stage]}")
    else:
        print("⚠ Pipeline has not started - no tables with data found")
    
    # Check for gaps in the pipeline
    if stages_with_data:
        print()
        print("STAGES WITH DATA:")
        for stage_num in sorted(stages_with_data):
            state = results[stage_num]
            print(f"  Stage {stage_num}: {state['stage_name']} - {state['row_count']:,} rows")
        
        # Identify gaps
        gaps = []
        for stage_num in range(min(stages_with_data), max(stages_with_data) + 1):
            if stage_num not in stages_with_data:
                gaps.append(stage_num)
        
        if gaps:
            print()
            print("⚠ GAPS DETECTED (missing stages between data):")
            for gap_stage in gaps:
                print(f"  Stage {gap_stage}: {STAGE_NAMES[gap_stage]} - NOT RUN")
    
    print()
    
    # Missing tables
    missing_tables = [s for s, r in results.items() if not r["exists"]]
    if missing_tables:
        print("MISSING TABLES:")
        print("-" * 80)
        for stage_num in missing_tables:
            state = results[stage_num]
            print(f"  Stage {stage_num}: {state['stage_name']} - {state['table_id']}")
        print()
    
    # Empty tables
    empty_tables = [s for s, r in results.items() if r["exists"] and r["row_count"] == 0]
    if empty_tables:
        print("EMPTY TABLES (exist but no data):")
        print("-" * 80)
        for stage_num in empty_tables:
            state = results[stage_num]
            print(f"  Stage {stage_num}: {state['stage_name']} - {state['table_id']}")
        print()
    
    # Errors
    error_tables = [s for s, r in results.items() if r["error"]]
    if error_tables:
        print("ERRORS:")
        print("-" * 80)
        for stage_num in error_tables:
            state = results[stage_num]
            print(f"  Stage {stage_num}: {state['stage_name']} - {state['error']}")
        print()


def main() -> int:
    """Main execution."""
    parser = argparse.ArgumentParser(description="Assess claude_code pipeline state")
    parser.add_argument(
        "--project",
        type=str,
        help="GCP project ID (overrides default)",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="BigQuery dataset (overrides default)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    
    args = parser.parse_args()
    
    try:
        client_wrapper = get_bigquery_client()
        if hasattr(client_wrapper, "client"):
            client = client_wrapper.client
        else:
            client = client_wrapper
        
        results = assess_pipeline_state(client, args.project, args.dataset)
        
        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))
        else:
            print_assessment_report(results)
        
        return 0
    
    except Exception as e:
        logger.error(f"Assessment failed: {e}", exc_info=True)
        print(f"\nERROR: Assessment failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
