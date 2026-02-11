
// --- COMPREHENSIVE ATOM METADATA SCHEMA ---
// Every atom is analyzed at ALL levels by default

// Semantic Level (What It Means)
export interface SemanticMetadata {
  theme: string;
  domain: string;
  abstraction_level: 'concrete' | 'conceptual' | 'abstract' | 'meta';
}

// Significance Level (Why It Matters)
export interface SignificanceMetadata {
  tier: 'Foundational' | 'Structural' | 'Insight' | 'Nuance' | 'Detail';
  novelty: number; // 0-1
  actionability: number; // 0-1
}

// Epistemic Level (How Certain)
export interface EpistemicMetadata {
  certainty: 'fact' | 'consensus' | 'claim' | 'speculation' | 'hypothesis';
  evidence_strength: number; // 0-1
  verifiability: 'observable' | 'testable' | 'logical' | 'intuitive';
}

// Temporal Level (When It Applies)
export interface TemporalMetadata {
  scope: 'universal' | 'historical' | 'current' | 'emerging' | 'future';
  durability: 'permanent' | 'durable' | 'transient' | 'ephemeral';
}

// Relational Level (What It Connects To)
export interface RelationalMetadata {
  entities: string[];
  concepts: string[];
  dependencies: string[];
  implications: string[];
}

// Dialectical Level (What It Opposes/Supports)
export interface DialecticalMetadata {
  supports: string[];
  contradicts: string[];
  tensions: string[];
  synthesis_potential: string;
}

// Affective Level (Emotional Valence)
export interface AffectiveMetadata {
  sentiment: number; // -1 to 1
  intensity: number; // 0-1
  stakes: 'existential' | 'high' | 'medium' | 'low' | 'trivial';
  urgency: number; // 0-1
}

// Pragmatic Level (What To Do)
export interface PragmaticMetadata {
  action_items: string[];
  preconditions: string[];
  consequences: string[];
  audience: string[];
}

// Structural Level (How It's Built)
export interface StructuralMetadata {
  type: 'claim' | 'definition' | 'comparison' | 'causation' | 'sequence' | 'classification';
  complexity: 'atomic' | 'compound' | 'nested';
  completeness: number; // 0-1
}

// Ontological Level (What Exists)
export interface OntologicalMetadata {
  entity_type: 'thing' | 'process' | 'relation' | 'property' | 'state';
  categories: string[];
  is_a: string[];
  has_parts: string[];
}

// Normative Level (What Should Be)
export interface NormativeMetadata {
  type: 'descriptive' | 'prescriptive' | 'evaluative';
  values_invoked: string[];
  should_statements: string[];
}

// Comprehensive Atom Metadata
export interface AtomMetadata {
  // LEGACY FIELDS (backward compatible)
  theme: string;
  significance: 'Fundamental' | 'Insight' | 'Prediction' | 'Nuance';
  tags: string[];
  dimension?: string;
  lens?: string;
  structure?: string;
  altitude?: string;

  // NEW: Full 12-dimensional analysis
  semantic?: SemanticMetadata;
  significance_analysis?: SignificanceMetadata;
  epistemic?: EpistemicMetadata;
  temporal?: TemporalMetadata;
  relational?: RelationalMetadata;
  dialectical?: DialecticalMetadata;
  affective?: AffectiveMetadata;
  pragmatic?: PragmaticMetadata;
  structural?: StructuralMetadata;
  ontological?: OntologicalMetadata;
  normative?: NormativeMetadata;

  // Enrichment tracking
  enrichment_coverage?: number; // 0-100, percentage of dimensions filled
  last_enriched?: number; // timestamp
}

export interface KnowledgeAtom {
  id: string; // Now a Hash
  content: string;
  sourceFile: string;
  metadata?: AtomMetadata;
  embedding?: number[]; // Vector representation
  embeddingStatus?: 'pending' | 'success' | 'failed'; // Status indicator
  createdAt: number;
}

export interface Cluster {
  id: string;
  label: string;
  centroid: KnowledgeAtom;
  items: KnowledgeAtom[];
}

