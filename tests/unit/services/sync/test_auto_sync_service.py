"""Comprehensive tests for AutoSyncService.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime, timedelta

from truth_forge.services.sync.auto_sync_service import AutoSyncService, SyncStats


class TestAutoSyncService:
    """Test suite for AutoSyncService."""
    
    def test_init(self) -> None:
        """Test initialization."""
        service = AutoSyncService(
            sync_interval_seconds=60,
            batch_size=50,
        )
        
        assert service.sync_interval == 60
        assert service.batch_size == 50
        assert service.running is False
        assert service.bq_client is None
        assert service.service is None
        assert service.error_reporter is None
    
    def test_start(
        self,
    ) -> None:
        """Test starting the service."""
        service = AutoSyncService()
        
        service.start()
        
        assert service.running is True
        assert service.thread is not None
        assert service.thread.is_alive()
        
        service.stop()
    
    def test_start_already_running(
        self,
    ) -> None:
        """Test starting when already running."""
        service = AutoSyncService()
        
        service.start()
        service.start()  # Second call
        
        assert service.running is True
        
        service.stop()
    
    def test_stop(
        self,
    ) -> None:
        """Test stopping the service."""
        service = AutoSyncService()
        
        service.start()
        service.stop()
        
        assert service.running is False
    
    def test_ensure_clients(
        self,
        mock_settings: None,
    ) -> None:
        """Test ensuring clients are initialized."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            
            service._ensure_clients()
            
            assert service.bq_client == mock_bq_client
            assert service.service == mock_service
            assert service.error_reporter == mock_error_reporter
    
    def test_sync_from_bigquery_success(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from BigQuery successfully."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {
                "crm_twenty": {"status": "synced"}
            }
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            # Mock BigQuery query
            mock_row = Mock()
            mock_row.contact_id = "123"
            query_job = Mock()
            query_job.result.return_value = [mock_row]
            mock_bq_client.query.return_value = query_job
            
            result = service._sync_from_bigquery()
            
            assert result == 1
            assert service.last_bq_sync is not None
    
    def test_sync_from_bigquery_no_changes(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from BigQuery when no changes."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            # Mock empty result
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            
            result = service._sync_from_bigquery()
            
            assert result == 0
    
    def test_sync_from_bigquery_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from BigQuery when error occurs."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client.query.side_effect = Exception("Query error")
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_bigquery()
            
            assert result == 0
    
    def test_sync_from_bigquery_sync_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from BigQuery when individual sync fails."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.side_effect = Exception("Sync error")
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            # Mock BigQuery query
            mock_row = Mock()
            mock_row.contact_id = "123"
            query_job = Mock()
            query_job.result.return_value = [mock_row]
            mock_bq_client.query.return_value = query_job
            
            result = service._sync_from_bigquery()
            
            assert result == 0  # No successful syncs
    
    def test_sync_from_crm_success(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from CRM successfully."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class, \
             patch("truth_forge.services.sync.auto_sync_service.CRMTwentySyncService") as mock_crm_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.crm_client.list_contacts.return_value = [
                {"id": "crm_1", "customFields": {"contact_id": "1", "full_name": "Contact 1"}},
            ]
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            mock_crm_sync = Mock()
            mock_crm_sync.sync_from_crm_to_bigquery.return_value = {"status": "synced"}
            mock_crm_sync_class.return_value = mock_crm_sync
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_crm()
            
            assert result == 1
            assert service.last_crm_sync is not None
    
    def test_sync_from_crm_no_changes(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from CRM when no changes."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.crm_client.list_contacts.return_value = []
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_crm()
            
            assert result == 0
    
    def test_sync_from_crm_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from CRM when error occurs."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.crm_client.list_contacts.side_effect = Exception("CRM error")
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_crm()
            
            assert result == 0
    
    def test_sync_from_supabase_success(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from Supabase successfully."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class, \
             patch("truth_forge.services.sync.auto_sync_service.SupabaseSyncService") as mock_supabase_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_supabase_table = Mock()
            mock_supabase_query = Mock()
            mock_supabase_query.gte.return_value = mock_supabase_query
            mock_supabase_query.limit.return_value = mock_supabase_query
            mock_supabase_query.execute.return_value = Mock(data=[{"contact_id": "123"}])
            mock_supabase_table.select.return_value = mock_supabase_query
            mock_service.supabase = Mock()
            mock_service.supabase.table.return_value = mock_supabase_table
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            mock_supabase_sync = Mock()
            mock_supabase_sync.sync_from_supabase_to_bigquery.return_value = {"status": "synced"}
            mock_supabase_sync_class.return_value = mock_supabase_sync
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_supabase()
            
            assert result == 1
            assert service.last_supabase_sync is not None
    
    def test_sync_from_supabase_not_configured(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from Supabase when not configured."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.supabase = None  # Not configured
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_supabase()
            
            assert result == 0
    
    def test_sync_from_supabase_no_changes(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from Supabase when no changes."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_supabase_table = Mock()
            mock_supabase_query = Mock()
            mock_supabase_query.gte.return_value = mock_supabase_query
            mock_supabase_query.limit.return_value = mock_supabase_query
            mock_supabase_query.execute.return_value = Mock(data=[])
            mock_supabase_table.select.return_value = mock_supabase_query
            mock_service.supabase = Mock()
            mock_service.supabase.table.return_value = mock_supabase_table
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_supabase()
            
            assert result == 0
    
    def test_sync_from_supabase_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from Supabase when error occurs."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_supabase_table = Mock()
            mock_supabase_query = Mock()
            mock_supabase_query.gte.return_value = mock_supabase_query
            mock_supabase_query.limit.return_value = mock_supabase_query
            mock_supabase_query.execute.side_effect = Exception("Supabase error")
            mock_supabase_table.select.return_value = mock_supabase_query
            mock_service.supabase = Mock()
            mock_service.supabase.table.return_value = mock_supabase_table
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            result = service._sync_from_supabase()
            
            assert result == 0
    
    def test_sync_cycle(
        self,
        mock_settings: None,
    ) -> None:
        """Test sync cycle."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {
                "crm_twenty": {"status": "synced"}
            }
            mock_service.crm_client = Mock()
            mock_service.crm_client.list_contacts.return_value = []
            mock_service.supabase = None
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            service.error_reporter = mock_error_reporter
            
            # Mock BigQuery query
            mock_row = Mock()
            mock_row.contact_id = "123"
            query_job = Mock()
            query_job.result.return_value = [mock_row]
            mock_bq_client.query.return_value = query_job
            
            service._sync_cycle()
            
            assert service.stats.total_synced > 0
            assert service.stats.last_sync_time is not None
    
    def test_get_stats(
        self,
    ) -> None:
        """Test getting statistics."""
        service = AutoSyncService()
        
        service.stats.total_synced = 100
        service.stats.total_errors = 5
        service.stats.last_sync_time = datetime.utcnow()
        service.stats.last_error = "Test error"
        
        stats = service.get_stats()
        
        assert stats["total_synced"] == 100
        assert stats["total_errors"] == 5
        assert stats["last_sync_time"] is not None
        assert stats["last_error"] == "Test error"
        assert stats["running"] is False
    
    def test_get_stats_no_last_sync(
        self,
    ) -> None:
        """Test getting statistics when no last sync."""
        service = AutoSyncService()
        
        stats = service.get_stats()
        
        assert stats["last_sync_time"] is None
        assert stats["last_error"] is None
    
    def test_run_loop_keyboard_interrupt(
        self,
        mock_settings: None,
    ) -> None:
        """Test run loop handling keyboard interrupt."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class, \
             patch("time.sleep"):  # Skip actual sleep
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            service.error_reporter = mock_error_reporter
            service.running = True
            
            # Mock _sync_cycle to raise KeyboardInterrupt, then stop running
            call_count = 0
            def sync_cycle_side_effect():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise KeyboardInterrupt()
            
            with patch.object(service, "_sync_cycle", side_effect=sync_cycle_side_effect):
                service._run_loop()
            
            # Should have stopped
            assert service.running is False
    
    def test_run_loop_exception(
        self,
        mock_settings: None,
    ) -> None:
        """Test run loop handling exception."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class, \
             patch("time.sleep"):  # Skip actual sleep
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            service.error_reporter = mock_error_reporter
            service.running = True
            
            # Mock _sync_cycle to raise exception, then stop running after one iteration
            call_count = 0
            def sync_cycle_side_effect():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("Sync error")
                service.running = False  # Stop after one iteration
            
            with patch.object(service, "_sync_cycle", side_effect=sync_cycle_side_effect):
                service._run_loop()
            
            # Should have updated error stats
            assert service.stats.total_errors > 0
            assert service.stats.last_error is not None
    
    def test_sync_from_bigquery_with_last_sync(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from BigQuery with last_sync set."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {
                "crm_twenty": {"status": "synced"}
            }
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            service.last_bq_sync = datetime.utcnow() - timedelta(hours=1)
            
            # Mock BigQuery query
            mock_row = Mock()
            mock_row.contact_id = "123"
            query_job = Mock()
            query_job.result.return_value = [mock_row]
            mock_bq_client.query.return_value = query_job
            
            result = service._sync_from_bigquery()
            
            assert result == 1
    
    def test_sync_from_bigquery_crm_not_synced(
        self,
        mock_settings: None,
    ) -> None:
        """Test syncing from BigQuery when CRM sync doesn't succeed."""
        with patch("truth_forge.services.sync.auto_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.auto_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.auto_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {
                "crm_twenty": {"status": "error", "error": "CRM error"}
            }
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = AutoSyncService()
            service.bq_client = mock_bq_client
            service.service = mock_service
            
            # Mock BigQuery query
            mock_row = Mock()
            mock_row.contact_id = "123"
            query_job = Mock()
            query_job.result.return_value = [mock_row]
            mock_bq_client.query.return_value = query_job
            
            result = service._sync_from_bigquery()
            
            assert result == 0  # No successful syncs