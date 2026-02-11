/**
 * BigQuery Atoms Export - Shared utility for exporting knowledge atoms
 * Exports atoms to Truth Forge BigQuery entities_unified table
 */

import { BigQuery } from '@google-cloud/bigquery';
import type { KnowledgeAtom } from './gemini-atomizer';

const projectId = process.env.BIGQUERY_PROJECT || 'truth-forge';
const datasetId = process.env.BIGQUERY_DATASET || 'main';

const bigquery = new BigQuery({ projectId });

/**
 * Export knowledge atoms to entities_unified table
 */
export async function exportAtoms(
    atoms: KnowledgeAtom[],
    tenantId: string = 'admin'
): Promise<void> {
    const tableName = 'entities_unified';

    const rows = atoms.map(atom => ({
        entity_id: atom.id,
        entity_type: 'knowledge_atom',
        source: atom.sourceFile || 'document-service',
        content: atom.content,
        metadata: JSON.stringify({
            significance: atom.metadata?.significance,
            tags: atom.metadata?.tags,
            extractedAt: atom.metadata?.extractedAt
        }),
        tenant_id: tenantId,
        created_at: new Date(atom.createdAt).toISOString(),
        embedding_status: atom.embeddingStatus || 'pending'
    }));

    try {
        await bigquery
            .dataset(datasetId)
            .table(tableName)
            .insert(rows, {
                skipInvalidRows: false,
                ignoreUnknownValues: true
            });

        console.log(`✅ Exported ${rows.length} atoms to BigQuery`);
    } catch (error) {
        console.error('❌ BigQuery export failed:', error);
        throw error;
    }
}

/**
 * Query atoms from BigQuery
 */
export async function queryAtoms(
    tenantId: string = 'admin',
    limit: number = 100
): Promise<any[]> {
    const query = `
    SELECT 
      entity_id,
      content,
      source,
      metadata,
      created_at
    FROM \`${projectId}.${datasetId}.entities_unified\`
    WHERE entity_type = 'knowledge_atom'
      AND tenant_id = @tenantId
    ORDER BY created_at DESC
    LIMIT ${limit}
  `;

    const options = {
        query,
        params: { tenantId }
    };

    const [rows] = await bigquery.query(options);
    return rows;
}

/**
 * Get atom count for tenant
 */
export async function getAtomCount(tenantId: string = 'admin'): Promise<number> {
    const query = `
    SELECT COUNT(*) as count
    FROM \`${projectId}.${datasetId}.entities_unified\`
    WHERE entity_type = 'knowledge_atom'
      AND tenant_id = @tenantId
  `;

    const [rows] = await bigquery.query({
        query,
        params: { tenantId }
    });

    return rows[0]?.count || 0;
}
