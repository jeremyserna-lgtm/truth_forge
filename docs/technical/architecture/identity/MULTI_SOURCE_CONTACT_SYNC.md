# Multi-Source Contact Sync Architecture

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Design - Ready for Implementation
**Owner**: Jeremy Serna

---

## Executive Summary

This architecture provides **complete alignment** across four contact data sources:
1. **BigQuery** (Canonical Source) - `identity.contacts_master` & `identity.contact_identifiers`
2. **Supabase** (Application Database) - `contacts_master` & `contact_identifiers`
3. **Local Database** (SQLite/Postgres) - Local contact tables
4. **CRM Twenty** (Visibility Layer) - Read/write with full propagation

**Extended to include**:
- **Businesses** - Separate businesses table with full sync support
- **People-Business Relationships** - Many-to-many relationships with tracking
- **Complete Transparency** - All errors reported, nothing hidden

**Key Principles**:
- **BigQuery is canonical** - All changes flow through BigQuery first
- **CRM Twenty is visibility layer** - Changes in CRM propagate to all sources
- **Bidirectional sync** - Changes anywhere propagate everywhere
- **Conflict resolution** - Last-write-wins with timestamp-based resolution
- **Rich LLM data** - Structured data optimized for dynamic prompting
- **Complete transparency** - All errors, issues, and problems are reported
- **Free linking** - People can link to businesses freely through relationships

---

## Canonical Data Model

### Core Contact Schema (Universal)

This schema works across all four systems with type mappings:

```typescript
interface CanonicalContact {
  // Primary Identifiers
  contact_id: string | number;              // Stable ID across all systems
  canonical_name: string;                   // Primary display name
  name_normalized: string;                  // For searching/matching
  
  // Name Components
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  nickname?: string;
  name_suffix?: string;
  title?: string;
  full_name?: string;
  
  // Organization
  organization?: string;
  job_title?: string;
  department?: string;
  is_business: boolean;
  
  // Relationship Categorization (Your System)
  category_code?: 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'X';
  subcategory_code?: string;                // e.g., "A1_IMMEDIATE_FAMILY_RAISED_TOGETHER"
  relationship_category?: string;           // family, friend, romantic, etc.
  
  // Rich LLM Data
  llm_context: {
    relationship_arc?: string;              // Narrative relationship history
    communication_style?: string;           // How they communicate
    key_interests?: string[];               // Topics they care about
    personality_notes?: string;             // Your observations
    important_dates?: Array<{               // Significant dates
      date: string;
      event: string;
      significance: string;
    }>;
    conversation_topics?: string[];          // Common topics
    emotional_depth?: number;               // 1-10 scale
    closeness_level?: number;              // 1-10 scale
    how_met?: string;                       // How you met
    current_state?: string;                 // Current relationship status
    blind_spots?: string[];                 // Things you might not see
    strengths?: string[];                    // Relationship strengths
    tensions?: string[];                    // Known friction points
  };
  
  // Communication Stats
  communication_stats?: {
    total_messages?: number;
    messages_per_year?: number;
    last_contact_date?: string;
    avg_response_time_hours?: number;
    you_initiate_pct?: number;
    relationship_health?: string;
  };
  
  // Social Network
  social_network?: {
    groups?: string[];
    also_knows?: string[];
    introduced_you_to?: string[];
  };
  
  // AI Insights
  ai_insights?: {
    mentioned_in_conversations?: number;
    primary_topics?: string[];
    sentiment_when_discussed?: number;
    user_concerns?: string[];
  };
  
  // Recommendations
  recommendations?: {
    contact_cadence?: string;
    conversation_topics?: string[];
    boundary_notes?: string;
  };
  
  // Metadata
  notes?: string;
  birthday?: string;
  is_me: boolean;
  
  // Sync Metadata
  sync_metadata: {
    last_updated: string;                   // ISO timestamp
    last_updated_by: string;                // System that made change
    version: number;                        // Incremental version
    sync_status: 'synced' | 'pending' | 'conflict';
    source_systems: string[];                // Which systems have this contact
  };
  
  // Timestamps
  created_at: string;
  updated_at: string;
  first_seen?: string;
  last_seen?: string;
}
```

