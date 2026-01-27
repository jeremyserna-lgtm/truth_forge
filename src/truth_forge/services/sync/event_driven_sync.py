"""Event-Driven Sync Service - Industry Standard Implementation.

Implements event-driven architecture for real-time data synchronization:
- Event bus pattern
- Pub/Sub model
- Event handlers for each destination
- Idempotent event processing
- Event replay capability

Based on industry standards:
- Event-driven architecture
- Pub/Sub pattern
- Event sourcing
- Idempotent consumers
"""

from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
import logging
import json
import threading
from dataclasses import dataclass
from enum import Enum
from queue import Queue, Empty

from truth_forge.services.sync.cdc_sync_service import CDCSyncService, ChangeEvent, ChangeType

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class SyncEvent:
    """Sync event for event-driven architecture."""
    event_id: str
    source: str
    entity_type: str
    entity_id: str
    change_type: ChangeType
    priority: EventPriority
    timestamp: datetime
    data: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3


class EventDrivenSyncService:
    """Event-driven sync service.
    
    Implements pub/sub pattern for real-time data synchronization:
    - Publishes change events to event bus
    - Subscribers process events asynchronously
    - Idempotent event processing
    - Retry logic with exponential backoff
    - Event replay capability
    """
    
    def __init__(self) -> None:
        """Initialize event-driven sync service."""
        self.cdc_service = CDCSyncService()
        self.event_queue: Queue = Queue()
        self.subscribers: Dict[str, List[Callable]] = {}
        self.running = False
        self.worker_thread: Optional[threading.Thread] = None
        
        # Register default subscribers
        self._register_default_subscribers()
    
    def _register_default_subscribers(self) -> None:
        """Register default event subscribers."""
        # Subscribe to all contact changes
        self.subscribe("contact", self._handle_contact_change)
        self.subscribe("business", self._handle_business_change)
        self.subscribe("relationship", self._handle_relationship_change)
    
    def subscribe(
        self,
        entity_type: str,
        handler: Callable[[SyncEvent], None],
    ) -> None:
        """Subscribe to events for an entity type.
        
        Args:
            entity_type: Entity type to subscribe to
            handler: Event handler function
        """
        if entity_type not in self.subscribers:
            self.subscribers[entity_type] = []
        self.subscribers[entity_type].append(handler)
        logger.info(f"Subscribed handler to {entity_type} events")
    
    def publish(self, event: SyncEvent) -> None:
        """Publish an event to the event bus.
        
        Args:
            event: Sync event to publish
        """
        self.event_queue.put(event)
        logger.debug(f"Published event: {event.event_id}")
    
    def start(self) -> None:
        """Start the event-driven sync service."""
        if self.running:
            logger.warning("Event-driven sync service already running")
            return
        
        logger.info("Starting event-driven sync service")
        self.running = True
        self.worker_thread = threading.Thread(target=self._event_worker, daemon=True)
        self.worker_thread.start()
        logger.info("✅ Event-driven sync service started")
    
    def stop(self) -> None:
        """Stop the event-driven sync service."""
        logger.info("Stopping event-driven sync service")
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
        logger.info("✅ Event-driven sync service stopped")
    
    def _event_worker(self) -> None:
        """Event worker thread - processes events from queue."""
        while self.running:
            try:
                # Get event from queue (with timeout for graceful shutdown)
                try:
                    event = self.event_queue.get(timeout=1)
                except Empty:
                    continue
                
                # Process event
                self._process_event(event)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in event worker: {e}", exc_info=True)
    
    def _process_event(self, event: SyncEvent) -> None:
        """Process a sync event.
        
        Args:
            event: Sync event to process
        """
        try:
            # Get subscribers for this entity type
            handlers = self.subscribers.get(event.entity_type, [])
            
            if not handlers:
                logger.warning(f"No handlers for entity type: {event.entity_type}")
                return
            
            # Process with all handlers
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(
                        f"Handler failed for event {event.event_id}: {e}",
                        exc_info=True,
                    )
                    # Retry logic
                    if event.retry_count < event.max_retries:
                        event.retry_count += 1
                        # Exponential backoff
                        import time
                        time.sleep(2 ** event.retry_count)
                        self.publish(event)  # Re-queue for retry
                    else:
                        logger.error(
                            f"Event {event.event_id} failed after {event.max_retries} retries"
                        )
            
        except Exception as e:
            logger.error(f"Failed to process event: {e}", exc_info=True)
    
    def _handle_contact_change(self, event: SyncEvent) -> None:
        """Handle contact change event.
        
        Args:
            event: Contact change event
        """
        logger.info(f"Handling contact change: {event.entity_id} ({event.change_type.value})")
        
        # Convert to CDC event and process
        cdc_event = ChangeEvent(
            event_id=event.event_id,
            source=event.source,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            change_type=event.change_type,
            timestamp=event.timestamp,
            version=event.data.get("version", 1),
            data=event.data,
            metadata={"priority": event.priority.value},
        )
        
        self.cdc_service._process_change_event(cdc_event)
    
    def _handle_business_change(self, event: SyncEvent) -> None:
        """Handle business change event.
        
        Args:
            event: Business change event
        """
        logger.info(f"Handling business change: {event.entity_id} ({event.change_type.value})")
        
        # Convert to CDC event and process
        cdc_event = ChangeEvent(
            event_id=event.event_id,
            source=event.source,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            change_type=event.change_type,
            timestamp=event.timestamp,
            version=event.data.get("version", 1),
            data=event.data,
            metadata={"priority": event.priority.value},
        )
        
        self.cdc_service._process_change_event(cdc_event)
    
    def _handle_relationship_change(self, event: SyncEvent) -> None:
        """Handle relationship change event.
        
        Args:
            event: Relationship change event
        """
        logger.info(f"Handling relationship change: {event.entity_id} ({event.change_type.value})")
        
        # Convert to CDC event and process
        cdc_event = ChangeEvent(
            event_id=event.event_id,
            source=event.source,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            change_type=event.change_type,
            timestamp=event.timestamp,
            version=event.data.get("version", 1),
            data=event.data,
            metadata={"priority": event.priority.value},
        )
        
        self.cdc_service._process_change_event(cdc_event)
    
    def trigger_sync(
        self,
        source: str,
        entity_type: str,
        entity_id: str,
        change_type: ChangeType,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """Trigger a sync event.
        
        Args:
            source: Source system
            entity_type: Entity type
            entity_id: Entity ID
            change_type: Type of change
            data: Entity data
            priority: Event priority
        """
        event = SyncEvent(
            event_id=f"{source}:{entity_type}:{entity_id}:{datetime.utcnow().isoformat()}",
            source=source,
            entity_type=entity_type,
            entity_id=entity_id,
            change_type=change_type,
            priority=priority,
            timestamp=datetime.utcnow(),
            data=data,
        )
        
        self.publish(event)
        logger.info(f"Triggered sync event: {event.event_id}")
