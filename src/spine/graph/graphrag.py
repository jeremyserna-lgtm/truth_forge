"""
GraphRAG — Knowledge Graph Enhanced Retrieval
The Spine / Truth Forge

Evolves The Spine from a data warehouse into an active reasoning graph.
Enables multi-hop reasoning, contradiction detection, and enhanced factual grounding.
"""

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RelationshipType(Enum):
    """Types of relationships between entities."""

    # Reference relationships
    REFERENCES = "references"  # Entity A mentions Entity B
    CITED_BY = "cited_by"  # Entity A is cited by Entity B
    SOURCE_OF = "source_of"  # Entity A is the source of claim in B

    # Semantic relationships
    CONTRADICTS = "contradicts"  # Entities make contradictory claims
    SUPPORTS = "supports"  # Entity A supports claim in Entity B
    EXTENDS = "extends"  # Entity A builds upon Entity B
    CLARIFIES = "clarifies"  # Entity A clarifies Entity B

    # Causal relationships
    CAUSES = "causes"  # Entity A causes/leads to Entity B
    CAUSED_BY = "caused_by"  # Entity A is caused by Entity B
    TEMPORALLY_FOLLOWS = "follows"  # Entity A occurs after Entity B

    # Hierarchical relationships
    PART_OF = "part_of"  # Entity A is part of Entity B
    CONTAINS = "contains"  # Entity A contains Entity B
    INSTANCE_OF = "instance_of"  # Entity A is an instance of type B

    # Agent relationships
    AUTHORED_BY = "authored_by"  # Entity A was authored by Agent B
    VERIFIED_BY = "verified_by"  # Entity A was verified by Agent B

    # Trust relationships
    CORROBORATES = "corroborates"  # Entity A corroborates Entity B
    CONFLICTS_WITH = "conflicts_with"  # Entity A conflicts with Entity B


@dataclass
class Relationship:
    """
    An edge in the knowledge graph connecting two entities.
    """

    id: str
    source_id: str  # entity_unified.canonical_id
    target_id: str  # entity_unified.canonical_id
    relationship_type: str  # RelationshipType value

    # Metadata
    confidence: float = 0.8  # How confident are we in this relationship
    weight: float = 1.0  # Strength of the relationship

    # Provenance
    extracted_by: str = ""  # What extracted this (model, rule, human)
    extracted_at: str = ""  # When
    source_context: str = ""  # Context from source entity
    target_context: str = ""  # Context from target entity

    # Verification
    verified: bool = False
    verified_by: str = ""
    verified_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Entity:
    """
    A node in the knowledge graph (simplified from entity_unified).
    """

    canonical_id: str
    content: str
    entity_type: str  # layer (L1-L8), source, etc.

    # Optional metadata
    source: str = ""
    timestamp: str = ""
    embedding: list[float] = field(default_factory=list)

    # Graph connectivity (populated by traversal)
    incoming_edges: list[str] = field(default_factory=list)
    outgoing_edges: list[str] = field(default_factory=list)


@dataclass
class TraversalPath:
    """
    A path through the knowledge graph.
    """

    entities: list[str]  # canonical_ids in order
    relationships: list[str]  # relationship_ids in order
    total_weight: float = 0.0
    total_confidence: float = 0.0

    def to_natural_language(
        self, entities_map: dict[str, Entity], rels_map: dict[str, Relationship]
    ) -> str:
        """Convert path to human-readable explanation."""
        parts = []
        for i, ent_id in enumerate(self.entities):
            entity = entities_map.get(ent_id)
            if entity:
                parts.append(f"[{entity.entity_type}] {entity.content[:100]}...")

            if i < len(self.relationships):
                rel = rels_map.get(self.relationships[i])
                if rel:
                    parts.append(f"  --{rel.relationship_type}-->")

        return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# RELATIONSHIP EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════════


