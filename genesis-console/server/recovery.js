/* global process */
// Genesis Console — Self-Healing Recovery
// TRIAD: SUPPORTIVE (self-healing) | FEDERATION: PRIMITIVE ENGINE | RECURSION: DEVELOPER
// "I build the bridge." Detects failures and builds repair sequences.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONSOLE_DIR = path.join(__dirname, '..');
const DATA_DIR = path.join(CONSOLE_DIR, 'data');
const RECOVERY_FILE = path.join(DATA_DIR, 'recovery_runs.jsonl');

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

const MAX_PENDING_EVENTS = 200;
const MAX_LOG_CHARS = 6000;

const state = {
    running: false,
    started_at: null,
    current_run_id: null,
    last_completed_at: null,
    last_status: 'idle',
    pending_events: [],
};

function nowIso() {
    return new Date().toISOString();
}

function appendRecord(filepath, record) {
    const line = `${JSON.stringify({ ...record, _ts: nowIso() })}\n`;
    fs.appendFileSync(filepath, line, 'utf-8');
}

function readRecords(filepath) {
    if (!fs.existsSync(filepath)) return [];
    const content = fs.readFileSync(filepath, 'utf-8').trim();
    if (!content) return [];
    return content
        .split('\n')
        .map((line) => {
            try {
                return JSON.parse(line);
            } catch {
                return null;
            }
        })
        .filter(Boolean);
}

function keepTail(text, maxChars = MAX_LOG_CHARS) {
    const value = String(text || '');
    if (value.length <= maxChars) return value;
    return value.slice(value.length - maxChars);
}

function enqueueEvent(event) {
    state.pending_events.push({
        id: crypto.randomUUID(),
        received_at: nowIso(),
        source: event.source || 'unknown',
        level: event.level || 'error',
        reason: String(event.reason || 'unspecified error'),
        context: event.context || {},
    });
    if (state.pending_events.length > MAX_PENDING_EVENTS) {
        state.pending_events.splice(0, state.pending_events.length - MAX_PENDING_EVENTS);
    }
}

async function runCommand(command, args, options = {}) {
    const timeoutMs = options.timeoutMs || 180000;
    const cwd = options.cwd || CONSOLE_DIR;

    return await new Promise((resolve) => {
        const started = Date.now();
        const child = spawn(command, args, {
            cwd,
            env: process.env,
            stdio: ['ignore', 'pipe', 'pipe'],
        });

        let stdout = '';
        let stderr = '';
        let timedOut = false;

        const timer = setTimeout(() => {
            timedOut = true;
            child.kill('SIGTERM');
            setTimeout(() => child.kill('SIGKILL'), 3000);
        }, timeoutMs);

        child.stdout.on('data', (chunk) => {
            stdout = keepTail(stdout + chunk.toString('utf-8'));
        });
        child.stderr.on('data', (chunk) => {
            stderr = keepTail(stderr + chunk.toString('utf-8'));
        });

        child.on('error', (error) => {
            clearTimeout(timer);
            resolve({
                ok: false,
                code: null,
                signal: null,
                timed_out: false,
                duration_ms: Date.now() - started,
                stdout,
                stderr: keepTail(`${stderr}\n${error.message}`),
                command: `${command} ${args.join(' ')}`,
            });
        });

        child.on('close', (code, signal) => {
            clearTimeout(timer);
            resolve({
                ok: !timedOut && code === 0,
                code,
                signal,
                timed_out: timedOut,
                duration_ms: Date.now() - started,
                stdout,
                stderr,
                command: `${command} ${args.join(' ')}`,
            });
        });
    });
}

async function runStep(id, title, fn) {
    const started = Date.now();
    try {
        const details = await fn();
        return {
            id,
            title,
            ok: details?.ok !== false,
            duration_ms: Date.now() - started,
            details: details || {},
        };
    } catch (error) {
        return {
            id,
            title,
            ok: false,
            duration_ms: Date.now() - started,
            details: {
                error: error.message,
            },
        };
    }
}

async function checkApiHealth() {
    const port = process.env.PORT || '3141';
    const url = `http://127.0.0.1:${port}/api/health`;
    try {
        const response = await fetch(url, { signal: AbortSignal.timeout(4000) });
        if (!response.ok) {
            return {
                ok: false,
                status: response.status,
                url,
                summary: `health endpoint responded ${response.status}`,
            };
        }
        const payload = await response.json();
        return {
            ok: payload.status === 'operational',
            url,
            backend_status: payload.status,
            ollama_connected: Boolean(payload.ollama?.connected),
            model_count: payload.ollama?.models?.length || 0,
        };
    } catch (error) {
        return {
            ok: false,
            url,
            summary: `health check failed: ${error.message}`,
        };
    }
}

async function runApiSmokeChecks() {
    const port = process.env.PORT || '3141';
    const routes = [
        '/api/health',
        '/api/kiosk/status',
        '/api/mission/history?limit=1',
        '/api/recovery/status',
        '/api/sentinel/status',
    ];
    const results = [];
    let ok = true;

    for (const route of routes) {
        const url = `http://127.0.0.1:${port}${route}`;
        try {
            const response = await fetch(url, { signal: AbortSignal.timeout(5000) });
            const routeOk = response.ok;
            if (!routeOk) ok = false;
            results.push({
                route,
                status: response.status,
                ok: routeOk,
            });
        } catch (error) {
            ok = false;
            results.push({
                route,
                ok: false,
                error: error.message,
            });
        }
    }

    return {
        ok,
        checks: results,
    };
}

