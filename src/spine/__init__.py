"""
The Spine — Data Infrastructure
Truth Forge

The Spine is the central data backbone containing:
- entity_unified: 11.8M+ entities from human-AI conversations
- entity_relationships: Graph edges connecting entities
- enrichments: Sentiment, topics, emotions
- embeddings: Gemini 3072, Scout 1024 vectors
"""

from .graph import (
    Entity,
    GraphRAGRetriever,
    GraphTraverser,
    Relationship,
    RelationshipExtractor,
    RelationshipType,
)


__version__ = "1.0.0"
__all__ = [
    "GraphRAGRetriever",
    "GraphTraverser",
    "RelationshipExtractor",
    "Relationship",
    "RelationshipType",
    "Entity",
]
