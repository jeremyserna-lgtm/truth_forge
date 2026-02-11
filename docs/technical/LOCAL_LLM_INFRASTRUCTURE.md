# Local LLM Infrastructure

**Hardware:** Apple M4 Max | 16 cores (12P + 4E) | 128 GB unified memory
**Created:** 2026-01-31
**Status:** ACTIVE SETUP

---

## Current State

### Hardware Capabilities

| Resource | Value | Implication |
|----------|-------|-------------|
| Unified Memory | 128 GB | Can run 100B+ parameter models |
| GPU Cores | 40 (M4 Max) | Native MLX acceleration |
| Memory Bandwidth | ~546 GB/s | Fast model loading |
| Neural Engine | 16-core | Hardware inference acceleration |

**Bottom line:** This machine can run virtually any open-source model locally.

---

## Installed Platforms

### 1. Ollama (PRIMARY)

| Status | Port | API |
|--------|------|-----|
| **RUNNING** | 11434 | OpenAI-compatible at `/v1/` |

**Installed Models:**

| Model | Size | Parameters | Quantization | Use Case |
|-------|------|------------|--------------|----------|
| `llama4:scout` | 67 GB | 108.6B | Q4_K_M | Flagship reasoning |
| `qwen2.5-coder:32b` | 19 GB | 32.8B | Q4_K_M | Code generation |
| `primitive:latest` | 2 GB | 3.2B | Q4_K_M | Custom fine-tune |
| `llama3.2:latest` | 2 GB | 3.2B | Q4_K_M | Fast general |
| `tinyllama:latest` | 637 MB | 1B | Q4_0 | Ultra-fast |
| `bge-large:latest` | 670 MB | 334M | F16 | Embeddings |

**Storage:** 84 GB in `~/.ollama/models/`

**API Examples:**
```bash
# List models
curl http://localhost:11434/api/tags

# Generate (native API)
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5-coder:32b",
  "prompt": "Write a Python function..."
}'

# Chat (OpenAI-compatible)
curl http://localhost:11434/v1/chat/completions -d '{
  "model": "qwen2.5-coder:32b",
  "messages": [{"role": "user", "content": "Hello"}]
}'
```

---

### 2. OpenClaw (UNIFIED GATEWAY - ALREADY CONFIGURED!)

| Status | Port | Type |
|--------|------|------|
| **RUNNING** | 18789 | Node.js gateway + native Mac app |

**Bundle ID:** `bot.molt.mac`
**Version:** 2026.1.29 (build 8345)

**THIS IS ALREADY YOUR UNIFIED GATEWAY.** OpenClaw is configured to route between multiple model providers.

**Configured Providers (from `~/.openclaw/openclaw.json`):**

| Provider | Base URL | Models | Status |
|----------|----------|--------|--------|
| `ollama` | `http://127.0.0.1:11434/v1` | qwen2.5-coder:32b, llama4:scout | ACTIVE |
| `vllm-mlx` | `http://127.0.0.1:8765/v1` | Llama-4-Scout-17B-16E-Instruct-8bit | NEEDS MLX SERVER |
| `anthropic` | (cloud) | claude-opus-4-5 | Available |

**Default Model:** `ollama/qwen2.5-coder:32b`

**Model Aliases:**
```
qwen   → ollama/qwen2.5-coder:32b
scout  → ollama/llama4:scout
mlx    → vllm-mlx/mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit
opus   → anthropic/claude-opus-4-5
```

**Fallback Chain:**
```
qwen2.5-coder → llama4:scout → MLX Scout-17B → claude-opus-4-5
   (primary)      (local)        (local)         (cloud)
```

**Capabilities:**
- [x] Multi-provider model routing
- [x] OpenAI-compatible API
- [x] Screen capture for agent context
- [x] Voice wake / speech recognition
- [x] AppleScript automation for agent actions
- [x] Web UI control panel at http://localhost:18789
- [x] Deep linking (`openclaw://`)
- [x] Subagent support (maxConcurrent: 8)

**Architecture:**
```
OpenClaw.app (native Swift)
    ↓
openclaw-gateway (Node.js :18789)
    ↓
    ├── ollama (:11434) ────── qwen2.5-coder, llama4:scout
    ├── vllm-mlx (:8765) ───── Llama-4-Scout-17B (MLX native)
    └── anthropic (cloud) ──── claude-opus-4-5
```

**Config Location:** `~/.openclaw/openclaw.json`

---

### 3. LM Studio

| Status | Port | Notes |
|--------|------|-------|
| INSTALLED | - | Not running, no models loaded |

**Location:** `/Applications/LM Studio.app`
**Models:** None in `~/.lmstudio/models/`

**Decision:** Keep as backup GUI option, not primary infrastructure

---

### 4. MLX (Python Native)

| Status | Type | Notes |
|--------|------|-------|
| INSTALLED | Python libraries | Apple Silicon optimized |

