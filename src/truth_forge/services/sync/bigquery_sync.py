"""BigQuery sync service - syncs from canonical source to all systems."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BigQuerySyncService:
    """Syncs contacts from BigQuery (canonical) to all other systems.
    
    BigQuery is the canonical source. All changes flow through BigQuery first,
    then propagate to Supabase, Local DB, and CRM Twenty.
    """

    def __init__(
        self,
        bq_client: Any,
        supabase_client: Any,
        local_db: Any,
        crm_twenty_client: Any,
    ) -> None:
        """Initialize BigQuery sync service.
        
        Args:
            bq_client: BigQuery client
            supabase_client: Supabase client
            local_db: Local database connection
            crm_twenty_client: CRM Twenty API client
        """
        self.bq_client = bq_client
        self.supabase = supabase_client
        self.local_db = local_db
        self.crm_twenty = crm_twenty_client

    def sync_contact_to_all(self, contact_id: str) -> Dict[str, Any]:
        """Sync a single contact from BigQuery to all systems.
        
        Args:
            contact_id: Contact ID in BigQuery
            
        Returns:
            Dict with sync results for each system
        """
        # 1. Fetch from BigQuery
        contact = self._fetch_from_bigquery(contact_id)
        if not contact:
            return {"error": f"Contact {contact_id} not found in BigQuery"}

        # 2. Sync to Supabase
        supabase_result = self._sync_to_supabase(contact)

        # 3. Sync to Local
        local_result = self._sync_to_local(contact)

        # 4. Sync to CRM Twenty
        crm_result = self._sync_to_crm_twenty(contact)

        return {
            "bigquery": {"status": "synced", "version": contact.get("version", 1)},
            "supabase": supabase_result,
            "local": local_result,
            "crm_twenty": crm_result,
        }

    def sync_all_contacts(
        self, last_sync_time: Optional[datetime] = None, batch_size: int = 100
    ) -> Dict[str, Any]:
        """Sync all contacts modified since last sync.
        
        Args:
            last_sync_time: Last sync timestamp (defaults to 24 hours ago)
            batch_size: Number of contacts to sync per batch
            
        Returns:
            Dict with sync summary
        """
        if not last_sync_time:
            from datetime import timedelta
            last_sync_time = datetime.utcnow() - timedelta(hours=24)

        query = """
        SELECT * FROM `identity.contacts_master`
        WHERE updated_at > @last_sync_time
        ORDER BY updated_at DESC
        LIMIT @batch_size
        """

        job_config = {
            "query_parameters": [
                ("last_sync_time", "TIMESTAMP", last_sync_time.isoformat()),
                ("batch_size", "INT64", batch_size),
            ]
        }

        query_job = self.bq_client.query(query, job_config=job_config)
        contacts = list(query_job.result())

        results = []
        for contact in contacts:
            result = self.sync_contact_to_all(str(contact["contact_id"]))
            results.append(result)

        return {
            "synced": len(results),
            "results": results,
            "last_sync_time": last_sync_time.isoformat(),
        }

    def _fetch_from_bigquery(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Fetch contact from BigQuery.
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Contact record or None
        """
        # Use existing identity.contacts_master table structure
        # Includes: apple_unique_id, name fields, organization, category_code, etc.
        # Extended fields may not exist yet, so we use SAFE_CAST to handle gracefully
        query = """
        SELECT 
          contact_id,
          apple_unique_id,
          first_name,
          last_name,
          middle_name,
          nickname,
          suffix,
          prefix,
          display_name,
          sorting_first_name,
          sorting_last_name,
          organization,
          job_title,
          department,
          category_code,
          subcategory_code,
          notes,
          birthday,
          is_business,
          created_at,
          updated_at,
          -- Extended fields (may not exist yet - use SAFE_CAST to handle gracefully)
          -- Only include if they exist in the schema
          COALESCE(display_name, 
            CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) as canonical_name,
          COALESCE(display_name, 
            CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) as full_name
        FROM `identity.contacts_master`
        WHERE CAST(contact_id AS STRING) = @contact_id
        LIMIT 1
        """

        # contact_id is STRING in BigQuery - always use STRING parameter
        from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
        job_config = QueryJobConfig(
            query_parameters=[
                ScalarQueryParameter("contact_id", "STRING", str(contact_id))
            ]
        )

        query_job = self.bq_client.query(query, job_config=job_config)
        results = list(query_job.result())

        if not results:
            return None

        # Convert BigQuery row to dict
        contact = dict(results[0])
        
        # Ensure canonical_name exists (already handled in query, but double-check)
        if not contact.get("canonical_name"):
            contact["canonical_name"] = contact.get("full_name") or f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()
        
        # Initialize extended fields (may not exist in schema)
        json_fields = ["llm_context", "communication_stats", "social_network", "ai_insights", "recommendations", "sync_metadata"]
        for field in json_fields:
            if field not in contact:
                contact[field] = {}
            elif contact[field] is not None:
                if isinstance(contact[field], str):
                    try:
                        import json
                        contact[field] = json.loads(contact[field])
                    except (json.JSONDecodeError, TypeError):
                        contact[field] = {}
                elif not isinstance(contact[field], dict):
                    contact[field] = {}
            else:
                contact[field] = {}
        
        return contact

    def _sync_to_supabase(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Sync contact to Supabase.
        
        Args:
            contact: Contact record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            # Transform BigQuery format to Supabase format
            supabase_contact = self._transform_bq_to_supabase(contact)

            # Upsert to Supabase
            # Supabase uses contact_id TEXT as unique identifier for sync
            result = (
                self.supabase.table("contacts_master")
                .upsert(supabase_contact, on_conflict="contact_id")
                .execute()
            )

            return {"status": "synced", "supabase_id": result.data[0]["id"]}
        except Exception as e:
            logger.error(f"Failed to sync to Supabase: {e}")
            return {"status": "error", "error": str(e)}

    def _sync_to_local(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Sync contact to local database.
        
        Args:
            contact: Contact record from BigQuery
            
        Returns:
            Sync result
        """
        try:
            # Transform BigQuery format to local format
            local_contact = self._transform_bq_to_local(contact)

            # Upsert to local DB with ALL fields
            cursor = self.local_db.cursor()
            cursor.execute(
                """
                INSERT INTO contacts_master (
                    contact_id, canonical_name, name_normalized,
                    first_name, last_name, middle_name, nickname,
                    name_suffix, title, full_name,
                    organization, job_title, department,
                    category_code, subcategory_code, relationship_category,
                    notes, birthday, is_business, is_me,
                    llm_context, communication_stats, social_network,
                    ai_insights, recommendations, sync_metadata,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contact_id) DO UPDATE SET
                    canonical_name = excluded.canonical_name,
                    name_normalized = excluded.name_normalized,
                    first_name = excluded.first_name,
                    last_name = excluded.last_name,
                    middle_name = excluded.middle_name,
                    nickname = excluded.nickname,
                    name_suffix = excluded.name_suffix,
                    title = excluded.title,
                    full_name = excluded.full_name,
                    organization = excluded.organization,
                    job_title = excluded.job_title,
                    department = excluded.department,
                    category_code = excluded.category_code,
                    subcategory_code = excluded.subcategory_code,
                    relationship_category = excluded.relationship_category,
                    notes = excluded.notes,
                    birthday = excluded.birthday,
                    is_business = excluded.is_business,
                    is_me = excluded.is_me,
                    llm_context = excluded.llm_context,
                    communication_stats = excluded.communication_stats,
                    social_network = excluded.social_network,
                    ai_insights = excluded.ai_insights,
                    recommendations = excluded.recommendations,
                    sync_metadata = excluded.sync_metadata,
                    updated_at = excluded.updated_at
                """,
                (
                    local_contact["contact_id"],
                    local_contact["canonical_name"],
                    local_contact.get("name_normalized"),
                    local_contact.get("first_name"),
                    local_contact.get("last_name"),
                    local_contact.get("middle_name"),
                    local_contact.get("nickname"),
                    local_contact.get("name_suffix"),
                    local_contact.get("title"),
                    local_contact.get("full_name"),
                    local_contact.get("organization"),
                    local_contact.get("job_title"),
                    local_contact.get("department"),
                    local_contact.get("category_code"),
                    local_contact.get("subcategory_code"),
                    local_contact.get("relationship_category"),
                    local_contact.get("notes"),
                    local_contact.get("birthday"),
                    local_contact.get("is_business", False),
                    local_contact.get("is_me", False),
                    local_contact.get("llm_context", "{}"),
                    local_contact.get("communication_stats", "{}"),
                    local_contact.get("social_network", "{}"),
                    local_contact.get("ai_insights", "{}"),
                    local_contact.get("recommendations", "{}"),
                    local_contact.get("sync_metadata", "{}"),
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat(),
                ),
            )
            self.local_db.commit()

            return {"status": "synced"}
        except Exception as e:
            # Local DB may not be configured - log but don't fail entire sync
            logger.warning(f"Failed to sync to local DB (may not be configured): {e}")
            return {"status": "error", "error": str(e)}

    def _sync_to_crm_twenty(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Sync contact to CRM Twenty.
        
        Uses TwentyCRMClient which gets API key from secrets manager.
        
        Args:
            contact: Contact record from BigQuery
            
        Returns:
            Sync result
        """
        if not self.crm_twenty:
            logger.warning("CRM Twenty client not configured, skipping sync")
            return {"status": "skipped", "error": "CRM client not configured"}
        
        try:
            contact_id = contact.get("contact_id")
            contact_name = contact.get("canonical_name") or contact.get("full_name") or "Unknown"
            
            logger.info(f"Syncing contact to CRM: {contact_name} (ID: {contact_id})")
            
            # Transform BigQuery format to CRM Twenty format
            crm_contact = self._transform_bq_to_crm_twenty(contact)
            
            logger.debug(f"Transformed contact data: name={crm_contact.get('name')}, "
                        f"email={crm_contact.get('email')}, "
                        f"customFields count={len(crm_contact.get('customFields', {}))}")

            # Upsert to CRM Twenty
            logger.debug(f"Calling upsert_contact for contact_id: {contact_id}")
            result = self.crm_twenty.upsert_contact(crm_contact)
            
            crm_id = result.get("id")
            if not crm_id:
                raise ValueError(f"Upsert returned no ID: {result}")

            logger.info(f"✅ Successfully synced contact {contact_name} to CRM (CRM ID: {crm_id})")
            return {"status": "synced", "crm_id": crm_id}
        except Exception as e:
            error_msg = f"Failed to sync contact to CRM Twenty: {e}"
            logger.error(error_msg, exc_info=True)
            # Don't fail entire sync if CRM sync fails - return error but continue
            return {"status": "error", "error": error_msg}

    def _transform_bq_to_supabase(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery contact to Supabase format.
        
        Aligns with existing identity.contacts_master structure.
        """
        import json

        # Use canonical_name or derive from full_name
        canonical_name = contact.get("canonical_name") or contact.get("full_name") or \
            f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()

        return {
            "contact_id": str(contact["contact_id"]),
            "canonical_name": canonical_name,
            "name_normalized": contact.get("name_normalized"),
            "first_name": contact.get("first_name"),
            "last_name": contact.get("last_name"),
            "middle_name": contact.get("middle_name"),
            "nickname": contact.get("nickname"),
            "name_suffix": contact.get("name_suffix"),
            "title": contact.get("title"),
            "full_name": contact.get("full_name"),
            "organization": contact.get("organization"),
            "job_title": contact.get("job_title"),
            "department": contact.get("department"),
            "category_code": contact.get("category_code"),
            "subcategory_code": contact.get("subcategory_code"),
            "relationship_category": contact.get("relationship_category"),
            "notes": contact.get("notes"),
            "birthday": contact.get("birthday"),
            "is_business": contact.get("is_business", False),
            "is_me": contact.get("is_me", False),
            # Extended fields
            "llm_context": json.dumps(contact.get("llm_context", {})),
            "communication_stats": json.dumps(contact.get("communication_stats", {})),
            "social_network": json.dumps(contact.get("social_network", {})),
            "ai_insights": json.dumps(contact.get("ai_insights", {})),
            "recommendations": json.dumps(contact.get("recommendations", {})),
            "sync_metadata": json.dumps(contact.get("sync_metadata", {})),
        }

    def _transform_bq_to_local(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery contact to local format.
        
        Includes ALL metadata fields for complete local storage.
        Aligns with existing identity.contacts_master structure.
        """
        import json

        canonical_name = contact.get("canonical_name") or contact.get("full_name") or \
            f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()

        return {
            "contact_id": str(contact["contact_id"]),
            "canonical_name": canonical_name,
            "name_normalized": contact.get("name_normalized"),
            "first_name": contact.get("first_name"),
            "last_name": contact.get("last_name"),
            "middle_name": contact.get("middle_name"),
            "nickname": contact.get("nickname"),
            "name_suffix": contact.get("name_suffix"),
            "title": contact.get("title"),
            "full_name": contact.get("full_name"),
            "organization": contact.get("organization"),
            "job_title": contact.get("job_title"),
            "department": contact.get("department"),
            "category_code": contact.get("category_code"),
            "subcategory_code": contact.get("subcategory_code"),
            "relationship_category": contact.get("relationship_category"),
            "notes": contact.get("notes"),
            "birthday": contact.get("birthday"),
            "is_business": contact.get("is_business", False),
            "is_me": contact.get("is_me", False),
            # ALL Extended fields (as JSON strings for local DB)
            "llm_context": json.dumps(contact.get("llm_context", {})),
            "communication_stats": json.dumps(contact.get("communication_stats", {})),
            "social_network": json.dumps(contact.get("social_network", {})),
            "ai_insights": json.dumps(contact.get("ai_insights", {})),
            "recommendations": json.dumps(contact.get("recommendations", {})),
            "sync_metadata": json.dumps(contact.get("sync_metadata", {})),
        }

    def _fetch_contact_identifiers(self, contact_id: str) -> Dict[str, Any]:
        """Fetch contact identifiers (emails, phones) from BigQuery.
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Dict with primary_email and primary_phone
        """
        try:
            query = """
            SELECT 
              identifier_type,
              identifier_value,
              is_primary
            FROM `identity.contact_identifiers`
            WHERE CAST(contact_id AS STRING) = @contact_id
              AND identifier_type IN ('email', 'phone')
            ORDER BY is_primary DESC, identifier_type
            """
            
            # contact_id is STRING in BigQuery
            from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
            job_config = QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("contact_id", "STRING", str(contact_id))
                ]
            )
            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            primary_email = None
            primary_phone = None
            
            for row in results:
                if row.identifier_type == "email" and not primary_email:
                    primary_email = row.identifier_value
                elif row.identifier_type == "phone" and not primary_phone:
                    primary_phone = row.identifier_value
                    
            return {
                "primary_email": primary_email,
                "primary_phone": primary_phone,
            }
        except Exception as e:
            # Table may not exist yet - this is OK, just return None
            logger.debug(f"Contact identifiers table may not exist or query failed: {e}")
            return {"primary_email": None, "primary_phone": None}

    def _fetch_contact_relationships(self, contact_id: str) -> Dict[str, Any]:
        """Fetch people-to-people relationships for a contact.
        
        Enhances social_network field with relationship data.
        
        Args:
            contact_id: Contact ID
            
        Returns:
            Dict with relationships data to merge into social_network
        """
        try:
            query = """
            SELECT 
              person_2_id as related_contact_id,
              relationship_type,
              relationship_subtype,
              is_current,
              relationship_status
            FROM `identity.people_relationships`
            WHERE person_1_id = @contact_id
              AND is_current = TRUE
            UNION ALL
            SELECT 
              person_1_id as related_contact_id,
              relationship_type,
              relationship_subtype,
              is_current,
              relationship_status
            FROM `identity.people_relationships`
            WHERE CAST(person_2_id AS STRING) = @contact_id
              AND is_current = TRUE
            """
            
            # contact_id is STRING in BigQuery
            from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
            job_config = QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("contact_id", "STRING", str(contact_id))
                ]
            )
            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            relationships = []
            for row in results:
                relationships.append({
                    "contact_id": str(row.related_contact_id),
                    "relationship_type": row.relationship_type,
                    "relationship_subtype": row.relationship_subtype,
                    "is_current": row.is_current,
                    "relationship_status": row.relationship_status,
                })
            
            return {
                "people_relationships": relationships,
                "relationship_count": len(relationships),
            }
        except Exception as e:
            # Table may not exist yet - this is OK, just return empty
            logger.debug(f"People relationships table may not exist or query failed: {e}")
            return {"people_relationships": [], "relationship_count": 0}

    def _transform_bq_to_crm_twenty(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Transform BigQuery contact to CRM Twenty format.
        
        Includes ALL contact metadata fields for complete relationship management.
        Aligns with existing identity.contacts_master structure.
        """
        import json

        canonical_name = contact.get("canonical_name") or contact.get("full_name") or \
            f"{contact.get('first_name', '')} {contact.get('last_name', '')}".strip()

        # Fetch contact identifiers (emails, phones)
        identifiers = self._fetch_contact_identifiers(str(contact["contact_id"]))
        
        # Fetch and enhance social_network with relationship data
        social_network = contact.get("social_network", {})
        if not isinstance(social_network, dict):
            try:
                import json
                social_network = json.loads(social_network) if isinstance(social_network, str) else {}
            except:
                social_network = {}
        
        # Merge relationship data into social_network
        relationships_data = self._fetch_contact_relationships(str(contact["contact_id"]))
        if relationships_data.get("people_relationships"):
            social_network["people_relationships"] = relationships_data["people_relationships"]
            social_network["relationship_count"] = relationships_data["relationship_count"]

        # Build customFields with ALL metadata
        custom_fields = {
            # Primary Identifiers
            "contact_id": str(contact["contact_id"]),
            "apple_unique_id": contact.get("apple_unique_id"),
            "apple_identity_unique_id": contact.get("apple_identity_unique_id"),
            
            # Name Components
            "first_name": contact.get("first_name"),
            "last_name": contact.get("last_name"),
            "middle_name": contact.get("middle_name"),
            "nickname": contact.get("nickname"),
            "name_suffix": contact.get("name_suffix"),
            "title": contact.get("title"),
            "full_name": contact.get("full_name"),
            "name_normalized": contact.get("name_normalized"),
            
            # Organization
            "organization": contact.get("organization"),
            "job_title": contact.get("job_title"),
            "department": contact.get("department"),
            
            # Relationship Categorization
            "category_code": contact.get("category_code"),
            "subcategory_code": contact.get("subcategory_code"),
            "relationship_category": contact.get("relationship_category"),
            
            # Metadata
            "notes": contact.get("notes"),
            "birthday": contact.get("birthday"),
            "is_business": contact.get("is_business", False),
            "is_me": contact.get("is_me", False),
            
            # Rich LLM Data (JSON strings)
            "llm_context": json.dumps(contact.get("llm_context", {})),
            "communication_stats": json.dumps(contact.get("communication_stats", {})),
            "social_network": json.dumps(social_network),  # Enhanced with relationships
            "ai_insights": json.dumps(contact.get("ai_insights", {})),
            "recommendations": json.dumps(contact.get("recommendations", {})),
            
            # Sync Metadata
            "sync_metadata": json.dumps(contact.get("sync_metadata", {})),
        }
        
        # Remove None values and empty strings to avoid sending empty fields
        # But keep False/0 values as they are valid
        custom_fields = {
            k: v for k, v in custom_fields.items() 
            if v is not None and v != "" and v != "null"
        }
        
        # Ensure we have at least contact_id in customFields
        if "contact_id" not in custom_fields:
            custom_fields["contact_id"] = str(contact["contact_id"])

        # Twenty CRM expects "name" as object with firstName/lastName
        # Start with basic fields only - custom fields may need to be set up first
        result = {
            "name": {
                "firstName": contact.get("first_name") or "",
                "lastName": contact.get("last_name") or "",
            },
        }
        
        # If no first/last name, use display name as firstName
        if not result["name"]["firstName"] and not result["name"]["lastName"]:
            result["name"]["firstName"] = canonical_name or "Contact"
        
        # Add email if available (Twenty CRM native fields)
        if identifiers.get("primary_email"):
            result["emails"] = {
                "primaryEmail": identifiers.get("primary_email"),
                "additionalEmails": []
            }
        # Phone uses phones object, not phone field
        if identifiers.get("primary_phone"):
            result["phones"] = {
                "primaryPhoneNumber": identifiers.get("primary_phone"),
                "primaryPhoneCountryCode": "",
                "primaryPhoneCallingCode": "",
                "additionalPhones": []
            }
        
        # Try to add custom fields - but only if they're set up
        # For now, skip customFields and add them in a separate update if needed
        # result.update(custom_fields)
        
        logger.debug(f"Transformed contact for CRM: name={result.get('name')}, "
                    f"email={result.get('email')}, "
                    f"customFields={len(custom_fields)} fields")
        
        return result
