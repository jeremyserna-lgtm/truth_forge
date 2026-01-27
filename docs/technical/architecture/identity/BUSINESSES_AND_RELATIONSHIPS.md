# Businesses and People-Business Relationships

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Design - Ready for Implementation
**Owner**: Jeremy Serna

---

## Executive Summary

This architecture adds **complete businesses support** with:
1. **Businesses table** - Separate table for business entities
2. **People-Business relationships** - Many-to-many relationships with full tracking
3. **Complete transparency** - All issues, problems, and errors are reported
4. **Full sync support** - Businesses sync across all systems
5. **Rich business data** - LLM-ready business context

**Key Principles**:
- **Nothing hidden** - All issues must be reported
- **Complete fidelity** - Full tracking of all relationships
- **Free linking** - People can link to businesses freely
- **Transparent errors** - All problems surfaced immediately

---

## Business Schema

### Canonical Business Model

```typescript
interface CanonicalBusiness {
  // Primary Identifiers
  business_id: string | number;            // Stable ID across all systems
  business_name: string;                    // Primary business name
  name_normalized: string;                   // For searching/matching
  
  // Business Information
  legal_name?: string;                      // Legal/registered name
  dba_name?: string;                        // "Doing Business As" name
  industry?: string;                         // Industry classification
  business_type?: string;                    // LLC, Corp, Partnership, etc.
  
  // Contact Information
  primary_phone?: string;
  primary_email?: string;
  website?: string;
  
  // Address
  address?: {
    street?: string;
    city?: string;
    state?: string;
    zip?: string;
    country?: string;
  };
  
  // Business Data
  business_data: {
    founded_year?: number;
    employee_count?: number;
    revenue_range?: string;                  // e.g., "$1M-$10M"
    description?: string;
    services?: string[];                     // Services offered
    products?: string[];                     // Products offered
    key_people?: string[];                   // Key personnel names
    competitors?: string[];                  // Competitor names
    partners?: string[];                     // Partner company names
  };
  
  // LLM Context (for dynamic prompting)
  llm_context: {
    business_relationship_arc?: string;     // Narrative history
    how_met?: string;                       // How you met/learned about
    current_state?: string;                 // Current relationship status
    business_notes?: string;                 // Your observations
    opportunities?: string[];                // Business opportunities
    concerns?: string[];                     // Concerns or issues
    strengths?: string[];                    // Business strengths
    weaknesses?: string[];                   // Business weaknesses
    strategic_value?: string;                // Strategic value to you
  };
  
  // Relationship Stats
  relationship_stats?: {
    total_people_linked?: number;          // Number of people linked
    total_interactions?: number;            // Total interactions
    last_interaction_date?: string;        // Last interaction
    relationship_health?: string;           // Health status
  };
  
  // Metadata
  notes?: string;
  tags?: string[];                          // Tags for categorization
  
  // Sync Metadata
  sync_metadata: {
    last_updated: string;                   // ISO timestamp
    last_updated_by: string;                // System that made change
    version: number;                        // Incremental version
    sync_status: 'synced' | 'pending' | 'conflict' | 'error';
    source_systems: string[];              // Which systems have this business
    sync_errors?: Array<{                   // **TRANSPARENT ERROR TRACKING**
      timestamp: string;
      system: string;
      error_type: string;
      error_message: string;
      error_details?: any;
      resolved: boolean;
    }>;
  };
  
  // Timestamps
  created_at: string;
  updated_at: string;
  first_seen?: string;
  last_seen?: string;
}
```

---

## People-Business Relationships

### Relationship Schema

```typescript
interface PeopleBusinessRelationship {
  // Primary Identifiers
  relationship_id: string | number;         // Unique relationship ID
  contact_id: string | number;              // FK to contacts_master
  business_id: string | number;             // FK to businesses_master
  
  // Relationship Details
  relationship_type: string;                // employee, owner, founder, client, vendor, partner, etc.
  role?: string;                            // Job title/role at business
  department?: string;                      // Department within business
  start_date?: string;                      // When relationship started
  end_date?: string;                        // When relationship ended (if applicable)
  is_current: boolean;                      // Is this an active relationship
  
  // Relationship Context
  relationship_context: {
    how_met?: string;                       // How they met through business
    relationship_arc?: string;              // Narrative history
    current_state?: string;                 // Current state
    notes?: string;                         // Relationship notes
    importance?: number;                     // 1-10 importance scale
    trust_level?: number;                   // 1-10 trust level
  };
  
  // Tracking Data
  tracking: {
    interaction_count?: number;            // Number of interactions
    last_interaction_date?: string;        // Last interaction
    interaction_topics?: string[];         // Common topics
    communication_channels?: string[];     // How you communicate
  };
  
  // Sync Metadata
  sync_metadata: {
    last_updated: string;
    last_updated_by: string;
    version: number;
    sync_status: 'synced' | 'pending' | 'conflict' | 'error';
    sync_errors?: Array<{                   // **TRANSPARENT ERROR TRACKING**
      timestamp: string;
      system: string;
      error_type: string;
      error_message: string;
      error_details?: any;
      resolved: boolean;
    }>;
  };
  
  // Timestamps
  created_at: string;
  updated_at: string;
}
```