**Installed Packages:**
```
mlx                 0.30.4
mlx-lm              0.30.4
mlx-metal           0.30.4
mlx-vlm             0.3.9    (vision-language)
vllm-mlx            0.2.5    (high-throughput serving)
transformers        5.0.0rc1
```

**Cached Models:**
- `mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit`
- `sentence-transformers/all-MiniLM-L6-v2`
- `j-hartmann/emotion-english-distilroberta-base`

**Serving Example:**
```bash
# Start MLX server on port 8765 (OpenClaw expects this port)
mlx_lm.server \
  --model mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit \
  --port 8765

# Or with vllm-mlx for higher throughput
python -m vllm_mlx.server --model <model> --port 8765

# Test the server
curl http://localhost:8765/v1/models
```

**IMPORTANT:** OpenClaw is pre-configured to route to `http://127.0.0.1:8765/v1` for MLX models.

---

## Goals

### Goal 1: Unified API Gateway - COMPLETE

**Status:** ALREADY DONE - OpenClaw IS the unified gateway.

**What OpenClaw Provides:**
- [x] OpenAI-compatible API (`/v1/chat/completions`)
- [x] Model routing based on provider prefix (`ollama/`, `vllm-mlx/`, `anthropic/`)
- [x] Cost tracking ($0 for local, tracks cloud usage)
- [x] Multi-provider support
- [x] Subagent orchestration

**Current Architecture:**
```
                    ┌─────────────────────────────────┐
                    │     OPENCLAW GATEWAY (:18789)   │
                    │   Unified model routing layer   │
                    └───────────────┬─────────────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              ↓                     ↓                     ↓
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │     OLLAMA      │   │    VLLM-MLX     │   │   ANTHROPIC     │
    │    (:11434)     │   │    (:8765)      │   │    (cloud)      │
    │                 │   │                 │   │                 │
    │ • llama4:scout  │   │ • Scout-17B-8bit│   │ • opus-4-5      │
    │ • qwen2.5-coder │   │   (MLX native)  │   │                 │
    │ • bge-large     │   │                 │   │                 │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
          ACTIVE              NEEDS START           AVAILABLE
```

**Completed:**
- [x] MLX server running on :8765 (launchd managed)
- [x] Fallback chain configured: qwen → scout → mlx → opus
- [x] Request logging enabled in `~/.openclaw/logs/`
- [x] launchd service created for MLX auto-start

---

### Goal 2: MLX Server Setup - COMPLETE

**Objective:** Get MLX server running on :8765 so OpenClaw can route to it.

**Why MLX alongside Ollama:**
- Vision-language models (mlx-vlm) - not in Ollama
- Native Apple Silicon optimization
- Models not available in GGUF format
- Benchmarking MLX vs Ollama performance

**Tasks:**
- [x] Start MLX server on port 8765
- [x] Verify OpenClaw can route to it
- [x] Create launchd plist for auto-start (`com.truthforge.mlx-server`)
- [ ] Set up mlx-vlm for vision tasks (future)
- [ ] Benchmark: MLX vs Ollama for Llama 4 Scout (future)

**Model Strategy:**
| Model Type | Platform | Reason |
|------------|----------|--------|
| General LLM | Ollama | Easier management, auto-start |
| Code | Ollama (qwen2.5-coder) | Already tuned, 131K context |
| Vision | MLX (mlx-vlm) | Native VLM support |
| Embeddings | Ollama (bge-large) | Simple API |
| Experimental | MLX | Latest HuggingFace models |
| Large context | MLX (Scout-17B) | 10M token context window |

**MLX Server Startup Command:**
```bash
mlx_lm.server \
  --model mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit \
  --port 8765 \
  --host 127.0.0.1
```

---

### Goal 3: OpenClaw Investigation - COMPLETE

**Findings:**

| Question | Answer |
|----------|--------|
| What models does OpenClaw connect to? | Ollama (:11434), MLX (:8765), Anthropic (cloud) |
| Does it have its own model routing? | YES - provider-based routing |
| How does agent orchestration work? | Subagents (max 8 concurrent), memory compaction |
| Can we extend it for unified gateway? | IT IS the gateway - already configured |
| What's openclaw-gateway doing? | WebSocket control plane + HTTP endpoints |

**Config File:** `~/.openclaw/openclaw.json`

**Key Settings:**
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "ollama/qwen2.5-coder:32b" },
      "maxConcurrent": 4,
      "subagents": { "maxConcurrent": 8 }
    }
  },
  "gateway": {
    "mode": "local",
    "http": { "endpoints": { "responses": { "enabled": true } } }
  }
}
```

---

## Configuration Files

### Ollama

**Config location:** `~/.ollama/`
**Models location:** `~/.ollama/models/`

```bash
# Environment variables (add to ~/.zshrc)
export OLLAMA_HOST=127.0.0.1:11434
export OLLAMA_KEEP_ALIVE=5m
export OLLAMA_NUM_PARALLEL=4
```

### MLX

**Cache location:** `~/.cache/huggingface/hub/`
**Server logs:** `~/.openclaw/logs/mlx-server.log`

```bash
# Environment variables
export HF_HOME=~/.cache/huggingface
export MLX_METAL_PREWARM=1
```

### MLX Auto-Start (launchd)

**Plist location:** `~/Library/LaunchAgents/com.truthforge.mlx-server.plist`

```bash
# Load the service (one-time)
launchctl load ~/Library/LaunchAgents/com.truthforge.mlx-server.plist

