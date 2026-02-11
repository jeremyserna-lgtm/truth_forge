/**
 * Documents API - Vercel Serverless Function
 * GET /api/admin/documents
 * 
 * Lists uploaded documents and their processing status
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';
import { Redis } from '@upstash/redis';
import { queryAtoms, getAtomCount } from '../_lib/bigquery-atoms';

// Initialize Redis
let redis: Redis | null = null;
if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    redis = new Redis({
        url: process.env.UPSTASH_REDIS_REST_URL,
        token: process.env.UPSTASH_REDIS_REST_TOKEN,
    });
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
    if (req.method === 'GET') {
        // GET /api/admin/documents - List all documents
        try {
            if (!redis) {
                return res.status(500).json({ error: 'Redis not configured' });
            }

            // Note: For production, you'd want to maintain a document index
            // For now, return a basic response
            return res.status(200).json({
                message: 'Document listing - use BigQuery to query atoms',
                note: 'Documents are stored temporarily in Redis for processing'
            });

        } catch (error: any) {
            console.error('Documents list error:', error);
            return res.status(500).json({
                error: 'Failed to list documents',
                details: error.message
            });
        }
    }

    if (req.method === 'POST' && req.url?.includes('/atoms')) {
        // POST /api/admin/documents/atoms - Query atoms from BigQuery
        try {
            const { tenantId = 'admin', limit = 100 } = req.body;

            const atoms = await queryAtoms(tenantId, limit);
            const count = await getAtomCount(tenantId);

            return res.status(200).json({
                success: true,
                count,
                atoms
            });

        } catch (error: any) {
            console.error('Atoms query error:', error);
            return res.status(500).json({
                error: 'Failed to query atoms',
                details: error.message
            });
        }
    }

    return res.status(405).json({ error: 'Method not allowed' });
}
