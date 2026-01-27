#!/usr/bin/env python3
"""Router: Retrieve Knowledge Atoms from Pipeline HOLD₂ and Move to Knowledge Atom System

HOLD₁ (Pipeline HOLD₂ files) → AGENT (Router) → HOLD₂ (Knowledge Atom System HOLD₂)

Pipeline systems produce knowledge atoms and place them in HOLD₂ of the pipeline holds.
They are stored there until they are retrieved by this router.

This router:
1. Reads knowledge atoms from all pipeline stage HOLD₂ files
2. Processes them through the canonical knowledge service
3. Moves them to the Knowledge Atom System HOLD₂ (canonical store)

🧠 STAGE FIVE GROUNDING
This script exists to retrieve knowledge atoms from pipeline HOLD₂ and move them
to the canonical knowledge atom system, ensuring proper deduplication and similarity normalization.

Structure: Discover pipeline HOLD₂ → Read atoms → Process through knowledge service → Write to canonical HOLD₂
Purpose: Bridge between pipeline-specific storage and canonical knowledge atom system
Boundaries: Only processes knowledge atoms from pipeline HOLD₂, doesn't modify pipeline data
Control: On-demand execution, processes all pending atoms from all stages

⚠️ WHAT THIS SCRIPT CANNOT SEE
- Pipeline execution state beyond HOLD₂ files
- Knowledge atom content beyond what's in HOLD₂
- External systems beyond knowledge service
- User intent beyond processing pending atoms

🔥 THE FURNACE PRINCIPLE
- Truth (input): Knowledge atoms in pipeline HOLD₂
- Heat (processing): Router processes through canonical knowledge service
- Meaning (output): Canonical knowledge atoms in Knowledge Atom System HOLD₂
- Care (delivery): Atoms available for RAG and knowledge graph

Usage:
    python router_knowledge_atoms.py [--stage N] [--all]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

# Add scripts directory to path for shared imports
scripts_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(scripts_dir))

from shared import get_pipeline_hold2_path, PIPELINE_NAME
from src.services.central_services.knowledge_service.knowledge_service import get_knowledge_service

try:
    from truth_forge.core import get_logger
except Exception:
    from src.services.central_services.core import get_logger

logger = get_logger(__name__)


def read_pipeline_hold2(stage: int) -> List[Dict[str, Any]]:
    """Read knowledge atoms from pipeline HOLD₂ for a specific stage.
    
    Args:
        stage: Stage number (0-16)
    
    Returns:
        List of knowledge atom records from pipeline HOLD₂
    """
    hold2_path = get_pipeline_hold2_path(stage, PIPELINE_NAME)
    
    if not hold2_path.exists():
        logger.debug(f"Pipeline HOLD₂ not found for stage {stage}: {hold2_path}")
        return []
    
    atoms = []
    try:
        with open(hold2_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    atom = json.loads(line)
                    # Only process atoms with status="pending" (not yet retrieved)
                    if atom.get("status") == "pending":
                        atoms.append(atom)
                except json.JSONDecodeError as e:
                    logger.warning(
                        f"Invalid JSON in pipeline HOLD₂ stage {stage} line {line_num}: {e}",
                        extra={"stage": stage, "line_num": line_num, "error": str(e)},
                    )
                    continue
    
    except Exception as e:
        logger.error(
            f"Failed to read pipeline HOLD₂ for stage {stage}: {e}",
            extra={"stage": stage, "hold2_path": str(hold2_path), "error": str(e)},
            exc_info=True,
        )
        raise
    
    return atoms


def mark_atom_retrieved(stage: int, atom_hash: str) -> None:
    """Mark an atom as retrieved in pipeline HOLD₂.
    
    Updates the atom's status from "pending" to "retrieved" in the pipeline HOLD₂ file.
    
    Args:
        stage: Stage number (0-16)
        atom_hash: Hash of the atom to mark as retrieved
    """
    hold2_path = get_pipeline_hold2_path(stage, PIPELINE_NAME)
    
    if not hold2_path.exists():
        return
    
    # Read all atoms, update status, write back
    atoms = []
    try:
        with open(hold2_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    atom = json.loads(line)
                    # Mark matching atom as retrieved
                    if atom.get("hash") == atom_hash:
                        atom["status"] = "retrieved"
                    atoms.append(atom)
                except json.JSONDecodeError:
                    continue
        
        # Write back updated atoms (atomic write to preserve data integrity)
        from src.services.central_services.core.safe_writes import safe_write_jsonl_atomic
        try:
            safe_write_jsonl_atomic(str(hold2_path), atoms, dedupe_key="content")
        except Exception as e:
            # If atomic write fails, log but don't fail the router
            logger.warning(
                f"Failed to update pipeline HOLD₂ status (non-critical): {e}",
                extra={"stage": stage, "atom_hash": atom_hash, "error": str(e)},
            )
    
    except Exception as e:
        logger.warning(
            f"Failed to mark atom as retrieved in pipeline HOLD₂: {e}",
            extra={"stage": stage, "atom_hash": atom_hash, "error": str(e)},
        )


def process_stage_atoms(stage: int) -> Dict[str, Any]:
    """Process knowledge atoms from a specific pipeline stage HOLD₂.
    
    Args:
        stage: Stage number (0-16)
    
    Returns:
        Dict with processing results: {"read": int, "processed": int, "errors": int}
    """
    logger.info(f"Processing knowledge atoms from stage {stage} pipeline HOLD₂")
    
    # Read atoms from pipeline HOLD₂
    atoms = read_pipeline_hold2(stage)
    
    if not atoms:
        logger.info(f"No pending atoms in stage {stage} pipeline HOLD₂")
        return {"read": 0, "processed": 0, "errors": 0}
    
    logger.info(f"Found {len(atoms)} pending atoms in stage {stage} pipeline HOLD₂")
    
    # Process each atom through canonical knowledge service
    knowledge_service = get_knowledge_service()
    processed = 0
    errors = 0
    
    for atom in atoms:
        try:
            # Extract atom data
            content = atom.get("content", "")
            source_name = atom.get("source_name", "claude_code_pipeline")
            source_id = atom.get("source_id")
            metadata = atom.get("metadata", {})
            atom_hash = atom.get("hash")
            
            if not content:
                logger.warning(f"Skipping atom with empty content in stage {stage}")
                errors += 1
                continue
            
            # Process through canonical knowledge service (writes to Knowledge Atom System HOLD₁, then router processes to HOLD₂)
            result = knowledge_service.exhale(
                content=content,
                source_name=source_name,
                source_id=source_id,
                metadata=metadata,
            )
            
            # Mark atom as retrieved in pipeline HOLD₂
            if atom_hash:
                mark_atom_retrieved(stage, atom_hash)
            
            processed += 1
            
            logger.debug(
                f"Processed atom from stage {stage}",
                extra={
                    "stage": stage,
                    "atom_hash": atom_hash,
                    "result": result,
                },
            )
        
        except Exception as e:
            logger.error(
                f"Failed to process atom from stage {stage}: {e}",
                extra={"stage": stage, "atom": atom, "error": str(e)},
                exc_info=True,
            )
            errors += 1
    
    logger.info(
        f"Stage {stage} processing complete",
        extra={
            "stage": stage,
            "read": len(atoms),
            "processed": processed,
            "errors": errors,
        },
    )
    
    return {"read": len(atoms), "processed": processed, "errors": errors}


def process_all_stages() -> Dict[str, Any]:
    """Process knowledge atoms from all pipeline stages.
    
    Returns:
        Dict with summary: {"total_read": int, "total_processed": int, "total_errors": int, "by_stage": Dict}
    """
    logger.info("Processing knowledge atoms from all pipeline stages")
    
    total_read = 0
    total_processed = 0
    total_errors = 0
    by_stage = {}
    
    for stage in range(17):  # Stages 0-16
        result = process_stage_atoms(stage)
        total_read += result["read"]
        total_processed += result["processed"]
        total_errors += result["errors"]
        by_stage[stage] = result
    
    logger.info(
        f"All stages processing complete",
        extra={
            "total_read": total_read,
            "total_processed": total_processed,
            "total_errors": total_errors,
            "by_stage": by_stage,
        },
    )
    
    return {
        "total_read": total_read,
        "total_processed": total_processed,
        "total_errors": total_errors,
        "by_stage": by_stage,
    }


def main() -> int:
    """Main entry point for router."""
    parser = argparse.ArgumentParser(
        description="Router: Retrieve knowledge atoms from pipeline HOLD₂ and move to knowledge atom system"
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=range(17),
        help="Process atoms from specific stage only (0-16)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process atoms from all stages (default)",
    )
    
    args = parser.parse_args()
    
    try:
        if args.stage is not None:
            # Process specific stage
            result = process_stage_atoms(args.stage)
            print(f"\n{'='*60}")
            print(f"ROUTER COMPLETE: Stage {args.stage}")
            print(f"{'='*60}")
            print(f"Atoms read: {result['read']}")
            print(f"Atoms processed: {result['processed']}")
            print(f"Errors: {result['errors']}")
            return 0 if result["errors"] == 0 else 1
        else:
            # Process all stages
            result = process_all_stages()
            print(f"\n{'='*60}")
            print(f"ROUTER COMPLETE: All Stages")
            print(f"{'='*60}")
            print(f"Total atoms read: {result['total_read']}")
            print(f"Total atoms processed: {result['total_processed']}")
            print(f"Total errors: {result['total_errors']}")
            print(f"\nBy Stage:")
            for stage, stage_result in result["by_stage"].items():
                if stage_result["read"] > 0:
                    print(f"  Stage {stage}: {stage_result['read']} read, {stage_result['processed']} processed, {stage_result['errors']} errors")
            return 0 if result["total_errors"] == 0 else 1
    
    except Exception as e:
        logger.error(
            f"Router failed: {e}",
            exc_info=True,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
