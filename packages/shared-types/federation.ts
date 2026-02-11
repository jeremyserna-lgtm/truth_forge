/**
 * Federation Types
 * Architecture for multi-app coordination, handoffs, and implementation planning
 */

// ============================================================================
// ARCHITECTURAL PLANNING
// ============================================================================

/**
 * Step in an implementation plan
 */
export interface ImplementationStep {
  id: string;
  sequence: number;
  name: string;
  description: string;
  dependsOn?: string[]; // IDs of prerequisite steps
  estimatedHours?: number;
  assignedTo?: string;
  status: 'pending' | 'in_progress' | 'complete' | 'blocked';
  blockedReason?: string;
  artifacts?: string[]; // IDs of related artifacts
  completedAt?: number;
}

/**
 * Complete architectural plan for a feature or initiative
 */
export interface ArchitecturalPlan {
  id: string;
  name: string;
  description: string;
  objective: string;
  scope: string;
  constraints?: string[];
  assumptions?: string[];
  risks?: Array<{
    risk: string;
    probability: 'low' | 'medium' | 'high';
    impact: 'low' | 'medium' | 'high';
    mitigation?: string;
  }>;
  steps: ImplementationStep[];
  timeline?: {
    startDate: number;
    targetCompletionDate: number;
    criticalPath?: string[];
  };
  resources?: {
    team?: string[];
    budget?: number;
    infrastructure?: string[];
  };
  successCriteria?: string[];
  createdAt: number;
  updatedAt: number;
}

// ============================================================================
// HANDOFF & COORDINATION
// ============================================================================

/**
 * An artifact produced during implementation
 */
export interface ImplementationArtifact {
  id: string;
  name: string;
  type: 'code' | 'document' | 'data' | 'test' | 'design' | 'other';
  description?: string;
  sourceStep: string; // Step ID that produced this
  targetStep?: string; // Step ID that consumes this
  location: string; // File path, URL, or reference
  version?: string;
  createdAt: number;
  createdBy?: string;
  reviewed?: boolean;
  reviewedBy?: string;
  reviewedAt?: number;
}

/**
 * Handoff envelope for passing work between systems/teams
 */
export interface HandoffEnvelope {
  id: string;
  from: string; // Source app or team
  to: string; // Target app or team
  planId: string; // Related architectural plan
  artifacts: ImplementationArtifact[];
  status: 'pending' | 'received' | 'in_progress' | 'complete';
  context?: {
    currentState?: Record<string, unknown>;
    nextSteps?: string[];
    notes?: string;
  };
  createdAt: number;
  handedOffAt?: number;
  completedAt?: number;
}

// ============================================================================
// CERTIFICATION & VERIFICATION
// ============================================================================

/**
 * Result of certification/verification against criteria
 */
export interface CertificationResult {
  criterion: string;
  passed: boolean;
  evidence?: string;
  notes?: string;
  checkedAt: number;
  checkedBy?: string;
}

/**
 * Break resolution record - when implementation diverges from plan
 */
export interface BreakResolution {
  id: string;
  planId: string;
  issue: string;
  originalExpectation: string;
  actualBehavior: string;
  rootCause?: string;
  resolution: string;
  impact: 'low' | 'medium' | 'high';
  resolvedAt: number;
  resolvedBy?: string;
  certifications: CertificationResult[];
}

/**
 * Federation contract - defines handoff expectations and verification
 */
export interface FederationContract {
  id: string;
  handoffId: string;
  expectations: string[];
  certifications: CertificationResult[];
  breaks: BreakResolution[];
  fullyMet: boolean;
  verifiedAt: number;
  verifiedBy?: string;
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard for ArchitecturalPlan
 */
export function isArchitecturalPlan(obj: unknown): obj is ArchitecturalPlan {
  if (typeof obj !== 'object' || obj === null) return false;
  const plan = obj as Record<string, unknown>;
  return (
    typeof plan.id === 'string' &&
    typeof plan.name === 'string' &&
    Array.isArray(plan.steps) &&
    typeof plan.createdAt === 'number'
  );
}

/**
 * Type guard for HandoffEnvelope
 */
export function isHandoffEnvelope(obj: unknown): obj is HandoffEnvelope {
  if (typeof obj !== 'object' || obj === null) return false;
  const envelope = obj as Record<string, unknown>;
  return (
    typeof envelope.id === 'string' &&
    typeof envelope.from === 'string' &&
    typeof envelope.to === 'string' &&
    Array.isArray(envelope.artifacts)
  );
}
