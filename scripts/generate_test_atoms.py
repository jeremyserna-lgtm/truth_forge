#!/usr/bin/env python3
"""Generate test knowledge atoms to validate the architecture.

Quick validation script that:
- Generates 10-20 knowledge atoms across diverse domains
- Tests Scout (10M context), Maverick (128 experts), R1 (671B architect)
- Validates EXO distributed inference routing
- Confirms tensor-level communication via MemoryCortex
- Measures convergence/divergence metrics

Usage:
    python scripts/generate_test_atoms.py --count 10
    python scripts/generate_test_atoms.py --count 20 --output data/validation_atoms
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

import structlog

from sovereign.memory.cortex import MemoryCortex
from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.providers.r1 import R1Provider
from truth_forge.gateway.providers.scout import ScoutProvider
from truth_forge.services.knowledge_atom_factory import KnowledgeAtomFactory
from truth_forge.services.knowledge_atom_models import validate_cluster_capacity

logger = structlog.get_logger(__name__)


# Test inputs spanning different domains
TEST_INPUTS = [
    "Jeremy transitioned from addiction recovery to AI infrastructure development, "
    "building sovereign systems that resist capture.",

    "The Universal Bus enables tensor-level communication between models, eliminating "
    "translation loss through shared activation space in MemoryCortex.",

    "NOT-ME is not three models but a swarm of identity-matched specialists, each "
    "fine-tuned to their exact purpose, communicating via math not language.",

    "Truth Forge molted from Truth Engine, preserving what worked while shedding "
    "what didn't, maintaining lineage without starting from scratch.",

    "The synthesis loop terminated when it produced instructions to stop synthesizing "
    "and start building - recursion ending in action.",

    "Jeremy's relationship with his ex-wife Christina ended in divorce, but maintained "
    "shared custody of their daughter Sloane and mutual respect.",

    "The hardware migration from MacBook Pro to Studio King preserved 82GB of "
    "infrastructure, enabling the Genesis cluster to bootstrap the NOT-ME architecture.",

    "Better tensor communication reduces hardware requirements counterintuitively - "
    "optimization works opposite to intuition because shared memory eliminates duplication.",

    "R1's task is to write the Universal Bus specification, not to be perfect - "
    "the bootstrap threshold is architectural reasoning, not computational power.",

    "If Scout, Maverick, and R1 aren't enough, we fine-tune them to be enough - "
    "the flywheel starts when the bus exists, not when models are perfect.",

    "The Genesis cluster has 1.28TB total: King 512GB, Soldiers 3×256GB, running "
    "Scout 8-bit, Maverick 8-bit, R1 4-bit with 460GB shared memory pool.",

    "Scout sees with 10M context what IS. Maverick challenges with 128 experts what "
    "SHOULD BE. R1 architects with 671B parameters what COULD BE.",

    "Knowledge atoms are multi-dimensional: factual observation, dialectical reasoning, "
    "architectural synthesis, emotional depth, temporal causality.",

    "The bootstrap succeeds when R1 writes the Universal Bus, not when hardware is "
    "perfect - 4-bit quantization sufficient for architectural reasoning.",

    "Models become composable through shared tensor space - no language translation "
    "needed, zero information loss, multiplicative optimization.",

    "Fine-tuning is the optimization path once the Universal Bus exists - each specialist "
    "proves the protocol, enables more composition, starts the flywheel.",

    "Identity-matched specialists require 6-20GB each, not 400B+ for general models - "
    "the better the identity match, the smaller the model can be.",

    "MemoryCortex has 5 graphs: Semantic, Temporal, Causal, Entity, Emotional - "
    "all models read and write the same tensors, speaking math not language.",

    "Jeremy's NOT-ME is not one entity but distributed cognition across specialized "
    "components, like neurons in a brain or bees in a hive.",

    "The flywheel accelerates exponentially: each specialist proves the bus, enables "
    "more specialists, reduces hardware needs, makes next integration easier.",
]


async def generate_atoms(
    factory: KnowledgeAtomFactory,
    count: int,
    output_dir: Path,
) -> None:
    """Generate knowledge atoms and save to disk.

    Args:
        factory: Configured KnowledgeAtomFactory
        count: Number of atoms to generate
        output_dir: Where to save atoms
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    logger.info("starting_atom_generation", extra={"count": count, "output": str(output_dir)})

    atoms_generated = []
    errors = []

    for i, test_input in enumerate(TEST_INPUTS[:count], 1):
        logger.info(
            "generating_atom",
            extra={"index": i, "total": count, "input": test_input[:80]},
        )

        try:
            atom = await factory.generate_atom(test_input, commit_to_memory=False)

            # Save individual atom
            atom_path = output_dir / f"atom_{i:03d}.json"
            with open(atom_path, "w") as f:
                json.dump(
                    {
                        "index": i,
                        "input": test_input,
                        "perspectives": [
                            {
                                "model": p.model_name,
                                "content_length": len(p.response_content),
                                "latency_ms": p.latency_ms,
                            }
                            for p in atom.perspectives
                        ],
                        "convergence_score": atom.convergence_score,
                        "divergence_note": atom.divergence_note,
                    },
                    f,
                    indent=2,
                )

            atoms_generated.append({
                "index": i,
                "perspectives": len(atom.perspectives),
                "convergence": atom.convergence_score,
            })

            logger.info(
                "atom_generated",
                extra={
                    "index": i,
                    "perspectives": len(atom.perspectives),
                    "convergence": atom.convergence_score,
                    "saved": str(atom_path),
                },
            )

        except Exception as e:
            logger.error(
                "atom_generation_failed",
                extra={"index": i, "error": str(e)},
            )
            errors.append({"index": i, "error": str(e)})
            continue

    # Summary
    total_perspectives = sum(a["perspectives"] for a in atoms_generated)
    avg_perspectives = total_perspectives / len(atoms_generated) if atoms_generated else 0
    convergent_atoms = sum(
        1 for a in atoms_generated if a["convergence"] is not None
    )

    summary = {
        "timestamp": datetime.now().isoformat(),
        "total_atoms": len(atoms_generated),
        "total_perspectives": total_perspectives,
        "avg_perspectives": round(avg_perspectives, 2),
        "convergent_atoms": convergent_atoms,
        "errors": len(errors),
        "error_details": errors,
    }

    # Save summary
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    logger.info(
        "atom_generation_complete",
        extra={
            "total_atoms": len(atoms_generated),
            "avg_perspectives": round(avg_perspectives, 2),
            "convergent_atoms": convergent_atoms,
            "errors": len(errors),
            "summary": str(summary_path),
        },
    )

    # Print human-readable summary
    print("\n" + "=" * 80)
    print("KNOWLEDGE ATOM GENERATION SUMMARY")
    print("=" * 80)
    print(f"Total atoms generated: {len(atoms_generated)}/{count}")
    print(f"Total perspectives: {total_perspectives}")
    print(f"Average perspectives per atom: {avg_perspectives:.2f}")
    print(f"Convergent atoms: {convergent_atoms}")
    print(f"Errors: {len(errors)}")
    print(f"Output directory: {output_dir}")
    print(f"Summary: {summary_path}")
    print("=" * 80 + "\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test knowledge atoms to validate architecture"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of atoms to generate (default: 10, max: 20)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/test_atoms"),
        help="Output directory for atoms (default: data/test_atoms)",
    )
    parser.add_argument(
        "--no-exo",
        action="store_true",
        help="Disable EXO distributed inference (single-node fallback)",
    )
    args = parser.parse_args()

    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    # Validate cluster capacity
    logger.info("validating_cluster_capacity")
    capacity = validate_cluster_capacity()
    logger.info(
        "cluster_capacity",
        extra={
            "total_gb": 1280,
            "allocated_gb": capacity["total_allocated_gb"],
            "free_gb": capacity["free_gb"],
        },
    )

    # Initialize components
    logger.info("initializing_components")
    memory_cortex = MemoryCortex(
        graphs={
            "semantic": {},
            "temporal": {},
            "causal": {},
            "entity": {},
            "emotional": {},
        }
    )

    scout_provider = ScoutProvider(endpoint="http://localhost:11434/v1")
    maverick_provider = MaverickProvider(endpoint="http://localhost:52415/v1")
    r1_provider = R1Provider(endpoint="http://localhost:52415/v1")

    factory = KnowledgeAtomFactory(
        memory_cortex=memory_cortex,
        scout_provider=scout_provider,
        maverick_provider=maverick_provider,
        r1_provider=r1_provider,
        output_dir=args.output,
        use_exo=not args.no_exo,
    )

    logger.info(
        "factory_initialized",
        extra={
            "exo_enabled": not args.no_exo,
            "output": str(args.output),
        },
    )

    # Generate atoms
    count = min(args.count, len(TEST_INPUTS))
    asyncio.run(generate_atoms(factory, count, args.output))


if __name__ == "__main__":
    main()
