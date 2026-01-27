"""Knowledge Service - LLM-powered knowledge processing.

The knowledge service processes content through an LLM (Claude) to extract
structured knowledge, generate summaries, and create embeddings.

Structure: HOLD₁ (Raw Content) → AGENT (LLM Processing) → HOLD₂ (Processed Knowledge)

Usage:
    from truth_forge.services.factory import get_service

    knowledge = get_service("knowledge")
    knowledge.inhale({"content": "Raw text to process", "source": "web"})
    knowledge.sync()  # Process through LLM
"""

from truth_forge.services.knowledge.service import KnowledgeService


__all__ = ["KnowledgeService"]
