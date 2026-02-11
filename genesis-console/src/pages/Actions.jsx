import { useCallback, useEffect, useMemo, useState } from 'react';
import { getJson, postJson } from '../api';

function inputStyle(width = '100%') {
    return {
        width,
        padding: '8px 12px',
        background: 'var(--genesis-bg)',
        border: '1px solid var(--genesis-border)',
        borderRadius: 'var(--radius-sm)',
        color: '#e5e7eb',
        fontFamily: 'var(--font-mono)',
        fontSize: 12,
        outline: 'none',
    };
}

function buttonStyle(kind = 'primary') {
    const base = {
        padding: '8px 12px',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--genesis-border)',
        fontSize: 10,
        fontFamily: 'var(--font-mono)',
        letterSpacing: 1,
        cursor: 'pointer',
    };

    if (kind === 'danger') {
        return {
            ...base,
            background: 'rgba(239,68,68,0.12)',
            color: '#ef4444',
            border: '1px solid rgba(239,68,68,0.25)',
        };
    }

    if (kind === 'success') {
        return {
            ...base,
            background: 'rgba(16,185,129,0.12)',
            color: '#10b981',
            border: '1px solid rgba(16,185,129,0.25)',
        };
    }

    return {
        ...base,
        background: 'rgba(59,130,246,0.12)',
        color: '#60a5fa',
        border: '1px solid rgba(59,130,246,0.25)',
    };
}

function parseTools(value) {
    return value
        .split(',')
        .map((tool) => tool.trim())
        .filter(Boolean);
}

function statusColor(ok) {
    return ok ? '#10b981' : '#f59e0b';
}

