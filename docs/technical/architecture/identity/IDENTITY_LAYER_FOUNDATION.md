# Identity Layer Foundation - Based on Apple Contacts Architecture

**Version**: 1.0.0
**Date**: 2025-12-08
**Status**: Foundation Design - Brand New Architecture
**Owner**: Jeremy Serna

---

## Executive Summary

This document defines a **brand new identity layer architecture** based on the Apple Contacts database structure. The Apple Contacts archive (`Contacts - 12-08-2025.abbu`) serves as the **foundational source of truth** for all identity resolution, with 1,651 contacts containing names, phone numbers, email addresses, and metadata.

The identity layer extends the Apple Contacts model to:
- Link contacts to SMS messages (via phone numbers)
- Link contacts to Grindr profiles (via name/phone matching)
- Link contacts to ChatGPT conversations (via user IDs/names)
- Link contacts to Zoom participants (via email/name matching)
- Resolve identities across all platforms
- Track relationship categories and subcategories

---

## Apple Contacts Architecture Analysis

### Core Data Model

The Apple Contacts database uses a **Core Data SQLite store** with the following key structure:

#### Main Contact Record (`ZABCDRECORD`)
- **Z_PK**: Primary key (internal)
- **ZUNIQUEID**: Stable unique identifier (e.g., `EDA9DB12-CDA3-43EC-AF5D-B782494FDCC0:ABPerson`)
- **ZIDENTITYUNIQUEID**: Identity linking ID (for unified contacts)
- **ZLINKID**: Link ID (for related contacts)
- **ZFIRSTNAME**, **ZLASTNAME**: Name components
- **ZNAME**: Full name
- **ZNAMENORMALIZED**: Normalized name (for searching)
- **ZORGANIZATION**: Organization name
- **ZNICKNAME**: Nickname
- **ZJOBTITLE**, **ZDEPARTMENT**: Professional info
- **ZCREATIONDATE**, **ZMODIFICATIONDATE**: Timestamps
- **Z_ENT**: Entity type (22 = Person, 19 = Group)

#### Phone Numbers (`ZABCDPHONENUMBER`)
- **ZOWNER**: Foreign key to `ZABCDRECORD.Z_PK`
- **ZFULLNUMBER**: Full phone number (e.g., `+19548735931`)
- **ZCOUNTRYCODE**, **ZAREACODE**, **ZLOCALNUMBER**: Components
- **ZLABEL**: Label (Mobile, Work, Home, etc.)
- **ZISPRIMARY**: Is primary phone
- **ZISPRIVATE**: Is private
- **ZORDERINGINDEX**: Display order

#### Email Addresses (`ZABCDEMAILADDRESS`)
- **ZOWNER**: Foreign key to `ZABCDRECORD.Z_PK`
- **ZADDRESS**: Email address
- **ZADDRESSNORMALIZED**: Normalized email (lowercase)
- **ZLABEL**: Label (Work, Home, etc.)
- **ZISPRIMARY**: Is primary email
- **ZISPRIVATE**: Is private
- **ZORDERINGINDEX**: Display order

#### Social Profiles (`ZABCDSOCIALPROFILE`)
- **ZOWNER**: Foreign key to `ZABCDRECORD.Z_PK`
- **ZSERVICENAME**: Service (Instagram, Facebook, etc.)
- **ZUSERNAME**: Username
- **ZUSERIDENTIFIER**: User identifier
- **ZURLSTRING**: Profile URL
- **ZDISPLAYNAME**: Display name

#### Notes (`ZABCDNOTE`)
- **ZCONTACT**: Foreign key to `ZABCDRECORD.Z_PK`
- **ZTEXT**: Note text (can contain relationship context)

### Key Design Patterns

1. **One-to-Many Relationships**: One contact can have multiple phones, emails, social profiles
2. **Stable Identifiers**: `ZUNIQUEID` is stable across syncs
3. **Identity Linking**: `ZIDENTITYUNIQUEID` and `ZLINKID` for unified contacts
4. **Normalization**: Normalized fields for searching/matching
5. **Primary Flags**: `ZISPRIMARY` flags for preferred identifiers
6. **Labels**: Labels for context (Mobile, Work, Home, etc.)

