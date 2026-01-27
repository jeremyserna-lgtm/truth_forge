"""Twenty CRM API Client.

Handles all interactions with Twenty CRM API.
Uses API key from secrets manager.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import json

import requests

from truth_forge.core.settings import settings
from truth_forge.services.secret.service import SecretService

logger = logging.getLogger(__name__)


class TwentyCRMClient:
    """Client for Twenty CRM API.
    
    Handles contacts, companies (businesses), and relationships.
    Uses API key from secrets manager.
    """

    def __init__(self, secret_service: Optional[SecretService] = None) -> None:
        """Initialize Twenty CRM client.
        
        Args:
            secret_service: SecretService instance (optional, will create if not provided)
        """
        self.secret_service = secret_service or SecretService()
        self.base_url = settings.twenty_base_url.rstrip("/")
        self.api_key = self._get_api_key()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.timeout = 30.0

    def _get_api_key(self) -> str:
        """Get Twenty CRM API key from secrets manager.
        
        Uses SecretService with multiple name variations for maximum compatibility.
        
        Returns:
            API key string
            
        Raises:
            ValueError: If API key cannot be retrieved
        """
        # Primary secret name (actual GCP secret name)
        primary_secret = "Twenty_CRM"
        
        # Alternative secret name variations (fallbacks)
        secret_variants = [
            "twenty-crm-api-key",   # Hyphen format
            "twenty_crm_api_key",   # Snake case
            "twenty_api_key",       # Short version
            "TWENTY_CRM_API_KEY",   # Uppercase
            "TWENTY_API_KEY",       # Uppercase short
            "twenty-api-key",       # Alternative hyphen
        ]

        # Try using SecretService with variants
        try:
            api_key = self.secret_service.get_secret_with_variants(
                primary_secret,
                secret_variants
            )
            if api_key and not api_key.startswith("mock_"):
                logger.info(f"✅ Retrieved Twenty CRM API key from secrets manager")
                return api_key
            elif api_key and api_key.startswith("mock_"):
                logger.warning("Secret service returned mock value (GCP_PROJECT_ID may not be set)")
        except Exception as e:
            logger.debug(f"Secret service retrieval failed: {e}")

        # Fallback to environment variable
        import os
        env_key = os.getenv("TWENTY_CRM_API_KEY") or os.getenv("TWENTY_API_KEY")
        if env_key:
            logger.info("✅ Using Twenty CRM API key from environment variable")
            return env_key

        # Provide helpful error message
        all_names = [primary_secret] + secret_variants
        error_msg = (
            "Twenty CRM API key not found in secrets manager or environment variables.\n"
            f"Tried secret names: {', '.join(all_names)}\n"
            "Tried environment variables: TWENTY_CRM_API_KEY, TWENTY_API_KEY\n\n"
            "To create the secret, run:\n"
            "  export PROJECT_ID=flash-clover-464719-g1\n"
            "  echo -n 'your-api-key-here' | gcloud secrets create twenty-crm-api-key \\\n"
            "    --data-file=- \\\n"
            "    --project=$PROJECT_ID\n\n"
            "Or verify existing secrets with:\n"
            "  python scripts/verify_api_key_secret.py"
        )
        raise ValueError(error_msg)

    # ============================================================================
    # CONTACTS
    # ============================================================================

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get a contact by ID.
        
        Args:
            contact_id: Twenty CRM contact ID
            
        Returns:
            Contact record
        """
        endpoint = f"{self.base_url}/rest/people/{contact_id}"
        response = requests.get(
            endpoint,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_contacts(
        self, updated_since: Optional[datetime] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List contacts.
        
        Args:
            updated_since: Only return contacts updated since this time
            limit: Maximum number of contacts to return
            
        Returns:
            List of contact records
        """
        params = {"limit": limit}
        if updated_since:
            params["updatedAfter"] = updated_since.isoformat()

        endpoint = f"{self.base_url}/rest/people"
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        result = response.json()
        
        # Handle different response formats
        if isinstance(result, list):
            # Ensure all items are dicts
            return [item if isinstance(item, dict) else {} for item in result]
        elif isinstance(result, dict):
            # Try common keys (people, data, results, items)
            data = result.get("people") or result.get("data") or result.get("results") or result.get("items") or []
            if isinstance(data, list):
                # Ensure all items are dicts
                return [item if isinstance(item, dict) else {} for item in data]
            elif isinstance(data, dict):
                # Single item wrapped in dict
                return [data]
            else:
                logger.warning(f"Unexpected data format: {type(data)}")
                return []
        else:
            logger.warning(f"Unexpected response type: {type(result)}")
            return []

    def create_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact.
        
        Args:
            contact_data: Contact data in Twenty CRM format
            
        Returns:
            Created contact record
        """
        # Twenty CRM API endpoint for creating people
        # Note: Twenty uses /rest/ or /graphql/ endpoints, but may also support /api/
        # Adjust endpoint if needed based on your Twenty instance
        endpoint = f"{self.base_url}/rest/people"
        
        logger.debug(f"Creating contact in CRM: {contact_data.get('name')}")
        logger.debug(f"POST {endpoint}")
        logger.debug(f"Request data keys: {list(contact_data.keys())}")
        logger.debug(f"CustomFields count: {len(contact_data.get('customFields', {}))}")
        
        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                json=contact_data,
                timeout=self.timeout,
            )
            response.raise_for_status()
            result = response.json()
            
            # Handle GraphQL-style response: {"data": {"createPerson": {...}}}
            if isinstance(result, dict) and "data" in result:
                create_person = result.get("data", {}).get("createPerson")
                if create_person:
                    result = create_person
            
            # Extract ID from nested structure if needed
            contact_id = result.get("id")
            if not contact_id and isinstance(result, dict):
                # Try nested paths
                contact_id = result.get("data", {}).get("id") or result.get("createPerson", {}).get("id")
            
            logger.info(f"✅ Created contact in CRM: {contact_id} - {contact_data.get('name', {}).get('firstName', 'Unknown')}")
            return result
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ HTTP error creating contact: {e}")
            logger.error(f"Response status: {response.status_code}")
            logger.error(f"Response body: {response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Error creating contact: {e}", exc_info=True)
            raise

    def update_contact(
        self, contact_id: str, contact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing contact.
        
        Args:
            contact_id: Twenty CRM contact ID
            contact_data: Updated contact data
            
        Returns:
            Updated contact record
        """
        endpoint = f"{self.base_url}/rest/people/{contact_id}"
        response = requests.patch(
            endpoint,
            headers=self.headers,
            json=contact_data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def upsert_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert a contact (create or update).
        
        Uses customFields.contact_id to find existing contact.
        Also syncs email and phone from contact_data.
        
        Args:
            contact_data: Contact data in Twenty CRM format
            
        Returns:
            Contact record (created or updated)
        """
        # Try to find existing contact by contact_id in customFields
        contact_id = contact_data.get("customFields", {}).get("contact_id")
        if contact_id:
            # Search for existing contact
            existing = self._find_contact_by_custom_id(contact_id)
            if existing:
                result = self.update_contact(existing["id"], contact_data)
                # Update email/phone if provided
                if contact_data.get("email") or contact_data.get("phone"):
                    self._update_contact_identifiers(
                        existing["id"],
                        email=contact_data.get("email"),
                        phone=contact_data.get("phone"),
                    )
                return result

        # Create new contact
        logger.info(f"Creating new contact in CRM (contact_id: {contact_id})")
        result = self.create_contact(contact_data)
        
        # Verify contact was created - handle GraphQL response format
        contact_id = result.get("id")
        if not contact_id and isinstance(result, dict):
            # Try nested paths for GraphQL responses
            contact_id = result.get("data", {}).get("createPerson", {}).get("id") or result.get("data", {}).get("id")
        
        if not contact_id:
            raise ValueError(f"Contact creation failed - no ID returned: {result}")
        
        # Ensure result has id at top level for consistency
        if not result.get("id"):
            result["id"] = contact_id
        
        logger.info(f"✅ Contact created successfully: {result.get('id')}")
        
        # Update email/phone if provided
        if contact_data.get("email") or contact_data.get("phone"):
            self._update_contact_identifiers(
                result["id"],
                email=contact_data.get("email"),
                phone=contact_data.get("phone"),
            )
        return result

    def _update_contact_identifiers(
        self, crm_contact_id: str, email: Optional[str] = None, phone: Optional[str] = None
    ) -> None:
        """Update contact email and phone identifiers.
        
        Args:
            crm_contact_id: Twenty CRM contact ID
            email: Email address
            phone: Phone number
        """
        update_data = {}
        if email:
            update_data["email"] = email
        if phone:
            update_data["phone"] = phone

        if update_data:
            try:
                self.update_contact(crm_contact_id, update_data)
            except Exception as e:
                # Non-critical - identifiers may not be updatable separately
                logger.debug(f"Failed to update contact identifiers (may not be supported): {e}")

    def _find_contact_by_custom_id(self, contact_id: str) -> Optional[Dict[str, Any]]:
        """Find contact by customFields.contact_id.
        
        Args:
            contact_id: Our canonical contact_id
            
        Returns:
            Contact record or None
        """
        # Note: This requires a search endpoint or filtering
        # For now, we'll try to get by ID if contact_id is numeric
        # In production, you'd use Twenty's search/filter API
        try:
            # Try as direct ID first
            return self.get_contact(contact_id)
        except requests.exceptions.HTTPError:
            # Not found, search in list
            contacts = self.list_contacts(limit=1000)
            for contact in contacts:
                # Ensure contact is a dict
                if not isinstance(contact, dict):
                    continue
                custom_fields = contact.get("customFields", {})
                if isinstance(custom_fields, dict) and custom_fields.get("contact_id") == contact_id:
                    return contact
            return None

    # ============================================================================
    # COMPANIES (BUSINESSES)
    # ============================================================================

    def get_company(self, company_id: str) -> Dict[str, Any]:
        """Get a company by ID.
        
        Args:
            company_id: Twenty CRM company ID
            
        Returns:
            Company record
        """
        endpoint = f"{self.base_url}/rest/companies/{company_id}"
        response = requests.get(
            endpoint,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_companies(
        self, updated_since: Optional[datetime] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List companies.
        
        Args:
            updated_since: Only return companies updated since this time
            limit: Maximum number of companies to return
            
        Returns:
            List of company records
        """
        params = {"limit": limit}
        if updated_since:
            params["updatedAfter"] = updated_since.isoformat()

        endpoint = f"{self.base_url}/rest/companies"
        response = requests.get(
            endpoint,
            headers=self.headers,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("data", [])

    def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company.
        
        Args:
            company_data: Company data in Twenty CRM format
            
        Returns:
            Created company record
        """
        endpoint = f"{self.base_url}/rest/companies"
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=company_data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def update_company(
        self, company_id: str, company_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing company.
        
        Args:
            company_id: Twenty CRM company ID
            company_data: Updated company data
            
        Returns:
            Updated company record
        """
        endpoint = f"{self.base_url}/rest/companies/{company_id}"
        response = requests.patch(
            endpoint,
            headers=self.headers,
            json=company_data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def upsert_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upsert a company (create or update).
        
        Uses customFields.business_id to find existing company.
        
        Args:
            company_data: Company data in Twenty CRM format
            
        Returns:
            Company record (created or updated)
        """
        business_id = company_data.get("customFields", {}).get("business_id")
        if business_id:
            existing = self._find_company_by_custom_id(business_id)
            if existing:
                return self.update_company(existing["id"], company_data)

        return self.create_company(company_data)

    def _find_company_by_custom_id(
        self, business_id: str
    ) -> Optional[Dict[str, Any]]:
        """Find company by customFields.business_id.
        
        Args:
            business_id: Our canonical business_id
            
        Returns:
            Company record or None
        """
        try:
            return self.get_company(business_id)
        except requests.exceptions.HTTPError:
            companies = self.list_companies(limit=1000)
            for company in companies:
                if company.get("customFields", {}).get("business_id") == business_id:
                    return company
            return None

    # ============================================================================
    # RELATIONSHIPS
    # ============================================================================

    def create_relationship(self, relationship_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a relationship between person and company.
        
        Args:
            relationship_data: Relationship data in Twenty CRM format
            
        Returns:
            Created relationship record
        """
        endpoint = f"{self.base_url}/rest/people-company-relationships"
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=relationship_data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def upsert_relationship(
        self, relationship_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upsert a relationship.
        
        Args:
            relationship_data: Relationship data
            
        Returns:
            Relationship record
        """
        # Twenty CRM may not have direct upsert, so we create
        # In production, you'd check for existing first
        return self.create_relationship(relationship_data)

    def get_person_relationships(self, person_id: str) -> List[Dict[str, Any]]:
        """Get all relationships for a person.
        
        Args:
            person_id: Twenty CRM person ID
            
        Returns:
            List of relationship records
        """
        endpoint = f"{self.base_url}/rest/people/{person_id}/relationships"
        response = requests.get(
            endpoint,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("data", [])

    # ============================================================================
    # CUSTOM FIELDS
    # ============================================================================

    def create_custom_field(
        self, object_type: str, field_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a custom field in Twenty CRM.
        
        Args:
            object_type: 'person' or 'company'
            field_data: Field definition
            
        Returns:
            Created field record
        """
        endpoint = f"{self.base_url}/rest/{object_type}-custom-fields"
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=field_data,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def list_custom_fields(self, object_type: str) -> List[Dict[str, Any]]:
        """List custom fields for an object type.
        
        Args:
            object_type: 'person' or 'company'
            
        Returns:
            List of custom field definitions
        """
        endpoint = f"{self.base_url}/rest/{object_type}-custom-fields"
        response = requests.get(
            endpoint,
            headers=self.headers,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json().get("data", [])

    def close(self) -> None:
        """Close the HTTP client.
        
        Note: requests doesn't require explicit closing, but we keep
        this method for API consistency and future async support.
        """
        # requests library doesn't require explicit closing
        # but we keep this for API consistency
        pass

    def __enter__(self) -> "TwentyCRMClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
