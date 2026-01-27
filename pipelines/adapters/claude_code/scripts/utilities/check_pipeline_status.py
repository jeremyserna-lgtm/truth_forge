#!/usr/bin/env python3
"""Check pipeline status and message counts for claude_code pipeline."""

import sys
from pathlib import Path

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_logger
from src.services.central_services.core.config import get_bigquery_client

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"

TABLES = {
    "stage_0": "claude_code_stage_0",
    "stage_1": "claude_code_stage_1",
    "stage_3": "claude_code_stage_3",
    "stage_4": "claude_code_stage_4",
    "stage_5": "claude_code_stage_5",
}

def check_table_exists(client, table_name: str) -> bool:
    """Check if a table exists."""
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        client.get_table(table_ref)
        return True
    except Exception:
        return False

def get_table_count(client, table_name: str) -> int:
    """Get row count for a table."""
    if not check_table_exists(client, table_name):
        return -1  # Table doesn't exist

    try:
        query = f"""
        SELECT COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        """
        result = list(client.query(query).result())
        if result:
            return result[0].count
        return 0
    except Exception as e:
        logger.warning(f"Error counting {table_name}: {e}")
        return -1

def get_source_breakdown(client, table_name: str) -> dict:
    """Get message count by source."""
    if not check_table_exists(client, table_name):
        return {}

    try:
        query = f"""
        SELECT
            source_name,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        GROUP BY source_name
        ORDER BY source_name
        """
        results = {}
        for row in client.query(query).result():
            results[row.source_name] = row.count
        return results
    except Exception as e:
        logger.warning(f"Error getting source breakdown for {table_name}: {e}")
        return {}

