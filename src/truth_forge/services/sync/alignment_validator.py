"""Alignment validation service for multi-source contact sync."""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AlignmentValidator:
    """Validates alignment between contact records across systems.
    
    Ensures data consistency and identifies drift between systems.
    """

    def __init__(self) -> None:
        """Initialize alignment validator."""
        self.category_codes = {"A", "B", "C", "D", "E", "F", "G", "H", "X"}

    def validate_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a contact record against alignment standards.
        
        Args:
            contact: Contact record to validate
            
        Returns:
            Validation result with errors and warnings
        """
        errors = []
        warnings = []

        # Required fields
        if not contact.get("contact_id"):
            errors.append("Missing required field: contact_id")
        if not contact.get("canonical_name"):
            errors.append("Missing required field: canonical_name")

        # Category code validation
        category_code = contact.get("category_code")
        if category_code and category_code not in self.category_codes:
            errors.append(
                f"Invalid category_code: {category_code}. Must be one of {self.category_codes}"
            )

        # Subcategory code validation
        subcategory_code = contact.get("subcategory_code")
        if subcategory_code:
            if not category_code:
                warnings.append(
                    "subcategory_code provided but category_code missing"
                )
            elif not subcategory_code.startswith(category_code):
                errors.append(
                    f"subcategory_code {subcategory_code} does not match category_code {category_code}"
                )

        # Sync metadata validation
        sync_metadata = contact.get("sync_metadata", {})
        if not sync_metadata.get("version"):
            warnings.append("Missing sync_metadata.version")
        if not sync_metadata.get("last_updated"):
            warnings.append("Missing sync_metadata.last_updated")
        if not sync_metadata.get("last_updated_by"):
            warnings.append("Missing sync_metadata.last_updated_by")

        # Type validation
        if contact.get("is_business") and not isinstance(contact["is_business"], bool):
            errors.append("is_business must be boolean")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def compare_contacts(
        self, contact1: Dict[str, Any], contact2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two contact records and identify differences.
        
        Args:
            contact1: First contact record
            contact2: Second contact record
            
        Returns:
            Comparison result with differences
        """
        differences = []

        # Compare key fields
        key_fields = [
            "contact_id",
            "canonical_name",
            "category_code",
            "subcategory_code",
            "organization",
        ]

        for field in key_fields:
            val1 = contact1.get(field)
            val2 = contact2.get(field)
            if val1 != val2:
                differences.append(
                    {
                        "field": field,
                        "value1": val1,
                        "value2": val2,
                    }
                )

        # Compare sync metadata
        meta1 = contact1.get("sync_metadata", {})
        meta2 = contact2.get("sync_metadata", {})
        if meta1.get("version") != meta2.get("version"):
            differences.append(
                {
                    "field": "sync_metadata.version",
                    "value1": meta1.get("version"),
                    "value2": meta2.get("version"),
                }
            )

        return {
            "aligned": len(differences) == 0,
            "differences": differences,
        }

    def validate_alignment(
        self,
        bigquery_contact: Dict[str, Any],
        supabase_contact: Optional[Dict[str, Any]] = None,
        local_contact: Optional[Dict[str, Any]] = None,
        crm_contact: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Validate alignment across all systems.
        
        Args:
            bigquery_contact: Contact from BigQuery (canonical)
            supabase_contact: Contact from Supabase
            local_contact: Contact from local DB
            crm_contact: Contact from CRM Twenty
            
        Returns:
            Alignment validation result
        """
        results = {
            "bigquery": self.validate_contact(bigquery_contact),
            "alignment": {},
        }

        # Compare with other systems
        if supabase_contact:
            results["supabase"] = self.validate_contact(supabase_contact)
            results["alignment"]["bigquery_vs_supabase"] = self.compare_contacts(
                bigquery_contact, supabase_contact
            )

        if local_contact:
            results["local"] = self.validate_contact(local_contact)
            results["alignment"]["bigquery_vs_local"] = self.compare_contacts(
                bigquery_contact, local_contact
            )

        if crm_contact:
            results["crm_twenty"] = self.validate_contact(crm_contact)
            results["alignment"]["bigquery_vs_crm"] = self.compare_contacts(
                bigquery_contact, crm_contact
            )

        # Overall alignment status
        all_aligned = all(
            comp.get("aligned", False)
            for comp in results["alignment"].values()
        )

        results["overall_aligned"] = all_aligned

        return results