---

## Truth Engine Identity Layer Design

### Foundation: Apple Contacts as Source of Truth

The Apple Contacts database (`Contacts - 12-08-2025.abbu`) contains:
- **1,651 contacts** with comprehensive data
- **1,123+ phone numbers** linked to contacts
- **564+ email addresses** linked to contacts
- **1,064+ contacts with names**
- **100+ organizations**

This becomes the **foundational identity registry** for all cross-platform resolution.

### Core Identity Tables

#### 1. `identity.contacts_master` (Foundation Table)

**Purpose**: Master contact registry based on Apple Contacts structure

**Schema**:
```sql
CREATE TABLE `identity.contacts_master` (
  -- Apple Contacts Identifiers
  contact_id INT64 NOT NULL,                    -- Generated sequential ID
  apple_unique_id STRING NOT NULL,              -- ZUNIQUEID from Apple Contacts
  apple_identity_unique_id STRING,              -- ZIDENTITYUNIQUEID (for unified contacts)
  apple_link_id STRING,                         -- ZLINKID (for related contacts)

  -- Name Fields (from Apple Contacts)
  first_name STRING,
  last_name STRING,
  middle_name STRING,
  nickname STRING,
  name_suffix STRING,
  title STRING,
  full_name STRING,                             -- ZNAME
  name_normalized STRING,                       -- ZNAMENORMALIZED (for searching)
  sorting_first_name STRING,                    -- ZSORTINGFIRSTNAME
  sorting_last_name STRING,                     -- ZSORTINGLASTNAME

  -- Organization Fields
  organization STRING,                          -- ZORGANIZATION
  job_title STRING,                             -- ZJOBTITLE
  department STRING,                            -- ZDEPARTMENT

  -- Relationship Categorization (Truth Engine Extension)
  category_code STRING,                         -- A, B, C, D, E, F, G, X
  subcategory_code STRING,                     -- Full format (e.g., A1_IMMEDIATE_FAMILY_RAISED_TOGETHER)
  relationship_category STRING,                 -- family, friend, romantic, etc.

  -- Metadata
  notes STRING,                                 -- From ZABCDNOTE
  birthday DATE,
  is_business BOOL DEFAULT FALSE,               -- TRUE if organization contact
  is_me BOOL DEFAULT FALSE,                     -- TRUE if this is Jeremy

  -- Timestamps
  created_at TIMESTAMP,                         -- ZCREATIONDATE
  updated_at TIMESTAMP,                         -- ZMODIFICATIONDATE
  first_seen_in_primitive_engine TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_seen_in_primitive_engine TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  -- Truth Engine Extensions
  primitive_engine_entity_id STRING,               -- Generated entity_id for unified_identities
  resolution_confidence FLOAT64 DEFAULT 1.0,   -- Confidence in identity resolution

  PRIMARY KEY (contact_id),
  UNIQUE (apple_unique_id),
  INDEX (name_normalized),
  INDEX (apple_identity_unique_id),
  INDEX (apple_link_id),
  INDEX (category_code, subcategory_code)
)
PARTITION BY DATE(created_at)
CLUSTER BY name_normalized, category_code;
```

#### 2. `identity.contact_identifiers` (Multi-Platform Identifiers)

**Purpose**: Store all identifiers (phone, email, social, platform-specific) linked to contacts

