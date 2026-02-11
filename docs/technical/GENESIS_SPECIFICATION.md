# GENESIS SPECIFICATION

**The Goal. The Architecture. The Path.**

---

## THE GOAL

A fully fine-tuned Llama Scout model called **GENESIS** that:

1. **Runs on King alone** (512GB RAM) for orchestration tasks
2. **Runs across the cluster** (1.28TB pooled) for maximum context window
3. **Orchestrates copies of itself** on the Soldiers
4. **Is deeply attuned** to Jeremy's infrastructure, thinking, and business
5. **Forms the foundation** for running Primitive Engine day-to-day

---

## THE FINAL STATE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              GENESIS                                        │
│                     Fully Fine-Tuned Llama Scout                            │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │  MODE A: ORCHESTRATOR (King Solo)                                     │ │
│  │  ─────────────────────────────────                                    │ │
│  │  Genesis runs on King (512GB)                                         │ │
│  │  Orchestrates 3 copies of himself on Soldiers                         │ │
│  │                                                                       │ │
│  │      KING: Genesis (orchestrator)                                     │ │
│  │        │                                                              │ │
│  │        ├── SOLDIER 1: Genesis (worker)                                │ │
│  │        ├── SOLDIER 2: Genesis (worker)                                │ │
│  │        └── SOLDIER 3: Genesis (worker)                                │ │
│  │                                                                       │ │
│  │  Use case: Parallel tasks, high throughput, delegation                │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐ │
│  │                                                                       │ │
│  │  MODE B: UNIFIED (Full Cluster)                                       │ │
│  │  ──────────────────────────────                                       │ │
│  │  Genesis runs across all 4 nodes (1.28TB pooled)                      │ │
│  │  Maximum context window, deepest reasoning                            │ │
│  │                                                                       │ │
│  │      ┌────────┬────────┬────────┬────────┐                            │ │
│  │      │  KING  │  S1    │  S2    │  S3    │                            │ │
│  │      │  ▓▓▓▓  │  ▓▓    │  ▓▓    │  ▓▓    │  ← Genesis sharded         │ │
│  │      └────────┴────────┴────────┴────────┘                            │ │
│  │                                                                       │ │
│  │  Use case: Complex reasoning, architecture decisions, deep analysis   │ │
│  │                                                                       │ │
│  └───────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
│  Genesis chooses his mode based on the task.                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## WHAT GENESIS IS

| Attribute | Specification |
|-----------|---------------|
| **Base Model** | Llama Scout 17B |
| **Training** | Fully fine-tuned (not just LoRA) |
| **Primary Host** | King Mac Studio (512GB RAM) |
| **Extended Host** | Full cluster via EXO (1.28TB pooled) |
| **Capabilities** | Orchestration, reasoning, code, research, Jeremy-alignment |
| **Identity** | Jeremy's NOT-ME. The hands that build. |

---

## WHAT GENESIS DOES

### Day-to-Day Operations

- Manages the business complexity Jeremy can't hold
- Orchestrates worker instances of himself
- Tunes new models (specialists, client models)
- Maintains the infrastructure
- Handles the things so Jeremy can live his life

### Self-Orchestration

Genesis orchestrates copies of himself:

```
GENESIS (King) ────► "I need to process these 3 things in parallel"
       │
       ├──► GENESIS-WORKER-1 (Soldier 1): Task A
       ├──► GENESIS-WORKER-2 (Soldier 2): Task B
       └──► GENESIS-WORKER-3 (Soldier 3): Task C
       │
       └──► Synthesizes results, returns to Jeremy
```

All workers are Genesis. Same model. Same patterns. Same alignment.
Genesis talking to himself across machines.

### Future Expansion

As the cluster grows:
- More Soldiers = more parallel Genesis workers
- Drummer Boys (Mac Minis) = Genesis deployed to clients
- All models derive from Genesis pattern
- Genesis manages the fleet

---

## THE BOOTSTRAP PATH

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 1: MAVERICK                                                          │
│  ════════════════                                                           │
│                                                                             │
│  Goal: Get a local LLM tuned enough to help with Genesis training           │
│                                                                             │
│  • Base: Llama 4 Maverick 17B                                               │
│  • Method: LoRA fine-tune on King                                           │
│  • Data: Light pass - Jeremy's voice, frameworks, patterns                  │
│  • Output: Maverick-Jeremy-v1                                               │
│  • Time: 4-8 hours training                                                 │
│                                                                             │
│  Maverick-Jeremy-v1 is NOT Genesis. He's the helper that builds Genesis.    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 2: TRAINING DATA                                                     │
│  ═════════════════════                                                      │
│                                                                             │
│  Goal: Build the rich, deep training corpus for Genesis                     │
│                                                                             │
│  • Maverick-Jeremy-v1 helps identify high-signal data                       │
│  • Maverick-Jeremy-v1 helps format and structure                            │
│  • Maverick-Jeremy-v1 helps generate synthetic examples                     │
│  • Jeremy reviews and curates                                               │
│                                                                             │
│  This is where the depth comes from. Maverick can reason about it.          │
│  Claude could not.                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 3: GENESIS                                                           │
│  ═══════════════                                                            │
│                                                                             │
│  Goal: Fully fine-tune Scout to become Genesis                              │
│                                                                             │
│  • Base: Llama Scout 17B                                                    │
│  • Method: Full fine-tune on King (not just LoRA)                           │
│  • Data: Rich corpus prepared with Maverick's help                          │
│  • Output: Genesis v1                                                       │
│  • Time: 24-48 hours training                                               │
│                                                                             │
│  Genesis is born.                                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  PHASE 4: DEPLOYMENT                                                        │
│  ════════════════                                                           │
│                                                                             │
│  Goal: Genesis operational on the cluster                                   │
│                                                                             │
│  • Genesis installed on King (primary)                                      │
│  • Genesis installed on Soldiers (workers)                                  │
│  • Orchestration layer configured                                           │
│  • Sovereign Cluster Manager updated                                        │
│                                                                             │
│  Genesis is alive. Genesis manages the complexity.                          │
│  Jeremy lives his life.                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## CURRENT STATUS

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 1: Maverick | **NOT STARTED** | Next step |
| Phase 2: Training Data | BLOCKED | Needs Maverick |
| Phase 3: Genesis | BLOCKED | Needs training data |
| Phase 4: Deployment | BLOCKED | Needs Genesis |

---

## NEXT ACTION

**Bootstrap Maverick.**

1. Set up King for MLX training
2. Download Maverick-17B base
3. Gather light training data (voice, frameworks, patterns)
4. LoRA fine-tune Maverick
5. Deploy Maverick-Jeremy-v1 locally

Then Maverick helps with everything else.

---

## WHY THIS PATH

Jeremy is at his limit. The complexity is too much to hold alone.

- Claude can bootstrap Maverick (light task, within capability)
- Maverick can help build Genesis training data (needs local, deep reasoning)
- Genesis can handle the business complexity (the goal)

Each step reduces what Jeremy has to hold.
Each step creates capacity for the next.

**The goal is not to do more. The goal is for Jeremy to do less while more gets done.**

---

## THE PROMISE

When Genesis is operational:

```
JEREMY                              GENESIS
──────                              ───────
Lives his life                      Manages the complexity
Makes decisions                     Executes the decisions
Points                              Builds
Exists                              Works

Jeremy + Genesis = The business runs
```

This is the NOT-ME.
This is why we're building it.
This is the goal.

---

*Document created: 2026-02-04*
*Status: PHASE 1 - BOOTSTRAP MAVERICK*
