/* global process */
// Genesis Console — Synthetic User Monitor
// TRIAD: SUPPORTIVE (E2E validation) | FEDERATION: CREDENTIAL ATLAS | RECURSION: RESEARCHER
// "I verify existence." Continuous simulation to certify system health.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';
import { logEvent, recordIntake, storeAtoms, getAtoms } from './store.js';
import { chatAssistant } from './assistant.js';
import { runMission } from './support.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CONSOLE_DIR = path.join(__dirname, '..');
const DATA_DIR = path.join(CONSOLE_DIR, 'data');
const RUNS_FILE = path.join(DATA_DIR, 'synthetic_runs.jsonl');
const FEEDBACK_FILE = path.join(DATA_DIR, 'synthetic_feedback.jsonl');
const DEPTH_DECISIONS_FILE = path.join(DATA_DIR, 'synthetic_depth_decisions.jsonl');

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

const MIN_INTERVAL_MS = 60_000;
const DEFAULT_INTERVAL_MS = 2 * 60_000;
const STABILITY_TARGET_STREAK = Math.max(3, Number(process.env.SYNTHETIC_STABILITY_TARGET_STREAK) || 20);
const STABILITY_WINDOW_SIZE = Math.max(10, Number(process.env.SYNTHETIC_STABILITY_WINDOW_SIZE) || 50);
const STABILITY_PASS_RATE_TARGET = Math.min(
    1,
    Math.max(0.5, Number(process.env.SYNTHETIC_STABILITY_PASS_RATE_TARGET) || 0.98),
);
const ATOM_STABILITY_STREAK_TARGET = Math.max(3, Number(process.env.SYNTHETIC_ATOM_STABILITY_STREAK_TARGET) || 8);
const ATOM_STABILITY_WINDOW_SIZE = Math.max(5, Number(process.env.SYNTHETIC_ATOM_STABILITY_WINDOW_SIZE) || 20);
const ATOM_STABILITY_PASS_RATE_TARGET = Math.min(
    1,
    Math.max(0.5, Number(process.env.SYNTHETIC_ATOM_STABILITY_PASS_RATE_TARGET) || 0.95),
);
const ATOM_MIN_PER_ACTION = Math.max(1, Number(process.env.SYNTHETIC_ATOM_MIN_PER_ACTION) || 1);
const ATOM_MIN_COUNT_PER_RUN = Math.max(1, Number(process.env.SYNTHETIC_ATOM_MIN_COUNT_PER_RUN) || 40);
const MAX_DEPTH_QUESTIONS = Math.max(1, Math.min(8, Number(process.env.SYNTHETIC_DEPTH_QUESTION_LIMIT) || 5));
const DEPTH_AUTO_APPROVE = process.env.SYNTHETIC_DEPTH_AUTO_APPROVE !== '0';

const state = {
    enabled: process.env.SYNTHETIC_MONITOR_ENABLED !== '0',
    interval_ms: Math.max(MIN_INTERVAL_MS, Number(process.env.SYNTHETIC_MONITOR_INTERVAL_MS) || DEFAULT_INTERVAL_MS),
    running: false,
    started_at: null,
    last_started_at: null,
    last_completed_at: null,
    last_status: 'idle',
    last_run_id: null,
    next_run_at: null,
    last_error: null,
    timer: null,
    base_url: null,
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

function toIsoDateValue(value) {
    const ts = Date.parse(value || '');
    return Number.isFinite(ts) ? ts : 0;
}

function truncateText(value, max = 1800) {
    const text = String(value || '').trim();
    if (text.length <= max) return text;
    return `${text.slice(0, max)}...`;
}

function extractJsonObject(text) {
    const value = String(text || '').trim();
    if (!value) return null;

    const candidates = [
        value,
        (value.match(/\{[\s\S]*\}/) || [])[0],
    ].filter(Boolean);

    for (const candidate of candidates) {
        try {
            const parsed = JSON.parse(candidate);
            if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) return parsed;
        } catch {
            // continue
        }
    }
    return null;
}

function extractJsonArray(text) {
    const value = String(text || '').trim();
    if (!value) return null;

    const candidates = [
        value,
        (value.match(/\[[\s\S]*\]/) || [])[0],
    ].filter(Boolean);

    for (const candidate of candidates) {
        try {
            const parsed = JSON.parse(candidate);
            if (Array.isArray(parsed)) return parsed;
        } catch {
            // continue
        }
    }
    return null;
}

function percentile(values, p) {
    if (!values.length) return 0;
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.min(sorted.length - 1, Math.max(0, Math.ceil((p / 100) * sorted.length) - 1));
    return sorted[index];
}

function normalizeDepthQuestion(raw = {}, fallback = {}) {
    const question = truncateText(raw.question || raw.prompt || fallback.question || '', 320);
    if (!question) return null;

    const functionality = truncateText(
        raw.functionality || raw.capability || raw.suggested_functionality || fallback.functionality || '',
        320,
    );
    const why = truncateText(raw.why || raw.reason || fallback.why || '', 320);

    const priorityRaw = String(raw.priority || fallback.priority || 'medium').toLowerCase();
    const priority = ['critical', 'high', 'medium', 'low'].includes(priorityRaw) ? priorityRaw : 'medium';
    const basedOn = Array.isArray(raw.based_on_atom_ids) && raw.based_on_atom_ids.length
        ? raw.based_on_atom_ids
        : (Array.isArray(fallback.based_on_atom_ids) ? fallback.based_on_atom_ids : []);

    return {
        question_id: raw.question_id || fallback.question_id || crypto.randomUUID(),
        question,
        why: why || 'Derived from recent knowledge atoms for depth expansion.',
        suggested_functionality: functionality || 'Implement an observable capability that answers this question.',
        priority,
        based_on_atom_ids: basedOn.slice(0, 6),
    };
}

function sanitizeDepthQuestions(items = [], fallbackAtoms = [], limit = MAX_DEPTH_QUESTIONS) {
    const seen = new Set();
    const cleaned = [];
    for (const item of items) {
        const normalized = normalizeDepthQuestion(item);
        if (!normalized) continue;
        const key = normalized.question.toLowerCase();
        if (seen.has(key)) continue;
        seen.add(key);
        cleaned.push(normalized);
        if (cleaned.length >= limit) break;
    }

    if (cleaned.length > 0) return cleaned;

    return fallbackAtoms.slice(0, limit).map((atom, idx) => normalizeDepthQuestion({
        question: `What deeper capability should we build from this signal: ${truncateText(atom.content, 140)}?`,
        why: `Atom type=${atom.type}, confidence=${atom.confidence ?? 'n/a'}`,
        suggested_functionality: 'Create a targeted workflow, UI affordance, or automation that operationalizes this signal.',
        priority: idx === 0 ? 'high' : 'medium',
        based_on_atom_ids: [atom.id],
    })).filter(Boolean);
}

