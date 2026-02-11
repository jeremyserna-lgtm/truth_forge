/**
 * Document Service Client
 *
 * Bridges Knowledge Atomizer (frontend) to Document Service (backend).
 * When DS is available, atoms are persisted to the backend + BigQuery.
 * When DS is unavailable, falls back to standalone mode (localStorage + direct Gemini).
 *
 * Pattern: ME (KA interface) → NOT-ME (DS processing) → HOLD (BigQuery persistence)
 */

import { KnowledgeAtom, AtomMetadata } from '../types';

const DS_BASE_URL = import.meta.env.VITE_DOCUMENT_SERVICE_URL || 'http://localhost:3001';
const RETRY_ATTEMPTS = 3;
const RETRY_DELAY_MS = 1000;

export type ConnectionStatus = 'connected' | 'disconnected' | 'checking';

/**
 * DocumentServiceError
 * Custom error class for Document Service API failures
 */
export class DocumentServiceError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public endpoint?: string
  ) {
    super(message);
    this.name = 'DocumentServiceError';
  }
}

/**
 * DocumentServiceClient
 * Manages communication with Document Service backend
 */
class DocumentServiceClient {
  private baseUrl: string;
  private status: ConnectionStatus = 'checking';
  private lastHealthCheck: number = 0;
  private healthCheckInterval: number = 30000; // 30 seconds

  constructor(baseUrl: string = DS_BASE_URL) {
    this.baseUrl = baseUrl;
    this.checkConnection();
  }

  // ==================== CONNECTION MANAGEMENT ====================

