/**
 * Document Processing API - Vercel Serverless Function
 * POST /api/admin/process
 * 
 * Processes uploaded document into knowledge atoms and exports to BigQuery
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';
import { Redis } from '@upstash/redis';
import { distillToAtoms } from '../_lib/gemini-atomizer';
import { exportAtoms } from '../_lib/bigquery-atoms';

// Initialize Redis
let redis: Redis | null = null;
if (process.env.UPSTASH_REDIS_REST_URL && process.env.UPSTASH_REDIS_REST_TOKEN) {
    redis = new Redis({
        url: process.env.UPSTASH_REDIS_REST_URL,
        token: process.env.UPSTASH_REDIS_REST_TOKEN,
    });
}

interface Document {
    id: string;
    name: string;
    content: string;
    size: number;
    uploadedAt: string;
    tenantId: string;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
    // Only allow POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { documentId } = req.body;

        if (!documentId) {
            return res.status(400).json({ error: 'documentId required' });
        }

        // Retrieve document from Redis
        if (!redis) {
            return res.status(500).json({ error: 'Redis not configured' });
        }

        const doc = await redis.get<Document>(`document:${documentId}`);
        if (!doc) {
            return res.status(404).json({ error: 'Document not found' });
        }

        console.log(`🧠 Processing document: ${doc.name}`);

        // Step 1: Distill to atoms using Gemini
        const atoms = await distillToAtoms(doc.content, doc.name);
        console.log(`✅ Extracted ${atoms.length} knowledge atoms`);

        // Step 2: Export to BigQuery
        await exportAtoms(atoms, doc.tenantId);
        console.log(`✅ Exported to BigQuery`);

        // Step 3: Store processing result in Redis
        await redis.set(`processed:${documentId}`, {
            documentId,
            atomsCreated: atoms.length,
            processedAt: new Date().toISOString(),
            status: 'complete'
        }, { ex: 30 * 24 * 60 * 60 }); // 30 day retention

        return res.status(200).json({
            success: true,
            message: 'Processing complete',
            documentId,
            atomsCreated: atoms.length,
            atoms: atoms.map(a => ({
                id: a.id,
                content: a.content,
                significance: a.metadata?.significance,
                tags: a.metadata?.tags
            }))
        });

    } catch (error: any) {
        console.error('Processing error:', error);
        return res.status(500).json({
            error: 'Processing failed',
            details: error.message
        });
    }
}
