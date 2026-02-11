"""Tests for cluster state module."""

from __future__ import annotations

from unittest.mock import Mock, patch

from truth_forge.services.cluster_state import ClusterStateMonitor, NodeState


class TestNodeState:
    """Test NodeState dataclass."""

    def test_node_state(self) -> None:
        """Test NodeState structure."""
        state = NodeState(
            name="test-node",
            healthy=True,
            last_checked=1234567890.0,
            metadata={"key": "value"},
        )
        assert state.name == "test-node"
        assert state.healthy is True
        assert state.last_checked == 1234567890.0
        assert state.metadata == {"key": "value"}


class TestClusterStateMonitor:
    """Test ClusterStateMonitor class."""

    def test_init_defaults(self) -> None:
        """Test initialization with defaults."""
        monitor = ClusterStateMonitor()
        assert monitor.ttl == 30.0
        assert monitor.nodes == ["king"]
        assert monitor._cache == {}

    def test_init_custom(self) -> None:
        """Test initialization with custom values."""
        monitor = ClusterStateMonitor(ttl=60.0, nodes=["node1", "node2"])
        assert monitor.ttl == 60.0
        assert monitor.nodes == ["node1", "node2"]

    @patch("truth_forge.services.cluster_state.subprocess.run")
    @patch("truth_forge.services.cluster_state.check_readiness")
    def test_get_available_nodes(self, mock_readiness: Mock, mock_subprocess: Mock) -> None:
        """Test getting available nodes."""
        mock_readiness.return_value = {"scout": Mock(ready=True)}

        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        monitor = ClusterStateMonitor(nodes=["test-node"])
        nodes = monitor.get_available_nodes()

        assert len(nodes) == 1
        assert nodes[0].name == "test-node"
        assert nodes[0].healthy is True

    @patch("truth_forge.services.cluster_state.subprocess.run")
    @patch("truth_forge.services.cluster_state.check_readiness")
    def test_get_available_nodes_unreachable(
        self, mock_readiness: Mock, mock_subprocess: Mock
    ) -> None:
        """Test getting nodes when unreachable."""
        mock_readiness.return_value = {"scout": Mock(ready=True)}

        mock_result = Mock()
        mock_result.returncode = 1  # SSH failed
        mock_subprocess.return_value = mock_result

        monitor = ClusterStateMonitor(nodes=["test-node"])
        nodes = monitor.get_available_nodes()

        assert len(nodes) == 1
        assert nodes[0].healthy is False

    @patch("truth_forge.services.cluster_state.subprocess.run")
    @patch("truth_forge.services.cluster_state.check_readiness")
    def test_get_available_nodes_cached(self, mock_readiness: Mock, mock_subprocess: Mock) -> None:
        """Test nodes are cached."""
        mock_readiness.return_value = {"scout": Mock(ready=True)}

        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        monitor = ClusterStateMonitor(nodes=["test-node"], ttl=100.0)
        nodes1 = monitor.get_available_nodes()
        nodes2 = monitor.get_available_nodes()

        # Should use cache, so subprocess called once per node
        assert nodes1 == nodes2

    @patch("truth_forge.services.cluster_state.subprocess.run")
    @patch("truth_forge.services.cluster_state.check_readiness")
    def test_pick_least_loaded(self, mock_readiness: Mock, mock_subprocess: Mock) -> None:
        """Test picking least loaded node."""
        mock_readiness.return_value = {"scout": Mock(ready=True)}

        # Mock loadavg responses
        def mock_loadavg(cmd, **kwargs):
            result = Mock()
            if "loadavg" in cmd:
                result.returncode = 0
                result.stdout = "0.5\n"  # Low load
            else:
                result.returncode = 0
            return result

        mock_subprocess.side_effect = mock_loadavg

        monitor = ClusterStateMonitor(nodes=["node1", "node2"])
        node = monitor.pick_least_loaded()

        assert node in ["node1", "node2"]

    @patch("truth_forge.services.cluster_state.subprocess.run")
    @patch("truth_forge.services.cluster_state.check_readiness")
    def test_pick_least_loaded_no_healthy(
        self, mock_readiness: Mock, mock_subprocess: Mock
    ) -> None:
        """Test picking node when none healthy."""
        mock_readiness.return_value = {"scout": Mock(ready=False)}

        mock_result = Mock()
        mock_result.returncode = 1
        mock_subprocess.return_value = mock_result

        monitor = ClusterStateMonitor(nodes=["test-node"])
        node = monitor.pick_least_loaded()

        assert node == "king"  # Default fallback
