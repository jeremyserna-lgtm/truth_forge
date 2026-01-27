#!/usr/bin/env python3
"""Sync Contacts to Twenty CRM - Fixed Version.

This script syncs contacts with proper error handling and validation.
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Sync contacts to Twenty CRM."""
    logger.info("=" * 60)
    logger.info("SYNCING CONTACTS TO TWENTY CRM")
    logger.info("=" * 60)
    
    project_id = "81233637196"
    bq_client = bigquery.Client(project=project_id)
    
    # Get contact IDs
    query = """
    SELECT contact_id, display_name, first_name, last_name
    FROM `identity.contacts_master`
    ORDER BY contact_id
    LIMIT 20
    """
    
    logger.info("Fetching contacts from BigQuery...")
    results = list(bq_client.query(query).result())
    logger.info(f"Found {len(results)} contacts to sync")
    
    with TwentyCRMService() as service:
        synced = 0
        errors = 0
        
        for i, row in enumerate(results, 1):
            contact_id = str(row.contact_id)
            name = row.display_name or f"{row.first_name or ''} {row.last_name or ''}".strip()
            
            logger.info(f"[{i}/{len(results)}] Syncing {name}...")
            
            try:
                result = service.bq_sync.sync_contact_to_all(contact_id)
                crm_result = result.get("crm_twenty", {})
                
                if crm_result.get("status") == "synced":
                    synced += 1
                    logger.info(f"  ✅ Synced! CRM ID: {crm_result.get('crm_id')}")
                else:
                    errors += 1
                    error = crm_result.get("error", "Unknown")
                    logger.error(f"  ❌ Failed: {error[:200]}")
            except Exception as e:
                errors += 1
                logger.error(f"  ❌ Exception: {e}")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("SYNC COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total: {len(results)}")
        logger.info(f"✅ Synced: {synced}")
        logger.info(f"❌ Errors: {errors}")
        
        # Verify
        contacts = service.crm_client.list_contacts(limit=100)
        logger.info(f"Total contacts in CRM: {len(contacts)}")


if __name__ == "__main__":
    main()
