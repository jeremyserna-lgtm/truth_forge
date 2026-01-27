"""State Reconstruction Service

Reconstructs entity state at any point in time by replaying events
from the event store.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

from shared.revolutionary_features import (
    reconstruct_entity_state,
    EVENT_STORE_TABLE,
)
from shared.constants import PROJECT_ID, DATASET_ID


class StateReconstructionService:
    """Service for reconstructing entity state from events."""
    
    def __init__(self, client: Optional[bigquery.Client] = None):
        """Initialize State Reconstruction Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
    
    def reconstruct_entity(
        self,
        entity_id: str,
        at_timestamp: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """Reconstruct entity state by replaying events.
        
        Args:
            entity_id: Entity ID
            at_timestamp: Reconstruct state at this time (None = latest)
        
        Returns:
            Entity state dictionary, or None if deleted
        """
        return reconstruct_entity_state(
            client=self.client,
            entity_id=entity_id,
            at_timestamp=at_timestamp,
        )
    
    def get_entity_event_history(
        self,
        entity_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Get complete event history for an entity.
        
        Args:
            entity_id: Entity ID
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
        
        Returns:
            List of events in chronological order
        """
        filters = [f"entity_id = '{entity_id}'"]
        
        if start_time:
            filters.append(f"event_timestamp >= TIMESTAMP('{start_time.isoformat()}')")
        if end_time:
            filters.append(f"event_timestamp <= TIMESTAMP('{end_time.isoformat()}')")
        
        query = f"""
        SELECT *
        FROM `{EVENT_STORE_TABLE}`
        WHERE {' AND '.join(filters)}
        ORDER BY event_timestamp ASC
        """
        
        result = list(self.client.query(query).result())
        return [dict(row) for row in result]
    
    def replay_events_to_state(
        self,
        events: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Replay events to reconstruct state.
        
        Args:
            events: List of events in chronological order
        
        Returns:
            Final state after replaying events
        """
        state = None
        
        for event in events:
            event_data = json.loads(event.get("event_data", "{}"))
            event_type = event.get("event_type")
            
            if event_type == "CREATED":
                state = event_data
            elif event_type == "UPDATED":
                if state is None:
                    state = {}
                state.update(event_data)
            elif event_type == "CORRECTED":
                # Correction replaces state
                state = event_data
            elif event_type == "DELETED":
                state = None
                break
        
        return state
    
    def get_causal_chain(
        self,
        entity_id: str,
    ) -> List[str]:
        """Get causal chain for an entity.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            List of event IDs in causal chain
        """
        query = f"""
        SELECT causal_chain
        FROM `{EVENT_STORE_TABLE}`
        WHERE entity_id = '{entity_id}'
        ORDER BY event_timestamp DESC
        LIMIT 1
        """
        
        result = list(self.client.query(query).result())
        
        if result:
            return result[0].causal_chain or []
        return []
