// Genesis Console — Persistent JSONL Store
// TRIAD: CORE (immutable substrate) | FEDERATION: TRUTH FORGE | RECURSION: —
// "I hold the soul." The Golden Record — append-only JSONL persistence.
// Implements HOLD₁ (intake) and HOLD₂ (atoms) as immutable ledgers.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';
import { queueRecoveryFromError } from './recovery.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });

const INTAKE_FILE = path.join(DATA_DIR, 'intake.jsonl');   // HOLD₁ — raw file metadata (CORE)
const ATOMS_FILE = path.join(DATA_DIR, 'atoms.jsonl');     // HOLD₂ — extracted knowledge atoms (CORE)
const LOG_FILE = path.join(DATA_DIR, 'system.jsonl');      // System event log (META)

/**
 * Append a record to a JSONL file (append-only, immutable)
 * This is the foundational CORE operation — once written, never modified.
 */
function appendRecord(filepath, record) {
    const line = JSON.stringify({ ...record, _ts: new Date().toISOString() }) + '\n';
    fs.appendFileSync(filepath, line, 'utf-8');
}

/**
 * Read all records from a JSONL file
 */
function readRecords(filepath) {
    if (!fs.existsSync(filepath)) return [];
    const content = fs.readFileSync(filepath, 'utf-8').trim();
    if (!content) return [];
    return content.split('\n').map(line => {
        try { return JSON.parse(line); }
        catch { return null; }
    }).filter(Boolean);
}

// ─── INTAKE (HOLD₁) ───

export function recordIntake(fileInfo) {
    const record = {
        id: crypto.randomUUID(),
        type: 'intake',
        filename: fileInfo.filename,
        mime_type: fileInfo.mimeType,
        size_bytes: fileInfo.sizeBytes,
        content_hash: crypto.createHash('sha256').update(fileInfo.content || '').digest('hex'),
        artifact_type: fileInfo.artifactType,
    };
    appendRecord(INTAKE_FILE, record);
    appendRecord(LOG_FILE, { level: 'info', msg: `HOLD₁: Intake recorded — ${fileInfo.filename}` });
    return record;
}

export function getIntakes() {
    return readRecords(INTAKE_FILE);
}

// ─── ATOMS (HOLD₂) ───

export function storeAtoms(atoms, sourceIntakeId) {
    const stored = [];
    for (const atom of atoms) {
        const record = {
            id: crypto.randomUUID(),
            source_intake_id: sourceIntakeId,
            type: atom.type || 'fact',
            content: atom.content || atom.text || '',
            confidence: atom.confidence ?? atom.conf ?? 0.8,
            entities: atom.entities || [],
            themes: atom.themes || [],
            framework_layer: atom.framework_layer || null,
            framework_dimension: atom.framework_dimension || null,
            cross_references: atom.cross_references || [],
            compound_depth: atom.compound_depth || 0,
        };
        appendRecord(ATOMS_FILE, record);
        stored.push(record);
    }
    appendRecord(LOG_FILE, {
        level: 'info',
        msg: `HOLD₂: ${stored.length} atoms stored from intake ${sourceIntakeId}`,
    });
    return stored;
}

export function getAtoms(limit = 100) {
    const all = readRecords(ATOMS_FILE);
    return all.slice(-limit).reverse(); // Most recent first
}

export function getAtomCount() {
    return readRecords(ATOMS_FILE).length;
}

// ─── LOG ───

export function logEvent(level, msg) {
    appendRecord(LOG_FILE, { level, msg });
    if (level === 'error') {
        queueRecoveryFromError({
            source: 'server_log',
            level,
            reason: msg,
        });
    }
}

export function getLog(limit = 50) {
    const all = readRecords(LOG_FILE);
    return all.slice(-limit);
}

// ─── STATS (Triad-Aware) ───

export function getStats() {
    const atoms = readRecords(ATOMS_FILE);
    const intakes = readRecords(INTAKE_FILE);

    const typeCounts = {};
    const triadCounts = { CORE: 0, SUPPORTIVE: 0, META: 0, unclassified: 0 };
    let totalConf = 0;

    atoms.forEach(a => {
        typeCounts[a.type] = (typeCounts[a.type] || 0) + 1;
        totalConf += (a.confidence || 0);

        // Triad layer distribution
        if (a.framework_layer && triadCounts[a.framework_layer] !== undefined) {
            triadCounts[a.framework_layer]++;
        } else {
            triadCounts.unclassified++;
        }
    });

    return {
        totalAtoms: atoms.length,
        totalIntakes: intakes.length,
        avgConfidence: atoms.length > 0 ? totalConf / atoms.length : 0,
        typeCounts,
        triadDistribution: triadCounts,
        triadClassified: atoms.length > 0
            ? Math.round(((atoms.length - triadCounts.unclassified) / atoms.length) * 100)
            : 0,
        lastAtomTime: atoms.length > 0 ? atoms[atoms.length - 1]._ts : null,
        lastIntakeTime: intakes.length > 0 ? intakes[intakes.length - 1]._ts : null,
    };
}
