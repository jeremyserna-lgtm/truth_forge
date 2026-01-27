-- People-to-People Relationships Migration
-- Version: 1.0.0
-- Date: 2026-01-27
--
-- This migration creates:
-- 1. People-people relationships table in all systems
-- 2. Social graph tracking infrastructure
-- 3. Relationship evolution tracking
-- 4. Complete transparency - nothing hidden

-- ============================================================================
-- BIGQUERY: people_relationships
-- ============================================================================

CREATE TABLE IF NOT EXISTS `identity.people_relationships` (
  -- Primary Identifiers
  relationship_id INT64 NOT NULL,
  person_1_id INT64 NOT NULL,               -- FK to contacts_master
  person_2_id INT64 NOT NULL,                -- FK to contacts_master
  
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
  FOREIGN KEY (person_1_id) REFERENCES `identity.contacts_master`(contact_id),
  FOREIGN KEY (person_2_id) REFERENCES `identity.contacts_master`(contact_id)
)
PARTITION BY DATE(created_at)
CLUSTER BY person_1_id, person_2_id, is_current
OPTIONS(
  description="People-to-people relationships with full social graph tracking"
);

CREATE INDEX IF NOT EXISTS idx_pr_person_1_id 
ON `identity.people_relationships`(person_1_id);

CREATE INDEX IF NOT EXISTS idx_pr_person_2_id 
ON `identity.people_relationships`(person_2_id);

CREATE INDEX IF NOT EXISTS idx_pr_is_current 
ON `identity.people_relationships`(is_current);

CREATE INDEX IF NOT EXISTS idx_pr_relationship_type 
ON `identity.people_relationships`(relationship_type);

CREATE INDEX IF NOT EXISTS idx_pr_both_people 
ON `identity.people_relationships`(person_1_id, person_2_id);

-- ============================================================================
-- SUPABASE: people_relationships
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  relationship_id TEXT NOT NULL UNIQUE,
  
  person_1_id TEXT NOT NULL,
  person_2_id TEXT NOT NULL,
  
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

CREATE INDEX IF NOT EXISTS idx_pr_person_1_id ON people_relationships(person_1_id);
CREATE INDEX IF NOT EXISTS idx_pr_person_2_id ON people_relationships(person_2_id);
CREATE INDEX IF NOT EXISTS idx_pr_is_current ON people_relationships(is_current);
CREATE INDEX IF NOT EXISTS idx_pr_relationship_type ON people_relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_pr_both_people ON people_relationships(person_1_id, person_2_id);

-- ============================================================================
-- TRIGGERS - Auto-update updated_at timestamps
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_people_relationships_updated_at 
BEFORE UPDATE ON people_relationships
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS - Documentation
-- ============================================================================

COMMENT ON TABLE people_relationships IS 'People-to-people relationships with full social graph tracking';
COMMENT ON COLUMN people_relationships.sync_errors IS 'All errors tracked here - nothing hidden';
COMMENT ON COLUMN people_relationships.social_context IS 'Social graph context: mutual connections, shared groups, etc.';
COMMENT ON COLUMN people_relationships.evolution IS 'Relationship evolution over time: changes, milestones';