---

## Database Schemas

### BigQuery: `identity.businesses_master`

```sql
CREATE TABLE `identity.businesses_master` (
  -- Primary Identifiers
  business_id INT64 NOT NULL,
  business_name STRING NOT NULL,
  name_normalized STRING,
  
  -- Business Information
  legal_name STRING,
  dba_name STRING,
  industry STRING,
  business_type STRING,
  
  -- Contact Information
  primary_phone STRING,
  primary_email STRING,
  website STRING,
  
  -- Address (JSON)
  address JSON,
  
  -- Business Data (JSON)
  business_data JSON,
  
  -- LLM Context (JSON)
  llm_context JSON,
  
  -- Relationship Stats (JSON)
  relationship_stats JSON,
  
  -- Metadata
  notes STRING,
  tags ARRAY<STRING>,
  
  -- Sync Metadata
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64 DEFAULT 1,
  sync_status STRING DEFAULT 'synced',
  source_systems ARRAY<STRING>,
  sync_errors ARRAY<STRUCT<              -- **ERROR TRACKING**
    timestamp TIMESTAMP,
    system STRING,
    error_type STRING,
    error_message STRING,
    error_details JSON,
    resolved BOOL
  >>,
  
  -- Timestamps
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  first_seen TIMESTAMP,
  last_seen TIMESTAMP,
  
  PRIMARY KEY (business_id),
  INDEX (name_normalized),
  INDEX (sync_status)
);
```

### BigQuery: `identity.people_business_relationships`

```sql
CREATE TABLE `identity.people_business_relationships` (
  -- Primary Identifiers
  relationship_id INT64 NOT NULL,
  contact_id INT64 NOT NULL,               -- FK to contacts_master
  business_id INT64 NOT NULL,              -- FK to businesses_master
  
  -- Relationship Details
  relationship_type STRING NOT NULL,
  role STRING,
  department STRING,
  start_date DATE,
  end_date DATE,
  is_current BOOL DEFAULT TRUE,
  
  -- Relationship Context (JSON)
  relationship_context JSON,
  
  -- Tracking Data (JSON)
  tracking JSON,
  
  -- Sync Metadata
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64 DEFAULT 1,
  sync_status STRING DEFAULT 'synced',
  sync_errors ARRAY<STRUCT<                -- **ERROR TRACKING**
    timestamp TIMESTAMP,
    system STRING,
    error_type STRING,
    error_message STRING,
    error_details JSON,
    resolved BOOL
  >>,
  
  -- Timestamps
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  
  PRIMARY KEY (relationship_id),
  FOREIGN KEY (contact_id) REFERENCES identity.contacts_master(contact_id),
  FOREIGN KEY (business_id) REFERENCES identity.businesses_master(business_id),
  UNIQUE (contact_id, business_id, relationship_type),
  INDEX (contact_id),
  INDEX (business_id),
  INDEX (is_current)
);
```

### Supabase: `businesses_master`

```sql
CREATE TABLE businesses_master (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id TEXT NOT NULL UNIQUE,        -- Maps to BigQuery business_id
  
  business_name TEXT NOT NULL,
  name_normalized TEXT,
  
  -- Business Information
  legal_name TEXT,
  dba_name TEXT,
  industry TEXT,
  business_type TEXT,
  
  -- Contact Information
  primary_phone TEXT,
  primary_email TEXT,
  website TEXT,
  
  -- Address (JSONB)
  address JSONB DEFAULT '{}',
  
  -- Business Data (JSONB)
  business_data JSONB DEFAULT '{}',
  
  -- LLM Context (JSONB)
  llm_context JSONB DEFAULT '{}',
  
  -- Relationship Stats (JSONB)
  relationship_stats JSONB DEFAULT '{}',
  
  -- Metadata
  notes TEXT,
  tags TEXT[],
  
  -- Sync Metadata
  last_updated TIMESTAMPTZ,
  last_updated_by TEXT,
  version INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  source_systems TEXT[],
  sync_errors JSONB DEFAULT '[]',         -- **ERROR TRACKING**
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  first_seen TIMESTAMPTZ,
  last_seen TIMESTAMPTZ
);

CREATE INDEX idx_businesses_business_id ON businesses_master(business_id);
CREATE INDEX idx_businesses_name_normalized ON businesses_master(name_normalized);
CREATE INDEX idx_businesses_sync_status ON businesses_master(sync_status);
```

