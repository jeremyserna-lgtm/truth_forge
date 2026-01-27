# People-to-People Relationships & Social Graph

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Design - Ready for Implementation
**Owner**: Jeremy Serna

---

## Executive Summary

This architecture adds **complete people-to-people relationships** to build a rich social graph:
1. **People-People Relationships** - Many-to-many relationships with full tracking
2. **Social Graph** - Who knows who, how they're connected
3. **Temporal Tracking** - Relationships evolve over time
4. **Complete transparency** - All issues, problems, and errors are reported
5. **Full sync support** - Relationships sync across all systems
6. **Rich relationship data** - LLM-ready relationship context

**Key Principles**:
- **Nothing hidden** - All issues must be reported
- **Complete fidelity** - Full tracking of all relationships over time
- **Free linking** - People can link to people freely
- **Social graph** - Build rich model of connections
- **Temporal evolution** - Track how relationships change over time

---

## People-People Relationship Schema

### Canonical Relationship Model

```typescript
interface CanonicalPeopleRelationship {
  // Primary Identifiers
  relationship_id: string | number;         // Stable ID across all systems
  person_1_id: string | number;            // First person (contact_id)
  person_2_id: string | number;             // Second person (contact_id)
  
  // Relationship Direction
  // Note: Relationships are bidirectional but can have asymmetric properties
  is_directed: boolean;                      // Is this relationship directional?
  direction: 'person_1_to_2' | 'person_2_to_1' | 'bidirectional';
  
  // Relationship Type
  relationship_type: string;                // friend, family, romantic, colleague, etc.
  relationship_subtype?: string;            // best_friend, close_friend, casual_friend, etc.
  
  // Temporal Tracking
  start_date?: string;                      // When relationship started
  end_date?: string;                        // When relationship ended (if applicable)
  is_current: boolean;                      // Is this an active relationship
  relationship_status?: string;              // active, dormant, ended, complicated, etc.
  
  // Relationship Context
  relationship_context: {
    how_met?: string;                       // How they met
    relationship_arc?: string;              // Narrative history of relationship
    current_state?: string;                 // Current state/status
    relationship_notes?: string;            // Your observations
    importance?: number;                     // 1-10 importance scale
    closeness_level?: number;               // 1-10 closeness scale
    trust_level?: number;                   // 1-10 trust level
    emotional_depth?: number;               // 1-10 emotional depth
    frequency_of_contact?: string;          // daily, weekly, monthly, rarely, etc.
    typical_interaction_type?: string;     // text, call, in_person, social_media, etc.
  };
  
  // Social Graph Context
  social_context: {
    introduced_by?: string;                 // Contact ID of person who introduced them
    common_connections?: string[];          // Array of contact_ids they both know
    shared_groups?: string[];               // Groups they're both in
    shared_interests?: string[];            // Interests they share
    shared_experiences?: Array<{            // Significant shared experiences
      date: string;
      event: string;
      significance: string;
    }>;
  };
  
  // Tracking Data
  tracking: {
    interaction_count?: number;            // Number of interactions
    last_interaction_date?: string;        // Last interaction
    interaction_topics?: string[];         // Common topics
    communication_channels?: string[];     // How they communicate
    interaction_frequency?: number;         // Interactions per month
    relationship_health?: string;           // healthy, strained, improving, etc.
  };
  
  // Relationship Evolution
  evolution: {
    previous_relationship_type?: string;   // What it was before
    relationship_changes?: Array<{          // History of changes
      date: string;
      change_type: string;                  // type_change, status_change, closeness_change
      from_value: string;
      to_value: string;
      reason?: string;
    }>;
    milestones?: Array<{                    // Relationship milestones
      date: string;
      milestone: string;
      significance: string;
    }>;
  };
  
  // LLM Context (for dynamic prompting)
  llm_context: {
    relationship_summary?: string;         // AI-generated summary
    key_dynamics?: string[];               // Key relationship dynamics
    blind_spots?: string[];                // Things you might not see
    strengths?: string[];                  // Relationship strengths
    tensions?: string[];                   // Known friction points
    patterns?: string[];                   // Recurring patterns
    recommendations?: string[];            // AI recommendations
  };
  
  // Sync Metadata
  sync_metadata: {
    last_updated: string;                   // ISO timestamp
    last_updated_by: string;                // System that made change
    version: number;                        // Incremental version
    sync_status: 'synced' | 'pending' | 'conflict' | 'error';
    source_systems: string[];              // Which systems have this relationship
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

## Relationship Types

### Standard Relationship Types

#### Personal Relationships
- **friend** - General friendship
  - Subtypes: `best_friend`, `close_friend`, `casual_friend`, `childhood_friend`, `work_friend`
- **family** - Family relationship
  - Subtypes: `parent`, `child`, `sibling`, `spouse`, `cousin`, `aunt_uncle`, `grandparent`, `in_law`
- **romantic** - Romantic relationship
  - Subtypes: `partner`, `dating`, `ex_partner`, `flirtation`, `hookup`
- **acquaintance** - Casual acquaintance
  - Subtypes: `social_acquaintance`, `professional_acquaintance`, `neighbor`

#### Professional Relationships
- **colleague** - Work colleague
  - Subtypes: `coworker`, `manager`, `direct_report`, `peer`, `mentor`, `mentee`
- **client** - Business client relationship
- **vendor** - Vendor/supplier relationship
- **partner** - Business partner

#### Other Relationships
- **introduced** - Person who introduced you
- **mutual_friend** - Mutual friend connection
- **enemy** - Negative relationship
- **blocked** - Blocked relationship
- **other** - Other relationship type

---

## Database Schemas

### BigQuery: `identity.people_relationships`

```sql
CREATE TABLE `identity.people_relationships` (
  -- Primary Identifiers
  relationship_id INT64 NOT NULL,
  person_1_id INT64 NOT NULL,               -- FK to contacts_master
  person_2_id INT64 NOT NULL,               -- FK to contacts_master
  
  -- Relationship Direction
  is_directed BOOL DEFAULT FALSE,
  direction STRING,                          -- 'person_1_to_2', 'person_2_to_1', 'bidirectional'
  
  -- Relationship Type
  relationship_type STRING NOT NULL,
  relationship_subtype STRING,
  
  -- Temporal Tracking
  start_date DATE,
  end_date DATE,
  is_current BOOL DEFAULT TRUE,
  relationship_status STRING,
  
  -- Relationship Context (JSON)
  relationship_context JSON,
  
  -- Social Graph Context (JSON)
  social_context JSON,
  
  -- Tracking Data (JSON)
  tracking JSON,
  
  -- Relationship Evolution (JSON)
  evolution JSON,
  
  -- LLM Context (JSON)
  llm_context JSON,
  
  -- Sync Metadata
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64 DEFAULT 1,
  sync_status STRING DEFAULT 'synced',
  source_systems ARRAY<STRING>,
  sync_errors ARRAY<STRUCT<
    timestamp TIMESTAMP,
    system STRING,
    error_type STRING,
    error_message STRING,
    error_details JSON,
    resolved BOOL
  >>,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  
  PRIMARY KEY (relationship_id),
  FOREIGN KEY (person_1_id) REFERENCES identity.contacts_master(contact_id),
  FOREIGN KEY (person_2_id) REFERENCES identity.contacts_master(contact_id),
  -- Ensure person_1_id < person_2_id for consistency (or use separate index)
  INDEX (person_1_id),
  INDEX (person_2_id),
  INDEX (is_current),
  INDEX (relationship_type)
)
PARTITION BY DATE(created_at)
CLUSTER BY person_1_id, person_2_id, is_current
OPTIONS(
  description="People-to-people relationships with full social graph tracking"
);
```

### Supabase: `people_relationships`

```sql
CREATE TABLE people_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  relationship_id TEXT NOT NULL UNIQUE,      -- Maps to BigQuery relationship_id
  
  person_1_id TEXT NOT NULL,                -- FK to contacts_master.contact_id
  person_2_id TEXT NOT NULL,                -- FK to contacts_master.contact_id
  
  -- Relationship Direction
  is_directed BOOLEAN DEFAULT false,
  direction TEXT,
  
  -- Relationship Type
  relationship_type TEXT NOT NULL,
  relationship_subtype TEXT,
  
  -- Temporal Tracking
  start_date DATE,
  end_date DATE,
  is_current BOOLEAN DEFAULT true,
  relationship_status TEXT,
  
  -- Relationship Context (JSONB)
  relationship_context JSONB DEFAULT '{}',
  
  -- Social Graph Context (JSONB)
  social_context JSONB DEFAULT '{}',
  
  -- Tracking Data (JSONB)
  tracking JSONB DEFAULT '{}',
  
  -- Relationship Evolution (JSONB)
  evolution JSONB DEFAULT '{}',
  
  -- LLM Context (JSONB)
  llm_context JSONB DEFAULT '{}',
  
  -- Sync Metadata
  last_updated TIMESTAMPTZ,
  last_updated_by TEXT,
  version INTEGER DEFAULT 1,
  sync_status TEXT DEFAULT 'synced',
  source_systems TEXT[],
  sync_errors JSONB DEFAULT '[]',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CHECK (person_1_id != person_2_id),       -- Can't have relationship with self
  FOREIGN KEY (person_1_id) REFERENCES contacts_master(contact_id),
  FOREIGN KEY (person_2_id) REFERENCES contacts_master(contact_id)
);

