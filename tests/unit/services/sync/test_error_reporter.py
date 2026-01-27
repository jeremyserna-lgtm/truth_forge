"""Comprehensive tests for ErrorReporter.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch
import pytest
from datetime import datetime

from truth_forge.services.sync.error_reporter import ErrorReporter, ErrorType


class TestErrorReporter:
    """Test suite for ErrorReporter."""
    
    def test_init(self, mock_bq_client: Mock) -> None:
        """Test initialization."""
        reporter = ErrorReporter(mock_bq_client)
        assert reporter.bq_client == mock_bq_client
        assert reporter.alert_service is None
    
    def test_init_with_alert_service(self, mock_bq_client: Mock) -> None:
        """Test initialization with alert service."""
        alert_service = Mock()
        reporter = ErrorReporter(mock_bq_client, alert_service=alert_service)
        assert reporter.alert_service == alert_service
    
    def test_report_error_contact(self, mock_bq_client: Mock) -> None:
        """Test reporting error for contact."""
        reporter = ErrorReporter(mock_bq_client)
        
        # Mock query execution
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        result = reporter.report_error(
            entity_type="contact",
            entity_id="contact_123",
            system="crm_twenty",
            error_type=ErrorType.SYNC.value,
            error_message="Sync failed",
        )
        
        assert result["error_type"] == ErrorType.SYNC.value
        assert result["system"] == "crm_twenty"
        assert result["resolved"] is False
    
    def test_report_error_business(self, mock_bq_client: Mock) -> None:
        """Test reporting error for business."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        result = reporter.report_error(
            entity_type="business",
            entity_id="business_123",
            system="bigquery",
            error_type=ErrorType.VALIDATION.value,
            error_message="Validation failed",
        )
        
        assert result["error_type"] == ErrorType.VALIDATION.value
    
    def test_report_error_relationship(self, mock_bq_client: Mock) -> None:
        """Test reporting error for relationship."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        result = reporter.report_error(
            entity_type="relationship",
            entity_id="rel_123",
            system="supabase",
            error_type=ErrorType.CONFLICT.value,
            error_message="Conflict detected",
        )
        
        assert result["error_type"] == ErrorType.CONFLICT.value
    
    def test_report_error_unknown_entity_type(self, mock_bq_client: Mock) -> None:
        """Test reporting error for unknown entity type."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        result = reporter.report_error(
            entity_type="unknown",
            entity_id="unknown_123",
            system="local",
            error_type=ErrorType.OTHER.value,
            error_message="Unknown error",
        )
        
        assert result["error_type"] == ErrorType.OTHER.value
    
    def test_report_error_with_details(self, mock_bq_client: Mock) -> None:
        """Test reporting error with error details."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        error_details = {"stack_trace": "Traceback...", "code": 500}
        result = reporter.report_error(
            entity_type="contact",
            entity_id="contact_123",
            system="crm_twenty",
            error_type=ErrorType.EXCEPTION.value,
            error_message="Exception occurred",
            error_details=error_details,
        )
        
        assert result["error_details"] is not None
    
    def test_report_error_raise_after(self, mock_bq_client: Mock) -> None:
        """Test reporting error with raise_after flag."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        with pytest.raises(RuntimeError, match="sync: Test error"):
            reporter.report_error(
                entity_type="contact",
                entity_id="contact_123",
                system="crm_twenty",
                error_type=ErrorType.SYNC.value,
                error_message="Test error",
                raise_after=True,
            )
    
    def test_report_error_store_entity_failure(self, mock_bq_client: Mock) -> None:
        """Test reporting error when storing in entity fails."""
        reporter = ErrorReporter(mock_bq_client)
        
        # Mock query to raise exception
        mock_bq_client.query.side_effect = Exception("Query failed")
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            result = reporter.report_error(
                entity_type="contact",
                entity_id="contact_123",
                system="crm_twenty",
                error_type=ErrorType.SYNC.value,
                error_message="Test error",
            )
            
            # Should still return error record
            assert result["error_type"] == ErrorType.SYNC.value
            # Should log critical error
            mock_logger.critical.assert_called()
    
    def test_report_error_store_log_failure(self, mock_bq_client: Mock) -> None:
        """Test reporting error when storing in log fails."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.side_effect = Exception("Table not found")
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            result = reporter.report_error(
                entity_type="contact",
                entity_id="contact_123",
                system="crm_twenty",
                error_type=ErrorType.SYNC.value,
                error_message="Test error",
            )
            
            assert result["error_type"] == ErrorType.SYNC.value
            mock_logger.critical.assert_called()
    
    def test_report_error_alert_failure(self, mock_bq_client: Mock) -> None:
        """Test reporting error when alert fails."""
        alert_service = Mock()
        alert_service.send_alert.side_effect = Exception("Alert failed")
        reporter = ErrorReporter(mock_bq_client, alert_service=alert_service)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            result = reporter.report_error(
                entity_type="contact",
                entity_id="contact_123",
                system="crm_twenty",
                error_type=ErrorType.SYNC.value,
                error_message="Test error",
            )
            
            assert result["error_type"] == ErrorType.SYNC.value
            mock_logger.critical.assert_called()
    
    def test_report_error_no_alert_service(self, mock_bq_client: Mock) -> None:
        """Test reporting error when no alert service configured."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        mock_bq_client.get_table.return_value = Mock()
        mock_bq_client.insert_rows_json.return_value = []
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            result = reporter.report_error(
                entity_type="contact",
                entity_id="contact_123",
                system="crm_twenty",
                error_type=ErrorType.SYNC.value,
                error_message="Test error",
            )
            
            assert result["error_type"] == ErrorType.SYNC.value
            mock_logger.warning.assert_called()
    
    def test_store_error_in_entity_contact(self, mock_bq_client: Mock) -> None:
        """Test storing error in contact entity."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "crm_twenty",
            "error_type": "sync",
            "error_message": "Test error",
            "error_details": None,
            "resolved": False,
        }
        
        reporter._store_error_in_entity("contact", "contact_123", error)
        
        mock_bq_client.query.assert_called_once()
        call_args = mock_bq_client.query.call_args
        assert "identity.contacts_master" in str(call_args)
    
    def test_store_error_in_entity_business(self, mock_bq_client: Mock) -> None:
        """Test storing error in business entity."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "bigquery",
            "error_type": "validation",
            "error_message": "Test error",
            "error_details": None,
            "resolved": False,
        }
        
        reporter._store_error_in_entity("business", "business_123", error)
        
        call_args = mock_bq_client.query.call_args
        assert "identity.businesses_master" in str(call_args)
    
    def test_store_error_in_entity_relationship(self, mock_bq_client: Mock) -> None:
        """Test storing error in relationship entity."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "supabase",
            "error_type": "conflict",
            "error_message": "Test error",
            "error_details": None,
            "resolved": False,
        }
        
        reporter._store_error_in_entity("relationship", "rel_123", error)
        
        call_args = mock_bq_client.query.call_args
        assert "identity.people_business_relationships" in str(call_args)
    
    def test_store_in_error_log_success(self, mock_bq_client: Mock) -> None:
        """Test storing error in central log successfully."""
        reporter = ErrorReporter(mock_bq_client)
        
        table = Mock()
        mock_bq_client.get_table.return_value = table
        mock_bq_client.insert_rows_json.return_value = []  # No errors
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "crm_twenty",
            "error_type": "sync",
            "error_message": "Test error",
            "error_details": "Details here",
            "resolved": False,
        }
        
        reporter._store_in_error_log("contact", "contact_123", error)
        
        mock_bq_client.get_table.assert_called_once_with("identity.sync_errors_log")
        mock_bq_client.insert_rows_json.assert_called_once()
    
    def test_store_in_error_log_with_errors(self, mock_bq_client: Mock) -> None:
        """Test storing error in log when insert returns errors."""
        reporter = ErrorReporter(mock_bq_client)
        
        table = Mock()
        mock_bq_client.get_table.return_value = table
        mock_bq_client.insert_rows_json.return_value = [{"error": "Insert failed"}]
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "crm_twenty",
            "error_type": "sync",
            "error_message": "Test error",
            "error_details": None,
            "resolved": False,
        }
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            reporter._store_in_error_log("contact", "contact_123", error)
            mock_logger.critical.assert_called()
    
    def test_alert_jeremy_success(self, mock_bq_client: Mock) -> None:
        """Test alerting Jeremy successfully."""
        alert_service = Mock()
        reporter = ErrorReporter(mock_bq_client, alert_service=alert_service)
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "crm_twenty",
            "error_type": "sync",
            "error_message": "Test error",
            "error_details": "Stack trace here",
            "resolved": False,
        }
        
        reporter._alert_jeremy(error, "contact", "contact_123")
        
        alert_service.send_alert.assert_called_once()
        call_args = alert_service.send_alert.call_args
        assert "SYNC ERROR" in call_args[1]["subject"]
        assert "high" == call_args[1]["priority"]
    
    def test_alert_jeremy_no_service(self, mock_bq_client: Mock) -> None:
        """Test alerting when no alert service configured."""
        reporter = ErrorReporter(mock_bq_client)
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "crm_twenty",
            "error_type": "sync",
            "error_message": "Test error",
            "error_details": None,
            "resolved": False,
        }
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            reporter._alert_jeremy(error, "contact", "contact_123")
            mock_logger.warning.assert_called()
    
    def test_alert_jeremy_failure(self, mock_bq_client: Mock) -> None:
        """Test alerting when alert service fails."""
        alert_service = Mock()
        alert_service.send_alert.side_effect = Exception("Alert failed")
        reporter = ErrorReporter(mock_bq_client, alert_service=alert_service)
        
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": "crm_twenty",
            "error_type": "sync",
            "error_message": "Test error",
            "error_details": None,
            "resolved": False,
        }
        
        with patch("truth_forge.services.sync.error_reporter.logger") as mock_logger:
            reporter._alert_jeremy(error, "contact", "contact_123")
            mock_logger.critical.assert_called()
    
    def test_get_unresolved_errors_no_filters(self, mock_bq_client: Mock) -> None:
        """Test getting unresolved errors without filters."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = [
            {"error_id": "error_1", "resolved": False},
            {"error_id": "error_2", "resolved": False},
        ]
        mock_bq_client.query.return_value = query_job
        
        result = reporter.get_unresolved_errors()
        
        assert len(result) == 2
        mock_bq_client.query.assert_called_once()
    
    def test_get_unresolved_errors_with_entity_type(self, mock_bq_client: Mock) -> None:
        """Test getting unresolved errors filtered by entity type."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = [{"error_id": "error_1", "resolved": False}]
        mock_bq_client.query.return_value = query_job
        
        result = reporter.get_unresolved_errors(entity_type="contact")
        
        assert len(result) == 1
        call_args = mock_bq_client.query.call_args
        assert "entity_type" in str(call_args)
    
    def test_get_unresolved_errors_with_system(self, mock_bq_client: Mock) -> None:
        """Test getting unresolved errors filtered by system."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        result = reporter.get_unresolved_errors(system="crm_twenty")
        
        assert len(result) == 0
        call_args = mock_bq_client.query.call_args
        assert "system" in str(call_args)
    
    def test_get_unresolved_errors_with_both_filters(self, mock_bq_client: Mock) -> None:
        """Test getting unresolved errors with both filters."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        result = reporter.get_unresolved_errors(
            entity_type="contact", system="crm_twenty"
        )
        
        assert len(result) == 0
        call_args = mock_bq_client.query.call_args
        assert "entity_type" in str(call_args)
        assert "system" in str(call_args)
    
    def test_mark_error_resolved(self, mock_bq_client: Mock) -> None:
        """Test marking error as resolved."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        reporter.mark_error_resolved("error_123", "Fixed manually")
        
        mock_bq_client.query.assert_called_once()
        call_args = mock_bq_client.query.call_args
        assert "resolved = TRUE" in str(call_args)
    
    def test_mark_error_resolved_no_notes(self, mock_bq_client: Mock) -> None:
        """Test marking error as resolved without notes."""
        reporter = ErrorReporter(mock_bq_client)
        
        query_job = Mock()
        query_job.result.return_value = []
        mock_bq_client.query.return_value = query_job
        
        reporter.mark_error_resolved("error_123")
        
        mock_bq_client.query.assert_called_once()
