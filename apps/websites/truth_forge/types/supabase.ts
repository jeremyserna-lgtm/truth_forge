/**
 * Supabase Database Types
 * Generated from supabase_migration.sql
 * 
 * These types match the Supabase schema for the unified user & context system.
 */

export type CategoryCode = 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'X';
export type UserType = 'standard' | 'admin' | 'code_holder' | 'public';
export type UserTier = 'FREE' | 'BASIC' | 'PRO' | 'PRO_PREDICTION' | 'SPONSORED';
export type UserRole = 'MODERATOR' | 'CLIENT' | 'CORPORATE';
export type ContextType = 'standard' | 'business' | 'personal' | 'project' | 'team';
export type CodeType = 'standard' | 'team' | 'context_mode' | 'public';
export type IdentifierType = 'phone' | 'email' | 'social_profile' | 'platform_id';
export type RelationshipCategory = 'family' | 'friend' | 'romantic' | 'professional' | 'acquaintance' | 'ex_romantic' | 'service_provider' | 'hostile';

// ============================================================================
// Database Table Types
// ============================================================================

export interface User {
  id: string;
  user_code: string;
  email?: string | null;
  phone?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  full_name?: string | null;
  nickname?: string | null;
  display_name: string;
  user_type: UserType;
  user_tier?: UserTier | null;
  user_role?: UserRole | null;
  is_active: boolean;
  is_verified: boolean;
  is_me: boolean;
  metadata: Record<string, any>;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  first_seen: string;
  last_seen: string;
}