class RelationshipExtractor:
    """
    Extracts relationships between entities in The Spine.

    Uses combination of:
    - Pattern matching (explicit references)
    - Semantic similarity (embeddings)
    - LLM extraction (complex relationships)
    """

    def __init__(self, llm_client: Any = None, similarity_threshold: float = 0.85):
        """
        Initialize extractor.

        Args:
            llm_client: LLM for complex extraction
            similarity_threshold: Threshold for semantic similarity
        """
        self.llm = llm_client
        self.similarity_threshold = similarity_threshold

    def _generate_relationship_id(self, source: str, target: str, rel_type: str) -> str:
        """Generate unique relationship ID."""
        content = f"{source}|{target}|{rel_type}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def extract_from_pair(self, source: Entity, target: Entity) -> list[Relationship]:
        """
        Extract relationships between two entities.

        Args:
            source: Source entity
            target: Target entity

        Returns:
            List of discovered relationships
        """
        relationships = []

        # 1. Check for explicit references
        ref_rels = self._extract_references(source, target)
        relationships.extend(ref_rels)

        # 2. Check for semantic relationships via embeddings
        if source.embedding and target.embedding:
            sem_rels = self._extract_semantic(source, target)
            relationships.extend(sem_rels)

        # 3. Use LLM for complex relationships
        if self.llm:
            llm_rels = await self._extract_with_llm(source, target)
            relationships.extend(llm_rels)

        return relationships

    def _extract_references(self, source: Entity, target: Entity) -> list[Relationship]:
        """Extract explicit reference patterns."""
        relationships = []

        # Check if target content appears in source
        import re

        # Direct mention
        if target.content[:50].lower() in source.content.lower():
            relationships.append(
                Relationship(
                    id=self._generate_relationship_id(
                        source.canonical_id, target.canonical_id, "references"
                    ),
                    source_id=source.canonical_id,
                    target_id=target.canonical_id,
                    relationship_type=RelationshipType.REFERENCES.value,
                    confidence=0.9,
                    extracted_by="pattern_matching",
                    extracted_at=datetime.utcnow().isoformat(),
                    source_context=source.content[:200],
                )
            )

        # Quote patterns
        quote_pattern = r'"([^"]+)"'
        quotes_in_source = re.findall(quote_pattern, source.content)
        for quote in quotes_in_source:
            if quote.lower() in target.content.lower():
                relationships.append(
                    Relationship(
                        id=self._generate_relationship_id(
                            source.canonical_id, target.canonical_id, "cited_by"
                        ),
                        source_id=source.canonical_id,
                        target_id=target.canonical_id,
                        relationship_type=RelationshipType.CITED_BY.value,
                        confidence=0.95,
                        extracted_by="pattern_matching",
                        extracted_at=datetime.utcnow().isoformat(),
                        source_context=f'Quoted: "{quote}"',
                    )
                )
                break

        return relationships

    def _extract_semantic(self, source: Entity, target: Entity) -> list[Relationship]:
        """Extract relationships via embedding similarity."""
        relationships = []

        if not source.embedding or not target.embedding:
            return relationships

        # Calculate cosine similarity
        similarity = self._cosine_similarity(source.embedding, target.embedding)

        if similarity >= self.similarity_threshold:
            # High similarity - likely related
            relationships.append(
                Relationship(
                    id=self._generate_relationship_id(
                        source.canonical_id, target.canonical_id, "supports"
                    ),
                    source_id=source.canonical_id,
                    target_id=target.canonical_id,
                    relationship_type=RelationshipType.SUPPORTS.value,
                    confidence=similarity,
                    weight=similarity,
                    extracted_by="semantic_similarity",
                    extracted_at=datetime.utcnow().isoformat(),
                )
            )
        elif similarity <= -0.7:  # Strong negative correlation
            # Low similarity might indicate contradiction
            relationships.append(
                Relationship(
                    id=self._generate_relationship_id(
                        source.canonical_id, target.canonical_id, "conflicts_with"
                    ),
                    source_id=source.canonical_id,
                    target_id=target.canonical_id,
                    relationship_type=RelationshipType.CONFLICTS_WITH.value,
                    confidence=abs(similarity),
                    weight=abs(similarity),
                    extracted_by="semantic_similarity",
                    extracted_at=datetime.utcnow().isoformat(),
                )
            )

        return relationships

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)

    async def _extract_with_llm(self, source: Entity, target: Entity) -> list[Relationship]:
        """Use LLM for complex relationship extraction."""

        prompt = f"""Analyze the relationship between these two pieces of content.

SOURCE CONTENT:
{source.content[:1000]}

TARGET CONTENT:
{target.content[:1000]}

Possible relationship types:
- contradicts: They make contradictory claims
- supports: Source supports claims in Target
- extends: Source builds upon Target
- clarifies: Source clarifies Target
- causes: Source causes/leads to Target
- part_of: Source is part of Target
- none: No significant relationship

Return ONLY valid JSON:
{{
  "relationship_type": "type or null",
  "confidence": 0.0 to 1.0,
  "explanation": "brief explanation"
}}
"""

        try:
            result = await self.llm.generate_content_async(prompt)
            data = json.loads(result.text)

            rel_type = data.get("relationship_type")
            if rel_type and rel_type != "none":
                return [
                    Relationship(
                        id=self._generate_relationship_id(
                            source.canonical_id, target.canonical_id, rel_type
                        ),
                        source_id=source.canonical_id,
                        target_id=target.canonical_id,
                        relationship_type=rel_type,
                        confidence=data.get("confidence", 0.7),
                        extracted_by="llm_extraction",
                        extracted_at=datetime.utcnow().isoformat(),
                        source_context=data.get("explanation", ""),
                    )
                ]
        except Exception:
            pass  # Fallback to other extraction methods

        return []


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH TRAVERSAL
# ═══════════════════════════════════════════════════════════════════════════════


