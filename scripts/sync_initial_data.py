#!/usr/bin/env python3
"""Initial sync - sync all existing data to Twenty CRM.

Run this once to sync all existing contacts, then use auto_sync for ongoing sync.

Usage:
    python scripts/sync_initial_data.py [--limit N]
"""

import sys
import argparse
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Sync all initial data."""
    parser = argparse.ArgumentParser(description="Initial sync to Twenty CRM")
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of contacts to sync (for testing)",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("INITIAL SYNC - SYNCING ALL DATA TO TWENTY CRM")
    logger.info("=" * 60)
    
    try:
        # Ensure GCP project is set
        project_id = settings.effective_gcp_project or "81233637196"
        import os
        if not os.getenv("GCP_PROJECT_ID"):
            os.environ["GCP_PROJECT_ID"] = project_id
        if not os.getenv("GOOGLE_CLOUD_PROJECT"):
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
        
        bq_client = bigquery.Client(project=project_id)
        
        # Get all contact IDs
        query = """
        SELECT 
            contact_id,
            display_name,
            first_name,
            last_name,
            organization
        FROM `identity.contacts_master`
        ORDER BY contact_id
        """
        
        if args.limit:
            query += f" LIMIT {args.limit}"
        
        logger.info("Fetching contacts from BigQuery...")
        query_job = bq_client.query(query)
        results = list(query_job.result())
        
        if not results:
            logger.warning("No contacts found in BigQuery")
            return
        
        logger.info(f"Found {len(results)} contacts to sync")
        
        # Sync each contact
        with TwentyCRMService() as service:
            synced = 0
            errors = 0
            
            for i, row in enumerate(results, 1):
                contact_id = str(row.contact_id)
                name = row.display_name or f"{row.first_name or ''} {row.last_name or ''}".strip() or f"Contact {contact_id}"
                
                if i % 10 == 0:
                    logger.info(f"\nProgress: {i}/{len(results)} (synced: {synced}, errors: {errors})")
                
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
                        logger.warning(f"  ⚠️  {name}: {crm_result.get('error')}")
                except Exception as e:
                    errors += 1
                    logger.error(f"  ❌ Failed to sync {name}: {e}")
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("INITIAL SYNC COMPLETE")
            logger.info("=" * 60)
            logger.info(f"Total contacts: {len(results)}")
            logger.info(f"✅ Successfully synced: {synced}")
            logger.info(f"❌ Errors: {errors}")
            
            # Verify in CRM
            logger.info("\nVerifying in Twenty CRM...")
            try:
                contacts = service.crm_client.list_contacts(limit=1000)
                logger.info(f"✅ Total contacts in CRM: {len(contacts)}")
                
                if contacts:
                    logger.info("\nFirst 5 contacts in CRM:")
                    for i, contact in enumerate(contacts[:5], 1):
                        logger.info(f"  {i}. {contact.get('name')} (ID: {contact.get('id')})")
            except Exception as e:
                logger.error(f"Failed to verify: {e}")
            
            if errors == 0:
                logger.info("\n✅ All contacts synced successfully!")
                logger.info("   You can now start the auto sync service:")
                logger.info("   python scripts/run_auto_sync.py")
            else:
                logger.warning(f"\n⚠️  {errors} contacts had sync issues")
                logger.warning("   Check logs above for details")
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
