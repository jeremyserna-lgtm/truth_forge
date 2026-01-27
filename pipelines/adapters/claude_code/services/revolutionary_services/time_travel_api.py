"""Time-Travel Query API Service

Provides API endpoints for querying data at any point in time using
bitemporal time-travel queries.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

from shared.revolutionary_features import generate_time_travel_query
from shared.constants import PROJECT_ID, DATASET_ID


class TimeTravelAPI:
    """API for time-travel queries across the pipeline."""
    
    def __init__(self, client: Optional[bigquery.Client] = None):
        """Initialize Time-Travel API.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
        self.dataset_id = DATASET_ID
    
    def query_conversation_at_time(
        self,
        conversation_id: str,
        valid_time: datetime,
        system_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Query conversation as it existed at a specific time.
        
        Args:
            conversation_id: Conversation ID
            valid_time: Point in time to query (valid time)
            system_time: Point in pipeline processing time (optional)
        
        Returns:
            Conversation data at that time
        """
        table = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_5"
        
        query = generate_time_travel_query(
            table=table,
            valid_time=valid_time,
            system_time=system_time,
            additional_filters={"conversation_id": conversation_id},
        )
        
        result = list(self.client.query(query).result())
        
        if result:
            return dict(result[0])
        return {}
    
    def query_turn_at_time(
        self,
        turn_id: str,
        valid_time: datetime,
        system_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Query turn as it existed at a specific time.
        
        Args:
            turn_id: Turn ID
            valid_time: Point in time to query
            system_time: Point in pipeline processing time (optional)
        
        Returns:
            Turn data at that time
        """
        table = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_6"
        
        query = generate_time_travel_query(
            table=table,
            valid_time=valid_time,
            system_time=system_time,
            additional_filters={"turn_id": turn_id},
        )
        
        result = list(self.client.query(query).result())
        
        if result:
            return dict(result[0])
        return {}
    
    def query_message_at_time(
        self,
        message_id: str,
        valid_time: datetime,
        system_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Query message as it existed at a specific time.
        
        Args:
            message_id: Message ID
            valid_time: Point in time to query
            system_time: Point in pipeline processing time (optional)
        
        Returns:
            Message data at that time
        """
        table = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_7"
        
        query = generate_time_travel_query(
            table=table,
            valid_time=valid_time,
            system_time=system_time,
            additional_filters={"message_id": message_id},
        )
        
        result = list(self.client.query(query).result())
        
        if result:
            return dict(result[0])
        return {}
    
    def query_entity_at_time(
        self,
        table_name: str,
        entity_id: str,
        valid_time: datetime,
        system_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Query any entity at a specific time.
        
        Args:
            table_name: Table name (e.g., "claude_code_stage_8")
            entity_id: Entity ID
            valid_time: Point in time to query
            system_time: Point in pipeline processing time (optional)
        
        Returns:
            Entity data at that time
        """
        table = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        
        query = generate_time_travel_query(
            table=table,
            valid_time=valid_time,
            system_time=system_time,
            additional_filters={"entity_id": entity_id},
        )
        
        result = list(self.client.query(query).result())
        
        if result:
            return dict(result[0])
        return {}
    
    def query_conversation_history(
        self,
        conversation_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """Query conversation history across time.
        
        Args:
            conversation_id: Conversation ID
            start_time: Start of time range (optional)
            end_time: End of time range (optional)
        
        Returns:
            List of conversation states across time
        """
        table = f"{PROJECT_ID}.{DATASET_ID}.claude_code_stage_5"
        
        filters = [f"conversation_id = '{conversation_id}'"]
        
        if start_time:
            filters.append(f"valid_time >= TIMESTAMP('{start_time.isoformat()}')")
        if end_time:
            filters.append(f"valid_time <= TIMESTAMP('{end_time.isoformat()}')")
        
        query = f"""
        SELECT *
        FROM `{table}`
        WHERE {' AND '.join(filters)}
        ORDER BY valid_time ASC, system_time ASC
        """
        
        result = list(self.client.query(query).result())
        return [dict(row) for row in result]