# Start manually
launchctl start com.truthforge.mlx-server

# Stop manually
launchctl stop com.truthforge.mlx-server

# Unload
launchctl unload ~/Library/LaunchAgents/com.truthforge.mlx-server.plist

# Check status
launchctl list | grep truthforge
```

---

## Quick Reference

### Start Services

```bash
# Ollama (usually auto-starts)
ollama serve

# MLX Server
python -m mlx_lm.server --model <model> --port 8080

# Check what's running
lsof -i :11434 :18789 :8080 :1234
```

### Test Endpoints

```bash
# Ollama
curl http://localhost:11434/api/tags

# MLX (when running)
curl http://localhost:8080/v1/models

# OpenClaw
open http://localhost:18789
```

### Model Management

```bash
# Ollama
ollama list                    # List models
ollama pull <model>            # Download model
ollama rm <model>              # Remove model
ollama show <model>            # Model details

# MLX (via HuggingFace)
huggingface-cli download mlx-community/<model>
```

---

## Progress Tracking

### Phase 1: Discovery - COMPLETE
- [x] Inventory hardware (M4 Max, 128 GB)
- [x] Inventory installed platforms (Ollama, OpenClaw, LM Studio, MLX)
- [x] Document current state
- [x] Investigate OpenClaw internals - IT IS THE GATEWAY
- [x] Test MLX server on :8765

### Phase 2: Configuration - COMPLETE
- [x] Start MLX server on :8765
- [x] Create launchd plist for MLX auto-start
- [x] Load launchd service (auto-starts on login)
- [x] Optimize Ollama settings for M4 Max (in ~/.zshrc)
- [x] Verify OpenClaw routes correctly to both backends

### Phase 3: Unified Gateway - COMPLETE (OpenClaw)
- [x] Choose gateway approach → OpenClaw (already configured)
- [x] Model routing implemented (ollama/, vllm-mlx/, anthropic/)
- [x] Request logging enabled (`~/.openclaw/logs/`)
- [x] Configure fallback chains (qwen → scout → mlx → opus)
- [ ] Add custom metrics/monitoring (future)

### Phase 4: Integration
- [ ] Connect to truth_forge pipelines
- [ ] Replace cloud API calls with local
- [ ] Benchmark cost savings
- [ ] Document usage patterns
- [ ] Create Python client for OpenClaw gateway

---

## Notes

### Why Local LLMs Matter for THE PATTERN

```
HOLD₁ (input) → AGENT (local LLM) → HOLD₂ (output)
```

**ME/NOT-ME Boundary:**
- Local LLMs = ME (under our control)
- Cloud APIs = NOT-ME (external dependency)

**Cost Governance:**
- Local = $0 per token
- Cloud = $$ per token
- Prefer local for iteration, cloud for production validation

### Memory Budget

With 128 GB unified memory:
```
Reserved for system:     ~8 GB
Available for models:   ~120 GB

Current Ollama usage:    ~84 GB (if all loaded)
Typical active models:   ~20-70 GB (1-2 models)
Remaining headroom:      ~50-100 GB
```

**Can run simultaneously:**
- llama4:scout (67 GB) + embeddings (670 MB) ✓
- qwen2.5-coder (19 GB) + llama4:scout (67 GB) ✓
- All small models together ✓

---

## Next Actions

### Completed (2026-01-31)

1. ~~Start MLX server on :8765~~ ✓ (launchd managed)
2. ~~Test OpenClaw routing to MLX~~ ✓ (both backends verified)
3. ~~Create launchd service for MLX~~ ✓ (`com.truthforge.mlx-server`)
4. ~~Optimize Ollama for M4 Max~~ ✓ (settings in ~/.zshrc)
5. ~~Configure fallback chains~~ ✓ (qwen → scout → mlx → opus)

### Future Work

1. **Benchmark local models**
   - qwen2.5-coder:32b vs Claude for code
   - llama4:scout vs Claude for reasoning
   - Measure tokens/sec, quality, cost savings

2. **Set up mlx-vlm for vision tasks**
   ```bash
   python -m mlx_vlm.server --model <vision-model> --port 8766
   ```

3. **Create Python client**
   - Wrapper for OpenClaw gateway
   - Drop-in replacement for OpenAI client
   - Automatic local → cloud fallback

4. **Connect to truth_forge pipelines**
   - Replace cloud API calls with local
   - Use OpenClaw gateway as unified endpoint

---

*Last updated: 2026-01-31 17:40 MST*
*Setup complete: MLX auto-start, Ollama optimized, fallback chains configured*
