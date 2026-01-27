# Supabase Schema - Unified User & Context System

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Design - Ready for Implementation
**Owner**: Jeremy Serna

---

## Overview

This schema unifies your existing contact categorization system (A-H, X categories with subcategories) with a multi-user, multi-code, multi-context deployment system for the truth-forge website.

**Key Features**:
- Multiple users with types and characteristics
- Multiple access codes per user
- Multiple conversation contexts
- Context qualities and metadata
- Unified with existing category/subcategory system
- Memory system integration

---

## Schema Design

### 1. `users` - Core User Registry

**Purpose**: Master user table for all users of the system (not just contacts, but actual system users)

```sql
CREATE TABLE users (
  -- Primary Identity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_code TEXT NOT NULL UNIQUE,              -- e.g., "CARTER", "HANNAH", "JEREMY"
  email TEXT UNIQUE,
  phone TEXT,
  
  -- Name Information
  first_name TEXT,
  last_name TEXT,
  full_name TEXT,
  nickname TEXT,
  display_name TEXT NOT NULL,                  -- Preferred display name
  
  -- User Type & Characteristics
  user_type TEXT NOT NULL DEFAULT 'standard',  -- standard, admin, code_holder, public
  user_tier TEXT,                              -- FREE, BASIC, PRO, PRO_PREDICTION, SPONSORED
  user_role TEXT,                              -- MODERATOR, CLIENT, CORPORATE
  
  -- Status
  is_active BOOLEAN DEFAULT true,
  is_verified BOOLEAN DEFAULT false,
  is_me BOOLEAN DEFAULT false,                 -- TRUE if this is Jeremy
  
  -- Metadata
  metadata JSONB DEFAULT '{}',                 -- Flexible storage for additional data
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  
  -- Indexes
  CONSTRAINT users_user_code_check CHECK (user_code = UPPER(user_code))
);

CREATE INDEX idx_users_user_code ON users(user_code);
CREATE INDEX idx_users_user_type ON users(user_type);
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_is_active ON users(is_active);
```

### 2. `user_characteristics` - User Characteristics & Traits

**Purpose**: Store characteristics, traits, and attributes about each user

```sql
CREATE TABLE user_characteristics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Characteristic Type
  characteristic_type TEXT NOT NULL,           -- interest, communication_style, ai_relationship, personality_trait, etc.
  characteristic_value TEXT NOT NULL,          -- The actual value
  characteristic_category TEXT,                -- Optional grouping
  
  -- Metadata
  confidence FLOAT DEFAULT 1.0,                -- 0.0-1.0 confidence in this characteristic
  source TEXT,                                 -- manual, ai_inferred, conversation, etc.
  notes TEXT,
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(user_id, characteristic_type, characteristic_value)
);

CREATE INDEX idx_user_characteristics_user_id ON user_characteristics(user_id);
CREATE INDEX idx_user_characteristics_type ON user_characteristics(characteristic_type);
```

### 3. `access_codes` - Access Code Management

**Purpose**: Manage access codes for users (like CARTER, HANNAH, etc.)

```sql
CREATE TABLE access_codes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,                   -- e.g., "CARTER", "HANNAH", "GOOGLE"
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- Optional: link to specific user
  
  -- Code Configuration
  code_type TEXT NOT NULL DEFAULT 'standard',  -- standard, team, context_mode, public
  is_active BOOLEAN DEFAULT true,
  is_single_use BOOLEAN DEFAULT false,
  expires_at TIMESTAMPTZ,
  
  -- Usage Limits
  max_uses INTEGER,                            -- NULL = unlimited
  use_count INTEGER DEFAULT 0,
  
  -- Context Configuration
  default_context_id UUID,                     -- FK to contexts table
  
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
```

### 4. `contexts` - Conversation Contexts

**Purpose**: Define different conversation contexts (e.g., Google partnership, general chat, specific project)

```sql
CREATE TABLE contexts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  context_code TEXT NOT NULL UNIQUE,           -- e.g., "GOOGLE_PARTNERSHIP", "GENERAL", "CREDENTIAL_ATLAS"
  context_name TEXT NOT NULL,                   -- Display name
  
  -- Context Type
  context_type TEXT NOT NULL DEFAULT 'standard', -- standard, business, personal, project, team
  
  -- Context Configuration
  system_prompt TEXT,                          -- Custom system prompt for this context
  welcome_message TEXT,
  capabilities JSONB DEFAULT '[]',             -- Available tools/capabilities
  
  -- Relationship to Contacts (Unified System)
  category_code TEXT,                          -- A, B, C, D, E, F, G, H, X (from contact system)
  subcategory_code TEXT,                       -- e.g., "A1_IMMEDIATE_FAMILY_RAISED_TOGETHER"
  relationship_category TEXT,                   -- family, friend, romantic, professional, etc.
  
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
```

