"""Business sync service - syncs businesses across all systems."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)


class BusinessSyncService:
    """Syncs businesses from BigQuery (canonical) to all other systems.
    
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
        """Initialize business sync service.
        
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

    def sync_business_to_all(self, business_id: str) -> Dict[str, Any]:
        """Sync a single business from BigQuery to all systems.
        
        Args:
            business_id: Business ID in BigQuery
            
        Returns:
            Dict with sync results for each system
        """
        try:
            # 1. Fetch from BigQuery
            business = self._fetch_business_from_bigquery(business_id)
            if not business:
                self.error_reporter.report_error(
                    "business",
                    business_id,
                    "bigquery",
                    "not_found",
                    f"Business {business_id} not found in BigQuery",
                )
                return {"error": f"Business {business_id} not found in BigQuery"}

            # 2. Sync to Supabase
            supabase_result = self._sync_business_to_supabase(business)

            # 3. Sync to Local
            local_result = self._sync_business_to_local(business)

            # 4. Sync to CRM Twenty
            crm_result = self._sync_business_to_crm_twenty(business)

            # Check for errors and report them
            results = {
                "bigquery": {"status": "synced", "version": business.get("version", 1)},
                "supabase": supabase_result,
                "local": local_result,
                "crm_twenty": crm_result,
            }

            for system, result in results.items():
                if result.get("status") == "error":
                    self.error_reporter.report_error(
                        "business",
                        business_id,
                        system,
                        "sync_failed",
                        result.get("error", "Unknown error"),
                        result,
                    )

            return results

        except Exception as e:
            # **NEVER HIDE ERRORS**
            self.error_reporter.report_error(
                "business",
                business_id,
                "bigquery",
                "exception",
                str(e),
                {"traceback": traceback.format_exc()},
            )
            raise

    def _fetch_business_from_bigquery(
        self, business_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch business from BigQuery.
        
        Args:
            business_id: Business ID
            
        Returns:
            Business record or None
        """
        try:
            query = """
            SELECT * FROM `identity.businesses_master`
            WHERE business_id = @business_id
            LIMIT 1
            """

            job_config = {
                "query_parameters": [("business_id", "INT64", int(business_id))]
            }

            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())

            if not results:
                return None

            return dict(results[0])
        except Exception as e:
            self.error_reporter.report_error(
                "business",
                business_id,
                "bigquery",
                "database",
                f"Failed to fetch business: {e}",
                {"traceback": traceback.format_exc()},
            )
            raise

    def _sync_business_to_supabase(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Sync business to Supabase.
        
        Args:
            business: Business record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            # Transform BigQuery format to Supabase format
            supabase_business = self._transform_bq_to_supabase(business)

            # Upsert to Supabase
            result = (
                self.supabase.table("businesses_master")
                .upsert(supabase_business, on_conflict="business_id")
                .execute()
            )

            return {"status": "synced", "supabase_id": result.data[0]["id"]}
        except Exception as e:
            error_msg = f"Failed to sync business to Supabase: {e}"
            self.error_reporter.report_error(
                "business",
                str(business.get("business_id")),
                "supabase",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _sync_business_to_local(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Sync business to local database.
        
        Args:
            business: Business record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            # Transform BigQuery format to local format
            local_business = self._transform_bq_to_local(business)

            # Upsert to local DB
            cursor = self.local_db.cursor()
            cursor.execute(
                """
                INSERT INTO businesses_master (
                    business_id, business_name, name_normalized,
                    industry, business_type, sync_metadata,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(business_id) DO UPDATE SET
                    business_name = excluded.business_name,
                    name_normalized = excluded.name_normalized,
                    updated_at = excluded.updated_at
                """,
                (
                    local_business["business_id"],
                    local_business["business_name"],
                    local_business.get("name_normalized"),
                    local_business.get("industry"),
                    local_business.get("business_type"),
                    str(local_business.get("sync_metadata", {})),
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                ),
            )
            self.local_db.commit()

            return {"status": "synced"}
        except Exception as e:
            error_msg = f"Failed to sync business to local DB: {e}"
            self.error_reporter.report_error(
                "business",
                str(business.get("business_id")),
                "local",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _sync_business_to_crm_twenty(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Sync business to CRM Twenty.
        
        Uses TwentyCRMClient which gets API key from secrets manager.
        
        Args:
            business: Business record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            # Transform BigQuery format to CRM Twenty format
            crm_business = self._transform_bq_to_crm_twenty(business)

            # Upsert to CRM Twenty
            result = self.crm_twenty.upsert_company(crm_business)

            return {"status": "synced", "crm_id": result.get("id")}
        except Exception as e:
            error_msg = f"Failed to sync business to CRM Twenty: {e}"
            self.error_reporter.report_error(
                "business",
                str(business.get("business_id")),
                "crm_twenty",
                "sync",
                error_msg,
                {"traceback": traceback.format_exc()},
            )
            return {"status": "error", "error": error_msg}

    def _transform_bq_to_supabase(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery business to Supabase format."""
        import json

        return {
            "business_id": str(business["business_id"]),
            "business_name": business["business_name"],
            "name_normalized": business.get("name_normalized"),
            "industry": business.get("industry"),
            "business_type": business.get("business_type"),
            "llm_context": json.dumps(business.get("llm_context", {})),
            "sync_metadata": json.dumps(business.get("sync_metadata", {})),
        }

    def _transform_bq_to_local(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery business to local format."""
        return {
            "business_id": str(business["business_id"]),
            "business_name": business["business_name"],
            "name_normalized": business.get("name_normalized"),
            "industry": business.get("industry"),
            "business_type": business.get("business_type"),
            "sync_metadata": business.get("sync_metadata", {}),
        }

    def _transform_bq_to_crm_twenty(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery business to CRM Twenty format."""
        import json

        return {
            "name": business["business_name"],
            "customFields": {
                "business_id": str(business["business_id"]),
                "industry": business.get("industry"),
                "business_type": business.get("business_type"),
                "llm_context": json.dumps(business.get("llm_context", {})),
                "sync_metadata": json.dumps(business.get("sync_metadata", {})),
            },
        }
