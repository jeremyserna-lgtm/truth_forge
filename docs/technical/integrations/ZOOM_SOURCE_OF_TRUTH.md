# Zoom Capture System - Source of Truth

**Status**: Active
**Last Updated**: 2025-12-08 18:47 (Click Detection Fully Operational)
**Owner**: `tools/zoom_daemon.py`
**This Document Supersedes**: All prior Zoom documentation (see Deprecated Documents below)

---

## Executive Summary

The Zoom capture system captures real-time meeting data via a single unified daemon that integrates with Truth Engine's central services. All observations flow to BigQuery for analysis and long-term storage.

**Key Capabilities:**
- Real-time chat message capture via accessibility API
- Avatar file monitoring with **stable zoom_user_id extraction**
- **Click detection** via Quartz event taps (requires Input Monitoring permission)
- **Identity correlation** between zoom_user_id and display_name
- Gallery observation with page change detection

| Metric | Value |
|--------|-------|
| **Active Daemon** | `tools/zoom_daemon.py` |
| **BigQuery Dataset** | `flash-clover-464719-g1.zoom` |
| **Observations Table** | `zoom.daemon_observations` |
| **Total Observations (today)** | 892+ stored, 999 uploaded to BQ |
| **Unique Zoom User IDs (session)** | 3 captured |
| **Total Clicks Captured (session)** | 55+ |
| **ID Format** | `zm_chat:`, `zm_proc:`, `zm_file:`, `zm_event:` |

---

## Architecture

```
                              ZOOM APPLICATION
    ┌─────────────────────────────────────────────────────────────┐
    │  Participants │ Chat Messages │ Gallery View │ My State     │
    └───────┬───────────────┬───────────────┬────────────┬────────┘
            │               │               │            │
            ▼               ▼               ▼            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    ZOOM DAEMON (UNIFIED)                     │
    │                  tools/zoom_daemon.py                        │
    ├─────────────────────────────────────────────────────────────┤
    │                                                              │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
    │  │  pyobjc/AX   │  │   Watchdog   │  │   Process    │       │
    │  │   Observer   │  │   Handler    │  │   Monitor    │       │
    │  │ (Chat+State) │  │   (Files)    │  │  (Lifecycle) │       │
    │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
    │         │                 │                 │                │
    │         └────────────────>├<────────────────┘                │
    │                           │                                  │
    │                           ▼                                  │
    │              ┌────────────────────────┐                      │
    │              │   Central Services     │                      │
    │              │   - get_logger()       │                      │
    │              │   - generate_zoom_*_id │                      │
    │              │   - track_cost()       │                      │
    │              └───────────┬────────────┘                      │
    │                          │                                   │
    │                          ▼                                   │
    │              ┌────────────────────────┐                      │
    │              │   SQLite Buffer        │                      │
    │              │   ~/Documents/zoom_daemon/observations.db     │
    │              └───────────┬────────────┘                      │
    │                          │                                   │
    │                          ▼                                   │
    │              ┌────────────────────────┐                      │
    │              │   BigQuery Uploader    │                      │
    │              │   get_bigquery_client()│                      │
    │              │   (cost-protected)     │                      │
    │              └────────────────────────┘                      │
    │                                                              │
    └─────────────────────────────────────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                        BIGQUERY                              │
    │              zoom.daemon_observations                        │
    │  ┌───────────────────────────────────────────────────────┐  │
    │  │ observation_id │ observation_type │ source │ data     │  │
    │  │ zm_chat:abc123 │ live_chat        │ pyobjc │ {...}    │  │
    │  │ zm_proc:def456 │ process          │ ps     │ {...}    │  │
    │  │ zm_file:ghi789 │ file             │ watch  │ {...}    │  │
    │  └───────────────────────────────────────────────────────┘  │
    └─────────────────────────────────────────────────────────────┘
```

---

## Identity Correlation System

### The Problem

Zoom has two types of identifiers:
1. **zoom_user_id** - Stable 32-char hex ID embedded in avatar filenames (`conf_avatar_{zoom_user_id}_{size}`)
2. **display_name** - Human-readable name that appears in chat and gallery (can change)

We need to correlate these to build a reliable identity map.

### The Solution: Interaction-Aware Correlation

**Key insight:** Correlation happens during USER INTERACTIONS, not passively.

When Jeremy interacts with Zoom's UI:

| Interaction | What Happens | Correlation Opportunity |
|-------------|--------------|-------------------------|
| **Page Change** | ~25 new names appear in gallery + ~25 avatars load | Batch correlation by timing |
| **Pin Someone** | 1 name highlighted + 1 avatar loads prominently | High-confidence 1:1 match |
| **Gallery Scroll** | 1-5 new names appear + 1-5 avatars load | Small batch correlation |
| **Chat Message** | Sender name appears + sender's avatar may load | Timing-based correlation |

