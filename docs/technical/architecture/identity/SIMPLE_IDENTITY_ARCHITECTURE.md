# Simple Identity Architecture for People You Love

**Created**: 2025-12-24
**Author**: Claude (Opus 4.5) with Jeremy
**Status**: Implementation Ready

---

## The Philosophy

You don't need automatic identity resolution. You need a **curated list of people who matter to you** with a way to link their various identifiers (phone, email, usernames) to that person.

This is a **three-table system**:
1. **known_people** - The people who matter
2. **identifiers** - How to find them (phone, email, username)
3. **relationship_history** - How the relationship has evolved over time (the arc)

---

## Table 1: `identity.known_people`

The people you choose to track. Not everyone you've ever messaged - the people who matter.

```sql
CREATE TABLE `flash-clover-464719-g1.identity.known_people` (
  -- Identity
  person_id STRING NOT NULL,              -- person:hash (immutable)

  -- How you know them
  preferred_name STRING NOT NULL,         -- "Adam Fleming"
  nickname STRING,                        -- "Nebula" (optional)

  -- Your categorization (A-H, S, U, X system)
  category_code STRING NOT NULL,          -- A, B, C, D, E, F, G, H, S, U, X
  subcategory_code STRING,                -- A1, B2, C3, etc.
  relationship_type STRING,               -- Derived: family, friend, romantic, etc.

  -- Rich context (what you know about them)
  metaphor STRING,                        -- "The Nebula - expansive, formative"
  how_met STRING,                         -- "Denver LGBTQ+ scene, 2023"
  relationship_arc STRING,                -- Free-form narrative
  current_state STRING,                   -- "In impasse since Thanksgiving"

  -- What you want to understand (from perspective_gatherer)
  understanding_goals ARRAY<STRING>,      -- Questions you want answered
  patterns_to_explore ARRAY<STRING>,      -- Dynamics to watch for

  -- Metadata
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  created_by STRING DEFAULT 'jeremy'
)
CLUSTER BY category_code, person_id
OPTIONS (
  description = 'Curated list of people who matter. Manually maintained by Jeremy.',
  labels = [
    ('system', 'primitive_engine_v2'),
    ('data_class', 'personal'),
    ('type', 'identity_core'),
    ('sensitivity', 'high')
  ]
);
```

### Category Codes (Your System)

| Code | Type | Subcodes | Description |
|------|------|----------|-------------|
| **A** | Family | A1-A4 | Blood relatives, chosen family |
| **B** | Friend | B1-B4 | Friends at various depths |
| **C** | Acquaintance | C1-C3 | People you know but aren't close with |
| **D** | Romantic | D1-D4 | Current romantic interests |
| **E** | Ex-Romantic | E1-E3 | Former romantic relationships |
| **F** | Service | F1-F2 | Service providers (doctors, etc.) |
| **G** | Professional | G1-G3 | Work contacts |
| **H** | Hostile | H1-H3 | People to be cautious of |
| **S** | Sexual | S1-S3 | Sexual-only connections |
| **U** | Unknown | U1 | Not yet categorized |
| **X** | Exclude | X1-X3 | Explicitly excluded from system |

---

## Table 2: `identity.identifiers`

The join table. Links identifiers (phone, email, username) to people.

```sql
CREATE TABLE `flash-clover-464719-g1.identity.identifiers` (
  -- The identifier
  identifier_type STRING NOT NULL,        -- phone, email, grindr, instagram, etc.
  identifier_value STRING NOT NULL,       -- "+15551234567", "adam@email.com"
  identifier_normalized STRING,           -- Normalized form for matching

  -- Who it belongs to
  person_id STRING NOT NULL,              -- FK to known_people.person_id

  -- Context
  is_primary BOOL DEFAULT FALSE,          -- Primary identifier for this type
  verified BOOL DEFAULT FALSE,            -- Jeremy has verified this link
  notes STRING,                           -- "Work phone", "Old email"

  -- Metadata
  created_at TIMESTAMP NOT NULL,
  source STRING,                          -- Where this came from: apple_contacts, manual, etc.

  -- Primary key is (identifier_type, identifier_value)
  PRIMARY KEY (identifier_type, identifier_value) NOT ENFORCED
)
CLUSTER BY identifier_type, person_id
OPTIONS (
  description = 'Maps identifiers (phone, email, username) to people. The join table.',
  labels = [
    ('system', 'primitive_engine_v2'),
    ('data_class', 'personal'),
    ('type', 'identity_mapping'),
    ('sensitivity', 'high')
  ]
);
```

