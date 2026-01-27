# Schema Alignment - Existing vs New

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Alignment Analysis
**Owner**: Jeremy Serna

---

## Executive Summary

This document aligns new schemas with existing implementations to avoid duplication and ensure consistency.

**Key Findings**:
1. **`identity.contacts_master`** already exists with Apple Contacts structure
2. **`identity.contact_identifiers`** already exists
3. **`identity.unified_identities`** already exists for cross-platform resolution
4. **`RelationshipService`** exists but is for organism partnerships (DuckDB), NOT people-to-people relationships
5. **New tables needed**: businesses_master, people_relationships, people_business_relationships

---

## Existing Tables (DO NOT DUPLICATE)

### 1. `identity.contacts_master` (EXISTS)

**Current Schema** (from IDENTITY_LAYER_FOUNDATION.md):
```sql
CREATE TABLE `identity.contacts_master` (
  contact_id INT64 NOT NULL,
  apple_unique_id STRING NOT NULL,
  apple_identity_unique_id STRING,
  apple_link_id STRING,
  
  -- Name Fields
  first_name STRING,
  last_name STRING,
  middle_name STRING,
  nickname STRING,
  name_suffix STRING,
  title STRING,
  full_name STRING,
  name_normalized STRING,
  sorting_first_name STRING,
  sorting_last_name STRING,
  
  -- Organization Fields
  organization STRING,
  job_title STRING,
  department STRING,
  
  -- Relationship Categorization
  category_code STRING,                         -- A, B, C, D, E, F, G, H, X
  subcategory_code STRING,
  relationship_category STRING,
  
  -- Metadata
  notes STRING,
  birthday DATE,
  is_business BOOL DEFAULT FALSE,
  is_me BOOL DEFAULT FALSE,
  
  -- Timestamps
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  first_seen_in_primitive_engine TIMESTAMP,
  last_seen_in_primitive_engine TIMESTAMP,
  
  -- Truth Engine Extensions
  primitive_engine_entity_id STRING,
  resolution_confidence FLOAT64 DEFAULT 1.0,
  
  PRIMARY KEY (contact_id),
  UNIQUE (apple_unique_id)
)
```

**Action**: EXTEND this table, don't duplicate. Add sync metadata fields.

### 2. `identity.contact_identifiers` (EXISTS)

**Current Schema**:
```sql
CREATE TABLE `identity.contact_identifiers` (
  identifier_id STRING NOT NULL,
  contact_id INT64 NOT NULL,
  identifier_type STRING NOT NULL,
  identifier_value STRING NOT NULL,
  identifier_normalized STRING,
  source_platform STRING,
  source_label STRING,
  apple_identifier_id STRING,
  is_primary BOOL DEFAULT FALSE,
  is_private BOOL DEFAULT FALSE,
  ordering_index INT64,
  -- Phone/Email/Social fields...
  first_seen TIMESTAMP,
  last_seen TIMESTAMP,
  confidence FLOAT64 DEFAULT 1.0,
  verification_status STRING,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  PRIMARY KEY (identifier_id),
  FOREIGN KEY (contact_id) REFERENCES identity.contacts_master(contact_id)
)
```

**Action**: Use as-is. No changes needed for sync.

### 3. `identity.unified_identities` (EXISTS)

**Current Schema**:
```sql
CREATE TABLE `identity.unified_identities` (
  entity_id STRING NOT NULL,
  contact_id INT64,
  identity_type STRING NOT NULL,
  identity_category STRING,
  preferred_name STRING,
  canonical_name STRING,
  name_variations ARRAY<STRING>,
  category_code STRING,
  subcategory_code STRING,
  relationship_category STRING,
  known_identifiers ARRAY<STRUCT<...>>,
  platform_links ARRAY<STRUCT<...>>,
  is_business BOOL DEFAULT FALSE,
  -- ... metrics, timestamps
)
```

**Action**: Use for cross-platform resolution. Businesses can use this OR separate table.

---

## New Tables (TO CREATE)

### 1. `identity.businesses_master` (NEW)

**Purpose**: Separate table for businesses (distinct from contacts)

**Rationale**: 
- `identity.contacts_master.is_business = TRUE` indicates a business contact
- But businesses need richer data (industry, revenue, etc.)
- Separate table allows businesses to have their own lifecycle

**Schema**: See `businesses_migration.sql`

