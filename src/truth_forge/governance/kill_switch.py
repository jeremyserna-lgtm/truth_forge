"""Kill switch utilities.

The kill switch can be armed in three ways (precedence highest to lowest):
1. Remote control-plane flag (/v1/kill-switch) if control plane reachable.
2. Local env var GENESIS_KILL_SWITCH=on/off
3. Feature flag default (genesis_feature_flags.yaml)
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from truth_forge.governance.control_plane import kill_switch_status
from truth_forge.governance.feature_flags import feature_flags


class KillSwitchError(RuntimeError):
    """Raised when kill switch is armed and execution must halt."""


@dataclass
class KillSwitchState:
    armed: bool
    source: str


def _env_armed() -> bool | None:
    raw = os.environ.get("GENESIS_KILL_SWITCH")
    if raw is None:
        return None
    return raw.lower() in {"1", "true", "on", "armed", "yes"}


def current_state() -> KillSwitchState:
    env = _env_armed()
    if env is not None:
        return KillSwitchState(armed=env, source="env")

    remote = kill_switch_status()
    if remote:
        return KillSwitchState(armed=True, source="control_plane")

    return KillSwitchState(armed=bool(feature_flags.kill_switch_armed), source="feature_flag")


def assert_not_armed() -> None:
    state = current_state()
    if state.armed:
        raise KillSwitchError(f"Kill switch engaged via {state.source}; aborting execution.")
