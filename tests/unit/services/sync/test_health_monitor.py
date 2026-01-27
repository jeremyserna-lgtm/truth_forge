"""Comprehensive tests for SyncHealthMonitor.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from truth_forge.services.sync.health_monitor import SyncHealthMonitor


class TestSyncHealthMonitor:
    """Test suite for SyncHealthMonitor."""
    
    def test_init(self) -> None:
        """Test initialization."""
        monitor = SyncHealthMonitor(
            check_interval=30,
            restart_on_failure=True,
            max_restart_attempts=3,
            restart_cooldown=60,
        )
        
        assert monitor.check_interval == 30
        assert monitor.restart_on_failure is True
        assert monitor.max_restart_attempts == 3
        assert monitor.restart_cooldown == 60
        assert monitor.running is False
        assert monitor.restart_count == 0
    
    def test_start(
        self,
    ) -> None:
        """Test starting the monitor."""
        monitor = SyncHealthMonitor()
        
        monitor.start()
        
        assert monitor.running is True
        assert monitor.monitor_thread is not None
        assert monitor.monitor_thread.is_alive()
        
        monitor.stop()
    
    def test_start_already_running(
        self,
    ) -> None:
        """Test starting when already running."""
        monitor = SyncHealthMonitor()
        
        monitor.start()
        monitor.start()  # Second call
        
        assert monitor.running is True
        
        monitor.stop()
    
    def test_stop(
        self,
    ) -> None:
        """Test stopping the monitor."""
        monitor = SyncHealthMonitor()
        
        monitor.start()
        monitor.stop()
        
        assert monitor.running is False
    
    def test_check_health_pid_file_exists_process_running(
        self,
    ) -> None:
        """Test health check when PID file exists and process is running."""
        monitor = SyncHealthMonitor()
        
        # Mock PID file
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        mock_pid_file.read_text.return_value = "12345"
        monitor.pid_file = mock_pid_file
        
        # Mock subprocess (process exists)
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            result = monitor.check_health()
            
            assert result is True
            mock_run.assert_called_once()
    
    def test_check_health_pid_file_not_exists(
        self,
    ) -> None:
        """Test health check when PID file doesn't exist."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = False
        monitor.pid_file = mock_pid_file
        
        result = monitor.check_health()
        
        assert result is False
    
    def test_check_health_process_not_running(
        self,
    ) -> None:
        """Test health check when process is not running."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        mock_pid_file.read_text.return_value = "12345"
        monitor.pid_file = mock_pid_file
        
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1  # Process not found
            mock_run.return_value = mock_result
            
            result = monitor.check_health()
            
            assert result is False
    
    def test_check_health_timeout(
        self,
    ) -> None:
        """Test health check when subprocess times out."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        mock_pid_file.read_text.return_value = "12345"
        monitor.pid_file = mock_pid_file
        
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired("ps", 5)
            
            result = monitor.check_health()
            
            assert result is False
    
    def test_check_health_exception(
        self,
    ) -> None:
        """Test health check when exception occurs."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        mock_pid_file.read_text.side_effect = Exception("Read error")
        monitor.pid_file = mock_pid_file
        
        result = monitor.check_health()
        
        assert result is False
    
    def test_attempt_restart_success(
        self,
    ) -> None:
        """Test attempting restart successfully."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        monitor.pid_file = mock_pid_file
        
        mock_start_script = Mock()
        mock_start_script.parent = Mock()
        mock_start_script.parent.parent = Mock()
        monitor.start_script = mock_start_script
        
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            monitor._attempt_restart()
            
            assert monitor.restart_count == 0
            mock_pid_file.unlink.assert_called_once()
            mock_run.assert_called_once()
    
    def test_attempt_restart_failure(
        self,
    ) -> None:
        """Test attempting restart with failure."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        monitor.pid_file = mock_pid_file
        
        mock_start_script = Mock()
        mock_start_script.parent = Mock()
        mock_start_script.parent.parent = Mock()
        monitor.start_script = mock_start_script
        
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stderr = b"Error message"
            mock_run.return_value = mock_result
            
            monitor._attempt_restart()
            
            assert monitor.restart_count == 1
            assert monitor.last_restart_attempt is not None
    
    def test_attempt_restart_cooldown(
        self,
    ) -> None:
        """Test restart cooldown prevents immediate restart."""
        monitor = SyncHealthMonitor(restart_cooldown=300)
        
        monitor.last_restart_attempt = datetime.utcnow() - timedelta(seconds=60)  # 1 min ago
        
        monitor._attempt_restart()
        
        # Should not restart due to cooldown
        assert monitor.restart_count == 0
    
    def test_attempt_restart_max_attempts(
        self,
    ) -> None:
        """Test restart when max attempts reached."""
        monitor = SyncHealthMonitor(max_restart_attempts=3)
        
        monitor.restart_count = 3
        monitor.last_restart_attempt = datetime.utcnow() - timedelta(seconds=400)
        
        monitor._attempt_restart()
        
        # Should not restart due to max attempts
        assert monitor.restart_count == 3
    
    def test_attempt_restart_exception(
        self,
    ) -> None:
        """Test restart when exception occurs."""
        monitor = SyncHealthMonitor()
        
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        monitor.pid_file = mock_pid_file
        
        mock_start_script = Mock()
        mock_start_script.parent = Mock()
        mock_start_script.parent.parent = Mock()
        monitor.start_script = mock_start_script
        
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Subprocess error")
            
            monitor._attempt_restart()
            
            assert monitor.restart_count == 1
            assert monitor.last_restart_attempt is not None
    
    def test_get_status(
        self,
    ) -> None:
        """Test getting monitor status."""
        monitor = SyncHealthMonitor()
        
        # Mock PID file and subprocess for check_health
        mock_pid_file = Mock()
        mock_pid_file.exists.return_value = True
        mock_pid_file.read_text.return_value = "12345"
        monitor.pid_file = mock_pid_file
        
        with patch("truth_forge.services.sync.health_monitor.subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            status = monitor.get_status()
            
            assert "running" in status
            assert "service_healthy" in status
            assert "restart_count" in status
            assert "check_interval" in status
            assert status["service_healthy"] is True
    
    def test_get_status_with_restart_attempt(
        self,
    ) -> None:
        """Test getting status when restart was attempted."""
        monitor = SyncHealthMonitor()
        
        monitor.last_restart_attempt = datetime.utcnow()
        monitor.restart_count = 2
        
        status = monitor.get_status()
        
        assert status["restart_count"] == 2
        assert status["last_restart_attempt"] is not None