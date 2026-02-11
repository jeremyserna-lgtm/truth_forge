"""Autonomous loop runner that keeps the agent doing work continuously.

The loop:
- Respects kill switch (bails if armed)
- Sends heartbeat to control plane (may return tasks)
- Executes any returned tasks; if none, runs an exploratory fallback
- Never idles; waits a small interval between iterations
"""

from __future__ import annotations

import threading
import time
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from truth_forge.governance import (
    KillSwitchError,
    assert_not_armed,
    feature_flags,
    heartbeat,
)
from truth_forge.services.cluster_execution_tool import ClusterExecutionTool
from truth_forge.services.sensors import collect_presence
from truth_forge.services.shadow_missions import ShadowState, run_shadow_suite


if TYPE_CHECKING:
    from truth_forge.services.orchestrator import Orchestrator


class AutonomousLoop:
    """Simple autonomous execution loop."""

    def __init__(
        self,
        orchestrator: Orchestrator,
        worker_id: str = "genesis-king",
        poll_interval: float = 5.0,
    ) -> None:
        self.orchestrator = orchestrator
        self.worker_id = worker_id
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._fallback_ops: Iterable[tuple[str, dict[str, Any]]] = [
            ("health_check", {}),
            ("explore", {"iterations": 1, "depth": "shallow"}),
        ]
        self._shadow_state = ShadowState()
        self._exec_tool = ClusterExecutionTool()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        fallback_iter = iter(self._fallback_ops)
        while not self._stop.is_set():
            try:
                assert_not_armed()
                presence = collect_presence()
                # Heartbeat and optional task poll
                hb = heartbeat(
                    self.worker_id,
                    {"mode": self.orchestrator.execution_mode, "presence": presence},
                )
                tasks = hb.get("tasks", []) if isinstance(hb, dict) else []

                if tasks:
                    for task in tasks:
                        op = task.get("operation")
                        params = task.get("params", {})
                        if op:
                            self.orchestrator.process(op, **params)
                else:
                    # Run next fallback operation (cycles)
                    try:
                        op, params = next(fallback_iter)
                    except StopIteration:
                        fallback_iter = iter(self._fallback_ops)
                        op, params = next(fallback_iter)

                    # If night hours (0-5 local), prefer night_watch
                    if presence.get("local_hour") is not None and 0 <= presence["local_hour"] <= 5:
                        op, params = "night_watch", {}

                    self.orchestrator.process(op, **params)

                    # Nightly shadow missions (once per day, night hours only)
                    if (
                        0 <= presence.get("local_hour", 24) <= 5
                        and self._shadow_state.should_run_today()
                    ):
                        shadow = run_shadow_suite(self.orchestrator, self._exec_tool)
                        self.orchestrator.governance.audit_trail.record(
                            operation="shadow_missions",
                            component="autonomous_loop",
                            category=None,
                            level=None,
                            context=shadow,
                        )

            except KillSwitchError:
                # stop loop if kill switch triggers
                break
            except Exception:
                # Swallow errors to keep going
                pass

            time.sleep(self.poll_interval)


def ensure_autonomous_loop(orchestrator: Orchestrator) -> None:
    """Start autonomous loop if enabled by feature flags."""
    if not feature_flags.autonomous_loop_enabled:
        return
    loop = AutonomousLoop(orchestrator=orchestrator)
    loop.start()
    # Keep reference on orchestrator to prevent GC
    orchestrator.autonomous_loop = loop
