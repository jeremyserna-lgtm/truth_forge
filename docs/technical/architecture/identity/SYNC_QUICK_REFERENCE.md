# Multi-Source Contact Sync - Quick Reference

**Version**: 1.0.0
**Date**: 2026-01-27

---

## Architecture Overview

```
BigQuery (Canonical) ←─── All changes flow through here first
    │
    ├──→ Supabase (Application DB)
    ├──→ Local DB (SQLite/Postgres)
    └──→ CRM Twenty (Visibility Layer)
```

**Key Rule**: BigQuery is canonical. All changes flow through BigQuery first, then propagate.

---

## Sync Services

### 1. BigQuerySyncService
**Purpose**: Sync from BigQuery to all systems

```python
from truth_forge.services.sync import BigQuerySyncService

# Sync single contact
service = BigQuerySyncService(bq_client, supabase, local_db, crm_twenty)
result = service.sync_contact_to_all("12345")

# Sync all modified contacts
result = service.sync_all_contacts(last_sync_time=datetime.now() - timedelta(hours=24))
```

### 2. SupabaseSyncService
**Purpose**: Sync from Supabase to BigQuery (then propagate)

```python
from truth_forge.services.sync import SupabaseSyncService

service = SupabaseSyncService(supabase, bq_client, bq_sync)
result = service.sync_from_supabase_to_bigquery("uuid-here")
```

### 3. CRMTwentySyncService
**Purpose**: Sync from CRM Twenty to BigQuery (then propagate)

```python
from truth_forge.services.sync import CRMTwentySyncService

service = CRMTwentySyncService(crm_client, bq_client, bq_sync)
result = service.sync_from_crm_to_bigquery("crm-id-here")
```

### 4. ConflictResolver
**Purpose**: Resolve conflicts between records

```python
from truth_forge.services.sync import ConflictResolver

resolver = ConflictResolver(bq_client)
result = resolver.resolve_conflict(source_record, target_record)
# Returns: {'winner': 'source'|'target'|None, 'reason': '...'}
```

### 5. AlignmentValidator
**Purpose**: Validate alignment across systems

```python
from truth_forge.services.sync import AlignmentValidator

validator = AlignmentValidator()
result = validator.validate_contact(contact)
result = validator.compare_contacts(contact1, contact2)
```

---

## LLM Prompting

### ContactPromptBuilder
**Purpose**: Build LLM prompts from contact data

```python
from truth_forge.services.llm import ContactPromptBuilder

builder = ContactPromptBuilder(contact_fetcher)

# Build context for single contact
context = builder.build_contact_context(contact)

# Build full prompt with contact
prompt = builder.build_prompt_with_contact(
    base_prompt="You are talking to...",
    contact_id="12345",
    source="bigquery"
)

# Build context for multiple contacts
context = builder.build_multi_contact_context(
    contact_ids=["12345", "67890"],
    source="bigquery"
)
```

---

## Canonical Data Model

### Required Fields
- `contact_id`: Stable ID across all systems
- `canonical_name`: Primary display name
- `sync_metadata.version`: Incremental version
- `sync_metadata.last_updated`: ISO timestamp
- `sync_metadata.last_updated_by`: System name

### Category Codes
- **A**: Family
- **B**: Friends
- **C**: Acquaintances
- **D**: Dating/Romantic
- **E**: Ex-Romantic
- **F**: Service Providers
- **G**: Professional/Coworkers
- **H**: Hostile
- **X**: Exclude

### Rich LLM Data Structure

```typescript
llm_context: {
  relationship_arc?: string;
  communication_style?: string;
  key_interests?: string[];
  personality_notes?: string;
  important_dates?: Array<{date, event, significance}>;
  conversation_topics?: string[];
  emotional_depth?: number;  // 1-10
  closeness_level?: number;  // 1-10
  how_met?: string;
  current_state?: string;
  blind_spots?: string[];
  strengths?: string[];
  tensions?: string[];
}
```

---

## Sync Flow

### Change in BigQuery
1. Update contact in BigQuery
2. `BigQuerySyncService.sync_contact_to_all()` → propagates to all

### Change in CRM Twenty
1. Update contact in CRM Twenty
2. `CRMTwentySyncService.sync_from_crm_to_bigquery()` → updates BigQuery
3. `BigQuerySyncService.sync_contact_to_all()` → propagates to all

### Change in Supabase
1. Update contact in Supabase
2. `SupabaseSyncService.sync_from_supabase_to_bigquery()` → updates BigQuery
3. `BigQuerySyncService.sync_contact_to_all()` → propagates to all

### Change in Local DB
1. Update contact in Local DB
2. `LocalSyncService.sync_from_local_to_bigquery()` → updates BigQuery
3. `BigQuerySyncService.sync_contact_to_all()` → propagates to all

---

## Conflict Resolution

**Strategy**: Last-Write-Wins with Version Control

1. Compare `version` (higher wins)
2. If equal, compare `last_updated` (later wins)
3. If both equal, store in `sync_conflicts` for manual resolution

---

## Validation Rules

### Required Fields
- `contact_id`
- `canonical_name`
- `sync_metadata.version`

### Type Mappings
- BigQuery `INT64` → Supabase `TEXT`
- BigQuery `STRING` → Supabase `TEXT`
- BigQuery `JSON` → Supabase `JSONB`
- BigQuery `TIMESTAMP` → Supabase `TIMESTAMPTZ`

### Category Validation
- `category_code` must be A-H or X
- `subcategory_code` must start with `category_code`

---

## Monitoring

### Sync Health
- Last successful sync per system
- Pending syncs count
- Conflict count
- Sync errors
- Data drift percentage

### Alerts
- Sync failure (any system)
- Conflict detected
- Data drift > 5%
- Sync latency > 5 minutes

---

## Common Patterns

### Sync on Webhook
```python
@app.post("/webhook/crm-twenty")
def crm_webhook(contact_id: str):
    crm_sync = CRMTwentySyncService(...)
    result = crm_sync.sync_from_crm_to_bigquery(contact_id)
    return result
```

### Scheduled Sync
```python
@schedule.every(5).minutes
def sync_all_systems():
    bq_sync = BigQuerySyncService(...)
    result = bq_sync.sync_all_contacts()
    logger.info(f"Synced {result['synced']} contacts")
```

### LLM Prompt with Contact
```python
builder = ContactPromptBuilder(contact_fetcher)
prompt = builder.build_prompt_with_contact(
    base_prompt="You are talking to a contact...",
    contact_id=contact_id,
    source="bigquery"
)
response = llm_client.complete(prompt)
```

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
