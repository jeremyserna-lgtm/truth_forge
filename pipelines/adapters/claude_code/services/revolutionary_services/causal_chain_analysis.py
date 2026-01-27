"""Causal Chain Analysis Service

Analyzes causal relationships between entities using event sourcing
and causal chains.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

from shared.revolutionary_features import EVENT_STORE_TABLE
from shared.constants import PROJECT_ID, DATASET_ID


class CausalChainAnalysis:
    """Service for analyzing causal relationships."""
    
    def __init__(self, client: bigquery.Client = None):
        """Initialize Causal Chain Analysis Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
    
    def get_causal_chain(
        self,
        entity_id: str,
    ) -> List[Dict[str, Any]]:
        """Get complete causal chain for an entity.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            List of events in causal chain
        """
        query = f"""
        SELECT *
        FROM `{EVENT_STORE_TABLE}`
        WHERE entity_id = '{entity_id}'
        ORDER BY event_timestamp ASC
        """
        
        result = list(self.client.query(query).result())
        events = [dict(row) for row in result]
        
        # Build causal chain
        causal_chain = []
        for event in events:
            causal_chain_ids = event.get("causal_chain", [])
            for chain_id in causal_chain_ids:
                # Get the event that caused this
                cause_query = f"""
                SELECT *
                FROM `{EVENT_STORE_TABLE}`
                WHERE event_id = '{chain_id}'
                """
                cause_result = list(self.client.query(cause_query).result())
                if cause_result:
                    causal_chain.append(dict(cause_result[0]))
        
        return causal_chain
    
    def find_causal_relationships(
        self,
        source_entity_id: str,
        target_entity_id: str,
    ) -> List[Dict[str, Any]]:
        """Find causal relationships between two entities.
        
        Args:
            source_entity_id: Source entity ID
            target_entity_id: Target entity ID
        
        Returns:
            List of causal relationships
        """
        # Get events for both entities
        source_events = self.get_causal_chain(source_entity_id)
        target_events = self.get_causal_chain(target_entity_id)
        
        # Find relationships
        relationships = []
        
        for target_event in target_events:
            causal_chain = target_event.get("causal_chain", [])
            for source_event in source_events:
                if source_event.get("event_id") in causal_chain:
                    relationships.append({
                        "source_event": source_event,
                        "target_event": target_event,
                        "relationship_type": "CAUSES",
                    })
        
        return relationships
    
    def analyze_causal_network(
        self,
        entity_ids: List[str],
    ) -> Dict[str, Any]:
        """Analyze causal network for multiple entities.
        
        Args:
            entity_ids: List of entity IDs
        
        Returns:
            Causal network analysis
        """
        network = {
            "entities": {},
            "relationships": [],
        }
        
        # Get causal chains for all entities
        for entity_id in entity_ids:
            network["entities"][entity_id] = self.get_causal_chain(entity_id)
        
        # Find relationships
        for i, source_id in enumerate(entity_ids):
            for target_id in entity_ids[i+1:]:
                relationships = self.find_causal_relationships(source_id, target_id)
                network["relationships"].extend(relationships)
        
        return network
