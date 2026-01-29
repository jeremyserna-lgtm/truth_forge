/**
 * Core types for multi-tenant document management service
 */

// ============================================================================
// TENANT TYPES
// ============================================================================

export type TenantType = 'personal' | 'business' | 'client';

export interface TenantFeatures {
    operationalDocs: boolean;      // Receipts, contracts, ledgers
    knowledgeAtoms: boolean;       // Distillation and enrichment
    truthForgeSync: boolean;       // Export to BigQuery entities_unified
    customModels: boolean;         // Fine-tune Scout 4 models
    conversationalAssistant: boolean; // "Not_me" chat interface
}

export interface StorageConfig {
    type: 'local' | 'gcs' | 's3';
    path?: string;                 // For local storage
    bucket?: string;               // For cloud storage
    credentials?: any;             // Cloud credentials
    encryptionKey?: string;        // Optional encryption
}

export interface Tenant {
    id: string;
    name: string;
    type: TenantType;
    storageConfig: StorageConfig;
    features: TenantFeatures;
    createdAt: Date;
    metadata?: Record<string, any>;
}

// ============================================================================
// DOCUMENT TYPES
// ============================================================================

export type DocumentType = 'operational' | 'knowledge' | 'raw';
export type OperationalCategory = 'receipt' | 'contract' | 'ledger' | 'invoice' | 'other';
export type KnowledgeCategory = 'theory' | 'technical' | 'research' | 'notes' | 'other';

export interface DocumentMetadata {
    filename: string;
    mimeType: string;
    sizeBytes: number;
    uploadedAt: Date;
    tags?: string[];
    customFields?: Record<string, any>;
}

export interface Document {
    id: string;
    tenantId: string;
    type: DocumentType;
    category?: OperationalCategory | KnowledgeCategory;
    metadata: DocumentMetadata;
    storageUri: string;            // Adapter-specific URI
    ocrStatus?: 'pending' | 'completed' | 'failed';
    ocrText?: string;
    createdAt: Date;
    updatedAt: Date;
}

// ============================================================================
// OPERATIONAL DOCUMENT TYPES
// ============================================================================

export interface ExtractedOperationalData {
    amount?: number;
    currency?: string;
    date?: Date;
    vendor?: string;
    vendorAddress?: string;
    category?: string;
    taxId?: string;
    items?: Array<{
        description: string;
        quantity?: number;
        unitPrice?: number;
        totalPrice?: number;
    }>;
    confidence?: number;          // OCR/extraction confidence 0-1
}

export interface OperationalDocument extends Document {
    type: 'operational';
    category: OperationalCategory;
    extracted?: ExtractedOperationalData;
}

// ============================================================================
// KNOWLEDGE ATOM TYPES
// ============================================================================

export type AtomSignificance = 'Fundamental' | 'Insight' | 'Prediction' | 'Nuance';

export interface AtomMetadata {
    theme: string;
    significance: AtomSignificance;
    tags: string[];
    dimension?: string;            // Lens used to generate
    lens?: string;
    structure?: string;
    altitude?: string;
}

export interface KnowledgeAtom {
    id: string;
    tenantId: string;
    documentId: string;             // Source document
    content: string;
    metadata: AtomMetadata;
    embedding?: number[];
    embeddingStatus?: 'pending' | 'success' | 'failed';
    createdAt: Date;
    updatedAt: Date;
}

// ============================================================================
// CHAT / CONVERSATIONAL TYPES
// ============================================================================

export interface ChatMessage {
    role: 'user' | 'assistant' | 'system';
    content: string;
    timestamp: Date;
    metadata?: {
        documentRefs?: string[];      // Referenced document IDs
        atomRefs?: string[];          // Referenced atom IDs
        suggestions?: string[];       // AI suggestions for improvement
    };
}

export interface ConversationSession {
    id: string;
    tenantId: string;
    messages: ChatMessage[];
    contextDocuments?: string[];    // Active document IDs in context
    contextAtoms?: string[];        // Active atom IDs in context
    createdAt: Date;
    updatedAt: Date;
}

// ============================================================================
// STORAGE ADAPTER INTERFACE
// ============================================================================

export interface UploadOptions {
    tenantId: string;
    filename: string;
    mimeType: string;
    metadata?: Record<string, any>;
}

export interface StorageAdapter {
    upload(buffer: Buffer, options: UploadOptions): Promise<string>;
    download(uri: string): Promise<Buffer>;
    delete(uri: string): Promise<void>;
    list(tenantId: string, filters?: Record<string, any>): Promise<string[]>;
    exists(uri: string): Promise<boolean>;
}

// ============================================================================
// OCR TYPES
// ============================================================================

export interface BoundingBox {
    x: number;
    y: number;
    width: number;
    height: number;
}

export interface OCRWord {
    text: string;
    confidence: number;
    boundingBox?: BoundingBox;
}

export interface OCRResult {
    text: string;
    confidence: number;
    words?: OCRWord[];
    language?: string;
    provider?: 'tesseract' | 'google-vision' | 'aws-textract';
}

// ============================================================================
// INTEGRATION TYPES (Truth Forge)
// ============================================================================

export interface Entity {
    entity_id: string;
    entity_type: string;
    source: string;
    content: string;
    metadata: Record<string, any>;
    created_at: Date;
}

export interface EnrichedEntity extends Entity {
    enrichment_level: string;
    enrichment_data?: Record<string, any>;
}

export interface EmbeddedEntity extends EnrichedEntity {
    embedding: number[];
    embedding_model: string;
}

// ============================================================================
// API REQUEST/RESPONSE TYPES
// ============================================================================

export interface UploadDocumentRequest {
    tenantId: string;
    type: DocumentType;
    category?: OperationalCategory | KnowledgeCategory;
    tags?: string[];
}

export interface UploadDocumentResponse {
    documentId: string;
    storageUri: string;
    ocrStatus?: string;
}

export interface DistillDocumentRequest {
    documentId: string;
    tenantId: string;
    lens?: string;
}

export interface DistillDocumentResponse {
    atomIds: string[];
    count: number;
}

export interface ChatRequest {
    tenantId: string;
    sessionId?: string;
    message: string;
    contextDocuments?: string[];
}

export interface ChatResponse {
    sessionId: string;
    message: ChatMessage;
    suggestions?: string[];         // "Not_me" suggestions for data completeness
    dataCompletenessScore?: number; // 0-100 assessment of fine-tuning readiness
}
