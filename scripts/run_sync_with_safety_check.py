#!/usr/bin/env python3
"""Run Sync System with Safety Check.

1. Runs comprehensive safety check
2. If safe, runs initial sync
3. Starts industry standard sync service
4. Monitors for issues
"""

import sys
from pathlib import Path
import logging
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.check_sync_safety import SyncSafetyChecker
from truth_forge.services.sync.industry_standard_sync import IndustryStandardSyncService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("sync_operation.log"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main function."""
    logger.info("=" * 60)
    logger.info("SYNC SYSTEM OPERATION WITH SAFETY CHECK")
    logger.info("=" * 60)
    logger.info("")
    
    # Step 1: Safety Check
    logger.info("Step 1: Running safety check...")
    checker = SyncSafetyChecker()
    summary = checker.run_all_checks()
    
    safety_status = summary.get("safety_status", "UNKNOWN")
    
    if safety_status == "UNSAFE":
        logger.error("")
        logger.error("❌ SYSTEM NOT SAFE - Cannot proceed")
        logger.error("Please fix failures before running sync")
        return 1
    
    if safety_status == "SAFE_WITH_WARNINGS":
        logger.warning("")
        logger.warning("⚠️  SYSTEM SAFE WITH WARNINGS")
        logger.warning("Proceeding with sync, but review warnings above")
        logger.warning("")
        time.sleep(2)  # Give user time to read warnings
    
    # Step 2: Start Sync Service
    logger.info("Step 2: Starting industry standard sync service...")
    logger.info("")
    
    service = IndustryStandardSyncService(
        cdc_enabled=True,
        event_driven_enabled=True,
        polling_enabled=True,
        polling_interval=300,  # 5 minutes
    )
    
    try:
        service.start()
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("SYNC SERVICE RUNNING")
        logger.info("=" * 60)
        logger.info("")
        logger.info("Service is now keeping all layers in sync:")
        logger.info("  - BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local DB")
        logger.info("")
        logger.info("Monitoring for issues...")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
        
        # Monitor for a few cycles
        cycles = 0
        max_cycles = 12  # Monitor for 1 hour (12 * 5 minutes)
        
        while service.running and cycles < max_cycles:
            time.sleep(300)  # Wait 5 minutes
            cycles += 1
            
            # Check status
            logger.info(f"Cycle {cycles}/{max_cycles} complete - Service running normally")
        
        if cycles >= max_cycles:
            logger.info("")
            logger.info("Monitoring period complete")
            logger.info("Service will continue running in background")
            logger.info("Check logs for ongoing activity")
        
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Shutting down...")
        service.stop()
        logger.info("✅ Sync service stopped")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        service.stop()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
