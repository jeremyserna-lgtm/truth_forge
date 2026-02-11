/* global Buffer, process */
// Genesis Console — API Server
// TRIAD: CORE (execution sandbox) | FEDERATION: TRUTH FORGE | RECURSION: —
// "I hold the soul." The substrate upon which all services run.
import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import {
    recordIntake, getIntakes, storeAtoms, getAtoms,
    getAtomCount, logEvent, getLog, getStats,
} from './store.js';
import { atomize, checkOllama } from './atomizer.js';
import {
    startWatcher, stopWatcher, getWatcherStatus,
    getFileIndex, triggerSweep, reprocessFile,
} from './watcher.js';
import {
    scanCoverage, fillGaps, startCoverageMonitor, stopCoverageMonitor,
    getCoverageReport, getCoverageGaps,
} from './coverage.js';
import {
    reflect, startReflector, stopReflector,
    getReflectorStatus, getReflectionInsights, notifyNewAtoms,
} from './reflector.js';
import {
    bootstrapTriad, getTriadStatus, auditTriad,
    assessTriadCompleteness, TRIAD_LAYERS,
    getOntology, FEDERATION_OF_SOVEREIGNS, RECURSIVE_MAGNIFICATION,
} from './triad.js';
import { chatAssistant, getAssistantHistory } from './assistant.js';
import { getRecoveryRuns, getRecoveryStatus, queueRecoveryFromError } from './recovery.js';
import {
    configureSyntheticMonitor,
    getSyntheticDepthDecision,
    getSyntheticFeedback,
    getSyntheticRuns,
    getSyntheticStatus,
    submitSyntheticDepthDecision,
    startSyntheticMonitor,
    triggerSyntheticRun,
} from './synthetic.js';
import {
    createOrRefreshIntentPlan,
    syncPlanTodos,
    getPlanningState,
    getToolCatalog,
    orchestrateToolUsage,
    getHandoverReadiness,
    rehearseHandover,
    runMission,
    getMissionHistory,
    getMissionRun,
    getSentinelStatus,
    recordSentinelHeartbeat,
    registerSentinelAnomaly,
    escalateSentinelIncident,
    runOperatorCheck,
    getSentinelIncident,
    startRecursiveCycle,
    ingestRecursiveCycle,
    evaluateRecursiveCycle,
    promoteRecursiveCycle,
    getRecursiveSynthesisHealth,
    getRecursiveCycle,
    getKioskStatus,
    enterKioskMaintenance,
    exitKioskMaintenance,
    recordKioskIntervention,
    createAnnotation,
    getAnnotations,
    getAnnotation,
    updateAnnotationStatus,
} from './support.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const PORT = process.env.PORT || 3141; // π — the Genesis port
const DIST_DIR = path.resolve(__dirname, '../dist');
const DIST_INDEX = path.join(DIST_DIR, 'index.html');

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));

// Automatically route 5xx responses into recovery, even when route handlers forget to log.
app.use((req, res, next) => {
    const startedAt = Date.now();
    res.on('finish', () => {
        if (res.statusCode < 500) return;
        if (req.path.startsWith('/api/recovery/')) return;
        const elapsed = Date.now() - startedAt;
        logEvent('error', `HTTP ${res.statusCode} ${req.method} ${req.originalUrl} (${elapsed}ms)`);
    });
    next();
});

// File upload handling
const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 50 * 1024 * 1024 }, // 50MB max
});

// ─── Health / Status ───

app.get('/api/health', async (req, res) => {
    const ollama = await checkOllama();
    const stats = getStats();
    const triad = getTriadStatus();
    res.json({
        status: 'operational',
        version: '0.1.0',
        framework: 'Three Ontological Roles',
        ontology: 'Triad = Structure. Recursion = Energy. Federation = Agency.',
        ollama,
        stats,
        triad: {
            complete: triad.health.complete,
            balance: triad.health.balance_score,
            services: triad.health.total_services,
            core: triad.health.core_count,
            supportive: triad.health.supportive_count,
            meta: triad.health.meta_count,
        },
        federation: triad.federation,
        recursion: triad.recursion,
        uptime: process.uptime(),
    });
});