### Contact Identifiers Schema

```typescript
interface CanonicalContactIdentifier {
  identifier_id: string;
  contact_id: string | number;
  
  identifier_type: 'phone' | 'email' | 'social_profile' | 'platform_id';
  identifier_value: string;
  identifier_normalized: string;
  
  source_platform?: string;                 // apple_contacts, sms, grindr, etc.
  source_label?: string;                    // Mobile, Work, Home, etc.
  
  // Phone Components
  country_code?: string;
  area_code?: string;
  local_number?: string;
  
  // Email Components
  email_domain?: string;
  
  // Social Profile
  social_service?: string;
  social_username?: string;
  social_url?: string;
  
  // Flags
  is_primary: boolean;
  is_private: boolean;
  is_verified: boolean;
  
  // Metadata
  confidence: number;                        // 0.0-1.0
  verification_status?: string;
  
  // Sync Metadata
  sync_metadata: {
    last_updated: string;
    last_updated_by: string;
    version: number;
  };
  
  // Timestamps
  created_at: string;
  updated_at: string;
  first_seen?: string;
  last_seen?: string;
}
```

---

## System-Specific Mappings

### BigQuery Schema

**IMPORTANT**: `identity.contacts_master` already exists. We EXTEND it, not recreate it.

**Existing Schema** (from IDENTITY_LAYER_FOUNDATION.md):
```sql
-- identity.contacts_master (EXISTS - DO NOT RECREATE)
-- See: docs/technical/architecture/identity/IDENTITY_LAYER_FOUNDATION.md
-- 
-- Key existing fields:
-- - contact_id, apple_unique_id, apple_identity_unique_id, apple_link_id
-- - first_name, last_name, middle_name, nickname, name_suffix, title, full_name
-- - name_normalized, sorting_first_name, sorting_last_name
-- - organization, job_title, department
-- - category_code, subcategory_code, relationship_category
-- - notes, birthday, is_business, is_me
-- - created_at, updated_at, first_seen_in_primitive_engine, last_seen_in_primitive_engine
-- - primitive_engine_entity_id, resolution_confidence
```

**Extensions to Add** (via ALTER TABLE):
```sql
-- Add sync metadata
ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS sync_metadata STRUCT<
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64,
  sync_status STRING,
  source_systems ARRAY<STRING>,
  sync_errors ARRAY<STRUCT<...>>
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

-- Add canonical_name if missing
ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS canonical_name STRING;
```

**See**: `EXTEND_EXISTING_TABLES.sql` for full migration script.

### Supabase Schema

**IMPORTANT**: `contacts_master` already exists in `supabase_migration.sql`. We EXTEND it.

**Existing Schema** (from supabase_migration.sql):
```sql
-- contacts_master (EXISTS - DO NOT RECREATE)
-- See: docs/technical/architecture/identity/supabase_migration.sql
```

**Extensions to Add** (via ALTER TABLE):
```sql
-- Add sync metadata and LLM fields
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS sync_metadata JSONB DEFAULT '{}';
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS llm_context JSONB DEFAULT '{}';
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS communication_stats JSONB DEFAULT '{}';
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS social_network JSONB DEFAULT '{}';
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS ai_insights JSONB DEFAULT '{}';
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS recommendations JSONB DEFAULT '{}';
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS canonical_name TEXT;
```

**See**: `EXTEND_EXISTING_TABLES.sql` for full migration script.

### Local Database Schema (SQLite/Postgres)

