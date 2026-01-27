"""Knowledge Graph Service

Builds and queries knowledge graphs of entity relationships,
enabling relationship discovery and graph-based queries.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import bigquery

from shared.constants import PROJECT_ID, DATASET_ID


KNOWLEDGE_GRAPH_TABLE = f"{PROJECT_ID}.{DATASET_ID}.knowledge_graph_relationships"

KNOWLEDGE_GRAPH_SCHEMA = [
    bigquery.SchemaField("relationship_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("target_entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("relationship_type", "STRING", mode="REQUIRED"),  # REPLIES_TO, REFERENCES, QUOTES, etc.
    bigquery.SchemaField("relationship_strength", "FLOAT"),  # 0.0-1.0 confidence
    bigquery.SchemaField("discovered_by", "STRING", mode="REQUIRED"),  # llm_analysis, pattern_matching, user_annotation
    bigquery.SchemaField("confidence", "FLOAT"),  # 0.0-1.0
    bigquery.SchemaField("metadata", "JSON"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("run_id", "STRING", mode="REQUIRED"),
]


class KnowledgeGraphService:
    """Service for building and querying knowledge graphs."""
    
    def __init__(self, client: bigquery.Client = None):
        """Initialize Knowledge Graph Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure knowledge graph table exists."""
        table_ref = bigquery.Table(KNOWLEDGE_GRAPH_TABLE, schema=KNOWLEDGE_GRAPH_SCHEMA)
        table_ref.clustering_fields = ["source_entity_id", "relationship_type"]
        
        try:
            self.client.create_table(table_ref, exists_ok=True)
        except Exception:
            pass  # Table may already exist
    
    def add_relationship(
        self,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        relationship_strength: float = 1.0,
        discovered_by: str = "pattern_matching",
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        run_id: str = "unknown",
    ) -> str:
        """Add a relationship to the knowledge graph.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            relationship_type: Type of relationship
            relationship_strength: Strength of relationship (0.0-1.0)
            discovered_by: How relationship was discovered
            confidence: Confidence in relationship (0.0-1.0)
            metadata: Additional metadata
            run_id: Current run ID
        
        Returns:
            relationship_id
        """
        from datetime import datetime, timezone
        import hashlib
        
        # Generate relationship ID
        content = f"rel:{source_entity_id}:{target_entity_id}:{relationship_type}"
        hash_value = hashlib.sha256(content.encode()).hexdigest()[:16]
        relationship_id = f"rel_{hash_value}"
        
        relationship = {
            "relationship_id": relationship_id,
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relationship_type": relationship_type,
            "relationship_strength": relationship_strength,
            "discovered_by": discovered_by,
            "confidence": confidence,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.now(timezone.utc),
            "run_id": run_id,
        }
        
        from src.services.central_services.core.bigquery_client import get_bigquery_client
        bq_client = get_bigquery_client()
        bq_client.load_rows_to_table(KNOWLEDGE_GRAPH_TABLE, [relationship])
        
        return relationship_id
    
    def get_relationships(
        self,
        entity_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",  # "outgoing", "incoming", "both"
    ) -> List[Dict[str, Any]]:
        """Get relationships for an entity.
        
        Args:
            entity_id: Entity ID
            relationship_type: Filter by relationship type (optional)
            direction: Direction of relationships
        
        Returns:
            List of relationships
        """
        filters = []
        
        if direction == "outgoing":
            filters.append(f"source_entity_id = '{entity_id}'")
        elif direction == "incoming":
            filters.append(f"target_entity_id = '{entity_id}'")
        else:  # both
            filters.append(f"(source_entity_id = '{entity_id}' OR target_entity_id = '{entity_id}')")
        
        if relationship_type:
            filters.append(f"relationship_type = '{relationship_type}'")
        
        query = f"""
        SELECT *
        FROM `{KNOWLEDGE_GRAPH_TABLE}`
        WHERE {' AND '.join(filters)}
        ORDER BY relationship_strength DESC, confidence DESC
        """
        
        result = list(self.client.query(query).result())
        return [dict(row) for row in result]
    
    def find_path(
        self,
        source_entity_id: str,
        target_entity_id: str,
        max_depth: int = 3,
    ) -> List[Dict[str, Any]]:
        """Find path between two entities.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
            max_depth: Maximum path depth
        
        Returns:
            List of relationships forming the path
        """
        # Simple BFS path finding (can be optimized)
        visited = set()
        queue = [(source_entity_id, [])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == target_entity_id:
                return path
            
            if len(path) >= max_depth:
                continue
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Get outgoing relationships
            relationships = self.get_relationships(current_id, direction="outgoing")
            
            for rel in relationships:
                next_id = rel["target_entity_id"]
                if next_id not in visited:
                    queue.append((next_id, path + [rel]))
        
        return []  # No path found
    
    def discover_reply_relationships(
        self,
        conversation_id: str,
    ) -> List[str]:
        """Discover reply relationships in a conversation.
        
        Args:
            conversation_id: Conversation ID
        
        Returns:
            List of relationship IDs created
        """
        # Query messages in conversation ordered by timestamp
        query = f"""
        SELECT entity_id, message_index, role, timestamp_utc
        FROM `{PROJECT_ID}.{DATASET_ID}.claude_code_stage_7`
        WHERE conversation_id = '{conversation_id}'
        ORDER BY timestamp_utc ASC, message_index ASC
        """
        
        messages = list(self.client.query(query).result())
        relationship_ids = []
        
        # Find reply relationships (assistant replies to user, user replies to assistant)
        for i in range(len(messages) - 1):
            current = messages[i]
            next_msg = messages[i + 1]
            
            # Assistant replies to user
            if current.role == "user" and next_msg.role == "assistant":
                rel_id = self.add_relationship(
                    source_entity_id=current.entity_id,
                    target_entity_id=next_msg.entity_id,
                    relationship_type="REPLIES_TO",
                    relationship_strength=1.0,
                    discovered_by="pattern_matching",
                    confidence=1.0,
                    metadata={
                        "conversation_id": conversation_id,
                        "pattern": "assistant_replies_to_user",
                    },
                )
                relationship_ids.append(rel_id)
            
            # User replies to assistant (continuing conversation)
            elif current.role == "assistant" and next_msg.role == "user":
                rel_id = self.add_relationship(
                    source_entity_id=current.entity_id,
                    target_entity_id=next_msg.entity_id,
                    relationship_type="CONTINUES",
                    relationship_strength=0.8,
                    discovered_by="pattern_matching",
                    confidence=0.9,
                    metadata={
                        "conversation_id": conversation_id,
                        "pattern": "user_continues_conversation",
                    },
                )
                relationship_ids.append(rel_id)
        
        return relationship_ids