class GraphTraverser:
    """
    Traverses The Spine knowledge graph for multi-hop reasoning.
    """

    def __init__(self, bq_client: Any = None):
        """
        Initialize traverser.

        Args:
            bq_client: BigQuery client for querying Spine
        """
        self.bq = bq_client

        # In-memory caches (for development)
        self._entities: dict[str, Entity] = {}
        self._relationships: dict[str, Relationship] = {}
        self._outgoing: dict[str, list[str]] = {}  # entity_id -> [relationship_ids]
        self._incoming: dict[str, list[str]] = {}  # entity_id -> [relationship_ids]

    def add_entity(self, entity: Entity):
        """Add entity to graph."""
        self._entities[entity.canonical_id] = entity
        if entity.canonical_id not in self._outgoing:
            self._outgoing[entity.canonical_id] = []
        if entity.canonical_id not in self._incoming:
            self._incoming[entity.canonical_id] = []

    def add_relationship(self, rel: Relationship):
        """Add relationship to graph."""
        self._relationships[rel.id] = rel

        if rel.source_id not in self._outgoing:
            self._outgoing[rel.source_id] = []
        self._outgoing[rel.source_id].append(rel.id)

        if rel.target_id not in self._incoming:
            self._incoming[rel.target_id] = []
        self._incoming[rel.target_id].append(rel.id)

    def get_neighbors(
        self, entity_id: str, direction: str = "both", relationship_types: list[str] = None
    ) -> list[tuple[Entity, Relationship]]:
        """
        Get neighboring entities.

        Args:
            entity_id: Starting entity
            direction: "outgoing", "incoming", or "both"
            relationship_types: Filter by relationship types

        Returns:
            List of (neighbor_entity, relationship) tuples
        """
        neighbors = []

        if direction in ("outgoing", "both"):
            for rel_id in self._outgoing.get(entity_id, []):
                rel = self._relationships.get(rel_id)
                if rel and (not relationship_types or rel.relationship_type in relationship_types):
                    neighbor = self._entities.get(rel.target_id)
                    if neighbor:
                        neighbors.append((neighbor, rel))

        if direction in ("incoming", "both"):
            for rel_id in self._incoming.get(entity_id, []):
                rel = self._relationships.get(rel_id)
                if rel and (not relationship_types or rel.relationship_type in relationship_types):
                    neighbor = self._entities.get(rel.source_id)
                    if neighbor:
                        neighbors.append((neighbor, rel))

        return neighbors

    def find_paths(
        self, start_id: str, end_id: str, max_hops: int = 3, relationship_types: list[str] = None
    ) -> list[TraversalPath]:
        """
        Find all paths between two entities.

        Args:
            start_id: Starting entity ID
            end_id: Ending entity ID
            max_hops: Maximum path length
            relationship_types: Filter by relationship types

        Returns:
            List of paths found
        """
        paths = []

        def dfs(
            current: str,
            target: str,
            path_entities: list[str],
            path_rels: list[str],
            visited: set[str],
            hops: int,
        ):
            if hops > max_hops:
                return

            if current == target and hops > 0:
                paths.append(TraversalPath(entities=path_entities[:], relationships=path_rels[:]))
                return

            if current in visited:
                return

            visited.add(current)

            for neighbor, rel in self.get_neighbors(current, "outgoing", relationship_types):
                path_entities.append(neighbor.canonical_id)
                path_rels.append(rel.id)

                dfs(neighbor.canonical_id, target, path_entities, path_rels, visited, hops + 1)

                path_entities.pop()
                path_rels.pop()

            visited.remove(current)

        dfs(start_id, end_id, [start_id], [], set(), 0)
        return paths

    def find_contradictions(
        self, entity_id: str, max_hops: int = 2
    ) -> list[tuple[Entity, Relationship]]:
        """
        Find entities that contradict the given entity.

        Uses explicit CONTRADICTS relationships and CONFLICTS_WITH.
        """
        contradicting = []
        contradiction_types = [
            RelationshipType.CONTRADICTS.value,
            RelationshipType.CONFLICTS_WITH.value,
        ]

        # Direct contradictions
        for neighbor, rel in self.get_neighbors(entity_id, "both", contradiction_types):
            contradicting.append((neighbor, rel))

        # Multi-hop (entity A supports B, B contradicts C, therefore A indirectly contradicts C)
        # TODO: Implement transitive contradiction detection

        return contradicting

    def find_supporting_evidence(
        self, entity_id: str, max_hops: int = 2
    ) -> list[tuple[Entity, Relationship, int]]:
        """
        Find entities that support the given entity.

        Returns: List of (entity, relationship, hop_distance) tuples
        """
        supporting = []
        support_types = [
            RelationshipType.SUPPORTS.value,
            RelationshipType.CORROBORATES.value,
            RelationshipType.SOURCE_OF.value,
        ]

        visited = {entity_id}
        queue = [(entity_id, 0)]

        while queue:
            current, distance = queue.pop(0)

            if distance >= max_hops:
                continue

            for neighbor, rel in self.get_neighbors(current, "both", support_types):
                if neighbor.canonical_id not in visited:
                    visited.add(neighbor.canonical_id)
                    supporting.append((neighbor, rel, distance + 1))
                    queue.append((neighbor.canonical_id, distance + 1))

        return supporting


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPHRAG RETRIEVER
# ═══════════════════════════════════════════════════════════════════════════════


