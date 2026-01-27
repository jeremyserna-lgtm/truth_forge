# Identity Layer - Layered Architecture

**Version**: 1.0.0
**Date**: 2025-12-08
**Status**: Architecture Design
**Owner**: Jeremy Serna

---

## Overview

The `identity` dataset is the **canonical dataset** for all identity tables and data. It uses a **layered architecture** that starts with the Apple Contacts database structure and builds unifying tables on top for cross-source ID resolution.

## Layered Architecture

### Layer 1: Raw Capture (Foundation)

**Purpose**: Store Apple Contacts database in its pure, unmodified form.

**Tables**:
- `identity.raw_apple_contacts_extractions` - Extraction tracking
- `identity.raw_apple_contacts_records` - Contact records (from `ZABCDRECORD`)
- `identity.raw_apple_contacts_phone_numbers` - Phone numbers (from `ZABCDPHONENUMBER`)
- `identity.raw_apple_contacts_email_addresses` - Email addresses (from `ZABCDEMAILADDRESS`)
- `identity.raw_apple_contacts_social_profiles` - Social profiles (from `ZABCDSOCIALPROFILE`)
- `identity.raw_apple_contacts_notes` - Notes (from `ZABCDNOTE`)

**Characteristics**:
- Pure capture - no transformation
- Preserves data exactly as it appears in Apple Contacts
- Enables reprocessing if needed
- Foundation for all higher layers

**Script**: `identity/scripts/extract_apple_contacts_raw.py`

---

### Layer 2: Operationalized Tables (Parsed & Structured)

**Purpose**: Parse raw capture data into structured, operationalized tables.

**Tables**:
- `identity.contacts_master` - Master contact table (parsed from raw)
- `identity.contact_identifiers` - Multi-platform identifiers (phones, emails, social)
- `identity.contact_relationships` - Relationship data (categories, subcategories)
- `identity.contact_metadata` - Additional metadata and notes

**Characteristics**:
- Parsed from raw capture
- Structured for operational use
- Includes categories and subcategories
- Normalized identifiers
- Business logic applied

**Source**: Parsed from `identity.raw_apple_contacts_*` tables

---

### Layer 3: Unifying Tables (Cross-Source Resolution)

**Purpose**: Unify identities across all data sources (SMS, Grindr, ChatGPT, documents, etc.).

**Tables**:
- `identity.unified_identities` - Master identity registry
- `identity.identity_resolutions` - Resolution history and confidence scores
- `identity.message_identity_links` - Links between messages and identities
- `identity.entity_identity_links` - Links between entities and identities
- `identity.cross_source_identifiers` - Identifier mappings across sources

**Characteristics**:
- Cross-source ID resolution
- Confidence scoring
- Relationship categories and subcategories
- Links to all data sources
- Canonical identity representation
- **Automatic resolution** (with manual override support)

**Source**: Resolved from:
- `identity.contacts_master` (Apple Contacts)
- `sms_messages_v2` (SMS data)
- `grindr.*` (Grindr data)
- `spine.*` (ChatGPT conversations)
- Other data sources

---

### Layer 4: Human Intervention & Override Layer

**Purpose**: Manual ID matching and resolution overrides for cases where automatic resolution fails or needs correction.

**Tables**:
- `identity.manual_resolutions` - Manual identity resolutions and overrides
- `identity.unresolved_identifiers` - Identifiers that couldn't be automatically resolved
- `identity.resolution_overrides` - Overrides to existing automatic resolutions
- `identity.merge_operations` - Manual identity merges

**Characteristics**:
- **Manual override priority**: Manual resolutions take precedence over automatic
- **Audit trail**: Track who made the override, when, and why
- **Override types**: Create new links, override existing, merge identities
- **Unresolved tracking**: Track identifiers that need manual intervention
- **Validation**: Ensure manual overrides are valid

**Workflow**:
1. Automatic resolution attempts to match identifiers
2. Unmatched identifiers → `identity.unresolved_identifiers`
3. Human reviews unresolved identifiers
4. Human creates manual resolution → `identity.manual_resolutions`
5. Resolution system checks manual resolutions first (highest priority)
6. Manual overrides can override existing automatic resolutions