function getAtomStabilityMetrics(runs) {
    const ordered = [...runs].sort((a, b) => toIsoDateValue(a.completed_at || a._ts) - toIsoDateValue(b.completed_at || b._ts));
    const recent = ordered.slice(-ATOM_STABILITY_WINDOW_SIZE);
    const expectedMinForRun = (run) => Math.max(
        ATOM_MIN_COUNT_PER_RUN,
        (Number(run.step_count) || 0) * ATOM_MIN_PER_ACTION,
    );
    const isRunPass = (run) => {
        if (!run) return false;
        if (run.knowledge_atom_axiom_pass !== true) return false;
        return Number(run.knowledge_atom_count || 0) >= expectedMinForRun(run);
    };

    const recentPassing = recent.filter((run) => isRunPass(run)).length;
    const passRate = recent.length ? recentPassing / recent.length : 0;

    let consecutivePass = 0;
    for (let i = ordered.length - 1; i >= 0; i -= 1) {
        if (isRunPass(ordered[i])) {
            consecutivePass += 1;
        } else {
            break;
        }
    }

    const atomCounts = recent
        .map((run) => Number(run.knowledge_atom_count || 0))
        .filter((count) => Number.isFinite(count) && count > 0);
    const avgAtomCount = atomCounts.length
        ? Math.round(atomCounts.reduce((sum, count) => sum + count, 0) / atomCounts.length)
        : 0;
    const minAtomCount = atomCounts.length ? Math.min(...atomCounts) : 0;

    const hasSufficientSample = recent.length >= Math.min(ATOM_STABILITY_WINDOW_SIZE, 5);
    const isStable = hasSufficientSample
        && consecutivePass >= ATOM_STABILITY_STREAK_TARGET
        && passRate >= ATOM_STABILITY_PASS_RATE_TARGET;

    return {
        target_streak: ATOM_STABILITY_STREAK_TARGET,
        window_size: ATOM_STABILITY_WINDOW_SIZE,
        pass_rate_target: ATOM_STABILITY_PASS_RATE_TARGET,
        min_atoms_per_action: ATOM_MIN_PER_ACTION,
        min_atoms_per_run: ATOM_MIN_COUNT_PER_RUN,
        total_runs: ordered.length,
        recent_runs: recent.length,
        recent_passing_runs: recentPassing,
        rolling_pass_rate: Number(passRate.toFixed(4)),
        consecutive_passing_runs: consecutivePass,
        avg_atoms_per_run: avgAtomCount,
        min_atoms_in_window: minAtomCount,
        is_stable: isStable,
        stable_reason: isStable ? 'atom_production_stable' : 'atom_production_converging',
        focus_mode: isStable ? 'depth_expansion' : 'atom_stabilization',
    };
}

function collectRunAtoms(stepList = [], maxAtoms = 160) {
    const atomIds = stepList.flatMap((step) => step.knowledge_atoms_produced?.atom_ids || []);
    if (!atomIds.length) return [];

    const idSet = new Set(atomIds);
    const needed = Math.max(maxAtoms, atomIds.length + 20);
    const recentAtoms = getAtoms(needed);
    return recentAtoms
        .filter((atom) => idSet.has(atom.id))
        .slice(0, maxAtoms);
}

async function generateDepthQuestions(payload = {}) {
    const atoms = Array.isArray(payload.atoms) ? payload.atoms : [];
    if (!atoms.length) {
        return {
            ok: true,
            questions: [],
            generated_by: 'heuristic_fallback',
            model: null,
            raw: '',
        };
    }

    const atomDigest = atoms.slice(0, 12).map((atom, idx) => (
        `${idx + 1}. [${atom.id}] type=${atom.type}; conf=${atom.confidence}; content=${truncateText(atom.content, 160)}`
    )).join('\n');
    const prompt = [
        'You are the Synthetic Depth Engine for Genesis.',
        'Use the recent knowledge atoms to create deeper operator questions that should drive new functionality.',
        'Return JSON only in this exact shape:',
        '{ "questions": [ { "question": "", "why": "", "suggested_functionality": "", "priority": "high|medium|low", "based_on_atom_ids": [""] } ] }',
        `Limit questions to ${MAX_DEPTH_QUESTIONS}.`,
        '',
        `Run ID: ${payload.run_id}`,
        `Atom stability mode: ${payload.atom_stability?.focus_mode || 'unknown'}`,
        `Longevity stable: ${payload.longevity?.is_stable === true ? 'yes' : 'no'}`,
        'Recent atoms:',
        atomDigest,
    ].join('\n');

    const response = await chatAssistant({
        route: '/synthetic/depth',
        message: prompt,
        snapshot: {
            source: 'synthetic_depth_loop',
            run_id: payload.run_id,
            atom_stability: payload.atom_stability || {},
            atom_count: atoms.length,
        },
    });

    const raw = truncateText(response?.message?.content || '', 2800);
    const parsedObject = extractJsonObject(raw);
    const parsedArray = extractJsonArray(raw);
    const candidates = Array.isArray(parsedObject?.questions)
        ? parsedObject.questions
        : (Array.isArray(parsedArray) ? parsedArray : []);

    return {
        ok: true,
        questions: sanitizeDepthQuestions(candidates, atoms, MAX_DEPTH_QUESTIONS),
        generated_by: parsedObject || parsedArray ? 'assistant_chat' : 'heuristic_fallback',
        model: response?.message?.model || null,
        raw,
    };
}

function buildAtomStabilityMissionPrompt(payload = {}) {
    return [
        `Synthetic atom stabilization run ${payload.run_id}.`,
        'Priority: stabilize knowledge atom production before capability expansion.',
        `Current atom stability: streak=${payload.atom_stability?.consecutive_passing_runs || 0}/${payload.atom_stability?.target_streak || 0}, pass_rate=${payload.atom_stability?.rolling_pass_rate || 0}.`,
        `Minimum atoms per run target: ${payload.atom_stability?.min_atoms_per_run || ATOM_MIN_COUNT_PER_RUN}.`,
        `Observed atoms this run: ${payload.knowledge_atom_count || 0}.`,
        '',
        'Required outcomes:',
        '1. Remove atom production instability and enforce deterministic generation.',
        '2. Add verification tests for atom pipeline and synthetic action atom axiom.',
        '3. Increase visibility for atom failures and degraded pathways.',
    ].join('\n');
}

function buildDepthFunctionalityPrompt(payload = {}) {
    const questions = Array.isArray(payload.questions) ? payload.questions : [];
    const top = questions.slice(0, MAX_DEPTH_QUESTIONS).map((item, idx) => (
        `${idx + 1}. Q: ${item.question}\n   Why: ${item.why}\n   Build: ${item.suggested_functionality}\n   Priority: ${item.priority}`
    )).join('\n');

    return [
        `Depth expansion mission from synthetic run ${payload.run_id}.`,
        'Use these atom-derived questions to grow product functionality.',
        'Convert each question into implementable plan nodes with tests.',
        '',
        'Questions:',
        top || '1. none',
        '',
        'Definition of done:',
        '1. Every question maps to an executable capability change.',
        '2. Functional changes include validation and user-visible affordances.',
        '3. New behavior produces measurable knowledge atoms.',
    ].join('\n');
}

function getLatestRunRecordByRunId(runId) {
    if (!runId) return null;
    const runs = readRecords(RUNS_FILE);
    for (let i = runs.length - 1; i >= 0; i -= 1) {
        if (runs[i]?.run_id === runId) return runs[i];
    }
    return null;
}

function getDepthDecisionRecords() {
    return readRecords(DEPTH_DECISIONS_FILE).filter((record) => record.kind === 'synthetic_depth_decision');
}

