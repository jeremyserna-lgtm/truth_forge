#!/usr/bin/env python3
"""Complete sync to Twenty CRM with full fidelity.

This script ensures data is actually synced to Twenty CRM.
It verifies setup, syncs data, and confirms records appear.

Usage:
    python scripts/sync_to_twenty_crm_complete.py [--limit N] [--contact-id ID]
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.services.sync.twenty_crm_client import TwentyCRMClient
from truth_forge.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def verify_setup(service: TwentyCRMService) -> bool:
    """Verify Twenty CRM setup is complete.
    
    Returns:
        True if setup is complete
    """
    logger.info("=" * 60)
    logger.info("VERIFYING SETUP")
    logger.info("=" * 60)
    
    try:
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
        logger.error(f"❌ Setup verification failed: {e}", exc_info=True)
        return False


def test_connection(service: TwentyCRMService) -> bool:
    """Test Twenty CRM connection.
    
    Returns:
        True if connection works
    """
    logger.info("\n" + "=" * 60)
    logger.info("TESTING CONNECTION")
    logger.info("=" * 60)
    
    try:
        contacts = service.crm_client.list_contacts(limit=5)
        logger.info(f"✅ Connection works! Found {len(contacts)} existing contacts")
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}", exc_info=True)
        logger.error("\nTroubleshooting:")
        logger.error("1. Check API key in Secret Manager")
        logger.error("2. Verify API key is valid")
        logger.error("3. Check network connectivity")
        return False


def get_contact_ids_from_bigquery(limit: Optional[int] = None, contact_id: Optional[str] = None) -> List[str]:
    """Get contact IDs from BigQuery.
    
    Returns:
        List of contact IDs
    """
    bq_client = bigquery.Client(project=settings.effective_gcp_project)
    
    if contact_id:
        return [contact_id]
    
    query = """
    SELECT contact_id, canonical_name, full_name, first_name, last_name
    FROM `identity.contacts_master`
    WHERE is_me = FALSE
    ORDER BY contact_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    try:
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if not results:
            logger.warning("⚠️  No contacts found in BigQuery")
            return []
        
        contact_ids = []
        for row in results:
            cid = str(row.contact_id)
            name = row.canonical_name or row.full_name or f"{row.first_name} {row.last_name}".strip()
            contact_ids.append(cid)
            logger.debug(f"Found contact: {name} (ID: {cid})")
        
        logger.info(f"Found {len(contact_ids)} contacts in BigQuery")
        return contact_ids
    except Exception as e:
        logger.error(f"❌ Failed to query BigQuery: {e}", exc_info=True)
        return []


