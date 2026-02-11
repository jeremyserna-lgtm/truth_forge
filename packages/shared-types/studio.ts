/**
 * Studio Types
 * Audio, video, and multimedia artifact generation and management
 */

// ============================================================================
// STUDIO FORMATS & MODES
// ============================================================================

/**
 * Output format for studio artifacts
 */
export type StudioFormat = 'mp3' | 'wav' | 'aac' | 'opus' | 'webm' | 'mp4' | 'mov';

/**
 * Studio generation mode
 */
export type StudioMode =
  | 'debate'
  | 'podcast'
  | 'dialogue'
  | 'monologue'
  | 'summary'
  | 'analysis'
  | 'narrative'
  | 'custom';

/**
 * Audio length classification
 */
export type AudioLength = 'short' | 'medium' | 'long';

/**
 * Studio artifact - generated multimedia content
 */
export interface StudioArtifact {
  id: string;
  mode: StudioMode;
  format: StudioFormat;
  duration: number; // seconds
  length: AudioLength;
  title: string;
  description?: string;
  source: {
    type: 'document' | 'atoms' | 'conversation' | 'custom';
    ids: string[]; // Document or atom IDs
    content?: string;
  };
  speakers?: Array<{
    id: string;
    name: string;
    role: string;
    voice?: string;
  }>;
  metadata?: {
    generatedModel?: string;
    generationTime?: number;
    temperature?: number;
    customParameters?: Record<string, unknown>;
  };
  status: 'generating' | 'complete' | 'failed';
  storageKey?: string;
  createdAt: number;
  completedAt?: number;
  error?: string;
}

// ============================================================================
// DYNAMIC STUDIO OPTIONS
// ============================================================================

/**
 * Option that can be dynamically selected in studio interface
 */
export interface DynamicStudioOption {
  id: string;
  label: string;
  value: string;
  description?: string;
  icon?: string;
  category?: string;
  enabled: boolean;
}

/**
 * Command type for dynamic studio operations
 */
export type CommandType =
  | 'generate'
  | 'regenerate'
  | 'pause'
  | 'resume'
  | 'cancel'
  | 'export'
  | 'publish'
  | 'delete';

/**
 * Dynamic command for studio operations
 */
export interface DynamicCommand {
  id: string;
  type: CommandType;
  artifactId?: string;
  parameters?: Record<string, unknown>;
  priority?: 'low' | 'normal' | 'high';
  executedAt?: number;
  result?: {
    success: boolean;
    message?: string;
    error?: string;
  };
}

// ============================================================================
// STUDIO SESSION
// ============================================================================

/**
 * Studio generation session
 */
export interface StudioSession {
  id: string;
  tenantId?: string;
  mode: StudioMode;
  createdAt: number;
  updatedAt: number;
  closedAt?: number;
  status: 'active' | 'paused' | 'completed' | 'failed';
  artifacts: StudioArtifact[];
  commands: DynamicCommand[];
  options?: DynamicStudioOption[];
  parameters?: {
    temperature?: number;
    voiceSettings?: Record<string, unknown>;
    qualityLevel?: 'low' | 'medium' | 'high';
    [key: string]: unknown;
  };
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard for StudioArtifact
 */
export function isStudioArtifact(obj: unknown): obj is StudioArtifact {
  if (typeof obj !== 'object' || obj === null) return false;
  const artifact = obj as Record<string, unknown>;
  return (
    typeof artifact.id === 'string' &&
    typeof artifact.mode === 'string' &&
    typeof artifact.format === 'string' &&
    typeof artifact.createdAt === 'number'
  );
}

/**
 * Type guard for StudioSession
 */
export function isStudioSession(obj: unknown): obj is StudioSession {
  if (typeof obj !== 'object' || obj === null) return false;
  const session = obj as Record<string, unknown>;
  return (
    typeof session.id === 'string' &&
    typeof session.mode === 'string' &&
    Array.isArray(session.artifacts)
  );
}
