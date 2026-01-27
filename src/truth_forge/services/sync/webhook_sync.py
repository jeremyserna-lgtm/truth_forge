"""Webhook-based sync for real-time synchronization.

Handles webhooks from Twenty CRM, Supabase, and other systems
to trigger immediate sync when changes occur.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.services.sync.crm_twenty_sync import CRMTwentySyncService
from truth_forge.services.sync.supabase_sync import SupabaseSyncService
from truth_forge.core.settings import settings
from google.cloud import bigquery

logger = logging.getLogger(__name__)


class WebhookSyncHandler:
    """Handles webhooks for real-time sync.
    
    When a change occurs in any system, webhook triggers immediate sync.
    """
    
    def __init__(self) -> None:
        """Initialize webhook handler."""
        self.bq_client = bigquery.Client(project=settings.effective_gcp_project)
        self.service = TwentyCRMService()
    
    def handle_crm_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook from Twenty CRM.
        
        Args:
            webhook_data: Webhook payload from CRM
            
        Returns:
            Sync result
        """
        try:
            event_type = webhook_data.get("event")
            contact_data = webhook_data.get("data", {})
            crm_id = contact_data.get("id") or webhook_data.get("id")
            
            logger.info(f"Received CRM webhook: {event_type} for contact {crm_id}")
            
            if event_type in ("created", "updated"):
                # Sync from CRM to BigQuery (then propagates)
                crm_sync = CRMTwentySyncService(
                    self.service.crm_client,
                    self.bq_client,
                    self.service.bq_sync,
                )
                result = crm_sync.sync_from_crm_to_bigquery(crm_id)
                return {"status": "synced", "result": result}
            elif event_type == "deleted":
                # Handle deletion
                logger.warning(f"Contact {crm_id} deleted in CRM - sync handled")
                return {"status": "deleted"}
            else:
                logger.warning(f"Unknown event type: {event_type}")
                return {"status": "ignored", "reason": f"Unknown event: {event_type}"}
                
        except Exception as e:
            logger.error(f"Error handling CRM webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def handle_supabase_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webhook from Supabase.
        
        Args:
            webhook_data: Webhook payload from Supabase
            
        Returns:
            Sync result
        """
        try:
            event_type = webhook_data.get("type")  # INSERT, UPDATE, DELETE
            table = webhook_data.get("table")
            record = webhook_data.get("record", {})
            
            if table != "contacts_master":
                return {"status": "ignored", "reason": f"Not contacts_master table"}
            
            contact_id = record.get("contact_id") or record.get("id")
            logger.info(f"Received Supabase webhook: {event_type} for contact {contact_id}")
            
            if event_type in ("INSERT", "UPDATE"):
                # Sync from Supabase to BigQuery (then propagates)
                supabase_sync = SupabaseSyncService(
                    self.service.supabase,
                    self.bq_client,
                    self.service.bq_sync,
                )
                result = supabase_sync.sync_from_supabase_to_bigquery(contact_id)
                return {"status": "synced", "result": result}
            elif event_type == "DELETE":
                logger.warning(f"Contact {contact_id} deleted in Supabase")
                return {"status": "deleted"}
            else:
                return {"status": "ignored", "reason": f"Unknown event: {event_type}"}
                
        except Exception as e:
            logger.error(f"Error handling Supabase webhook: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
    
    def handle_bigquery_change(self, contact_id: str) -> Dict[str, Any]:
        """Handle change detected in BigQuery.
        
        Args:
            contact_id: Contact ID that changed
            
        Returns:
            Sync result
        """
        try:
            logger.info(f"Syncing contact {contact_id} from BigQuery to all systems")
            result = self.service.bq_sync.sync_contact_to_all(contact_id)
            return {"status": "synced", "result": result}
        except Exception as e:
            logger.error(f"Error syncing from BigQuery: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}
