"""Tests for explorer service module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.services.explorer.service import (
    MAX_CALLS_PER_SESSION,
    MAX_COST_PER_SESSION,
    ExplorerService,
)


class TestConstants:
    """Test module constants."""

    def test_max_cost_per_session(self) -> None:
        """Test MAX_COST_PER_SESSION constant."""
        assert MAX_COST_PER_SESSION == 0.50

    def test_max_calls_per_session(self) -> None:
        """Test MAX_CALLS_PER_SESSION constant."""
        assert MAX_CALLS_PER_SESSION == 100


class TestExplorerService:
    """Test ExplorerService class."""

    @patch("truth_forge.services.explorer.service.BaseService.__init__")
    def test_init(self, mock_base_init: Mock) -> None:
        """Test ExplorerService initialization."""
        mock_base_init.return_value = None

        service = ExplorerService()
        assert service.service_name == "explorer"
        assert service._session_cost == 0.0
        assert service._session_calls == 0

    @patch("truth_forge.services.explorer.service.BaseService.__init__")
    @patch("truth_forge.services.explorer.service.ToolBridge")
    @patch("truth_forge.services.explorer.service.get_explorer_context")
    def test_on_startup(
        self, mock_context: Mock, mock_tool_bridge: Mock, mock_base_init: Mock
    ) -> None:
        """Test service startup."""
        mock_base_init.return_value = None
        mock_context.return_value = 500_000

        mock_bridge_instance = Mock()
        mock_bridge_instance.get_tool_names.return_value = [
            "tool1",
            "tool2",
        ]  # Return list for len()
        mock_tool_bridge.return_value = mock_bridge_instance

        service = ExplorerService()
        service._logger = Mock()
        service.on_startup()

        assert service._tool_bridge is not None
        assert service._context_manager is not None

    @patch("truth_forge.services.explorer.service.BaseService.__init__")
    def test_get_session_stats(self, mock_base_init: Mock) -> None:
        """Test getting session statistics."""
        mock_base_init.return_value = None

        service = ExplorerService()
        service._session_cost = 0.25
        service._session_calls = 50

        stats = service.get_session_stats()
        assert stats["cost"] == 0.25
        assert stats["calls"] == 50

    @patch("truth_forge.services.explorer.service.BaseService.__init__")
    def test_process(self, mock_base_init: Mock) -> None:
        """Test process method."""
        mock_base_init.return_value = None

        service = ExplorerService()
        service._logger = Mock()

        # Mock explore method
        mock_report = Mock()
        mock_report.model_dump.return_value = {"session_id": "test"}
        service.explore = Mock(return_value=mock_report)

        config_dict = {"iterations": 5, "depth": "medium"}
        result = service.process(config_dict)

        assert result["session_id"] == "test"
        service.explore.assert_called_once()
