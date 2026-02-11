// Genesis Console — Passive Atomization Watcher
// TRIAD: CORE (file observation) | FEDERATION: TRUTH FORGE | RECURSION: RESEARCHER
// "I hold the soul." High-velocity filesystem observation and ingestion.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import chokidar from 'chokidar';
import { recordIntake, storeAtoms, logEvent, getStats } from './store.js';
import { atomize, checkOllama } from './atomizer.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const INDEX_FILE = path.join(DATA_DIR, 'index.json');

// ─── Configuration ───

const TRUTH_FORGE_ROOT = path.resolve(__dirname, '..', '..');

// File extensions to atomize (text-based, meaningful content)
const ATOMIZABLE_EXTENSIONS = new Set([
    '.md', '.txt', '.py', '.js', '.jsx', '.ts', '.tsx',
    '.json', '.yaml', '.yml', '.toml', '.sh', '.html', '.css', '.csv',
    '.go', '.rs', '.rb', '.java', '.sql', '.graphql', '.proto',
]);

// Directories to always ignore
const IGNORE_DIRS = new Set([
    'node_modules', '.git', '.venv', 'htmlcov', '.mypy_cache',
    '.pytest_cache', '.ruff_cache', '__pycache__', '.vercel',
    '.next', 'dist', 'build', '.DS_Store', '.Trash',
]);

// Specific paths to ignore (relative to truth_forge root)
const IGNORE_PATHS = [
    'genesis-console/data',       // Don't atomize the atoms
    'genesis-console/node_modules',
];

// File constraints
const MIN_FILE_SIZE = 50;         // bytes — skip trivially small files
const MAX_FILE_SIZE = 500 * 1024; // 500KB — chunk larger files separately
const CHUNK_SIZE = 8000;          // chars per chunk for large files

// Rate limiting
const DELAY_BETWEEN_FILES = 2000;  // ms between sequential file processing
const DEBOUNCE_MS = 3000;          // ms debounce for file change events
const MAX_QUEUE_SIZE = 10000;      // max files in queue

// Priority tiers
const PRIORITY = {
    P0_SPEC: 0,     // Root *.md files — strategic and most valuable
    P1_SOURCE: 1,   // *.py, *.js, *.jsx, *.ts, *.tsx
    P2_DOCS: 2,     // Nested *.md, *.txt
    P3_CONFIG: 3,   // *.json, *.yaml, *.yml, *.toml
    P4_OTHER: 4,    // *.sh, *.html, *.css, etc.
};

// ─── File Hash Index (Deduplication) ───

let fileIndex = {};

function loadIndex() {
    try {
        if (fs.existsSync(INDEX_FILE)) {
            fileIndex = JSON.parse(fs.readFileSync(INDEX_FILE, 'utf-8'));
        }
    } catch {
        fileIndex = {};
    }
}

function saveIndex() {
    fs.writeFileSync(INDEX_FILE, JSON.stringify(fileIndex, null, 2), 'utf-8');
}

function hashFile(content) {
    return crypto.createHash('sha256').update(content).digest('hex');
}

function isProcessed(filepath, content) {
    const hash = hashFile(content);
    const entry = fileIndex[filepath];
    return entry && entry.hash === hash;
}

function markProcessed(filepath, content, atomCount) {
    fileIndex[filepath] = {
        hash: hashFile(content),
        last_processed: new Date().toISOString(),
        atom_count: atomCount,
        size: content.length,
    };
    // Save periodically, not on every file (perf)
    if (Math.random() < 0.1) saveIndex();
}

// ─── File Classification ───

function shouldIgnore(filepath) {
    const rel = path.relative(TRUTH_FORGE_ROOT, filepath);
    const parts = rel.split(path.sep);

    // Check if any path segment is in ignore list
    for (const part of parts) {
        if (IGNORE_DIRS.has(part)) return true;
    }

    // Check specific paths
    for (const ip of IGNORE_PATHS) {
        if (rel.startsWith(ip)) return true;
    }

    // Check extension
    const ext = path.extname(filepath).toLowerCase();
    if (!ATOMIZABLE_EXTENSIONS.has(ext)) return true;

    // Skip lock files
    const basename = path.basename(filepath);
    if (basename.endsWith('.lock') || basename === 'package-lock.json') return true;

    return false;
}

function getPriority(filepath) {
    const rel = path.relative(TRUTH_FORGE_ROOT, filepath);
    const ext = path.extname(filepath).toLowerCase();
    const depth = rel.split(path.sep).length;

    // Root MD files are P0
    if (depth === 1 && ext === '.md') return PRIORITY.P0_SPEC;

    // Source code
    if (['.py', '.js', '.jsx', '.ts', '.tsx'].includes(ext)) return PRIORITY.P1_SOURCE;

    // Nested docs
    if (['.md', '.txt'].includes(ext)) return PRIORITY.P2_DOCS;

    // Config
    if (['.json', '.yaml', '.yml', '.toml'].includes(ext)) return PRIORITY.P3_CONFIG;

    return PRIORITY.P4_OTHER;
}

