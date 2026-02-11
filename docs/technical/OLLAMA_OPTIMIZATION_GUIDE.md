# Ollama Memory Optimization Guide

## Problem

The llama4:scout model (108.6B parameters, Q4_K_M) requires:
- **67GB** disk storage
- **114GB** VRAM allocation
- On a **128GB** system, this leaves only **14GB** for:
  - macOS system
  - Other applications
  - Context window growth
  - Memory spikes during inference

This causes memory overrun and server crashes.

---

## Solution: Environment Variables

Create a LaunchAgent or shell profile with these optimizations:

### Option 1: Shell Profile (~/.zshrc or ~/.bashrc)

```bash
# Ollama Memory Optimizations
export OLLAMA_NUM_CTX=32768          # Reduce context window (default can expand)
export OLLAMA_NUM_GPU=999            # Use all GPU layers
export OLLAMA_FLASH_ATTENTION=1      # Enable flash attention (memory efficient)
export OLLAMA_KV_CACHE_TYPE=q4_0     # Quantized KV cache (saves ~50% KV memory)
export OLLAMA_KEEP_ALIVE=10m         # Unload model after 10 min idle
export OLLAMA_MAX_LOADED_MODELS=1    # Only one model at a time
```

### Option 2: LaunchAgent (Persistent)

Create `~/Library/LaunchAgents/com.ollama.env.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.env</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_NUM_CTX</key>
        <string>32768</string>
        <key>OLLAMA_FLASH_ATTENTION</key>
        <string>1</string>
        <key>OLLAMA_KV_CACHE_TYPE</key>
        <string>q4_0</string>
        <key>OLLAMA_KEEP_ALIVE</key>
        <string>10m</string>
        <key>OLLAMA_MAX_LOADED_MODELS</key>
        <string>1</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

---

## Key Optimizations Explained

### 1. OLLAMA_NUM_CTX (Context Window)

| Value | Memory Impact | Use Case |
|-------|---------------|----------|
| 4096 | Minimal | Quick queries |
| 8192 | Low | Standard chat |
| 32768 | Moderate | Coding tasks |
| 131072 | High | Document analysis |
| 262144 | Maximum | Full context (unsafe on 128GB) |

**Recommendation:** Start with `32768` for stability, increase as needed.

### 2. OLLAMA_KV_CACHE_TYPE

The KV cache stores attention states. Quantizing it saves significant memory:

| Type | Memory | Quality |
|------|--------|---------|
| f16 | 100% | Best |
| q8_0 | 50% | Good |
| q4_0 | 25% | Acceptable |

**Recommendation:** Use `q4_0` for Scout to prevent overrun.

### 3. OLLAMA_FLASH_ATTENTION

Flash Attention computes attention in chunks, reducing peak memory:
- Standard attention: O(n^2) memory
- Flash attention: O(n) memory

**Recommendation:** Always enable (`1`).

### 4. OLLAMA_KEEP_ALIVE

Automatically unloads models after idle period:
- `5m` = 5 minutes
- `10m` = 10 minutes
- `0` = Unload immediately after request
- `-1` = Never unload

**Recommendation:** `10m` balances responsiveness and memory.

### 5. OLLAMA_MAX_LOADED_MODELS

On 128GB with Scout (114GB VRAM), only one large model can fit:

**Recommendation:** `1` to prevent loading multiple models.

---

## Quick Start Commands

### Apply Optimizations (Current Session)

```bash
# Run this before starting Ollama
export OLLAMA_NUM_CTX=32768
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KV_CACHE_TYPE=q4_0
export OLLAMA_KEEP_ALIVE=10m
export OLLAMA_MAX_LOADED_MODELS=1

# Restart Ollama
pkill ollama
ollama serve &
```

### Verify Settings

```bash
# Check if model loads with reduced memory
ollama run llama4:scout "Hello"

# Monitor memory during inference
while true; do memory_pressure; sleep 2; done
```

---

## Memory Budget (128GB System)

| Component | Allocation |
|-----------|------------|
| macOS + Apps | 8 GB |
| Scout Base Model | 67 GB |
| KV Cache (q4_0, 32K ctx) | ~4 GB |
| Working Memory | 8 GB |
| **Headroom** | **41 GB** |

With optimizations, you have **41GB headroom** instead of **14GB**.

---

## Alternative: Use MLX for Interactive

For fast, interactive use, prefer MLX (already running on port 8765):

```bash
# MLX model is smaller, faster, Metal-optimized
curl http://127.0.0.1:8765/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit",
       "messages": [{"role": "user", "content": "Hello"}]}'
```

**Use Ollama Scout for:**
- Long context tasks (262K capability)
- Batch processing
- When you need the full 108.6B

**Use MLX Scout for:**
- Interactive chat
- Quick queries
- Development/testing

---

## Monitoring Commands

```bash
# Check memory pressure
memory_pressure

# Check Ollama memory usage
ps aux | grep ollama

# Check loaded models
curl http://localhost:11434/api/ps | python3 -m json.tool

# Force unload all models
curl http://localhost:11434/api/generate -d '{"model": "llama4:scout", "keep_alive": 0}'
```

---

## SOVEREIGN Integration

In the SOVEREIGN architecture, these optimizations should be:

1. **Automated** in the startup sequence
2. **Monitored** by the Heartbeat Protocol
3. **Adjusted** based on current task requirements

The Context Manager should dynamically set `OLLAMA_NUM_CTX` based on:
- Available memory
- Current task requirements
- Concurrent processes

---

*Document Version: 1.0.0*
*Purpose: Prevent memory overrun with llama4:scout on 128GB systems*
