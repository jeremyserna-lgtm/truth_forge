#!/usr/bin/env python3
"""
Analyze existing BigQuery enrichments for Genesis training

Queries:
- entities_unified schema and sample data
- entities_enrichments schema and sample data  
- entities_embeddings schema and sample data

Identifies:
- What enrichments already exist
- What metadata fields are available
- What patterns/framework elements are tagged
- Gaps between current state and Genesis requirements

Outputs analysis to help design the training corpus preparation pipeline.
"""

import json
from google.cloud import bigquery
from pathlib import Path
from datetime import datetime


PROJECT_ID = "flash-clover-464719-g1"
DATASET_ID = "spine"


def analyze_table_schema(client: bigquery.Client, table_name: str):
    """Get schema information for a table."""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name}")
    print(f"{'='*80}")
    
    try:
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = client.get_table(table_ref)
        
        print(f"\nSchema ({len(table.schema)} columns):")
        print("-" * 80)
        
        for field in table.schema:
            nullable = "NULLABLE" if field.is_nullable else "REQUIRED"
            mode = field.mode if field.mode != "NULLABLE" else ""
            print(f"  {field.name:30s} {field.field_type:15s} {nullable:10s} {mode}")
        
        print(f"\nTable Stats:")
        print(f"  Total rows: {table.num_rows:,}")
        print(f"  Size: {table.num_bytes / (1024**3):.2f} GB")
        print(f"  Created: {table.created}")
        print(f"  Modified: {table.modified}")
        
        return table.schema
    
    except Exception as e:
        print(f"❌ Error accessing {table_name}: {e}")
        return None


