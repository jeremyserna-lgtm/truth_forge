#!/usr/bin/env python3
"""Sync all contacts, businesses, and relationships to Twenty CRM.

This script syncs all existing data from BigQuery to Twenty CRM.
Run this after setup_twenty_crm.py to populate the CRM with all data.

Usage:
    python scripts/sync_all_to_twenty_crm.py [--limit N] [--dry-run]
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.services.sync.business_sync import BusinessSyncService
from truth_forge.services.sync.relationship_sync import RelationshipSyncService
from truth_forge.services.sync.people_relationship_sync import PeopleRelationshipSyncService
from truth_forge.services.sync.error_reporter import ErrorReporter
from truth_forge.core.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_all_contact_ids(bq_client: bigquery.Client, limit: int = None) -> List[str]:
    """Fetch all contact IDs from BigQuery.
    
    Args:
        bq_client: BigQuery client
        limit: Maximum number of contacts to fetch
        
    Returns:
        List of contact IDs
    """
    query = """
    SELECT contact_id
    FROM `identity.contacts_master`
    ORDER BY contact_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    query_job = bq_client.query(query)
    results = list(query_job.result())
    
    return [str(row.contact_id) for row in results]


def fetch_all_business_ids(bq_client: bigquery.Client, limit: int = None) -> List[str]:
    """Fetch all business IDs from BigQuery.
    
    Args:
        bq_client: BigQuery client
        limit: Maximum number of businesses to fetch
        
    Returns:
        List of business IDs
    """
    query = """
    SELECT business_id
    FROM `identity.businesses_master`
    ORDER BY business_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    try:
        query_job = bq_client.query(query)
        results = list(query_job.result())
        return [str(row.business_id) for row in results]
    except Exception as e:
        logger.warning(f"Failed to fetch businesses (table may not exist): {e}")
        return []


def fetch_all_relationship_ids(bq_client: bigquery.Client, limit: int = None) -> List[str]:
    """Fetch all people-business relationship IDs from BigQuery.
    
    Args:
        bq_client: BigQuery client
        limit: Maximum number of relationships to fetch
        
    Returns:
        List of relationship IDs
    """
    query = """
    SELECT relationship_id
    FROM `identity.people_business_relationships`
    ORDER BY relationship_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    try:
        query_job = bq_client.query(query)
        results = list(query_job.result())
        return [str(row.relationship_id) for row in results]
    except Exception as e:
        logger.warning(f"Failed to fetch relationships (table may not exist): {e}")
        return []


def fetch_all_people_relationship_ids(bq_client: bigquery.Client, limit: int = None) -> List[str]:
    """Fetch all people-to-people relationship IDs from BigQuery.
    
    Args:
        bq_client: BigQuery client
        limit: Maximum number of relationships to fetch
        
    Returns:
        List of relationship IDs
    """
    query = """
    SELECT relationship_id
    FROM `identity.people_relationships`
    ORDER BY relationship_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    try:
        query_job = bq_client.query(query)
        results = list(query_job.result())
        return [str(row.relationship_id) for row in results]
    except Exception as e:
        logger.warning(f"Failed to fetch people relationships (table may not exist): {e}")
        return []


def sync_contacts(
    service: TwentyCRMService,
    contact_ids: List[str],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Sync all contacts to Twenty CRM.
    
    Args:
        service: Twenty CRM service
        contact_ids: List of contact IDs to sync
        dry_run: If True, don't actually sync
        
    Returns:
        Sync summary
    """
    logger.info(f"Syncing {len(contact_ids)} contacts...")
    
    synced = 0
    errors = 0
    error_details = []
    
    for i, contact_id in enumerate(contact_ids, 1):
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Would sync contact {contact_id} ({i}/{len(contact_ids)})")
                synced += 1
            else:
                logger.info(f"Syncing contact {contact_id} ({i}/{len(contact_ids)})...")
                result = service.bq_sync.sync_contact_to_all(contact_id)
                
                if result.get("crm_twenty", {}).get("status") == "synced":
                    synced += 1
                else:
                    errors += 1
                    error_details.append({
                        "contact_id": contact_id,
                        "error": result.get("crm_twenty", {}).get("error"),
                    })
        except Exception as e:
            errors += 1
            error_details.append({"contact_id": contact_id, "error": str(e)})
            logger.error(f"Failed to sync contact {contact_id}: {e}")
    
    return {
        "total": len(contact_ids),
        "synced": synced,
        "errors": errors,
        "error_details": error_details,
    }


