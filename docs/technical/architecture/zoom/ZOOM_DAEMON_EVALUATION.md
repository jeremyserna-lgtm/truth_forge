> **DEPRECATED** - This document is superseded by [ZOOM_SOURCE_OF_TRUTH.md](../ZOOM_SOURCE_OF_TRUTH.md)
>
> The redesign proposed here has been implemented in `tools/zoom_daemon.py`.
> This document is kept for historical reference only.

---

# Zoom Daemon Evaluation and Redesign

**Date:** 2025-12-02
**Purpose:** Evaluate current daemons and design capture-store-release pipeline
**Status:** DEPRECATED - Implemented

---

## Current State: PROBLEMS

### 12 Zoom Tools (Redundant, Overlapping)

| File | Size | Purpose | Issues |
|------|------|---------|--------|
| `zoom_capture_robust.py` | 34KB | Multi-pathway capture | Uses AppleScript, memory leak |
| `zoom_chat_daemon.py` | 17KB | Chat capture | Overlaps with others |
| `zoom_enhanced_extractor.py` | 20KB | Enhanced extraction | Overlaps with session_extractor |
| `zoom_event_capture.py` | 21KB | Event-driven capture | Uses AppleScript, memory leak |
| `zoom_existence_watcher.py` | 58KB | Existence tracking | Too complex, partial implementation |
| `zoom_identity_mapper.py` | 11KB | Identity mapping | Utility, not daemon |
| `zoom_import_avatars.py` | 5KB | Avatar import | Utility, not daemon |
| `zoom_meeting_group_detector.py` | 10KB | Meeting detection | Utility |
| `zoom_session_extractor.py` | 27KB | Session extraction | Core, but has memory leak |
| `zoom_timeline_capture.py` | 21KB | Timeline capture | Overlaps with others |
| `zoom_ui_state_extractor.py` | 24KB | UI state | Uses AppleScript heavily |
| `zoom_user_experience_watcher.py` | 39KB | UX capture | New, needs integration |

### 3 Active Daemons at Login (All have issues)

1. **com.truthengine.zoom-event-capture** → `zoom_event_capture.py`
   - Problem: Memory leak (System Events)
   - Problem: No BigQuery pipeline
   - Problem: Local JSON accumulation

2. **com.truthengine.zoom-robust-capture** → `zoom_capture_robust.py`
   - Problem: Memory leak (System Events)
   - Problem: Aggressive polling (1s)
   - Problem: No cleanup after capture

3. **com.truthengine.zoom-session-daemon** → `zoom_session_extractor.py`
   - Problem: Memory leak (fixed but needs testing)
   - Problem: 60s interval (misses rapid changes)
   - Problem: No BigQuery integration

### Core Issues

1. **Memory**: AppleScript calls System Events which accumulates memory
2. **Redundancy**: 3 daemons doing similar work
3. **No Pipeline**: Data stuck in local JSON files
4. **No Cleanup**: Local disk fills up
5. **No Validation**: Can't verify data integrity
6. **Complexity**: Too many files, hard to maintain

---

## Redesign: CAPTURE → STORE → RELEASE

### Single Daemon Principle

**ONE daemon** that does:

```
OBSERVE → CAPTURE → WRITE_LOCAL → CLEAR_MEMORY → (periodic) UPLOAD_BIGQUERY → VALIDATE → DELETE_LOCAL
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ZOOM APPLICATION                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │Participant│  │   Chat   │  │  Gallery │  │ My State │             │
│  │   List   │  │ Messages │  │   View   │  │Mute/Video│             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
└───────┼─────────────┼─────────────┼─────────────┼───────────────────┘
        │             │             │             │
        ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIFIED ZOOM DAEMON                               │
│                                                                      │
│  1. OBSERVE (every 5s)                                              │
│     - Read Zoom UI via accessibility API                            │
│     - Detect changes from previous state                            │
│     - Create observation record                                      │
│                                                                      │
│  2. CAPTURE (on change)                                             │
│     - Record who/what/when                                          │
│     - Hash for deduplication                                        │
│     - Timestamp everything                                          │
│                                                                      │
│  3. WRITE LOCAL (immediately)                                       │
│     - SQLite buffer (minimal footprint)                             │
│     - Append-only (no updates)                                      │
│                                                                      │
│  4. CLEAR MEMORY (after write)                                      │
│     - Release AppleScript/System Events                             │
│     - Clear internal state (keep only hashes)                       │
│     - Force garbage collection                                       │
│                                                                      │
│  5. UPLOAD BIGQUERY (batched, daily)                                │
│     - Respect daily write limits (10GB/table/day)                   │
│     - Upload in batches of 1000 rows                                │
│     - Track upload progress                                          │
│                                                                      │
│  6. VALIDATE (after upload)                                         │
│     - Query BigQuery to confirm row count                           │
│     - Verify checksums match                                        │
│                                                                      │
│  7. DELETE LOCAL (after validation)                                 │
│     - Delete only confirmed uploaded data                           │
│     - Keep failed uploads for retry                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Memory Management

```python
def capture_cycle():
    # 1. OBSERVE
    data = observe_zoom_state()  # AppleScript call

    # 2. CAPTURE changes
    changes = detect_changes(data, previous_hashes)

    # 3. WRITE to local SQLite
    write_to_buffer(changes)

    # 4. CLEAR MEMORY
    del data
    del changes
    clear_system_events()  # Kill System Events process
    gc.collect()  # Force garbage collection

    # Keep only hashes for dedup (minimal memory)
    previous_hashes = {hash(x) for x in get_current_hashes()}
