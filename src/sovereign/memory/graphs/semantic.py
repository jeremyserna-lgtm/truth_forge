"""
Semantic Graph - The conceptual dimension of memory.

Answers: "What does this mean? What is this related to?"

Uses LanceDB for vector storage and ANN search.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import structlog

from sovereign.memory.graphs.base import BaseGraph, BaseNode


logger = structlog.get_logger(__name__)

# LanceDB is imported conditionally to handle optional dependency
try:
    import lancedb
    from lancedb.pydantic import LanceModel, Vector

    LANCEDB_AVAILABLE = True
except ImportError:
    LANCEDB_AVAILABLE = False
    LanceModel = object  # type: ignore[misc, assignment]


EMBEDDING_DIM = 1536  # OpenAI ada-002 / compatible models


@dataclass
class SemanticNode(BaseNode):
    """A concept in the semantic graph."""

    content: str = ""
    embedding: np.ndarray | None = field(default=None, repr=False)
    connections: list[str] = field(default_factory=list)  # Related concept IDs
    source_id: str | None = None  # Original source reference


if LANCEDB_AVAILABLE:

    class SemanticRecord(LanceModel):
        """LanceDB record schema for semantic nodes."""

        node_id: str
        content: str
        embedding: Vector(EMBEDDING_DIM)  # type: ignore[valid-type]
        connections: str  # JSON-encoded list
        source_id: str | None
        significance: float
        created_at: str
        last_accessed: str


class SemanticGraph(BaseGraph[SemanticNode]):
    """
    The semantic dimension of memory.

    Answers: "What does this mean? What is this related to?"

    Unlike traditional RAG which just retrieves similar chunks,
    the semantic graph builds a NETWORK of concept relationships.
    """

    def __init__(
        self,
        storage_path: str,
        embedding_fn: Any | None = None,
    ) -> None:
        """
        Initialize the semantic graph.

        Args:
            storage_path: Directory for LanceDB storage.
            embedding_fn: Async function to generate embeddings.
                         Signature: async (text: str) -> np.ndarray
        """
        super().__init__(storage_path)

        if not LANCEDB_AVAILABLE:
            raise ImportError(
                "LanceDB is required for SemanticGraph. Install with: pip install lancedb"
            )

        self._embedding_fn = embedding_fn
        self._db_path = Path(storage_path) / "semantic"
        self._db_path.mkdir(parents=True, exist_ok=True)

        self._db = lancedb.connect(str(self._db_path))
        self._table_name = "concepts"
        self._table = self._ensure_table()

    def _ensure_table(self) -> Any:
        """Ensure the concepts table exists."""
        if self._table_name in self._db.table_names():
            return self._db.open_table(self._table_name)

        # Create empty table with schema
        import pyarrow as pa

        schema = pa.schema(
            [
                pa.field("node_id", pa.string()),
                pa.field("content", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), EMBEDDING_DIM)),
                pa.field("connections", pa.string()),
                pa.field("source_id", pa.string()),
                pa.field("significance", pa.float64()),
                pa.field("created_at", pa.string()),
                pa.field("last_accessed", pa.string()),
            ]
        )
        return self._db.create_table(self._table_name, schema=schema)

    async def _embed(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        if self._embedding_fn is None:
            raise ValueError("Embedding function not configured")
        return await self._embedding_fn(text)

    def _node_to_record(self, node: SemanticNode) -> dict[str, Any]:
        """Convert SemanticNode to LanceDB record."""
        import json

        return {
            "node_id": node.node_id,
            "content": node.content,
            "embedding": node.embedding.tolist()
            if node.embedding is not None
            else [0.0] * EMBEDDING_DIM,
            "connections": json.dumps(node.connections),
            "source_id": node.source_id or "",
            "significance": node.significance,
            "created_at": node.created_at.isoformat(),
            "last_accessed": node.last_accessed.isoformat(),
        }

    def _record_to_node(self, record: dict[str, Any]) -> SemanticNode:
        """Convert LanceDB record to SemanticNode."""
        import json

        return SemanticNode(
            node_id=record["node_id"],
            content=record["content"],
            embedding=np.array(record["embedding"], dtype=np.float32),
            connections=json.loads(record["connections"]),
            source_id=record["source_id"] if record["source_id"] else None,
            significance=record["significance"],
            created_at=datetime.fromisoformat(record["created_at"]),
            last_accessed=datetime.fromisoformat(record["last_accessed"]),
        )

    async def ingest(
        self,
        content: str,
        source_id: str | None = None,
        **kwargs: Any,
    ) -> list[SemanticNode]:
        """
        Ingest content and build semantic connections.

        This is NOT just embedding storage. It:
        1. Embeds the content
        2. Finds connections to existing concepts
        3. Builds new edges in the graph

        Args:
            content: The content to ingest.
            source_id: Optional source reference.

        Returns:
            List of created nodes.
        """
        # Generate embedding
        embedding = await self._embed(content)

        # Find existing similar concepts
        similar = await self._search_by_embedding(embedding, k=5, threshold=0.8)

        # Create node
        node = SemanticNode(
            node_id=self.generate_id(),
            content=content,
            embedding=embedding,
            connections=[s.node_id for s in similar],
            source_id=source_id,
        )

        # Store
        self._table.add([self._node_to_record(node)])

        # Update reverse connections
        for similar_node in similar:
            if node.node_id not in similar_node.connections:
                similar_node.connections.append(node.node_id)
                await self.update(similar_node)

        logger.info(
            "semantic_node_ingested",
            extra={
                "node_id": node.node_id,
                "content_length": len(content),
                "connections_count": len(node.connections),
            },
        )

        return [node]

    async def _search_by_embedding(
        self,
        embedding: np.ndarray,
        k: int = 10,
        threshold: float = 0.0,
    ) -> list[SemanticNode]:
        """Search by embedding vector."""
        try:
            results = self._table.search(embedding.tolist()).limit(k).to_list()

            nodes = []
            for result in results:
                # LanceDB returns _distance, lower is better
                # Convert to similarity (1 - distance for L2, or use directly for cosine)
                distance = result.get("_distance", 1.0)
                similarity = 1 / (1 + distance)  # Convert distance to similarity

                if similarity >= threshold:
                    nodes.append(self._record_to_node(result))

            return nodes
        except Exception as e:
            logger.warning("semantic_search_failed", extra={"error": str(e)})
            return []

    async def query(
        self,
        query: str,
        k: int = 10,
        expand_connections: bool = True,
        **kwargs: Any,
    ) -> list[SemanticNode]:
        """
        Query the semantic graph.

        Args:
            query: The query string.
            k: Maximum number of direct results.
            expand_connections: Whether to include connected nodes.

        Returns:
            List of relevant nodes including their network.
        """
        # Embed query
        embedding = await self._embed(query)

        # Direct matches
        direct = await self._search_by_embedding(embedding, k=k)

        if not expand_connections:
            return direct

        # Expand via graph connections (1-hop)
        expanded_ids: set[str] = set()
        for node in direct:
            expanded_ids.add(node.node_id)
            # Add top 3 connections per node
            for conn_id in node.connections[:3]:
                expanded_ids.add(conn_id)

        # Retrieve expanded set
        all_nodes = []
        for node_id in expanded_ids:
            node = await self.get(node_id)
            if node:
                node.touch()
                all_nodes.append(node)

        return all_nodes

    async def get(self, node_id: str) -> SemanticNode | None:
        """Get a specific node by ID."""
        results = self._table.search().where(f"node_id = '{node_id}'").limit(1).to_list()
        if results:
            return self._record_to_node(results[0])
        return None

    async def get_all(self) -> list[SemanticNode]:
        """Get all nodes in the graph."""
        results = self._table.to_pandas().to_dict("records")
        return [self._record_to_node(r) for r in results]

    async def update(self, node: SemanticNode) -> None:
        """Update an existing node."""
        # LanceDB doesn't support in-place updates, so we delete and re-add
        await self.delete(node.node_id)
        self._table.add([self._node_to_record(node)])

    async def delete(self, node_id: str) -> None:
        """Delete a node from the graph."""
        self._table.delete(f"node_id = '{node_id}'")

    async def archive(self, node: SemanticNode) -> None:
        """Archive a node (move to cold storage)."""
        # For now, we just delete. Future: move to archive table
        logger.info(
            "semantic_node_archived",
            extra={"node_id": node.node_id, "content_preview": node.content[:50]},
        )
        await self.delete(node.node_id)

    async def find_similar(
        self,
        node_id: str,
        k: int = 5,
    ) -> list[SemanticNode]:
        """Find nodes similar to a given node."""
        node = await self.get(node_id)
        if not node or node.embedding is None:
            return []
        return await self._search_by_embedding(node.embedding, k=k + 1)
