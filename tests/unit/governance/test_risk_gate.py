"""Tests for risk gate module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.governance.risk_gate import should_ask_permission


class TestShouldAskPermission:
    """Test should_ask_permission function."""

    @patch("truth_forge.governance.risk_gate.feature_flags")
    def test_discovery_mode_never_asks(self, mock_flags: Mock) -> None:
        """Test discovery mode never asks for permission."""
        mock_flags.risk_thresholds.servant_prompt = 3
        mock_flags.risk_thresholds.sovereign_prompt = 4

        # Discovery mode should never ask
        assert should_ask_permission("discovery", 5) is False
        assert should_ask_permission("discovery", 1) is False

    @patch("truth_forge.governance.risk_gate.feature_flags")
    def test_servant_mode_threshold(self, mock_flags: Mock) -> None:
        """Test servant mode uses servant threshold."""
        mock_flags.risk_thresholds.servant_prompt = 3
        mock_flags.risk_thresholds.sovereign_prompt = 4

        # Risk level > servant threshold
        assert should_ask_permission("servant", 4) is True
        # Risk level == servant threshold
        assert should_ask_permission("servant", 3) is False
        # Risk level < servant threshold
        assert should_ask_permission("servant", 2) is False

    @patch("truth_forge.governance.risk_gate.feature_flags")
    def test_sovereign_mode_threshold(self, mock_flags: Mock) -> None:
        """Test sovereign mode uses sovereign threshold."""
        mock_flags.risk_thresholds.servant_prompt = 3
        mock_flags.risk_thresholds.sovereign_prompt = 4

        # Risk level >= sovereign threshold
        assert should_ask_permission("sovereign", 4) is True
        assert should_ask_permission("sovereign", 5) is True
        # Risk level < sovereign threshold
        assert should_ask_permission("sovereign", 3) is False

    @patch("truth_forge.governance.risk_gate.feature_flags")
    def test_case_insensitive(self, mock_flags: Mock) -> None:
        """Test mode is case-insensitive."""
        mock_flags.risk_thresholds.servant_prompt = 3
        mock_flags.risk_thresholds.sovereign_prompt = 4

        assert should_ask_permission("SERVANT", 4) is True
        assert should_ask_permission("Sovereign", 5) is True
        assert should_ask_permission("DISCOVERY", 5) is False

    @patch("truth_forge.governance.risk_gate.feature_flags")
    def test_default_servant_mode(self, mock_flags: Mock) -> None:
        """Test default mode is servant."""
        mock_flags.risk_thresholds.servant_prompt = 3
        mock_flags.risk_thresholds.sovereign_prompt = 4

        # Unknown mode defaults to servant
        assert should_ask_permission("unknown", 4) is True
        assert should_ask_permission("unknown", 3) is False