```sql
-- contacts_master (Local)
CREATE TABLE contacts_master (
  id SERIAL PRIMARY KEY,
  contact_id TEXT NOT NULL UNIQUE,
  
  canonical_name TEXT NOT NULL,
  name_normalized TEXT,
  
  -- ... (same structure as Supabase)
  
  -- Rich LLM Data (JSON)
  llm_context JSONB,
  communication_stats JSONB,
  social_network JSONB,
  ai_insights JSONB,
  recommendations JSONB,
  
  -- Sync Metadata
  last_updated TIMESTAMP,
  last_updated_by TEXT,
  version INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  source_systems TEXT[],
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### CRM Twenty Schema

CRM Twenty uses its own schema, but we map to it:

```typescript
interface TwentyCRMContact {
  id: string;                               // Twenty CRM ID
  name: string;                              // Maps to canonical_name
  email?: string;                            // Primary email
  phone?: string;                            // Primary phone
  
  // Custom Fields (Twenty CRM supports custom fields)
  customFields: {
    contact_id: string;                      // Our canonical ID
    category_code?: string;
    subcategory_code?: string;
    relationship_category?: string;
    llm_context?: string;                    // JSON string
    communication_stats?: string;           // JSON string
    social_network?: string;                 // JSON string
    ai_insights?: string;                    // JSON string
    recommendations?: string;              // JSON string
    sync_metadata?: string;                  // JSON string
  };
  
  // Twenty CRM native fields
  company?: { id: string; name: string };
  tags?: string[];
  notes?: string;
  
  // Sync Metadata
  updatedAt: string;
  createdAt: string;
}
```

---

## Sync Architecture

### Sync Flow Diagram

```
┌─────────────┐
│  BigQuery   │ ←─── CANONICAL SOURCE
│ (Canonical) │
└──────┬──────┘
       │
       ├─────────────────────────────────┐
       │                                 │
       ▼                                 ▼
┌─────────────┐                  ┌─────────────┐
│  Supabase   │                  │   Local DB  │
│ (App DB)    │                  │  (SQLite)   │
└──────┬──────┘                  └──────┬──────┘
       │                                 │
       │                                 │
       └─────────────┬──────────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ CRM Twenty  │
              │ (Visibility)│
              └─────────────┘
```

### Sync Direction Rules

1. **BigQuery → All**: Changes in BigQuery propagate to all systems
2. **CRM Twenty → BigQuery → All**: Changes in CRM flow to BigQuery first, then all
3. **Supabase → BigQuery → All**: Changes in Supabase flow to BigQuery first, then all
4. **Local → BigQuery → All**: Changes in Local flow to BigQuery first, then all

### Conflict Resolution Strategy

**Last-Write-Wins with Version Control**:

1. Each record has `version` (incremental) and `last_updated` (timestamp)
2. On conflict, compare:
   - If `version` differs: Higher version wins
   - If `version` same: Later `last_updated` wins
   - If both same: Manual resolution required
3. Winning record propagates to all systems
4. Losing record stored in `sync_conflicts` table for review

---

## Sync Services

### 1. BigQuery Sync Service

**Purpose**: Sync from BigQuery to all other systems

```python
# src/truth_forge/services/sync/bigquery_sync.py

from typing import List, Dict, Any
from google.cloud import bigquery
from supabase import create_client
import sqlite3

class BigQuerySyncService:
    """Syncs contacts from BigQuery (canonical) to all other systems."""
    
    def __init__(self):
        self.bq_client = bigquery.Client()
        self.supabase = create_client(...)
        self.local_db = sqlite3.connect('local_contacts.db')
    
    def sync_contact_to_all(self, contact_id: str) -> Dict[str, Any]:
        """Sync a single contact from BigQuery to all systems."""
        # 1. Fetch from BigQuery
        contact = self._fetch_from_bigquery(contact_id)
        
        # 2. Sync to Supabase
        supabase_result = self._sync_to_supabase(contact)
        
        # 3. Sync to Local
        local_result = self._sync_to_local(contact)
        
        # 4. Sync to CRM Twenty
        crm_result = self._sync_to_crm_twenty(contact)
        
        return {
            'bigquery': {'status': 'synced', 'version': contact['version']},
            'supabase': supabase_result,
            'local': local_result,
            'crm_twenty': crm_result
        }
    
    def sync_all_contacts(self, batch_size: int = 100) -> Dict[str, Any]:
        """Sync all contacts from BigQuery."""
        # Fetch all contacts modified since last sync
        query = """
        SELECT * FROM `identity.contacts_master`
        WHERE updated_at > @last_sync_time
        ORDER BY updated_at DESC
        LIMIT @batch_size
        """
        
        contacts = self.bq_client.query(query).result()
        
        results = []
        for contact in contacts:
            result = self.sync_contact_to_all(contact['contact_id'])
            results.append(result)
        
        return {'synced': len(results), 'results': results}
