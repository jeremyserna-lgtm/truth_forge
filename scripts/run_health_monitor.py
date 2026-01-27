#!/usr/bin/env python3
"""Run Health Monitor for Sync Service.

Monitors sync service and restarts if it stops.
Can run as separate service or integrate into daemon.
"""

import sys
from pathlib import Path
import logging
import signal

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from truth_forge.services.sync.health_monitor import SyncHealthMonitor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("sync_health_monitor.log"),
    ],
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main function."""
    logger.info("=" * 60)
    logger.info("SYNC HEALTH MONITOR")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This monitor will:")
    logger.info("  ✅ Check sync service health every minute")
    logger.info("  ✅ Restart service if it stops")
    logger.info("  ✅ Log all activity")
    logger.info("")
    
    monitor = SyncHealthMonitor(
        check_interval=60,  # Check every minute
        restart_on_failure=True,
        max_restart_attempts=5,
        restart_cooldown=300,  # 5 minutes between restarts
    )
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        logger.info("\n\nReceived shutdown signal...")
        monitor.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start monitor
    try:
        monitor.start()
        
        logger.info("")
        logger.info("Health monitor running. Press Ctrl+C to stop.")
        logger.info("")
        
        # Keep main thread alive
        while monitor.running:
            import time
            time.sleep(1)
            
            # Print status every 5 minutes
            if hasattr(monitor, '_last_status_print'):
                elapsed = time.time() - monitor._last_status_print
                if elapsed > 300:  # 5 minutes
                    status = monitor.get_status()
                    logger.info(f"📊 Status: Service healthy={status['service_healthy']}, "
                              f"Restarts={status['restart_count']}")
                    monitor._last_status_print = time.time()
            else:
                monitor._last_status_print = time.time()
        
    except KeyboardInterrupt:
        logger.info("\n\nShutting down...")
        monitor.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        monitor.stop()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