export interface UploadedDocument {
  id: string;
  name: string;
  content: string;
  size: number;
  tags?: string[];
}

export interface ChatMessage {
  role: 'user' | 'model' | 'system';
  text: string;
  isError?: boolean;
  speakerName?: string; // For Debate mode (e.g., "Side A")
}

export interface TokenUsage {
  used: number;
  limit: number;
}

// Linear workflow: INGEST → REFINE → STORE → USE
export type AppView = 'ingest' | 'refine' | 'store' | 'interact' | 'studio' | 'architect' | 'triad';

export enum CommandType {
  BASIC = 'BASIC',
  META = 'META',
  DYNAMIC = 'DYNAMIC'
}

export interface DynamicCommand {
  label: string;
  prompt: string;
  description?: string;
}

// --- MODEL PROVIDER TYPES (Unified) ---

export type ModelProvider = 'gemini' | 'ollama';

// All supported model IDs across providers
export type ModelId =
  // Gemini Cloud models
  | 'gemini-2.5-pro'
  | 'gemini-2.5-flash'
  | 'gemini-2.5-flash-lite'
  // Local Ollama models
  | 'llama4-scout'
  | 'llama3.2'
  | 'mistral';

export interface ModelConfig {
  id: ModelId;
  provider: ModelProvider;
  label: string;
  tokenLimit: number;           // Max context window
  description: string;
  strengths: string[];
  endpoint?: string;            // For Ollama: base URL (default: http://localhost:11434)
  supportsStructuredOutput?: boolean;  // JSON mode support
  supportsEmbeddings?: boolean;        // Native embedding support
}

// Real-time context tracking
export interface ContextWindowState {
  tokensUsed: number;
  tokenLimit: number;
  percentUsed: number;
  modelId: ModelId;
  breakdown: {
    systemPrompt: number;
    documents: number;
    atoms: number;
    chatHistory: number;
    currentMessage: number;
  };
}

// Provider health/status
export interface ProviderStatus {
  provider: ModelProvider;
  available: boolean;
  models: string[];           // Available models from provider
  error?: string;
  lastChecked: number;
}

export interface DebateTopic {
  id: string;
  label: string;
  question: string;
}

export interface DebateTurn {
  speaker: 'Side A' | 'Side B' | 'Moderator' | 'Audience';
  text: string;
}

export interface DebateRound {
  roundNumber: number;
  turns: DebateTurn[];
}

// --- SPINAL ENRICHMENT TYPES ---

export type SpinalLevel = 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7' | 'L8';

export interface NLPStats {
  sentiment: number; // -1 to 1 (TextBlob simulation)
  subjectivity: number; // 0 to 1
  emotions: string[]; // NRCLex simulation
  readingLevel?: string; // TextStat simulation
}

export interface SpinalNode {
  id: string;
  level: SpinalLevel;
  content: string;
  metadata: {
    role?: string; // For L5/L6
    topic?: string; // For L7
    sequence?: number;
    stats?: NLPStats;
  };
  children?: SpinalNode[]; // L7 has L6 children, etc.
}

export interface StructureCandidate {
    path: string; // e.g., "root", "root[].mapping"
    type: 'Array' | 'Object';
    count: number;
    sampleKeys: string[];
    depth: number;
}

export interface StructureAnalysis {
    candidates: StructureCandidate[];
    rawJson: any;
}

export interface ImportConfig {
    l8Path: string; // Path to Conversations
    l5Path: string; // Path to Messages (relative to L8 if applicable)
}

export interface RecommendedAtom {
  atom: KnowledgeAtom;
  score: number;
  reason: string;
}

export interface StandardMessage {
    role: 'user' | 'model';
    content: string;
    timestamp?: number;
}

export interface ContextAnalysis {
    summary?: string;
    trends?: string;
    gaps?: string;
    lastUpdated: number;
}

// --- STUDIO TYPES ---

export type StudioFormat = 'Deep Dive' | 'Critique' | 'Briefing Doc' | 'Blog Post' | 'Podcast' | 'Debate' | 'Spoken Critique' | 'Brief' | 'Custom';
export type StudioMode = 'Text' | 'Audio';
export type AudioLength = 'Short' | 'Medium' | 'Long';

