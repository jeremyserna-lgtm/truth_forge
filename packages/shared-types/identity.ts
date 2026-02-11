/**
 * Identity Architecture Types
 * From Document Service: meta-layers extracted from user documents to build consciousness architecture
 */

// ============================================================================
// META-LAYER TYPES
// ============================================================================

/**
 * Life Perspectives - how they view the world through different lenses
 * Examples: Family, Travel, Career, Health, Spirituality
 */
export interface LifePerspective {
  id: string;
  name: string; // e.g., "Family", "Travel"
  description: string; // What this means to them
  prominence: number; // 0-100 how often this appears
  keywords: string[];
  exampleAtoms: string[]; // Atom IDs that exemplify this
  confidence: number; // 0-1 extraction confidence
}

/**
 * History Layer - temporal layers of their life
 * Examples: Rural Childhood, Urban College, Young Family, Career Pivot
 */
export interface HistoryLayer {
  id: string;
  name: string; // e.g., "Rural Childhood"
  period?: {
    start?: string; // "early 2000s", "childhood"
    end?: string;
  };
  description: string;
  keyEvents: string[]; // Major events in this period
  characteristics: string[]; // Defining traits of this period
  exampleAtoms: string[];
  confidence: number;
}

/**
 * People - important individuals in their life
 */
export interface Person {
  id: string;
  name: string; // May be role-based: "Mom", "Professor"
  relationship: string; // "Parent", "Mentor", "Friend"
  significance: string; // Why they matter
  mentions: number; // How often they appear
  context: string[]; // What contexts they appear in
  exampleAtoms: string[];
  confidence: number;
}

/**
 * Primitives - fundamental concepts that shape their worldview
 * Examples: "Growth", "Connection", "Independence", "Justice"
 */
export interface Primitive {
  id: string;
  concept: string; // The core concept
  definition: string; // What it means to them
  manifestations: string[]; // How it shows up in their life
  frequency: number; // How foundational it is
  exampleAtoms: string[];
  confidence: number;
}

/**
 * Anchors - core values and principles
 * Examples: "Be there for family", "Keep learning", "Stay authentic"
 */
export interface Anchor {
  id: string;
  value: string; // The core value
  expression: string; // How they express it
  importance: number; // 0-100 centrality to identity
  conflictsWith?: string[]; // IDs of competing anchors
  supportsBy?: string[]; // IDs of supporting anchors
  exampleAtoms: string[];
  confidence: number;
}

// ============================================================================
// FURNACE PROCESSING TYPES
// ============================================================================

/**
 * Pattern - unnamed feeling now given vocabulary
 */
export interface Pattern {
  id: string;
  name: string; // The pattern name
  description: string; // What it is
  validation: string; // Why this resonates
  examples: string[]; // Atom IDs demonstrating it
  resonanceScore: number; // 0-100 how well this fits
}

/**
 * Expanded Atom - original atom processed through meta-layers
 */
export interface ExpandedAtom {
  originalAtomId: string;
  expansions: {
    perspective: string; // Which Life Perspective was applied
    expandedContent: string; // New insight through this lens
    confidence: number;
  }[];
  debates: {
    proposition: string;
    counterpoint: string;
    synthesis: string;
  }[];
  patterns: Pattern[];
}

// ============================================================================
// IDENTITY SYNTHESIS TYPES
// ============================================================================

/**
 * Purpose Statement - what the Not-Me exists to do
 * Examples:
 * - "Help Sarah manage her life so she can be there for family"
 * - "Help Sarah navigate grad school so she can be successful and grow"
 */
export interface PurposeStatement {
  id: string;
  statement: string; // The full purpose
  domain: string; // "life management", "grad school"
  goal: string; // "be there for family", "be successful"
  supportedBy: {
    perspectives: string[]; // IDs
    anchors: string[]; // IDs
    primitives: string[]; // IDs
  };
  strength: number; // 0-100 how well supported
}

/**
 * Identity synthesis - the coherent "Not-Me" that emerges
 */
export interface NotMeIdentity {
  id: string;
  tenantId: string;

  // Purpose statements - actionable identity
  purposes: PurposeStatement[];

  // Coherence metrics
  coherence: {
    overall: number; // 0-100 how unified the identity is
    tensions: string[]; // Competing values/goals
    strengths: string[]; // Clear, strong aspects
  };

  // Supporting structure
  basedOn: {
    documentCount: number;
    atomCount: number;
    perspectiveCount: number;
    historyLayerCount: number;
    peopleCount: number;
    primitiveCount: number;
    anchorCount: number;
  };

  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// COMPLETE CLIENT ARCHITECTURE
// ============================================================================

/**
 * The full consciousness architecture for a client
 */
export interface ClientArchitecture {
  tenantId: string;

  // Layer 1: Raw data
  documents: string[]; // Document IDs
  atoms: string[]; // Atom IDs

  // Layer 2: Meta-understanding
  metaLayers: {
    perspectives: LifePerspective[];
    history: HistoryLayer[];
    people: Person[];
    primitives: Primitive[];
    anchors: Anchor[];
  };

  // Layer 3: Furnace processing
  furnace: {
    expandedAtoms: ExpandedAtom[];
    patterns: Pattern[];
  };

  // Layer 4: Identity synthesis
  identity: NotMeIdentity;

  // Metadata
  lastProcessed: Date;
  processingStatus:
    | 'raw'
    | 'atoms_extracted'
    | 'meta_extracted'
    | 'furnace_processed'
    | 'identity_synthesized';
}

// ============================================================================
// PROCESSING PIPELINE TYPES
// ============================================================================

/**
 * Request to extract meta-layers from atoms and documents
 */
export interface MetaLayerExtractionRequest {
  tenantId: string;
  atomIds: string[];
  documentIds: string[];
}

/**
 * Response with extracted meta-layers
 */
export interface MetaLayerExtractionResponse {
  perspectives: LifePerspective[];
  history: HistoryLayer[];
  people: Person[];
  primitives: Primitive[];
  anchors: Anchor[];
  processingTime: number;
}

/**
 * Request to process atoms through the Furnace
 */
export interface FurnaceProcessingRequest {
  tenantId: string;
  atomIds: string[];
  metaLayers: ClientArchitecture['metaLayers'];
}

/**
 * Response with furnace-processed atoms
 */
export interface FurnaceProcessingResponse {
  expandedAtoms: ExpandedAtom[];
  patterns: Pattern[];
  processingTime: number;
}

/**
 * Request to synthesize identity from full architecture
 */
export interface IdentitySynthesisRequest {
  tenantId: string;
  architecture: ClientArchitecture;
}

/**
 * Response with synthesized identity
 */
export interface IdentitySynthesisResponse {
  identity: NotMeIdentity;
  processingTime: number;
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

/**
 * Type guard for NotMeIdentity
 */
export function isNotMeIdentity(obj: unknown): obj is NotMeIdentity {
  if (typeof obj !== 'object' || obj === null) return false;
  const identity = obj as Record<string, unknown>;
  return (
    typeof identity.id === 'string' &&
    typeof identity.tenantId === 'string' &&
    Array.isArray(identity.purposes)
  );
}

/**
 * Type guard for ClientArchitecture
 */
export function isClientArchitecture(obj: unknown): obj is ClientArchitecture {
  if (typeof obj !== 'object' || obj === null) return false;
  const arch = obj as Record<string, unknown>;
  return (
    typeof arch.tenantId === 'string' &&
    Array.isArray(arch.documents) &&
    Array.isArray(arch.atoms) &&
    typeof arch.metaLayers === 'object' &&
    typeof arch.lastProcessed === 'object'
  );
}
