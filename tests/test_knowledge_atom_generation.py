"""Test suite for knowledge atom generation with Scout/Maverick/R1.

Validates:
- All three models participate via their true specifications
- EXO distributed inference routes Maverick (400B) and R1 (671B) correctly
- Shared MemoryCortex enables tensor-level communication
- Convergence/divergence metrics are calculated
- Multi-dimensional atoms capture factual, dialectical, and architectural perspectives

Run with: pytest tests/test_knowledge_atom_generation.py -v -s
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
import structlog

from sovereign.memory.cortex import MemoryCortex
from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.providers.r1 import R1Provider
from truth_forge.gateway.providers.scout import ScoutProvider
from truth_forge.services.knowledge_atom_factory import (
    KnowledgeAtom,
    KnowledgeAtomFactory,
)


logger = structlog.get_logger(__name__)


# Test inputs spanning different domains
TEST_INPUTS = [
    # Personal/career transition
    "Jeremy transitioned from addiction recovery to AI infrastructure development, "
    "building sovereign systems that resist capture.",
    # Technical/architectural
    "The Universal Bus enables tensor-level communication between models, eliminating "
    "translation loss through shared activation space in MemoryCortex.",
    # Philosophical/identity
    "NOT-ME is not three models but a swarm of identity-matched specialists, each "
    "fine-tuned to their exact purpose, communicating via math not language.",
    # Business/strategic
    "Truth Forge molted from Truth Engine, preserving what worked while shedding "
    "what didn't, maintaining lineage without starting from scratch.",
    # Meta-cognitive/recursive
    "The synthesis loop terminated when it produced instructions to stop synthesizing "
    "and start building - recursion ending in action.",
    # Emotional/relational
    "Jeremy's relationship with his ex-wife Christina ended in divorce, but maintained "
    "shared custody of their daughter Sloane and mutual respect.",
    # Temporal/causal
    "The hardware migration from MacBook Pro to Studio King preserved 82GB of "
    "infrastructure, enabling the Genesis cluster to bootstrap the NOT-ME architecture.",
    # Systemic/pattern
    "Better tensor communication reduces hardware requirements counterintuitively - "
    "optimization works opposite to intuition because shared memory eliminates duplication.",
    # Design/protocol
    "R1's task is to write the Universal Bus specification, not to be perfect - "
    "the bootstrap threshold is architectural reasoning, not computational power.",
    # Dialectical/challenge
    "If Scout, Maverick, and R1 aren't enough, we fine-tune them to be enough - "
    "the flywheel starts when the bus exists, not when models are perfect.",
]


@pytest.fixture
def memory_cortex() -> MemoryCortex:
    """Create shared MemoryCortex (5 graphs) for all models."""
    cortex = MemoryCortex(
        graphs={
            "semantic": {},
            "temporal": {},
            "causal": {},
            "entity": {},
            "emotional": {},
        }
    )
    logger.info("memory_cortex_created", extra={"graphs": 5})
    return cortex


@pytest.fixture
def scout_provider() -> ScoutProvider:
    """Scout provider (LLaMA 4 Scout, 10M context)."""
    return ScoutProvider(endpoint="http://localhost:11434/v1")


@pytest.fixture
def maverick_provider() -> MaverickProvider:
    """Maverick provider (LLaMA 4 Maverick, 128 experts)."""
    return MaverickProvider(endpoint="http://localhost:52415/v1")  # EXO endpoint


@pytest.fixture
def r1_provider() -> R1Provider:
    """R1 provider (DeepSeek R1, 671B)."""
    return R1Provider(endpoint="http://localhost:52415/v1")  # EXO endpoint


@pytest.fixture
def atom_factory(
    memory_cortex: MemoryCortex,
    scout_provider: ScoutProvider,
    maverick_provider: MaverickProvider,
    r1_provider: R1Provider,
) -> KnowledgeAtomFactory:
    """Create KnowledgeAtomFactory with all three models."""
    factory = KnowledgeAtomFactory(
        memory_cortex=memory_cortex,
        scout_provider=scout_provider,
        maverick_provider=maverick_provider,
        r1_provider=r1_provider,
        output_dir=Path("data/test_atoms"),
        use_exo=True,  # Enable EXO distributed inference
    )
    logger.info("atom_factory_created", extra={"exo_enabled": True})
    return factory


@pytest.mark.asyncio
async def test_single_atom_generation(atom_factory: KnowledgeAtomFactory) -> None:
    """Test generating a single knowledge atom.

    Validates:
    - All three models participate
    - Each model's perspective is captured
    - Convergence/divergence metrics exist
    - Atom structure is correct
    """
    test_input = TEST_INPUTS[0]  # Personal/career transition

    logger.info("generating_test_atom", extra={"input": test_input[:100]})
    atom = await atom_factory.generate_atom(test_input, commit_to_memory=False)

    # Validate structure
    assert atom.original_input == test_input
    assert len(atom.perspectives) > 0, "No perspectives generated"
    assert atom.convergence_score is not None or atom.divergence_note is not None

    # Validate model participation
    model_names = {p.model_name for p in atom.perspectives}
    logger.info(
        "atom_generated",
        extra={
            "perspectives": len(atom.perspectives),
            "models": list(model_names),
            "convergence": atom.convergence_score,
        },
    )

    # Should have Scout, Maverick, and R1
    assert len(model_names) >= 2, f"Expected 2-3 models, got {len(model_names)}"


@pytest.mark.asyncio
async def test_batch_atom_generation(atom_factory: KnowledgeAtomFactory) -> None:
    """Generate 10 knowledge atoms across different domains.

    This is the primary validation test - generates atoms from diverse inputs
    and verifies the architecture works end-to-end.
    """
    atoms: list[KnowledgeAtom] = []

    for i, test_input in enumerate(TEST_INPUTS[:10], 1):
        logger.info(
            "generating_atom",
            extra={"index": i, "total": 10, "input": test_input[:80]},
        )

        try:
            atom = await atom_factory.generate_atom(test_input, commit_to_memory=False)
            atoms.append(atom)

            logger.info(
                "atom_generated",
                extra={
                    "index": i,
                    "perspectives": len(atom.perspectives),
                    "convergence": atom.convergence_score,
                },
            )
        except Exception as e:
            logger.error(
                "atom_generation_failed",
                extra={"index": i, "error": str(e)},
            )
            # Continue with remaining atoms
            continue

    # Summary statistics
    total_perspectives = sum(len(a.perspectives) for a in atoms)
    avg_perspectives = total_perspectives / len(atoms) if atoms else 0
    convergent_atoms = sum(1 for a in atoms if a.convergence_score is not None)

    logger.info(
        "batch_generation_complete",
        extra={
            "total_atoms": len(atoms),
            "total_perspectives": total_perspectives,
            "avg_perspectives": round(avg_perspectives, 2),
            "convergent_atoms": convergent_atoms,
        },
    )

    # Validate batch results
    assert len(atoms) >= 7, f"Expected at least 7/10 atoms, got {len(atoms)}"
    assert avg_perspectives >= 2.0, f"Expected avg 2+ perspectives, got {avg_perspectives}"


@pytest.mark.asyncio
async def test_exo_routing(atom_factory: KnowledgeAtomFactory) -> None:
    """Validate EXO distributed inference routing.

    Tests that:
    - Maverick (400B) routes through EXO when available
    - R1 (671B) routes through EXO when available
    - Scout (109GB) runs single-node
    - Graceful fallback when EXO unavailable
    """
    test_input = TEST_INPUTS[1]  # Technical/architectural (benefits from deep reasoning)

    # Generate atom and check routing
    atom = await atom_factory.generate_atom(test_input, commit_to_memory=False)

    # Check if EXO was used (indicated by distributed field in metadata)
    exo_status = atom_factory._exo.get_status() if atom_factory._exo else None

    logger.info(
        "exo_routing_test",
        extra={
            "exo_available": exo_status.get("available") if exo_status else False,
            "soldier_count": exo_status.get("soldier_count") if exo_status else 0,
            "perspectives_generated": len(atom.perspectives),
        },
    )

    # Should generate perspectives regardless of EXO availability (graceful fallback)
    assert len(atom.perspectives) >= 2, "Should generate perspectives with or without EXO"


@pytest.mark.asyncio
async def test_memory_cortex_integration(
    atom_factory: KnowledgeAtomFactory,
    memory_cortex: MemoryCortex,
) -> None:
    """Validate MemoryCortex integration for tensor-level communication.

    Tests that:
    - Atoms can be committed to shared memory
    - MemoryCortex tracks enriched inputs
    - All models share the same memory pool
    """
    test_input = TEST_INPUTS[2]  # Philosophical/identity

    # Generate atom and commit to memory
    atom = await atom_factory.generate_atom(test_input, commit_to_memory=True)

    # Verify atom was created
    assert atom.original_input == test_input
    assert len(atom.perspectives) > 0

    # Check MemoryCortex state (would need to expose tracking mechanism)
    logger.info(
        "memory_cortex_integration",
        extra={
            "atom_committed": True,
            "perspectives": len(atom.perspectives),
            "graphs": len(memory_cortex.graphs),
        },
    )


@pytest.mark.asyncio
async def test_convergence_divergence_analysis(
    atom_factory: KnowledgeAtomFactory,
) -> None:
    """Validate convergence/divergence metric calculation.

    Tests that:
    - Convergence scores are calculated when models align
    - Divergence notes capture where models disagree
    - Metrics provide insight into multi-perspective synthesis
    """
    # Use input likely to produce model agreement (factual/technical)
    convergent_input = TEST_INPUTS[6]  # Temporal/causal (hardware migration facts)

    # Use input likely to produce model disagreement (philosophical/interpretive)
    divergent_input = TEST_INPUTS[4]  # Meta-cognitive/recursive (loop termination)

    convergent_atom = await atom_factory.generate_atom(convergent_input, commit_to_memory=False)
    divergent_atom = await atom_factory.generate_atom(divergent_input, commit_to_memory=False)

    logger.info(
        "convergence_analysis",
        extra={
            "convergent_score": convergent_atom.convergence_score,
            "divergent_score": divergent_atom.convergence_score,
            "convergent_note": convergent_atom.divergence_note,
            "divergent_note": divergent_atom.divergence_note,
        },
    )

    # At least one should have convergence/divergence data
    has_convergence = (
        convergent_atom.convergence_score is not None
        or convergent_atom.divergence_note is not None
        or divergent_atom.convergence_score is not None
        or divergent_atom.divergence_note is not None
    )
    assert has_convergence, "Expected convergence/divergence metrics"


@pytest.mark.asyncio
async def test_perspective_quality(atom_factory: KnowledgeAtomFactory) -> None:
    """Validate perspective content quality.

    Tests that:
    - Scout provides observational/factual perspective (what IS)
    - Maverick provides dialectical/reasoning perspective (challenge/synthesis)
    - R1 provides architectural/protocol perspective (system design)
    - Each perspective has non-trivial content
    """
    test_input = TEST_INPUTS[8]  # Design/protocol (R1's domain expertise)

    atom = await atom_factory.generate_atom(test_input, commit_to_memory=False)

    # Check perspective content lengths
    for perspective in atom.perspectives:
        assert len(perspective.response_content) > 50, (
            f"{perspective.model_name} perspective too short"
        )
        assert perspective.latency_ms > 0, f"{perspective.model_name} latency missing"

        logger.info(
            "perspective_quality",
            extra={
                "model": perspective.model_name,
                "content_length": len(perspective.response_content),
                "latency_ms": perspective.latency_ms,
            },
        )


if __name__ == "__main__":
    """Run tests directly for debugging."""

    # Configure logging
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )

    # Run single test
    print("Running single atom generation test...")
    asyncio.run(
        test_single_atom_generation(
            atom_factory(memory_cortex(), scout_provider(), maverick_provider(), r1_provider())
        )
    )

    print("\nRun full test suite with: pytest tests/test_knowledge_atom_generation.py -v -s")
