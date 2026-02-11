# Genesis Governance / Safety Additions (2026-02-06)

Scope implemented in truth_forge:

- **Feature flags** (`config/base/genesis_feature_flags.yaml`) with env overrides `GENESIS_FLAG_*`.
- **Control plane client** (`src/truth_forge/governance/control_plane.py`):
  - `/v1/tasks` enqueue with idempotency key
  - `/v1/tasks/lease` renewals
  - `/v1/audit` fan-out (non-blocking)
  - `/v1/kill-switch` status
- **Kill switch** (`governance/kill_switch.py`):
  - Sources: env `GENESIS_KILL_SWITCH`, control-plane flag, feature flag default.
  - `assert_not_armed()` raises `KillSwitchEngaged`.
- **Peer review scaffold** (`governance/peer_review.py`):
  - Model-agnostic consensus wrapper; pluggable voters.
- **Privacy scrub** (`governance/privacy.py`):
  - Redacts email/phone/SSN in text or message lists.
- **Risk gate helper** (`governance/risk_gate.py`):
  - Permission logic for servant/sovereign/discovery with thresholds from flags.
- **Autonomous loop** (`services/autonomous_loop.py`):
  - Runs continuously when enabled, polling control-plane heartbeats for tasks; otherwise cycles health→explore to avoid idle.
  - Governed by kill switch and feature flag `autonomous_loop_enabled` (default: on).
- **Cognitive Bridge** (`services/cognitive_bridge.py`):
  - Config-driven routing (scout/maverick/r1) with fallback chain and context-aware override
  - Uses `config/base/cognitive_bridge_config.json` (updated endpoints: Scout :8765, Maverick :8766, R1 :8767)
  - Maverick provider available; R1 provider present but will fall back until download completes
- **Exports** wired via `governance/__init__.py` for easy imports.

Recommended wiring (next steps):
1. Call `assert_not_armed()` at the start of any execution tool and before distributed dispatch.
2. Wrap high-risk tool results with `verify_claim` when `feature_flags.peer_review_required` is True or when safety score < `routing.require_peer_review_above`.
3. Run user-/model-facing text through `scrub_text`/`scrub_messages` before export to training or logs when `privacy_scrub_enabled` is True.
4. Use `should_ask_permission(mode, risk_level)` to gate prompts in UI/CLI.
5. Send every audit event both to local `AuditTrail` and `control_plane.record_audit` (best-effort).
6. Keep `autonomous_loop_enabled` on in prod; kill switch remains the only stop mechanism.

Flag defaults are conservative (sovereign/network/cluster disabled; kill switch default off). Override via env for rollout:
```
export GENESIS_FLAG_SOVEREIGN_MODE_ENABLED=true
export GENESIS_KILL_SWITCH=off
```
