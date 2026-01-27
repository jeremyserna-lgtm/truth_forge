# Universal Program Interaction Model

## Purpose

A framework for capturing everything a user can see, use, and interact with in any computer program. This model defines the foundational concepts that apply universally across all software applications, enabling comprehensive state capture regardless of the specific application being monitored.

---

## I. Core Ontology

### The Three Fundamental Dimensions

Every element in any program exists within three dimensions:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTENCE DIMENSIONS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DIMENSION 1: VISIBILITY                                        │
│  ├── VISIBLE: User can perceive it                             │
│  │   ├── Currently Shown: Rendered on screen now               │
│  │   ├── Accessible: Not shown but user can navigate to it     │
│  │   └── Indicated: Existence signaled (badge, count, icon)    │
│  │                                                              │
│  └── HIDDEN: User cannot perceive it                           │
│      ├── Conditionally Hidden: Becomes visible under rules     │
│      ├── Permanently Hidden: Never shown to this user          │
│      └── Structurally Hidden: Exists but no UI path to it     │
│                                                                 │
│  DIMENSION 2: INTERACTIVITY                                     │
│  ├── USABLE: User can change/trigger it                        │
│  │   ├── Direct: Click, type, drag                             │
│  │   ├── Indirect: Causes change via other action              │
│  │   └── Constrained: Usable only under conditions             │
│  │                                                              │
│  └── OBSERVABLE: User can only witness it                      │
│      ├── Pure Display: Shows information, no interaction       │
│      ├── System Output: Results of system actions              │
│      └── Other User State: What others control                 │
│                                                                 │
│  DIMENSION 3: MUTABILITY                                        │
│  ├── STATIC: Does not change                                   │
│  │   ├── Immutable: Cannot change by design                    │
│  │   └── Stable: Could change but hasn't                       │
│  │                                                              │
│  └── DYNAMIC: Changes over time                                │
│      ├── User-Caused: Changes from user actions                │
│      ├── System-Caused: Changes from application logic         │
│      ├── Time-Caused: Changes on schedule/timer                │
│      └── External-Caused: Changes from outside the program     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The State Space

Every program exists in a state space defined by:

```
STATE = (Elements, Relationships, Context)

Where:
  Elements = all discrete things that exist
  Relationships = how elements connect to each other
  Context = environmental conditions (time, user, session)
```

---

## II. Element Classification System

### Level 0: Existence Classes

```
EXISTENCE_CLASS:
  ├── REAL: Actually exists in program memory/state
  │   ├── Materialized: Has concrete representation
  │   └── Virtual: Exists only as computed value
  │
  ├── POTENTIAL: Could exist under certain conditions
  │   ├── Conditional: Will exist if condition met
  │   └── Future: Will exist at future time
  │
  └── PHANTOM: Referenced but doesn't exist
      ├── Placeholder: UI slot for something not yet there
      └── Reference: Points to non-existent thing
```

### Level 1: Primary Types

Every element in any program falls into one of these primary types:

```
PRIMARY_TYPE:
  ├── CONTAINER: Holds other elements
  │   ├── Window: Top-level viewport
  │   ├── Panel: Section within window
  │   ├── List: Collection of similar items
  │   ├── Group: Collection of related items
  │   └── Viewport: Scrollable/paginated view area
  │
  ├── CONTROL: User can manipulate
  │   ├── Button: Triggers action
  │   ├── Input: Accepts user data
  │   ├── Toggle: Binary state switch
  │   ├── Selector: Choose from options
  │   ├── Slider: Range value control
  │   └── Handle: Resize/move controller
  │
  ├── DISPLAY: Shows information
  │   ├── Text: Readable content
  │   ├── Media: Image/video/audio
  │   ├── Indicator: Status representation
  │   ├── Graph: Data visualization
  │   └── Avatar: User/entity representation
  │
  ├── CONTENT: User-generated or retrieved data
  │   ├── Message: Communication unit
  │   ├── Document: Structured content
  │   ├── Record: Data entry
  │   └── Asset: Binary content (file, image)
  │
  └── SYSTEM: Program infrastructure
      ├── Session: User's connection state
      ├── Permission: Access control state
      ├── Setting: Configuration value
      └── Event: Something that happened
```

### Level 2: Visibility States

