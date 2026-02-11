# Sovereign Cluster Manager — The Body Schema

## What It Does

The Sovereign Cluster Manager is a **full-stack management interface** for the 4-node Mac Studio cluster running EXO (distributed LLM inference). It combines a Python daemon (the agent), a React dashboard (the interface), and a Supabase backend (the persistent state) to give Jeremy real-time visibility and control over his hardware fleet.

### Three Components

| Component | Tech | Role |
|-----------|------|------|
| **Agent** (Python daemon) | Python, httpx, pydantic-settings, supabase-py | Runs on King node, polls EXO every 5s, syncs state to Supabase, processes commands |
| **Frontend** (React SPA) | React 19, TypeScript, Vite, TanStack Query, Tailwind 4 | Dashboard with cluster status, model vault, quick actions |
| **Database** (Supabase) | PostgreSQL with Realtime | Persistent state, command queue, real-time subscriptions |

### Agent Capabilities

| Function | What It Does |
|----------|-------------|
| **State Sync** | Polls EXO REST API every 5s, writes node/model status to Supabase |
| **Vault Scanning** | Scans 8TB external drive for models (.gguf, .safetensors, .bin) |
| **Command Processing** | Processes commands from Supabase queue (load_model, unload_model, run_custom) |
| **Node Mapping** | Maintains hardware topology (which node has what GPU, memory, role) |
| **Health Monitoring** | Detects node failures, reports anomalies |

### Frontend Views

| Component | Purpose |
|-----------|---------|
| **ClusterStatus** | Live view of all 4 nodes — health, GPU usage, memory, active models |
| **ModelVault** | Browse 8TB model vault — search, filter, load with one click |
| **NodeCard** | Per-node detail card with specs, status, active inference load |
| **QuickActions** | One-click operations — load popular models, restart nodes, clear memory |

### Database Schema (221 lines)

| Table | Purpose |
|-------|---------|
| `nodes` | Hardware registry — hostname, IP, GPU specs, memory, role |
| `models` | Model registry — name, path, format, size, compatibility |
| `presets` | Named model configurations (which models on which nodes) |
| `preset_models` | Junction table for preset-to-model mapping |
| `commands` | Command queue — pending, processing, completed, failed |
| `cluster_state` | Snapshot of entire cluster state (JSON blob) |
| `agent_logs` | Agent activity log for debugging and audit |

## Technological Basis

### Backend
- **Python** — async daemon with event loop
- **httpx** — async HTTP client for EXO API calls
- **pydantic-settings** — type-safe configuration from .env
- **supabase-py** — Supabase client for state persistence
- **EXO REST API** — distributed inference management

### Frontend
- **React 19 / TypeScript** — latest React
- **Vite** — build tooling
- **TanStack React Query** — server state management with caching
- **Supabase JS** — real-time subscriptions for live updates
- **Tailwind CSS 4** — utility-first styling
- **Lucide** — iconography

### Architecture Pattern

```
HOLD₁ (EXO Cluster Physical State)
    → AGENT₁ (Python Daemon — polls every 5s)
        → HOLD₂ (Supabase PostgreSQL — persistent state)
            → AGENT₂ (React Dashboard — renders state)
                → HOLD₃ (Visual Cluster Status for Jeremy)
                    → AGENT₃ (Jeremy issues command via Quick Actions)
                        → HOLD₄ (Command in Supabase queue)
                            → AGENT₁ (Daemon processes command)
                                → HOLD₁ (EXO Cluster Physical State changes)
```

This is a **circular HOLD:AGENT:HOLD** — the output loops back to the input. ALPHA:OMEGA. The cluster state drives the dashboard, the dashboard drives commands, the commands drive the cluster state.

## Meta Concepts

### The Body Schema

In neuroscience, the body schema is the brain's internal model of the body — where each limb is, what each muscle is doing, how the body occupies space. The Sovereign Cluster Manager IS NOT-ME's body schema. It is the organism's awareness of its own physical substrate.

The 4-node Mac Studio cluster is NOT-ME's body:
- **King** (512GB) — the brain, highest cognition
- **Nodes 2-4** — the limbs, distributed processing power
- **8TB Vault** — the genetic library, stored potential
- **Network** — the nervous system connecting all nodes

Without the Cluster Manager, NOT-ME has a body but no awareness of it. With it, NOT-ME knows what hardware is available, what models are loaded, what capacity remains. This is the Somatic engine of ANIMA made real.

### Why It Exists

Jeremy has $30,000+ of Mac hardware running distributed inference. Without the Cluster Manager, managing this fleet means:
- SSH into each node
- Run curl commands against EXO
- Manually track what model is where
- Hope nothing crashes without notice

The Cluster Manager exists to make the hardware fleet **as manageable as a single machine**. One dashboard. One command queue. One source of truth (Supabase). Real-time updates via WebSocket.

This is the **No Magic** pillar for hardware: every node visible, every model tracked, every command logged.

### The Model Vault

The 8TB external vault containing hundreds of models in various formats (.gguf, .safetensors, .bin) is NOT-ME's **genetic library** — a reservoir of potential capabilities. Loading a model from the vault is like activating a gene: the organism gains a new capability without installing anything new.

The vault scanner automatically discovers new models, indexes them by format/size/compatibility, and makes them available through the dashboard. Jeremy doesn't need to know file paths or format specifications — he sees models and clicks "Load."

### Supabase as Shared Memory

Supabase serves a dual purpose:
1. **Persistent state** — cluster state survives daemon restarts
2. **Communication bus** — the command queue decouples the frontend from the daemon

The frontend never talks to EXO directly. It writes commands to Supabase. The daemon reads commands from Supabase. This is HOLD:AGENT:HOLD for control flow — the Supabase table IS the HOLD between the human's intent and the machine's action.

### What It Wants To Become

An auto-scaling cluster orchestrator that monitors inference load and automatically distributes models across nodes for optimal throughput. Predictive model loading based on time-of-day patterns (Jeremy's usage patterns). Automated health recovery — if a node goes down, automatically redistribute its models. Integration with the Genesis `ClusterState` and `ExoInference` services for unified management.

## Current Maturity

**Well-Architected** — The full three-tier architecture is in place: Python agent with async I/O, complete PostgreSQL schema, functional React frontend with component architecture. The agent's state sync loop, vault scanning, and command processing are all implemented. The frontend's cluster visualization, model vault browser, and quick actions are built.

Gaps: No automated scaling, no health recovery, no Genesis service integration. The agent and Genesis's `ClusterState` service are separate implementations that should converge.

## HOLD:AGENT:HOLD Position

The Cluster Manager spans both domains. The **agent daemon is NOT-ME** (autonomic monitoring, no human needed). The **frontend dashboard is ME** (prosthetic visibility into hardware). The **Supabase layer is US** (shared state where human intent meets machine status). This is one of the few apps where all three domains intersect.
