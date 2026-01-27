"""Error reporter - ensures complete transparency, nothing hidden.

All errors, issues, and problems are reported to Jeremy.
Nothing is hidden or suppressed.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error types for categorization."""
    VALIDATION = "validation"
    SYNC = "sync"
    CONFLICT = "conflict"
    NETWORK = "network"
    DATABASE = "database"
    NOT_FOUND = "not_found"
    PERMISSION = "permission"
    EXCEPTION = "exception"
    OTHER = "other"


class ErrorReporter:
    """Reports all errors transparently - nothing hidden.
    
    Every error is:
    1. Stored in entity's sync_errors array
    2. Stored in central error log
    3. Alerted to Jeremy
    4. Logged to monitoring system
    """

    def __init__(
        self,
        bq_client: Any,
        alert_service: Optional[Any] = None,
    ) -> None:
        """Initialize error reporter.
        
        Args:
            bq_client: BigQuery client for error log
            alert_service: Service for alerting Jeremy (email/Slack)
        """
        self.bq_client = bq_client
        self.alert_service = alert_service

    def report_error(
        self,
        entity_type: str,  # 'business', 'relationship', 'contact'
        entity_id: str,
        system: str,  # 'bigquery', 'supabase', 'local', 'crm_twenty'
        error_type: str,
        error_message: str,
        error_details: Any = None,
        raise_after: bool = False,
    ) -> Dict[str, Any]:
        """Report an error - ALWAYS called, never hidden.
        
        Args:
            entity_type: Type of entity (business, relationship, contact)
            entity_id: ID of the entity
            system: System where error occurred
            error_type: Type of error (from ErrorType enum or string)
            error_message: Human-readable error message
            error_details: Full error details (stack trace, etc.)
            raise_after: Whether to raise exception after reporting
            
        Returns:
            Error record
        """
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system,
            "error_type": error_type,
            "error_message": error_message,
            "error_details": (
                str(error_details) if error_details else None
            ),
            "resolved": False,
        }

        # 1. Store in entity's sync_errors array
        try:
            self._store_error_in_entity(entity_type, entity_id, error)
        except Exception as e:
            logger.critical(
                f"CRITICAL: Failed to store error in entity: {e}. "
                f"Original error: {error_message}"
            )

        # 2. Store in central error log (BigQuery)
        try:
            self._store_in_error_log(entity_type, entity_id, error)
        except Exception as e:
            logger.critical(
                f"CRITICAL: Failed to store error in log: {e}. "
                f"Original error: {error_message}"
            )

        # 3. Alert Jeremy (email/Slack/notification)
        try:
            self._alert_jeremy(error, entity_type, entity_id)
        except Exception as e:
            logger.critical(
                f"CRITICAL: Failed to alert Jeremy: {e}. "
                f"Original error: {error_message}"
            )

        # 4. Log to monitoring system
        logger.error(
            f"SYNC ERROR [{error_type}] in {system} for {entity_type} {entity_id}: "
            f"{error_message}"
        )
        if error_details:
            logger.error(f"Error details: {error_details}")

        if raise_after:
            raise RuntimeError(f"{error_type}: {error_message}")

        return error

    def _store_error_in_entity(
        self, entity_type: str, entity_id: str, error: Dict[str, Any]
    ) -> None:
        """Store error in entity's sync_errors array.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            error: Error record
        """
        if entity_type == "business":
            table_name = "identity.businesses_master"
            id_field = "business_id"
        elif entity_type == "relationship":
            table_name = "identity.people_business_relationships"
            id_field = "relationship_id"
        elif entity_type == "contact":
            table_name = "identity.contacts_master"
            id_field = "contact_id"
        else:
            logger.warning(f"Unknown entity_type: {entity_type}")
            return

        # Append error to sync_errors array
        query = f"""
        UPDATE `{table_name}`
        SET sync_errors = ARRAY_CONCAT(
          COALESCE(sync_errors, []),
          [STRUCT(
            @timestamp AS timestamp,
            @system AS system,
            @error_type AS error_type,
            @error_message AS error_message,
            @error_details AS error_details,
            @resolved AS resolved
          )]
        ),
        sync_status = 'error',
        updated_at = CURRENT_TIMESTAMP()
        WHERE {id_field} = @entity_id
        """

        job_config = {
            "query_parameters": [
                ("entity_id", "INT64" if id_field.endswith("_id") else "STRING", entity_id),
                ("timestamp", "TIMESTAMP", error["timestamp"]),
                ("system", "STRING", error["system"]),
                ("error_type", "STRING", error["error_type"]),
                ("error_message", "STRING", error["error_message"]),
                ("error_details", "STRING", error["error_details"]),
                ("resolved", "BOOL", error["resolved"]),
            ]
        }

        self.bq_client.query(query, job_config=job_config).result()

    def _store_in_error_log(
        self, entity_type: str, entity_id: str, error: Dict[str, Any]
    ) -> None:
        """Store error in central error log.
        
        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            error: Error record
        """
        table = self.bq_client.get_table("identity.sync_errors_log")

        rows_to_insert = [
            {
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "timestamp": error["timestamp"],
                "system": error["system"],
                "error_type": error["error_type"],
                "error_message": error["error_message"],
                "error_details": error["error_details"],
                "resolved": error["resolved"],
            }
        ]

        errors = self.bq_client.insert_rows_json(table, rows_to_insert)
        if errors:
            logger.critical(f"Failed to insert error log: {errors}")

    def _alert_jeremy(
        self, error: Dict[str, Any], entity_type: str, entity_id: str
    ) -> None:
        """Alert Jeremy about the error - nothing hidden.
        
        Args:
            error: Error record
            entity_type: Type of entity
            entity_id: Entity ID
        """
        if not self.alert_service:
            # Log if no alert service configured
            logger.warning("No alert service configured - error not alerted")
            return

        alert_message = f"""
SYNC ERROR DETECTED

Entity Type: {entity_type}
Entity ID: {entity_id}
System: {error['system']}
Error Type: {error['error_type']}
Error Message: {error['error_message']}
Timestamp: {error['timestamp']}

Error Details:
{error['error_details'] or 'None'}

This error has been logged and stored. Please review.
"""

        try:
            self.alert_service.send_alert(
                subject=f"SYNC ERROR: {error['error_type']} in {error['system']}",
                message=alert_message,
                priority="high",
            )
        except Exception as e:
            logger.critical(f"Failed to send alert to Jeremy: {e}")

    def get_unresolved_errors(
        self, entity_type: Optional[str] = None, system: Optional[str] = None
    ) -> list[Dict[str, Any]]:
        """Get unresolved errors.
        
        Args:
            entity_type: Filter by entity type
            system: Filter by system
            
        Returns:
            List of unresolved errors
        """
        query = """
        SELECT * FROM `identity.sync_errors_log`
        WHERE resolved = FALSE
        """
        params = []

        if entity_type:
            query += " AND entity_type = @entity_type"
            params.append(("entity_type", "STRING", entity_type))

        if system:
            query += " AND system = @system"
            params.append(("system", "STRING", system))

        query += " ORDER BY timestamp DESC LIMIT 100"

        job_config = {"query_parameters": params} if params else None
        query_job = self.bq_client.query(query, job_config=job_config)
        return [dict(row) for row in query_job.result()]

    def mark_error_resolved(
        self, error_id: str, resolution_notes: Optional[str] = None
    ) -> None:
        """Mark an error as resolved.
        
        Args:
            error_id: Error ID
            resolution_notes: Notes about resolution
        """
        query = """
        UPDATE `identity.sync_errors_log`
        SET resolved = TRUE,
            resolution_notes = @resolution_notes,
            resolved_at = CURRENT_TIMESTAMP()
        WHERE error_id = @error_id
        """

        job_config = {
            "query_parameters": [
                ("error_id", "STRING", error_id),
                ("resolution_notes", "STRING", resolution_notes),
            ]
        }

        self.bq_client.query(query, job_config=job_config).result()