def sync_businesses(
    service: TwentyCRMService,
    business_ids: List[str],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Sync all businesses to Twenty CRM.
    
    Args:
        service: Twenty CRM service
        business_ids: List of business IDs to sync
        dry_run: If True, don't actually sync
        
    Returns:
        Sync summary
    """
    if not business_ids:
        logger.info("No businesses to sync")
        return {"total": 0, "synced": 0, "errors": 0}
    
    logger.info(f"Syncing {len(business_ids)} businesses...")
    
    synced = 0
    errors = 0
    error_details = []
    
    for i, business_id in enumerate(business_ids, 1):
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Would sync business {business_id} ({i}/{len(business_ids)})")
                synced += 1
            else:
                logger.info(f"Syncing business {business_id} ({i}/{len(business_ids)})...")
                result = service.business_sync.sync_business_to_all(business_id)
                
                if result.get("crm_twenty", {}).get("status") == "synced":
                    synced += 1
                else:
                    errors += 1
                    error_details.append({
                        "business_id": business_id,
                        "error": result.get("crm_twenty", {}).get("error"),
                    })
        except Exception as e:
            errors += 1
            error_details.append({"business_id": business_id, "error": str(e)})
            logger.error(f"Failed to sync business {business_id}: {e}")
    
    return {
        "total": len(business_ids),
        "synced": synced,
        "errors": errors,
        "error_details": error_details,
    }


def main() -> None:
    """Main sync function."""
    parser = argparse.ArgumentParser(description="Sync all data to Twenty CRM")
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of records to sync (for testing)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode (don't actually sync)",
    )
    parser.add_argument(
        "--skip-contacts",
        action="store_true",
        help="Skip syncing contacts",
    )
    parser.add_argument(
        "--skip-businesses",
        action="store_true",
        help="Skip syncing businesses",
    )
    
    args = parser.parse_args()
    
    logger.info("Initializing Twenty CRM service...")
    
    try:
        bq_client = bigquery.Client(project=settings.effective_gcp_project)
        
        with TwentyCRMService() as service:
            # Verify setup first
            logger.info("Verifying Twenty CRM setup...")
            verify_result = service.verify_setup()
            
            if not verify_result["all_complete"]:
                logger.error("❌ Twenty CRM setup incomplete!")
                logger.error("Please run: python scripts/setup_twenty_crm.py")
                sys.exit(1)
            
            logger.info("✅ Twenty CRM setup verified")
            
            summary = {
                "contacts": {"total": 0, "synced": 0, "errors": 0},
                "businesses": {"total": 0, "synced": 0, "errors": 0},
            }
            
            # Sync contacts
            if not args.skip_contacts:
                logger.info("\n" + "=" * 60)
                logger.info("SYNCING CONTACTS")
                logger.info("=" * 60)
                contact_ids = fetch_all_contact_ids(bq_client, limit=args.limit)
                summary["contacts"] = sync_contacts(service, contact_ids, dry_run=args.dry_run)
            
            # Sync businesses
            if not args.skip_businesses:
                logger.info("\n" + "=" * 60)
                logger.info("SYNCING BUSINESSES")
                logger.info("=" * 60)
                business_ids = fetch_all_business_ids(bq_client, limit=args.limit)
                summary["businesses"] = sync_businesses(service, business_ids, dry_run=args.dry_run)
            
            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("SYNC SUMMARY")
            logger.info("=" * 60)
            logger.info(f"Contacts: {summary['contacts']['synced']}/{summary['contacts']['total']} synced, {summary['contacts']['errors']} errors")
            logger.info(f"Businesses: {summary['businesses']['synced']}/{summary['businesses']['total']} synced, {summary['businesses']['errors']} errors")
            
            if summary["contacts"]["errors"] > 0 or summary["businesses"]["errors"] > 0:
                logger.warning("\n⚠️  Some syncs failed. Check error details above.")
                sys.exit(1)
            else:
                logger.info("\n✅ All syncs completed successfully!")
    
    except Exception as e:
        logger.error(f"Failed to sync to Twenty CRM: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
