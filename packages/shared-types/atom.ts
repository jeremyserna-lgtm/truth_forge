/**
 * Unified Knowledge Atom Type
 * Combines the rich 12-dimensional metadata from Knowledge Atomizer (KA)
 * with multi-tenant and document service features from Document Service (DS)
 */

// ============================================================================
// 12-DIMENSIONAL METADATA INTERFACES (from Knowledge Atomizer)
// ============================================================================

/**
 * Semantic Dimension - meaning and linguistic content
 */
export interface SemanticMetadata {
  meanings: string[];
  concepts: string[];
  semanticDensity?: number;
  ambiguity?: number;
}

/**
 * Significance Dimension - importance and relevance
 */
export interface SignificanceMetadata {
  importance: number; // 0-1
  relevance: number; // 0-1
  topicalWeight?: number;
  contextualRelevance?: number;
}

/**
 * Epistemic Dimension - knowledge status and certainty
 */
export interface EpistemicMetadata {
  certainty: number; // 0-1 confidence level
  knowledgeType: 'empirical' | 'theoretical' | 'experiential' | 'speculative';
  sources?: string[]; // source references
  validationStatus?: 'unvalidated' | 'validated' | 'disputed';
}

/**
 * Temporal Dimension - time-related metadata
 */
export interface TemporalMetadata {
  timeframe?: string;
  era?: string;
  frequency?: string;
  seasonality?: string;
  causality?: {
    precedes?: string[];
    follows?: string[];
  };
}

/**
 * Relational Dimension - connections to other atoms and concepts
 */
export interface RelationalMetadata {
  relatedAtomIds?: string[];
  relatedConcepts?: string[];
  relationships?: Array<{
    targetId: string;
    type: string; // 'supports', 'contradicts', 'elaborates', etc.
    strength?: number; // 0-1
  }>;
}

/**
 * Dialectical Dimension - tensions, contradictions, synthesis
 */
export interface DialecticalMetadata {
  thesis?: string;
  antithesis?: string;
  synthesis?: string;
  tensions?: string[];
  paradoxes?: string[];
  complementaryPairs?: Array<[string, string]>;
}

/**
 * Affective Dimension - emotional and evaluative content
 */
export interface AffectiveMetadata {
  emotionalValence?: number; // -1 (negative) to 1 (positive)
  emotionalIntensity?: number; // 0-1
  sentiment?: 'positive' | 'negative' | 'neutral' | 'mixed';
  affectTags?: string[];
  personalResonance?: number; // 0-1
}

/**
 * Pragmatic Dimension - practical utility and application
 */
export interface PragmaticMetadata {
  actionability: number; // 0-1 how actionable
  applicableTo?: string[];
  useCase?: string;
  outcomes?: string[];
  implementation?: {
    steps?: string[];
    difficulty?: 'easy' | 'moderate' | 'hard';
    resources?: string[];
  };
}

/**
 * Structural Dimension - form and organization
 */
export interface StructuralMetadata {
  complexity: number; // 0-1
  coherence: number; // 0-1
  hierarchy?: string;
  dependencies?: string[];
  components?: string[];
  patterns?: string[];
}

/**
 * Ontological Dimension - being and categorical membership
 */
export interface OntologicalMetadata {
  category?: string;
  type?: string;
  essence?: string;
  universals?: string[];
  particulars?: string[];
  abstractionLevel?: 'concrete' | 'abstract' | 'meta';
}

/**
 * Normative Dimension - values, shoulds, rights
 */
export interface NormativeMetadata {
  values?: string[];
  norms?: string[];
  obligations?: string[];
  rights?: string[];
  ethicalDimensions?: string[];
  prescriptiveContent?: string;
}

/**
 * Enrichment tracking - which dimensions have been processed
 */
export interface EnrichmentTracking {
  enrichedDimensions: Array<keyof AtomMetadata>;
  enrichmentTimestamp?: number;
  enrichmentModel?: string;
  enrichmentVersion?: string;
}

/**
 * Complete Atom Metadata - combines all dimensions plus enrichment tracking
 */
export interface AtomMetadata {
  // 12-dimensional enrichment (from Knowledge Atomizer)
  semantic?: SemanticMetadata;
  significance?: SignificanceMetadata;
  epistemic?: EpistemicMetadata;
  temporal?: TemporalMetadata;
  relational?: RelationalMetadata;
  dialectical?: DialecticalMetadata;
  affective?: AffectiveMetadata;
  pragmatic?: PragmaticMetadata;
  structural?: StructuralMetadata;
  ontological?: OntologicalMetadata;
  normative?: NormativeMetadata;

  // Legacy fields (backward compatibility)
  summary?: string;
  tags?: string[];
  keywords?: string[];
  category?: string;

  // Enrichment tracking
  enrichment?: EnrichmentTracking;
}

/**
 * Embedding representation for vector similarity search
 */
export interface EmbeddingData {
  vector: number[];
  model: string;
  timestamp: number;
  dimensions: number;
}

/**
 * Status of embedding generation
 */
export enum EmbeddingStatus {
  PENDING = 'pending',
  GENERATING = 'generating',
  COMPLETE = 'complete',
  FAILED = 'failed',
}

/**
 * Unified Knowledge Atom
 * The canonical type that unifies Knowledge Atomizer and Document Service
 */
export interface KnowledgeAtom {
  /** SHA-256 hash of content for deduplication */
  id: string;

  /** The actual content of the atom */
  content: string;

  /** Source file reference (where this atom came from) */
  sourceFile?: string;

  /** Optional comprehensive metadata */
  metadata?: AtomMetadata;

  /** Optional vector embedding for similarity search */
  embedding?: EmbeddingData;

  /** Status of embedding generation */
  embeddingStatus?: EmbeddingStatus;

  /** Creation timestamp (number for universal JSON compatibility) */
  createdAt: number;

  // ========================================================================
  // Document Service Extensions (optional, backward-compatible)
  // ========================================================================

  /** Multi-tenant support (defaults to 'personal' for KA compatibility) */
  tenantId?: string;

  /** Link to source document (optional, for tracking provenance) */
  documentId?: string;

  /** Last modification timestamp (number for universal JSON compatibility) */
  updatedAt?: number;
}

/**
 * Type guard to check if an object is a valid KnowledgeAtom
 */
export function isKnowledgeAtom(obj: unknown): obj is KnowledgeAtom {
  if (typeof obj !== 'object' || obj === null) return false;
  const atom = obj as Record<string, unknown>;
  return (
    typeof atom.id === 'string' &&
    typeof atom.content === 'string' &&
    typeof atom.createdAt === 'number'
  );
}
