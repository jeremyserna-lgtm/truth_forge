"""Industry Standard Sync Service - Complete Implementation.

Combines CDC, event-driven architecture, and polling for comprehensive sync:
- CDC for change tracking
- Event-driven for real-time sync
- Polling for catch-up
- Idempotent operations
- Conflict resolution
- Eventual consistency

Based on industry standards:
- Change Data Capture (CDC)
- Event-Driven Architecture
- Event Sourcing
- Pub/Sub Pattern
- Eventual Consistency
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import threading
import time

from google.cloud import bigquery

from truth_forge.services.sync.cdc_sync_service import CDCSyncService, ChangeType
from truth_forge.services.sync.event_driven_sync import EventDrivenSyncService, EventPriority
from truth_forge.services.sync.auto_sync_service import AutoSyncService
from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.core.settings import settings

logger = logging.getLogger(__name__)


class IndustryStandardSyncService:
    """Industry Standard Sync Service.
    
    Combines multiple sync patterns for comprehensive data synchronization:
    - CDC for change tracking and audit trail
    - Event-driven for real-time sync
    - Polling for catch-up and reliability
    - Idempotent operations
    - Conflict resolution
    - Eventual consistency
    """
    
    def __init__(
        self,
        cdc_enabled: bool = True,
        event_driven_enabled: bool = True,
        polling_enabled: bool = True,
        polling_interval: int = 300,  # 5 minutes
    ) -> None:
        """Initialize industry standard sync service.
        
        Args:
            cdc_enabled: Enable CDC change tracking
            event_driven_enabled: Enable event-driven sync
            polling_enabled: Enable polling-based sync
            polling_interval: Polling interval in seconds
        """
        self.cdc_enabled = cdc_enabled
        self.event_driven_enabled = event_driven_enabled
        self.polling_enabled = polling_enabled
        self.polling_interval = polling_interval
        
        # Initialize services
        self.cdc_service: Optional[CDCSyncService] = None
        self.event_service: Optional[EventDrivenSyncService] = None
        self.polling_service: Optional[AutoSyncService] = None
        
        if cdc_enabled:
            self.cdc_service = CDCSyncService()
        
        if event_driven_enabled:
            self.event_service = EventDrivenSyncService()
        
        if polling_enabled:
            self.polling_service = AutoSyncService(
                sync_interval_seconds=polling_interval,
            )
        
        self.running = False
        self.thread: Optional[threading.Thread] = None
    
    def start(self) -> None:
        """Start all sync services."""
        if self.running:
            logger.warning("Industry standard sync service already running")
            return
        
        logger.info("=" * 60)
        logger.info("STARTING INDUSTRY STANDARD SYNC SERVICE")
        logger.info("=" * 60)
        logger.info(f"CDC: {'✅' if self.cdc_enabled else '❌'}")
        logger.info(f"Event-Driven: {'✅' if self.event_driven_enabled else '❌'}")
        logger.info(f"Polling: {'✅' if self.polling_enabled else '❌'}")
        logger.info("")
        
        # Start CDC service (always available for change tracking)
        if self.cdc_service:
            logger.info("CDC service ready")
        
        # Start event-driven service
        if self.event_service:
            self.event_service.start()
            logger.info("✅ Event-driven sync service started")
        
        # Start polling service
        if self.polling_service:
            self.polling_service.start()
            logger.info("✅ Polling sync service started")
        
        # Start CDC change processor
        if self.cdc_service:
            self.running = True
            self.thread = threading.Thread(target=self._cdc_processor_loop, daemon=True)
            self.thread.start()
            logger.info("✅ CDC change processor started")
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("INDUSTRY STANDARD SYNC SERVICE RUNNING")
        logger.info("=" * 60)
        logger.info("All layers will stay in sync automatically")
        logger.info("Press Ctrl+C to stop")
        logger.info("")
    
    def stop(self) -> None:
        """Stop all sync services."""
        logger.info("Stopping industry standard sync service...")
        self.running = False
        
        if self.event_service:
            self.event_service.stop()
        
        if self.polling_service:
            self.polling_service.stop()
        
        if self.thread:
            self.thread.join(timeout=10)
        
        logger.info("✅ Industry standard sync service stopped")
    
    def _cdc_processor_loop(self) -> None:
        """CDC change processor loop - processes pending changes."""
        while self.running:
            try:
                if self.cdc_service:
                    # Process pending changes
                    processed = self.cdc_service.process_pending_changes(limit=100)
                    if processed > 0:
                        logger.info(f"Processed {processed} pending CDC changes")
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in CDC processor loop: {e}", exc_info=True)
                time.sleep(60)
    
    def capture_change(
        self,
        source: str,
        entity_type: str,
        entity_id: str,
        change_type: ChangeType,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """Capture and process a change.
        
        This is the main entry point for capturing changes from any source.
        It will:
        1. Store change in CDC change log
        2. Publish event to event bus (if enabled)
        3. Trigger immediate sync
        
        Args:
            source: Source system
            entity_type: Entity type
            entity_id: Entity ID
            change_type: Type of change
            data: Entity data
            priority: Event priority
        """
        # Capture in CDC
        if self.cdc_service:
            event = self.cdc_service.capture_change(
                source=source,
                entity_type=entity_type,
                entity_id=entity_id,
                change_type=change_type,
                data=data,
            )
            logger.info(f"Captured change: {event.event_id}")
        
        # Publish to event bus
        if self.event_service:
            self.event_service.trigger_sync(
                source=source,
                entity_type=entity_type,
                entity_id=entity_id,
                change_type=change_type,
                data=data,
                priority=priority,
            )
            logger.debug(f"Published event for: {entity_id}")
    
    def get_sync_status(self, entity_id: str, entity_type: str = "contact") -> Dict[str, Any]:
        """Get comprehensive sync status for an entity.
        
        Args:
            entity_id: Entity ID
            entity_type: Entity type
            
        Returns:
            Sync status dictionary
        """
        status = {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Get CDC status
        if self.cdc_service:
            cdc_status = self.cdc_service.get_sync_status(entity_id, entity_type)
            status["cdc"] = cdc_status
        
        # Get polling status
        if self.polling_service:
            stats = self.polling_service.get_stats()
            status["polling"] = {
                "running": stats.get("running", False),
                "last_sync": stats.get("last_sync_time"),
                "total_synced": stats.get("total_synced", 0),
            }
        
        return status
    
    def sync_contact_now(self, contact_id: str, source: str = "bigquery") -> Dict[str, Any]:
        """Manually trigger sync for a contact.
        
        Args:
            contact_id: Contact ID
            source: Source system
            
        Returns:
            Sync result
        """
        logger.info(f"Manually syncing contact {contact_id} from {source}")
        
        # Fetch contact data
        service = TwentyCRMService()
        
        if source == "bigquery":
            # Fetch from BigQuery
            contact = service.bq_sync._fetch_from_bigquery(contact_id)
            if not contact:
                return {"error": f"Contact {contact_id} not found in BigQuery"}
            
            # Capture change
            self.capture_change(
                source="bigquery",
                entity_type="contact",
                entity_id=contact_id,
                change_type=ChangeType.UPDATE,
                data=contact,
                priority=EventPriority.HIGH,
            )
            
            # Also trigger immediate sync
            result = service.bq_sync.sync_contact_to_all(contact_id)
            return result
        
        elif source == "crm_twenty":
            # Fetch from CRM
            contact = service.crm_client.get_contact(contact_id)
            if not contact:
                return {"error": f"Contact {contact_id} not found in CRM"}
            
            # Capture change
            self.capture_change(
                source="crm_twenty",
                entity_type="contact",
                entity_id=contact_id,
                change_type=ChangeType.UPDATE,
                data=contact,
                priority=EventPriority.HIGH,
            )
            
            # Trigger sync
            crm_sync = service.crm_sync
            result = crm_sync.sync_from_crm_to_bigquery(contact_id)
            return result
        
        else:
            return {"error": f"Unknown source: {source}"}
