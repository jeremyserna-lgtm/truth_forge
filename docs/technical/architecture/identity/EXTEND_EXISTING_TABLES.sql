-- Extend Existing Tables with Sync Metadata and LLM Fields
-- Version: 1.0.0
-- Date: 2026-01-27
--
-- This migration EXTENDS existing tables rather than creating duplicates.
-- Aligns with existing identity.contacts_master structure.

-- ============================================================================
-- EXTEND identity.contacts_master
-- ============================================================================

-- Add sync metadata (if not exists)
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

-- Add LLM context fields (if not exists)
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

-- Add canonical_name if missing (for consistency)
ALTER TABLE `identity.contacts_master`
ADD COLUMN IF NOT EXISTS canonical_name STRING;

-- Update canonical_name from full_name if null
UPDATE `identity.contacts_master`
SET canonical_name = COALESCE(full_name, CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, '')))
WHERE canonical_name IS NULL;

-- ============================================================================
-- EXTEND identity.contact_identifiers
-- ============================================================================

-- Add sync metadata (if not exists)
ALTER TABLE `identity.contact_identifiers`
ADD COLUMN IF NOT EXISTS sync_metadata STRUCT<
  last_updated TIMESTAMP,
  last_updated_by STRING,
  version INT64
>;

-- ============================================================================
-- EXTEND Supabase contacts_master
-- ============================================================================
-- Note: contacts_master already exists in supabase_migration.sql
-- Primary key is UUID (id), but we need contact_id TEXT to map to BigQuery INT64
-- This extends it with sync metadata and LLM fields

-- Add contact_id if missing (maps to BigQuery contact_id INT64 as TEXT)
-- This is the stable ID across all systems
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS contact_id TEXT UNIQUE;

-- Create index on contact_id for sync operations (if not exists)
CREATE INDEX IF NOT EXISTS idx_contacts_master_contact_id ON contacts_master(contact_id);

-- Add sync metadata
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

-- Add canonical_name if missing
ALTER TABLE contacts_master
ADD COLUMN IF NOT EXISTS canonical_name TEXT;

-- Update canonical_name from full_name if null
UPDATE contacts_master
SET canonical_name = COALESCE(full_name, CONCAT(COALESCE(first_name, ''), ' ', COALESCE(last_name, '')))
WHERE canonical_name IS NULL;

-- ============================================================================
-- EXTEND Supabase contact_identifiers
-- ============================================================================

ALTER TABLE contact_identifiers
ADD COLUMN IF NOT EXISTS sync_metadata JSONB DEFAULT '{}';

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON COLUMN contacts_master.sync_metadata IS 'Sync metadata for multi-source alignment';
COMMENT ON COLUMN contacts_master.llm_context IS 'Rich LLM context for dynamic prompting';
COMMENT ON COLUMN contacts_master.communication_stats IS 'Communication statistics and metrics';
COMMENT ON COLUMN contacts_master.social_network IS 'Social network context (groups, mutual connections)';
COMMENT ON COLUMN contacts_master.ai_insights IS 'AI-generated insights about the contact';
COMMENT ON COLUMN contacts_master.recommendations IS 'AI recommendations for interaction';
