#!/usr/bin/env python3
"""
Text Quality Assessment Script

Assesses text quality in Stage 0 to determine if Stage 2 (Normalization) is needed.

Usage:
    python assess_text_quality.py
"""
from __future__ import annotations

#!/usr/bin/env python3
"""
Text Quality Assessment Script

Assesses text quality in Stage 0 to determine if Stage 2 (Normalization) is needed.

Usage:
    python assess_text_quality.py
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


script_id = "pipelines.claude_code.scripts.assessment.assess_text_quality.py"

import sys
from pathlib import Path

# Add project root and src to path
PROJECT_ROOT = Path(__file__).resolve().parents[5]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "src"))

from src.services.central_services.core import get_current_run_id, get_logger
from src.services.central_services.core.config import get_bigquery_client
from google.cloud import bigquery

logger = get_logger(__name__)

PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"
STAGE_0_TABLE = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_0"

def assess_text_quality():
    """Assess text quality and provide recommendations."""

    run_id = get_current_run_id()

    logger.info(
        "Starting text quality assessment",
        extra={"run_id": run_id, "table": STAGE_0_TABLE}
    )

    # Get BigQuery client
    client = get_bigquery_client()
    if hasattr(client, 'client'):
        bq_client = client.client
    else:
        bq_client = client

    query = f"""
    SELECT
      source_name,
      COUNT(*) as total_messages,

      -- Whitespace issues
      COUNT(CASE WHEN text LIKE '%  %' THEN 1 END) as double_space_count,
      ROUND(COUNT(CASE WHEN text LIKE '%  %' THEN 1 END) * 100.0 / COUNT(*), 2) as double_space_pct,

      COUNT(CASE WHEN text LIKE '%\\n\\n\\n%' THEN 1 END) as triple_newline_count,
      COUNT(CASE WHEN text LIKE '%\\t%' THEN 1 END) as tab_count,

      -- Leading/trailing whitespace
      COUNT(CASE WHEN LENGTH(text) != LENGTH(TRIM(text)) THEN 1 END) as whitespace_trim_count,
      ROUND(COUNT(CASE WHEN LENGTH(text) != LENGTH(TRIM(text)) THEN 1 END) * 100.0 / COUNT(*), 2) as whitespace_trim_pct,

      -- Text length stats
      AVG(LENGTH(text)) as avg_length,
      MIN(LENGTH(text)) as min_length,
      MAX(LENGTH(text)) as max_length,

      -- Empty/null text
      COUNT(CASE WHEN text IS NULL OR LENGTH(TRIM(text)) = 0 THEN 1 END) as empty_text_count

    FROM `{STAGE_0_TABLE}`
    GROUP BY source_name
    ORDER BY source_name
    """

    try:
        query_job = bq_client.query(query)
        results = list(query_job.result())

        if not results:
            print("❌ No data found in Stage 0 table. Run Stage 0 first.")
            return 1

        print("\n" + "="*80)
        print("TEXT QUALITY ASSESSMENT RESULTS")
        print("="*80)

        needs_normalization = False

        for row in results:
            print(f"\n📊 Source: {row.source_name}")
            print(f"   Total Messages: {row.total_messages:,}")
            print(f"\n   Whitespace Issues:")
            print(f"   - Double Spaces: {row.double_space_count:,} ({row.double_space_pct}%)")
            print(f"   - Triple Newlines: {row.triple_newline_count:,}")
            print(f"   - Tabs: {row.tab_count:,}")
            print(f"   - Leading/Trailing Whitespace: {row.whitespace_trim_count:,} ({row.whitespace_trim_pct}%)")
            print(f"\n   Text Length:")
            print(f"   - Average: {row.avg_length:.0f} chars")
            print(f"   - Min: {row.min_length} chars")
            print(f"   - Max: {row.max_length:,} chars")
            print(f"   - Empty/Null: {row.empty_text_count:,}")

            # Determine if normalization needed
            issues = (
                row.double_space_count > 0 or
                row.triple_newline_count > 0 or
                row.tab_count > 0 or
                row.whitespace_trim_pct > 5.0  # More than 5% have whitespace issues
            )

            if issues:
                needs_normalization = True
                print(f"\n   ⚠️  RECOMMENDATION: Stage 2 (Normalization) is RECOMMENDED")
            else:
                print(f"\n   ✅ RECOMMENDATION: Stage 2 (Normalization) can be SKIPPED")

        print("\n" + "="*80)
        if needs_normalization:
            print("OVERALL RECOMMENDATION: ⚠️  Implement Stage 2 (Text Normalization)")
        else:
            print("OVERALL RECOMMENDATION: ✅ Skip Stage 2 (Text Normalization)")
        print("="*80 + "\n")

        return 0

    except Exception as e:
        logger.error(f"Error assessing text quality: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    exit(assess_text_quality())