### Supabase: `people_business_relationships`

```sql
CREATE TABLE people_business_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  relationship_id TEXT NOT NULL UNIQUE,    -- Maps to BigQuery relationship_id
  
  contact_id TEXT NOT NULL,                -- FK to contacts_master.contact_id
  business_id TEXT NOT NULL,               -- FK to businesses_master.business_id
  
  -- Relationship Details
  relationship_type TEXT NOT NULL,
  role TEXT,
  department TEXT,
  start_date DATE,
  end_date DATE,
  is_current BOOLEAN DEFAULT true,
  
  -- Relationship Context (JSONB)
  relationship_context JSONB DEFAULT '{}',
  
  -- Tracking Data (JSONB)
  tracking JSONB DEFAULT '{}',
  
  -- Sync Metadata
  last_updated TIMESTAMPTZ,
  last_updated_by TEXT,
  version INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  sync_errors JSONB DEFAULT '[]',          -- **ERROR TRACKING**
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE (contact_id, business_id, relationship_type),
  FOREIGN KEY (contact_id) REFERENCES contacts_master(contact_id),
  FOREIGN KEY (business_id) REFERENCES businesses_master(business_id)
);

CREATE INDEX idx_pbr_contact_id ON people_business_relationships(contact_id);
CREATE INDEX idx_pbr_business_id ON people_business_relationships(business_id);
CREATE INDEX idx_pbr_is_current ON people_business_relationships(is_current);
```

---

## Error Tracking & Transparency

### Error Schema

All errors are tracked in `sync_errors` array:

```typescript
interface SyncError {
  timestamp: string;                        // When error occurred
  system: string;                           // Which system (bigquery, supabase, local, crm_twenty)
  error_type: string;                       // Type: 'validation', 'sync', 'conflict', 'network', etc.
  error_message: string;                    // Human-readable error message
  error_details?: any;                      // Full error details (stack trace, etc.)
  resolved: boolean;                        // Has this error been resolved?
}
```

### Error Reporting Service

```python
# src/truth_forge/services/sync/error_reporter.py

class ErrorReporter:
    """Reports all errors transparently - nothing hidden."""
    
    def report_error(
        self,
        entity_type: str,                   # 'business' or 'relationship'
        entity_id: str,
        system: str,
        error_type: str,
        error_message: str,
        error_details: Any = None
    ) -> None:
        """Report an error - ALWAYS called, never hidden."""
        
        error = {
            'timestamp': datetime.utcnow().isoformat(),
            'system': system,
            'error_type': error_type,
            'error_message': error_message,
            'error_details': str(error_details) if error_details else None,
            'resolved': False
        }
        
        # 1. Store in entity's sync_errors array
        self._store_error_in_entity(entity_type, entity_id, error)
        
        # 2. Store in central error log (BigQuery)
        self._store_in_error_log(entity_type, entity_id, error)
        
        # 3. Alert Jeremy (email/Slack/notification)
        self._alert_jeremy(error)
        
        # 4. Log to monitoring system
        logger.error(f"SYNC ERROR: {error_type} in {system} for {entity_type} {entity_id}: {error_message}")
    
    def _alert_jeremy(self, error: Dict) -> None:
        """Alert Jeremy about the error - nothing hidden."""
        # Send email/Slack notification
        # Include full error details
        pass
```

---

## Sync Services Updates

All sync services must:
1. **Handle businesses** - Sync businesses across all systems
2. **Handle relationships** - Sync people-business relationships
3. **Report errors** - Use ErrorReporter for all errors
4. **Never hide issues** - All problems must be reported

### Updated BigQuerySyncService

```python
def sync_business_to_all(self, business_id: str) -> Dict[str, Any]:
    """Sync a business from BigQuery to all systems."""
    try:
        business = self._fetch_business_from_bigquery(business_id)
        if not business:
            self.error_reporter.report_error(
                'business', business_id, 'bigquery',
                'not_found', f'Business {business_id} not found in BigQuery'
            )
            return {'error': 'Business not found'}
        
        # Sync to all systems
        results = {
            'supabase': self._sync_business_to_supabase(business),
            'local': self._sync_business_to_local(business),
            'crm_twenty': self._sync_business_to_crm_twenty(business)
        }
        
        # Check for errors
        for system, result in results.items():
            if result.get('status') == 'error':
                self.error_reporter.report_error(
                    'business', business_id, system,
                    'sync_failed', result.get('error', 'Unknown error'),
                    result
                )
        
        return results
    except Exception as e:
        # **NEVER HIDE ERRORS**
        self.error_reporter.report_error(
            'business', business_id, 'bigquery',
            'exception', str(e), {'traceback': traceback.format_exc()}
        )
        raise
```