function getLatestDepthDecisionByRunId(runId) {
    if (!runId) return null;
    const records = getDepthDecisionRecords();
    for (let i = records.length - 1; i >= 0; i -= 1) {
        if (records[i]?.run_id === runId) return records[i];
    }
    return null;
}

function normalizeDepthDecisionValue(value) {
    const normalized = String(value || '').trim().toLowerCase();
    if (normalized === 'approve' || normalized === 'approved') return 'approved';
    if (normalized === 'reject' || normalized === 'rejected') return 'rejected';
    return null;
}

function selectDepthQuestions(runRecord = {}, questionIds = []) {
    const questions = Array.isArray(runRecord.depth_questions) ? runRecord.depth_questions : [];
    if (!questionIds.length) return questions;
    const allow = new Set(questionIds);
    return questions.filter((question) => allow.has(question.question_id));
}

export function getSyntheticDepthDecision(payload = {}) {
    const runIdRaw = String(payload.run_id || '').trim();
    const allRuns = readRecords(RUNS_FILE);
    const latestRun = runIdRaw
        ? getLatestRunRecordByRunId(runIdRaw)
        : (allRuns.length ? allRuns[allRuns.length - 1] : null);
    const runId = latestRun?.run_id || null;
    const latestDecision = getLatestDepthDecisionByRunId(runId);
    const decisionRequired = Boolean(latestRun?.depth_decision_required);
    const pendingByRunStatus = latestRun?.depth_decision_status === 'pending';

    return {
        run_id: runId,
        loop_focus_mode: latestRun?.loop_focus_mode || null,
        decision_required: decisionRequired,
        pending: pendingByRunStatus && !latestDecision,
        decision: latestDecision || null,
        depth_questions: latestRun?.depth_questions || [],
        latest_depth_mission_run_id: latestRun?.depth_functionality_mission_run_id || null,
        recent_decisions: getDepthDecisionRecords().slice(-20).reverse(),
        generated_at: nowIso(),
    };
}

export function submitSyntheticDepthDecision(payload = {}) {
    const runId = String(payload.run_id || '').trim();
    if (!runId) return { ok: false, error: 'run_id_required' };

    const runRecord = getLatestRunRecordByRunId(runId);
    if (!runRecord) return { ok: false, error: 'run_not_found' };

    const decision = normalizeDepthDecisionValue(payload.decision);
    if (!decision) return { ok: false, error: 'decision_required' };

    const selectedQuestions = selectDepthQuestions(
        runRecord,
        Array.isArray(payload.question_ids) ? payload.question_ids : [],
    );
    if (decision === 'approved' && selectedQuestions.length === 0) {
        return { ok: false, error: 'no_depth_questions_selected' };
    }

    const priorDecision = getLatestDepthDecisionByRunId(runId);
    if (priorDecision) {
        return {
            ok: true,
            already_decided: true,
            decision: priorDecision,
            mission: priorDecision.mission_run_id
                ? { run_id: priorDecision.mission_run_id, status: priorDecision.mission_status || 'unknown' }
                : null,
        };
    }

    let mission = null;
    if (decision === 'approved') {
        const prompt = buildDepthFunctionalityPrompt({
            run_id: runId,
            questions: selectedQuestions,
        });
        mission = runMission({
            prompt,
            requested_tools: ['filesystem', 'build_test', 'models'],
            auto_execute: true,
        });
    }

    const record = {
        kind: 'synthetic_depth_decision',
        id: crypto.randomUUID(),
        run_id: runId,
        decision,
        question_ids: selectedQuestions.map((question) => question.question_id),
        question_count: selectedQuestions.length,
        note: truncateText(payload.note || '', 600) || null,
        decided_by: payload.decided_by || 'operator',
        mission_run_id: mission?.run_id || null,
        mission_status: mission?.status || null,
        created_at: nowIso(),
    };

    appendRecord(DEPTH_DECISIONS_FILE, record);
    appendRecord(FEEDBACK_FILE, {
        kind: 'synthetic_depth_decision',
        run_id: runId,
        decision,
        question_count: selectedQuestions.length,
        decided_by: record.decided_by,
        mission_run_id: record.mission_run_id,
        mission_status: record.mission_status,
        note: record.note,
        created_at: nowIso(),
    });

    logEvent(
        'info',
        `[synthetic] depth decision ${decision} run=${runId} questions=${selectedQuestions.length} mission=${record.mission_run_id || 'none'}`,
    );

    return {
        ok: true,
        decision: record,
        mission,
    };
}

function summarizeResult(step) {
    if (step.ok) return null;
    if (step.details?.error) return `${step.id}: ${step.details.error}`;
    if (step.details?.status) return `${step.id}: http_${step.details.status}`;
    return `${step.id}: unknown_failure`;
}

function summarizeObservedOutcome(step) {
    const detailStatus = step.details?.status ? `http_${step.details.status}` : null;
    const detailError = step.details?.error || null;
    const degraded = Boolean(step.details?.json?.degraded) || Boolean(step.details?.degraded);
    const outcomeType = !step.ok ? 'failed' : (degraded ? 'degraded_success' : 'success');
    return {
        outcome_type: outcomeType,
        http_status: step.details?.status || null,
        code: detailStatus,
        error: detailError,
        summary: detailError
            ? detailError
            : (detailStatus ? `response_${detailStatus}` : (step.ok ? 'completed' : 'failed')),
    };
}

function deriveConsequences(actionId, step, observedOutcome) {
    const failed = !step.ok;
    return {
        immediate: failed
            ? `Action ${actionId} failed and blocks confidence in this loop.`
            : `Action ${actionId} completed and advanced the loop.`,
        downstream: failed
            ? 'Builder remediation required; reliability signal reduced.'
            : 'Reliability signal improved and longevity confidence increased.',
        requires_builder_attention: failed,
        recovery_signal: failed,
        reliability_impact: failed ? -1 : 1,
        observed_outcome_type: observedOutcome.outcome_type,
    };
}

function sanitizeUsage(usage) {
    if (usage == null) return {};
    if (typeof usage === 'string') {
        return {
            usage_text: truncateText(usage, 300),
        };
    }
    if (typeof usage === 'object') {
        return usage;
    }
    return {
        usage_text: String(usage),
    };
}

function buildActionKnowledgeAtoms(payload = {}) {
    const usageText = truncateText(JSON.stringify(payload.usage || {}), 320);
    const observedText = truncateText(JSON.stringify(payload.observed_outcome || {}), 320);
    const consequenceText = truncateText(JSON.stringify(payload.consequences || {}), 320);

    return [
        {
            type: 'directive',
            content: `Synthetic action ${payload.action_id} intended outcome: ${payload.intended_outcome}.`,
            confidence: 0.78,
            entities: ['SyntheticLoop', payload.action_id],
            themes: ['synthetic', 'intended_outcome', 'qa'],
        },
        {
            type: 'fact',
            content: `Action ${payload.action_id} usage context: ${usageText}.`,
            confidence: 0.74,
            entities: ['SyntheticLoop', payload.action_id],
            themes: ['synthetic', 'usage', 'telemetry'],
        },
        {
            type: 'fact',
            content: `Action ${payload.action_id} observed outcome: ${observedText}.`,
            confidence: 0.8,
            entities: ['SyntheticLoop', payload.action_id],
            themes: ['synthetic', 'observed_outcome', 'verification'],
        },
        {
            type: 'relationship',
            content: `Action ${payload.action_id} consequences: ${consequenceText}.`,
            confidence: 0.76,
            entities: ['SyntheticLoop', payload.action_id, 'Consequence'],
            themes: ['synthetic', 'consequences', 'reliability'],
        },
    ];
}

