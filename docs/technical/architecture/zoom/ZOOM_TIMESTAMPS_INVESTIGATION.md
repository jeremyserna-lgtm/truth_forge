> **DEPRECATED** - This document is superseded by [ZOOM_SOURCE_OF_TRUTH.md](../ZOOM_SOURCE_OF_TRUTH.md)
>
> This document is kept for historical reference only.

---

# Zoom Timestamps Investigation

**Date:** 2025-12-02
**Purpose:** Find what timestamps Zoom already has, capture them

---

## The Principle

Time is always one thing at one time and never it again and never it before.

We don't invent timestamps. We find the timestamps Zoom already records.

---

## Investigation: What Timestamps Does Zoom Have?

### 1. Meeting/Session Level

| What Exists | Timestamp Zoom Has | Where It Lives |
|-------------|-------------------|----------------|
| Meeting start | Meeting started timestamp | Meeting info, logs |
| Meeting end | Meeting ended timestamp | Logs, or when process terminates |
| Meeting scheduled time | Scheduled timestamp | Calendar integration |

### 2. Participant Level

| What Exists | Timestamp Zoom Has | Where It Lives |
|-------------|-------------------|----------------|
| Participant joins | Join timestamp | Participant list updates |
| Participant leaves | Leave timestamp | Participant list updates |
| Host transfer | Transfer timestamp | When host changes |

### 3. Message Level

| What Exists | Timestamp Zoom Has | Where It Lives |
|-------------|-------------------|----------------|
| Message sent | Send timestamp | Chat message metadata |
| Message received | Display timestamp | When it appears in UI |
| Message edited | Edit timestamp | If message was edited |

### 4. UI/Accessibility Level

| What Exists | Timestamp Zoom Has | Where It Lives |
|-------------|-------------------|----------------|
| Window opened | Window create time | OS tracks this |
| UI element appeared | Element creation | Accessibility events |
| UI element changed | Change event time | Accessibility events |

### 5. Process Level

| What Exists | Timestamp Zoom Has | Where It Lives |
|-------------|-------------------|----------------|
| Zoom process start | Process create time | OS process info |
| Zoom process end | Process terminate time | OS process info |

---

## What We Capture

For each thing that exists:
1. **Find its timestamp** (the one Zoom/OS already has)
2. **Record the thing + timestamp**

```
THING: Message "Hello"
TIMESTAMP: 2025-12-02T14:30:45Z (when Zoom says it was sent)
RECORD: {thing: "Hello", timestamp: "2025-12-02T14:30:45Z"}
```

---

## The Tables Map to Timestamps

| Table | What Exists | Timestamp We Capture |
|-------|-------------|---------------------|
| `zoom_session_existence` | Meeting | started_at (Zoom's start time), ended_at (Zoom's end time) |
| `zoom_participant_existence` | User in meeting | arrived_at (join time), departed_at (leave time) |
| `zoom_event_existence` | Message/action | event_timestamp (when Zoom says it happened) |
| `zoom_volatile_existence` | Temp state | created_at_ts (when we observed it), destroyed_at_ts (when it ceased) |

---

## Sources of Timestamps in Zoom

### Accessibility API
- UI element creation/change events have timestamps
- Window events have timestamps
- Focus changes have timestamps

### Process Info
- Process start time (from OS)
- Process CPU/memory snapshots have timestamps

### Chat Messages
- Each message has a timestamp (visible in chat)
- Format: usually HH:MM or HH:MM:SS

### Meeting Info
- Meeting start time
- Duration counter (implies start time)
- Participant join/leave (in participant panel)

---

## Implementation

```python
# For each thing we find:
def capture_with_timestamp(thing, timestamp_source):
    """
    thing = what exists
    timestamp_source = where Zoom/OS records when it exists
    """
    timestamp = get_timestamp_from_source(timestamp_source)
    record = {
        'thing': thing,
        'timestamp': timestamp
    }
    store(record)
```

---

## The Result

Everything on timeline:
- Meetings (started_at → ended_at)
- Participants (arrived_at → departed_at)
- Messages (event_timestamp)
- Volatile states (created_at_ts → destroyed_at_ts)

All queryable by time. All arrangeable however we want. All because we captured the timestamps that already exist.

---

*Time is always one thing at one time and never it again and never it before.*
