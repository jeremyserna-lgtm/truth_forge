# Existence Extraction Pipeline

**Date:** 2025-12-02
**Principle:** ONLY COPY. NEVER PROCESS.

---

## Core Principle

**Every state is a COMPLETE INDEPENDENT COPY.**
**Every change is just POINTERS to two states.**

If you copy correctly, you're done.
No transformation. No processing that can go wrong.
States are self-contained. Changes are just references.

---

## Stage 0 vs Stage 1

### Stage 0: Source Copy
**What exists in the source, exactly as it exists.**

- Native source data (ps output, lsof output, stat() results)
- Files already have changes implemented in them
- You get current_states but NO change entities
- **This is NOT your data. This is the SOURCE's data.**

```
Source (ps, lsof, filesystem)
    ↓
COPY EXACTLY (no IDs, no processing)
    ↓
source_copy table (raw_output blob)
```

### Stage 1: Sequenced States
**Add canonical IDs + implement changes as entities.**

- Takes Stage 0 copies
- Adds canonical IDs (state_0, state_1, state_n)
- Creates change entities by comparing states
- **Changes are the FIRST entities YOU add to native source**

```
Stage 0 (source_copy)
    ↓
Parse → Identify entities → Sequence states
    ↓
entities table (permanent identity)
states table (sequenced: state_0, state_1, ...)
changes table (derived: state_before → state_after)
```

### Why This Separation Matters

1. **Stage 0 is pristine** - You can always go back to raw source
2. **Stage 1 is derived** - Your canonical IDs and change entities are YOUR additions
3. **Changes don't exist natively** - They exist because YOU compare states
4. **You can reprocess** - If Stage 1 logic changes, reprocess from Stage 0

---

## Architecture: Versioned Existence

### Entities (permanent identity)
```
entity_id: entity_f1e8674ca17b
entity_type: process
identifier: pid:2314
name: zoom.us
```

### States (complete independent copies)
```
state_id: state_a31ce23d2763      (UNIQUE)
entity_id: entity_f1e8674ca17b
state_data: { complete copy of source }
observed_at: 2025-12-02T18:51:08
is_start_state: 1
```

Each state is self-contained. You can read any state without reading others.

### Changes (just pointers)
```
change_id: change_7631fd75bdb3    (UNIQUE)
state_before_id: state_a31ce23d2763
state_after_id: state_7631fd75bdb3
```

You don't implement the change. You have both complete states. Compare them if you want to know what changed.

---

## Tables

| Table | What | Independence |
|-------|------|--------------|
| `entities` | Permanent identity | Standalone |
| `states` | Complete copy at timestamp | Each state is independent |
| `changes` | Pointers: before → after | Just references |
| `sessions` | Session boundaries | Standalone |

---

## Data Flow

```
Source Data (ps, lsof, filesystem)
    ↓
COPY EXACTLY (no transformation)
    ↓
State (complete, independent, has ID)
    ↓
Compare to previous state
    ↓
If different: Create change (just pointers)
```

---

## Example: zoom.us Process

**Entity:**
```
entity_id: entity_f1e8674ca17b
identifier: pid:2314
name: zoom.us
state_count: 2
change_count: 1
```

**Start State (complete copy):**
```
state_id: state_a31ce23d2763
state_data: {
  "raw_line": "jeremyserna 2314 35.1 1.4 ... 43:40.32 zoom.us",
  "cpu": "35.1",
  "mem": "1.4",
  "time": "43:40.32"
}
```

**Change (just pointers):**
```
change_id: change_7631fd75bdb3
state_before_id: state_a31ce23d2763
state_after_id: state_7631fd75bdb3
```

**Current State (complete copy):**
```
state_id: state_7631fd75bdb3
state_data: {
  "raw_line": "jeremyserna 2314 37.5 1.4 ... 43:43.83 zoom.us",
  "cpu": "37.5",
  "mem": "1.4",
  "time": "43:43.83"
}
```

---

## Files

| File | Purpose |
|------|---------|
| `tools/stage0_source_copy.py` | Stage 0: Pure source copy |
| `tools/stage1_sequenced_states.py` | Stage 1: Add canonical IDs + change entities |
| `tools/versioned_existence_extractor.py` | Combined extractor (legacy) |
| `data/existence/stage0_source_copy.db` | Stage 0 buffer |
| `data/existence/stage1_sequenced_states.db` | Stage 1 buffer |

---

## Commands

```bash
# Stage 0: Copy source data
python3 tools/stage0_source_copy.py --status           # Check status
python3 tools/stage0_source_copy.py --interval 60      # Run continuous
python3 tools/stage0_source_copy.py --latest ps_aux    # Get latest copy

# Stage 1: Process into sequenced states
python3 tools/stage1_sequenced_states.py --status      # Check status
python3 tools/stage1_sequenced_states.py --process     # Process Stage 0 → Stage 1
python3 tools/stage1_sequenced_states.py --history entity_xxx  # Get entity history

# Legacy (combined Stage 0 + 1)
python3 tools/versioned_existence_extractor.py --status
python3 tools/versioned_existence_extractor.py --interval 60
```

