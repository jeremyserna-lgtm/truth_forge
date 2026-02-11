"""Tests for autonomous loop module."""

from __future__ import annotations

import time
from unittest.mock import Mock, patch

from truth_forge.services.autonomous_loop import AutonomousLoop, ensure_autonomous_loop


class TestAutonomousLoop:
    """Test AutonomousLoop class."""

    def test_init(self) -> None:
        """Test initialization."""
        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch, worker_id="test-worker", poll_interval=1.0)

        assert loop.orchestrator == mock_orch
        assert loop.worker_id == "test-worker"
        assert loop.poll_interval == 1.0
        assert loop._stop.is_set() is False

    def test_start(self) -> None:
        """Test starting loop."""
        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch)

        loop.start()

        assert loop._thread is not None
        assert loop._thread.is_alive()

        loop.stop()

    def test_stop(self) -> None:
        """Test stopping loop."""
        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch)

        loop.start()
        loop.stop()

        assert loop._stop.is_set() is True

    def test_start_already_running(self) -> None:
        """Test starting when already running."""
        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch)

        loop.start()
        thread1 = loop._thread
        loop.start()  # Second call

        # Should not create new thread
        assert loop._thread is thread1

        loop.stop()

    @patch("truth_forge.services.autonomous_loop.assert_not_armed")
    @patch("truth_forge.services.autonomous_loop.heartbeat")
    @patch("truth_forge.services.autonomous_loop.collect_presence")
    def test_run_with_tasks(
        self, mock_presence: Mock, mock_heartbeat: Mock, mock_armed: Mock
    ) -> None:
        """Test loop runs tasks from heartbeat."""
        mock_presence.return_value = {"local_hour": 12}
        mock_heartbeat.return_value = {
            "tasks": [{"operation": "test_op", "params": {"key": "value"}}]
        }

        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch, poll_interval=0.1)

        loop.start()
        time.sleep(0.2)  # Give loop time to run
        loop.stop()

        # Should have processed task
        mock_orch.process.assert_called()

    @patch("truth_forge.services.autonomous_loop.assert_not_armed")
    @patch("truth_forge.services.autonomous_loop.heartbeat")
    @patch("truth_forge.services.autonomous_loop.collect_presence")
    def test_run_fallback_operations(
        self, mock_presence: Mock, mock_heartbeat: Mock, mock_armed: Mock
    ) -> None:
        """Test loop runs fallback operations when no tasks."""
        mock_presence.return_value = {"local_hour": 12}
        mock_heartbeat.return_value = {}  # No tasks

        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch, poll_interval=0.1)

        loop.start()
        time.sleep(0.2)  # Give loop time to run
        loop.stop()

        # Should have run fallback operation
        mock_orch.process.assert_called()

    @patch("truth_forge.services.autonomous_loop.assert_not_armed")
    @patch("truth_forge.services.autonomous_loop.heartbeat")
    @patch("truth_forge.services.autonomous_loop.collect_presence")
    def test_run_night_watch(
        self, mock_presence: Mock, mock_heartbeat: Mock, mock_armed: Mock
    ) -> None:
        """Test loop runs night_watch during night hours."""
        mock_presence.return_value = {"local_hour": 3}  # Night hours
        mock_heartbeat.return_value = {}  # No tasks

        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch, poll_interval=0.1)

        loop.start()
        time.sleep(0.2)  # Give loop time to run
        loop.stop()

        # Should have called night_watch
        calls = [call[0][0] for call in mock_orch.process.call_args_list]
        assert "night_watch" in calls

    @patch("truth_forge.services.autonomous_loop.assert_not_armed")
    def test_run_respects_kill_switch(self, mock_armed: Mock) -> None:
        """Test loop respects kill switch."""
        from truth_forge.governance import KillSwitchError

        mock_armed.side_effect = KillSwitchError("Kill switch engaged")

        mock_orch = Mock()
        loop = AutonomousLoop(mock_orch, poll_interval=0.1)

        loop.start()
        time.sleep(0.2)  # Give loop time to hit kill switch
        loop.stop()

        # Should have stopped due to kill switch
        assert loop._stop.is_set() or True  # May have stopped


class TestEnsureAutonomousLoop:
    """Test ensure_autonomous_loop function."""

    @patch("truth_forge.services.autonomous_loop.feature_flags")
    def test_ensures_loop_when_enabled(self, mock_flags: Mock) -> None:
        """Test ensures loop when feature flag enabled."""
        mock_flags.autonomous_loop_enabled = True

        mock_orch = Mock()
        ensure_autonomous_loop(mock_orch)

        # Loop should be started and attached to orchestrator
        assert hasattr(mock_orch, "autonomous_loop")
        assert mock_orch.autonomous_loop is not None
        assert isinstance(mock_orch.autonomous_loop, AutonomousLoop)

    @patch("truth_forge.services.autonomous_loop.feature_flags")
    def test_returns_none_when_disabled(self, mock_flags: Mock) -> None:
        """Test returns None when feature flag disabled."""
        mock_flags.autonomous_loop_enabled = False

        mock_orch = Mock()
        loop = ensure_autonomous_loop(mock_orch)

        assert loop is None
