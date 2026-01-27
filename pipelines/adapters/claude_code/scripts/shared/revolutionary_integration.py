"""Revolutionary Features Integration Helper

This module provides helper functions to integrate revolutionary features
into pipeline stages with minimal code changes.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from google.cloud import bigquery

from shared.revolutionary_features import (
    add_bitemporal_to_record,
    record_event,
    record_provenance,
    ensure_event_store_table,
    ensure_provenance_table,
    calculate_data_hash,
)
from shared.constants import PIPELINE_NAME, SOURCE_NAME


def integrate_revolutionary_features(
    client: bigquery.Client,
    entity_id: str,
    record: Dict[str, Any],
    stage: int,
    run_id: str,
    valid_time: datetime,
    input_data: Optional[Dict[str, Any]] = None,
    transformation: Optional[str] = None,
    transformation_params: Optional[Dict[str, Any]] = None,
    parent_provenance_id: Optional[str] = None,
    previous_event_id: Optional[str] = None,
    causal_chain: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    logger=None,
) -> Dict[str, Any]:
    """Integrate all revolutionary features into a record.
    
    This function:
    1. Adds bitemporal fields to the record
    2. Records an event in the event store
    3. Records provenance with cryptographic hashing
    
    Args:
        client: BigQuery client
        entity_id: Entity ID
        record: Record dictionary (will be modified)
        stage: Pipeline stage number
        run_id: Current run ID
        valid_time: When data actually occurred
        input_data: Input data for provenance (optional)
        transformation: Transformation description (optional)
        transformation_params: Transformation parameters (optional)
        parent_provenance_id: Parent provenance ID (optional)
        previous_event_id: Previous event ID (optional)
        causal_chain: Causal chain list (optional)
        metadata: Additional metadata (optional)
        logger: Logger instance (optional)
    
    Returns:
        Dictionary with event_id and provenance_id
    """
    system_time = datetime.now(timezone.utc)
    result = {"event_id": None, "provenance_id": None}
    
    # 1. Add bitemporal fields
    record = add_bitemporal_to_record(record, valid_time=valid_time, system_time=system_time)
    
    # 2. Record event
    try:
        ensure_event_store_table(client)
        event_id = record_event(
            client=client,
            entity_id=entity_id,
            event_type="CREATED",
            event_data=record.copy(),  # Copy to avoid modification
            stage=stage,
            run_id=run_id,
            previous_event_id=previous_event_id,
            causal_chain=causal_chain or [],
            metadata={
                **(metadata or {}),
                "pipeline": PIPELINE_NAME,
                "source": SOURCE_NAME,
            },
        )
        result["event_id"] = event_id
        if logger:
            logger.debug("event_recorded", entity_id=entity_id, event_id=event_id, stage=stage)
    except Exception as e:
        if logger:
            logger.warning("event_recording_failed", entity_id=entity_id, error=str(e), stage=stage)
        # Don't fail pipeline if event recording fails
    
    # 3. Record provenance
    try:
        ensure_provenance_table(client)
        if input_data is None:
            # Use minimal input data if not provided
            input_data = {
                "entity_id": entity_id,
                "stage": stage,
            }
        
        if transformation is None:
            transformation = f"stage_{stage}_processing"
        
        provenance_id = record_provenance(
            client=client,
            entity_id=entity_id,
            stage=stage,
            input_data=input_data,
            output_data=record.copy(),  # Copy to avoid modification
            transformation=transformation,
            transformation_params=transformation_params or {},
            parent_provenance_id=parent_provenance_id,
            run_id=run_id,
        )
        result["provenance_id"] = provenance_id
        if logger:
            logger.debug("provenance_recorded", entity_id=entity_id, provenance_id=provenance_id, stage=stage)
    except Exception as e:
        if logger:
            logger.warning("provenance_recording_failed", entity_id=entity_id, error=str(e), stage=stage)
        # Don't fail pipeline if provenance recording fails
    
    return result


def get_valid_time_from_record(record: Dict[str, Any]) -> datetime:
    """Extract valid_time from record, with fallback.
    
    Tries to find a timestamp field in the record that represents
    when the data actually occurred.
    
    Args:
        record: Record dictionary
    
    Returns:
        Valid time datetime
    """
    # Try various timestamp fields
    timestamp_fields = [
        "source_message_timestamp",
        "timestamp_utc",
        "first_message_time",
        "last_message_time",
        "created_at",
        "valid_time",  # Already has it
    ]
    
    for field in timestamp_fields:
        if field in record and record[field]:
            value = record[field]
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    continue
    
    # Fallback to now
    return datetime.now(timezone.utc)


def build_input_data_for_provenance(
    record: Dict[str, Any],
    source_fields: List[str],
) -> Dict[str, Any]:
    """Build input data dictionary for provenance tracking.
    
    Extracts specified fields from record to create input data.
    
    Args:
        record: Record dictionary
        source_fields: List of field names to extract
    
    Returns:
        Input data dictionary
    """
    input_data = {}
    for field in source_fields:
        if field in record:
            input_data[field] = record[field]
    return input_data