class GraphRAGRetriever:
    """
    Graph-enhanced RAG retriever.

    Combines:
    - Traditional semantic search (embeddings)
    - Graph traversal (relationships)
    - Contradiction detection
    """

    def __init__(
        self,
        traverser: GraphTraverser,
        extractor: RelationshipExtractor = None,
        llm_client: Any = None,
    ):
        """
        Initialize retriever.

        Args:
            traverser: Graph traversal engine
            extractor: Relationship extractor
            llm_client: LLM for query processing
        """
        self.traverser = traverser
        self.extractor = extractor
        self.llm = llm_client

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        include_graph_context: bool = True,
        check_contradictions: bool = True,
    ) -> dict[str, Any]:
        """
        Retrieve relevant context for a query using GraphRAG.

        Args:
            query: User query
            top_k: Number of results to return
            include_graph_context: Whether to traverse graph for context
            check_contradictions: Whether to check for contradictions

        Returns:
            Dict with entities, relationships, contradictions, and reasoning
        """
        # Step 1: Traditional semantic search (placeholder)
        # In production, this would use The Spine embedding search
        seed_entities = await self._semantic_search(query, top_k)

        # Step 2: Graph expansion
        expanded_entities = []
        all_relationships = []

        if include_graph_context:
            for entity in seed_entities:
                # Get 1-hop neighbors
                neighbors = self.traverser.get_neighbors(entity.canonical_id)
                expanded_entities.extend([n for n, _ in neighbors])
                all_relationships.extend([r for _, r in neighbors])

        # Step 3: Contradiction detection
        contradictions = []
        if check_contradictions:
            for entity in seed_entities:
                contras = self.traverser.find_contradictions(entity.canonical_id)
                contradictions.extend(contras)

        # Step 4: Build reasoning context
        reasoning_context = self._build_reasoning_context(
            query, seed_entities, expanded_entities, all_relationships, contradictions
        )

        return {
            "seed_entities": [
                e.to_dict() if hasattr(e, "to_dict") else asdict(e) for e in seed_entities
            ],
            "expanded_entities": [
                e.to_dict() if hasattr(e, "to_dict") else asdict(e) for e in expanded_entities[:20]
            ],
            "relationships": [r.to_dict() for r in all_relationships[:30]],
            "contradictions_found": len(contradictions) > 0,
            "contradictions": [
                {"entity": asdict(e), "relationship": r.to_dict()} for e, r in contradictions[:5]
            ],
            "reasoning_context": reasoning_context,
            "query": query,
        }

    async def _semantic_search(self, query: str, top_k: int) -> list[Entity]:
        """
        Perform semantic search over The Spine.

        In production, this queries BigQuery with embedding similarity.
        """
        # Placeholder - return entities from traverser cache
        return list(self.traverser._entities.values())[:top_k]

    def _build_reasoning_context(
        self,
        query: str,
        seed_entities: list[Entity],
        expanded_entities: list[Entity],
        relationships: list[Relationship],
        contradictions: list[tuple[Entity, Relationship]],
    ) -> str:
        """Build natural language reasoning context for LLM."""

        lines = ["GRAPH REASONING CONTEXT:"]
        lines.append("=" * 50)
        lines.append(f"Query: {query}")
        lines.append("")

        lines.append("DIRECTLY RELEVANT ENTITIES:")
        for i, entity in enumerate(seed_entities[:5], 1):
            lines.append(f"  {i}. [{entity.entity_type}] {entity.content[:150]}...")

        lines.append("")
        lines.append("CONNECTED CONTEXT:")
        for rel in relationships[:10]:
            lines.append(
                f"  • {rel.source_id[:8]} --[{rel.relationship_type}]--> {rel.target_id[:8]}"
            )

        if contradictions:
            lines.append("")
            lines.append("⚠️ CONTRADICTIONS DETECTED:")
            for entity, rel in contradictions[:3]:
                lines.append(f"  • {entity.content[:100]}...")
                lines.append(f"    Relationship: {rel.relationship_type}")

        lines.append("=" * 50)
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# BIGQUERY SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