### Identifier Types

| Type | Example Value | Normalization |
|------|---------------|---------------|
| `phone` | `+15551234567` | E.164 format |
| `email` | `adam@example.com` | Lowercase, trimmed |
| `grindr` | `profile_id_123` | As-is |
| `instagram` | `@adam_fleming` | Lowercase, no @ |
| `twitter` | `@adam_f` | Lowercase, no @ |
| `chatgpt_participant` | `user` | Only "user" or "assistant" |
| `apple_contact_id` | `uuid-here` | As-is |

---

## Table 3: `identity.relationship_history`

The relationship arc. Tracks how relationships change over time.

```sql
CREATE TABLE `flash-clover-464719-g1.identity.relationship_history` (
  -- Identity
  history_id STRING NOT NULL,             -- hist:{person_hash}:{date_hash}
  person_id STRING NOT NULL,              -- FK to known_people.person_id

  -- The transition
  from_category STRING,                   -- Previous category (null for initial)
  from_subcategory STRING,                -- Previous subcategory
  to_category STRING NOT NULL,            -- New category
  to_subcategory STRING,                  -- New subcategory

  -- Context
  transition_date DATE NOT NULL,          -- When the transition occurred
  transition_reason STRING,               -- Why the change happened
  precipitating_event STRING,             -- Specific event that triggered change
  emotional_context STRING,               -- How Jeremy felt about the change

  -- Arc narrative
  arc_note STRING,                        -- Narrative note about this point

  -- Metadata
  created_at TIMESTAMP NOT NULL,
  created_by STRING DEFAULT 'jeremy'
)
CLUSTER BY person_id, transition_date
OPTIONS (
  description = 'Tracks relationship category changes over time. The relationship arc.',
  labels = [
    ('system', 'primitive_engine_v2'),
    ('data_class', 'personal'),
    ('type', 'identity_history'),
    ('sensitivity', 'high')
  ]
);
```

### What the Arc Tracks

The relationship arc captures the flow of categories and subcategories across time:

| Field | Purpose | Example |
|-------|---------|---------|
| `from_category` | Previous category | `"D"` (Romantic) |
| `to_category` | New category | `"E"` (Ex-Romantic) |
| `transition_date` | When it changed | `"2025-11-15"` |
| `transition_reason` | Why | `"Broke up after Thanksgiving fight"` |
| `precipitating_event` | Specific trigger | `"Discovered infidelity"` |
| `emotional_context` | How you felt | `"Heartbroken but relieved"` |
| `arc_note` | Narrative | `"Saw the pattern from previous relationships"` |

### Example Arc for Adam

```
2023-03-15: Started as friend (B2)
2023-07-22: B2 -> D1 (friend -> romantic) - Started dating after pride
   Note: Felt excited, cautious
2024-02-14: D1 -> D2 (deepening) - Valentine's Day commitment
   Note: Genuine connection forming
2024-11-28: D2 -> E1 (romantic -> ex) - Thanksgiving impasse
   Note: Pain, but clarity about patterns
```

### Querying the Arc

```sql
-- Get full relationship arc for a person
SELECT
  transition_date,
  from_category,
  to_category,
  transition_reason,
  arc_note
FROM identity.relationship_history
WHERE person_id = 'person:adam_fleming:a3f2b1c4'
ORDER BY transition_date ASC;

-- Find all relationships that went from romantic to ex
SELECT
  p.preferred_name,
  h.transition_date,
  h.transition_reason,
  h.precipitating_event
FROM identity.relationship_history h
JOIN identity.known_people p ON h.person_id = p.person_id
WHERE h.from_category = 'D'
  AND h.to_category = 'E'
ORDER BY h.transition_date DESC;
```

---

## How It Works

### Linking Messages to People

```sql
-- Text Messages: Who is this phone number?
SELECT
  m.*,
  p.preferred_name,
  p.category_code,
  p.relationship_type
FROM text_messages m
LEFT JOIN identity.identifiers i
  ON i.identifier_type = 'phone'
  AND i.identifier_normalized = normalize_phone(m.phone_number)
LEFT JOIN identity.known_people p
  ON i.person_id = p.person_id;
```

### Query: All Messages with Close Friends

