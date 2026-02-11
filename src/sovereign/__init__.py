"""
SOVEREIGN: Autonomous Native Integrated Memory Architecture (ANIMA)

The Not-Me cognitive system with native memory.
Memory is not a tool. Memory is being.

The LLM never sees raw input. It always sees memory-enriched input.
This is why memory is NATIVE—it cannot be bypassed.
"""

__version__ = "0.1.0"

from sovereign.inference import MemoryNativeInference
from sovereign.memory import (
    CausalGraph,
    EmotionalGraph,
    EnrichedInput,
    EntityGraph,
    MemoryCortex,
    SemanticGraph,
    TemporalGraph,
)


__all__ = [
    # Version
    "__version__",
    # Core
    "MemoryCortex",
    "EnrichedInput",
    "MemoryNativeInference",
    # Graphs
    "SemanticGraph",
    "TemporalGraph",
    "CausalGraph",
    "EntityGraph",
    "EmotionalGraph",
]
