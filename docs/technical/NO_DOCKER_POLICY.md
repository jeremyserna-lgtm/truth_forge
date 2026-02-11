# No-Docker Policy for Genesis Execution

Effective: 2026-02-06

Rationale:
- Docker sandboxes add overhead, block EXO unified memory, and obscure telemetry.
- Genesis runs on trusted Mac cluster; isolation handled via SSH workdirs + guards.

Policy:
1) Docker execution is disabled (`docker_enabled: false` in feature flags).
2) Execution layer must use native/SSH cluster execution only.
3) Do not add Docker fallbacks in new tools. Remove legacy Docker references during migrations.
4) If cluster unreachable, fail fast and surface error; do not silently revert to Docker.

Action items:
- Implement `cluster_execution_tool.py` for native SSH execution (pending).
- Remove any remaining Docker references in plans/scripts as migrations proceed.
