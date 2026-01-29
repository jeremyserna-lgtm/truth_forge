/**
 * Admin Routes - Document Management Portal
 */

import { Router } from 'express';
import multer from 'multer';
import { geminiService } from '../../services/gemini';
import { bigqueryService } from '../../services/bigquery';

interface Document {
    id: string;
    name: string;
    content: string;
    size: number;
    uploadedAt: string;
    tags: string[];
}

interface KnowledgeAtom {
    id: string;
    content: string;
    sourceFile: string;
    metadata?: any;
    embeddingStatus?: string;
    createdAt: number;
}

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

// In-memory storage for demo (replace with DB later)
const documents: Map<string, Document> = new Map();
const atoms: Map<string, KnowledgeAtom> = new Map();

/**
 * GET /admin/documents
 * List all documents
 */
router.get('/documents', (req, res) => {
    const docs = Array.from(documents.values());
    res.json({ documents: docs });
});

/**
 * POST /admin/upload
 * Upload a document
 */
router.post('/upload', upload.single('file'), (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    const doc: Document = {
        id: `doc_${Date.now()}`,
        name: req.file.originalname,
        content: req.file.buffer.toString('utf-8'),
        size: req.file.size,
        uploadedAt: new Date().toISOString(),
        tags: []
    };

    documents.set(doc.id, doc);

    res.json({
        message: 'Document uploaded successfully',
        document: doc
    });
});

/**
 * POST /admin/process/:documentId
 * Process document into atoms (one-click processing)
 */
router.post('/process/:documentId', async (req, res) => {
    const { documentId } = req.params;
    const doc = documents.get(documentId);

    if (!doc) {
        return res.status(404).json({ error: 'Document not found' });
    }

    try {
        // Step 1: Distill to atoms using Gemini
        console.log(`🧠 Distilling atoms from ${doc.name}...`);
        const extractedAtoms = await geminiService.distillToAtoms(doc.content, doc.name);

        // Step 2: Store atoms
        extractedAtoms.forEach(atom => atoms.set(atom.id, atom as any));

        // Step 3: Export to BigQuery
        console.log(`📤 Exporting ${extractedAtoms.length} atoms to BigQuery...`);
        await bigqueryService.exportAtoms(extractedAtoms, 'admin');

        res.json({
            message: 'Processing complete',
            atomsCreated: extractedAtoms.length,
            atoms: extractedAtoms
        });
    } catch (error: any) {
        console.error('Processing error:', error);
        res.status(500).json({
            error: 'Processing failed',
            details: error.message
        });
    }
});

/**
 * GET /admin/atoms
 * List all atoms
 */
router.get('/atoms', (req, res) => {
    const allAtoms = Array.from(atoms.values());
    res.json({ atoms: allAtoms });
});

/**
 * GET /admin/stats
 * Get statistics
 */
router.get('/stats', async (req, res) => {
    const bigqueryCount = await bigqueryService.getAtomCount('admin');

    res.json({
        documents: documents.size,
        atomsInMemory: atoms.size,
        atomsInBigQuery: bigqueryCount
    });
});

export default router;