```
VISIBILITY_STATE:
  ├── SHOWN
  │   ├── Prominent: In primary focus area
  │   ├── Peripheral: In secondary area
  │   ├── Minimized: Collapsed but present
  │   └── Obscured: Behind another element
  │
  ├── ACCESSIBLE
  │   ├── Navigable: Can reach via UI action
  │   ├── Searchable: Can find via search
  │   └── Deep-Linked: Can reach via direct path
  │
  ├── INDICATED
  │   ├── Badged: Shows count/notification
  │   ├── Iconified: Represented by icon only
  │   └── Referenced: Mentioned in visible element
  │
  └── HIDDEN
      ├── Role-Hidden: Not available for user's role
      ├── State-Hidden: Not available in current state
      ├── Time-Hidden: Not available at this time
      ├── Feature-Hidden: Feature not enabled
      └── Implementation-Hidden: Exists but no UI exposure
```

### Level 3: Interaction Modes

```
INTERACTION_MODE:
  ├── ACTIVE
  │   ├── Click: Single activation
  │   ├── Double-Click: Enhanced activation
  │   ├── Long-Press: Held activation
  │   ├── Type: Text input
  │   ├── Drag: Move/reorder
  │   ├── Drop: Place dragged item
  │   ├── Scroll: Navigate within view
  │   ├── Pinch/Zoom: Scale view
  │   └── Gesture: Complex input pattern
  │
  ├── PASSIVE
  │   ├── Hover: Mouse presence
  │   ├── Focus: Keyboard target
  │   └── Select: Chosen but not activated
  │
  └── DISABLED
      ├── Grayed: Visible but inactive
      ├── Blocked: Action prevented
      └── Removed: No longer available
```

---

## III. Change Model

### Change Categories

Every change in any program falls into one of these categories:

```
CHANGE_TYPE:
  ├── APPEARANCE_CHANGE
  │   ├── Visibility: show/hide
  │   ├── Position: move
  │   ├── Size: resize
  │   ├── Style: color, font, border
  │   └── Order: z-index, list order
  │
  ├── CONTENT_CHANGE
  │   ├── Addition: new content added
  │   ├── Modification: existing content changed
  │   ├── Deletion: content removed
  │   └── Replacement: old content swapped for new
  │
  ├── STATE_CHANGE
  │   ├── Activation: enabled/disabled
  │   ├── Selection: selected/deselected
  │   ├── Mode: operating mode switch
  │   └── Phase: lifecycle stage change
  │
  └── RELATIONSHIP_CHANGE
      ├── Association: elements linked
      ├── Dissociation: elements unlinked
      ├── Reordering: sequence changed
      └── Hierarchy: parent-child changed
```

### Change Triggers

What causes changes:

```
TRIGGER_TYPE:
  ├── USER_ACTION
  │   ├── Direct: User explicitly acted
  │   ├── Indirect: User action caused cascade
  │   └── Implicit: User presence/behavior
  │
  ├── SYSTEM_ACTION
  │   ├── Scheduled: Timer/cron triggered
  │   ├── Reactive: Response to event
  │   ├── Proactive: System-initiated
  │   └── Maintenance: Cleanup/optimization
  │
  ├── EXTERNAL_ACTION
  │   ├── Other User: Another user acted
  │   ├── Integration: External system acted
  │   └── Network: Connection state changed
  │
  └── TEMPORAL
      ├── Clock: Time-based trigger
      ├── Duration: After elapsed time
      └── Deadline: At specific time
```

### Change Capture Model

```
CHANGE_RECORD:
  timestamp: When change detected
  element_id: What changed
  change_type: Category of change
  trigger_type: What caused it
  before_state: State before change
  after_state: State after change
  related_changes: Other changes in same transaction
  user_attribution: If user caused, which user
  reversible: Can this be undone
  captured_evidence: Screenshot, state dump, etc.
```

---

## IV. Decision Layers

What determines what a user sees and can do:

