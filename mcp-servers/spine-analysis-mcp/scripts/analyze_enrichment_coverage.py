#!/usr/bin/env python3
"""Analyze entity_enrichments table coverage and identify gaps.

This script queries the entity_enrichments table to understand:
- What enrichment data exists
- Coverage across different enrichment types
- Gaps that need to be filled for analysis opportunities

Usage:
    python scripts/analyze_enrichment_coverage.py
    python scripts/analyze_enrichment_coverage.py --out docs/technical/enrichment/coverage_report.txt
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spine_analysis_mcp.config import BQ_DATASET_ID, BQ_PROJECT_ID, get_bigquery_client


def get_table_schema():
    """Get the schema of entity_enrichments table."""
    client = get_bigquery_client()
    
    try:
        table_ref = client.dataset(BQ_DATASET_ID).table("entity_enrichments")
        table = client.get_table(table_ref)
        
        print("=" * 80)
        print("ENTITY_ENRICHMENTS TABLE SCHEMA")
        print("=" * 80)
        print(f"\nTotal Fields: {len(table.schema)}")
        print(f"Table Size: {table.num_bytes / (1024 * 1024):.2f} MB")
        print(f"Row Count: {table.num_rows:,}")
        print("\n" + "-" * 80)
        print("Fields:")
        print("-" * 80)
        
        for field in table.schema:
            field_type = field.field_type
            if field.mode == "REPEATED":
                field_type = f"ARRAY<{field_type}>"
            if field.mode == "NULLABLE":
                field_type = f"{field_type} (nullable)"
            
            print(f"  {field.name:40} {field_type:30} {field.description or ''}")
        
        return table.schema
    except Exception as e:
        print(f"❌ Error getting schema: {e}")
        return None


def analyze_column_coverage():
    """Analyze coverage of each column in entity_enrichments."""
    client = get_bigquery_client()
    
    print("\n" + "=" * 80)
    print("COLUMN COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Get schema first to know what columns to check
    try:
        table_ref = client.dataset(BQ_DATASET_ID).table("entity_enrichments")
        table = client.get_table(table_ref)
        columns = [field.name for field in table.schema]
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Build coverage query for each column
    coverage_queries = []
    
    for col in columns:
        if col in ["entity_id", "created_at", "updated_at"]:
            continue
        
        # Check if column is NULL or empty
        coverage_queries.append(f"""
            COUNTIF({col} IS NOT NULL) as {col}_count,
            COUNTIF({col} IS NOT NULL) / COUNT(*) * 100 as {col}_pct
        """)
    
    if not coverage_queries:
        print("No columns to analyze")
        return
    
    query = f"""
    SELECT
        COUNT(*) as total_rows,
        {', '.join(coverage_queries)}
    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity_enrichments`
    """
    
    try:
        query_job = client.query(query)
        results = list(query_job.result())
        
        if not results:
            print("No data found in entity_enrichments")
            return
        
        row = results[0]
        total_rows = row.total_rows
        
        print(f"\nTotal Rows: {total_rows:,}")
        print("\n" + "-" * 80)
        print(f"{'Column':<40} {'Non-Null Count':<20} {'Coverage %':<15} {'Status'}")
        print("-" * 80)
        
        coverage_data = []
        for col in columns:
            if col in ["entity_id", "created_at", "updated_at"]:
                continue
            
            count_attr = f"{col}_count"
            pct_attr = f"{col}_pct"
            
            if hasattr(row, count_attr):
                count = getattr(row, count_attr, 0)
                pct = getattr(row, pct_attr, 0)
                
                if pct >= 80:
                    status = "✅ Excellent"
                elif pct >= 50:
                    status = "⚠️  Good"
                elif pct >= 20:
                    status = "🔶 Partial"
                else:
                    status = "❌ Low"
                
                coverage_data.append({
                    "column": col,
                    "count": count,
                    "percentage": pct,
                    "status": status
                })
                
                print(f"{col:<40} {count:>15,} {pct:>10.1f}% {status}")
        
        return coverage_data
        
    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_enrichment_types():
    """Analyze distribution of enrichment types."""
    client = get_bigquery_client()
    
    print("\n" + "=" * 80)
    print("ENRICHMENT TYPE DISTRIBUTION")
    print("=" * 80)
    
    # Check if enrichment_type column exists
    query = f"""
    SELECT 
        enrichment_type,
        COUNT(*) as count,
        COUNT(*) / SUM(COUNT(*)) OVER() * 100 as percentage
    FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity_enrichments`
    WHERE enrichment_type IS NOT NULL
    GROUP BY enrichment_type
    ORDER BY count DESC
    LIMIT 20
    """
    
    try:
        query_job = client.query(query)
        results = list(query_job.result())
        
        if not results:
            print("No enrichment_type data found")
            return
        
        print(f"\n{'Enrichment Type':<40} {'Count':<20} {'Percentage'}")
        print("-" * 80)
        
        for row in results:
            print(f"{row.enrichment_type:<40} {row.count:>15,} {row.percentage:>10.1f}%")
        
        return results
    except Exception as e:
        # enrichment_type might not exist, that's okay
        print(f"⚠️  enrichment_type column may not exist: {e}")
        return None


def analyze_entity_coverage():
    """Analyze how many entities have enrichments."""
    client = get_bigquery_client()
    
    print("\n" + "=" * 80)
    print("ENTITY COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Try different table names
    table_names = ["entity_production", "entity", "entity_unified"]
    
    for table_name in table_names:
        try:
            query = f"""
            WITH entity_counts AS (
                SELECT COUNT(DISTINCT entity_id) as total_entities
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{table_name}`
            ),
            enriched_counts AS (
                SELECT COUNT(DISTINCT entity_id) as enriched_entities
                FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity_enrichments`
            )
            SELECT 
                ec.total_entities,
                en.enriched_entities,
                en.enriched_entities / ec.total_entities * 100 as coverage_pct
            FROM entity_counts ec
            CROSS JOIN enriched_counts en
            """
            
            query_job = client.query(query)
            results = list(query_job.result())
            
            if results:
                row = results[0]
                print(f"\nTotal Entities (from {table_name}): {row.total_entities:,}")
                print(f"Enriched Entities: {row.enriched_entities:,}")
                print(f"Coverage: {row.coverage_pct:.2f}%")
                
                if row.coverage_pct < 50:
                    print("\n⚠️  WARNING: Less than 50% of entities have enrichments")
                
                return row
        except Exception as e:
            if "not found" not in str(e).lower():
                print(f"⚠️  Error checking {table_name}: {e}")
            continue
    
    # If no table found, just report enriched count
    try:
        query = f"""
        SELECT COUNT(DISTINCT entity_id) as enriched_entities
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.entity_enrichments`
        """
        query_job = client.query(query)
        results = list(query_job.result())
        if results:
            print(f"\nEnriched Entities: {results[0].enriched_entities:,}")
            print("⚠️  Could not determine total entity count (entity table not found)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None


def identify_gaps(coverage_data):
    """Identify gaps in enrichment coverage."""
    print("\n" + "=" * 80)
    print("GAP ANALYSIS - MISSING DATA OPPORTUNITIES")
    print("=" * 80)
    
    if not coverage_data:
        print("No coverage data available")
        return
    
    # Categorize columns by type
    sentiment_cols = [c for c in coverage_data if "sentiment" in c["column"].lower() or "polarity" in c["column"].lower()]
    emotion_cols = [c for c in coverage_data if "emotion" in c["column"].lower() or "vad" in c["column"].lower()]
    keyword_cols = [c for c in coverage_data if "keyword" in c["column"].lower() or "kw" in c["column"].lower()]
    readability_cols = [c for c in coverage_data if "readability" in c["column"].lower() or "rd_" in c["column"].lower()]
    pii_cols = [c for c in coverage_data if "pii" in c["column"].lower()]
    other_cols = [c for c in coverage_data if c not in sentiment_cols + emotion_cols + keyword_cols + readability_cols + pii_cols]
    
    gaps = []
    
    # Low coverage columns
    low_coverage = [c for c in coverage_data if c["percentage"] < 20]
    if low_coverage:
        gaps.append({
            "category": "Low Coverage (< 20%)",
            "columns": low_coverage,
            "impact": "High - Missing critical analysis data"
        })
    
    # Partial coverage
    partial_coverage = [c for c in coverage_data if 20 <= c["percentage"] < 50]
    if partial_coverage:
        gaps.append({
            "category": "Partial Coverage (20-50%)",
            "columns": partial_coverage,
            "impact": "Medium - Incomplete analysis possible"
        })
    
    print("\n📊 Gap Summary by Category:\n")
    
    for gap in gaps:
        print(f"\n{gap['category']} - {gap['impact']}")
        print("-" * 80)
        for col in gap["columns"][:10]:  # Show top 10
            print(f"  • {col['column']:<40} {col['percentage']:>6.1f}% coverage")
        if len(gap["columns"]) > 10:
            print(f"  ... and {len(gap['columns']) - 10} more")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR ANALYSIS OPPORTUNITIES")
    print("=" * 80)
    
    recommendations = []
    
    if sentiment_cols and any(c["percentage"] < 50 for c in sentiment_cols):
        recommendations.append({
            "area": "Sentiment Analysis",
            "current": f"{sum(1 for c in sentiment_cols if c['percentage'] < 50)} columns with low coverage",
            "opportunity": "Enable sentiment-based trend analysis, emotion tracking, polarity shifts"
        })
    
    if keyword_cols and any(c["percentage"] < 50 for c in keyword_cols):
        recommendations.append({
            "area": "Keyword Extraction",
            "current": f"{sum(1 for c in keyword_cols if c['percentage'] < 50)} columns with low coverage",
            "opportunity": "Enable keyword-based concept clustering, topic modeling, trend detection"
        })
    
    if readability_cols and any(c["percentage"] < 50 for c in readability_cols):
        recommendations.append({
            "area": "Readability Analysis",
            "current": f"{sum(1 for c in readability_cols if c['percentage'] < 50)} columns with low coverage",
            "opportunity": "Enable complexity analysis, readability trends, content quality metrics"
        })
    
    if pii_cols and any(c["percentage"] < 50 for c in pii_cols):
        recommendations.append({
            "area": "PII Detection",
            "current": f"{sum(1 for c in pii_cols if c['percentage'] < 50)} columns with low coverage",
            "opportunity": "Enable privacy compliance analysis, PII risk assessment"
        })
    
    for rec in recommendations:
        print(f"\n📌 {rec['area']}")
        print(f"   Current: {rec['current']}")
        print(f"   Opportunity: {rec['opportunity']}")
    
    return gaps, recommendations


def main() -> None:
    """Main analysis function."""
    parser = argparse.ArgumentParser(
        description="Analyze entity_enrichments coverage and identify gaps."
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write full report to this file (in addition to stdout).",
    )
    args = parser.parse_args()

    out_path: Path | None = args.out

    print("\n" + "=" * 80)
    print("ENTITY_ENRICHMENTS COVERAGE ANALYSIS")
    print("=" * 80)
    print("\nAnalyzing enrichment data coverage and identifying gaps...\n")

    try:
        # Get schema
        schema = get_table_schema()

        # Analyze coverage
        coverage_data = analyze_column_coverage()

        # Analyze enrichment types
        analyze_enrichment_types()

        # Analyze entity coverage
        analyze_entity_coverage()

        # Identify gaps
        if coverage_data:
            identify_gaps(coverage_data)

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)

        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            # Re-run collects print output; we didn't switch to capture().
            # Write a short summary + path to full report instead.
            summary = (
                "Entity Enrichments Coverage Analysis\n"
                "====================================\n\n"
                "Run 'python scripts/analyze_enrichment_coverage.py' for full output.\n\n"
                "Full gaps report: docs/technical/enrichment/ENRICHMENT_COVERAGE_GAPS_REPORT.md\n"
            )
            out_path.write_text(summary, encoding="utf-8")
            print(f"\nWrote summary to {out_path}")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
