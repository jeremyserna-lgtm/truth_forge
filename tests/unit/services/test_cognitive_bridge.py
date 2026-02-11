from truth_forge.gateway.types import CompletionRequest
from truth_forge.services.cognitive_bridge import CognitiveBridge


class DummyProvider:
    def __init__(self, available=True):
        self._available = available
        self.calls = 0

    def is_available(self):
        return self._available

    def complete(self, request):
        self.calls += 1
        return type("Resp", (), {"content": "ok", "model": "dummy", "provider": "dummy"})()


def test_fallback_to_scout_when_maverick_down(monkeypatch, tmp_path):
    cfg = tmp_path / "bridge.json"
    cfg.write_text(
        """
        {
          "models": {
            "scout": {"provider": "scout", "endpoint": "http://localhost:8765/v1", "max_context": 100000},
            "maverick": {"provider": "maverick", "endpoint": "http://localhost:8766/v1", "max_context": 131072},
            "r1": {"provider": "r1", "endpoint": "http://localhost:8767/v1", "max_context": 32768}
          },
          "routing": {
            "simple_chat": "scout",
            "architecture_design": "maverick",
            "fallback_chain": ["scout","maverick","r1"]
          },
          "thresholds": {"large_context_tokens": 80000}
        }
        """
    )
    bridge = CognitiveBridge(config_path=cfg)
    bridge.maverick = DummyProvider(available=False)
    bridge.r1 = DummyProvider(available=False)
    bridge.scout = DummyProvider(available=True)

    req = CompletionRequest(prompt="simple", model="scout-genesis", max_tokens=10)
    res = bridge.complete(req, task_type="architecture_design")
    assert bridge.scout.calls == 1
    assert res.content == "ok"


def test_uses_maverick_when_available(monkeypatch, tmp_path):
    cfg = tmp_path / "bridge.json"
    cfg.write_text(
        """
        {
          "models": {
            "scout": {"provider": "scout", "endpoint": "http://localhost:8765/v1", "max_context": 100000},
            "maverick": {"provider": "maverick", "endpoint": "http://localhost:8766/v1", "max_context": 131072},
            "r1": {"provider": "r1", "endpoint": "http://localhost:8767/v1", "max_context": 32768}
          },
          "routing": {
            "simple_chat": "scout",
            "architecture_design": "maverick",
            "fallback_chain": ["maverick","scout","r1"]
          },
          "thresholds": {"large_context_tokens": 80000}
        }
        """
    )
    bridge = CognitiveBridge(config_path=cfg)
    bridge.maverick = DummyProvider(available=True)
    bridge.r1 = DummyProvider(available=False)
    bridge.scout = DummyProvider(available=True)
    # Stub readiness to allow Maverick
    monkeypatch.setattr(
        "truth_forge.services.cognitive_bridge.check_readiness",
        lambda: {
            "maverick": type("R", (), {"ready": True})(),
            "scout": type("R", (), {"ready": True})(),
            "r1": type("R", (), {"ready": False})(),
        },
    )

    req = CompletionRequest(prompt="design", model="maverick-genesis", max_tokens=10)
    res = bridge.complete(req, task_type="architecture_design")
    assert bridge.maverick.calls == 1
    assert res.content == "ok"
