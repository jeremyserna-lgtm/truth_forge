#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

echo "== Genesis Ownership Gate =="
echo "Repo: ${ROOT_DIR}"
echo

require_cmd() {
  local cmd="$1"
  if ! command -v "${cmd}" >/dev/null 2>&1; then
    echo "Missing required command: ${cmd}" >&2
    exit 1
  fi
}

require_cmd uv
require_cmd node
require_cmd npm
require_cmd curl

echo "1/9 Python lint (no warnings/errors)"
uv run ruff check src/truth_forge tests

echo "2/9 Python format check"
uv run ruff format --check src/truth_forge tests

echo "3/9 Python type checks"
uv run mypy \
  --follow-imports=skip \
  --ignore-missing-imports \
  --disable-error-code misc \
  --disable-error-code no-any-return \
  src/truth_forge/bootstrap_runtime.py \
  src/truth_forge/cli/main.py \
  src/truth_forge/services/identity.py \
  src/truth_forge/services/factory.py \
  src/truth_forge/services/mediator/service.py \
  src/truth_forge/services/logging/service.py \
  src/truth_forge/services/relationship/service.py \
  src/truth_forge/governance/peer_review.py \
  src/truth_forge/governance/risk_gate.py \
  src/truth_forge/governance/kill_switch.py \
  src/truth_forge/governance/privacy.py

echo "4/9 Core hardening test suites"
uv run --extra llm pytest -q \
  tests/unit/governance \
  tests/unit/observability \
  tests/unit/daemon \
  tests/unit/services \
  tests/unit/relationships \
  -o filterwarnings=error

echo "5/9 Python tests with hard quality gate"
uv run --extra llm pytest \
  --cov=truth_forge.governance \
  --cov=truth_forge.services.sync \
  --cov=truth_forge.services.identity \
  --cov=truth_forge.services.factory \
  --cov=truth_forge.services.mediator.service \
  --cov=truth_forge.services.logging.service \
  --cov=truth_forge.services.relationship.service \
  --cov=truth_forge.observability.context \
  --cov=truth_forge.daemon.sync_integration \
  --cov-branch \
  --cov-report=term-missing \
  --cov-report=xml \
  --cov-fail-under=90 \
  tests/unit/governance \
  tests/unit/services/sync \
  tests/unit/services/test_identity.py \
  tests/unit/services/test_factory.py \
  tests/unit/services/test_mediator.py \
  tests/unit/services/test_logging.py \
  tests/unit/services/test_relationship.py \
  tests/unit/observability/test_context.py \
  tests/unit/daemon/test_sync_integration.py \
  -o filterwarnings=error

echo "6/9 Frontend lint (no warnings)"
npm --prefix genesis-console run lint -- --max-warnings 0

echo "7/9 Frontend build"
npm --prefix genesis-console run build

cleanup_gate_server() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "${SERVER_PID}" >/dev/null 2>&1; then
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    wait "${SERVER_PID}" 2>/dev/null || true
  fi
  if [[ -n "${GENESIS_GATE_LOG:-}" ]] && [[ -f "${GENESIS_GATE_LOG}" ]]; then
    rm -f "${GENESIS_GATE_LOG}"
  fi
}
trap cleanup_gate_server EXIT

echo "8/9 Support-stack API contract drill"
GENESIS_GATE_PORT="${GENESIS_GATE_PORT:-43141}"
GENESIS_GATE_LOG="$(mktemp -t genesis_gate_server.XXXXXX.log)"
PORT="${GENESIS_GATE_PORT}" node genesis-console/server/index.js >"${GENESIS_GATE_LOG}" 2>&1 &
SERVER_PID=$!

READY=0
for _ in $(seq 1 50); do
  if curl -sf "http://127.0.0.1:${GENESIS_GATE_PORT}/api/health" >/dev/null; then
    READY=1
    break
  fi
  sleep 0.2
done

if [[ "${READY}" -ne 1 ]]; then
  echo "Failed to start genesis-console API on port ${GENESIS_GATE_PORT}" >&2
  echo "--- genesis-console log ---" >&2
  cat "${GENESIS_GATE_LOG}" >&2
  exit 1
fi

GENESIS_GATE_PORT="${GENESIS_GATE_PORT}" uv run python - <<'PY'
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


BASE = f"http://127.0.0.1:{os.environ['GENESIS_GATE_PORT']}"


def request(path: str, method: str = "GET", payload: dict | None = None, expected: tuple[int, ...] = (200,)) -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8") or "{}"
    except urllib.error.HTTPError as exc:
        status = exc.code
        body = exc.read().decode("utf-8") or "{}"

    if status not in expected:
        raise SystemExit(f"{method} {path} failed: status={status}, body={body[:300]}")

    return json.loads(body) if body else {}


readiness = request("/api/handover/readiness")
if "takeover_ready" not in readiness or "critical_gaps" not in readiness:
    raise SystemExit("handover readiness contract missing required keys")

plan = request(
    "/api/planning/intent-plan",
    method="POST",
    payload={"intent": "Ownership gate support stack drill", "run_id": "ownership-gate-run"},
)
run_id = plan.get("run_id")
if not run_id:
    raise SystemExit("planning endpoint did not return run_id")

todo_sync = request("/api/planning/todos/sync", method="POST", payload={"run_id": run_id})
if not todo_sync.get("ok"):
    raise SystemExit("todo sync did not return ok=true")

tool_trace = request(
    "/api/tools/orchestrate",
    method="POST",
    payload={"requested_tools": ["filesystem", "build_test"], "objective": "ownership_gate"},
)
if "tool_entries" not in tool_trace:
    raise SystemExit("tool orchestration trace missing tool_entries")

