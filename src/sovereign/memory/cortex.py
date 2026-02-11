"""
Memory Cortex - The integration layer that makes memory NATIVE.

Every input flows through here.
Every output flows through here.
Memory is not optional—it's the fabric of cognition.

The LLM NEVER sees raw input. It always sees memory-enriched input.
This is why memory is NATIVE—it cannot be bypassed.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import structlog

from sovereign.memory.graphs.causal import CausalGraph
from sovereign.memory.graphs.emotional import EmotionalGraph
from sovereign.memory.graphs.entity import EntityGraph
from sovereign.memory.graphs.semantic import SemanticGraph
from sovereign.memory.graphs.temporal import TemporalGraph


logger = structlog.get_logger(__name__)


@dataclass
class EnrichedInput:
    """
    What the LLM actually receives.

    NOT the raw user input—the memory-enriched version.
    """

    original_input: str
    semantic_context: list[dict[str, Any]] = field(default_factory=list)
    temporal_context: list[dict[str, Any]] = field(default_factory=list)
    causal_context: list[dict[str, Any]] = field(default_factory=list)
    entity_context: list[dict[str, Any]] = field(default_factory=list)
    emotional_context: dict[str, Any] = field(default_factory=dict)
    enrichment_metadata: dict[str, Any] = field(default_factory=dict)


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
    ) -> None:
        """
        Initialize the Memory Cortex.

        Args:
            semantic: The semantic graph (what does this mean?)
            temporal: The temporal graph (when did this happen?)
            causal: The causal graph (why did this happen?)
            entity: The entity graph (who/what is this?)
            emotional: The emotional graph (how did this feel?)
        """
        self._semantic = semantic
        self._temporal = temporal
        self._causal = causal
        self._entity = entity
        self._emotional = emotional

    async def perceive(self, input_text: str) -> EnrichedInput:
        """
        Transform raw input into memory-enriched input.

        This is the PERCEPTION phase—before any thinking happens.
        The LLM never sees raw input. It sees this.

        Args:
            input_text: The raw user input.

        Returns:
            EnrichedInput with context from all five memory dimensions.
        """
        start_time = datetime.utcnow()

        # Parallel queries to all graphs
        semantic_task = self._semantic.query(input_text, k=5)
        temporal_task = self._temporal.query_recent(days=7)
        causal_task = self._causal.query_related(input_text)
        entity_task = self._entity.query_mentioned(input_text)
        emotional_task = self._emotional.query_current_state()

        # Gather all results
        (
            semantic_nodes,
            temporal_nodes,
            causal_nodes,
            entity_nodes,
            emotional_state,
        ) = await asyncio.gather(
            semantic_task,
            temporal_task,
            causal_task,
            entity_task,
            emotional_task,
        )

        # Format contexts
        semantic_context = self._format_semantic(semantic_nodes)
        temporal_context = self._format_temporal(temporal_nodes)
        causal_context = self._format_causal(causal_nodes)
        entity_context = self._format_entity(entity_nodes)
        emotional_context = self._format_emotional(emotional_state)

        elapsed = (datetime.utcnow() - start_time).total_seconds()

        enriched = EnrichedInput(
            original_input=input_text,
            semantic_context=semantic_context,
            temporal_context=temporal_context,
            causal_context=causal_context,
            entity_context=entity_context,
            emotional_context=emotional_context,
            enrichment_metadata={
                "enriched_at": datetime.utcnow().isoformat(),
                "graphs_queried": 5,
                "enrichment_time_seconds": elapsed,
                "semantic_hits": len(semantic_nodes),
                "temporal_hits": len(temporal_nodes),
                "causal_hits": len(causal_nodes),
                "entity_hits": len(entity_nodes),
            },
        )

        logger.info(
            "perception_complete",
            extra={
                "input_length": len(input_text),
                "enrichment_time_seconds": elapsed,
                "total_context_items": (
                    len(semantic_context)
                    + len(temporal_context)
                    + len(causal_context)
                    + len(entity_context)
                ),
            },
        )

        return enriched

    async def commit(self, input_text: str, output_text: str) -> None:
        """
        Commit interaction to all memory graphs.

        This is the INTEGRATION phase—after response is generated.
        Happens AUTOMATICALLY, not via tool call.

        Args:
            input_text: The original user input.
            output_text: The generated response.
        """
        timestamp = datetime.utcnow()
        combined = f"{input_text}\n\n{output_text}"

        # Store in all graphs (parallel)
        await asyncio.gather(
            self._semantic.ingest(combined),
            self._temporal.ingest(combined, timestamp=timestamp),
            self._causal.ingest(output_text),
            self._entity.ingest(output_text, timestamp=timestamp),
            self._emotional.ingest(input_text, timestamp=timestamp),
        )

        logger.info(
            "memory_committed",
            extra={
                "input_length": len(input_text),
                "output_length": len(output_text),
                "timestamp": timestamp.isoformat(),
            },
        )

    def build_context_block(self, enriched: EnrichedInput) -> str:
        """
        Build the context block that prepends user input.

        This is what makes memory INVISIBLE to the user
        but VISIBLE to the LLM.

        Args:
            enriched: The enriched input from perceive().

        Returns:
            Formatted context block string.
        """
        sections = []

        # Semantic context
        if enriched.semantic_context:
            semantic_lines = []
            for item in enriched.semantic_context[:5]:
                semantic_lines.append(f"- {item.get('content', '')[:100]}")
            if semantic_lines:
                sections.append("## Relevant Concepts (Semantic)\n" + "\n".join(semantic_lines))

        # Temporal context
        if enriched.temporal_context:
            temporal_lines = []
            for item in enriched.temporal_context[:5]:
                date_str = item.get("document_date", "")
                content = item.get("content", "")[:80]
                temporal_lines.append(f"- [{date_str}] {content}")
            if temporal_lines:
                sections.append("## Recent Timeline (Temporal)\n" + "\n".join(temporal_lines))

        # Causal context
        if enriched.causal_context:
            causal_lines = []
            for item in enriched.causal_context[:3]:
                content = item.get("content", "")[:100]
                causal_lines.append(f"- {content}")
            if causal_lines:
                sections.append("## Causal Background\n" + "\n".join(causal_lines))

        # Entity context
        if enriched.entity_context:
            entity_lines = []
            for item in enriched.entity_context[:5]:
                name = item.get("name", "")
                entity_type = item.get("entity_type", "")
                mentions = item.get("mentions", 0)
                entity_lines.append(f"- {name} ({entity_type}, {mentions} mentions)")
            if entity_lines:
                sections.append("## Known Entities\n" + "\n".join(entity_lines))

        # Emotional context
        if enriched.emotional_context:
            tone = enriched.emotional_context.get("dominant_tone", "calm")
            intensity = enriched.emotional_context.get("intensity", 0.5)
            sections.append(
                f"## Emotional State\n- Current tone: {tone} (intensity: {intensity:.1f})"
            )

        # Build final block
        if sections:
            context_block = "<memory_context>\n" + "\n\n".join(sections) + "\n</memory_context>"
        else:
            context_block = ""

        return f"{context_block}\n\n## User Message\n{enriched.original_input}"

    def _format_semantic(self, nodes: list[Any]) -> list[dict[str, Any]]:
        """Format semantic nodes for context."""
        return [
            {
                "node_id": node.node_id,
                "content": node.content,
                "significance": node.significance,
                "connections": len(node.connections),
            }
            for node in nodes
        ]

    def _format_temporal(self, nodes: list[Any]) -> list[dict[str, Any]]:
        """Format temporal nodes for context."""
        return [
            {
                "node_id": node.node_id,
                "content": node.content,
                "document_date": node.document_date.isoformat() if node.document_date else "",
                "event_date": node.event_date.isoformat() if node.event_date else None,
            }
            for node in nodes
        ]

    def _format_causal(self, nodes: list[Any]) -> list[dict[str, Any]]:
        """Format causal nodes for context."""
        return [
            {
                "node_id": node.node_id,
                "content": node.content,
                "causes_count": len(node.causes),
                "effects_count": len(node.effects),
            }
            for node in nodes
        ]

    def _format_entity(self, nodes: list[Any]) -> list[dict[str, Any]]:
        """Format entity nodes for context."""
        return [
            {
                "node_id": node.node_id,
                "name": node.name,
                "entity_type": node.entity_type,
                "mentions": node.mentions,
                "aliases": node.aliases[:3],  # Top 3 aliases
            }
            for node in nodes
        ]

    def _format_emotional(self, state: dict[str, Any]) -> dict[str, Any]:
        """Format emotional state for context."""
        return state

    async def consolidate(self) -> None:
        """
        Consolidate memory graphs.

        Called during sleep-time compute to merge related nodes,
        strengthen connections, and optimize storage.
        """
        logger.info("memory_consolidation_started")

        # Run decay on all graphs
        semantic_archived = await self._semantic.decay()
        temporal_archived = await self._temporal.decay()
        causal_archived = await self._causal.decay()
        entity_archived = await self._entity.decay()
        emotional_archived = await self._emotional.decay()

        logger.info(
            "memory_consolidation_complete",
            extra={
                "semantic_archived": semantic_archived,
                "temporal_archived": temporal_archived,
                "causal_archived": causal_archived,
                "entity_archived": entity_archived,
                "emotional_archived": emotional_archived,
            },
        )

    async def optimize_graphs(self) -> None:
        """
        Optimize graph storage and indices.

        Called during sleep-time compute.
        """
        # This would include things like:
        # - Rebalancing indices
        # - Vacuuming databases
        # - Optimizing vector indices
        logger.info("graph_optimization_complete")

    async def discover_connections(self) -> int:
        """
        Discover new connections between nodes across graphs.

        Called during sleep-time compute to find emergent patterns.

        Returns:
            Number of new connections discovered.
        """
        # This would include cross-graph analysis like:
        # - Linking entities to semantic concepts
        # - Finding causal patterns in temporal sequences
        # - Associating emotional patterns with entities
        logger.info("connection_discovery_complete")
        return 0
