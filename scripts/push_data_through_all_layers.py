#!/usr/bin/env python3
"""Push data through all layers to ensure complete sync.

This script ensures all metadata flows through:
1. BigQuery (canonical) → Supabase → Local → Twenty CRM
2. Twenty CRM → BigQuery → Supabase → Local
3. Supabase → BigQuery → All systems

Usage:
    python scripts/push_data_through_all_layers.py [--source SOURCE] [--contact-id ID]
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from google.cloud import bigquery
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.services.sync.supabase_sync import SupabaseSyncService
from truth_forge.services.sync.crm_twenty_sync import CRMTwentySyncService
from truth_forge.core.settings import settings
from truth_forge.services.secret.service import SecretService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def push_from_bigquery(
    service: TwentyCRMService,
    contact_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Push data from BigQuery through all layers.
    
    Args:
        service: Twenty CRM service
        contact_id: Specific contact ID (optional)
        limit: Limit number of contacts (optional)
        
    Returns:
        Push summary
    """
    logger.info("=" * 60)
    logger.info("PUSHING FROM BIGQUERY → ALL LAYERS")
    logger.info("=" * 60)
    
    bq_client = bigquery.Client(project=settings.effective_gcp_project)
    
    if contact_id:
        contact_ids = [contact_id]
    else:
        query = """
        SELECT contact_id
        FROM `identity.contacts_master`
        WHERE is_me = FALSE
        ORDER BY contact_id
        """
        if limit:
            query += f" LIMIT {limit}"
        
        query_job = bq_client.query(query)
        results = list(query_job.result())
        contact_ids = [str(row.contact_id) for row in results]
    
    logger.info(f"Pushing {len(contact_ids)} contacts from BigQuery...")
    
    synced = 0
    errors = 0
    
    for i, cid in enumerate(contact_ids, 1):
        try:
            logger.info(f"Pushing contact {cid} ({i}/{len(contact_ids)})...")
            result = service.bq_sync.sync_contact_to_all(cid)
            
            # Check all systems
            systems = ["supabase", "local", "crm_twenty"]
            all_synced = all(
                result.get(system, {}).get("status") == "synced"
                for system in systems
            )
            
            if all_synced:
                synced += 1
                logger.info(f"  ✅ Contact {cid} synced to all systems")
            else:
                errors += 1
                logger.warning(f"  ⚠️  Contact {cid} had sync issues")
                for system in systems:
                    sys_result = result.get(system, {})
                    if sys_result.get("status") != "synced":
                        logger.warning(f"    {system}: {sys_result.get('error', 'Unknown error')}")
        except Exception as e:
            errors += 1
            logger.error(f"  ❌ Failed to push contact {cid}: {e}")
    
    return {
        "source": "bigquery",
        "total": len(contact_ids),
        "synced": synced,
        "errors": errors,
    }


