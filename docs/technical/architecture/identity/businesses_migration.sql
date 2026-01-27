-- Businesses and People-Business Relationships Migration
-- Version: 1.0.0
-- Date: 2026-01-27
--
-- This migration creates:
-- 1. Businesses table in all systems
-- 2. People-business relationships table
-- 3. Error tracking infrastructure
-- 4. Complete transparency - nothing hidden

-- ============================================================================
-- BIGQUERY: businesses_master
-- ============================================================================

CREATE TABLE IF NOT EXISTS `identity.businesses_master` (
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
  first_seen TIMESTAMP,
  last_seen TIMESTAMP,
  
  PRIMARY KEY (business_id)
)
PARTITION BY DATE(created_at)
CLUSTER BY name_normalized, sync_status
OPTIONS(
  description="Master businesses table - canonical source"
);

CREATE INDEX IF NOT EXISTS idx_businesses_name_normalized 
ON `identity.businesses_master`(name_normalized);

CREATE INDEX IF NOT EXISTS idx_businesses_sync_status 
ON `identity.businesses_master`(sync_status);

-- ============================================================================
-- BIGQUERY: people_business_relationships
-- ============================================================================

CREATE TABLE IF NOT EXISTS `identity.people_business_relationships` (
  -- Primary Identifiers
  relationship_id INT64 NOT NULL,
  contact_id INT64 NOT NULL,
  business_id INT64 NOT NULL,
  
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
  FOREIGN KEY (contact_id) REFERENCES `identity.contacts_master`(contact_id),
  FOREIGN KEY (business_id) REFERENCES `identity.businesses_master`(business_id)
)
PARTITION BY DATE(created_at)
CLUSTER BY contact_id, business_id, is_current
OPTIONS(
  description="People-business relationships with full tracking"
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_pbr_unique 
ON `identity.people_business_relationships`(contact_id, business_id, relationship_type);

CREATE INDEX IF NOT EXISTS idx_pbr_contact_id 
ON `identity.people_business_relationships`(contact_id);

CREATE INDEX IF NOT EXISTS idx_pbr_business_id 
ON `identity.people_business_relationships`(business_id);

CREATE INDEX IF NOT EXISTS idx_pbr_is_current 
ON `identity.people_business_relationships`(is_current);

-- ============================================================================
-- BIGQUERY: sync_errors_log (Central Error Log)
-- ============================================================================

CREATE TABLE IF NOT EXISTS `identity.sync_errors_log` (
  error_id STRING NOT NULL,
  entity_type STRING NOT NULL,              -- 'business', 'relationship', 'contact'
  entity_id STRING NOT NULL,
  timestamp TIMESTAMP NOT NULL,
  system STRING NOT NULL,
  error_type STRING NOT NULL,
  error_message STRING NOT NULL,
  error_details JSON,
  resolved BOOL DEFAULT FALSE,
  resolution_notes STRING,
  resolved_at TIMESTAMP,
  
  PRIMARY KEY (error_id)
)
PARTITION BY DATE(timestamp)
CLUSTER BY entity_type, system, resolved
OPTIONS(
  description="Central error log - all errors tracked, nothing hidden"
);

CREATE INDEX IF NOT EXISTS idx_errors_unresolved 
ON `identity.sync_errors_log`(resolved) WHERE resolved = FALSE;

CREATE INDEX IF NOT EXISTS idx_errors_entity 
ON `identity.sync_errors_log`(entity_type, entity_id);

-- ============================================================================
-- SUPABASE: businesses_master
-- ============================================================================

CREATE TABLE IF NOT EXISTS businesses_master (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  business_id TEXT NOT NULL UNIQUE,
  
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
  sync_errors JSONB DEFAULT '[]',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  first_seen TIMESTAMPTZ,
  last_seen TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_businesses_business_id ON businesses_master(business_id);
CREATE INDEX IF NOT EXISTS idx_businesses_name_normalized ON businesses_master(name_normalized);
CREATE INDEX IF NOT EXISTS idx_businesses_sync_status ON businesses_master(sync_status);

-- ============================================================================
-- SUPABASE: people_business_relationships
-- ============================================================================

CREATE TABLE IF NOT EXISTS people_business_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  relationship_id TEXT NOT NULL UNIQUE,
  
  contact_id TEXT NOT NULL,
  business_id TEXT NOT NULL,
  
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
  sync_errors JSONB DEFAULT '[]',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE (contact_id, business_id, relationship_type),
  FOREIGN KEY (contact_id) REFERENCES contacts_master(contact_id),
  FOREIGN KEY (business_id) REFERENCES businesses_master(business_id)
);

CREATE INDEX IF NOT EXISTS idx_pbr_contact_id ON people_business_relationships(contact_id);
CREATE INDEX IF NOT EXISTS idx_pbr_business_id ON people_business_relationships(business_id);
CREATE INDEX IF NOT EXISTS idx_pbr_is_current ON people_business_relationships(is_current);

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

CREATE TRIGGER update_businesses_updated_at 
BEFORE UPDATE ON businesses_master
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_relationships_updated_at 
BEFORE UPDATE ON people_business_relationships
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS - Documentation
-- ============================================================================

COMMENT ON TABLE businesses_master IS 'Businesses master table - syncs across all systems';
COMMENT ON TABLE people_business_relationships IS 'People-business relationships with full tracking';
COMMENT ON COLUMN businesses_master.sync_errors IS 'All errors tracked here - nothing hidden';
COMMENT ON COLUMN people_business_relationships.sync_errors IS 'All errors tracked here - nothing hidden';
