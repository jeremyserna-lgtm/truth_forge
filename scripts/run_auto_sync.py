#!/usr/bin/env python3
"""Run automatic sync service.

This service keeps all layers (BigQuery, Twenty CRM, Supabase, Local) in sync automatically.
Runs continuously and requires no manual intervention.

Usage:
    python scripts/run_auto_sync.py [--interval SECONDS] [--batch-size N]
    
    # Run in background
    nohup python scripts/run_auto_sync.py > auto_sync.log 2>&1 &
"""

import sys
import argparse
import signal
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.services.sync.auto_sync_service import AutoSyncService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("auto_sync.log"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Run automatic sync service")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Sync interval in seconds (default: 300 = 5 minutes)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for syncing (default: 100)",
    )
    parser.add_argument(
        "--initial-sync",
        action="store_true",
        help="Run initial full sync before starting auto sync",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("AUTOMATIC SYNC SERVICE")
    logger.info("=" * 60)
    logger.info(f"Sync interval: {args.interval} seconds")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info("")
    logger.info("This service will:")
    logger.info("  - Keep BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local in sync")
    logger.info("  - Run automatically every {} seconds".format(args.interval))
    logger.info("  - Require no manual intervention")
    logger.info("  - Log all activity to auto_sync.log")
    logger.info("")
    
    # Create service
    service = AutoSyncService(
        sync_interval_seconds=args.interval,
        batch_size=args.batch_size,
    )
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        logger.info("\n\nReceived shutdown signal...")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run initial sync if requested
    if args.initial_sync:
        logger.info("Running initial full sync...")
        from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
        from google.cloud import bigquery
        from truth_forge.core.settings import settings
        
        bq_client = bigquery.Client(project=settings.effective_gcp_project)
        
        with TwentyCRMService() as sync_service:
            # Get all contact IDs
            query = """
            SELECT contact_id
            FROM `identity.contacts_master`
            ORDER BY contact_id
            """
            results = list(bq_client.query(query).result())
            contact_ids = [str(row.contact_id) for row in results]
            
            logger.info(f"Syncing {len(contact_ids)} contacts initially...")
            
            for i, contact_id in enumerate(contact_ids, 1):
                if i % 10 == 0:
                    logger.info(f"  Progress: {i}/{len(contact_ids)}")
                try:
                    sync_service.bq_sync.sync_contact_to_all(contact_id)
                except Exception as e:
                    logger.error(f"  Failed to sync {contact_id}: {e}")
            
            logger.info("✅ Initial sync complete!")
    
    # Start auto sync service
    try:
        service.start()
        
        # Keep main thread alive
        logger.info("\n" + "=" * 60)
        logger.info("AUTO SYNC SERVICE RUNNING")
        logger.info("=" * 60)
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        while service.running:
            import time
            time.sleep(1)
            
            # Print stats periodically
            if service.stats.last_sync_time:
                from datetime import datetime
                elapsed = (datetime.utcnow() - service.stats.last_sync_time).total_seconds()
                if elapsed > 600:  # 10 minutes
                    stats = service.get_stats()
                    logger.info(f"\n📊 Stats: {stats['total_synced']} synced, "
                              f"{stats['total_errors']} errors, "
                              f"last sync: {stats['last_sync_time']}")
                    # Don't reset timer - let it track actual last sync
        
    except KeyboardInterrupt:
        logger.info("\n\nShutting down...")
        service.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    from datetime import datetime
    main()
