"""
Temporal Graph - The chronological dimension of memory.

Answers: "When did this happen? What came before/after?"

Uses DuckDB for timeline queries and efficient range scans.

Key insight from Supermemory: DUAL TIMESTAMPS.
- document_date: When we discussed it
- event_date: When it actually happened
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import duckdb
import structlog

from sovereign.memory.graphs.base import BaseGraph, BaseNode


logger = structlog.get_logger(__name__)


@dataclass
class TemporalNode(BaseNode):
    """A moment in the temporal graph."""

    content: str = ""
    document_date: datetime = field(default_factory=datetime.utcnow)  # When discussed
    event_date: datetime | None = None  # When it actually happened
    prev_node: str | None = None  # Previous in timeline
    next_node: str | None = None  # Next in timeline
    source_id: str | None = None


class TemporalGraph(BaseGraph[TemporalNode]):
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

    def __init__(
        self,
        storage_path: str,
        date_extractor: Any | None = None,
    ) -> None:
        """
        Initialize the temporal graph.

        Args:
            storage_path: Directory for DuckDB storage.
            date_extractor: Async function to extract event dates from text.
                           Signature: async (text: str) -> list[datetime]
        """
        super().__init__(storage_path)

        self._date_extractor = date_extractor
        self._db_path = Path(storage_path) / "temporal"
        self._db_path.mkdir(parents=True, exist_ok=True)

        self._conn = duckdb.connect(str(self._db_path / "temporal.duckdb"))
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure the temporal tables exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS temporal_nodes (
                node_id VARCHAR PRIMARY KEY,
                content VARCHAR NOT NULL,
                document_date TIMESTAMP NOT NULL,
                event_date TIMESTAMP,
                prev_node VARCHAR,
                next_node VARCHAR,
                source_id VARCHAR,
                significance DOUBLE DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes for efficient timeline queries
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_document_date
            ON temporal_nodes(document_date)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_date
            ON temporal_nodes(event_date)
        """)

    def _row_to_node(self, row: tuple[Any, ...]) -> TemporalNode:
        """Convert database row to TemporalNode."""
        return TemporalNode(
            node_id=row[0],
            content=row[1],
            document_date=row[2],
            event_date=row[3],
            prev_node=row[4],
            next_node=row[5],
            source_id=row[6],
            significance=row[7],
            created_at=row[8],
            last_accessed=row[9],
        )

    async def _extract_event_dates(self, content: str) -> list[datetime]:
        """Extract event dates from content."""
        if self._date_extractor is None:
            return []
        return await self._date_extractor(content)

    async def _find_predecessor(self, timestamp: datetime) -> TemporalNode | None:
        """Find the node immediately before this timestamp."""
        result = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE document_date < ?
            ORDER BY document_date DESC
            LIMIT 1
        """,
            [timestamp],
        ).fetchone()

        return self._row_to_node(result) if result else None

    async def _find_successor(self, timestamp: datetime) -> TemporalNode | None:
        """Find the node immediately after this timestamp."""
        result = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE document_date > ?
            ORDER BY document_date ASC
            LIMIT 1
        """,
            [timestamp],
        ).fetchone()

        return self._row_to_node(result) if result else None

    async def ingest(
        self,
        content: str,
        timestamp: datetime | None = None,
        source_id: str | None = None,
        **kwargs: Any,
    ) -> list[TemporalNode]:
        """
        Ingest a moment into the temporal graph.

        Extracts both document_date and event_date,
        then links into the timeline.

        Args:
            content: The content to ingest.
            timestamp: When this was documented (defaults to now).
            source_id: Optional source reference.

        Returns:
            List containing the created node.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Extract event dates from content
        event_dates = await self._extract_event_dates(content)
        event_date = event_dates[0] if event_dates else None

        # Find position in timeline
        prev_node = await self._find_predecessor(timestamp)
        next_node = await self._find_successor(timestamp)

        # Create node
        node = TemporalNode(
            node_id=self.generate_id(),
            content=content,
            document_date=timestamp,
            event_date=event_date,
            prev_node=prev_node.node_id if prev_node else None,
            next_node=next_node.node_id if next_node else None,
            source_id=source_id,
        )

        # Insert into database
        self._conn.execute(
            """
            INSERT INTO temporal_nodes
            (node_id, content, document_date, event_date, prev_node, next_node,
             source_id, significance, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                node.node_id,
                node.content,
                node.document_date,
                node.event_date,
                node.prev_node,
                node.next_node,
                node.source_id,
                node.significance,
                node.created_at,
                node.last_accessed,
            ],
        )

        # Update chain links
        if prev_node:
            self._conn.execute(
                """
                UPDATE temporal_nodes SET next_node = ? WHERE node_id = ?
            """,
                [node.node_id, prev_node.node_id],
            )

        if next_node:
            self._conn.execute(
                """
                UPDATE temporal_nodes SET prev_node = ? WHERE node_id = ?
            """,
                [node.node_id, next_node.node_id],
            )

        logger.info(
            "temporal_node_ingested",
            extra={
                "node_id": node.node_id,
                "document_date": timestamp.isoformat(),
                "event_date": event_date.isoformat() if event_date else None,
            },
        )

        return [node]

    async def query(
        self,
        query: str,
        k: int = 10,
        **kwargs: Any,
    ) -> list[TemporalNode]:
        """
        Query by content search within temporal context.

        Args:
            query: Search string.
            k: Maximum results.

        Returns:
            Matching nodes ordered by document_date.
        """
        results = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE content LIKE ?
            ORDER BY document_date DESC
            LIMIT ?
        """,
            [f"%{query}%", k],
        ).fetchall()

        return [self._row_to_node(r) for r in results]

    async def query_timeline(
        self,
        start: datetime,
        end: datetime,
    ) -> list[TemporalNode]:
        """Get all memories in a time range."""
        results = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE document_date >= ? AND document_date <= ?
            ORDER BY document_date ASC
        """,
            [start, end],
        ).fetchall()

        return [self._row_to_node(r) for r in results]

    async def query_recent(self, days: int = 7) -> list[TemporalNode]:
        """Get recent memories."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        results = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE document_date >= ?
            ORDER BY document_date DESC
        """,
            [cutoff],
        ).fetchall()

        return [self._row_to_node(r) for r in results]

    async def query_before(self, event: str, limit: int = 10) -> list[TemporalNode]:
        """What happened before this event?"""
        # Find the event
        target_result = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE content LIKE ?
            ORDER BY document_date DESC
            LIMIT 1
        """,
            [f"%{event}%"],
        ).fetchone()

        if not target_result:
            return []

        target = self._row_to_node(target_result)

        # Traverse backwards through chain
        results: list[TemporalNode] = []
        current_id = target.prev_node

        while current_id and len(results) < limit:
            current = await self.get(current_id)
            if current:
                results.append(current)
                current_id = current.prev_node
            else:
                break

        return results

    async def query_after(self, event: str, limit: int = 10) -> list[TemporalNode]:
        """What happened after this event?"""
        # Find the event
        target_result = self._conn.execute(
            """
            SELECT * FROM temporal_nodes
            WHERE content LIKE ?
            ORDER BY document_date DESC
            LIMIT 1
        """,
            [f"%{event}%"],
        ).fetchone()

        if not target_result:
            return []

        target = self._row_to_node(target_result)

        # Traverse forwards through chain
        results: list[TemporalNode] = []
        current_id = target.next_node

        while current_id and len(results) < limit:
            current = await self.get(current_id)
            if current:
                results.append(current)
                current_id = current.next_node
            else:
                break

        return results

    async def get(self, node_id: str) -> TemporalNode | None:
        """Get a specific node by ID."""
        result = self._conn.execute(
            """
            SELECT * FROM temporal_nodes WHERE node_id = ?
        """,
            [node_id],
        ).fetchone()

        if result:
            # Update last_accessed
            self._conn.execute(
                """
                UPDATE temporal_nodes
                SET last_accessed = ?
                WHERE node_id = ?
            """,
                [datetime.utcnow(), node_id],
            )
            return self._row_to_node(result)
        return None

    async def get_all(self) -> list[TemporalNode]:
        """Get all nodes in the graph."""
        results = self._conn.execute("""
            SELECT * FROM temporal_nodes ORDER BY document_date DESC
        """).fetchall()
        return [self._row_to_node(r) for r in results]

    async def update(self, node: TemporalNode) -> None:
        """Update an existing node."""
        self._conn.execute(
            """
            UPDATE temporal_nodes SET
                content = ?,
                document_date = ?,
                event_date = ?,
                prev_node = ?,
                next_node = ?,
                source_id = ?,
                significance = ?,
                last_accessed = ?
            WHERE node_id = ?
        """,
            [
                node.content,
                node.document_date,
                node.event_date,
                node.prev_node,
                node.next_node,
                node.source_id,
                node.significance,
                datetime.utcnow(),
                node.node_id,
            ],
        )

    async def delete(self, node_id: str) -> None:
        """Delete a node from the graph."""
        # First, fix the chain links
        node = await self.get(node_id)
        if node:
            if node.prev_node:
                self._conn.execute(
                    """
                    UPDATE temporal_nodes SET next_node = ? WHERE node_id = ?
                """,
                    [node.next_node, node.prev_node],
                )

            if node.next_node:
                self._conn.execute(
                    """
                    UPDATE temporal_nodes SET prev_node = ? WHERE node_id = ?
                """,
                    [node.prev_node, node.next_node],
                )

        self._conn.execute(
            """
            DELETE FROM temporal_nodes WHERE node_id = ?
        """,
            [node_id],
        )

    async def archive(self, node: TemporalNode) -> None:
        """Archive a node (move to cold storage)."""
        logger.info(
            "temporal_node_archived",
            extra={
                "node_id": node.node_id,
                "document_date": node.document_date.isoformat(),
            },
        )
        await self.delete(node.node_id)
