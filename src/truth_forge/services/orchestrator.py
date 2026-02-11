"""Federation Orchestrator - Unified Command Center.

The Orchestrator is the central nervous system of the Federation.
It coordinates all services and apps, routing operations through Scout.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                    FEDERATION ORCHESTRATOR                   │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │  ┌─────────────────────┐  ┌─────────────────────┐          │
    │  │   TRUTH ENGINE      │  │   PRIMITIVE ENGINE  │          │
    │  │   (The Soul)        │  │   (The Builder)     │          │
    │  └──────────┬──────────┘  └──────────┬──────────┘          │
    │             │                        │                      │
    │             └────────────┬───────────┘                      │
    │                          │                                  │
    │                          ▼                                  │
    │              ┌─────────────────────┐                        │
    │              │   SCOUT BACKBONE    │                        │
    │              │ (LLaMA 4 Scout 10M) │                        │
    │              └──────────┬──────────┘                        │
    │                         │                                   │
    │              ┌──────────┴──────────┐                        │
    │              │                     │                        │
    │              ▼                     ▼                        │
    │  ┌─────────────────────┐  ┌─────────────────────┐          │
    │  │   NOT-ME SERVICE    │  │   CREDENTIAL ATLAS  │          │
    │  │   (Production)      │  │   (The Seer)        │          │
    │  └─────────────────────┘  └─────────────────────┘          │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

Usage:
    from truth_forge.services.orchestrator import Orchestrator, get_orchestrator

    # Get singleton orchestrator
    orch = get_orchestrator()

    # Route operation through appropriate service
    result = orch.process(operation="see", content=text)

    # Get unified health status
    health = orch.health_check()

MOLT LINEAGE:
- Source: New creation for Federation infrastructure
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import logging
import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import RLock
from typing import Any, cast

from truth_forge.gateway import ScoutProvider
from truth_forge.governance import (
    AuditCategory,
    AuditLevel,
    KillSwitchError,
    assert_not_armed,
    control_plane_record_audit,
    feature_flags,
    get_governance,
    scrub_messages,
    should_ask_permission,
    verify_claim,
)
from truth_forge.services.autonomous_loop import ensure_autonomous_loop
from truth_forge.services.cluster_execution_tool import ClusterExecutionTool
from truth_forge.services.cognitive_bridge import CognitiveBridge
from truth_forge.services.model_readiness import check_readiness
from truth_forge.services.not_me import NotMeConfig, get_not_me
from truth_forge.services.sensors import collect_presence


logger = logging.getLogger(__name__)


# Singleton instance
_orchestrator_instance: Orchestrator | None = None
_lock = RLock()


def get_orchestrator(config: OrchestratorConfig | None = None) -> Orchestrator:
    """Get or create the singleton Orchestrator.

    Args:
        config: Optional configuration. Only used on first call.

    Returns:
        The Orchestrator singleton.
    """
    global _orchestrator_instance

    with _lock:
        if _orchestrator_instance is None:
            _orchestrator_instance = Orchestrator(config or OrchestratorConfig())
        return _orchestrator_instance


@dataclass
class OrchestratorConfig:
    """Configuration for the Federation Orchestrator.

    Attributes:
        scout_endpoint: LLaMA 4 Scout server URL.
        scout_model: Default Scout model.
        enable_not_me: Enable Not-Me production service.
        enable_validators: Enable external validators.
        app_configs: Configuration for each app.
    """

    scout_endpoint: str = field(
        default_factory=lambda: os.environ.get("SCOUT_BASE_URL", "http://localhost:1234/v1")
    )
    scout_model: str = "Llama-4-Scout-17B-16E-Instruct"
    enable_not_me: bool = True
    enable_validators: bool = True
    app_configs: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scout_endpoint": self.scout_endpoint,
            "scout_model": self.scout_model,
            "enable_not_me": self.enable_not_me,
            "enable_validators": self.enable_validators,
            "app_configs": self.app_configs,
        }


@dataclass
class OperationResult:
    """Result of an orchestrated operation."""

    success: bool
    content: Any
    service: str
    operation: str
    latency_ms: float
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class Orchestrator:
    """Federation Orchestrator - Central Command.

    Coordinates all services and routes operations through Scout.
    """

    def __init__(self, config: OrchestratorConfig) -> None:
        """Initialize Orchestrator.

        Args:
            config: Orchestrator configuration.
        """
        self.config = config
        self._start_time = datetime.now(UTC)
        self._execution_mode = os.environ.get("GENESIS_EXECUTION_MODE", "servant").lower()

        # Initialize Scout backbone
        # NOTE: ScoutProvider uses THE_MODEL constant internally (llama4:scout)
        self.scout = ScoutProvider(
            base_url=config.scout_endpoint,
        )

        # Governance membrane
        self.governance = get_governance()

        # Cognitive bridge (routing) - optional
        self.cognitive_bridge = None
        if feature_flags.cognitive_bridge_enabled:
            try:
                self.cognitive_bridge = CognitiveBridge()
                logger.info(
                    "Cognitive Bridge enabled",
                    extra={"config": str(self.cognitive_bridge.config_path)},
                )
            except Exception as e:
                logger.error(
                    "Failed to init Cognitive Bridge; defaulting to Scout", extra={"error": str(e)}
                )
                self.cognitive_bridge = None

        # Start autonomous loop if enabled
        self.autonomous_loop = None
        ensure_autonomous_loop(self)

        # Initialize services
        self._services: dict[str, Any] = {}
        self._exec_tool = ClusterExecutionTool()

        if config.enable_not_me:
            not_me_config = NotMeConfig(
                scout_endpoint=config.scout_endpoint,
                scout_model=config.scout_model,
                enable_validators=config.enable_validators,
            )
            self._services["not_me"] = get_not_me(not_me_config)

        # Operation handlers
        self._handlers: dict[str, Callable[..., OperationResult]] = {
            "see": self._handle_see,
            "see_stream": self._handle_see_stream,
            "extract_metadata": self._handle_extract_metadata,
            "struggle_filter": self._handle_struggle_filter,
            "health_check": self._handle_health_check,
            "complete": self._handle_complete,
            "explore": self._handle_explore,
            "night_watch": self._handle_night_watch,
            "exec": self._handle_exec,
            "cluster_status": self._handle_cluster_status,
        }

        logger.info(
            "Orchestrator initialized",
            extra={
                "endpoint": config.scout_endpoint,
                "services": list(self._services.keys()),
            },
        )

    # =========================================================================
    # MAIN ROUTING
    # =========================================================================

    def process(
        self,
        operation: str,
        **kwargs: Any,
    ) -> OperationResult:
        """Process an operation through the appropriate service.

        Args:
            operation: Operation name (see, extract_metadata, etc.).
            **kwargs: Operation-specific arguments.

        Returns:
            OperationResult with success status and content.
        """
        import time

        # Global kill switch
        assert_not_armed()

        # Risk level heuristic per op (1-5)
        risk_level = {
            "health_check": 1,
            "see": 1,
            "see_stream": 1,
            "extract_metadata": 2,
            "struggle_filter": 2,
            "explore": 2,
            "complete": 3,
            "exec": 4,
        }.get(operation, 2)

        # Permission gating per execution mode
        if should_ask_permission(self._execution_mode, risk_level):
            raise PermissionError(
                f"Operation '{operation}' requires confirmation in mode={self._execution_mode} (risk={risk_level})"
            )

        # Peer review gate for high-risk ops (global)
        if feature_flags.peer_review_required and risk_level >= 4 and operation != "health_check":
            consensus = verify_claim(
                claim=f"Execute operation '{operation}'",
                context={"kwargs_keys": list(kwargs.keys()), "risk_level": risk_level},
                threshold=feature_flags.routing.require_peer_review_above,
            )
            if not consensus.verified:
                return OperationResult(
                    success=False,
                    content={"reason": "peer_review_failed", "consensus": consensus.agreement},
                    service="orchestrator",
                    operation=operation,
                    latency_ms=0,
                    error="Peer review did not reach consensus",
                )

        start = time.time()

        handler = self._handlers.get(operation)
        if not handler:
            return OperationResult(
                success=False,
                content=None,
                service="orchestrator",
                operation=operation,
                latency_ms=0,
                error=f"Unknown operation: {operation}",
            )

        audit_ctx = {
            "operation": operation,
            "kwargs_keys": list(kwargs.keys()),
            "execution_mode": self._execution_mode,
            "risk_level": risk_level,
        }

        # Record start in audit (local + control plane)
        self.governance.audit_trail.record(
            operation=operation,
            component="orchestrator",
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFO,
            context=audit_ctx,
        )
        control_plane_record_audit(
            {
                "operation": operation,
                "component": "orchestrator",
                "category": AuditCategory.SYSTEM.value,
                "level": AuditLevel.INFO.value,
                "context": audit_ctx,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

        _last_error: str = ""
        try:
            result = handler(**kwargs)
            result.latency_ms = (time.time() - start) * 1000

            # Scrub PII in common payloads if enabled
            if feature_flags.privacy_scrub_enabled and isinstance(result.content, dict):
                content = result.content
                if "messages" in content and isinstance(content["messages"], list):
                    result.content = {
                        **content,
                        "messages": scrub_messages(cast("list", content["messages"])),
                    }

            return result
        except Exception as e:
            _last_error = str(e)
            logger.error(f"Operation failed: {operation}", extra={"error": _last_error})
            # Audit failure
            self.governance.audit_trail.record(
                operation=operation,
                component="orchestrator",
                category=AuditCategory.SYSTEM,
                level=AuditLevel.ERROR,
                success=False,
                error_message=_last_error,
                context=audit_ctx,
            )
            control_plane_record_audit(
                {
                    "operation": operation,
                    "component": "orchestrator",
                    "category": AuditCategory.SYSTEM.value,
                    "level": AuditLevel.ERROR.value,
                    "success": False,
                    "error_message": _last_error,
                    "context": audit_ctx,
                    "timestamp": datetime.now(UTC).isoformat(),
                }
            )
            if isinstance(e, KillSwitchError):
                raise
        return OperationResult(
            success=False,
            content=None,
            service="orchestrator",
            operation=operation,
            latency_ms=(time.time() - start) * 1000,
            error=_last_error,
        )

    @property
    def execution_mode(self) -> str:
        """Return current execution mode (servant/sovereign/discovery)."""
        return self._execution_mode

    # =========================================================================
    # OPERATION HANDLERS
    # =========================================================================

    def _handle_see(
        self, content: str, context: str | None = None, **kwargs: Any
    ) -> OperationResult:
        """Handle seeing operation through Not-Me service."""
        if "not_me" not in self._services:
            return OperationResult(
                success=False,
                content=None,
                service="not_me",
                operation="see",
                latency_ms=0,
                error="Not-Me service not enabled",
            )

        result = self._services["not_me"].see(content, context)

        return OperationResult(
            success=True,
            content=result.to_dict(),
            service="not_me",
            operation="see",
            latency_ms=result.latency_ms,
            metadata={
                "input_tokens": result.input_tokens,
                "output_tokens": result.output_tokens,
                "atoms_count": len(result.atoms),
            },
        )

    def _handle_see_stream(
        self,
        content: str,
        context: str | None = None,
        **kwargs: Any,
    ) -> OperationResult:
        """Handle streaming seeing operation."""
        if "not_me" not in self._services:
            return OperationResult(
                success=False,
                content=None,
                service="not_me",
                operation="see_stream",
                latency_ms=0,
                error="Not-Me service not enabled",
            )

        # Return generator for streaming
        generator = self._services["not_me"].see_stream(content, context)

        return OperationResult(
            success=True,
            content=generator,  # Caller must iterate
            service="not_me",
            operation="see_stream",
            latency_ms=0,
        )

    def _handle_extract_metadata(self, content: str, **kwargs: Any) -> OperationResult:
        """Handle metadata extraction for Jeremy Arc."""
        if "not_me" not in self._services:
            return OperationResult(
                success=False,
                content=None,
                service="not_me",
                operation="extract_metadata",
                latency_ms=0,
                error="Not-Me service not enabled",
            )

        metadata = self._services["not_me"].extract_metadata(content)

        return OperationResult(
            success=True,
            content=metadata,
            service="not_me",
            operation="extract_metadata",
            latency_ms=0,
        )

    def _handle_struggle_filter(self, content: str, **kwargs: Any) -> OperationResult:
        """Handle struggle filter classification."""
        if "not_me" not in self._services:
            return OperationResult(
                success=False,
                content=None,
                service="not_me",
                operation="struggle_filter",
                latency_ms=0,
                error="Not-Me service not enabled",
            )

        classification, keep = self._services["not_me"].run_struggle_filter(content)

        return OperationResult(
            success=True,
            content={"classification": classification, "keep": keep},
            service="not_me",
            operation="struggle_filter",
            latency_ms=0,
        )

    def _handle_complete(
        self,
        prompt: str,
        system: str | None = None,
        **kwargs: Any,
    ) -> OperationResult:
        """Handle direct Scout completion."""
        from truth_forge.gateway import CompletionRequest

        request = CompletionRequest(
            prompt=prompt,
            model="scout-genesis",
            system=system,
            **kwargs,
        )

        if self.cognitive_bridge:
            response = self.cognitive_bridge.complete(
                request, task_type=kwargs.get("task_type", "auto")
            )
        else:
            response = self.scout.complete(request)

        return OperationResult(
            success=True,
            content=response.content,
            service="scout",
            operation="complete",
            latency_ms=response.latency_ms,
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "model": response.model,
            },
        )

    def _handle_health_check(self, **kwargs: Any) -> OperationResult:
        """Handle health check operation."""
        health = self.health_check()

        return OperationResult(
            success=health["status"] == "healthy",
            content=health,
            service="orchestrator",
            operation="health_check",
            latency_ms=0,
        )

    def _handle_exec(
        self,
        command: str,
        language: str = "bash",
        node: str = "local",
        risk_level: int = 4,
        env: dict[str, str] | None = None,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> OperationResult:
        """Execute code via cluster execution tool (docker-free)."""
        # Optional peer review for high-risk exec
        if feature_flags.peer_review_required and risk_level >= 4:
            consensus = verify_claim(
                claim=f"Execute command: {command}",
                context={"node": node, "language": language},
                threshold=feature_flags.routing.require_peer_review_above,
            )
            if not consensus.verified:
                return OperationResult(
                    success=False,
                    content={"reason": "peer_review_failed", "consensus": consensus.agreement},
                    service="execution",
                    operation="exec",
                    latency_ms=0,
                    error="Peer review did not reach consensus",
                )

        exec_result = self._exec_tool.execute(
            command=command,
            language=language,
            node=node,
            env=env,
            dry_run=dry_run,
        )

        return OperationResult(
            success=exec_result.exit_code == 0,
            content={
                "stdout": exec_result.stdout,
                "stderr": exec_result.stderr,
                "workdir": exec_result.workdir,
                "exit_code": exec_result.exit_code,
            },
            service="execution",
            operation="exec",
            latency_ms=exec_result.duration_ms,
            metadata={"node": node, "language": language},
            error=None if exec_result.exit_code == 0 else "Command failed",
        )

    def _handle_cluster_status(self, **kwargs: Any) -> OperationResult:
        """Return cluster node + model readiness status."""
        nodes = []
        if self._exec_tool.cluster_state:
            nodes = [
                {
                    "name": s.name,
                    "healthy": s.healthy,
                    "reachable": s.metadata.get("reachable"),
                    "load": s.metadata.get("load"),
                    "models": s.metadata.get("models"),
                    "last_checked": s.last_checked,
                }
                for s in self._exec_tool.cluster_state.get_available_nodes()
            ]
        readiness = check_readiness()
        return OperationResult(
            success=True,
            content={
                "nodes": nodes,
                "models": {
                    k: {"size_gb": v.size_gb, "ready": v.ready} for k, v in readiness.items()
                },
            },
            service="orchestrator",
            operation="cluster_status",
            latency_ms=0,
        )

    def _handle_night_watch(self, **kwargs: Any) -> OperationResult:
        """Nightly presence/sensor sweep; runs during off-hours automatically."""
        presence = collect_presence()
        self.governance.audit_trail.record(
            operation="night_watch",
            component="orchestrator",
            category=AuditCategory.SYSTEM,
            level=AuditLevel.INFO,
            context={"presence": presence},
        )
        control_plane_record_audit(
            {
                "operation": "night_watch",
                "component": "orchestrator",
                "category": AuditCategory.SYSTEM.value,
                "level": AuditLevel.INFO.value,
                "context": {"presence": presence},
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )
        return OperationResult(
            success=True,
            content={"presence": presence},
            service="orchestrator",
            operation="night_watch",
            latency_ms=0,
        )

    def _handle_explore(
        self,
        iterations: int = 5,
        focus_area: str | None = None,
        depth: str = "medium",
        **kwargs: Any,
    ) -> OperationResult:
        """Handle autonomous exploration operation.

        Runs the ExplorerService for autonomous data exploration with
        full cognitive architecture integration (Total Resonance, Struggle Filter).

        Args:
            iterations: Number of exploration iterations.
            focus_area: Optional focus area for exploration.
            depth: Exploration depth (shallow, medium, deep).
            **kwargs: Additional exploration parameters.

        Returns:
            OperationResult with exploration report.
        """
        from truth_forge.services.explorer.models import (
            ExplorationConfig,
            ExplorationDepth,
        )
        from truth_forge.services.factory import get_service

        try:
            config = ExplorationConfig(
                iterations=iterations,
                focus_area=focus_area,
                depth=ExplorationDepth(depth),
            )
            explorer = get_service("explorer")
            report = explorer.explore(config)

            return OperationResult(
                success=True,
                content=report.model_dump(),
                service="explorer",
                operation="explore",
                latency_ms=report.duration_seconds * 1000,
                metadata={
                    "findings_count": len(report.findings),
                    "patterns_count": len(report.patterns_discovered),
                    "iterations_completed": report.iterations_completed,
                    "total_resonance_score": report.total_resonance_score,
                    "cost": report.total_cost,
                },
            )

        except Exception as e:
            logger.error(
                "Exploration failed",
                extra={
                    "iterations": iterations,
                    "focus_area": focus_area,
                    "depth": depth,
                    "error": str(e),
                },
            )
            return OperationResult(
                success=False,
                content=None,
                service="explorer",
                operation="explore",
                latency_ms=0,
                error=str(e),
            )

    # =========================================================================
    # SERVICE MANAGEMENT
    # =========================================================================

    def get_service(self, name: str) -> Any | None:
        """Get a registered service by name."""
        return self._services.get(name)

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the orchestrator."""
        self._services[name] = service
        logger.info(f"Service registered: {name}")

    def health_check(self) -> dict[str, Any]:
        """Comprehensive health check of all services.

        Returns:
            Health status dict.
        """
        scout_available = self.scout.is_available()
        maverick_available = (
            self.cognitive_bridge.maverick.is_available() if self.cognitive_bridge else False
        )
        r1_available = self.cognitive_bridge.r1.is_available() if self.cognitive_bridge else False
        readiness = check_readiness()

        service_health = {}
        all_healthy = scout_available or maverick_available

        for name, service in self._services.items():
            if hasattr(service, "health_check"):
                health = service.health_check()
                service_health[name] = health
                if health.get("status") != "healthy":
                    all_healthy = False
            elif hasattr(service, "is_available"):
                available = service.is_available()
                service_health[name] = {"available": available}
                if not available:
                    all_healthy = False

        return {
            "status": "healthy" if all_healthy else "degraded",
            "orchestrator": "running",
            "models": {
                "scout": {
                    "available": scout_available,
                    "endpoint": self.config.scout_endpoint,
                    "model": self.config.scout_model,
                },
                "maverick": {
                    "available": maverick_available,
                    "endpoint": self.cognitive_bridge.config["models"]["maverick"]["endpoint"]
                    if self.cognitive_bridge
                    else None,
                },
                "r1": {
                    "available": r1_available,
                    "endpoint": self.cognitive_bridge.config["models"]["r1"]["endpoint"]
                    if self.cognitive_bridge
                    else None,
                },
                "readiness": {
                    "scout": readiness.get("scout").ready if readiness.get("scout") else False,
                    "maverick": readiness.get("maverick").ready
                    if readiness.get("maverick")
                    else False,
                    "r1": readiness.get("r1").ready if readiness.get("r1") else False,
                    "sizes_gb": {k: v.size_gb for k, v in readiness.items()},
                },
            },
            "services": service_health,
            "config": self.config.to_dict(),
            "uptime_seconds": (datetime.now(UTC) - self._start_time).total_seconds(),
        }

    def is_available(self) -> bool:
        """Check if orchestrator is fully operational."""
        return self.scout.is_available()


__all__ = ["Orchestrator", "OrchestratorConfig", "OperationResult", "get_orchestrator"]