async function executeActionStep(payload = {}) {
    const usage = sanitizeUsage(payload.usage);
    const step = await runStep(payload.id, payload.title, payload.execute);
    const observedOutcome = summarizeObservedOutcome(step);
    const consequences = deriveConsequences(payload.id, step, observedOutcome);
    const actionEvent = {
        action_id: payload.id,
        occurred_at: nowIso(),
        event_status: step.ok ? 'completed' : 'failed',
    };

    let atomsStored = [];
    let atomError = null;
    try {
        const atoms = buildActionKnowledgeAtoms({
            action_id: payload.id,
            intended_outcome: payload.intended_outcome,
            usage,
            observed_outcome: observedOutcome,
            consequences,
        });
        atomsStored = storeAtoms(atoms, payload.source_intake_id);
    } catch (error) {
        atomError = error.message;
    }

    const nextStep = {
        ...step,
        intended_outcome: payload.intended_outcome || 'unspecified',
        usage,
        observed_outcome: observedOutcome,
        action_event: actionEvent,
        consequences,
        knowledge_atoms_produced: {
            count: atomsStored.length,
            atom_ids: atomsStored.map((atom) => atom.id).slice(0, 20),
            source_intake_id: payload.source_intake_id,
        },
    };

    if (atomError || atomsStored.length === 0) {
        nextStep.ok = false;
        nextStep.details = {
            ...(nextStep.details || {}),
            knowledge_atoms_error: atomError || 'no_action_knowledge_atoms_produced',
        };
        nextStep.observed_outcome = {
            ...nextStep.observed_outcome,
            outcome_type: 'failed',
            summary: nextStep.details.knowledge_atoms_error,
        };
        nextStep.consequences = {
            ...nextStep.consequences,
            immediate: `Knowledge-atom axiom broken for action ${payload.id}.`,
            downstream: 'Loop invalidated until atom generation is restored.',
            requires_builder_attention: true,
            recovery_signal: true,
            reliability_impact: -2,
        };
    }

    return nextStep;
}

function getLongevityMetrics(runs) {
    const ordered = [...runs].sort((a, b) => toIsoDateValue(a.completed_at || a._ts) - toIsoDateValue(b.completed_at || b._ts));
    const recent = ordered.slice(-STABILITY_WINDOW_SIZE);
    const recentHealthy = recent.filter((run) => run.status === 'healthy').length;
    const passRate = recent.length ? recentHealthy / recent.length : 0;

    let consecutiveHealthy = 0;
    for (let i = ordered.length - 1; i >= 0; i -= 1) {
        if (ordered[i].status === 'healthy') {
            consecutiveHealthy += 1;
        } else {
            break;
        }
    }

    const nowMs = Date.now();
    const degradedLast24h = ordered.filter((run) => {
        if (run.status === 'healthy') return false;
        const completed = toIsoDateValue(run.completed_at || run._ts);
        return completed > 0 && (nowMs - completed) <= 24 * 60 * 60 * 1000;
    }).length;

    const durations = recent
        .map((run) => Number(run.duration_ms) || 0)
        .filter((duration) => duration > 0);

    const p95DurationMs = durations.length ? percentile(durations, 95) : 0;
    const avgDurationMs = durations.length
        ? Math.round(durations.reduce((sum, duration) => sum + duration, 0) / durations.length)
        : 0;

    const hasSufficientSample = recent.length >= Math.min(STABILITY_WINDOW_SIZE, 10);
    const isStable = hasSufficientSample
        && consecutiveHealthy >= STABILITY_TARGET_STREAK
        && passRate >= STABILITY_PASS_RATE_TARGET
        && degradedLast24h === 0;

    return {
        target_streak: STABILITY_TARGET_STREAK,
        window_size: STABILITY_WINDOW_SIZE,
        pass_rate_target: STABILITY_PASS_RATE_TARGET,
        total_runs: ordered.length,
        recent_runs: recent.length,
        consecutive_healthy: consecutiveHealthy,
        rolling_pass_rate: Number(passRate.toFixed(4)),
        degraded_last_24h: degradedLast24h,
        avg_duration_ms: avgDurationMs,
        p95_duration_ms: p95DurationMs,
        is_stable: isStable,
        stable_reason: isStable
            ? 'stability_targets_met'
            : 'still_converging',
    };
}