**Priority Order** (highest to lowest):
1. **Manual Resolution** (Layer 4) - Highest confidence, human-verified
2. **Automatic Resolution** (Layer 3) - Algorithm-based
3. **Unresolved** - No match found

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: Raw Capture                     │
│  Apple Contacts SQLite → identity.raw_apple_contacts_*      │
│  (Pure capture, no transformation)                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Layer 2: Operationalized Tables               │
│  Raw Capture → identity.contacts_master                     │
│  Raw Capture → identity.contact_identifiers                  │
│  Raw Capture → identity.contact_relationships                │
│  (Parsed, structured, categorized)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Layer 3: Unifying Tables                       │
│  contacts_master + SMS + Grindr + ChatGPT + ...             │
│  → identity.unified_identities                              │
│  → identity.identity_resolutions                            │
│  → identity.message_identity_links                         │
│  (Cross-source resolution, canonical identities)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Layer 4: Human Intervention & Override            │
│  Manual resolutions → identity.manual_resolutions          │
│  Unresolved → identity.unresolved_identifiers               │
│  Overrides → identity.resolution_overrides                  │
│  Merges → identity.merge_operations                         │
│  (Human-verified, highest priority)                          │
└─────────────────────────────────────────────────────────────┘
```

## Layer 1: Raw Capture

### Purpose

Store Apple Contacts database in its **pure, unmodified form** before any parsing or operationalization.

### Design Principles

1. **No Transformation**: Data stored exactly as it appears in Apple Contacts
2. **Complete Audit Trail**: Track every extraction run
3. **Raw JSON Preservation**: Store complete records as JSON for reference
4. **Temporal Tracking**: Track extraction timestamps
5. **Source Traceability**: Link all records to source database

### Tables

See `docs/architecture/IDENTITY_LAYER_RAW_CAPTURE.md` for complete table schemas.

### Extraction

- **Script**: `identity/scripts/extract_apple_contacts_raw.py`
- **Source**: `~/Library/Application Support/AddressBook/`
- **Frequency**: Incremental (only new/modified entities)
- **Deduplication**: Uses `modification_date` to skip unchanged entities

---

## Layer 2: Operationalized Tables

### Purpose

Parse raw capture data into structured, operationalized tables with:
- Normalized identifiers
- Categories and subcategories
- Relationship data
- Business logic applied

### Tables

#### `identity.contacts_master`

**Purpose**: Master contact table parsed from raw capture.

**Source**: `identity.raw_apple_contacts_records`

**Fields**:
- Core identity fields (name, organization, etc.)
- Apple-specific fields (unique_id, link_id, etc.)
- Truth Engine extensions (categories, subcategories)
- Relationship data

#### `identity.contact_identifiers`

**Purpose**: Multi-platform identifiers for contacts.

**Source**:
- `identity.raw_apple_contacts_phone_numbers`
- `identity.raw_apple_contacts_email_addresses`
- `identity.raw_apple_contacts_social_profiles`

**Fields**:
- Identifier type (phone, email, social)
- Identifier value
- Platform
- Is primary
- Confidence

#### `identity.contact_relationships`

**Purpose**: Relationship data with categories and subcategories.

**Source**: `identity.raw_apple_contacts_records` (parsed)

**Fields**:
- Category code (A-G, X)
- Subcategory code
- Relationship category (normalized)
- Relationship tags
- Confidence

### Parsing Logic

1. **Extract from Raw**: Read from `identity.raw_apple_contacts_*` tables
2. **Normalize Identifiers**: Standardize phone numbers, emails, etc.
3. **Apply Categories**: Map category codes to relationship categories
4. **Link Relationships**: Connect contacts to categories/subcategories
5. **Generate IDs**: Use identity service for canonical IDs

---

## Layer 3: Unifying Tables

### Purpose

Unify identities across **all data sources**:
- Apple Contacts (Layer 2)
- SMS messages
- Grindr conversations
- ChatGPT conversations
- Documents
- Other sources

### Tables

#### `identity.unified_identities`

**Purpose**: Master identity registry for all sources.

**Schema**: See `docs/schema/identity/unified_identities.yaml`

**Fields**:
- `entity_id` - Canonical identity ID
- `identity_type` - person, persona, organization, unknown
- `preferred_name` - Preferred display name
- `canonical_name` - Normalized canonical name
- `known_identifiers` - Array of identifiers from all sources
- `identity_category` - Category (A-G, X)
- `relationship_category` - Normalized relationship category
- `relationship_tags` - Additional relationship tags
- `confidence` - Resolution confidence score

#### `identity.identity_resolutions`

**Purpose**: Track resolution history and confidence scores.

**Fields**:
- `resolution_id` - Unique resolution ID
- `entity_id` - Canonical identity ID
- `source_identifier_type` - phone, email, username, etc.
- `source_identifier_value` - Identifier value
- `source_platform` - SMS, Grindr, ChatGPT, etc.
- `confidence` - Resolution confidence (0.0-1.0)
- `resolution_method` - How identity was resolved
- `resolved_at` - When resolution occurred

#### `identity.message_identity_links`

**Purpose**: Link messages to identities.

**Fields**:
- `link_id` - Unique link ID
- `entity_id` - Canonical identity ID
- `message_id` - Message ID from source
- `source_platform` - SMS, Grindr, ChatGPT, etc.
- `link_type` - FROM, TO, ABOUT, MENTIONED
- `confidence` - Link confidence

#### `identity.entity_identity_links`

**Purpose**: Link entities (documents, conversations, etc.) to identities.

**Fields**:
- `link_id` - Unique link ID
- `entity_id` - Canonical identity ID
- `source_entity_id` - Entity ID from source
- `source_platform` - Document, conversation, etc.
- `link_type` - AUTHOR, MENTIONED, REFERENCED
- `confidence` - Link confidence

#### `identity.cross_source_identifiers`

**Purpose**: Map identifiers across sources.

**Fields**:
- `identifier_id` - Unique identifier ID
- `entity_id` - Canonical identity ID
- `identifier_type` - phone, email, username, etc.
- `identifier_value` - Identifier value
- `source_platform` - SMS, Grindr, ChatGPT, Contacts, etc.
- `is_primary` - Is this the primary identifier
- `confidence` - Identifier confidence

### Resolution Logic (Priority Order)

**Resolution Priority** (checked in order):
1. **Manual Resolution** (Layer 4) - Check `identity.manual_resolutions` first
2. **Exact Match** - Match identifiers exactly (phone, email, etc.)
3. **Fuzzy Match** - Match with fuzzy logic (display names, etc.)
4. **Context Match** - Match using conversation context
5. **Cross-Platform Match** - Match across platforms using known identifiers
6. **Unresolved** - If no match found, add to `identity.unresolved_identifiers`

**Manual Override Priority**:
- Manual resolutions **always** take precedence over automatic
- Manual overrides can **replace** existing automatic resolutions
- Manual merges can **combine** multiple identities

### Confidence Scoring

- **Definitive (1.0)**: Exact identifier match
- **High (0.8-0.9)**: Strong match with multiple signals
- **Medium (0.6-0.7)**: Moderate match with some signals
- **Low (0.4-0.5)**: Weak match with few signals
- **Very Low (0.0-0.3)**: Tentative match

---

## Categories and Subcategories

### Category Framework (Managed by Relationship Service)

**Categories** (A-G, X) - Stored in identity tables, managed by relationship service:
- **A**: Immediate Family
- **B**: Extended Family
- **C**: Close Friends
- **D**: Friends
- **E**: Acquaintances
- **F**: Professional
- **G**: Other
- **X**: Unknown/Uncategorized

**Subcategories**:
- Hierarchical subcategories within each category
- Example: `A1_IMMEDIATE_FAMILY_RAISED_TOGETHER`
- Stored in identity tables, managed by relationship service
- Normalized to relationship categories via relationship service

### Relationship Categories (Managed by Relationship Service)

**Normalized relationship categories** - Managed by relationship service:
- `IMMEDIATE_FAMILY`
- `EXTENDED_FAMILY`
- `CLOSE_FRIEND`
- `FRIEND`
- `ACQUAINTANCE`
- `PROFESSIONAL`
- `OTHER`
- `UNKNOWN`

**Identity Layer Responsibilities**:
- Store category codes (A-G, X) in identity tables
- Store subcategory codes in identity tables
- **Delegate relationship management to relationship service**
- Use relationship service for relationship queries
- Use relationship service for relationship updates

**Relationship Service Responsibilities**:
- Manage relationship metadata
- Normalize category codes to relationship categories
- Provide relationship queries
- Track relationship changes
- Manage relationship confidence scores

---

## Implementation Phases

### Phase 1: Raw Capture ✅

- [x] Design raw capture layer
- [x] Create BigQuery DDL
- [x] Build extraction script
- [x] Extract Apple Contacts database

### Phase 2: Operationalized Tables (Next)

- [ ] Design operationalized tables
- [ ] Create BigQuery DDL
- [ ] Build parsing script
- [ ] Parse raw capture data
- [ ] Apply categories and subcategories

### Phase 3: Unifying Tables (Future)

- [ ] Design unifying tables
- [ ] Create BigQuery DDL
- [ ] Build resolution service
- [ ] Resolve identities across sources
- [ ] Link messages and entities

### Phase 4: Human Intervention Layer (Future)

- [ ] Design manual resolution tables
- [ ] Create BigQuery DDL
- [ ] Build manual resolution UI/API
- [ ] Track unresolved identifiers
- [ ] Support resolution overrides
- [ ] Support identity merges

---

## Integration Points

### Data Sources

1. **Apple Contacts** (Layer 1 → Layer 2 → Layer 3)
2. **SMS Messages** (`sms_messages_v2` → Layer 3)
3. **Grindr** (`grindr.*` → Layer 3)
4. **ChatGPT** (`spine.*` → Layer 3)
5. **Documents** (`spine.*` → Layer 3)
6. **Other Sources** (→ Layer 3)

### Central Services Integration

1. **ID Service** (`architect_central_services.core.identity_service`)
   - **Purpose**: Generate all entity IDs
   - **Used For**: `entity_id` generation, ID registry
   - **Identity Layer Uses**: `generate_person_id()`, `generate_agent_id()`, `register_id()`
   - **DO NOT**: Generate IDs manually

2. **Relationship Service** (`architect_central_services.core.relationship_service`)
   - **Purpose**: Manage relationships and categories
   - **Used For**: Person-to-person relationships, category/subcategory management
   - **Identity Layer Uses**: `get_relationship_manager()`, `create_relationship()`, `get_relationships()`
   - **DO NOT**: Duplicate relationship logic

3. **Identity Resolution Service** (Layer 3)
   - **Purpose**: Cross-source identity resolution
   - **Uses**: ID service for IDs, relationship service for relationships
   - **Manages**: Resolution logic, confidence scoring, cross-source matching

4. **Governance Service** (`architect_central_services.governance`)
   - **Purpose**: Audit trail and cost tracking
   - **Used For**: All operations, cost tracking, audit logs
   - **Identity Layer Uses**: `record_audit()`, `track_cost()`, `get_unified_governance()`

5. **Standard Categories** (`architect_central_services.governance.governance_service.standard_categories`)
   - **Purpose**: Standard category definitions
   - **Used For**: Category validation, standard values
   - **Identity Layer Uses**: `validate_category()`, standard category sets

---

## Central Services Integration

### ID Service Integration

**All ID generation MUST use the Identity Service**:
- `generate_person_id()` - For person identities
- `generate_agent_id()` - For AI persona identities
- `generate_organization_id()` - For organization identities
- `generate_run_id()` - For extraction runs
- `register_id()` - Register IDs in central registry

**Identity Layer Responsibilities**:
- Use ID service for all entity IDs
- Store IDs in `identity.unified_identities.entity_id`
- Link to `governance.id_registry` via ID service
- **DO NOT** generate IDs manually

**Example**:
```python
from architect_central_services import generate_person_id

