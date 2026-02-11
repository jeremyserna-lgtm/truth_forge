"""ClusterStateMonitor - health cache for nodes/models."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field

from truth_forge.services.model_readiness import check_readiness


@dataclass
class NodeState:
    name: str
    healthy: bool
    last_checked: float
    metadata: dict = field(default_factory=dict)


class ClusterStateMonitor:
    def __init__(self, ttl: float = 30.0, nodes: list[str] | None = None) -> None:
        self.ttl = ttl
        self.nodes = nodes or ["king"]
        self._cache: dict[str, NodeState] = {}

    def _ssh_check(self, node: str) -> bool:
        try:
            result = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=2", node, "echo ok"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _loadavg(self, node: str) -> float | None:
        try:
            result = subprocess.run(
                ["ssh", "-o", "BatchMode=yes", node, "cat /proc/loadavg | awk '{print $1}'"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if result.returncode == 0:
                return float(result.stdout.strip().split()[0])
        except Exception:
            return None
        return None

    def get_available_nodes(self) -> list[NodeState]:
        now = time.time()
        if self._cache and (now - next(iter(self._cache.values())).last_checked) < self.ttl:
            return list(self._cache.values())

        readiness = check_readiness()
        states: list[NodeState] = []
        for node in self.nodes:
            reachable = self._ssh_check(node)
            load = self._loadavg(node) if reachable else None
            # consider node healthy if reachable and Scout ready
            healthy = reachable and readiness.get("scout", None) and readiness["scout"].ready
            states.append(
                NodeState(
                    name=node,
                    healthy=bool(healthy),
                    last_checked=now,
                    metadata={
                        "reachable": reachable,
                        "load": load,
                        "models": {k: v.ready for k, v in readiness.items()},
                    },
                )
            )

        self._cache = {s.name: s for s in states}
        return states

    def pick_least_loaded(self) -> str:
        states = self.get_available_nodes()
        healthy = [s for s in states if s.healthy]
        if not healthy:
            return "king"
        # sort by load if available, else preserve order
        healthy_with_load = [s for s in healthy if s.metadata.get("load") is not None]
        if healthy_with_load:
            healthy_with_load.sort(key=lambda s: s.metadata.get("load", 0))
            return healthy_with_load[0].name
        return healthy[0].name
