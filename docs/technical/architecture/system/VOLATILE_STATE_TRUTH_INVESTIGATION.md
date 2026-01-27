# The Truth About Volatile States

**Date:** 2025-12-02
**Purpose:** Find the truth of what volatile states ARE, not how to capture them

---

## The Principle

**Fidelity is to TRUTH.**

The process is already decided: COPY.
The only job: Find the truth of what exists.

---

## Investigation: What IS the truth?

### Question 1: How does macOS know something is volatile?

The truth is: macOS doesn't have a concept of "volatile" as a category.

What macOS HAS:
- **File system events** - FSEvents API fires when files are created, modified, deleted
- **Process lifecycle** - Mach kernel tracks process creation, termination
- **Notifications** - NSDistributedNotificationCenter broadcasts events
- **Accessibility events** - AX API fires when UI elements change

These are THE SYSTEMS. They are event-driven. They fire when things happen.

### Question 2: What IS a volatile state?

The truth is: "Volatile" is OUR interpretation.

What ACTUALLY exists:
- A file in /tmp (the file exists, the OS tracks its lifecycle)
- A process in memory (the process exists, the kernel tracks its lifecycle)
- A UI element on screen (the element exists, accessibility tracks its lifecycle)

The "volatility" is just the LIFECYCLE characteristic - it will eventually not exist.

### Question 3: How does the OS track lifecycle?

**Files:**
- Created → FSEvent `kFSEventStreamEventFlagItemCreated`
- Modified → FSEvent `kFSEventStreamEventFlagItemModified`
- Deleted → FSEvent `kFSEventStreamEventFlagItemRemoved`

**Processes:**
- Started → `NSWorkspace.didLaunchApplicationNotification`
- Terminated → `NSWorkspace.didTerminateApplicationNotification`

**UI Elements:**
- Created → `AXUIElementCreateNotification`
- Changed → `AXValueChangedNotification`
- Destroyed → `AXUIElementDestroyedNotification`

**Clipboard:**
- Changed → `NSPasteboard.changeCount` increments

---

## The Truth

The truth is:

1. **Things exist** (files, processes, UI elements)
2. **The OS tracks their lifecycle via events** (created, changed, destroyed)
3. **"Volatile" is just things that will eventually be destroyed**
4. **The events are the truth** - they fire when existence changes

---

## What This Means for Copying

The truth to copy is: **THE EVENTS**

| What Exists | The Truth of Its Lifecycle | What We Copy |
|-------------|---------------------------|--------------|
| A file | FSEvent stream | The event (created/modified/deleted) |
| A process | Process notification | The event (started/terminated) |
| A UI element | AX notification | The event (appeared/changed/disappeared) |
| Clipboard content | changeCount increment | The event (content changed) |

We don't poll. We don't invent. We subscribe to THE TRUTH - the events that the OS itself uses to track existence.

---

## The Implementation Follows From Truth

Once we know the truth, the implementation is obvious:

```
TRUTH: FSEvents fires when files are created/modified/deleted
       ↓
COPY:  Subscribe to FSEvents, record what it tells us
```

```
TRUTH: Process notifications fire when apps start/stop
       ↓
COPY:  Subscribe to notifications, record what they tell us
```

```
TRUTH: AX notifications fire when UI elements change
       ↓
COPY:  Subscribe to AX notifications, record what they tell us
```

The schema follows from the truth of what the event contains.
The timing follows from when the event fires.
The structure follows from how the event is structured.

We copy the truth. The truth is the events.

---

## Next Step

Find the exact truth of each event type:
- What fields does an FSEvent contain?
- What fields does a process notification contain?
- What fields does an AX notification contain?

Then copy those fields. Exactly. As they are.