```sql
SELECT
  m.text,
  m.timestamp,
  p.preferred_name,
  p.metaphor
FROM text_messages m
JOIN identity.identifiers i ON i.identifier_normalized = normalize_phone(m.phone_number)
JOIN identity.known_people p ON i.person_id = p.person_id
WHERE p.category_code = 'B'  -- Friends
  AND p.subcategory_code IN ('B1', 'B2')  -- Close friends
ORDER BY m.timestamp DESC;
```

### Query: Conversation Volume by Relationship Type

```sql
SELECT
  p.relationship_type,
  p.category_code,
  COUNT(DISTINCT p.person_id) as people,
  COUNT(*) as total_messages,
  AVG(LENGTH(m.text)) as avg_message_length
FROM text_messages m
JOIN identity.identifiers i ON i.identifier_normalized = normalize_phone(m.phone_number)
JOIN identity.known_people p ON i.person_id = p.person_id
WHERE p.category_code != 'X'  -- Exclude excluded
GROUP BY p.relationship_type, p.category_code
ORDER BY total_messages DESC;
```

---

## Population Strategy

### Phase 1: Seed from Apple Contacts (Automatic)

```python
# Already have contact data - extract and populate
def seed_from_apple_contacts():
    """
    For each contact in Apple Contacts:
    1. Create person in known_people (if categorized)
    2. Create identifiers for phone, email
    """
    contacts = get_apple_contacts()

    for contact in contacts:
        if contact.category_code:  # Only categorized contacts
            person_id = generate_person_id(contact.name)

            # Insert person
            insert_known_person(
                person_id=person_id,
                preferred_name=contact.display_name,
                category_code=contact.category_code,
                subcategory_code=contact.subcategory_code,
            )

            # Insert identifiers
            for phone in contact.phones:
                insert_identifier(
                    identifier_type='phone',
                    identifier_value=phone,
                    identifier_normalized=normalize_phone(phone),
                    person_id=person_id,
                    source='apple_contacts'
                )
```

### Phase 2: Surface Unknowns (Pipelines)

During pipeline processing, surface unknowns for manual linking:

```python
def process_text_message(message):
    phone = normalize_phone(message.sender_phone)

    # Try to find person
    person = lookup_person_by_identifier('phone', phone)

    if person:
        message.identity_entity_id = person.person_id
    else:
        # Log unknown for later review
        log_unknown_identifier(
            identifier_type='phone',
            identifier_value=phone,
            sample_message=message.text[:100],
            timestamp=message.timestamp
        )
```

### Phase 3: Review Tool (Manual Curation)

Simple CLI or Streamlit app:

```
===========================================
UNKNOWN IDENTIFIER REVIEW
===========================================

Phone: +1-555-867-5309
First seen: 2024-03-15
Message count: 47
Sample: "Hey, it's Mike from the gym..."

Actions:
  [1] Link to existing person
  [2] Create new person
  [3] Mark as X (exclude)
  [4] Skip for now

Choice: _
```

---

## Central Services Integration

### ID Generation

```python
from architect_central_services import generate_person_id

# Person IDs are immutable and deterministic
person_id = generate_person_id("Adam Fleming")  # → person:adam-fleming:a3f2b1c4
```

### Logging

```python
from architect_central_services import get_logger, log_event

logger = get_logger(__name__)

def link_identifier_to_person(identifier_type, identifier_value, person_id):
    logger.info(
        "Linking identifier to person",
        extra={
            "identifier_type": identifier_type,
            "person_id": person_id,
            "operation": "identity_link"
        }
    )
    # ... actual linking
```

### Governance

```python
from architect_central_services.governance import get_unified_governance

governance = get_unified_governance()

# Audit trail for identity changes
governance.record_audit(
    AuditRecord(
        category=AuditCategory.IDENTITY_OPERATION,
        level=AuditLevel.INFO,
        operation="person_created",
        component="identity_service",
        metadata={
            "person_id": person_id,
            "category_code": "B",
            "created_by": "jeremy"
        }
    )
)
```

---

## What This Enables

### 1. Cross-Platform Views

