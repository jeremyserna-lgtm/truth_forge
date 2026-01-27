> **DEPRECATED** - This document is superseded by [ZOOM_SOURCE_OF_TRUTH.md](../ZOOM_SOURCE_OF_TRUTH.md)
>
> This document is kept for historical reference only.

---

# How Zoom Actually Stores Data

## Principle

**Don't reinvent. Duplicate and capture.**

Zoom already captures and stores data in specific ways. We just need to:
1. Mirror what Zoom stores
2. Capture when Zoom changes it
3. Put it in BigQuery raw
4. Process later

---

## Zoom's Persistent Data Layer

### Location: `~/Library/Application Support/zoom.us/data/`

This data **survives meetings**. Changes are rare - usually only when new contacts are encountered.

#### XMPP User Directories
```
~/Library/Application Support/zoom.us/data/
├── abc123@xmpp.zoom.us/        # One directory per known user
├── def456@xmpp.zoom.us/
├── ghi789@xmpp.zoom.us/
└── ...
```

**What changes**: New directory created when meeting someone new.
**Capture trigger**: On meeting start (check for new directories)

#### Avatar Cache
```
~/Library/Application Support/zoom.us/data/ConfAvatar/
├── conf_avatar_deadbeef1234_64
├── conf_avatar_deadbeef1234_128
├── conf_avatar_deadbeef1234_256
├── conf_avatar_abcd5678_64
└── ...
```

Format: `conf_avatar_{hash}_{size}`

**What changes**: New avatar files when meeting someone new or avatar changes
**Capture trigger**: File mtime changes (new files appear)

#### Preferences (defaults plist)
```bash
defaults read us.zoom.xos
defaults read ZoomChat
```

Contains:
- Per-XMPP user preferences (keys like `abc123@xmpp.zoom.us_LastChatTime`)
- General Zoom settings
- Recent meeting history

**What changes**: When settings change or new users encountered
**Capture trigger**: On session start (snapshot current state)

---

## Zoom's Temporary Data Layer

This data **only exists during a meeting**. When meeting ends, it's GONE.

### Source: Accessibility API (AppleScript)

The temporary data is NOT stored in files - it exists only in Zoom's running process.

#### Windows
```applescript
tell application "System Events"
    tell process "zoom.us"
        name of every window
    end tell
end tell
```

Returns: "Zoom Meeting", "Meeting chat", "zoom floating video window", etc.

**What changes**: Windows open/close
**Capture trigger**: EVENT (window state change)

#### Chat Messages
Accessible through chat window table elements.

**What changes**: New messages appear as rows
**Capture trigger**: EVENT (row count changes) + TEMPORAL (every 30s backup)

#### Participants
Accessible through chat sidebar or participants panel.

**What changes**: Join/leave events
**Capture trigger**: EVENT (participant list changes)

#### Speaking Status
Accessible through floating window or meeting indicators.

**What changes**: Very frequently (whoever is talking)
**Capture trigger**: TEMPORAL (every 2-5s polling)

#### Meeting State
- Recording status (UI indicator)
- Screen share status (window presence)
- Mute/video status (button descriptions)

**What changes**: User actions or meeting events
**Capture trigger**: EVENT (state change detected)

---

## Capture Strategy (Mirror Zoom's Structure)

### For Persistent Data

**When to capture**:
- Meeting START: Full snapshot of persistent layer
- Meeting END: Check for new additions
- TEMPORAL: Not needed (data is stable)

**What to store in BigQuery**:
```json
{
  "persistent_snapshot": {
    "captured_at": "2025-12-02T10:00:00",
    "xmpp_ids": ["abc123", "def456"],
    "avatar_fingerprints": {
      "deadbeef1234": {
        "hash": "deadbeef1234",
        "sizes": ["64", "128", "256"],
        "file_mtime": "2025-12-02T09:30:00"
      }
    },
    "preferences_snapshot": {...}  // Raw plist data
  }
}
```

**Storage**: Store raw. No parsing. Just JSON dump of what exists.

### For Temporary Data

**When to capture**:
- EVENT: Chat message count changes → capture
- EVENT: Participant list changes → capture
- EVENT: Meeting state changes → capture
- TEMPORAL: Every 30s as backup
- SESSION_END: CRITICAL final capture