export interface StudioArtifact {
  id: string;
  title: string;
  type: StudioFormat;
  mode: StudioMode;
  content: string; // Markdown content or Transcript
  audioUrl?: string; // Blob URL
  createdAt: number;
  metaAnalysis?: {
    keyPoints: string[];
    actionItems: string[];
    considerations: string[];
    tone: string;
    performance: string;
  };
}

export interface DynamicStudioOption {
  label: string;
  description: string;
  prompt_angle: string;
}

// --- GENESIS / FINE-TUNING TYPES ---

export interface GenesisConfig {
    paradigm: 'Seeing' | 'Prediction';
    mode: 'Continuous' | 'Frozen';
    errorSignal: 'Single (Validation-Seeking)' | 'Multi-Objective';
    relationship: 'Mutual Discovery' | 'Teacher-Student';
}

export interface JeremyArcMetric {
    stage5Density: number; // 0-100%
    paradoxCount: number;
    metaCognitiveTokens: number;
    readiness: 'Not Ready' | 'Developing' | 'Converging' | 'Genesis Ready';
}

export interface TrainingExport {
    systemPrompt: string;
    datasetSize: number;
    estimatedEpochs: number;
    blobUrl: string;
}

// --- ARCHITECT / PLAN TYPES ---

export interface ImplementationStep {
  stepId: string;
  description: string;
  inputs: string[];
  expectedOutputs: string[];
  dependencies: string[]; // stepIds this depends on
}

export interface ArchitecturalPlan {
  planId: string;
  createdAt: number;
  sourceDocuments: string[]; // doc ids
  sourceAtoms: string[]; // atom ids

  goal: string;
  context: string;
  requirements: string[];

  implementationSteps: ImplementationStep[];

  successCriteria: string[];
  failureModes: string[];

  status: 'draft' | 'exported' | 'in_progress' | 'certified' | 'defect';
  handoffTo?: 'implementation_service' | 'certification_service' | 'break_detection';
}

export interface HandoffEnvelope {
  envelopeId: string;
  fromService: 'knowledge_atomizer' | 'implementation' | 'certification' | 'break_detection';
  toService: 'knowledge_atomizer' | 'implementation' | 'certification' | 'break_detection' | 'human';
  createdAt: number;

  payloadType: 'plan' | 'artifact' | 'certification' | 'break_resolution';
  payload: ArchitecturalPlan | ImplementationArtifact | CertificationResult | BreakResolution;

  lineage: Array<{
    service: string;
    envelopeId: string;
    timestamp: number;
  }>;

  context: {
    originalGoal: string;
    cycleCount: number;
    totalElapsed: number;
  };
}

export interface ImplementationArtifact {
  artifactId: string;
  sourcePlanId: string;
  createdAt: number;

  artifactType: 'code' | 'document' | 'config' | 'spec';
  content: string;
  location?: string;

  buildLog: Array<{
    stepId: string;
    action: string;
    result: 'success' | 'failure';
    errors?: string[];
  }>;

  selfAssessment: {
    completedSteps: string[];
    issuesEncountered: string[];
    confidenceLevel: number; // 0-100
  };
}

export interface CertificationResult {
  certificationId: string;
  artifactId: string;
  planId: string;
  certifiedAt: number;

  result: 'CERTIFIED' | 'DEFECT';

  verificationReport: {
    criteriaChecked: Array<{
      criterion: string;
      passed: boolean;
      evidence: string;
    }>;
    coverage: number; // percentage
    issuesFound: string[];
  };

  defectReport?: string;
}

export interface BreakResolution {
  breakId: string;
  source: 'knowledge_atomizer' | 'implementation' | 'certification';
  breakType: 'defect' | 'error' | 'timeout' | 'contradiction';
  detectedAt: number;

  analysis: {
    rootCause: string;
    affectedArtifacts: string[];
    severity: 'recoverable' | 'critical';
  };

  resolution: {
    action: 'retry' | 'revise_plan' | 'escalate_to_human' | 'quarantine';
    targetService?: string;
    instructions?: string;
  };
}