```
DECISION_LAYER:
  ├── LAYER 0: EXISTENCE
  │   │  Does this element exist at all?
  │   ├── Feature Flag: Is feature enabled?
  │   ├── Version: Is this version active?
  │   └── Configuration: Is it configured to exist?
  │
  ├── LAYER 1: PERMISSION
  │   │  Is user allowed to access this?
  │   ├── Role: User's role allows access?
  │   ├── Subscription: User's tier includes this?
  │   ├── Ownership: User owns/created this?
  │   └── Grant: User was specifically given access?
  │
  ├── LAYER 2: CONTEXT
  │   │  Does context allow this?
  │   ├── State: Is system in right state?
  │   ├── Time: Is it the right time?
  │   ├── Location: Is user in right place?
  │   └── Device: Does device support this?
  │
  ├── LAYER 3: PRESENTATION
  │   │  How is it being shown?
  │   ├── Layout: Where does it appear?
  │   ├── Priority: What order/prominence?
  │   ├── Personalization: User preferences?
  │   └── Responsive: Screen size adaptation?
  │
  └── LAYER 4: INTERACTION
      │  Can user interact with it now?
      ├── Enabled: Is control active?
      ├── Focused: Can it receive input?
      ├── Blocked: Is something preventing it?
      └── Busy: Is it processing something?
```

---

## V. Capture Architecture

### What Must Be Captured

To fully represent a user's experience with any program:

```
CAPTURE_REQUIREMENTS:
  ├── ELEMENT INVENTORY
  │   │  All elements that exist
  │   ├── Complete element list with types
  │   ├── Element hierarchy (parent-child)
  │   ├── Element relationships (links, references)
  │   └── Element metadata (ids, names, attributes)
  │
  ├── VISIBILITY MAP
  │   │  What user can see at any moment
  │   ├── Currently rendered elements
  │   ├── Elements user could navigate to
  │   ├── Elements that are indicated but not shown
  │   └── Elements that exist but are hidden (and why)
  │
  ├── INTERACTION MAP
  │   │  What user can do at any moment
  │   ├── Currently actionable controls
  │   ├── Disabled controls (and why disabled)
  │   ├── Hidden controls (and why hidden)
  │   └── Interaction modes available
  │
  ├── CONTENT SNAPSHOT
  │   │  What data exists at any moment
  │   ├── All content in containers
  │   ├── All values in controls
  │   ├── All text in displays
  │   └── All state in system elements
  │
  ├── CHANGE STREAM
  │   │  All changes over time
  │   ├── Change records with full context
  │   ├── Change sequences (related changes)
  │   ├── Change patterns (recurring changes)
  │   └── Change anomalies (unexpected changes)
  │
  └── DECISION STATE
      │  Why things are as they are
      ├── Active feature flags
      ├── User's permissions
      ├── Current context conditions
      ├── Presentation rules in effect
      └── Interaction constraints active
```

### Capture Timing

When to capture:

```
CAPTURE_TRIGGERS:
  ├── EVENT-DRIVEN
  │   │  Capture when something happens
  │   ├── User Action: Any user input
  │   ├── State Change: Any state transition
  │   ├── Content Change: Any content modification
  │   └── Error: Any error condition
  │
  ├── TEMPORAL
  │   │  Capture on schedule
  │   ├── Heartbeat: Regular interval (e.g., 30s)
  │   ├── Session Boundary: Start/end of session
  │   └── Time Marker: Specific times (midnight, etc.)
  │
  ├── FORCED
  │   │  Capture on demand
  │   ├── Manual Trigger: User requests capture
  │   ├── Signal: External signal received
  │   └── API Call: Programmatic request
  │
  └── CONDITION
      │  Capture when condition met
      ├── Threshold: Value exceeds limit
      ├── Pattern: Sequence matches pattern
      └── Anomaly: Deviation from normal
```

---

## VI. Application Model

### How To Apply This Framework

For any specific application:

#### Step 1: Element Inventory

```python
# Enumerate all elements in the application
def inventory_elements(application):
    elements = []
    for element in application.get_all_elements():
        elements.append({
            "id": element.id,
            "type": classify_type(element),
            "parent": element.parent.id if element.parent else None,
            "children": [c.id for c in element.children],
            "visibility": classify_visibility(element),
            "interactivity": classify_interactivity(element),
            "mutability": classify_mutability(element),
        })
    return elements
```

#### Step 2: Visibility Mapping

```python
# Map what user can see
def map_visibility(application, user):
    visible = []
    accessible = []
    indicated = []
    hidden = []

    for element in application.elements:
        if element.is_rendered():
            visible.append(element)
        elif element.is_navigable_by(user):
            accessible.append(element)
        elif element.is_indicated_to(user):
            indicated.append(element)
        else:
            hidden.append({
                "element": element,
                "reason": determine_hidden_reason(element, user)
            })

    return {
        "visible": visible,
        "accessible": accessible,
        "indicated": indicated,
        "hidden": hidden
    }
```