app.get('/api/ollama', async (req, res) => {
    const status = await checkOllama();
    res.json(status);
});

// ─── INTAKE ───

app.get('/api/intakes', (req, res) => {
    res.json(getIntakes());
});

// ─── ATOMS ───

app.get('/api/atoms', (req, res) => {
    const limit = parseInt(req.query.limit) || 100;
    const atoms = getAtoms(limit);
    res.json({
        atoms,
        total: getAtomCount(),
    });
});

app.get('/api/stats', (req, res) => {
    res.json(getStats());
});

// ─── LOG ───

app.get('/api/log', (req, res) => {
    const limit = parseInt(req.query.limit) || 50;
    res.json(getLog(limit));
});

// ─── AUTO RECOVERY (SELF-HEAL + TEST LOOP) ───

app.get('/api/recovery/status', (_req, res) => {
    res.json(getRecoveryStatus());
});

app.get('/api/recovery/runs', (req, res) => {
    const limit = req.query.limit ? parseInt(req.query.limit) : 20;
    res.json(getRecoveryRuns(limit));
});

app.post('/api/recovery/trigger', (req, res) => {
    const queued = queueRecoveryFromError({
        source: req.body?.source || 'operator',
        level: req.body?.level || 'error',
        reason: req.body?.reason || 'manual_recovery_trigger',
        context: req.body?.context || {},
    });
    logEvent('warn', `Auto-recovery manually queued (${queued.pending_events} pending)`);
    res.json({
        ok: true,
        queued,
        status: getRecoveryStatus(),
    });
});

app.post('/api/recovery/report-error', (req, res) => {
    const reason = String(req.body?.reason || '').trim();
    if (!reason) {
        return res.status(400).json({ ok: false, error: 'reason_required' });
    }
    const queued = queueRecoveryFromError({
        source: req.body?.source || 'client_runtime',
        level: req.body?.level || 'error',
        reason,
        context: req.body?.context || {},
    });
    logEvent('warn', `Client error queued for auto-recovery (${queued.pending_events} pending)`);
    res.json({
        ok: true,
        queued,
    });
});

// ─── SYNTHETIC USER MONITOR (E2E CONTINUOUS VALIDATION) ───

app.get('/api/synthetic/status', (_req, res) => {
    res.json(getSyntheticStatus());
});

app.get('/api/synthetic/runs', (req, res) => {
    const limit = req.query.limit ? parseInt(req.query.limit) : 20;
    res.json(getSyntheticRuns(limit));
});

app.get('/api/synthetic/feedback', (req, res) => {
    const limit = req.query.limit ? parseInt(req.query.limit) : 20;
    res.json(getSyntheticFeedback(limit));
});

app.get('/api/synthetic/depth/decision', (req, res) => {
    const runId = req.query.run_id ? String(req.query.run_id) : '';
    res.json(getSyntheticDepthDecision({ run_id: runId }));
});

app.post('/api/synthetic/trigger', async (req, res) => {
    const reason = req.body?.reason || 'manual_trigger';
    const run = await triggerSyntheticRun(reason);
    const statusCode = run?.ok === false ? 500 : 200;
    res.status(statusCode).json(run);
});

app.post('/api/synthetic/depth/decision', (req, res) => {
    const result = submitSyntheticDepthDecision(req.body || {});
    if (!result.ok) {
        return res.status(400).json(result);
    }
    res.json(result);
});

app.post('/api/synthetic/configure', (req, res) => {
    const next = configureSyntheticMonitor({
        enabled: req.body?.enabled,
        interval_ms: req.body?.interval_ms,
    });
    res.json(next);
});

// ─── PLAN / TODO SUPPORT STACK ───

app.post('/api/planning/intent-plan', (req, res) => {
    const plan = createOrRefreshIntentPlan(req.body || {});
    logEvent('info', `Plan refreshed (${plan.id}) for run ${plan.run_id}`);
    res.json(plan);
});