### Avatar User ID Extraction

Avatar filenames contain stable user IDs:
```
conf_avatar_c064aaebfaebe42a893eb2abebf38340_102
          └──────────────────────────────────┘
                    zoom_user_id (32 chars)
```

The daemon extracts this via regex and stores it in the `data.zoom_user_id` field.

### IdentityTracker Class

Located in `tools/zoom_daemon.py`:

```python
class IdentityTracker:
    """Tracks Zoom participant identities and correlates user IDs with display names."""

    # Correlation windows
    CORRELATION_WINDOW_SECONDS = 10  # Individual correlation
    BATCH_WINDOW_SECONDS = 3         # Page change burst detection
    PAGE_CHANGE_THRESHOLD = 0.5      # >50% new names = page change

    # State tracking
    user_ids: Dict[str, Dict]        # zoom_user_id -> {first_seen, last_seen, avatar_hash}
    display_names: Dict[str, Dict]   # display_name -> {first_seen, last_seen, chat_count}
    mappings: Dict[str, str]         # zoom_user_id -> display_name (confirmed)
    reverse_mappings: Dict[str, str] # display_name -> zoom_user_id

    # Interaction tracking
    interaction_pending: Optional[str]  # 'page_change', 'pin', 'scroll'
    interaction_names: Set[str]         # Names that appeared with this interaction
    interaction_avatars: List[str]      # Avatar user_ids that appeared
```

### Correlation Data Example

From today's session:
```
Avatar 2c90681ee6f74748a7b120f20123d802 at 10:01:35
  → "ProudMethhead NJ" first appeared at 10:02:01 (26 sec apart)
  → BEST MATCH - timing correlation candidate

Avatar 6536e33366af049614efc456b587a162 at 10:00:45
  → "dadjustslamming" at 10:00:08 (36 sec apart)
  → "MELB Silver Daddy" at 10:00:03 (41 sec apart)
  → AMBIGUOUS - need interaction context to resolve
```

---

## Click Detection System

### What macOS CAN Detect

macOS provides full visibility into UI interactions via:

| API | What It Detects | Used For |
|-----|-----------------|----------|
| **Quartz Event Tap** | ALL mouse clicks system-wide | Know WHEN something was clicked |
| **AXUIElementCopyElementAtPosition** | Element at any screen coordinate | Know WHAT was clicked |
| **AXUIElementCopyAttributeValue** | Element properties (role, description, title, ID) | Classify the click |
| **NSWorkspace** | Frontmost application | Filter for Zoom only |

### ClickObserver Class

Located in `tools/zoom_daemon.py`:

```python
class ClickObserver:
    """Observes mouse clicks and identifies what was clicked in Zoom."""

    def observe_click(self, x: float, y: float) -> Optional[Dict]:
        """Called when a click happens. Returns click info if it's on Zoom."""
        if not self.is_zoom_frontmost():
            return None

        element_info = self.get_element_at_click(x, y)
        click_type = self.classify_click(element_info)

        # click_type: 'page_next', 'page_prev', 'pin', 'participant', 'chat', 'button'
        return {'timestamp': ..., 'x': x, 'y': y, 'click_type': click_type, 'element': element_info}
```

### Click Classification

| Click Type | Detection Pattern | Daemon Action |
|------------|-------------------|---------------|
| `page_next` | AXDescription contains "next page" | Set `interaction_pending = 'page_change'` |
| `page_prev` | AXDescription contains "previous page" | Set `interaction_pending = 'page_change'` |
| `pin` | AXDescription contains "pin" or "spotlight" | Set `interaction_pending = 'pin'` |
| `participant` | AXRole = "AXTabGroup" with "Name, status" description | Extract name, set pending pin |
| `chat` | AXDescription contains "chat" or "message" | Track chat interaction |
| `button` | AXRole = "AXButton" | Log button click |

### Test Tools

```bash
# Test what element is under your cursor (hover test)
python tools/test_click_detection.py

# Monitor actual clicks in real-time (click listener)
python tools/test_click_listener.py
```

### macOS Permissions Required

Click detection requires two separate macOS permissions:

| Permission | Location | Required For |
|------------|----------|--------------|
| **Input Monitoring** | System Settings > Privacy & Security > Input Monitoring | Quartz event tap (receiving click events) |
| **Accessibility** | System Settings > Privacy & Security > Accessibility | AXUIElement APIs (identifying clicked elements) |