```sql
-- All my interactions with Adam across all platforms
SELECT
  'text' as platform, m.timestamp, m.text
FROM text_messages m
JOIN identity.identifiers i ON i.identifier_normalized = normalize_phone(m.phone_number)
WHERE i.person_id = 'person:adam-fleming:a3f2b1c4'

UNION ALL

SELECT
  'grindr' as platform, g.timestamp, g.message
FROM grindr_messages g
JOIN identity.identifiers i ON i.identifier_value = g.profile_id AND i.identifier_type = 'grindr'
WHERE i.person_id = 'person:adam-fleming:a3f2b1c4'

ORDER BY timestamp DESC;
```

### 2. Relationship Analytics

```sql
-- Communication patterns by relationship depth
SELECT
  p.category_code,
  p.subcategory_code,
  COUNT(DISTINCT p.person_id) as people,
  SUM(message_count) as total_messages,
  AVG(avg_response_time_hours) as avg_response_hours
FROM (
  SELECT
    i.person_id,
    COUNT(*) as message_count,
    AVG(response_time) as avg_response_time_hours
  FROM text_messages m
  JOIN identity.identifiers i ON ...
  GROUP BY i.person_id
) msg_stats
JOIN identity.known_people p ON msg_stats.person_id = p.person_id
GROUP BY p.category_code, p.subcategory_code;
```

### 3. Perspective Gatherer Integration

```python
# Your friend profiles (Adam, Butch, Eric, etc.) link directly
def get_friend_profile(person_id):
    person = get_known_person(person_id)

    return {
        "name": person.preferred_name,
        "metaphor": person.metaphor,
        "relationship_arc": person.relationship_arc,
        "current_state": person.current_state,
        "understanding_goals": person.understanding_goals,
        "patterns_to_explore": person.patterns_to_explore
    }
```

---

## Migration Path

### From Current State

1. **Keep existing `id_registry`** - it works for entity IDs
2. **Create `known_people` and `identifiers`** - new tables
3. **Migrate categorized contacts** from Apple Contacts to `known_people`
4. **Extract identifiers** (phone, email) to `identifiers` table
5. **Update pipelines** to populate `identity_entity_id` via lookup

### What Gets Deprecated

- Complex 4-layer identity architecture (never built)
- Automatic resolution with confidence scoring (over-engineered)
- `unified_identities` table (if it exists) - replaced by simpler structure

---

## Files Created

```
architect_central_services/
├── src/architect_central_services/
│   ├── core/identity_service/
│   │   └── id_generator.py          # Central ID generation (updated)
│   │       - generate_known_person_id()
│   │       - generate_relationship_history_id()
│   │       - generate_identifier_id()
│   │
│   └── identity/
│       ├── __init__.py              # Exports all functions
│       ├── known_people.py          # CRUD for known_people
│       ├── identifiers.py           # CRUD for identifiers
│       ├── relationship_arc.py      # Arc tracking functions
│       └── normalization.py         # Phone/email normalization
│
├── identity/
│   └── sql/
│       ├── known_people.sql         # DDL
│       ├── identifiers.sql          # DDL
│       └── relationship_history.sql # DDL
│
└── governance/governance_service/
    └── standard_categories.py       # Updated with identity categories
        - ALLOWED_PERSON_CATEGORIES
        - ALLOWED_PERSON_SUBCATEGORIES
        - ALLOWED_IDENTIFIER_TYPES
        - CATEGORY_TO_RELATIONSHIP mapping
        - get_relationship_type()

tools/
└── identity_review/
    └── app.py                        # Streamlit review app (TODO)
```

---

## Summary

| Old Approach | New Approach |
|--------------|--------------|
| 4 layers (Raw→Operationalized→Unifying→Human) | 3 tables (known_people + identifiers + relationship_history) |
| Automatic resolution with confidence scoring | Manual curation with identifier lookup |
| Apple Contacts as canonical source | Your categorizations as canonical source |
| Complex cross-source matching | Simple identifier→person join |
| Static categories | Dynamic arcs that track relationship evolution |
| Weeks to build | Hours to build |

**This will work because:**
1. Phone numbers are already unique identifiers - no fuzzy matching needed
2. You're the curator - the "resolution" is your knowledge of who people are
3. Unknowns surface for review instead of being guessed at
4. Simple joins replace complex ML matching
5. Your friend profiles (Adam, Butch, etc.) integrate directly
6. Relationship arcs capture the narrative of how connections evolve

---

## Next Steps

1. Create the BigQuery tables
2. Create the identity service module in central services
3. Seed from existing Apple Contacts data
4. Update text messages pipeline to use identity lookup
5. Build simple review tool for unknowns
