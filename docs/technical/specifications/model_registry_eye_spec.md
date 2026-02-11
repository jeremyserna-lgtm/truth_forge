# MODEL REGISTRY EYE — Build Spec

## What This Is

A visual model management interface for Jeremy's 4-node Mac Studio cluster running Ollama. Jeremy currently has 3+ LLMs downloaded and is evaluating Llama Maverick quantization options (4-bit, 6-bit, 8-bit, BF-16). He cannot parse model options as chat text. He needs to SEE them.

**This is a React web app. Single page. Cards, not chat.**

---

## Architecture

**Stack**: React + TypeScript + Tailwind CSS
**Backend**: FastAPI (Python) — thin wrapper around Ollama API + cluster status
**Data**: Ollama API (`/api/tags`, `/api/show`, `/api/ps`) across all 4 nodes
**Deployment**: Runs locally, accessible at `localhost:3000`

### The 4 Cluster Nodes

| Name | Role | RAM | Hostname/IP |
|------|------|-----|-------------|
| King | Primary Mac Studio | 512GB | (Jeremy provides) |
| Soldier 1 | Worker Mac Studio | 256GB | (Jeremy provides) |
| Soldier 2 | Worker Mac Studio | 256GB | (Jeremy provides) |
| Soldier 3 | Worker Mac Studio | 256GB | (Jeremy provides) |

The backend pings Ollama on each node to aggregate model state across the full cluster.

---

## What Jeremy Sees When He Opens It

### Top Bar — Cluster Health Strip
A horizontal bar showing all 4 nodes:
- Node name (King, Soldier 1-3)
- Status: 🟢 Online / 🔴 Offline
- RAM: Used / Total (e.g., "128GB / 512GB")
- Currently loaded model (if any)
- GPU utilization %

This is ALWAYS visible. Jeremy should always know cluster state at a glance.

### Main Area — Model Cards

Each downloaded model gets a CARD. Not a list. A card.

**Card shows:**
- Model name (e.g., "Llama Maverick 4-bit")
- Model family tag (e.g., "llama-maverick", "llama-scout")  
- Quantization level (Q4_K_M, Q6_K, Q8_0, BF16) — displayed as a colored badge
  - 4-bit = blue (smallest, fastest, least accurate)
  - 6-bit = green (balanced)
  - 8-bit = orange (high quality)
  - BF16 = red (full precision, largest)
- File size on disk
- Parameter count
- Context window size
- RAM required to load
- Status: Downloaded / Loading / Running / Available to Pull
- Which node(s) it's deployed on (node badges)
- Last used timestamp

**Card actions (buttons on each card):**
- **Load** → Pick which node to load it on (dropdown of available nodes with enough RAM)
- **Unload** → Remove from active memory on a node
- **Delete** → Remove from disk (with confirmation)
- **Compare** → Add to comparison view (checkbox, multi-select)
- **Fine-tune** → Opens fine-tune panel (future, grayed out for v1 with tooltip "Coming soon")

### Comparison View

When Jeremy checks 2-4 models for comparison, a bottom panel slides up showing them side by side:

| Property | Maverick 4-bit | Maverick 6-bit | Maverick 8-bit | Maverick BF16 |
|----------|---------------|----------------|----------------|---------------|
| Size on disk | 24GB | 36GB | 48GB | 96GB |
| RAM required | 26GB | 38GB | 52GB | 98GB |
| Parameters | 400B | 400B | 400B | 400B |
| Context window | 128K | 128K | 128K | 128K |
| Quant method | Q4_K_M | Q6_K | Q8_0 | BF16 |
| Quality tradeoff | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Speed tradeoff | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Fits on Soldier? | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No (needs King) |
| Fits on King? | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

**This is the thing Jeremy needs RIGHT NOW.** He's looking at text about quantization options and can't parse it. This table, visual and scannable, solves that immediately.

### Available Models Panel (Right Sidebar or Tab)

Models available to pull from Ollama registry but NOT yet downloaded:
- Searchable list
- Shows name, sizes available, parameter counts
- One-click "Pull" button → starts download, shows progress bar on the card
- Filter by: family, size range, quantization level

### The Seer Strip — Bottom Bar

This is the AI layer. A persistent strip at the bottom of the screen with 3 contextual suggestions. These update based on what Jeremy is looking at and what the system knows.

**Examples of what the Seer suggests:**

