> **DEPRECATED** - This document is superseded by [ZOOM_SOURCE_OF_TRUTH.md](../ZOOM_SOURCE_OF_TRUTH.md)
>
> This document is kept for historical reference only.

---

# Zoom Pipeline - Universal Pattern Alignment

## Overview

This document describes how the Zoom data pipeline aligns with the Truth Engine's universal data processing patterns defined in `UNIFIED_STAGE_PATTERNS.md`.

The Zoom pipeline captures real-time meeting data and processes it through stages that mirror the ChatGPT ingestion pipeline, enabling unified querying across all communication sources.

---

## Stage Architecture

### Zoom Stage Pattern

| Stage | Purpose | Input | Output | Status |
|-------|---------|-------|--------|--------|
| Stage 0 | Raw capture/upload | JSON files | `raw_sessions` | ✅ Implemented |
| Stage 1 | Message extraction | `raw_sessions` | `stage_1_messages` | ✅ Implemented |
| Stage 2 | Metadata extraction | `stage_1_messages` | `stage_2_metadata` | 🔲 TODO |
| Stage 3 | System ID generation | `stage_2_metadata` | `stage_3_entities` | 🔲 TODO |
| Stage 4 | Text cleanup | `stage_3_entities` | `stage_4_clean` | 🔲 TODO |
| Stage 5 | Entity creation | `stage_4_clean` | `stage_5_entities` | 🔲 TODO |
| Promotion | SPINE integration | `stage_5_entities` | `spine.entity_unified` | 🔲 TODO |

### Comparison with ChatGPT Pipeline

| Pattern | ChatGPT | Zoom | Alignment |
|---------|---------|------|-----------|
| Stage 0 Raw Storage | Conversations JSON | Sessions JSON | ✅ Same |
| Stage 1 Extraction | Messages from conversations | Messages from sessions | ✅ Same |
| Entity ID Generation | `chatgpt:msg:{hash}` | `zoom:msg:{hash}` | ✅ Same pattern |
| Conversation ID | `chatgpt:conv:{id}` | `zoom:conv:{session_id}` | ✅ Same pattern |
| Deduplication | Source ID then Entity ID | Source ID then Entity ID | ✅ Same |
| SPINE Promotion | Unified entity table | Unified entity table | ✅ Same target |

---

## Stage 0: Raw Capture (Zoom-Specific)

### Unique Challenge: Ephemeral Data

Unlike ChatGPT (which has persistent export files), Zoom data is **ephemeral**:
- Chat messages exist only during active meeting
- Meeting ends → data vanishes forever
- Must capture at the RIGHT MOMENT

### Capture Triggers

| Trigger | When | Priority |
|---------|------|----------|
| `SESSION_START` | Meeting joined | CRITICAL |
| `SESSION_END` | Meeting ending | CRITICAL (data about to vanish) |
| `NEW_MESSAGE` | Chat message detected | HIGH |
| `PARTICIPANT_JOIN` | New participant | HIGH |
| `PARTICIPANT_LEAVE` | Participant left | HIGH |
| `TEMPORAL_BACKUP` | Every 30 seconds | SAFETY NET |
| `FORCE_FILE` | Touch trigger file | MANUAL |
| `FORCE_SIGNAL` | SIGUSR1 | MANUAL |

### BigQuery Schema: `zoom_capture.raw_sessions`

```sql
-- Identity
session_id STRING NOT NULL,
meeting_id STRING,
meeting_name STRING,
meeting_url STRING,

-- Timing
join_timestamp TIMESTAMP,
leave_timestamp TIMESTAMP,
duration_seconds INT64,

-- Raw Data (JSON, no parsing)
participants_raw JSON,
everyone_chat_raw JSON,
dm_chats_raw JSON,
persistent_data JSON,
temporary_data JSON,
avatar_fingerprints JSON,

-- Counts
participant_count INT64,
everyone_message_count INT64,
dm_message_count INT64,

-- Enhanced Data (from zoom_enhanced_extractor.py)
-- meeting_info: {meeting_id, meeting_url, host, meeting_topic}
-- recording_status: {is_recording, recording_type}
-- screen_share_status: {is_sharing, sharer_name}
-- toolbar_state: {my_audio_muted, my_video_off}

-- Extraction Metadata
extraction_method STRING,
extraction_version STRING,
extracted_at TIMESTAMP,
created_at TIMESTAMP,
last_updated TIMESTAMP
```