async function checkOllamaPort() {
    const probe = await runCommand('bash', ['-lc', 'lsof -iTCP:11434 -sTCP:LISTEN -n -P || true'], {
        timeoutMs: 8000,
    });
    const lines = probe.stdout
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean);
    const hasOllama = lines.some((line) => line.toLowerCase().includes('ollama'));
    return {
        ok: probe.ok,
        has_listener: lines.length > 0,
        has_ollama_listener: hasOllama,
        listeners: lines.slice(0, 10),
    };
}

async function executeRecovery(events) {
    const runId = crypto.randomUUID();
    state.running = true;
    state.started_at = nowIso();
    state.current_run_id = runId;
    state.last_status = 'running';

    const steps = [];
    const runStart = Date.now();

    const nodeModulesExists = fs.existsSync(path.join(CONSOLE_DIR, 'node_modules'));
    if (!nodeModulesExists) {
        steps.push(await runStep('install_dependencies', 'Install dependencies', async () => {
            const result = await runCommand('npm', ['--prefix', CONSOLE_DIR, 'install'], { timeoutMs: 300000 });
            return { ...result, ok: result.ok };
        }));
    } else {
        steps.push({
            id: 'install_dependencies',
            title: 'Install dependencies',
            ok: true,
            duration_ms: 0,
            details: {
                skipped: true,
                reason: 'node_modules_present',
            },
        });
    }

    const lintStep = await runStep('lint', 'Run lint', async () => {
        const result = await runCommand('npm', ['--prefix', CONSOLE_DIR, 'run', 'lint'], { timeoutMs: 240000 });
        return { ...result, ok: result.ok };
    });
    steps.push(lintStep);

    const buildStep = await runStep('build', 'Run build', async () => {
        const result = await runCommand('npm', ['--prefix', CONSOLE_DIR, 'run', 'build'], { timeoutMs: 240000 });
        return { ...result, ok: result.ok };
    });
    steps.push(buildStep);

    if (!lintStep.ok || !buildStep.ok) {
        steps.push(await runStep('repair_dependencies', 'Repair dependencies', async () => {
            const result = await runCommand('npm', ['--prefix', CONSOLE_DIR, 'install'], { timeoutMs: 300000 });
            return { ...result, ok: result.ok };
        }));

        if (!lintStep.ok) {
            steps.push(await runStep('lint_retry', 'Re-run lint after repair', async () => {
                const result = await runCommand('npm', ['--prefix', CONSOLE_DIR, 'run', 'lint'], { timeoutMs: 240000 });
                return { ...result, ok: result.ok };
            }));
        }

        if (!buildStep.ok) {
            steps.push(await runStep('build_retry', 'Re-run build after repair', async () => {
                const result = await runCommand('npm', ['--prefix', CONSOLE_DIR, 'run', 'build'], { timeoutMs: 240000 });
                return { ...result, ok: result.ok };
            }));
        }
    }

    steps.push(await runStep('health_check', 'Check API health', async () => {
        return await checkApiHealth();
    }));

    steps.push(await runStep('api_smoke', 'Run API smoke checks', async () => {
        return await runApiSmokeChecks();
    }));

    steps.push(await runStep('ollama_probe', 'Probe Ollama listener', async () => {
        return await checkOllamaPort();
    }));

    const ok = steps.every((step) => step.ok);
    const runRecord = {
        kind: 'auto_recovery_run',
        run_id: runId,
        started_at: state.started_at,
        completed_at: nowIso(),
        duration_ms: Date.now() - runStart,
        status: ok ? 'recovered' : 'degraded',
        triggered_by: events,
        step_count: steps.length,
        failed_steps: steps.filter((step) => !step.ok).map((step) => step.id),
        steps,
        summary: ok
            ? 'Recovery checks passed (lint/build/health/probe).'
            : 'Recovery finished with failed steps. Inspect run details.',
    };

    appendRecord(RECOVERY_FILE, runRecord);
    state.running = false;
    state.started_at = null;
    state.current_run_id = null;
    state.last_completed_at = runRecord.completed_at;
    state.last_status = runRecord.status;

    if (state.pending_events.length > 0) {
        void scheduleRecovery();
    }

    return runRecord;
}

async function scheduleRecovery() {
    if (state.running) return null;
    if (state.pending_events.length === 0) return null;
    const events = state.pending_events.splice(0, state.pending_events.length);
    return await executeRecovery(events);
}

export function queueRecoveryFromError(event = {}) {
    enqueueEvent({
        source: event.source || 'server_log',
        level: event.level || 'error',
        reason: event.reason || 'Unspecified error',
        context: event.context || {},
    });
    void scheduleRecovery();
    return {
        queued: true,
        pending_events: state.pending_events.length,
    };
}

export function getRecoveryStatus() {
    const runs = readRecords(RECOVERY_FILE);
    const latest = runs.length ? runs[runs.length - 1] : null;
    return {
        running: state.running,
        started_at: state.started_at,
        current_run_id: state.current_run_id,
        pending_events: state.pending_events.length,
        last_completed_at: state.last_completed_at,
        last_status: state.last_status,
        latest_run: latest,
    };
}

export function getRecoveryRuns(limit = 20) {
    const value = Number.isFinite(Number(limit)) ? Math.max(1, Math.min(200, Number(limit))) : 20;
    const runs = readRecords(RECOVERY_FILE);
    return {
        runs: runs.slice(-value).reverse(),
        total: runs.length,
        generated_at: nowIso(),
    };
}
