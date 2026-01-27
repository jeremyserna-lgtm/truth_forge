"""People-to-people relationship sync service.

Syncs relationships between people across all systems.
Builds rich social graph with full tracking.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


class PeopleRelationshipSyncService:
    """Syncs people-to-people relationships across all systems.
    
    All errors are reported transparently - nothing hidden.
    """

    def __init__(
        self,
        bq_client: Any,
        supabase_client: Any,
        local_db: Any,
        crm_twenty_client: Any,
        error_reporter: Any,
    ) -> None:
        """Initialize people relationship sync service.
        
        Args:
            bq_client: BigQuery client
            supabase_client: Supabase client
            local_db: Local database connection
            crm_twenty_client: CRM Twenty API client
            error_reporter: ErrorReporter instance
        """
        self.bq_client = bq_client
        self.supabase = supabase_client
        self.local_db = local_db
        self.crm_twenty = crm_twenty_client
        self.error_reporter = error_reporter

    def sync_relationship_to_all(self, relationship_id: str) -> Dict[str, Any]:
        """Sync a relationship from BigQuery to all systems.
        
        Args:
            relationship_id: Relationship ID in BigQuery
            
        Returns:
            Dict with sync results for each system
        """
        try:
            # 1. Fetch from BigQuery
            relationship = self._fetch_relationship_from_bigquery(relationship_id)
            if not relationship:
                self.error_reporter.report_error(
                    "people_relationship",
                    relationship_id,
                    "bigquery",
                    "not_found",
                    f"Relationship {relationship_id} not found in BigQuery",
                )
                return {
                    "error": f"Relationship {relationship_id} not found in BigQuery"
                }

            # 2. Sync to Supabase
            supabase_result = self._sync_relationship_to_supabase(relationship)

            # 3. Sync to Local
            local_result = self._sync_relationship_to_local(relationship)

            # 4. Sync to CRM Twenty
            crm_result = self._sync_relationship_to_crm_twenty(relationship)

            results = {
                "bigquery": {
                    "status": "synced",
                    "version": relationship.get("version", 1),
                },
                "supabase": supabase_result,
                "local": local_result,
                "crm_twenty": crm_result,
            }

            # Check for errors
            for system, result in results.items():
                if result.get("status") == "error":
                    self.error_reporter.report_error(
                        "people_relationship",
                        relationship_id,
                        system,
                        "sync_failed",
                        result.get("error", "Unknown error"),
                        result,
                    )

            return results

        except Exception as e:
            # **NEVER HIDE ERRORS**
            self.error_reporter.report_error(
                "people_relationship",
                relationship_id,
                "bigquery",
                "exception",
                str(e),
                {"traceback": traceback.format_exc()},
            )
            raise

    def _fetch_relationship_from_bigquery(
        self, relationship_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch relationship from BigQuery.
        
        Args:
            relationship_id: Relationship ID
            
        Returns:
            Relationship record or None
        """
        try:
            query = """
            SELECT * FROM `identity.people_relationships`
            WHERE relationship_id = @relationship_id
            LIMIT 1
            """

            job_config = {
                "query_parameters": [
                    ("relationship_id", "INT64", int(relationship_id))
                ]
            }

            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())

            if not results:
                return None

            return dict(results[0])
        except Exception as e:
            self.error_reporter.report_error(
                "people_relationship",
                relationship_id,
                "bigquery",
                "database",
                f"Failed to fetch relationship: {e}",
                {"traceback": traceback.format_exc()},
            )
            raise

    def _sync_relationship_to_supabase(
        self, relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync relationship to Supabase.
        
        Args:
            relationship: Relationship record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            supabase_relationship = self._transform_bq_to_supabase(relationship)

            result = (
                self.supabase.table("people_relationships")
                .upsert(supabase_relationship, on_conflict="relationship_id")
                .execute()
            )

            return {"status": "synced", "supabase_id": result.data[0]["id"]}
        except Exception as e:
            error_msg = f"Failed to sync relationship to Supabase: {e}"
            self.error_reporter.report_error(
                "people_relationship",
                str(relationship.get("relationship_id")),
                "supabase",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _sync_relationship_to_local(
        self, relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync relationship to local database.
        
        Args:
            relationship: Relationship record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            local_relationship = self._transform_bq_to_local(relationship)

            cursor = self.local_db.cursor()
            cursor.execute(
                """
                INSERT INTO people_relationships (
                    relationship_id, person_1_id, person_2_id,
                    relationship_type, relationship_subtype, is_current,
                    sync_metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(relationship_id) DO UPDATE SET
                    relationship_type = excluded.relationship_type,
                    is_current = excluded.is_current,
                    updated_at = excluded.updated_at
                """,
                (
                    local_relationship["relationship_id"],
                    local_relationship["person_1_id"],
                    local_relationship["person_2_id"],
                    local_relationship["relationship_type"],
                    local_relationship.get("relationship_subtype"),
                    local_relationship.get("is_current", True),
                    str(local_relationship.get("sync_metadata", {})),
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                ),
            )
            self.local_db.commit()

            return {"status": "synced"}
        except Exception as e:
            error_msg = f"Failed to sync relationship to local DB: {e}"
            self.error_reporter.report_error(
                "people_relationship",
                str(relationship.get("relationship_id")),
                "local",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _sync_relationship_to_crm_twenty(
        self, relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Sync relationship to CRM Twenty.
        
        Args:
            relationship: Relationship record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            crm_relationship = self._transform_bq_to_crm_twenty(relationship)
            result = self.crm_twenty.upsert_relationship(crm_relationship)
            return {"status": "synced", "crm_id": result.get("id")}
        except Exception as e:
            error_msg = f"Failed to sync relationship to CRM Twenty: {e}"
            self.error_reporter.report_error(
                "people_relationship",
                str(relationship.get("relationship_id")),
                "crm_twenty",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _transform_bq_to_supabase(
        self, relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform BigQuery relationship to Supabase format."""
        import json

        return {
            "relationship_id": str(relationship["relationship_id"]),
            "person_1_id": str(relationship["person_1_id"]),
            "person_2_id": str(relationship["person_2_id"]),
            "is_directed": relationship.get("is_directed", False),
            "direction": relationship.get("direction"),
            "relationship_type": relationship["relationship_type"],
            "relationship_subtype": relationship.get("relationship_subtype"),
            "start_date": relationship.get("start_date"),
            "end_date": relationship.get("end_date"),
            "is_current": relationship.get("is_current", True),
            "relationship_status": relationship.get("relationship_status"),
            "relationship_context": json.dumps(
                relationship.get("relationship_context", {})
            ),
            "social_context": json.dumps(relationship.get("social_context", {})),
            "tracking": json.dumps(relationship.get("tracking", {})),
            "evolution": json.dumps(relationship.get("evolution", {})),
            "llm_context": json.dumps(relationship.get("llm_context", {})),
            "sync_metadata": json.dumps(relationship.get("sync_metadata", {})),
        }

    def _transform_bq_to_local(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery relationship to local format."""
        return {
            "relationship_id": str(relationship["relationship_id"]),
            "person_1_id": str(relationship["person_1_id"]),
            "person_2_id": str(relationship["person_2_id"]),
            "relationship_type": relationship["relationship_type"],
            "relationship_subtype": relationship.get("relationship_subtype"),
            "is_current": relationship.get("is_current", True),
            "sync_metadata": relationship.get("sync_metadata", {}),
        }

    def _transform_bq_to_crm_twenty(
        self, relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform BigQuery relationship to CRM Twenty format."""
        import json

        return {
            "person1Id": str(relationship["person_1_id"]),
            "person2Id": str(relationship["person_2_id"]),
            "relationshipType": relationship["relationship_type"],
            "customFields": {
                "relationship_id": str(relationship["relationship_id"]),
                "relationship_subtype": relationship.get("relationship_subtype"),
                "relationship_context": json.dumps(
                    relationship.get("relationship_context", {})
                ),
                "social_context": json.dumps(relationship.get("social_context", {})),
            },
        }
