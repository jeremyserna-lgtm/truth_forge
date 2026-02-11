/**
 * Document Service Types
 * Types for multi-tenant document management, OCR, and BigQuery integration
 */

// ============================================================================
// TENANT TYPES
// ============================================================================

/**
 * Type of tenant (organization category)
 */
export type TenantType = 'individual' | 'organization' | 'enterprise';

/**
 * Features available to a tenant
 */
export interface TenantFeatures {
  maxDocumentsPerMonth: number;
  maxDocumentSizeBytes: number;
  supportedFileTypes: string[];
  ocrEnabled: boolean;
  bigQueryIntegration: boolean;
  customMetadata: boolean;
  apiAccess: boolean;
}

/**
 * Storage configuration for a tenant
 */
export interface StorageConfig {
  provider: 'gcs' | 'local' | 'hybrid';
  bucketName?: string;
  region?: string;
  retentionDays: number;
  redundancy: 'none' | 'regional' | 'multi-region';
}

/**
 * Complete Tenant entity
 */
export interface Tenant {
  id: string;
  name: string;
  type: TenantType;
  organizationId?: string;
  features: TenantFeatures;
  storage: StorageConfig;
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// DOCUMENT TYPES
// ============================================================================

/**
 * Type of document
 */
export type DocumentType =
  | 'pdf'
  | 'image'
  | 'text'
  | 'spreadsheet'
  | 'presentation'
  | 'video'
  | 'audio'
  | 'other';

/**
 * Operational categories (what the document does)
 */
export type OperationalCategory =
  | 'invoice'
  | 'receipt'
  | 'contract'
  | 'report'
  | 'directive'
  | 'procedure'
  | 'specification'
  | 'manual'
  | 'checklist'
  | 'form'
  | 'correspondence'
  | 'record'
  | 'other';

/**
 * Knowledge categories (what knowledge the document contains)
 */
export type KnowledgeCategory =
  | 'technical'
  | 'business'
  | 'personal'
  | 'educational'
  | 'reference'
  | 'planning'
  | 'analysis'
  | 'synthesis'
  | 'narrative'
  | 'regulatory'
  | 'other';

/**
 * Document metadata
 */
export interface DocumentMetadata {
  title: string;
  description?: string;
  author?: string;
  createdAt: Date;
  modifiedAt?: Date;
  fileSize: number;
  mimeType: string;
  pageCount?: number;
  language?: string;
  tags?: string[];
  operationalCategory?: OperationalCategory;
  knowledgeCategory?: KnowledgeCategory;
  customFields?: Record<string, unknown>;
}

/**
 * Complete Document entity
 */
export interface Document {
  id: string;
  tenantId: string;
  type: DocumentType;
  metadata: DocumentMetadata;
  content?: string; // Full text content (may be truncated in some contexts)
  contentHash: string; // SHA-256 hash of content for deduplication
  storageKey: string; // Path in storage system
  status: 'uploading' | 'processing' | 'ready' | 'failed' | 'archived';
  processingErrors?: string[];
  createdAt: Date;
  updatedAt: Date;
}

// ============================================================================
// EXTRACTED DATA TYPES
// ============================================================================

/**
 * Operational data extracted from documents
 * Structured, actionable information for workflows
 */
export interface ExtractedOperationalData {
  documentId: string;
  extractedAt: Date;
  fields: Array<{
    name: string;
    value: string | number | boolean | null;
    confidence: number; // 0-1
    source: 'ocr' | 'parsing' | 'manual' | 'llm';
  }>;
  tables?: Array<{
    name?: string;
    rows: Array<Record<string, unknown>>;
  }>;
  keyValues?: Record<string, unknown>;
}

/**
 * Document with operational data extracted
 */
export interface OperationalDocument extends Document {
  operationalData?: ExtractedOperationalData;
}

// ============================================================================
// UPLOAD TYPES
// ============================================================================

/**
 * Document uploaded from Knowledge Atomizer
 */
export interface UploadedDocument {
  id: string;
  name: string;
  content: string;
  size: number;
  tags?: string[];
  createdAt?: Date;
  mimeType?: string;
}