  /**
   * Check connection status to Document Service
   * Caches result for healthCheckInterval before rechecking
   */
  async checkConnection(): Promise<boolean> {
    const now = Date.now();

    // Return cached result if recently checked
    if (this.lastHealthCheck > 0 && now - this.lastHealthCheck < this.healthCheckInterval) {
      return this.status === 'connected';
    }

    this.lastHealthCheck = now;
    this.status = 'checking';

    try {
      await this.request<{ status: string }>('/health');
      this.status = 'connected';
      console.log('[DocumentServiceClient] Connected to Document Service');
      return true;
    } catch (error) {
      this.status = 'disconnected';
      console.warn('[DocumentServiceClient] Document Service unavailable:', error instanceof Error ? error.message : error);
      return false;
    }
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus {
    return this.status;
  }

  /**
   * Check if currently connected
   */
  isConnected(): boolean {
    return this.status === 'connected';
  }

  // ==================== ATOM OPERATIONS ====================

  /**
   * Sync atoms from KA to DS backend
   * Persists atoms to backend database and exports to BigQuery
   */
  async syncAtoms(
    atoms: KnowledgeAtom[],
    tenantId?: string
  ): Promise<{
    synced: number;
    exported: number;
    errors: string[];
  }> {
    if (!this.isConnected()) {
      throw new DocumentServiceError(
        'Document Service not connected. Cannot sync atoms.',
        503
      );
    }

    try {
      const response = await this.request<{
        synced: number;
        exported: number;
        errors: string[];
      }>('/integration/atoms/sync', {
        method: 'POST',
        body: JSON.stringify({
          atoms,
          tenantId,
        }),
      });

      console.log(`[DocumentServiceClient] Synced ${response.synced} atoms, exported ${response.exported}`);
      return response;
    } catch (error) {
      throw new DocumentServiceError(
        `Failed to sync atoms: ${error instanceof Error ? error.message : String(error)}`,
        undefined,
        '/integration/atoms/sync'
      );
    }
  }

  /**
   * Get atoms from DS backend with optional filtering
   */
  async getAtoms(options?: {
    tenantId?: string;
    limit?: number;
    enrichmentMin?: number;
    enrichmentMax?: number;
  }): Promise<{ atoms: KnowledgeAtom[]; total: number }> {
    if (!this.isConnected()) {
      throw new DocumentServiceError(
        'Document Service not connected. Cannot fetch atoms.',
        503
      );
    }

    try {
      const params = new URLSearchParams();
      if (options?.tenantId) params.append('tenantId', options.tenantId);
      if (options?.limit) params.append('limit', String(options.limit));
      if (options?.enrichmentMin !== undefined) params.append('enrichmentMin', String(options.enrichmentMin));
      if (options?.enrichmentMax !== undefined) params.append('enrichmentMax', String(options.enrichmentMax));

      const queryString = params.toString();
      const path = queryString ? `/integration/atoms?${queryString}` : '/integration/atoms';

      const response = await this.request<{
        atoms: KnowledgeAtom[];
        total: number;
      }>(path);

      console.log(`[DocumentServiceClient] Retrieved ${response.atoms.length} atoms from backend`);
      return response;
    } catch (error) {
      throw new DocumentServiceError(
        `Failed to get atoms: ${error instanceof Error ? error.message : String(error)}`,
        undefined,
        '/integration/atoms'
      );
    }
  }

  /**
   * Enrich atoms using DS backend (Gemini-powered 12-dimensional enrichment)
   * Processes atoms through LLM to add semantic depth
   */
  async enrichAtoms(
    atomIds: string[],
    dimensions?: string[]
  ): Promise<{
    enriched: KnowledgeAtom[];
    failed: string[];
  }> {
    if (!this.isConnected()) {
      throw new DocumentServiceError(
        'Document Service not connected. Cannot enrich atoms.',
        503
      );
    }

    try {
      const response = await this.request<{
        enriched: KnowledgeAtom[];
        failed: string[];
      }>('/integration/atoms/enrich', {
        method: 'POST',
        body: JSON.stringify({
          atomIds,
          dimensions,
        }),
      });

      console.log(`[DocumentServiceClient] Enriched ${response.enriched.length} atoms, ${response.failed.length} failed`);
      return response;
    } catch (error) {
      throw new DocumentServiceError(
        `Failed to enrich atoms: ${error instanceof Error ? error.message : String(error)}`,
        undefined,
        '/integration/atoms/enrich'
      );
    }
  }

  // ==================== DOCUMENT OPERATIONS ====================

  /**
   * Upload a document file and get back extracted atoms
   * Sends file as multipart/form-data to backend for processing
   */
  async uploadAndDistill(file: File): Promise<{
    document: { id: string; name: string; size: number };
    atoms: KnowledgeAtom[];
  }> {
    if (!this.isConnected()) {
      throw new DocumentServiceError(
        'Document Service not connected. Cannot upload document.',
        503
      );
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await this.requestWithFormData<{
        document: { id: string; name: string; size: number };
        atoms: KnowledgeAtom[];
      }>('/integration/documents/upload', {
        method: 'POST',
        body: formData,
      });

      console.log(
        `[DocumentServiceClient] Uploaded "${file.name}" and extracted ${response.atoms.length} atoms`
      );
      return response;
    } catch (error) {
      throw new DocumentServiceError(
        `Failed to upload document: ${error instanceof Error ? error.message : String(error)}`,
        undefined,
        '/integration/documents/upload'
      );
    }
  }

  // ==================== EXPORT OPERATIONS ====================

  /**
   * Export atoms to BigQuery
   * Persists atoms to BigQuery for long-term storage and analytics
   */
  async exportToBigQuery(
    atomIds: string[],
    tenantId?: string
  ): Promise<{
    exported: number;
    table: string;
  }> {
    if (!this.isConnected()) {
      throw new DocumentServiceError(
        'Document Service not connected. Cannot export to BigQuery.',
        503
      );
    }

    try {
      const response = await this.request<{
        exported: number;
        table: string;
      }>('/integration/export/bigquery', {
        method: 'POST',
        body: JSON.stringify({
          atomIds,
          tenantId,
        }),
      });

      console.log(`[DocumentServiceClient] Exported ${response.exported} atoms to BigQuery table: ${response.table}`);
      return response;
    } catch (error) {
      throw new DocumentServiceError(
        `Failed to export to BigQuery: ${error instanceof Error ? error.message : String(error)}`,
        undefined,
        '/integration/export/bigquery'
      );
    }
  }

  // ==================== CONTEXT OPERATIONS ====================

  /**
   * Save active context to DS (replaces localStorage)
   * Persists the current working context including atoms and analysis state
   */
  async saveContext(
    contextId: string,
    atoms: KnowledgeAtom[],
    analysis?: object
  ): Promise<boolean> {
    if (!this.isConnected()) {
      console.warn('[DocumentServiceClient] Document Service not connected. Falling back to localStorage.');
      return false;
    }

    try {
      const response = await this.request<{ success: boolean }>(
        '/integration/context/save',
        {
          method: 'POST',
          body: JSON.stringify({
            contextId,
            atoms,
            analysis,
          }),
        }
      );

      console.log(`[DocumentServiceClient] Saved context "${contextId}" with ${atoms.length} atoms`);
      return response.success;
    } catch (error) {
      console.warn(
        `[DocumentServiceClient] Failed to save context: ${error instanceof Error ? error.message : String(error)}`
      );
      return false;
    }
  }

  /**
   * Load saved context from DS
   * Retrieves previously saved working context
   */
  async loadContext(
    contextId: string
  ): Promise<{
    atoms: KnowledgeAtom[];
    analysis?: object;
  } | null> {
    if (!this.isConnected()) {
      console.warn('[DocumentServiceClient] Document Service not connected. Cannot load context.');
      return null;
    }

    try {
      const response = await this.request<{
        contextId: string;
        atoms: KnowledgeAtom[];
        analysis?: object;
        createdAt: string;
        updatedAt: string;
      }>(`/integration/context/${contextId}`);

      console.log(`[DocumentServiceClient] Loaded context "${contextId}" with ${response.atoms.length} atoms`);
      return {
        atoms: response.atoms,
        analysis: response.analysis,
      };
    } catch (error) {
      if (error instanceof DocumentServiceError && error.statusCode === 404) {
        console.log(`[DocumentServiceClient] Context "${contextId}" not found`);
        return null;
      }
      console.warn(
        `[DocumentServiceClient] Failed to load context: ${error instanceof Error ? error.message : String(error)}`
      );
      return null;
    }
  }

  // ==================== STATS ====================

  /**
   * Get combined statistics from DS
   * Returns overview of documents, atoms, enrichment coverage
   */
  async getStats(): Promise<{
    documents: number;
    atomsInMemory: number;
    atomsInBigQuery: number;
    enrichmentCoverage: number;
  }> {
    if (!this.isConnected()) {
      throw new DocumentServiceError(
        'Document Service not connected. Cannot fetch stats.',
        503
      );
    }

    try {
      const response = await this.request<{
        documents: number;
        atomsInMemory: number;
        atomsInBigQuery: number;
        enrichmentCoverage: number;
      }>('/integration/stats');

      console.log('[DocumentServiceClient] Retrieved statistics');
      return response;
    } catch (error) {
      throw new DocumentServiceError(
        `Failed to get stats: ${error instanceof Error ? error.message : String(error)}`,
        undefined,
        '/integration/stats'
      );
    }
  }

  // ==================== PRIVATE HELPERS ====================

  /**
   * Generic fetch wrapper with error handling and retry logic
   * Automatically manages connection status
   */
  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    return this.requestWithRetry<T>(path, { ...options });
  }