### 5. `context_qualities` - Context-Specific Qualities

**Purpose**: Store qualities, insights, and metadata specific to each context

```sql
CREATE TABLE context_qualities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  context_id UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,  -- Optional: user-specific quality
  
  -- Quality Type
  quality_type TEXT NOT NULL,                  -- insight, preference, constraint, goal, pattern, etc.
  quality_key TEXT NOT NULL,                    -- e.g., "communication_style", "key_concern", "success_metric"
  quality_value TEXT NOT NULL,                  -- The actual value
  
  -- Metadata
  confidence FLOAT DEFAULT 1.0,
  source TEXT,                                 -- manual, ai_inferred, conversation, etc.
  priority INTEGER DEFAULT 0,                  -- Higher = more important
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
```

### 6. `user_contexts` - User-Context Relationships

**Purpose**: Link users to contexts with relationship metadata

```sql
CREATE TABLE user_contexts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  context_id UUID NOT NULL REFERENCES contexts(id) ON DELETE CASCADE,
  access_code_id UUID REFERENCES access_codes(id) ON DELETE SET NULL,
  
  -- Relationship Metadata
  relationship_type TEXT,                      -- owner, participant, viewer, etc.
  relationship_status TEXT DEFAULT 'active',  -- active, inactive, archived
  
  -- Context-Specific User Data
  user_context_data JSONB DEFAULT '{}',        -- User-specific data for this context
  
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
```

### 7. `user_memory` - LLM Memory System (Unified)

**Purpose**: Store LLM conversation memory, unified with user and context system

```sql
CREATE TABLE user_memory (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  user_code TEXT,                              -- Denormalized for quick lookup
  context_id UUID REFERENCES contexts(id) ON DELETE SET NULL,
  
  -- Memory Data
  insights TEXT[],                             -- Array of insights
  topics TEXT[],                               -- Array of topics
  interests TEXT[],                            -- From user_model
  key_quotes TEXT[],                           -- Memorable quotes
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
```

### 8. `conversations` - Conversation Sessions

**Purpose**: Track conversation sessions with users in specific contexts

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id TEXT NOT NULL UNIQUE,             -- External session ID (from chat API)
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  user_code TEXT,                              -- Denormalized
  context_id UUID REFERENCES contexts(id) ON DELETE SET NULL,
  access_code_id UUID REFERENCES access_codes(id) ON DELETE SET NULL,
  
  -- Conversation Metadata
  message_count INTEGER DEFAULT 0,
  total_tokens INTEGER DEFAULT 0,
  has_files BOOLEAN DEFAULT false,
  
  -- Status
  status TEXT DEFAULT 'active',               -- active, completed, archived
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_message_at TIMESTAMPTZ
);

CREATE INDEX idx_conversations_session_id ON conversations(session_id);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_user_code ON conversations(user_code);
CREATE INDEX idx_conversations_context_id ON conversations(context_id);
```

### 9. `contacts_master` - Unified Contact System

**Purpose**: Link to your existing contact categorization system

```sql
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
  category_code TEXT,                          -- A, B, C, D, E, F, G, H, X
  subcategory_code TEXT,                       -- e.g., A1_IMMEDIATE_FAMILY_RAISED_TOGETHER
  relationship_category TEXT,                   -- family, friend, romantic, etc.
  
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
```

### 10. `contact_identifiers` - Contact Identifiers

**Purpose**: Store phone numbers, emails, social profiles for contacts

```sql
CREATE TABLE contact_identifiers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID NOT NULL REFERENCES contacts_master(id) ON DELETE CASCADE,
  
  -- Identifier Details
  identifier_type TEXT NOT NULL,               -- phone, email, social_profile, platform_id
  identifier_value TEXT NOT NULL,
  identifier_normalized TEXT,
  
  -- Source Information
  source_platform TEXT,                        -- apple_contacts, sms, grindr, chatgpt, zoom
  source_label TEXT,                           -- Mobile, Work, Home, etc.
  
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
  verification_status TEXT,                    -- verified, unverified, disputed
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  -- Constraints
  UNIQUE(contact_id, identifier_type, identifier_value)
);