**Schema**:
```sql
CREATE TABLE `identity.contact_identifiers` (
  identifier_id STRING NOT NULL,                -- Generated ID
  contact_id INT64 NOT NULL,                    -- FK to contacts_master

  -- Identifier Details
  identifier_type STRING NOT NULL,              -- phone, email, social_profile, platform_id
  identifier_value STRING NOT NULL,             -- The identifier value
  identifier_normalized STRING,                 -- Normalized for matching

  -- Source Information
  source_platform STRING,                       -- apple_contacts, sms, grindr, chatgpt, zoom
  source_label STRING,                          -- Mobile, Work, Home, etc. (from Apple Contacts)

  -- Apple Contacts Fields (if from Apple Contacts)
  apple_identifier_id STRING,                  -- Z_PK from ZABCDPHONENUMBER, etc.
  is_primary BOOL DEFAULT FALSE,                -- ZISPRIMARY
  is_private BOOL DEFAULT FALSE,                -- ZISPRIVATE
  ordering_index INT64,                         -- ZORDERINGINDEX

  -- Phone Number Components (if identifier_type = 'phone')
  country_code STRING,
  area_code STRING,
  local_number STRING,
  last_four_digits STRING,                      -- For fuzzy matching

  -- Email Components (if identifier_type = 'email')
  email_domain STRING,                          -- Extracted domain

  -- Social Profile Details (if identifier_type = 'social_profile')
  social_service STRING,                        -- Instagram, Facebook, etc.
  social_username STRING,
  social_user_identifier STRING,
  social_url STRING,

  -- Platform-Specific Identifiers
  platform_user_id STRING,                      -- For ChatGPT, Zoom, etc.
  platform_conversation_id STRING,              -- For linking to conversations

  -- Metadata
  first_seen TIMESTAMP,
  last_seen TIMESTAMP,
  confidence FLOAT64 DEFAULT 1.0,               -- Confidence this identifier belongs to contact
  verification_status STRING,                   -- verified, unverified, disputed

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  PRIMARY KEY (identifier_id),
  FOREIGN KEY (contact_id) REFERENCES identity.contacts_master(contact_id),
  INDEX (contact_id),
  INDEX (identifier_type, identifier_value),
  INDEX (identifier_normalized),
  INDEX (source_platform),
  INDEX (is_primary)
)
PARTITION BY DATE(created_at)
CLUSTER BY contact_id, identifier_type;
```

#### 3. `identity.unified_identities` (Cross-Platform Identity Resolution)

**Purpose**: Unified identity registry that links contacts to all platforms

**Schema**:
```sql
CREATE TABLE `identity.unified_identities` (
  -- Identity Identifiers
  entity_id STRING NOT NULL,                   -- Generated by IdentityService
  contact_id INT64,                             -- FK to contacts_master (if linked)

  -- Identity Type
  identity_type STRING NOT NULL,                -- person, persona, organization
  identity_category STRING,                     -- real_person, ai_persona, organization

  -- Name Information
  preferred_name STRING,                        -- Display name
  canonical_name STRING,                        -- Normalized for matching
  name_variations ARRAY<STRING>,                -- All known name variations

  -- Relationship Context
  category_code STRING,                         -- From contacts_master
  subcategory_code STRING,                     -- From contacts_master
  relationship_category STRING,                 -- family, friend, romantic, etc.

  -- Known Identifiers (Array of Struct)
  known_identifiers ARRAY<STRUCT<
    identifier_type STRING,
    identifier_value STRING,
    identifier_normalized STRING,
    platform STRING,
    source_label STRING,
    confidence FLOAT64,
    first_seen TIMESTAMP,
    last_seen TIMESTAMP,
    is_primary BOOL,
    verification_status STRING
  >>,

  -- Cross-Platform Links
  platform_links ARRAY<STRUCT<
    platform STRING,
    platform_user_id STRING,
    platform_display_name STRING,
    link_confidence FLOAT64,
    first_linked_at TIMESTAMP,
    last_linked_at TIMESTAMP
  >>,

  -- Metadata
  is_business BOOL DEFAULT FALSE,
  is_ai_persona BOOL DEFAULT FALSE,
  resolution_method STRING,                     -- apple_contacts, phone_match, email_match, etc.
  resolution_confidence FLOAT64 DEFAULT 1.0,

  -- Metrics
  total_messages INT64 DEFAULT 0,
  total_interactions INT64 DEFAULT 0,
  platforms_present ARRAY<STRING>,              -- [sms, grindr, chatgpt, zoom]
  first_interaction TIMESTAMP,
  last_interaction TIMESTAMP,

  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  PRIMARY KEY (entity_id),
  FOREIGN KEY (contact_id) REFERENCES identity.contacts_master(contact_id),
  INDEX (contact_id),
  INDEX (canonical_name),
  INDEX (identity_type),
  INDEX (category_code, subcategory_code)
)
PARTITION BY DATE(created_at)
CLUSTER BY entity_id, identity_type;
```

