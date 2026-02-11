"""Feature flag loader for Genesis/Agent Zero adaptations.

Flags are defined in YAML (config/base/genesis_feature_flags.yaml) and can be
overridden by environment variables of the form GENESIS_FLAG_<UPPER_SNAKE>.

Example:
    from truth_forge.governance.feature_flags import feature_flags
    if feature_flags.cluster_execution_enabled:
        ...
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from truth_forge.core.paths import CONFIG_ROOT


_DEFAULT_FLAG_FILE = CONFIG_ROOT / "base" / "genesis_feature_flags.yaml"


def _env_override(key: str, default: Any) -> Any:
    """Return env override with best-effort casting."""
    env_key = f"GENESIS_FLAG_{key.upper()}"
    raw = os.environ.get(env_key)
    if raw is None:
        return default

    lowered = raw.lower()
    if lowered in {"true", "1", "yes", "on"}:
        return True
    if lowered in {"false", "0", "no", "off"}:
        return False
    return raw


@dataclass
class RoutingFlags:
    safety_floor: float
    require_peer_review_above: float


@dataclass
class RiskThresholds:
    servant_prompt: int
    sovereign_prompt: int
    irreversible: int


@dataclass
class FeatureFlags:
    sovereign_mode_enabled: bool
    cluster_execution_enabled: bool
    genesis_network_enabled: bool
    autonomous_loop_enabled: bool
    cognitive_bridge_enabled: bool
    docker_enabled: bool
    peer_review_required: bool
    training_export_enabled: bool
    privacy_scrub_enabled: bool
    audit_log_enabled: bool
    kill_switch_armed: bool
    routing: RoutingFlags
    risk_thresholds: RiskThresholds
    control_plane: dict[str, Any]
    telemetry: dict[str, Any]

    @classmethod
    def load(cls, path: Path = _DEFAULT_FLAG_FILE) -> FeatureFlags:
        if not path.exists():
            raise FileNotFoundError(f"Feature flag file not found: {path}")

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        routing = data.get("routing", {})
        risk = data.get("risk_thresholds", {})

        return cls(
            sovereign_mode_enabled=_env_override(
                "sovereign_mode_enabled", data.get("sovereign_mode_enabled", False)
            ),
            cluster_execution_enabled=_env_override(
                "cluster_execution_enabled", data.get("cluster_execution_enabled", False)
            ),
            genesis_network_enabled=_env_override(
                "genesis_network_enabled", data.get("genesis_network_enabled", False)
            ),
            autonomous_loop_enabled=_env_override(
                "autonomous_loop_enabled", data.get("autonomous_loop_enabled", True)
            ),
            cognitive_bridge_enabled=_env_override(
                "cognitive_bridge_enabled", data.get("cognitive_bridge_enabled", False)
            ),
            docker_enabled=_env_override("docker_enabled", data.get("docker_enabled", False)),
            peer_review_required=_env_override(
                "peer_review_required", data.get("peer_review_required", True)
            ),
            training_export_enabled=_env_override(
                "training_export_enabled", data.get("training_export_enabled", True)
            ),
            privacy_scrub_enabled=_env_override(
                "privacy_scrub_enabled", data.get("privacy_scrub_enabled", True)
            ),
            audit_log_enabled=_env_override(
                "audit_log_enabled", data.get("audit_log_enabled", True)
            ),
            kill_switch_armed=_env_override(
                "kill_switch_armed", data.get("kill_switch_armed", True)
            ),
            routing=RoutingFlags(
                safety_floor=float(
                    _env_override("routing_safety_floor", routing.get("safety_floor", 0.6))
                ),
                require_peer_review_above=float(
                    _env_override(
                        "routing_require_peer_review_above",
                        routing.get("require_peer_review_above", 0.8),
                    )
                ),
            ),
            risk_thresholds=RiskThresholds(
                servant_prompt=int(
                    _env_override("risk_servant_prompt", risk.get("servant_prompt", 2))
                ),
                sovereign_prompt=int(
                    _env_override("risk_sovereign_prompt", risk.get("sovereign_prompt", 5))
                ),
                irreversible=int(_env_override("risk_irreversible", risk.get("irreversible", 5))),
            ),
            control_plane=data.get("control_plane", {}),
            telemetry=data.get("telemetry", {}),
        )


# Eagerly load flags once; lightweight and safe to import widely.
feature_flags = FeatureFlags.load()
