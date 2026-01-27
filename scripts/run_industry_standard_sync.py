#!/usr/bin/env python3
"""Run Industry Standard Sync Service.

Implements industry-standard data synchronization:
- Change Data Capture (CDC)
- Event-Driven Architecture
- Polling for reliability
- All layers stay in sync automatically

Usage:
    python scripts/run_industry_standard_sync.py
    python scripts/run_industry_standard_sync.py --no-cdc
    python scripts/run_industry_standard_sync.py --no-event-driven
    python scripts/run_industry_standard_sync.py --no-polling
"""

import sys
import argparse
import signal
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.services.sync.industry_standard_sync import IndustryStandardSyncService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("industry_standard_sync.log"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Main function."""
    parser = argparse.ArgumentParser(description="Run industry standard sync service")
    parser.add_argument(
        "--no-cdc",
        action="store_true",
        help="Disable CDC change tracking",
    )
    parser.add_argument(
        "--no-event-driven",
        action="store_true",
        help="Disable event-driven sync",
    )
    parser.add_argument(
        "--no-polling",
        action="store_true",
        help="Disable polling-based sync",
    )
    parser.add_argument(
        "--polling-interval",
        type=int,
        default=300,
        help="Polling interval in seconds (default: 300)",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("INDUSTRY STANDARD SYNC SERVICE")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This service implements industry-standard patterns:")
    logger.info("  ✅ Change Data Capture (CDC) - Change tracking & audit trail")
    logger.info("  ✅ Event-Driven Architecture - Real-time sync")
    logger.info("  ✅ Polling - Reliability & catch-up")
    logger.info("")
    logger.info("All layers will stay in sync automatically:")
    logger.info("  - BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local DB")
    logger.info("")
    
    # Create service
    service = IndustryStandardSyncService(
        cdc_enabled=not args.no_cdc,
        event_driven_enabled=not args.no_event_driven,
        polling_enabled=not args.no_polling,
        polling_interval=args.polling_interval,
    )
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        logger.info("\n\nReceived shutdown signal...")
        service.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start service
    try:
        service.start()
        
        # Keep main thread alive
        logger.info("")
        logger.info("Service running. Press Ctrl+C to stop.")
        logger.info("")
        
        while service.running:
            import time
            time.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("\n\nShutting down...")
        service.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        service.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