def main():
    """Main execution function."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("CLAUDE CODEX GITHUB PIPELINE STATUS")
    print("="*80 + "\n")

    # Get counts for each stage
    stage_counts = {}
    for stage_name, table_name in TABLES.items():
        count = get_table_count(bq_client, table_name)
        stage_counts[stage_name] = count

        status = "✅ EXISTS" if count >= 0 else "❌ MISSING"
        count_str = f"{count:,}" if count >= 0 else "N/A"
        print(f"{stage_name.upper():12} {status:12} {count_str:>12} messages")

    print("\n" + "-"*80)
    print("SOURCE BREAKDOWN (Stage 3 - Registered Messages)")
    print("-"*80)

    if stage_counts["stage_3"] > 0:
        source_breakdown = get_source_breakdown(bq_client, TABLES["stage_3"])
        for source, count in source_breakdown.items():
            print(f"  {source:20} {count:>12,} messages")
    else:
        print("  No data in Stage 3")

    print("\n" + "-"*80)
    print("PIPELINE PROGRESS")
    print("-"*80)

    # Calculate progress
    if stage_counts["stage_0"] > 0:
        print(f"Stage 0 (Extraction):     {stage_counts['stage_0']:,} messages")
    else:
        print("Stage 0 (Extraction):     Not run")

    if stage_counts["stage_1"] > 0:
        print(f"Stage 1 (Enrichment):    {stage_counts['stage_1']:,} messages")
        if stage_counts["stage_0"] > 0:
            pct = (stage_counts["stage_1"] / stage_counts["stage_0"]) * 100
            print(f"  → {pct:.1f}% of Stage 0 processed")
    else:
        print("Stage 1 (Enrichment):    Not run")

    if stage_counts["stage_3"] > 0:
        print(f"Stage 3 (ID Registration): {stage_counts['stage_3']:,} messages")
        if stage_counts["stage_1"] > 0:
            pct = (stage_counts["stage_3"] / stage_counts["stage_1"]) * 100
            print(f"  → {pct:.1f}% of Stage 1 processed")
    else:
        print("Stage 3 (ID Registration): Not run")

    if stage_counts["stage_4"] > 0:
        print(f"Stage 4 (LLM Correction): {stage_counts['stage_4']:,} messages")
        if stage_counts["stage_3"] > 0:
            pct = (stage_counts["stage_4"] / stage_counts["stage_3"]) * 100
            print(f"  → {pct:.1f}% of Stage 3 processed")
    else:
        print("Stage 4 (LLM Correction): Not run")

    if stage_counts["stage_5"] > 0:
        print(f"Stage 5 (Ready Messages):  {stage_counts['stage_5']:,} messages")
        if stage_counts["stage_4"] > 0:
            pct = (stage_counts["stage_5"] / stage_counts["stage_4"]) * 100
            print(f"  → {pct:.1f}% of Stage 4 ready")
    else:
        print("Stage 5 (Ready Messages): Not run")

    print("\n" + "="*80)

    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-"*80)

    if stage_counts["stage_0"] == -1:
        print("1. Run Stage 0 to extract messages from TruthService")
    elif stage_counts["stage_1"] == -1 or (stage_counts["stage_1"] > 0 and stage_counts["stage_1"] < stage_counts["stage_0"]):
        remaining = stage_counts["stage_0"] - stage_counts["stage_1"] if stage_counts["stage_1"] > 0 else stage_counts["stage_0"]
        print(f"1. Run Stage 1 to enrich {remaining:,} messages")
    elif stage_counts["stage_3"] == -1 or (stage_counts["stage_3"] > 0 and stage_counts["stage_3"] < stage_counts["stage_1"]):
        remaining = stage_counts["stage_1"] - stage_counts["stage_3"] if stage_counts["stage_3"] > 0 else stage_counts["stage_1"]
        print(f"1. Run Stage 3 to register {remaining:,} entity_ids")
    elif stage_counts["stage_4"] == -1 or (stage_counts["stage_4"] > 0 and stage_counts["stage_4"] < stage_counts["stage_3"]):
        remaining = stage_counts["stage_3"] - stage_counts["stage_4"] if stage_counts["stage_4"] > 0 else stage_counts["stage_3"]
        print(f"1. Run Stage 4 to correct {remaining:,} messages")
    else:
        print("1. ✅ All stages complete!")

    print("="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())

script_id = "pipelines.claude_code.scripts.utilities.check_pipeline_status.py"

import sys
from pathlib import Path

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_logger
from src.services.central_services.core.config import get_bigquery_client

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"

TABLES = {
    "stage_0": "claude_code_stage_0",
    "stage_1": "claude_code_stage_1",
    "stage_3": "claude_code_stage_3",
    "stage_4": "claude_code_stage_4",
    "stage_5": "claude_code_stage_5",
}

def check_table_exists(client, table_name: str) -> bool:
    """Check if a table exists."""
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        client.get_table(table_ref)
        return True
    except Exception:
        return False

def get_table_count(client, table_name: str) -> int:
    """Get row count for a table."""
    if not check_table_exists(client, table_name):
        return -1  # Table doesn't exist

    try:
        query = f"""
        SELECT COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        """
        result = list(client.query(query).result())
        if result:
            return result[0].count
        return 0
    except Exception as e:
        logger.warning(f"Error counting {table_name}: {e}")
        return -1

def get_source_breakdown(client, table_name: str) -> dict:
    """Get message count by source."""
    if not check_table_exists(client, table_name):
        return {}

    try:
        query = f"""
        SELECT
            source_name,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        GROUP BY source_name
        ORDER BY source_name
        """
        results = {}
        for row in client.query(query).result():
            results[row.source_name] = row.count
        return results
    except Exception as e:
        logger.warning(f"Error getting source breakdown for {table_name}: {e}")
        return {}

def main():
    """Main execution function."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("CLAUDE CODEX GITHUB PIPELINE STATUS")
    print("="*80 + "\n")

    # Get counts for each stage
    stage_counts = {}
    for stage_name, table_name in TABLES.items():
        count = get_table_count(bq_client, table_name)
        stage_counts[stage_name] = count

        status = "✅ EXISTS" if count >= 0 else "❌ MISSING"
        count_str = f"{count:,}" if count >= 0 else "N/A"
        print(f"{stage_name.upper():12} {status:12} {count_str:>12} messages")

    print("\n" + "-"*80)
    print("SOURCE BREAKDOWN (Stage 3 - Registered Messages)")
    print("-"*80)

    if stage_counts["stage_3"] > 0:
        source_breakdown = get_source_breakdown(bq_client, TABLES["stage_3"])
        for source, count in source_breakdown.items():
            print(f"  {source:20} {count:>12,} messages")
    else:
        print("  No data in Stage 3")

    print("\n" + "-"*80)
    print("PIPELINE PROGRESS")
    print("-"*80)

    # Calculate progress
    if stage_counts["stage_0"] > 0:
        print(f"Stage 0 (Extraction):     {stage_counts['stage_0']:,} messages")
    else:
        print("Stage 0 (Extraction):     Not run")

    if stage_counts["stage_1"] > 0:
        print(f"Stage 1 (Enrichment):    {stage_counts['stage_1']:,} messages")
        if stage_counts["stage_0"] > 0:
            pct = (stage_counts["stage_1"] / stage_counts["stage_0"]) * 100
            print(f"  → {pct:.1f}% of Stage 0 processed")
    else:
        print("Stage 1 (Enrichment):    Not run")

    if stage_counts["stage_3"] > 0:
        print(f"Stage 3 (ID Registration): {stage_counts['stage_3']:,} messages")
        if stage_counts["stage_1"] > 0:
            pct = (stage_counts["stage_3"] / stage_counts["stage_1"]) * 100
            print(f"  → {pct:.1f}% of Stage 1 processed")
    else:
        print("Stage 3 (ID Registration): Not run")

    if stage_counts["stage_4"] > 0:
        print(f"Stage 4 (LLM Correction): {stage_counts['stage_4']:,} messages")
        if stage_counts["stage_3"] > 0:
            pct = (stage_counts["stage_4"] / stage_counts["stage_3"]) * 100
            print(f"  → {pct:.1f}% of Stage 3 processed")
    else:
        print("Stage 4 (LLM Correction): Not run")

    if stage_counts["stage_5"] > 0:
        print(f"Stage 5 (Ready Messages):  {stage_counts['stage_5']:,} messages")
        if stage_counts["stage_4"] > 0:
            pct = (stage_counts["stage_5"] / stage_counts["stage_4"]) * 100
            print(f"  → {pct:.1f}% of Stage 4 ready")
    else:
        print("Stage 5 (Ready Messages): Not run")

    print("\n" + "="*80)

    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-"*80)

    if stage_counts["stage_0"] == -1:
        print("1. Run Stage 0 to extract messages from TruthService")
    elif stage_counts["stage_1"] == -1 or (stage_counts["stage_1"] > 0 and stage_counts["stage_1"] < stage_counts["stage_0"]):
        remaining = stage_counts["stage_0"] - stage_counts["stage_1"] if stage_counts["stage_1"] > 0 else stage_counts["stage_0"]
        print(f"1. Run Stage 1 to enrich {remaining:,} messages")
    elif stage_counts["stage_3"] == -1 or (stage_counts["stage_3"] > 0 and stage_counts["stage_3"] < stage_counts["stage_1"]):
        remaining = stage_counts["stage_1"] - stage_counts["stage_3"] if stage_counts["stage_3"] > 0 else stage_counts["stage_1"]
        print(f"1. Run Stage 3 to register {remaining:,} entity_ids")
    elif stage_counts["stage_4"] == -1 or (stage_counts["stage_4"] > 0 and stage_counts["stage_4"] < stage_counts["stage_3"]):
        remaining = stage_counts["stage_3"] - stage_counts["stage_4"] if stage_counts["stage_4"] > 0 else stage_counts["stage_3"]
        print(f"1. Run Stage 4 to correct {remaining:,} messages")
    else:
        print("1. ✅ All stages complete!")

    print("="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())
