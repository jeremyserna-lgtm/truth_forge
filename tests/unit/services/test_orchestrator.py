"""Comprehensive tests for the Federation Orchestrator module.

Covers:
- OrchestratorConfig defaults and serialization
- OperationResult creation and fields
- Orchestrator initialization (with/without cognitive bridge)
- process() routing, kill switch, permission gating, peer review, PII scrubbing
- All operation handlers: see, see_stream, extract_metadata, struggle_filter,
  complete, health_check, exec, cluster_status, night_watch, explore
- Service management (get_service, register_service)
- health_check() aggregation
- is_available()
- get_orchestrator() singleton
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from truth_forge.governance.kill_switch import KillSwitchError
from truth_forge.services.orchestrator import (
    OperationResult,
    Orchestrator,
    OrchestratorConfig,
    get_orchestrator,
)


# ---------------------------------------------------------------------------
# Helpers / Fixtures
# ---------------------------------------------------------------------------

# Common patches required for every Orchestrator construction.
# They prevent real network/service initialization.
_ORCH_PATCHES = {
    "scout": "truth_forge.services.orchestrator.ScoutProvider",
    "governance": "truth_forge.services.orchestrator.get_governance",
    "flags": "truth_forge.services.orchestrator.feature_flags",
    "loop": "truth_forge.services.orchestrator.ensure_autonomous_loop",
    "not_me": "truth_forge.services.orchestrator.get_not_me",
    "armed": "truth_forge.services.orchestrator.assert_not_armed",
    "should_ask": "truth_forge.services.orchestrator.should_ask_permission",
    "check_readiness": "truth_forge.services.orchestrator.check_readiness",
    "collect_presence": "truth_forge.services.orchestrator.collect_presence",
    "control_plane_audit": "truth_forge.services.orchestrator.control_plane_record_audit",
    "scrub_messages": "truth_forge.services.orchestrator.scrub_messages",
    "verify_claim": "truth_forge.services.orchestrator.verify_claim",
    "cluster_tool": "truth_forge.services.orchestrator.ClusterExecutionTool",
}


@pytest.fixture()
def _mock_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure a clean environment for Orchestrator tests."""
    monkeypatch.setenv("GENESIS_EXECUTION_MODE", "servant")
    monkeypatch.delenv("SCOUT_BASE_URL", raising=False)


@pytest.fixture()
def mocks(_mock_env: None) -> dict[str, Mock]:
    """Patch all external dependencies and return a dict of mocks."""
    patchers = {name: patch(target) for name, target in _ORCH_PATCHES.items()}
    started: dict[str, Mock] = {}
    for name, p in patchers.items():
        started[name] = p.start()
    # Sensible defaults
    started["flags"].cognitive_bridge_enabled = False
    started["flags"].peer_review_required = False
    started["flags"].privacy_scrub_enabled = False
    started["flags"].routing = Mock(require_peer_review_above=0.5, safety_floor=0.3)
    started["flags"].risk_thresholds = Mock(servant_prompt=3, sovereign_prompt=4, irreversible=5)
    started["should_ask"].return_value = False
    started["check_readiness"].return_value = {}
    started["collect_presence"].return_value = {"hostname": "test"}
    started["control_plane_audit"].return_value = None
    # Governance mock with audit_trail.record
    mock_gov = Mock()
    mock_gov.audit_trail = Mock()
    started["governance"].return_value = mock_gov
    # Cluster exec tool mock
    started["cluster_tool"].return_value = Mock(cluster_state=None)
    yield started  # type: ignore[misc]
    for p in patchers.values():
        p.stop()


def _make_orchestrator(
    mocks: dict[str, Mock],
    enable_not_me: bool = False,
    enable_validators: bool = True,
) -> Orchestrator:
    """Build an Orchestrator with all externals mocked."""
    config = OrchestratorConfig(
        enable_not_me=enable_not_me,
        enable_validators=enable_validators,
    )
    return Orchestrator(config)


# ---------------------------------------------------------------------------
# OrchestratorConfig
# ---------------------------------------------------------------------------


