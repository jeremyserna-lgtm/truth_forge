"""Bootstrap runtime checks for triad takeover readiness.

This module defines a practical "bootstrap moment" contract:
- Scout on MLX (or configured local endpoint)
- Maverick endpoint online
- R1/DeepSeek endpoint online
- EXO service reachable
- Filesystem/code execution path available
- Vision stack importable
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from truth_forge.gateway.providers.maverick import MaverickProvider
from truth_forge.gateway.providers.r1 import R1Provider
from truth_forge.gateway.providers.scout import ScoutProvider
from truth_forge.gateway.types import CompletionRequest


def _probe_models_endpoint(base_url: str, timeout: float = 5.0) -> dict[str, Any]:
    """Probe an OpenAI-compatible /models endpoint."""
    url = f"{base_url.rstrip('/')}/models"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        models = [m.get("id", "") for m in data.get("data", []) if isinstance(m, dict)]
        return {
            "available": True,
            "url": url,
            "models": models,
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - defensive for varied local env errors
        return {
            "available": False,
            "url": url,
            "models": [],
            "error": str(exc),
        }


def _resolve_endpoints() -> dict[str, str]:
    """Resolve runtime endpoints from config/env with local defaults."""
    config_path = os.environ.get("COGNITIVE_BRIDGE_CONFIG")
    if not config_path:
        config_path = str(
            Path(__file__).resolve().parents[2] / "config" / "base" / "cognitive_bridge_config.json"
        )

    config_models: dict[str, dict[str, Any]] = {}
    try:
        with Path(config_path).open("r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        config_models = cfg.get("models", {})
    except Exception:
        config_models = {}

    scout_cfg = config_models.get("scout", {}).get("endpoint", "http://localhost:8765/v1")
    maverick_cfg = config_models.get("maverick", {}).get("endpoint", "http://localhost:8766/v1")
    r1_cfg = config_models.get("r1", {}).get("endpoint", "http://localhost:8767/v1")

    return {
        "scout": os.environ.get("SCOUT_BASE_URL", scout_cfg),
        "maverick": os.environ.get("MAVERICK_BASE_URL", maverick_cfg),
        "r1": os.environ.get("R1_BASE_URL", r1_cfg),
        "exo": os.environ.get("EXO_BASE_URL", "http://localhost:8000"),
        "ollama": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        "genesis_api": os.environ.get("GENESIS_API_BASE_URL", "http://localhost:3141"),
    }


def _check_filesystem_exec() -> dict[str, Any]:
    """Validate command execution and filesystem write/read path."""
    with tempfile.TemporaryDirectory(prefix="genesis_bootstrap_") as tmpdir:
        proc = subprocess.run(
            ["bash", "-lc", "echo bootstrap_ok > tf_bootstrap.txt && cat tf_bootstrap.txt"],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=20,
        )
    ok = proc.returncode == 0 and "bootstrap_ok" in proc.stdout
    return {
        "available": ok,
        "exit_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }


def _check_vision_stack() -> dict[str, Any]:
    """Validate local vision/image stack dependencies."""
    try:
        import PIL

        return {
            "available": True,
            "library": "Pillow",
            "version": getattr(PIL, "__version__", "unknown"),
        }
    except Exception as exc:
        return {"available": False, "library": "Pillow", "error": str(exc)}


def _dir_size_bytes(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for file_name in files:
            try:
                total += (Path(root) / file_name).stat().st_size
            except FileNotFoundError:
                continue
    return total


def _to_readiness_dict() -> dict[str, dict[str, Any]]:
    """Check local cache readiness without importing services package."""
    hf_cache = Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface" / "hub"))
    models = {
        "scout": (
            hf_cache / "models--mlx-community--Llama-4-Scout-17B-16E-Instruct-8bit",
            100.0,
        ),
        "maverick": (
            hf_cache / "models--mlx-community--Llama-4-Maverick-17B-128E-Instruct-4bit",
            260.0,
        ),
        "r1": (
            hf_cache / "models--mlx-community--DeepSeek-R1-4bit",
            400.0,
        ),
    }

    readiness: dict[str, dict[str, Any]] = {}
    for name, (path, expected_gb) in models.items():
        size_gb = round((_dir_size_bytes(path) / (1024**3)) if path.exists() else 0.0, 2)
        ready = size_gb >= expected_gb * 0.9
        readiness[name] = {
            "path": str(path),
            "size_gb": size_gb,
            "expected_gb": expected_gb,
            "ready": ready,
        }
    return readiness


def _probe_exo(base_url: str) -> dict[str, Any]:
    """Probe EXO service status using OpenAI-compatible /v1/models."""
    url = f"{base_url.rstrip('/')}/v1/models"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=2.0):
            pass
        available = True
    except Exception:
        available = False
    return {
        "endpoint": base_url,
        "available": available,
        "workers": {},
        "soldier_count": 3,
    }


def _probe_support_endpoint(base_url: str, endpoint: str, timeout: float = 2.0) -> dict[str, Any]:
    """Probe one-app support endpoints exposed by genesis-console backend."""
    url = f"{base_url.rstrip('/')}{endpoint}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
            status_code = getattr(resp, "status", 200)
        return {
            "available": True,
            "url": url,
            "status_code": status_code,
            "payload_preview": list(payload.keys()) if isinstance(payload, dict) else [],
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - varied local env behavior
        return {
            "available": False,
            "url": url,
            "status_code": None,
            "payload_preview": [],
            "error": str(exc),
        }


def _build_next_actions(report: dict[str, Any]) -> list[str]:
    """Generate actionable next steps from current runtime status."""
    actions: list[str] = []
    services = report["services"]
    capabilities = report["capabilities"]

    if not services["scout_mlx"]["available"]:
        actions.append("Start Scout MLX endpoint and set SCOUT_BASE_URL to its /v1 URL.")
    if not services["maverick"]["available"]:
        actions.append("Start Maverick endpoint and set MAVERICK_BASE_URL.")
    if not services["r1"]["available"]:
        actions.append("Start DeepSeek R1 endpoint and set R1_BASE_URL.")
    if not services["exo"]["available"]:
        actions.append("Start EXO service and confirm EXO_BASE_URL reaches /v1/models.")
    if not services["handover_support"]["available"]:
        actions.append(
            "Start genesis-console backend and expose /api/handover/readiness for takeover support."
        )
    if not services["sentinel"]["available"]:
        actions.append("Expose /api/sentinel/status for continuity sentinel monitoring.")
    if not services["recursive_synthesis"]["available"]:
        actions.append(
            "Expose /api/synthesis/recursive/health for recursive synthesis protocol checks."
        )
    if not capabilities["filesystem_exec"]["available"]:
        actions.append("Fix local execution path before autonomous code operations.")
    if not capabilities["vision_stack"]["available"]:
        actions.append("Install/repair Pillow for image and screenshot processing.")
    if not actions:
        actions.append("Bootstrap threshold reached. Enable smoke tests with '--smoke'.")
    return actions


def _run_smoke(endpoints: dict[str, str], timeout_tokens: int = 24) -> dict[str, Any]:
    """Run minimal inference calls against triad providers."""
    smoke: dict[str, Any] = {}

    checks = [
        ("scout", ScoutProvider(base_url=endpoints["scout"]), "scout-genesis"),
        ("maverick", MaverickProvider(base_url=endpoints["maverick"]), "maverick-genesis"),
        ("r1", R1Provider(base_url=endpoints["r1"]), "r1-genesis"),
    ]

    for name, provider, model in checks:
        if not provider.is_available():
            smoke[name] = {"ok": False, "error": "provider unavailable"}
            continue
        try:
            response = provider.complete(
                CompletionRequest(
                    prompt=f"Reply with READY:{name.upper()} only.",
                    model=model,
                    max_tokens=timeout_tokens,
                    temperature=0.0,
                )
            )
            smoke[name] = {
                "ok": True,
                "content_preview": response.content[:80],
                "latency_ms": round(response.latency_ms, 1),
            }
        except Exception as exc:  # pragma: no cover - defensive in varied local envs
            smoke[name] = {"ok": False, "error": str(exc)}

    return smoke


def collect_bootstrap_runtime(smoke: bool = False) -> dict[str, Any]:
    """Collect full bootstrap readiness report for Scout/Maverick/R1 + EXO + MLX."""
    endpoints = _resolve_endpoints()

    services = {
        "scout_mlx": _probe_models_endpoint(endpoints["scout"]),
        "maverick": _probe_models_endpoint(endpoints["maverick"]),
        "r1": _probe_models_endpoint(endpoints["r1"]),
        "ollama": _probe_models_endpoint(endpoints["ollama"]),
        "exo": _probe_exo(endpoints["exo"]),
        "handover_support": _probe_support_endpoint(
            endpoints["genesis_api"], "/api/handover/readiness"
        ),
        "sentinel": _probe_support_endpoint(endpoints["genesis_api"], "/api/sentinel/status"),
        "recursive_synthesis": _probe_support_endpoint(
            endpoints["genesis_api"], "/api/synthesis/recursive/health"
        ),
    }

    capabilities = {
        "filesystem_exec": _check_filesystem_exec(),
        "vision_stack": _check_vision_stack(),
    }

    readiness = _to_readiness_dict()

    triad_online = (
        services["scout_mlx"]["available"]
        and services["maverick"]["available"]
        and services["r1"]["available"]
    )

    report: dict[str, Any] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "endpoints": endpoints,
        "services": services,
        "readiness": readiness,
        "capabilities": {
            **capabilities,
            "triad_online": triad_online,
            "exo_online": bool(services["exo"].get("available", False)),
            "mlx_online": bool(services["scout_mlx"]["available"]),
            "handover_support_stack": bool(services["handover_support"]["available"]),
            "continuity_sentinel_stack": bool(services["sentinel"]["available"]),
            "recursive_synthesis_stack": bool(services["recursive_synthesis"]["available"]),
            "takeover_ready": triad_online
            and bool(services["exo"].get("available", False))
            and bool(services["handover_support"]["available"])
            and capabilities["filesystem_exec"]["available"]
            and capabilities["vision_stack"]["available"],
        },
    }

    if smoke:
        report["smoke"] = _run_smoke(endpoints)

    report["next_actions"] = _build_next_actions(report)
    return report


__all__ = ["collect_bootstrap_runtime"]