### 2. `identity.people_relationships` (NEW)

**Purpose**: People-to-people relationships for social graph

**Rationale**:
- `RelationshipService` is for organism partnerships (DuckDB, trust levels)
- This is for human social graph (who knows who)
- Completely different purpose - no duplication

**Schema**: See `people_relationships_migration.sql`

### 3. `identity.people_business_relationships` (NEW)

**Purpose**: Many-to-many people-business relationships

**Rationale**: 
- New requirement - people can link to businesses
- Not covered by existing tables

**Schema**: See `businesses_migration.sql`

---

## Schema Extensions (ALTER EXISTING)

### Extend `identity.contacts_master` with Sync Metadata

```sql
-- Add sync metadata fields to existing table
ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS sync_metadata STRUCT<
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64,
  sync_status STRING,
  source_systems ARRAY<STRING>,
  sync_errors ARRAY<STRUCT<
    timestamp TIMESTAMP,
    system STRING,
    error_type STRING,
    error_message STRING,
    error_details JSON,
    resolved BOOL
  >>
>;

-- Add LLM context fields
ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS llm_context JSON;

ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS communication_stats JSON;

ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS social_network JSON;

ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS ai_insights JSON;

ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS recommendations JSON;
```

### Extend `identity.contact_identifiers` with Sync Metadata

```sql
ALTER TABLE `identity.contact_identifiers`
ADD COLUMN IF NOT EXISTS sync_metadata STRUCT<
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64
>;
```

---

## Alignment Strategy

### Contacts

**Use Existing**: `identity.contacts_master` and `identity.contact_identifiers`

**Extend With**:
- Sync metadata fields
- LLM context fields
- Communication stats
- Social network data

**Don't Create**: New contacts_master table

### Businesses

**Create New**: `identity.businesses_master`

**Rationale**: 
- Businesses need different fields than contacts
- Can still link via `unified_identities` if needed
- Separate lifecycle and management

### People Relationships

**Create New**: `identity.people_relationships`

**Rationale**:
- `RelationshipService` is for organism partnerships (different purpose)
- This is for human social graph
- No duplication

### People-Business Relationships

**Create New**: `identity.people_business_relationships`

**Rationale**: New requirement, not covered by existing tables

---

## Migration Path

### Phase 1: Extend Existing Tables

1. Add sync metadata to `identity.contacts_master`
2. Add LLM context fields to `identity.contacts_master`
3. Add sync metadata to `identity.contact_identifiers`

### Phase 2: Create New Tables

1. Create `identity.businesses_master`
2. Create `identity.people_relationships`
3. Create `identity.people_business_relationships`

### Phase 3: Data Migration

1. Extract businesses from `identity.contacts_master` where `is_business = TRUE`
2. Create businesses in `identity.businesses_master`
3. Create people-business relationships
4. Create people-people relationships from category codes

---

## RelationshipService Clarification

**Existing**: `src/truth_forge/services/relationship/service.py`

**Purpose**: Organism partnerships (trust levels, interaction context)
- Uses DuckDB (local)
- Stores partnership data as JSON
- Tracks trust levels, interaction history
- For organism's social memory

**New**: `PeopleRelationshipSyncService`

**Purpose**: Human social graph (who knows who)
- Uses BigQuery (canonical)
- Structured relationship data
- Tracks people-to-people connections
- For social graph modeling

**No Conflict**: Different purposes, different storage, different use cases.

---

## Supabase Alignment

### Use Existing Supabase Schema

The `supabase_migration.sql` already created:
- `contacts_master` table
- `contact_identifiers` table

**Action**: Extend these with sync metadata, don't recreate.

### Add New Tables

- `businesses_master`
- `people_relationships`
- `people_business_relationships`

---

## Summary

| Table | Status | Action |
|-------|--------|--------|
| `identity.contacts_master` | EXISTS | EXTEND with sync metadata + LLM fields |
| `identity.contact_identifiers` | EXISTS | EXTEND with sync metadata |
| `identity.unified_identities` | EXISTS | USE AS-IS |
| `identity.businesses_master` | NEW | CREATE |
| `identity.people_relationships` | NEW | CREATE |
| `identity.people_business_relationships` | NEW | CREATE |
| `RelationshipService` (DuckDB) | EXISTS | NO CONFLICT (different purpose) |

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Alignment Complete