**Status Display Format:**
```
Clicks: 55/0
        │   └─ Zoom-specific clicks (requires Accessibility permission)
        └───── Total clicks captured (requires Input Monitoring permission)
```

**Implementation Details:**
- Uses module-level callback function (required for pyobjc compatibility)
- Runs in background thread with CFRunLoop
- Memory: ~550MB with central services stack loaded
- Event tap created at `kCGSessionEventTap` level (session-wide)

---

## Active Components

### 1. Daemon (`tools/zoom_daemon.py`)

**The ONE active daemon.** All other zoom daemons are deprecated.

```bash
# Run daemon (foreground)
python tools/zoom_daemon.py

# Check status
python tools/zoom_daemon.py --status

# Single capture cycle (testing)
python tools/zoom_daemon.py --once

# Force BigQuery upload
python tools/zoom_daemon.py --upload

# Cleanup old data
python tools/zoom_daemon.py --cleanup
```

**Configuration** (in script header):
```python
DATA_DIR = ~/Documents/zoom_daemon
BQ_PROJECT = "flash-clover-464719-g1"
BQ_DATASET = "zoom"
BQ_TABLE = "daemon_observations"
BQ_MAX_DAILY_WRITES = 1000
MAX_MEMORY_MB = 800  # Central services + pyobjc need ~550MB
OBSERVE_INTERVAL = 5  # seconds
```

### 2. Documentation (`tools/ZOOM_DAEMON.md`)

**The ONE active documentation file** for daemon usage, configuration, and troubleshooting.

### 3. BigQuery Table (`zoom.daemon_observations`)

```sql
CREATE TABLE zoom.daemon_observations (
    observation_id STRING NOT NULL,     -- zm_chat:xxx, zm_proc:xxx, etc.
    observation_type STRING NOT NULL,   -- live_chat, process, file, etc.
    source STRING NOT NULL,             -- pyobjc, watchdog, process_monitor
    observation_hash STRING NOT NULL,   -- SHA-256 for deduplication
    data STRING,                        -- JSON blob with full details
    observed_at TIMESTAMP NOT NULL,
    uploaded_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(observed_at)
CLUSTER BY observation_type, source;
```

### 4. Local Storage (`~/Documents/zoom_daemon/`)

```
~/Documents/zoom_daemon/
├── observations.db    # SQLite buffer (8.9MB)
└── daemon.log         # Operational logs
```

---

## Observation Types

| Type | ID Prefix | Source | Content |
|------|-----------|--------|---------|
| `live_chat` | `zm_chat:` | pyobjc/AX API | Real-time chat messages with sender name |
| `process` | `zm_proc:` | ps command | Zoom process lifecycle |
| `file` | `zm_file:` | Watchdog | File changes - **includes zoom_user_id for avatars** |
| `meeting_event` | `zm_event:` | AppleScript | Meeting start/end |
| `state_change` | `zm_event:` | AppleScript | Mute/video changes |
| `directory` | `zm_file:` | Watchdog | Directory listings |
| `chat` | `zm_file:` | Watchdog | Saved chat files |

### File Observation Data Structure (Avatars)

```json
{
  "path": "/Users/.../ConfAvatar/conf_avatar_c064aaebfaebe42a893eb2abebf38340_102",
  "name": "conf_avatar_c064aaebfaebe42a893eb2abebf38340_102",
  "zoom_user_id": "c064aaebfaebe42a893eb2abebf38340",
  "content_hash": "a840eacf5c35470c7459443b8d58740288bad290b4ce474999bcd4e6ab2af15b",
  "source_type": "avatars",
  "event_type": "modified"
}
```

### Chat Observation Data Structure

```json
{
  "timestamp": "10:09 AM",
  "sender": "ButtDickNYC",
  "message": "NYc here",
  "scraped_at": "2025-12-08T10:11:49.780690",
  "date": "2025-12-08",
  "session_id": "run:1765213909:1bb4a1bc"
}
```

---

## Central Services Integration

The daemon integrates with `architect_central_services`:

| Service | Usage |
|---------|-------|
| **Logging** | `get_logger("zoom_daemon")` - All logs via central logger |
| **Identity** | `generate_zoom_chat_id()`, `generate_zoom_process_id()`, etc. |
| **Cost Tracking** | `track_cost()` for BigQuery uploads |
| **BigQuery Client** | `get_bigquery_client()` - Cost-protected client |

---

## Data Flow

```
1. OBSERVE   → Capture event (pyobjc, watchdog, or ps)
2. ID        → Generate zoom-specific ID (zm_chat:xxx)
3. HASH      → SHA-256 for deduplication
4. DEDUPE    → Skip if hash already exists
5. STORE     → Write to SQLite with fsync
6. LOG       → Central logger records capture
7. RELEASE   → Clear memory (System Events, GC)
8. UPLOAD    → Batch to BigQuery (respects 1000/day quota)
9. COST      → Track upload cost via central services
```

