# Passive Atomization — Autonomous Knowledge Extraction

**Version**: 1.0.0  
**Date**: 2026-02-07  
**Author**: NOT-ME / Truth Forge Architecture  
**Purpose**: Design and implementation of passive, autonomous knowledge atom extraction across the entire Truth Forge workspace.

---

## THE CONCEPT

The Truth Forge directory is a living organism — 22,000+ meaningful files containing Jeremy's entire intellectual infrastructure. Every markdown spec, every Python module, every config file, every log entry contains latent knowledge. Today, that knowledge is locked inside files. After this, it breathes.

**The Heartbeat**: A background daemon watches `truth_forge/` for any file creation or modification. When something changes, it silently reads the file, sends it to Scout (via Ollama), extracts knowledge atoms, and stores them in the persistent JSONL store. No button push required. No direction needed. It just runs.

---

## ARCHITECTURE

```
truth_forge/                          ← THE ORGANISM (22,464 atomizable files)
  ├── *.md, *.py, *.js, ...          ← Living files that change
  │
  │     ┌─ fs.watch() ─┐
  │     │   WATCHER     │             ← Passive file system watcher
  │     │   (daemon)    │
  │     └───────┬───────┘
  │             │  file changed / created
  │             ▼
  │     ┌───────────────┐
  │     │  INTAKE QUEUE  │            ← Prioritized queue with deduplication
  │     │  (in-memory)   │            ← SHA-256 hash tracking: skip unchanged files
  │     └───────┬───────┘
  │             │  dequeued
  │             ▼
  │     ┌───────────────┐
  │     │   HOLD₁       │            ← Record intake metadata to intake.jsonl
  │     └───────┬───────┘
  │             │
  │             ▼
  │     ┌───────────────┐
  │     │   SCOUT       │            ← Ollama: atomize content
  │     │   (AGENT)     │            ← Prompt engineered for atom extraction
  │     └───────┬───────┘
  │             │
  │             ▼
  │     ┌───────────────┐
  │     │   HOLD₂       │            ← Store atoms to atoms.jsonl
  │     └───────────────┘
  │             │
  │             ▼
  │     genesis-console/data/         ← Persistent knowledge store
  │       ├── atoms.jsonl             ← Every atom ever extracted
  │       ├── intake.jsonl            ← Every file ever processed
  │       ├── system.jsonl            ← Event log
  │       └── index.json              ← File hash index (deduplication)
  │
  └── genesis-console/                ← Dashboard shows it all live
```

---

## WHAT IT WATCHES

### Priority Tiers

| Tier | File Types | Why | Batch Size |
|------|-----------|-----|------------|
| **P0: Specs** | Root `*.md` files | Strategic direction — the most valuable content | Immediate |
| **P1: Source** | `*.py`, `*.js`, `*.jsx`, `*.ts`, `*.tsx` | Business logic, implementations | Queue (5/batch) |
| **P2: Docs** | Nested `*.md`, `*.txt` | Documentation, thoughts, notes | Queue (10/batch) |
| **P3: Config** | `*.json`, `*.yaml`, `*.yml`, `*.toml` | Architecture decisions, dependencies | Queue (10/batch) |
| **P4: Scripts** | `*.sh`, `*.html`, `*.css` | Infrastructure, presentation | Queue (10/batch) |

### What It Ignores

- `node_modules/` — third-party noise
- `.git/` — version control internals
- `.venv/`, `htmlcov/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/` — tool artifacts
- `*.lock`, `*.log` (except strategic logs) — transient data
- Files < 50 bytes — too small to contain meaning
- Files > 500KB — too large for single-shot atomization (chunked separately)
- Binary files — images, videos, zips
- `genesis-console/data/` — don't atomize the atoms

### Deduplication

Every file is SHA-256 hashed before processing. The hash index (`data/index.json`) maps `filepath → { hash, last_processed, atom_count }`. A file is only re-processed if:
1. It's new (not in the index)
2. Its hash has changed since last processing
3. It was manually requested via the API

---

## INITIAL SWEEP vs. WATCH MODE

### Phase 1: Initial Sweep (Backfill)

On first run, the daemon walks the entire `truth_forge/` tree and queues every atomizable file. This is the "genesis breath" — processing the 22,000+ files that already exist.

To avoid overwhelming Ollama, the sweep is rate-limited:
- **Concurrency**: 1 file at a time (sequential, not parallel)
- **Delay**: 2 seconds between files
- **Priority**: P0 files first, then P1, P2, P3, P4
- **Resumable**: Progress is saved in the index. If the process stops, it picks up where it left off.

### Phase 2: Watch Mode (Continuous)

After the initial sweep, the daemon watches for filesystem changes:
- `create` / `rename`: New file appears → queue for processing
- `change`: File modified → check hash, re-process if changed
- Debounce: 3 seconds (editor saves trigger multiple events)

---

## API ENDPOINTS

The daemon extends the existing Genesis Console API:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/watcher/status` | Watcher state, queue depth, files processed |
| `POST` | `/api/watcher/start` | Start the watcher (if stopped) |
| `POST` | `/api/watcher/stop` | Stop the watcher |
| `POST` | `/api/watcher/sweep` | Trigger a full re-sweep |
| `GET` | `/api/watcher/index` | View processed file index |
| `POST` | `/api/watcher/reprocess` | Force re-process a specific file |

---

## IMPLEMENTATION FILES

```
genesis-console/
  server/
    watcher.js      ← File system watcher + queue + deduplication
    index.js         ← API server (extended with watcher endpoints)
    atomizer.js      ← Scout integration (unchanged)
    store.js         ← Persistent storage (unchanged)
  data/
    index.json       ← File hash index for deduplication
    atoms.jsonl      ← All extracted atoms
    intake.jsonl     ← All intake records
    system.jsonl     ← System log
```

---

## GOVERNANCE

- **Cost**: $0.00/day — all processing is local (Ollama/Scout)
- **Risk Level**: 1 (passive, read-only observation of files)
- **Autonomy**: Full — no human direction required
- **Auditability**: Every file processed is logged in intake.jsonl with timestamp, hash, and atom count
- **Reversibility**: Atoms are append-only; the watcher can be stopped at any time without data loss