app.post('/api/planning/todos/sync', (req, res) => {
    const synced = syncPlanTodos(req.body || {});
    if (!synced.ok) {
        return res.status(404).json(synced);
    }
    logEvent('info', `Todo graph synced for plan ${synced.snapshot.plan_id}`);
    res.json(synced);
});

app.get('/api/planning/state/:run_id', (req, res) => {
    const state = getPlanningState(req.params.run_id);
    res.json(state);
});

app.get('/api/tools/catalog', (_req, res) => {
    res.json({
        tools: getToolCatalog(),
    });
});

app.post('/api/tools/orchestrate', (req, res) => {
    const trace = orchestrateToolUsage(req.body || {});
    logEvent('info', `Tool orchestration trace recorded (${trace.id})`);
    res.json(trace);
});

app.get('/api/handover/readiness', (_req, res) => {
    const readiness = getHandoverReadiness();
    res.json(readiness);
});

app.post('/api/handover/rehearse', (req, res) => {
    const rehearsal = rehearseHandover(req.body || {});
    logEvent('info', `Handover rehearsal completed (${rehearsal.id}) pass=${rehearsal.pass}`);
    res.json(rehearsal);
});

// ─── MISSION CONTROL (INTENT -> PLAN -> EXECUTION) ───

app.post('/api/mission/run', (req, res) => {
    const mission = runMission(req.body || {});
    const level = mission.status === 'failed' ? 'error' : 'info';
    logEvent(level, `Mission run ${mission.run_id} status=${mission.status}`);
    if (mission.status === 'failed') {
        return res.status(500).json(mission);
    }
    res.json(mission);
});

app.get('/api/mission/history', (req, res) => {
    const limit = parseInt(req.query.limit) || 20;
    res.json(getMissionHistory({ limit }));
});

app.get('/api/mission/:run_id', (req, res) => {
    const mission = getMissionRun(req.params.run_id);
    if (!mission) {
        return res.status(404).json({ error: 'mission_not_found' });
    }
    res.json(mission);
});

// ─── KIOSK OPERATIONS ───

app.get('/api/kiosk/status', (_req, res) => {
    res.json(getKioskStatus());
});

app.post('/api/kiosk/maintenance/enter', (req, res) => {
    const result = enterKioskMaintenance(req.body || {});
    logEvent('warn', `Kiosk maintenance entered by ${result.policy.requested_by}`);
    res.json(result);
});

app.post('/api/kiosk/maintenance/exit', (req, res) => {
    const result = exitKioskMaintenance(req.body || {});
    logEvent('info', `Kiosk maintenance exited by ${result.policy.requested_by}`);
    res.json(result);
});

app.post('/api/kiosk/interventions', (req, res) => {
    const record = recordKioskIntervention(req.body || {});
    const level = record.severity === 'critical' ? 'warn' : 'info';
    logEvent(level, `Kiosk intervention ${record.intervention_type} (${record.id})`);
    res.json(record);
});

// ─── ANNOTATIONS (IN-APP FEEDBACK / QUESTIONS) ───

app.get('/api/annotations', (req, res) => {
    const route = req.query.route ? String(req.query.route) : undefined;
    const status = req.query.status ? String(req.query.status) : undefined;
    const limit = req.query.limit ? parseInt(req.query.limit) : undefined;
    res.json(getAnnotations({ route, status, limit }));
});

app.post('/api/annotations', (req, res) => {
    const created = createAnnotation(req.body || {});
    if (!created.ok) {
        const code = created.error === 'message_required' ? 400 : 422;
        return res.status(code).json(created);
    }
    logEvent('info', `Annotation created (${created.annotation.id}) on route ${created.annotation.route}`);
    res.json(created.annotation);
});

app.get('/api/annotations/:id', (req, res) => {
    const annotation = getAnnotation(req.params.id);
    if (!annotation) {
        return res.status(404).json({ error: 'annotation_not_found' });
    }
    res.json(annotation);
});