function getArtifactType(ext) {
    const map = {
        '.py': 'CODE', '.js': 'CODE', '.jsx': 'CODE', '.ts': 'CODE', '.tsx': 'CODE',
        '.go': 'CODE', '.rs': 'CODE', '.rb': 'CODE', '.java': 'CODE', '.sh': 'CODE',
        '.json': 'DATA', '.csv': 'DATA', '.yaml': 'DATA', '.yml': 'DATA', '.toml': 'DATA',
        '.md': 'DOCUMENT', '.txt': 'DOCUMENT', '.html': 'DOCUMENT',
        '.css': 'CODE', '.sql': 'CODE', '.graphql': 'CODE', '.proto': 'DATA',
    };
    return map[ext] || 'DOCUMENT';
}

/**
 * Classify which Triad layer a file likely belongs to based on its path and content.
 * This helps Scout understand the architectural role of the file being atomized.
 */
function classifyFileTriadRole(relPath) {
    const lower = relPath.toLowerCase();
    // META: governance, reflection, behavioral rules, sentinel, audits
    if (/(reflect|meta|sentinel|governance|behavior|audit|paradigm|triad)/.test(lower)) return 'META';
    // SUPPORTIVE: coverage, recovery, synthetic, assistant, monitoring, testing
    if (/(coverage|recovery|synthetic|assistant|monitor|test|helper|support|quality|gap)/.test(lower)) return 'SUPPORTIVE';
    // CORE: store, atomizer, watcher, pipeline, api, engine, data model
    if (/(store|atom|watch|pipeline|engine|index|server|core|model)/.test(lower)) return 'CORE';
    // Docs and specs lean META (governance of knowledge)
    if (lower.endsWith('.md') || lower.includes('docs/')) return 'META';
    // Default for source code is CORE
    if (/\.(py|js|jsx|ts|tsx|go|rs|rb|java)$/.test(lower)) return 'CORE';
    return null;
}

// ─── Processing Queue ───

class ProcessingQueue {
    constructor() {
        this.queue = [];
        this.processing = false;
        this.processed = 0;
        this.errors = 0;
        this.totalAtoms = 0;
        this.startTime = null;
        this.currentFile = null;
        this.paused = false;
    }

    add(filepath, priority = PRIORITY.P4_OTHER) {
        if (this.queue.length >= MAX_QUEUE_SIZE) return;
        // Don't add duplicates
        if (this.queue.some(item => item.filepath === filepath)) return;

        this.queue.push({ filepath, priority, queued_at: Date.now() });
        // Sort by priority (lower = higher priority)
        this.queue.sort((a, b) => a.priority - b.priority);
    }

    get size() { return this.queue.length; }

    get status() {
        return {
            queueSize: this.queue.length,
            processing: this.processing,
            processed: this.processed,
            errors: this.errors,
            totalAtoms: this.totalAtoms,
            currentFile: this.currentFile,
            paused: this.paused,
            startTime: this.startTime,
            uptime: this.startTime ? Date.now() - this.startTime : 0,
        };
    }

    async start() {
        if (this.processing) return;
        this.processing = true;
        this.startTime = Date.now();
        logEvent('info', `Watcher queue started — ${this.queue.length} files queued`);

        while (this.queue.length > 0 && this.processing) {
            if (this.paused) {
                await sleep(1000);
                continue;
            }

            const item = this.queue.shift();
            await this.processFile(item.filepath);
            await sleep(DELAY_BETWEEN_FILES);
        }

        this.processing = false;
        logEvent('info', `Watcher queue drained — ${this.processed} files processed, ${this.totalAtoms} atoms extracted`);
        saveIndex();
    }

    stop() {
        this.processing = false;
        logEvent('info', 'Watcher queue stopped');
    }

    pause() { this.paused = true; }
    resume() { this.paused = false; }

    async processFile(filepath) {
        try {
            // Read file
            const content = fs.readFileSync(filepath, 'utf-8');
            const rel = path.relative(TRUTH_FORGE_ROOT, filepath);

            // Size checks
            if (content.length < MIN_FILE_SIZE) return;

            // Deduplication check
            if (isProcessed(filepath, content)) {
                return; // Already processed, skip
            }

            this.currentFile = rel;
            const ext = path.extname(filepath).toLowerCase();
            const artifactType = getArtifactType(ext);

            // HOLD₁ — Record intake
            const intake = recordIntake({
                filename: rel,
                mimeType: `text/${ext.slice(1)}`,
                sizeBytes: Buffer.byteLength(content),
                artifactType,
                content,
            });

            // Handle large files by chunking
            let contentToProcess = content;
            if (content.length > MAX_FILE_SIZE) {
                // Take first chunk + last chunk to get overview
                contentToProcess = content.slice(0, CHUNK_SIZE) +
                    '\n\n[...FILE TRUNCATED...]\n\n' +
                    content.slice(-CHUNK_SIZE);
                logEvent('info', `Watcher: Chunked ${rel} (${(content.length / 1024).toFixed(0)}KB → ${(contentToProcess.length / 1024).toFixed(0)}KB)`);
            }

            // Add file metadata context with Triad classification for better atomization
            const triadRole = classifyFileTriadRole(rel);
            const triadContext = triadRole
                ? `ARCHITECTURAL TRIAD ROLE: ${triadRole} — assess this file's contribution to its ${triadRole} layer\n`
                : '';
            const contextualContent = `FILE: ${rel}\nTYPE: ${artifactType}\nSIZE: ${content.length} chars\n${triadContext}\n${contentToProcess}`;

            // AGENT — Send to Scout
            const result = await atomize(contextualContent, rel);

            // HOLD₂ — Store atoms
            const stored = storeAtoms(result.atoms, intake.id);

            // Mark as processed
            markProcessed(filepath, content, stored.length);
            this.processed++;
            this.totalAtoms += stored.length;

            logEvent('success', `Watcher: ${rel} → ${stored.length} atoms (${result.elapsed_ms}ms)`);
        } catch (err) {
            this.errors++;
            const rel = path.relative(TRUTH_FORGE_ROOT, filepath);
            logEvent('error', `Watcher: Failed ${rel} — ${err.message}`);
        } finally {
            this.currentFile = null;
        }
    }
}