---

## Current Data State (2025-12-08)

### Local SQLite Buffer
| Type | Count |
|------|-------|
| live_chat | 547 |
| process | 139 |
| file | 40 |
| directory | 18 |
| meeting_event | 18 |
| state_change | 8 |
| chat | 1 |
| **Total** | **771** |

### BigQuery (`zoom.daemon_observations`)
| Type | Count |
|------|-------|
| live_chat | 674 |
| process | 139 |
| file | 40 |
| meeting_event | 18 |
| directory | 18 |
| state_change | 8 |
| chat | 1 |
| **Total** | **898** |

### Other Zoom Tables (Legacy/Unused)
| Table | Rows | Status |
|-------|------|--------|
| zoom.entity_relationships | 138,778 | Legacy from prior pipeline |
| zoom.manifested_wholes | 13,195 | Legacy |
| zoom.unified_extractions | 13,195 | Legacy |
| zoom.state_sequence_index | 6,846 | Legacy |
| zoom.entity_registry | 6,771 | Legacy |
| system_capture.zoom_* | 0 | Unused |

---

## Deprecated Components

### Deprecated Daemons (DO NOT USE)

| Daemon | Location | Replaced By |
|--------|----------|-------------|
| `zoom_unified_daemon.py` | `tools/` | `zoom_daemon.py` |
| `zoom_chat_daemon.py` | `tools/` | `zoom_daemon.py` |
| `zoom_local_first_daemon.py` | `architect_central_services/scripts/` | `zoom_daemon.py` |
| `zoom_event_daemon.py` | `architect_central_services/scripts/` | `zoom_daemon.py` |
| `zoom_timestamp_daemon.py` | `architect_central_services/scripts/` | `zoom_daemon.py` |
| `zoom_chat_daemon/zoom_chat_capture.py` | `tools/` | `zoom_daemon.py` |

### Deprecated Utilities (Archive Candidates)

| Tool | Location | Notes |
|------|----------|-------|
| `zoom_existence_watcher.py` | `tools/` | Replaced by daemon |
| `zoom_user_experience_watcher.py` | `tools/` | Replaced by daemon |
| `zoom_capture_robust.py` | `tools/` | Replaced by daemon |
| `zoom_timeline_capture.py` | `tools/` | Replaced by daemon |
| `zoom_session_extractor.py` | `tools/` | Replaced by daemon |
| `zoom_enhanced_extractor.py` | `tools/` | Replaced by daemon |
| `zoom_ui_state_extractor.py` | `tools/` | Replaced by daemon |
| `zoom_event_capture.py` | `tools/` | Replaced by daemon |
| `extract_zoom_chat.py` | `tools/` | Replaced by daemon |
| `test_zoom_capture.py` | `tools/` | Test only |
| `force_zoom_capture.sh` | `tools/` | Test only |
| `force_live_zoom_capture.py` | `tools/` | Test only |
| `zoom_frida_scanner.py` | `tools/` | Research (blocked by SIP) |
| `zoom_lldb_scanner.py` | `tools/` | Research |

### Active Utilities (KEEP)

| Tool | Location | Purpose |
|------|----------|---------|
| `zoom_identity_mapper.py` | `tools/` | Maps display names to canonical IDs |
| `zoom_import_avatars.py` | `tools/` | Imports avatars to BigQuery |
| `zoom_meeting_group_detector.py` | `tools/` | Meeting group detection |

---

## Deprecated Documentation

The following documents are superseded by this file:

