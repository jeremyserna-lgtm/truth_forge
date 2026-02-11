"""
ANIMA: Autonomous Native Integrated Memory Architecture

Memory exists across five orthogonal dimensions:
1. Semantic - What does this mean?
2. Temporal - When did this happen?
3. Causal - Why did this happen?
4. Entity - Who/what is this?
5. Emotional - How did this feel?

Every memory exists SIMULTANEOUSLY in all five dimensions.
"""

from sovereign.memory.cortex import EnrichedInput, MemoryCortex
from sovereign.memory.graphs.causal import CausalEdge, CausalGraph, CausalNode, CausalRelation
from sovereign.memory.graphs.emotional import EmotionalGraph, EmotionalNode, EmotionalTone
from sovereign.memory.graphs.entity import EntityGraph, EntityNode, EntityRelation
from sovereign.memory.graphs.semantic import SemanticGraph, SemanticNode
from sovereign.memory.graphs.temporal import TemporalGraph, TemporalNode


__all__ = [
    # Core
    "MemoryCortex",
    "EnrichedInput",
    # Semantic
    "SemanticGraph",
    "SemanticNode",
    # Temporal
    "TemporalGraph",
    "TemporalNode",
    # Causal
    "CausalGraph",
    "CausalNode",
    "CausalEdge",
    "CausalRelation",
    # Entity
    "EntityGraph",
    "EntityNode",
    "EntityRelation",
    # Emotional
    "EmotionalGraph",
    "EmotionalNode",
    "EmotionalTone",
]