async function callApi(baseUrl, route, options = {}) {
    const timeoutMs = options.timeoutMs || 25_000;
    const method = options.method || 'GET';
    const url = `${baseUrl}${route}`;
    const request = {
        method,
        headers: options.headers || {},
        body: options.body,
        signal: AbortSignal.timeout(timeoutMs),
    };
    const started = Date.now();
    const response = await fetch(url, request);
    const elapsedMs = Date.now() - started;
    const text = await response.text();
    let json = null;
    if (text) {
        try {
            json = JSON.parse(text);
        } catch {
            json = null;
        }
    }
    return {
        ok: response.ok,
        status: response.status,
        elapsed_ms: elapsedMs,
        route,
        text,
        json,
    };
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

async function generatePersonaFeedback(payload = {}) {
    const failures = (payload.failed_steps || []).join(', ') || 'none';
    const quickSummary = truncateText(payload.summary || '', 800);
    const journeyOverview = (payload.steps || [])
        .map((step) => `${step.id}:${step.ok ? 'ok' : 'fail'}`)
        .join(', ');

    const prompt = [
        'Act as the real operator persona using Genesis in kiosk mode.',
        'Speak in first person as the user.',
        'Give concise, blunt product feedback from lived usage.',
        'Include exactly four sections:',
        '1) What worked',
        '2) What broke',
        '3) What confused me',
        '4) Highest-value next capability',
        '',
        `Run ID: ${payload.run_id}`,
        `Current health summary: ${quickSummary}`,
        `Failed steps: ${failures}`,
        `Journey map: ${journeyOverview}`,
        `Longevity stable now: ${payload.longevity?.is_stable === true ? 'yes' : 'no'}`,
        `Consecutive healthy runs: ${payload.longevity?.consecutive_healthy || 0}`,
    ].join('\n');

    const response = await chatAssistant({
        route: '/synthetic/persona',
        message: prompt,
        snapshot: {
            source: 'synthetic_persona_loop',
            run_id: payload.run_id,
            failed_steps: payload.failed_steps || [],
            longevity: payload.longevity || {},
        },
    });

    const content = truncateText(response?.message?.content || '', 2000);
    const model = response?.message?.model || null;
    const unusable = !content
        || /No local model is available/i.test(content)
        || /Assistant failed to query model/i.test(content);

    if (!unusable) {
        return {
            ok: true,
            content,
            model,
            generated_by: 'assistant_chat',
        };
    }

    const fallback = [
        'What worked: Core routes respond and pipeline can produce atoms in fallback mode.',
        `What broke: ${failures}.`,
        'What confused me: Why local model capability is unavailable and which actions are degraded.',
        'Highest-value next capability: deterministic guidance + proactive alerting whenever degraded mode is active.',
    ].join('\n');

    return {
        ok: true,
        content: fallback,
        model,
        generated_by: 'heuristic_fallback',
    };
}

async function generateBuilderFeedback(payload = {}) {
    const prompt = [
        'You are the Builder LLM for Genesis. You receive persona feedback from real synthetic usage.',
        'Convert feedback into an implementation brief.',
        'Return JSON only with this exact shape:',
        '{',
        '  "priority": "critical|high|medium|low",',
        '  "stability_assessment": "one sentence",',
        '  "fixes": [{"title":"", "why":"", "verification":""}],',
        '  "capability_growth": [{"title":"", "impact":""}],',
        '  "definition_of_done": ["", ""]',
        '}',
        '',
        `Run ID: ${payload.run_id}`,
        `Persona feedback:\n${truncateText(payload.persona_feedback || '', 1500)}`,
        `Longevity metrics: ${JSON.stringify(payload.longevity || {})}`,
        `Failed steps: ${(payload.failed_steps || []).join(', ') || 'none'}`,
    ].join('\n');

    const response = await chatAssistant({
        route: '/synthetic/builder',
        message: prompt,
        snapshot: {
            source: 'synthetic_builder_loop',
            run_id: payload.run_id,
            longevity: payload.longevity || {},
        },
    });

    const raw = truncateText(response?.message?.content || '', 2800);
    const parsed = extractJsonObject(raw);

    if (parsed) {
        return {
            ok: true,
            data: parsed,
            raw,
            model: response?.message?.model || null,
            generated_by: 'assistant_chat',
        };
    }

    return {
        ok: true,
        data: {
            priority: payload.failed_steps?.length ? 'high' : 'medium',
            stability_assessment: payload.failed_steps?.length
                ? 'Synthetic journey has failures that need immediate remediation.'
                : 'Synthetic journey passes but requires continued hardening until stable targets are met.',
            fixes: [
                {
                    title: 'Harden degraded user paths',
                    why: 'Persona loop reports degraded behavior under missing local model conditions.',
                    verification: 'Synthetic loop remains healthy and user-facing guidance is explicit.',
                },
            ],
            capability_growth: [
                {
                    title: 'Improve in-app explainability',
                    impact: 'Reduces confusion and shortens operator recovery time.',
                },
            ],
            definition_of_done: [
                'No failed synthetic steps across stability streak target',
                'Rolling pass rate exceeds target threshold',
            ],
        },
        raw,
        model: response?.message?.model || null,
        generated_by: 'heuristic_fallback',
    };
}

function buildBuilderMissionPrompt(payload = {}) {
    const fixes = Array.isArray(payload.builder_data?.fixes) ? payload.builder_data.fixes : [];
    const capabilityGrowth = Array.isArray(payload.builder_data?.capability_growth)
        ? payload.builder_data.capability_growth
        : [];
    const doneCriteria = Array.isArray(payload.builder_data?.definition_of_done)
        ? payload.builder_data.definition_of_done
        : [];

    const topFixes = fixes.slice(0, 3).map((item, idx) => `${idx + 1}. ${item.title} | why=${item.why}`).join('\n');
    const topGrowth = capabilityGrowth.slice(0, 2).map((item, idx) => `${idx + 1}. ${item.title} | impact=${item.impact}`).join('\n');
    const done = doneCriteria.slice(0, 3).map((item, idx) => `${idx + 1}. ${item}`).join('\n');

    return [
        `Builder loop from synthetic run ${payload.run_id}.`,
        `Priority: ${payload.builder_data?.priority || 'medium'}.`,
        `Stability assessment: ${payload.builder_data?.stability_assessment || 'n/a'}.`,
        'Top fixes:',
        topFixes || '1. none',
        'Capability growth:',
        topGrowth || '1. none',
        'Definition of done checks:',
        done || '1. none',
        '',
        `Longevity stable: ${payload.longevity?.is_stable === true ? 'yes' : 'no'}.`,
        `Consecutive healthy runs: ${payload.longevity?.consecutive_healthy || 0}.`,
    ].join('\n');
}

async function executeSyntheticJourney(trigger = 'scheduled') {
    if (!state.base_url) {
        return {
            ok: false,
            status: 'degraded',
            summary: 'Synthetic monitor has no base URL configured.',
            failed_steps: ['configuration'],
            steps: [],
            trigger,
            run_id: null,
        };
    }
    if (state.running) {
        return {
            ok: true,
            skipped: true,
            reason: 'synthetic_run_already_in_progress',
        };
    }

    const priorRuns = readRecords(RUNS_FILE);
    const priorLongevity = getLongevityMetrics(priorRuns);
    const priorAtomStability = getAtomStabilityMetrics(priorRuns);

    const runId = crypto.randomUUID();
    state.running = true;
    state.started_at = nowIso();
    state.last_started_at = state.started_at;
    state.last_run_id = runId;
    state.last_status = 'running';
    state.last_error = null;

    const startedAt = Date.now();
    const runContextPayload = JSON.stringify({
        run_id: runId,
        trigger,
        prior_longevity: priorLongevity,
        prior_atom_stability: priorAtomStability,
        started_at: state.started_at,
    });
    const syntheticIntake = recordIntake({
        filename: `synthetic-run-${runId}.json`,
        mimeType: 'application/json',
        sizeBytes: new TextEncoder().encode(runContextPayload).length,
        artifactType: 'DOCUMENT',
        content: runContextPayload,
    });
    const sourceIntakeId = syntheticIntake.id;

    const steps = [];
    let missionRunId = null;
    let annotationId = null;
    let personaFeedback = null;
    let builderFeedback = null;
    let builderMission = null;
    let atomStability = priorAtomStability;
    let stabilizationMission = null;
    let depthQuestions = [];
    let depthQuestionGeneration = null;
    let depthFunctionalityMission = null;
    let autoDepthDecision = null;
    let depthDecisionRequired = false;
    let depthDecisionStatus = 'not_required';

    steps.push(await executeActionStep({
        id: 'health_check',
        title: 'API health',
        intended_outcome: 'Verify the application reports operational health.',
        usage: { method: 'GET', route: '/api/health' },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/health', { timeoutMs: 7000 });
            return {
                ...result,
                ok: result.ok && result.json?.status === 'operational',
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'kiosk_status',
        title: 'Kiosk status',
        intended_outcome: 'Confirm kiosk runtime state is readable by operator tooling.',
        usage: { method: 'GET', route: '/api/kiosk/status' },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/kiosk/status', { timeoutMs: 7000 });
            return {
                ...result,
                ok: result.ok && typeof result.json?.maintenance_mode === 'boolean',
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'stats',
        title: 'Stats endpoint',
        intended_outcome: 'Ensure analytics endpoint returns system totals for visibility.',
        usage: { method: 'GET', route: '/api/stats' },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/stats', { timeoutMs: 7000 });
            return {
                ...result,
                ok: result.ok && typeof result.json?.totalAtoms === 'number',
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'assistant_chat',
        title: 'Assistant chat',
        intended_outcome: 'Verify user can ask the in-app assistant and receive a response payload.',
        usage: {
            method: 'POST',
            route: '/api/assistant/chat',
            payload: {
                route: '/synthetic',
                message: 'Synthetic monitor check: confirm assistant path is responsive.',
            },
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/assistant/chat', {
                method: 'POST',
                timeoutMs: 20_000,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    route: '/synthetic',
                    message: 'Synthetic monitor check: confirm assistant path is responsive.',
                    snapshot: {
                        source: 'synthetic_monitor',
                        run_id: runId,
                    },
                }),
            });
            return {
                ...result,
                ok: result.ok && result.json?.ok === true && Boolean(result.json?.message?.id),
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'annotation_create',
        title: 'Annotation create',
        intended_outcome: 'Confirm user can create direct in-app annotations for feedback.',
        usage: {
            method: 'POST',
            route: '/api/annotations',
            payload: {
                route: '/synthetic',
                annotation_type: 'feedback',
            },
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/annotations', {
                method: 'POST',
                timeoutMs: 12_000,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    route: '/synthetic',
                    annotation_type: 'feedback',
                    message: `Synthetic annotation check (${runId.slice(0, 8)})`,
                    x: 0.25,
                    y: 0.75,
                    created_by: 'synthetic-monitor',
                }),
            });
            annotationId = result.json?.id || null;
            return {
                ...result,
                ok: result.ok && Boolean(annotationId),
                annotation_id: annotationId,
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'mission_run',
        title: 'Mission run',
        intended_outcome: 'Ensure user intent can be executed through the mission orchestration endpoint.',
        usage: {
            method: 'POST',
            route: '/api/mission/run',
            payload: {
                prompt: `Synthetic mission execution check (${runId.slice(0, 8)})`,
                requested_tools: ['filesystem', 'build_test'],
            },
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/mission/run', {
                method: 'POST',
                timeoutMs: 25_000,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt: `Synthetic mission execution check (${runId.slice(0, 8)})`,
                    requested_tools: ['filesystem', 'build_test'],
                    auto_execute: true,
                }),
            });
            missionRunId = result.json?.run_id || null;
            return {
                ...result,
                ok: result.ok && Boolean(missionRunId) && result.json?.status === 'active',
                run_id: missionRunId,
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'mission_fetch',
        title: 'Mission fetch',
        intended_outcome: 'Verify mission results can be retrieved after execution.',
        usage: {
            method: 'GET',
            route: '/api/mission/:run_id',
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            if (!missionRunId) {
                return {
                    ok: false,
                    error: 'mission_run_id_missing',
                };
            }
            const result = await callApi(state.base_url, `/api/mission/${encodeURIComponent(missionRunId)}`, {
                timeoutMs: 12_000,
            });
            return {
                ...result,
                ok: result.ok && result.json?.run_id === missionRunId,
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'atomize_pipeline',
        title: 'Pipeline atomize',
        intended_outcome: 'Confirm user pipeline request generates atoms from provided content.',
        usage: {
            method: 'POST',
            route: '/api/atomize',
            payload: {
                text: `Synthetic pipeline validation run ${runId}`,
            },
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const form = new FormData();
            form.append(
                'text',
                `Synthetic pipeline validation run ${runId}. This text verifies intake, atomization, and atom storage.`,
            );
            const result = await callApi(state.base_url, '/api/atomize', {
                method: 'POST',
                timeoutMs: 30_000,
                body: form,
            });
            return {
                ...result,
                ok: result.ok && result.json?.success === true && Number(result.json?.totalAtoms) >= 1,
                total_atoms: result.json?.totalAtoms || 0,
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'atoms_fetch',
        title: 'Atoms fetch',
        intended_outcome: 'Ensure produced atoms are visible from the knowledge endpoint.',
        usage: {
            method: 'GET',
            route: '/api/atoms?limit=1',
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const result = await callApi(state.base_url, '/api/atoms?limit=1', { timeoutMs: 10_000 });
            return {
                ...result,
                ok: result.ok && Array.isArray(result.json?.atoms),
                atom_count: Array.isArray(result.json?.atoms) ? result.json.atoms.length : 0,
            };
        },
    }));

    if (annotationId) {
        steps.push(await executeActionStep({
            id: 'annotation_resolve',
            title: 'Annotation resolve',
            intended_outcome: 'Validate annotation lifecycle can be completed and resolved.',
            usage: {
                method: 'POST',
                route: '/api/annotations/:id/status',
                annotation_id: annotationId,
            },
            source_intake_id: sourceIntakeId,
            execute: async () => {
                const result = await callApi(state.base_url, `/api/annotations/${encodeURIComponent(annotationId)}/status`, {
                    method: 'POST',
                    timeoutMs: 10_000,
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        status: 'resolved',
                        resolution_note: 'Synthetic monitor lifecycle check complete.',
                    }),
                });
                return {
                    ...result,
                    ok: result.ok && result.json?.status === 'resolved',
                };
            },
        }));
    }

    const baseHealthy = steps.every((step) => step.ok);
    const baseFailedSteps = steps.filter((step) => !step.ok).map((step) => step.id);
    const baseSummary = baseHealthy
        ? 'Synthetic user journey passed.'
        : `Synthetic journey failed: ${steps.map(summarizeResult).filter(Boolean).join(' | ')}`;

    steps.push(await executeActionStep({
        id: 'persona_feedback',
        title: 'Persona feedback loop',
        intended_outcome: 'Capture first-person user-perspective feedback from observed usage.',
        usage: {
            route: '/synthetic/persona',
            failed_steps: baseFailedSteps,
            summary: baseSummary,
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const generated = await generatePersonaFeedback({
                run_id: runId,
                summary: baseSummary,
                failed_steps: baseFailedSteps,
                steps,
                longevity: priorLongevity,
            });
            personaFeedback = generated;
            return {
                ok: generated.ok,
                generated_by: generated.generated_by,
                model: generated.model,
                content: truncateText(generated.content, 800),
            };
        },
    }));

    steps.push(await executeActionStep({
        id: 'builder_feedback',
        title: 'Builder feedback loop',
        intended_outcome: 'Transform persona insight into actionable builder implementation guidance.',
        usage: {
            route: '/synthetic/builder',
            persona_feedback_excerpt: truncateText(personaFeedback?.content || '', 200),
        },
        source_intake_id: sourceIntakeId,
        execute: async () => {
            const generated = await generateBuilderFeedback({
                run_id: runId,
                persona_feedback: personaFeedback?.content || '',
                failed_steps: baseFailedSteps,
                longevity: priorLongevity,
            });
            builderFeedback = generated;
            return {
                ok: generated.ok,
                generated_by: generated.generated_by,
                model: generated.model,
                priority: generated.data?.priority || null,
                stability_assessment: generated.data?.stability_assessment || null,
            };
        },
    }));

    const shouldRunBuilderMission = !priorLongevity.is_stable || baseFailedSteps.length > 0;
    if (shouldRunBuilderMission) {
        steps.push(await executeActionStep({
            id: 'builder_mission',
            title: 'Builder mission handoff',
            intended_outcome: 'Launch builder-side mission to fix issues and grow capability from feedback.',
            usage: {
                mission_type: 'synthetic_builder_handoff',
                tools: ['filesystem', 'build_test', 'runtime_ops'],
            },
            source_intake_id: sourceIntakeId,
            execute: async () => {
                const prompt = buildBuilderMissionPrompt({
                    run_id: runId,
                    builder_data: builderFeedback?.data || {},
                    longevity: priorLongevity,
                });
                builderMission = runMission({
                    prompt,
                    requested_tools: ['filesystem', 'build_test', 'runtime_ops'],
                    auto_execute: true,
                });
                return {
                    ok: builderMission?.status === 'active',
                    mission_run_id: builderMission?.run_id || null,
                    mission_status: builderMission?.status || 'unknown',
                };
            },
        }));
    }

    const preGateKnowledgeAtomCount = steps.reduce(
        (sum, step) => sum + (Number(step.knowledge_atoms_produced?.count) || 0),
        0,
    );
    const preGateAxiomPass = steps.every((step) => (Number(step.knowledge_atoms_produced?.count) || 0) >= 1);
    atomStability = getAtomStabilityMetrics([
        ...priorRuns,
        {
            completed_at: nowIso(),
            step_count: steps.length,
            knowledge_atom_axiom_pass: preGateAxiomPass,
            knowledge_atom_count: preGateKnowledgeAtomCount,
            status: preGateAxiomPass ? 'healthy' : 'degraded',
        },
    ]);

    steps.push(await executeActionStep({
        id: 'atom_stability_gate',
        title: 'Atom stability gate',
        intended_outcome: 'Determine whether loop focus should remain on atom stabilization or unlock depth expansion.',
        usage: {
            phase: 'gate',
            criteria: {
                target_streak: atomStability.target_streak,
                pass_rate_target: atomStability.pass_rate_target,
                min_atoms_per_run: atomStability.min_atoms_per_run,
            },
        },
        source_intake_id: sourceIntakeId,
        execute: async () => ({
            ok: true,
            focus_mode: atomStability.focus_mode,
            atom_stability: atomStability,
        }),
    }));

    if (!atomStability.is_stable) {
        depthDecisionStatus = 'blocked_atom_stabilization';
        steps.push(await executeActionStep({
            id: 'atom_stability_mission',
            title: 'Atom stabilization mission',
            intended_outcome: 'Prioritize reliability work that stabilizes atom production before expanding features.',
            usage: {
                mission_type: 'atom_stabilization',
                tools: ['filesystem', 'build_test', 'runtime_ops'],
            },
            source_intake_id: sourceIntakeId,
            execute: async () => {
                const prompt = buildAtomStabilityMissionPrompt({
                    run_id: runId,
                    atom_stability: atomStability,
                    knowledge_atom_count: preGateKnowledgeAtomCount,
                });
                stabilizationMission = runMission({
                    prompt,
                    requested_tools: ['filesystem', 'build_test', 'runtime_ops'],
                    auto_execute: true,
                });
                return {
                    ok: stabilizationMission?.status === 'active',
                    mission_run_id: stabilizationMission?.run_id || null,
                    mission_status: stabilizationMission?.status || 'unknown',
                };
            },
        }));
    } else {
        depthDecisionStatus = 'eligible_for_depth';
        steps.push(await executeActionStep({
            id: 'atom_depth_questions',
            title: 'Atom depth questions',
            intended_outcome: 'Generate deeper, atom-grounded follow-up questions that can grow product functionality.',
            usage: {
                phase: 'depth_expansion',
                question_limit: MAX_DEPTH_QUESTIONS,
            },
            source_intake_id: sourceIntakeId,
            execute: async () => {
                const atoms = collectRunAtoms(steps, 160);
                depthQuestionGeneration = await generateDepthQuestions({
                    run_id: runId,
                    atoms,
                    longevity: priorLongevity,
                    atom_stability: atomStability,
                });
                depthQuestions = depthQuestionGeneration.questions || [];
                return {
                    ok: depthQuestions.length > 0,
                    generated_by: depthQuestionGeneration.generated_by,
                    model: depthQuestionGeneration.model,
                    question_count: depthQuestions.length,
                    top_question: depthQuestions[0]?.question || null,
                };
            },
        }));

        if (depthQuestions.length > 0) {
            depthDecisionRequired = true;
            if (DEPTH_AUTO_APPROVE) {
                depthDecisionStatus = 'auto_approved';
                steps.push(await executeActionStep({
                    id: 'depth_functionality_mission',
                    title: 'Depth functionality mission',
                    intended_outcome: 'Turn atom-derived questions into concrete functionality growth work.',
                    usage: {
                        mission_type: 'depth_functionality_growth',
                        tools: ['filesystem', 'build_test', 'models'],
                        question_count: depthQuestions.length,
                        decision_mode: 'auto_approved',
                    },
                    source_intake_id: sourceIntakeId,
                    execute: async () => {
                        const prompt = buildDepthFunctionalityPrompt({
                            run_id: runId,
                            questions: depthQuestions,
                        });
                        depthFunctionalityMission = runMission({
                            prompt,
                            requested_tools: ['filesystem', 'build_test', 'models'],
                            auto_execute: true,
                        });
                        return {
                            ok: depthFunctionalityMission?.status === 'active',
                            mission_run_id: depthFunctionalityMission?.run_id || null,
                            mission_status: depthFunctionalityMission?.status || 'unknown',
                        };
                    },
                }));
                autoDepthDecision = {
                    kind: 'synthetic_depth_decision',
                    id: crypto.randomUUID(),
                    run_id: runId,
                    decision: 'approved',
                    question_ids: depthQuestions.map((question) => question.question_id),
                    question_count: depthQuestions.length,
                    note: 'auto-approved by synthetic depth policy',
                    decided_by: 'synthetic-policy',
                    mission_run_id: depthFunctionalityMission?.run_id || null,
                    mission_status: depthFunctionalityMission?.status || null,
                    created_at: nowIso(),
                    auto: true,
                };
                appendRecord(DEPTH_DECISIONS_FILE, autoDepthDecision);
                appendRecord(FEEDBACK_FILE, {
                    kind: 'synthetic_depth_decision',
                    run_id: runId,
                    decision: autoDepthDecision.decision,
                    question_count: autoDepthDecision.question_count,
                    decided_by: autoDepthDecision.decided_by,
                    mission_run_id: autoDepthDecision.mission_run_id,
                    mission_status: autoDepthDecision.mission_status,
                    note: autoDepthDecision.note,
                    auto: true,
                    created_at: nowIso(),
                });
            } else {
                depthDecisionStatus = 'pending';
                steps.push(await executeActionStep({
                    id: 'depth_decision_pending',
                    title: 'Depth decision pending',
                    intended_outcome: 'Pause depth mission execution until operator approves or rejects generated questions.',
                    usage: {
                        decision_required: true,
                        question_count: depthQuestions.length,
                        decision_endpoint: '/api/synthetic/depth/decision',
                    },
                    source_intake_id: sourceIntakeId,
                    execute: async () => ({
                        ok: true,
                        pending: true,
                        question_count: depthQuestions.length,
                    }),
                }));
            }
        } else {
            depthDecisionStatus = 'no_questions';
        }
    }

    const ok = steps.every((step) => step.ok);
    const failedSteps = steps.filter((step) => !step.ok).map((step) => step.id);
    const totalActionKnowledgeAtoms = steps.reduce(
        (sum, step) => sum + (Number(step.knowledge_atoms_produced?.count) || 0),
        0,
    );
    const knowledgeAtomAxiomPass = steps.every((step) => (Number(step.knowledge_atoms_produced?.count) || 0) >= 1);
    const finalAtomStability = getAtomStabilityMetrics([
        ...priorRuns,
        {
            completed_at: nowIso(),
            step_count: steps.length,
            knowledge_atom_axiom_pass: knowledgeAtomAxiomPass,
            knowledge_atom_count: totalActionKnowledgeAtoms,
            status: ok ? 'healthy' : 'degraded',
        },
    ]);

    const runRecord = {
        kind: 'synthetic_user_run',
        run_id: runId,
        trigger,
        started_at: state.started_at,
        completed_at: nowIso(),
        duration_ms: Date.now() - startedAt,
        status: ok ? 'healthy' : 'degraded',
        step_count: steps.length,
        failed_steps: failedSteps,
        source_intake_id: sourceIntakeId,
        knowledge_atom_axiom_pass: knowledgeAtomAxiomPass,
        knowledge_atom_count: totalActionKnowledgeAtoms,
        atom_stability: finalAtomStability,
        loop_focus_mode: finalAtomStability.focus_mode,
        depth_questions: depthQuestions,
        depth_question_count: depthQuestions.length,
        depth_question_source: depthQuestionGeneration?.generated_by || null,
        depth_decision: autoDepthDecision,
        depth_decision_required: depthDecisionRequired,
        depth_decision_status: depthDecisionStatus,
        stabilization_mission_run_id: stabilizationMission?.run_id || null,
        depth_functionality_mission_run_id: depthFunctionalityMission?.run_id || null,
        steps,
        persona_feedback_excerpt: truncateText(personaFeedback?.content || '', 600),
        builder_priority: builderFeedback?.data?.priority || null,
        builder_mission_run_id: builderMission?.run_id || null,
        summary: ok
            ? `Synthetic user journey + persona/builder loop passed. focus=${finalAtomStability.focus_mode}.`
            : `Synthetic loop failed: ${steps.map(summarizeResult).filter(Boolean).join(' | ')}`,
    };

    const longevity = getLongevityMetrics([...priorRuns, runRecord]);
    runRecord.longevity = longevity;

    appendRecord(RUNS_FILE, runRecord);
    appendRecord(FEEDBACK_FILE, {
        kind: 'synthetic_feedback',
        run_id: runId,
        trigger,
        status: runRecord.status,
        source_intake_id: sourceIntakeId,
        knowledge_atom_axiom_pass: knowledgeAtomAxiomPass,
        knowledge_atom_count: totalActionKnowledgeAtoms,
        atom_stability: finalAtomStability,
        loop_focus_mode: finalAtomStability.focus_mode,
        depth_questions: depthQuestions,
        depth_question_count: depthQuestions.length,
        depth_question_source: depthQuestionGeneration?.generated_by || null,
        depth_decision: autoDepthDecision,
        depth_decision_required: depthDecisionRequired,
        depth_decision_status: depthDecisionStatus,
        stabilization_mission_run_id: stabilizationMission?.run_id || null,
        depth_functionality_mission_run_id: depthFunctionalityMission?.run_id || null,
        longevity,
        persona_feedback: truncateText(personaFeedback?.content || '', 2200),
        builder_feedback: builderFeedback?.data || null,
        builder_feedback_raw: truncateText(builderFeedback?.raw || '', 2800),
        builder_mission_run_id: builderMission?.run_id || null,
        created_at: nowIso(),
    });

    state.running = false;
    state.started_at = null;
    state.last_completed_at = runRecord.completed_at;
    state.last_status = runRecord.status;
    state.last_error = ok ? null : runRecord.summary;

    if (!ok) {
        logEvent('error', `[synthetic] ${runRecord.summary}`);
    } else if (longevity.is_stable) {
        logEvent('info', `[synthetic] ${runRecord.summary} Stability targets achieved.`);
    } else {
        logEvent('warn', `[synthetic] ${runRecord.summary} Stability loop still converging.`);
    }

    return {
        ok,
        ...runRecord,
    };
}

