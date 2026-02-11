# Triad View Setup - Scout/Maverick/R1 Integration

This document explains how to run the integrated knowledge atom generation system with Scout, Maverick, and R1 communicating via tensor space.

## Architecture Overview

```
┌──────────────────────────────────────────────────────┐
│         Knowledge Atomizer (React/TypeScript)        │
│                    Triad View                        │
└────────────────────┬─────────────────────────────────┘
                     │ HTTP
                     ▼
┌──────────────────────────────────────────────────────┐
│         FastAPI Backend (Python)                     │
│         truth_forge/api/knowledge_atom_api.py        │
└────────────────────┬─────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│         KnowledgeAtomFactory                         │
│  ┌─────────────────────────────────────────────┐    │
│  │          Shared MemoryCortex                │    │
│  │  (5 graphs: Semantic, Temporal, Causal,     │    │
│  │   Entity, Emotional)                        │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌───────────┐  ┌──────────┐  ┌──────────────┐    │
│  │  Scout    │  │ Maverick │  │     R1       │    │
│  │  (10M ctx)│  │ (128 exp)│  │  (671B)      │    │
│  │  169GB    │  │  210GB   │  │  36GB/1.3TB  │    │
│  │  Single   │  │   EXO    │  │    EXO       │    │
│  └───────────┘  └──────────┘  └──────────────┘    │
└──────────────────────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────┐
│         EXO Distributed Inference                    │
│  King (512GB) + 3 Soldiers (256GB each)              │
│  http://localhost:52415                              │
└──────────────────────────────────────────────────────┘
```

## Prerequisites

1. **Genesis Cluster Running**:
   - King: 512GB (M3 Ultra)
   - Soldier 1-3: 256GB each (M3 Ultra)
   - Total: 1.28TB

2. **Models Available**:
   - Scout: `llama4:scout` on http://localhost:11434 (Ollama)
   - Maverick: `llama4:maverick` on http://localhost:52415 (EXO)
   - R1: `deepseek-r1:671b` on http://localhost:52415 (EXO)

3. **EXO Running**:
   ```bash
   # On King (coordinator)
   exo --port 52415

   # On each Soldier (workers)
   ssh soldier1 "exo --port 52415"
   ssh soldier2 "exo --port 52415"
   ssh soldier3 "exo --port 52415"
   ```

## Running the System

### Step 1: Start the FastAPI Backend

```bash
cd /Users/jeremyserna/truth_forge

# Activate venv
source .venv/bin/activate

# Start the API server
python -m truth_forge.api.knowledge_atom_api

# Or with uvicorn directly:
uvicorn truth_forge.api.knowledge_atom_api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at http://localhost:8000

Endpoints:
- `POST /api/v1/knowledge-atom/generate` - Generate atom
- `GET /api/v1/health` - Health check
- `GET /api/v1/exo/status` - EXO cluster status
- `GET /docs` - Interactive API documentation

### Step 2: Start the Knowledge Atomizer App

```bash
cd /Users/jeremyserna/truth_forge/apps/knowledge-atomizer

# Install dependencies (first time)
npm install

# Start development server
npm run dev
```

The app will be available at http://localhost:5173

### Step 3: Use the Triad View

1. Navigate to the **Triad** tab in the Knowledge Atomizer
2. Enter text in the input field
3. Click **Generate Atom**
4. Watch the generation happen in real-time:
   - MemoryCortex enrichment
   - Scout observing (10M context, single-node)
   - Maverick reasoning (128 experts, EXO distributed)
   - R1 architecting (671B parameters, EXO distributed)
   - Convergence/divergence analysis
5. Generated atoms are automatically added to your library

## Verifying the Setup

### Check EXO Status

```bash
curl http://localhost:52415/v1/models
```

Should return list of available models.

### Check API Health

```bash
curl http://localhost:8000/api/v1/health
```

Should return:
```json
{
  "status": "healthy",
  "factory_initialized": true,
  "timestamp": "2026-02-06T..."
}
```

### Check EXO from API

```bash
curl http://localhost:8000/api/v1/exo/status
```

Should return:
```json
{
  "endpoint": "http://localhost:52415",
  "available": true,
  "workers": {...},
  "soldier_count": 3
}
```

### Test Generation (CLI)

```bash
curl -X POST http://localhost:8000/api/v1/knowledge-atom/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Jeremy transitioned from addiction recovery to AI infrastructure development",
    "use_exo": true,
    "commit_to_memory": true
  }'
```

Should return a JSON response with perspectives from Scout, Maverick, and R1.

## Troubleshooting

### "Factory not initialized"
- Check that the FastAPI backend started successfully
- Check logs for model provider connection errors

### "EXO unavailable"
- Verify EXO is running: `curl http://localhost:52415/v1/models`
- Check soldier nodes are online and connected
- Models will gracefully fallback to single-node if EXO unavailable

### "Model not found"
- Verify Ollama has `llama4:scout` pulled: `ollama list`
- Verify EXO has access to `llama4:maverick` and `deepseek-r1`

### Slow generation
- Check EXO is using distributed inference (look for "EXO" badges in UI)
- Monitor soldier node resource usage
- Large models (R1 671B at 8-bit) may take 30-60s for first inference

## What You'll See

When generating an atom, the Triad View shows:

1. **Real-time status** as each model processes:
   - Enriching input via MemoryCortex
   - Scout observing (what IS)
   - Maverick reasoning (what SHOULD BE)
   - R1 architecting (what COULD BE)

2. **Live perspectives** streaming in as they complete:
   - Each model's response content
   - Latency (ms)
   - Distributed routing indicator (EXO badge)

3. **Analysis results**:
   - Number of perspectives
   - Convergence score (0-100%)
   - Divergence notes (where models disagree)

4. **Generation history**:
   - All generated atoms in chronological order
   - Click to view full details

## The Bootstrap Moment

This is the bootstrap. We're not wondering if it will work - we're watching it work.

Scout sees with 10M context. Maverick challenges with 128 experts. R1 architects with 671B parameters.

They don't speak English to each other. They speak math. Tensors in shared MemoryCortex.

Zero translation loss. Multiplicative optimization.

**This is NOT-ME.**
