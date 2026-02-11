"""
Emotional Graph - The affective dimension of memory.

Answers: "How did this feel? What's the emotional context?"

Uses DuckDB for emotional pattern storage and queries.

This is CRITICAL for the Not-Me because:
1. Struggle Filter uses it (keep resolutions, discard loops)
2. Stance selection depends on emotional state
3. Total Resonance requires predicting emotional metadata
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import duckdb
import structlog

from sovereign.memory.graphs.base import BaseGraph, BaseNode


logger = structlog.get_logger(__name__)


class EmotionalTone(Enum):
    """Primary emotional tones in interactions."""

    DETERMINED = "determined"
    ANXIOUS = "anxious"
    CURIOUS = "curious"
    FRUSTRATED = "frustrated"
    RESOLVED = "resolved"
    CELEBRATORY = "celebratory"
    CONTEMPLATIVE = "contemplative"
    URGENT = "urgent"
    CALM = "calm"
    CONFUSED = "confused"


@dataclass
class EmotionalNode(BaseNode):
    """An emotional moment in memory."""

    content: str = ""
    tone: EmotionalTone = EmotionalTone.CALM
    intensity: float = 0.5  # 0-1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    associated_entities: list[str] = field(default_factory=list)
    associated_topics: list[str] = field(default_factory=list)


class EmotionalGraph(BaseGraph[EmotionalNode]):
    """
    The emotional dimension of memory.

    Answers: "How did this feel? What's the emotional context?"

    This is CRITICAL for the Not-Me because:
    1. Struggle Filter uses it (keep resolutions, discard loops)
    2. Stance selection depends on emotional state
    3. Total Resonance requires predicting emotional metadata
    """

    def __init__(
        self,
        storage_path: str,
        emotion_analyzer: Any | None = None,
    ) -> None:
        """
        Initialize the emotional graph.

        Args:
            storage_path: Directory for DuckDB storage.
            emotion_analyzer: Async function to analyze emotional content.
                             Signature: async (text: str) -> tuple[EmotionalTone, float]
        """
        super().__init__(storage_path)

        self._emotion_analyzer = emotion_analyzer
        self._db_path = Path(storage_path) / "emotional"
        self._db_path.mkdir(parents=True, exist_ok=True)

        self._conn = duckdb.connect(str(self._db_path / "emotional.duckdb"))
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure the emotional tables exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS emotional_nodes (
                node_id VARCHAR PRIMARY KEY,
                content VARCHAR NOT NULL,
                tone VARCHAR NOT NULL,
                intensity DOUBLE DEFAULT 0.5,
                timestamp TIMESTAMP NOT NULL,
                associated_entities VARCHAR DEFAULT '[]',
                associated_topics VARCHAR DEFAULT '[]',
                significance DOUBLE DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Indexes
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_emotional_timestamp
            ON emotional_nodes(timestamp)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_emotional_tone
            ON emotional_nodes(tone)
        """)

    def _row_to_node(self, row: tuple[Any, ...]) -> EmotionalNode:
        """Convert database row to EmotionalNode."""
        import json

        return EmotionalNode(
            node_id=row[0],
            content=row[1],
            tone=EmotionalTone(row[2]),
            intensity=row[3],
            timestamp=row[4],
            associated_entities=json.loads(row[5]) if row[5] else [],
            associated_topics=json.loads(row[6]) if row[6] else [],
            significance=row[7],
            created_at=row[8],
            last_accessed=row[9],
        )

    async def ingest(
        self,
        content: str,
        timestamp: datetime | None = None,
        entities: list[str] | None = None,
        topics: list[str] | None = None,
        **kwargs: Any,
    ) -> list[EmotionalNode]:
        """
        Extract emotional content from text.

        Args:
            content: The content to analyze.
            timestamp: When this was observed.
            entities: Associated entity IDs.
            topics: Associated topic strings.

        Returns:
            List containing the created emotional node.
        """
        import json

        if timestamp is None:
            timestamp = datetime.utcnow()

        # Analyze emotion
        if self._emotion_analyzer:
            tone, intensity = await self._emotion_analyzer(content)
        else:
            # Default neutral
            tone = EmotionalTone.CALM
            intensity = 0.5

        node = EmotionalNode(
            node_id=self.generate_id(),
            content=content,
            tone=tone,
            intensity=intensity,
            timestamp=timestamp,
            associated_entities=entities or [],
            associated_topics=topics or [],
        )

        self._conn.execute(
            """
            INSERT INTO emotional_nodes
            (node_id, content, tone, intensity, timestamp, associated_entities,
             associated_topics, significance, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                node.node_id,
                node.content,
                node.tone.value,
                node.intensity,
                node.timestamp,
                json.dumps(node.associated_entities),
                json.dumps(node.associated_topics),
                node.significance,
                node.created_at,
                node.last_accessed,
            ],
        )

        logger.info(
            "emotional_node_created",
            extra={
                "node_id": node.node_id,
                "tone": tone.value,
                "intensity": intensity,
            },
        )

        return [node]

    async def query(
        self,
        query: str,
        k: int = 10,
        **kwargs: Any,
    ) -> list[EmotionalNode]:
        """
        Query emotional nodes by content.

        Args:
            query: Search string.
            k: Maximum results.

        Returns:
            Matching emotional nodes.
        """
        results = self._conn.execute(
            """
            SELECT * FROM emotional_nodes
            WHERE content LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            [f"%{query}%", k],
        ).fetchall()

        return [self._row_to_node(r) for r in results]

    async def query_emotional_pattern(
        self,
        entity_id: str | None = None,
        topic: str | None = None,
        time_range: tuple[datetime, datetime] | None = None,
    ) -> list[EmotionalNode]:
        """
        Find emotional patterns.

        Example: "What's the emotional trend around this topic?"

        Args:
            entity_id: Filter by associated entity.
            topic: Filter by associated topic.
            time_range: Filter by time range.

        Returns:
            Emotional nodes matching the filters.
        """
        query = "SELECT * FROM emotional_nodes WHERE 1=1"
        params: list[Any] = []

        if entity_id:
            query += " AND associated_entities LIKE ?"
            params.append(f"%{entity_id}%")

        if topic:
            query += " AND associated_topics LIKE ?"
            params.append(f"%{topic}%")

        if time_range:
            query += " AND timestamp >= ? AND timestamp <= ?"
            params.extend([time_range[0], time_range[1]])

        query += " ORDER BY timestamp DESC LIMIT 50"

        results = self._conn.execute(query, params).fetchall()
        return [self._row_to_node(r) for r in results]

    async def query_current_state(self) -> dict[str, Any]:
        """
        Get current emotional state summary.

        Used by MemoryCortex for context enrichment.

        Returns:
            Dictionary with current emotional state.
        """
        # Get recent emotional nodes (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        results = self._conn.execute(
            """
            SELECT tone, AVG(intensity) as avg_intensity, COUNT(*) as count
            FROM emotional_nodes
            WHERE timestamp >= ?
            GROUP BY tone
            ORDER BY count DESC
        """,
            [cutoff],
        ).fetchall()

        if not results:
            return {
                "dominant_tone": EmotionalTone.CALM.value,
                "intensity": 0.5,
                "tone_distribution": {},
            }

        tone_distribution = {row[0]: {"avg_intensity": row[1], "count": row[2]} for row in results}
        dominant_tone = results[0][0]
        dominant_intensity = results[0][1]

        return {
            "dominant_tone": dominant_tone,
            "intensity": dominant_intensity,
            "tone_distribution": tone_distribution,
        }

    async def detect_loop(self, recent_n: int = 10) -> bool:
        """
        Detect if user is in an anxiety loop.

        Used by Struggle Filter to identify unproductive cycles.

        Args:
            recent_n: Number of recent nodes to analyze.

        Returns:
            True if an anxiety/frustration loop is detected.
        """
        results = self._conn.execute(
            """
            SELECT tone FROM emotional_nodes
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            [recent_n],
        ).fetchall()

        if len(results) < recent_n // 2:
            return False

        anxious_tones = {EmotionalTone.ANXIOUS.value, EmotionalTone.FRUSTRATED.value}
        anxious_count = sum(1 for row in results if row[0] in anxious_tones)

        # 70% anxious/frustrated = loop
        return anxious_count / len(results) > 0.7

    async def detect_resolution(self, content: str) -> bool:
        """
        Detect if content represents a resolution.

        Used by Struggle Filter to identify breakthrough moments.

        Args:
            content: Content to analyze.

        Returns:
            True if this appears to be a resolution.
        """
        if self._emotion_analyzer is None:
            # Simple heuristic without analyzer
            resolution_markers = [
                "solved",
                "fixed",
                "working",
                "done",
                "figured out",
                "got it",
                "finally",
                "success",
                "works now",
                "resolved",
            ]
            content_lower = content.lower()
            return any(marker in content_lower for marker in resolution_markers)

        tone, intensity = await self._emotion_analyzer(content)
        return tone == EmotionalTone.RESOLVED and intensity > 0.6

    async def get_recent(self, n: int = 10) -> list[EmotionalNode]:
        """Get the most recent emotional nodes."""
        results = self._conn.execute(
            """
            SELECT * FROM emotional_nodes
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            [n],
        ).fetchall()
        return [self._row_to_node(r) for r in results]

    async def get_by_tone(
        self,
        tone: EmotionalTone,
        limit: int = 20,
    ) -> list[EmotionalNode]:
        """Get nodes with a specific emotional tone."""
        results = self._conn.execute(
            """
            SELECT * FROM emotional_nodes
            WHERE tone = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            [tone.value, limit],
        ).fetchall()
        return [self._row_to_node(r) for r in results]

    async def get(self, node_id: str) -> EmotionalNode | None:
        """Get a specific node by ID."""
        result = self._conn.execute(
            """
            SELECT * FROM emotional_nodes WHERE node_id = ?
        """,
            [node_id],
        ).fetchone()

        if result:
            self._conn.execute(
                """
                UPDATE emotional_nodes SET last_accessed = ? WHERE node_id = ?
            """,
                [datetime.utcnow(), node_id],
            )
            return self._row_to_node(result)
        return None

    async def get_all(self) -> list[EmotionalNode]:
        """Get all nodes in the graph."""
        results = self._conn.execute("""
            SELECT * FROM emotional_nodes ORDER BY timestamp DESC
        """).fetchall()
        return [self._row_to_node(r) for r in results]

    async def update(self, node: EmotionalNode) -> None:
        """Update an existing node."""
        import json

        self._conn.execute(
            """
            UPDATE emotional_nodes SET
                content = ?,
                tone = ?,
                intensity = ?,
                timestamp = ?,
                associated_entities = ?,
                associated_topics = ?,
                significance = ?,
                last_accessed = ?
            WHERE node_id = ?
        """,
            [
                node.content,
                node.tone.value,
                node.intensity,
                node.timestamp,
                json.dumps(node.associated_entities),
                json.dumps(node.associated_topics),
                node.significance,
                datetime.utcnow(),
                node.node_id,
            ],
        )

    async def delete(self, node_id: str) -> None:
        """Delete a node from the graph."""
        self._conn.execute(
            """
            DELETE FROM emotional_nodes WHERE node_id = ?
        """,
            [node_id],
        )

    async def archive(self, node: EmotionalNode) -> None:
        """Archive a node (move to cold storage)."""
        logger.info(
            "emotional_node_archived",
            extra={
                "node_id": node.node_id,
                "tone": node.tone.value,
            },
        )
        await self.delete(node.node_id)
