// =============================================================================
// SOVEREIGN GENESIS - Unified Types
// =============================================================================

// --- VIEW STATES ---

export type GenesisView = 'atomizer' | 'interface' | 'studio';

// Atomizer sub-views (INGEST → REFINE → STORE → USE)
export type AtomizerView = 'ingest' | 'refine' | 'store' | 'interact' | 'studio' | 'architect';

// Interface sub-views
export enum InterfaceView {
  DASHBOARD = 'DASHBOARD',
  TERMINAL = 'TERMINAL',
  FIDELITY = 'FIDELITY',
  SEEING_SESSION = 'SEEING_SESSION',
  BOOTSTRAP = 'BOOTSTRAP',
  SPINE = 'SPINE'
}

// Studio tabs
export type StudioTab = 'chat' | 'code' | 'preview';

// --- ATOMIZER TYPES ---

// Semantic Level (What It Means)
export interface SemanticMetadata {
  theme: string;
  domain: string;
  abstraction_level: 'concrete' | 'conceptual' | 'abstract' | 'meta';
}

// Significance Level (Why It Matters)
export interface SignificanceMetadata {
  tier: 'Foundational' | 'Structural' | 'Insight' | 'Nuance' | 'Detail';
  novelty: number;
  actionability: number;
}

// Epistemic Level (How Certain)
export interface EpistemicMetadata {
  certainty: 'fact' | 'consensus' | 'claim' | 'speculation' | 'hypothesis';
  evidence_strength: number;
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
  sentiment: number;
  intensity: number;
  stakes: 'existential' | 'high' | 'medium' | 'low' | 'trivial';
  urgency: number;
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
  completeness: number;
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
  theme: string;
  significance: 'Fundamental' | 'Insight' | 'Prediction' | 'Nuance';
  tags: string[];
  dimension?: string;
  lens?: string;
  structure?: string;
  altitude?: string;
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
  enrichment_coverage?: number;
  last_enriched?: number;
}

export interface KnowledgeAtom {
  id: string;
  content: string;
  sourceFile: string;
  metadata?: AtomMetadata;
  embedding?: number[];
  embeddingStatus?: 'pending' | 'success' | 'failed';
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
  speakerName?: string;
}

export interface TokenUsage {
  used: number;
  limit: number;
}

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

// --- MODEL PROVIDER TYPES ---

export type ModelProvider = 'gemini' | 'ollama';

export type ModelId =
  | 'gemini-2.5-pro'
  | 'gemini-2.5-flash'
  | 'gemini-2.5-flash-lite'
  | 'llama4-scout'
  | 'llama3.2'
  | 'mistral';

export interface ModelConfig {
  id: ModelId;
  provider: ModelProvider;
  label: string;
  tokenLimit: number;
  description: string;
  strengths: string[];
  endpoint?: string;
  supportsStructuredOutput?: boolean;
  supportsEmbeddings?: boolean;
}

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

export interface ProviderStatus {
  provider: ModelProvider;
  available: boolean;
  models: string[];
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

export interface ContextAnalysis {
  summary?: string;
  trends?: string;
  gaps?: string;
  lastUpdated: number;
}

// --- STUDIO TYPES (Content Creation) ---

export type StudioFormat = 'Deep Dive' | 'Critique' | 'Briefing Doc' | 'Blog Post' | 'Podcast' | 'Debate' | 'Spoken Critique' | 'Brief' | 'Custom';
export type StudioMode = 'Text' | 'Audio';
export type AudioLength = 'Short' | 'Medium' | 'Long';

export interface StudioArtifact {
  id: string;
  title: string;
  type: StudioFormat;
  mode: StudioMode;
  content: string;
  audioUrl?: string;
  createdAt: number;
  metaAnalysis?: {
    keyPoints: string[];
    actionItems: string[];
    considerations: string[];
    tone: string;
    performance: string;
  };
}

// --- INTERFACE TYPES ---

export interface Metric {
  name: string;
  value: string | number;
  status: 'PASS' | 'FAIL' | 'WARNING' | 'OPTIMAL';
  description: string;
  trend?: 'up' | 'down' | 'stable';
}

export interface LogEntry {
  id: string;
  timestamp: string;
  type: 'DECISION' | 'TRUNCATION' | 'SYSTEM' | 'MANIFESTATION' | 'VALIDATION_PENALTY';
  message: string;
  metadata: {
    decision_source?: 'HUMAN_DECISION' | 'AI_DEFAULT' | 'EMPIRE_PROTOCOL';
    data_kept?: string;
    data_lost?: string;
    magic_numbers_detected?: number;
    layer?: string;
    validation_penalty_applied?: boolean;
  };
}

export interface InterfaceMessage {
  id: string;
  role: 'user' | 'model';
  content: string;
  metadata?: {
    emotion?: string;
    thoughtType?: string;
    cognitiveStage?: string;
    processingTime?: string;
    mode?: string;
  };
}

// Message type for Terminal component
export interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  metadata?: {
    emotion?: string;
    thoughtType?: string;
    cognitiveStage?: string;
    processingTime?: string;
    mode?: string;
  };
}

// Re-export from localLLMService
export { SOVEREIGN_SYSTEM_PROMPT } from '../services/localLLMService';

// --- APP BUILDER TYPES (Sovereign Studio) ---

export interface BuilderMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface GeneratedFile {
  path: string;
  content: string;
}

export interface AppProject {
  name: string;
  description: string;
  files: GeneratedFile[];
}

export interface BuildResult {
  success: boolean;
  launcher?: string;
  port?: number;
}

// --- ARCHITECT TYPES ---

export interface ImplementationStep {
  stepId: string;
  description: string;
  inputs: string[];
  expectedOutputs: string[];
  dependencies: string[];
}

export interface ArchitecturalPlan {
  planId: string;
  createdAt: number;
  sourceDocuments: string[];
  sourceAtoms: string[];
  goal: string;
  context: string;
  requirements: string[];
  implementationSteps: ImplementationStep[];
  successCriteria: string[];
  failureModes: string[];
  status: 'draft' | 'exported' | 'in_progress' | 'certified' | 'defect';
  handoffTo?: 'implementation_service' | 'certification_service' | 'break_detection';
}

// --- ADDITIONAL TYPES (for service compatibility) ---

export type SpinalLevel = 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7' | 'L8';

export interface NLPStats {
  sentiment: number;
  subjectivity: number;
  emotions: string[];
  readingLevel?: string;
}

export interface SpinalNode {
  id: string;
  level: SpinalLevel;
  content: string;
  metadata: {
    role?: string;
    topic?: string;
    sequence?: number;
    stats?: NLPStats;
  };
  children?: SpinalNode[];
}

export interface StructureCandidate {
  path: string;
  type: 'Array' | 'Object';
  count: number;
  sampleKeys: string[];
  depth: number;
}

export interface StructureAnalysis {
  candidates: StructureCandidate[];
  rawJson: unknown;
}

export interface ImportConfig {
  l8Path: string;
  l5Path: string;
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

export interface DynamicStudioOption {
  label: string;
  description: string;
  prompt_angle: string;
}

export interface GenesisConfig {
  paradigm: 'Seeing' | 'Prediction';
  mode: 'Continuous' | 'Frozen';
  errorSignal: 'Single (Validation-Seeking)' | 'Multi-Objective';
  relationship: 'Mutual Discovery' | 'Teacher-Student';
}

export interface JeremyArcMetric {
  stage5Density: number;
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
    confidenceLevel: number;
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
    coverage: number;
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
