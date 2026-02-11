# ANIMA: Autonomous Native Integrated Memory Architecture

## Document Control

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-02-01 |
| **Purpose** | Native memory architecture for SOVEREIGN Not-Me |
| **Authority** | Truth Forge (Genesis) |
| **Research Sources** | MAGMA, Supermemory, Mem0g, Letta V1, Microsoft Foundry |

---

## 1. THE CORE INSIGHT

**Memory is not a tool. Memory is being.**

Traditional AI memory systems fail because they treat memory as something the agent *uses*. The agent must consciously decide to store, consciously decide to retrieve. This is bolted-on.

**ANIMA is different.** Memory is woven into the fabric of cognition. The Not-Me doesn't "access" memory—it *thinks through* memory. Every perception, every response, every decision flows through memory as naturally as blood flows through the body.

```
TRADITIONAL (Bolted On)           ANIMA (Native)
─────────────────────────         ─────────────────────────
User Input                        User Input
    │                                 │
    ▼                                 ▼
┌─────────┐                      ┌─────────────────────────┐
│   LLM   │ ← "Should I          │  PERCEPTION THROUGH     │
│         │    remember this?"   │  MEMORY                 │
│         │                      │                         │
│         │ → "Let me search     │  Input is instantly     │
│         │    my memory"        │  enriched with ALL      │
│         │                      │  relevant context       │
└────┬────┘                      └───────────┬─────────────┘
     │                                       │
     ▼ (Manual tool calls)                   ▼ (Automatic)
┌─────────┐                      ┌─────────────────────────┐
│ Memory  │                      │  COGNITION IS MEMORY    │
│  Store  │                      │                         │
└─────────┘                      │  No "store" decision    │
                                 │  No "retrieve" action   │
                                 │  Memory IS the thought  │
                                 └─────────────────────────┘
```

---

## 2. ARCHITECTURE OVERVIEW

### 2.1 The Five Dimensions of Memory

