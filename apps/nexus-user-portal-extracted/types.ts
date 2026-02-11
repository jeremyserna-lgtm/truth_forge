export interface User {
  id: string;
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  address: string;
  avatar?: string;
  tier: SubscriptionTier;
}

export enum SubscriptionTier {
  STAGE_3_FROZEN = 'STAGE_3',
  STAGE_4_FLUID = 'STAGE_4',
  STAGE_5_STRUCTURAL = 'STAGE_5'
}

export enum AppContext {
  PORTAL = 'PORTAL',
  DATA_SYNTHESIS = 'DATA_SYNTHESIS',
  FOUNDRY = 'FOUNDRY',
  OBSERVABILITY = 'OBSERVABILITY'
}

export enum AppView {
  AUTH = 'AUTH',
  DASHBOARD = 'DASHBOARD'
}

export enum DashboardTab {
  ACCOUNT = 'ACCOUNT',
  BILLING = 'BILLING',
  SECURITY = 'SECURITY',
  NOTIFICATIONS = 'NOTIFICATIONS'
}

export enum DataLayer {
  RAW = 'RAW',
  SEMANTIC = 'SEMANTIC',
  PATTERN = 'PATTERN'
}

export enum SourceCategory {
  DOCUMENTS = 'DOCUMENTS',
  IMAGES = 'IMAGES',
  VIDEOS = 'VIDEOS',
  AUDIO = 'AUDIO',
  ARCHITECTURE = 'ARCHITECTURE'
}

export enum SynthesisPattern {
  SUMMARIZE = 'SUMMARIZE',
  KEY_POINTS = 'KEY_POINTS',
  CRITIQUE = 'CRITIQUE',
  DEBATE = 'DEBATE',
  DEEP_DIVE = 'DEEP_DIVE'
}

export enum SynthesisView {
  SOURCES = 'SOURCES',
  ARCHITECTURE = 'ARCHITECTURE',
  CHAT = 'CHAT',
  SYNTHESIZE = 'SYNTHESIZE'
}

export enum ChatMode {
  ENGAGE = 'ENGAGE',
  ORGANIZE = 'ORGANIZE',
  ASK = 'ASK'
}

export interface KnowledgeAtom {
  id: string;
  label: string;
  description: string;
  depth: number; // 1-10 indicating system depth
  resonance: number; // 0-100 indicating relevance
  type: 'axiom' | 'concept' | 'derivative';
}