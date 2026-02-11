#!/usr/bin/env python3
"""
Genesis Cluster Dynamic Context Calculator

Calculates the actual usable context window based on:
1. Available cluster nodes (queries EXO)
2. Total unified memory across active nodes
3. Model memory requirements
4. KV cache requirements per token

This runs in real-time and adjusts as nodes come online/offline.
"""

import json
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

# Cluster configuration
CLUSTER_NODES = {
    "King": {"ip": "192.168.68.121", "memory_gb": 512},
    "Soldier-1": {"ip": "192.168.68.112", "memory_gb": 256},
    "Soldier-2": {"ip": "192.168.68.123", "memory_gb": 256},
    "Soldier-3": {"ip": "192.168.68.115", "memory_gb": 256},
}

# Model specifications
MODELS = {
    "mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit": {
        "name": "Scout",
        "params_b": 17,
        "experts": 16,
        "quantization": "8bit",
        "model_size_gb": 104,  # From EXO: 103950MB
        "hidden_size": 5120,
        "num_layers": 48,
        "num_kv_heads": 8,
        "max_position_embeddings": 10_485_760,
        "bytes_per_kv_token": 640,  # Estimated: 2 * layers * 2 * hidden * kv_heads / 8
    },
    "mlx-community/Llama-4-Maverick-17B-128E-Instruct-4bit": {
        "name": "Maverick",
        "params_b": 17,
        "experts": 128,
        "quantization": "4bit",
        "model_size_gb": 200,  # Estimated
        "hidden_size": 5120,
        "num_layers": 48,
        "num_kv_heads": 8,
        "max_position_embeddings": 1_048_576,
        "bytes_per_kv_token": 640,
    },
}


@dataclass
class ClusterState:
    """Current state of the Genesis cluster."""
    active_nodes: list[str]
    total_memory_gb: int
    available_memory_gb: int
    model_loaded: Optional[str]
    model_size_gb: int
    max_context_tokens: int
    recommended_context_tokens: int


def check_node_status(ip: str, timeout: int = 5) -> bool:
    """Check if a node is reachable and running EXO."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout={}".format(timeout),
             "-o", "StrictHostKeyChecking=no",
             "jeremyserna@{}".format(ip),
             "pgrep -f 'python.*exo' >/dev/null && echo OK"],
            capture_output=True, text=True, timeout=timeout + 2
        )
        return "OK" in result.stdout
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def get_exo_cluster_info(king_ip: str = "192.168.68.121") -> dict:
    """Query EXO API for cluster and model info."""
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5",
             "jeremyserna@{}".format(king_ip),
             "curl -s http://localhost:8000/v1/models"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError):
        pass
    return {"data": []}


def calculate_context_window(
    total_memory_gb: int,
    model_id: str,
    headroom_gb: int = 50
) -> tuple[int, int]:
    """
    Calculate max and recommended context window.

    Returns:
        (max_context_tokens, recommended_context_tokens)
    """
    model = MODELS.get(model_id)
    if not model:
        # Unknown model, use conservative defaults
        return (100_000, 50_000)

    model_size_gb = model["model_size_gb"]
    available_for_kv = total_memory_gb - model_size_gb - headroom_gb

    if available_for_kv <= 0:
        return (0, 0)

    # Calculate max tokens based on KV cache
    available_bytes = available_for_kv * 1024 * 1024 * 1024
    max_tokens = int(available_bytes / model["bytes_per_kv_token"])

    # Cap at model's architectural maximum
    max_tokens = min(max_tokens, model["max_position_embeddings"])

    # Recommended is 80% of max for safety margin
    recommended = int(max_tokens * 0.8)

    return (max_tokens, recommended)


def get_cluster_state() -> ClusterState:
    """Get current cluster state with calculated context window."""
    # Check which nodes are active
    active_nodes = []
    total_memory = 0

    for name, info in CLUSTER_NODES.items():
        if check_node_status(info["ip"]):
            active_nodes.append(name)
            total_memory += info["memory_gb"]

    # Get loaded model from EXO
    exo_info = get_exo_cluster_info()
    model_loaded = None
    model_size = 0

    # Find Scout or active model
    for m in exo_info.get("data", []):
        if "scout" in m.get("id", "").lower():
            model_loaded = m["id"]
            model_size = m.get("storage_size_megabytes", 0) // 1024
            break

    # Calculate context window
    if model_loaded:
        max_ctx, rec_ctx = calculate_context_window(total_memory, model_loaded)
    else:
        max_ctx, rec_ctx = (0, 0)

    available_memory = total_memory - model_size - 50  # 50GB headroom

    return ClusterState(
        active_nodes=active_nodes,
        total_memory_gb=total_memory,
        available_memory_gb=max(0, available_memory),
        model_loaded=model_loaded,
        model_size_gb=model_size,
        max_context_tokens=max_ctx,
        recommended_context_tokens=rec_ctx,
    )


def print_cluster_status():
    """Print human-readable cluster status."""
    state = get_cluster_state()

    print("=" * 60)
    print("GENESIS CLUSTER STATUS")
    print("=" * 60)
    print()
    print("ACTIVE NODES:")
    for node in state.active_nodes:
        info = CLUSTER_NODES[node]
        print(f"  ✓ {node} ({info['ip']}) - {info['memory_gb']}GB")

    inactive = set(CLUSTER_NODES.keys()) - set(state.active_nodes)
    for node in inactive:
        info = CLUSTER_NODES[node]
        print(f"  ✗ {node} ({info['ip']}) - OFFLINE")

    print()
    print(f"TOTAL MEMORY: {state.total_memory_gb}GB")
    print(f"AVAILABLE FOR KV CACHE: {state.available_memory_gb}GB")
    print()
    print(f"LOADED MODEL: {state.model_loaded or 'None'}")
    print(f"MODEL SIZE: {state.model_size_gb}GB")
    print()
    print("CONTEXT WINDOW:")
    print(f"  Maximum:     {state.max_context_tokens:>15,} tokens")
    print(f"  Recommended: {state.recommended_context_tokens:>15,} tokens")
    print()

    if state.max_context_tokens > 1_000_000:
        print(f"  That's {state.max_context_tokens / 1_000_000:.1f}M tokens!")

    print("=" * 60)

    # Output JSON for programmatic use
    print()
    print("JSON OUTPUT:")
    print(json.dumps({
        "active_nodes": state.active_nodes,
        "total_memory_gb": state.total_memory_gb,
        "available_memory_gb": state.available_memory_gb,
        "model_loaded": state.model_loaded,
        "model_size_gb": state.model_size_gb,
        "max_context_tokens": state.max_context_tokens,
        "recommended_context_tokens": state.recommended_context_tokens,
    }, indent=2))


if __name__ == "__main__":
    print_cluster_status()