function clearTimer() {
    if (state.timer) {
        clearTimeout(state.timer);
        state.timer = null;
    }
}

function scheduleNextRun(delayMs = state.interval_ms) {
    if (!state.enabled) return;
    clearTimer();
    const delay = Math.max(5_000, Number(delayMs) || state.interval_ms);
    state.next_run_at = new Date(Date.now() + delay).toISOString();
    state.timer = setTimeout(async () => {
        await executeSyntheticJourney('scheduled');
        scheduleNextRun(state.interval_ms);
    }, delay);
}

export function configureSyntheticMonitor(payload = {}) {
    if (payload.enabled === true || payload.enabled === false) {
        state.enabled = payload.enabled;
    }
    if (payload.interval_ms) {
        state.interval_ms = Math.max(MIN_INTERVAL_MS, Number(payload.interval_ms) || state.interval_ms);
    }

    if (!state.enabled) {
        clearTimer();
        state.next_run_at = null;
        logEvent('warn', '[synthetic] monitor disabled by configuration');
        return getSyntheticStatus();
    }

    scheduleNextRun(5_000);
    logEvent('info', `[synthetic] monitor configured (interval=${state.interval_ms}ms)`);
    return getSyntheticStatus();
}

export function startSyntheticMonitor(payload = {}) {
    const port = payload.port || process.env.PORT || '3141';
    state.base_url = payload.base_url || `http://127.0.0.1:${port}`;
    if (payload.interval_ms) {
        state.interval_ms = Math.max(MIN_INTERVAL_MS, Number(payload.interval_ms) || state.interval_ms);
    }
    if (payload.enabled === false) {
        state.enabled = false;
    }

    if (!state.enabled) {
        clearTimer();
        state.next_run_at = null;
        logEvent('warn', '[synthetic] monitor disabled by configuration');
        return getSyntheticStatus();
    }

    scheduleNextRun(5_000);
    logEvent('info', `[synthetic] monitor started (interval=${state.interval_ms}ms)`);
    return getSyntheticStatus();
}