#### 4. `identity.identity_resolutions` (Resolution History)

**Purpose**: Track how identities were resolved across platforms

**Schema**:
```sql
CREATE TABLE `identity.identity_resolutions` (
  resolution_id STRING NOT NULL,
  entity_id STRING NOT NULL,                   -- FK to unified_identities
  contact_id INT64,                             -- FK to contacts_master

  -- Source Information
  source_platform STRING NOT NULL,             -- sms, grindr, chatgpt, zoom
  source_identifier_type STRING NOT NULL,      -- phone, email, profile_id, user_id
  source_identifier_value STRING NOT NULL,
  source_display_name STRING,

  -- Resolution Details
  resolution_method STRING NOT NULL,           -- apple_contacts_match, phone_match, email_match, name_match, etc.
  resolution_confidence FLOAT64 NOT NULL,     -- 0.0-1.0
  resolution_context JSON,                      -- Additional context

  -- Status
  resolution_status STRING,                     -- resolved, pending, manual_review, disputed
  verified_by_user BOOL DEFAULT FALSE,
  verification_timestamp TIMESTAMP,

  -- Timestamps
  resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),

  PRIMARY KEY (resolution_id),
  FOREIGN KEY (entity_id) REFERENCES identity.unified_identities(entity_id),
  FOREIGN KEY (contact_id) REFERENCES identity.contacts_master(contact_id),
  INDEX (entity_id),
  INDEX (contact_id),
  INDEX (source_platform, source_identifier_type, source_identifier_value),
  INDEX (resolution_status)
)
PARTITION BY DATE(resolved_at)
CLUSTER BY entity_id, source_platform;
```

---

## Identity Resolution Flow

### Step 1: Bootstrap from Apple Contacts

1. **Extract all contacts** from Apple Contacts archive
2. **Create `contacts_master` records** for each contact
3. **Create `contact_identifiers` records** for all phones, emails, social profiles
4. **Generate `entity_id`** for each contact using `IdentityService.generate_person_id()`
5. **Create `unified_identities` records** linking to contacts

### Step 2: Link SMS Messages

1. **Extract phone numbers** from SMS messages (`source_data.sms_messages_v2.normalized_phone`)
2. **Match against `contact_identifiers`** where `identifier_type = 'phone'`
3. **Link SMS messages** to contacts via `contact_id`
4. **Create `identity_resolutions`** records for SMS → Contact links
5. **Update `unified_identities.known_identifiers`** with SMS platform links

### Step 3: Link Grindr Profiles

1. **Extract Grindr profiles** with display names, real names, phone numbers
2. **Match against `contacts_master`**:
   - By phone number (if available in Grindr profile notes)
   - By name (fuzzy matching on `name_normalized`)
3. **Create `identity_resolutions`** for Grindr → Contact links
4. **Update `unified_identities`** with Grindr platform links

### Step 4: Link ChatGPT Conversations

1. **Extract ChatGPT user IDs** and conversation contexts
2. **Match against `contacts_master`**:
   - By name mentions in conversations
   - By email (if available)
3. **Create `identity_resolutions`** for ChatGPT → Contact links
4. **Update `unified_identities`** with ChatGPT platform links

### Step 5: Link Zoom Participants

1. **Extract Zoom participant emails** and display names
2. **Match against `contact_identifiers`** where `identifier_type = 'email'`
3. **Create `identity_resolutions`** for Zoom → Contact links
4. **Update `unified_identities`** with Zoom platform links

---

## Key Design Principles

### 1. Apple Contacts as Foundation

