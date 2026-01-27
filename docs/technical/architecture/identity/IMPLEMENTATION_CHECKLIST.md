# Implementation Checklist - Aligned Schemas

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Ready for Implementation

---

## ✅ Alignment Complete

All schemas have been aligned with existing implementations. No duplication.

---

## Migration Order

### Step 1: Extend Existing Tables

**File**: `EXTEND_EXISTING_TABLES.sql`

**Actions**:
- [ ] Run BigQuery ALTER TABLE statements to extend `identity.contacts_master`
- [ ] Run BigQuery ALTER TABLE statements to extend `identity.contact_identifiers`
- [ ] Run Supabase ALTER TABLE statements to extend `contacts_master`
- [ ] Run Supabase ALTER TABLE statements to extend `contact_identifiers`
- [ ] Verify all new columns exist
- [ ] Backfill `canonical_name` from `full_name` where missing

**Verification**:
```sql
-- BigQuery
SELECT 
  contact_id,
  canonical_name,
  sync_metadata,
  llm_context
FROM `identity.contacts_master`
LIMIT 1;

-- Supabase
SELECT 
  contact_id,
  canonical_name,
  sync_metadata,
  llm_context
FROM contacts_master
LIMIT 1;
```

### Step 2: Create Businesses Tables

**File**: `businesses_migration.sql`

**Actions**:
- [ ] Create `identity.businesses_master` in BigQuery
- [ ] Create `businesses_master` in Supabase
- [ ] Create `identity.people_business_relationships` in BigQuery
- [ ] Create `people_business_relationships` in Supabase
- [ ] Create `identity.sync_errors_log` in BigQuery
- [ ] Verify all tables created successfully

**Verification**:
```sql
-- BigQuery
SELECT COUNT(*) FROM `identity.businesses_master`;
SELECT COUNT(*) FROM `identity.people_business_relationships`;

-- Supabase
SELECT COUNT(*) FROM businesses_master;
SELECT COUNT(*) FROM people_business_relationships;
```

### Step 3: Create People Relationships Tables

**File**: `people_relationships_migration.sql`

**Actions**:
- [ ] Create `identity.people_relationships` in BigQuery
- [ ] Create `people_relationships` in Supabase
- [ ] Verify all indexes created
- [ ] Test relationship queries

**Verification**:
```sql
-- BigQuery
SELECT COUNT(*) FROM `identity.people_relationships`;

-- Supabase
SELECT COUNT(*) FROM people_relationships;
```

---

## Code Updates Required

### ✅ Sync Services

- [x] `BigQuerySyncService` - Updated to use existing `identity.contacts_master` structure
- [x] `SupabaseSyncService` - Updated to align with existing Supabase schema
- [x] `BusinessSyncService` - Created for businesses
- [x] `PeopleRelationshipSyncService` - Created for people relationships
- [x] `RelationshipSyncService` - Created for people-business relationships
- [x] `ErrorReporter` - Created for transparent error tracking

### ✅ Transform Functions

- [x] Updated to use existing field names (`full_name`, `apple_unique_id`, etc.)
- [x] Handle missing `canonical_name` (derive from `full_name`)
- [x] Preserve all existing fields from `identity.contacts_master`

---

## Testing Checklist

### Contacts Sync

- [ ] Test sync from BigQuery → Supabase
- [ ] Test sync from Supabase → BigQuery
- [ ] Test sync from BigQuery → Local DB
- [ ] Test sync from BigQuery → CRM Twenty
- [ ] Verify all existing fields preserved
- [ ] Verify new sync metadata fields populated

### Businesses Sync

- [ ] Test create business in BigQuery
- [ ] Test sync business to all systems
- [ ] Test update business in CRM Twenty → propagate
- [ ] Verify error tracking works

### People Relationships Sync

- [ ] Test create relationship in BigQuery
- [ ] Test sync relationship to all systems
- [ ] Test social graph queries
- [ ] Test mutual connections query
- [ ] Verify relationship evolution tracking

### Error Tracking

- [ ] Test error reporting on sync failure
- [ ] Verify errors stored in `sync_errors` arrays
- [ ] Verify errors logged to `sync_errors_log`
- [ ] Test error alerting to Jeremy
- [ ] Verify no errors are hidden

---

## Data Migration

### From Existing Contacts

- [ ] Extract businesses from `identity.contacts_master` where `is_business = TRUE`
- [ ] Create businesses in `identity.businesses_master`
- [ ] Create people-business relationships
- [ ] Extract people relationships from category codes
- [ ] Create people-people relationships

### Backfill Sync Metadata

- [ ] Set initial `sync_metadata` for all existing contacts
- [ ] Set `version = 1` for all existing records
- [ ] Set `sync_status = 'synced'` for all existing records
- [ ] Set `source_systems = ['bigquery']` for all existing records

---

## Verification Queries

### Check Alignment

```sql
-- Verify contacts_master has all required fields
SELECT 
  contact_id,
  apple_unique_id,
  full_name,
  canonical_name,
  category_code,
  sync_metadata,
  llm_context
FROM `identity.contacts_master`
LIMIT 5;

-- Verify businesses table exists
SELECT COUNT(*) as business_count
FROM `identity.businesses_master`;

-- Verify people relationships table exists
SELECT COUNT(*) as relationship_count
FROM `identity.people_relationships`;

-- Verify sync errors log exists
SELECT COUNT(*) as error_count
FROM `identity.sync_errors_log`
WHERE resolved = FALSE;
```

---

## Known Alignments

### ✅ Contacts
- Uses existing `identity.contacts_master` structure
- Preserves all Apple Contacts fields
- Extends with sync metadata + LLM fields

### ✅ Identifiers
- Uses existing `identity.contact_identifiers` structure
- Extends with sync metadata

### ✅ Businesses
- New table (not duplicating contacts)
- Links to contacts via relationships table

### ✅ People Relationships
- New table (not duplicating RelationshipService)
- Different purpose: social graph vs organism partnerships

---

## No Duplication ✅

- ✅ No duplicate contacts_master
- ✅ No duplicate contact_identifiers
- ✅ No conflict with RelationshipService
- ✅ All new tables serve distinct purposes
- ✅ All extensions align with existing structure

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Ready for Implementation
