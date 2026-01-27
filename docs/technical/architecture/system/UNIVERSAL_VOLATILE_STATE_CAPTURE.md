# Universal Volatile State Capture System

**Date:** 2025-12-02
**Status:** DESIGN - Ready for implementation
**Purpose:** Capture ALL volatile states from ANY system to discover what data exists

---

## THE CRITICAL PRINCIPLE: Mirror How It Actually Exists

**DO NOT invent structure. Capture the way the system stores it.**

### Investigation Results (2025-12-02)

We investigated how volatile states ACTUALLY exist in systems:

| System | How It Actually Stores Volatile State | What We Capture |
|--------|--------------------------------------|-----------------|
| **Zoom Chat** | Individual message elements in scrollable table (no aggregate entity) | Individual message existence, NOT an invented "conversation" |
| **Processes** | Individual process memory spaces (no OS aggregate) | Individual process existence |
| **Temp Files** | Individual files (no session aggregate) | Individual file existence |
| **Clipboard** | Single entity at a time (OS maintains as one thing) | The clipboard state as one entity |

### The Rule

```
IF the system stacks individuals together (displayed as one thing)
   → Capture individuals (because that's what exists)

IF the system creates an aggregate with its own identifier
   → Capture the aggregate (because that's what exists)

IF the system has BOTH individuals AND an aggregate identifier
   → Capture BOTH (because both exist)

NEVER invent structure that doesn't exist in the source system.
```

### Why This Matters

1. **Efficiency**: Systems do the most efficient thing possible
2. **Truth**: We're capturing what EXISTS, not our interpretation
3. **Fidelity**: When we later need to understand the volatile state, we see it as the system saw it
4. **No Lost Information**: We don't collapse individual items into aggregates that lose detail

---

## The Vision

```
VOLATILE STATE (Any System)          BIGQUERY (Permanent)
========================            ===================

Unknown app creates volatile  →     Captured as-is
                                    ↓
Unknown system reacts to you  →     Captured as-is
                                    ↓
Unknown process stores temp   →     Captured as-is
                                    ↓
                              NOW YOU CAN SEE:
                              - What volatile states exist
                              - What systems create them
                              - What they contain
                              - What you lose when they vanish
                              - What persistent systems they imply
```

---

## The Insight

**If a system creates volatile states, it probably also creates persistent states.**

By capturing volatile states:
1. **Discover unknown data sources** - "I didn't know this app was tracking X"
2. **Find systems reacting to you** - "This process spikes when I do Y"
3. **Identify what you're losing** - "Every time Z ends, I lose W"
4. **Bootstrap knowledge** - Capture first, understand later

---

## What Are Volatile States?

On macOS, volatile states include:

### Process Memory
- Application heap/stack data
- In-memory caches
- Session state
- Undo buffers

### Temporary Files
- `/tmp/*`
- `~/Library/Caches/*`
- App-specific temp directories
- `.DS_Store` files

### System Events
- Accessibility events (UI changes)
- NSNotificationCenter events
- FSEvents (file system changes)
- Network activity

### UI State
- Window positions, sizes
- Active application
- Clipboard contents
- Menu bar state

### Process State
- Running processes
- Open file handles
- Network connections
- Environment variables

---

## Universal Capture Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  UNIVERSAL VOLATILE MONITOR                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   FSEvents  │  │ Accessibility│  │  Process    │              │
│  │   Monitor   │  │   Monitor   │  │  Monitor    │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         ▼                ▼                ▼                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              VOLATILE STATE COLLECTOR                    │    │
│  │                                                          │    │
│  │  On ANY change:                                          │    │
│  │    1. Capture entire state as JSON                       │    │
│  │    2. Tag with source, timestamp, trigger                │    │
│  │    3. Store to BigQuery (no parsing)                     │    │
│  │    4. Move on                                            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                            │                                     │
│                            ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                     BIGQUERY                             │    │
│  │                                                          │    │
│  │  volatile_states_universal                               │    │
│  │    - volatile_id                                         │    │
│  │    - capture_timestamp                                   │    │
│  │    - source_system (zoom, chrome, finder, etc)           │    │
│  │    - source_type (process, file, ui, network)            │    │
│  │    - trigger_event (what caused the capture)             │    │
│  │    - raw_state_json (ENTIRE state, no parsing)           │    │
│  │    - state_size_bytes                                    │    │
│  │    - checksum                                            │    │
│  │                                                          │    │
│  │  QUERY LATER TO DISCOVER:                                │    │
│  │    - What systems produce volatile states?               │    │
│  │    - What data do they contain?                          │    │
│  │    - What patterns correlate with my activity?           │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Strategy

### Phase 1: Monitor Known Volatile Sources

Start with sources we know produce volatile states:

