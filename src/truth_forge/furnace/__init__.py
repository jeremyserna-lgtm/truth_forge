"""The Furnace - Truth to Meaning to Care.

The Furnace is the core metabolic pattern of truth_forge:

    Raw Truth -> Extract Truths -> Retrieve Corpus -> Forge Together -> Enriched Narrative

This is not transformation. This is forging.

PHILOSOPHY:
- TRUTH: What is true here? (ME, CLAUDE, WORLD perspectives)
- MEANING: Which truths matter?
- CARE: Careful, Honest, Thorough

THE PATTERN:
    HOLD:AGENT:HOLD applies here too:
    - HOLD_1 (input): Raw truth, narratives, experiences
    - AGENT (furnace): Extract, retrieve, synthesize, forge
    - HOLD_2 (output): Enriched narratives with provenance

MOLT LINEAGE:
- Source: Truth_Engine furnace_engine.py (archived)
- Version: 2.0.0
- Date: 2026-01-26
- Rationale: Decouple from BigQuery, make LLM-agnostic
"""

from __future__ import annotations

from truth_forge.furnace.engine import (
    ForgeResult,
    FurnaceConfig,
    FurnaceEngine,
    Truth,
)


__all__ = [
    "FurnaceEngine",
    "FurnaceConfig",
    "ForgeResult",
    "Truth",
]