**What to store in BigQuery**:
```json
{
  "temporary_snapshot": {
    "captured_at": "2025-12-02T10:00:00",
    "capture_reason": "new_message",
    "zoom_status": "CHAT_OPEN",
    "windows": ["Zoom Meeting", "Meeting chat"],
    "meeting_name": "Weekly Sync",
    "speaking": "Jeremy Serna",
    "chat_participants": ["Alice", "Bob", "Charlie"],
    "everyone_chat_raw": [
      {"time": "10:00 AM", "sender": "Alice", "content": "Hello!"},
      {"time": "10:01 AM", "sender": "Bob", "content": "Hi there"}
    ],
    "dm_chats_raw": {
      "Alice": [{"time": "10:02 AM", "sender": "You", "content": "Private msg"}]
    }
  }
}
```

**Storage**: Store raw. Exactly as extracted from UI. No parsing.

---

## Change Detection (How Zoom Does It)

### Zoom's Change Model

1. **Persistent changes are ADDITIVE**: New XMPP dirs, new avatars, new preference keys
2. **Temporary changes are TRANSIENT**: Messages appear, participants join/leave, speaker changes

### Our Change Detection

```python
# Persistent: Compare sets
previous_xmpp_ids = {"abc123", "def456"}
current_xmpp_ids = {"abc123", "def456", "ghi789"}  # New!
new_ids = current_xmpp_ids - previous_xmpp_ids

# Temporary: Compare state
previous_message_count = 5
current_message_count = 7  # 2 new messages!
if current_message_count > previous_message_count:
    trigger_capture("new_message")
```

---

## BigQuery Schema (Raw, Unprocessed)

### Table: `zoom_capture.raw_snapshots`

This is the SOURCE OF TRUTH. Every capture = one row.

```sql
CREATE TABLE zoom_capture.raw_snapshots (
  -- Capture identity
  capture_id STRING NOT NULL,
  capture_timestamp TIMESTAMP NOT NULL,
  capture_reason STRING NOT NULL,

  -- Session identity
  session_id STRING,

  -- RAW persistent data (JSON, no parsing)
  persistent_xmpp_ids JSON,
  persistent_avatar_fingerprints JSON,
  persistent_preferences JSON,

  -- RAW temporary data (JSON, no parsing)
  temporary_zoom_status STRING,
  temporary_windows JSON,
  temporary_meeting_name STRING,
  temporary_speaking STRING,
  temporary_participants JSON,
  temporary_everyone_chat JSON,
  temporary_dm_chats JSON,
  temporary_recording_status JSON,
  temporary_screen_share JSON,

  -- Metadata
  extraction_method STRING,
  extraction_version STRING,
  data_quality_flags JSON,

  -- Lineage
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Key Design Decisions

1. **JSON columns for variable data**: Avatar fingerprints, preferences, chats - all stored as JSON
2. **No parsing at capture time**: "10:00 AM" stays as "10:00 AM", not converted to timestamp
3. **No normalization at capture time**: Names stay as captured, not lowercased
4. **No deduplication at capture time**: Multiple captures = multiple rows

---

## Processing (Later Stages)

Stage 0 = Raw capture (this document)
Stage 1 = Extract messages from JSON into individual rows
Stage 2 = Parse timestamps, normalize names, correlate IDs
Stage 3+ = Enrichment, embeddings, etc.

**The philosophy**: Capture raw. Process later. Never lose data.

---

## Summary

| Data Type | Where Zoom Stores | How It Changes | When We Capture |
|-----------|-------------------|----------------|-----------------|
| XMPP IDs | Directory structure | New dirs added | SESSION_START |
| Avatars | ConfAvatar files | New files added | SESSION_START, FILE_CHANGE |
| Preferences | defaults plist | Keys added/changed | SESSION_START |
| Windows | Process memory | Open/close | EVENT |
| Chat messages | Process memory | New rows | EVENT + TEMPORAL |
| Participants | Process memory | Join/leave | EVENT + TEMPORAL |
| Speaking | Process memory | Frequent | TEMPORAL |
| Meeting state | Process memory | User actions | EVENT |

**The rule**: If Zoom stores it, we capture it. If Zoom changes it, we capture the change. Store raw in BigQuery. Process later.
