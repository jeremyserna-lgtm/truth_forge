"""Shadow Missions - autonomous self-tests to ensure the stack keeps working.

These run without user prompts, exercising:
- Model routing (Scout/Maverick fallback)
- Code execution path (cluster_execution_tool, local)
- Memory/telemetry surface (audit via orchestrator)
"""

from __future__ import annotations

import time
from datetime import date
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from truth_forge.services.cluster_execution_tool import ClusterExecutionTool
    from truth_forge.services.orchestrator import Orchestrator


class ShadowState:
    """Tracks last run date to avoid spamming tests."""

    def __init__(self) -> None:
        self.last_run: date | None = None

    def should_run_today(self) -> bool:
        today = date.today()
        if self.last_run == today:
            return False
        self.last_run = today
        return True


def run_shadow_suite(
    orchestrator: Orchestrator,
    exec_tool: ClusterExecutionTool,
) -> dict[str, Any]:
    """Execute a small battery of self-tests.

    Returns:
        Summary dict with results.
    """
    results: dict[str, Any] = {"ts": time.time(), "steps": []}

    # 1) Routing smoke test (simple prompt)
    try:
        res = orchestrator.process(
            "complete", prompt="Say 'shadow-ok' in one word.", task_type="auto"
        )
        ok = res.success and "shadow" in (res.content or "")
        results["steps"].append({"name": "routing_complete", "success": ok, "detail": res.error})
    except Exception as e:
        results["steps"].append({"name": "routing_complete", "success": False, "detail": str(e)})

    # 2) Code execution smoke test (local)
    try:
        exec_res = exec_tool.execute("echo shadow-exec")
        ok = exec_res.exit_code == 0 and "shadow-exec" in exec_res.stdout
        results["steps"].append({"name": "code_exec", "success": ok, "detail": exec_res.stderr})
    except Exception as e:
        results["steps"].append({"name": "code_exec", "success": False, "detail": str(e)})

    # 3) Health check
    try:
        health = orchestrator.health_check()
        ok = health.get("status") == "healthy"
        results["steps"].append({"name": "health_check", "success": ok, "detail": health})
    except Exception as e:
        results["steps"].append({"name": "health_check", "success": False, "detail": str(e)})

    results["all_passed"] = all(step["success"] for step in results["steps"])
    return results