def push_from_crm(
    service: TwentyCRMService,
    crm_contact_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Push data from Twenty CRM through all layers.
    
    Args:
        service: Twenty CRM service
        crm_contact_id: Specific CRM contact ID (optional)
        limit: Limit number of contacts (optional)
        
    Returns:
        Push summary
    """
    logger.info("=" * 60)
    logger.info("PUSHING FROM TWENTY CRM → ALL LAYERS")
    logger.info("=" * 60)
    
    if crm_contact_id:
        crm_ids = [crm_contact_id]
    else:
        contacts = service.crm_client.list_contacts(limit=limit or 100)
        crm_ids = [c["id"] for c in contacts]
    
    logger.info(f"Pushing {len(crm_ids)} contacts from CRM...")
    
    synced = 0
    errors = 0
    
    for i, crm_id in enumerate(crm_ids, 1):
        try:
            logger.info(f"Pushing CRM contact {crm_id} ({i}/{len(crm_ids)})...")
            
            # Sync from CRM to BigQuery (which propagates to all)
            crm_sync = CRMTwentySyncService(
                service.crm_client, service.bq_client, service.bq_sync
            )
            result = crm_sync.sync_from_crm_to_bigquery(crm_id)
            
            if result.get("status") == "synced":
                synced += 1
                logger.info(f"  ✅ CRM contact {crm_id} synced to all systems")
            else:
                errors += 1
                logger.warning(f"  ⚠️  CRM contact {crm_id} had sync issues: {result.get('error')}")
        except Exception as e:
            errors += 1
            logger.error(f"  ❌ Failed to push CRM contact {crm_id}: {e}")
    
    return {
        "source": "crm_twenty",
        "total": len(crm_ids),
        "synced": synced,
        "errors": errors,
    }


def push_from_supabase(
    service: TwentyCRMService,
    supabase_contact_id: Optional[str] = None,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """Push data from Supabase through all layers.
    
    Args:
        service: Twenty CRM service
        supabase_contact_id: Specific Supabase contact ID (optional)
        limit: Limit number of contacts (optional)
        
    Returns:
        Push summary
    """
    logger.info("=" * 60)
    logger.info("PUSHING FROM SUPABASE → ALL LAYERS")
    logger.info("=" * 60)
    
    if supabase_contact_id:
        supabase_ids = [supabase_contact_id]
    else:
        result = service.supabase.table("contacts_master").select("id,contact_id").limit(limit or 100).execute()
        supabase_ids = [c["contact_id"] or c["id"] for c in result.data]
    
    logger.info(f"Pushing {len(supabase_ids)} contacts from Supabase...")
    
    synced = 0
    errors = 0
    
    for i, supabase_id in enumerate(supabase_ids, 1):
        try:
            logger.info(f"Pushing Supabase contact {supabase_id} ({i}/{len(supabase_ids)})...")
            
            # Sync from Supabase to BigQuery (which propagates to all)
            supabase_sync = SupabaseSyncService(
                service.supabase, service.bq_client, service.bq_sync
            )
            result = supabase_sync.sync_from_supabase_to_bigquery(supabase_id)
            
            if result.get("status") == "synced":
                synced += 1
                logger.info(f"  ✅ Supabase contact {supabase_id} synced to all systems")
            else:
                errors += 1
                logger.warning(f"  ⚠️  Supabase contact {supabase_id} had sync issues: {result.get('error')}")
        except Exception as e:
            errors += 1
            logger.error(f"  ❌ Failed to push Supabase contact {supabase_id}: {e}")
    
    return {
        "source": "supabase",
        "total": len(supabase_ids),
        "synced": synced,
        "errors": errors,
    }


def verify_data_consistency(
    service: TwentyCRMService,
    contact_id: str,
) -> Dict[str, Any]:
    """Verify data consistency across all layers.
    
    Args:
        service: Twenty CRM service
        contact_id: Contact ID to verify
        
    Returns:
        Consistency report
    """
    logger.info(f"\nVerifying data consistency for contact {contact_id}...")
    
    # Fetch from each system
    bq_client = bigquery.Client(project=settings.effective_gcp_project)
    
    # BigQuery
    bq_query = """
    SELECT contact_id, canonical_name, category_code, llm_context
    FROM `identity.contacts_master`
    WHERE contact_id = @contact_id
    LIMIT 1
    """
    bq_job = bq_client.query(bq_query, job_config={
        "query_parameters": [("contact_id", "INT64", int(contact_id))]
    })
    bq_result = list(bq_job.result())
    bq_data = dict(bq_result[0]) if bq_result else None
    
    # Supabase
    supabase_result = service.supabase.table("contacts_master").select("*").eq("contact_id", contact_id).execute()
    supabase_data = supabase_result.data[0] if supabase_result.data else None
    
    # CRM
    crm_contacts = service.crm_client.list_contacts(limit=1000)
    crm_data = None
    for c in crm_contacts:
        if c.get("customFields", {}).get("contact_id") == contact_id:
            crm_data = c
            break
    
    # Compare
    consistency = {
        "contact_id": contact_id,
        "bigquery": bq_data is not None,
        "supabase": supabase_data is not None,
        "crm_twenty": crm_data is not None,
    }
    
    if bq_data and supabase_data and crm_data:
        # Check key fields
        consistency["canonical_name_match"] = (
            bq_data.get("canonical_name") == supabase_data.get("canonical_name") == crm_data.get("name")
        )
        consistency["category_code_match"] = (
            bq_data.get("category_code") == supabase_data.get("category_code") == crm_data.get("customFields", {}).get("category_code")
        )
    
    return consistency


def main() -> None:
    """Main push function."""
    parser = argparse.ArgumentParser(description="Push data through all layers")
    parser.add_argument(
        "--source",
        choices=["bigquery", "crm", "supabase", "all"],
        default="all",
        help="Source system to push from",
    )
    parser.add_argument(
        "--contact-id",
        help="Specific contact ID to push",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of contacts",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify data consistency after push",
    )
    
    args = parser.parse_args()
    
    logger.info("Initializing services...")
    
    try:
        with TwentyCRMService() as service:
            results = []
            
            if args.source in ("bigquery", "all"):
                result = push_from_bigquery(service, args.contact_id, args.limit)
                results.append(result)
            
            if args.source in ("crm", "all"):
                result = push_from_crm(service, args.contact_id, args.limit)
                results.append(result)
            
            if args.source in ("supabase", "all"):
                result = push_from_supabase(service, args.contact_id, args.limit)
                results.append(result)
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("PUSH SUMMARY")
            logger.info("=" * 60)
            
            for result in results:
                logger.info(f"\n{result['source'].upper()}:")
                logger.info(f"  Total: {result['total']}")
                logger.info(f"  Synced: {result['synced']}")
                logger.info(f"  Errors: {result['errors']}")
            
            # Verify if requested
            if args.verify and args.contact_id:
                consistency = verify_data_consistency(service, args.contact_id)
                logger.info("\n" + "=" * 60)
                logger.info("CONSISTENCY CHECK")
                logger.info("=" * 60)
                logger.info(f"Contact {args.contact_id}:")
                logger.info(f"  BigQuery: {'✅' if consistency['bigquery'] else '❌'}")
                logger.info(f"  Supabase: {'✅' if consistency['supabase'] else '❌'}")
                logger.info(f"  CRM Twenty: {'✅' if consistency['crm_twenty'] else '❌'}")
                if "canonical_name_match" in consistency:
                    logger.info(f"  Name Match: {'✅' if consistency['canonical_name_match'] else '❌'}")
                    logger.info(f"  Category Match: {'✅' if consistency['category_code_match'] else '❌'}")
    
    except Exception as e:
        logger.error(f"Failed to push data: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
