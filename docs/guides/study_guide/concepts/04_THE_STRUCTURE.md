# The Structure: HOLD → AGENT → HOLD

**Layer**: Theory (WHY) + Specification (WHAT)
**Purpose**: Understand the universal pattern that governs all work in Truth Engine

---

## 🎓 LEARNING: What is "The Structure"?

The Structure is the **universal, scale-invariant pattern** for all work within the framework. It defines all action as a sequence of two states: rest and transition.

### The Core Pattern

```
HOLD (rest) → AGENT (transition) → HOLD (rest)
```

- **HOLD**: A state of rest or a **data container** (a noun)
- **AGENT**: A state of transition or a **process** (a verb) that transforms data from one state to another
- **The Atomic Pattern**: The smallest possible unit of action in The Framework

---

## 💡 CONCEPT: Scale Invariance

This pattern applies at **every level**:

| Scale | HOLD₁ | AGENT | HOLD₂ |
|-------|-------|-------|-------|
| **Function** | Input string | `normalize()` | Cleaned string |
| **Script** | `input.jsonl` | `my_script.py` | `staging.jsonl` |
| **Pipeline** | Staging files | `sync_to_cloud.py` | BigQuery table |
| **System** | Raw user WANT | The entire Framework | A changed user |

**The same pattern, at every scale.** This is what makes Truth Engine predictable and understandable.

---

## The Canonical Data Flow

In technical implementation, this follows a **Canonical Data Flow**:

```
HOLD₁ (Raw Source)
    │
    │  [AGENT: Processing]
    │
    ▼
HOLD₂ (Immutable Audit Trail)
    │
    │  [Deduplication]
    │
    ▼
HOLD₃ (Canonical Store)
```

### 1. HOLD₁: Raw Source Data

**Purpose**: Unprocessed input from the world

**Characteristics**:
- Raw, unstructured
- May contain duplicates
- May contain errors
- Source of truth for "what happened"

**Examples**:
- Raw JSONL files
- Unprocessed logs
- User input
- External API responses

### 2. AGENT: Processing Script

**Purpose**: Transformation logic that processes HOLD₁ into HOLD₂

**Characteristics**:
- Pure transformation (no side effects)
- Idempotent (safe to run multiple times)
- Observable (logs everything)
- Fail-safe (handles errors gracefully)

**Examples**:
- `normalize_data.py`
- `extract_knowledge_atoms.py`
- `sync_to_bigquery.py`

### 3. HOLD₂: Immutable Audit Trail

**Purpose**: Append-only, deduplicated output

**Characteristics**:
- Immutable (append-only)
- Deduplicated (no duplicates)
- Auditable (full traceability)
- Queryable (can be searched)

**Examples**:
- `staging/knowledge_atoms.jsonl`
- `staging/contacts.jsonl`
- `staging/events.jsonl`

### 4. HOLD₃: Canonical Store

**Purpose**: Final, strictly unique, queryable truth

**Characteristics**:
- Strictly unique (one record per unique entity)
- Queryable (optimized for queries)
- Authoritative (source of truth)
- Permanent (long-term storage)

**Examples**:
- BigQuery tables
- DuckDB databases
- Canonical knowledge graph

---

## 🎯 PRACTICE: Recognizing The Structure

### Example 1: A Simple Function

```python
def normalize_name(name: str) -> str:
    """HOLD₁: name → AGENT: normalize → HOLD₂: normalized_name"""
    # HOLD₁: Input (raw string)
    raw_name = name

    # AGENT: Processing
    normalized = raw_name.strip().lower().title()

    # HOLD₂: Output (cleaned string)
    return normalized
```

### Example 2: A Script

```python
# HOLD₁: Raw input file
input_file = "data/raw/contacts.jsonl"

# AGENT: Processing script
def process_contacts(input_file):
    contacts = read_jsonl(input_file)
    processed = []
    for contact in contacts:
        # Transform each contact
        processed.append(normalize_contact(contact))

    # HOLD₂: Output to staging
    write_jsonl("staging/contacts.jsonl", processed)

    # HOLD₃: Output to canonical store
    sync_to_bigquery(processed)

# Execute the agent
process_contacts(input_file)
```

### Example 3: A Service

```python
# HOLD₁: Raw content
content = "Jeremy builds Truth Engine."

# AGENT: Knowledge service
knowledge_service = get_knowledge_service()
result = knowledge_service.exhale(
    content=content,
    source_name="conversation"
)

# HOLD₂: Staging (immutable audit trail)
# Written to: staging/knowledge_atoms.jsonl

# HOLD₃: Canonical store
# Synced to: BigQuery knowledge_atoms table
```

---

## ⚠️ WARNING: Common Mistakes

### 1. Skipping HOLD₂

**Don't do this:**
```python
# BAD: Going directly from HOLD₁ to HOLD₃
raw_data = read_file("input.jsonl")
sync_to_bigquery(raw_data)  # No audit trail!
```

**Do this instead:**
```python
# GOOD: Following the canonical flow
raw_data = read_file("input.jsonl")
processed = transform(raw_data)
write_jsonl("staging/processed.jsonl", processed)  # HOLD₂
sync_to_bigquery(processed)  # HOLD₃
```

### 2. Modifying HOLD₂

**Don't do this:**
```python
# BAD: Modifying the audit trail
data = read_jsonl("staging/data.jsonl")
data[0]['field'] = 'modified'  # Modifying immutable data!
write_jsonl("staging/data.jsonl", data)
```

**Do this instead:**
```python
# GOOD: Creating new records, not modifying old ones
old_data = read_jsonl("staging/data.jsonl")
new_record = create_correction(old_data[0])
append_jsonl("staging/data.jsonl", new_record)  # Append-only
```

### 3. Side Effects in AGENT

**Don't do this:**
```python
# BAD: AGENT has side effects
def process_data(data):
    global_state['counter'] += 1  # Side effect!
    send_email()  # Side effect!
    return transform(data)
```

**Do this instead:**
```python
# GOOD: AGENT is pure transformation
def process_data(data):
    # Pure transformation, no side effects
    return transform(data)

# Side effects happen in separate steps
processed = process_data(data)
log_operation(processed)  # Separate step
notify_user(processed)  # Separate step
```

---

## The Structure in Services

All services in Truth Engine follow The Structure:

```python
# HOLD₁: Input
content = "Some text to process"

# AGENT: Service processing
service = get_knowledge_service()
result = service.exhale(content=content)

# HOLD₂: Staging output
# Automatically written to staging/knowledge_atoms.jsonl

# HOLD₃: Canonical store
# Automatically synced to BigQuery
```

**The service interface (`exhale`/`inhale`) abstracts The Structure, but it's still there underneath.**

---

## 🚀 MOMENTUM: Why This Matters

Understanding The Structure helps you:

1. **Write consistent code** - Every script follows the same pattern
2. **Debug more easily** - You know where to look for data at each stage
3. **Build reliable systems** - The pattern ensures data integrity
4. **Understand the codebase** - Everything follows the same structure

---

## 📚 Next Steps

Now that you understand The Structure, read:
- **[The Cycle](./05_THE_CYCLE.md)** - How The Cycle orchestrates multiple Structures
- **[Central Services Architecture](../architecture/01_CENTRAL_SERVICES.md)** - How services implement The Structure

---

**Remember**: The Structure is universal. Whether you're processing a single string or an entire database, the pattern is the same. This consistency makes the system predictable, testable, and understandable.