```

### Local Buffer Schema (SQLite)

```sql
-- Minimal footprint, append-only
CREATE TABLE zoom_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    observation_type TEXT NOT NULL,  -- 'participant', 'chat', 'state'
    observation_hash TEXT NOT NULL,  -- For dedup
    observation_data TEXT NOT NULL,  -- JSON blob
    observed_at TEXT NOT NULL,
    uploaded_to_bq INTEGER DEFAULT 0,
    uploaded_at TEXT,
    validated INTEGER DEFAULT 0
);

CREATE INDEX idx_uploaded ON zoom_observations(uploaded_to_bq);
CREATE INDEX idx_hash ON zoom_observations(observation_hash);
```

### BigQuery Daily Upload

```python
# Respect BigQuery limits: 10GB/table/day, 1000 streaming inserts/sec
DAILY_BATCH_SIZE = 10000  # rows per upload
BATCH_DELAY_SECONDS = 60  # wait between batches

def daily_upload():
    pending = get_unuploaded_observations()

    for batch in chunks(pending, DAILY_BATCH_SIZE):
        upload_to_bigquery(batch)
        mark_as_uploaded(batch)
        time.sleep(BATCH_DELAY_SECONDS)

    # Validate
    validate_bigquery_counts()

    # Delete confirmed local data
    delete_validated_local()
```

---

## Implementation Plan

### Phase 1: Single Unified Daemon

**File:** `zoom_unified_daemon.py`

**Replaces:**
- `zoom_event_capture.py`
- `zoom_capture_robust.py`
- `zoom_session_extractor.py`
- `zoom_user_experience_watcher.py`

**Features:**
- Single entry point
- Memory management (clear after each cycle)
- SQLite buffer (not JSON files)
- Configurable intervals

### Phase 2: BigQuery Pipeline

**File:** `zoom_bq_uploader.py`

**Features:**
- Daily batch upload
- Under write limits
- Validation after upload
- Local cleanup after validation

### Phase 3: Cleanup and Deprecation

**Actions:**
- Remove old daemons from LaunchAgents
- Archive old tools (don't delete yet)
- Document the new system

---

## LaunchAgent Configuration

**Single daemon:** `com.truthengine.zoom-unified.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.truthengine.zoom-unified</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>-u</string>
        <string>/Users/jeremyserna/PrimitiveEngine/tools/zoom_unified_daemon.py</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <!-- Memory management: restart if memory exceeds 100MB -->
    <key>HardResourceLimits</key>
    <dict>
        <key>MemoryLimit</key>
        <integer>104857600</integer>
    </dict>

    <key>ProcessType</key>
    <string>Background</string>

    <key>LowPriorityIO</key>
    <true/>

    <key>Nice</key>
    <integer>10</integer>

    <key>StandardOutPath</key>
    <string>/Users/jeremyserna/Documents/zoom_sessions/unified_daemon.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/jeremyserna/Documents/zoom_sessions/unified_daemon.error.log</string>
</dict>
</plist>
```

---

## Validation Checklist

Before this is production-ready:

- [ ] Memory stays under 100MB during continuous operation
- [ ] System Events memory is cleared every 10 scans
- [ ] Local SQLite buffer stays under 100MB
- [ ] BigQuery upload succeeds under daily limits
- [ ] Local data is deleted ONLY after BigQuery validation
- [ ] No data loss during Zoom session start/end
- [ ] Complete capture of: participants, chat, state changes
- [ ] Works at login without overwhelming system

---

## Summary

**Current:** 12 files, 3 daemons, memory leaks, no pipeline
**Target:** 2 files, 1 daemon, memory management, BigQuery pipeline, validated cleanup