app.post('/api/annotations/:id/status', (req, res) => {
    const updated = updateAnnotationStatus(req.params.id, req.body || {});
    if (!updated.ok) {
        const code = updated.error === 'annotation_not_found' ? 404 : 422;
        return res.status(code).json(updated);
    }
    logEvent('info', `Annotation ${updated.annotation.id} status -> ${updated.annotation.status}`);
    res.json(updated.annotation);
});

// ─── IN-APP ASSISTANT (LOCAL MODEL COPILOT) ───

app.get('/api/assistant/history', (req, res) => {
    const limit = req.query.limit ? parseInt(req.query.limit) : 60;
    res.json(getAssistantHistory(limit));
});

app.post('/api/assistant/chat', async (req, res) => {
    const result = await chatAssistant(req.body || {});
    if (!result.ok) {
        const code = result.error === 'message_required' ? 400 : 500;
        return res.status(code).json(result);
    }
    const model = result.message?.model || 'unavailable';
    logEvent('info', `Assistant chat completed (${model})`);
    res.json(result);
});

// ─── CONTINUITY SENTINEL ───

app.get('/api/sentinel/status', (req, res) => {
    const threshold_seconds = parseInt(req.query.threshold_seconds) || 120;
    const status = getSentinelStatus({ threshold_seconds });
    res.json(status);
});

app.post('/api/sentinel/heartbeat', (req, res) => {
    const heartbeat = recordSentinelHeartbeat(req.body || {});
    logEvent('info', `Sentinel heartbeat received from ${heartbeat.unit_id}`);
    res.json(heartbeat);
});

app.post('/api/sentinel/anomaly', (req, res) => {
    const anomaly = registerSentinelAnomaly(req.body || {});
    logEvent('warn', `Sentinel anomaly opened (${anomaly.incident_id}) severity=${anomaly.severity}`);
    res.json(anomaly);
});

app.post('/api/sentinel/escalate', (req, res) => {
    if (!req.body?.incident_id) {
        return res.status(400).json({ error: 'incident_id required' });
    }
    const escalation = escalateSentinelIncident(req.body);
    logEvent('warn', `Sentinel escalation (${escalation.incident_id}) stage=${escalation.stage}`);
    res.json(escalation);
});

app.post('/api/sentinel/operator-check', (req, res) => {
    const check = runOperatorCheck(req.body || {});
    logEvent('info', `Operator check triggered (${check.id})`);
    res.json(check);
});

app.get('/api/sentinel/incidents/:id', (req, res) => {
    const incident = getSentinelIncident(req.params.id);
    if (!incident) {
        return res.status(404).json({ error: 'incident_not_found' });
    }
    res.json(incident);
});

// ─── RECURSIVE SYNTHESIS PROTOCOL ───

app.post('/api/synthesis/recursive/cycle', (req, res) => {
    const cycle = startRecursiveCycle(req.body || {});
    logEvent('info', `Recursive synthesis cycle started (${cycle.cycle_id})`);
    res.json(cycle);
});

app.post('/api/synthesis/recursive/ingest', (req, res) => {
    const result = ingestRecursiveCycle(req.body || {});
    if (!result.ok) {
        return res.status(404).json(result);
    }
    logEvent('info', `Recursive synthesis ingest complete (${result.cycle.cycle_id})`);
    res.json(result);
});

app.post('/api/synthesis/recursive/evaluate', (req, res) => {
    const result = evaluateRecursiveCycle(req.body || {});
    if (!result.ok) {
        return res.status(404).json(result);
    }
    logEvent('info', `Recursive synthesis evaluated (${result.cycle.cycle_id}) -> ${result.cycle.decision}`);
    res.json(result);
});

app.post('/api/synthesis/recursive/promote', (req, res) => {
    const result = promoteRecursiveCycle(req.body || {});
    if (!result.ok) {
        const code = result.error === 'cycle_not_promotable' ? 409 : 404;
        return res.status(code).json(result);
    }
    logEvent('success', `Recursive synthesis promoted (${result.cycle.cycle_id})`);
    res.json(result);
});