#### Step 3: Change Detection

```python
# Detect changes between states
def detect_changes(before_state, after_state):
    changes = []

    # Check for added elements
    for elem in after_state.elements:
        if elem not in before_state.elements:
            changes.append({
                "type": "addition",
                "element": elem,
                "timestamp": now()
            })

    # Check for removed elements
    for elem in before_state.elements:
        if elem not in after_state.elements:
            changes.append({
                "type": "deletion",
                "element": elem,
                "timestamp": now()
            })

    # Check for modified elements
    for elem in before_state.elements:
        if elem in after_state.elements:
            before = before_state.get_state(elem)
            after = after_state.get_state(elem)
            if before != after:
                changes.append({
                    "type": "modification",
                    "element": elem,
                    "before": before,
                    "after": after,
                    "timestamp": now()
                })

    return changes
```

#### Step 4: Complete State Capture

```python
# Capture complete state at a point in time
def capture_complete_state(application, user, trigger):
    return {
        "timestamp": now(),
        "trigger": trigger,
        "user": user.id,
        "session": user.session.id,

        "elements": inventory_elements(application),
        "visibility": map_visibility(application, user),
        "content": capture_all_content(application),
        "controls": capture_all_control_states(application),

        "decisions": {
            "feature_flags": application.get_feature_flags(),
            "permissions": user.get_permissions(),
            "context": application.get_context(),
            "constraints": application.get_constraints()
        },

        "ui_state": {
            "windows": get_window_states(application),
            "focus": get_focused_element(application),
            "selection": get_selected_elements(application),
            "scroll_positions": get_scroll_positions(application),
            "pagination": get_pagination_states(application)
        }
    }
```

---

## VII. Universal State Tree

### Complete State Model

```
APPLICATION_STATE
├── identity
│   ├── application_id: Unique application identifier
│   ├── version: Application version
│   ├── instance_id: This running instance
│   └── session_id: Current user session
│
├── user
│   ├── user_id: User identifier
│   ├── role: User's role
│   ├── permissions: What user can do
│   ├── preferences: User settings
│   └── session_state: User's session data
│
├── structure
│   ├── elements[]: All elements that exist
│   │   ├── id: Element identifier
│   │   ├── type: Element classification
│   │   ├── parent: Parent element
│   │   ├── children[]: Child elements
│   │   └── relationships[]: Other connections
│   │
│   └── hierarchy: Element tree structure
│
├── visibility
│   ├── rendered[]: Currently on screen
│   ├── accessible[]: Navigable to
│   ├── indicated[]: Existence signaled
│   ├── hidden[]: Not visible
│   │   └── reason: Why hidden
│   └── constraints: What limits visibility
│
├── interactivity
│   ├── enabled[]: Can interact with
│   ├── disabled[]: Cannot interact with
│   │   └── reason: Why disabled
│   ├── focused: Current focus target
│   └── selected[]: Currently selected
│
├── content
│   ├── data[]: All data/content items
│   │   ├── id: Content identifier
│   │   ├── type: Content type
│   │   ├── value: Content value
│   │   ├── source: Where it came from
│   │   └── timestamps: Created, modified
│   │
│   └── relationships: Content connections
│
├── ui_state
│   ├── windows[]
│   │   ├── id: Window identifier
│   │   ├── title: Window title
│   │   ├── position: (x, y)
│   │   ├── size: (width, height)
│   │   ├── state: normal/minimized/maximized/fullscreen
│   │   ├── z_order: Stacking order
│   │   └── visible: Is window visible
│   │
│   ├── viewports[]
│   │   ├── id: Viewport identifier
│   │   ├── scroll_position: Current scroll
│   │   ├── total_content_size: Full content dimensions
│   │   ├── visible_area: What's currently shown
│   │   └── pagination: Page state if paginated
│   │
│   └── layout
│       ├── mode: Layout mode (grid, list, etc.)
│       ├── density: Compact/normal/comfortable
│       └── responsive_state: Current breakpoint
│
├── decisions
│   ├── feature_flags: What features are enabled
│   ├── permissions: What actions are allowed
│   ├── context: Environmental conditions
│   ├── rules: Business rules in effect
│   └── constraints: Technical limitations
│
└── temporal
    ├── captured_at: Timestamp of capture
    ├── session_started: Session start time
    ├── last_interaction: Last user action
    └── changes_since_last_capture: Delta
```

