"""CRM Twenty sync service - syncs from CRM Twenty to BigQuery (canonical).

Uses TwentyCRMClient which gets API key from secrets manager.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class CRMTwentySyncService:
    """Syncs contacts from CRM Twenty to BigQuery (canonical).
    
    CRM Twenty is the visibility layer. Changes in CRM flow to BigQuery first,
    then propagate to all systems.
    """

    def __init__(
        self, crm_client: Any, bq_client: Any, bq_sync: Any
    ) -> None:
        """Initialize CRM Twenty sync service.
        
        Args:
            crm_client: CRM Twenty API client
            bq_client: BigQuery client
            bq_sync: BigQuerySyncService for propagation
        """
        self.crm = crm_client
        self.bq_client = bq_client
        self.bq_sync = bq_sync

    def sync_from_crm_to_bigquery(self, crm_contact_id: str) -> Dict[str, Any]:
        """Sync a contact from CRM Twenty to BigQuery.
        
        Args:
            crm_contact_id: Contact ID in CRM Twenty
            
        Returns:
            Sync result
        """
        # 1. Fetch from CRM Twenty
        try:
            crm_contact = self.crm.get_contact(crm_contact_id)
        except Exception as e:
            logger.error(f"Failed to fetch from CRM Twenty: {e}")
            return {"status": "error", "error": str(e)}

        # 2. Transform to canonical format
        canonical_contact = self._transform_crm_to_canonical(crm_contact)

        # 3. Upsert to BigQuery (with conflict resolution)
        bq_result = self._upsert_to_bigquery(canonical_contact)

        # 4. Trigger propagation to all systems
        if bq_result.get("status") == "synced":
            self.bq_sync.sync_contact_to_all(canonical_contact["contact_id"])

        return bq_result

    def sync_all_from_crm(
        self, last_sync_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Sync all contacts modified since last sync.
        
        Args:
            last_sync_time: Last sync timestamp
            
        Returns:
            Sync summary
        """
        try:
            # Fetch all contacts from CRM
            crm_contacts = self.crm.list_contacts(updated_since=last_sync_time)

            results = []
            for contact in crm_contacts:
                sync_result = self.sync_from_crm_to_bigquery(contact["id"])
                results.append(sync_result)

            return {"synced": len(results), "results": results}
        except Exception as e:
            logger.error(f"Failed to sync all from CRM: {e}")
            return {"status": "error", "error": str(e)}

    def _parse_json_field(self, value: Any, default: Any = None) -> Any:
        """Parse JSON field safely.
        
        Args:
            value: JSON string or dict
            default: Default value if parsing fails
            
        Returns:
            Parsed JSON or default
        """
        if value is None:
            return default or {}
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return default or {}
        return default or {}

    def _transform_crm_to_canonical(self, crm_contact: Dict[str, Any]) -> Dict[str, Any]:
        """Transform CRM Twenty contact to canonical format.
        
        Includes ALL contact metadata fields for complete relationship management.
        
        Args:
            crm_contact: Contact from CRM Twenty
            
        Returns:
            Canonical contact format
        """
        custom_fields = crm_contact.get("customFields", {})

        # Parse JSON fields
        llm_context = self._parse_json_field(custom_fields.get("llm_context"))
        communication_stats = self._parse_json_field(custom_fields.get("communication_stats"))
        social_network = self._parse_json_field(custom_fields.get("social_network"))
        ai_insights = self._parse_json_field(custom_fields.get("ai_insights"))
        recommendations = self._parse_json_field(custom_fields.get("recommendations"))
        sync_metadata = self._parse_json_field(custom_fields.get("sync_metadata"))

        # Get or generate contact_id
        contact_id = custom_fields.get("contact_id")
        if not contact_id:
            # Generate from name if no contact_id
            import hashlib
            contact_id = int(
                hashlib.md5(crm_contact["name"].encode()).hexdigest()[:15], 16
            )

        # Update sync metadata
        sync_metadata.update(
            {
                "last_updated": crm_contact.get("updatedAt", datetime.utcnow().isoformat()),
                "last_updated_by": "crm_twenty",
                "version": sync_metadata.get("version", 0) + 1,
                "sync_status": "synced",
                "source_systems": list(
                    set(sync_metadata.get("source_systems", []) + ["crm_twenty"])
                ),
            }
        )

        # Build canonical name from components or use name
        canonical_name = (
            custom_fields.get("full_name") or
            crm_contact.get("name") or
            f"{custom_fields.get('first_name', '')} {custom_fields.get('last_name', '')}".strip()
        )

        return {
            # Primary Identifiers
            "contact_id": int(contact_id) if isinstance(contact_id, str) else contact_id,
            "canonical_name": canonical_name,
            "name_normalized": custom_fields.get("name_normalized") or canonical_name.lower().strip(),
            "apple_unique_id": custom_fields.get("apple_unique_id"),
            "apple_identity_unique_id": custom_fields.get("apple_identity_unique_id"),
            
            # Name Components
            "first_name": custom_fields.get("first_name"),
            "last_name": custom_fields.get("last_name"),
            "middle_name": custom_fields.get("middle_name"),
            "nickname": custom_fields.get("nickname"),
            "name_suffix": custom_fields.get("name_suffix"),
            "title": custom_fields.get("title"),
            "full_name": custom_fields.get("full_name") or canonical_name,
            
            # Organization
            "organization": custom_fields.get("organization") or (crm_contact.get("company", {}).get("name") if crm_contact.get("company") else None),
            "job_title": custom_fields.get("job_title"),
            "department": custom_fields.get("department"),
            
            # Relationship Categorization
            "category_code": custom_fields.get("category_code"),
            "subcategory_code": custom_fields.get("subcategory_code"),
            "relationship_category": custom_fields.get("relationship_category"),
            
            # Metadata
            "notes": custom_fields.get("notes"),
            "birthday": custom_fields.get("birthday"),
            "is_business": custom_fields.get("is_business", False),
            "is_me": custom_fields.get("is_me", False),
            
            # Rich LLM Data
            "llm_context": llm_context,
            "communication_stats": communication_stats,
            "social_network": social_network,
            "ai_insights": ai_insights,
            "recommendations": recommendations,
            
            # Sync Metadata
            "sync_metadata": sync_metadata,
            
            # Timestamps
            "created_at": crm_contact.get("createdAt", datetime.utcnow().isoformat()),
            "updated_at": crm_contact.get("updatedAt", datetime.utcnow().isoformat()),
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
