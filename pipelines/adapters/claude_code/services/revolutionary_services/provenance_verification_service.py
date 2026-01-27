"""Provenance Verification Service

Verifies data integrity by checking cryptographic provenance chains.
"""
from __future__ import annotations

from typing import Any, Dict, List

from google.cloud import bigquery

from shared.revolutionary_features import (
    verify_provenance_chain,
    PROVENANCE_TABLE,
)
from shared.constants import PROJECT_ID, DATASET_ID


class ProvenanceVerificationService:
    """Service for verifying data provenance and integrity."""
    
    def __init__(self, client: bigquery.Client = None):
        """Initialize Provenance Verification Service.
        
        Args:
            client: BigQuery client (creates new if None)
        """
        self.client = client or bigquery.Client(project=PROJECT_ID)
    
    def verify_entity_provenance(
        self,
        entity_id: str,
    ) -> Dict[str, Any]:
        """Verify complete provenance chain for an entity.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            Verification report
        """
        return verify_provenance_chain(
            client=self.client,
            entity_id=entity_id,
        )
    
    def get_provenance_chain(
        self,
        entity_id: str,
    ) -> List[Dict[str, Any]]:
        """Get complete provenance chain for an entity.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            List of provenance records in order
        """
        query = f"""
        SELECT *
        FROM `{PROVENANCE_TABLE}`
        WHERE entity_id = '{entity_id}'
        ORDER BY stage ASC
        """
        
        result = list(self.client.query(query).result())
        return [dict(row) for row in result]
    
    def verify_batch_provenance(
        self,
        entity_ids: List[str],
    ) -> Dict[str, Dict[str, Any]]:
        """Verify provenance for multiple entities.
        
        Args:
            entity_ids: List of entity IDs
        
        Returns:
            Dictionary mapping entity_id to verification report
        """
        results = {}
        
        for entity_id in entity_ids:
            results[entity_id] = self.verify_entity_provenance(entity_id)
        
        return results
    
    def get_failed_verifications(
        self,
        entity_ids: List[str],
    ) -> List[str]:
        """Get list of entities with failed verifications.
        
        Args:
            entity_ids: List of entity IDs
        
        Returns:
            List of entity IDs with failed verifications
        """
        results = self.verify_batch_provenance(entity_ids)
        
        failed = []
        for entity_id, report in results.items():
            if not report.get("verified", False):
                failed.append(entity_id)
        
        return failed