// ─── File System Watcher ───

let watcher = null;
let queue = new ProcessingQueue();
let watcherActive = false;
const changeTimers = new Map(); // Debounce timers per file

export function startWatcher() {
    if (watcherActive) return { status: 'already_running' };

    loadIndex();

    watcher = chokidar.watch(TRUTH_FORGE_ROOT, {
        ignored: (filepath, stats) => {
            const basename = path.basename(filepath);
            // Ignore hidden dirs, node_modules, etc.
            if (IGNORE_DIRS.has(basename)) return true;
            // Ignore the data directory
            if (filepath.includes('genesis-console/data')) return true;
            // Ignore non-atomizable files (but allow directories through)
            if (stats?.isFile()) {
                return shouldIgnore(filepath);
            }
            return false;
        },
        persistent: true,
        ignoreInitial: false,  // Process existing files on startup
        depth: 15,
        awaitWriteFinish: {
            stabilityThreshold: 2000,
            pollInterval: 500,
        },
    });

    watcher.on('add', (filepath) => {
        debounceAdd(filepath);
    });

    watcher.on('change', (filepath) => {
        debounceAdd(filepath);
    });

    watcher.on('ready', () => {
        watcherActive = true;
        logEvent('success', `Watcher: Monitoring ${TRUTH_FORGE_ROOT} — initial scan complete, ${queue.size} files queued`);

        // Start processing queue
        queue.start().catch(err => {
            logEvent('error', `Watcher queue error: ${err.message}`);
        });
    });

    watcher.on('error', (err) => {
        logEvent('error', `Watcher error: ${err.message}`);
    });

    logEvent('info', `Watcher: Starting scan of ${TRUTH_FORGE_ROOT}...`);
    return { status: 'started' };
}

function debounceAdd(filepath) {
    // Clear previous timer for this file
    if (changeTimers.has(filepath)) {
        clearTimeout(changeTimers.get(filepath));
    }

    // Set new debounce timer
    changeTimers.set(filepath, setTimeout(() => {
        changeTimers.delete(filepath);

        if (shouldIgnore(filepath)) return;

        // Check file exists and is readable
        try {
            const stat = fs.statSync(filepath);
            if (!stat.isFile()) return;
            if (stat.size < MIN_FILE_SIZE) return;
        } catch { return; }

        const priority = getPriority(filepath);
        queue.add(filepath, priority);

        // If queue isn't running, start it
        if (!queue.processing) {
            queue.start().catch(err => {
                logEvent('error', `Queue restart error: ${err.message}`);
            });
        }
    }, DEBOUNCE_MS));
}

export function stopWatcher() {
    if (watcher) {
        watcher.close();
        watcher = null;
    }
    queue.stop();
    watcherActive = false;
    saveIndex();
    logEvent('info', 'Watcher: Stopped');
    return { status: 'stopped' };
}

export function getWatcherStatus() {
    return {
        active: watcherActive,
        root: TRUTH_FORGE_ROOT,
        indexSize: Object.keys(fileIndex).length,
        ...queue.status,
    };
}

export function getFileIndex() {
    return fileIndex;
}

export async function triggerSweep() {
    logEvent('info', 'Watcher: Manual sweep triggered');
    // Reset the index to force re-processing
    fileIndex = {};
    saveIndex();
    // Restart the watcher to trigger initial scan
    stopWatcher();
    await sleep(1000);
    return startWatcher();
}

export async function reprocessFile(filepath) {
    const abs = path.isAbsolute(filepath)
        ? filepath
        : path.join(TRUTH_FORGE_ROOT, filepath);

    if (!fs.existsSync(abs)) {
        throw new Error(`File not found: ${filepath}`);
    }

    // Remove from index to force reprocessing
    delete fileIndex[abs];
    saveIndex();

    // Process immediately
    await queue.processFile(abs);
    saveIndex();

    return { status: 'reprocessed', filepath: abs };
}

export { queue };

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}
