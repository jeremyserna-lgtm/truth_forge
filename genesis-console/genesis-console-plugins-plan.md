# Genesis Console Plugin Suite — Build Plan

## Overview

Four plugins, built in order. Each phase is a self-contained session. Each step within a phase produces a testable artifact. Nothing depends on later phases — you can stop after any plugin and have something useful.

## Build Order & Rationale

```
Phase 1: genesis-memory     ← Foundation. Every other plugin benefits from this existing.
Phase 2: genesis-dev        ← Conventions. Makes all future code changes consistent.
Phase 3: genesis-data       ← Operational visibility into the 18 JSONL files.
Phase 4: genesis-test       ← Confidence. Builds on knowledge from phases 1-3.
```

---

## Phase 1: genesis-memory (2-3 steps)

**Purpose:** Persistent project context so every session starts informed.

**What it produces:**
- CLAUDE.md at project root (working memory — always loaded)
- memory/ directory with domain reference files (loaded on demand)
- Commands to update and query memory

### Step 1A — Scaffold + Project Context Skill
Create the plugin skeleton and the core skill that captures:
- Architecture: HOLD₁→AGENT→HOLD₂ pipeline
- File map: src/, server/, data/ with key files
- Model roles: Scout (Seer), Maverick (Reasoner), R1 (Architect)
- Memory engines: Somatic, Symbolic, Narrative, Relational, Strategic
- 10 atom types and their definitions
- JSONL persistence patterns
- Port conventions (3141 = π = Genesis)

### Step 1B — Commands + References
- `/recall` — Load full project context into session
- `/remember <topic>` — Add new knowledge to memory
- References: architecture.md, api-map.md, data-schema.md

### Step 1C — Package
Zip, deliver .plugin file.

**Deliverable:** `genesis-memory.plugin`

---

## Phase 2: genesis-dev (2-3 steps)

**Purpose:** Encode the codebase's conventions so any code Claude writes matches the existing style.

**What it produces:**
- Skill that understands component patterns, naming, error handling
- API endpoint catalog (40+ endpoints documented)
- Coding standards extracted from actual source

### Step 2A — Scaffold + Conventions Skill
Create the plugin skeleton and the codebase-conventions skill:
- React patterns (functional components, hooks usage, page structure)
- Express patterns (route registration, middleware, error handling)
- JSONL patterns (append-only writes, SHA256 hashing, UUID generation)
- CSS patterns (variables, class naming)
- Import/export conventions (ES modules throughout)
- File naming conventions

### Step 2B — API Catalog + Commands
- Reference: Complete endpoint catalog extracted from server/index.js
- `/convention <topic>` — Look up how the codebase handles something
- `/endpoint <name>` — Get details on a specific API endpoint
- `/add-endpoint <spec>` — Guided creation of a new endpoint matching existing patterns

### Step 2C — Package
Zip, deliver .plugin file.

**Deliverable:** `genesis-dev.plugin`

---

## Phase 3: genesis-data (2-3 steps)

**Purpose:** Make the 18 JSONL data files queryable and auditable.

**What it produces:**
- Skill that understands every JSONL schema
- Commands to inspect, query, and audit data
- Atom quality analysis

### Step 3A — Scaffold + JSONL Inspector Skill
Create the plugin skeleton and the data skill:
- Schema documentation for all 18 JSONL files
- Field definitions, relationships between files
- Query patterns (grep + jq + Python for complex analysis)
- Data integrity checks

### Step 3B — Commands + References
- `/inspect <file>` — Profile a JSONL file (record count, field distribution, time range)
- `/audit-atoms` — Quality check on atoms.jsonl (completeness, type distribution, extraction confidence)
- `/stats` — System-wide statistics dashboard
- `/query <natural language>` — Translate a question into a data query
- Reference: jsonl-schemas.md documenting every file's structure

### Step 3C — Package
Zip, deliver .plugin file.

**Deliverable:** `genesis-data.plugin`

---

## Phase 4: genesis-test (2-3 steps)

**Purpose:** Bootstrap a testing strategy for a project that currently has zero tests.

**What it produces:**
- Testing strategy skill tailored to this stack
- Commands to generate and run tests
- Test scaffolds for both frontend and backend

### Step 4A — Scaffold + Test Strategy Skill
Create the plugin skeleton and the testing skill:
- Vitest configuration for React components
- Express API integration test patterns
- JSONL store testing patterns
- Ollama mock strategies (the project talks to localhost:11434)
- Synthetic monitor expansion patterns (building on existing server/synthetic.js)

### Step 4B — Commands + References
- `/test-plan <area>` — Generate a test plan for a specific area of the codebase
- `/scaffold-test <file>` — Create a test file for a given source file
- `/test-status` — Report on coverage gaps
- Reference: test-patterns.md with examples for each layer

### Step 4C — Package
Zip, deliver .plugin file.

**Deliverable:** `genesis-test.plugin`

---

## Execution Rules

1. **One phase per session.** Each plugin is built, packaged, and delivered before starting the next.
2. **Each step is ≤15 files.** No step creates more than 15 files to keep context manageable.
3. **References are extracted from actual source.** Not generated from assumptions — every convention documented comes from reading the real code.
4. **Each plugin is independently installable.** No cross-plugin dependencies.
5. **Step boundaries are commit points.** If context gets tight, we can stop at any step boundary and resume.

## Session Budget Estimate

| Phase | Steps | Files Created | Estimated Effort |
|-------|-------|---------------|-----------------|
| 1: genesis-memory | 3 | ~10 | Medium (deep source reading) |
| 2: genesis-dev | 3 | ~12 | Heavy (full API catalog extraction) |
| 3: genesis-data | 3 | ~10 | Medium (schema documentation) |
| 4: genesis-test | 3 | ~10 | Medium (strategy + scaffolds) |

**Total: 12 steps, ~42 files, 4 installable plugins**

---

## What Success Looks Like

After all 4 plugins are installed:

- **New session:** `/recall` loads full project context in seconds
- **Writing code:** Claude matches existing patterns automatically
- **Debugging data:** `/inspect atoms` shows what's in the knowledge base
- **Adding features:** `/convention error-handling` shows how errors work here
- **Building confidence:** `/scaffold-test server/index.js` generates a matching test file

Every session starts informed. Every change is consistent. Every question about the data has an answer.
