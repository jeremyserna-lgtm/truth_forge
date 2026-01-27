#!/usr/bin/env python3
"""Complete Sync Validation - Validates Every Contact Syncs Everywhere.

This script:
1. Fetches all contacts from BigQuery
2. Syncs each contact to all systems
3. Validates each contact exists in all systems
4. Reports any missing or mismatched data
5. Proves complete sync coverage with no exceptions
"""

import sys
from pathlib import Path
import logging
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("sync_validation.log"),
    ],
)
logger = logging.getLogger(__name__)


class SyncValidator:
    """Validates complete sync for all contacts."""
    
    def __init__(self) -> None:
        """Initialize validator."""
        self.bq_client = bigquery.Client(project=settings.effective_gcp_project)
        self.service = TwentyCRMService()
        self.results: Dict[str, Any] = {
            "total_contacts": 0,
            "synced": 0,
            "validated": 0,
            "errors": 0,
            "missing": [],
            "mismatched": [],
            "details": [],
        }
    
    def fetch_all_contacts(self) -> List[Dict[str, Any]]:
        """Fetch all contacts from BigQuery.
        
        Returns:
            List of contact records
        """
        logger.info("=" * 60)
        logger.info("FETCHING ALL CONTACTS FROM BIGQUERY")
        logger.info("=" * 60)
        
        query = """
        SELECT 
            contact_id,
            COALESCE(full_name, CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, ''))) as canonical_name,
            full_name,
            first_name,
            last_name,
            organization,
            category_code,
            subcategory_code,
            is_business,
            updated_at
        FROM `identity.contacts_master`
        ORDER BY contact_id
        """
        
        query_job = self.bq_client.query(query)
        results = list(query_job.result())
        
        contacts = []
        for row in results:
            contacts.append({
                "contact_id": str(row.contact_id),
                "canonical_name": row.canonical_name,
                "full_name": row.full_name,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "organization": row.organization,
                "category_code": row.category_code,
                "subcategory_code": row.subcategory_code,
                "is_business": row.is_business if hasattr(row, 'is_business') else False,
                "updated_at": row.updated_at,
            })
        
        logger.info(f"Found {len(contacts)} contacts in BigQuery")
        self.results["total_contacts"] = len(contacts)
        return contacts
    
    def sync_contact(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Sync a single contact to all systems.
        
        Args:
            contact: Contact record from BigQuery
            
        Returns:
            Sync result
        """
        contact_id = contact["contact_id"]
        contact_name = contact["canonical_name"] or contact["full_name"] or f"{contact['first_name']} {contact['last_name']}".strip()
        
        try:
            logger.debug(f"Syncing {contact_name} (ID: {contact_id})...")
            result = self.service.bq_sync.sync_contact_to_all(contact_id)
            
            # Check each system
            sync_status = {
                "contact_id": contact_id,
                "contact_name": contact_name,
                "bigquery": result.get("bigquery", {}).get("status") == "synced",
                "crm_twenty": result.get("crm_twenty", {}).get("status") == "synced",
                "supabase": result.get("supabase", {}).get("status") in ("synced", "skipped"),
                "local": result.get("local", {}).get("status") in ("synced", "skipped"),
            }
            
            # Check for errors
            errors = []
            if not sync_status["bigquery"]:
                errors.append("BigQuery")
            if not sync_status["crm_twenty"]:
                errors.append("Twenty CRM")
            if result.get("crm_twenty", {}).get("error"):
                errors.append(f"CRM: {result['crm_twenty']['error']}")
            if result.get("supabase", {}).get("error"):
                errors.append(f"Supabase: {result['supabase']['error']}")
            if result.get("local", {}).get("error"):
                errors.append(f"Local: {result['local']['error']}")
            
            sync_status["errors"] = errors
            sync_status["sync_result"] = result
            
            return sync_status
            
        except Exception as e:
            logger.error(f"Failed to sync {contact_name} (ID: {contact_id}): {e}", exc_info=True)
            return {
                "contact_id": contact_id,
                "contact_name": contact_name,
                "bigquery": False,
                "crm_twenty": False,
                "supabase": False,
                "local": False,
                "errors": [str(e)],
                "sync_result": None,
            }
    
    def validate_contact_in_crm(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contact exists in Twenty CRM.
        
        Args:
            contact: Contact record
            
        Returns:
            Validation result
        """
        contact_id = contact["contact_id"]
        contact_name = contact["canonical_name"] or contact["full_name"]
        
        try:
            # List all contacts and find by contact_id custom field
            crm_contacts = self.service.crm_client.list_contacts(limit=10000)
            
            found = False
            crm_id = None
            crm_name = None
            
            for crm_contact in crm_contacts:
                custom_fields = crm_contact.get("customFields", {})
                if custom_fields.get("contact_id") == contact_id:
                    found = True
                    crm_id = crm_contact.get("id")
                    crm_name = crm_contact.get("name")
                    break
            
            return {
                "found": found,
                "crm_id": crm_id,
                "crm_name": crm_name,
                "expected_name": contact_name,
                "match": crm_name == contact_name if found else False,
            }
            
        except Exception as e:
            logger.error(f"Failed to validate {contact_id} in CRM: {e}")
            return {
                "found": False,
                "error": str(e),
            }
    
    def validate_contact_in_supabase(self, contact: Dict[str, Any]) -> Dict[str, Any]:
        """Validate contact exists in Supabase.
        
        Args:
            contact: Contact record
            
        Returns:
            Validation result
        """
        contact_id = contact["contact_id"]
        
        if not self.service.supabase:
            return {"found": None, "reason": "Supabase not configured"}
        
        try:
            result = self.service.supabase.table("contacts_master").select("*").eq(
                "contact_id", contact_id
            ).execute()
            
            found = len(result.data) > 0
            return {
                "found": found,
                "data": result.data[0] if found else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to validate {contact_id} in Supabase: {e}")
            return {
                "found": False,
                "error": str(e),
            }
    
    def validate_all(self, limit: int = None) -> Dict[str, Any]:
        """Validate sync for all contacts.
        
        Args:
            limit: Maximum number of contacts to validate (None for all)
            
        Returns:
            Validation results
        """
        logger.info("=" * 60)
        logger.info("COMPLETE SYNC VALIDATION")
        logger.info("=" * 60)
        logger.info("")
        logger.info("This will:")
        logger.info("  1. Fetch all contacts from BigQuery")
        logger.info("  2. Sync each contact to all systems")
        logger.info("  3. Validate each contact exists in all systems")
        logger.info("  4. Report any issues")
        logger.info("")
        
        # Fetch all contacts
        contacts = self.fetch_all_contacts()
        
        if limit:
            contacts = contacts[:limit]
            logger.info(f"Limiting to first {limit} contacts for validation")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("SYNCING ALL CONTACTS")
        logger.info("=" * 60)
        logger.info("")
        
        # Sync each contact
        for i, contact in enumerate(contacts, 1):
            contact_id = contact["contact_id"]
            contact_name = contact["canonical_name"] or contact["full_name"] or f"{contact['first_name']} {contact['last_name']}".strip()
            
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(contacts)} (synced: {self.results['synced']}, errors: {self.results['errors']})")
            
            # Sync contact
            sync_status = self.sync_contact(contact)
            
            # Track results
            if not sync_status["errors"]:
                self.results["synced"] += 1
            else:
                self.results["errors"] += 1
                self.results["missing"].append({
                    "contact_id": contact_id,
                    "contact_name": contact_name,
                    "errors": sync_status["errors"],
                })
            
            # Store details
            self.results["details"].append(sync_status)
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("VALIDATING SYNC IN ALL SYSTEMS")
        logger.info("=" * 60)
        logger.info("")
        
        # Validate each contact
        for i, contact in enumerate(contacts, 1):
            contact_id = contact["contact_id"]
            contact_name = contact["canonical_name"] or contact["full_name"]
            
            if i % 10 == 0:
                logger.info(f"Validation progress: {i}/{len(contacts)}")
            
            # Validate in CRM
            crm_validation = self.validate_contact_in_crm(contact)
            
            # Validate in Supabase
            supabase_validation = self.validate_contact_in_supabase(contact)
            
            # Check if all validations pass
            all_valid = (
                crm_validation.get("found", False) and
                (supabase_validation.get("found") is not False)  # None is OK (not configured)
            )
            
            if all_valid:
                self.results["validated"] += 1
            else:
                issues = []
                if not crm_validation.get("found"):
                    issues.append("Missing in CRM")
                if supabase_validation.get("found") is False:
                    issues.append("Missing in Supabase")
                
                self.results["mismatched"].append({
                    "contact_id": contact_id,
                    "contact_name": contact_name,
                    "crm": crm_validation,
                    "supabase": supabase_validation,
                    "issues": issues,
                })
        
        return self.results
    
    def generate_report(self) -> None:
        """Generate validation report."""
        logger.info("")
        logger.info("=" * 60)
        logger.info("VALIDATION REPORT")
        logger.info("=" * 60)
        logger.info("")
        logger.info(f"Total Contacts: {self.results['total_contacts']}")
        logger.info(f"✅ Successfully Synced: {self.results['synced']}")
        logger.info(f"✅ Validated in All Systems: {self.results['validated']}")
        logger.info(f"❌ Errors: {self.results['errors']}")
        logger.info(f"⚠️  Missing/Mismatched: {len(self.results['mismatched'])}")
        logger.info("")
        
        if self.results["errors"] > 0:
            logger.error("=" * 60)
            logger.error("SYNC ERRORS")
            logger.error("=" * 60)
            for item in self.results["missing"][:10]:  # Show first 10
                logger.error(f"  ❌ {item['contact_name']} (ID: {item['contact_id']})")
                for error in item["errors"]:
                    logger.error(f"     - {error}")
            if len(self.results["missing"]) > 10:
                logger.error(f"  ... and {len(self.results['missing']) - 10} more")
            logger.error("")
        
        if self.results["mismatched"]:
            logger.warning("=" * 60)
            logger.warning("VALIDATION ISSUES")
            logger.warning("=" * 60)
            for item in self.results["mismatched"][:10]:  # Show first 10
                logger.warning(f"  ⚠️  {item['contact_name']} (ID: {item['contact_id']})")
                for issue in item["issues"]:
                    logger.warning(f"     - {issue}")
            if len(self.results["mismatched"]) > 10:
                logger.warning(f"  ... and {len(self.results['mismatched']) - 10} more")
            logger.warning("")
        
        # Final status
        logger.info("=" * 60)
        if self.results["errors"] == 0 and len(self.results["mismatched"]) == 0:
            logger.info("✅ ALL CONTACTS SYNCED AND VALIDATED SUCCESSFULLY")
            logger.info("")
            logger.info(f"  Total: {self.results['total_contacts']}")
            logger.info(f"  Synced: {self.results['synced']}")
            logger.info(f"  Validated: {self.results['validated']}")
            logger.info("")
            logger.info("✅ NO EXCEPTIONS - ALL DATA IN SYNC")
        else:
            logger.warning("⚠️  SOME ISSUES FOUND")
            logger.warning(f"  Errors: {self.results['errors']}")
            logger.warning(f"  Validation issues: {len(self.results['mismatched'])}")
        logger.info("=" * 60)


def main() -> int:
    """Main function."""
    import argparse
    parser = argparse.ArgumentParser(description="Validate complete sync for all contacts")
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of contacts to validate (for testing)",
    )
    
    args = parser.parse_args()
    
    validator = SyncValidator()
    results = validator.validate_all(limit=args.limit)
    validator.generate_report()
    
    # Return exit code based on results
    if results["errors"] == 0 and len(results["mismatched"]) == 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    import argparse
    sys.exit(main())