class TestOrchestratorConfig:
    """Tests for the OrchestratorConfig dataclass."""

    def test_defaults(self) -> None:
        config = OrchestratorConfig()
        assert config.scout_model == "Llama-4-Scout-17B-16E-Instruct"
        assert config.enable_not_me is True
        assert config.enable_validators is True
        assert config.app_configs == {}

    def test_custom_values(self) -> None:
        config = OrchestratorConfig(
            scout_endpoint="http://custom:9999",
            scout_model="custom-model",
            enable_not_me=False,
        )
        assert config.scout_endpoint == "http://custom:9999"
        assert config.scout_model == "custom-model"
        assert config.enable_not_me is False

    def test_to_dict_contains_all_keys(self) -> None:
        config = OrchestratorConfig()
        d = config.to_dict()
        expected_keys = {
            "scout_endpoint",
            "scout_model",
            "enable_not_me",
            "enable_validators",
            "app_configs",
        }
        assert set(d.keys()) == expected_keys

    def test_scout_endpoint_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SCOUT_BASE_URL", "http://envhost:5555")
        config = OrchestratorConfig()
        assert config.scout_endpoint == "http://envhost:5555"


# ---------------------------------------------------------------------------
# OperationResult
# ---------------------------------------------------------------------------


class TestOperationResult:
    """Tests for OperationResult dataclass."""

    def test_defaults(self) -> None:
        result = OperationResult(
            success=True,
            content="ok",
            service="svc",
            operation="op",
            latency_ms=42.0,
        )
        assert result.error is None
        assert result.metadata == {}
        assert isinstance(result.timestamp, datetime)

    def test_with_error(self) -> None:
        result = OperationResult(
            success=False,
            content=None,
            service="svc",
            operation="op",
            latency_ms=0.0,
            error="boom",
        )
        assert result.error == "boom"
        assert result.success is False


# ---------------------------------------------------------------------------
# Orchestrator Initialization
# ---------------------------------------------------------------------------


