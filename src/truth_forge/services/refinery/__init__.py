"""LLM Refinery Service Package.

The LLM Refinery is the processing furnace that transforms raw conversation
data into the L2-L8 hierarchical entity structure using local LLMs.

This package provides:
- LLMRefineryService: Core service for conversation processing
- RefineryConfig: Configuration dataclass
- create_refinery_service: Factory function

BIOLOGICAL METAPHOR:
- Refinery = The Furnace's processing chamber
- LLM = The metabolic enzymes breaking down raw data
- Entities (L2-L8) = The nutrients extracted from metabolism
- Enrichments = The vitamins and minerals (metadata) captured

HOLD PATTERN:
- HOLD₁ (intake): Raw conversation JSON
- AGENT (LLM): Extracts hierarchical structure + enrichments
- HOLD₂ (processed): entity_unified + entity_enrichments

Usage:
    from truth_forge.services.factory import get_service

    refinery = get_service("refinery")
    entities, enrichments = refinery.process(conversation)
"""

from truth_forge.services.refinery.service import (
    LLMRefineryService,
    RefineryConfig,
    create_refinery_service,
)


__all__ = [
    "LLMRefineryService",
    "RefineryConfig",
    "create_refinery_service",
]
