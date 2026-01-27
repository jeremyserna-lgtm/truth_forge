"""Automatic sync service - keeps all layers in sync automatically.

This service runs continuously and ensures:
- BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local DB
- All changes propagate automatically
- No manual intervention required
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
import time
import threading
from dataclasses import dataclass

from google.cloud import bigquery

from truth_forge.services.sync.twenty_crm_service import TwentyCRMService
from truth_forge.services.sync.bigquery_sync import BigQuerySyncService
from truth_forge.services.sync.supabase_sync import SupabaseSyncService
from truth_forge.services.sync.crm_twenty_sync import CRMTwentySyncService
from truth_forge.services.sync.error_reporter import ErrorReporter
from truth_forge.core.settings import settings

logger = logging.getLogger(__name__)


# Initialize service instance (singleton pattern)
_auto_sync_service: Optional["AutoSyncService"] = None


@dataclass
class SyncStats:
    """Sync statistics."""
    total_synced: int = 0
    total_errors: int = 0
    last_sync_time: Optional[datetime] = None
    last_error: Optional[str] = None


class AutoSyncService:
    """Automatic sync service that keeps all layers in sync.
    
    Runs continuously and syncs changes automatically:
    - Polls BigQuery for changes
    - Polls Twenty CRM for changes
    - Polls Supabase for changes
    - Propagates changes to all systems
    """
    
    def __init__(
        self,
        sync_interval_seconds: int = 300,  # 5 minutes
        batch_size: int = 100,
    ) -> None:
        """Initialize auto sync service.
        
        Args:
            sync_interval_seconds: How often to check for changes
            batch_size: Number of records to sync per batch
        """
        self.sync_interval = sync_interval_seconds
        self.batch_size = batch_size
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.stats = SyncStats()
        
        # Initialize clients (lazy initialization to avoid issues)
        self.bq_client: Optional[bigquery.Client] = None
        self.service: Optional[TwentyCRMService] = None
        self.error_reporter: Optional[ErrorReporter] = None
        
        # Track last sync times per source for efficient polling
        self.last_bq_sync: Optional[datetime] = None
        self.last_crm_sync: Optional[datetime] = None
        self.last_supabase_sync: Optional[datetime] = None
        
    def start(self) -> None:
        """Start the auto sync service."""
        if self.running:
            logger.warning("Auto sync service already running")
            return
        
        logger.info("=" * 60)
        logger.info("STARTING AUTO SYNC SERVICE")
        logger.info("=" * 60)
        logger.info(f"Sync interval: {self.sync_interval} seconds")
        logger.info(f"Batch size: {self.batch_size}")
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
        logger.info("✅ Auto sync service started")
        logger.info("   Service will keep all layers in sync automatically")
        logger.info("   Press Ctrl+C to stop")
    
    def stop(self) -> None:
        """Stop the auto sync service."""
        logger.info("Stopping auto sync service...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=10)
        logger.info("✅ Auto sync service stopped")
    
    def _run_loop(self) -> None:
        """Main sync loop."""
        while self.running:
            try:
                self._sync_cycle()
                time.sleep(self.sync_interval)
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in sync cycle: {e}", exc_info=True)
                self.stats.total_errors += 1
                self.stats.last_error = str(e)
                # Continue running even on errors
                time.sleep(self.sync_interval)
    
    def _ensure_clients(self) -> None:
        """Ensure clients are initialized."""
        if not self.bq_client:
            self.bq_client = bigquery.Client(project=settings.effective_gcp_project)
        if not self.service:
            self.service = TwentyCRMService()
        if not self.error_reporter:
            self.error_reporter = ErrorReporter(self.bq_client)
    
    def _sync_cycle(self) -> None:
        """One sync cycle - syncs changes from all sources."""
        self._ensure_clients()
        
        cycle_start = datetime.utcnow()
        logger.info(f"\n{'=' * 60}")
        logger.info(f"SYNC CYCLE - {cycle_start.isoformat()}")
        logger.info(f"{'=' * 60}")
        
        # 1. Sync from BigQuery (canonical) to all systems
        logger.info("\n[1/3] Syncing from BigQuery to all systems...")
        bq_synced = self._sync_from_bigquery()
        
        # 2. Sync from Twenty CRM to BigQuery (then propagates)
        logger.info("\n[2/3] Syncing from Twenty CRM to BigQuery...")
        crm_synced = self._sync_from_crm()
        
        # 3. Sync from Supabase to BigQuery (then propagates)
        logger.info("\n[3/3] Syncing from Supabase to BigQuery...")
        supabase_synced = self._sync_from_supabase()
        
        # Update stats
        total_synced = bq_synced + crm_synced + supabase_synced
        self.stats.total_synced += total_synced
        self.stats.last_sync_time = cycle_start
        
        cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
        logger.info(f"\n{'=' * 60}")
        logger.info(f"SYNC CYCLE COMPLETE")
        logger.info(f"{'=' * 60}")
        logger.info(f"Duration: {cycle_duration:.2f}s")
        logger.info(f"Synced: {total_synced} records")
        logger.info(f"Total synced (all time): {self.stats.total_synced}")
        logger.info(f"Total errors: {self.stats.total_errors}")
        logger.info(f"Next sync in: {self.sync_interval}s")
    
    def _sync_from_bigquery(self) -> int:
        """Sync changes from BigQuery to all systems.
        
        Returns:
            Number of contacts synced
        """
        try:
            # Get contacts modified since last BigQuery sync
            last_sync = self.last_bq_sync
            if not last_sync:
                # First run - sync contacts from last 24 hours
                last_sync = datetime.utcnow() - timedelta(days=1)
            
            query = """
            SELECT contact_id
            FROM `identity.contacts_master`
            WHERE updated_at > @last_sync
            ORDER BY updated_at DESC
            LIMIT @batch_size
            """
            
            job_config = {
                "query_parameters": [
                    ("last_sync", "TIMESTAMP", last_sync.isoformat()),
                    ("batch_size", "INT64", self.batch_size),
                ]
            }
            
            query_job = self.bq_client.query(query, job_config=job_config)
            results = list(query_job.result())
            
            if not results:
                logger.info("  No changes in BigQuery")
                return 0
            
            logger.info(f"  Found {len(results)} contacts to sync from BigQuery")
            
            synced = 0
            for row in results:
                try:
                    contact_id = str(row.contact_id)
                    result = self.service.bq_sync.sync_contact_to_all(contact_id)
                    
                    # Check if CRM sync succeeded
                    if result.get("crm_twenty", {}).get("status") == "synced":
                        synced += 1
                    else:
                        error = result.get("crm_twenty", {}).get("error")
                        logger.warning(f"  ⚠️  Contact {contact_id} sync issue: {error}")
                except Exception as e:
                    logger.error(f"  ❌ Failed to sync contact {row.contact_id}: {e}")
            
            logger.info(f"  ✅ Synced {synced}/{len(results)} contacts from BigQuery")
            
            # Update last sync time
            if synced > 0:
                self.last_bq_sync = datetime.utcnow()
            
            return synced
            
        except Exception as e:
            logger.error(f"Error syncing from BigQuery: {e}", exc_info=True)
            return 0
    
    def _sync_from_crm(self) -> int:
        """Sync changes from Twenty CRM to BigQuery.
        
        Returns:
            Number of contacts synced
        """
        if not self.service:
            self._ensure_clients()
        
        try:
            # Get contacts updated since last CRM sync
            last_sync = self.last_crm_sync
            if not last_sync:
                last_sync = datetime.utcnow() - timedelta(days=1)
            
            # List contacts from CRM
            contacts = self.service.crm_client.list_contacts(
                updated_since=last_sync,
                limit=self.batch_size,
            )
            
            if not contacts:
                logger.info("  No changes in Twenty CRM")
                return 0
            
            logger.info(f"  Found {len(contacts)} contacts to sync from CRM")
            
            synced = 0
            crm_sync = CRMTwentySyncService(
                self.service.crm_client,
                self.bq_client,
                self.service.bq_sync,
            )
            
            for contact in contacts:
                try:
                    crm_id = contact.get("id")
                    result = crm_sync.sync_from_crm_to_bigquery(crm_id)
                    
                    if result.get("status") == "synced":
                        synced += 1
                    else:
                        error = result.get("error")
                        logger.warning(f"  ⚠️  CRM contact {crm_id} sync issue: {error}")
                except Exception as e:
                    logger.error(f"  ❌ Failed to sync CRM contact {contact.get('id')}: {e}")
            
            logger.info(f"  ✅ Synced {synced}/{len(contacts)} contacts from CRM")
            
            # Update last sync time
            if synced > 0:
                self.last_crm_sync = datetime.utcnow()
            
            return synced
            
        except Exception as e:
            logger.error(f"Error syncing from CRM: {e}", exc_info=True)
            return 0
    
    def _sync_from_supabase(self) -> int:
        """Sync changes from Supabase to BigQuery.
        
        Returns:
            Number of contacts synced
        """
        if not self.service:
            self._ensure_clients()
        
        try:
            if not self.service.supabase:
                logger.debug("  Supabase not configured, skipping")
                return 0
            
            # Get contacts updated since last Supabase sync
            last_sync = self.last_supabase_sync
            if not last_sync:
                last_sync = datetime.utcnow() - timedelta(days=1)
            
            result = self.service.supabase.table("contacts_master").select("*").gte(
                "updated_at", last_sync.isoformat()
            ).limit(self.batch_size).execute()
            
            contacts = result.data
            if not contacts:
                logger.info("  No changes in Supabase")
                return 0
            
            logger.info(f"  Found {len(contacts)} contacts to sync from Supabase")
            
            synced = 0
            supabase_sync = SupabaseSyncService(
                self.service.supabase,
                self.bq_client,
                self.service.bq_sync,
            )
            
            for contact in contacts:
                try:
                    contact_id = contact.get("contact_id") or contact.get("id")
                    result = supabase_sync.sync_from_supabase_to_bigquery(contact_id)
                    
                    if result.get("status") == "synced":
                        synced += 1
                    else:
                        error = result.get("error")
                        logger.warning(f"  ⚠️  Supabase contact {contact_id} sync issue: {error}")
                except Exception as e:
                    logger.error(f"  ❌ Failed to sync Supabase contact {contact.get('id')}: {e}")
            
            logger.info(f"  ✅ Synced {synced}/{len(contacts)} contacts from Supabase")
            
            # Update last sync time
            if synced > 0:
                self.last_supabase_sync = datetime.utcnow()
            
            return synced
            
        except Exception as e:
            logger.error(f"Error syncing from Supabase: {e}", exc_info=True)
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get sync statistics.
        
        Returns:
            Statistics dict
        """
        return {
            "running": self.running,
            "total_synced": self.stats.total_synced,
            "total_errors": self.stats.total_errors,
            "last_sync_time": self.stats.last_sync_time.isoformat() if self.stats.last_sync_time else None,
            "last_error": self.stats.last_error,
            "sync_interval": self.sync_interval,
        }
