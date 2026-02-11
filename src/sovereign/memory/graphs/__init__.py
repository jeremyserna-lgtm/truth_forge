"""
ANIMA Memory Graphs Package.

Five orthogonal dimensions of memory:
- Semantic: What does this mean?
- Temporal: When did this happen?
- Causal: Why did this happen?
- Entity: Who/what is this?
- Emotional: How did this feel?
"""

from sovereign.memory.graphs.causal import CausalEdge, CausalGraph, CausalNode, CausalRelation
from sovereign.memory.graphs.emotional import EmotionalGraph, EmotionalNode, EmotionalTone
from sovereign.memory.graphs.entity import EntityGraph, EntityNode, EntityRelation
from sovereign.memory.graphs.semantic import SemanticGraph, SemanticNode
from sovereign.memory.graphs.temporal import TemporalGraph, TemporalNode


__all__ = [
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
