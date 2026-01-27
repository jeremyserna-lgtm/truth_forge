-- Supabase Migration: Unified User & Context System
-- Version: 1.0.0
-- Date: 2026-01-27
-- 
-- This migration creates the unified schema for:
-- - Multiple users with types and characteristics
-- - Multiple access codes per user
-- - Multiple conversation contexts
-- - Context qualities and metadata
-- - Unified with existing category/subcategory system
-- - Memory system integration

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS - Core User Registry
-- ============================================================================

CREATE TABLE users (
  -- Primary Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_code TEXT NOT NULL UNIQUE,
  email TEXT UNIQUE,
  phone TEXT,
  
  -- Name Information
  first_name TEXT,
  last_name TEXT,
  full_name TEXT,
  nickname TEXT,
  display_name TEXT NOT NULL,
  
  -- User Type & Characteristics
  user_type TEXT NOT NULL DEFAULT 'standard',
  user_tier TEXT,
  user_role TEXT,
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  is_me BOOLEAN DEFAULT false,
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT users_user_code_check CHECK (user_code = UPPER(user_code))
);

CREATE INDEX idx_users_user_code ON users(user_code);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_is_active ON users(is_active);

-- ============================================================================
-- 2. USER_CHARACTERISTICS - User Characteristics & Traits
-- ============================================================================

CREATE TABLE user_characteristics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Characteristic Type
  characteristic_type TEXT NOT NULL,
  characteristic_value TEXT NOT NULL,
  characteristic_category TEXT,
  
  -- Metadata
  confidence FLOAT DEFAULT 1.0,
  source TEXT,
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(user_id, characteristic_type, characteristic_value)
);

CREATE INDEX idx_user_characteristics_user_id ON user_characteristics(user_id);
CREATE INDEX idx_user_characteristics_type ON user_characteristics(characteristic_type);

-- ============================================================================
-- 3. ACCESS_CODES - Access Code Management
-- ============================================================================

CREATE TABLE access_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Code Configuration
  code_type TEXT NOT NULL DEFAULT 'standard',
  is_active BOOLEAN DEFAULT true,
  is_single_use BOOLEAN DEFAULT false,
  expires_at TIMESTAMPTZ,
  
  -- Usage Limits
  max_uses INTEGER,
  use_count INTEGER DEFAULT 0,
  
  -- Context Configuration
  default_context_id UUID,
  
  -- Metadata
  description TEXT,
  metadata JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_used_at TIMESTAMPTZ,
  
  -- Constraints
  CONSTRAINT access_codes_code_check CHECK (code = UPPER(code))
);

CREATE INDEX idx_access_codes_code ON access_codes(code);
CREATE INDEX idx_access_codes_user_id ON access_codes(user_id);
CREATE INDEX idx_access_codes_is_active ON access_codes(is_active);

-- ============================================================================
-- 4. CONTEXTS - Conversation Contexts
-- ============================================================================

CREATE TABLE contexts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  context_code TEXT NOT NULL UNIQUE,
  context_name TEXT NOT NULL,
  
  -- Context Type
  context_type TEXT NOT NULL DEFAULT 'standard',
  
  -- Context Configuration
  system_prompt TEXT,
  welcome_message TEXT,
  capabilities JSONB DEFAULT '[]',
  
  -- Relationship to Contacts (Unified System)
  category_code TEXT,
  subcategory_code TEXT,
  relationship_category TEXT,
  
  -- Metadata
  description TEXT,
  metadata JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT contexts_context_code_check CHECK (context_code = UPPER(context_code)),
  CONSTRAINT contexts_category_code_check CHECK (
    category_code IS NULL OR category_code IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X')
  )
);

CREATE INDEX idx_contexts_context_code ON contexts(context_code);
CREATE INDEX idx_contexts_category_code ON contexts(category_code);
CREATE INDEX idx_contexts_is_active ON contexts(is_active);

-- Add foreign key for access_codes.default_context_id
ALTER TABLE access_codes 
ADD CONSTRAINT fk_access_codes_default_context 
FOREIGN KEY (default_context_id) REFERENCES contexts(id) ON DELETE SET NULL;

-- ============================================================================
-- 5. CONTEXT_QUALITIES - Context-Specific Qualities
-- ============================================================================

CREATE TABLE context_qualities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  context_id UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Quality Type
  quality_type TEXT NOT NULL,
  quality_key TEXT NOT NULL,
  quality_value TEXT NOT NULL,
  
  -- Metadata
  confidence FLOAT DEFAULT 1.0,
  source TEXT,
  priority INTEGER DEFAULT 0,
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(context_id, user_id, quality_key)
);

CREATE INDEX idx_context_qualities_context_id ON context_qualities(context_id);
CREATE INDEX idx_context_qualities_user_id ON context_qualities(user_id);
CREATE INDEX idx_context_qualities_quality_type ON context_qualities(quality_type);

-- ============================================================================
-- 6. USER_CONTEXTS - User-Context Relationships
-- ============================================================================

CREATE TABLE user_contexts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  context_id UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,
  access_code_id UUID REFERENCES access_codes(id) ON DELETE SET NULL,
  
  -- Relationship Metadata
  relationship_type TEXT,
  relationship_status TEXT DEFAULT 'active',
  
  -- Context-Specific User Data
  user_context_data JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed_at TIMESTAMPTZ,
  
  -- Constraints
  UNIQUE(user_id, context_id)
);

CREATE INDEX idx_user_contexts_user_id ON user_contexts(user_id);
CREATE INDEX idx_user_contexts_context_id ON user_contexts(context_id);
CREATE INDEX idx_user_contexts_access_code_id ON user_contexts(access_code_id);

-- ============================================================================
-- 7. USER_MEMORY - LLM Memory System (Unified)
-- ============================================================================