RELATIONSHIPS_TABLE_SCHEMA = """
-- Schema for spine.entity_relationships table
-- Run this in BigQuery to create the table

CREATE TABLE IF NOT EXISTS `{project}.spine.entity_relationships` (
  -- Identity
  id STRING NOT NULL,
  source_id STRING NOT NULL,
  target_id STRING NOT NULL,
  relationship_type STRING NOT NULL,
  
  -- Strength
  confidence FLOAT64,
  weight FLOAT64,
  
  -- Provenance
  extracted_by STRING,
  extracted_at TIMESTAMP,
  source_context STRING,
  target_context STRING,
  
  -- Verification
  verified BOOL DEFAULT FALSE,
  verified_by STRING,
  verified_at TIMESTAMP
)
CLUSTER BY source_id, target_id;

-- Graph traversal query examples

-- 1. Find all relationships for an entity
-- SELECT * FROM `{project}.spine.entity_relationships`
-- WHERE source_id = @entity_id OR target_id = @entity_id;

-- 2. Find contradictions
-- SELECT * FROM `{project}.spine.entity_relationships`
-- WHERE relationship_type IN ('contradicts', 'conflicts_with')
-- AND (source_id = @entity_id OR target_id = @entity_id);

-- 3. Multi-hop traversal (2 hops)
-- WITH hop1 AS (
--   SELECT target_id, relationship_type FROM entity_relationships WHERE source_id = @start_id
-- ),
-- hop2 AS (
--   SELECT er.target_id, er.relationship_type, h1.target_id as intermediate
--   FROM entity_relationships er
--   JOIN hop1 h1 ON er.source_id = h1.target_id
-- )
-- SELECT * FROM hop2;
"""


