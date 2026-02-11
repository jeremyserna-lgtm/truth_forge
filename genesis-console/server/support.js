// Genesis Console — Support & Governance Engine
// TRIAD: META (governing logic) | FEDERATION: CREDENTIAL ATLAS | RECURSION: MANAGER
// "I verify existence." Sentinel governance, recursive synthesis,
// mission orchestration, and behavioral constraint enforcement.
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DATA_DIR = path.join(__dirname, '..', 'data');

if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
}

const FILES = {
    planning: path.join(DATA_DIR, 'planning.jsonl'),
    todos: path.join(DATA_DIR, 'todos.jsonl'),
    toolOrchestration: path.join(DATA_DIR, 'tool_orchestration.jsonl'),
    handover: path.join(DATA_DIR, 'handover.jsonl'),
    sentinel: path.join(DATA_DIR, 'sentinel.jsonl'),
    recursive: path.join(DATA_DIR, 'recursive_synthesis.jsonl'),
    mission: path.join(DATA_DIR, 'mission_runs.jsonl'),
    kiosk: path.join(DATA_DIR, 'kiosk_ops.jsonl'),
    annotations: path.join(DATA_DIR, 'annotations.jsonl'),
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

function riskScore(level) {
    const map = { low: 1, medium: 2, high: 3, critical: 4 };
    return map[level] || 1;
}

function clamp01(value) {
    if (!Number.isFinite(value)) return 0.5;
    if (value < 0) return 0;
    if (value > 1) return 1;
    return value;
}

function latestBy(records, predicate) {
    for (let i = records.length - 1; i >= 0; i -= 1) {
        if (predicate(records[i])) return records[i];
    }
    return null;
}

function parseIntentToNodes(intent) {
    const text = (intent || '').trim();
    if (!text) {
        return [
            {
                node_id: crypto.randomUUID(),
                title: 'Define execution intent',
                status: 'pending',
                depends_on: [],
                acceptance_criteria: ['Intent is explicit and testable'],
            },
        ];
    }

    const segments = text
        .split(/[\n.!?]+/)
        .map((part) => part.trim())
        .filter(Boolean)
        .slice(0, 12);

    return segments.map((segment, idx) => ({
        node_id: crypto.randomUUID(),
        title: segment,
        status: 'pending',
        depends_on: idx === 0 ? [] : [idx - 1],
        acceptance_criteria: [`Completed: ${segment}`],
    }));
}

export function createOrRefreshIntentPlan(payload = {}) {
    const runId = payload.run_id || crypto.randomUUID();
    const plan = {
        id: crypto.randomUUID(),
        run_id: runId,
        intent: payload.intent || '',
        current_state: payload.current_state || {},
        nodes: parseIntentToNodes(payload.intent || ''),
        acceptance_criteria: payload.acceptance_criteria || [],
        revenue_links: payload.revenue_links || [],
        created_at: nowIso(),
        updated_at: nowIso(),
    };

    appendRecord(FILES.planning, plan);
    return plan;
}

function getLatestPlanByRunId(runId) {
    const plans = readRecords(FILES.planning);
    return latestBy(plans, (plan) => plan.run_id === runId);
}

function getLatestPlanById(planId) {
    const plans = readRecords(FILES.planning);
    return latestBy(plans, (plan) => plan.id === planId);
}

function buildTodosFromPlan(plan) {
    return (plan.nodes || []).map((node, idx) => ({
        todo_id: crypto.randomUUID(),
        node_id: node.node_id,
        title: node.title,
        status: idx === 0 ? 'in_progress' : 'pending',
        notes: '',
        updated_at: nowIso(),
    }));
}

function getLatestTodoSnapshot(planId) {
    const snapshots = readRecords(FILES.todos);
    return latestBy(snapshots, (snapshot) => snapshot.plan_id === planId);
}

export function syncPlanTodos(payload = {}) {
    const plan = payload.plan_id
        ? getLatestPlanById(payload.plan_id)
        : getLatestPlanByRunId(payload.run_id || '');

    if (!plan) {
        return {
            ok: false,
            error: 'plan_not_found',
        };
    }

    const latestSnapshot = getLatestTodoSnapshot(plan.id);
    const todos = latestSnapshot ? structuredClone(latestSnapshot.todos) : buildTodosFromPlan(plan);

    const outcomes = Array.isArray(payload.outcomes) ? payload.outcomes : [];
    const byTodo = new Map(todos.map((todo) => [todo.todo_id, todo]));

    outcomes.forEach((outcome) => {
        const todo = byTodo.get(outcome.todo_id);
        if (!todo) return;
        todo.status = outcome.status || todo.status;
        todo.notes = outcome.note || todo.notes;
        todo.updated_at = nowIso();
    });

    const snapshot = {
        id: crypto.randomUUID(),
        plan_id: plan.id,
        run_id: plan.run_id,
        todos,
        outcomes,
        created_at: nowIso(),
    };

    appendRecord(FILES.todos, snapshot);
    return {
        ok: true,
        snapshot,
    };
}

export function getPlanningState(runId) {
    const plan = getLatestPlanByRunId(runId);
    if (!plan) {
        return {
            run_id: runId,
            status: 'no_plan',
            blockers: [],
            next_actions: [],
            confidence: 0,
        };
    }

    const todoSnapshot = getLatestTodoSnapshot(plan.id);
    const todos = todoSnapshot?.todos || [];
    const blockers = todos.filter((todo) => todo.status === 'blocked');
    const nextActions = todos
        .filter((todo) => todo.status === 'pending' || todo.status === 'in_progress')
        .slice(0, 5)
        .map((todo) => todo.title);

    const completedCount = todos.filter((todo) => todo.status === 'completed').length;
    const confidence = todos.length === 0 ? 0.5 : Math.max(0.1, completedCount / todos.length);

    return {
        run_id: runId,
        plan,
        todos,
        blockers,
        next_actions: nextActions,
        confidence,
        status: blockers.length > 0 ? 'blocked' : 'active',
        updated_at: nowIso(),
    };
}

const TOOL_CATALOG = [
    {
        tool_id: 'filesystem',
        scope: 'Local file read/write and project manipulation',
        risk_level: 'high',
        requires_verification: true,
        rollback_procedure: 'Restore from git history or backup snapshot',
    },
    {
        tool_id: 'models',
        scope: 'Local/cloud model invocation and inference routing',
        risk_level: 'medium',
        requires_verification: true,
        rollback_procedure: 'Route back to known-good model profile',
    },
    {
        tool_id: 'network',
        scope: 'External HTTP calls and API integrations',
        risk_level: 'high',
        requires_verification: true,
        rollback_procedure: 'Disable outbound integration policy and retry local path',
    },
    {
        tool_id: 'build_test',
        scope: 'Build, lint, and automated test execution',
        risk_level: 'medium',
        requires_verification: false,
        rollback_procedure: 'Revert failing change-set and rerun baseline test suite',
    },
    {
        tool_id: 'runtime_ops',
        scope: 'Service lifecycle operations and runtime maintenance',
        risk_level: 'critical',
        requires_verification: true,
        rollback_procedure: 'Failover to safe mode and restart supervised services',
    },
];

export function getToolCatalog() {
    return TOOL_CATALOG;
}

export function orchestrateToolUsage(payload = {}) {
    const requestedTools = Array.isArray(payload.requested_tools) ? payload.requested_tools : [];

    const toolEntries = requestedTools.map((toolId) => {
        const found = TOOL_CATALOG.find((tool) => tool.tool_id === toolId);
        if (!found) {
            return {
                tool_id: toolId,
                resolved: false,
                risk_level: 'critical',
                preflight_ok: false,
                reason: 'tool_not_in_catalog',
            };
        }

        return {
            ...found,
            resolved: true,
            preflight_ok: true,
            reason: 'ok',
        };
    });

    const unresolved = toolEntries.filter((entry) => !entry.resolved);
    const highestRisk = toolEntries.reduce((max, entry) => {
        return riskScore(entry.risk_level) > riskScore(max) ? entry.risk_level : max;
    }, 'low');

    const orchestration = {
        id: crypto.randomUUID(),
        plan_id: payload.plan_id || null,
        todo_id: payload.todo_id || null,
        objective: payload.objective || 'structured_tool_execution',
        fallback_path: payload.fallback_path || 'safe_mode_escalation',
        requested_tools: requestedTools,
        tool_entries: toolEntries,
        unresolved_tools: unresolved.map((entry) => entry.tool_id),
        highest_risk_level: highestRisk,
        policy_checked: true,
        created_at: nowIso(),
    };

    appendRecord(FILES.toolOrchestration, orchestration);
    return orchestration;
}

function getLatestOrchestration() {
    const traces = readRecords(FILES.toolOrchestration);
    return traces.length ? traces[traces.length - 1] : null;
}

export function getHandoverReadiness() {
    const plans = readRecords(FILES.planning);
    const latestPlan = plans.length ? plans[plans.length - 1] : null;
    const latestTodo = latestPlan ? getLatestTodoSnapshot(latestPlan.id) : null;
    const latestOrchestration = getLatestOrchestration();

    const criticalGaps = [];
    if (!latestPlan) criticalGaps.push('plan_graph_missing');
    if (!latestTodo) criticalGaps.push('todo_graph_missing');
    if (!latestOrchestration) criticalGaps.push('tool_orchestration_trace_missing');

    const nonCriticalGaps = [];
    if (TOOL_CATALOG.length === 0) nonCriticalGaps.push('tool_catalog_empty');

    const report = {
        id: crypto.randomUUID(),
        takeover_ready: criticalGaps.length === 0,
        critical_gaps: criticalGaps,
        non_critical_gaps: nonCriticalGaps,
        evidence: {
            latest_plan_id: latestPlan?.id || null,
            latest_todo_snapshot_id: latestTodo?.id || null,
            latest_tool_trace_id: latestOrchestration?.id || null,
        },
        created_at: nowIso(),
    };

    appendRecord(FILES.handover, { kind: 'readiness', ...report });
    return report;
}

function getLatestRehearsal() {
    const records = readRecords(FILES.handover);
    return latestBy(records, (record) => record.kind === 'rehearsal');
}

export function rehearseHandover(payload = {}) {
    const prior = getLatestRehearsal();
    const plan = createOrRefreshIntentPlan({
        run_id: payload.run_id,
        intent:
            payload.intent ||
            'Maintain plan lifecycle, sync todos, and execute governed tool usage during handover',
        current_state: payload.current_state || {},
        acceptance_criteria: payload.acceptance_criteria || [],
        revenue_links: payload.revenue_links || [],
    });

    const initialSync = syncPlanTodos({ plan_id: plan.id, outcomes: [] });
    const firstTodo = initialSync.snapshot?.todos?.[0];
    const completedSync = syncPlanTodos({
        plan_id: plan.id,
        outcomes: firstTodo
            ? [
                {
                    todo_id: firstTodo.todo_id,
                    status: 'completed',
                    note: 'handover rehearsal completed first actionable step',
                },
            ]
            : [],
    });

    const toolTrace = orchestrateToolUsage({
        plan_id: plan.id,
        todo_id: firstTodo?.todo_id || null,
        requested_tools: payload.requested_tools || ['filesystem', 'build_test'],
        objective: 'handover_rehearsal',
        fallback_path: 'escalate_to_owner',
    });

    const readiness = getHandoverReadiness();
    const pass = readiness.takeover_ready && toolTrace.unresolved_tools.length === 0;

    const rehearsal = {
        kind: 'rehearsal',
        id: crypto.randomUUID(),
        pass,
        regression_diff: {
            previous_pass: prior ? Boolean(prior.pass) : null,
            changed: prior ? Boolean(prior.pass) !== pass : false,
        },
        evidence: {
            plan_id: plan.id,
            todo_snapshot_id: completedSync.snapshot?.id || null,
            tool_trace_id: toolTrace.id,
            readiness_report_id: readiness.id,
        },
        created_at: nowIso(),
    };

    appendRecord(FILES.handover, rehearsal);
    return rehearsal;
}

export function recordSentinelHeartbeat(payload = {}) {
    const record = {
        event_type: 'heartbeat',
        id: crypto.randomUUID(),
        unit_id: payload.unit_id || 'unknown-unit',
        capability_vector: payload.capability_vector || {},
        health_state: payload.health_state || 'online',
        timestamp: nowIso(),
    };
    appendRecord(FILES.sentinel, record);
    return record;
}

export function registerSentinelAnomaly(payload = {}) {
    const incident = {
        event_type: 'incident_opened',
        id: crypto.randomUUID(),
        incident_id: payload.incident_id || crypto.randomUUID(),
        unit_id: payload.unit_id || 'unknown-unit',
        severity: payload.severity || 'high',
        blast_radius: payload.blast_radius || 'unknown',
        details: payload.details || '',
        state: 'open',
        created_at: nowIso(),
    };
    appendRecord(FILES.sentinel, incident);
    return incident;
}

export function escalateSentinelIncident(payload = {}) {
    const escalation = {
        event_type: 'incident_escalation',
        id: crypto.randomUUID(),
        incident_id: payload.incident_id,
        stage: payload.stage || 'self_heal',
        note: payload.note || '',
        created_at: nowIso(),
    };
    appendRecord(FILES.sentinel, escalation);
    return escalation;
}

export function runOperatorCheck(payload = {}) {
    const check = {
        event_type: 'operator_check',
        id: crypto.randomUUID(),
        incident_id: payload.incident_id || null,
        channel: payload.channel || 'primary',
        consent_policy: payload.consent_policy || 'anomaly_only',
        note: payload.note || '',
        created_at: nowIso(),
    };
    appendRecord(FILES.sentinel, check);
    return check;
}

export function getSentinelIncident(incidentId) {
    const records = readRecords(FILES.sentinel).filter(
        (record) => record.incident_id === incidentId,
    );

    if (!records.length) return null;

    const opened = records.find((record) => record.event_type === 'incident_opened') || null;
    const escalations = records.filter((record) => record.event_type === 'incident_escalation');
    const operatorChecks = records.filter((record) => record.event_type === 'operator_check');

    return {
        incident_id: incidentId,
        opened,
        escalations,
        operator_checks: operatorChecks,
        timeline: records,
    };
}

export function getSentinelStatus(payload = {}) {
    const thresholdSeconds = Number(payload.threshold_seconds) || 120;
    const nowMs = Date.now();

    const records = readRecords(FILES.sentinel);
    const heartbeats = records.filter((record) => record.event_type === 'heartbeat');
    const incidents = records.filter((record) => record.event_type === 'incident_opened');

    const latestByUnit = new Map();
    heartbeats.forEach((heartbeat) => {
        latestByUnit.set(heartbeat.unit_id, heartbeat);
    });

    const units = Array.from(latestByUnit.values()).map((heartbeat) => {
        const ageMs = nowMs - Date.parse(heartbeat.timestamp || heartbeat._ts || nowIso());
        const stale = ageMs > thresholdSeconds * 1000;
        return {
            unit_id: heartbeat.unit_id,
            last_heartbeat: heartbeat.timestamp || heartbeat._ts,
            stale,
            capability_vector: heartbeat.capability_vector || {},
            health_state: stale ? 'degraded' : heartbeat.health_state,
        };
    });

    return {
        threshold_seconds: thresholdSeconds,
        units,
        open_incidents: incidents.length,
        escalation_required: units.some((unit) => unit.stale),
        generated_at: nowIso(),
    };
}

function getLatestRecursiveCycle(cycleId) {
    const records = readRecords(FILES.recursive);
    return latestBy(records, (record) => record.cycle_id === cycleId);
}

export function startRecursiveCycle(payload = {}) {
    const cycle = {
        cycle_id: payload.cycle_id || crypto.randomUUID(),
        status: 'started',
        inputs: {
            conversation: payload.conversation || '',
            plan_deltas: payload.plan_deltas || [],
            code_diffs: payload.code_diffs || [],
            incidents: payload.incidents || [],
        },
        atoms: [],
        learning_candidates: [],
        governance: {
            cost_ok: null,
            risk_ok: null,
            peer_review_ok: null,
        },
        decision: null,
        decision_rationale: null,
        product_effects: payload.product_effects || [],
        mind_change_record: payload.mind_change_record || null,
        promoted_item: null,
        created_at: nowIso(),
        updated_at: nowIso(),
    };

    appendRecord(FILES.recursive, cycle);
    return cycle;
}

export function ingestRecursiveCycle(payload = {}) {
    const current = getLatestRecursiveCycle(payload.cycle_id || '');
    if (!current) {
        return { ok: false, error: 'cycle_not_found' };
    }

    const outputs = Array.isArray(payload.outputs) ? payload.outputs : [];
    const atoms = outputs.map((output) => ({
        atom_id: crypto.randomUUID(),
        type: output.type || 'synthesis',
        content: output.content || '',
        source: output.source || 'recursive_cycle',
        created_at: nowIso(),
    }));

    const next = {
        ...current,
        status: 'ingested',
        atoms: [...(current.atoms || []), ...atoms],
        learning_candidates: [
            ...(current.learning_candidates || []),
            ...(payload.learning_candidates || []),
        ],
        updated_at: nowIso(),
    };

    appendRecord(FILES.recursive, next);
    return { ok: true, cycle: next };
}

export function evaluateRecursiveCycle(payload = {}) {
    const current = getLatestRecursiveCycle(payload.cycle_id || '');
    if (!current) {
        return { ok: false, error: 'cycle_not_found' };
    }

    const governance = {
        cost_ok: payload.cost_ok ?? true,
        risk_ok: payload.risk_ok ?? true,
        peer_review_ok: payload.peer_review_ok ?? true,
    };

    const productEffects = payload.product_effects || current.product_effects || [];

    let decision = payload.decision || null;
    if (!decision) {
        if (governance.cost_ok && governance.risk_ok && governance.peer_review_ok && productEffects.length > 0) {
            decision = 'promote';
        } else if (productEffects.length === 0) {
            decision = 'defer_research';
        } else {
            decision = 'reject';
        }
    }

    const next = {
        ...current,
        status: 'evaluated',
        governance,
        decision,
        decision_rationale:
            payload.decision_rationale ||
            (decision === 'promote'
                ? 'governance_passed_and_product_effect_mapped'
                : 'insufficient_governed_product_effect'),
        product_effects: productEffects,
        mind_change_record: payload.mind_change_record || current.mind_change_record || null,
        updated_at: nowIso(),
    };

    appendRecord(FILES.recursive, next);
    return { ok: true, cycle: next };
}

export function promoteRecursiveCycle(payload = {}) {
    const current = getLatestRecursiveCycle(payload.cycle_id || '');
    if (!current) {
        return { ok: false, error: 'cycle_not_found' };
    }

    if (current.decision !== 'promote' && !payload.force) {
        return { ok: false, error: 'cycle_not_promotable' };
    }

    const promotedItem = {
        backlog_item_id: crypto.randomUUID(),
        title: payload.title || 'Recursive synthesis promoted backlog item',
        product_effects: current.product_effects || [],
        created_at: nowIso(),
    };

    const next = {
        ...current,
        status: 'promoted',
        promoted_item: promotedItem,
        updated_at: nowIso(),
    };

    appendRecord(FILES.recursive, next);
    return { ok: true, cycle: next };
}

export function getRecursiveSynthesisHealth() {
    const records = readRecords(FILES.recursive);
    const cycleIds = [...new Set(records.map((record) => record.cycle_id).filter(Boolean))];
    return {
        available: true,
        cycle_count: cycleIds.length,
        event_count: records.length,
        last_cycle_id: cycleIds.length ? cycleIds[cycleIds.length - 1] : null,
        checked_at: nowIso(),
    };
}

export function getRecursiveCycle(cycleId) {
    return getLatestRecursiveCycle(cycleId);
}

function getLatestAnnotationsMap() {
    const records = readRecords(FILES.annotations).filter((record) => record.kind === 'annotation');
    const byId = new Map();
    records.forEach((record) => {
        byId.set(record.id, record);
    });
    return byId;
}

export function createAnnotation(payload = {}) {
    const message = String(payload.message || '').trim();
    if (!message) return { ok: false, error: 'message_required' };

    const annotationType = String(payload.annotation_type || 'feedback');
    const allowedTypes = new Set(['feedback', 'question', 'issue']);
    const type = allowedTypes.has(annotationType) ? annotationType : 'feedback';

    const annotation = {
        kind: 'annotation',
        id: crypto.randomUUID(),
        route: payload.route || '/',
        x: clamp01(Number(payload.x)),
        y: clamp01(Number(payload.y)),
        annotation_type: type,
        message,
        anchor_text: payload.anchor_text || null,
        context: payload.context || {},
        status: 'open',
        resolution_note: null,
        created_by: payload.created_by || 'operator',
        created_at: nowIso(),
        updated_at: nowIso(),
    };

    appendRecord(FILES.annotations, annotation);
    return { ok: true, annotation };
}

export function getAnnotations(payload = {}) {
    const limitRaw = Number(payload.limit);
    const limit = Number.isFinite(limitRaw) && limitRaw > 0 ? Math.min(500, Math.floor(limitRaw)) : 200;

    let annotations = Array.from(getLatestAnnotationsMap().values());

    if (payload.route) {
        annotations = annotations.filter((annotation) => annotation.route === payload.route);
    }
    if (payload.status && payload.status !== 'all') {
        annotations = annotations.filter((annotation) => annotation.status === payload.status);
    }

    annotations.sort((a, b) => Date.parse(b.updated_at || b._ts || '') - Date.parse(a.updated_at || a._ts || ''));
    return {
        annotations: annotations.slice(0, limit),
        total: annotations.length,
        generated_at: nowIso(),
    };
}

export function getAnnotation(annotationId) {
    return getLatestAnnotationsMap().get(annotationId) || null;
}

export function updateAnnotationStatus(annotationId, payload = {}) {
    const current = getAnnotation(annotationId);
    if (!current) return { ok: false, error: 'annotation_not_found' };

    const nextStatus = payload.status || 'open';
    const allowed = new Set(['open', 'resolved', 'archived']);
    if (!allowed.has(nextStatus)) {
        return { ok: false, error: 'invalid_status' };
    }

    const updated = {
        ...current,
        status: nextStatus,
        resolution_note: payload.resolution_note || current.resolution_note || null,
        updated_at: nowIso(),
    };

    appendRecord(FILES.annotations, updated);
    return { ok: true, annotation: updated };
}

function inferToolsFromPrompt(prompt = '') {
    const text = String(prompt || '').toLowerCase();
    const tools = new Set(['filesystem']);

    if (/(build|lint|test|coverage|ownership gate)/.test(text)) tools.add('build_test');
    if (/(service|runtime|restart|kiosk|maintenance|deploy|watchdog)/.test(text)) tools.add('runtime_ops');
    if (/(model|mlx|exo|scout|maverick|r1|deepseek|lora|fine[\s-]?tune)/.test(text)) tools.add('models');
    if (/(api|http|remote|cloud|download|fetch)/.test(text)) tools.add('network');

    return Array.from(tools);
}

function buildMissionSummary({
    status,
    readiness,
    planningState,
    toolTrace,
    cycleDecision,
}) {
    const unresolved = toolTrace?.unresolved_tools?.length || 0;
    const blockers = planningState?.blockers?.length || 0;
    const readinessText = readiness?.takeover_ready ? 'handover ready' : 'handover has critical gaps';
    const decisionText = cycleDecision ? `recursive decision=${cycleDecision}` : 'recursive decision unavailable';

    return `${status}: ${readinessText}; unresolved_tools=${unresolved}; blockers=${blockers}; ${decisionText}`;
}

function getLatestMissionRun(runId) {
    const records = readRecords(FILES.mission);
    return latestBy(records, (record) => record.kind === 'mission_run' && record.run_id === runId);
}

export function getMissionRun(runId) {
    const current = getLatestMissionRun(runId);
    if (!current) return null;

    const timeline = readRecords(FILES.mission)
        .filter((record) => record.kind === 'mission_run' && record.run_id === runId)
        .slice(-25);

    return {
        ...current,
        timeline,
    };
}

export function getMissionHistory(payload = {}) {
    const limitRaw = Number(payload.limit);
    const limit = Number.isFinite(limitRaw) && limitRaw > 0 ? Math.min(100, Math.floor(limitRaw)) : 20;
    const records = readRecords(FILES.mission).filter((record) => record.kind === 'mission_run');

    const latestRuns = [];
    const seenRunIds = new Set();
    for (let i = records.length - 1; i >= 0; i -= 1) {
        const record = records[i];
        if (!record.run_id || seenRunIds.has(record.run_id)) continue;
        latestRuns.push(record);
        seenRunIds.add(record.run_id);
        if (latestRuns.length >= limit) break;
    }

    return {
        runs: latestRuns,
        total_events: records.length,
        generated_at: nowIso(),
    };
}

export function runMission(payload = {}) {
    const prompt = (payload.prompt || payload.intent || '').trim();
    const runId = payload.run_id || crypto.randomUUID();
    const autoExecute = payload.auto_execute !== false;
    const requestedTools = Array.isArray(payload.requested_tools) && payload.requested_tools.length > 0
        ? payload.requested_tools
        : inferToolsFromPrompt(prompt);
    const steps = [];
    const startedAt = nowIso();
    const missionId = crypto.randomUUID();

    try {
        const plan = createOrRefreshIntentPlan({
            run_id: runId,
            intent: prompt || 'Autonomous mission run with governed planning and execution.',
            current_state: payload.current_state || {},
            acceptance_criteria: payload.acceptance_criteria || [],
            revenue_links: payload.revenue_links || [],
        });
        steps.push({ step: 'plan_refreshed', ok: true, plan_id: plan.id });

        const synced = syncPlanTodos({ plan_id: plan.id, outcomes: [] });
        steps.push({ step: 'todo_synced', ok: Boolean(synced.ok), snapshot_id: synced.snapshot?.id || null });

        const activeTodo = synced.snapshot?.todos?.find(
            (todo) => todo.status === 'in_progress' || todo.status === 'pending',
        ) || null;
        let executionSync = null;
        if (autoExecute && activeTodo) {
            executionSync = syncPlanTodos({
                plan_id: plan.id,
                outcomes: [
                    {
                        todo_id: activeTodo.todo_id,
                        status: 'completed',
                        note: 'auto-progressed by mission run',
                    },
                ],
            });
            steps.push({
                step: 'todo_advanced',
                ok: Boolean(executionSync.ok),
                todo_id: activeTodo.todo_id,
            });
        }

        const toolTrace = orchestrateToolUsage({
            run_id: runId,
            plan_id: plan.id,
            todo_id: activeTodo?.todo_id || null,
            objective: payload.objective || 'mission_autonomous_execution',
            requested_tools: requestedTools,
            fallback_path: payload.fallback_path || 'owner_escalation',
        });
        steps.push({
            step: 'tool_orchestration',
            ok: toolTrace.unresolved_tools.length === 0,
            trace_id: toolTrace.id,
            unresolved_tools: toolTrace.unresolved_tools,
        });

        const rehearsal = rehearseHandover({
            run_id: runId,
            intent: prompt,
            requested_tools: requestedTools,
        });
        steps.push({ step: 'handover_rehearsal', ok: rehearsal.pass, rehearsal_id: rehearsal.id });

        const heartbeat = recordSentinelHeartbeat({
            unit_id: payload.unit_id || 'mission-operator',
            health_state: 'online',
            capability_vector: {
                planning: true,
                orchestration: true,
                synthesis: true,
                kiosk_ops: true,
            },
        });
        steps.push({ step: 'sentinel_heartbeat', ok: true, heartbeat_id: heartbeat.id });

        const cycle = startRecursiveCycle({
            conversation: prompt,
            plan_deltas: [plan.id],
            product_effects: payload.product_effects || ['operator_velocity'],
            mind_change_record: payload.mind_change_record || 'mission run auto-synthesis',
        });
        steps.push({ step: 'recursive_start', ok: true, cycle_id: cycle.cycle_id });

        const ingested = ingestRecursiveCycle({
            cycle_id: cycle.cycle_id,
            outputs: [
                {
                    type: 'mission',
                    source: 'mission_api',
                    content: prompt || 'no-prompt mission request',
                },
            ],
            learning_candidates: [
                {
                    kind: 'mission',
                    note: 'operator interaction translated into governed run',
                },
            ],
        });
        steps.push({ step: 'recursive_ingest', ok: Boolean(ingested.ok) });

        const evaluated = evaluateRecursiveCycle({
            cycle_id: cycle.cycle_id,
            cost_ok: true,
            risk_ok: toolTrace.unresolved_tools.length === 0,
            peer_review_ok: rehearsal.pass,
            product_effects: payload.product_effects || ['operator_velocity'],
        });
        steps.push({
            step: 'recursive_evaluate',
            ok: Boolean(evaluated.ok),
            decision: evaluated.cycle?.decision || null,
        });

        let promoted = null;
        if (evaluated.ok && evaluated.cycle?.decision === 'promote') {
            promoted = promoteRecursiveCycle({
                cycle_id: cycle.cycle_id,
                title: payload.backlog_title || `Mission backlog: ${prompt || runId}`,
            });
            steps.push({ step: 'recursive_promote', ok: Boolean(promoted.ok) });
        }

        const planningState = getPlanningState(runId);
        const readiness = getHandoverReadiness();
        const sentinel = getSentinelStatus({ threshold_seconds: 120 });
        const status = readiness.takeover_ready && toolTrace.unresolved_tools.length === 0 ? 'active' : 'needs_attention';

        const mission = {
            kind: 'mission_run',
            id: missionId,
            run_id: runId,
            prompt,
            auto_execute: autoExecute,
            requested_tools: requestedTools,
            status,
            summary: buildMissionSummary({
                status,
                readiness,
                planningState,
                toolTrace,
                cycleDecision: evaluated.cycle?.decision || null,
            }),
            artifacts: {
                plan_id: plan.id,
                todo_snapshot_id: (executionSync?.snapshot || synced.snapshot)?.id || null,
                tool_trace_id: toolTrace.id,
                rehearsal_id: rehearsal.id,
                cycle_id: cycle.cycle_id,
                promoted_backlog_item_id: promoted?.cycle?.promoted_item?.backlog_item_id || null,
            },
            readiness,
            sentinel,
            planning_state: planningState,
            steps,
            created_at: startedAt,
            updated_at: nowIso(),
        };

        appendRecord(FILES.mission, mission);
        return mission;
    } catch (error) {
        const failed = {
            kind: 'mission_run',
            id: missionId,
            run_id: runId,
            prompt,
            auto_execute: autoExecute,
            requested_tools: requestedTools,
            status: 'failed',
            summary: `failed: ${error.message}`,
            error: error.message,
            steps,
            created_at: startedAt,
            updated_at: nowIso(),
        };
        appendRecord(FILES.mission, failed);
        return failed;
    }
}

function getLatestKioskPolicy() {
    const records = readRecords(FILES.kiosk);
    return latestBy(records, (record) => record.kind === 'policy');
}

export function getKioskStatus() {
    const records = readRecords(FILES.kiosk);
    const policy = getLatestKioskPolicy();
    const interventions = records
        .filter((record) => record.kind === 'intervention')
        .slice(-20)
        .reverse();

    const nowMs = Date.now();
    const expiresAtMs = policy?.expires_at ? Date.parse(policy.expires_at) : null;
    const maintenanceActive = Boolean(
        policy?.maintenance_mode && (expiresAtMs === null || Number.isNaN(expiresAtMs) || expiresAtMs > nowMs),
    );

    return {
        available: true,
        maintenance_mode: maintenanceActive,
        maintenance_reason: maintenanceActive ? policy?.reason || null : null,
        maintenance_until: maintenanceActive ? policy?.expires_at || null : null,
        maintenance_requested_by: maintenanceActive ? policy?.requested_by || null : null,
        policy_id: policy?.id || null,
        intervention_count: interventions.length,
        recent_interventions: interventions.slice(0, 5),
        checked_at: nowIso(),
    };
}

export function enterKioskMaintenance(payload = {}) {
    const durationRaw = Number(payload.duration_minutes);
    const durationMinutes = Number.isFinite(durationRaw) && durationRaw > 0
        ? Math.min(1440, Math.floor(durationRaw))
        : 30;
    const expiresAt = payload.expires_at || new Date(Date.now() + durationMinutes * 60000).toISOString();

    const record = {
        kind: 'policy',
        id: crypto.randomUUID(),
        maintenance_mode: true,
        reason: payload.reason || 'manual_maintenance_request',
        requested_by: payload.requested_by || 'operator',
        duration_minutes: durationMinutes,
        expires_at: expiresAt,
        created_at: nowIso(),
    };
    appendRecord(FILES.kiosk, record);

    return {
        ok: true,
        policy: record,
        status: getKioskStatus(),
    };
}

export function exitKioskMaintenance(payload = {}) {
    const record = {
        kind: 'policy',
        id: crypto.randomUUID(),
        maintenance_mode: false,
        reason: payload.reason || 'maintenance_complete',
        requested_by: payload.requested_by || 'operator',
        expires_at: null,
        created_at: nowIso(),
    };
    appendRecord(FILES.kiosk, record);

    return {
        ok: true,
        policy: record,
        status: getKioskStatus(),
    };
}

export function recordKioskIntervention(payload = {}) {
    const record = {
        kind: 'intervention',
        id: crypto.randomUUID(),
        intervention_type: payload.intervention_type || 'manual_check',
        severity: payload.severity || 'info',
        details: payload.details || '',
        requested_by: payload.requested_by || 'operator',
        run_id: payload.run_id || null,
        created_at: nowIso(),
    };
    appendRecord(FILES.kiosk, record);
    return record;
}