def sync_contact_to_crm(
    service: TwentyCRMService,
    contact_id: str,
    bq_client: bigquery.Client,
) -> Dict[str, Any]:
    """Sync a single contact to Twenty CRM.
    
    Returns:
        Sync result with detailed status
    """
    try:
        logger.info(f"Syncing contact {contact_id}...")
        
        # Use BigQuerySyncService directly to ensure CRM sync happens
        bq_sync = BigQuerySyncService(
            bq_client,
            service.supabase,
            None,  # local_db - optional
            service.crm_client,
        )
        
        # Sync to all systems (including CRM)
        result = bq_sync.sync_contact_to_all(contact_id)
        
        # Check CRM result specifically
        crm_result = result.get("crm_twenty", {})
        
        if crm_result.get("status") == "synced":
            crm_id = crm_result.get("crm_id")
            logger.info(f"  ✅ Synced to CRM! CRM ID: {crm_id}")
            
            # Verify it actually exists in CRM
            try:
                verify_contact = service.crm_client.get_contact(crm_id)
                logger.info(f"  ✅ Verified in CRM: {verify_contact.get('name')}")
                return {
                    "status": "success",
                    "contact_id": contact_id,
                    "crm_id": crm_id,
                    "crm_name": verify_contact.get("name"),
                }
            except Exception as e:
                logger.warning(f"  ⚠️  Synced but verification failed: {e}")
                return {
                    "status": "synced_but_unverified",
                    "contact_id": contact_id,
                    "crm_id": crm_id,
                    "error": str(e),
                }
        else:
            error = crm_result.get("error", "Unknown error")
            logger.error(f"  ❌ CRM sync failed: {error}")
            return {
                "status": "error",
                "contact_id": contact_id,
                "error": error,
            }
    except Exception as e:
        logger.error(f"  ❌ Sync failed with exception: {e}", exc_info=True)
        return {
            "status": "exception",
            "contact_id": contact_id,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def main() -> None:
    """Main sync function."""
    parser = argparse.ArgumentParser(description="Complete sync to Twenty CRM")
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of contacts to sync",
    )
    parser.add_argument(
        "--contact-id",
        help="Sync specific contact ID",
    )
    parser.add_argument(
        "--skip-setup-check",
        action="store_true",
        help="Skip setup verification",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("TWENTY CRM COMPLETE SYNC")
    logger.info("=" * 60)
    
    try:
        # Initialize service
        logger.info("Initializing Twenty CRM service...")
        with TwentyCRMService() as service:
            # Step 1: Verify setup
            if not args.skip_setup_check:
                if not verify_setup(service):
                    logger.error("\n❌ Setup incomplete. Please run setup first:")
                    logger.error("   python scripts/setup_twenty_crm.py")
                    sys.exit(1)
            
            # Step 2: Test connection
            if not test_connection(service):
                logger.error("\n❌ Connection failed. Please check API key and connectivity.")
                sys.exit(1)
            
            # Step 3: Get contact IDs
            logger.info("\n" + "=" * 60)
            logger.info("GETTING CONTACTS FROM BIGQUERY")
            logger.info("=" * 60)
            
            bq_client = bigquery.Client(project=settings.effective_gcp_project)
            contact_ids = get_contact_ids_from_bigquery(limit=args.limit, contact_id=args.contact_id)
            
            if not contact_ids:
                logger.error("❌ No contacts to sync")
                sys.exit(1)
            
            # Step 4: Sync contacts
            logger.info("\n" + "=" * 60)
            logger.info(f"SYNCING {len(contact_ids)} CONTACTS TO TWENTY CRM")
            logger.info("=" * 60)
            
            results = []
            success_count = 0
            error_count = 0
            
            for i, contact_id in enumerate(contact_ids, 1):
                logger.info(f"\n[{i}/{len(contact_ids)}] ", end="")
                result = sync_contact_to_crm(service, contact_id, bq_client)
                results.append(result)
                
                if result["status"] == "success":
                    success_count += 1
                else:
                    error_count += 1
            
            # Step 5: Summary
            logger.info("\n" + "=" * 60)
            logger.info("SYNC SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Total contacts: {len(contact_ids)}")
            logger.info(f"✅ Successfully synced: {success_count}")
            logger.info(f"❌ Failed: {error_count}")
            
            # Step 6: Verify in CRM
            logger.info("\n" + "=" * 60)
            logger.info("VERIFYING IN TWENTY CRM")
            logger.info("=" * 60)
            
            try:
                all_contacts = service.crm_client.list_contacts(limit=1000)
                logger.info(f"Total contacts in CRM: {len(all_contacts)}")
                
                if all_contacts:
                    logger.info("\nFirst 5 contacts in CRM:")
                    for i, contact in enumerate(all_contacts[:5], 1):
                        name = contact.get("name", "Unknown")
                        crm_id = contact.get("id")
                        custom_id = contact.get("customFields", {}).get("contact_id")
                        logger.info(f"  {i}. {name} (CRM ID: {crm_id}, Contact ID: {custom_id})")
                
                if len(all_contacts) > 0:
                    logger.info("\n✅ Data is now in Twenty CRM!")
                    logger.info("   Check the Twenty CRM UI to see your contacts.")
                else:
                    logger.warning("\n⚠️  No contacts found in CRM after sync")
                    logger.warning("   Check error messages above for issues")
            except Exception as e:
                logger.error(f"Failed to verify in CRM: {e}", exc_info=True)
            
            # Exit with appropriate code
            if error_count > 0:
                logger.warning(f"\n⚠️  {error_count} contacts failed to sync. Check errors above.")
                sys.exit(1)
            else:
                logger.info("\n✅ All contacts synced successfully!")
                sys.exit(0)
    
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Sync interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