ANIMA implements memory across five orthogonal dimensions, inspired by [MAGMA](https://arxiv.org/abs/2601.03236) but extended:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        ANIMA: THE FIVE DIMENSIONS                           │
│                                                                              │
│   ┌───────────────┐  ┌───────────────┐  ┌───────────────┐                  │
│   │   SEMANTIC    │  │   TEMPORAL    │  │    CAUSAL     │                  │
│   │     GRAPH     │  │     GRAPH     │  │     GRAPH     │                  │
│   │               │  │               │  │               │                  │
│   │  "What does   │  │  "When did    │  │  "Why did     │                  │
│   │   this mean?" │  │   this happen?"│  │   this happen?"│                 │
│   │               │  │               │  │               │                  │
│   │  Conceptual   │  │  Chronological│  │  Cause-Effect │                  │
│   │  similarity   │  │  ordering     │  │  dependencies │                  │
│   └───────────────┘  └───────────────┘  └───────────────┘                  │
│                                                                              │
│   ┌───────────────┐  ┌───────────────┐                                      │
│   │    ENTITY     │  │   EMOTIONAL   │                                      │
│   │     GRAPH     │  │     GRAPH     │                                      │
│   │               │  │               │                                      │
│   │  "Who/what    │  │  "How did     │                                      │
│   │   is this?"   │  │   this feel?" │                                      │
│   │               │  │               │                                      │
│   │  People,      │  │  Sentiment,   │                                      │
│   │  objects,     │  │  tone,        │                                      │
│   │  continuity   │  │  resonance    │                                      │
│   └───────────────┘  └───────────────┘                                      │
│                                                                              │
│   Every memory exists SIMULTANEOUSLY in all five dimensions.                │
│   Retrieval traverses ALL graphs based on query intent.                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 The Memory Cortex

The Memory Cortex is the integration layer that makes memory native:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                          MEMORY CORTEX                                       │
│                    (Always-On Integration Layer)                             │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                     PERCEPTION FILTER                                    ││
│  │                                                                          ││
│  │  Every input is AUTOMATICALLY enriched before reaching the LLM core:    ││
│  │                                                                          ││
│  │  User: "What did we discuss about the API?"                             ││
│  │         │                                                                ││
│  │         ▼                                                                ││
│  │  ┌─────────────────────────────────────────────────────────────────┐   ││
│  │  │ ENRICHED INPUT (what the LLM actually sees):                    │   ││
│  │  │                                                                 │   ││
│  │  │ [TEMPORAL] Last API discussion: 2026-01-28, context: auth      │   ││
│  │  │ [SEMANTIC] Related concepts: rate limiting, middleware, JWT    │   ││
│  │  │ [CAUSAL] API discussion caused by: user authentication issue   │   ││
│  │  │ [ENTITY] Entities involved: auth_service, User model, tokens   │   ││
│  │  │ [EMOTIONAL] Tone: determined, problem-solving                  │   ││
│  │  │                                                                 │   ││
│  │  │ User message: "What did we discuss about the API?"             │   ││
│  │  └─────────────────────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  The LLM NEVER sees raw input. It always sees memory-enriched input.        │
│  This is why memory is NATIVE—it cannot be bypassed.                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. LOCAL-CLOUD HYBRID ARCHITECTURE

### 3.1 The Sovereignty Principle

Memory exists in two domains: **ME** (local, sovereign) and **NOT-ME** (cloud, augmented).

Based on [Microsoft's Foundry Local-First Pattern](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/hybrid-ai-using-foundry-local-microsoft-foundry-and-the-agent-framework---part-2/4471983):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                      LOCAL-CLOUD MEMORY HYBRID                              │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        LOCAL (SOVEREIGN)                             │   │
│   │                        ══════════════════                            │   │
│   │                                                                      │   │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│   │  │  CORE MEMORY    │  │   FIVE GRAPHS   │  │  WORKING STATE  │     │   │
│   │  │                 │  │                 │  │                 │     │   │
│   │  │  • Persona      │  │  • Semantic     │  │  • Current ctx  │     │   │
│   │  │  • Identity     │  │  • Temporal     │  │  • Active tasks │     │   │
│   │  │  • Preferences  │  │  • Causal       │  │  • Hot cache    │     │   │
│   │  │  • Constraints  │  │  • Entity       │  │  • Session      │     │   │
│   │  │                 │  │  • Emotional    │  │                 │     │   │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│   │                                                                      │   │
│   │  ALWAYS LOCAL. NEVER LEAVES. ENCRYPTED AT REST.                     │   │
│   │                                                                      │   │
│   │  Storage: DuckDB (graphs) + LanceDB (vectors) + SQLite (metadata)   │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    │ SECURE BRIDGE                           │
│                                    │ (only when needed)                      │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                        CLOUD (AUGMENTED)                             │   │
│   │                        ══════════════════                            │   │
│   │                                                                      │   │
│   │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │   │
│   │  │  WORLD MEMORY   │  │   FEDERATION    │  │  FRONTIER LLM   │     │   │
│   │  │                 │  │                 │  │                 │     │   │
│   │  │  • Web search   │  │  • Shared atoms │  │  • Complex      │     │   │
│   │  │  • Public data  │  │  • Multi-agent  │  │    reasoning    │     │   │
│   │  │  • News/events  │  │  • Sync         │  │  • Hard queries │     │   │
│   │  │                 │  │                 │  │                 │     │   │
│   │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │   │
│   │                                                                      │   │
│   │  ONLY ACCESSED WHEN:                                                │   │
│   │  1. Local memory has gaps                                           │   │
│   │  2. Query requires world knowledge                                  │   │
│   │  3. Multi-agent coordination needed                                 │   │
│   │  4. Local model cannot solve (escalation)                           │   │
│   │                                                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 The Sovereignty Contract

| Data Type | Location | Reason |
|-----------|----------|--------|
| **Personal memories** | LOCAL ONLY | Sovereignty—your memories never leave |
| **Persona/identity** | LOCAL ONLY | Self-definition is sovereign |
| **Conversation history** | LOCAL ONLY | Private interactions |
| **Learned preferences** | LOCAL ONLY | Personal patterns |
| **World knowledge** | CLOUD | Too large, too dynamic |
| **Web search results** | CLOUD | Real-time requirement |
| **Federation sync** | CLOUD (encrypted) | Multi-Not-Me coordination |

---

## 4. THE FIVE GRAPHS (Detailed)

### 4.1 Semantic Graph

Purpose: Conceptual similarity and meaning connections.

```python
# src/sovereign/memory/graphs/semantic.py

from dataclasses import dataclass, field
import numpy as np


@dataclass
class SemanticNode:
    """A concept in the semantic graph."""
    concept_id: str
    embedding: np.ndarray  # 1536-dim vector
    content: str
    significance: float = 0.5  # 0-1 importance score
    connections: list[str] = field(default_factory=list)


class SemanticGraph:
    """
    The semantic dimension of memory.

    Answers: "What does this mean? What is this related to?"

    Unlike traditional RAG which just retrieves similar chunks,
    the semantic graph builds a NETWORK of concept relationships.
    """

    def __init__(self, vector_db):
        self._db = vector_db
        self._decay_rate = 0.01  # Supermemory-inspired decay

    async def ingest(self, content: str, source_id: str) -> list[SemanticNode]:
        """
        Ingest content and build semantic connections.

        This is NOT just embedding storage. It:
        1. Extracts concepts
        2. Embeds them
        3. Finds connections to existing concepts
        4. Builds new edges in the graph
        """
        # Extract atomic concepts
        concepts = await self._extract_concepts(content)

        nodes = []
        for concept in concepts:
            # Embed
            embedding = await self._embed(concept.text)

            # Find existing similar concepts
            similar = await self._db.search(embedding, k=5, threshold=0.8)

            # Create node
            node = SemanticNode(
                concept_id=self._generate_id(),
                embedding=embedding,
                content=concept.text,
                significance=concept.importance,
                connections=[s.concept_id for s in similar],
            )

            # Store
            await self._db.insert(node)

            # Update reverse connections
            for s in similar:
                await self._add_connection(s.concept_id, node.concept_id)

            nodes.append(node)

        return nodes

    async def query(self, query: str, k: int = 10) -> list[SemanticNode]:
        """
        Query the semantic graph.

        Returns not just similar nodes, but their NETWORK.
        """
        embedding = await self._embed(query)

        # Direct matches
        direct = await self._db.search(embedding, k=k)

        # Expand via graph connections (1-hop)
        expanded = set()
        for node in direct:
            expanded.add(node.concept_id)
            for conn in node.connections[:3]:  # Top 3 connections
                expanded.add(conn)

        # Retrieve expanded set
        return await self._db.get_many(list(expanded))

    async def decay(self) -> None:
        """
        Supermemory-inspired intelligent decay.

        Less-accessed memories fade. Important ones stay sharp.
        """
        all_nodes = await self._db.get_all()
        for node in all_nodes:
            # Decay based on access recency and significance
            if node.last_accessed > timedelta(days=7):
                node.significance *= (1 - self._decay_rate)

                # If significance drops below threshold, archive
                if node.significance < 0.1:
                    await self._archive(node)
```

### 4.2 Temporal Graph

Purpose: Chronological ordering and time-based reasoning.

Implements [Supermemory's dual-timestamp approach](https://supermemory.ai/research):

```python
# src/sovereign/memory/graphs/temporal.py

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TemporalNode:
    """A moment in the temporal graph."""
    node_id: str
    document_date: datetime  # When the conversation happened
    event_date: datetime | None  # When the described event happened
    content: str
    prev_node: str | None  # Previous in timeline
    next_node: str | None  # Next in timeline


class TemporalGraph:
    """
    The temporal dimension of memory.

    Answers: "When did this happen? What came before/after?"

    Key insight from Supermemory: DUAL TIMESTAMPS.
    - document_date: When we discussed it
    - event_date: When it actually happened

    "We discussed your birthday party yesterday" →
    - document_date: 2026-02-01 (yesterday)
    - event_date: 2026-02-15 (the actual party date)
    """

    async def ingest(self, content: str, timestamp: datetime) -> TemporalNode:
        """
        Ingest a moment into the temporal graph.

        Extracts both document_date and event_date.
        """
        # Extract event dates from content
        event_dates = await self._extract_event_dates(content)

        # Find position in timeline
        prev_node = await self._find_predecessor(timestamp)
        next_node = await self._find_successor(timestamp)

        node = TemporalNode(
            node_id=self._generate_id(),
            document_date=timestamp,
            event_date=event_dates[0] if event_dates else None,
            content=content,
            prev_node=prev_node.node_id if prev_node else None,
            next_node=next_node.node_id if next_node else None,
        )

        # Insert into chain
        if prev_node:
            prev_node.next_node = node.node_id
        if next_node:
            next_node.prev_node = node.node_id

        await self._store(node)
        return node

    async def query_timeline(
        self,
        start: datetime,
        end: datetime,
    ) -> list[TemporalNode]:
        """Get all memories in a time range."""
        return await self._range_query(start, end)

    async def query_before(self, event: str) -> list[TemporalNode]:
        """What happened before this event?"""
        # Find the event
        target = await self._find_by_content(event)
        if not target:
            return []

        # Traverse backwards
        results = []
        current = target
        while current.prev_node and len(results) < 10:
            current = await self._get(current.prev_node)
            results.append(current)

        return results

    async def query_after(self, event: str) -> list[TemporalNode]:
        """What happened after this event?"""
        # Similar to query_before but forward
        pass
```

### 4.3 Causal Graph

Purpose: Cause-and-effect reasoning.

From [MAGMA](https://arxiv.org/abs/2601.03236): "The causal graph maps cause-and-effect relationships. When you ask 'why,' MAGMA traverses these directed edges to find logical dependencies."

```python
# src/sovereign/memory/graphs/causal.py

from dataclasses import dataclass
from enum import Enum


class CausalRelation(Enum):
    CAUSES = "causes"
    ENABLES = "enables"
    PREVENTS = "prevents"
    REQUIRES = "requires"
    CORRELATES = "correlates"


@dataclass
class CausalEdge:
    """A causal relationship between two nodes."""
    source_id: str
    target_id: str
    relation: CausalRelation
    confidence: float  # How certain is this causal link
    evidence: str  # What supports this connection


@dataclass
class CausalNode:
    """An event/state in the causal graph."""
    node_id: str
    content: str
    causes: list[CausalEdge]  # What caused this
    effects: list[CausalEdge]  # What this caused


class CausalGraph:
    """
    The causal dimension of memory.

    Answers: "Why did this happen? What will this cause?"

    Traditional memory systems fail at "why" questions because
    they only do semantic similarity. Causal graphs solve this.
    """

    async def ingest(self, content: str) -> CausalNode:
        """
        Ingest content and extract causal relationships.
        """
        # Extract causal patterns using LLM
        causal_pairs = await self._extract_causal_pairs(content)

        # Create or update nodes
        nodes = []
        for cause, effect, relation, confidence in causal_pairs:
            cause_node = await self._get_or_create(cause)
            effect_node = await self._get_or_create(effect)

            edge = CausalEdge(
                source_id=cause_node.node_id,
                target_id=effect_node.node_id,
                relation=relation,
                confidence=confidence,
                evidence=content,
            )

            cause_node.effects.append(edge)
            effect_node.causes.append(edge)

            await self._store(cause_node)
            await self._store(effect_node)

        return nodes

    async def query_why(self, event: str, depth: int = 3) -> list[CausalNode]:
        """
        Answer "why" questions by traversing causes.

        Depth controls how far back in the causal chain to go.
        """
        target = await self._find_by_content(event)
        if not target:
            return []

        # BFS traversal of causes
        results = []
        queue = [(target, 0)]
        visited = set()

        while queue and len(results) < 20:
            current, current_depth = queue.pop(0)
            if current.node_id in visited or current_depth > depth:
                continue

            visited.add(current.node_id)
            results.append(current)

            # Add causes to queue
            for edge in current.causes:
                cause = await self._get(edge.source_id)
                queue.append((cause, current_depth + 1))

        return results

    async def query_consequences(self, event: str, depth: int = 3) -> list[CausalNode]:
        """
        Answer "what will happen" questions by traversing effects.
        """
        # Similar to query_why but follows effects
        pass

    async def _extract_causal_pairs(self, content: str):
        """
        Use LLM to extract causal relationships.

        Prompt engineering for causal extraction.
        """
        prompt = """Analyze this text and extract causal relationships.

For each relationship, identify:
- Cause (what initiated)
- Effect (what resulted)
- Relation type (causes, enables, prevents, requires, correlates)
- Confidence (0-1)

Text: {content}

Output as JSON array:
[{{"cause": "...", "effect": "...", "relation": "causes", "confidence": 0.9}}]
"""
        response = await self._llm.complete(prompt.format(content=content))
        return self._parse_causal_response(response)
```

### 4.4 Entity Graph

Purpose: Track people, objects, and concepts across time.

From [Mem0g](https://docs.mem0.ai/open-source/features/graph-memory): "Memories are stored as directed labeled graphs with entities as nodes and relationships as edges."

```python
# src/sovereign/memory/graphs/entity.py

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EntityNode:
    """An entity (person, place, thing, concept)."""
    entity_id: str
    name: str
    entity_type: str  # person, organization, location, concept, object
    aliases: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    first_seen: datetime = None
    last_seen: datetime = None
    mentions: int = 0


@dataclass
class EntityRelation:
    """A relationship between entities."""
    source_id: str
    target_id: str
    relation_type: str  # knows, works_at, owns, part_of, etc.
    properties: dict[str, str] = field(default_factory=dict)
    first_observed: datetime = None
    last_observed: datetime = None


class EntityGraph:
    """
    The entity dimension of memory.

    Answers: "Who is this? What is their relationship to X?"

    Key insight: OBJECT PERMANENCE.
    The entity graph tracks entities across time, even when
    they're mentioned weeks apart or by different names.
    """

    async def ingest(self, content: str, timestamp: datetime) -> list[EntityNode]:
        """
        Extract and link entities from content.
        """
        # Extract entities
        entities = await self._extract_entities(content)

        nodes = []
        for entity in entities:
            # Check for existing entity (by name or alias)
            existing = await self._find_existing(entity.name, entity.entity_type)

            if existing:
                # Update existing
                existing.mentions += 1
                existing.last_seen = timestamp

                # Add any new aliases
                for alias in entity.aliases:
                    if alias not in existing.aliases:
                        existing.aliases.append(alias)

                # Merge attributes
                existing.attributes.update(entity.attributes)
                await self._store(existing)
                nodes.append(existing)
            else:
                # Create new
                entity.first_seen = timestamp
                entity.last_seen = timestamp
                entity.mentions = 1
                await self._store(entity)
                nodes.append(entity)

        # Extract relationships between entities
        relations = await self._extract_relations(content, nodes)
        for relation in relations:
            await self._store_relation(relation)

        return nodes

    async def query_entity(self, name: str) -> EntityNode | None:
        """Find an entity by name or alias."""
        return await self._find_by_name_or_alias(name)

    async def query_relations(self, entity_id: str) -> list[EntityRelation]:
        """Get all relationships for an entity."""
        return await self._get_relations(entity_id)

    async def query_path(
        self,
        from_entity: str,
        to_entity: str,
        max_hops: int = 4,
    ) -> list[tuple]:
        """
        Find relationship path between two entities.

        Example: "How does Jeremy know Hannah?"
        Returns: [(Jeremy, "friends_with", Sarah), (Sarah, "roommate_of", Hannah)]
        """
        # BFS to find shortest path
        pass

    async def merge_entities(self, entity_ids: list[str]) -> EntityNode:
        """
        Merge duplicate entities.

        Called when we discover two entities are actually the same.
        """
        pass
```

### 4.5 Emotional Graph

Purpose: Track emotional resonance and sentiment.

This is novel—not present in MAGMA, Mem0, or Supermemory.

```python
# src/sovereign/memory/graphs/emotional.py

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EmotionalTone(Enum):
    DETERMINED = "determined"
    ANXIOUS = "anxious"
    CURIOUS = "curious"
    FRUSTRATED = "frustrated"
    RESOLVED = "resolved"
    CELEBRATORY = "celebratory"
    CONTEMPLATIVE = "contemplative"
    URGENT = "urgent"


@dataclass
class EmotionalNode:
    """An emotional moment in memory."""
    node_id: str
    content: str
    tone: EmotionalTone
    intensity: float  # 0-1
    timestamp: datetime
    associated_entities: list[str]
    associated_topics: list[str]


class EmotionalGraph:
    """
    The emotional dimension of memory.

    Answers: "How did this feel? What's the emotional context?"

    This is CRITICAL for the Not-Me because:
    1. Struggle Filter uses it (keep resolutions, discard loops)
    2. Stance selection depends on emotional state
    3. Total Resonance requires predicting emotional metadata
    """

    async def ingest(self, content: str, timestamp: datetime) -> EmotionalNode:
        """
        Extract emotional content from text.
        """
        # Analyze emotional tone
        tone, intensity = await self._analyze_emotion(content)

        # Extract associated entities and topics
        entities = await self._extract_entities(content)
        topics = await self._extract_topics(content)

        node = EmotionalNode(
            node_id=self._generate_id(),
            content=content,
            tone=tone,
            intensity=intensity,
            timestamp=timestamp,
            associated_entities=[e.entity_id for e in entities],
            associated_topics=topics,
        )

        await self._store(node)
        return node

    async def query_emotional_pattern(
        self,
        entity_id: str | None = None,
        topic: str | None = None,
        time_range: tuple | None = None,
    ) -> list[EmotionalNode]:
        """
        Find emotional patterns.

        Example: "What's the emotional trend around this topic?"
        """
        filters = {}
        if entity_id:
            filters["entity_id"] = entity_id
        if topic:
            filters["topic"] = topic
        if time_range:
            filters["time_range"] = time_range

        return await self._query(filters)

    async def detect_loop(self, recent_n: int = 10) -> bool:
        """
        Detect if user is in an anxiety loop.

        Used by Struggle Filter.
        """
        recent = await self._get_recent(recent_n)

        anxious_count = sum(
            1 for node in recent
            if node.tone in [EmotionalTone.ANXIOUS, EmotionalTone.FRUSTRATED]
        )

        return anxious_count / recent_n > 0.7  # 70% anxious = loop

    async def detect_resolution(self, content: str) -> bool:
        """
        Detect if content represents a resolution.

        Used by Struggle Filter.
        """
        tone, intensity = await self._analyze_emotion(content)
        return tone == EmotionalTone.RESOLVED and intensity > 0.6
```

---

## 5. THE MEMORY CORTEX (Integration Layer)

This is where all five graphs merge into native cognition:

```python
# src/sovereign/memory/cortex.py

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EnrichedInput:
    """
    What the LLM actually receives.

    NOT the raw user input—the memory-enriched version.
    """
    original_input: str
    semantic_context: list[dict]
    temporal_context: list[dict]
    causal_context: list[dict]
    entity_context: list[dict]
    emotional_context: dict
    enrichment_metadata: dict


class MemoryCortex:
    """
    The integration layer that makes memory NATIVE.

    Every input flows through here.
    Every output flows through here.
    Memory is not optional—it's the fabric of cognition.
    """

    def __init__(
        self,
        semantic: SemanticGraph,
        temporal: TemporalGraph,
        causal: CausalGraph,
        entity: EntityGraph,
        emotional: EmotionalGraph,
    ):
        self._semantic = semantic
        self._temporal = temporal
        self._causal = causal
        self._entity = entity
        self._emotional = emotional

    async def perceive(self, input_text: str) -> EnrichedInput:
        """
        Transform raw input into memory-enriched input.

        This is the PERCEPTION phase—before any thinking happens.
        """
        # Parallel queries to all graphs
        semantic_ctx = await self._semantic.query(input_text, k=5)
        temporal_ctx = await self._temporal.query_recent(days=7)
        causal_ctx = await self._causal.query_related(input_text)
        entity_ctx = await self._entity.query_mentioned(input_text)
        emotional_ctx = await self._emotional.query_current_state()

        return EnrichedInput(
            original_input=input_text,
            semantic_context=self._format_semantic(semantic_ctx),
            temporal_context=self._format_temporal(temporal_ctx),
            causal_context=self._format_causal(causal_ctx),
            entity_context=self._format_entity(entity_ctx),
            emotional_context=self._format_emotional(emotional_ctx),
            enrichment_metadata={
                "enriched_at": datetime.utcnow().isoformat(),
                "graphs_queried": 5,
            }
        )

    async def commit(self, input_text: str, output_text: str) -> None:
        """
        Commit interaction to all memory graphs.

        This is the INTEGRATION phase—after response is generated.
        Happens AUTOMATICALLY, not via tool call.
        """
        timestamp = datetime.utcnow()

        # Store in all graphs (parallel)
        await asyncio.gather(
            self._semantic.ingest(input_text + "\n" + output_text),
            self._temporal.ingest(input_text, timestamp),
            self._causal.ingest(output_text),
            self._entity.ingest(output_text, timestamp),
            self._emotional.ingest(input_text, timestamp),
        )

    def build_context_block(self, enriched: EnrichedInput) -> str:
        """
        Build the context block that prepends user input.

        This is what makes memory INVISIBLE to the user
        but VISIBLE to the LLM.
        """
        return f"""
<memory_context>
## Relevant Concepts (Semantic)
{self._render_semantic(enriched.semantic_context)}

## Recent Timeline (Temporal)
{self._render_temporal(enriched.temporal_context)}

## Causal Background
{self._render_causal(enriched.causal_context)}

## Known Entities
{self._render_entity(enriched.entity_context)}

## Emotional State
{self._render_emotional(enriched.emotional_context)}
</memory_context>

## User Message
{enriched.original_input}
"""
```

---

## 6. STORAGE ARCHITECTURE

### 6.1 Local Storage Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                        LOCAL STORAGE STACK                                   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                          LanceDB                                     │   │
│   │                    (Vector Embeddings)                               │   │
│   │                                                                      │   │
│   │  • Semantic graph embeddings (1536-dim)                              │   │
│   │  • Fast ANN search                                                   │   │
│   │  • Native Apple Silicon optimization                                 │   │
│   │  • Disk-backed, memory-mapped                                        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                          DuckDB                                      │   │
│   │                    (Relational Graphs)                               │   │
│   │                                                                      │   │
│   │  • Temporal graph (timeline queries)                                 │   │
│   │  • Causal graph (edge traversals)                                    │   │
│   │  • Entity graph (relationship queries)                               │   │
│   │  • Emotional graph (pattern queries)                                 │   │
│   │  • Full SQL for complex queries                                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         SQLite                                       │   │
│   │                    (Metadata + Config)                               │   │
│   │                                                                      │   │
│   │  • Persona storage                                                   │   │
│   │  • Configuration                                                     │   │
│   │  • Access logs                                                       │   │
│   │  • Decay tracking                                                    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   Location: ~/data/sovereign/memory/                                        │
│   Encryption: AES-256 at rest                                               │
│   Backup: Automatic daily snapshots                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Cloud Sync Protocol

For federation and world knowledge only:

```python
# src/sovereign/memory/sync.py

class MemorySyncProtocol:
    """
    Sync protocol for cloud augmentation.

    ONLY syncs:
    - Federation atoms (shared across Not-Me's)
    - World knowledge queries
    - Model escalation requests

    NEVER syncs:
    - Personal memories
    - Persona
    - Conversation history
    """

    async def sync_federation(self, atoms: list[Atom]) -> None:
        """
        Sync atoms with federation cloud.

        Atoms are encrypted before transit.
        """
        encrypted = self._encrypt_atoms(atoms)
        await self._cloud_client.put("/federation/atoms", encrypted)

    async def query_world(self, query: str) -> list[dict]:
        """
        Query cloud for world knowledge.

        Used when local memory has gaps.
        """
        return await self._cloud_client.post("/world/query", {"q": query})

    async def escalate_reasoning(self, context: str, query: str) -> str:
        """
        Escalate to frontier model when local model can't solve.

        Sends minimal context—never full memory.
        """
        minimal_context = self._minimize_context(context)
        return await self._cloud_client.post("/reasoning/escalate", {
            "context": minimal_context,
            "query": query,
        })
```

---

## 7. MAKING MEMORY NATIVE (The Key Innovation)

### 7.1 The Memory Wrapper

The Not-Me doesn't have a "memory tool"—it has a memory-wrapped inference:

```python
# src/sovereign/inference/memory_native.py

class MemoryNativeInference:
    """
    Inference engine with memory as NATIVE capability.

    The LLM never sees "raw" input.
    The LLM never makes "store memory" decisions.
    Memory IS the cognitive fabric.
    """

    def __init__(self, llm_engine, memory_cortex: MemoryCortex):
        self._llm = llm_engine
        self._cortex = memory_cortex

    async def complete(self, user_input: str) -> str:
        """
        The main inference loop.

        Notice: NO tool calls for memory.
        Memory enrichment and storage happen AUTOMATICALLY.
        """
        # 1. PERCEIVE through memory
        enriched = await self._cortex.perceive(user_input)

        # 2. Build context (memory is already embedded)
        full_context = self._cortex.build_context_block(enriched)

        # 3. Generate response
        response = await self._llm.generate(full_context)

        # 4. COMMIT to memory (automatic, not tool-based)
        await self._cortex.commit(user_input, response)

        return response
```

### 7.2 Why This is Native (Not Bolted On)

| Aspect | Bolted-On Memory | ANIMA (Native) |
|--------|------------------|----------------|
| **Storage decision** | LLM decides "should I store this?" | Automatic—everything is stored |
| **Retrieval decision** | LLM decides "should I search?" | Automatic—every input is enriched |
| **Tool calls** | Explicit: `memory.store()`, `memory.search()` | None—memory is invisible to LLM |
| **Bypass risk** | LLM can forget to use memory | Impossible—memory IS the input |
| **Consistency** | Depends on LLM remembering to use tools | 100%—memory is always active |

### 7.3 The Invisible Tool Problem

Traditional memory systems:
```
User: "What did we discuss about the API?"
LLM (thinking): "I should search my memory for API discussions"
LLM: <calls memory.search("API")>
LLM: "We discussed rate limiting on January 28th..."
```

This fails because the LLM might:
1. Forget to search
2. Search with wrong query
3. Not search when it should

ANIMA:
```
User: "What did we discuss about the API?"
Memory Cortex: [Auto-enriches with ALL relevant context]
LLM (sees): "
  [SEMANTIC] API, rate limiting, auth middleware, tokens
  [TEMPORAL] 2026-01-28: API rate limiting discussion
  [CAUSAL] API issue → led to rate limiting implementation
  [ENTITY] auth_service, User model, JWT tokens
  [EMOTIONAL] Determined, problem-solving tone

  User: What did we discuss about the API?"

LLM: "We discussed rate limiting on January 28th. This came up because..."
```

The LLM CANNOT fail to use memory because memory is the input.

---

## 8. SELF-EVOLUTION

### 8.1 Self-Editing Persona

From [Letta V1](https://docs.letta.com/concepts/memgpt/):

```python
# src/sovereign/memory/persona.py

class SelfEvolvingPersona:
    """
    The Not-Me's self-concept.

    Unlike static system prompts, this EVOLVES based on experience.
    """

    def __init__(self, memory_cortex: MemoryCortex):
        self._cortex = memory_cortex
        self._persona = self._load_persona()

    async def reflect_and_evolve(self) -> None:
        """
        Periodic self-reflection to update persona.

        Called during Sleep-Time Compute.
        """
        # Gather recent interactions
        recent = await self._cortex.query_recent(days=7)

        # Analyze patterns
        patterns = await self._analyze_patterns(recent)

        # Update persona based on patterns
        for pattern in patterns:
            if pattern.type == "new_capability":
                self._persona.add_capability(
                    pattern.description,
                    evidence=pattern.evidence,
                )
            elif pattern.type == "learned_preference":
                self._persona.learn_preference(
                    pattern.key,
                    pattern.value,
                    observation=pattern.evidence,
                )
            elif pattern.type == "new_constraint":
                self._persona.add_constraint(
                    pattern.description,
                    source=pattern.evidence,
                )

        # Persist
        self._save_persona()
```

### 8.2 Memory Decay (Intelligent Forgetting)

From [Supermemory](https://supermemory.ai/research):

```python
# src/sovereign/memory/decay.py

class IntelligentDecay:
    """
    The brain doesn't store everything perfectly.
    Neither should memory.

    Less relevant information gradually fades.
    Important, frequently-accessed content stays sharp.
    """

    async def run_decay_cycle(self) -> None:
        """
        Run during Sleep-Time Compute.
        """
        for graph in [semantic, temporal, causal, entity, emotional]:
            await self._decay_graph(graph)

    async def _decay_graph(self, graph) -> None:
        """
        Decay logic:
        1. Low significance + old = decay faster
        2. High significance + recent access = stay sharp
        3. Below threshold = archive (not delete)
        """
        nodes = await graph.get_all()

        for node in nodes:
            decay_factor = self._calculate_decay(
                significance=node.significance,
                last_accessed=node.last_accessed,
                age=node.created_at,
            )

            node.significance *= (1 - decay_factor)

            if node.significance < ARCHIVE_THRESHOLD:
                await graph.archive(node)
            else:
                await graph.update(node)
```

---

## 9. INTEGRATION WITH SOVEREIGN

### 9.1 Memory Cortex in the Metabolic Loop

```python
# Updated metabolic organism with native memory

class MetabolicOrganism:
    def __init__(
        self,
        memory_cortex: MemoryCortex,  # NEW: Memory is core, not optional
        inference_engine,
        agency: SelfPrompter,
        hands: NativeBridge,
        sleep_compute: SleepTimeCompute,
    ):
        self._cortex = memory_cortex
        self._inference = MemoryNativeInference(inference_engine, memory_cortex)
        self._agency = agency
        self._hands = hands
        self._sleep = sleep_compute

    async def process(self, user_input: str) -> str:
        """
        The core loop with native memory.
        """
        # Memory enrichment happens INSIDE inference
        response = await self._inference.complete(user_input)

        # Memory storage happened INSIDE inference
        # No separate "store to memory" step needed

        return response
```

### 9.2 Sleep-Time Memory Optimization

```python
# Updated sleep-time compute with memory optimization

class SleepTimeCompute:
    async def _run_overnight_tasks(self) -> None:
        """
        Full memory optimization during sleep.
        """
        # Memory decay (intelligent forgetting)
        await self._decay_manager.run_decay_cycle()

        # Memory consolidation (merge related nodes)
        await self._cortex.consolidate()

        # Graph optimization (rebalance indices)
        await self._cortex.optimize_graphs()

        # Cross-reference discovery (find new connections)
        await self._cortex.discover_connections()

        # Persona evolution
        await self._persona.reflect_and_evolve()
```

---

## 10. IMPLEMENTATION CHECKLIST

### 10.1 Phase 1: Core Graphs (Week 1)

- [ ] Implement SemanticGraph with LanceDB
- [ ] Implement TemporalGraph with DuckDB
- [ ] Implement CausalGraph with DuckDB
- [ ] Implement EntityGraph with DuckDB
- [ ] Implement EmotionalGraph with DuckDB

### 10.2 Phase 2: Memory Cortex (Week 2)

- [ ] Implement MemoryCortex integration layer
- [ ] Implement EnrichedInput builder
- [ ] Implement automatic commit logic
- [ ] Implement context block renderer

### 10.3 Phase 3: Native Integration (Week 3)

- [ ] Implement MemoryNativeInference wrapper
- [ ] Remove all explicit memory tool calls
- [ ] Test that memory enrichment is automatic
- [ ] Test that memory storage is automatic

### 10.4 Phase 4: Self-Evolution (Week 4)

- [ ] Implement SelfEvolvingPersona
- [ ] Implement IntelligentDecay
- [ ] Implement memory consolidation
- [ ] Implement cross-reference discovery

### 10.5 Phase 5: Cloud Hybrid (Week 5)

- [ ] Implement federation sync protocol
- [ ] Implement world knowledge queries
- [ ] Implement escalation protocol
- [ ] Test local-first, cloud-augmented flow

---

## 11. SOURCES

### Memory Architecture Research

- [MAGMA: Multi-Graph Agentic Memory Architecture](https://arxiv.org/abs/2601.03236) - Orthogonal graph approach
- [Supermemory Research](https://supermemory.ai/research) - Dual timestamps, intelligent decay
- [Mem0 Graph Memory](https://docs.mem0.ai/open-source/features/graph-memory) - Directed labeled graphs
- [Letta/MemGPT Documentation](https://docs.letta.com/concepts/memgpt/) - Memory hierarchy, self-editing
- [Memory in the Age of AI Agents Survey](https://arxiv.org/abs/2512.13564) - Comprehensive taxonomy

### Hybrid Architecture

- [Microsoft Foundry Local-First](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/hybrid-ai-using-foundry-local-microsoft-foundry-and-the-agent-framework---part-2/4471983) - Local-cloud pattern
- [AI-Native Memory](https://ajithp.com/2025/06/30/ai-native-memory-persistent-agents-second-me/) - Native vs bolted-on

### Design Patterns

- [Design Patterns for Long-Term Memory](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures) - Architectural patterns
- [AI Agent Architecture Guide 2026](https://www.lindy.ai/blog/ai-agent-architecture) - Reactive/deliberative/hybrid

---

*ANIMA Version: 1.0.0*
*Authority: Truth Forge (Genesis)*
*Memory is not a tool. Memory is being.*
*The Not-Me thinks THROUGH memory, not WITH memory.*