---

## Relationship Types

### Standard Relationship Types

- **employee** - Person works at business
- **owner** - Person owns business
- **founder** - Person founded business
- **co_founder** - Person co-founded business
- **client** - Business is a client
- **vendor** - Business is a vendor/supplier
- **partner** - Business partnership
- **investor** - Person invested in business
- **advisor** - Person advises business
- **board_member** - Person on board
- **consultant** - Person consults for business
- **customer** - Person is customer of business
- **competitor** - Business is competitor
- **other** - Other relationship type

---

## LLM Integration

### Business Context Builder

```python
def build_business_context(self, business: Dict) -> str:
    """Build rich context string for LLM prompts."""
    parts = []
    
    parts.append(f"**Business**: {business['business_name']}")
    if business.get('industry'):
        parts.append(f"**Industry**: {business['industry']}")
    
    # LLM Context
    llm_ctx = business.get('llm_context', {})
    if llm_ctx.get('business_relationship_arc'):
        parts.append(f"**Relationship Arc**: {llm_ctx['business_relationship_arc']}")
    if llm_ctx.get('strategic_value'):
        parts.append(f"**Strategic Value**: {llm_ctx['strategic_value']}")
    
    return "\n".join(parts)

def build_relationship_context(self, relationship: Dict) -> str:
    """Build context for people-business relationship."""
    parts = []
    
    parts.append(f"**Relationship Type**: {relationship['relationship_type']}")
    if relationship.get('role'):
        parts.append(f"**Role**: {relationship['role']}")
    if relationship.get('is_current'):
        parts.append(f"**Status**: Current")
    else:
        parts.append(f"**Status**: Ended ({relationship.get('end_date')})")
    
    return "\n".join(parts)
```

---

## Validation Rules

### Business Validation

1. **Required fields**: `business_id`, `business_name`
2. **Name normalization**: Must match pattern
3. **Sync metadata**: Must have version, last_updated, last_updated_by
4. **Error tracking**: All errors must be in sync_errors array

### Relationship Validation

1. **Required fields**: `relationship_id`, `contact_id`, `business_id`, `relationship_type`
2. **Foreign keys**: Must reference valid contact and business
3. **Dates**: `end_date` must be after `start_date` if both present
4. **Uniqueness**: Same person-business-relationship_type combination must be unique

---

## Migration from Existing Data

### Extract Businesses from Contacts

```sql
-- Extract businesses from contacts_master
SELECT DISTINCT
  organization as business_name,
  COUNT(*) as people_count
FROM identity.contacts_master
WHERE organization IS NOT NULL
  AND organization != ''
GROUP BY organization
ORDER BY people_count DESC;
```

### Create Businesses

```python
# For each unique organization in contacts_master:
# 1. Create business in businesses_master
# 2. Create people_business_relationships for each person
```

---

## Monitoring & Alerts

### Error Dashboard

Track:
- Total errors by system
- Unresolved errors
- Error types distribution
- Recent errors (last 24 hours)

### Alerts to Jeremy

- **Any error** - Immediate notification
- **Sync failure** - Alert with full details
- **Validation failure** - Alert with validation errors
- **Conflict detected** - Alert with conflict details

**Nothing is hidden. All issues are reported immediately.**

---

## Implementation Checklist

- [ ] Create `businesses_master` table in BigQuery
- [ ] Create `people_business_relationships` table in BigQuery
- [ ] Create corresponding tables in Supabase
- [ ] Create corresponding tables in Local DB
- [ ] Update CRM Twenty schema for businesses
- [ ] Implement ErrorReporter service
- [ ] Update all sync services to handle businesses
- [ ] Update all sync services to handle relationships
- [ ] Add error reporting to all sync operations
- [ ] Create business context builder for LLM
- [ ] Create relationship context builder for LLM
- [ ] Set up error alerting to Jeremy
- [ ] Create error dashboard
- [ ] Migrate existing business data

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Design Complete - Ready for Implementation

**TRANSPARENCY COMMITMENT**: All errors, issues, and problems will be reported. Nothing will be hidden.