```

### 2. CRM Twenty Sync Service

**Purpose**: Sync from CRM Twenty to BigQuery (then propagate)

```python
# src/truth_forge/services/sync/crm_twenty_sync.py

class CRMTwentySyncService:
    """Syncs contacts from CRM Twenty to BigQuery (canonical)."""
    
    def __init__(self):
        self.crm_client = TwentyCRMClient(...)
        self.bq_client = bigquery.Client()
        self.bq_sync = BigQuerySyncService()
    
    def sync_from_crm_to_bigquery(self, crm_contact_id: str) -> Dict[str, Any]:
        """Sync a contact from CRM Twenty to BigQuery."""
        # 1. Fetch from CRM Twenty
        crm_contact = self.crm_client.get_contact(crm_contact_id)
        
        # 2. Transform to canonical format
        canonical_contact = self._transform_crm_to_canonical(crm_contact)
        
        # 3. Upsert to BigQuery (with conflict resolution)
        result = self._upsert_to_bigquery(canonical_contact)
        
        # 4. Trigger propagation to all systems
        if result['status'] == 'synced':
            self.bq_sync.sync_contact_to_all(canonical_contact['contact_id'])
        
        return result
    
    def _transform_crm_to_canonical(self, crm_contact: Dict) -> Dict:
        """Transform CRM Twenty contact to canonical format."""
        return {
            'contact_id': crm_contact['customFields']['contact_id'],
            'canonical_name': crm_contact['name'],
            'category_code': crm_contact['customFields'].get('category_code'),
            'subcategory_code': crm_contact['customFields'].get('subcategory_code'),
            'llm_context': json.loads(crm_contact['customFields'].get('llm_context', '{}')),
            'sync_metadata': {
                'last_updated': crm_contact['updatedAt'],
                'last_updated_by': 'crm_twenty',
                'version': self._get_next_version(crm_contact['customFields']['contact_id']),
                'sync_status': 'synced',
                'source_systems': ['crm_twenty', 'bigquery']
            }
        }
```

### 3. Supabase Sync Service

**Purpose**: Sync from Supabase to BigQuery (then propagate)

```python
# src/truth_forge/services/sync/supabase_sync.py

class SupabaseSyncService:
    """Syncs contacts from Supabase to BigQuery (canonical)."""
    
    def __init__(self):
        self.supabase = create_client(...)
        self.bq_client = bigquery.Client()
        self.bq_sync = BigQuerySyncService()
    
    def sync_from_supabase_to_bigquery(self, supabase_contact_id: str) -> Dict[str, Any]:
        """Sync a contact from Supabase to BigQuery."""
        # 1. Fetch from Supabase
        supabase_contact = self.supabase.table('contacts_master').select('*').eq('id', supabase_contact_id).execute()
        
        # 2. Transform to canonical format
        canonical_contact = self._transform_supabase_to_canonical(supabase_contact.data[0])
        
        # 3. Upsert to BigQuery (with conflict resolution)
        result = self._upsert_to_bigquery(canonical_contact)
        
        # 4. Trigger propagation
        if result['status'] == 'synced':
            self.bq_sync.sync_contact_to_all(canonical_contact['contact_id'])
        
        return result