| Source | Type | Monitor Method |
|--------|------|----------------|
| Zoom chat | Process UI | Accessibility API |
| Chrome tabs | Process UI | Accessibility API |
| Clipboard | System | NSPasteboard observer |
| Active window | System | NSWorkspace notifications |
| Temp files | Filesystem | FSEvents on /tmp, ~/Library/Caches |
| Running processes | Process | Process enumeration |

### Phase 2: Expand to Discovery Mode

Watch for ANY system that creates volatile state patterns:

```python
# Capture ANY FSEvent in watched directories
# Capture ANY accessibility event
# Capture ANY process state change
# Store everything, analyze later
```

### Phase 3: Bootstrap Unknown Systems

Query BigQuery to discover:
```sql
-- What systems are creating volatile states I didn't know about?
SELECT source_system, COUNT(*) as volatile_count
FROM volatile_states_universal
WHERE source_system NOT IN ('zoom', 'chrome', 'finder')  -- Known systems
GROUP BY source_system
ORDER BY volatile_count DESC;

-- What data is in these unknown volatile states?
SELECT raw_state_json
FROM volatile_states_universal
WHERE source_system = 'unknown_app_discovered'
LIMIT 10;
```

---

## BigQuery Schema

```sql
-- Universal volatile state capture
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.system_capture.volatile_states_universal` (
    -- Identity
    volatile_id STRING NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,

    -- Source identification
    source_system STRING,           -- zoom.us, Chrome, Finder, Terminal, etc.
    source_process_id INT64,        -- PID if applicable
    source_process_name STRING,     -- Process name
    source_type STRING,             -- process, file, ui, network, clipboard

    -- Trigger
    trigger_event STRING,           -- what_caused_capture
    trigger_details STRING,         -- additional trigger context

    -- The volatile state - RAW, NO PARSING
    raw_state_json STRING,          -- Entire state as JSON string
    state_size_bytes INT64,
    state_checksum STRING,          -- For deduplication

    -- Context
    active_application STRING,      -- What app was active when captured
    active_window_title STRING,
    user_idle_seconds INT64,        -- How long user has been idle

    -- Discovery tracking
    is_known_source BOOL,           -- Did we already know about this source?
    discovery_notes STRING,         -- Notes if this is a new discovery

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    ingestion_date DATE NOT NULL
)
PARTITION BY ingestion_date
CLUSTER BY source_system, source_type
OPTIONS(
    description='Universal volatile state capture - all systems, all sources',
    labels=[
        ("system", "universal_capture"),
        ("purpose", "volatile_discovery"),
        ("data_quality", "raw")
    ]
);
```

---

## Monitor Implementation

### Core Monitor Class

```python
class UniversalVolatileMonitor:
    """
    Captures volatile states from ANY source.

    Design: Capture everything, process nothing, discover later.
    """

    def __init__(self):
        self.bq_client = bigquery.Client()
        self.known_sources = set()  # Sources we expect

        # Start monitors
        self.start_fs_monitor()      # File system changes
        self.start_accessibility_monitor()  # UI changes
        self.start_process_monitor() # Process changes
        self.start_clipboard_monitor()  # Clipboard changes

    def capture_volatile_state(self, source_system: str, source_type: str,
                                trigger: str, state: Any) -> str:
        """
        Capture a volatile state to BigQuery.

        Args:
            source_system: What system produced this (zoom.us, Chrome, etc.)
            source_type: Type of volatile state (process, file, ui, etc.)
            trigger: What caused this capture
            state: The actual state data (will be JSON serialized)

        Returns:
            volatile_id of the captured state
        """
        volatile_id = f"vol_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Serialize state as-is (pure copy)
        raw_json = json.dumps(state, default=str)

        row = {
            "volatile_id": volatile_id,
            "capture_timestamp": datetime.now().isoformat(),
            "source_system": source_system,
            "source_type": source_type,
            "trigger_event": trigger,
            "raw_state_json": raw_json,
            "state_size_bytes": len(raw_json),
            "state_checksum": hashlib.md5(raw_json.encode()).hexdigest(),
            "is_known_source": source_system in self.known_sources,
            "ingestion_date": datetime.now().strftime("%Y-%m-%d")
        }

        # Insert to BigQuery
        self.bq_client.insert_rows_json(
            "flash-clover-464719-g1.system_capture.volatile_states_universal",
            [row]
        )

        # Discovery alert if new source
        if source_system not in self.known_sources:
            print(f"DISCOVERY: New volatile state source: {source_system}")
            self.known_sources.add(source_system)

        return volatile_id
