"""
Entity Graph - The identity dimension of memory.

Answers: "Who is this? What is their relationship to X?"

Uses DuckDB for entity storage and relationship queries.

Key insight: OBJECT PERMANENCE.
The entity graph tracks entities across time, even when
they're mentioned weeks apart or by different names.

From Mem0g: "Memories are stored as directed labeled graphs
with entities as nodes and relationships as edges."
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb
import structlog

from sovereign.memory.graphs.base import BaseGraph, BaseNode


logger = structlog.get_logger(__name__)


@dataclass
class EntityRelation:
    """A relationship between entities."""

    relation_id: str
    source_id: str
    target_id: str
    relation_type: str  # knows, works_at, owns, part_of, etc.
    properties: dict[str, str] = field(default_factory=dict)
    first_observed: datetime = field(default_factory=datetime.utcnow)
    last_observed: datetime = field(default_factory=datetime.utcnow)


@dataclass
class EntityNode(BaseNode):
    """An entity (person, place, thing, concept)."""

    name: str = ""
    entity_type: str = ""  # person, organization, location, concept, object
    aliases: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    mentions: int = 0


class EntityGraph(BaseGraph[EntityNode]):
    """
    The entity dimension of memory.

    Answers: "Who is this? What is their relationship to X?"

    Key insight: OBJECT PERMANENCE.
    The entity graph tracks entities across time, even when
    they're mentioned weeks apart or by different names.
    """

    def __init__(
        self,
        storage_path: str,
        entity_extractor: Any | None = None,
    ) -> None:
        """
        Initialize the entity graph.

        Args:
            storage_path: Directory for DuckDB storage.
            entity_extractor: Async function to extract entities from text.
                             Signature: async (text: str) -> list[EntityNode]
        """
        super().__init__(storage_path)

        self._entity_extractor = entity_extractor
        self._db_path = Path(storage_path) / "entity"
        self._db_path.mkdir(parents=True, exist_ok=True)

        self._conn = duckdb.connect(str(self._db_path / "entity.duckdb"))
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Ensure the entity tables exist."""
        # Entities table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                node_id VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                entity_type VARCHAR NOT NULL,
                aliases VARCHAR DEFAULT '[]',
                attributes VARCHAR DEFAULT '{}',
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                mentions INTEGER DEFAULT 0,
                significance DOUBLE DEFAULT 0.5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Relations table
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_relations (
                relation_id VARCHAR PRIMARY KEY,
                source_id VARCHAR NOT NULL,
                target_id VARCHAR NOT NULL,
                relation_type VARCHAR NOT NULL,
                properties VARCHAR DEFAULT '{}',
                first_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_observed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES entities(node_id),
                FOREIGN KEY (target_id) REFERENCES entities(node_id)
            )
        """)

        # Indexes
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(entity_type)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_relation_source ON entity_relations(source_id)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_relation_target ON entity_relations(target_id)
        """)

    def _row_to_node(self, row: tuple[Any, ...]) -> EntityNode:
        """Convert database row to EntityNode."""
        import json

        return EntityNode(
            node_id=row[0],
            name=row[1],
            entity_type=row[2],
            aliases=json.loads(row[3]) if row[3] else [],
            attributes=json.loads(row[4]) if row[4] else {},
            first_seen=row[5],
            last_seen=row[6],
            mentions=row[7],
            significance=row[8],
            created_at=row[9],
            last_accessed=row[10],
        )

    def _row_to_relation(self, row: tuple[Any, ...]) -> EntityRelation:
        """Convert database row to EntityRelation."""
        import json

        return EntityRelation(
            relation_id=row[0],
            source_id=row[1],
            target_id=row[2],
            relation_type=row[3],
            properties=json.loads(row[4]) if row[4] else {},
            first_observed=row[5],
            last_observed=row[6],
        )

    async def _find_existing(
        self,
        name: str,
        entity_type: str,
    ) -> EntityNode | None:
        """Find existing entity by name or alias."""
        import json

        # Check by exact name
        result = self._conn.execute(
            """
            SELECT * FROM entities
            WHERE LOWER(name) = LOWER(?) AND entity_type = ?
            LIMIT 1
        """,
            [name, entity_type],
        ).fetchone()

        if result:
            return self._row_to_node(result)

        # Check by alias
        all_entities = self._conn.execute(
            """
            SELECT * FROM entities WHERE entity_type = ?
        """,
            [entity_type],
        ).fetchall()

        for row in all_entities:
            aliases = json.loads(row[3]) if row[3] else []
            if name.lower() in [a.lower() for a in aliases]:
                return self._row_to_node(row)

        return None

    async def ingest(
        self,
        content: str,
        timestamp: datetime | None = None,
        **kwargs: Any,
    ) -> list[EntityNode]:
        """
        Extract and link entities from content.

        Args:
            content: The content to extract entities from.
            timestamp: When this content was observed.

        Returns:
            List of extracted/updated entity nodes.
        """
        import json

        if timestamp is None:
            timestamp = datetime.utcnow()

        if self._entity_extractor is None:
            return []

        # Extract entities using LLM
        extracted = await self._entity_extractor(content)

        nodes = []
        for entity in extracted:
            # Check for existing entity
            existing = await self._find_existing(entity.name, entity.entity_type)

            if existing:
                # Update existing entity
                existing.mentions += 1
                existing.last_seen = timestamp

                # Add any new aliases
                for alias in entity.aliases:
                    if alias.lower() not in [a.lower() for a in existing.aliases]:
                        existing.aliases.append(alias)

                # Merge attributes
                existing.attributes.update(entity.attributes)

                # Update in database
                self._conn.execute(
                    """
                    UPDATE entities SET
                        aliases = ?,
                        attributes = ?,
                        last_seen = ?,
                        mentions = ?,
                        last_accessed = ?
                    WHERE node_id = ?
                """,
                    [
                        json.dumps(existing.aliases),
                        json.dumps(existing.attributes),
                        existing.last_seen,
                        existing.mentions,
                        datetime.utcnow(),
                        existing.node_id,
                    ],
                )

                nodes.append(existing)

                logger.info(
                    "entity_updated",
                    extra={
                        "entity_id": existing.node_id,
                        "name": existing.name,
                        "mentions": existing.mentions,
                    },
                )
            else:
                # Create new entity
                entity.node_id = self.generate_id()
                entity.first_seen = timestamp
                entity.last_seen = timestamp
                entity.mentions = 1

                self._conn.execute(
                    """
                    INSERT INTO entities
                    (node_id, name, entity_type, aliases, attributes,
                     first_seen, last_seen, mentions, significance, created_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    [
                        entity.node_id,
                        entity.name,
                        entity.entity_type,
                        json.dumps(entity.aliases),
                        json.dumps(entity.attributes),
                        entity.first_seen,
                        entity.last_seen,
                        entity.mentions,
                        entity.significance,
                        entity.created_at,
                        entity.last_accessed,
                    ],
                )

                nodes.append(entity)

                logger.info(
                    "entity_created",
                    extra={
                        "entity_id": entity.node_id,
                        "name": entity.name,
                        "type": entity.entity_type,
                    },
                )

        return nodes

    async def query(
        self,
        query: str,
        k: int = 10,
        **kwargs: Any,
    ) -> list[EntityNode]:
        """
        Query entities by name or content search.

        Args:
            query: Search string.
            k: Maximum results.

        Returns:
            Matching entity nodes.
        """
        results = self._conn.execute(
            """
            SELECT * FROM entities
            WHERE LOWER(name) LIKE LOWER(?)
               OR LOWER(aliases) LIKE LOWER(?)
            ORDER BY mentions DESC, last_seen DESC
            LIMIT ?
        """,
            [f"%{query}%", f"%{query}%", k],
        ).fetchall()

        return [self._row_to_node(r) for r in results]

    async def query_entity(self, name: str) -> EntityNode | None:
        """Find an entity by name or alias."""
        results = await self.query(name, k=1)
        return results[0] if results else None

    async def query_relations(self, entity_id: str) -> list[EntityRelation]:
        """Get all relationships for an entity."""
        results = self._conn.execute(
            """
            SELECT * FROM entity_relations
            WHERE source_id = ? OR target_id = ?
            ORDER BY last_observed DESC
        """,
            [entity_id, entity_id],
        ).fetchall()

        return [self._row_to_relation(r) for r in results]

    async def add_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict[str, str] | None = None,
    ) -> EntityRelation:
        """Add a relationship between two entities."""
        import json

        # Check for existing relation
        existing = self._conn.execute(
            """
            SELECT * FROM entity_relations
            WHERE source_id = ? AND target_id = ? AND relation_type = ?
            LIMIT 1
        """,
            [source_id, target_id, relation_type],
        ).fetchone()

        if existing:
            # Update last observed
            self._conn.execute(
                """
                UPDATE entity_relations
                SET last_observed = ?, properties = ?
                WHERE relation_id = ?
            """,
                [
                    datetime.utcnow(),
                    json.dumps(properties or {}),
                    existing[0],
                ],
            )
            relation = self._row_to_relation(existing)
            relation.last_observed = datetime.utcnow()
            return relation

        # Create new relation
        relation = EntityRelation(
            relation_id=self.generate_id(),
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            properties=properties or {},
        )

        self._conn.execute(
            """
            INSERT INTO entity_relations
            (relation_id, source_id, target_id, relation_type, properties,
             first_observed, last_observed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            [
                relation.relation_id,
                relation.source_id,
                relation.target_id,
                relation.relation_type,
                json.dumps(relation.properties),
                relation.first_observed,
                relation.last_observed,
            ],
        )

        logger.info(
            "entity_relation_created",
            extra={
                "source_id": source_id,
                "target_id": target_id,
                "relation_type": relation_type,
            },
        )

        return relation

    async def query_path(
        self,
        from_entity: str,
        to_entity: str,
        max_hops: int = 4,
    ) -> list[tuple[EntityNode, EntityRelation, EntityNode]]:
        """
        Find relationship path between two entities.

        Example: "How does Jeremy know Hannah?"
        Returns: [(Jeremy, "friends_with", Sarah), (Sarah, "roommate_of", Hannah)]

        Args:
            from_entity: Starting entity name.
            to_entity: Target entity name.
            max_hops: Maximum path length.

        Returns:
            List of (source, relation, target) tuples forming the path.
        """
        from_node = await self.query_entity(from_entity)
        to_node = await self.query_entity(to_entity)

        if not from_node or not to_node:
            return []

        # BFS to find shortest path
        queue: list[tuple[str, list[tuple[str, str, str]]]] = [(from_node.node_id, [])]
        visited: set[str] = set()

        while queue:
            current_id, path = queue.pop(0)

            if current_id == to_node.node_id:
                # Found path - convert to full objects
                result = []
                for src_id, rel_type, tgt_id in path:
                    src = await self.get(src_id)
                    tgt = await self.get(tgt_id)
                    if src and tgt:
                        rel = EntityRelation(
                            relation_id="",
                            source_id=src_id,
                            target_id=tgt_id,
                            relation_type=rel_type,
                        )
                        result.append((src, rel, tgt))
                return result

            if current_id in visited or len(path) >= max_hops:
                continue

            visited.add(current_id)

            # Get all relations for current entity
            relations = await self.query_relations(current_id)
            for rel in relations:
                if rel.source_id == current_id:
                    next_id = rel.target_id
                else:
                    next_id = rel.source_id

                if next_id not in visited:
                    new_path = path + [(current_id, rel.relation_type, next_id)]
                    queue.append((next_id, new_path))

        return []

    async def query_mentioned(self, content: str) -> list[EntityNode]:
        """
        Find entities mentioned in content.

        Used by MemoryCortex for automatic context building.

        Args:
            content: Content to scan for entity mentions.

        Returns:
            Entities that appear to be mentioned.
        """
        # Get all entities and check for mentions
        all_entities = await self.get_all()

        mentioned = []
        content_lower = content.lower()

        for entity in all_entities:
            # Check name
            if entity.name.lower() in content_lower:
                mentioned.append(entity)
                continue

            # Check aliases
            for alias in entity.aliases:
                if alias.lower() in content_lower:
                    mentioned.append(entity)
                    break

        return mentioned

    async def merge_entities(self, entity_ids: list[str]) -> EntityNode | None:
        """
        Merge duplicate entities into one.

        Called when we discover multiple entities are actually the same.

        Args:
            entity_ids: List of entity IDs to merge.

        Returns:
            The merged entity.
        """

        if len(entity_ids) < 2:
            return None

        # Get all entities
        entities = []
        for eid in entity_ids:
            entity = await self.get(eid)
            if entity:
                entities.append(entity)

        if len(entities) < 2:
            return None

        # Keep the one with most mentions as primary
        entities.sort(key=lambda e: e.mentions, reverse=True)
        primary = entities[0]

        # Merge others into primary
        for entity in entities[1:]:
            # Merge aliases
            for alias in entity.aliases:
                if alias not in primary.aliases:
                    primary.aliases.append(alias)

            # Add name as alias
            if entity.name not in primary.aliases and entity.name != primary.name:
                primary.aliases.append(entity.name)

            # Merge attributes
            primary.attributes.update(entity.attributes)

            # Sum mentions
            primary.mentions += entity.mentions

            # Use earliest first_seen
            primary.first_seen = min(primary.first_seen, entity.first_seen)

            # Use latest last_seen
            primary.last_seen = max(primary.last_seen, entity.last_seen)

            # Update relations to point to primary
            self._conn.execute(
                """
                UPDATE entity_relations
                SET source_id = ?
                WHERE source_id = ?
            """,
                [primary.node_id, entity.node_id],
            )

            self._conn.execute(
                """
                UPDATE entity_relations
                SET target_id = ?
                WHERE target_id = ?
            """,
                [primary.node_id, entity.node_id],
            )

            # Delete merged entity
            await self.delete(entity.node_id)

        # Update primary
        await self.update(primary)

        logger.info(
            "entities_merged",
            extra={
                "primary_id": primary.node_id,
                "merged_count": len(entities) - 1,
            },
        )

        return primary

    async def get(self, node_id: str) -> EntityNode | None:
        """Get a specific entity by ID."""
        result = self._conn.execute(
            """
            SELECT * FROM entities WHERE node_id = ?
        """,
            [node_id],
        ).fetchone()

        if result:
            self._conn.execute(
                """
                UPDATE entities SET last_accessed = ? WHERE node_id = ?
            """,
                [datetime.utcnow(), node_id],
            )
            return self._row_to_node(result)
        return None

    async def get_all(self) -> list[EntityNode]:
        """Get all entities in the graph."""
        results = self._conn.execute("""
            SELECT * FROM entities ORDER BY mentions DESC, last_seen DESC
        """).fetchall()
        return [self._row_to_node(r) for r in results]

    async def update(self, node: EntityNode) -> None:
        """Update an existing entity."""
        import json

        self._conn.execute(
            """
            UPDATE entities SET
                name = ?,
                entity_type = ?,
                aliases = ?,
                attributes = ?,
                first_seen = ?,
                last_seen = ?,
                mentions = ?,
                significance = ?,
                last_accessed = ?
            WHERE node_id = ?
        """,
            [
                node.name,
                node.entity_type,
                json.dumps(node.aliases),
                json.dumps(node.attributes),
                node.first_seen,
                node.last_seen,
                node.mentions,
                node.significance,
                datetime.utcnow(),
                node.node_id,
            ],
        )

    async def delete(self, node_id: str) -> None:
        """Delete an entity and its relations from the graph."""
        # Delete relations first
        self._conn.execute(
            """
            DELETE FROM entity_relations WHERE source_id = ? OR target_id = ?
        """,
            [node_id, node_id],
        )

        # Delete entity
        self._conn.execute(
            """
            DELETE FROM entities WHERE node_id = ?
        """,
            [node_id],
        )

    async def archive(self, node: EntityNode) -> None:
        """Archive an entity (move to cold storage)."""
        logger.info(
            "entity_archived",
            extra={"node_id": node.node_id, "name": node.name},
        )
        await self.delete(node.node_id)
