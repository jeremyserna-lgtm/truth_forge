/**
 * Integration Routes - Knowledge Atomizer ↔ Document Service
 *
 * These endpoints allow the Knowledge Atomizer frontend to use
 * Document Service as its persistent backend instead of localStorage.
 *
 * Pattern: HOLD₁ (KA uploads) → AGENT (DS processes) → HOLD₂ (BigQuery/Memory)
 */

import { Router } from 'express';
import multer from 'multer';
import { geminiService } from '../../services/gemini';
import { bigqueryService } from '../../services/bigquery';

// Types
interface KnowledgeAtom {
    id: string;
    content: string;
    sourceFile: string;
    metadata?: any;
    embeddingStatus?: string;
    createdAt: number;
}

interface IntegrationContext {
    contextId: string;
    atoms: KnowledgeAtom[];
    analysis?: object;
    savedAt: number;
}

// In-memory storage (consistent with admin/customer routes)
const atomsMemory: Map<string, KnowledgeAtom> = new Map();
const contextsMemory: Map<string, IntegrationContext> = new Map();
const documentsMemory: Map<string, any> = new Map();

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

/**
 * POST /integration/atoms/sync
 * Sync atoms from Knowledge Atomizer to Document Service
 * Stores in memory AND exports to BigQuery
 */
router.post('/atoms/sync', async (req, res) => {
    try {
        const { atoms, tenantId = 'default' } = req.body;

        if (!Array.isArray(atoms)) {
            return res.status(400).json({ error: 'atoms must be an array' });
        }

        const errors: string[] = [];
        let synced = 0;
        let exported = 0;

        // Store atoms in memory
        atoms.forEach((atom: any) => {
            try {
                const newAtom: KnowledgeAtom = {
                    id: atom.id || `atom_${Date.now()}_${Math.random()}`,
                    content: atom.content,
                    sourceFile: atom.sourceFile || 'knowledge-atomizer',
                    metadata: atom.metadata,
                    embeddingStatus: 'pending',
                    createdAt: Date.now()
                };
                atomsMemory.set(newAtom.id, newAtom);
                synced++;
            } catch (error: any) {
                errors.push(`Failed to store atom: ${error.message}`);
            }
        });

        // Export to BigQuery
        try {
            const atomsToExport = atoms.map((atom: any) => ({
                id: atom.id || `atom_${Date.now()}_${Math.random()}`,
                content: atom.content,
                sourceFile: atom.sourceFile || 'knowledge-atomizer',
                metadata: atom.metadata,
                embeddingStatus: 'pending',
                createdAt: new Date()
            }));

            await bigqueryService.exportAtoms(atomsToExport, tenantId);
            exported = atomsToExport.length;
        } catch (error: any) {
            console.error('BigQuery export error:', error);
            errors.push(`BigQuery export failed: ${error.message}`);
        }

        res.json({
            synced,
            exported,
            errors,
            message: errors.length === 0 ? 'Sync successful' : 'Sync completed with errors'
        });
    } catch (error: any) {
        console.error('Sync error:', error);
        res.status(500).json({
            error: 'Sync failed',
            details: error.message
        });
    }
});

/**
 * GET /integration/atoms
 * Get all atoms with optional filtering
 */
router.get('/atoms', async (req, res) => {
    try {
        const { tenantId = 'default', limit = 100, enrichmentMin = 0, enrichmentMax = 100 } = req.query;

        let atoms = Array.from(atomsMemory.values());

        // Filter by enrichment score if metadata contains enrichment data
        if (enrichmentMin || enrichmentMax) {
            const minScore = parseInt(enrichmentMin as string) || 0;
            const maxScore = parseInt(enrichmentMax as string) || 100;

            atoms = atoms.filter(atom => {
                const enrichmentScore = atom.metadata?.enrichment?.average_score || 0;
                return enrichmentScore >= minScore && enrichmentScore <= maxScore;
            });
        }

        // Apply limit
        const limitNum = Math.min(parseInt(limit as string) || 100, 1000);
        atoms = atoms.slice(0, limitNum);

        res.json({
            atoms,
            total: atomsMemory.size,
            returned: atoms.length
        });
    } catch (error: any) {
        console.error('Get atoms error:', error);
        res.status(500).json({
            error: 'Failed to retrieve atoms',
            details: error.message
        });
    }
});