- **Source of Truth**: Apple Contacts is the authoritative source for contact information
- **Stable Identifiers**: Use `apple_unique_id` as stable reference
- **Preserve Structure**: Maintain Apple Contacts relationships (phones, emails, social profiles)
- **Extend, Don't Replace**: Add Truth Engine extensions without breaking Apple Contacts structure

### 2. Multi-Identifier Support

- **One Contact, Many Identifiers**: One contact can have multiple phones, emails, social profiles
- **Primary Flags**: Use `is_primary` to identify preferred identifiers
- **Labels**: Preserve Apple Contacts labels (Mobile, Work, Home, etc.)
- **Normalization**: Normalize all identifiers for matching

### 3. Cross-Platform Resolution

- **Platform-Agnostic**: Identity layer works across all platforms
- **Confidence Scoring**: Track confidence for all resolutions
- **Resolution History**: Maintain audit trail of how identities were resolved
- **Manual Override**: Allow user verification and correction

### 4. Relationship Categorization

- **Category Framework**: Use A-G, X category codes
- **Subcategory Codes**: Full format (e.g., A1_IMMEDIATE_FAMILY_RAISED_TOGETHER)
- **Inference**: Infer categories from contact names, organizations, notes
- **Manual Assignment**: Allow manual category assignment

---

## Implementation Phases

### Phase 1: Bootstrap Apple Contacts (Week 1)

**Goal**: Import all Apple Contacts data into Truth Engine identity layer

**Tasks**:
1. Extract all contacts from Apple Contacts archive
2. Create `contacts_master` records
3. Create `contact_identifiers` records for all phones, emails, social profiles
4. Generate `entity_id` for each contact
5. Create `unified_identities` records
6. Validate data completeness

**Deliverables**:
- `identity.contacts_master` table populated with 1,651 contacts
- `identity.contact_identifiers` table populated with all identifiers
- `identity.unified_identities` table populated with all contacts

### Phase 2: Link SMS Messages (Week 2)

**Goal**: Link SMS messages to contacts via phone numbers

**Tasks**:
1. Extract phone numbers from `source_data.sms_messages_v2`
2. Match against `contact_identifiers` (phone type)
3. Link SMS messages to contacts
4. Create `identity_resolutions` records
5. Update `unified_identities.known_identifiers`

**Deliverables**:
- SMS messages linked to contacts
- `identity_resolutions` records for SMS → Contact links
- Updated `unified_identities` with SMS platform links

### Phase 3: Link Grindr Profiles (Week 3)

**Goal**: Link Grindr profiles to contacts via name/phone matching

**Tasks**:
1. Extract Grindr profiles with names, phones
2. Match against `contacts_master` (name fuzzy matching)
3. Match against `contact_identifiers` (phone matching)
4. Create `identity_resolutions` records
5. Update `unified_identities` with Grindr links

**Deliverables**:
- Grindr profiles linked to contacts
- `identity_resolutions` records for Grindr → Contact links
- Updated `unified_identities` with Grindr platform links

### Phase 4: Link ChatGPT & Zoom (Week 4)

**Goal**: Link ChatGPT conversations and Zoom participants to contacts

**Tasks**:
1. Extract ChatGPT user IDs and conversation contexts
2. Extract Zoom participant emails and names
3. Match against `contacts_master` and `contact_identifiers`
4. Create `identity_resolutions` records
5. Update `unified_identities` with platform links

**Deliverables**:
- ChatGPT conversations linked to contacts
- Zoom participants linked to contacts
- Complete cross-platform identity resolution

### Phase 5: Category Framework (Week 5)

**Goal**: Add relationship categorization to contacts

**Tasks**:
1. Infer categories from contact names, organizations, notes
2. Allow manual category assignment
3. Update `contacts_master` with category codes
4. Update `unified_identities` with relationship categories
5. Validate category assignments

**Deliverables**:
- Category codes assigned to contacts
- Relationship categorization complete
- Category framework integrated

---

## Data Extraction Queries

