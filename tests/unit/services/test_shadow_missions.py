"""Tests for shadow missions module."""

from __future__ import annotations

from datetime import date
from unittest.mock import Mock, patch

from truth_forge.services.shadow_missions import ShadowState, run_shadow_suite


class TestShadowState:
    """Test ShadowState class."""

    def test_should_run_today_first_time(self) -> None:
        """Test should_run_today returns True first time."""
        state = ShadowState()
        assert state.should_run_today() is True

    def test_should_run_today_same_day(self) -> None:
        """Test should_run_today returns False same day."""
        state = ShadowState()
        state.should_run_today()  # First call
        assert state.should_run_today() is False  # Second call same day

    def test_should_run_today_updates_last_run(self) -> None:
        """Test should_run_today updates last_run."""
        state = ShadowState()
        state.should_run_today()
        assert state.last_run == date.today()

    @patch("truth_forge.services.shadow_missions.date")
    def test_should_run_today_different_day(self, mock_date: Mock) -> None:
        """Test should_run_today returns True on different day."""
        state = ShadowState()
        state.should_run_today()  # First call

        # Simulate next day
        mock_date.today.return_value = date(2026, 1, 29)
        state.last_run = date(2026, 1, 28)

        assert state.should_run_today() is True


class TestRunShadowSuite:
    """Test run_shadow_suite function."""

    def test_run_shadow_suite_structure(self) -> None:
        """Test shadow suite returns correct structure."""
        mock_orch = Mock()
        mock_orch.process.return_value = Mock(success=True, content="shadow-ok", error=None)
        mock_orch.health_check.return_value = {"status": "healthy"}

        mock_exec = Mock()
        mock_exec.execute.return_value = Mock(exit_code=0, stdout="shadow-exec", stderr="")

        results = run_shadow_suite(mock_orch, mock_exec)

        assert "ts" in results
        assert "steps" in results
        assert "all_passed" in results
        assert len(results["steps"]) == 3

    def test_run_shadow_suite_routing_test(self) -> None:
        """Test routing smoke test."""
        mock_orch = Mock()
        mock_orch.process.return_value = Mock(success=True, content="shadow-ok", error=None)

        mock_exec = Mock()
        mock_exec.execute.return_value = Mock(exit_code=0, stdout="shadow-exec", stderr="")

        results = run_shadow_suite(mock_orch, mock_exec)

        routing_step = next(s for s in results["steps"] if s["name"] == "routing_complete")
        assert routing_step["success"] is True

    def test_run_shadow_suite_code_exec_test(self) -> None:
        """Test code execution smoke test."""
        mock_orch = Mock()
        mock_orch.process.return_value = Mock(success=True, content="shadow-ok", error=None)
        mock_orch.health_check.return_value = {"status": "healthy"}

        mock_exec = Mock()
        mock_exec.execute.return_value = Mock(exit_code=0, stdout="shadow-exec", stderr="")

        results = run_shadow_suite(mock_orch, mock_exec)

        exec_step = next(s for s in results["steps"] if s["name"] == "code_exec")
        assert exec_step["success"] is True

    def test_run_shadow_suite_health_check(self) -> None:
        """Test health check step."""
        mock_orch = Mock()
        mock_orch.process.return_value = Mock(success=True, content="shadow-ok", error=None)
        mock_orch.health_check.return_value = {"status": "healthy"}

        mock_exec = Mock()
        mock_exec.execute.return_value = Mock(exit_code=0, stdout="shadow-exec", stderr="")

        results = run_shadow_suite(mock_orch, mock_exec)

        health_step = next(s for s in results["steps"] if s["name"] == "health_check")
        assert health_step["success"] is True

    def test_run_shadow_suite_handles_errors(self) -> None:
        """Test shadow suite handles errors gracefully."""
        mock_orch = Mock()
        mock_orch.process.side_effect = Exception("Routing failed")

        mock_exec = Mock()
        mock_exec.execute.return_value = Mock(exit_code=0, stdout="shadow-exec", stderr="")

        results = run_shadow_suite(mock_orch, mock_exec)

        # Should still return results with failure
        assert "steps" in results
        routing_step = next(s for s in results["steps"] if s["name"] == "routing_complete")
        assert routing_step["success"] is False

    def test_run_shadow_suite_handles_exec_error(self) -> None:
        """Test shadow suite handles code execution errors."""
        mock_orch = Mock()
        mock_orch.process.return_value = Mock(success=True, content="shadow-ok", error=None)

        mock_exec = Mock()
        mock_exec.execute.side_effect = Exception("Execution failed")

        results = run_shadow_suite(mock_orch, mock_exec)

        exec_step = next(s for s in results["steps"] if s["name"] == "code_exec")
        assert exec_step["success"] is False
        assert "Execution failed" in exec_step["detail"]

    def test_run_shadow_suite_handles_health_check_error(self) -> None:
        """Test shadow suite handles health check errors."""
        mock_orch = Mock()
        mock_orch.process.return_value = Mock(success=True, content="shadow-ok", error=None)
        mock_orch.health_check.side_effect = Exception("Health check failed")

        mock_exec = Mock()
        mock_exec.execute.return_value = Mock(exit_code=0, stdout="shadow-exec", stderr="")

        results = run_shadow_suite(mock_orch, mock_exec)

        health_step = next(s for s in results["steps"] if s["name"] == "health_check")
        assert health_step["success"] is False
        assert "Health check failed" in health_step["detail"]