CREATE INDEX idx_pr_person_1_id ON people_relationships(person_1_id);
CREATE INDEX idx_pr_person_2_id ON people_relationships(person_2_id);
CREATE INDEX idx_pr_is_current ON people_relationships(is_current);
CREATE INDEX idx_pr_relationship_type ON people_relationships(relationship_type);
CREATE INDEX idx_pr_both_people ON people_relationships(person_1_id, person_2_id);
```

---

## Social Graph Queries

### Find All Connections for a Person

```sql
-- All relationships for a person (as person_1 or person_2)
SELECT 
  CASE 
    WHEN person_1_id = @person_id THEN person_2_id
    ELSE person_1_id
  END as connected_person_id,
  relationship_type,
  relationship_subtype,
  is_current,
  relationship_context,
  tracking
FROM identity.people_relationships
WHERE person_1_id = @person_id OR person_2_id = @person_id
ORDER BY is_current DESC, tracking->>'last_interaction_date' DESC;
```

### Find Mutual Connections

```sql
-- Find people who know both person A and person B
WITH person_a_connections AS (
  SELECT 
    CASE WHEN person_1_id = @person_a_id THEN person_2_id ELSE person_1_id END as contact_id
  FROM identity.people_relationships
  WHERE (person_1_id = @person_a_id OR person_2_id = @person_a_id)
    AND is_current = TRUE
),
person_b_connections AS (
  SELECT 
    CASE WHEN person_1_id = @person_b_id THEN person_2_id ELSE person_1_id END as contact_id
  FROM identity.people_relationships
  WHERE (person_1_id = @person_b_id OR person_2_id = @person_b_id)
    AND is_current = TRUE
)
SELECT 
  c.contact_id,
  c.canonical_name,
  c.category_code
