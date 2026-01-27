"""Conflict resolution service for multi-source contact sync."""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Resolves conflicts between contact records from different sources.
    
    Uses last-write-wins strategy with version control:
    1. Higher version wins
    2. If versions equal, later timestamp wins
    3. If both equal, manual resolution required
    """

    def __init__(self, bq_client: Any) -> None:
        """Initialize conflict resolver.
        
        Args:
            bq_client: BigQuery client for storing conflicts
        """
        self.bq_client = bq_client

    def resolve_conflict(
        self, source_record: Dict[str, Any], target_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Resolve conflict between two records.
        
        Args:
            source_record: Record from source system
            target_record: Record from target system
            
        Returns:
            Dict with 'winner', 'reason', and optional 'conflict_id'
        """
        source_version = source_record.get("sync_metadata", {}).get("version", 0)
        target_version = target_record.get("sync_metadata", {}).get("version", 0)

        # Compare versions
        if source_version > target_version:
            return {"winner": "source", "reason": "higher_version"}

        if source_version < target_version:
            return {"winner": "target", "reason": "higher_version"}

        # Versions equal, compare timestamps
        source_time_str = source_record.get("sync_metadata", {}).get("last_updated")
        target_time_str = target_record.get("sync_metadata", {}).get("last_updated")

        if not source_time_str or not target_time_str:
            # Missing timestamps - manual resolution
            return {
                "winner": None,
                "reason": "missing_timestamps",
                "conflict_id": self._store_conflict(source_record, target_record),
            }

        try:
            source_time = datetime.fromisoformat(source_time_str.replace("Z", "+00:00"))
            target_time = datetime.fromisoformat(target_time_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError) as e:
            logger.warning(f"Invalid timestamp format: {e}")
            return {
                "winner": None,
                "reason": "invalid_timestamps",
                "conflict_id": self._store_conflict(source_record, target_record),
            }

        if source_time > target_time:
            return {"winner": "source", "reason": "later_timestamp"}

        if source_time < target_time:
            return {"winner": "target", "reason": "later_timestamp"}

        # Same version and timestamp - manual resolution needed
        return {
            "winner": None,
            "reason": "manual_resolution_required",
            "conflict_id": self._store_conflict(source_record, target_record),
        }

    def _store_conflict(
        self, source: Dict[str, Any], target: Dict[str, Any]
    ) -> str:
        """Store conflict for manual resolution.
        
        Args:
            source: Source record
            target: Target record
            
        Returns:
            Conflict ID
        """
        conflict_id = str(uuid4())

        # Store in BigQuery conflicts table
        try:
            table = self.bq_client.get_table("identity.sync_conflicts")
            rows_to_insert = [
                {
                    "conflict_id": conflict_id,
                    "source_record": str(source),
                    "target_record": str(target),
                    "source_system": source.get("sync_metadata", {}).get("last_updated_by", "unknown"),
                    "target_system": target.get("sync_metadata", {}).get("last_updated_by", "unknown"),
                    "created_at": datetime.utcnow().isoformat(),
                    "status": "pending",
                }
            ]
            self.bq_client.insert_rows_json(table, rows_to_insert)
            logger.info(f"Stored conflict {conflict_id} for manual resolution")
        except Exception as e:
            logger.error(f"Failed to store conflict: {e}")

        return conflict_id

    def get_conflicts(self, status: str = "pending") -> list[Dict[str, Any]]:
        """Get conflicts by status.
        
        Args:
            status: Conflict status (pending, resolved, ignored)
            
        Returns:
            List of conflict records
        """
        query = f"""
        SELECT * FROM `identity.sync_conflicts`
        WHERE status = @status
        ORDER BY created_at DESC
        """
        job_config = self.bq_client.query(
            query, job_config={"query_parameters": [("status", "STRING", status)]}
        )
        return list(job_config.result())
