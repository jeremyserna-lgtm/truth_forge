/**
 * API Contract Types
 * Defines request/response contracts between Document Service and Knowledge Atomizer
 */

import { KnowledgeAtom, EmbeddingStatus } from './atom';
import { Document, UploadedDocument } from './document';

// ============================================================================
// DOCUMENT UPLOAD (KA → DS)
// ============================================================================

/**
 * Request to upload a document from KA to DS
 */
export interface UploadDocumentRequest {
  tenantId?: string;
  document: UploadedDocument;
  tags?: string[];
  operationalCategory?: string;
  knowledgeCategory?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Response from document upload
 */
export interface UploadDocumentResponse {
  success: boolean;
  documentId: string;
  contentHash: string;
  storageKey: string;
  message?: string;
  error?: string;
}

// ============================================================================
// ATOM DISTILLATION (DS → KA)
// ============================================================================

/**
 * Request to distill atoms from document content
 */
export interface DistillRequest {
  documentId: string;
  content: string;
  tenantId?: string;
  parameters?: {
    minAtomLength?: number;
    maxAtomLength?: number;
    granularity?: 'fine' | 'medium' | 'coarse';
  };
}

/**
 * Response with distilled atoms
 */
export interface DistillResponse {
  atoms: Array<{
    content: string;
    sourceFile: string;
    confidence: number;
  }>;
  processingTime: number;
  atomCount: number;
  error?: string;
}

// ============================================================================
// ATOM ENRICHMENT (NEW - KA → DS for 12-dimension processing)
// ============================================================================

/**
 * Request to enrich atoms with 12-dimensional metadata
 */
export interface EnrichRequest {
  atoms: KnowledgeAtom[];
  tenantId?: string;
  dimensions?: Array<
    | 'semantic'
    | 'significance'
    | 'epistemic'
    | 'temporal'
    | 'relational'
    | 'dialectical'
    | 'affective'
    | 'pragmatic'
    | 'structural'
    | 'ontological'
    | 'normative'
  >;
  model?: string;
  parameters?: Record<string, unknown>;
}

/**
 * Response with enriched atoms
 */
export interface EnrichResponse {
  atoms: KnowledgeAtom[];
  enrichedCount: number;
  enrichmentModel: string;
  processingTime: number;
  error?: string;
}

// ============================================================================
// ATOM SYNCHRONIZATION (NEW - KA → DS)
// ============================================================================

/**
 * Request to sync atoms from KA to DS
 */
export interface SyncAtomsRequest {
  atoms: KnowledgeAtom[];
  tenantId?: string;
  documentId?: string;
  upsert?: boolean; // If true, update existing atoms; if false, only add new
  metadata?: Record<string, unknown>;
}

/**
 * Response from atom sync
 */
export interface SyncAtomsResponse {
  success: boolean;
  synced: number;
  skipped: number;
  errors: Array<{
    atomId: string;
    reason: string;
  }>;
  message?: string;
}

// ============================================================================
// BIGQUERY EXPORT
// ============================================================================

/**
 * Request to export atoms/documents to BigQuery
 */
export interface ExportToBigQueryRequest {
  tenantId?: string;
  dataType: 'atoms' | 'documents' | 'both';
  atoms?: KnowledgeAtom[];
  documents?: Document[];
  targetDataset?: string;
  targetTable?: string;
  includeMetadata?: boolean;
  incremental?: boolean;
}

/**
 * Response from BigQuery export
 */
export interface ExportToBigQueryResponse {
  success: boolean;
  recordsExported: number;
  dataset: string;
  table: string;
  estimatedCost?: number;
  message?: string;
  error?: string;
}

// ============================================================================
// STATISTICS & REPORTING
// ============================================================================

/**
 * Request for system statistics
 */
export interface StatsRequest {
  tenantId?: string;
  startDate?: number;
  endDate?: number;
  includeDocuments?: boolean;
  includeAtoms?: boolean;
  includeBigQuery?: boolean;
}

/**
 * Response with system statistics
 */
export interface StatsResponse {
  tenantId?: string;
  timestamp: number;
  documents?: {
    total: number;
    byType: Record<string, number>;
    byCategory: Record<string, number>;
    totalSize: number;
  };
  atoms?: {
    total: number;
    enriched: number;
    byEmbeddingStatus: Record<EmbeddingStatus, number>;
    averageConfidence: number;
  };
  bigQuery?: {
    rowsExported: number;
    lastExport: number;
    estimatedCost: number;
  };
}

// ============================================================================
// ERROR RESPONSE
// ============================================================================

/**
 * Standard error response
 */
export interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  timestamp: number;
}

/**
 * Type guard for error response
 */
export function isApiErrorResponse(obj: unknown): obj is ApiErrorResponse {
  if (typeof obj !== 'object' || obj === null) return false;
  const response = obj as Record<string, unknown>;
  return (
    response.success === false &&
    typeof response.error === 'object' &&
    response.error !== null &&
    typeof (response.error as Record<string, unknown>).code === 'string'
  );
}