  /**
   * Fetch wrapper for FormData (multipart/form-data)
   * Does not set Content-Type header (browser sets it with boundary)
   */
  private async requestWithFormData<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    return this.requestWithRetry<T>(path, { ...options }, true);
  }

  /**
   * Internal method handling retries and error management
   */
  private async requestWithRetry<T>(
    path: string,
    options: RequestInit = {},
    isFormData: boolean = false
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= RETRY_ATTEMPTS; attempt++) {
      try {
        const requestOptions: RequestInit = {
          ...options,
          headers: {
            ...(options.headers || {}),
          },
        };

        // Set Content-Type for JSON requests (not FormData - browser sets multipart/form-data)
        if (!isFormData && !(options.body instanceof FormData)) {
          if (!requestOptions.headers) requestOptions.headers = {};
          const headers = requestOptions.headers as Record<string, string>;
          headers['Content-Type'] = 'application/json';
        }

        const response = await fetch(url, requestOptions);

        // Handle non-OK responses
        if (!response.ok) {
          let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

          try {
            const errorBody = await response.json();
            if (errorBody.message) {
              errorMessage = errorBody.message;
            }
          } catch {
            // If response is not JSON, use status message
          }

          const error = new DocumentServiceError(
            errorMessage,
            response.status,
            path
          );

          // Don't retry on client errors (4xx)
          if (response.status >= 400 && response.status < 500) {
            console.error(`[DocumentServiceClient] Client error on ${path}:`, errorMessage);
            throw error;
          }

          // For server errors (5xx), retry
          lastError = error;
          if (attempt < RETRY_ATTEMPTS) {
            const delay = RETRY_DELAY_MS * attempt;
            console.warn(
              `[DocumentServiceClient] Attempt ${attempt}/${RETRY_ATTEMPTS} failed (${response.status}). Retrying in ${delay}ms...`
            );
            await this.sleep(delay);
            continue;
          }
          throw error;
        }

        // Success - parse response
        const data = await response.json() as T;
        return data;
      } catch (error) {
        // Network errors or parsing errors
        if (error instanceof DocumentServiceError) {
          throw error;
        }

        lastError = error instanceof Error ? error : new Error(String(error));

        // Check if this is a network error
        if (lastError.message.includes('Failed to fetch') || lastError.message.includes('NetworkError')) {
          this.status = 'disconnected';
          console.error(`[DocumentServiceClient] Network error on ${path}:`, lastError.message);
        }

        if (attempt < RETRY_ATTEMPTS) {
          const delay = RETRY_DELAY_MS * attempt;
          console.warn(
            `[DocumentServiceClient] Attempt ${attempt}/${RETRY_ATTEMPTS} failed: ${lastError.message}. Retrying in ${delay}ms...`
          );
          await this.sleep(delay);
          continue;
        }

        throw new DocumentServiceError(
          `Request to ${path} failed after ${RETRY_ATTEMPTS} attempts: ${lastError.message}`,
          undefined,
          path
        );
      }
    }

    // This should not be reached, but as fallback
    throw lastError || new DocumentServiceError(
      `Request to ${path} failed`,
      undefined,
      path
    );
  }

  /**
   * Simple sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Singleton instance
export const documentServiceClient = new DocumentServiceClient();
export default documentServiceClient;