from __future__ import annotations
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
from __future__ import annotations

#!/usr/bin/env python3
"""Check pipeline status and message counts for claude_code pipeline."""
from __future__ import annotations

from pathlib import Path

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_logger
from src.services.central_services.core.config import get_bigquery_client

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"

TABLES = {
    "stage_0": "claude_code_stage_0",
    "stage_1": "claude_code_stage_1",
    "stage_3": "claude_code_stage_3",
    "stage_4": "claude_code_stage_4",
    "stage_5": "claude_code_stage_5",
}

def check_table_exists(client, table_name: str) -> bool:
    """Check if a table exists."""
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        client.get_table(table_ref)
        return True
    except Exception:
        return False

def get_table_count(client, table_name: str) -> int:
    """Get row count for a table."""
    if not check_table_exists(client, table_name):
        return -1  # Table doesn't exist

    try:
        query = f"""
        SELECT COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        """
        result = list(client.query(query).result())
        if result:
            return result[0].count
        return 0
    except Exception as e:
        logger.warning(f"Error counting {table_name}: {e}")
        return -1

def get_source_breakdown(client, table_name: str) -> dict:
    """Get message count by source."""
    if not check_table_exists(client, table_name):
        return {}

    try:
        query = f"""
        SELECT
            source_name,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        GROUP BY source_name
        ORDER BY source_name
        """
        results = {}
        for row in client.query(query).result():
            results[row.source_name] = row.count
        return results
    except Exception as e:
        logger.warning(f"Error getting source breakdown for {table_name}: {e}")
        return {}

