/**
 * bigqueryExportService.ts — Knowledge Atom → BigQuery Writer
 *
 * Exports Knowledge Atoms to BigQuery's knowledge_atoms table.
 * Follows ALL data enforcement rules:
 *   - NEVER streaming inserts (batch only)
 *   - SafeBigQueryWriter pattern
 *   - WRITE_APPEND only
 *   - Full validation before write
 *   - DLQ for failed records
 *
 * This service generates the export payload. Actual BigQuery write
 * is performed either via:
 *   1. truth-forge MCP (when running in Claude Code)
 *   2. REST API via server proxy (when running in browser)
 *   3. NDJSON file export for manual load
 */

import type { KnowledgeAtom } from '../types';

// ============================================================
// TYPES
// ============================================================

export interface BigQueryAtomRow {
  id: string;
  content: string;
  source_file: string;
  source_file_path: string;
  source_system: string;
  source_pipeline: string;

  // Flattened metadata
  theme: string | null;
  domain: string | null;
  significance_tier: string | null;
  novelty: number | null;
  actionability: number | null;
  certainty: string | null;
  evidence_strength: number | null;
  temporal_scope: string | null;
  temporal_durability: string | null;
  sentiment: number | null;
  intensity: number | null;
  stakes: string | null;
  urgency: number | null;
  structural_type: string | null;
  complexity: string | null;
  completeness: number | null;

  // JSON fields
  relational_entities: string;   // JSON array
  relational_concepts: string;   // JSON array
  action_items: string;          // JSON array

  // Embedding
  embedding: number[] | null;
  embedding_status: string;
  embedding_model: string | null;

  // Enrichment
  enrichment_coverage: number;

  // Timestamps
  created_at: string;            // ISO 8601
  last_enriched: string | null;  // ISO 8601

  // Dedup
  content_hash: string;
}

export interface ExportResult {
  success: boolean;
  rowsExported: number;
  errors: ExportError[];
  dlqRecords: KnowledgeAtom[];
  exportPath?: string;
}

export interface ExportError {
  atomId: string;
  error: string;
  field?: string;
}

// ============================================================
// VALIDATION (Four Pillars: Fail-Safe + No Magic)
// ============================================================

/**
 * Validate an atom before export. Returns errors if invalid.
 * NEVER skip validation — data enforcement rule.
 */
function validateAtom(atom: KnowledgeAtom): ExportError[] {
  const errors: ExportError[] = [];

  if (!atom.id || atom.id.trim() === '') {
    errors.push({ atomId: atom.id || 'MISSING', error: 'Missing atom ID', field: 'id' });
  }

  if (!atom.content || atom.content.trim() === '') {
    errors.push({ atomId: atom.id, error: 'Missing content', field: 'content' });
  }

  if (!atom.sourceFile || atom.sourceFile.trim() === '') {
    errors.push({ atomId: atom.id, error: 'Missing source_file', field: 'sourceFile' });
  }

  if (atom.metadata?.affective?.sentiment != null) {
    const s = atom.metadata.affective.sentiment;
    if (s < -1 || s > 1) {
      errors.push({ atomId: atom.id, error: `Sentiment ${s} out of range [-1, 1]`, field: 'sentiment' });
    }
  }

  if (atom.metadata?.enrichment_coverage != null) {
    const c = atom.metadata.enrichment_coverage;
    if (c < 0 || c > 100) {
      errors.push({ atomId: atom.id, error: `Enrichment coverage ${c} out of range [0, 100]`, field: 'enrichment_coverage' });
    }
  }

  return errors;
}

// ============================================================
// TRANSFORMATION
// ============================================================

/**
 * Convert a KnowledgeAtom to a BigQuery-ready row.
 * Flattens the 12-dimensional metadata into columns.
 */
function atomToBigQueryRow(
  atom: KnowledgeAtom,
  sourceFilePath: string = '',
  sourceSystem: string = 'knowledge_atomizer',
  sourcePipeline: string = 'atom_forge'
): BigQueryAtomRow {
  const m = atom.metadata;

  return {
    id: atom.id,
    content: atom.content,
    source_file: atom.sourceFile,
    source_file_path: sourceFilePath,
    source_system: sourceSystem,
    source_pipeline: sourcePipeline,

    // Flattened semantic
    theme: m?.semantic?.theme || m?.theme || null,
    domain: m?.semantic?.domain || null,

    // Flattened significance
    significance_tier: m?.significance_analysis?.tier || m?.significance || null,
    novelty: m?.significance_analysis?.novelty ?? null,
    actionability: m?.significance_analysis?.actionability ?? null,

    // Flattened epistemic
    certainty: m?.epistemic?.certainty || null,
    evidence_strength: m?.epistemic?.evidence_strength ?? null,

    // Flattened temporal
    temporal_scope: m?.temporal?.scope || null,
    temporal_durability: m?.temporal?.durability || null,

    // Flattened affective
    sentiment: m?.affective?.sentiment ?? null,
    intensity: m?.affective?.intensity ?? null,
    stakes: m?.affective?.stakes || null,
    urgency: m?.affective?.urgency ?? null,

    // Flattened structural
    structural_type: m?.structural?.type || null,
    complexity: m?.structural?.complexity || null,
    completeness: m?.structural?.completeness ?? null,

    // JSON arrays
    relational_entities: JSON.stringify(m?.relational?.entities || []),
    relational_concepts: JSON.stringify(m?.relational?.concepts || []),
    action_items: JSON.stringify(m?.pragmatic?.action_items || []),

    // Embedding
    embedding: atom.embedding || null,
    embedding_status: atom.embeddingStatus || 'pending',
    embedding_model: atom.embedding ? 'text-embedding-004' : null,

    // Enrichment
    enrichment_coverage: m?.enrichment_coverage ?? 0,

    // Timestamps
    created_at: new Date(atom.createdAt).toISOString(),
    last_enriched: m?.last_enriched ? new Date(m.last_enriched).toISOString() : null,

    // Dedup hash
    content_hash: atom.id,  // SHA-256 is already the content hash
  };
}

