"""Tests for bootstrap runtime readiness reporting."""

from __future__ import annotations

import truth_forge.bootstrap_runtime as mod


def test_collect_bootstrap_runtime_shape(monkeypatch) -> None:
    """collect_bootstrap_runtime returns required top-level sections."""
    monkeypatch.setattr(
        mod,
        "_resolve_endpoints",
        lambda: {
            "scout": "http://localhost:8765/v1",
            "maverick": "http://localhost:8766/v1",
            "r1": "http://localhost:8767/v1",
            "exo": "http://localhost:8000",
            "ollama": "http://localhost:11434/v1",
            "genesis_api": "http://localhost:3141",
        },
    )
    monkeypatch.setattr(
        mod, "_probe_models_endpoint", lambda _url: {"available": True, "models": []}
    )
    monkeypatch.setattr(mod, "_check_filesystem_exec", lambda: {"available": True})
    monkeypatch.setattr(mod, "_check_vision_stack", lambda: {"available": True})
    monkeypatch.setattr(mod, "_to_readiness_dict", lambda: {"scout": {"ready": True}})
    monkeypatch.setattr(mod, "_build_next_actions", lambda _r: ["ok"])

    monkeypatch.setattr(mod, "_probe_exo", lambda _url: {"available": True, "workers": {}})
    monkeypatch.setattr(
        mod,
        "_probe_support_endpoint",
        lambda _base, _endpoint: {"available": True, "url": "mock"},
    )

    report = mod.collect_bootstrap_runtime(smoke=False)
    assert "timestamp" in report
    assert "services" in report
    assert "capabilities" in report
    assert report["capabilities"]["takeover_ready"] is True
    assert report["capabilities"]["handover_support_stack"] is True


def test_collect_bootstrap_runtime_generates_actions_for_missing_services(monkeypatch) -> None:
    """Next actions should request triad bring-up when services are offline."""
    monkeypatch.setattr(
        mod,
        "_resolve_endpoints",
        lambda: {
            "scout": "http://localhost:8765/v1",
            "maverick": "http://localhost:8766/v1",
            "r1": "http://localhost:8767/v1",
            "exo": "http://localhost:8000",
            "ollama": "http://localhost:11434/v1",
            "genesis_api": "http://localhost:3141",
        },
    )

    def _probe(url: str) -> dict:
        if "8765" in url:
            return {"available": False, "models": [], "error": "down"}
        return {"available": True, "models": []}

    monkeypatch.setattr(mod, "_probe_models_endpoint", _probe)
    monkeypatch.setattr(mod, "_check_filesystem_exec", lambda: {"available": True})
    monkeypatch.setattr(mod, "_check_vision_stack", lambda: {"available": True})
    monkeypatch.setattr(mod, "_to_readiness_dict", lambda: {})
    monkeypatch.setattr(mod, "_probe_exo", lambda _url: {"available": True, "workers": {}})
    monkeypatch.setattr(
        mod,
        "_probe_support_endpoint",
        lambda _base, _endpoint: {"available": True, "url": "mock"},
    )

    report = mod.collect_bootstrap_runtime(smoke=False)
    assert report["capabilities"]["takeover_ready"] is False
    assert any("Scout MLX endpoint" in item for item in report["next_actions"])