def main():
    """Main execution function."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("CLAUDE CODEX GITHUB PIPELINE STATUS")
    print("="*80 + "\n")

    # Get counts for each stage
    stage_counts = {}
    for stage_name, table_name in TABLES.items():
        count = get_table_count(bq_client, table_name)
        stage_counts[stage_name] = count

        status = "✅ EXISTS" if count >= 0 else "❌ MISSING"
        count_str = f"{count:,}" if count >= 0 else "N/A"
        print(f"{stage_name.upper():12} {status:12} {count_str:>12} messages")

    print("\n" + "-"*80)
    print("SOURCE BREAKDOWN (Stage 3 - Registered Messages)")
    print("-"*80)

    if stage_counts["stage_3"] > 0:
        source_breakdown = get_source_breakdown(bq_client, TABLES["stage_3"])
        for source, count in source_breakdown.items():
            print(f"  {source:20} {count:>12,} messages")
    else:
        print("  No data in Stage 3")

    print("\n" + "-"*80)
    print("PIPELINE PROGRESS")
    print("-"*80)

    # Calculate progress
    if stage_counts["stage_0"] > 0:
        print(f"Stage 0 (Extraction):     {stage_counts['stage_0']:,} messages")
    else:
        print("Stage 0 (Extraction):     Not run")

    if stage_counts["stage_1"] > 0:
        print(f"Stage 1 (Enrichment):    {stage_counts['stage_1']:,} messages")
        if stage_counts["stage_0"] > 0:
            pct = (stage_counts["stage_1"] / stage_counts["stage_0"]) * 100
            print(f"  → {pct:.1f}% of Stage 0 processed")
    else:
        print("Stage 1 (Enrichment):    Not run")

    if stage_counts["stage_3"] > 0:
        print(f"Stage 3 (ID Registration): {stage_counts['stage_3']:,} messages")
        if stage_counts["stage_1"] > 0:
            pct = (stage_counts["stage_3"] / stage_counts["stage_1"]) * 100
            print(f"  → {pct:.1f}% of Stage 1 processed")
    else:
        print("Stage 3 (ID Registration): Not run")

    if stage_counts["stage_4"] > 0:
        print(f"Stage 4 (LLM Correction): {stage_counts['stage_4']:,} messages")
        if stage_counts["stage_3"] > 0:
            pct = (stage_counts["stage_4"] / stage_counts["stage_3"]) * 100
            print(f"  → {pct:.1f}% of Stage 3 processed")
    else:
        print("Stage 4 (LLM Correction): Not run")

    if stage_counts["stage_5"] > 0:
        print(f"Stage 5 (Ready Messages):  {stage_counts['stage_5']:,} messages")
        if stage_counts["stage_4"] > 0:
            pct = (stage_counts["stage_5"] / stage_counts["stage_4"]) * 100
            print(f"  → {pct:.1f}% of Stage 4 ready")
    else:
        print("Stage 5 (Ready Messages): Not run")

    print("\n" + "="*80)

    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-"*80)

    if stage_counts["stage_0"] == -1:
        print("1. Run Stage 0 to extract messages from TruthService")
    elif stage_counts["stage_1"] == -1 or (stage_counts["stage_1"] > 0 and stage_counts["stage_1"] < stage_counts["stage_0"]):
        remaining = stage_counts["stage_0"] - stage_counts["stage_1"] if stage_counts["stage_1"] > 0 else stage_counts["stage_0"]
        print(f"1. Run Stage 1 to enrich {remaining:,} messages")
    elif stage_counts["stage_3"] == -1 or (stage_counts["stage_3"] > 0 and stage_counts["stage_3"] < stage_counts["stage_1"]):
        remaining = stage_counts["stage_1"] - stage_counts["stage_3"] if stage_counts["stage_3"] > 0 else stage_counts["stage_1"]
        print(f"1. Run Stage 3 to register {remaining:,} entity_ids")
    elif stage_counts["stage_4"] == -1 or (stage_counts["stage_4"] > 0 and stage_counts["stage_4"] < stage_counts["stage_3"]):
        remaining = stage_counts["stage_3"] - stage_counts["stage_4"] if stage_counts["stage_4"] > 0 else stage_counts["stage_3"]
        print(f"1. Run Stage 4 to correct {remaining:,} messages")
    else:
        print("1. ✅ All stages complete!")

    print("="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())

script_id = "pipelines.claude_code.scripts.utilities.check_pipeline_status.py"

import sys
from pathlib import Path

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_logger
from src.services.central_services.core.config import get_bigquery_client

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"

TABLES = {
    "stage_0": "claude_code_stage_0",
    "stage_1": "claude_code_stage_1",
    "stage_3": "claude_code_stage_3",
    "stage_4": "claude_code_stage_4",
    "stage_5": "claude_code_stage_5",
}

def check_table_exists(client, table_name: str) -> bool:
    """Check if a table exists."""
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        client.get_table(table_ref)
        return True
    except Exception:
        return False

def get_table_count(client, table_name: str) -> int:
    """Get row count for a table."""
    if not check_table_exists(client, table_name):
        return -1  # Table doesn't exist

    try:
        query = f"""
        SELECT COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        """
        result = list(client.query(query).result())
        if result:
            return result[0].count
        return 0
    except Exception as e:
        logger.warning(f"Error counting {table_name}: {e}")
        return -1

def get_source_breakdown(client, table_name: str) -> dict:
    """Get message count by source."""
    if not check_table_exists(client, table_name):
        return {}

    try:
        query = f"""
        SELECT
            source_name,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE level = 5
        GROUP BY source_name
        ORDER BY source_name
        """
        results = {}
        for row in client.query(query).result():
            results[row.source_name] = row.count
        return results
    except Exception as e:
        logger.warning(f"Error getting source breakdown for {table_name}: {e}")
        return {}

def main():
    """Main execution function."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("CLAUDE CODEX GITHUB PIPELINE STATUS")
    print("="*80 + "\n")

    # Get counts for each stage
    stage_counts = {}
    for stage_name, table_name in TABLES.items():
        count = get_table_count(bq_client, table_name)
        stage_counts[stage_name] = count

        status = "✅ EXISTS" if count >= 0 else "❌ MISSING"
        count_str = f"{count:,}" if count >= 0 else "N/A"
        print(f"{stage_name.upper():12} {status:12} {count_str:>12} messages")

    print("\n" + "-"*80)
    print("SOURCE BREAKDOWN (Stage 3 - Registered Messages)")
    print("-"*80)

    if stage_counts["stage_3"] > 0:
        source_breakdown = get_source_breakdown(bq_client, TABLES["stage_3"])
        for source, count in source_breakdown.items():
            print(f"  {source:20} {count:>12,} messages")
    else:
        print("  No data in Stage 3")

    print("\n" + "-"*80)
    print("PIPELINE PROGRESS")
    print("-"*80)

    # Calculate progress
    if stage_counts["stage_0"] > 0:
        print(f"Stage 0 (Extraction):     {stage_counts['stage_0']:,} messages")
    else:
        print("Stage 0 (Extraction):     Not run")

    if stage_counts["stage_1"] > 0:
        print(f"Stage 1 (Enrichment):    {stage_counts['stage_1']:,} messages")
        if stage_counts["stage_0"] > 0:
            pct = (stage_counts["stage_1"] / stage_counts["stage_0"]) * 100
            print(f"  → {pct:.1f}% of Stage 0 processed")
    else:
        print("Stage 1 (Enrichment):    Not run")

    if stage_counts["stage_3"] > 0:
        print(f"Stage 3 (ID Registration): {stage_counts['stage_3']:,} messages")
        if stage_counts["stage_1"] > 0:
            pct = (stage_counts["stage_3"] / stage_counts["stage_1"]) * 100
            print(f"  → {pct:.1f}% of Stage 1 processed")
    else:
        print("Stage 3 (ID Registration): Not run")

    if stage_counts["stage_4"] > 0:
        print(f"Stage 4 (LLM Correction): {stage_counts['stage_4']:,} messages")
        if stage_counts["stage_3"] > 0:
            pct = (stage_counts["stage_4"] / stage_counts["stage_3"]) * 100
            print(f"  → {pct:.1f}% of Stage 3 processed")
    else:
        print("Stage 4 (LLM Correction): Not run")

    if stage_counts["stage_5"] > 0:
        print(f"Stage 5 (Ready Messages):  {stage_counts['stage_5']:,} messages")
        if stage_counts["stage_4"] > 0:
            pct = (stage_counts["stage_5"] / stage_counts["stage_4"]) * 100
            print(f"  → {pct:.1f}% of Stage 4 ready")
    else:
        print("Stage 5 (Ready Messages): Not run")

    print("\n" + "="*80)

    # Recommendations
    print("\nRECOMMENDATIONS:")
    print("-"*80)

    if stage_counts["stage_0"] == -1:
        print("1. Run Stage 0 to extract messages from TruthService")
    elif stage_counts["stage_1"] == -1 or (stage_counts["stage_1"] > 0 and stage_counts["stage_1"] < stage_counts["stage_0"]):
        remaining = stage_counts["stage_0"] - stage_counts["stage_1"] if stage_counts["stage_1"] > 0 else stage_counts["stage_0"]
        print(f"1. Run Stage 1 to enrich {remaining:,} messages")
    elif stage_counts["stage_3"] == -1 or (stage_counts["stage_3"] > 0 and stage_counts["stage_3"] < stage_counts["stage_1"]):
        remaining = stage_counts["stage_1"] - stage_counts["stage_3"] if stage_counts["stage_3"] > 0 else stage_counts["stage_1"]
        print(f"1. Run Stage 3 to register {remaining:,} entity_ids")
    elif stage_counts["stage_4"] == -1 or (stage_counts["stage_4"] > 0 and stage_counts["stage_4"] < stage_counts["stage_3"]):
        remaining = stage_counts["stage_3"] - stage_counts["stage_4"] if stage_counts["stage_4"] > 0 else stage_counts["stage_3"]
        print(f"1. Run Stage 4 to correct {remaining:,} messages")
    else:
        print("1. ✅ All stages complete!")

    print("="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
