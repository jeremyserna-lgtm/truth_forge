#!/usr/bin/env python3

"""Check how many messages are available in the source (entity_unified)."""

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
SOURCE_TABLE = "entity_unified"

def check_source_messages(client):
    """Check how many messages are available in entity_unified."""
    # Extract source_name from source_pipeline or source_file
    query = f"""
    SELECT
        CASE
          WHEN LOWER(source_pipeline) LIKE '%claude_code%' OR LOWER(source_file) LIKE '%claude_code%' THEN 'claude_code'
          WHEN LOWER(source_pipeline) LIKE '%codex%' OR LOWER(source_file) LIKE '%codex%' THEN 'codex'
          WHEN LOWER(source_pipeline) LIKE '%github%' OR LOWER(source_file) LIKE '%github%' THEN 'github'
          ELSE 'unknown'
        END as source_name,
        COUNT(*) as count
    FROM `{PROJECT_ID}.{DATASET_ID}.{SOURCE_TABLE}`
    WHERE level = 5
      AND text IS NOT NULL
      AND text != ''
      AND LENGTH(TRIM(text)) >= 10
      AND (
        LOWER(source_pipeline) LIKE '%claude_code%' OR LOWER(source_file) LIKE '%claude_code%' OR
        LOWER(source_pipeline) LIKE '%codex%' OR LOWER(source_file) LIKE '%codex%' OR
        LOWER(source_pipeline) LIKE '%github%' OR LOWER(source_file) LIKE '%github%'
      )
      AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)  -- Partition filter
    GROUP BY source_name
    ORDER BY source_name
    """

    try:
        results = {}
        total = 0
        for row in client.query(query).result():
            if row.source_name != 'unknown':
                results[row.source_name] = row.count
                total += row.count

        return results, total
    except Exception as e:
        logger.error(f"Error checking source messages: {e}", exc_info=True)
        return {}, 0

def main():
    """Main execution function."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("SOURCE MESSAGES AVAILABLE (entity_unified)")
    print("="*80 + "\n")

    results, total = check_source_messages(bq_client)

    if results:
        for source, count in results.items():
            print(f"{source:20} {count:>12,} messages")
        print("-"*80)
        print(f"{'TOTAL':20} {total:>12,} messages")
    else:
        print("No messages found in source table")
        print("(Make sure entity_unified table exists and has data)")

    print("="*80 + "\n")

    return total

if __name__ == "__main__":
    exit(main() if main() > 0 else 1)

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
SOURCE_TABLE = "entity_unified"

def check_source_messages(client):
    """Check how many messages are available in entity_unified."""
    # Extract source_name from source_pipeline or source_file
    query = f"""
    SELECT
        CASE
          WHEN LOWER(source_pipeline) LIKE '%claude_code%' OR LOWER(source_file) LIKE '%claude_code%' THEN 'claude_code'
          WHEN LOWER(source_pipeline) LIKE '%codex%' OR LOWER(source_file) LIKE '%codex%' THEN 'codex'
          WHEN LOWER(source_pipeline) LIKE '%github%' OR LOWER(source_file) LIKE '%github%' THEN 'github'
          ELSE 'unknown'
        END as source_name,
        COUNT(*) as count
    FROM `{PROJECT_ID}.{DATASET_ID}.{SOURCE_TABLE}`
    WHERE level = 5
      AND text IS NOT NULL
      AND text != ''
      AND LENGTH(TRIM(text)) >= 10
      AND (
        LOWER(source_pipeline) LIKE '%claude_code%' OR LOWER(source_file) LIKE '%claude_code%' OR
        LOWER(source_pipeline) LIKE '%codex%' OR LOWER(source_file) LIKE '%codex%' OR
        LOWER(source_pipeline) LIKE '%github%' OR LOWER(source_file) LIKE '%github%'
      )
      AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)  -- Partition filter
    GROUP BY source_name
    ORDER BY source_name
    """

    try:
        results = {}
        total = 0
        for row in client.query(query).result():
            if row.source_name != 'unknown':
                results[row.source_name] = row.count
                total += row.count

        return results, total
    except Exception as e:
        logger.error(f"Error checking source messages: {e}", exc_info=True)
        return {}, 0

def main():
    """Main execution function."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("SOURCE MESSAGES AVAILABLE (entity_unified)")
    print("="*80 + "\n")

    results, total = check_source_messages(bq_client)

    if results:
        for source, count in results.items():
            print(f"{source:20} {count:>12,} messages")
        print("-"*80)
        print(f"{'TOTAL':20} {total:>12,} messages")
    else:
        print("No messages found in source table")
        print("(Make sure entity_unified table exists and has data)")

    print("="*80 + "\n")

    return total

if __name__ == "__main__":
    exit(main() if main() > 0 else 1)
