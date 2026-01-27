"""Supabase sync service - syncs from Supabase to BigQuery (canonical)."""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class SupabaseSyncService:
    """Syncs contacts from Supabase to BigQuery (canonical).
    
    Changes in Supabase flow to BigQuery first, then propagate to all systems.
    """

    def __init__(self, supabase_client: Any, bq_client: Any, bq_sync: Any) -> None:
        """Initialize Supabase sync service.
        
        Args:
            supabase_client: Supabase client
            bq_client: BigQuery client
            bq_sync: BigQuerySyncService for propagation
        """
        self.supabase = supabase_client
        self.bq_client = bq_client
        self.bq_sync = bq_sync

    def sync_from_supabase_to_bigquery(
        self, supabase_contact_id: str
    ) -> Dict[str, Any]:
        """Sync a contact from Supabase to BigQuery.
        
        Args:
            supabase_contact_id: Contact ID in Supabase (UUID)
            
        Returns:
            Sync result
        """
        # 1. Fetch from Supabase
        # Supabase uses UUID (id) as primary key, but we also have contact_id TEXT
        # Try by contact_id first (for sync operations), then by id (UUID)
        result = (
            self.supabase.table("contacts_master")
            .select("*")
            .or_(f"contact_id.eq.{supabase_contact_id},id.eq.{supabase_contact_id}")
            .execute()
        )

        if not result.data:
            return {"error": f"Contact {supabase_contact_id} not found in Supabase"}

        supabase_contact = result.data[0]

        # 2. Transform to canonical format
        canonical_contact = self._transform_supabase_to_canonical(supabase_contact)

        # 3. Upsert to BigQuery (with conflict resolution)
        bq_result = self._upsert_to_bigquery(canonical_contact)

        # 4. Trigger propagation to all systems
        if bq_result.get("status") == "synced":
            self.bq_sync.sync_contact_to_all(canonical_contact["contact_id"])

        return bq_result

    def sync_all_from_supabase(
        self, last_sync_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync all contacts modified since last sync.
        
        Args:
            last_sync_time: Last sync timestamp
            
        Returns:
            Sync summary
        """
        if not last_sync_time:
            from datetime import timedelta
            last_sync_time = datetime.utcnow() - timedelta(hours=24)

        result = (
            self.supabase.table("contacts_master")
            .select("*")
            .gte("updated_at", last_sync_time.isoformat())
            .execute()
        )

        results = []
        for contact in result.data:
            sync_result = self.sync_from_supabase_to_bigquery(contact["id"])
            results.append(sync_result)

        return {"synced": len(results), "results": results}

    def _transform_supabase_to_canonical(
        self, supabase_contact: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transform Supabase contact to canonical format.
        
        Aligns with existing identity.contacts_master structure.
        
        Args:
            supabase_contact: Contact from Supabase
            
        Returns:
            Canonical contact format (matches identity.contacts_master)
        """
        # Parse JSONB fields - ALL metadata fields
        # Handle both JSONB (dict) and string formats gracefully
        def parse_json_field(value: Any, default: Any = None) -> Any:
            """Parse JSON field safely."""
            if value is None:
                return default or {}
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return default or {}
            return default or {}

        llm_context = parse_json_field(supabase_contact.get("llm_context"))
        communication_stats = parse_json_field(supabase_contact.get("communication_stats"))
        social_network = parse_json_field(supabase_contact.get("social_network"))
        ai_insights = parse_json_field(supabase_contact.get("ai_insights"))
        recommendations = parse_json_field(supabase_contact.get("recommendations"))
        sync_metadata = parse_json_field(supabase_contact.get("sync_metadata"))

        # Update sync metadata
        sync_metadata.update(
            {
                "last_updated": datetime.utcnow().isoformat(),
                "last_updated_by": "supabase",
                "version": sync_metadata.get("version", 0) + 1,
                "sync_status": "synced",
                "source_systems": list(
                    set(sync_metadata.get("source_systems", []) + ["supabase"])
                ),
            }
        )

        # Use canonical_name or derive from full_name
        canonical_name = supabase_contact.get("canonical_name") or \
            supabase_contact.get("full_name") or \
            f"{supabase_contact.get('first_name', '')} {supabase_contact.get('last_name', '')}".strip()

        # Get contact_id (TEXT) - convert to INT64 for BigQuery
        contact_id_str = supabase_contact.get("contact_id")
        if not contact_id_str:
            # If no contact_id, we can't sync (missing stable ID)
            # Log error but don't raise - return error dict instead
            error_msg = f"Contact {supabase_contact.get('id')} missing contact_id (stable ID)"
            logger.error(error_msg)
            raise ValueError(error_msg)

        return {
            "contact_id": int(contact_id_str),
            "canonical_name": canonical_name,
            "name_normalized": supabase_contact.get("name_normalized"),
            "first_name": supabase_contact.get("first_name"),
            "last_name": supabase_contact.get("last_name"),
            "middle_name": supabase_contact.get("middle_name"),
            "nickname": supabase_contact.get("nickname"),
            "name_suffix": supabase_contact.get("name_suffix"),
            "title": supabase_contact.get("title"),
            "full_name": supabase_contact.get("full_name"),
            "organization": supabase_contact.get("organization"),
            "job_title": supabase_contact.get("job_title"),
            "department": supabase_contact.get("department"),
            "category_code": supabase_contact.get("category_code"),
            "subcategory_code": supabase_contact.get("subcategory_code"),
            "relationship_category": supabase_contact.get("relationship_category"),
            "notes": supabase_contact.get("notes"),
            "birthday": supabase_contact.get("birthday"),
            "is_business": supabase_contact.get("is_business", False),
            "is_me": supabase_contact.get("is_me", False),
            # ALL Extended fields
            "llm_context": llm_context,
            "communication_stats": communication_stats,
            "social_network": social_network,
            "ai_insights": ai_insights,
            "recommendations": recommendations,
            "sync_metadata": sync_metadata,
            "created_at": supabase_contact.get("created_at"),
            "updated_at": datetime.utcnow().isoformat(),
        }

    def _upsert_to_bigquery(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert contact to BigQuery with conflict resolution.
        
        Args:
            contact: Canonical contact format
            
        Returns:
            Upsert result
        """
        try:
            # Check if contact exists
            query = """
            SELECT * FROM `identity.contacts_master`
            WHERE contact_id = @contact_id
            LIMIT 1
            """
            job_config = {
                "query_parameters": [("contact_id", "INT64", contact["contact_id"])]
            }
            query_job = self.bq_client.query(query, job_config=job_config)
            existing = list(query_job.result())

            # Resolve conflict if exists
            if existing:
                from .conflict_resolver import ConflictResolver

                resolver = ConflictResolver(self.bq_client)
                conflict_result = resolver.resolve_conflict(contact, dict(existing[0]))

                if conflict_result.get("winner") == "target":
                    # Existing record wins, don't update
                    return {
                        "status": "skipped",
                        "reason": "existing_record_newer",
                    }

            # Insert or update
            rows_to_insert = [contact]
            table = self.bq_client.get_table("identity.contacts_master")
            errors = self.bq_client.insert_rows_json(table, rows_to_insert)

            if errors:
                return {"status": "error", "errors": errors}

            return {"status": "synced", "contact_id": contact["contact_id"]}
        except Exception as e:
            logger.error(f"Failed to upsert to BigQuery: {e}")
            return {"status": "error", "error": str(e)}
