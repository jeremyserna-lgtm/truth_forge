"""Tests for kill switch module."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from truth_forge.governance.kill_switch import (
    KillSwitchError,
    KillSwitchState,
    assert_not_armed,
    current_state,
)


class TestKillSwitchState:
    """Test KillSwitchState dataclass."""

    def test_kill_switch_state(self) -> None:
        """Test KillSwitchState structure."""
        state = KillSwitchState(armed=True, source="env")
        assert state.armed is True
        assert state.source == "env"


class TestCurrentState:
    """Test current_state function."""

    @patch("truth_forge.governance.kill_switch.kill_switch_status")
    @patch("truth_forge.governance.kill_switch.feature_flags")
    def test_env_armed(self, mock_flags: Mock, mock_status: Mock) -> None:
        """Test state from environment variable."""
        mock_flags.kill_switch_armed = False
        mock_status.return_value = False

        with patch.dict("os.environ", {"GENESIS_KILL_SWITCH": "on"}):
            state = current_state()
            assert state.armed is True
            assert state.source == "env"

    @patch("truth_forge.governance.kill_switch.kill_switch_status")
    @patch("truth_forge.governance.kill_switch.feature_flags")
    def test_env_disarmed(self, mock_flags: Mock, mock_status: Mock) -> None:
        """Test state from environment variable (disarmed)."""
        mock_flags.kill_switch_armed = True
        mock_status.return_value = True

        with patch.dict("os.environ", {"GENESIS_KILL_SWITCH": "off"}):
            state = current_state()
            assert state.armed is False
            assert state.source == "env"

    @patch("truth_forge.governance.kill_switch.kill_switch_status")
    @patch("truth_forge.governance.kill_switch.feature_flags")
    def test_control_plane_armed(self, mock_flags: Mock, mock_status: Mock) -> None:
        """Test state from control plane."""
        mock_flags.kill_switch_armed = False
        mock_status.return_value = True

        with patch.dict("os.environ", {}, clear=True):
            state = current_state()
            assert state.armed is True
            assert state.source == "control_plane"

    @patch("truth_forge.governance.kill_switch.kill_switch_status")
    @patch("truth_forge.governance.kill_switch.feature_flags")
    def test_feature_flag_fallback(self, mock_flags: Mock, mock_status: Mock) -> None:
        """Test state falls back to feature flag."""
        mock_flags.kill_switch_armed = True
        mock_status.return_value = False

        with patch.dict("os.environ", {}, clear=True):
            state = current_state()
            assert state.armed is True
            assert state.source == "feature_flag"

    def test_env_variants(self) -> None:
        """Test various environment variable values."""
        for value in ["1", "true", "on", "armed", "yes"]:
            with patch.dict("os.environ", {"GENESIS_KILL_SWITCH": value}):
                state = current_state()
                assert state.armed is True


class TestAssertNotArmed:
    """Test assert_not_armed function."""

    @patch("truth_forge.governance.kill_switch.current_state")
    def test_not_armed_passes(self, mock_state: Mock) -> None:
        """Test assert_not_armed passes when not armed."""
        mock_state.return_value = KillSwitchState(armed=False, source="feature_flag")
        # Should not raise
        assert_not_armed()

    @patch("truth_forge.governance.kill_switch.current_state")
    def test_armed_raises_error(self, mock_state: Mock) -> None:
        """Test assert_not_armed raises when armed."""
        mock_state.return_value = KillSwitchState(armed=True, source="env")
        with pytest.raises(KillSwitchError, match="Kill switch engaged"):
            assert_not_armed()
