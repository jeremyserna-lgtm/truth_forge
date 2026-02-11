# @truth-forge/shared-types

Unified type definitions for Truth Forge applications.

This package provides a single source of truth for types shared between:
- **Knowledge Atomizer** (frontend, React) - Rich 12-dimensional metadata
- **Document Service** (backend, Express) - Multi-tenant, OCR, BigQuery integration

## Package Structure

### Core Types

- **atom.ts** - Unified `KnowledgeAtom` type combining 12-dimensional metadata from KA with multi-tenant/document features from DS
- **document.ts** - Document service types: tenants, documents, extraction, uploading
- **chat.ts** - Unified messaging: `ChatMessage`, `ConversationSession`, `ChatRequest`/`ChatResponse`
- **identity.ts** - Consciousness architecture: meta-layers, furnace processing, identity synthesis

### Integration Types

- **api.ts** - API contracts between DS and KA:
  - Document upload/distillation
  - Atom enrichment (12-dimensions)
  - Atom synchronization
  - BigQuery export
  - Statistics/reporting

- **model.ts** - LLM configuration and usage tracking
- **federation.ts** - Multi-app coordination: architectural plans, handoffs, certification
- **studio.ts** - Audio/video generation: modes, artifacts, dynamic options

## Key Design Decisions

### Backward Compatibility

The unified `KnowledgeAtom` is designed for backward compatibility:
- Uses `number` for timestamps (universal JSON serialization)
- Document Service fields (`tenantId`, `documentId`, `updatedAt`) are optional
- Knowledge Atomizer works without them (defaults to `tenantId: 'personal'`)

### 12-Dimensional Metadata

From Knowledge Atomizer, fully integrated in unified atom:

1. **Semantic** - Meanings, concepts, linguistic content
2. **Significance** - Importance, relevance, weight
3. **Epistemic** - Certainty, knowledge type, validation
4. **Temporal** - Timeframes, eras, causality
5. **Relational** - Connections to other atoms
6. **Dialectical** - Tensions, synthesis, paradoxes
7. **Affective** - Emotions, valence, personal resonance
8. **Pragmatic** - Actionability, implementation, outcomes
9. **Structural** - Complexity, coherence, dependencies
10. **Ontological** - Category, essence, abstraction level
11. **Normative** - Values, obligations, ethics

### Type Guards

Most major types include type guard functions:
- `isKnowledgeAtom()`
- `isChatMessage()`
- `isConversationSession()`
- `isNotMeIdentity()`
- `isClientArchitecture()`
- etc.

## Usage

```typescript
import {
  KnowledgeAtom,
  Document,
  ChatMessage,
  ConversationSession,
  UploadDocumentRequest,
  NotMeIdentity,
} from '@truth-forge/shared-types';

// Create an atom with full metadata
const atom: KnowledgeAtom = {
  id: 'sha256hash',
  content: 'The atom content',
  sourceFile: 'original.txt',
  createdAt: Date.now(),
  tenantId: 'acme-corp', // Optional, for DS integration
  metadata: {
    semantic: {
      meanings: ['concept1', 'concept2'],
      concepts: ['related', 'ideas'],
    },
    significance: {
      importance: 0.8,
      relevance: 0.9,
    },
    // ... other dimensions
  },
};

// Type-safe API calls
const request: UploadDocumentRequest = {
  tenantId: 'acme-corp',
  document: { id: 'doc1', name: 'file.txt', content: '...', size: 1024 },
};

// Identity synthesis
const identity: NotMeIdentity = {
  id: 'identity1',
  tenantId: 'user-1',
  purposes: [
    {
      id: 'p1',
      statement: 'Help user be there for family',
      domain: 'life',
      goal: 'family support',
      supportedBy: { perspectives: [], anchors: [], primitives: [] },
      strength: 85,
    },
  ],
  coherence: { overall: 90, tensions: [], strengths: [] },
  basedOn: { /* counts */ },
  createdAt: new Date(),
  updatedAt: new Date(),
};
```

## Integration Points

### Knowledge Atomizer → Document Service

- **Upload**: `UploadDocumentRequest` → `UploadDocumentResponse`
- **Sync Atoms**: `SyncAtomsRequest` → `SyncAtomsResponse`
- **Enrich**: `EnrichRequest` → `EnrichResponse` (12-dimension processing)

### Document Service → Knowledge Atomizer

- **Distill**: `DistillRequest` → `DistillResponse`
- **Export**: `ExportToBigQueryRequest` → `ExportToBigQueryResponse`

### Shared Operations

- **Chat**: `ChatRequest`/`ChatResponse` with `ConversationSession`
- **Stats**: `StatsRequest` → `StatsResponse`
- **Federation**: `ArchitecturalPlan`, `HandoffEnvelope`, `FederationContract`
