// Genesis Console — Coverage Assessor
// TRIAD: SUPPORTIVE (gap detection) | FEDERATION: CREDENTIAL ATLAS | RECURSION: RESEARCHER
// "I verify existence." Scans for dark zones, scores coverage, fills gaps.
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { logEvent } from './store.js';
import { queue as watcherQueue, getFileIndex } from './watcher.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');
const COVERAGE_FILE = path.join(DATA_DIR, 'coverage.jsonl');
const TRUTH_FORGE_ROOT = path.resolve(__dirname, '..', '..');

// Atomizable extensions (same as watcher)
const ATOMIZABLE = new Set([
    '.md', '.txt', '.py', '.js', '.jsx', '.ts', '.tsx',
    '.json', '.yaml', '.yml', '.toml', '.sh', '.html', '.css', '.csv',
    '.go', '.rs', '.rb', '.java', '.sql', '.graphql', '.proto',
]);

const IGNORE_DIRS = new Set([
    'node_modules', '.git', '.venv', 'htmlcov', '.mypy_cache',
    '.pytest_cache', '.ruff_cache', '__pycache__', '.vercel',
    '.next', 'dist', 'build', '.DS_Store', '.Trash',
]);

// ─── Coverage Scan ───

let lastReport = null;
let scanInterval = null;
let scanning = false;

/**
 * Walk the truth_forge/ tree and build a coverage map.
 * For each directory, count: total files, atomized files, total atoms, freshness.
 */
export function scanCoverage() {
    if (scanning) return lastReport;
    scanning = true;

    const fileIndex = getFileIndex();
    const dirMap = {}; // dir → { total, atomized, atoms, stale, files: [] }
    let totalFiles = 0;
    let atomizedFiles = 0;
    let totalAtoms = 0;
    let staleFiles = 0;
    let gaps = [];

    try {
        walkDir(TRUTH_FORGE_ROOT, (filepath) => {
            const ext = path.extname(filepath).toLowerCase();
            if (!ATOMIZABLE.has(ext)) return;

            // Skip trivially small files
            try {
                const stat = fs.statSync(filepath);
                if (stat.size < 50) return;
            } catch { return; }

            const rel = path.relative(TRUTH_FORGE_ROOT, filepath);
            const dir = path.dirname(rel);

            if (!dirMap[dir]) {
                dirMap[dir] = { total: 0, atomized: 0, atoms: 0, stale: 0, files: [] };
            }

            totalFiles++;
            dirMap[dir].total++;

            const entry = fileIndex[filepath];
            if (entry) {
                atomizedFiles++;
                dirMap[dir].atomized++;
                dirMap[dir].atoms += (entry.atom_count || 0);
                totalAtoms += (entry.atom_count || 0);

                // Check freshness: was file modified after last processing?
                try {
                    const stat = fs.statSync(filepath);
                    const modTime = stat.mtimeMs;
                    const processedTime = new Date(entry.last_processed).getTime();
                    if (modTime > processedTime + 5000) {
                        staleFiles++;
                        dirMap[dir].stale++;
                        gaps.push({
                            filepath: rel,
                            reason: 'stale',
                            last_processed: entry.last_processed,
                            atom_count: entry.atom_count,
                        });
                    }
                } catch { /* skip */ }
            } else {
                // Not in index — gap
                gaps.push({
                    filepath: rel,
                    reason: 'unprocessed',
                });
            }
        });
    } catch (err) {
        logEvent('error', `Coverage scan error: ${err.message}`);
    }

    // Score each directory
    const directories = Object.entries(dirMap)
        .map(([dir, data]) => ({
            directory: dir,
            ...data,
            coverage_pct: data.total > 0 ? Math.round((data.atomized / data.total) * 100) : 0,
            atoms_per_file: data.atomized > 0 ? Math.round((data.atoms / data.atomized) * 10) / 10 : 0,
            freshness_pct: data.atomized > 0 ? Math.round(((data.atomized - data.stale) / data.atomized) * 100) : 0,
        }))
        .sort((a, b) => a.coverage_pct - b.coverage_pct); // Lowest coverage first

    // Overall metrics
    const report = {
        timestamp: new Date().toISOString(),
        metrics: {
            breadth: {
                label: 'Breadth',
                desc: '% of atomizable files processed',
                value: totalFiles > 0 ? Math.round((atomizedFiles / totalFiles) * 100) : 0,
                target: 80,
                total_files: totalFiles,
                atomized_files: atomizedFiles,
            },
            depth: {
                label: 'Depth',
                desc: 'Average atoms per processed file',
                value: atomizedFiles > 0 ? Math.round((totalAtoms / atomizedFiles) * 10) / 10 : 0,
                target: 3,
                total_atoms: totalAtoms,
            },
            freshness: {
                label: 'Freshness',
                desc: '% of processed files still current',
                value: atomizedFiles > 0 ? Math.round(((atomizedFiles - staleFiles) / atomizedFiles) * 100) : 0,
                target: 90,
                stale_files: staleFiles,
            },
            quality: {
                label: 'Quality',
                desc: 'Average atom confidence (requires atom data)',
                value: 0, // Filled by caller if atom data available
                target: 75,
            },
        },
        overall_score: 0,
        gap_count: gaps.length,
        directory_count: directories.length,
        dark_zones: directories.filter(d => d.coverage_pct === 0).map(d => d.directory),
        directories: directories.slice(0, 50), // Top 50 worst-covered dirs
        gaps: gaps.slice(0, 100), // Top 100 gap files
    };

    // Overall score = average of dimension scores
    const dims = report.metrics;
    report.overall_score = Math.round(
        (Math.min(100, (dims.breadth.value / dims.breadth.target) * 100) +
            Math.min(100, (dims.depth.value / dims.depth.target) * 100) +
            Math.min(100, (dims.freshness.value / dims.freshness.target) * 100)) / 3
    );

    // Save report
    const line = JSON.stringify(report) + '\n';
    fs.appendFileSync(COVERAGE_FILE, line, 'utf-8');

    lastReport = report;
    scanning = false;

    logEvent('info', `Coverage scan complete: ${report.metrics.breadth.value}% breadth, ${report.gap_count} gaps, ${report.dark_zones.length} dark zones`);

    return report;
}