/**
 * POST /integration/atoms/enrich
 * Enrich atoms with 12-dimensional metadata using Gemini
 */
router.post('/atoms/enrich', async (req, res) => {
    try {
        const { atomIds, dimensions } = req.body;

        if (!Array.isArray(atomIds)) {
            return res.status(400).json({ error: 'atomIds must be an array' });
        }

        const enriched: KnowledgeAtom[] = [];
        const failed: string[] = [];

        // Process each atom
        for (const atomId of atomIds) {
            const atom = atomsMemory.get(atomId);

            if (!atom) {
                failed.push(`Atom not found: ${atomId}`);
                continue;
            }

            try {
                console.log(`🧠 Enriching atom ${atomId}...`);

                // Use Gemini to enrich the atom
                const enrichmentData = await geminiService.enrichAtom(
                    { content: atom.content, metadata: atom.metadata },
                    dimensions
                );

                // Calculate average enrichment score
                const scores: number[] = [];
                Object.values(enrichmentData).forEach((dim: any) => {
                    if (dim?.score !== undefined) {
                        scores.push(dim.score);
                    }
                });
                const averageScore = scores.length > 0 ? scores.reduce((a, b) => a + b) / scores.length : 0;

                // Update atom with enrichment data
                const enrichedAtom: KnowledgeAtom = {
                    ...atom,
                    metadata: {
                        ...atom.metadata,
                        enrichment: {
                            ...enrichmentData,
                            average_score: averageScore,
                            dimensions_covered: Object.keys(enrichmentData).length,
                            enriched_at: new Date().toISOString()
                        }
                    },
                    embeddingStatus: 'enriched'
                };

                // Update in memory
                atomsMemory.set(atomId, enrichedAtom);
                enriched.push(enrichedAtom);

                console.log(`✅ Enriched atom ${atomId} with score ${averageScore.toFixed(1)}`);
            } catch (error: any) {
                failed.push(`Enrichment failed for ${atomId}: ${error.message}`);
                console.error(`❌ Enrichment error for ${atomId}:`, error);
            }
        }

        res.json({
            enriched,
            failed,
            message: failed.length === 0 ? 'All atoms enriched' : `Enriched ${enriched.length}, failed ${failed.length}`
        });
    } catch (error: any) {
        console.error('Enrich error:', error);
        res.status(500).json({
            error: 'Enrichment failed',
            details: error.message
        });
    }
});

/**
 * POST /integration/documents/upload
 * Upload document and distill to atoms in one operation
 */
router.post('/documents/upload', upload.single('file'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No file uploaded' });
        }

        const { tenantId = 'default' } = req.body;

        // Create document record
        const docId = `doc_${Date.now()}`;
        const documentContent = req.file.buffer.toString('utf-8');

        const document = {
            id: docId,
            name: req.file.originalname,
            size: req.file.size,
            uploadedAt: new Date().toISOString(),
            tenantId
        };

        documentsMemory.set(docId, document);

        // Step 1: Distill document to atoms using Gemini
        console.log(`📄 Uploading and distilling ${req.file.originalname}...`);
        const extractedAtoms = await geminiService.distillToAtoms(documentContent, req.file.originalname);

        // Step 2: Store atoms in memory
        const atomIds: string[] = [];
        extractedAtoms.forEach(atom => {
            const newAtom: KnowledgeAtom = {
                id: atom.id,
                content: atom.content,
                sourceFile: req.file!.originalname,
                metadata: {
                    ...atom.metadata,
                    documentId: docId
                },
                embeddingStatus: 'pending',
                createdAt: Date.now()
            };
            atomsMemory.set(atom.id, newAtom);
            atomIds.push(atom.id);
        });

        // Step 3: Export atoms to BigQuery
        try {
            await bigqueryService.exportAtoms(extractedAtoms, tenantId);
            console.log(`📤 Exported ${extractedAtoms.length} atoms to BigQuery`);
        } catch (error: any) {
            console.error('BigQuery export error:', error);
            // Non-fatal - continue even if BigQuery fails
        }

        res.json({
            document,
            atoms: extractedAtoms,
            atomCount: extractedAtoms.length,
            message: `Document processed: ${extractedAtoms.length} atoms created`
        });
    } catch (error: any) {
        console.error('Upload error:', error);
        res.status(500).json({
            error: 'Document upload/distillation failed',
            details: error.message
        });
    }
});

