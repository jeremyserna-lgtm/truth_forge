/**
 * Document Upload API - Vercel Serverless Function
 * POST /api/admin/upload
 * 
 * Handles multipart file upload for document processing
 */

import type { VercelRequest, VercelResponse } from '@vercel/node';
import { IncomingForm, Fields, Files } from 'formidable';
import { Redis } from '@upstash/redis';
import * as fs from 'fs';

// Initialize Redis for document storage
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

function parseForm(req: VercelRequest): Promise<{ fields: Fields; files: Files }> {
    return new Promise((resolve, reject) => {
        const form = new IncomingForm({
            multiples: false,
            maxFileSize: 10 * 1024 * 1024 // 10MB limit
        });

        form.parse(req, (err, fields, files) => {
            if (err) reject(err);
            else resolve({ fields, files });
        });
    });
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
    // Only allow POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        // Parse multipart form data
        const { fields, files } = await parseForm(req);

        const file = Array.isArray(files.file) ? files.file[0] : files.file;
        if (!file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        // Read file content
        const content = fs.readFileSync(file.filepath, 'utf-8');

        // Create document record
        const doc: Document = {
            id: `doc_${Date.now()}`,
            name: file.originalFilename || 'unnamed.txt',
            content,
            size: file.size,
            uploadedAt: new Date().toISOString(),
            tenantId: (Array.isArray(fields.tenantId) ? fields.tenantId[0] : fields.tenantId) || 'admin'
        };

        // Store in Redis (7 day expiry for processing queue)
        if (redis) {
            await redis.set(`document:${doc.id}`, doc, { ex: 7 * 24 * 60 * 60 });
        }

        // Clean up temp file
        fs.unlinkSync(file.filepath);

        return res.status(200).json({
            success: true,
            message: 'Document uploaded successfully',
            document: {
                id: doc.id,
                name: doc.name,
                size: doc.size,
                uploadedAt: doc.uploadedAt
            }
        });

    } catch (error: any) {
        console.error('Upload error:', error);
        return res.status(500).json({
            error: 'Upload failed',
            details: error.message
        });
    }
}