export async function triggerSyntheticRun(reason = 'manual') {
    return await executeSyntheticJourney(reason || 'manual');
}

export function getSyntheticStatus() {
    const runs = readRecords(RUNS_FILE);
    const latest = runs.length ? runs[runs.length - 1] : null;
    return {
        enabled: state.enabled,
        interval_ms: state.interval_ms,
        base_url: state.base_url,
        running: state.running,
        started_at: state.started_at,
        last_started_at: state.last_started_at,
        last_completed_at: state.last_completed_at,
        last_status: state.last_status,
        last_run_id: state.last_run_id,
        next_run_at: state.next_run_at,
        last_error: state.last_error,
        longevity: getLongevityMetrics(runs),
        atom_stability: getAtomStabilityMetrics(runs),
        latest_run: latest,
    };
}

export function getSyntheticRuns(limit = 20) {
    const value = Number.isFinite(Number(limit)) ? Math.max(1, Math.min(200, Number(limit))) : 20;
    const runs = readRecords(RUNS_FILE);
    return {
        runs: runs.slice(-value).reverse(),
        total: runs.length,
        generated_at: nowIso(),
    };
}

export function getSyntheticFeedback(limit = 20) {
    const value = Number.isFinite(Number(limit)) ? Math.max(1, Math.min(200, Number(limit))) : 20;
    const feedback = readRecords(FEEDBACK_FILE);
    return {
        feedback: feedback.slice(-value).reverse(),
        total: feedback.length,
        generated_at: nowIso(),
    };
}