CREATE INDEX idx_contact_identifiers_contact_id ON contact_identifiers(contact_id);
CREATE INDEX idx_contact_identifiers_type_value ON contact_identifiers(identifier_type, identifier_value);
CREATE INDEX idx_contact_identifiers_normalized ON contact_identifiers(identifier_normalized);
```

---

## Category & Subcategory Reference

### Category Codes
| Code | Category | Description |
|------|----------|-------------|
| **A** | Family | Immediate and extended family |
| **B** | Friends | Close friends, casual friends |
| **C** | Acquaintances | People you know but not well |
| **D** | Dating/Romantic | Current partner, dating, hookups |
| **E** | Ex-Romantic | Former romantic partners |
| **F** | Service Providers | Healthcare, financial, delivery |
| **G** | Professional/Coworkers | Work colleagues, business contacts |
| **H** | Hostile | People with negative relationships |
| **X** | Exclude | System, spam, group-only |

### Subcategory Examples
- **A1_IMMEDIATE_FAMILY_RAISED_TOGETHER**
- **B1_BEST_FRIENDS**, **B2_CORE_FRIENDS**, **B3_CASUAL_FRIENDS**
- **D1_CURRENT_PARTNER**, **D2_SERIOUS_DATING**
- **G1_CLOSE_COWORKER**, **G2_COWORKER**, **G3_BUSINESS_CONTACT**

---

## Relationships

```
users (1) ──→ (many) user_characteristics
users (1) ──→ (many) access_codes
users (1) ──→ (many) user_contexts ──→ (many) contexts
users (1) ──→ (1) user_memory
users (1) ──→ (1) contacts_master (if contact is also a user)

contexts (1) ──→ (many) context_qualities
contexts (1) ──→ (many) user_contexts
contexts (1) ──→ (many) user_memory

contacts_master (1) ──→ (many) contact_identifiers

access_codes (1) ──→ (many) conversations
access_codes (1) ──→ (1) contexts (default_context_id)
```

---

## Migration from Existing System

### From Redis Memory to Supabase

Your current Redis memory structure:
```typescript
interface UserMemory {
  userCode: string;
  userName: string;
  firstSeen: string;
  lastSeen: string;
  conversationCount: number;
  insights: string[];
  topics: string[];
  userModel: {
    interests: string[];
    communicationStyle: string;
    aiRelationship: string;
    notMeInterests: string[];
    keyQuotes: string[];
  };
}
```

Maps to `user_memory` table:
- `user_code` → `user_code`
- `userName` → Lookup from `users.display_name`
- `insights` → `insights[]`
- `userModel.interests` → `interests[]`
- `userModel.keyQuotes` → `key_quotes[]`
- `userModel.communicationStyle` → `communication_style`
- `userModel.aiRelationship` → `ai_relationship`

### From USER_PROFILES to Supabase

Your current `USER_PROFILES` in chat.ts:
```typescript
USER_PROFILES: {
  "CARTER": { name: "Carter Altman-Kaough", code: "CARTER", context: "..." },
  "HANNAH": { name: "Hannah Parker", code: "HANNAH", context: "..." },
  ...
}
```

Maps to:
- `users` table: Create user records
- `access_codes` table: Create code records linked to users
- `contexts` table: Create context records (e.g., "GOOGLE_PARTNERSHIP")
- `context_qualities` table: Store the context text as quality

---

## Example Queries

### Get User with Memory and Context
```sql
SELECT 
  u.*,
  um.insights,
  um.interests,
  um.key_quotes,
  c.context_name,
  cq.quality_value as context_insight
FROM users u
LEFT JOIN user_memory um ON u.user_code = um.user_code
LEFT JOIN user_contexts uc ON u.id = uc.user_id
LEFT JOIN contexts c ON uc.context_id = c.id
LEFT JOIN context_qualities cq ON c.id = cq.context_id
WHERE u.user_code = 'CARTER';
```

### Get All Users by Category
```sql
SELECT 
  u.*,
  cm.category_code,
  cm.subcategory_code,
  cm.relationship_category
FROM users u
LEFT JOIN contacts_master cm ON u.id = cm.user_id
WHERE cm.category_code = 'G'  -- Professional
ORDER BY cm.subcategory_code;
```

### Get Context Qualities for a User
```sql
SELECT 
  c.context_name,
  cq.quality_type,
  cq.quality_key,
  cq.quality_value
FROM contexts c
JOIN context_qualities cq ON c.id = cq.context_id
WHERE cq.user_id = (SELECT id FROM users WHERE user_code = 'HANNAH')
ORDER BY cq.priority DESC;
```

---

## Next Steps

1. **Create Supabase Project**: Set up new Supabase project
2. **Run Migrations**: Execute this schema in Supabase SQL editor
3. **Migrate Data**: 
   - Import existing contacts from BigQuery/Apple Contacts
   - Migrate Redis memory to `user_memory` table
   - Create users and access codes from `USER_PROFILES`
4. **Update Chat API**: Modify `/api/chat.ts` to use Supabase instead of Redis
5. **Add Row Level Security**: Configure RLS policies for multi-tenant security

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Design Complete - Ready for Implementation
