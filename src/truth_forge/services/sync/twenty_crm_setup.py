"""Twenty CRM Setup Service.

Sets up custom fields and data model in Twenty CRM.
Run this once to initialize the CRM with our schema.
"""

from typing import Dict, Any, List, Optional
import logging

from truth_forge.services.sync.twenty_crm_client import TwentyCRMClient
from truth_forge.services.secret.service import SecretService

logger = logging.getLogger(__name__)


class TwentyCRMSetup:
    """Sets up Twenty CRM with our data model.
    
    Creates custom fields for:
    - Contacts (contact_id, category_code, llm_context, etc.)
    - Companies (business_id, industry, llm_context, etc.)
    - Relationships (relationship_id, relationship_type, etc.)
    """

    def __init__(self, client: Optional[TwentyCRMClient] = None) -> None:
        """Initialize setup service.
        
        Args:
            client: TwentyCRMClient instance (optional, will create if not provided)
        """
        self.client = client or TwentyCRMClient()

    def setup_all(self) -> Dict[str, Any]:
        """Set up all custom fields and data model.
        
        Returns:
            Setup results
        """
        results = {
            "person_fields": self.setup_person_custom_fields(),
            "company_fields": self.setup_company_custom_fields(),
            "status": "complete",
        }

        return results

    def setup_person_custom_fields(self) -> List[Dict[str, Any]]:
        """Set up custom fields for persons (contacts).
        
        Returns:
            List of created field definitions
        """
        fields = [
            # Primary Identifiers
            {
                "name": "contact_id",
                "label": "Contact ID",
                "type": "TEXT",
                "description": "Canonical contact ID from BigQuery",
                "isRequired": False,
            },
            {
                "name": "apple_unique_id",
                "label": "Apple Unique ID",
                "type": "TEXT",
                "description": "Apple Contacts ZUNIQUEID",
                "isRequired": False,
            },
            {
                "name": "apple_identity_unique_id",
                "label": "Apple Identity Unique ID",
                "type": "TEXT",
                "description": "Apple Contacts ZIDENTITYUNIQUEID",
                "isRequired": False,
            },
            # Name Components
            {
                "name": "first_name",
                "label": "First Name",
                "type": "TEXT",
                "description": "First name",
                "isRequired": False,
            },
            {
                "name": "last_name",
                "label": "Last Name",
                "type": "TEXT",
                "description": "Last name",
                "isRequired": False,
            },
            {
                "name": "middle_name",
                "label": "Middle Name",
                "type": "TEXT",
                "description": "Middle name",
                "isRequired": False,
            },
            {
                "name": "nickname",
                "label": "Nickname",
                "type": "TEXT",
                "description": "Nickname",
                "isRequired": False,
            },
            {
                "name": "name_suffix",
                "label": "Name Suffix",
                "type": "TEXT",
                "description": "Name suffix (Jr., Sr., III, etc.)",
                "isRequired": False,
            },
            {
                "name": "title",
                "label": "Title",
                "type": "TEXT",
                "description": "Title (Mr., Mrs., Dr., etc.)",
                "isRequired": False,
            },
            {
                "name": "full_name",
                "label": "Full Name",
                "type": "TEXT",
                "description": "Full name",
                "isRequired": False,
            },
            {
                "name": "name_normalized",
                "label": "Name Normalized",
                "type": "TEXT",
                "description": "Normalized name for searching",
                "isRequired": False,
            },
            # Organization
            {
                "name": "organization",
                "label": "Organization",
                "type": "TEXT",
                "description": "Organization name",
                "isRequired": False,
            },
            {
                "name": "job_title",
                "label": "Job Title",
                "type": "TEXT",
                "description": "Job title",
                "isRequired": False,
            },
            {
                "name": "department",
                "label": "Department",
                "type": "TEXT",
                "description": "Department",
                "isRequired": False,
            },
            # Relationship Categorization
            {
                "name": "category_code",
                "label": "Category Code",
                "type": "SELECT",
                "options": ["A", "B", "C", "D", "E", "F", "G", "H", "X"],
                "description": "Relationship category code",
                "isRequired": False,
            },
            {
                "name": "subcategory_code",
                "label": "Subcategory Code",
                "type": "TEXT",
                "description": "Full subcategory code (e.g., A1_IMMEDIATE_FAMILY_RAISED_TOGETHER)",
                "isRequired": False,
            },
            {
                "name": "relationship_category",
                "label": "Relationship Category",
                "type": "SELECT",
                "options": [
                    "family",
                    "friend",
                    "romantic",
                    "professional",
                    "acquaintance",
                    "ex_romantic",
                    "service_provider",
                    "hostile",
                ],
                "description": "Relationship category",
                "isRequired": False,
            },
            # Metadata
            {
                "name": "notes",
                "label": "Notes",
                "type": "TEXT",
                "description": "Contact notes",
                "isRequired": False,
            },
            {
                "name": "birthday",
                "label": "Birthday",
                "type": "DATE",
                "description": "Birthday",
                "isRequired": False,
            },
            {
                "name": "is_business",
                "label": "Is Business",
                "type": "BOOLEAN",
                "description": "True if this is a business contact",
                "isRequired": False,
            },
            {
                "name": "is_me",
                "label": "Is Me",
                "type": "BOOLEAN",
                "description": "True if this is Jeremy",
                "isRequired": False,
            },
            # Rich LLM Data
            {
                "name": "llm_context",
                "label": "LLM Context",
                "type": "TEXT",
                "description": "Rich LLM context data (JSON string)",
                "isRequired": False,
            },
            {
                "name": "communication_stats",
                "label": "Communication Stats",
                "type": "TEXT",
                "description": "Communication statistics (JSON string)",
                "isRequired": False,
            },
            {
                "name": "social_network",
                "label": "Social Network",
                "type": "TEXT",
                "description": "Social network context (JSON string)",
                "isRequired": False,
            },
            {
                "name": "ai_insights",
                "label": "AI Insights",
                "type": "TEXT",
                "description": "AI-generated insights (JSON string)",
                "isRequired": False,
            },
            {
                "name": "recommendations",
                "label": "Recommendations",
                "type": "TEXT",
                "description": "AI recommendations (JSON string)",
                "isRequired": False,
            },
            # Sync Metadata
            {
                "name": "sync_metadata",
                "label": "Sync Metadata",
                "type": "TEXT",
                "description": "Sync metadata (JSON string)",
                "isRequired": False,
            },
        ]

        created_fields = []
        existing_fields = {
            field["name"]: field
            for field in self.client.list_custom_fields("person")
        }

        for field_def in fields:
            field_name = field_def["name"]
            if field_name in existing_fields:
                logger.info(f"Custom field '{field_name}' already exists, skipping")
                created_fields.append(existing_fields[field_name])
            else:
                try:
                    created = self.client.create_custom_field("person", field_def)
                    created_fields.append(created)
                    logger.info(f"Created custom field: {field_name}")
                except Exception as e:
                    logger.error(f"Failed to create field '{field_name}': {e}")

        return created_fields

    def setup_company_custom_fields(self) -> List[Dict[str, Any]]:
        """Set up custom fields for companies (businesses).
        
        Returns:
            List of created field definitions
        """
        fields = [
            {
                "name": "business_id",
                "label": "Business ID",
                "type": "TEXT",
                "description": "Canonical business ID from BigQuery",
                "isRequired": False,
            },
            {
                "name": "industry",
                "label": "Industry",
                "type": "TEXT",
                "description": "Business industry",
                "isRequired": False,
            },
            {
                "name": "business_type",
                "label": "Business Type",
                "type": "SELECT",
                "options": ["LLC", "Corp", "Partnership", "Sole Proprietorship", "Other"],
                "description": "Legal business type",
                "isRequired": False,
            },
            {
                "name": "llm_context",
                "label": "LLM Context",
                "type": "TEXT",
                "description": "Rich LLM context data (JSON string)",
                "isRequired": False,
            },
            {
                "name": "business_data",
                "label": "Business Data",
                "type": "TEXT",
                "description": "Business data (JSON string)",
                "isRequired": False,
            },
            {
                "name": "relationship_stats",
                "label": "Relationship Stats",
                "type": "TEXT",
                "description": "Relationship statistics (JSON string)",
                "isRequired": False,
            },
            {
                "name": "sync_metadata",
                "label": "Sync Metadata",
                "type": "TEXT",
                "description": "Sync metadata (JSON string)",
                "isRequired": False,
            },
        ]

        created_fields = []
        existing_fields = {
            field["name"]: field
            for field in self.client.list_custom_fields("company")
        }

        for field_def in fields:
            field_name = field_def["name"]
            if field_name in existing_fields:
                logger.info(f"Custom field '{field_name}' already exists, skipping")
                created_fields.append(existing_fields[field_name])
            else:
                try:
                    created = self.client.create_custom_field("company", field_def)
                    created_fields.append(created)
                    logger.info(f"Created custom field: {field_name}")
                except Exception as e:
                    logger.error(f"Failed to create field '{field_name}': {e}")

        return created_fields

    def verify_setup(self) -> Dict[str, Any]:
        """Verify that all custom fields are set up correctly.
        
        Returns:
            Verification results
        """
        person_fields = self.client.list_custom_fields("person")
        company_fields = self.client.list_custom_fields("company")

        required_person_fields = {
            "contact_id",
            "category_code",
            "subcategory_code",
            "relationship_category",
            "llm_context",
            "sync_metadata",
        }

        required_company_fields = {
            "business_id",
            "industry",
            "llm_context",
            "sync_metadata",
        }

        person_field_names = {field["name"] for field in person_fields}
        company_field_names = {field["name"] for field in company_fields}

        missing_person = required_person_fields - person_field_names
        missing_company = required_company_fields - company_field_names

        return {
            "person_fields": {
                "total": len(person_fields),
                "required": len(required_person_fields),
                "missing": list(missing_person),
                "complete": len(missing_person) == 0,
            },
            "company_fields": {
                "total": len(company_fields),
                "required": len(required_company_fields),
                "missing": list(missing_company),
                "complete": len(missing_company) == 0,
            },
            "all_complete": len(missing_person) == 0 and len(missing_company) == 0,
        }