### Extract Contacts from Apple Contacts

```sql
-- Extract all contacts with identifiers
SELECT
  r.Z_PK as apple_contact_pk,
  r.ZUNIQUEID as apple_unique_id,
  r.ZIDENTITYUNIQUEID as apple_identity_unique_id,
  r.ZLINKID as apple_link_id,
  r.ZFIRSTNAME as first_name,
  r.ZLASTNAME as last_name,
  r.ZMIDDLENAME as middle_name,
  r.ZNICKNAME as nickname,
  r.ZNAME as full_name,
  r.ZNAMENORMALIZED as name_normalized,
  r.ZORGANIZATION as organization,
  r.ZJOBTITLE as job_title,
  r.ZDEPARTMENT as department,
  r.ZCREATIONDATE as created_at,
  r.ZMODIFICATIONDATE as updated_at,
  n.ZTEXT as notes
FROM ZABCDRECORD r
LEFT JOIN ZABCDNOTE n ON r.Z_PK = n.ZCONTACT
WHERE r.Z_ENT = 22  -- Person entity type
ORDER BY r.Z_PK;
```

### Extract Phone Numbers

```sql
-- Extract all phone numbers with contact links
SELECT
  p.Z_PK as apple_phone_pk,
  p.ZOWNER as apple_contact_pk,
  p.ZFULLNUMBER as full_number,
  p.ZCOUNTRYCODE as country_code,
  p.ZAREACODE as area_code,
  p.ZLOCALNUMBER as local_number,
  p.ZLABEL as label,
  p.ZISPRIMARY as is_primary,
  p.ZISPRIVATE as is_private,
  p.ZORDERINGINDEX as ordering_index
FROM ZABCDPHONENUMBER p
JOIN ZABCDRECORD r ON p.ZOWNER = r.Z_PK
WHERE r.Z_ENT = 22
ORDER BY p.ZOWNER, p.ZISPRIMARY DESC, p.ZORDERINGINDEX;
```

### Extract Email Addresses

```sql
-- Extract all email addresses with contact links
SELECT
  e.Z_PK as apple_email_pk,
  e.ZOWNER as apple_contact_pk,
  e.ZADDRESS as email_address,
  e.ZADDRESSNORMALIZED as email_normalized,
  e.ZLABEL as label,
  e.ZISPRIMARY as is_primary,
  e.ZISPRIVATE as is_private,
  e.ZORDERINGINDEX as ordering_index
FROM ZABCDEMAILADDRESS e
JOIN ZABCDRECORD r ON e.ZOWNER = r.Z_PK
WHERE r.Z_ENT = 22
ORDER BY e.ZOWNER, e.ZISPRIMARY DESC, e.ZORDERINGINDEX;
```

### Extract Social Profiles

```sql
-- Extract all social profiles with contact links
SELECT
  s.Z_PK as apple_social_pk,
  s.ZOWNER as apple_contact_pk,
  s.ZSERVICENAME as service_name,
  s.ZUSERNAME as username,
  s.ZUSERIDENTIFIER as user_identifier,
  s.ZURLSTRING as url_string,
  s.ZDISPLAYNAME as display_name
FROM ZABCDSOCIALPROFILE s
JOIN ZABCDRECORD r ON s.ZOWNER = r.Z_PK
WHERE r.Z_ENT = 22
ORDER BY s.ZOWNER;
```

---

## Next Steps

1. **Review and Approve**: Review this foundation design
2. **Create BigQuery Tables**: Generate DDL for all identity tables
3. **Build Extraction Script**: Create script to extract from Apple Contacts archive
4. **Build Import Pipeline**: Create pipeline to import into BigQuery
5. **Implement Resolution Service**: Build identity resolution service
6. **Link Platforms**: Implement platform linking (SMS, Grindr, ChatGPT, Zoom)
7. **Add Category Framework**: Implement relationship categorization

---

**Last Updated**: 2025-12-08
**Version**: 1.0.0
**Status**: Foundation Design Complete - Ready for Implementation