/**
 * POST /integration/export/bigquery
 * Export specific atoms to BigQuery
 */
router.post('/export/bigquery', async (req, res) => {
    try {
        const { atomIds, tenantId = 'default' } = req.body;

        if (!Array.isArray(atomIds)) {
            return res.status(400).json({ error: 'atomIds must be an array' });
        }

        // Collect atoms to export
        const atomsToExport: KnowledgeAtom[] = [];
        atomIds.forEach(id => {
            const atom = atomsMemory.get(id);
            if (atom) {
                atomsToExport.push(atom);
            }
        });

        if (atomsToExport.length === 0) {
            return res.status(400).json({ error: 'No valid atoms found to export' });
        }

        // Export to BigQuery
        await bigqueryService.exportAtoms(atomsToExport, tenantId);

        res.json({
            exported: atomsToExport.length,
            table: `${process.env.BIGQUERY_DATASET || 'main'}.entities_unified`,
            message: `Exported ${atomsToExport.length} atoms to BigQuery`
        });
    } catch (error: any) {
        console.error('BigQuery export error:', error);
        res.status(500).json({
            error: 'BigQuery export failed',
            details: error.message
        });
    }
});

/**
 * GET /integration/stats
 * Get combined statistics
 */
router.get('/stats', async (req, res) => {
    try {
        // Get BigQuery count
        const bigqueryCount = await bigqueryService.getAtomCount('default');

        // Calculate enrichment coverage
        const allAtoms = Array.from(atomsMemory.values());
        const enrichedAtoms = allAtoms.filter(a => a.metadata?.enrichment?.average_score !== undefined);
        const enrichmentCoverage = allAtoms.length > 0 ? (enrichedAtoms.length / allAtoms.length) * 100 : 0;

        res.json({
            documents: documentsMemory.size,
            atomsInMemory: atomsMemory.size,
            atomsInBigQuery: bigqueryCount,
            enrichmentCoverage: enrichmentCoverage.toFixed(1),
            contexts: contextsMemory.size
        });
    } catch (error: any) {
        console.error('Stats error:', error);
        res.status(500).json({
            error: 'Failed to get stats',
            details: error.message
        });
    }
});

/**
 * POST /integration/context/save
 * Save active context (replaces localStorage)
 */
router.post('/context/save', (req, res) => {
    try {
        const { contextId, atoms, analysis } = req.body;

        if (!contextId) {
            return res.status(400).json({ error: 'contextId is required' });
        }

        if (!Array.isArray(atoms)) {
            return res.status(400).json({ error: 'atoms must be an array' });
        }

        const context: IntegrationContext = {
            contextId,
            atoms,
            analysis,
            savedAt: Date.now()
        };

        contextsMemory.set(contextId, context);

        res.json({
            saved: true,
            contextId,
            atomCount: atoms.length,
            message: `Context saved with ${atoms.length} atoms`
        });
    } catch (error: any) {
        console.error('Context save error:', error);
        res.status(500).json({
            error: 'Failed to save context',
            details: error.message
        });
    }
});

/**
 * GET /integration/context/:contextId
 * Load saved context
 */
router.get('/context/:contextId', (req, res) => {
    try {
        const { contextId } = req.params;
        const context = contextsMemory.get(contextId);

        if (!context) {
            return res.status(404).json({ error: 'Context not found' });
        }

        res.json(context);
    } catch (error: any) {
        console.error('Context load error:', error);
        res.status(500).json({
            error: 'Failed to load context',
            details: error.message
        });
    }
});

export default router;
