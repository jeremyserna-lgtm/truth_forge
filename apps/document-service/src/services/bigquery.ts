/**
 * BigQuery Export Service
 */

import { BigQuery } from '@google-cloud/bigquery';
import { KnowledgeAtom } from '../types';

export class BigQueryService {
    private bigquery: BigQuery;
    private projectId: string;
    private datasetId: string;

    constructor() {
        this.projectId = process.env.BIGQUERY_PROJECT || 'truth-forge';
        this.datasetId = process.env.BIGQUERY_DATASET || 'main';

        this.bigquery = new BigQuery({
            projectId: this.projectId
        });
    }

    /**
     * Export knowledge atoms to entities_unified table
     */
    async exportAtoms(atoms: KnowledgeAtom[], tenantId: string = 'admin'): Promise<void> {
        const tableName = 'entities_unified';

        const rows = atoms.map(atom => ({
            entity_id: atom.id,
            entity_type: 'knowledge_atom',
            source: (atom as any).sourceFile || 'unknown',
            content: atom.content,
            metadata: JSON.stringify({
                significance: atom.metadata?.significance,
                tags: atom.metadata?.tags
            }),
            tenant_id: tenantId,
            created_at: atom.createdAt instanceof Date ? atom.createdAt.toISOString() : new Date(atom.createdAt).toISOString(),
            embedding_status: atom.embeddingStatus || 'pending'
        }));

        try {
            await this.bigquery
                .dataset(this.datasetId)
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
    async queryAtoms(tenantId: string = 'admin', limit: number = 100): Promise<any[]> {
        const query = `
      SELECT 
        entity_id,
        content,
        source,
        metadata,
        created_at
      FROM \`${this.projectId}.${this.datasetId}.entities_unified\`
      WHERE entity_type = 'knowledge_atom'
        AND tenant_id = @tenantId
      ORDER BY created_at DESC
      LIMIT ${limit}
    `;

        const options = {
            query,
            params: { tenantId }
        };

        const [rows] = await this.bigquery.query(options);
        return rows;
    }

    /**
     * Get atom count for tenant
     */
    async getAtomCount(tenantId: string = 'admin'): Promise<number> {
        const query = `
      SELECT COUNT(*) as count
      FROM \`${this.projectId}.${this.datasetId}.entities_unified\`
      WHERE entity_type = 'knowledge_atom'
        AND tenant_id = @tenantId
    `;

        const [rows] = await this.bigquery.query({
            query,
            params: { tenantId }
        });

        return rows[0]?.count || 0;
    }
}

export const bigqueryService = new BigQueryService();