```

### 4. Local Database Sync Service

**Purpose**: Sync from Local DB to BigQuery (then propagate)

```python
# src/truth_forge/services/sync/local_sync.py

class LocalSyncService:
    """Syncs contacts from Local DB to BigQuery (canonical)."""
    
    def __init__(self):
        self.local_db = sqlite3.connect('local_contacts.db')
        self.bq_client = bigquery.Client()
        self.bq_sync = BigQuerySyncService()
    
    def sync_from_local_to_bigquery(self, local_contact_id: str) -> Dict[str, Any]:
        """Sync a contact from Local DB to BigQuery."""
        # 1. Fetch from Local
        local_contact = self._fetch_from_local(local_contact_id)
        
        # 2. Transform to canonical format
        canonical_contact = self._transform_local_to_canonical(local_contact)
        
        # 3. Upsert to BigQuery
        result = self._upsert_to_bigquery(canonical_contact)
        
        # 4. Trigger propagation
        if result['status'] == 'synced':
            self.bq_sync.sync_contact_to_all(canonical_contact['contact_id'])
        
        return result
```

---

## Conflict Resolution Service

```python
# src/truth_forge/services/sync/conflict_resolver.py

class ConflictResolver:
    """Resolves conflicts between contact records."""
    
    def resolve_conflict(self, source_record: Dict, target_record: Dict) -> Dict[str, Any]:
        """Resolve conflict between two records."""
        
        # Compare versions
        if source_record['sync_metadata']['version'] > target_record['sync_metadata']['version']:
            return {'winner': 'source', 'reason': 'higher_version'}
        
        if source_record['sync_metadata']['version'] < target_record['sync_metadata']['version']:
            return {'winner': 'target', 'reason': 'higher_version'}
        
        # Versions equal, compare timestamps
        source_time = datetime.fromisoformat(source_record['sync_metadata']['last_updated'])
        target_time = datetime.fromisoformat(target_record['sync_metadata']['last_updated'])
        
        if source_time > target_time:
            return {'winner': 'source', 'reason': 'later_timestamp'}
        
        if source_time < target_time:
            return {'winner': 'target', 'reason': 'later_timestamp'}
        
        # Same version and timestamp - manual resolution needed
        return {
            'winner': None,
            'reason': 'manual_resolution_required',
            'conflict_id': self._store_conflict(source_record, target_record)
        }
    
    def _store_conflict(self, source: Dict, target: Dict) -> str:
        """Store conflict for manual resolution."""
        conflict_id = str(uuid.uuid4())
        
        # Store in BigQuery conflicts table
        self.bq_client.insert_rows_json('identity.sync_conflicts', [{
            'conflict_id': conflict_id,
            'source_record': source,
            'target_record': target,
            'created_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }])
        
        return conflict_id
```

---

## Alignment Standard

### Data Validation Rules

1. **Required Fields**:
   - `contact_id` (must be stable across all systems)
   - `canonical_name` (must match across all systems)
   - `sync_metadata.version` (must increment on each change)

2. **Type Mappings**:
   - BigQuery: `INT64` → Supabase: `TEXT` (store as string)
   - BigQuery: `STRING` → Supabase: `TEXT`
   - BigQuery: `JSON` → Supabase: `JSONB`
   - BigQuery: `TIMESTAMP` → Supabase: `TIMESTAMPTZ`

3. **Normalization Rules**:
   - `name_normalized`: Lowercase, remove special chars, trim
   - `identifier_normalized`: Lowercase, remove formatting (phones/emails)

4. **Category/Subcategory Validation**:
   - `category_code` must be one of: A, B, C, D, E, F, G, H, X
   - `subcategory_code` must match pattern: `{category_code}{number}_{DESCRIPTION}`

### Sync Validation

Before syncing, validate:
1. Required fields present
2. Types match expected format
3. Category/subcategory valid
4. Version increments correctly
5. Timestamps valid ISO format

---

## LLM Prompting Integration

### Dynamic Prompt Builder

```python
# src/truth_forge/services/llm/contact_prompt_builder.py

class ContactPromptBuilder:
    """Builds LLM prompts from contact data."""
    
    def build_contact_context(self, contact: Dict) -> str:
        """Build rich context string for LLM prompts."""
        
        parts = []
        
        # Basic Info
        parts.append(f"**Contact**: {contact['canonical_name']}")
        if contact.get('organization'):
            parts.append(f"**Organization**: {contact['organization']}")
        
        # Relationship Context
        if contact.get('category_code'):
            parts.append(f"**Category**: {contact['category_code']} ({contact.get('relationship_category', 'unknown')})")
        if contact.get('subcategory_code'):
            parts.append(f"**Subcategory**: {contact['subcategory_code']}")
        
        # LLM Context
        llm_ctx = contact.get('llm_context', {})
        if llm_ctx.get('relationship_arc'):
            parts.append(f"**Relationship Arc**: {llm_ctx['relationship_arc']}")
        if llm_ctx.get('communication_style'):
            parts.append(f"**Communication Style**: {llm_ctx['communication_style']}")
        if llm_ctx.get('key_interests'):
            parts.append(f"**Interests**: {', '.join(llm_ctx['key_interests'])}")
        if llm_ctx.get('current_state'):
            parts.append(f"**Current State**: {llm_ctx['current_state']}")
        
        # Communication Stats
        comm_stats = contact.get('communication_stats', {})
        if comm_stats.get('last_contact_date'):
            parts.append(f"**Last Contact**: {comm_stats['last_contact_date']}")
        if comm_stats.get('relationship_health'):
            parts.append(f"**Relationship Health**: {comm_stats['relationship_health']}")
        
        # AI Insights
        ai_insights = contact.get('ai_insights', {})
        if ai_insights.get('primary_topics'):
            parts.append(f"**Common Topics**: {', '.join(ai_insights['primary_topics'])}")
        
        # Recommendations
        recommendations = contact.get('recommendations', {})
        if recommendations.get('conversation_topics'):
            parts.append(f"**Suggested Topics**: {', '.join(recommendations['conversation_topics'])}")
        
        return "\n".join(parts)
    
    def build_prompt_with_contact(self, base_prompt: str, contact_id: str) -> str:
        """Build full prompt with contact context."""
        contact = self._fetch_contact(contact_id)
        contact_context = self.build_contact_context(contact)
        
        return f"""{base_prompt}

## Contact Context
{contact_context}
"""
```

---

## Implementation Plan

### Phase 1: Foundation (Week 1)
1. Create canonical schema in BigQuery
2. Create sync metadata fields in all systems
3. Implement conflict resolution service
4. Create validation service

### Phase 2: BigQuery → All (Week 2)
1. Implement BigQuery sync service
2. Sync to Supabase
3. Sync to Local DB
4. Sync to CRM Twenty

### Phase 3: All → BigQuery (Week 3)
1. Implement CRM Twenty sync service
2. Implement Supabase sync service
3. Implement Local DB sync service
4. Test bidirectional sync

### Phase 4: Automation (Week 4)
1. Set up scheduled sync jobs
2. Implement webhook triggers
3. Create monitoring dashboard
4. Add alerting

### Phase 5: LLM Integration (Week 5)
1. Implement prompt builder
2. Integrate with dynamic prompting system
3. Test with LLM calls
4. Optimize prompt structure

---

## Monitoring & Alerts

### Sync Health Dashboard

Track:
- Last successful sync per system
- Pending syncs count
- Conflict count
- Sync errors
- Data drift (differences between systems)

### Alerts

- Sync failure (any system)
- Conflict detected (requires manual resolution)
- Data drift detected (> 5% difference)
- Sync latency (> 5 minutes)

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Design Complete - Ready for Implementation