When Jeremy first opens the app:
- "You have Maverick in 4-bit. The 6-bit fits on any Soldier and gives meaningfully better quality for credential data. Want me to pull it?"
- "King has 384GB free. You could load the BF16 for highest quality testing."
- "You haven't tried Scout yet. It's optimized for long-context tasks like document analysis. Want to see the options?"

When Jeremy is comparing models:
- "For fine-tuning on credential data, 8-bit gives the best quality-to-RAM ratio. Here's why..."
- "The 4-bit and 6-bit can run simultaneously on Soldier 1 and Soldier 2 for A/B testing."
- "BF16 is only worth it if you need maximum accuracy for production. For development, 6-bit is indistinguishable."

When Jeremy loads a model:
- "Loaded Maverick 6-bit on Soldier 2. Want to run a quick benchmark against the 4-bit on Soldier 1?"
- "This model works well with your existing credential extraction pipeline. Want to test it?"
- "Soldier 3 is idle. Want to load Scout there for comparison?"

**Implementation for v1**: The Seer strip calls an LLM (use one of Jeremy's local models via Ollama, or fall back to Gemini API) with context about:
- Current cluster state
- What models are loaded/available
- Jeremy's recent actions in the registry
- A system prompt explaining Jeremy's work (credential data, fine-tuning goals, on-premise deployment focus)

The prompt asks: "Given this state, what are the 3 most useful things Jeremy should consider doing next?" and displays the responses as clickable action buttons.

**After every action Jeremy takes**, the Seer regenerates its 3 suggestions based on the new state.

---

## API Endpoints (FastAPI Backend)

```
GET  /api/cluster/status          → Health of all 4 nodes
GET  /api/models/local            → All downloaded models across cluster  
GET  /api/models/running          → Currently loaded models per node
GET  /api/models/available        → Available from Ollama registry (cached)
GET  /api/models/{name}/details   → Detailed model info
POST /api/models/pull             → Pull a model (node + model name)
POST /api/models/load             → Load model into memory on specific node
POST /api/models/unload           → Unload model from node
POST /api/models/delete           → Delete model from node
GET  /api/seer/suggest            → Get 3 contextual suggestions given current state
POST /api/actions/log             → Log a user action (for future atom generation)
```

The backend iterates over all 4 node IPs and aggregates Ollama responses.

---

## Ollama API Reference (What the Backend Wraps)

These are the Ollama REST endpoints the backend calls per node:

```
GET  http://{node}:11434/api/tags     → List local models
POST http://{node}:11434/api/show     → Model details (send {"name": "model"})
GET  http://{node}:11434/api/ps       → Running models
POST http://{node}:11434/api/pull     → Pull model (streaming)
POST http://{node}:11434/api/generate → Test generation
DELETE http://{node}:11434/api/delete  → Delete model
```

---

## Build Order

1. **Backend first**: FastAPI app that talks to Ollama on all 4 nodes (or start with 1 node if cluster isn't fully networked yet). Get `/cluster/status` and `/models/local` working.
2. **Cluster health strip**: Top bar showing node status. This validates the backend works.
3. **Model cards**: Display downloaded models as cards with key stats. This is the core value.
4. **Comparison view**: Side-by-side comparison panel. This is what Jeremy needs TODAY.
5. **Pull/Load/Unload actions**: Buttons on cards that trigger model management.
6. **Available models sidebar**: Browse and pull new models.
7. **Seer strip**: The AI suggestion bar at the bottom. This is the soul but can come last in v1.

**Jeremy can start using it after step 4.** Everything after that is enhancement.

---

## What This Becomes

This Model Registry is the first "Eye" — the first visual interface built in the pattern that Sovereign Forge will eventually produce automatically. It establishes:

- **Cards over chat**: Spatial display of options, not text walls
- **Comparison as primitive**: Side-by-side evaluation built in
- **Seer as suggestion engine**: AI surfaces options, human clicks
- **Every interaction is data**: Actions logged for future knowledge atom generation
- **Cluster-aware**: Everything knows about all 4 nodes

When Sovereign Forge exists, "build me a model registry" is something it produces. For now, we build it by hand — and it becomes the PATTERN that teaches Forge what an Eye looks like.

---

## Node Configuration

Jeremy needs to provide:
- IP addresses or hostnames for all 4 nodes (King + 3 Soldiers)
- Confirmation that Ollama is running and accessible on port 11434 on each
- If nodes aren't all online yet, the backend gracefully handles offline nodes (shows them as 🔴 in the health strip)

If only 1 node is running, build against that. The multi-node aggregation pattern is the same — it just loops over 1 instead of 4.