def get_relationships_schema_sql(project_id: str) -> str:
    """Get the BigQuery schema SQL with project ID substituted."""
    return RELATIONSHIPS_TABLE_SCHEMA.format(project=project_id)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio

    async def demo():
        print("=== GraphRAG Demo ===\n")

        # Create sample entities
        entity1 = Entity(
            canonical_id="e1_paris_capital",
            content="Paris is the capital of France.",
            entity_type="statement",
        )

        entity2 = Entity(
            canonical_id="e2_france_country",
            content="France is a country in Western Europe.",
            entity_type="statement",
        )

        entity3 = Entity(
            canonical_id="e3_paris_population",
            content="Paris has a population of approximately 2.1 million.",
            entity_type="statement",
        )

        entity4 = Entity(
            canonical_id="e4_contradiction",
            content="Lyon is the capital of France.",
            entity_type="statement",
        )

        # Build graph
        traverser = GraphTraverser()
        for entity in [entity1, entity2, entity3, entity4]:
            traverser.add_entity(entity)

        # Add relationships
        traverser.add_relationship(
            Relationship(
                id="r1",
                source_id="e1_paris_capital",
                target_id="e2_france_country",
                relationship_type="references",
                confidence=0.9,
            )
        )

        traverser.add_relationship(
            Relationship(
                id="r2",
                source_id="e3_paris_population",
                target_id="e1_paris_capital",
                relationship_type="extends",
                confidence=0.85,
            )
        )

        traverser.add_relationship(
            Relationship(
                id="r3",
                source_id="e4_contradiction",
                target_id="e1_paris_capital",
                relationship_type="contradicts",
                confidence=0.95,
            )
        )

        print("1. Graph Statistics:")
        print(f"   Entities: {len(traverser._entities)}")
        print(f"   Relationships: {len(traverser._relationships)}")

        print("\n2. Neighbors of 'Paris is the capital':")
        neighbors = traverser.get_neighbors("e1_paris_capital")
        for neighbor, rel in neighbors:
            print(f"   --[{rel.relationship_type}]--> {neighbor.content[:50]}...")

        print("\n3. Contradictions for 'Paris is the capital':")
        contras = traverser.find_contradictions("e1_paris_capital")
        for entity, rel in contras:
            print(f"   ⚠️ {entity.content}")

        print("\n4. Supporting evidence for 'Paris is the capital':")
        support = traverser.find_supporting_evidence("e1_paris_capital")
        for entity, rel, hops in support:
            print(f"   [{hops} hop(s)] {entity.content[:50]}...")

        print("\n5. GraphRAG Retrieval:")
        retriever = GraphRAGRetriever(traverser)
        result = await retriever.retrieve("What is the capital of France?", top_k=5)
        print(f"   Seeds: {len(result['seed_entities'])}")
        print(f"   Expanded: {len(result['expanded_entities'])}")
        print(f"   Contradictions: {result['contradictions_found']}")
        print(f"\n{result['reasoning_context']}")

    asyncio.run(demo())
