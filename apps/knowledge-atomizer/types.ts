
export interface AtomMetadata {
  theme: string;
  significance: 'Fundamental' | 'Insight' | 'Prediction' | 'Nuance';
  tags: string[];
  dimension?: string; // The lens used to generate this atom
  // Multi-dimensional breakdown
  lens?: string;
  structure?: string;
  altitude?: string;
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

export type AppView = 'data' | 'genesis' | 'context' | 'enrichment' | 'clusters' | 'interact' | 'studio';

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

export type ModelId = 'gemini-3-pro-preview' | 'gemini-3-flash-preview' | 'gemini-flash-lite-latest';

export interface ModelConfig {
  id: ModelId;
  label: string;
  tokenLimit: number;
  description: string;
  strengths: string[];
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