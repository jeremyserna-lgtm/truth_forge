> **DEPRECATED** - This document is superseded by [ZOOM_SOURCE_OF_TRUTH.md](../ZOOM_SOURCE_OF_TRUTH.md)
>
> This document is kept for historical reference only.

---

# Zoom Multi-Layer Capture Architecture

**Date:** 2025-12-02
**Status:** CANONICAL - Implementation must follow this document exactly
**Problem Statement:** The Adidas conversation existed, was visible, and should have been captured through multiple layers - but wasn't.

---

## Part 1: The Failure Analysis

### What Happened

On 2025-12-02, a 47+ message Zoom conversation with Adidas was lost. The daemon captured only 2 messages.

### Why It Happened

```
THE SPECIFICATION-IMPLEMENTATION GAP
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  SPECIFICATION (Documented - Correct):                          │
│  "Capture ALL messages in the conversation"                     │
│  "Temporary data vanishes when meeting ends"                    │
│  "Must capture at the RIGHT MOMENT"                             │
│                                                                 │
│  IMPLEMENTATION (Written - Incomplete):                         │
│  extract_chat_messages() only captured VISIBLE messages         │
│  Zoom virtualizes rendering - only visible rows exist in UI     │
│  Messages above/below scroll area were not captured             │
│                                                                 │
│  VERIFICATION (Skipped - Fatal):                                │
│  Nobody tested: "Does output contain ALL messages?"             │
│  Nobody compared: captured count vs actual count                │
│  Implementation was assumed correct because it ran              │
│                                                                 │
│  RESULT: 47 messages existed → 2 captured → 45 lost             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The Root Cause

**The implementation was not verified against the specification.**

- Specification said: "Capture ALL messages"
- Implementation captured: "Visible messages"
- Gap: 45 messages
- Verification: Never performed
- Result: Thought it worked. It didn't.

---

## Part 2: The Principle - Complete Data Existence Mirror

### Core Truth

**BigQuery must be a complete mirror of Zoom's entire data existence ontology.**

Not just chat content - every layer of how data EXISTS in Zoom must exist in BigQuery.

### What This Means

```
ZOOM DATA EXISTENCE                    BIGQUERY MIRROR
==================                     ===============

