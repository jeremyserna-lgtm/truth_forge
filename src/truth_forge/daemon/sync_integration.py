"""Daemon Integration for Automatic Sync Service.

Integrates the automatic sync service into the daemon so it runs automatically
on daemon startup without requiring separate scripts.
"""

from typing import Optional
import logging
import threading

from truth_forge.services.sync.industry_standard_sync import IndustryStandardSyncService

logger = logging.getLogger(__name__)


class SyncDaemonIntegration:
    """Integration of sync service into daemon."""
    
    def __init__(self) -> None:
        """Initialize sync daemon integration."""
        self.sync_service: Optional[IndustryStandardSyncService] = None
        self._thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start automatic sync service in daemon."""
        if self.sync_service and self.sync_service.running:
            logger.warning("Sync service already running")
            return
        
        logger.info("Starting automatic sync service in daemon...")
        
        # Create sync service
        self.sync_service = IndustryStandardSyncService(
            cdc_enabled=True,
            event_driven_enabled=True,
            polling_enabled=True,
            polling_interval=300,  # 5 minutes
        )
        
        # Start in background thread
        self._thread = threading.Thread(
            target=self._run_sync_service,
            daemon=True,
            name="AutoSyncService"
        )
        self._thread.start()
        
        logger.info("✅ Automatic sync service started in daemon")
    
    def stop(self) -> None:
        """Stop automatic sync service."""
        if self.sync_service:
            logger.info("Stopping automatic sync service...")
            self.sync_service.stop()
            self.sync_service = None
        
        if self._thread:
            self._thread.join(timeout=10)
            self._thread = None
        
        logger.info("✅ Automatic sync service stopped")
    
    def _run_sync_service(self) -> None:
        """Run sync service in background thread."""
        try:
            if self.sync_service:
                self.sync_service.start()
                
                # Keep thread alive while service runs
                while self.sync_service.running:
                    import time
                    time.sleep(1)
        except Exception as e:
            logger.error(f"Error in sync service thread: {e}", exc_info=True)
    
    @property
    def is_running(self) -> bool:
        """Check if sync service is running."""
        return self.sync_service is not None and self.sync_service.running
