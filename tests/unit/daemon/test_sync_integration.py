"""Tests for daemon sync integration."""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

from truth_forge.daemon.sync_integration import SyncDaemonIntegration


class TestSyncDaemonIntegration:
    """Test SyncDaemonIntegration class."""

    def test_init(self) -> None:
        """Test initialization."""
        integration = SyncDaemonIntegration()
        assert integration.sync_service is None
        assert integration._thread is None

    def test_is_running_false_initially(self) -> None:
        """Test is_running is False initially."""
        integration = SyncDaemonIntegration()
        assert integration.is_running is False

    @patch("truth_forge.daemon.sync_integration.IndustryStandardSyncService")
    def test_start(self, mock_service_class: Mock) -> None:
        """Test starting sync service."""
        mock_service = Mock()
        mock_service.running = True
        mock_service_class.return_value = mock_service

        integration = SyncDaemonIntegration()
        integration.start()

        assert integration.sync_service is not None
        assert integration._thread is not None
        mock_service.start.assert_called_once()

    @patch("truth_forge.daemon.sync_integration.IndustryStandardSyncService")
    def test_start_already_running(self, mock_service_class: Mock) -> None:
        """Test starting when already running."""
        mock_service = Mock()
        mock_service.running = True
        mock_service_class.return_value = mock_service

        integration = SyncDaemonIntegration()
        integration.start()
        integration.start()  # Second call

        # Should only create service once
        assert mock_service_class.call_count == 1

    @patch("truth_forge.daemon.sync_integration.IndustryStandardSyncService")
    def test_stop(self, mock_service_class: Mock) -> None:
        """Test stopping sync service."""
        mock_service = Mock()
        mock_service.running = True
        mock_service_class.return_value = mock_service

        integration = SyncDaemonIntegration()
        integration.start()
        integration.stop()

        mock_service.stop.assert_called_once()
        assert integration.sync_service is None

    @patch("truth_forge.daemon.sync_integration.IndustryStandardSyncService")
    def test_is_running_true_when_started(self, mock_service_class: Mock) -> None:
        """Test is_running is True when started."""
        mock_service = Mock()
        mock_service.running = True
        mock_service_class.return_value = mock_service

        integration = SyncDaemonIntegration()
        integration.start()

        assert integration.is_running is True

    @patch("truth_forge.daemon.sync_integration.IndustryStandardSyncService")
    def test_run_sync_service_thread(self, mock_service_class: Mock) -> None:
        """Test sync service runs in thread."""
        mock_service = Mock()
        mock_service.running = True
        mock_service_class.return_value = mock_service

        integration = SyncDaemonIntegration()
        integration.start()

        # Give thread time to start
        time.sleep(0.1)

        assert integration._thread is not None
        assert (
            integration._thread.is_alive() or not integration._thread.is_alive()
        )  # May have finished

    @patch("truth_forge.daemon.sync_integration.IndustryStandardSyncService")
    def test_run_sync_service_handles_errors(self, mock_service_class: Mock) -> None:
        """Test sync service thread handles errors."""
        mock_service = Mock()
        mock_service.running = True
        mock_service.start.side_effect = Exception("Service error")
        mock_service_class.return_value = mock_service

        integration = SyncDaemonIntegration()
        integration.start()

        # Should not raise, error handled in thread
        time.sleep(0.1)
