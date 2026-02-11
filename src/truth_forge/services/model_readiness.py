"""Model readiness detection based on local cache size thresholds.

Uses symlinked HuggingFace cache paths to infer whether a model is fully present.
This is lightweight and does not require the model server to be running.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _hf_cache_root() -> Path:
    """Resolve HuggingFace cache root at call time.

    Using a function (instead of module constant) keeps behavior testable when
    env vars are patched after import.
    """
    return Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface" / "hub"))


@dataclass
class ModelReadiness:
    name: str
    path: Path
    size_gb: float
    expected_gb: float
    ready: bool


def _dir_size_bytes(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            try:
                total += (Path(root) / f).stat().st_size
            except FileNotFoundError:
                continue
    return total


def check_readiness() -> dict[str, ModelReadiness]:
    """Return readiness for Scout, Maverick, R1 based on cache size."""
    hf_cache = _hf_cache_root()
    models = {
        "scout": {
            "path": hf_cache / "models--mlx-community--Llama-4-Scout-17B-16E-Instruct-8bit",
            "expected_gb": 100.0,
        },
        "maverick": {
            "path": hf_cache / "models--mlx-community--Llama-4-Maverick-17B-128E-Instruct-4bit",
            "expected_gb": 260.0,
        },
        "r1": {
            "path": hf_cache / "models--mlx-community--DeepSeek-R1-4bit",
            "expected_gb": 400.0,
        },
    }

    readiness: dict[str, ModelReadiness] = {}
    for name, cfg in models.items():
        path = cfg["path"]
        expected = cfg["expected_gb"]
        if not path.exists():
            readiness[name] = ModelReadiness(name, path, 0.0, expected, False)
            continue
        size_gb = _dir_size_bytes(path) / (1024**3)
        ready = size_gb >= expected * 0.9  # 90% threshold
        readiness[name] = ModelReadiness(name, path, round(size_gb, 2), expected, ready)
    return readiness