FROM identity.contacts_master c
WHERE c.contact_id IN (
  SELECT contact_id FROM person_a_connections
  INTERSECT
  SELECT contact_id FROM person_b_connections
);
```

### Find Relationship Path Between Two People

```sql
-- Find shortest path between two people (up to 3 degrees)
WITH RECURSIVE relationship_path AS (
  -- Direct relationship
  SELECT 
    person_1_id,
    person_2_id,
    relationship_type,
    1 as depth,
    ARRAY[person_1_id, person_2_id] as path
  FROM identity.people_relationships
  WHERE (person_1_id = @person_a_id AND person_2_id = @person_b_id)
     OR (person_1_id = @person_b_id AND person_2_id = @person_a_id)
  
  UNION ALL
  
  -- Indirect relationships (up to 3 degrees)
  SELECT 
    r.person_1_id,
    r.person_2_id,
    r.relationship_type,
    rp.depth + 1,
    rp.path || r.person_2_id
  FROM identity.people_relationships r
  JOIN relationship_path rp ON (
    (rp.person_2_id = r.person_1_id AND r.person_2_id != ALL(rp.path))
    OR (rp.person_2_id = r.person_2_id AND r.person_1_id != ALL(rp.path))
  )
  WHERE rp.depth < 3
    AND r.is_current = TRUE
)
SELECT * FROM relationship_path
WHERE person_2_id = @person_b_id
ORDER BY depth
LIMIT 1;
```

---

## Relationship Evolution Tracking

### Track Relationship Changes

```python
def update_relationship_evolution(
    relationship_id: str,
    change_type: str,
    from_value: str,
    to_value: str,
    reason: Optional[str] = None
) -> None:
    """Track a change in relationship."""
    
    evolution_entry = {
        'date': datetime.utcnow().isoformat(),
        'change_type': change_type,  # 'type_change', 'status_change', 'closeness_change'
        'from_value': from_value,
        'to_value': to_value,
        'reason': reason
    }
    
    # Append to evolution.relationship_changes array
    query = """
    UPDATE `identity.people_relationships`
    SET evolution = JSON_SET(
      COALESCE(evolution, '{}'),
      '$.relationship_changes',
      JSON_ARRAY_APPEND(
        COALESCE(JSON_EXTRACT(evolution, '$.relationship_changes'), '[]'),
        '$',
        @evolution_entry
      )
    )
    WHERE relationship_id = @relationship_id
    """
    
    # Execute update...
