#!/usr/bin/env python3

"""Check what's actually in entity_unified table."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_logger
from src.services.central_services.core.config import get_bigquery_client

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
TABLE = "entity_unified"

def check_table():
    """Check entity_unified table structure and sample data."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("ENTITY_UNIFIED TABLE ANALYSIS")
    print("="*80 + "\n")

    # Check total rows
    try:
        query = f"""
        SELECT COUNT(*) as total
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
        """
        result = list(bq_client.query(query).result())
        total = result[0].total if result else 0
        print(f"Total L5 messages (last 365 days): {total:,}\n")
    except Exception as e:
        print(f"Error counting: {e}\n")
        return

    # Check source_pipeline values
    try:
        query = f"""
        SELECT
            source_pipeline,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
          AND source_pipeline IS NOT NULL
        GROUP BY source_pipeline
        ORDER BY count DESC
        LIMIT 20
        """
        print("Top source_pipeline values:")
        for row in bq_client.query(query).result():
            print(f"  {row.source_pipeline:50} {row.count:>10,}")
        print()
    except Exception as e:
        print(f"Error checking source_pipeline: {e}\n")

    # Check source_file patterns
    try:
        query = f"""
        SELECT
            CASE
              WHEN LOWER(source_file) LIKE '%claude%' OR LOWER(source_pipeline) LIKE '%claude%' THEN 'claude_related'
              WHEN LOWER(source_file) LIKE '%codex%' OR LOWER(source_pipeline) LIKE '%codex%' THEN 'codex_related'
              WHEN LOWER(source_file) LIKE '%github%' OR LOWER(source_pipeline) LIKE '%github%' THEN 'github_related'
              ELSE 'other'
            END as category,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
        GROUP BY category
        ORDER BY count DESC
        """
        print("Source categories:")
        for row in bq_client.query(query).result():
            print(f"  {row.category:20} {row.count:>10,}")
        print()
    except Exception as e:
        print(f"Error checking categories: {e}\n")

    # Sample rows
    try:
        query = f"""
        SELECT
            entity_id,
            source_pipeline,
            source_file,
            LEFT(text, 50) as text_sample,
            content_date
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
        ORDER BY content_date DESC
        LIMIT 5
        """
        print("Sample rows:")
        for row in bq_client.query(query).result():
            print(f"  {row.entity_id[:20]}... | {row.source_pipeline or 'NULL':30} | {row.text_sample}")
        print()
    except Exception as e:
        print(f"Error getting samples: {e}\n")

    print("="*80 + "\n")

if __name__ == "__main__":
    check_table()

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_logger
from src.services.central_services.core.config import get_bigquery_client

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
TABLE = "entity_unified"

def check_table():
    """Check entity_unified table structure and sample data."""
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    print("\n" + "="*80)
    print("ENTITY_UNIFIED TABLE ANALYSIS")
    print("="*80 + "\n")

    # Check total rows
    try:
        query = f"""
        SELECT COUNT(*) as total
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
        """
        result = list(bq_client.query(query).result())
        total = result[0].total if result else 0
        print(f"Total L5 messages (last 365 days): {total:,}\n")
    except Exception as e:
        print(f"Error counting: {e}\n")
        return

    # Check source_pipeline values
    try:
        query = f"""
        SELECT
            source_pipeline,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
          AND source_pipeline IS NOT NULL
        GROUP BY source_pipeline
        ORDER BY count DESC
        LIMIT 20
        """
        print("Top source_pipeline values:")
        for row in bq_client.query(query).result():
            print(f"  {row.source_pipeline:50} {row.count:>10,}")
        print()
    except Exception as e:
        print(f"Error checking source_pipeline: {e}\n")

    # Check source_file patterns
    try:
        query = f"""
        SELECT
            CASE
              WHEN LOWER(source_file) LIKE '%claude%' OR LOWER(source_pipeline) LIKE '%claude%' THEN 'claude_related'
              WHEN LOWER(source_file) LIKE '%codex%' OR LOWER(source_pipeline) LIKE '%codex%' THEN 'codex_related'
              WHEN LOWER(source_file) LIKE '%github%' OR LOWER(source_pipeline) LIKE '%github%' THEN 'github_related'
              ELSE 'other'
            END as category,
            COUNT(*) as count
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
        GROUP BY category
        ORDER BY count DESC
        """
        print("Source categories:")
        for row in bq_client.query(query).result():
            print(f"  {row.category:20} {row.count:>10,}")
        print()
    except Exception as e:
        print(f"Error checking categories: {e}\n")

    # Sample rows
    try:
        query = f"""
        SELECT
            entity_id,
            source_pipeline,
            source_file,
            LEFT(text, 50) as text_sample,
            content_date
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE}`
        WHERE level = 5
          AND content_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
        ORDER BY content_date DESC
        LIMIT 5
        """
        print("Sample rows:")
        for row in bq_client.query(query).result():
            print(f"  {row.entity_id[:20]}... | {row.source_pipeline or 'NULL':30} | {row.text_sample}")
        print()
    except Exception as e:
        print(f"Error getting samples: {e}\n")

    print("="*80 + "\n")

if __name__ == "__main__":
    check_table()
