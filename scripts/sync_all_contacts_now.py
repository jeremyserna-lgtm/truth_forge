#!/usr/bin/env python3
"""Sync All Contacts to Twenty CRM - Immediate Execution.

This script syncs all contacts from BigQuery to Twenty CRM immediately.
Fixes schema issues and ensures API key is retrieved correctly.
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set GCP project before any imports
os.environ["GCP_PROJECT_ID"] = "81233637196"
os.environ["GOOGLE_CLOUD_PROJECT"] = "81233637196"

from google.cloud import bigquery
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Sync all contacts to Twenty CRM."""
    logger.info("=" * 60)
    logger.info("SYNCING ALL CONTACTS TO TWENTY CRM")
    logger.info("=" * 60)
    logger.info("")
    
    project_id = "81233637196"
    bq_client = bigquery.Client(project=project_id)
    
    # Get all contact IDs (using actual schema)
    query = """
    SELECT contact_id, display_name, first_name, last_name, organization
    FROM `identity.contacts_master`
    ORDER BY contact_id
    """
    
    logger.info("Fetching contacts from BigQuery...")
    query_job = bq_client.query(query)
    results = list(query_job.result())
    
    if not results:
        logger.warning("No contacts found in BigQuery")
        return
    
    logger.info(f"Found {len(results)} contacts to sync")
    logger.info("")
    
    # Sync each contact
    with TwentyCRMService() as service:
        synced = 0
        errors = 0
        
        for i, row in enumerate(results, 1):
            contact_id = str(row.contact_id)
            name = row.display_name or f"{row.first_name or ''} {row.last_name or ''}".strip() or f"Contact {contact_id}"
            
            if i % 10 == 0:
                logger.info(f"Progress: {i}/{len(results)} (synced: {synced}, errors: {errors})")
            
            try:
                logger.debug(f"Syncing {name} (ID: {contact_id})...")
                result = service.bq_sync.sync_contact_to_all(contact_id)
                
                crm_result = result.get("crm_twenty", {})
                if crm_result.get("status") == "synced":
                    synced += 1
                    if i % 50 == 0:  # Log every 50th
                        logger.info(f"  ✅ Synced {name} (CRM ID: {crm_result.get('crm_id')})")
                else:
                    errors += 1
                    error_msg = crm_result.get("error", "Unknown error")
                    logger.warning(f"  ⚠️  {name}: {error_msg}")
            except Exception as e:
                errors += 1
                logger.error(f"  ❌ Failed to sync {name}: {e}")
        
        # Summary
        logger.info("")
        logger.info("=" * 60)
        logger.info("SYNC COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total contacts: {len(results)}")
        logger.info(f"✅ Successfully synced: {synced}")
        logger.info(f"❌ Errors: {errors}")
        logger.info("")
        
        # Verify in CRM
        logger.info("Verifying in Twenty CRM...")
        try:
            contacts = service.crm_client.list_contacts(limit=1000)
            logger.info(f"✅ Total contacts in CRM: {len(contacts)}")
            
            if contacts:
                logger.info("")
                logger.info("First 10 contacts in CRM:")
                for i, contact in enumerate(contacts[:10], 1):
                    logger.info(f"  {i}. {contact.get('name')} (ID: {contact.get('id')})")
        except Exception as e:
            logger.error(f"Failed to verify: {e}")
        
        if errors == 0:
            logger.info("")
            logger.info("✅ All contacts synced successfully!")
        else:
            logger.warning("")
            logger.warning(f"⚠️  {errors} contacts had sync issues")
            logger.warning("   Check logs above for details")


if __name__ == "__main__":
    main()
