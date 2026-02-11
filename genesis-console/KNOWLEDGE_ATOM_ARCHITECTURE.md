# Knowledge Atom Architecture — Three-Layer System

**Version**: 1.0.0  
**Date**: 2026-02-07  
**Purpose**: Self-aware, self-reinforcing knowledge atom production across all of Truth Forge.

---

## THE THREE LAYERS

The Knowledge Atom system operates at three concentric levels. Each layer depends on the one below it and feeds the one above it.

```
     ┌─────────────────────────────────────────────────┐
     │              META LAYER                         │
     │         "Paradigm Reflector"                    │
     │                                                 │
     │   Uses Scout to assess the knowledge atom       │
     │   paradigm itself. Produces atoms ABOUT atoms.  │
     │   Answers: Is this working? Where are gaps?     │
     │   How should the paradigm evolve?               │
     │                                                 │
     │   Outputs: paradigm_atoms — atoms about the     │
     │   system's own knowledge production             │
     ├─────────────────────────────────────────────────┤
     │           SUPPORTIVE LAYER                      │
     │        "Coverage Assessor"                      │
     │                                                 │
     │   Actively ensures atom production occurs       │
     │   everywhere it can. Scans the codebase for     │
     │   unatomized regions, scores coverage, and      │
     │   queues files that need attention.              │
     │                                                 │
     │   Tracks: coverage %, gap identification,       │
     │   production rate, quality distribution          │
     ├─────────────────────────────────────────────────┤
     │              CORE LAYER                         │
     │          "Passive Watcher"                      │
     │                                                 │
     │   Watches truth_forge/ for file changes.        │
     │   Sends content to Scout via Ollama.            │
     │   Stores atoms in append-only JSONL.            │
     │   SHA-256 dedup. Priority queuing.              │
     │                                                 │
     │   Files: watcher.js, atomizer.js, store.js      │
     └─────────────────────────────────────────────────┘
```

---

## LAYER 1: CORE — Passive Watcher (`watcher.js`)

**Status**: Built. Running.

**What it does**:
- Watches the entire `truth_forge/` directory tree via chokidar
- Queues new/changed files by priority (P0 specs → P4 scripts)
- SHA-256 deduplicates to skip unchanged files
- Sends file content to Scout for atomization
- Stores atoms in `data/atoms.jsonl`, intake records in `data/intake.jsonl`
- Rate-limited: 1 file at a time, 2s delay between files
- Auto-starts when Ollama comes online

**What it tracks**:
- Files processed, atoms extracted, queue depth, error count

---

## LAYER 2: SUPPORTIVE — Coverage Assessor (`coverage.js`)

**What it does**:
- Periodically scans truth_forge/ to build a coverage map
- Identifies "dark zones" — directories and files with zero or stale atom coverage
- Scores each directory by: files total, files atomized, atoms per file, freshness
- Produces a coverage report as a core system metric
- Queues under-covered files into the watcher for processing
- Ensures no corner of the codebase goes un-examined

**Coverage Dimensions**:

| Dimension | Metric | Target |
|-----------|--------|--------|
| **Breadth** | % of atomizable files processed | > 80% |
| **Depth** | Average atoms per file | > 3 |
| **Freshness** | % of files re-processed after modification | > 90% |
| **Quality** | Average confidence across all atoms | > 0.75 |
| **Type Diversity** | Distinct atom types produced | All 10 types present |

**Cycle**: Runs every 10 minutes. Each cycle:
1. Walk truth_forge/ tree
2. Compare against file index (data/index.json)
3. Score each directory
4. Identify gaps (unprocessed files, stale files, low-atom files)
5. Queue gap files into the watcher
6. Emit a coverage report to data/coverage.jsonl

---

## LAYER 3: META — Paradigm Reflector (`reflector.js`)

**What it does**:
- Uses Scout to reason about the knowledge atom system itself
- Periodically generates "meta-atoms" — knowledge about the system's own knowledge production
- Asks questions like:
  - "What patterns emerge from the atoms we've collected?"
  - "Which areas of the codebase produce the richest knowledge?"
  - "Are there contradictions between atoms from different sources?"
  - "What does the distribution of atom types tell us about the codebase?"
  - "How should the atomization prompt evolve based on results?"
- Produces atoms of type `meta_pattern` and `synthesis`
- Feeds insights back into the system to improve future atomization
- Tracks the health of the paradigm itself as a first-class metric

**Reflection Cycle**: Runs every 30 minutes (or after every 100 new atoms). Each cycle:
1. Read the last N atoms from data/atoms.jsonl
2. Read the coverage report from data/coverage.jsonl
3. Build a reflection prompt with system state + recent atoms
4. Send to Scout: "Assess the knowledge atom paradigm"
5. Store resulting meta-atoms
6. Log assessment to data/reflections.jsonl

**Self-Reference**: The reflector's own output IS atoms. So the system literally watches itself produce, assesses that production, and produces knowledge about the production. This is the recursive loop.

---

## DATA FLOW

```
truth_forge/
  └── [any file changes]
        │
        ▼
  ┌─────────────┐
  │ CORE LAYER  │  Watcher detects change → atomizes → stores
  │ watcher.js  │
  └──────┬──────┘
         │ atoms stored in data/atoms.jsonl
         ▼
  ┌──────────────────┐
  │ SUPPORTIVE LAYER │  Scans for coverage gaps → queues missing files
  │ coverage.js      │  into the watcher
  └──────┬───────────┘
         │ coverage report + gap identification
         ▼
  ┌──────────────────┐
  │   META LAYER     │  Reflects on atom production → produces meta-atoms
  │ reflector.js     │  → feeds back into atoms.jsonl
  └──────────────────┘
         │
         └──→ meta-atoms stored in same atoms.jsonl
              (the system watches itself grow)
```

---

## API ENDPOINTS

### Core (existing)
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/watcher/status` | Watcher state |
| `POST` | `/api/watcher/start` | Start watcher |
| `POST` | `/api/watcher/stop` | Stop watcher |

### Supportive (new)
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/coverage/report` | Current coverage metrics |
| `GET` | `/api/coverage/gaps` | Unatomized / stale regions |
| `POST` | `/api/coverage/scan` | Trigger a coverage scan |

### Meta (new)
| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/reflector/status` | Reflector state + last assessment |
| `GET` | `/api/reflector/insights` | Recent meta-atoms and paradigm health |
| `POST` | `/api/reflector/reflect` | Trigger a reflection cycle |

---

## GOVERNANCE

- **Autonomy**: All three layers operate autonomously. No human direction required.
- **Cost**: $0.00/day — all processing is local via Ollama/Scout.
- **Self-Healing**: If Ollama goes offline, all layers pause and resume when it returns.
- **Audit Trail**: Every action is logged in JSONL files. Every atom has provenance.
- **The Immutable Pattern**: The system cannot modify source files. It only reads and produces atoms.
