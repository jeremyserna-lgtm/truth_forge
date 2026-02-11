/**
 * @truth-forge/shared-types
 * Unified type definitions for Truth Forge apps
 *
 * This package provides a single source of truth for types shared between:
 * - Knowledge Atomizer (frontend, React) - 12-dimensional metadata
 * - Document Service (backend, Express) - multi-tenant, OCR, BigQuery
 */

// ============================================================================
// ATOM TYPES - Knowledge Atomizer + Document Service
// ============================================================================
export type {
  SemanticMetadata,
  SignificanceMetadata,
  EpistemicMetadata,
  TemporalMetadata,
  RelationalMetadata,
  DialecticalMetadata,
  AffectiveMetadata,
  PragmaticMetadata,
  StructuralMetadata,
  OntologicalMetadata,
  NormativeMetadata,
  EnrichmentTracking,
  AtomMetadata,
  EmbeddingData,
  KnowledgeAtom,
} from './atom';

export { EmbeddingStatus, isKnowledgeAtom } from './atom';

// ============================================================================
// DOCUMENT TYPES - Document Service
// ============================================================================
export type {
  TenantType,
  TenantFeatures,
  StorageConfig,
  Tenant,
  DocumentType,
  OperationalCategory,
  KnowledgeCategory,
  DocumentMetadata,
  Document,
  ExtractedOperationalData,
  OperationalDocument,
  UploadedDocument,
} from './document';

// ============================================================================
// CHAT TYPES - Unified messaging
// ============================================================================
export type {
  ChatRole,
  ChatMessage,
  ConversationSession,
  ChatRequest,
  ChatResponse,
} from './chat';

export {
  getChatMessageText,
  isChatMessage,
  isConversationSession,
} from './chat';

// ============================================================================
// API TYPES - Document Service ↔ Knowledge Atomizer contracts
// ============================================================================
export type {
  UploadDocumentRequest,
  UploadDocumentResponse,
  DistillRequest,
  DistillResponse,
  EnrichRequest,
  EnrichResponse,
  SyncAtomsRequest,
  SyncAtomsResponse,
  ExportToBigQueryRequest,
  ExportToBigQueryResponse,
  StatsRequest,
  StatsResponse,
  ApiErrorResponse,
} from './api';

export { isApiErrorResponse } from './api';

// ============================================================================
// MODEL TYPES - LLM configuration and usage
// ============================================================================
export type {
  ModelProvider,
  ModelId,
  ModelConfig,
  ContextWindowState,
  ProviderStatus,
  TokenUsage,
  SessionTokenMetrics,
} from './model';

export {
  parseModelId,
  estimateCost,
  getContextRemaining,
} from './model';

// ============================================================================
// FEDERATION TYPES - Multi-app coordination
// ============================================================================
export type {
  ImplementationStep,
  ArchitecturalPlan,
  ImplementationArtifact,
  HandoffEnvelope,
  CertificationResult,
  BreakResolution,
  FederationContract,
} from './federation';

export {
  isArchitecturalPlan,
  isHandoffEnvelope,
} from './federation';

// ============================================================================
// STUDIO TYPES - Audio/video generation
// ============================================================================
export type {
  StudioFormat,
  StudioMode,
  AudioLength,
  StudioArtifact,
  DynamicStudioOption,
  CommandType,
  DynamicCommand,
  StudioSession,
} from './studio';

export {
  isStudioArtifact,
  isStudioSession,
} from './studio';

// ============================================================================
// IDENTITY TYPES - Consciousness architecture
// ============================================================================
export type {
  LifePerspective,
  HistoryLayer,
  Person,
  Primitive,
  Anchor,
  Pattern,
  ExpandedAtom,
  PurposeStatement,
  NotMeIdentity,
  ClientArchitecture,
  MetaLayerExtractionRequest,
  MetaLayerExtractionResponse,
  FurnaceProcessingRequest,
  FurnaceProcessingResponse,
  IdentitySynthesisRequest,
  IdentitySynthesisResponse,
} from './identity';

export {
  isNotMeIdentity,
  isClientArchitecture,
} from './identity';
