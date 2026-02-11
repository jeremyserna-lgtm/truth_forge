#!/usr/bin/env python3
"""
BigQuery Setup Script
Truth Forge

Creates the necessary BigQuery tables for:
- spine.audit_log (Zero Trust logging)
- spine.entity_relationships (GraphRAG)
"""

from google.cloud import bigquery


# Auto-detect from gcloud credentials
PROJECT_ID = None  # Will be set from client
DATASET = "spine"


def create_audit_log_table(client: bigquery.Client):
    """Create the audit_log table."""

    schema = [
        bigquery.SchemaField("audit_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("decision_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("session_id", "STRING"),
        bigquery.SchemaField("user_id", "STRING"),
        bigquery.SchemaField("worker_id", "STRING"),
        bigquery.SchemaField("input_hash", "STRING"),
        bigquery.SchemaField("input_summary", "STRING"),
        bigquery.SchemaField("output_hash", "STRING"),
        bigquery.SchemaField("output_summary", "STRING"),
        bigquery.SchemaField("model_used", "STRING"),
        bigquery.SchemaField("model_version", "STRING"),
        bigquery.SchemaField("routing_reason", "STRING"),
        bigquery.SchemaField("verification_status", "STRING"),
        bigquery.SchemaField("verification_score", "FLOAT64"),
        bigquery.SchemaField("verifications", "JSON"),
        bigquery.SchemaField("constitutional_score", "FLOAT64"),
        bigquery.SchemaField("principles_checked", "STRING", mode="REPEATED"),
        bigquery.SchemaField("principles_violated", "STRING", mode="REPEATED"),
        bigquery.SchemaField("shaping_forces", "JSON"),
        bigquery.SchemaField("reasoning_trace", "STRING"),
        bigquery.SchemaField("fracture_triggered", "BOOL"),
        bigquery.SchemaField("fracture_reason", "STRING"),
        bigquery.SchemaField("cost_usd", "FLOAT64"),
        bigquery.SchemaField("payment_tx_hash", "STRING"),
        bigquery.SchemaField("duration_ms", "INT64"),
        bigquery.SchemaField("error", "STRING"),
        bigquery.SchemaField("tags", "STRING", mode="REPEATED"),
    ]

    table_id = f"{PROJECT_ID}.{DATASET}.audit_log"

    table = bigquery.Table(table_id, schema=schema)
    table.time_partitioning = bigquery.TimePartitioning(
        type_=bigquery.TimePartitioningType.DAY, field="timestamp"
    )
    table.clustering_fields = ["decision_type", "worker_id"]
    table.description = "Zero Trust audit log for all AI decisions"

    try:
        table = client.create_table(table)
        print(f"✓ Created table {table_id}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table {table_id} already exists")
            return True
        else:
            print(f"✗ Failed to create {table_id}: {e}")
            return False


def create_entity_relationships_table(client: bigquery.Client):
    """Create the entity_relationships table for GraphRAG."""

    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("source_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("target_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("relationship_type", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("confidence", "FLOAT64"),
        bigquery.SchemaField("weight", "FLOAT64"),
        bigquery.SchemaField("extracted_by", "STRING"),
        bigquery.SchemaField("extracted_at", "TIMESTAMP"),
        bigquery.SchemaField("source_context", "STRING"),
        bigquery.SchemaField("target_context", "STRING"),
        bigquery.SchemaField("verified", "BOOL"),
        bigquery.SchemaField("verified_by", "STRING"),
        bigquery.SchemaField("verified_at", "TIMESTAMP"),
    ]

    table_id = f"{PROJECT_ID}.{DATASET}.entity_relationships"

    table = bigquery.Table(table_id, schema=schema)
    table.clustering_fields = ["source_id", "target_id"]
    table.description = "Graph edges connecting entities in The Spine for GraphRAG"

    try:
        table = client.create_table(table)
        print(f"✓ Created table {table_id}")
        return True
    except Exception as e:
        if "Already Exists" in str(e):
            print(f"  Table {table_id} already exists")
            return True
        else:
            print(f"✗ Failed to create {table_id}: {e}")
            return False


def main():
    global PROJECT_ID

    # Initialize client (auto-detects project from credentials)
    client = bigquery.Client()
    PROJECT_ID = client.project

    print("═══════════════════════════════════════════════════════════")
    print("         TRUTH FORGE — BIGQUERY SETUP")
    print("═══════════════════════════════════════════════════════════")
    print(f"Project: {PROJECT_ID}")
    print(f"Dataset: {DATASET}")
    print()

    # First ensure dataset exists
    dataset_id = f"{PROJECT_ID}.{DATASET}"
    try:
        client.get_dataset(dataset_id)
        print(f"  Dataset {DATASET} exists")
    except Exception:
        print(f"  Creating dataset {DATASET}...")
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = "US"
        client.create_dataset(dataset)
        print(f"  ✓ Created dataset {DATASET}")

    # Create tables
    print()
    print("Creating tables...")
    create_audit_log_table(client)
    create_entity_relationships_table(client)

    # Verify
    print()
    print("Verifying tables exist...")
    tables = list(client.list_tables(f"{PROJECT_ID}.{DATASET}"))
    table_names = [t.table_id for t in tables]

    if "audit_log" in table_names:
        print("  ✓ spine.audit_log")
    else:
        print("  ✗ spine.audit_log NOT FOUND")

    if "entity_relationships" in table_names:
        print("  ✓ spine.entity_relationships")
    else:
        print("  ✗ spine.entity_relationships NOT FOUND")

    print()
    print("═══════════════════════════════════════════════════════════")
    print("         SETUP COMPLETE")
    print("═══════════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
