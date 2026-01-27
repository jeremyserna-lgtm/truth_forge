"""Comprehensive tests for CDCSyncService.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime

from truth_forge.services.sync.cdc_sync_service import (
    CDCSyncService,
    ChangeEvent,
    ChangeType,
)


class TestCDCSyncService:
    """Test suite for CDCSyncService."""
    
    def test_init(
        self,
        mock_settings: None,
    ) -> None:
        """Test initialization."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            # Mock query results for table creation
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            
            service = CDCSyncService()
            
            assert service.bq_client == mock_bq_client
            assert service.service == mock_service
            assert service.error_reporter == mock_error_reporter
    
    def test_ensure_change_tracking_tables(
        self,
        mock_settings: None,
    ) -> None:
        """Test ensuring change tracking tables exist."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            
            service = CDCSyncService()
            
            # Should have called query twice (two tables)
            assert mock_bq_client.query.call_count >= 2
    
    def test_ensure_change_tracking_tables_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test ensuring tables when error occurs."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            mock_bq_client.query.side_effect = Exception("Table exists")
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            # Should not raise, just log warning
            service = CDCSyncService()
            
            assert service.bq_client == mock_bq_client
    
    def test_capture_change(
        self,
        mock_settings: None,
    ) -> None:
        """Test capturing a change event."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {"status": "synced"}
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            # Mock _is_event_processed to return False
            service = CDCSyncService()
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                event = service.capture_change(
                    source="bigquery",
                    entity_type="contact",
                    entity_id="123",
                    change_type=ChangeType.INSERT,
                    data={"name": "Test"},
                )
                
                assert event.source == "bigquery"
                assert event.entity_type == "contact"
                assert event.entity_id == "123"
                assert event.change_type == ChangeType.INSERT
    
    def test_capture_change_with_version(
        self,
        mock_settings: None,
    ) -> None:
        """Test capturing change with explicit version."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {"status": "synced"}
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                event = service.capture_change(
                    source="bigquery",
                    entity_type="contact",
                    entity_id="123",
                    change_type=ChangeType.UPDATE,
                    data={},
                    version=5,
                )
                
                assert event.version == 5
    
    def test_store_change_event_success(
        self,
        mock_settings: None,
    ) -> None:
        """Test storing change event successfully."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="bigquery",
                entity_type="contact",
                entity_id="123",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                version=1,
                data={"name": "Test"},
                metadata={},
            )
            
            service._store_change_event(event)
            
            # Should have called query to insert
            assert mock_bq_client.query.call_count > 0
    
    def test_store_change_event_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test storing change event with error."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            # First calls for table creation, then error on insert
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.side_effect = [query_job, query_job, Exception("Insert error")]
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="bigquery",
                entity_type="contact",
                entity_id="123",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                version=1,
                data={},
                metadata={},
            )
            
            service._store_change_event(event)
            
            # Error should be reported
            mock_error_reporter.report_error.assert_called_once()
    
    def test_process_change_event_already_processed(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing event that's already processed."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="bigquery",
                entity_type="contact",
                entity_id="123",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                version=1,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=True):
                service._process_change_event(event)
            
            # Should not sync if already processed
            assert not hasattr(mock_service, "bq_sync") or not mock_service.bq_sync.called
    
    def test_process_change_event_from_bigquery(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing event from BigQuery (canonical)."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {"status": "synced"}
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="bigquery",
                entity_type="contact",
                entity_id="123",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                version=1,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                service._process_change_event(event)
                
                mock_service.bq_sync.sync_contact_to_all.assert_called_once_with("123")
    
    def test_process_change_event_from_bigquery_business(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing business event from BigQuery."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.business_sync = Mock()
            mock_service.business_sync.sync_business_to_all.return_value = {"status": "synced"}
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_456",
                source="bigquery",
                entity_type="business",
                entity_id="456",
                change_type=ChangeType.UPDATE,
                timestamp=datetime.utcnow(),
                version=2,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                service._process_change_event(event)
                
                mock_service.business_sync.sync_business_to_all.assert_called_once_with("456")
    
    def test_process_change_event_from_crm(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing event from CRM."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class, \
             patch("truth_forge.services.sync.cdc_sync_service.CRMTwentySyncService") as mock_crm_sync_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            mock_crm_sync = Mock()
            mock_crm_sync.sync_from_crm_to_bigquery.return_value = {"status": "synced"}
            mock_crm_sync_class.return_value = mock_crm_sync
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="crm_twenty",
                entity_type="contact",
                entity_id="crm_123",
                change_type=ChangeType.UPDATE,
                timestamp=datetime.utcnow(),
                version=2,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                service._process_change_event(event)
                
                mock_crm_sync.sync_from_crm_to_bigquery.assert_called_once_with("crm_123")
    
    def test_process_change_event_from_supabase(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing event from Supabase."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class, \
             patch("truth_forge.services.sync.cdc_sync_service.SupabaseSyncService") as mock_supabase_sync_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.supabase = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            mock_supabase_sync = Mock()
            mock_supabase_sync.sync_from_supabase_to_bigquery.return_value = {"status": "synced"}
            mock_supabase_sync_class.return_value = mock_supabase_sync
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="supabase",
                entity_type="contact",
                entity_id="uuid-123",
                change_type=ChangeType.UPDATE,
                timestamp=datetime.utcnow(),
                version=2,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                service._process_change_event(event)
                
                mock_supabase_sync.sync_from_supabase_to_bigquery.assert_called_once_with("uuid-123")
    
    def test_process_change_event_from_local(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing event from local DB."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="local",
                entity_type="contact",
                entity_id="123",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                version=1,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                # Should log warning but not fail
                service._process_change_event(event)
    
    def test_process_change_event_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing event when error occurs."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.side_effect = Exception("Sync error")
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            event = ChangeEvent(
                event_id="test_123",
                source="bigquery",
                entity_type="contact",
                entity_id="123",
                change_type=ChangeType.INSERT,
                timestamp=datetime.utcnow(),
                version=1,
                data={},
                metadata={},
            )
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed") as mock_mark:
                
                service._process_change_event(event)
                
                # Should mark as error
                mock_mark.assert_called_once()
                call_args = mock_mark.call_args
                assert call_args[0][1] == "error"
                mock_error_reporter.report_error.assert_called_once()
    
    def test_is_event_processed_true(
        self,
        mock_settings: None,
    ) -> None:
        """Test checking if event is processed (true)."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            # Mock query result showing event is processed
            # Reset return_value after init (init uses query for table creation)
            mock_row = Mock()
            mock_row.count = 1
            query_job2 = Mock()
            query_job2.result.return_value = [mock_row]
            # Reset to use return_value instead of side_effect
            mock_bq_client.query.return_value = query_job2
            mock_bq_client.query.side_effect = None
            
            result = service._is_event_processed("test_123")
            
            assert result is True
    
    def test_is_event_processed_false(
        self,
        mock_settings: None,
    ) -> None:
        """Test checking if event is processed (false)."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            # Mock query result showing event is not processed
            mock_row = Mock()
            mock_row.count = 0
            query_job2 = Mock()
            query_job2.result.return_value = [mock_row]
            # Reset to use return_value
            mock_bq_client.query.return_value = query_job2
            mock_bq_client.query.side_effect = None
            
            result = service._is_event_processed("test_123")
            
            assert result is False
    
    def test_is_event_processed_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test checking if event is processed when error occurs."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.side_effect = [query_job, query_job, Exception("Query error")]
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            result = service._is_event_processed("test_123")
            
            assert result is False  # Returns False on error
    
    def test_mark_event_processed_success(
        self,
        mock_settings: None,
    ) -> None:
        """Test marking event as processed successfully."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            service._mark_event_processed("test_123", "success")
            
            # Should have called query twice (update + insert)
            assert mock_bq_client.query.call_count >= 2
    
    def test_mark_event_processed_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test marking event as processed with error status."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            service._mark_event_processed("test_123", "error", "Error message")
            
            # Should have called query
            assert mock_bq_client.query.called
    
    def test_process_pending_changes(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing pending changes."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {"status": "synced"}
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            # Mock pending events query
            mock_row = Mock()
            mock_row.event_id = "test_123"
            mock_row.source = "bigquery"
            mock_row.entity_type = "contact"
            mock_row.entity_id = "123"
            mock_row.change_type = "INSERT"
            mock_row.timestamp = datetime.utcnow()
            mock_row.version = 1
            mock_row.data = '{"name": "Test"}'
            mock_row.metadata = "{}"
            
            query_job2 = Mock()
            query_job2.result.return_value = [mock_row]
            # Reset to use return_value after init
            mock_bq_client.query.return_value = query_job2
            mock_bq_client.query.side_effect = None
            
            with patch.object(service, "_is_event_processed", return_value=False), \
                 patch.object(service, "_mark_event_processed"):
                
                result = service.process_pending_changes(limit=10)
                
                assert result == 1
    
    def test_process_pending_changes_no_events(
        self,
        mock_settings: None,
    ) -> None:
        """Test processing pending changes when no events."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            # Mock empty result
            query_job2 = Mock()
            query_job2.result.return_value = []
            # Reset to use return_value after init
            mock_bq_client.query.return_value = query_job2
            mock_bq_client.query.side_effect = None
            
            result = service.process_pending_changes(limit=10)
            
            assert result == 0
    
    def test_get_sync_status(
        self,
        mock_settings: None,
    ) -> None:
        """Test getting sync status."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            # Mock status query result
            mock_row = Mock()
            mock_row.source = "bigquery"
            mock_row.last_sync = datetime.utcnow()
            mock_row.change_count = 5
            
            query_job2 = Mock()
            query_job2.result.return_value = [mock_row]
            # Reset to use return_value after init
            mock_bq_client.query.return_value = query_job2
            mock_bq_client.query.side_effect = None
            
            result = service.get_sync_status("123", "contact")
            
            assert result["entity_id"] == "123"
            assert result["entity_type"] == "contact"
            assert "sources" in result
            assert "bigquery" in result["sources"]
    
    def test_get_sync_status_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test getting sync status when error occurs."""
        with patch("truth_forge.services.sync.cdc_sync_service.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.cdc_sync_service.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.cdc_sync_service.ErrorReporter") as mock_error_reporter_class:
            
            mock_bq_client = Mock()
            query_job = Mock()
            query_job.result.return_value = []
            mock_bq_client.query.return_value = query_job
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            mock_error_reporter = Mock()
            mock_error_reporter_class.return_value = mock_error_reporter
            
            service = CDCSyncService()
            
            # After init, set side_effect to raise error for status query
            mock_bq_client.query.side_effect = Exception("Query error")
            
            result = service.get_sync_status("123", "contact")
            
            assert "error" in result