"""Tests for daemon service module.

Tests the TruthForgeDaemon, DaemonConfig, and DaemonStatus classes.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.daemon.service import (
    DaemonConfig,
    DaemonStatus,
    TruthForgeDaemon,
    run_daemon,
)


class TestDaemonConfig:
    """Tests for DaemonConfig dataclass."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = DaemonConfig()

        assert config.host == "127.0.0.1"
        assert config.port == 8765
        assert config.heartbeat_interval == 30
        assert config.enable_governance is True

    def test_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = DaemonConfig(
            host="0.0.0.0",
            port=9000,
            heartbeat_interval=60,
            enable_governance=False,
        )

        assert config.host == "0.0.0.0"
        assert config.port == 9000
        assert config.heartbeat_interval == 60
        assert config.enable_governance is False


class TestDaemonStatus:
    """Tests for DaemonStatus dataclass."""

    def test_default_values(self) -> None:
        """Test default status values."""
        status = DaemonStatus()

        assert status.heartbeat_count == 0
        assert status.last_heartbeat is None
        assert status.is_healthy is True
        assert status.started_at is not None

    def test_to_dict(self) -> None:
        """Test to_dict produces correct structure."""
        now = datetime.now(UTC)
        status = DaemonStatus(
            started_at=now,
            heartbeat_count=5,
            last_heartbeat=now,
            is_healthy=True,
        )

        result = status.to_dict()

        assert "started_at" in result
        assert "heartbeat_count" in result
        assert result["heartbeat_count"] == 5
        assert "last_heartbeat" in result
        assert "is_healthy" in result
        assert result["is_healthy"] is True
        assert "uptime_seconds" in result

    def test_to_dict_no_heartbeat(self) -> None:
        """Test to_dict with no heartbeat yet."""
        status = DaemonStatus()

        result = status.to_dict()

        assert result["last_heartbeat"] is None
        assert result["heartbeat_count"] == 0


class TestTruthForgeDaemon:
    """Tests for TruthForgeDaemon class."""

    def test_init_default_config(self) -> None:
        """Test initialization with default config."""
        daemon = TruthForgeDaemon()

        assert daemon.config.host == "127.0.0.1"
        assert daemon.config.port == 8765
        assert daemon.status.is_healthy is True
        assert daemon._server is None

    def test_init_custom_config(self) -> None:
        """Test initialization with custom config."""
        config = DaemonConfig(host="0.0.0.0", port=9000)
        daemon = TruthForgeDaemon(config)

        assert daemon.config.host == "0.0.0.0"
        assert daemon.config.port == 9000

    def test_version_constant(self) -> None:
        """Test VERSION class constant."""
        assert TruthForgeDaemon.VERSION == "2.0.0"

    def test_is_running_initially_false(self) -> None:
        """Test is_running is False before start."""
        daemon = TruthForgeDaemon()

        assert daemon.is_running is False

    def test_send_heartbeat(self) -> None:
        """Test _send_heartbeat updates status."""
        daemon = TruthForgeDaemon()

        assert daemon.status.heartbeat_count == 0
        assert daemon.status.last_heartbeat is None

        daemon._send_heartbeat()

        assert daemon.status.heartbeat_count == 1
        assert daemon.status.last_heartbeat is not None

    def test_send_heartbeat_increments(self) -> None:
        """Test _send_heartbeat increments count."""
        daemon = TruthForgeDaemon()

        daemon._send_heartbeat()
        daemon._send_heartbeat()
        daemon._send_heartbeat()

        assert daemon.status.heartbeat_count == 3

    def test_stop_sets_unhealthy(self) -> None:
        """Test stop sets is_healthy to False."""
        daemon = TruthForgeDaemon()
        assert daemon.status.is_healthy is True

        daemon.stop()

        assert daemon.status.is_healthy is False

    def test_stop_sets_stop_event(self) -> None:
        """Test stop sets the stop event."""
        daemon = TruthForgeDaemon()
        assert not daemon._stop_event.is_set()

        daemon.stop()

        assert daemon._stop_event.is_set()

    @patch.object(TruthForgeDaemon, "start")
    def test_start_async_returns_thread(self, mock_start: MagicMock) -> None:
        """Test start_async returns a thread and calls start."""
        daemon = TruthForgeDaemon()

        thread = daemon.start_async()
        thread.join(timeout=1)

        mock_start.assert_called_once()

    def test_start_heartbeat(self) -> None:
        """Test _start_heartbeat creates and starts a thread."""
        daemon = TruthForgeDaemon()

        daemon._start_heartbeat()

        try:
            assert daemon._heartbeat_thread is not None
            assert daemon._heartbeat_thread.is_alive()
        finally:
            daemon._stop_event.set()
            daemon._heartbeat_thread.join(timeout=2)

    @patch("truth_forge.daemon.service.HTTPServer")
    def test_start_creates_server(self, mock_server_class: MagicMock) -> None:
        """Test start creates HTTP server."""
        mock_server = MagicMock()
        mock_server.serve_forever.side_effect = KeyboardInterrupt
        mock_server_class.return_value = mock_server

        daemon = TruthForgeDaemon()

        daemon.start()

        mock_server_class.assert_called_once()
        # Server should be None after stop
        assert daemon._server is None


class TestRunDaemon:
    """Tests for run_daemon function."""

    @patch.object(TruthForgeDaemon, "start")
    def test_run_daemon_creates_and_starts(self, mock_start: MagicMock) -> None:
        """Test run_daemon creates daemon and starts it."""
        run_daemon(host="0.0.0.0", port=9001)

        mock_start.assert_called_once()

    @patch.object(TruthForgeDaemon, "start")
    def test_run_daemon_default_args(self, mock_start: MagicMock) -> None:
        """Test run_daemon with default arguments."""
        run_daemon()

        mock_start.assert_called_once()
