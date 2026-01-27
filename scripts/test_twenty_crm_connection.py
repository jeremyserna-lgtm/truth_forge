#!/usr/bin/env python3
"""Test Twenty CRM connection and list existing records.

This script helps diagnose why records aren't showing up in Twenty CRM.

Usage:
    python scripts/test_twenty_crm_connection.py
"""

import sys
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.services.sync.twenty_crm_client import TwentyCRMClient
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def test_connection() -> bool:
    """Test basic API connection.
    
    Returns:
        True if connection works
    """
    logger.info("=" * 60)
    logger.info("TESTING TWENTY CRM CONNECTION")
    logger.info("=" * 60)
    
    try:
        with TwentyCRMClient() as client:
            logger.info("✅ Successfully connected to Twenty CRM")
            logger.info(f"   Base URL: {client.base_url}")
            logger.info(f"   API Key: {'*' * 20} (hidden)")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to connect: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Check API key is stored in Secret Manager:")
        logger.error("   gcloud secrets list --project=flash-clover-464719-g1 | grep twenty")
        logger.error("2. Check API key name matches: twenty-crm-api-key")
        logger.error("3. Verify API key is valid")
        return False


def list_existing_contacts() -> int:
    """List existing contacts in Twenty CRM.
    
    Returns:
        Number of contacts found
    """
    logger.info("\n" + "=" * 60)
    logger.info("LISTING EXISTING CONTACTS")
    logger.info("=" * 60)
    
    try:
        with TwentyCRMClient() as client:
            contacts = client.list_contacts(limit=100)
            logger.info(f"Found {len(contacts)} contacts in Twenty CRM")
            
            if contacts:
                logger.info("\nFirst 5 contacts:")
                for i, contact in enumerate(contacts[:5], 1):
                    logger.info(f"  {i}. {contact.get('name', 'Unknown')} (ID: {contact.get('id')})")
                    custom_fields = contact.get("customFields", {})
                    contact_id = custom_fields.get("contact_id")
                    if contact_id:
                        logger.info(f"     Contact ID: {contact_id}")
            else:
                logger.warning("⚠️  No contacts found in Twenty CRM")
                logger.warning("   You need to sync data from BigQuery")
            
            return len(contacts)
    except Exception as e:
        logger.error(f"❌ Failed to list contacts: {e}")
        return 0


def check_setup() -> bool:
    """Check if custom fields are set up.
    
    Returns:
        True if setup is complete
    """
    logger.info("\n" + "=" * 60)
    logger.info("CHECKING SETUP")
    logger.info("=" * 60)
    
    try:
        with TwentyCRMService() as service:
            result = service.verify_setup()
            
            if result["all_complete"]:
                logger.info("✅ Setup complete!")
                logger.info(f"   Person fields: {result['person_fields']['total']}")
                logger.info(f"   Company fields: {result['company_fields']['total']}")
                return True
            else:
                logger.error("❌ Setup incomplete!")
                if result["person_fields"]["missing"]:
                    logger.error(f"   Missing person fields: {result['person_fields']['missing']}")
                if result["company_fields"]["missing"]:
                    logger.error(f"   Missing company fields: {result['company_fields']['missing']}")
                logger.error("\nRun setup first:")
                logger.error("   python scripts/setup_twenty_crm.py")
                return False
    except Exception as e:
        logger.error(f"❌ Failed to check setup: {e}")
        return False


def test_sync_one_contact() -> bool:
    """Test syncing one contact from BigQuery.
    
    Returns:
        True if sync works
    """
    logger.info("\n" + "=" * 60)
    logger.info("TESTING SYNC (ONE CONTACT)")
    logger.info("=" * 60)
    
    try:
        from google.cloud import bigquery
        from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
        from truth_forge.core.settings import settings
        
        # Get one contact ID from BigQuery
        bq_client = bigquery.Client(project=settings.effective_gcp_project)
        query = """
        SELECT contact_id, canonical_name
        FROM `identity.contacts_master`
        WHERE is_me = FALSE
        LIMIT 1
        """
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if not results:
            logger.warning("⚠️  No contacts found in BigQuery")
            return False
        
        contact_id = str(results[0].contact_id)
        contact_name = results[0].canonical_name or "Unknown"
        
        logger.info(f"Testing sync for contact: {contact_name} (ID: {contact_id})")
        
        # Sync to CRM
        with TwentyCRMService() as service:
            result = service.bq_sync.sync_contact_to_all(contact_id)
            
            crm_result = result.get("crm_twenty", {})
            if crm_result.get("status") == "synced":
                logger.info(f"✅ Successfully synced contact {contact_id} to CRM")
                logger.info(f"   CRM ID: {crm_result.get('crm_id')}")
                return True
            else:
                logger.error(f"❌ Failed to sync contact: {crm_result.get('error')}")
                return False
    except Exception as e:
        logger.error(f"❌ Failed to test sync: {e}", exc_info=True)
        return False


def main() -> None:
    """Run all diagnostic tests."""
    logger.info("Twenty CRM Diagnostic Tool\n")
    
    # Test connection
    if not test_connection():
        logger.error("\n❌ Connection failed. Fix connection issues first.")
        sys.exit(1)
    
    # Check setup
    setup_ok = check_setup()
    
    # List existing contacts
    contact_count = list_existing_contacts()
    
    # If no contacts and setup is OK, test sync
    if contact_count == 0 and setup_ok:
        logger.info("\n" + "=" * 60)
        logger.info("NO CONTACTS FOUND - TESTING SYNC")
        logger.info("=" * 60)
        
        if test_sync_one_contact():
            logger.info("\n✅ Sync test successful!")
            logger.info("   You can now sync all contacts:")
            logger.info("   python scripts/sync_all_to_twenty_crm.py")
        else:
            logger.error("\n❌ Sync test failed. Check errors above.")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Connection: {'✅ OK' if test_connection() else '❌ FAILED'}")
    logger.info(f"Setup: {'✅ Complete' if setup_ok else '❌ Incomplete'}")
    logger.info(f"Contacts in CRM: {contact_count}")
    
    if contact_count == 0:
        logger.info("\n📋 Next Steps:")
        logger.info("1. If setup incomplete: python scripts/setup_twenty_crm.py")
        logger.info("2. Sync all contacts: python scripts/sync_all_to_twenty_crm.py")
        logger.info("3. Or sync specific contact: python scripts/push_data_through_all_layers.py --contact-id <ID>")


if __name__ == "__main__":
    main()