# Generate person ID using central service
entity_id = generate_person_id(
    full_name="John Smith",
    identifier_type="phone",
    identifier_value="+15551234567",
    platform="contacts"
)
```

### Relationship Service Integration

**All relationship management MUST use the Relationship Service**:
- `get_relationship_manager()` - Get relationship manager
- `create_relationship()` - Create relationships between entities
- `get_relationships()` - Query relationships
- `update_relationship()` - Update relationship metadata

**Identity Layer Responsibilities**:
- Use relationship service for person-to-person relationships
- Use relationship service for entity-to-entity relationships
- Store relationship categories/subcategories via relationship service
- **DO NOT** duplicate relationship logic

**Categories and Subcategories**:
- Use standard categories from `standard_categories.py`
- Use relationship service for relationship management
- Store category codes (A-G, X) in identity tables
- Let relationship service manage relationship metadata

**Example**:
```python
from architect_central_services.core.relationship_service import get_relationship_manager

# Create relationship using central service
relationship_manager = get_relationship_manager()
relationship_manager.create_relationship(
    from_entity_id="person:john-smith:abc123",
    to_entity_id="person:jane-doe:def456",
    relationship_type="friend",
    category_code="C",
    subcategory_code="C1",
    confidence=0.9
)
```

### Standard Categories Integration

**All categories MUST use standard categories**:
- Import from `architect_central_services.governance.governance_service.standard_categories`
- Use `validate_category()` for validation
- **DO NOT** create custom categories without approval

**Identity-Specific Categories**:
- Relationship categories: Use relationship service
- Identity types: `person`, `persona`, `organization`, `unknown`
- Resolution confidence: 0.0-1.0 (float)

## Design Principles

1. **Layered Architecture**: Clear separation of concerns
2. **Canonical Dataset**: `identity` dataset is the source of truth
3. **Incremental Build**: Build layers incrementally
4. **Cross-Source Resolution**: Unify identities across all sources
5. **Confidence Scoring**: Track resolution confidence
6. **Audit Trail**: Track all operations and changes
7. **Data Purity**: Preserve raw data in Layer 1
8. **Human Override Priority**: Manual resolutions always take precedence
9. **Unresolved Tracking**: Track identifiers needing manual intervention
10. **Override Support**: Support overriding existing automatic resolutions
11. **Central Services Alignment**: Use ID service for IDs, relationship service for relationships
12. **Standard Categories**: Use standard categories from central services

---

## Layer 4: Human Intervention & Override Layer

### Purpose

Provide manual ID matching and resolution overrides for cases where:
- Automatic resolution fails (no match found)
- Automatic resolution is incorrect (wrong match)
- Identities need to be merged (duplicate identities)
- New identities need to be created (not in contacts)

### Tables

#### `identity.manual_resolutions`

**Purpose**: Store manual identity resolutions created by humans.

**Fields**:
- `manual_resolution_id` - Unique resolution ID
- `entity_id` - Canonical identity ID (target identity)
- `source_identifier_type` - phone, email, username, etc.
- `source_identifier_value` - Identifier value
- `source_platform` - SMS, Grindr, ChatGPT, etc.
- `resolution_type` - CREATE_NEW, LINK_TO_EXISTING, OVERRIDE_EXISTING
- `previous_entity_id` - Previous entity ID (if overriding)
- `confidence` - Always 1.0 for manual resolutions
- `resolved_by` - User who made the resolution
- `resolved_at` - When resolution was made
- `resolution_notes` - Notes explaining the resolution
- `is_active` - Is this resolution active

**Characteristics**:
- **Highest priority**: Checked before automatic resolution
- **Always confidence 1.0**: Human-verified
- **Audit trail**: Track who, when, why

#### `identity.unresolved_identifiers`

**Purpose**: Track identifiers that couldn't be automatically resolved.

**Fields**:
- `unresolved_id` - Unique unresolved identifier ID
- `source_identifier_type` - phone, email, username, etc.
- `source_identifier_value` - Identifier value
- `source_platform` - SMS, Grindr, ChatGPT, etc.
- `display_name` - Display name (if available)
- `context` - Context where identifier was found
- `first_seen` - First time this identifier was seen
- `last_seen` - Last time this identifier was seen
- `occurrence_count` - How many times this identifier appeared
- `resolution_status` - PENDING, IN_REVIEW, RESOLVED, IGNORED
- `assigned_to` - User assigned to resolve (if any)
- `priority` - HIGH, MEDIUM, LOW
- `notes` - Notes about the identifier

**Characteristics**:
- **Queue for manual review**: Identifiers needing human intervention
- **Priority tracking**: High priority for frequent identifiers
- **Status tracking**: Track resolution progress

#### `identity.resolution_overrides`

**Purpose**: Override existing automatic resolutions.

**Fields**:
- `override_id` - Unique override ID
- `original_resolution_id` - Original automatic resolution ID
- `original_entity_id` - Original entity ID (being overridden)
- `new_entity_id` - New entity ID (correct identity)
- `override_reason` - Why the override was made
- `override_type` - CORRECT_MATCH, MERGE_IDENTITIES, SPLIT_IDENTITY
- `overridden_by` - User who made the override
- `overridden_at` - When override was made
- `is_active` - Is this override active
- `notes` - Additional notes

**Characteristics**:
- **Override automatic**: Replace automatic resolution with manual
- **Track original**: Keep record of what was overridden
- **Audit trail**: Track who, when, why

#### `identity.merge_operations`

**Purpose**: Track manual identity merges (combining duplicate identities).

**Fields**:
- `merge_id` - Unique merge ID
- `source_entity_id` - Entity ID being merged (source)
- `target_entity_id` - Entity ID being merged into (target)
- `merge_reason` - Why identities were merged
- `merged_by` - User who performed the merge
- `merged_at` - When merge was performed
- `merge_metadata` - Additional merge metadata (JSON)
- `is_active` - Is this merge active

**Characteristics**:
- **Combine identities**: Merge duplicate identities into one
- **Preserve history**: Keep record of what was merged
- **Audit trail**: Track who, when, why

### Resolution Priority Logic

**When resolving an identifier, check in this order**:

1. **Check Manual Resolutions** (`identity.manual_resolutions`)
   - If active manual resolution exists → Use it (confidence 1.0)
   - Skip to step 5

2. **Check Resolution Overrides** (`identity.resolution_overrides`)
   - If override exists for this identifier → Use override
   - Skip to step 5

3. **Check Automatic Resolution** (Layer 3)
   - Run automatic resolution algorithms
   - If match found → Use it (with confidence score)
   - If no match → Go to step 4

4. **Add to Unresolved** (`identity.unresolved_identifiers`)
   - If no match found → Add to unresolved queue
   - Mark as PENDING for manual review

5. **Return Resolution**
   - Return entity_id and confidence
   - Log resolution source (manual vs automatic)

### Manual Resolution Workflow

1. **Automatic Resolution Fails**
   - Identifier added to `identity.unresolved_identifiers`
   - Status: PENDING

2. **Human Reviews Unresolved**
   - Human reviews `identity.unresolved_identifiers`
   - Identifies correct identity or creates new one

3. **Human Creates Manual Resolution**
   - Creates record in `identity.manual_resolutions`
   - Links identifier to entity_id
   - Sets confidence to 1.0

4. **System Uses Manual Resolution**
   - Future resolution checks check manual resolutions first
   - Uses manual resolution (highest priority)

5. **Update Unresolved Status**
   - Updates `identity.unresolved_identifiers` status to RESOLVED
   - Links to manual_resolution_id

### Override Workflow

1. **Automatic Resolution is Wrong**
   - Human identifies incorrect automatic resolution
   - Creates override in `identity.resolution_overrides`

2. **Override Takes Effect**
   - System checks overrides before automatic resolutions
   - Uses override entity_id instead of original

3. **Original Resolution Marked**
   - Original resolution marked as overridden
   - Audit trail preserved

### Merge Workflow

1. **Duplicate Identities Found**
   - Human identifies duplicate identities
   - Decides which is the canonical identity

2. **Create Merge Operation**
   - Creates record in `identity.merge_operations`
   - Specifies source and target entity_ids

3. **Merge Takes Effect**
   - System uses target entity_id for all references
   - Source entity_id is deprecated (but preserved)

4. **Update Unified Identities**
   - Updates `identity.unified_identities` with merged data
   - Preserves history of merge

### API/UI Requirements

**Manual Resolution Interface**:
- View unresolved identifiers
- Search for identities
- Create manual resolutions
- Override existing resolutions
- Merge identities

**Features**:
- Search by identifier (phone, email, username)
- Search by display name
- View context where identifier appeared
- View existing resolutions
- Create new identities if needed

---

## Related Documentation

- `docs/architecture/IDENTITY_LAYER_RAW_CAPTURE.md` - Layer 1 design
- `docs/architecture/IDENTITY_LAYER_FOUNDATION.md` - Foundation design
- `docs/schema/identity/unified_identities.yaml` - Layer 3 schema
- `identity/scripts/extract_apple_contacts_raw.py` - Layer 1 extraction
- `identity/sql/create_raw_capture_tables.sql` - Layer 1 DDL

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0
**Status**: Architecture Design Complete
