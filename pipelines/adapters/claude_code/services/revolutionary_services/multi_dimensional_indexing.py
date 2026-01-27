"""Multi-Dimensional Indexing Utilities

Enables indexing and querying across multiple dimensions:
- Spatial (position in conversation)
- Temporal (time)
- Semantic (meaning/embeddings)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from google.cloud import bigquery

from shared.constants import PROJECT_ID, DATASET_ID


MULTI_DIM_INDEX_TABLE = f"{PROJECT_ID}.{DATASET_ID}.multi_dimensional_index"

MULTI_DIM_INDEX_SCHEMA = [
    bigquery.SchemaField("index_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("entity_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("level", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("spatial_index", "STRING", mode="REPEATED"),  # Position coordinates
    bigquery.SchemaField("temporal_index", "STRING", mode="REPEATED"),  # Time coordinates
    bigquery.SchemaField("semantic_index", "STRING", mode="REPEATED"),  # Embedding vector (as strings)
    bigquery.SchemaField("composite_hash", "STRING", mode="REQUIRED"),  # Hash of all dimensions
    bigquery.SchemaField("metadata", "JSON"),
    bigquery.SchemaField("created_at", "TIMESTAMP", mode="REQUIRED"),
]


class MultiDimensionalIndexing:
    """Service for multi-dimensional indexing."""
    
    def __init__(self, client: bigquery.Client = None):
        """Initialize Multi-Dimensional Indexing Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
        self._ensure_table()
    
    def _ensure_table(self):
        """Ensure multi-dimensional index table exists."""
        table_ref = bigquery.Table(MULTI_DIM_INDEX_TABLE, schema=MULTI_DIM_INDEX_SCHEMA)
        table_ref.clustering_fields = ["level", "entity_id"]
        
        try:
            self.client.create_table(table_ref, exists_ok=True)
        except Exception:
            pass  # Table may already exist
    
    def calculate_spatial_index(
        self,
        conversation_id: str,
        turn_index: Optional[int] = None,
        message_index: Optional[int] = None,
        sentence_index: Optional[int] = None,
        word_index: Optional[int] = None,
    ) -> List[str]:
        """Calculate spatial index (position in conversation).
        
        Args:
            conversation_id: Conversation ID
            turn_index: Turn index (optional)
            message_index: Message index (optional)
            sentence_index: Sentence index (optional)
            word_index: Word index (optional)
        
        Returns:
            Spatial index as list of coordinates
        """
        # Normalize to 0-1 range for efficient indexing
        # This is a simplified version - can be enhanced
        
        spatial = [conversation_id]
        
        if turn_index is not None:
            spatial.append(f"turn_{turn_index}")
        if message_index is not None:
            spatial.append(f"msg_{message_index}")
        if sentence_index is not None:
            spatial.append(f"sent_{sentence_index}")
        if word_index is not None:
            spatial.append(f"word_{word_index}")
        
        return spatial
    
    def calculate_temporal_index(
        self,
        timestamp: datetime,
    ) -> List[str]:
        """Calculate temporal index (time coordinates).
        
        Args:
            timestamp: Timestamp
        
        Returns:
            Temporal index as list of coordinates
        """
        return [
            str(timestamp.year),
            str(timestamp.month),
            str(timestamp.day),
            str(timestamp.hour),
            str(timestamp.minute),
            str(timestamp.second),
        ]
    
    def calculate_semantic_index(
        self,
        embedding: Optional[List[float]] = None,
        text: Optional[str] = None,
    ) -> List[str]:
        """Calculate semantic index (meaning/embeddings).
        
        Args:
            embedding: Embedding vector (optional)
            text: Text to hash if no embedding (optional)
        
        Returns:
            Semantic index as list of strings
        """
        if embedding:
            # Convert embedding to strings (first 10 dimensions for indexing)
            return [str(v) for v in embedding[:10]]
        elif text:
            # Hash text for semantic similarity
            hash_value = hashlib.sha256(text.encode()).hexdigest()
            return [hash_value[:8], hash_value[8:16], hash_value[16:24]]
        else:
            return []
    
    def index_entity(
        self,
        entity_id: str,
        level: int,
        spatial_index: List[str],
        temporal_index: List[str],
        semantic_index: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Index an entity across multiple dimensions.
        
        Args:
            entity_id: Entity ID
            level: Entity level (L2-L8)
            spatial_index: Spatial coordinates
            temporal_index: Temporal coordinates
            semantic_index: Semantic coordinates
            metadata: Additional metadata
        
        Returns:
            index_id
        """
        from datetime import timezone
        
        # Calculate composite hash
        composite = json.dumps({
            "spatial": spatial_index,
            "temporal": temporal_index,
            "semantic": semantic_index,
        }, sort_keys=True)
        composite_hash = hashlib.sha256(composite.encode()).hexdigest()
        
        index_id = f"idx_{composite_hash[:16]}"
        
        index_record = {
            "index_id": index_id,
            "entity_id": entity_id,
            "level": level,
            "spatial_index": spatial_index,
            "temporal_index": temporal_index,
            "semantic_index": semantic_index,
            "composite_hash": composite_hash,
            "metadata": json.dumps(metadata or {}),
            "created_at": datetime.now(timezone.utc),
        }
        
        from src.services.central_services.core.bigquery_client import get_bigquery_client
        bq_client = get_bigquery_client()
        bq_client.load_rows_to_table(MULTI_DIM_INDEX_TABLE, [index_record])
        
        return index_id
    
    def query_multi_dimensional(
        self,
        spatial_filters: Optional[List[str]] = None,
        temporal_filters: Optional[List[str]] = None,
        semantic_filters: Optional[List[str]] = None,
        level: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Query across multiple dimensions.
        
        Args:
            spatial_filters: Spatial filter conditions
            temporal_filters: Temporal filter conditions
            semantic_filters: Semantic filter conditions
            level: Entity level filter (optional)
        
        Returns:
            List of matching entities
        """
        filters = []
        
        if spatial_filters:
            for i, filter_val in enumerate(spatial_filters):
                filters.append(f"'{filter_val}' IN UNNEST(spatial_index)")
        
        if temporal_filters:
            for i, filter_val in enumerate(temporal_filters):
                filters.append(f"'{filter_val}' IN UNNEST(temporal_index)")
        
        if semantic_filters:
            for i, filter_val in enumerate(semantic_filters):
                filters.append(f"'{filter_val}' IN UNNEST(semantic_index)")
        
        if level:
            filters.append(f"level = {level}")
        
        if not filters:
            return []
        
        query = f"""
        SELECT *
        FROM `{MULTI_DIM_INDEX_TABLE}`
        WHERE {' AND '.join(filters)}
        ORDER BY composite_hash
        """
        
        result = list(self.client.query(query).result())
        return [dict(row) for row in result]
