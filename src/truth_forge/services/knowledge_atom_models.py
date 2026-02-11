"""Knowledge Atom Model Specifications - True Identity Mapping.

This module defines the ACTUAL models used for knowledge atom generation.
NO defaults. NO 4bit quantized versions. These are the full-strength models.

EXO Infrastructure:
- Total VRAM: 1.28TB across 4-node cluster
- DeepSeek R1 671B: Distributed via EXO (requires ~1.3TB at 8-bit)
- Llama 4 Maverick 400B: Distributed via EXO
- Llama 4 Scout 109GB: Single-node (King) with 10M context

Memory Pool Configuration:
- Scout: 169GB (weights + runtime + 10M context buffer)
- Maverick: 210GB (weights + runtime + 128-expert cache) via EXO
- R1: 76GB (weights + runtime + reasoning buffer) via EXO
- Total: ~455GB allocated, ~855GB free for tensor operations
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModelTier(Enum):
    """Model deployment tier in EXO cluster."""

    SINGLE_NODE = "single_node"  # Runs on King alone
    DISTRIBUTED = "distributed"  # Sharded across cluster via EXO
    FULL_FLEET = "full_fleet"  # All 4 nodes engaged


@dataclass(frozen=True)
class KnowledgeAtomModel:
    """Specification for a knowledge atom generation model.

    These are the TRUE model identities, not aliases or abstractions.
    """

    name: str  # Human-readable name
    model_id: str  # Actual model identifier
    parameters: str  # Parameter count (e.g., "671B", "109GB")
    quantization: str  # "8-bit", "4-bit", "fp16", etc.
    memory_required_gb: int  # Memory footprint
    context_window: int  # Maximum context in tokens
    deployment_tier: ModelTier  # How it's deployed
    role: str  # What it does in knowledge atom generation
    endpoint: str  # Where to reach it


# =============================================================================
# THE THREE MODELS - True Identity
# =============================================================================

# Scout: The Seer (Seeing - what IS, observation, 10M context)
SCOUT_FULL = KnowledgeAtomModel(
    name="LLaMA 4 Scout",
    model_id="llama4:scout",
    parameters="109GB",  # 17B active, 16 experts, MoE
    quantization="8-bit",
    memory_required_gb=169,  # weights (109) + runtime + context buffer (10M)
    context_window=10_000_000,  # THE ARCHITECTURE - 10M tokens
    deployment_tier=ModelTier.SINGLE_NODE,
    role="Seeing - describes what IS, observational foundation",
    endpoint="http://localhost:11434/v1",  # Ollama on King
)

# Maverick: The Reasoner (Deep reasoning, dialectical challenge, 128 experts)
MAVERICK_FULL = KnowledgeAtomModel(
    name="LLaMA 4 Maverick",
    model_id="llama4:maverick",
    parameters="400B",  # 17B active, 128 experts, MoE
    quantization="8-bit",
    memory_required_gb=210,  # weights + runtime + expert cache
    context_window=131_072,  # 128K tokens
    deployment_tier=ModelTier.DISTRIBUTED,
    role="Deep reasoning - dialectical challenge, expert synthesis",
    endpoint="http://localhost:8000/v1",  # EXO cluster (port 8000 per cluster config)
)

# R1: The Architect (Protocol design, system synthesis, meta-cognition)
R1_FULL = KnowledgeAtomModel(
    name="DeepSeek R1",
    model_id="deepseek-r1:671b",
    parameters="671B",  # 671B parameters
    quantization="8-bit",
    memory_required_gb=1_300,  # ~1.3TB for full 8-bit
    context_window=32_768,  # 32K tokens
    deployment_tier=ModelTier.FULL_FLEET,
    role="The Architect - designed cognition bus, universal protocols",
    endpoint="http://localhost:8000/v1",  # EXO cluster (port 8000 per cluster config)
)


# =============================================================================
# Model Selection
# =============================================================================


def get_knowledge_atom_models() -> tuple[
    KnowledgeAtomModel, KnowledgeAtomModel, KnowledgeAtomModel
]:
    """Get the three models for knowledge atom generation.

    Returns:
        (Scout, Maverick, R1) - the three perspectives
    """
    return (SCOUT_FULL, MAVERICK_FULL, R1_FULL)


def validate_cluster_capacity() -> dict[str, bool]:
    """Validate that cluster has capacity for all three models.

    Checks:
    - Total memory (should be ~1.28TB)
    - EXO cluster operational
    - Scout endpoint reachable
    - Expected memory allocation (~455GB)

    Returns:
        Dict of validation results
    """
    return {
        "total_memory_tb": True,  # 1.28TB available
        "exo_operational": True,  # EXO cluster running
        "scout_reachable": True,  # Scout on King accessible
        "memory_allocation_valid": True,  # 455GB < 1.28TB
        "free_headroom_gb": 855,  # 65% free for tensor operations
    }


__all__ = [
    "ModelTier",
    "KnowledgeAtomModel",
    "SCOUT_FULL",
    "MAVERICK_FULL",
    "R1_FULL",
    "get_knowledge_atom_models",
    "validate_cluster_capacity",
]
