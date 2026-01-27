# The Cycle: WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE

**Layer**: Theory (WHY)
**Purpose**: Understand the pulse of life that powers Truth Engine

---

## 🎓 LEARNING: What is "The Cycle"?

The Cycle is the **"pulse of life"** and the deterministic mechanism through which the system operates in the immediate processing moment. It's not about the past or future—it's about the act of processing in the present moment.

### The Core Insight

The Cycle is not a one-time event but a **continuous pulse**:

```
WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE
  ↑                                              ↓
  └────────────────── Loop Back ─────────────────┘
```

**Every operation in Truth Engine follows this cycle.**

---

## 💡 CONCEPT: The Six Stages

### 1. WANT: The User's Intent

**What it is**: The user's intent or request. The initial desire or need.

**Characteristics**:
- Comes from Me (The Architect)
- May be explicit ("Help me organize files")
- May be implicit (a backlog item, a system need)
- The starting point of all action

**In Code**:
```python
user_want = "Find all contacts named Adam"
backlog_item = "Process the new data files"
system_need = "Sync staging to BigQuery"
```

### 2. CHOOSE: The Decision Point

**What it is**: The selection of a specific action or task. The decision point.

**Characteristics**:
- Determines which path to take
- May involve multiple options
- Requires understanding the WANT
- Creates the plan

**In Code**:
```python
# Choose the appropriate service
if "contact" in user_want.lower():
    service = get_contacts_service()
    action = "search_contacts"
elif "knowledge" in user_want.lower():
    service = get_knowledge_service()
    action = "search_knowledge"
```

### 3. EXIST:NOW: Current State Awareness

**What it is**: Awareness of the current state of the organism. The present moment consciousness.

**Characteristics**:
- Knows what exists right now
- Understands current context
- Aware of system state
- Grounded in the present

**In Code**:
```python
# Get current state
current_state = get_framework_state()
current_run_id = get_current_run_id()
correlation_ids = get_correlation_ids()

# Understand context
context = {
    "run_id": current_run_id,
    "state": current_state,
    "timestamp": datetime.now()
}
```

### 4. SEE: Active Perception

**What it is**: Active perception and observation via "Lenses" to gather data without judgment.

**Characteristics**:
- Gathers information
- Uses "Lenses" (different ways of seeing)
- No judgment, just observation
- Multiple perspectives

**In Code**:
```python
# See through different lenses
contacts = see_contacts(query="Adam")
knowledge = see_knowledge(query="Adam")
relationships = see_relationships(entity="Adam")

# Gather without judgment
all_data = {
    "contacts": contacts,
    "knowledge": knowledge,
    "relationships": relationships
}
```

### 5. HOLD: Storage and Persistence

**What it is**: The storage and persistence of data. The memory state.

**Characteristics**:
- Stores what was seen
- Creates memory
- Persists across time
- Enables recall

**In Code**:
```python
# Store what was seen
store_result(contacts, location="staging/contacts.jsonl")
store_result(knowledge, location="staging/knowledge.jsonl")
store_result(relationships, location="staging/relationships.jsonl")
```

### 6. MOVE: Transformation and Action

**What it is**: The actual transformation or action performed by the system. The execution.

**Characteristics**:
- Performs the work
- Transforms data
- Creates change
- Produces results

**In Code**:
```python
# Execute the transformation
result = move(
    data=all_data,
    action=action,
    context=context
)

# The result becomes new input for the next cycle
return result
```

---

## The Complete Cycle in Action

### Example: Finding a Contact

```python
# 1. WANT: User's intent
user_want = "Find all contacts named Adam"

# 2. CHOOSE: Select action
if "contact" in user_want.lower() and "find" in user_want.lower():
    service = get_contacts_service()
    action = "search_contacts"
    query = extract_query(user_want)  # "Adam"

# 3. EXIST:NOW: Current state
current_run_id = get_current_run_id()
context = {
    "run_id": current_run_id,
    "timestamp": datetime.now(),
    "user_want": user_want
}

# 4. SEE: Gather data
contacts = service.inhale(query=query, limit=20)

# 5. HOLD: Store result
store_result(
    contacts,
    location="staging/search_results.jsonl",
    run_id=current_run_id
)

# 6. MOVE: Transform and return
result = format_contacts_for_display(contacts)
return result

# The result may become WANT for the next cycle
# (e.g., "Show me more details about contact X")
```

---

## 🎯 PRACTICE: Tracing The Cycle

Try this exercise with any operation:

1. **Identify WANT**: What is the user trying to accomplish?
2. **Identify CHOOSE**: What decision was made? What path was selected?
3. **Identify EXIST:NOW**: What is the current state? What context exists?
4. **Identify SEE**: What data was gathered? What lenses were used?
5. **Identify HOLD**: Where was data stored? What memory was created?
6. **Identify MOVE**: What transformation occurred? What action was taken?

You'll find The Cycle in every operation once you know what to look for.

---

## The Cycle and The Structure

The Cycle orchestrates multiple Structures:

```
WANT
  │
  ▼
CHOOSE → [HOLD₁ → AGENT → HOLD₂]  (Structure 1)
  │
  ▼
EXIST:NOW
  │
  ▼
SEE → [HOLD₁ → AGENT → HOLD₂]  (Structure 2)
  │
  ▼
HOLD → [HOLD₁ → AGENT → HOLD₂]  (Structure 3)
  │
  ▼
MOVE → [HOLD₁ → AGENT → HOLD₂]  (Structure 4)
  │
  ▼
(Result becomes new WANT)
```

**The Cycle is the conductor. The Structure is the orchestra.**

---

## ⚠️ WARNING: Common Mistakes

### 1. Skipping Stages

**Don't do this:**
```python
# BAD: Skipping EXIST:NOW and SEE
user_want = "Find contacts"
contacts = get_contacts_service().inhale(query="")  # No context!
return contacts
```

**Do this instead:**
```python
# GOOD: Following all stages
user_want = "Find contacts"
current_run_id = get_current_run_id()  # EXIST:NOW
contacts = get_contacts_service().inhale(query="", limit=20)  # SEE
store_result(contacts, run_id=current_run_id)  # HOLD
return format_contacts(contacts)  # MOVE
```

### 2. Not Looping Back

**Don't do this:**
```python
# BAD: One-time execution
result = process_once(user_want)
return result  # End of cycle
```

**Do this instead:**
```python
# GOOD: Continuous pulse
while True:
    want = get_next_want()
    result = process_cycle(want)
    if result.creates_new_want:
        add_to_want_queue(result.new_want)  # Loop back
```

### 3. Ignoring Context

**Don't do this:**
```python
# BAD: No context awareness
def process(want):
    return execute(want)  # No awareness of current state
```

**Do this instead:**
```python
# GOOD: Context-aware
def process(want):
    context = get_current_context()  # EXIST:NOW
    return execute(want, context=context)
```

---

## 🚀 MOMENTUM: Why This Matters

Understanding The Cycle helps you:

1. **Design better workflows** - Every operation follows the same rhythm
2. **Debug more easily** - You know which stage failed
3. **Build reliable systems** - The cycle ensures nothing is skipped
4. **Understand the system** - Everything follows the same pulse

---

## 📚 Next Steps

Now that you understand The Cycle, read:
- **[Central Services Architecture](../architecture/01_CENTRAL_SERVICES.md)** - How services implement The Cycle
- **[Data Flow Patterns](../architecture/03_DATA_FLOW.md)** - How data flows through The Cycle

---

**Remember**: The Cycle is not about the past or future—it's about the act of processing in the present moment. It's the pulse of life that powers Truth Engine.