---

## Why This Works

1. **Copy correctly = done.** No processing step to get wrong.
2. **States are independent.** Read any state without context.
3. **Changes are just pointers.** No transformation logic.
4. **Everything has ID.** Entity, state, change - all addressable.
5. **Complete data.** Each state has the full source data, not a diff.

---

## Multi-Layer Observation

### The Three Layers

| Layer | What It Watches | Timestamp Meaning |
|-------|-----------------|-------------------|
| **Persistence** | Where states are saved | End of state_n, start of state_n+1 |
| **Process** | Programs present/absent | Execution boundaries |
| **Event** | System actions initiated | Intention initiation |

### Watching Always (Present or Not)

```
NOT MONITORED              BEING MONITORED              NOT MONITORED
(state: absent)         (state_0...state_n)           (state: absent)
      │                         │                           │
      └────────┬────────────────┴─────────────────┬─────────┘
               │                                  │
          start_event                        stop_event
      (absent → present)                  (present → absent)
```

### Cross-Layer Correlation = Causality

```
EVENT LAYER:        [user clicks "Open Zoom"]
                              │
                         timestamp_A
                              │
PROCESS LAYER:      [zoom.us appears in ps]
                              │
                         timestamp_B
                              │
PERSISTENCE LAYER:  [state file written]
                              │
                         timestamp_C

GAP (A→B): intention_to_execution
GAP (B→C): execution_to_state
GAP (A→C): intention_to_state (total latency)
```

### Files

| File | Purpose |
|------|---------|
| `tools/layer_observer.py` | Multi-layer observation + correlation |
| `data/existence/layer_observations.db` | Layer observation buffer |

### Commands

```bash
# Multi-layer observation
python3 tools/layer_observer.py --status      # Check status
python3 tools/layer_observer.py --interval 5  # Run continuous
python3 tools/layer_observer.py --once        # Single observation
python3 tools/layer_observer.py --watch /path # Add persistence watch
```

---

## Complete Observer

**All processes, all layers, all timestamps - unified.**

| Layer | What | Captures |
|-------|------|----------|
| **process** | Every process | start, stop, change |
| **persistence** | 90+ app paths | create, modify |
| **network** | All connections | start, stop |
| **system** | User focus, display | focus, sleep, wake |

All observations have:
- `timestamp` (ISO format)
- `timestamp_ms` (epoch milliseconds for correlation)
- `subject_id` (unique identifier)
- `event_type` (start, stop, change, create, modify, focus)

```bash
python3 tools/complete_observer.py --status     # Check status
python3 tools/complete_observer.py --once       # Single observation
python3 tools/complete_observer.py --correlate  # Cross-layer correlations
python3 tools/complete_observer.py --interval 3 # Run continuous
```

---

## System Integration (Run at Login)

### Quick Commands

```bash
./tools/existence_force.sh start     # Start all services
./tools/existence_force.sh stop      # Stop all services
./tools/existence_force.sh status    # Show complete status
./tools/existence_force.sh once      # Force single extraction
./tools/existence_force.sh correlate # Show cross-layer correlations
```

### LaunchAgents (All Run at Login)

| Service | Interval | Purpose |
|---------|----------|---------|
| `com.truthengine.complete-observer` | 3s | ALL layers, ALL timestamps |
| `com.truthengine.layer-observer` | 5s | Cross-layer correlation |
| `com.truthengine.stage0` | 60s | Raw source copy |
| `com.truthengine.stage1-processor` | 5min | Sequenced states + changes |

### Files

| File | Purpose | Buffer |
|------|---------|--------|
| `tools/complete_observer.py` | All layers unified | `complete_observations.db` |
| `tools/layer_observer.py` | Cross-layer correlation | `layer_observations.db` |
| `tools/stage0_source_copy.py` | Pure source copy | `stage0_source_copy.db` |
| `tools/stage1_sequenced_states.py` | Sequenced states | `stage1_sequenced_states.db` |
| `tools/existence_force.sh` | Control all services | - |

Logs: `~/PrimitiveEngine/logs/`

### Manual Control

```bash
# Start/stop individual services
launchctl load ~/Library/LaunchAgents/com.truthengine.complete-observer.plist
launchctl unload ~/Library/LaunchAgents/com.truthengine.complete-observer.plist

# Check running services
launchctl list | grep truthengine
```

---

## What This System Guarantees

1. **Every process start/stop** - Captured within 3 seconds
2. **Every file state change** - Across 90+ application paths
3. **Every network connection** - Start and stop events
4. **Every user focus change** - Active application tracking
5. **All timestamps unified** - Millisecond precision, cross-layer correlation
6. **All changes as entities** - state_before → state_after with unique IDs
7. **Runs at login** - Automatic, continuous monitoring
8. **Force trigger available** - Manual extraction anytime
