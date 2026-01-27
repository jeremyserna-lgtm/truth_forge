"""Comprehensive tests for WebhookSyncHandler.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch
import pytest

from truth_forge.services.sync.webhook_sync import WebhookSyncHandler


class TestWebhookSyncHandler:
    """Test suite for WebhookSyncHandler."""
    
    def test_init(
        self,
        mock_settings: None,
    ) -> None:
        """Test initialization."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            assert handler.bq_client == mock_bq_client
            assert handler.service == mock_service
    
    def test_handle_crm_webhook_created(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling CRM webhook for created event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.webhook_sync.CRMTwentySyncService") as mock_crm_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_crm_sync = Mock()
            mock_crm_sync.sync_from_crm_to_bigquery.return_value = {"status": "synced"}
            mock_crm_sync_class.return_value = mock_crm_sync
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "event": "created",
                "data": {"id": "crm_123"},
            }
            
            result = handler.handle_crm_webhook(webhook_data)
            
            assert result["status"] == "synced"
            mock_crm_sync.sync_from_crm_to_bigquery.assert_called_once_with("crm_123")
    
    def test_handle_crm_webhook_updated(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling CRM webhook for updated event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.webhook_sync.CRMTwentySyncService") as mock_crm_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_crm_sync = Mock()
            mock_crm_sync.sync_from_crm_to_bigquery.return_value = {"status": "synced"}
            mock_crm_sync_class.return_value = mock_crm_sync
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "event": "updated",
                "id": "crm_456",
            }
            
            result = handler.handle_crm_webhook(webhook_data)
            
            assert result["status"] == "synced"
            mock_crm_sync.sync_from_crm_to_bigquery.assert_called_once_with("crm_456")
    
    def test_handle_crm_webhook_deleted(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling CRM webhook for deleted event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "event": "deleted",
                "data": {"id": "crm_123"},
            }
            
            result = handler.handle_crm_webhook(webhook_data)
            
            assert result["status"] == "deleted"
    
    def test_handle_crm_webhook_unknown_event(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling CRM webhook for unknown event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "event": "unknown",
                "data": {"id": "crm_123"},
            }
            
            result = handler.handle_crm_webhook(webhook_data)
            
            assert result["status"] == "ignored"
            assert "Unknown event" in result["reason"]
    
    def test_handle_crm_webhook_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling CRM webhook with error."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.webhook_sync.CRMTwentySyncService") as mock_crm_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.crm_client = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_crm_sync = Mock()
            mock_crm_sync.sync_from_crm_to_bigquery.side_effect = Exception("Sync error")
            mock_crm_sync_class.return_value = mock_crm_sync
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "event": "created",
                "data": {"id": "crm_123"},
            }
            
            result = handler.handle_crm_webhook(webhook_data)
            
            assert result["status"] == "error"
            assert "Sync error" in result["error"]
    
    def test_handle_supabase_webhook_insert(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling Supabase webhook for INSERT event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.webhook_sync.SupabaseSyncService") as mock_supabase_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.supabase = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_supabase_sync = Mock()
            mock_supabase_sync.sync_from_supabase_to_bigquery.return_value = {"status": "synced"}
            mock_supabase_sync_class.return_value = mock_supabase_sync
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "type": "INSERT",
                "table": "contacts_master",
                "record": {"contact_id": "123"},
            }
            
            result = handler.handle_supabase_webhook(webhook_data)
            
            assert result["status"] == "synced"
            mock_supabase_sync.sync_from_supabase_to_bigquery.assert_called_once_with("123")
    
    def test_handle_supabase_webhook_update(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling Supabase webhook for UPDATE event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.webhook_sync.SupabaseSyncService") as mock_supabase_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.supabase = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_supabase_sync = Mock()
            mock_supabase_sync.sync_from_supabase_to_bigquery.return_value = {"status": "synced"}
            mock_supabase_sync_class.return_value = mock_supabase_sync
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "type": "UPDATE",
                "table": "contacts_master",
                "record": {"id": "uuid-123"},
            }
            
            result = handler.handle_supabase_webhook(webhook_data)
            
            assert result["status"] == "synced"
            mock_supabase_sync.sync_from_supabase_to_bigquery.assert_called_once_with("uuid-123")
    
    def test_handle_supabase_webhook_delete(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling Supabase webhook for DELETE event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "type": "DELETE",
                "table": "contacts_master",
                "record": {"contact_id": "123"},
            }
            
            result = handler.handle_supabase_webhook(webhook_data)
            
            assert result["status"] == "deleted"
    
    def test_handle_supabase_webhook_wrong_table(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling Supabase webhook for wrong table."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "type": "INSERT",
                "table": "other_table",
                "record": {"id": "123"},
            }
            
            result = handler.handle_supabase_webhook(webhook_data)
            
            assert result["status"] == "ignored"
            assert "Not contacts_master" in result["reason"]
    
    def test_handle_supabase_webhook_unknown_event(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling Supabase webhook for unknown event."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "type": "UNKNOWN",
                "table": "contacts_master",
                "record": {"contact_id": "123"},
            }
            
            result = handler.handle_supabase_webhook(webhook_data)
            
            assert result["status"] == "ignored"
            assert "Unknown event" in result["reason"]
    
    def test_handle_supabase_webhook_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling Supabase webhook with error."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class, \
             patch("truth_forge.services.sync.webhook_sync.SupabaseSyncService") as mock_supabase_sync_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.supabase = Mock()
            mock_service.bq_sync = Mock()
            mock_service_class.return_value = mock_service
            
            mock_supabase_sync = Mock()
            mock_supabase_sync.sync_from_supabase_to_bigquery.side_effect = Exception("Sync error")
            mock_supabase_sync_class.return_value = mock_supabase_sync
            
            handler = WebhookSyncHandler()
            
            webhook_data = {
                "type": "INSERT",
                "table": "contacts_master",
                "record": {"contact_id": "123"},
            }
            
            result = handler.handle_supabase_webhook(webhook_data)
            
            assert result["status"] == "error"
            assert "Sync error" in result["error"]
    
    def test_handle_bigquery_change_success(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling BigQuery change successfully."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.return_value = {"status": "synced"}
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            result = handler.handle_bigquery_change("123")
            
            assert result["status"] == "synced"
            mock_service.bq_sync.sync_contact_to_all.assert_called_once_with("123")
    
    def test_handle_bigquery_change_error(
        self,
        mock_settings: None,
    ) -> None:
        """Test handling BigQuery change with error."""
        with patch("truth_forge.services.sync.webhook_sync.bigquery.Client") as mock_bq_client_class, \
             patch("truth_forge.services.sync.webhook_sync.TwentyCRMService") as mock_service_class:
            
            mock_bq_client = Mock()
            mock_bq_client_class.return_value = mock_bq_client
            
            mock_service = Mock()
            mock_service.bq_sync = Mock()
            mock_service.bq_sync.sync_contact_to_all.side_effect = Exception("Sync error")
            mock_service_class.return_value = mock_service
            
            handler = WebhookSyncHandler()
            
            result = handler.handle_bigquery_change("123")
            
            assert result["status"] == "error"
            assert "Sync error" in result["error"]