app.get('/api/synthesis/recursive/health', (_req, res) => {
    res.json(getRecursiveSynthesisHealth());
});

app.get('/api/synthesis/recursive/:cycle_id', (req, res) => {
    const cycle = getRecursiveCycle(req.params.cycle_id);
    if (!cycle) {
        return res.status(404).json({ error: 'cycle_not_found' });
    }
    res.json(cycle);
});

// ─── PASSIVE ATOMIZATION WATCHER ───

app.get('/api/watcher/status', (req, res) => {
    res.json(getWatcherStatus());
});

app.post('/api/watcher/start', (req, res) => {
    const result = startWatcher();
    logEvent('info', `Watcher start requested: ${result.status}`);
    res.json(result);
});

app.post('/api/watcher/stop', (req, res) => {
    const result = stopWatcher();
    logEvent('info', `Watcher stop requested: ${result.status}`);
    res.json(result);
});

app.post('/api/watcher/sweep', async (req, res) => {
    try {
        const result = await triggerSweep();
        logEvent('info', 'Full re-sweep triggered');
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.get('/api/watcher/index', (req, res) => {
    const index = getFileIndex();
    const limit = parseInt(req.query.limit) || 100;
    const entries = Object.entries(index)
        .sort((a, b) => (b[1].last_processed || '').localeCompare(a[1].last_processed || ''))
        .slice(0, limit)
        .map(([filepath, data]) => ({ filepath, ...data }));
    res.json({
        total: Object.keys(index).length,
        entries,
    });
});

app.post('/api/watcher/reprocess', async (req, res) => {
    const filepath = req.body?.filepath;
    if (!filepath) {
        return res.status(400).json({ error: 'filepath required' });
    }
    try {
        const result = await reprocessFile(filepath);
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ─── COVERAGE ASSESSOR (SUPPORTIVE LAYER) ───

app.get('/api/coverage/report', (req, res) => {
    res.json(getCoverageReport());
});

app.get('/api/coverage/gaps', (req, res) => {
    const limit = parseInt(req.query.limit) || 50;
    res.json(getCoverageGaps(limit));
});

app.post('/api/coverage/scan', (req, res) => {
    try {
        const report = scanCoverage();
        logEvent('info', 'Coverage scan triggered manually');
        res.json(report);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/coverage/fill-gaps', (req, res) => {
    const maxFiles = parseInt(req.body?.max_files) || 50;
    const result = fillGaps(maxFiles);
    res.json(result);
});

// ─── PARADIGM REFLECTOR (META LAYER) ───

app.get('/api/reflector/status', (req, res) => {
    res.json(getReflectorStatus());
});

app.get('/api/reflector/insights', (req, res) => {
    const limit = parseInt(req.query.limit) || 10;
    res.json(getReflectionInsights(limit));
});

app.post('/api/reflector/reflect', async (req, res) => {
    try {
        const result = await reflect();
        res.json(result);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

// ─── THE THREE ONTOLOGICAL ROLES ───
// Triad = Structure. Recursion = Energy. Federation = Agency.

app.get('/api/triad', (req, res) => {
    res.json(getTriadStatus());
});

app.get('/api/triad/layers', (req, res) => {
    res.json(TRIAD_LAYERS);
});

app.post('/api/triad/audit', async (req, res) => {
    try {
        const audit = await auditTriad();
        res.json(audit);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.post('/api/triad/assess', (req, res) => {
    const { subsystem, components } = req.body || {};
    if (!subsystem || !components) {
        return res.status(400).json({ error: 'subsystem and components required' });
    }
    const assessment = assessTriadCompleteness(subsystem, components);
    res.json(assessment);
});

// Full ontological framework — all three pillars as one
app.get('/api/ontology', (req, res) => {
    res.json(getOntology());
});

// Federation of Sovereigns — who is acting?
app.get('/api/federation', (req, res) => {
    res.json(FEDERATION_OF_SOVEREIGNS);
});

// Recursive Magnification — is this alive?
app.get('/api/recursion', (req, res) => {
    res.json(RECURSIVE_MAGNIFICATION);
});

// ─── THE PIPELINE: ATOMIZE ───
// This is the real deal. File in → Scout processes → atoms stored → atoms returned.

app.post('/api/atomize', upload.array('files', 20), async (req, res) => {
    try {
        const files = req.files || [];
        const textContent = req.body.text || '';

        if (files.length === 0 && !textContent) {
            return res.status(400).json({ error: 'No files or text provided' });
        }

        logEvent('info', `Pipeline triggered — ${files.length} file(s), ${textContent.length} chars text`);

        const results = [];

        // Process uploaded files
        for (const file of files) {
            const content = file.buffer.toString('utf-8');

            // Detect artifact type
            const ext = path.extname(file.originalname).slice(1).toLowerCase();
            const artifactType = getArtifactType(ext);

            // HOLD₁ — Record intake
            const intake = recordIntake({
                filename: file.originalname,
                mimeType: file.mimetype,
                sizeBytes: file.size,
                artifactType,
                content,
            });

            logEvent('info', `HOLD₁: ${file.originalname} → ${artifactType} (${file.size} bytes)`);

            // AGENT — Send to Scout
            try {
                const result = await atomize(content, file.originalname);

                // HOLD₂ — Store atoms
                const stored = storeAtoms(result.atoms, intake.id);

                logEvent('success', `HOLD₂: ${stored.length} atoms extracted from ${file.originalname} in ${result.elapsed_ms}ms`);

                results.push({
                    intake_id: intake.id,
                    filename: file.originalname,
                    artifact_type: artifactType,
                    atoms: stored,
                    model: result.model,
                    elapsed_ms: result.elapsed_ms,
                    input_chars: result.input_chars,
                });
            } catch (err) {
                logEvent('error', `Atomization failed for ${file.originalname}: ${err.message}`);
                results.push({
                    intake_id: intake.id,
                    filename: file.originalname,
                    error: err.message,
                });
            }
        }

        // Process raw text input
        if (textContent) {
            const intake = recordIntake({
                filename: 'text-input',
                mimeType: 'text/plain',
                sizeBytes: Buffer.byteLength(textContent),
                artifactType: 'DOCUMENT',
                content: textContent,
            });

            try {
                const result = await atomize(textContent, 'text-input');
                const stored = storeAtoms(result.atoms, intake.id);

                logEvent('success', `HOLD₂: ${stored.length} atoms from text input in ${result.elapsed_ms}ms`);

                results.push({
                    intake_id: intake.id,
                    filename: 'text-input',
                    artifact_type: 'DOCUMENT',
                    atoms: stored,
                    model: result.model,
                    elapsed_ms: result.elapsed_ms,
                });
            } catch (err) {
                logEvent('error', `Text atomization failed: ${err.message}`);
                results.push({
                    intake_id: intake.id,
                    filename: 'text-input',
                    error: err.message,
                });
            }
        }

        const totalAtoms = results.reduce((sum, r) => sum + (r.atoms?.length || 0), 0);
        logEvent('info', `Pipeline complete — ${totalAtoms} total atoms extracted`);

        res.json({
            success: true,
            results,
            totalAtoms,
            stats: getStats(),
        });
    } catch (err) {
        logEvent('error', `Pipeline error: ${err.message}`);
        res.status(500).json({ error: err.message });
    }
});

// ─── UI Hosting (Production Build) ───

if (fs.existsSync(DIST_INDEX)) {
    app.use(express.static(DIST_DIR));
    app.get(/^\/(?!api).*/, (_req, res) => {
        res.sendFile(DIST_INDEX);
    });
} else {
    app.get('/', (_req, res) => {
        res.status(503).json({
            error: 'ui_not_built',
            hint: 'Run `npm --prefix genesis-console run build` to generate the UI bundle.',
        });
    });
}

// ─── Global Error Guard ───

app.use((err, req, res, next) => {
    void next;
    const msg = err?.message || 'unknown_server_error';
    logEvent('error', `Unhandled server error [${req.method} ${req.originalUrl}]: ${msg}`);
    res.status(500).json({
        error: 'internal_server_error',
        message: msg,
    });
});

// ─── Artifact Type Detection ───

function getArtifactType(ext) {
    const map = {
        py: 'CODE', js: 'CODE', ts: 'CODE', jsx: 'CODE', tsx: 'CODE',
        go: 'CODE', rs: 'CODE', sh: 'CODE', rb: 'CODE', java: 'CODE',
        json: 'DATA', csv: 'DATA', yaml: 'DATA', yml: 'DATA', toml: 'DATA', xml: 'DATA',
        md: 'DOCUMENT', txt: 'DOCUMENT', pdf: 'DOCUMENT', docx: 'DOCUMENT', html: 'DOCUMENT',
        mp3: 'AUDIO', wav: 'AUDIO', m4a: 'AUDIO', ogg: 'AUDIO',
        mp4: 'VIDEO', mov: 'VIDEO', webm: 'VIDEO',
        png: 'IMAGE', jpg: 'IMAGE', jpeg: 'IMAGE', svg: 'IMAGE', gif: 'IMAGE',
    };
    return map[ext] || 'DOCUMENT';
}

// ─── Start Server ───

process.on('unhandledRejection', (reason) => {
    const msg = reason instanceof Error ? reason.message : String(reason || 'unknown_rejection');
    logEvent('error', `Unhandled promise rejection: ${msg}`);
});

process.on('uncaughtException', (error) => {
    const msg = error instanceof Error ? error.message : String(error || 'unknown_exception');
    logEvent('error', `Uncaught exception: ${msg}`);
});

app.listen(PORT, () => {
    logEvent('info', `Genesis API server started on port ${PORT}`);

    // Bootstrap the Three Ontological Roles — register all services
    bootstrapTriad();

    startSyntheticMonitor({ port: PORT });
    console.log(`
  ╔══════════════════════════════════════════════════╗
  ║     GENESIS API — Sovereign Backend              ║
  ║     http://localhost:${PORT}                          ║
  ║                                                  ║
  ║     THREE ONTOLOGICAL ROLES: ACTIVE              ║
  ║     ┌─────────────────────────────────────┐      ║
  ║     │ TRIAD     = Structure  (Anatomy)    │      ║
  ║     │ RECURSION = Energy     (Metabolism)  │      ║
  ║     │ FEDERATION = Agency   (Who Acts)    │      ║
  ║     └─────────────────────────────────────┘      ║
  ║     CORE → SUPPORTIVE → META                     ║
  ║     Truth Forge · Primitive Engine · Cred Atlas   ║
  ║     File → Scout → Atoms → Disk                  ║
  ╚══════════════════════════════════════════════════╝
  `);

    // Check Ollama on startup
    checkOllama().then(status => {
        if (status.connected) {
            console.log(`  ✓ Ollama connected — ${status.models.length} model(s) available`);
            status.models.forEach(m => console.log(`    • ${m.name}`));
            // Auto-start all three layers
            console.log('  ⟳ Starting three-layer atom architecture...');
            setTimeout(() => {
                startWatcher();           // CORE: passive file watching
                startCoverageMonitor();   // SUPPORTIVE: gap detection
                startReflector();         // META: paradigm reflection
                console.log('  ✓ CORE: Watcher active — monitoring truth_forge/');
                console.log('  ✓ SUPPORTIVE: Coverage assessor active — scanning for gaps');
                console.log('  ✓ META: Paradigm reflector active — self-awareness engaged');
            }, 3000);
        } else {
            console.log('  ✗ Ollama not detected at localhost:11434');
            console.log('    Start Ollama to enable the three-layer atom architecture');
            console.log('    All layers auto-start when Ollama becomes available');
            const ollamaCheckInterval = setInterval(async () => {
                const check = await checkOllama();
                if (check.connected) {
                    clearInterval(ollamaCheckInterval);
                    console.log('  ✓ Ollama detected — starting three-layer architecture');
                    startWatcher();
                    startCoverageMonitor();
                    startReflector();
                }
            }, 30000);
        }
        console.log('');
    });
});
