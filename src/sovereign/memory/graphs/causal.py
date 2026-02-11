"""
Causal Graph - The cause-and-effect dimension of memory.

Answers: "Why did this happen? What will this cause?"

Uses DuckDB for graph traversals and relationship queries.

From MAGMA: "The causal graph maps cause-and-effect relationships.
When you ask 'why,' MAGMA traverses these directed edges to find
logical dependencies."
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import duckdb
import structlog

from sovereign.memory.graphs.base import BaseGraph, BaseNode


logger = structlog.get_logger(__name__)


class CausalRelation(Enum):
    """Types of causal relationships."""

    CAUSES = "causes"
    ENABLES = "enables"
    PREVENTS = "prevents"
    REQUIRES = "requires"
    CORRELATES = "correlates"


@dataclass
class CausalEdge:
    """A causal relationship between two nodes."""

    edge_id: str
    source_id: str
    target_id: str
    relation: CausalRelation
    confidence: float  # How certain is this causal link (0-1)
    evidence: str  # What supports this connection
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CausalNode(BaseNode):
    """An event/state in the causal graph."""

    content: str = ""
    causes: list[CausalEdge] = field(default_factory=list)  # What caused this
    effects: list[CausalEdge] = field(default_factory=list)  # What this caused


class CausalGraph(BaseGraph[CausalNode]):
    """
    The causal dimension of memory.

    Answers: "Why did this happen? What will this cause?"

    Traditional memory systems fail at "why" questions because
    they only do semantic similarity. Causal graphs solve this
    by tracking cause-and-effect relationships explicitly.
    """

    def __init__(
        self,
        storage_path: str,
        causal_extractor: Any | None = None,
    ) -> None:
        """
        Initialize the causal graph.

        Args:
            storage_path: Directory for DuckDB storage.
            causal_extractor: Async function to extract causal pairs from text.
                             Signature: async (text: str) -> list[tuple]
                             Returns: [(cause, effect, relation, confidence), ...]
        """
        super().__init__(storage_path)

        self._causal_extractor = causal_extractor
        self._db_path = Path(storage_path) / "causal"
        self._db_path.mkdir(parents=True, exist_ok=True)

        self._conn = duckdb.connect(str(self._db_path / "causal.duckdb"))
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure the causal tables exist."""
        # Nodes table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS causal_nodes (
                node_id VARCHAR PRIMARY KEY,
                content VARCHAR NOT NULL,
                significance DOUBLE DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Edges table (the causal relationships)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS causal_edges (
                edge_id VARCHAR PRIMARY KEY,
                source_id VARCHAR NOT NULL,
                target_id VARCHAR NOT NULL,
                relation VARCHAR NOT NULL,
                confidence DOUBLE DEFAULT 0.5,
                evidence VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES causal_nodes(node_id),
                FOREIGN KEY (target_id) REFERENCES causal_nodes(node_id)
            )
        """)

        # Indexes for efficient traversals
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON causal_edges(source_id)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_target ON causal_edges(target_id)
        """)

    def _row_to_node(self, row: tuple[Any, ...]) -> CausalNode:
        """Convert database row to CausalNode."""
        node = CausalNode(
            node_id=row[0],
            content=row[1],
            significance=row[2],
            created_at=row[3],
            last_accessed=row[4],
        )
        return node

    def _row_to_edge(self, row: tuple[Any, ...]) -> CausalEdge:
        """Convert database row to CausalEdge."""
        return CausalEdge(
            edge_id=row[0],
            source_id=row[1],
            target_id=row[2],
            relation=CausalRelation(row[3]),
            confidence=row[4],
            evidence=row[5] or "",
            created_at=row[6],
        )

    async def _get_or_create_node(self, content: str) -> CausalNode:
        """Get existing node by content or create new one."""
        # Check for existing node with similar content
        result = self._conn.execute(
            """
            SELECT * FROM causal_nodes WHERE content = ? LIMIT 1
        """,
            [content],
        ).fetchone()

        if result:
            return self._row_to_node(result)

        # Create new node
        node = CausalNode(
            node_id=self.generate_id(),
            content=content,
        )

        self._conn.execute(
            """
            INSERT INTO causal_nodes (node_id, content, significance, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?)
        """,
            [node.node_id, node.content, node.significance, node.created_at, node.last_accessed],
        )

        return node

    async def _load_node_edges(self, node: CausalNode) -> CausalNode:
        """Load causes and effects for a node."""
        # Load causes (edges where this node is the target)
        causes = self._conn.execute(
            """
            SELECT * FROM causal_edges WHERE target_id = ?
        """,
            [node.node_id],
        ).fetchall()
        node.causes = [self._row_to_edge(r) for r in causes]

        # Load effects (edges where this node is the source)
        effects = self._conn.execute(
            """
            SELECT * FROM causal_edges WHERE source_id = ?
        """,
            [node.node_id],
        ).fetchall()
        node.effects = [self._row_to_edge(r) for r in effects]

        return node

    async def ingest(
        self,
        content: str,
        **kwargs: Any,
    ) -> list[CausalNode]:
        """
        Ingest content and extract causal relationships.

        Args:
            content: The content to analyze for causal relationships.

        Returns:
            List of created/updated nodes.
        """
        if self._causal_extractor is None:
            # Without an extractor, just store the content as a node
            node = await self._get_or_create_node(content)
            return [node]

        # Extract causal pairs using LLM
        causal_pairs = await self._causal_extractor(content)

        nodes = []
        for cause_text, effect_text, relation_str, confidence in causal_pairs:
            # Get or create nodes for cause and effect
            cause_node = await self._get_or_create_node(cause_text)
            effect_node = await self._get_or_create_node(effect_text)

            # Create edge
            edge = CausalEdge(
                edge_id=self.generate_id(),
                source_id=cause_node.node_id,
                target_id=effect_node.node_id,
                relation=CausalRelation(relation_str),
                confidence=confidence,
                evidence=content,
            )

            # Store edge
            self._conn.execute(
                """
                INSERT INTO causal_edges
                (edge_id, source_id, target_id, relation, confidence, evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    edge.edge_id,
                    edge.source_id,
                    edge.target_id,
                    edge.relation.value,
                    edge.confidence,
                    edge.evidence,
                    edge.created_at,
                ],
            )

            # Load edges into nodes
            cause_node = await self._load_node_edges(cause_node)
            effect_node = await self._load_node_edges(effect_node)

            nodes.extend([cause_node, effect_node])

            logger.info(
                "causal_edge_created",
                extra={
                    "cause": cause_text[:50],
                    "effect": effect_text[:50],
                    "relation": relation_str,
                    "confidence": confidence,
                },
            )

        return nodes

    async def query(
        self,
        query: str,
        k: int = 10,
        **kwargs: Any,
    ) -> list[CausalNode]:
        """
        Query the causal graph by content search.

        Args:
            query: Search string.
            k: Maximum results.

        Returns:
            Matching nodes with their causal relationships loaded.
        """
        results = self._conn.execute(
            """
            SELECT * FROM causal_nodes
            WHERE content LIKE ?
            ORDER BY last_accessed DESC
            LIMIT ?
        """,
            [f"%{query}%", k],
        ).fetchall()

        nodes = []
        for row in results:
            node = self._row_to_node(row)
            node = await self._load_node_edges(node)
            nodes.append(node)

        return nodes

    async def query_why(self, event: str, depth: int = 3) -> list[CausalNode]:
        """
        Answer "why" questions by traversing causes.

        Finds what caused the given event by following causal
        edges backwards through the graph.

        Args:
            event: The event/content to find causes for.
            depth: How far back in the causal chain to go.

        Returns:
            List of causal nodes representing the cause chain.
        """
        # Find the target node
        target_result = self._conn.execute(
            """
            SELECT * FROM causal_nodes
            WHERE content LIKE ?
            ORDER BY last_accessed DESC
            LIMIT 1
        """,
            [f"%{event}%"],
        ).fetchone()

        if not target_result:
            return []

        target = self._row_to_node(target_result)

        # BFS traversal of causes
        results: list[CausalNode] = []
        queue: list[tuple[CausalNode, int]] = [(target, 0)]
        visited: set[str] = set()

        while queue and len(results) < 20:
            current, current_depth = queue.pop(0)
            if current.node_id in visited or current_depth > depth:
                continue

            visited.add(current.node_id)
            current = await self._load_node_edges(current)
            results.append(current)

            # Add causes to queue
            for edge in current.causes:
                cause_node = await self.get(edge.source_id)
                if cause_node:
                    queue.append((cause_node, current_depth + 1))

        return results

    async def query_consequences(self, event: str, depth: int = 3) -> list[CausalNode]:
        """
        Answer "what will happen" questions by traversing effects.

        Finds what the given event will cause by following causal
        edges forward through the graph.

        Args:
            event: The event/content to find effects for.
            depth: How far forward in the causal chain to go.

        Returns:
            List of causal nodes representing the effect chain.
        """
        # Find the source node
        source_result = self._conn.execute(
            """
            SELECT * FROM causal_nodes
            WHERE content LIKE ?
            ORDER BY last_accessed DESC
            LIMIT 1
        """,
            [f"%{event}%"],
        ).fetchone()

        if not source_result:
            return []

        source = self._row_to_node(source_result)

        # BFS traversal of effects
        results: list[CausalNode] = []
        queue: list[tuple[CausalNode, int]] = [(source, 0)]
        visited: set[str] = set()

        while queue and len(results) < 20:
            current, current_depth = queue.pop(0)
            if current.node_id in visited or current_depth > depth:
                continue

            visited.add(current.node_id)
            current = await self._load_node_edges(current)
            results.append(current)

            # Add effects to queue
            for edge in current.effects:
                effect_node = await self.get(edge.target_id)
                if effect_node:
                    queue.append((effect_node, current_depth + 1))

        return results

    async def query_related(self, content: str) -> list[CausalNode]:
        """
        Find causally related nodes for context enrichment.

        Used by MemoryCortex for automatic context building.

        Args:
            content: Content to find causal context for.

        Returns:
            Nodes causally related to the content.
        """
        # Find nodes matching content
        direct = await self.query(content, k=5)

        # Expand to include causes and effects (1 hop)
        related_ids: set[str] = set()
        for node in direct:
            related_ids.add(node.node_id)
            for edge in node.causes[:3]:
                related_ids.add(edge.source_id)
            for edge in node.effects[:3]:
                related_ids.add(edge.target_id)

        # Fetch all related nodes
        results = []
        for node_id in related_ids:
            node = await self.get(node_id)
            if node:
                results.append(node)

        return results

    async def get(self, node_id: str) -> CausalNode | None:
        """Get a specific node by ID with edges loaded."""
        result = self._conn.execute(
            """
            SELECT * FROM causal_nodes WHERE node_id = ?
        """,
            [node_id],
        ).fetchone()

        if result:
            # Update last_accessed
            self._conn.execute(
                """
                UPDATE causal_nodes SET last_accessed = ? WHERE node_id = ?
            """,
                [datetime.utcnow(), node_id],
            )

            node = self._row_to_node(result)
            return await self._load_node_edges(node)
        return None

    async def get_all(self) -> list[CausalNode]:
        """Get all nodes in the graph."""
        results = self._conn.execute("""
            SELECT * FROM causal_nodes ORDER BY last_accessed DESC
        """).fetchall()

        nodes = []
        for row in results:
            node = self._row_to_node(row)
            node = await self._load_node_edges(node)
            nodes.append(node)

        return nodes

    async def update(self, node: CausalNode) -> None:
        """Update an existing node."""
        self._conn.execute(
            """
            UPDATE causal_nodes SET
                content = ?,
                significance = ?,
                last_accessed = ?
            WHERE node_id = ?
        """,
            [node.content, node.significance, datetime.utcnow(), node.node_id],
        )

    async def delete(self, node_id: str) -> None:
        """Delete a node and its edges from the graph."""
        # Delete edges first
        self._conn.execute(
            """
            DELETE FROM causal_edges WHERE source_id = ? OR target_id = ?
        """,
            [node_id, node_id],
        )

        # Delete node
        self._conn.execute(
            """
            DELETE FROM causal_nodes WHERE node_id = ?
        """,
            [node_id],
        )

    async def archive(self, node: CausalNode) -> None:
        """Archive a node (move to cold storage)."""
        logger.info(
            "causal_node_archived",
            extra={"node_id": node.node_id, "content_preview": node.content[:50]},
        )
        await self.delete(node.node_id)