class TestOrchestratorInit:
    """Test Orchestrator.__init__ paths."""

    def test_basic_init(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        assert orch.config is not None
        assert orch.scout is not None
        assert orch.governance is not None
        assert orch.cognitive_bridge is None  # disabled via flag

    def test_init_with_not_me_enabled(self, mocks: dict[str, Mock]) -> None:
        mock_nm_service = Mock()
        mocks["not_me"].return_value = mock_nm_service
        orch = _make_orchestrator(mocks, enable_not_me=True)
        assert "not_me" in orch._services

    def test_init_cognitive_bridge_enabled(self, mocks: dict[str, Mock]) -> None:
        mocks["flags"].cognitive_bridge_enabled = True
        mock_bridge = Mock()
        mock_bridge.config_path = "/fake/path"
        with patch(
            "truth_forge.services.orchestrator.CognitiveBridge",
            return_value=mock_bridge,
        ):
            orch = _make_orchestrator(mocks)
            assert orch.cognitive_bridge is mock_bridge

    def test_init_cognitive_bridge_failure_falls_back(self, mocks: dict[str, Mock]) -> None:
        mocks["flags"].cognitive_bridge_enabled = True
        with patch(
            "truth_forge.services.orchestrator.CognitiveBridge",
            side_effect=RuntimeError("no config"),
        ):
            orch = _make_orchestrator(mocks)
            assert orch.cognitive_bridge is None  # graceful fallback

    def test_execution_mode_from_env(
        self, mocks: dict[str, Mock], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("GENESIS_EXECUTION_MODE", "SOVEREIGN")
        orch = _make_orchestrator(mocks)
        assert orch.execution_mode == "sovereign"

    def test_execution_mode_default(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        assert orch.execution_mode == "servant"


# ---------------------------------------------------------------------------
# process() — Routing & Control Flow
# ---------------------------------------------------------------------------


class TestProcessRouting:
    """Test Orchestrator.process() routing logic."""

    def test_unknown_operation_returns_failure(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        result = orch.process("totally_bogus")
        assert result.success is False
        assert "Unknown operation" in (result.error or "")

    def test_kill_switch_propagates(self, mocks: dict[str, Mock]) -> None:
        mocks["armed"].side_effect = KillSwitchError("armed via env")
        orch = _make_orchestrator(mocks)
        with pytest.raises(KillSwitchError, match="armed via env"):
            orch.process("health_check")

    def test_permission_gating_raises(self, mocks: dict[str, Mock]) -> None:
        mocks["should_ask"].return_value = True
        orch = _make_orchestrator(mocks)
        with pytest.raises(PermissionError, match="requires confirmation"):
            orch.process("exec", command="echo hi")

    def test_peer_review_blocks_high_risk(self, mocks: dict[str, Mock]) -> None:
        """Peer review failure blocks exec (risk >= 4)."""
        mocks["flags"].peer_review_required = True
        mock_consensus = Mock(verified=False, agreement=0.0)
        mocks["verify_claim"].return_value = mock_consensus
        orch = _make_orchestrator(mocks)
        result = orch.process("exec", command="echo hi")
        assert result.success is False
        assert "peer review" in (result.error or "").lower()

    def test_peer_review_allows_when_consensus(self, mocks: dict[str, Mock]) -> None:
        """Peer review passes, operation proceeds."""
        mocks["flags"].peer_review_required = True
        mock_consensus = Mock(verified=True, agreement=1.0)
        mocks["verify_claim"].return_value = mock_consensus

        # Set up exec tool return value
        exec_result = Mock(exit_code=0, stdout="hello", stderr="", workdir="/tmp", duration_ms=10)
        mocks["cluster_tool"].return_value.execute.return_value = exec_result

        orch = _make_orchestrator(mocks)
        result = orch.process("exec", command="echo hello")
        assert result.success is True

    def test_privacy_scrub_on_dict_content(self, mocks: dict[str, Mock]) -> None:
        """PII scrubbing happens when feature flag enabled and content has messages."""
        mocks["flags"].privacy_scrub_enabled = True
        mocks["scrub_messages"].return_value = [{"role": "user", "content": "[redacted]"}]

        # Return a dict with messages from the health_check handler
        # We need a handler that returns dict content with messages; override _handle_health_check
        orch = _make_orchestrator(mocks)

        # Monkey-patch a handler to return content with messages key
        def _fake_handler(**kwargs):  # type: ignore[no-untyped-def]
            return OperationResult(
                success=True,
                content={"messages": [{"role": "user", "content": "secret@email.com"}]},
                service="test",
                operation="see",
                latency_ms=0,
            )

        orch._handlers["see"] = _fake_handler
        result = orch.process("see", content="anything")
        mocks["scrub_messages"].assert_called_once()
        assert result.content["messages"] == [{"role": "user", "content": "[redacted]"}]

    def test_handler_exception_returns_failure(self, mocks: dict[str, Mock]) -> None:
        """If a handler raises, process returns a failure result (not an exception)."""
        orch = _make_orchestrator(mocks)

        def _boom(**kwargs):  # type: ignore[no-untyped-def]
            raise ValueError("handler exploded")

        orch._handlers["see"] = _boom
        result = orch.process("see", content="x")
        assert result.success is False
        assert "handler exploded" in (result.error or "")

    def test_handler_kill_switch_error_re_raised(self, mocks: dict[str, Mock]) -> None:
        """KillSwitchError from a handler is re-raised, not swallowed."""
        orch = _make_orchestrator(mocks)

        def _kill(**kwargs):  # type: ignore[no-untyped-def]
            raise KillSwitchError("mid-operation kill")

        orch._handlers["see"] = _kill
        with pytest.raises(KillSwitchError):
            orch.process("see", content="x")

    def test_audit_trail_recorded_on_success(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        orch.process("health_check")
        # audit_trail.record should be called at least once (start of process)
        assert mocks["governance"].return_value.audit_trail.record.called

    def test_audit_trail_recorded_on_failure(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)

        def _fail(**kwargs):  # type: ignore[no-untyped-def]
            raise RuntimeError("fail")

        orch._handlers["see"] = _fail
        orch.process("see", content="x")
        # Should have 2 audit calls: start + error
        assert mocks["governance"].return_value.audit_trail.record.call_count >= 2

    def test_control_plane_audit_called(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        orch.process("health_check")
        assert mocks["control_plane_audit"].called

    def test_latency_ms_populated(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        result = orch.process("health_check")
        assert result.latency_ms >= 0


# ---------------------------------------------------------------------------
# Handler: see
# ---------------------------------------------------------------------------


class TestHandleSee:
    """Test _handle_see operation."""

    def test_not_me_disabled(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks, enable_not_me=False)
        result = orch.process("see", content="hi")
        assert result.success is False
        assert "Not-Me service not enabled" in (result.error or "")

    def test_success(self, mocks: dict[str, Mock]) -> None:
        mock_see_result = Mock()
        mock_see_result.to_dict.return_value = {"insight": "yes"}
        mock_see_result.latency_ms = 55.0
        mock_see_result.input_tokens = 10
        mock_see_result.output_tokens = 20
        mock_see_result.atoms = ["a1"]
        mock_nm = Mock()
        mock_nm.see.return_value = mock_see_result
        mocks["not_me"].return_value = mock_nm

        orch = _make_orchestrator(mocks, enable_not_me=True)
        result = orch.process("see", content="something")
        assert result.success is True
        assert result.content == {"insight": "yes"}
        assert result.metadata["atoms_count"] == 1


# ---------------------------------------------------------------------------
# Handler: see_stream
# ---------------------------------------------------------------------------


class TestHandleSeeStream:
    """Test _handle_see_stream operation."""

    def test_not_me_disabled(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks, enable_not_me=False)
        result = orch.process("see_stream", content="hi")
        assert result.success is False
        assert "Not-Me service not enabled" in (result.error or "")

    def test_returns_generator(self, mocks: dict[str, Mock]) -> None:
        mock_gen = iter(["chunk1", "chunk2"])
        mock_nm = Mock()
        mock_nm.see_stream.return_value = mock_gen
        mocks["not_me"].return_value = mock_nm

        orch = _make_orchestrator(mocks, enable_not_me=True)
        result = orch.process("see_stream", content="data")
        assert result.success is True
        # content should be the generator itself
        assert list(result.content) == ["chunk1", "chunk2"]


# ---------------------------------------------------------------------------
# Handler: extract_metadata
# ---------------------------------------------------------------------------


class TestHandleExtractMetadata:
    """Test _handle_extract_metadata operation."""

    def test_not_me_disabled(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks, enable_not_me=False)
        result = orch.process("extract_metadata", content="hi")
        assert result.success is False

    def test_success(self, mocks: dict[str, Mock]) -> None:
        mock_nm = Mock()
        mock_nm.extract_metadata.return_value = {"emotion": "joy"}
        mocks["not_me"].return_value = mock_nm
        orch = _make_orchestrator(mocks, enable_not_me=True)
        result = orch.process("extract_metadata", content="happy text")
        assert result.success is True
        assert result.content == {"emotion": "joy"}


# ---------------------------------------------------------------------------
# Handler: struggle_filter
# ---------------------------------------------------------------------------


class TestHandleStruggleFilter:
    """Test _handle_struggle_filter operation."""

    def test_not_me_disabled(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks, enable_not_me=False)
        result = orch.process("struggle_filter", content="x")
        assert result.success is False

    def test_success(self, mocks: dict[str, Mock]) -> None:
        mock_nm = Mock()
        mock_nm.run_struggle_filter.return_value = ("swimming", True)
        mocks["not_me"].return_value = mock_nm
        orch = _make_orchestrator(mocks, enable_not_me=True)
        result = orch.process("struggle_filter", content="I'm building")
        assert result.success is True
        assert result.content["classification"] == "swimming"
        assert result.content["keep"] is True


# ---------------------------------------------------------------------------
# Handler: complete
# ---------------------------------------------------------------------------


class TestHandleComplete:
    """Test _handle_complete operation."""

    def test_complete_via_scout(self, mocks: dict[str, Mock]) -> None:
        mock_response = Mock()
        mock_response.content = "scout response"
        mock_response.latency_ms = 100.0
        mock_response.input_tokens = 50
        mock_response.output_tokens = 30
        mock_response.model = "scout-genesis"
        mocks["scout"].return_value.complete.return_value = mock_response

        orch = _make_orchestrator(mocks)
        result = orch.process("complete", prompt="Hello")
        assert result.success is True
        assert result.content == "scout response"
        assert result.metadata["model"] == "scout-genesis"

    def test_complete_via_cognitive_bridge(self, mocks: dict[str, Mock]) -> None:
        mocks["flags"].cognitive_bridge_enabled = True
        mock_bridge = Mock()
        mock_bridge.config_path = "/fake"
        mock_resp = Mock()
        mock_resp.content = "bridge response"
        mock_resp.latency_ms = 50.0
        mock_resp.input_tokens = 10
        mock_resp.output_tokens = 20
        mock_resp.model = "maverick"
        mock_bridge.complete.return_value = mock_resp

        with patch(
            "truth_forge.services.orchestrator.CognitiveBridge",
            return_value=mock_bridge,
        ):
            orch = _make_orchestrator(mocks)
            # NOTE: Do not pass task_type as kwarg because it flows into
            # CompletionRequest(**kwargs) which does not accept it.
            # Instead, test without extra kwargs so the bridge path is exercised.
            result = orch.process("complete", prompt="test")
            assert result.success is True
            assert result.content == "bridge response"
            mock_bridge.complete.assert_called_once()


# ---------------------------------------------------------------------------
# Handler: health_check
# ---------------------------------------------------------------------------


class TestHandleHealthCheck:
    """Test _handle_health_check and health_check()."""

    def test_healthy_when_scout_available(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = True
        orch = _make_orchestrator(mocks)
        result = orch.process("health_check")
        assert result.success is True
        assert result.content["status"] == "healthy"

    def test_degraded_when_scout_unavailable(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = False
        orch = _make_orchestrator(mocks)
        result = orch.process("health_check")
        assert result.content["status"] == "degraded"

    def test_health_check_includes_services(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = True
        # Register a mock service with health_check
        mock_service = Mock()
        mock_service.health_check.return_value = {"status": "healthy"}
        mock_nm = Mock()
        mock_nm.health_check.return_value = {"status": "healthy"}
        mocks["not_me"].return_value = mock_nm

        orch = _make_orchestrator(mocks, enable_not_me=True)
        health = orch.health_check()
        assert "not_me" in health["services"]

    def test_health_check_with_is_available_service(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = True
        orch = _make_orchestrator(mocks)
        # Register service with is_available but no health_check
        mock_service = Mock(spec=["is_available"])
        mock_service.is_available.return_value = True
        orch.register_service("custom_svc", mock_service)
        health = orch.health_check()
        assert health["services"]["custom_svc"]["available"] is True

    def test_health_check_degraded_when_service_unhealthy(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = True
        orch = _make_orchestrator(mocks)
        mock_service = Mock()
        mock_service.health_check.return_value = {"status": "degraded"}
        orch.register_service("bad_svc", mock_service)
        health = orch.health_check()
        assert health["status"] == "degraded"

    def test_health_check_uptime(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = True
        orch = _make_orchestrator(mocks)
        health = orch.health_check()
        assert health["uptime_seconds"] >= 0

    def test_health_check_model_readiness(self, mocks: dict[str, Mock]) -> None:
        @dataclass
        class FakeReadiness:
            ready: bool
            size_gb: float

        mocks["check_readiness"].return_value = {
            "scout": FakeReadiness(ready=True, size_gb=100.0),
            "maverick": FakeReadiness(ready=False, size_gb=50.0),
            "r1": FakeReadiness(ready=False, size_gb=0.0),
        }
        mocks["scout"].return_value.is_available.return_value = True
        orch = _make_orchestrator(mocks)
        health = orch.health_check()
        assert health["models"]["readiness"]["scout"] is True
        assert health["models"]["readiness"]["maverick"] is False

    def test_health_check_with_cognitive_bridge(self, mocks: dict[str, Mock]) -> None:
        mocks["flags"].cognitive_bridge_enabled = True
        mock_bridge = Mock()
        mock_bridge.config_path = "/fake"
        mock_bridge.maverick = Mock()
        mock_bridge.maverick.is_available.return_value = True
        mock_bridge.r1 = Mock()
        mock_bridge.r1.is_available.return_value = False
        mock_bridge.config = {
            "models": {
                "maverick": {"endpoint": "http://mav:1234"},
                "r1": {"endpoint": "http://r1:5678"},
            },
        }
        mocks["scout"].return_value.is_available.return_value = False

        with patch(
            "truth_forge.services.orchestrator.CognitiveBridge",
            return_value=mock_bridge,
        ):
            orch = _make_orchestrator(mocks)
            health = orch.health_check()
            # maverick is available, so overall can be healthy
            assert health["models"]["maverick"]["available"] is True
            assert health["models"]["r1"]["available"] is False


# ---------------------------------------------------------------------------
# Handler: exec
# ---------------------------------------------------------------------------


class TestHandleExec:
    """Test _handle_exec operation."""

    def test_exec_success(self, mocks: dict[str, Mock]) -> None:
        exec_result = Mock(
            exit_code=0,
            stdout="hello",
            stderr="",
            workdir="/tmp/w",
            duration_ms=15.0,
        )
        mocks["cluster_tool"].return_value.execute.return_value = exec_result
        orch = _make_orchestrator(mocks)
        result = orch.process("exec", command="echo hello")
        assert result.success is True
        assert result.content["stdout"] == "hello"
        assert result.content["exit_code"] == 0
        assert result.error is None

    def test_exec_failure(self, mocks: dict[str, Mock]) -> None:
        exec_result = Mock(
            exit_code=1,
            stdout="",
            stderr="not found",
            workdir="/tmp/w",
            duration_ms=5.0,
        )
        mocks["cluster_tool"].return_value.execute.return_value = exec_result
        orch = _make_orchestrator(mocks)
        result = orch.process("exec", command="bad_cmd")
        assert result.success is False
        assert result.error == "Command failed"

    def test_exec_peer_review_blocks(self, mocks: dict[str, Mock]) -> None:
        mocks["flags"].peer_review_required = True
        mock_consensus = Mock(verified=False, agreement=0.0)
        mocks["verify_claim"].return_value = mock_consensus
        orch = _make_orchestrator(mocks)
        # The process-level peer review blocks first for risk>=4
        result = orch.process("exec", command="dangerous")
        assert result.success is False
        assert "peer review" in (result.error or "").lower()


# ---------------------------------------------------------------------------
# Handler: cluster_status
# ---------------------------------------------------------------------------


class TestHandleClusterStatus:
    """Test _handle_cluster_status operation."""

    def test_no_cluster_state(self, mocks: dict[str, Mock]) -> None:
        mocks["cluster_tool"].return_value.cluster_state = None
        orch = _make_orchestrator(mocks)
        result = orch.process("cluster_status")
        assert result.success is True
        assert result.content["nodes"] == []

    def test_with_cluster_state(self, mocks: dict[str, Mock]) -> None:
        mock_node = Mock()
        mock_node.name = "king"
        mock_node.healthy = True
        mock_node.metadata = {"reachable": True, "load": 0.5, "models": ["scout"]}
        mock_node.last_checked = "2026-01-01T00:00:00"
        mock_state = Mock()
        mock_state.get_available_nodes.return_value = [mock_node]
        mocks["cluster_tool"].return_value.cluster_state = mock_state

        orch = _make_orchestrator(mocks)
        result = orch.process("cluster_status")
        assert result.success is True
        assert len(result.content["nodes"]) == 1
        assert result.content["nodes"][0]["name"] == "king"


# ---------------------------------------------------------------------------
# Handler: night_watch
# ---------------------------------------------------------------------------


class TestHandleNightWatch:
    """Test _handle_night_watch operation."""

    def test_success(self, mocks: dict[str, Mock]) -> None:
        mocks["collect_presence"].return_value = {"hostname": "king", "pid": 123}
        orch = _make_orchestrator(mocks)
        result = orch.process("night_watch")
        assert result.success is True
        assert result.content["presence"]["hostname"] == "king"
        # Should record audit
        assert mocks["governance"].return_value.audit_trail.record.called


# ---------------------------------------------------------------------------
# Handler: explore
# ---------------------------------------------------------------------------


class TestHandleExplore:
    """Test _handle_explore operation."""

    def test_success(self, mocks: dict[str, Mock]) -> None:
        mock_report = Mock()
        mock_report.model_dump.return_value = {"summary": "explored"}
        mock_report.duration_seconds = 1.5
        mock_report.findings = ["f1", "f2"]
        mock_report.patterns_discovered = ["p1"]
        mock_report.iterations_completed = 5
        mock_report.total_resonance_score = 0.8
        mock_report.total_cost = 0.0

        mock_explorer = Mock()
        mock_explorer.explore.return_value = mock_report

        orch = _make_orchestrator(mocks)

        # _handle_explore does lazy imports of ExplorationConfig, ExplorationDepth,
        # and get_service. We patch at the source (truth_forge.services.factory and
        # truth_forge.services.explorer.models).
        mock_config_cls = Mock(return_value=Mock())
        mock_depth_cls = Mock(return_value="medium")

        with (
            patch(
                "truth_forge.services.factory.ServiceFactory.get",
                return_value=mock_explorer,
            ),
            patch(
                "truth_forge.services.explorer.models.ExplorationConfig",
                mock_config_cls,
            ),
            patch(
                "truth_forge.services.explorer.models.ExplorationDepth",
                mock_depth_cls,
            ),
        ):
            result = orch.process("explore", iterations=3, focus_area="test")
            assert result.success is True
            assert result.content == {"summary": "explored"}
            assert result.metadata["findings_count"] == 2

    def test_failure_returns_error_result(self, mocks: dict[str, Mock]) -> None:
        """When explorer raises, _handle_explore catches and returns failure."""
        orch = _make_orchestrator(mocks)

        with patch(
            "truth_forge.services.factory.ServiceFactory.get",
            side_effect=RuntimeError("explorer not available"),
        ):
            result = orch.process("explore")
            assert result.success is False
            assert result.error is not None


# ---------------------------------------------------------------------------
# Service Management
# ---------------------------------------------------------------------------


class TestServiceManagement:
    """Test get_service and register_service."""

    def test_get_service_returns_registered(self, mocks: dict[str, Mock]) -> None:
        mock_nm = Mock()
        mocks["not_me"].return_value = mock_nm
        orch = _make_orchestrator(mocks, enable_not_me=True)
        assert orch.get_service("not_me") is mock_nm

    def test_get_service_returns_none_for_unknown(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        assert orch.get_service("does_not_exist") is None

    def test_register_service(self, mocks: dict[str, Mock]) -> None:
        orch = _make_orchestrator(mocks)
        custom = Mock()
        orch.register_service("custom", custom)
        assert orch.get_service("custom") is custom


# ---------------------------------------------------------------------------
# is_available
# ---------------------------------------------------------------------------


class TestIsAvailable:
    """Test Orchestrator.is_available."""

    def test_available_when_scout_available(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = True
        orch = _make_orchestrator(mocks)
        assert orch.is_available() is True

    def test_unavailable_when_scout_down(self, mocks: dict[str, Mock]) -> None:
        mocks["scout"].return_value.is_available.return_value = False
        orch = _make_orchestrator(mocks)
        assert orch.is_available() is False


# ---------------------------------------------------------------------------
# get_orchestrator() Singleton
# ---------------------------------------------------------------------------


class TestGetOrchestrator:
    """Test get_orchestrator singleton."""

    @patch("truth_forge.services.orchestrator._orchestrator_instance", None)
    @patch("truth_forge.services.orchestrator.Orchestrator")
    def test_creates_singleton(self, mock_cls: Mock) -> None:
        mock_instance = Mock()
        mock_cls.return_value = mock_instance
        o1 = get_orchestrator()
        o2 = get_orchestrator()
        assert o1 is o2
        assert mock_cls.call_count == 1

    @patch("truth_forge.services.orchestrator._orchestrator_instance", None)
    @patch("truth_forge.services.orchestrator.Orchestrator")
    def test_uses_provided_config(self, mock_cls: Mock) -> None:
        mock_cls.return_value = Mock()
        config = OrchestratorConfig(scout_model="custom")
        get_orchestrator(config)
        call_config = mock_cls.call_args[0][0]
        assert call_config.scout_model == "custom"

    @patch("truth_forge.services.orchestrator._orchestrator_instance", None)
    @patch("truth_forge.services.orchestrator.Orchestrator")
    def test_uses_default_config_when_none(self, mock_cls: Mock) -> None:
        mock_cls.return_value = Mock()
        get_orchestrator(None)
        call_config = mock_cls.call_args[0][0]
        assert isinstance(call_config, OrchestratorConfig)