```

---

## LLM Integration

### Relationship Context Builder

```python
def build_relationship_context(self, relationship: Dict) -> str:
    """Build rich context string for LLM prompts."""
    parts = []
    
    # Basic Info
    parts.append(f"**Relationship Type**: {relationship['relationship_type']}")
    if relationship.get('relationship_subtype'):
        parts.append(f"**Subtype**: {relationship['relationship_subtype']}")
    
    # Status
    if relationship.get('is_current'):
        parts.append(f"**Status**: Current")
    else:
        parts.append(f"**Status**: Ended ({relationship.get('end_date')})")
    
    # Relationship Context
    rel_ctx = relationship.get('relationship_context', {})
    if rel_ctx.get('relationship_arc'):
        parts.append(f"**Relationship Arc**: {rel_ctx['relationship_arc']}")
    if rel_ctx.get('closeness_level'):
        parts.append(f"**Closeness**: {rel_ctx['closeness_level']}/10")
    if rel_ctx.get('how_met'):
        parts.append(f"**How They Met**: {rel_ctx['how_met']}")
    
    # Social Context
    social_ctx = relationship.get('social_context', {})
    if social_ctx.get('common_connections'):
        parts.append(f"**Mutual Connections**: {len(social_ctx['common_connections'])} people")
    if social_ctx.get('shared_interests'):
        parts.append(f"**Shared Interests**: {', '.join(social_ctx['shared_interests'])}")
    
    # Tracking
    tracking = relationship.get('tracking', {})
    if tracking.get('last_interaction_date'):
        parts.append(f"**Last Interaction**: {tracking['last_interaction_date']}")
    if tracking.get('relationship_health'):
        parts.append(f"**Relationship Health**: {tracking['relationship_health']}")
    
    # LLM Context
    llm_ctx = relationship.get('llm_context', {})
    if llm_ctx.get('key_dynamics'):
        parts.append(f"**Key Dynamics**: {', '.join(llm_ctx['key_dynamics'])}")
    if llm_ctx.get('recommendations'):
        parts.append(f"**Recommendations**: {', '.join(llm_ctx['recommendations'])}")
    
    return "\n".join(parts)