def sample_data(client: bigquery.Client, table_name: str, limit: int = 5):
    """Get sample rows from a table."""
    print(f"\nSample Data ({limit} rows):")
    print("-" * 80)
    
    try:
        query = f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
        WHERE text IS NOT NULL
        LIMIT {limit}
        """
        
        results = client.query(query).result()
        
        rows = []
        for i, row in enumerate(results, 1):
            row_dict = dict(row)
            rows.append(row_dict)
            
            print(f"\nRow {i}:")
            # Print key fields
            for key in ['entity_id', 'level', 'entity_type', 'text', 'metadata']:
                if key in row_dict:
                    value = row_dict[key]
                    if key == 'text':
                        value = str(value)[:100] + "..." if value and len(str(value)) > 100 else value
                    if key == 'metadata':
                        # Parse JSON metadata if it's a string
                        if isinstance(value, str):
                            try:
                                value = json.loads(value)
                                value = json.dumps(value, indent=2)[:300] + "..."
                            except:
                                pass
                    print(f"  {key}: {value}")
        
        return rows
    
    except Exception as e:
        print(f"❌ Error sampling {table_name}: {e}")
        return []


def analyze_metadata_fields(client: bigquery.Client, table_name: str):
    """Analyze what fields exist in metadata JSON."""
    print(f"\nMetadata Field Analysis:")
    print("-" * 80)
    
    try:
        # Query to extract all unique metadata keys
        query = f"""
        WITH parsed_metadata AS (
            SELECT 
                entity_id,
                level,
                source_pipeline,
                JSON_EXTRACT_SCALAR(metadata, '$') as metadata_str
            FROM `{PROJECT_ID}.{DATASET_ID}.{table_name}`
            WHERE metadata IS NOT NULL
            LIMIT 1000
        )
        SELECT 
            level,
            source_pipeline,
            COUNT(*) as count,
            ANY_VALUE(metadata_str) as sample_metadata
        FROM parsed_metadata
        GROUP BY level, source_pipeline
        ORDER BY level, source_pipeline
        """
        
        results = client.query(query).result()
        
        metadata_fields = {}
        
        for row in results:
            key = f"L{row.level} - {row.source_pipeline}"
            
            # Parse sample metadata
            if row.sample_metadata:
                try:
                    sample = json.loads(row.sample_metadata)
                    fields = list(sample.keys())
                    metadata_fields[key] = {
                        "level": row.level,
                        "source": row.source_pipeline,
                        "count": row.count,
                        "fields": fields
                    }
                    
                    print(f"\n{key} ({row.count} rows):")
                    print(f"  Fields: {', '.join(fields)}")
                except:
                    pass
        
        return metadata_fields
    
    except Exception as e:
        print(f"❌ Error analyzing metadata: {e}")
        return {}


def check_enrichment_tables(client: bigquery.Client):
    """Check if enrichment/embedding tables exist."""
    print(f"\n{'='*80}")
    print(f"CHECKING FOR ENRICHMENT/EMBEDDING TABLES")
    print(f"{'='*80}")
    
    dataset_ref = client.dataset(DATASET_ID, project=PROJECT_ID)
    
    tables = list(client.list_tables(dataset_ref))
    table_names = [table.table_id for table in tables]
    
    print(f"\nAll tables in {DATASET_ID} dataset:")
    for name in sorted(table_names):
        print(f"  - {name}")
    
    # Check for specific enrichment tables
    enrichment_indicators = ['enrichment', 'embedding', 'emotion', 'sentiment', 'topic']
    
    print(f"\nTables with enrichment indicators:")
    found = False
    for name in table_names:
        if any(indicator in name.lower() for indicator in enrichment_indicators):
            print(f"  ✅ {name}")
            found = True
    
    if not found:
        print(f"  ❌ No enrichment/embedding tables found")
    
    return table_names


def generate_enrichment_gap_analysis(schemas, metadata_fields, table_list):
    """Generate analysis of what we have vs what Genesis needs."""
    
    # Genesis requirements
    genesis_required = {
        "emotion": "Primary emotion (28 categories from GoEmotions)",
        "thought_type": "Type of cognitive process",
        "cognitive_stage": "Stage in problem-solving",
        "pattern": "Framework pattern demonstrated"
    }
    
    print(f"\n{'='*80}")
    print(f"GAP ANALYSIS: Current State vs Genesis Requirements")
    print(f"{'='*80}")
    
    print(f"\n🎯 Genesis Training Requirements:")
    for field, desc in genesis_required.items():
        print(f"  - {field}: {desc}")
    
    print(f"\n📊 Current State:")
    print(f"  Tables available: {len(table_list)}")
    print(f"  Metadata fields analyzed: {len(metadata_fields)} level/source combinations")
    
    # Check what exists in metadata
    all_fields = set()
    for meta_info in metadata_fields.values():
        all_fields.update(meta_info.get("fields", []))
    
    print(f"\n📋 All unique metadata fields found:")
    for field in sorted(all_fields):
        print(f"  - {field}")
    
    # Gap analysis
    print(f"\n❌ GAPS - Missing Genesis Required Fields:")
    gaps = []
    for field in genesis_required.keys():
        if field not in all_fields:
            print(f"  - {field}: NOT FOUND (needs to be added)")
            gaps.append(field)
        else:
            print(f"  ✅ {field}: FOUND")
    
    # Related fields that might help
    print(f"\n🔍 Related fields that might be useful:")
    related_keywords = ['sentiment', 'emotion', 'topic', 'category', 'type', 'stage', 'pattern']
    for field in sorted(all_fields):
        if any(keyword in field.lower() for keyword in related_keywords):
            print(f"  - {field}")
    
    return {
        "genesis_required": genesis_required,
        "current_fields": list(all_fields),
        "gaps": gaps,
        "metadata_by_level": metadata_fields
    }


def main():
    """Main analysis function."""
    client = bigquery.Client(project=PROJECT_ID)
    
    print(f"{'='*80}")
    print(f"GENESIS TRAINING DATA ENRICHMENT ANALYSIS")
    print(f"{'='*80}")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET_ID}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # 1. Check what tables exist
    table_list = check_enrichment_tables(client)
    
    # 2. Analyze entities_unified
    schemas = {}
    metadata_fields = {}
    
    if "entity_unified" in table_list:
        schema = analyze_table_schema(client, "entity_unified")
        if schema:
            schemas["entity_unified"] = schema
        
        sample_data(client, "entity_unified", limit=3)
        metadata_fields = analyze_metadata_fields(client, "entity_unified")
    
    # 3. Analyze entities_enrichments (if it exists)
    if "entities_enrichments" in table_list:
        schema = analyze_table_schema(client, "entities_enrichments")
        if schema:
            schemas["entities_enrichments"] = schema
        sample_data(client, "entities_enrichments", limit=3)
    
    # 4. Analyze entities_embeddings (if it exists)
    if "entities_embeddings" in table_list:
        schema = analyze_table_schema(client, "entities_embeddings")
        if schema:
            schemas["entities_embeddings"] = schema
        sample_data(client, "entities_embeddings", limit=3)
    
    # 5. Gap analysis
    gap_analysis = generate_enrichment_gap_analysis(schemas, metadata_fields, table_list)
    
    # 6. Save report
    output_dir = Path("training/data_prep/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": PROJECT_ID,
        "dataset": DATASET_ID,
        "tables_analyzed": list(schemas.keys()),
        "metadata_fields": metadata_fields,
        "gap_analysis": gap_analysis
    }
    
    report_path = output_dir / "enrichment_analysis.json"
    with open(report_path, 'w') as f:
        json.dump(report, indent=2, fp=f)
    
    print(f"\n✅ Analysis complete! Report saved to: {report_path}")


if __name__ == "__main__":
    main()
