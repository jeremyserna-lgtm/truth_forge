"""Genesis Control Plane client and schemas.

This provides a minimal, authenticated client for talking to a central
control-plane API that owns task queues, audit ingestion, leases, and
kill-switch state. It is intentionally lightweight and can be swapped
for a real service later.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any

import requests
from requests import Response

from truth_forge.governance.feature_flags import feature_flags


class ControlPlaneError(RuntimeError):
    """Raised when control plane returns an error response."""


def _headers() -> dict[str, str]:
    api_key_env = feature_flags.control_plane.get("api_key_env", "GENESIS_CONTROL_PLANE_KEY")
    api_key = os.environ.get(api_key_env, "")
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _full_url(path: str) -> str:
    base = feature_flags.control_plane.get("base_url", "http://localhost:8788")
    return f"{base.rstrip('/')}{path}"


def _raise_for_status(resp: Response) -> None:
    if resp.status_code >= 400:
        raise ControlPlaneError(f"{resp.status_code}: {resp.text}")


@dataclass
class TaskRequest:
    task_id: str
    parent_id: str | None
    payload: dict[str, Any]
    ttl_seconds: int = 900
    idempotency_key: str | None = None

    def to_json(self) -> str:
        body = asdict(self)
        # drop None keys for cleanliness
        return json.dumps({k: v for k, v in body.items() if v is not None})


@dataclass
class LeaseRequest:
    task_id: str
    worker_id: str
    lease_seconds: int = 120

    def to_json(self) -> str:
        return json.dumps(asdict(self))


def enqueue_task(task: TaskRequest) -> dict[str, Any]:
    resp = requests.post(
        _full_url("/v1/tasks"), data=task.to_json(), headers=_headers(), timeout=10
    )
    _raise_for_status(resp)
    return resp.json()


def renew_lease(lease: LeaseRequest) -> dict[str, Any]:
    resp = requests.post(
        _full_url("/v1/tasks/lease"), data=lease.to_json(), headers=_headers(), timeout=10
    )
    _raise_for_status(resp)
    return resp.json()


def record_audit(event: dict[str, Any]) -> None:
    # fire-and-forget with short timeout; failures are logged but non-blocking
    try:
        resp = requests.post(
            _full_url("/v1/audit"), data=json.dumps(event), headers=_headers(), timeout=3
        )
        _raise_for_status(resp)
    except Exception:
        # Swallow errors; upstream callers should also write to local audit trail
        return


def heartbeat(worker_id: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = {"worker_id": worker_id, "timestamp": int(time.time()), "payload": payload or {}}
    resp = requests.post(
        _full_url("/v1/heartbeat"), data=json.dumps(body), headers=_headers(), timeout=5
    )
    _raise_for_status(resp)
    return resp.json()


def kill_switch_status() -> bool:
    try:
        resp = requests.get(_full_url("/v1/kill-switch"), headers=_headers(), timeout=3)
        if resp.status_code == 404:
            return False
        _raise_for_status(resp)
        data = resp.json()
        return bool(data.get("armed", False))
    except Exception:
        return False
