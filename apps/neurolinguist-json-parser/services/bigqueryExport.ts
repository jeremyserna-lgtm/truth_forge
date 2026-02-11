/**
 * BigQuery Export Service
 * Handles direct export of validated entities to BigQuery via serverless API
 *
 * This service follows the DATA PROTECTION LAWS:
 * - Validates entities before export
 * - Uses batch load (never streaming)
 * - Creates backup before write
 * - Reports all errors
 */

import type { Conversation } from '../types';
import { exportToNativeSpineFormat, NativeSpineEntity } from './spineExport';
import { validateConversation, ValidationResult } from './exportValidation';

/**
 * BigQuery export result
 */
export interface BigQueryExportResult {
  success: boolean;
  error?: string;
  rows_written?: number;
  backup_table?: string;
  backup_rows?: number;
  table?: string;
  validation_errors?: string[];
  total_errors?: number;
}

/**
 * Export progress callback
 */
export type ExportProgressCallback = (progress: {
  stage: 'validating' | 'preparing' | 'uploading' | 'complete' | 'error';
  message: string;
  percentage: number;
}) => void;

/**
 * API base URL - uses relative path for same-origin, or configurable for dev
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

/**
 * Validate entities for BigQuery export (dry run)
 */
export async function validateForBigQuery(
  conversation: Conversation,
  options: {
    sourceFile?: string;
    includeWords?: boolean;
  } = {}
): Promise<{
  valid: boolean;
  entityCount: number;
  validationResult: ValidationResult;
  errors: string[];
}> {
  // First, validate conversation structure
  const validationResult = validateConversation(conversation);

  if (!validationResult.valid) {
    return {
      valid: false,
      entityCount: 0,
      validationResult,
      errors: validationResult.issues.map(i => `${i.code}: ${i.message}`),
    };
  }

  // Generate entities to validate
  const exportResult = await exportToNativeSpineFormat(conversation, {
    sourceFile: options.sourceFile,
    includeWords: options.includeWords ?? true,
  });

  // Call API in dry_run mode
  try {
    const response = await fetch(`${API_BASE_URL}/bigquery-export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        entities: exportResult.entities,
        dry_run: true,
      }),
    });

    const result = await response.json();

    return {
      valid: result.success,
      entityCount: exportResult.entities.length,
      validationResult,
      errors: result.validation_errors || [],
    };
  } catch (error) {
    return {
      valid: false,
      entityCount: exportResult.entities.length,
      validationResult,
      errors: [`API error: ${error instanceof Error ? error.message : 'Unknown error'}`],
    };
  }
}

/**
 * Export conversation directly to BigQuery
 */
export async function exportToBigQuery(
  conversation: Conversation,
  options: {
    sourceFile?: string;
    includeWords?: boolean;
    onProgress?: ExportProgressCallback;
  } = {}
): Promise<BigQueryExportResult> {
  const { onProgress } = options;

  try {
    // Stage 1: Validate
    onProgress?.({
      stage: 'validating',
      message: 'Validating conversation structure...',
      percentage: 10,
    });

    const validationResult = validateConversation(conversation);
    if (!validationResult.valid) {
      const errors = validationResult.issues
        .filter(i => i.level === 'error')
        .map(i => i.message);

      return {
        success: false,
        error: `Validation failed: ${validationResult.stats.errors} errors`,
        validation_errors: errors,
        total_errors: validationResult.stats.errors,
      };
    }

    // Stage 2: Prepare entities
    onProgress?.({
      stage: 'preparing',
      message: 'Generating BigQuery-compatible entities...',
      percentage: 30,
    });

    const exportResult = await exportToNativeSpineFormat(conversation, {
      sourceFile: options.sourceFile,
      includeWords: options.includeWords ?? true,
    });

    const entityCount = exportResult.entities.length;

    // Stage 3: Upload to BigQuery
    onProgress?.({
      stage: 'uploading',
      message: `Uploading ${entityCount.toLocaleString()} entities to BigQuery...`,
      percentage: 50,
    });

    const response = await fetch(`${API_BASE_URL}/bigquery-export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        entities: exportResult.entities,
        dry_run: false,
      }),
    });

    const result: BigQueryExportResult = await response.json();

    if (result.success) {
      onProgress?.({
        stage: 'complete',
        message: `Successfully exported ${result.rows_written?.toLocaleString()} rows`,
        percentage: 100,
      });
    } else {
      onProgress?.({
        stage: 'error',
        message: result.error || 'Export failed',
        percentage: 100,
      });
    }

    return result;
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';

    onProgress?.({
      stage: 'error',
      message: `Export failed: ${errorMessage}`,
      percentage: 100,
    });

    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Check if BigQuery export API is available
 */
export async function checkBigQueryApiStatus(): Promise<{
  available: boolean;
  message: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/bigquery-export`, {
      method: 'OPTIONS',
    });

    if (response.ok) {
      return {
        available: true,
        message: 'BigQuery export API is available',
      };
    }

    return {
      available: false,
      message: `API returned status ${response.status}`,
    };
  } catch (error) {
    return {
      available: false,
      message: `API not reachable: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
}

/**
 * Get export statistics for a conversation
 */
export async function getExportStats(
  conversation: Conversation,
  options: { includeWords?: boolean } = {}
): Promise<{
  totalEntities: number;
  byLevel: Record<number, number>;
  estimatedSize: string;
}> {
  const exportResult = await exportToNativeSpineFormat(conversation, {
    includeWords: options.includeWords ?? true,
  });

  const byLevel: Record<number, number> = {};
  for (const entity of exportResult.entities) {
    byLevel[entity.level] = (byLevel[entity.level] || 0) + 1;
  }

  // Estimate size (rough: ~500 bytes per entity average)
  const estimatedBytes = exportResult.entities.length * 500;
  let estimatedSize: string;

  if (estimatedBytes < 1024) {
    estimatedSize = `${estimatedBytes} B`;
  } else if (estimatedBytes < 1024 * 1024) {
    estimatedSize = `${(estimatedBytes / 1024).toFixed(1)} KB`;
  } else {
    estimatedSize = `${(estimatedBytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return {
    totalEntities: exportResult.entities.length,
    byLevel,
    estimatedSize,
  };
}