```

### File System Monitor

```python
def start_fs_monitor(self):
    """Monitor file system for volatile state creation."""
    import fsevents

    VOLATILE_PATHS = [
        "/tmp",
        str(Path.home() / "Library/Caches"),
        str(Path.home() / "Library/Application Support"),
    ]

    def on_fs_event(path, flags):
        # Capture the volatile file state
        try:
            if Path(path).exists():
                stat = Path(path).stat()
                state = {
                    "path": path,
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                    "content_preview": self._safe_read_preview(path)
                }

                # Detect source system from path
                source = self._detect_source_from_path(path)

                self.capture_volatile_state(
                    source_system=source,
                    source_type="file",
                    trigger=f"fs_event:{flags}",
                    state=state
                )
        except Exception:
            pass

    observer = fsevents.Observer()
    for path in VOLATILE_PATHS:
        observer.schedule(on_fs_event, path)
    observer.start()
```

### Accessibility Monitor

```python
def start_accessibility_monitor(self):
    """Monitor UI changes for volatile states."""
    # Uses pyobjc to watch accessibility events

    def on_ui_change(notification):
        app_name = notification.userInfo().get("NSWorkspaceApplicationKey")

        # Capture the UI state
        state = {
            "active_app": app_name,
            "windows": self._get_window_list(),
            "focused_element": self._get_focused_element()
        }

        self.capture_volatile_state(
            source_system=app_name or "unknown",
            source_type="ui",
            trigger="ui_change",
            state=state
        )
```

### Process Monitor

```python
def start_process_monitor(self):
    """Monitor process changes."""
    import psutil

    previous_pids = set()

    def check_processes():
        current_pids = set(psutil.pids())

        # New processes
        new_pids = current_pids - previous_pids
        for pid in new_pids:
            try:
                proc = psutil.Process(pid)
                state = {
                    "pid": pid,
                    "name": proc.name(),
                    "cmdline": proc.cmdline(),
                    "cwd": proc.cwd(),
                    "create_time": proc.create_time()
                }

                self.capture_volatile_state(
                    source_system=proc.name(),
                    source_type="process",
                    trigger="process_start",
                    state=state
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        previous_pids = current_pids
```

---

## Discovery Queries

Once data is captured, discover what exists:

### Find Unknown Systems

```sql
-- Systems creating volatile states we didn't know about
SELECT
    source_system,
    source_type,
    COUNT(*) as capture_count,
    MIN(capture_timestamp) as first_seen,
    MAX(capture_timestamp) as last_seen
FROM `flash-clover-464719-g1.system_capture.volatile_states_universal`
WHERE is_known_source = FALSE
GROUP BY source_system, source_type
ORDER BY capture_count DESC;
```

### Correlate with User Activity

```sql
-- What volatile states correlate with my activity?
SELECT
    source_system,
    trigger_event,
    active_application,
    COUNT(*) as occurrences
FROM `flash-clover-464719-g1.system_capture.volatile_states_universal`
WHERE user_idle_seconds < 5  -- Active usage
GROUP BY source_system, trigger_event, active_application
ORDER BY occurrences DESC;
```

### Sample Unknown Volatile Data

```sql
-- What's in the volatile states from a new discovery?
SELECT
    capture_timestamp,
    trigger_event,
    JSON_EXTRACT_SCALAR(raw_state_json, '$.path') as file_path,
    JSON_EXTRACT_SCALAR(raw_state_json, '$.size') as file_size
FROM `flash-clover-464719-g1.system_capture.volatile_states_universal`
WHERE source_system = 'NewDiscoveredApp'
ORDER BY capture_timestamp DESC
LIMIT 100;
```

---

## What This Enables

### 1. Discover Unknown Data Sources
"I didn't know Slack was creating temp files with message previews"

### 2. Find Persistent Systems
"If this app creates volatile temp files, it probably has a persistent database"

### 3. Understand What You Lose
"Every time I close this app, 47 volatile records disappear"

### 4. Identify Reactive Systems
"This process spikes 2 seconds after I click in Zoom"

### 5. Bootstrap Knowledge
Capture first → Analyze later → Build targeted extractors

---

## Implementation Priority

1. **Create BigQuery table** - `system_capture.volatile_states_universal`
2. **Build core monitor** - UniversalVolatileMonitor class
3. **Add Zoom volatile capture** - Already done (L6)
4. **Add file system monitor** - FSEvents on temp directories
5. **Add process monitor** - Track process creation/termination
6. **Add clipboard monitor** - Capture clipboard changes
7. **Run discovery queries** - Find unknown systems
8. **Build targeted extractors** - For interesting discoveries

---

## Change Log

| Date | Change |
|------|--------|
| 2025-12-02 | Initial design based on Zoom volatile state insight |

---

*This system exists to answer: "What volatile data exists that I'm losing, and what systems are creating it?"*