CREATE TABLE user_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  user_code TEXT,
  context_id UUID REFERENCES contexts(id) ON DELETE SET NULL,
  
  -- Memory Data
  insights TEXT[],
  topics TEXT[],
  interests TEXT[],
  key_quotes TEXT[],
  communication_style TEXT,
  ai_relationship TEXT,
  not_me_interests TEXT[],
  
  -- Conversation Tracking
  conversation_count INTEGER DEFAULT 0,
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  
  -- Metadata
  metadata JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(user_code, context_id)
);

CREATE INDEX idx_user_memory_user_code ON user_memory(user_code);
CREATE INDEX idx_user_memory_user_id ON user_memory(user_id);
CREATE INDEX idx_user_memory_context_id ON user_memory(context_id);

-- ============================================================================
-- 8. CONVERSATIONS - Conversation Sessions
-- ============================================================================

CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL UNIQUE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  user_code TEXT,
  context_id UUID REFERENCES contexts(id) ON DELETE SET NULL,
  access_code_id UUID REFERENCES access_codes(id) ON DELETE SET NULL,
  
  -- Conversation Metadata
  message_count INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,
  has_files BOOLEAN DEFAULT false,
  
  -- Status
  status TEXT DEFAULT 'active',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_message_at TIMESTAMPTZ
);

CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_code ON conversations(user_code);
CREATE INDEX idx_conversations_context_id ON conversations(context_id);

-- ============================================================================
-- 9. CONTACTS_MASTER - Unified Contact System
-- ============================================================================

CREATE TABLE contacts_master (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  -- Apple Contacts Identifiers (if applicable)
  apple_unique_id TEXT UNIQUE,
  apple_identity_unique_id TEXT,
  apple_link_id TEXT,
  
  -- Name Fields
  first_name TEXT,
  last_name TEXT,
  middle_name TEXT,
  nickname TEXT,
  name_suffix TEXT,
  title TEXT,
  full_name TEXT,
  name_normalized TEXT,
  
  -- Organization Fields
  organization TEXT,
  job_title TEXT,
  department TEXT,
  
  -- Relationship Categorization (Your Existing System)
  category_code TEXT,
  subcategory_code TEXT,
  relationship_category TEXT,
  
  -- Link to Users (if this contact is also a system user)
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  
  -- Metadata
  notes TEXT,
  birthday DATE,
  is_business BOOLEAN DEFAULT false,
  is_me BOOLEAN DEFAULT false,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  CONSTRAINT contacts_category_code_check CHECK (
    category_code IS NULL OR category_code IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'X')
  )
);

CREATE INDEX idx_contacts_master_user_id ON contacts_master(user_id);
CREATE INDEX idx_contacts_master_category_code ON contacts_master(category_code);
CREATE INDEX idx_contacts_master_name_normalized ON contacts_master(name_normalized);

-- ============================================================================
-- 10. CONTACT_IDENTIFIERS - Contact Identifiers
-- ============================================================================

CREATE TABLE contact_identifiers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID NOT NULL REFERENCES contacts_master(id) ON DELETE CASCADE,
  
  -- Identifier Details
  identifier_type TEXT NOT NULL,
  identifier_value TEXT NOT NULL,
  identifier_normalized TEXT,
  
  -- Source Information
  source_platform TEXT,
  source_label TEXT,
  
  -- Flags
  is_primary BOOLEAN DEFAULT false,
  is_private BOOLEAN DEFAULT false,
  
  -- Phone Components (if type = 'phone')
  country_code TEXT,
  area_code TEXT,
  local_number TEXT,
  
  -- Email Components (if type = 'email')
  email_domain TEXT,
  
  -- Social Profile (if type = 'social_profile')
  social_service TEXT,
  social_username TEXT,
  social_url TEXT,
  
  -- Metadata
  confidence FLOAT DEFAULT 1.0,
  verification_status TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(contact_id, identifier_type, identifier_value)
);

CREATE INDEX idx_contact_identifiers_contact_id ON contact_identifiers(contact_id);
CREATE INDEX idx_contact_identifiers_type_value ON contact_identifiers(identifier_type, identifier_value);
CREATE INDEX idx_contact_identifiers_normalized ON contact_identifiers(identifier_normalized);

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

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_characteristics_updated_at BEFORE UPDATE ON user_characteristics
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_access_codes_updated_at BEFORE UPDATE ON access_codes
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contexts_updated_at BEFORE UPDATE ON contexts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_context_qualities_updated_at BEFORE UPDATE ON context_qualities
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_contexts_updated_at BEFORE UPDATE ON user_contexts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_memory_updated_at BEFORE UPDATE ON user_memory
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contacts_master_updated_at BEFORE UPDATE ON contacts_master
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contact_identifiers_updated_at BEFORE UPDATE ON contact_identifiers
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS - Documentation
-- ============================================================================

COMMENT ON TABLE users IS 'Core user registry for all system users';
COMMENT ON TABLE user_characteristics IS 'User characteristics, traits, and attributes';
COMMENT ON TABLE access_codes IS 'Access code management for user authentication';
COMMENT ON TABLE contexts IS 'Conversation contexts with system prompts and configuration';
COMMENT ON TABLE context_qualities IS 'Context-specific qualities, insights, and metadata';
COMMENT ON TABLE user_contexts IS 'User-context relationships with metadata';
COMMENT ON TABLE user_memory IS 'LLM conversation memory unified with user and context system';
COMMENT ON TABLE conversations IS 'Conversation session tracking';
COMMENT ON TABLE contacts_master IS 'Unified contact system with category/subcategory categorization';
COMMENT ON TABLE contact_identifiers IS 'Contact identifiers (phone, email, social profiles)';
