# Truth Engine: Data Models

**Version**: 1.0
**Created**: 2025-12-24
**Parent**: [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md)

---

## Overview

This document defines the complete data schemas for the Truth Engine interface layer. These models bridge the existing entity substrate (51.8M entities in BigQuery) with the user-facing experiences.

---

## Core Entities

### Entity Hierarchy (Existing)

The L1-L12 hierarchy is already in production in `spine.entity_unified`:

| Level | Entity Type | Count | Description |
|-------|-------------|-------|-------------|
| L1 | Token | 39,878,305 | Individual tokens (words, punctuation) |
| L2 | Word | 8,381,533 | Word-level entities |
| L3 | Span | 2,902,957 | Multi-word spans |
| L4 | Sentence | 511,487 | Complete sentences |
| L5 | Message | 53,697 | Individual messages in conversations |
| L6 | Turn | 25,316 | Conversational turns |
| L7 | Topic | (enrichment) | Topic groupings |
| L8 | Conversation | 351 | Complete conversation threads |
| L9-L12 | Emergent | (future) | Higher-order patterns |

**Schema** (`spine.entity_unified`):
```sql
entity_id STRING NOT NULL,
entity_type STRING NOT NULL,
level INT64 NOT NULL,
source STRING NOT NULL,
content STRING,
metadata JSON,
parent_id STRING,
created_at TIMESTAMP,
updated_at TIMESTAMP
```

---

## Relationship Models

### RelationshipProfile

The core model for relationship management.

**TypeScript Interface**:
```typescript
interface RelationshipProfile {
  // Identity
  profile_id: string;           // Format: prof_xxxxxxxx
  name: string;
  category: RelationshipCategory;

  // Contact Information
  contact: {
    phone?: string;
    email?: string;
    location?: string;
    apple_contact_id?: string;  // Link to Apple Contacts
  };

  // Relationship Context
  relationship: {
    known_since?: string;       // ISO date or description
    how_met?: string;           // Narrative description
    type?: RelationshipType;    // friend, family, partner, colleague, etc.
    closeness_level?: number;   // 1-10 scale
  };

  // Biographical Information
  biography: {
    occupation?: string;
    employer?: string;
    interests?: string[];
    key_life_events?: string[]; // Major events you know about
    personality_notes?: string; // Your observations
  };

  // Communication Patterns
  communication: {
    message_count?: number;
    last_contact?: string;      // ISO date
    frequency?: CommunicationFrequency;
    typical_topics?: string[];
    emotional_depth?: number;   // 1-10 scale
    preferred_channel?: string; // text, call, in-person
  };

  // AI-Generated Analysis
  analysis: {
    relationship_arc?: string;      // Narrative summary
    what_matters_to_them?: string[];
    how_they_experience_me?: string;
    blind_spots?: string[];         // Things you might not see
    current_state?: string;         // Current relationship status
    tensions?: string[];            // Known friction points
    strengths?: string[];           // Relationship strengths
  };

  // Perspective Gatherer
  interview: {
    completed?: boolean;
    code?: string;              // Interview access code
    completed_at?: string;
    summary?: string;
    key_insights?: string[];
  };

  // Action Tracking
  action_items?: ActionItem[];
  notes?: Note[];

  // Metadata
  source: 'manual' | 'apple_contacts' | 'ai_generated';
  created_at: string;
  updated_at: string;
}

type RelationshipCategory =
  | 'INNER_CIRCLE'    // Closest friends, partners
  | 'CLOSE_FRIEND'    // Regular close contact
  | 'FRIEND'          // Standard friends
  | 'ACQUAINTANCE'    // Know them, not close
  | 'PROFESSIONAL'    // Work relationships
  | 'SERVICE'         // Service providers
  | 'HISTORICAL'      // Past relationships
  | 'AI_COMPANION'    // AI relationships (Clara, etc.)
  | 'FAMILY'          // Family members
  | 'UNCATEGORIZED';  // Not yet categorized

type RelationshipType =
  | 'best_friend'
  | 'close_friend'
  | 'friend'
  | 'romantic_partner'
  | 'ex_partner'
  | 'family_parent'
  | 'family_sibling'
  | 'family_extended'
  | 'colleague'
  | 'mentor'
  | 'mentee'
  | 'service_provider'
  | 'ai_companion'
  | 'other';

type CommunicationFrequency =
  | 'daily'
  | 'weekly'
  | 'monthly'
  | 'quarterly'
  | 'yearly'
  | 'rarely';

interface ActionItem {
  id: string;
  content: string;
  priority: 'high' | 'medium' | 'low';
  due_date?: string;
  completed: boolean;
  created_at: string;
}

interface Note {
  id: string;
  content: string;
  created_at: string;
}
```

