# Cluster Execution Guide (Docker-free)

Status (2026-02-06):
- Tool: `src/truth_forge/services/cluster_execution_tool.py` (local execution, denylist, timeout, per-task temp workdir)
- Orchestrator: `exec` operation wired to cluster tool (feature flags: `cluster_execution_enabled=true`, `docker_enabled=false`)
- Tests: `tests/unit/services/test_cluster_execution_tool.py` (passing)
- SSH path scaffolded (user/port/key); remote exec creates per-run `/tmp/genesis_exec_*` dirs
- Streaming supported (local + SSH) with session isolation; env injection; dry-run mode; node selection (`node=any` picks preferred list)
- Resource limits wrapper (CPU seconds, virtual memory KB) applied via `ulimit` for local exec
- Remote path now applies `ulimit` as well; peer-review gate enforced for high-risk ops via orchestrator
- ClusterStateMonitor stub present; `node=any` can use it to pick least-loaded (placeholder logic)
- Orchestrator exposes `cluster_status` operation returning node reachability/load + model readiness

Design:
- No Docker fallback. Fail fast if cluster unreachable.
- SSH scaffold exists but not enabled yet (native/local only in this env).
- Denylist guard blocks destructive commands; configurable per instance.
- Future: short-lived SSH certs per task; per-node selection; streaming logs.

Usage (local):
```python
from truth_forge.services.cluster_execution_tool import ClusterExecutionTool
tool = ClusterExecutionTool()
res = tool.execute("echo hi", language="bash")
```

Or via orchestrator:
```python
from truth_forge.services.orchestrator import get_orchestrator
orch = get_orchestrator()
res = orch.process("exec", command="echo hi", language="bash")
```

Next Steps:
1) Integrate load-aware node selection and health checks (via cluster_state once built).
2) Enforce resource limits on SSH path (cgroups/ulimit remote) and stream logs over WebSocket.
3) Wire EXO-aware routing for large memory tasks.
4) Replace denylist with policy-backed allowlist and risk tagging.
