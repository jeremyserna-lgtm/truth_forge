# Identity Layer Design - Truth Engine

**Version**: 1.0.0
**Date**: 2025-12-08
**Status**: Design Document - Ready for Iteration
**Owner**: Jeremy Serna

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Identity Architecture Overview](#identity-architecture-overview)
4. [Identity Types and Categories](#identity-types-and-categories)
5. [ID Generation and Resolution](#id-generation-and-resolution)
6. [Cross-Source Identity Resolution](#cross-source-identity-resolution)
7. [Unique Circumstances and Edge Cases](#unique-circumstances-and-edge-cases)
8. [Category and Subcategory Framework](#category-and-subcategory-framework)
9. [AI Assistant Identity Handling](#ai-assistant-identity-handling)
10. [Implementation Patterns](#implementation-patterns)
11. [Data Model](#data-model)
12. [Resolution Confidence Scoring](#resolution-confidence-scoring)
13. [Future Considerations](#future-considerations)

---

## Executive Summary

The Truth Engine identity layer provides a **unified, canonical identity system** that resolves people and AI assistants across all data sources (SMS, Grindr, ChatGPT, Zoom, documents, emails, browser history, etc.). It handles the complex reality that:

- **One person** appears across multiple platforms with different identifiers (phone, email, username, profile_id)
- **One person** is referenced in multiple ways (direct messages, mentions in conversations, documents, emails)
- **AI assistants** have distinct identities that need to be tracked separately from people
- **Relationships** are categorized using a hierarchical framework (A-G categories with subcategories)
- **Confidence levels** must be tracked for all identity resolutions

This document defines the complete identity architecture, resolution patterns, and unique circumstances that must be handled.

---

## Problem Statement

### The Core Challenge

A single canonical person identity must be resolved across:

1. **Direct Communication Channels**
   - SMS text messages (phone numbers)
   - Grindr messages (profile IDs, display names)
   - ChatGPT conversations (user IDs, conversation contexts)
   - Zoom chats (participant IDs, email addresses)
   - Email (email addresses, display names)

2. **Indirect References**
   - Mentions in AI conversations ("I talked to John yesterday")
   - Named entities in documents ("Meeting with Sarah next week")
   - References in emails ("CC: Mike")
   - Browser history (contacted via web forms)

3. **Multiple Identifiers Per Person**
   - Phone numbers (multiple formats: +1, (555), 555-1234)
   - Email addresses (personal, work, aliases)
   - Platform-specific IDs (Grindr profile_id, ChatGPT user_id)
   - Display names (changeable, platform-specific)
   - Contact IDs (from iPhone contacts_master)

4. **AI Assistants as Distinct Identities**
   - ChatGPT personas (Clara, The Analyst, etc.)
   - Claude personas (different sessions, different contexts)
   - Gemini personas
   - Each AI assistant needs its own identity tracking

### Key Questions

1. **How do we know** that "John Smith" in SMS is the same person as "john_smith" in Grindr?
2. **How confident** are we in the match?
3. **How do we handle** display name changes (Grindr display names change frequently)?
4. **How do we link** messages FROM people vs. messages ABOUT people?
5. **How do we categorize** relationships (family, friends, dating, professional)?
6. **How do we track** AI assistants separately from people?

---

## Identity Architecture Overview

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Source-Specific Identity                          │
│  - SMS: phone numbers, contact_id                          │
│  - Grindr: profile_id, display_name, real_name            │
│  - ChatGPT: user_id, conversation_id, persona_name         │
│  - Zoom: participant_id, email, display_name               │
│  - Documents: named entities (PERSON, ORG)                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Unified Identity Resolution                        │
│  - identity.unified_identities (canonical person/AI identity)│
│  - identity.identity_resolutions (source → unified mapping)  │
│  - identity.message_identity_links (messages → identities) │
│  - identity.entity_identity_links (entities → identities) │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Cross-Source Linking                              │
│  - Multi-platform person resolution                        │
│  - Confidence aggregation                                    │
│  - Relationship categorization                             │
│  - AI assistant tracking                                   │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **IdentityService** (`architect_central_services/core/identity_service/`)
   - Generates canonical entity IDs
   - Manages ID registry (`identity.id_registry`)
   - Provides deterministic ID generation

2. **IdentityResolutionService** (`primitive_engine/identity/identity_resolution_service.py`)
   - Resolves source identifiers to unified identities
   - Links messages to identities
   - Links named entities to identities
   - Manages confidence scoring

3. **Unified Identities Table** (`identity.unified_identities`)
   - Master registry of all people and AI assistants
   - Stores all known identifiers across platforms
   - Tracks relationship categories and subcategories

4. **Resolution Tables**
   - `identity.identity_resolutions`: Source identifiers → unified identities
   - `identity.message_identity_links`: Messages → identities (FROM, TO, ABOUT)
   - `identity.entity_identity_links`: Named entities → identities

---

## Identity Types and Categories

### Identity Types

| Type | Description | Examples |
|------|-------------|----------|
| **person** | Real human being | "John Smith", "Sarah Johnson" |
| **persona** | AI assistant/persona | "Clara", "The Analyst", "Claude Sonnet 4.5" |
| **organization** | Business/company | "Google", "Acme Corp" |
| **unknown** | Unresolved identity | Temporary until resolved |

### Identity Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **real_person** | Confirmed human being | All people from SMS, Grindr, etc. |
| **ai_persona** | AI assistant | ChatGPT personas, Claude personas |
| **organization** | Business/company | Companies, service providers |
| **bot** | Automated system | System bots, automated responses |
| **unknown** | Unresolved | Pending resolution |

### Relationship Categories (from contacts_master)

| Category | Code | Description |
|----------|------|-------------|
| **Family** | A | Immediate and extended family |
| **Friends** | B | Close friends, casual friends |
| **Acquaintances** | C | People you know but not well |
| **Dating/Romantic** | D | Current partner, dating, hookups |
| **Ex-Romantic** | E | Former romantic partners |
| **Service Providers** | F | Healthcare, financial, delivery |
| **Professional/Coworkers** | G | Work colleagues, business contacts |
| **Hostile** | H | People with negative relationships |
| **Exclude** | X | System, spam, group-only |

---

## ID Generation and Resolution

### Person ID Generation

**Format**: `person:{name_slug}:{identifier_hash}`

**Priority Order** (ensures uniqueness):
1. **phone** (most reliable - unique per person)
2. **email** (reliable - unique per person)
3. **username** (platform-specific)
4. **profile_id** (platform-specific stable ID)
5. **contact_id** (from contacts_master)
6. **Fallback**: hash of name + platform + conversation_id/context

**Example**:
```python
# Phone number (highest priority)
generate_person_id(
    person_name="John Smith",
    identifier_type="phone",
    identifier_value="+15551234567",
    platform="sms"
)
# Returns: person:john-smith:a1b2c3d4e5f6

# Email (second priority)
generate_person_id(
    person_name="John Smith",
    identifier_type="email",
    identifier_value="john@example.com",
    platform="email"
)
# Returns: person:john-smith:x7y8z9a0b1c2

# Contact ID (if available)
generate_person_id(
    person_name="John Smith",
    contact_id=12345,
    platform="sms"
)
# Returns: person:john-smith:m3n4o5p6q7r8
```

**Key Properties**:
- **Deterministic**: Same input → same ID
- **Immutable**: ID never changes once created
- **Collision-resistant**: SHA-256 truncated to 12 chars
- **Content-addressable**: Hash based on best available identifier

### AI Assistant ID Generation

**Format**: `persona:{name_hash}` or `agent:{name_slug}`

**Example**:
```python
# ChatGPT persona
generate_persona_id("Clara")
# Returns: persona:3f8a2b9c1d4e

# Claude agent
generate_agent_id("Claude", model="sonnet-4.5")
# Returns: agent:claude-sonnet-4-5
```

**Key Properties**:
- **Deterministic**: Same name/model → same ID
- **Platform-aware**: Tracks which platform (ChatGPT, Claude, Gemini)
- **Session-aware**: Can track different sessions of same persona

---

## Cross-Source Identity Resolution

### Resolution Methods

#### Method 1: Exact Identifier Match (Highest Confidence)

**When**: Same identifier appears in multiple sources

**Process**:
1. Normalize identifier (phone: remove formatting, email: lowercase)
2. Search `identity.unified_identities.known_identifiers` for exact match
3. If found: Link to existing identity (confidence: 1.0)
4. If not found: Create new identity

**Example**:
```python
# SMS: phone = "+15551234567"
# Grindr: phone = "+1 (555) 123-4567" (from profile notes)
# Both normalize to: "15551234567"
# → Same identity: person:john-smith:a1b2c3d4e5f6
```

**Confidence**: **1.0** (100% - same identifier)

#### Method 2: Contact Master Lookup (High Confidence)

**When**: Identifier matches `source_data.contacts_master` or `source_data.contact_identifiers`

**Process**:
1. Look up identifier in `contact_identifiers`
2. Get `contact_id` and `canonical_name` from `contacts_master`
3. Search `identity.unified_identities` for matching `contact_id` or `canonical_name`
4. If found: Link to existing identity (confidence: 0.90-0.95)
5. If not found: Create new identity with `contact_id` link

**Example**:
```python
# SMS: phone = "+15551234567"
# Lookup in contact_identifiers → contact_id = 12345
# Lookup in contacts_master → canonical_name = "John Smith"
# Search unified_identities for contact_id=12345
# → Found: person:john-smith:a1b2c3d4e5f6
```

**Confidence**: **0.90-0.95** (high - from authoritative contacts source)

#### Method 3: Name-Based Matching (Medium Confidence)

**When**: Only name available (no identifier match)

**Process**:
1. Normalize name (lowercase, remove punctuation)
2. Search `identity.unified_identities` for matching `canonical_name`
3. Use fuzzy matching (Levenshtein distance, Jaro-Winkler)
4. If match found: Link with confidence based on similarity (0.60-0.85)
5. If not found: Create new identity

**Example**:
```python
# Grindr: display_name = "Looking 4 top", real_name = "John Smith"
# Normalize: canonical_name = "john smith"
# Search unified_identities for canonical_name LIKE "john smith"
# → Found: person:john-smith:a1b2c3d4e5f6 (from SMS)
# Confidence: 0.85 (name match from profile notes)
```

**Confidence**: **0.60-0.85** (medium - names can be ambiguous)

#### Method 4: Cross-Platform Aggregation (Variable Confidence)

**When**: Multiple identifiers suggest same person

**Process**:
1. Collect all identifiers from all sources
2. Search `identity.unified_identities.known_identifiers` for any match
3. Aggregate confidence from multiple matches
4. If aggregate confidence >= 0.80: Link to existing identity
5. If not: Create new identity

**Example**:
```python
# Grindr: real_name = "John Smith", phone = "+15551234567"
# SMS: phone = "+15551234567" → person:john-smith:a1b2c3d4e5f6
# ChatGPT: mentioned "John Smith" in conversation
# → Aggregate: phone match (1.0) + name match (0.85) = 0.92
# → Link ChatGPT mention to person:john-smith:a1b2c3d4e5f6
```

**Confidence**: **0.70-0.95** (high - multi-platform confirmation)

#### Method 5: Manual Override (Highest Confidence)

**When**: User manually confirms identity

**Process**:
1. User reviews identity resolution
2. User confirms or corrects match
3. Store manual override in `identity.unified_identities.manual_override`
4. Update confidence to 1.0

**Confidence**: **1.0** (100% - user confirmed)

---

## Unique Circumstances and Edge Cases

### 1. Display Name Changes (Grindr, Zoom, etc.)

**Problem**: Display names change frequently, but person is the same.

**Solution**:
- Use **stable identifiers** (profile_id, phone, email) as primary keys
- Store display names in `known_identifiers` with timestamps
- Track display name history in `disambiguation_context`
- Resolution uses stable identifiers first, display names as fallback

**Example**:
```python
# Grindr profile_id = "profile_abc123"
# Display name changed: "Looking 4 top" → "John" → "JSmith"
# All resolve to same identity: person:john-smith:a1b2c3d4e5f6
# Because profile_id is stable
```

### 2. Multiple Phone Numbers Per Person

**Problem**: One person has multiple phone numbers (personal, work, burner).

**Solution**:
- Store all phone numbers in `known_identifiers` array
- Link all phone numbers to same `entity_id`
- Use `contact_id` from `contacts_master` to link multiple numbers
- Resolution matches on any phone number

**Example**:
```python
# Person: John Smith
# Phone 1: "+15551234567" (personal)
# Phone 2: "+15559876543" (work)
# Both link to: person:john-smith:a1b2c3d4e5f6
# Via contact_id = 12345 (from contacts_master)
```

### 3. Same Name, Different People

**Problem**: Multiple people with same name (e.g., "John Smith").

**Solution**:
- Use **identifiers** (phone, email) to distinguish
- Same name + different identifier = different `entity_id`
- Resolution requires identifier match, not just name match

**Example**:
```python
# Person 1: "John Smith", phone = "+15551234567"
# → person:john-smith:a1b2c3d4e5f6

# Person 2: "John Smith", phone = "+15559876543"
# → person:john-smith:x7y8z9a0b1c2

# Different entity_ids because different identifiers
```

### 4. Messages FROM vs. ABOUT People

**Problem**: Need to distinguish:
- Messages **FROM** a person (they sent it)
- Messages **TO** a person (sent to them)
- Messages **ABOUT** a person (they're mentioned)

**Solution**:
- Use `identity.message_identity_links` with `link_type`:
  - `from`: Message sent by this identity
  - `to`: Message sent to this identity
  - `about`: Person mentioned in message (named entity)
- Use `link_role` for additional context:
  - `sender`, `recipient`, `mentioned`, `quoted`

**Example**:
```python
# SMS message: "Hey John, how are you?"
# Link 1: link_type="from", entity_id="person:jeremy-serna:...", link_role="sender"
# Link 2: link_type="to", entity_id="person:john-smith:...", link_role="recipient"

# ChatGPT message: "I talked to Sarah yesterday"
# Link 1: link_type="from", entity_id="person:jeremy-serna:...", link_role="sender"
# Link 2: link_type="about", entity_id="person:sarah-johnson:...", link_role="mentioned"
```

### 5. AI Conversations About People

**Problem**: AI conversations mention people who aren't direct participants.

**Solution**:
- Extract named entities (PERSON, ORG) from AI conversation messages
- Link named entities to unified identities via `identity.entity_identity_links`
- Use `linking_method` = "name_match" or "context_inference"
- Use `linking_confidence` based on name matching quality

**Example**:
```python
# ChatGPT message: "I had dinner with Mike last night"
# Extract named entity: "Mike" (PERSON)
# Resolve to: person:mike-wilson:b2c3d4e5f6g7
# Link via entity_identity_links:
#   entity_id = "span_L03_abc123" (named entity span)
#   identity_entity_id = "person:mike-wilson:b2c3d4e5f6g7"
#   linking_method = "name_match"
#   linking_confidence = 0.75
```

### 6. Platform-Specific Identifiers

**Problem**: Each platform has different identifier types:
- SMS: phone numbers
- Grindr: profile_id, display_name, real_name
- ChatGPT: user_id, conversation_id, persona_name
- Zoom: participant_id, email, display_name
- Email: email addresses, display names

**Solution**:
- Store all identifiers in `known_identifiers` array
- Each identifier has: `identifier_type`, `identifier_value`, `platform`, `confidence`
- Resolution searches across all identifiers
- Platform-specific identifiers stored with platform context

**Example**:
```python
# Unified identity: person:john-smith:a1b2c3d4e5f6
# known_identifiers = [
#   {"identifier_type": "phone", "identifier_value": "+15551234567", "platform": "sms"},
#   {"identifier_type": "profile_id", "identifier_value": "profile_abc123", "platform": "grindr"},
#   {"identifier_type": "email", "identifier_value": "john@example.com", "platform": "email"},
#   {"identifier_type": "user_id", "identifier_value": "user_xyz789", "platform": "chatgpt_web"}
# ]
```

### 7. Group Conversations

**Problem**: Group conversations have multiple participants.

**Solution**:
- Link conversation to multiple identities via `persona_id` (for AI) or participant links
- Store participant list in conversation metadata
- Link each message to sender identity via `message_identity_links`
- Track group membership in `identity_metrics.conversation_count`

**Example**:
```python
# Group SMS conversation with 3 participants
# Conversation links:
#   - person:jeremy-serna:... (me)
#   - person:john-smith:... (participant 1)
#   - person:sarah-johnson:... (participant 2)

# Each message links to sender:
#   message_1: link_type="from", entity_id="person:john-smith:..."
#   message_2: link_type="from", entity_id="person:sarah-johnson:..."
```

### 8. Temporary/Unresolved Identities

**Problem**: Some identities can't be resolved immediately (display name only, no identifier).

**Solution**:
- Create temporary identity with `identity_type="unknown"`
- Store available identifiers (display name, platform context)
- Flag for manual review if confidence < 0.60
- Update identity when more information becomes available

**Example**:
```python
# Grindr: display_name = "Looking 4 top", no profile_id, no real_name
# Create temporary identity:
#   entity_id = "person:looking-4-top:t1u2v3w4x5y6"
#   identity_type = "unknown"
#   confidence = 0.50
#   flag_for_review = true

# Later: User adds real_name = "John Smith" in profile notes
# Update identity:
#   entity_id = "person:john-smith:a1b2c3d4e5f6" (resolved)
#   identity_type = "person"
#   confidence = 0.90
```

---

## Category and Subcategory Framework

### Category Codes (A-G, X)

| Code | Category | Description |
|------|----------|-------------|
| **A** | Family | Immediate and extended family |
| **B** | Friends | Close friends, casual friends |
| **C** | Acquaintances | People you know but not well |
| **D** | Dating/Romantic | Current partner, dating, hookups |
| **E** | Ex-Romantic | Former romantic partners |
| **F** | Service Providers | Healthcare, financial, delivery |
| **G** | Professional/Coworkers | Work colleagues, business contacts |
| **H** | Hostile | People with negative relationships |
| **X** | Exclude | System, spam, group-only |

### Subcategory Codes (Full Format)

#### Family (A)
- `A1_IMMEDIATE_FAMILY_RAISED_TOGETHER`
- `A2_IMMEDIATE_FAMILY_RAISED_SEPARATELY`
- `A3_IMMEDIATE_FAMILY_ESTRANGED`
- `A4_EXTENDED_FAMILY`

#### Friends (B)
- `B1_BEST_FRIENDS`
- `B2_CORE_FRIENDS`
- `B3_CASUAL_FRIENDS`
- `B4_CHILDHOOD_FRIEND`
- `B5_WORK_FRIEND`

#### Acquaintances (C)
- `C1_ACQUAINTANCE_FREQUENT`
- `C2_ACQUAINTANCE_INFREQUENT`
- `C3_ACQUAINTANCE_INACTIVE`

#### Dating/Romantic (D)
- `D1_CURRENT_PARTNER`
- `D2_SERIOUS_DATING`
- `D3_CASUAL_DATING`
- `D4_FLIRTING`
- `D5_HOOKUP`

#### Ex-Romantic (E)
- `E1_EX_FRIENDLY`
- `E2_EX_COMPLICATED`
- `E3_EX_NO_CONTACT`

#### Service Providers (F)
- `F1_HEALTHCARE`
- `F2_FINANCIAL`
- `F3_DELIVERY_FOOD`
- `F4_PERSONAL_SERVICES`

#### Professional/Coworkers (G)
- `G1_CLOSE_COWORKER`
- `G2_COWORKER`
- `G3_BUSINESS_CONTACT`

#### Hostile (H)
- `H1_CLOSE_HOSTILE`
- `H2_DISTANT_HOSTILE`
- `H3_STRANGER_HOSTILE`

#### Exclude (X)
- `X1_SYSTEM`
- `X2_SPAM`
- `X3_GROUP_ONLY`

### Integration with contacts_master

**Source**: `source_data.contacts_master` and `source_data.contact_identifiers`

**Process**:
1. Look up identifier in `contact_identifiers` → get `contact_id`
2. Look up `contact_id` in `contacts_master` → get `category_code`, `subcategory`, `canonical_name`
3. Map `category_code` to `relationship_category`:
   - A → "family"
   - B → "friend"
   - C → "acquaintance"
   - D → "romantic"
   - E → "ex_romantic"
   - F → "service_provider"
   - G → "professional"
   - H → "hostile"
   - X → None (excluded)
4. Normalize `subcategory` to full format (A1 → A1_IMMEDIATE_FAMILY_RAISED_TOGETHER)
5. Store in `identity.unified_identities`:
   - `category_code`: "A", "B", "C", etc.
   - `subcategory_code`: "A1_IMMEDIATE_FAMILY_RAISED_TOGETHER"
   - `relationship_category`: "family", "friend", etc.
   - `contact_id`: 12345

**Example**:
```python
# SMS: phone = "+15551234567"
# Lookup in contact_identifiers → contact_id = 12345
# Lookup in contacts_master:
#   canonical_name = "John Smith"
#   category_code = "B"
#   subcategory = "B1"
#   organization = None

# Resolution:
#   entity_id = "person:john-smith:a1b2c3d4e5f6"
#   category_code = "B"
#   subcategory_code = "B1_BEST_FRIENDS"
#   relationship_category = "friend"
#   contact_id = 12345
```

---

## AI Assistant Identity Handling

### AI Assistant Types

| Type | Description | Examples |
|------|-------------|----------|
| **persona** | Named AI assistant | "Clara", "The Analyst", "Claude Sonnet 4.5" |
| **agent** | System agent | "Claude", "Gemini", "ChatGPT" |

### AI Assistant Identity Generation

**Format**: `persona:{name_hash}` or `agent:{name_slug}`

**Example**:
```python
# ChatGPT persona
generate_persona_id("Clara")
# Returns: persona:3f8a2b9c1d4e

# Claude agent
generate_agent_id("Claude", model="sonnet-4.5")
# Returns: agent:claude-sonnet-4-5
```

### AI Assistant Tracking

**Table**: `identity.agent_sessions`

**Fields**:
- `agent_id`: Generated agent ID
- `agent_name`: AI name (e.g., "Claude")
- `nickname`: User-given nickname (e.g., "Clara")
- `memory_file_path`: Path to reflection memory file
- `created_at`: Session creation timestamp
- `session_start`: Session start timestamp
- `jeremy_gave_nickname`: Whether user gave nickname
- `anchor_moment`: Whether this is an anchor moment

**Example**:
```python
# ChatGPT conversation with persona "Clara"
# Generate persona_id: persona:3f8a2b9c1d4e
# Store in agent_sessions:
#   agent_id = "persona:3f8a2b9c1d4e"
#   agent_name = "ChatGPT"
#   nickname = "Clara"
#   memory_file_path = "/path/to/clara_memory.json"
```

### AI Assistant vs. Person Distinction

**Key Differences**:
- **People**: Have phone numbers, email addresses, real-world identifiers
- **AI Assistants**: Have platform IDs, persona names, session contexts
- **Resolution**: AI assistants never resolve to people (separate identity types)

**Example**:
```python
# Person: John Smith
#   identity_type = "person"
#   known_identifiers = [{"phone": "+15551234567"}, {"email": "john@example.com"}]

# AI Assistant: Clara
#   identity_type = "persona"
#   known_identifiers = [{"chatgpt_id": "user_xyz789"}, {"persona_name": "Clara"}]
#   is_ai_persona = true
#   persona_platform = "chatgpt"
```

---

## Implementation Patterns

### Pattern 1: Resolve Identity from Source Data

```python
from architect_central_services.core.identity_service import generate_person_id
from primitive_engine.identity.identity_resolution_service import IdentityResolutionService

# Initialize resolution service
resolution_service = IdentityResolutionService(project_id="flash-clover-464719-g1")

# Resolve identity from SMS
identity = resolution_service.resolve_identity(
    identifier_type="phone",
    identifier_value="+15551234567",
    platform="sms",
    display_name="John Smith",
    identity_type="person"
)

# Returns:
# {
#   "entity_id": "person:john-smith:a1b2c3d4e5f6",
#   "preferred_name": "John Smith",
#   "identity_type": "person",
#   "confidence": 1.0
# }
```

### Pattern 2: Link Message to Identity

```python
# Link message FROM a person
link_id = resolution_service.link_message_to_identity(
    message_id="msg_abc123",
    entity_id="person:john-smith:a1b2c3d4e5f6",
    link_type="from",
    source_type="sms",
    source_identifier="+15551234567",
    link_role="sender",
    linking_method="direct",
    linking_confidence=1.0
)

# Link message ABOUT a person (named entity)
link_id = resolution_service.link_entity_to_identity(
    entity_id="span_L03_abc123",  # Named entity span
    entity_text="John",
    entity_type="PERSON",
    identity_entity_id="person:john-smith:a1b2c3d4e5f6",
    parent_entity_id="msg_xyz789",
    conversation_id="conv_chatgpt_123",
    linking_method="name_match",
    linking_confidence=0.75,
    context="I talked to John yesterday"
)
```

### Pattern 3: Cross-Source Resolution

```python
# Resolve Grindr profile to unified identity
identity = resolution_service.resolve_identity(
    identifier_type="profile_id",
    identifier_value="profile_abc123",
    platform="grindr",
    display_name="Looking 4 top",
    identity_type="person",
    all_identifiers=[
        ("profile_id", "profile_abc123"),
        ("real_name", "John Smith"),  # From profile notes
        ("phone", "+15551234567")  # If available
    ]
)

# System automatically:
# 1. Checks for existing identity with profile_id
# 2. Checks for existing identity with phone number
# 3. Checks for existing identity with name match
# 4. Creates new identity if no match found
```

---

## Data Model

### identity.unified_identities

**Purpose**: Master registry of all people and AI assistants

**Key Fields**:
- `entity_id`: Unique identifier (generated by IdentityService)
- `identity_type`: person, persona, organization, unknown
- `preferred_name`: Display name
- `canonical_name`: Normalized name (for matching)
- `known_identifiers`: Array of all identifiers across platforms
- `category_code`: A, B, C, D, E, F, G, X
- `subcategory_code`: Full format (e.g., A1_IMMEDIATE_FAMILY_RAISED_TOGETHER)
- `relationship_category`: family, friend, romantic, etc.
- `contact_id`: Link to contacts_master
- `is_business`: Whether this is a business/organization

**Schema**: See `docs/schema/identity/unified_identities.yaml`

### identity.identity_resolutions

**Purpose**: Maps source identifiers to unified identities

**Key Fields**:
- `resolution_id`: Unique resolution ID
- `entity_id`: Unified identity entity_id
- `source_type`: Platform (sms, grindr, chatgpt_web, etc.)
- `source_identifier`: Platform-specific identifier
- `source_identifier_type`: Type (phone, email, profile_id, etc.)
- `resolution_method`: stable_id, profile_note, fuzzy_match, etc.
- `resolution_confidence`: Confidence (0.0-1.0)
- `resolution_status`: resolved, pending, manual_review

### identity.message_identity_links

**Purpose**: Links messages to identities

**Key Fields**:
- `link_id`: Unique link ID
- `message_id`: Message ID (L5 entity)
- `entity_id`: Unified identity entity_id
- `link_type`: from, to, about
- `link_role`: sender, recipient, mentioned, quoted
- `source_type`: Platform
- `source_identifier`: Platform-specific identifier
- `linking_method`: direct, entity_resolution, context_inference
- `linking_confidence`: Confidence (0.0-1.0)

### identity.entity_identity_links

**Purpose**: Links named entities to identities

**Key Fields**:
- `link_id`: Unique link ID
- `entity_id`: Named entity ID (from spine.entity_production)
- `identity_entity_id`: Unified identity entity_id
- `entity_level`: SPINE level (L1-L12)
- `entity_text`: Text of the entity
- `entity_type`: spaCy entity type (PERSON, ORG, etc.)
- `parent_entity_id`: Parent entity (e.g., L5 message)
- `conversation_id`: Conversation ID (L8)
- `linking_method`: exact_name_match, fuzzy_match, context_inference
- `linking_confidence`: Confidence (0.0-1.0)

---

## Resolution Confidence Scoring

### Confidence Levels

| Level | Range | Meaning | Action |
|-------|-------|---------|--------|
| **Definitive** | 0.95-1.0 | Very high confidence | Auto-link, no review needed |
| **High** | 0.80-0.94 | High confidence | Auto-link, flag for review |
| **Medium** | 0.60-0.79 | Moderate confidence | Flag for manual review |
| **Low** | 0.40-0.59 | Low confidence | Require manual review |
| **Very Low** | 0.0-0.39 | Very low confidence | Do not link, create new identity |

### Confidence Calculation

**Base Confidence** (from resolution method):
- Stable ID: 1.0
- Contact Master: 0.90-0.95
- Exact Identifier Match: 1.0
- Name Match: 0.60-0.85
- Fuzzy Match: 0.60-0.80
- Cross-Platform: 0.70-0.95

**Adjustment Factors**:
- **Name Normalization Quality**: ±0.05
- **Temporal Consistency**: ±0.10 (same name over time)
- **Multi-Source Confirmation**: +0.10 (confirmed in multiple sources)
- **Display Name Changes**: -0.20 (name changed recently)
- **Profile Note Recency**: ±0.05 (recent note = higher confidence)

**Final Confidence**:
```
final_confidence = base_confidence + adjustments
final_confidence = min(1.0, max(0.0, final_confidence))
```

### Example Calculation

```python
# Profile note resolution
base_confidence = 0.90  # Profile note method

# Adjustments
name_normalization = 0.05  # Clean name
temporal_consistency = 0.10  # Same name for 6 months
multi_source = 0.10  # Also found in SMS contacts
display_name_change = -0.20  # Display name changed last week

# Final
final_confidence = 0.90 + 0.05 + 0.10 + 0.10 - 0.20
final_confidence = 0.95  # Definitive level
```

---

## Future Considerations

### 1. Identity Merging

**Problem**: Two identities later discovered to be the same person.

**Solution**:
- Create identity merge records
- Preserve both entity_ids (mark one as merged)
- Update all links to point to canonical identity
- Track merge history for audit

### 2. Identity Disambiguation UI

**Problem**: Manual review needed for low-confidence resolutions.

**Solution**:
- Build UI for reviewing identity resolutions
- Show confidence scores and resolution methods
- Allow manual confirmation/correction
- Learn from manual corrections to improve algorithms

### 3. Identity Relationship Graph

**Problem**: Need to query relationships between identities.

**Solution**:
- Build relationship graph from category/subcategory codes
- Track relationship strength (frequency, recency)
- Support graph queries (e.g., "all family members", "all friends")

### 4. Identity Privacy Controls

**Problem**: Some identities need privacy protection.

**Solution**:
- Add privacy flags to identities
- Control which identities appear in queries
- Support identity anonymization for sensitive data

### 5. Identity Temporal Tracking

**Problem**: Relationships change over time.

**Solution**:
- Track relationship changes (category_code updates)
- Store relationship history
- Support temporal queries (e.g., "friends in 2024")

---

## References

### Code References

- **IdentityService**: `architect_central_services/src/architect_central_services/core/identity_service/identity_service.py`
- **IdentityResolutionService**: `architect_central_services/src/primitive_engine/identity/identity_resolution_service.py`
- **ID Generator**: `architect_central_services/src/architect_central_services/core/identity_service/id_generator.py`
- **Identity Schema**: `docs/schema/identity/unified_identities.yaml`
- **Identity Registry Schema**: `architect_central_services/src/architect_central_services/core/data_models/identity_schema.sql`

### Documentation References

- **Grindr Identity Resolution**: `data_sources/grindr/docs/06_IDENTITY_RESOLUTION.md`
- **SMS Pipeline**: `architect_central_services/src/architect_central_services/core/data_models/source_data_schema.sql`
- **Category Framework**: Referenced in `identity_resolution_service.py` (lines 802-906)

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0
**Status**: Design Complete - Ready for Iteration