```

---

## Sync Services

### PeopleRelationshipSyncService

```python
class PeopleRelationshipSyncService:
    """Syncs people-people relationships across all systems."""
    
    def sync_relationship_to_all(self, relationship_id: str) -> Dict[str, Any]:
        """Sync a relationship from BigQuery to all systems."""
        try:
            relationship = self._fetch_relationship_from_bigquery(relationship_id)
            if not relationship:
                self.error_reporter.report_error(
                    'people_relationship', relationship_id, 'bigquery',
                    'not_found', f'Relationship {relationship_id} not found'
                )
                return {'error': 'Relationship not found'}
            
            results = {
                'supabase': self._sync_relationship_to_supabase(relationship),
                'local': self._sync_relationship_to_local(relationship),
                'crm_twenty': self._sync_relationship_to_crm_twenty(relationship)
            }
            
            # Check for errors
            for system, result in results.items():
                if result.get('status') == 'error':
                    self.error_reporter.report_error(
                        'people_relationship', relationship_id, system,
                        'sync_failed', result.get('error', 'Unknown error'),
                        result
                    )
            
            return results
        except Exception as e:
            self.error_reporter.report_error(
                'people_relationship', relationship_id, 'bigquery',
                'exception', str(e), {'traceback': traceback.format_exc()}
            )
            raise
```

---

## Validation Rules

### Relationship Validation

1. **Required fields**: `relationship_id`, `person_1_id`, `person_2_id`, `relationship_type`
2. **Self-relationship check**: `person_1_id` != `person_2_id`
3. **Foreign keys**: Both must reference valid contacts
4. **Dates**: `end_date` must be after `start_date` if both present
5. **Direction**: If `is_directed` is true, `direction` must be set

---

## Migration from Existing Data

### Extract Relationships from Contacts

```sql
-- Extract family relationships from category codes
INSERT INTO identity.people_relationships (
  person_1_id, person_2_id, relationship_type,
  relationship_subtype, is_current, relationship_context
)
SELECT 
  c1.contact_id as person_1_id,
  c2.contact_id as person_2_id,
  'family' as relationship_type,
  CASE 
    WHEN c1.subcategory_code LIKE 'A1%' THEN 'immediate_family'
    WHEN c1.subcategory_code LIKE 'A4%' THEN 'extended_family'
    ELSE 'family'
  END as relationship_subtype,
  TRUE as is_current,
  JSON_OBJECT(
    'how_met', 'family_member',
    'importance', 8
  ) as relationship_context
FROM identity.contacts_master c1
JOIN identity.contacts_master c2 
  ON c1.category_code = 'A' 
  AND c2.category_code = 'A'
  AND c1.contact_id < c2.contact_id  -- Avoid duplicates
WHERE c1.category_code = 'A' AND c2.category_code = 'A';
```

---

## Implementation Checklist

- [ ] Create `people_relationships` table in BigQuery
- [ ] Create corresponding table in Supabase
- [ ] Create corresponding table in Local DB
- [ ] Update CRM Twenty schema for relationships
- [ ] Implement PeopleRelationshipSyncService
- [ ] Add relationship context builder for LLM
- [ ] Create social graph query functions
- [ ] Add relationship evolution tracking
- [ ] Set up error alerting
- [ ] Migrate existing relationship data
- [ ] Create relationship visualization tools

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Design Complete - Ready for Implementation

**TRANSPARENCY COMMITMENT**: All errors, issues, and problems will be reported. Nothing will be hidden.