// ============================================================
// EXPORT METHODS
// ============================================================

/**
 * Export atoms as NDJSON (Newline-Delimited JSON) for BigQuery batch load.
 * This is the safest export path — creates a file that can be loaded
 * via `bq load` or SafeBigQueryWriter.
 */
export function exportToNDJSON(
  atoms: KnowledgeAtom[],
  options: {
    sourceFilePath?: string;
    sourceSystem?: string;
    sourcePipeline?: string;
  } = {}
): ExportResult {
  const validRows: BigQueryAtomRow[] = [];
  const dlqRecords: KnowledgeAtom[] = [];
  const errors: ExportError[] = [];

  // Validate every atom — NEVER skip validation
  for (const atom of atoms) {
    const validationErrors = validateAtom(atom);
    if (validationErrors.length > 0) {
      errors.push(...validationErrors);
      dlqRecords.push(atom);  // Send to DLQ
      continue;
    }

    try {
      const row = atomToBigQueryRow(
        atom,
        options.sourceFilePath || '',
        options.sourceSystem || 'knowledge_atomizer',
        options.sourcePipeline || 'atom_forge'
      );
      validRows.push(row);
    } catch (e) {
      errors.push({
        atomId: atom.id,
        error: `Transformation failed: ${e instanceof Error ? e.message : String(e)}`
      });
      dlqRecords.push(atom);
    }
  }

  // Generate NDJSON content
  const ndjsonContent = validRows
    .map(row => JSON.stringify(row))
    .join('\n');

  // Create downloadable file
  const blob = new Blob([ndjsonContent], { type: 'application/x-ndjson' });
  const url = URL.createObjectURL(blob);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = `knowledge_atoms_export_${timestamp}.ndjson`;

  // Trigger download
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  return {
    success: dlqRecords.length === 0,
    rowsExported: validRows.length,
    errors,
    dlqRecords,
    exportPath: filename,
  };
}

/**
 * Generate the BigQuery load command for the exported NDJSON file.
 * User can run this in their terminal to load data.
 */
export function generateLoadCommand(
  ndjsonPath: string,
  project: string = 'flash-clover-464719-g1',
  dataset: string = 'knowledge_atoms',
  table: string = 'knowledge_atoms'
): string {
  return `bq load \\
  --source_format=NEWLINE_DELIMITED_JSON \\
  --replace=false \\
  ${project}:${dataset}.${table} \\
  ${ndjsonPath}`;
}

/**
 * Export atoms as a Python script that uses SafeBigQueryWriter.
 * This generates a ready-to-run script for the truth_forge environment.
 */
export function exportAsSafeBQScript(
  atoms: KnowledgeAtom[],
  options: {
    sourceSystem?: string;
    sourcePipeline?: string;
  } = {}
): string {
  const rows = atoms
    .filter(a => validateAtom(a).length === 0)
    .map(a => atomToBigQueryRow(a, '', options.sourceSystem, options.sourcePipeline));

  return `#!/usr/bin/env python3
"""
Auto-generated Knowledge Atom BigQuery loader.
Uses SafeBigQueryWriter — the ONLY approved write method.
Generated by Atom-Forge at ${new Date().toISOString()}
"""
import json
from google.cloud import bigquery
from pipelines.core.bigquery_safe import SafeBigQueryWriter

PROJECT_ID = "flash-clover-464719-g1"
DATASET = "knowledge_atoms"
TABLE = "knowledge_atoms"

client = bigquery.Client(project=PROJECT_ID)
writer = SafeBigQueryWriter(client, f"{PROJECT_ID}.{DATASET}.{TABLE}")

records = json.loads('''
${JSON.stringify(rows, null, 2)}
''')

print(f"Loading {len(records)} knowledge atoms...")
rows_written = writer.write_batch(records)
print(f"Successfully wrote {rows_written} atoms to BigQuery")
`;
}

/**
 * Get export statistics for a set of atoms.
 */
export function getExportStats(atoms: KnowledgeAtom[]): {
  total: number;
  valid: number;
  invalid: number;
  withEmbeddings: number;
  avgEnrichment: number;
  byCategory: Record<string, number>;
} {
  let valid = 0;
  let invalid = 0;
  let withEmbeddings = 0;
  let totalEnrichment = 0;
  const byCategory: Record<string, number> = {};

  for (const atom of atoms) {
    const errors = validateAtom(atom);
    if (errors.length > 0) {
      invalid++;
    } else {
      valid++;
    }

    if (atom.embedding && atom.embedding.length > 0) {
      withEmbeddings++;
    }

    totalEnrichment += atom.metadata?.enrichment_coverage ?? 0;

    const theme = atom.metadata?.semantic?.theme || atom.metadata?.theme || 'uncategorized';
    byCategory[theme] = (byCategory[theme] || 0) + 1;
  }

  return {
    total: atoms.length,
    valid,
    invalid,
    withEmbeddings,
    avgEnrichment: atoms.length > 0 ? totalEnrichment / atoms.length : 0,
    byCategory,
  };
}