/**
 * Queue gap files into the watcher for processing.
 * This is how the Supportive layer feeds the Core layer.
 */
export function fillGaps(maxFiles = 50) {
    if (!lastReport) scanCoverage();
    const report = lastReport;
    if (!report) return { queued: 0 };

    let queued = 0;
    for (const gap of report.gaps.slice(0, maxFiles)) {
        const abs = path.join(TRUTH_FORGE_ROOT, gap.filepath);
        if (fs.existsSync(abs)) {
            // Priority based on reason: unprocessed > stale
            const priority = gap.reason === 'unprocessed' ? 2 : 3;
            watcherQueue.add(abs, priority);
            queued++;
        }
    }

    if (queued > 0) {
        logEvent('info', `Coverage assessor queued ${queued} gap files for atomization`);

        // Ensure the watcher queue is processing
        if (!watcherQueue.processing) {
            watcherQueue.start().catch(err => {
                logEvent('error', `Queue restart from coverage: ${err.message}`);
            });
        }
    }

    return { queued, total_gaps: report.gap_count };
}

/**
 * Start periodic coverage scanning.
 */
export function startCoverageMonitor(intervalMs = 10 * 60 * 1000) {
    if (scanInterval) return { status: 'already_running' };

    // Initial scan after 60 seconds (let watcher settle first)
    setTimeout(() => {
        try {
            scanCoverage();
            fillGaps(20); // Queue first batch of gap files
        } catch (err) {
            logEvent('error', `Initial coverage scan failed: ${err.message}`);
        }
    }, 60000);

    // Periodic scan
    scanInterval = setInterval(() => {
        try {
            scanCoverage();
            fillGaps(20);
        } catch (err) {
            logEvent('error', `Coverage scan cycle failed: ${err.message}`);
        }
    }, intervalMs);

    logEvent('info', `Coverage monitor started (interval: ${intervalMs / 60000}min)`);
    return { status: 'started', interval_ms: intervalMs };
}

export function stopCoverageMonitor() {
    if (scanInterval) {
        clearInterval(scanInterval);
        scanInterval = null;
    }
    return { status: 'stopped' };
}

export function getCoverageReport() {
    return lastReport || { status: 'no_scan_yet', hint: 'POST /api/coverage/scan to trigger' };
}

export function getCoverageGaps(limit = 50) {
    if (!lastReport) return { gaps: [], dark_zones: [] };
    return {
        gaps: lastReport.gaps.slice(0, limit),
        dark_zones: lastReport.dark_zones,
        gap_count: lastReport.gap_count,
    };
}

// ─── Directory Walker ───

function walkDir(dir, callback) {
    let entries;
    try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
    } catch { return; }

    for (const entry of entries) {
        if (IGNORE_DIRS.has(entry.name)) continue;
        if (entry.name.startsWith('.')) continue; // Skip hidden files/dirs

        const full = path.join(dir, entry.name);

        if (entry.isDirectory()) {
            // Skip the atom data directory
            if (full.includes('genesis-console/data')) continue;
            walkDir(full, callback);
        } else if (entry.isFile()) {
            callback(full);
        }
    }
}