| Document | Location | Status |
|----------|----------|--------|
| `ZOOM_DAEMON_EVALUATION.md` | `docs/architecture/` | **DEPRECATED** - Design doc, implemented |
| `ZOOM_CHAT_CAPTURE_SYSTEM.md` | `docs/capture/` | **DEPRECATED** - Replaced by daemon |
| `ZOOM_SESSION_CAPTURE_ARCHITECTURE.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_STAGED_PIPELINE_ARCHITECTURE.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_COMPLETE_DATA_TAXONOMY.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_DATA_STORAGE_ANALYSIS.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_ENCRYPTED_DATA_INVESTIGATION.md` | `docs/architecture/` | **DEPRECATED** - Research complete |
| `ZOOM_UNIVERSAL_PIPELINE_ALIGNMENT.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_COMPREHENSIVE_CAPTURE_AND_ENCRYPTION.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_COMPLETE_INTERACTION_TAXONOMY.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_IMPLEMENTATION_VALIDATION_2025-12-02.md` | `docs/architecture/` | **DEPRECATED** - Historical |
| `ZOOM_MULTI_LAYER_CAPTURE_ARCHITECTURE.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_TIMESTAMPS_INVESTIGATION.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_COMPLETE_DATA_SCHEMA.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_USER_EXPERIENCE_SCHEMA.md` | `docs/architecture/` | **DEPRECATED** |
| `ZOOM_DATA_CATALOG.md` | `docs/` | **DEPRECATED** |
| `ROOT_CAUSE_ANALYSIS_ZOOM_CAPTURE.md` | `architect_central_services/docs/` | **DEPRECATED** |
| `ZOOM_NATIVE_FILES_COMPLETE_INVENTORY.md` | `architect_central_services/docs/` | **DEPRECATED** |
| `INDIVIDUAL_ZOOM_FEED_CAPTURE_ANALYSIS.md` | `architect_central_services/docs/` | **DEPRECATED** |
| `STAGE_0_ZOOM_CHAT.md` | `architect_central_services/docs/` | **DEPRECATED** |
| `ZOOM_TO_ENTITY_UNIFIED_MAPPING.md` | `architect_central_services/pipelines/zoom/docs/` | **DEPRECATED** |
| `ZOOM_PIPELINE_ENTERPRISE_SPECIFICATION.md` | `architect_central_services/pipelines/zoom/docs/` | **DEPRECATED** |

---

## Running as a Service

### macOS (launchd)

**Plist Location**: `~/Library/LaunchAgents/com.truthengine.zoom-daemon.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.truthengine.zoom-daemon</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/jeremyserna/PrimitiveEngine/tools/zoom_daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/jeremyserna/Documents/zoom_daemon/launchd.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jeremyserna/Documents/zoom_daemon/launchd.err.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/jeremyserna/PrimitiveEngine</string>
</dict>
</plist>
```

**Commands**:
```bash
# Load daemon
launchctl load ~/Library/LaunchAgents/com.truthengine.zoom-daemon.plist

# Unload daemon
launchctl unload ~/Library/LaunchAgents/com.truthengine.zoom-daemon.plist

# Check status
launchctl list | grep zoom
```

---

## Troubleshooting

### Daemon not capturing chat
- Ensure Zoom chat panel is open (can be behind other windows)
- Check accessibility permissions: System Settings > Privacy > Accessibility > Terminal

### High memory usage
- Daemon auto-exits at 300MB (for launchd restart)
- Run `--cleanup` to delete old validated data

### BigQuery not uploading
- Check quota: `python tools/zoom_daemon.py --status`
- Verify credentials: `export GOOGLE_APPLICATION_CREDENTIALS=...`
- Force upload: `python tools/zoom_daemon.py --upload`

### Cost protection blocking uploads
- The centralized BigQuery client enforces cost limits
- This is expected behavior to prevent $44 cost spikes

---

## Future Enhancements

### Recently Implemented (2025-12-08)
- ✅ **zoom_user_id extraction** - Stable IDs extracted from avatar filenames
- ✅ **Gallery observation** - Track visible participant names via AX API
- ✅ **Click detection framework** - Quartz event taps and element identification
- ✅ **Click observer integration** - Click listener running in background thread, monitoring Zoom UI
- ✅ **IdentityTracker** - Correlation infrastructure between user IDs and names
- ✅ **Page change detection** - Detect when gallery view changes significantly

### In Progress
- 🔄 **Persistent identity mappings** - Store confirmed correlations to SQLite/BigQuery
- 🔄 **Pin detection** - Identify who is pinned/spotlighted

### Planned
- 📋 **Sentiment analysis** - Process chat content for emotional signals
- 📋 **Relationship building** - Auto-create relationships from interactions
- 📋 **Meeting group detection** - Cluster participants by meeting frequency
- 📋 **Avatar image storage** - Store avatar images to BigQuery/GCS

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.3.1 | 2025-12-08 | Click detection operational (module-level callback fix for pyobjc), Input Monitoring permission documented |
| 2.3.0 | 2025-12-08 | Click observer fully integrated into daemon main loop |
| 2.2.0 | 2025-12-08 | Identity correlation system, click detection, gallery observation |
| 2.1.0 | 2025-12-08 | zoom_user_id extraction from avatar filenames |
| 2.0.0 | 2025-12-08 | Central services integration (logging, IDs, cost tracking) |
| 1.0.0 | 2025-12-08 | Initial unified daemon replacing 5 deprecated daemons |

---

*This is the single source of truth for Zoom capture. All other documents are deprecated.*
