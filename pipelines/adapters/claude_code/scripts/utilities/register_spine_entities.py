#!/usr/bin/env python3
"""
Register spine.entity_unified entity_ids with the canonical identity service.

Entity_unified IDs already use Primitive.identity format (conv:, msg:, turn:,
sent:, span:, word:). This script finds entity_ids that exist in entity_unified
but are NOT in identity.id_registry and MERGEs them into the registry so the
canonical identity service knows about them.

Uses Run Service to track the registration run (start/complete) and Relationship
Service to record parent_id → entity_id "contains" relationships for the spine
hierarchy.

Usage:
    python register_spine_entities.py [--dry-run] [--with-relationships] [--relationship-batch N]

Run from pipeline scripts dir or project root. Requires BigQuery access.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

_project_root = Path(__file__).resolve().parents[4]
_src = _project_root / "src"
_scripts = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root))
sys.path.insert(0, str(_scripts))
sys.path.insert(0, str(_src))

from google.cloud import bigquery

from truth_forge.core import set_run_id
from truth_forge.identity import generate_run_id
from truth_forge.central_services.run_service import RunService
from truth_forge.central_services.relationship_service import RelationshipService

PROJECT_ID = "flash-clover-464719-g1"
SPINE_DATASET = "spine"
ENTITY_UNIFIED = "entity_unified"
IDENTITY_DATASET = "identity"
ID_REGISTRY = "id_registry"

ENTITY_UNIFIED_TABLE = f"`{PROJECT_ID}.{SPINE_DATASET}.{ENTITY_UNIFIED}`"
REGISTRY_TABLE = f"`{PROJECT_ID}.{IDENTITY_DATASET}.{ID_REGISTRY}`"

LEVEL_TO_TYPE = {
    2: "word",
    3: "span",
    4: "sentence",
    5: "message",
    6: "turn",
    8: "conversation",
}


def _entity_type_from_id(eid: str | None) -> str:
    """Infer entity type from truth_forge.identity-style entity_id prefix."""
    if not eid:
        return "entity"
    if eid.startswith("conv:"):
        return "conversation"
    if eid.startswith("turn:"):
        return "turn"
    if eid.startswith("msg:"):
        return "message"
    if eid.startswith("sent:"):
        return "sentence"
    if eid.startswith("span:"):
        return "span"
    if eid.startswith("word:"):
        return "word"
    return "entity"

def _merge_sql() -> str:
    """Build MERGE statement to register unregistered spine entity_ids."""
    return f"""
    MERGE {REGISTRY_TABLE} AS target
    USING (
        SELECT
            e.entity_id,
            CASE e.level
                WHEN 2 THEN 'word'
                WHEN 3 THEN 'span'
                WHEN 4 THEN 'sentence'
                WHEN 5 THEN 'message'
                WHEN 6 THEN 'turn'
                WHEN 8 THEN 'conversation'
                ELSE 'entity'
            END AS entity_type,
            TO_JSON(STRUCT(
                CAST(e.level AS INT64) AS level,
                e.source_pipeline AS source_pipeline
            )) AS context_data,
            CURRENT_TIMESTAMP() AS first_generated_at
        FROM (
            SELECT entity_id, ANY_VALUE(level) AS level, ANY_VALUE(source_pipeline) AS source_pipeline
            FROM {ENTITY_UNIFIED_TABLE}
            GROUP BY entity_id
        ) e
        WHERE NOT EXISTS (
            SELECT 1 FROM {REGISTRY_TABLE} r WHERE r.entity_id = e.entity_id
        )
    ) AS source
    ON target.entity_id = source.entity_id
    WHEN NOT MATCHED THEN
        INSERT (
            entity_id,
            entity_type,
            generation_method,
            context_data,
            stable,
            first_generated_at,
            first_requestor,
            generation_count,
            status,
            created_at,
            updated_at,
            source_system,
            parent_entity_id
        )
        VALUES (
            source.entity_id,
            source.entity_type,
            'hash_based',
            source.context_data,
            TRUE,
            source.first_generated_at,
            'spine_registration_backfill',
            1,
            'active',
            CURRENT_TIMESTAMP(),
            CURRENT_TIMESTAMP(),
            CAST(NULL AS STRING),
            CAST(NULL AS STRING)
        )
    """


def _count_unregistered(client: bigquery.Client) -> int:
    q = f"""
    SELECT COUNT(*) AS n
    FROM (
        SELECT entity_id FROM {ENTITY_UNIFIED_TABLE} GROUP BY entity_id
    ) e
    WHERE NOT EXISTS (SELECT 1 FROM {REGISTRY_TABLE} r WHERE r.entity_id = e.entity_id)
    """
    row = next(iter(client.query(q).result()))
    return row.n


def _exhale_relationships(
    client: bigquery.Client,
    batch_size: int,
    limit: int | None = None,
) -> int:
    """Query entity_unified for parent_id → entity_id, exhale via RelationshipService. Returns count exhaled."""
    rel_svc = RelationshipService()
    limit_clause = f"LIMIT {limit}" if limit is not None else ""
    query = f"""
    SELECT DISTINCT entity_id, parent_id, level
    FROM {ENTITY_UNIFIED_TABLE}
    WHERE parent_id IS NOT NULL
    ORDER BY level, entity_id
    {limit_clause}
    """
    job = client.query(query)
    exhaled = 0
    for r in job.result():
        try:
            rel_svc.exhale(
                source_entity_id=r.parent_id,
                target_entity_id=r.entity_id,
                source_entity_type=_entity_type_from_id(r.parent_id),
                target_entity_type=LEVEL_TO_TYPE.get(r.level, _entity_type_from_id(r.entity_id)),
                relationship_type="contains",
                relationship_category="structural",
                direction="forward",
                source_id="spine_registration_backfill",
            )
            exhaled += 1
        except Exception as e:
            print(f"Warning: relationship exhale failed {r.entity_id} <- {r.parent_id}: {e}")
        if exhaled > 0 and exhaled % batch_size == 0:
            print(f"  Relationships exhaled: {exhaled:,} ...")
    return exhaled


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Register spine entity_unified entity_ids with identity.id_registry"
    )
    parser.add_argument("--dry-run", action="store_true", help="Count unregistered only, do not MERGE")
    parser.add_argument(
        "--with-relationships",
        action="store_true",
        help="Also exhale parent_id→entity_id 'contains' relationships via Relationship Service",
    )
    parser.add_argument(
        "--relationship-batch",
        type=int,
        default=5000,
        help="Batch size for relationship exhale progress (default: 5000)",
    )
    parser.add_argument(
        "--relationship-limit",
        type=int,
        default=None,
        help="Cap number of relationships to exhale (default: no limit). Use for testing.",
    )
    args = parser.parse_args()

    run_id = generate_run_id()
    set_run_id(run_id)
    run_svc = RunService()
    run_start = time.perf_counter()

    client = bigquery.Client(project=PROJECT_ID)
    unregistered = _count_unregistered(client)
    print(f"Unregistered entity_unified entity_ids: {unregistered:,}")

    if args.dry_run:
        print("Dry run: no MERGE executed.")
        try:
            run_svc.exhale(
                run_type="script",
                component="register_spine_entities",
                operation="register",
                status="completed",
                run_id=run_id,
                result_data={"unregistered_count": unregistered, "dry_run": True},
                metrics={"unregistered": unregistered},
                metadata={"dry_run": True, "with_relationships": args.with_relationships},
            )
        except Exception as run_err:
            print(f"Warning: Run Service exhale failed: {run_err}")
        return 0

    if unregistered == 0:
        print("Nothing to register.")

    try:
        metrics = {"registered": 0 if unregistered == 0 else unregistered, "merge_seconds": 0}
        result_data = {"registered": 0 if unregistered == 0 else unregistered, "unregistered_before": unregistered}

        if unregistered > 0:
            start = time.perf_counter()
            sql = _merge_sql()
            print("Running MERGE into identity.id_registry...")
            job = client.query(sql)
            job.result()
            elapsed = time.perf_counter() - start
            metrics["merge_seconds"] = round(elapsed, 2)
            print(f"MERGE complete ({elapsed:.1f}s).")

        if args.with_relationships:
            print("Exhaling parent→entity relationships via Relationship Service...")
            rel_start = time.perf_counter()
            rel_count = _exhale_relationships(
                client, args.relationship_batch, args.relationship_limit
            )
            rel_elapsed = time.perf_counter() - rel_start
            result_data["relationships_exhaled"] = rel_count
            result_data["relationship_seconds"] = round(rel_elapsed, 2)
            print(f"Relationships exhaled: {rel_count:,} ({rel_elapsed:.1f}s).")

        run_elapsed = time.perf_counter() - run_start
        metrics["total_seconds"] = round(run_elapsed, 2)
        try:
            run_svc.exhale(
                run_type="script",
                component="register_spine_entities",
                operation="register",
                status="completed",
                run_id=run_id,
                result_data=result_data,
                metrics=metrics,
                metadata={"with_relationships": args.with_relationships},
            )
        except Exception as run_err:
            print(f"Warning: Run Service exhale failed (registration succeeded): {run_err}")
        return 0
    except Exception as e:
        try:
            run_svc.exhale(
                run_type="script",
                component="register_spine_entities",
                operation="register",
                status="failed",
                run_id=run_id,
                error_message=str(e),
                result_data={"unregistered_before": unregistered},
                metrics={"registered": 0},
                metadata={"with_relationships": args.with_relationships},
            )
        except Exception as run_err:
            print(f"Warning: Run Service exhale (failed) failed: {run_err}")
        raise


if __name__ == "__main__":
    sys.exit(main())
