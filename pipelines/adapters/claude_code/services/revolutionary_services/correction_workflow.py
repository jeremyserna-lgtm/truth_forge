"""Correction Workflow Service

Enables corrections to entities using bitemporal features,
preserving history while allowing corrections.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from google.cloud import bigquery

from shared.revolutionary_features import (
    record_event,
    ensure_event_store_table,
)
from shared.constants import PROJECT_ID, DATASET_ID


class CorrectionWorkflow:
    """Service for correcting entities while preserving history."""
    
    def __init__(self, client: bigquery.Client = None):
        """Initialize Correction Workflow Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
    
    def correct_entity(
        self,
        table_name: str,
        entity_id: str,
        corrected_data: Dict[str, Any],
        correction_reason: str,
        run_id: str,
        logger=None,
    ) -> Dict[str, Any]:
        """Correct an entity by ending current version and creating new one.
        
        This preserves history while allowing corrections.
        
        Args:
            table_name: Table name (e.g., "claude_code_stage_7")
            entity_id: Entity ID to correct
            corrected_data: Corrected data
            correction_reason: Reason for correction
            run_id: Current run ID
            logger: Logger instance (optional)
        
        Returns:
            Dictionary with correction details
        """
        now = datetime.now(timezone.utc)
        full_table = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        
        # Get current version
        current_query = f"""
        SELECT *
        FROM `{full_table}`
        WHERE entity_id = '{entity_id}'
          AND system_time_end IS NULL
        LIMIT 1
        """
        
        current_result = list(self.client.query(current_query).result())
        
        if not current_result:
            raise ValueError(f"Entity {entity_id} not found in {table_name}")
        
        current = dict(current_result[0])
        
        # End current version
        update_query = f"""
        UPDATE `{full_table}`
        SET system_time_end = TIMESTAMP('{now.isoformat()}')
        WHERE entity_id = '{entity_id}'
          AND system_time_end IS NULL
        """
        
        self.client.query(update_query).result()
        
        # Create corrected version
        corrected_record = {
            **current,  # Start with current data
            **corrected_data,  # Apply corrections
            "entity_id": entity_id,  # Same entity_id
            "system_time": now,  # New system time
            "valid_time": current.get("valid_time"),  # Same valid time
            "system_time_end": None,  # Current until superseded
            "valid_time_end": None,  # Still valid
        }
        
        # Add correction metadata
        metadata = json.loads(corrected_record.get("metadata", "{}"))
        metadata["corrections"] = metadata.get("corrections", []) + [{
            "corrected_at": now.isoformat(),
            "reason": correction_reason,
            "previous_system_time": current.get("system_time").isoformat() if current.get("system_time") else None,
        }]
        corrected_record["metadata"] = json.dumps(metadata)
        
        # Insert corrected version
        from src.services.central_services.core.bigquery_client import get_bigquery_client
        bq_client = get_bigquery_client()
        bq_client.load_rows_to_table(full_table, [corrected_record])
        
        # Record correction event
        try:
            ensure_event_store_table(self.client)
            event_id = record_event(
                client=self.client,
                entity_id=entity_id,
                event_type="CORRECTED",
                event_data=corrected_record,
                stage=0,  # Correction stage
                run_id=run_id,
                previous_event_id=None,  # Will be linked automatically
                causal_chain=[],
                metadata={
                    "correction_reason": correction_reason,
                    "table": table_name,
                },
            )
            
            if logger:
                logger.info("entity_corrected", entity_id=entity_id, event_id=event_id, reason=correction_reason)
        except Exception as e:
            if logger:
                logger.warning("correction_event_failed", entity_id=entity_id, error=str(e))
        
        return {
            "entity_id": entity_id,
            "corrected_at": now.isoformat(),
            "correction_reason": correction_reason,
            "previous_system_time": current.get("system_time").isoformat() if current.get("system_time") else None,
            "new_system_time": now.isoformat(),
        }
    
    def get_correction_history(
        self,
        entity_id: str,
    ) -> List[Dict[str, Any]]:
        """Get correction history for an entity.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            List of corrections
        """
        from shared.revolutionary_features import EVENT_STORE_TABLE
        
        query = f"""
        SELECT *
        FROM `{EVENT_STORE_TABLE}`
        WHERE entity_id = '{entity_id}'
          AND event_type = 'CORRECTED'
        ORDER BY event_timestamp ASC
        """
        
        result = list(self.client.query(query).result())
        return [dict(row) for row in result]