---

## VIII. Black Zones (Universal)

What cannot be captured in any program:

```
UNIVERSAL_BLACK_ZONES:
  ├── SERVER-ONLY STATE
  │   │  State that never reaches client
  │   ├── Server-side session data
  │   ├── Other users' private data
  │   ├── Encryption keys and secrets
  │   └── Audit logs of other users
  │
  ├── ENCRYPTED DATA
  │   │  Data encrypted without our key
  │   ├── End-to-end encrypted content
  │   ├── Server-encrypted databases
  │   └── Hardware-encrypted storage
  │
  ├── PAST STATE
  │   │  State before capture started
  │   ├── Historical data not retrieved
  │   ├── Deleted content
  │   └── Previous session state
  │
  ├── INTERNAL PROCESSING
  │   │  Ephemeral computational state
  │   ├── Memory during execution
  │   ├── CPU register state
  │   └── Network packet contents
  │
  └── EXTERNAL SYSTEMS
      │  State in systems we don't monitor
      ├── Backend databases
      ├── Third-party integrations
      └── Linked accounts
```

---

## IX. Implementation Checklist

For capturing any program comprehensively:

### Required Components

- [ ] **Element Extractor**: Enumerate all UI elements
- [ ] **State Capturer**: Capture element states
- [ ] **Change Detector**: Detect state transitions
- [ ] **Trigger System**: Event/temporal/force capture
- [ ] **Storage Backend**: Persist captured state
- [ ] **Query Interface**: Retrieve historical state

### Required Capture Points

- [ ] Session start/end
- [ ] Every user action
- [ ] Every state change
- [ ] Regular heartbeat intervals
- [ ] On-demand triggers

### Required Metadata

- [ ] Timestamps (capture time, event time)
- [ ] User identification
- [ ] Session identification
- [ ] Trigger reason
- [ ] Capture method

### Required Documentation

- [ ] Element inventory for the application
- [ ] Visibility rules and decision layers
- [ ] Interaction modes available
- [ ] Known black zones specific to application

---

## X. Scaling Guidelines

### Depth vs. Breadth

```
CAPTURE_DEPTH:
  ├── MINIMAL (Discovery)
  │   │  Just know what exists
  │   ├── Element inventory only
  │   └── Basic type classification
  │
  ├── STANDARD (Monitoring)
  │   │  Track what changes
  │   ├── Element states
  │   ├── Change detection
  │   └── Basic timing
  │
  ├── COMPREHENSIVE (Analysis)
  │   │  Understand behavior
  │   ├── Full state capture
  │   ├── Relationship mapping
  │   ├── Decision layer capture
  │   └── Content capture
  │
  └── FORENSIC (Complete)
      │  Reconstruct experience
      ├── Everything above
      ├── Visual capture (screenshots)
      ├── Timing precision (ms level)
      └── All black zones documented
```

### Application-Specific Extensions

When applying to a specific application, extend the base model:

```python
# Base model
UNIVERSAL_ELEMENT_TYPES = ["container", "control", "display", "content", "system"]

# Application-specific extension (example: video conferencing)
APPLICATION_ELEMENT_TYPES = UNIVERSAL_ELEMENT_TYPES + [
    "participant",      # Person in meeting
    "stream",          # Video/audio stream
    "reaction",        # Emoji reaction
    "annotation",      # Screen annotation
    "breakout_room",   # Sub-meeting container
]

# Application-specific visibility rules
APPLICATION_VISIBILITY_RULES = {
    "participant_video": {
        "depends_on": ["camera_enabled", "bandwidth_sufficient", "view_mode"],
        "hidden_reasons": ["camera_off", "poor_connection", "gallery_overflow"]
    }
}
```

---

## XI. Relationship to SPINE

This universal model maps to the Truth Engine SPINE hierarchy:

| Universal Concept | SPINE Level | Description |
|------------------|-------------|-------------|
| Application Instance | L8 | Conversation/Session |
| User Session | L7 | Session within application |
| Content Batch | L6 | Group of related content |
| Individual Content | L5 | Single message/record |
| Content Atoms | L1-L4 | Entities, sentiment, metadata |

---

**This framework provides the conceptual foundation for capturing any software application's complete user experience state.**

**Last Updated**: 2025-12-02
**Status**: Universal framework - apply to specific applications as needed
**Derived From**: Zoom Complete Interaction Taxonomy