L0: ENCRYPTED (Can't Read)       →     Know it EXISTS (metadata only)
    - zoomus.zmdb                       - encrypted_data_existence
    - Contact history                   - What databases exist
    - Historical chats                  - What tables they have
    - Can't decrypt                     - Size, modification times
                                        - TRUTH: "Data exists but content inaccessible"

L1: CONVERSATION (Entity)        →     Full conversation as entity
    - Chat history as whole             - conversation_states
    - Has beginning, messages, end      - Complete scrollable history
    - Exists as coherent unit           - Temporal versions (every 30s)
                                        - TRUTH: "Conversation as it exists at time T"

L2: MESSAGE (Atomic Event)       →     Messages as send/receive events
    - Each message sent/received        - message_events
    - Event-driven, momentary           - Timestamp of event
    - Comes into existence, persists    - Direction (sent/received)
                                        - TRUTH: "Message M existed at time T"

L3: VISION (What's Visible)      →     UI visibility state
    - What's currently rendered         - vision_states
    - Scroll position                   - What messages are visible NOW
    - Window state                      - Which DM thread is open
                                        - TRUTH: "At time T, user saw X"

L4: PROCESSING (Behind Vision)   →     System state before rendering
    - Message queue                     - processing_states
    - Unread indicators                 - Pending messages
    - Notifications                     - Read/unread status
                                        - TRUTH: "System has M, vision shows N"

L5: TEMPORAL (Versions)          →     Point-in-time snapshots
    - Conversation at 10:00 AM          - temporal_snapshots
    - Conversation at 10:30 AM          - Every capture is a version
    - Delta between snapshots           - Can reconstruct any point
                                        - TRUTH: "At time T, state was S"

L6: VOLATILE (Process Memory)    →     Temporary state capture
    - Chat in process memory            - volatile_states
    - Will vanish when meeting ends     - Captured before it disappears
    - Most complete version exists HERE - Continuous capture makes permanent
    - This is what we LOST              - TRUTH: "Temporary state T captured at time X"
                                        - GOAL: Make ephemeral permanent
```

### The Volatile State Problem (Adidas Case)

```
WHAT HAPPENED:
==============
Zoom stores chat messages in PROCESS MEMORY during meeting
                                     ↓
When meeting ends, process memory is released
                                     ↓
Chat messages vanish - they were TEMPORARY
                                     ↓
We captured visible window (2 messages)
                                     ↓
Full conversation (47 messages) was in volatile memory
                                     ↓
Meeting ended → Volatile memory released → 45 messages LOST FOREVER

THE SOLUTION:
=============
Capture volatile state CONTINUOUSLY
                                     ↓
Every 30 seconds, capture EVERYTHING in volatile memory
                                     ↓
Store as volatile_state snapshot in BigQuery
                                     ↓
Volatile becomes permanent through capture
                                     ↓
Even if meeting ends, we have all snapshots
                                     ↓
Most complete version is the LAST snapshot before meeting end
```

### The Complete Principle

1. **Everything I can SEE** → Captured (vision layer)
2. **Everything I can ACCESS** → Captured (conversation layer)
3. **Everything I can USE** → Captured (message events)
4. **Everything that MANIFESTS** → Captured (processing layer)
5. **Everything I CAN'T SEE but know EXISTS** → Metadata captured (encrypted layer)

**The ONLY thing not captured is encrypted content I cannot access.
But even then, I capture the TRUTH that it exists.**

---

## Part 2B: The Pure Copy Principle - Stage 0 Extraction

### Core Truth

**Stage 0 (Extraction) does ONE thing: Copy and bring over. Nothing else.**

The extraction layer exists as it exists in Zoom. It does not transform. It does not encode. It does not parse. It does not clean up. It copies.

### What This Means

```
EXTRACTION (STAGE 0) RULES
==========================

✅ ALLOWED:
- Copy data exactly as it exists
- Store exactly as it was found
- Preserve all original structure
- Preserve all original encoding
- Preserve all original format
- Store bytes as bytes
- Store strings as strings
- Store JSON as JSON (not parsed)

❌ NOT ALLOWED:
- Parse or interpret content
- Clean up formatting
- Normalize encoding
- Extract sub-components
- Add metadata that changes meaning
- Transform structure
- Combine or split data
- Apply any business logic

THE ONLY GOAL: Make a faithful copy in BigQuery
```

### Why This Matters

```
ZOOM (Source of Truth)                 BIGQUERY (Mirror of Truth)
======================                 ==========================

Exactly as it exists           →       Exactly as it exists
                                       (same bytes, same structure)

                               ↓

                        LATER STAGES (2, 3, 4...)
                        Do parsing, cleanup, enrichment
                        BUT Stage 0 remains pristine
```

### The Principle

1. **Stage 0 is a copy operation** - Nothing more
2. **BigQuery becomes the new source of truth** - Identical to Zoom at capture moment
3. **All transformation happens AFTER Stage 0** - In later stages
4. **Stage 0 data is never modified** - Immutable capture
5. **You can always reconstruct** - Because Stage 0 is pristine

### Storage Pattern

```sql
-- Stage 0: Raw mirror of Zoom (IMMUTABLE)
zoom_capture.raw_sessions        -- Entire session JSON as captured
zoom_capture.raw_messages        -- Individual messages, byte-for-byte
zoom_capture.raw_participants    -- Participant data exactly as found
zoom_capture.raw_encrypted_meta  -- Metadata about encrypted data

-- Later Stages: Transformed data (derived from Stage 0)
zoom_enriched.parsed_messages    -- Stage 2+ processing
zoom_enriched.cleaned_text       -- Stage 3+ cleanup
zoom_enriched.entities           -- Stage 4+ extraction
```

### Verification

Stage 0 is correct when:
- **Byte comparison**: Stage 0 data = Original data (bit-for-bit if possible)
- **Structure preservation**: JSON structure unchanged
- **No added fields**: Nothing inserted except capture metadata (timestamp, capture_id)
- **No removed fields**: All original data present
- **No encoding changes**: Character encoding preserved

---

## Part 3: The Verification Protocol (MANDATORY)

**Any implementation of this architecture MUST follow this protocol. Implementation is NOT complete until all steps pass.**

### Step 1: Specification (What Exactly Should Happen)

Before writing any code, document:

| Question | Answer |
|----------|--------|
| What is being captured? | ALL messages in a Zoom chat conversation |
| How many should be captured? | EVERY message that exists, regardless of scroll position |
| When should capture happen? | On every message send/receive, every 30s, and on demand |
| What is the success metric? | Captured message count = Actual message count |

### Step 2: Implementation (Write Code That Claims To Do It)

Write code according to specification. Code must:
- Scroll through entire chat history (not just visible window)
- Capture every message encountered during scroll
- Deduplicate by message content/time/sender hash
- Store with full metadata

### Step 3: Verification (Test Against Known State)

**This step is MANDATORY. Do not skip.**

```
VERIFICATION TEST PROCEDURE
===========================
1. Create a test conversation with KNOWN message count
   - Send exactly 20 messages in a Zoom chat
   - Note the exact count: 20

2. Run the capture implementation
   - Execute daemon with full capture mode
   - Let it complete

3. Compare output to expected
   - Count messages in output file
   - Expected: 20
   - Actual: [count from output]

4. Evaluate
   - If Actual = Expected: PASS - proceed to validation
   - If Actual ≠ Expected: FAIL - fix implementation, repeat from step 2
```

### Step 4: Validation (Test Against Reality)

**This step is MANDATORY. Do not skip.**

```
VALIDATION TEST PROCEDURE
=========================
1. Real Zoom conversation (not test)
   - During active meeting
   - Manually scroll through chat and count messages
   - Record count: [manual count]

2. Run capture
   - Execute daemon with full capture mode
   - Let it complete

3. Compare to reality
   - Count messages in output
   - Compare to manual count

4. Evaluate
   - If counts match: VALIDATED
   - If counts differ: NOT VALIDATED - investigate discrepancy
```

### Step 5: Documentation (Record What Was Tested)

After verification and validation pass, document:

```
VERIFICATION RECORD
===================
Date: [date]
Test type: [verification/validation]
Input: [description of test input]
Expected output: [what should have happened]
Actual output: [what actually happened]
Result: [PASS/FAIL]
Notes: [any observations]
```

---

## Part 4: Required Architecture

### Layer 1: EVENT CAPTURE (On Message)

```
┌─────────────────────────────────────────────────────────────────┐
│ Trigger: Every message send/receive                             │
│ Method: Accessibility event monitoring (UI element changes)     │
│ Captures:                                                       │
│   - Individual message as atomic event                          │
│   - Timestamp of event                                          │
│   - Sender, content, context                                    │
│   - Event type (sent/received/edited/deleted)                   │
│ Storage: zoom_capture.events                                    │
│                                                                 │
│ WHY: Even if periodic capture misses it, the event was caught   │
│                                                                 │
│ VERIFICATION REQUIREMENT:                                       │
│   - Send 5 messages rapidly                                     │
│   - Verify 5 events captured                                    │
│   - If not 5: implementation incorrect                          │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 2: STATE CAPTURE (Periodic - Every 30 Seconds)

```
┌─────────────────────────────────────────────────────────────────┐
│ Trigger: Every 30 seconds during active meeting                 │
│ Method: Accessibility API with FULL SCROLL-THROUGH              │
│ Captures:                                                       │
│   - COMPLETE conversation state (ALL messages, not just visible)│
│   - Scroll from top to bottom, capture every message            │
│   - All participants in current session                         │
│   - Session metadata (meeting name, host, etc.)                 │
│ Storage: zoom_capture.states                                    │
│                                                                 │
│ WHY: Redundancy - catches anything events missed                │
│                                                                 │
│ VERIFICATION REQUIREMENT:                                       │
│   - Create conversation with 30 messages (more than visible)    │
│   - Run state capture                                           │
│   - Verify 30 messages in output                                │
│   - If not 30: scroll-through implementation incorrect          │
└─────────────────────────────────────────────────────────────────┘
```

### Layer 3: FORCE CAPTURE (On Demand)

```
┌─────────────────────────────────────────────────────────────────┐
│ Trigger: Manual command (--force flag) or API call              │
│ Method: Complete scroll-through of entire chat history          │
│ Captures:                                                       │
│   - EVERYTHING visible in chat (full scroll-through)            │
│   - Marked as "force capture" with timestamp                    │
│   - Full conversation reconstruction                            │
│ Storage: zoom_capture.force_captures                            │
│                                                                 │
│ WHY: Definitive snapshot when you KNOW you want it              │
│                                                                 │
│ VERIFICATION REQUIREMENT:                                       │
│   - Same as Layer 2: known message count → capture → compare    │
│   - Force capture must capture ALL messages, not visible subset │
└─────────────────────────────────────────────────────────────────┘
```

### Reconstruction Layer

```
┌─────────────────────────────────────────────────────────────────┐
│ Purpose: Rebuild any conversation at any point in time          │
│ Method: Merge events + states + force captures                  │
│ Output:                                                         │
│   - Complete conversation as it existed                         │
│   - Timeline of changes                                         │
│   - Gaps identified if any layer missed something               │
│                                                                 │
│ WHY: Multiple layers = redundancy = nothing lost                │
│                                                                 │
│ VERIFICATION REQUIREMENT:                                       │
│   - Create conversation with 50 messages                        │
│   - Capture via all three layers                                │
│   - Reconstruct                                                 │
│   - Verify: 50 unique messages in reconstruction                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Part 5: Implementation Requirements

### For State Capture (Full Scroll-Through)

The extraction MUST:

1. **Focus the chat scroll area**
2. **Navigate to TOP of conversation** (Home key or Cmd+Home)
3. **Capture all visible messages**
4. **Scroll DOWN one page**
5. **Capture newly visible messages** (deduplicate against already captured)
6. **Repeat steps 4-5 until no new messages found**
7. **Return ALL captured messages**

```
SCROLL-THROUGH ALGORITHM
========================
seenMessages = {}
allMessages = []

scrollToTop()
while True:
    visibleMessages = getVisibleMessages()
    newMessagesFound = False

    for msg in visibleMessages:
        key = hash(msg.time + msg.sender + msg.content)
        if key not in seenMessages:
            seenMessages[key] = True
            allMessages.append(msg)
            newMessagesFound = True

    if not newMessagesFound:
        break  # Reached end of conversation

    scrollDown()

return allMessages
```

### For Event Capture

The event capture MUST:

1. **Monitor for UI changes** in chat window
2. **Detect new message elements** appearing
3. **Capture message immediately** when detected
4. **Store as atomic event** with timestamp

### Verification Test Cases

Before any implementation is considered complete, these tests MUST pass:

| Test | Input | Expected | Implementation Status |
|------|-------|----------|----------------------|
| TC-1: Visible messages only | 5 messages, all visible | 5 captured | Must pass |
| TC-2: Messages beyond scroll | 30 messages, 10 visible | 30 captured | Must pass |
| TC-3: Rapid message burst | 10 messages in 5 seconds | 10 captured | Must pass |
| TC-4: Force capture | 50 message history | 50 captured | Must pass |
| TC-5: Real conversation | Manual count N | N captured | Must pass |

---

## Part 6: Data Model - Complete Data Existence Mirror

The schema mirrors Zoom's complete data existence ontology. Stage 0 tables are immutable pure copies. Later stage tables are derived transformations.

### LAYER 0: Encrypted Data Existence (Can't Read, Know It Exists)

```sql
-- Metadata about encrypted data we cannot access
CREATE TABLE zoom_capture.encrypted_data_existence (
    capture_id STRING NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,

    -- What exists (but we can't read)
    database_path STRING,           -- e.g., ~/Library/Application Support/zoom.us/data/zoomus.zmdb
    database_exists BOOL,
    database_size_bytes INT64,
    database_modified_at TIMESTAMP,

    -- What tables exist (schema only, no data)
    table_names ARRAY<STRING>,      -- ['ZMESSAGE', 'ZCONTACT', ...]

    -- The truth we capture
    truth_statement STRING,         -- "Data exists but content inaccessible"

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### LAYER 1: Conversation States (Full Entity at Point in Time)

```sql
-- Complete conversation as it exists at capture moment (STAGE 0 - IMMUTABLE)
CREATE TABLE zoom_capture.conversation_states (
    state_id STRING NOT NULL,
    capture_id STRING NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,

    -- Session identity
    session_id STRING NOT NULL,
    meeting_name STRING,

    -- Complete conversation - RAW, no parsing
    raw_conversation_json STRING,   -- Entire chat as JSON, byte-for-byte
    message_count INT64,            -- Count only, no transformation

    -- Capture metadata (only allowed additions)
    capture_method STRING,          -- 'full_scroll_through'
    scroll_iterations INT64,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### LAYER 2: Message Events (Atomic Send/Receive)

```sql
-- Individual message events as they happen (STAGE 0 - IMMUTABLE)
CREATE TABLE zoom_capture.message_events (
    event_id STRING NOT NULL,
    capture_id STRING NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,

    -- Event identity
    session_id STRING,
    event_type STRING NOT NULL,     -- 'sent', 'received', 'edited', 'deleted'

    -- Raw message - NO PARSING
    raw_message_json STRING,        -- Entire message object as captured

    -- Capture metadata only
    capture_method STRING,          -- 'accessibility_event'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### LAYER 3: Vision States (What's Visible in UI)

```sql
-- UI visibility state at capture moment (STAGE 0 - IMMUTABLE)
CREATE TABLE zoom_capture.vision_states (
    vision_id STRING NOT NULL,
    capture_id STRING NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,

    -- What's visible
    session_id STRING,
    visible_messages_json STRING,   -- Messages currently rendered in viewport
    visible_message_count INT64,
    scroll_position STRING,         -- 'top', 'middle', 'bottom'

    -- UI state
    chat_window_open BOOL,
    active_chat_tab STRING,         -- 'everyone', 'dm:{participant}'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### LAYER 4: Processing States (System State Behind Vision)

```sql
-- System state before rendering (STAGE 0 - IMMUTABLE)
CREATE TABLE zoom_capture.processing_states (
    processing_id STRING NOT NULL,
    capture_id STRING NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,

    session_id STRING,

    -- What system knows (that vision may not show)
    total_message_count INT64,      -- System's count
    unread_count INT64,
    pending_messages_json STRING,   -- Messages queued but not rendered

    -- Participants state
    participants_json STRING,       -- All participants system knows about

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### LAYER 5: Temporal Snapshots (Point-in-Time Versions)

```sql
-- Every capture is a temporal version (STAGE 0 - IMMUTABLE)
CREATE TABLE zoom_capture.temporal_snapshots (
    snapshot_id STRING NOT NULL,
    capture_id STRING NOT NULL,
    snapshot_timestamp TIMESTAMP NOT NULL,

    session_id STRING NOT NULL,

    -- Complete state at this moment
    conversation_state_id STRING,   -- FK to conversation_states
    vision_state_id STRING,         -- FK to vision_states
    processing_state_id STRING,     -- FK to processing_states

    -- Delta from previous snapshot
    previous_snapshot_id STRING,
    messages_added_count INT64,
    messages_changed_count INT64,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### LAYER 6: Volatile States (Process Memory - Ephemeral to Permanent)

```sql
-- Temporary state that vanishes when meeting ends - captured to make permanent
CREATE TABLE zoom_capture.volatile_states (
    volatile_id STRING NOT NULL,
    capture_id STRING NOT NULL,
    capture_timestamp TIMESTAMP NOT NULL,

    -- Session context
    session_id STRING NOT NULL,
    meeting_name STRING,

    -- The volatile state - what would vanish when meeting ends
    volatile_conversation_json STRING,   -- Complete chat from process memory
    volatile_message_count INT64,        -- Total messages in volatile state
    volatile_participants_json STRING,   -- All participants in volatile state
    volatile_participant_count INT64,

    -- Capture context
    meeting_active BOOL,                 -- Was meeting still active when captured
    capture_reason STRING,               -- periodic, event, session_end
    seconds_since_last_capture INT64,

    -- Completeness tracking
    is_complete_scroll BOOL,             -- Did capture scroll through entire conversation
    scroll_iterations INT64,

    -- Purpose statement
    truth_statement STRING DEFAULT 'Volatile state captured before disappearance',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    ingestion_date DATE NOT NULL
);
```

**Why This Layer Matters:**
- This is the layer where the Adidas conversation existed
- This is what vanishes when meeting ends
- Continuous capture of this layer makes ephemeral permanent
- The LAST volatile capture before session_end has the most complete state

### RECONSTRUCTION (Derived - NOT Stage 0)

```sql
-- Reconstructed conversation from all layers (DERIVED DATA)
CREATE TABLE zoom_enriched.reconstructed_conversations (
    conversation_id STRING NOT NULL,
    session_id STRING NOT NULL,

    -- Merged from all layers
    complete_messages JSON,
    participants ARRAY<STRING>,

    -- Source tracking
    source_conversation_states ARRAY<STRING>,
    source_message_events ARRAY<STRING>,
    source_vision_states ARRAY<STRING>,

    -- Completeness assessment
    gaps_detected BOOL,
    gap_details JSON,

    reconstruction_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);
```

### Schema Summary

```
STAGE 0 (IMMUTABLE - Pure Copy)          DERIVED (Transformation)
================================         ========================
L0: zoom_capture.encrypted_data_existence    zoom_enriched.parsed_messages
L1: zoom_capture.conversation_states         zoom_enriched.cleaned_text
L2: zoom_capture.message_events              zoom_enriched.entities
L3: zoom_capture.vision_states               zoom_enriched.reconstructed_conversations
L4: zoom_capture.processing_states
L5: zoom_capture.temporal_snapshots
L6: zoom_capture.volatile_states         ← THE CRITICAL LAYER (Adidas was here)
```

**L6 is the most critical layer.** This is where temporary data lives. Without capturing L6 continuously, data vanishes when meeting ends.

---

## Part 7: Success Criteria - Complete Data Existence Mirror

Implementation is complete when BigQuery is a **complete mirror of Zoom's data existence**.

### The Core Success Metric

```
FOR EVERY WAY DATA EXISTS IN ZOOM:
  BigQuery has a corresponding record that captures that existence

FOR EVERY MOMENT DATA CAN BE OBSERVED IN ZOOM:
  BigQuery has a temporal snapshot of that observation

FOR EVERY LAYER OF DATA EXISTENCE:
  BigQuery has a table that mirrors that layer
```

### Data Existence Criteria

| Layer | Zoom State | BigQuery Mirror | Success Test |
|-------|-----------|-----------------|--------------|
| L0 | Encrypted DBs exist | `encrypted_data_existence` | Metadata captured |
| L1 | Conversation as entity | `conversation_states` | Full chat captured |
| L2 | Message send/receive | `message_events` | Events captured |
| L3 | Visible in UI | `vision_states` | Viewport captured |
| L4 | System knowledge | `processing_states` | Counts captured |
| L5 | Point in time | `temporal_snapshots` | Versions captured |
| **L6** | **Process memory (temporary)** | `volatile_states` | **Ephemeral→Permanent** |

**L6 is the critical layer.** Without continuous L6 capture, temporary data vanishes when meeting ends.

### Pure Copy Criteria (Stage 0)

- [ ] **No transformation**: Raw data = Captured data (byte-for-byte)
- [ ] **No parsing**: JSON stored as string, not decomposed
- [ ] **No cleanup**: Whitespace, encoding preserved
- [ ] **No interpretation**: Content stored, not analyzed
- [ ] **Only allowed additions**: capture_id, capture_timestamp

### Verification Criteria

- [ ] TC-1 through TC-5 all PASS
- [ ] Verification records documented
- [ ] Real conversation validated (manual count = captured count)
- [ ] Byte comparison: captured JSON = original JSON

### Completeness Criteria

- [ ] **Everything I can see** is in BigQuery
- [ ] **Everything I can access** is in BigQuery
- [ ] **Everything I can use** is in BigQuery
- [ ] **Everything that manifests** is in BigQuery
- [ ] **Everything I can't see but know exists** has metadata in BigQuery

### Operational Criteria

- [ ] Daemon runs continuously without error
- [ ] All 6 Stage 0 tables populated
- [ ] Temporal snapshots captured every 30 seconds
- [ ] Message events captured in real-time
- [ ] Jeremy never has to copy-paste manually again

---

## Part 8: The Adidas Test Case (Retroactive Analysis)

### What Should Have Happened

```
LAYER 1 (Events): Every message sent/received → captured as event
LAYER 2 (State): Every 30 seconds → full conversation state captured
LAYER 3 (Force): When --force ran → complete scroll capture

RESULT: We would have the conversation from:
- 47 individual message events
- Multiple state snapshots showing conversation growth
- At least one force capture with complete history
```

### What Actually Happened

```
LAYER 1: Not implemented (no events captured)
LAYER 2: Implemented incorrectly (only visible messages captured)
LAYER 3: Not fully implemented (no scroll-through)

RESULT: We have only:
- 2 messages visible at capture moment
- Your manual copy-paste (adidas.txt)
```

### What We Learned

```
LESSON 1: Specification ≠ Implementation
- Knowing what to do is not doing it
- Documentation was correct; implementation was wrong

LESSON 2: Implementation ≠ Verification
- Code that runs is not code that works
- Must verify output matches specification

LESSON 3: Verification is mandatory, not optional
- If verification was done, gap would have been caught
- 47 messages specified → 2 captured → test fails → fix before deploy

LESSON 4: The verification step must be IN THE DOCUMENT
- So that implementers can't skip it
- So that future implementations include it automatically
- So that the pattern is followed every time
```

---

## Part 9: Implementation Checklist

Anyone implementing this architecture MUST complete this checklist:

```
IMPLEMENTATION CHECKLIST
========================

□ SPECIFICATION UNDERSTOOD
  - [ ] Read this entire document
  - [ ] Understand why previous implementation failed
  - [ ] Understand verification requirements

□ LAYER 1 IMPLEMENTED (Event Capture)
  - [ ] Code written for event detection
  - [ ] TC-3 (rapid burst) passes
  - [ ] Events stored in zoom_capture.events

□ LAYER 2 IMPLEMENTED (State Capture)
  - [ ] Code written with full scroll-through
  - [ ] TC-2 (beyond scroll) passes
  - [ ] States stored in zoom_capture.states

□ LAYER 3 IMPLEMENTED (Force Capture)
  - [ ] Code written with --force flag
  - [ ] TC-4 (50 messages) passes
  - [ ] Force captures stored correctly

□ ALL VERIFICATIONS PASSED
  - [ ] TC-1: Visible messages only - PASS
  - [ ] TC-2: Messages beyond scroll - PASS
  - [ ] TC-3: Rapid message burst - PASS
  - [ ] TC-4: Force capture - PASS
  - [ ] TC-5: Real conversation - PASS

□ VALIDATION COMPLETED
  - [ ] Real Zoom conversation used
  - [ ] Manual count recorded
  - [ ] Captured count matches manual count
  - [ ] Verification record documented

□ DEPLOYMENT READY
  - [ ] All tests pass
  - [ ] Daemon runs without error
  - [ ] BigQuery integration verified
```

---

## Part 10: The Timestamp Principle - Universal Basis

### Core Truth

**Timestamp is the universal basis of connection.**

- If it has a timestamp → it exists
- To exist → it needs a timestamp (an event triggered it)
- Computers record timestamps as part of records

### Why Timestamp is the Right Universal Basis

**The Logical Chain:**

```
VOLATILE STATE → requires knowing START and END (by definition)
              ↓
START/END → require TIME to distinguish them
              ↓
TIME → exists independently (self-evident, requires nothing else)
              ↓
Therefore: TIME is the minimal requirement for tracking existence
              ↓
TIMESTAMP = time encoded as data
              ↓
TIMESTAMP is the universal basis because:
  - Everything that exists, exists at some time
  - Everything that changes, changes at some time
  - Everything that ceases, ceases at some time
  - Time requires nothing else to be meaningful
```

**The Validation:**

| What We Need | Why Timestamp Enables It |
|-------------|-------------------------|
| Know something existed | Timestamp = proof it existed at that time |
| Know when it started | started_at timestamp |
| Know when it ended | ended_at timestamp |
| Know what else existed at the same time | Query by timestamp range |
| Know sequence of events | Order by timestamp |
| Know duration | ended_at - started_at |
| Give existence to things without timestamps | Capture timestamp = when we observed it |

**Time is Self-Evident:**
- Time doesn't need to be defined in terms of other things
- Time is the substrate everything else happens on
- This makes it the perfect universal basis
- Things WITH timestamps can be placed on timeline
- Things WITHOUT timestamps can be GIVEN timestamps at capture

### Timestamps Enable Future Layers

**Timestamps work for things that don't exist yet.**

Any future analytical layer can be created by defining timestamp boundaries:

```
EXISTING DATA (with timestamps)
         ↓
DEFINE NEW LAYER (using timestamp boundaries)
         ↓
NEW LAYER NOW EXISTS (queryable by timestamp)
```

**Example: Persona Layer**

If you want to analyze "which AI persona was active when this message was sent":

1. Define personas by timestamp boundaries:
   - Persona A: 2025-01-01 to 2025-06-15
   - Persona B: 2025-06-15 to present

2. Only one persona exists at a time (like clipboard)

3. Query: "All messages during Persona A"
   ```sql
   SELECT * FROM messages
   WHERE event_timestamp BETWEEN '2025-01-01' AND '2025-06-15'
   ```

**Any Layer You Define Later:**
- Drug bender layer: bender_started_at, bender_ended_at
- Focus session layer: session_started_at, session_ended_at
- Emotional state layer: state_started_at, state_ended_at
- Any logical grouping with timestamp boundaries

**Signals Get Timestamps:**
- If signal has timestamp → use it
- If signal doesn't → give it one at capture
- Everything becomes timestamp-addressable
- Future layers can always be built

### The Simple Approach

```
FIND WHAT EXISTS → FIND ITS TIMESTAMP → RECORD THE THING AND ITS TIMESTAMP
```

Every version that has a timestamp gets recorded. This is how you get far.

### The Zoom Hierarchy (On Timeline)

```
TIMELINE (Universal)
    │
    └── SESSION (meeting_id)
         │   - started_at timestamp (existence begins)
         │   - ended_at timestamp (existence ends)
         │
         └── PARTICIPANTS
         │    │   - arrived_at timestamp (existence begins)
         │    │   - departed_at timestamp (existence ends)
         │
         └── EVENTS (messages, reactions, etc.)
         │    │   - event_timestamp (moment it happened)
         │
         └── VOLATILE STATES
              │   - created_at_ts timestamp (existence begins)
              │   - destroyed_at_ts timestamp (existence ends)
```

### Why Timestamps Work

1. **Session determines volatile state existence** - When meeting_id has ended_at, volatile states cease
2. **Participants exist within sessions** - arrived_at/departed_at bound their existence
3. **Events occur within sessions** - Each has a timestamp marking when it happened
4. **Volatile states exist while session exists** - Their lifecycle maps to session lifecycle

### The Tables (system_capture dataset)

| Table | What Exists | Timestamp Fields |
|-------|-------------|------------------|
| `zoom_session_existence` | Meetings | started_at, ended_at |
| `zoom_participant_existence` | Users in meetings | arrived_at, departed_at |
| `zoom_event_existence` | Messages, reactions | event_timestamp |
| `zoom_volatile_existence` | Temp states | created_at_ts, destroyed_at_ts |

### The View: Complete Timeline

`zoom_complete_timeline` - Everything on the timeline:
- Sessions starting/ending
- Participants arriving/departing
- Events occurring
- Volatile states appearing/disappearing

All queryable by timestamp. All mapped to days. All proving existence through timestamps.

---

## Part 11: Change Log

| Date | Change | Reason |
|------|--------|--------|
| 2025-12-02 | Initial creation | Adidas conversation lost |
| 2025-12-02 | Added failure analysis | Document why first implementation failed |
| 2025-12-02 | Added verification protocol | Ensure future implementations don't repeat failure |
| 2025-12-02 | Added implementation checklist | Make verification mandatory, not optional |
| 2025-12-02 | Added Complete Data Existence Mirror model | BigQuery must mirror ALL layers of Zoom data existence |
| 2025-12-02 | Added Pure Copy Principle | Stage 0 is copy-only, no transformation |
| 2025-12-02 | Added 6-layer data model | L0-L5 capturing encrypted, conversation, message, vision, processing, temporal |
| 2025-12-02 | Updated success criteria | Complete data existence mirror as core metric |
| 2025-12-02 | Added L6 volatile_states | Capture process memory before it vanishes |
| 2025-12-02 | Added Volatile State Problem section | Document how temporary data caused Adidas loss |
| 2025-12-02 | Created all 7 BigQuery tables | L0-L6 tables now exist in zoom_capture dataset |
| 2025-12-02 | Added Timestamp Principle | Timestamp as universal basis of connection |
| 2025-12-02 | Created zoom_*_existence tables | Session, participant, event, volatile existence on timeline |
| 2025-12-02 | Created zoom_complete_timeline view | Everything on timeline queryable by timestamp |

---

*This document is the source of truth for Zoom capture implementation.*
*Implementation must follow this document exactly.*
*Verification is mandatory.*
*If verification fails, implementation is not complete.*