**BigQuery Schema** (`identity.relationship_profiles`):
```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.relationship_profiles` (
  profile_id STRING NOT NULL,
  name STRING NOT NULL,
  category STRING NOT NULL,

  -- Contact JSON
  contact JSON,
  -- Structure: { phone, email, location, apple_contact_id }

  -- Relationship JSON
  relationship JSON,
  -- Structure: { known_since, how_met, type, closeness_level }

  -- Biography JSON
  biography JSON,
  -- Structure: { occupation, employer, interests, key_life_events, personality_notes }

  -- Communication JSON
  communication JSON,
  -- Structure: { message_count, last_contact, frequency, typical_topics, emotional_depth, preferred_channel }

  -- Analysis JSON
  analysis JSON,
  -- Structure: { relationship_arc, what_matters_to_them, how_they_experience_me, blind_spots, current_state, tensions, strengths }

  -- Interview JSON
  interview JSON,
  -- Structure: { completed, code, completed_at, summary, key_insights }

  action_items ARRAY<STRUCT<
    id STRING,
    content STRING,
    priority STRING,
    due_date STRING,
    completed BOOL,
    created_at STRING
  >>,

  notes ARRAY<STRUCT<
    id STRING,
    content STRING,
    created_at STRING
  >>,

  source STRING NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY category, name
OPTIONS (
  description = "Relationship profiles for identity layer",
  labels = [("system", "primitive_engine"), ("layer", "identity"), ("component", "relationships")]
);
```

---

### InterviewSession

Model for perspective gathering interviews.

**TypeScript Interface**:
```typescript
interface InterviewSession {
  // Identity
  session_id: string;           // Format: intv_xxxxxxxx
  profile_id: string;           // Link to relationship profile
  code: string;                 // Unique access code (e.g., "adam-2024")

  // Status
  status: InterviewStatus;

  // Friend Configuration
  friend_profile: {
    name: string;
    relationship_to_jeremy: string;
    interview_focus?: string[];     // Areas to explore
    questions_to_ask?: string[];    // Specific questions
    context_for_claude?: string;    // Background for the AI
  };

  // Conversation
  messages: InterviewMessage[];

  // Accumulated Analysis
  analysis: {
    themes_detected: string[];
    sentiment_overall: number;
    key_observations: string[];
    blind_spots_surfaced: string[];
    relationship_insights: string[];
  };

  // Final Output
  summary?: string;             // Generated summary

  // Timestamps
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

type InterviewStatus =
  | 'pending'       // Created, not started
  | 'in_progress'   // Friend is actively interviewing
  | 'completed'     // Interview finished
  | 'expired';      // Code expired

interface InterviewMessage {
  id: string;
  role: 'assistant' | 'user';   // Claude or friend
  content: string;
  timestamp: string;
  metadata?: {
    sentiment?: number;
    themes?: string[];
  };
}
```

**BigQuery Schema** (`identity.interview_sessions`):
```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.interview_sessions` (
  session_id STRING NOT NULL,
  profile_id STRING NOT NULL,
  code STRING NOT NULL,
  status STRING NOT NULL,

  friend_profile JSON,
  -- Structure: { name, relationship_to_jeremy, interview_focus, questions_to_ask, context_for_claude }

  messages JSON,
  -- Array of: { id, role, content, timestamp, metadata }

  analysis JSON,
  -- Structure: { themes_detected, sentiment_overall, key_observations, blind_spots_surfaced, relationship_insights }

  summary STRING,

  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(created_at)
CLUSTER BY status, profile_id
OPTIONS (
  description = "Perspective gathering interview sessions",
  labels = [("system", "primitive_engine"), ("layer", "identity"), ("component", "interviews")]
);
```

---

### RelationshipCategorization

Audit trail for categorization decisions.

**TypeScript Interface**:
```typescript
interface RelationshipCategorization {
  categorization_id: string;    // Format: cat_xxxxxxxx
  profile_id: string;

  previous_category?: RelationshipCategory;
  new_category: RelationshipCategory;

  categorized_by: CategorizationSource;
  ai_confidence?: number;       // 0-1 for AI suggestions
  ai_reasoning?: string;        // Why AI suggested this
  user_override_reason?: string;  // If user overrode AI

  categorized_at: string;
}

type CategorizationSource =
  | 'user_manual'       // User directly selected
  | 'ai_suggested'      // AI suggested, user confirmed
  | 'ai_auto'           // AI auto-categorized (low confidence ok)
  | 'batch_import';     // Imported from external source
```

**BigQuery Schema** (`identity.relationship_categorizations`):
```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.relationship_categorizations` (
  categorization_id STRING NOT NULL,
  profile_id STRING NOT NULL,

  previous_category STRING,
  new_category STRING NOT NULL,

  categorized_by STRING NOT NULL,
  ai_confidence FLOAT64,
  ai_reasoning STRING,
  user_override_reason STRING,

  categorized_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
OPTIONS (
  description = "Audit trail for relationship categorization decisions",
  labels = [("system", "primitive_engine"), ("layer", "identity"), ("component", "audit")]
);
```

---

## Analysis Models

### PatternDetection

Model for detected cognitive/behavioral patterns.

**TypeScript Interface**:
```typescript
interface DetectedPattern {
  pattern_id: string;           // Format: pat_xxxxxxxx

  // Pattern Definition
  name: string;
  description: string;
  pattern_type: PatternType;

  // Evidence
  evidence: {
    conversation_ids: string[];
    message_ids: string[];
    date_range: { start: string; end: string; };
    frequency: number;          // Times detected
  };

  // Analysis
  characteristics: string[];
  related_patterns: string[];   // pattern_ids

  // For observers (anonymized version)
  anonymized_description?: string;
  is_public: boolean;

  created_at: string;
  updated_at: string;
}

type PatternType =
  | 'cognitive'         // Thinking patterns
  | 'emotional'         // Emotional patterns
  | 'behavioral'        // Action patterns
  | 'relational'        // Relationship patterns
  | 'temporal';         // Time-based patterns
```

### TimelineEvent

Model for timeline visualization.

**TypeScript Interface**:
```typescript
interface TimelineEvent {
  event_id: string;

  // Timing
  date: string;
  day_number?: number;          // Relative to Day Zero

  // Event Details
  title: string;
  description?: string;
  event_type: TimelineEventType;

  // Links
  entity_ids?: string[];        // Related entities
  profile_ids?: string[];       // Related people

  // Significance
  significance_score: number;   // 1-10
  themes: string[];

  created_at: string;
}

type TimelineEventType =
  | 'milestone'         // Major life event
  | 'conversation'      // Significant conversation
  | 'pattern_shift'     // Pattern changed
  | 'relationship'      // Relationship event
  | 'system';           // System event (Day Zero, etc.)
```

---

## Privacy Models

### PrivacyLayer

Access control for audience-based privacy.

**TypeScript Interface**:
```typescript
interface PrivacyAccess {
  profile_id: string;           // Who this is about
  viewer_id: string;            // Who is viewing
  layer: PrivacyLayer;

  permissions: {
    view_contact: boolean;
    view_communication: boolean;
    view_analysis: boolean;
    view_interview: boolean;
    view_patterns: boolean;
    submit_observations: boolean;
    edit: boolean;
  };

  granted_at: string;
  granted_by: 'owner' | 'system';
}

type PrivacyLayer =
  | 'core'              // Jeremy only - full access
  | 'intimate'          // Partners - high access
  | 'close'             // Close friends - moderate access
  | 'friend'            // Friends - limited access
  | 'family'            // Family - filtered access
  | 'observer'          // Researchers - anonymized access
  | 'public';           // Anyone - minimal/none
```

### HowIsJeremyState

Model for the "How is Jeremy" dashboard.

**TypeScript Interface**:
```typescript
interface HowIsJeremyState {
  // Current State
  snapshot_at: string;

  // Translated Signals (not raw metrics)
  mood: {
    trajectory: 'improving' | 'stable' | 'declining';
    description: string;        // "Building momentum"
    confidence: number;
  };

  energy: {
    level: 'high' | 'moderate' | 'low';
    quality: string;            // "Focused", "Scattered", etc.
  };

  focus: {
    current: string;            // "Truth Engine architecture"
    intensity: number;          // 1-10
  };

  emotional_weather: {
    description: string;        // "Intense but grounded"
    valence: number;            // -1 to 1
  };

  // Actionable Guidance
  good_time_to_reach_out: boolean;
  what_he_might_need: string;
  what_to_avoid: string;

  // Source (for transparency)
  based_on: {
    message_count: number;
    date_range: { start: string; end: string; };
  };
}
```

---

## Substrate Fluidity Models

### InterfaceRegistry

Model for schema-driven UI generation. Enables the interface to discover and render views automatically.

**TypeScript Interface**:
```typescript
interface InterfaceRegistryEntry {
  // Identity
  entry_id: string;

  // Target
  dataset: string;
  table_or_view: string;

  // Display Metadata
  display_name: string;
  description: string;
  icon?: string;                    // Icon identifier
  color?: string;                   // Theme color

  // Rendering Hints
  render_type: RenderType;
  default_columns?: string[];       // Which columns to show by default
  sortable_columns?: string[];
  filterable_columns?: string[];
  searchable_columns?: string[];

  // Relationships
  related_views?: string[];         // Other views this links to
  parent_view?: string;             // Hierarchical parent

  // Access Control
  audience: AudienceLevel[];        // Who can see this

  // Discovery
  auto_discovered: boolean;         // Found via INFORMATION_SCHEMA
  manually_enriched: boolean;       // Had metadata added

  created_at: string;
  updated_at: string;
}

type RenderType =
  | 'table'           // Standard table view
  | 'cards'           // Card grid
  | 'timeline'        // Temporal visualization
  | 'graph'           // Network graph
  | 'dashboard'       // Metrics dashboard
  | 'detail';         // Single record detail

type AudienceLevel =
  | 'operator'        // Jeremy only
  | 'intimate'        // Close friends/partners
  | 'observer'        // Researchers
  | 'public';         // Anyone
```

**BigQuery Schema** (`identity.interface_registry`):
```sql
CREATE TABLE IF NOT EXISTS `flash-clover-464719-g1.identity.interface_registry` (
  entry_id STRING NOT NULL,

  -- Target
  dataset STRING NOT NULL,
  table_or_view STRING NOT NULL,

  -- Display Metadata
  display_name STRING NOT NULL,
  description STRING,
  icon STRING,
  color STRING,

  -- Rendering Hints JSON
  rendering JSON,
  -- Structure: {
  --   render_type, default_columns, sortable_columns,
  --   filterable_columns, searchable_columns
  -- }

  -- Relationships JSON
  relationships JSON,
  -- Structure: { related_views, parent_view }

  -- Access Control
  audience ARRAY<STRING>,

  -- Discovery Flags
  auto_discovered BOOL DEFAULT FALSE,
  manually_enriched BOOL DEFAULT FALSE,

  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(),
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP()
)
CLUSTER BY dataset, table_or_view
OPTIONS (
  description = "Registry of discoverable views for dynamic interface rendering",
  labels = [("system", "primitive_engine"), ("layer", "interface"), ("component", "registry")]
);
```

### SchemaDiscovery

Helper for discovering available data sources.

**TypeScript Interface**:
```typescript
interface DiscoveredSchema {
  dataset: string;
  table_name: string;
  table_type: 'BASE TABLE' | 'VIEW';

  // From BigQuery labels
  labels: Record<string, string>;

  // From table description
  description?: string;

  // Schema analysis
  columns: SchemaColumn[];
  row_count?: number;
  size_bytes?: number;

  // Registry match
  registry_entry?: InterfaceRegistryEntry;
}

interface SchemaColumn {
  name: string;
  data_type: string;
  is_nullable: boolean;
  description?: string;
}
```

**Discovery Query**:
```sql
-- Discover all tables/views with their metadata
SELECT
  table_catalog,
  table_schema as dataset,
  table_name,
  table_type,
  ARRAY(
    SELECT AS STRUCT option_name, option_value
    FROM `flash-clover-464719-g1`.INFORMATION_SCHEMA.TABLE_OPTIONS t2
    WHERE t2.table_schema = t.table_schema
      AND t2.table_name = t.table_name
  ) as options
FROM `flash-clover-464719-g1`.INFORMATION_SCHEMA.TABLES t
WHERE table_schema IN ('spine', 'identity', 'governance', 'ai_coordination')
ORDER BY table_schema, table_name;
```

---

## Integration Models

### ExistingSystemLinks

Links to existing BigQuery tables.

```typescript
// Links to existing spine.entity_unified
interface EntityLink {
  entity_id: string;
  entity_type: EntityLevel;
}

// Links to existing identity.id_registry
interface IDRegistryLink {
  id_registry_entry: string;
  id_type: string;
}

// Links to existing governance.contact_classifications
interface ContactClassificationLink {
  contact_id: string;
  classification: string;
}
```

---

## API Contracts

### REST Endpoints

```typescript
// Relationships
GET    /api/relationships                    → RelationshipProfile[]
GET    /api/relationships/:id                → RelationshipProfile
POST   /api/relationships                    → RelationshipProfile
PATCH  /api/relationships/:id                → RelationshipProfile
POST   /api/relationships/:id/categorize     → RelationshipCategorization
POST   /api/relationships/:id/generate-profile → RelationshipProfile

// Interviews
GET    /api/interview/:code                  → InterviewSession
POST   /api/interview/:code/message          → InterviewMessage
POST   /api/interview/:code/complete         → InterviewSession

// Analysis
GET    /api/analysis/timeline                → TimelineEvent[]
GET    /api/analysis/patterns                → DetectedPattern[]
POST   /api/analysis/query                   → QueryResult

// Intimates Dashboard
GET    /api/how-is-jeremy/:access_token      → HowIsJeremyState
```

---

## Migration from Existing Data

### From Apple Contacts

```sql
-- Migrate contacts to relationship_profiles
INSERT INTO identity.relationship_profiles
SELECT
  CONCAT('prof_', GENERATE_UUID()) as profile_id,
  full_name as name,
  COALESCE(suggested_category, 'UNCATEGORIZED') as category,
  JSON_OBJECT(
    'phone', phone_number,
    'email', email_address,
    'apple_contact_id', record_id
  ) as contact,
  JSON_OBJECT() as relationship,
  JSON_OBJECT() as biography,
  JSON_OBJECT() as communication,
  JSON_OBJECT() as analysis,
  JSON_OBJECT() as interview,
  [] as action_items,
  [] as notes,
  'apple_contacts' as source,
  CURRENT_TIMESTAMP() as created_at,
  CURRENT_TIMESTAMP() as updated_at
FROM identity.raw_apple_contacts_merged
WHERE suggested_category IS NOT NULL;
```

### From Perspective Gatherer YAML

```python
# tools/perspective_gatherer/friends/*.yaml → identity.interview_sessions
def migrate_friend_profile(yaml_path: Path) -> dict:
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    return {
        'session_id': generate_interview_id(),
        'profile_id': find_or_create_profile(data['name']),
        'code': generate_interview_code(data['name']),
        'status': 'pending',
        'friend_profile': {
            'name': data['name'],
            'relationship_to_jeremy': data.get('relationship', ''),
            'interview_focus': data.get('focus_areas', []),
            'context_for_claude': data.get('context', '')
        }
    }
```

---

## Related Documents

- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Overall vision
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) - Technical architecture
- [AUDIENCE_EXPERIENCES.md](./AUDIENCE_EXPERIENCES.md) - UX design
- [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) - Build phases
- [../architecture/IDENTITY_LAYER_ARCHITECTURE.md](../architecture/IDENTITY_LAYER_ARCHITECTURE.md) - Existing identity layer detail