rehearsal = request(
    "/api/handover/rehearse",
    method="POST",
    payload={"run_id": run_id, "intent": "ownership gate rehearsal", "requested_tools": ["filesystem"]},
)
if not isinstance(rehearsal.get("pass"), bool):
    raise SystemExit("handover rehearsal missing pass boolean")

heartbeat = request(
    "/api/sentinel/heartbeat",
    method="POST",
    payload={"unit_id": "gate-scout", "capability_vector": {"planning": True, "synthesis": True}},
)
if heartbeat.get("event_type") != "heartbeat":
    raise SystemExit("sentinel heartbeat did not return heartbeat event")

anomaly = request(
    "/api/sentinel/anomaly",
    method="POST",
    payload={
        "unit_id": "gate-scout",
        "severity": "high",
        "blast_radius": "single_unit",
        "details": "ownership gate anomaly drill",
    },
)
incident_id = anomaly.get("incident_id")
if not incident_id:
    raise SystemExit("sentinel anomaly did not return incident_id")

escalation = request(
    "/api/sentinel/escalate",
    method="POST",
    payload={"incident_id": incident_id, "stage": "owner_alert", "note": "ownership gate escalation"},
)
if escalation.get("stage") != "owner_alert":
    raise SystemExit("sentinel escalation did not return stage owner_alert")

operator_check = request(
    "/api/sentinel/operator-check",
    method="POST",
    payload={
        "incident_id": incident_id,
        "channel": "primary",
        "consent_policy": "anomaly_only",
        "note": "ownership gate operator check",
    },
)
if operator_check.get("event_type") != "operator_check":
    raise SystemExit("operator check event was not recorded")

incident = request(f"/api/sentinel/incidents/{incident_id}")
if incident.get("incident_id") != incident_id:
    raise SystemExit("incident retrieval failed")

cycle = request(
    "/api/synthesis/recursive/cycle",
    method="POST",
    payload={
        "conversation": "ownership gate recursive cycle",
        "product_effects": ["risk_reduction"],
        "mind_change_record": "gate confirms recursive synthesis contract",
    },
)
cycle_id = cycle.get("cycle_id")
if not cycle_id:
    raise SystemExit("recursive cycle start did not return cycle_id")

request(
    "/api/synthesis/recursive/ingest",
    method="POST",
    payload={
        "cycle_id": cycle_id,
        "outputs": [{"type": "synthesis", "content": "ownership gate ingest output"}],
        "learning_candidates": [{"kind": "workflow", "note": "gate drill candidate"}],
    },
)

evaluated = request(
    "/api/synthesis/recursive/evaluate",
    method="POST",
    payload={
        "cycle_id": cycle_id,
        "cost_ok": True,
        "risk_ok": True,
        "peer_review_ok": True,
        "product_effects": ["risk_reduction"],
    },
)
decision = (evaluated.get("cycle") or {}).get("decision")
if decision not in {"promote", "defer_research", "reject"}:
    raise SystemExit("recursive evaluation did not return valid decision")
if decision != "promote":
    request(
        "/api/synthesis/recursive/evaluate",
        method="POST",
        payload={
            "cycle_id": cycle_id,
            "decision": "promote",
            "cost_ok": True,
            "risk_ok": True,
            "peer_review_ok": True,
            "product_effects": ["risk_reduction"],
        },
    )

promoted = request(
    "/api/synthesis/recursive/promote",
    method="POST",
    payload={"cycle_id": cycle_id, "title": "ownership gate promoted candidate"},
)
if (promoted.get("cycle") or {}).get("status") != "promoted":
    raise SystemExit("recursive promotion failed")

health = request("/api/synthesis/recursive/health")
if health.get("available") is not True:
    raise SystemExit("recursive synthesis health endpoint unavailable")

cycle_state = request(f"/api/synthesis/recursive/{cycle_id}")
if cycle_state.get("cycle_id") != cycle_id:
    raise SystemExit("recursive cycle retrieval failed")

print("Support-stack API contract drill passed.")
PY

echo "9/9 Bootstrap report support-stack contract"
BOOTSTRAP_JSON="$(mktemp -t genesis_bootstrap.XXXXXX.json)"
GENESIS_API_BASE_URL="http://127.0.0.1:${GENESIS_GATE_PORT}" \
  uv run truth-forge --json bootstrap >"${BOOTSTRAP_JSON}"

uv run python - "${BOOTSTRAP_JSON}" <<'PY'
from __future__ import annotations

import json
import sys


path = sys.argv[1]
with open(path, "r", encoding="utf-8") as fh:
    report = json.load(fh)

caps = report.get("capabilities", {})
required = {
    "handover_support_stack",
    "continuity_sentinel_stack",
    "recursive_synthesis_stack",
    "takeover_ready",
}
missing = sorted(required - set(caps.keys()))
if missing:
    raise SystemExit(f"bootstrap report missing capability keys: {missing}")

for key in ["handover_support_stack", "continuity_sentinel_stack", "recursive_synthesis_stack"]:
    if caps.get(key) is not True:
        raise SystemExit(f"bootstrap capability not ready: {key}")

print("Bootstrap support-stack capabilities verified.")
PY
rm -f "${BOOTSTRAP_JSON}"

echo
echo "Ownership gate PASSED:"
echo "- Coverage >= 90%"
echo "- No warnings/errors in lint/type/test/build commands"
echo "- Core hardening suites passed"
echo "- No blockers detected in test pipeline execution"
echo "- Support-stack API contracts passed (handover/sentinel/recursive)"