---

## Stage 1: Message Extraction

### Universal Pattern Compliance

| Pattern | ChatGPT | Zoom | Status |
|---------|---------|------|--------|
| Entity Reading | `dict(row)` + metadata preservation | ✅ Same | ✅ |
| Entity ID Generation | MD5 hash | MD5 hash | ✅ |
| Source ID Deduplication | By source_message_id | By zoom_message_id | ✅ |
| Table Creation | Schema evolution support | Schema evolution support | ✅ |
| Error Handling | Structured logging | Structured logging | ✅ |
| Progress Reporting | Heartbeats + stats | Basic logging | 🔶 Needs enhancement |

### Entity ID Pattern

```python
def generate_entity_id(session_id, chat_type, sender, time_str, content):
    payload = f"{session_id}|{chat_type}|{sender}|{time_str}|{content}"
    hash_value = hashlib.md5(payload.encode()).hexdigest()
    return f"zoom:msg:{hash_value}"
```

### BigQuery Schema: `zoom_capture.stage_1_messages`

```sql
-- Entity IDs (matches SPINE pattern)
entity_id STRING NOT NULL,        -- zoom:msg:{hash}
conversation_id STRING,           -- zoom:conv:{session_id}
message_id STRING,                -- Same as entity_id

-- Zoom Native IDs
zoom_session_id STRING NOT NULL,
zoom_message_id STRING NOT NULL,

-- Content
text STRING NOT NULL,

-- Sender Identity
sender_display_name STRING,
sender_participant_id STRING,

-- Chat Context
chat_type STRING,                 -- "everyone" or "dm"
dm_recipient_id STRING,
direction STRING,                 -- "sent" or "received"

-- Timing
message_time_string STRING,       -- Original display ("10:30 AM")
message_timestamp TIMESTAMP,      -- Parsed (TODO)

-- Session Context
meeting_name STRING,
meeting_group_id STRING,

-- Source Metadata (matches SPINE)
source_pipeline STRING NOT NULL,  -- "zoom"
source_platform STRING,           -- "zoom_video_chat"
source_system STRING,             -- "zoom"
source_file STRING,

-- Processing Metadata
extraction_timestamp TIMESTAMP,
stage_1_processed_at TIMESTAMP,
stage_1_version STRING,
run_id STRING,
ingestion_date DATE               -- Partition key
```

---

## Stage 2+: Future Implementation

### Stage 2: Metadata Extraction

Will extract and normalize:
- Timestamp parsing (convert "10:30 AM" to proper timestamp)
- Display name normalization
- Meeting group detection
- Participant role extraction

### Stage 3: System ID Generation

Will add:
- Sequence calculation within session
- Canonical participant IDs (via identity service)
- Cross-session correlation

### Stage 4: Text Cleanup

Will apply:
- Encoding fixes (ftfy)
- HTML/formatting removal
- Whitespace normalization
- Preserve original in metadata

### Stage 5: Entity Creation

Will extract:
- Named entities (spaCy)
- Sentiment analysis
- L1-L4 + L6 hierarchy alignment

### SPINE Promotion