export interface UserCharacteristic {
  id: string;
  user_id: string;
  characteristic_type: string;
  characteristic_value: string;
  characteristic_category?: string | null;
  confidence: number;
  source?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccessCode {
  id: string;
  code: string;
  user_id?: string | null;
  code_type: CodeType;
  is_active: boolean;
  is_single_use: boolean;
  expires_at?: string | null;
  max_uses?: number | null;
  use_count: number;
  default_context_id?: string | null;
  description?: string | null;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  last_used_at?: string | null;
}

export interface Context {
  id: string;
  context_code: string;
  context_name: string;
  context_type: ContextType;
  system_prompt?: string | null;
  welcome_message?: string | null;
  capabilities: string[];
  category_code?: CategoryCode | null;
  subcategory_code?: string | null;
  relationship_category?: RelationshipCategory | null;
  description?: string | null;
  metadata: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContextQuality {
  id: string;
  context_id: string;
  user_id?: string | null;
  quality_type: string;
  quality_key: string;
  quality_value: string;
  confidence: number;
  source?: string | null;
  priority: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserContext {
  id: string;
  user_id: string;
  context_id: string;
  access_code_id?: string | null;
  relationship_type?: string | null;
  relationship_status: string;
  user_context_data: Record<string, any>;
  created_at: string;
  updated_at: string;
  last_accessed_at?: string | null;
}

export interface UserMemory {
  id: string;
  user_id?: string | null;
  user_code?: string | null;
  context_id?: string | null;
  insights: string[];
  topics: string[];
  interests: string[];
  key_quotes: string[];
  communication_style?: string | null;
  ai_relationship?: string | null;
  not_me_interests: string[];
  conversation_count: number;
  first_seen: string;
  last_seen: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Conversation {
  id: string;
  session_id: string;
  user_id?: string | null;
  user_code?: string | null;
  context_id?: string | null;
  access_code_id?: string | null;
  message_count: number;
  total_tokens: number;
  has_files: boolean;
  status: string;
  created_at: string;
  updated_at: string;
  last_message_at?: string | null;
}

export interface ContactMaster {
  id: string;
  apple_unique_id?: string | null;
  apple_identity_unique_id?: string | null;
  apple_link_id?: string | null;
  first_name?: string | null;
  last_name?: string | null;
  middle_name?: string | null;
  nickname?: string | null;
  name_suffix?: string | null;
  title?: string | null;
  full_name?: string | null;
  name_normalized?: string | null;
  organization?: string | null;
  job_title?: string | null;
  department?: string | null;
  category_code?: CategoryCode | null;
  subcategory_code?: string | null;
  relationship_category?: RelationshipCategory | null;
  user_id?: string | null;
  notes?: string | null;
  birthday?: string | null;
  is_business: boolean;
  is_me: boolean;
  created_at: string;
  updated_at: string;
}

export interface ContactIdentifier {
  id: string;
  contact_id: string;
  identifier_type: IdentifierType;
  identifier_value: string;
  identifier_normalized?: string | null;
  source_platform?: string | null;
  source_label?: string | null;
  is_primary: boolean;
  is_private: boolean;
  country_code?: string | null;
  area_code?: string | null;
  local_number?: string | null;
  email_domain?: string | null;
  social_service?: string | null;
  social_username?: string | null;
  social_url?: string | null;
  confidence: number;
  verification_status?: string | null;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// Helper Types
// ============================================================================

export interface UserWithMemory extends User {
  memory?: UserMemory | null;
  contexts?: Context[];
  characteristics?: UserCharacteristic[];
}

export interface ContextWithQualities extends Context {
  qualities?: ContextQuality[];
  users?: User[];
}

export interface ContactWithIdentifiers extends ContactMaster {
  identifiers?: ContactIdentifier[];
  user?: User | null;
}

// ============================================================================
// Subcategory Code Constants
// ============================================================================

export const SUBCATEGORY_CODES = {
  // Family (A)
  A1_IMMEDIATE_FAMILY_RAISED_TOGETHER: 'A1_IMMEDIATE_FAMILY_RAISED_TOGETHER',
  A2_IMMEDIATE_FAMILY_RAISED_SEPARATELY: 'A2_IMMEDIATE_FAMILY_RAISED_SEPARATELY',
  A3_IMMEDIATE_FAMILY_ESTRANGED: 'A3_IMMEDIATE_FAMILY_ESTRANGED',
  A4_EXTENDED_FAMILY: 'A4_EXTENDED_FAMILY',
  
  // Friends (B)
  B1_BEST_FRIENDS: 'B1_BEST_FRIENDS',
  B2_CORE_FRIENDS: 'B2_CORE_FRIENDS',
  B3_CASUAL_FRIENDS: 'B3_CASUAL_FRIENDS',
  B4_CHILDHOOD_FRIEND: 'B4_CHILDHOOD_FRIEND',
  B5_WORK_FRIEND: 'B5_WORK_FRIEND',
  
  // Acquaintances (C)
  C1_ACQUAINTANCE_FREQUENT: 'C1_ACQUAINTANCE_FREQUENT',
  C2_ACQUAINTANCE_INFREQUENT: 'C2_ACQUAINTANCE_INFREQUENT',
  C3_ACQUAINTANCE_INACTIVE: 'C3_ACQUAINTANCE_INACTIVE',
  
  // Dating/Romantic (D)
  D1_CURRENT_PARTNER: 'D1_CURRENT_PARTNER',
  D2_SERIOUS_DATING: 'D2_SERIOUS_DATING',
  D3_CASUAL_DATING: 'D3_CASUAL_DATING',
  D4_FLIRTING: 'D4_FLIRTING',
  D5_HOOKUP: 'D5_HOOKUP',
  
  // Ex-Romantic (E)
  E1_EX_FRIENDLY: 'E1_EX_FRIENDLY',
  E2_EX_COMPLICATED: 'E2_EX_COMPLICATED',
  E3_EX_NO_CONTACT: 'E3_EX_NO_CONTACT',
  
  // Service Providers (F)
  F1_HEALTHCARE: 'F1_HEALTHCARE',
  F2_FINANCIAL: 'F2_FINANCIAL',
  F3_DELIVERY_FOOD: 'F3_DELIVERY_FOOD',
  F4_PERSONAL_SERVICES: 'F4_PERSONAL_SERVICES',
  
  // Professional/Coworkers (G)
  G1_CLOSE_COWORKER: 'G1_CLOSE_COWORKER',
  G2_COWORKER: 'G2_COWORKER',
  G3_BUSINESS_CONTACT: 'G3_BUSINESS_CONTACT',
  
  // Hostile (H)
  H1_CLOSE_HOSTILE: 'H1_CLOSE_HOSTILE',
  H2_DISTANT_HOSTILE: 'H2_DISTANT_HOSTILE',
  H3_STRANGER_HOSTILE: 'H3_STRANGER_HOSTILE',
  
  // Exclude (X)
  X1_SYSTEM: 'X1_SYSTEM',
  X2_SPAM: 'X2_SPAM',
  X3_GROUP_ONLY: 'X3_GROUP_ONLY',
} as const;

export type SubcategoryCode = typeof SUBCATEGORY_CODES[keyof typeof SUBCATEGORY_CODES];
