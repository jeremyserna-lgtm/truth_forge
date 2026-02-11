"""Risk-based prompting/permission logic shared by execution layers."""

from __future__ import annotations

from truth_forge.governance.feature_flags import feature_flags


def should_ask_permission(execution_mode: str, risk_level: int) -> bool:
    """
    Decide whether to prompt the user before executing an action.

    Args:
        execution_mode: servant | sovereign | discovery
        risk_level: integer 1-5 (5 = irreversible)
    """
    mode = execution_mode.lower()
    thresholds = feature_flags.risk_thresholds

    if mode == "discovery":
        return False
    if mode == "sovereign":
        return risk_level >= thresholds.sovereign_prompt
    # servant (default)
    return risk_level > thresholds.servant_prompt