Will merge Zoom messages into `spine.entity_unified`:
- Same schema as ChatGPT messages
- Unified querying across all sources
- Cross-platform analytics

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ZOOM CAPTURE DAEMON                          │
│  (zoom_capture_robust.py + zoom_enhanced_extractor.py)             │
│                                                                     │
│  Triggers: EVENT (messages, participants, session)                  │
│            TEMPORAL (30s backup)                                    │
│            FORCE (file, signal)                                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STAGE 0: RAW CAPTURE                           │
│  ~/Documents/zoom_sessions/session_*.json                          │
│                          ↓                                          │
│  zoom_capture.raw_sessions (BigQuery)                              │
│                                                                     │
│  Principle: Store raw. No parsing. No processing.                   │
│  Purpose: Pure source of truth                                      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STAGE 1: MESSAGE EXTRACTION                       │
│  zoom_capture.stage_1_messages (BigQuery)                          │
│                                                                     │
│  Principle: Flatten JSON into individual message rows               │
│  Pattern: Source ID deduplication (zoom_message_id)                │
│  Output: One row per message (everyone + DM)                        │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STAGE 2+: ENRICHMENT PIPELINE                     │
│  (Following ChatGPT universal pattern)                             │
│                                                                     │
│  Stage 2: Metadata extraction                                       │
│  Stage 3: System ID generation                                      │
│  Stage 4: Text cleanup                                              │
│  Stage 5: Entity creation (spaCy)                                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       SPINE PROMOTION                               │
│  spine.entity_unified                                               │
│                                                                     │
│  Unified table for:                                                 │
│  - ChatGPT conversations                                            │
│  - SMS messages                                                     │
│  - Zoom meeting chats                                               │
│  - (Future: Grindr, Sniffies, Email, etc.)                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Files

| File | Purpose |
|------|---------|
| `tools/zoom_session_extractor.py` | Base data extraction from Zoom UI |
| `tools/zoom_enhanced_extractor.py` | Enhanced extraction (meeting info, recording, etc.) |
| `tools/zoom_capture_robust.py` | Daemon with EVENT + TEMPORAL + FORCE triggers |
| `architect_central_services/pipelines/zoom/scripts/stage_0/upload_raw_sessions.py` | Stage 0 upload |
| `architect_central_services/pipelines/zoom/scripts/stage_1/zoom_stage_1.py` | Stage 1 processor |

---

## Launch Agents

| Agent | File | Purpose |
|-------|------|---------|
| Robust Capture | `com.truthengine.zoom-robust-capture.plist` | Main capture daemon |
| Event Capture | `com.truthengine.zoom-event-capture.plist` | Legacy event-driven capture |

---

## Validation Queries

### Stage 0: Raw Sessions

```sql
-- Count raw sessions
SELECT COUNT(*) as session_count
FROM `flash-clover-464719-g1.zoom_capture.raw_sessions`;

-- Recent captures
SELECT
  session_id,
  meeting_name,
  participant_count,
  everyone_message_count,
  dm_message_count,
  extracted_at
FROM `flash-clover-464719-g1.zoom_capture.raw_sessions`
ORDER BY extracted_at DESC
LIMIT 10;
```

### Stage 1: Messages

```sql
-- Count messages
SELECT COUNT(*) as message_count
FROM `flash-clover-464719-g1.zoom_capture.stage_1_messages`;

-- Messages by session
SELECT
  zoom_session_id,
  chat_type,
  COUNT(*) as message_count
FROM `flash-clover-464719-g1.zoom_capture.stage_1_messages`
GROUP BY zoom_session_id, chat_type
ORDER BY message_count DESC;
```

---

## Key Differences from ChatGPT Pipeline

| Aspect | ChatGPT | Zoom |
|--------|---------|------|
| Data Source | Export JSON files | Live UI extraction |
| Data Persistence | Files persist | Data vanishes at meeting end |
| Capture Frequency | On-demand export | Real-time daemon |
| Session Concept | Conversation thread | Meeting session |
| Message Threading | Continuous | Per-meeting isolated |
| Identity | User IDs | Display names + XMPP |

---

## Alignment Status

| Component | Aligned | Notes |
|-----------|---------|-------|
| Stage 0 Raw Storage | ✅ | JSON → BigQuery |
| Stage 1 Extraction | ✅ | Same pattern |
| Entity ID Generation | ✅ | `zoom:msg:{hash}` |
| Conversation ID | ✅ | `zoom:conv:{session_id}` |
| Deduplication | ✅ | Source ID pattern |
| SPINE Schema | ✅ | Same target |
| Retry Logic | 🔶 | Add to Stage 1 |
| Progress Reporting | 🔶 | Enhance |
| Heartbeats | 🔶 | Add |

---

**Last Updated**: 2025-12-02
**Status**: Stage 0-1 implemented, Stage 2+ pending
**Next**: Implement Stage 2 metadata extraction
