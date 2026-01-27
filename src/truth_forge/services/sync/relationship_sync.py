"""People-business relationship sync service."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


class RelationshipSyncService:
    """Syncs people-business relationships across all systems.
    
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
        """Initialize relationship sync service.
        
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
            Dict with sync results
        """
        try:
            # 1. Fetch from BigQuery
            relationship = self._fetch_relationship_from_bigquery(relationship_id)
            if not relationship:
                self.error_reporter.report_error(
                    "relationship",
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
                        "relationship",
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
                "relationship",
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
        """Fetch relationship from BigQuery."""
        try:
            query = """
            SELECT * FROM `identity.people_business_relationships`
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
                "relationship",
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
        """Sync relationship to Supabase."""
        try:
            supabase_relationship = self._transform_bq_to_supabase(relationship)

            result = (
                self.supabase.table("people_business_relationships")
                .upsert(supabase_relationship, on_conflict="relationship_id")
                .execute()
            )

            return {"status": "synced", "supabase_id": result.data[0]["id"]}
        except Exception as e:
            error_msg = f"Failed to sync relationship to Supabase: {e}"
            self.error_reporter.report_error(
                "relationship",
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
        """Sync relationship to local database."""
        try:
            local_relationship = self._transform_bq_to_local(relationship)

            cursor = self.local_db.cursor()
            cursor.execute(
                """
                INSERT INTO people_business_relationships (
                    relationship_id, contact_id, business_id,
                    relationship_type, role, is_current,
                    sync_metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(relationship_id) DO UPDATE SET
                    relationship_type = excluded.relationship_type,
                    role = excluded.role,
                    updated_at = excluded.updated_at
                """,
                (
                    local_relationship["relationship_id"],
                    local_relationship["contact_id"],
                    local_relationship["business_id"],
                    local_relationship["relationship_type"],
                    local_relationship.get("role"),
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
                "relationship",
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
        """Sync relationship to CRM Twenty."""
        try:
            crm_relationship = self._transform_bq_to_crm_twenty(relationship)
            result = self.crm_twenty.upsert_relationship(crm_relationship)
            return {"status": "synced", "crm_id": result.get("id")}
        except Exception as e:
            error_msg = f"Failed to sync relationship to CRM Twenty: {e}"
            self.error_reporter.report_error(
                "relationship",
                str(relationship.get("relationship_id")),
                "crm_twenty",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _transform_bq_to_supabase(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery relationship to Supabase format."""
        import json

        return {
            "relationship_id": str(relationship["relationship_id"]),
            "contact_id": str(relationship["contact_id"]),
            "business_id": str(relationship["business_id"]),
            "relationship_type": relationship["relationship_type"],
            "role": relationship.get("role"),
            "department": relationship.get("department"),
            "is_current": relationship.get("is_current", True),
            "relationship_context": json.dumps(
                relationship.get("relationship_context", {})
            ),
            "sync_metadata": json.dumps(relationship.get("sync_metadata", {})),
        }

    def _transform_bq_to_local(self, relationship: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery relationship to local format."""
        return {
            "relationship_id": str(relationship["relationship_id"]),
            "contact_id": str(relationship["contact_id"]),
            "business_id": str(relationship["business_id"]),
            "relationship_type": relationship["relationship_type"],
            "role": relationship.get("role"),
            "is_current": relationship.get("is_current", True),
            "sync_metadata": relationship.get("sync_metadata", {}),
        }

    def _transform_bq_to_crm_twenty(
        self, relationship: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform BigQuery relationship to CRM Twenty format."""
        import json

        return {
            "personId": str(relationship["contact_id"]),
            "companyId": str(relationship["business_id"]),
            "role": relationship.get("role"),
            "customFields": {
                "relationship_id": str(relationship["relationship_id"]),
                "relationship_type": relationship["relationship_type"],
                "relationship_context": json.dumps(
                    relationship.get("relationship_context", {})
                ),
            },
        }