export default function ActionsPage() {
    const [runId, setRunId] = useState('');
    const [intent, setIntent] = useState('Bootstrap handover stack and keep support architecture stable.');
    const [toolInput, setToolInput] = useState('filesystem,build_test');
    const [incidentId, setIncidentId] = useState('');
    const [cycleId, setCycleId] = useState('');
    const [message, setMessage] = useState('');

    const [handover, setHandover] = useState(null);
    const [sentinel, setSentinel] = useState(null);
    const [recursiveHealth, setRecursiveHealth] = useState(null);
    const [planningState, setPlanningState] = useState(null);
    const [recoveryStatus, setRecoveryStatus] = useState(null);
    const [recoveryRuns, setRecoveryRuns] = useState([]);
    const [syntheticStatus, setSyntheticStatus] = useState(null);
    const [syntheticRuns, setSyntheticRuns] = useState([]);
    const [syntheticFeedback, setSyntheticFeedback] = useState([]);
    const [syntheticEnabled, setSyntheticEnabled] = useState(true);
    const [syntheticIntervalMs, setSyntheticIntervalMs] = useState('120000');
    const [lastResult, setLastResult] = useState(null);

    const summary = useMemo(() => {
        const takeoverReady = Boolean(handover?.takeover_ready);
        const criticalGaps = handover?.critical_gaps?.length || 0;
        const openIncidents = sentinel?.open_incidents || 0;
        const cycleCount = recursiveHealth?.cycle_count || 0;
        return { takeoverReady, criticalGaps, openIncidents, cycleCount };
    }, [handover, sentinel, recursiveHealth]);

    const refresh = useCallback(async () => {
        try {
            const [nextHandover, nextSentinel, nextRecursive] = await Promise.all([
                getJson('/api/handover/readiness'),
                getJson('/api/sentinel/status'),
                getJson('/api/synthesis/recursive/health'),
            ]);

            setHandover(nextHandover);
            setSentinel(nextSentinel);
            setRecursiveHealth(nextRecursive);
            const [nextRecoveryStatus, nextRecoveryRuns, nextSyntheticStatus, nextSyntheticRuns, nextSyntheticFeedback] = await Promise.all([
                getJson('/api/recovery/status'),
                getJson('/api/recovery/runs?limit=8'),
                getJson('/api/synthetic/status'),
                getJson('/api/synthetic/runs?limit=6'),
                getJson('/api/synthetic/feedback?limit=4'),
            ]);
            setRecoveryStatus(nextRecoveryStatus);
            setRecoveryRuns(nextRecoveryRuns.runs || []);
            setSyntheticStatus(nextSyntheticStatus);
            setSyntheticRuns(nextSyntheticRuns.runs || []);
            setSyntheticFeedback(nextSyntheticFeedback.feedback || []);
            setSyntheticEnabled(nextSyntheticStatus?.enabled !== false);
            if (nextSyntheticStatus?.interval_ms) {
                setSyntheticIntervalMs(String(nextSyntheticStatus.interval_ms));
            }

            if (runId) {
                try {
                    const nextPlanning = await getJson(`/api/planning/state/${encodeURIComponent(runId)}`);
                    setPlanningState(nextPlanning);
                } catch {
                    setPlanningState(null);
                }
            }

            setMessage('Support stack refreshed.');
        } catch (err) {
            setMessage(`Refresh failed: ${err.message}`);
        }
    }, [runId]);

    useEffect(() => {
        const initial = setTimeout(() => {
            void refresh();
        }, 0);
        return () => clearTimeout(initial);
    }, [refresh]);

    const runAction = useCallback(async (label, fn) => {
        try {
            const result = await fn();
            setLastResult({ label, result });
            setMessage(`${label} completed.`);
            await refresh();
            return result;
        } catch (err) {
            setMessage(`${label} failed: ${err.message}`);
            return null;
        }
    }, [refresh]);

    const handleCreatePlan = async () => {
        const result = await runAction('Intent plan refresh', () => postJson('/api/planning/intent-plan', {
            run_id: runId || undefined,
            intent,
        }));
        if (result?.run_id) setRunId(result.run_id);
    };

    const handleSyncTodos = async () => {
        if (!runId) {
            setMessage('Set run id first (create a plan).');
            return;
        }
        await runAction('Todo sync', () => postJson('/api/planning/todos/sync', { run_id: runId }));
    };

    const handleOrchestrate = async () => {
        await runAction('Tool orchestration', () => postJson('/api/tools/orchestrate', {
            objective: 'actions_ui_orchestration',
            requested_tools: parseTools(toolInput),
            run_id: runId || undefined,
            fallback_path: 'owner_escalation',
        }));
    };

    const handleRehearsal = async () => {
        const result = await runAction('Handover rehearsal', () => postJson('/api/handover/rehearse', {
            run_id: runId || undefined,
            intent,
            requested_tools: parseTools(toolInput),
        }));
        if (result?.evidence?.plan_id && !runId) {
            const planId = result.evidence.plan_id;
            setMessage(`Handover rehearsal completed (plan ${planId.slice(0, 8)}...)`);
        }
    };

    const handleHeartbeat = async () => {
        await runAction('Sentinel heartbeat', () => postJson('/api/sentinel/heartbeat', {
            unit_id: 'scout',
            health_state: 'online',
            capability_vector: {
                planning: true,
                orchestration: true,
                synthesis: true,
            },
        }));
    };

    const handleAnomaly = async () => {
        const result = await runAction('Sentinel anomaly', () => postJson('/api/sentinel/anomaly', {
            unit_id: 'scout',
            severity: 'high',
            blast_radius: 'single_unit',
            details: 'manual anomaly drill from actions UI',
        }));
        if (result?.incident_id) setIncidentId(result.incident_id);
    };

    const handleEscalate = async () => {
        if (!incidentId) {
            setMessage('Set incident id first.');
            return;
        }
        await runAction('Sentinel escalation', () => postJson('/api/sentinel/escalate', {
            incident_id: incidentId,
            stage: 'owner_alert',
            note: 'escalated from actions UI',
        }));
    };

    const handleOperatorCheck = async () => {
        if (!incidentId) {
            setMessage('Set incident id first.');
            return;
        }
        await runAction('Operator check', () => postJson('/api/sentinel/operator-check', {
            incident_id: incidentId,
            channel: 'primary',
            consent_policy: 'anomaly_only',
            note: 'operator check-in from actions UI',
        }));
    };

    const handleStartCycle = async () => {
        const result = await runAction('Recursive cycle start', () => postJson('/api/synthesis/recursive/cycle', {
            cycle_id: cycleId || undefined,
            conversation: intent,
            plan_deltas: runId ? [`run:${runId}`] : [],
            product_effects: ['reliability_gain'],
            mind_change_record: 'support stack requires continuous recursive evaluation',
        }));
        if (result?.cycle_id) setCycleId(result.cycle_id);
    };

    const handleIngestCycle = async () => {
        if (!cycleId) {
            setMessage('Set cycle id first (start a cycle).');
            return;
        }
        await runAction('Recursive cycle ingest', () => postJson('/api/synthesis/recursive/ingest', {
            cycle_id: cycleId,
            outputs: [
                {
                    type: 'synthesis',
                    source: 'actions_ui',
                    content: intent,
                },
            ],
            learning_candidates: [
                {
                    kind: 'workflow',
                    note: 'keep handover/sentinel/recursive checks active in every gate',
                },
            ],
        }));
    };

    const handleEvaluateCycle = async () => {
        if (!cycleId) {
            setMessage('Set cycle id first (start a cycle).');
            return;
        }
        await runAction('Recursive cycle evaluate', () => postJson('/api/synthesis/recursive/evaluate', {
            cycle_id: cycleId,
            product_effects: ['delivery_risk_reduction'],
            cost_ok: true,
            risk_ok: true,
            peer_review_ok: true,
            mind_change_record: 'promote only with governed product impact',
        }));
    };

    const handlePromoteCycle = async () => {
        if (!cycleId) {
            setMessage('Set cycle id first (start a cycle).');
            return;
        }
        await runAction('Recursive cycle promote', () => postJson('/api/synthesis/recursive/promote', {
            cycle_id: cycleId,
            title: 'Support-stack governance backlog item',
        }));
    };

    const handleRecoveryTrigger = async () => {
        await runAction('Auto-recovery trigger', () => postJson('/api/recovery/trigger', {
            source: 'actions_ui',
            level: 'error',
            reason: intent || 'operator_requested_auto_recovery',
            context: {
                run_id: runId || null,
                incident_id: incidentId || null,
            },
        }));
    };

    const handleSyntheticTrigger = async () => {
        await runAction('Synthetic E2E trigger', () => postJson('/api/synthetic/trigger', {
            reason: 'actions_ui_manual_trigger',
        }));
    };

    const handleSyntheticConfigure = async () => {
        await runAction('Synthetic monitor configure', () => postJson('/api/synthetic/configure', {
            enabled: syntheticEnabled,
            interval_ms: Number(syntheticIntervalMs) || 120000,
        }));
    };

    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>ACTIONS</h1>
                <p>Operate the handover stack, continuity sentinel, and recursive synthesis protocol from one governance surface.</p>
            </div>

            <div className="grid-4">
                <div className="stat-card">
                    <span className="stat-label">TAKEOVER READY</span>
                    <span className="stat-value" style={{ color: statusColor(summary.takeoverReady) }}>
                        {summary.takeoverReady ? 'YES' : 'NO'}
                    </span>
                    <span className="stat-sub">handover support stack</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">CRITICAL GAPS</span>
                    <span className="stat-value" style={{ color: summary.criticalGaps === 0 ? '#10b981' : '#ef4444' }}>
                        {summary.criticalGaps}
                    </span>
                    <span className="stat-sub">blocking handover items</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">OPEN INCIDENTS</span>
                    <span className="stat-value" style={{ color: summary.openIncidents === 0 ? '#10b981' : '#f59e0b' }}>
                        {summary.openIncidents}
                    </span>
                    <span className="stat-sub">continuity sentinel</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">RECURSIVE CYCLES</span>
                    <span className="stat-value" style={{ color: '#8b5cf6' }}>{summary.cycleCount}</span>
                    <span className="stat-sub">synthesis history depth</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">AUTO RECOVERY</span>
                    <span className="stat-value" style={{ color: recoveryStatus?.running ? '#f59e0b' : '#10b981', fontSize: 18 }}>
                        {recoveryStatus?.running ? 'RUNNING' : 'IDLE'}
                    </span>
                    <span className="stat-sub">pending: {recoveryStatus?.pending_events || 0}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">SYNTHETIC E2E</span>
                    <span className="stat-value" style={{ color: syntheticStatus?.running ? '#f59e0b' : '#10b981', fontSize: 18 }}>
                        {syntheticStatus?.running ? 'RUNNING' : (syntheticStatus?.last_status || 'IDLE').toUpperCase()}
                    </span>
                    <span className="stat-sub">
                        stable: {syntheticStatus?.longevity?.is_stable ? 'YES' : 'NO'} | next: {syntheticStatus?.next_run_at || 'n/a'}
                    </span>
                </div>
            </div>

            <div className="card">
                <div className="card-header">GLOBAL CONTROLS</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr auto', gap: 10 }}>
                    <input
                        type="text"
                        placeholder="run id"
                        value={runId}
                        onChange={(e) => setRunId(e.target.value)}
                        title="Mission run id for planning and handover actions"
                        style={inputStyle()}
                    />
                    <input
                        type="text"
                        placeholder="requested tools (comma separated)"
                        value={toolInput}
                        onChange={(e) => setToolInput(e.target.value)}
                        title="Comma-separated tools requested for orchestration"
                        style={inputStyle()}
                    />
                    <button type="button" onClick={() => void refresh()} style={buttonStyle('success')} title="Refresh all support-stack snapshots">REFRESH</button>
                </div>
                <textarea
                    value={intent}
                    onChange={(e) => setIntent(e.target.value)}
                    rows={3}
                    title="Intent context used by actions on this screen"
                    style={{ ...inputStyle(), marginTop: 10, resize: 'vertical' }}
                />
                <div style={{ marginTop: 10, fontSize: 11, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                    {message || 'Ready.'}
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">HANDOVER SUPPORT</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                        <button type="button" onClick={() => void handleCreatePlan()} style={buttonStyle()} title="Create or refresh intent plan for the current run">INTENT PLAN</button>
                        <button type="button" onClick={() => void handleSyncTodos()} style={buttonStyle()} title="Sync plan items into todo graph">SYNC TODOS</button>
                        <button type="button" onClick={() => void handleOrchestrate()} style={buttonStyle()} title="Generate tool orchestration trace for this objective">ORCHESTRATE</button>
                        <button type="button" onClick={() => void handleRehearsal()} style={buttonStyle('success')} title="Run handover rehearsal and readiness checks">REHEARSE</button>
                    </div>
                    <div style={{ marginTop: 12, fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                        Critical gaps: {(handover?.critical_gaps || []).join(', ') || 'none'}
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">CONTINUITY SENTINEL</div>
                    <input
                        type="text"
                        placeholder="incident id"
                        value={incidentId}
                        onChange={(e) => setIncidentId(e.target.value)}
                        title="Incident id for anomaly escalation and operator checks"
                        style={inputStyle()}
                    />
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 10 }}>
                        <button type="button" onClick={() => void handleHeartbeat()} style={buttonStyle('success')} title="Send a unit heartbeat signal">HEARTBEAT</button>
                        <button type="button" onClick={() => void handleAnomaly()} style={buttonStyle('danger')} title="Create an anomaly incident for drill/testing">ANOMALY</button>
                        <button type="button" onClick={() => void handleEscalate()} style={buttonStyle('danger')} title="Escalate the selected incident">ESCALATE</button>
                        <button type="button" onClick={() => void handleOperatorCheck()} style={buttonStyle()} title="Run operator outreach check for incident">CHECK-IN</button>
                    </div>
                </div>
            </div>

            <div className="card">
                <div className="card-header">RECURSIVE SYNTHESIS</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto auto auto', gap: 8 }}>
                    <input
                        type="text"
                        placeholder="cycle id"
                        value={cycleId}
                        onChange={(e) => setCycleId(e.target.value)}
                        title="Recursive synthesis cycle id"
                        style={inputStyle()}
                    />
                    <button type="button" onClick={() => void handleStartCycle()} style={buttonStyle('success')} title="Start a new recursive synthesis cycle">START</button>
                    <button type="button" onClick={() => void handleIngestCycle()} style={buttonStyle()} title="Ingest outputs into active cycle">INGEST</button>
                    <button type="button" onClick={() => void handleEvaluateCycle()} style={buttonStyle()} title="Evaluate cycle against governance gates">EVALUATE</button>
                    <button type="button" onClick={() => void handlePromoteCycle()} style={buttonStyle('success')} title="Promote cycle if promotable">PROMOTE</button>
                </div>
            </div>

            <div className="card">
                <div className="card-header">AUTO RECOVERY</div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    <button
                        type="button"
                        onClick={() => void handleRecoveryTrigger()}
                        style={buttonStyle('danger')}
                        title="Queue immediate self-heal + lint/build/runtime checks"
                    >
                        TRIGGER RECOVERY
                    </button>
                    <button
                        type="button"
                        onClick={() => void refresh()}
                        style={buttonStyle('success')}
                        title="Refresh recovery status and recent runs"
                    >
                        REFRESH RECOVERY
                    </button>
                </div>
                <div style={{ marginTop: 10, fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                    last: {recoveryStatus?.last_status || 'n/a'} | completed: {recoveryStatus?.last_completed_at || 'n/a'}
                </div>
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {recoveryRuns.map((run) => (
                        <div key={run.run_id} style={{
                            padding: '8px 10px',
                            background: 'var(--genesis-bg)',
                            border: '1px solid var(--genesis-border)',
                            borderRadius: 8,
                            fontFamily: 'var(--font-mono)',
                            fontSize: 10,
                            color: '#9ca3af',
                        }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                                <span>{run.status}</span>
                                <span>{run.duration_ms}ms</span>
                            </div>
                            <div>{run.summary}</div>
                        </div>
                    ))}
                    {recoveryRuns.length === 0 && (
                        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            No recovery runs yet.
                        </div>
                    )}
                </div>
            </div>

            <div className="card">
                <div className="card-header">SYNTHETIC USER MONITOR</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'auto 180px auto', gap: 8, marginBottom: 10 }}>
                    <button
                        type="button"
                        onClick={() => setSyntheticEnabled((value) => !value)}
                        style={buttonStyle(syntheticEnabled ? 'success' : 'danger')}
                        title="Toggle synthetic monitoring"
                    >
                        {syntheticEnabled ? 'MONITOR ON' : 'MONITOR OFF'}
                    </button>
                    <input
                        type="text"
                        value={syntheticIntervalMs}
                        onChange={(event) => setSyntheticIntervalMs(event.target.value)}
                        title="Synthetic loop interval in milliseconds"
                        placeholder="interval ms"
                        style={inputStyle()}
                    />
                    <button
                        type="button"
                        onClick={() => void handleSyntheticConfigure()}
                        style={buttonStyle()}
                        title="Apply synthetic loop settings"
                    >
                        APPLY LOOP
                    </button>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                    <button
                        type="button"
                        onClick={() => void handleSyntheticTrigger()}
                        style={buttonStyle('success')}
                        title="Run an immediate synthetic end-to-end user journey"
                    >
                        RUN E2E NOW
                    </button>
                    <button
                        type="button"
                        onClick={() => void refresh()}
                        style={buttonStyle()}
                        title="Refresh synthetic monitor status and history"
                    >
                        REFRESH E2E
                    </button>
                </div>
                <div style={{ marginTop: 10, fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                    enabled: {String(syntheticStatus?.enabled ?? false)} | interval: {syntheticStatus?.interval_ms || 0}ms | last: {syntheticStatus?.last_status || 'n/a'}
                </div>
                <div style={{ marginTop: 6, fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                    streak: {syntheticStatus?.longevity?.consecutive_healthy || 0}/{syntheticStatus?.longevity?.target_streak || 0}
                    {' '}| pass rate: {syntheticStatus?.longevity?.rolling_pass_rate ?? 0}
                    {' '}| degraded 24h: {syntheticStatus?.longevity?.degraded_last_24h ?? 0}
                </div>
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {syntheticRuns.map((run) => (
                        <div key={run.run_id} style={{
                            padding: '8px 10px',
                            background: 'var(--genesis-bg)',
                            border: '1px solid var(--genesis-border)',
                            borderRadius: 8,
                            fontFamily: 'var(--font-mono)',
                            fontSize: 10,
                            color: '#9ca3af',
                        }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                                <span>{run.status}</span>
                                <span>{run.duration_ms}ms</span>
                            </div>
                            <div>{run.summary}</div>
                        </div>
                    ))}
                    {syntheticRuns.length === 0 && (
                        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            No synthetic runs yet.
                        </div>
                    )}
                </div>
                <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                    {syntheticFeedback.map((entry) => (
                        <div key={entry.run_id} style={{
                            padding: '8px 10px',
                            background: 'var(--genesis-bg)',
                            border: '1px solid var(--genesis-border)',
                            borderRadius: 8,
                            fontFamily: 'var(--font-mono)',
                            fontSize: 10,
                            color: '#9ca3af',
                        }}
                        >
                            <div style={{ marginBottom: 4 }}>
                                persona feedback ({entry.status}) | priority: {entry.builder_feedback?.priority || 'n/a'}
                            </div>
                            <div>{String(entry.persona_feedback || '').slice(0, 220) || 'No persona feedback captured.'}</div>
                        </div>
                    ))}
                    {syntheticFeedback.length === 0 && (
                        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            No persona/builder feedback yet.
                        </div>
                    )}
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">LIVE STATE</div>
                    <pre style={{
                        margin: 0,
                        padding: 10,
                        background: 'var(--genesis-bg)',
                        borderRadius: 8,
                        maxHeight: 360,
                        overflow: 'auto',
                        fontSize: 10,
                        color: '#9ca3af',
                        fontFamily: 'var(--font-mono)',
                        lineHeight: 1.5,
                    }}>
                        {JSON.stringify({ handover, sentinel, recursiveHealth, planningState }, null, 2)}
                    </pre>
                </div>

                <div className="card">
                    <div className="card-header">LAST ACTION</div>
                    <pre style={{
                        margin: 0,
                        padding: 10,
                        background: 'var(--genesis-bg)',
                        borderRadius: 8,
                        maxHeight: 360,
                        overflow: 'auto',
                        fontSize: 10,
                        color: '#9ca3af',
                        fontFamily: 'var(--font-mono)',
                        lineHeight: 1.5,
                    }}>
                        {JSON.stringify(lastResult, null, 2)}
                    </pre>
                </div>
            </div>
        </div>
    );
}
