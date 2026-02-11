import { useCallback, useEffect, useMemo, useState } from 'react';
import { getJson, postJson } from '../api';

function parseTools(value) {
    return value
        .split(',')
        .map((tool) => tool.trim())
        .filter(Boolean);
}

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

function statusColor(status) {
    if (status === 'active') return '#10b981';
    if (status === 'failed') return '#ef4444';
    if (status === 'needs_attention') return '#f59e0b';
    return '#9ca3af';
}

function focusColor(mode) {
    if (mode === 'depth_expansion') return '#10b981';
    if (mode === 'atom_stabilization') return '#f59e0b';
    return '#9ca3af';
}

export default function MissionPage({ apiOnline = true }) {
    const [prompt, setPrompt] = useState('Build and execute the next governed milestone in this app.');
    const [runId, setRunId] = useState('');
    const [toolInput, setToolInput] = useState('filesystem,build_test,runtime_ops');
    const [autoExecute, setAutoExecute] = useState(true);
    const [maintenanceReason, setMaintenanceReason] = useState('scheduled_maintenance');
    const [maintenanceMinutes, setMaintenanceMinutes] = useState('30');
    const [message, setMessage] = useState('');
    const [busy, setBusy] = useState(false);

    const [kioskStatus, setKioskStatus] = useState(null);
    const [history, setHistory] = useState([]);
    const [activeMission, setActiveMission] = useState(null);
    const [syntheticRun, setSyntheticRun] = useState(null);
    const [depthDecision, setDepthDecision] = useState(null);

    const missionSummary = useMemo(() => {
        if (!activeMission) return null;
        return {
            status: activeMission.status || 'unknown',
            runId: activeMission.run_id || '-',
            readiness: activeMission.readiness?.takeover_ready === true ? 'READY' : 'GAPS',
            blockers: activeMission.planning_state?.blockers?.length || 0,
            unresolvedTools: activeMission.steps?.find((step) => step.step === 'tool_orchestration')?.unresolved_tools?.length || 0,
        };
    }, [activeMission]);

    const refresh = useCallback(async () => {
        try {
            const [nextKiosk, nextHistory, nextSyntheticRuns, nextDepthDecision] = await Promise.all([
                getJson('/api/kiosk/status'),
                getJson('/api/mission/history?limit=20'),
                getJson('/api/synthetic/runs?limit=1'),
                getJson('/api/synthetic/depth/decision'),
            ]);
            setKioskStatus(nextKiosk);
            setHistory(nextHistory.runs || []);
            const latestSyntheticRun = nextSyntheticRuns.runs?.[0] || null;
            setSyntheticRun(latestSyntheticRun);
            setDepthDecision(nextDepthDecision);

            const missionId = runId || (nextHistory.runs?.[0]?.run_id ?? '');
            if (missionId) {
                const mission = await getJson(`/api/mission/${encodeURIComponent(missionId)}`);
                setRunId(mission.run_id);
                setActiveMission(mission);
            }
        } catch (err) {
            setMessage(`Refresh failed: ${err.message}`);
        }
    }, [runId]);

    useEffect(() => {
        const timer = setTimeout(() => {
            void refresh();
        }, 0);
        return () => clearTimeout(timer);
    }, [refresh]);

    const runMission = async () => {
        if (!prompt.trim()) {
            setMessage('Mission prompt required.');
            return;
        }
        if (!apiOnline) {
            setMessage('Mission blocked: API is offline. Restart from the Genesis Kiosk desktop icon or start server on http://127.0.0.1:3141.');
            return;
        }
        setBusy(true);
        setMessage('Running mission...');
        try {
            const mission = await postJson('/api/mission/run', {
                prompt,
                run_id: runId || undefined,
                requested_tools: parseTools(toolInput),
                auto_execute: autoExecute,
            });
            setRunId(mission.run_id);
            setActiveMission(mission);
            setMessage(`Mission ${mission.run_id} completed with status ${mission.status}.`);
            await refresh();
        } catch (err) {
            setMessage(`Mission failed: ${err.message}. Auto-recovery was notified.`);
        } finally {
            setBusy(false);
        }
    };

    const enterMaintenance = async () => {
        setBusy(true);
        try {
            await postJson('/api/kiosk/maintenance/enter', {
                reason: maintenanceReason,
                duration_minutes: Number(maintenanceMinutes) || 30,
                requested_by: 'mission-page',
            });
            setMessage('Kiosk maintenance mode enabled.');
            await refresh();
        } catch (err) {
            setMessage(`Enable maintenance failed: ${err.message}`);
        } finally {
            setBusy(false);
        }
    };

    const exitMaintenance = async () => {
        setBusy(true);
        try {
            await postJson('/api/kiosk/maintenance/exit', {
                reason: 'operator_resume',
                requested_by: 'mission-page',
            });
            setMessage('Kiosk maintenance mode disabled.');
            await refresh();
        } catch (err) {
            setMessage(`Disable maintenance failed: ${err.message}`);
        } finally {
            setBusy(false);
        }
    };

    const logIntervention = async () => {
        setBusy(true);
        try {
            await postJson('/api/kiosk/interventions', {
                intervention_type: 'manual_intervention',
                severity: 'info',
                details: prompt,
                requested_by: 'mission-page',
                run_id: runId || null,
            });
            setMessage('Intervention logged.');
            await refresh();
        } catch (err) {
            setMessage(`Intervention log failed: ${err.message}`);
        } finally {
            setBusy(false);
        }
    };

    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>MISSION</h1>
                <p>Type intent here. Genesis will plan and execute the governed stack by default.</p>
            </div>

            <div className="grid-4">
                <div className="stat-card">
                    <span className="stat-label">MISSION STATUS</span>
                    <span className="stat-value" style={{ color: statusColor(missionSummary?.status) }}>
                        {(missionSummary?.status || 'idle').toUpperCase()}
                    </span>
                    <span className="stat-sub">latest run state</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">RUN ID</span>
                    <span className="stat-value" style={{ fontSize: 16 }}>
                        {(missionSummary?.runId || '-').slice(0, 10)}
                    </span>
                    <span className="stat-sub">active mission</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">HANDOVER</span>
                    <span className="stat-value" style={{ color: missionSummary?.readiness === 'READY' ? '#10b981' : '#f59e0b' }}>
                        {missionSummary?.readiness || 'N/A'}
                    </span>
                    <span className="stat-sub">takeover readiness</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">KIOSK MODE</span>
                    <span className="stat-value" style={{ color: kioskStatus?.maintenance_mode ? '#f59e0b' : '#10b981' }}>
                        {kioskStatus?.maintenance_mode ? 'MAINTENANCE' : 'LOCKED'}
                    </span>
                    <span className="stat-sub">runtime posture</span>
                </div>
            </div>

            <div className="card">
                <div className="card-header">INTENT COMMAND</div>
                <textarea
                    value={prompt}
                    onChange={(event) => setPrompt(event.target.value)}
                    rows={4}
                    title="Describe what you want Genesis to do"
                    style={{ ...inputStyle(), resize: 'vertical' }}
                />
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr auto auto', gap: 8, marginTop: 10 }}>
                    <input
                        type="text"
                        placeholder="run id (optional)"
                        value={runId}
                        onChange={(event) => setRunId(event.target.value)}
                        title="Optional run id to continue an existing mission context"
                        style={inputStyle()}
                    />
                    <input
                        type="text"
                        placeholder="requested tools"
                        value={toolInput}
                        onChange={(event) => setToolInput(event.target.value)}
                        title="Comma-separated tool list requested for this run"
                        style={inputStyle()}
                    />
                    <button type="button" onClick={() => setAutoExecute((value) => !value)} style={buttonStyle(autoExecute ? 'success' : 'primary')} title="Toggle automatic execution after planning">
                        {autoExecute ? 'AUTO EXEC ON' : 'AUTO EXEC OFF'}
                    </button>
                    <button type="button" onClick={() => void runMission()} style={buttonStyle('success')} disabled={busy || !apiOnline} title="Run mission planning and execution">
                        RUN MISSION
                    </button>
                </div>
                <div style={{ marginTop: 10, fontSize: 11, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                    {message || (apiOnline ? 'Ready.' : 'API offline. Launch from desktop icon to auto-start backend.')}
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">KIOSK OPERATIONS</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr auto auto', gap: 8 }}>
                        <input
                            type="text"
                            placeholder="maintenance reason"
                            value={maintenanceReason}
                            onChange={(event) => setMaintenanceReason(event.target.value)}
                            title="Reason recorded for entering kiosk maintenance"
                            style={inputStyle()}
                        />
                        <input
                            type="number"
                            min="1"
                            max="1440"
                            value={maintenanceMinutes}
                            onChange={(event) => setMaintenanceMinutes(event.target.value)}
                            title="How long maintenance mode should remain active"
                            style={inputStyle()}
                        />
                        <button type="button" onClick={() => void enterMaintenance()} style={buttonStyle('danger')} disabled={busy} title="Unlock kiosk for maintenance operations">
                            ENTER MAINT
                        </button>
                        <button type="button" onClick={() => void exitMaintenance()} style={buttonStyle('success')} disabled={busy} title="Return to locked kiosk mode">
                            RESUME KIOSK
                        </button>
                    </div>
                    <div style={{ display: 'flex', gap: 8, marginTop: 10 }}>
                        <button type="button" onClick={() => void logIntervention()} style={buttonStyle()} disabled={busy} title="Record a maintenance intervention event">
                            LOG INTERVENTION
                        </button>
                        <button type="button" onClick={() => void refresh()} style={buttonStyle('primary')} disabled={busy} title="Reload mission and kiosk data">
                            REFRESH STATE
                        </button>
                    </div>
                    <div style={{ marginTop: 12, fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                        until: {kioskStatus?.maintenance_until || 'n/a'} | interventions: {kioskStatus?.intervention_count || 0}
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">RECENT MISSIONS</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 220, overflowY: 'auto' }}>
                        {history.map((item) => (
                            <button
                                key={item.id}
                                type="button"
                                onClick={async () => {
                                    setRunId(item.run_id);
                                    try {
                                        const detail = await getJson(`/api/mission/${encodeURIComponent(item.run_id)}`);
                                        setActiveMission(detail);
                                        setMessage(`Loaded mission ${item.run_id}.`);
                                    } catch (err) {
                                        setMessage(`Load mission failed: ${err.message}`);
                                    }
                                }}
                                style={{
                                    ...buttonStyle('primary'),
                                    textAlign: 'left',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                }}
                                title={`Load mission ${item.run_id}`}
                            >
                                <span>{item.run_id.slice(0, 10)}</span>
                                <span style={{ color: statusColor(item.status) }}>{(item.status || 'unknown').toUpperCase()}</span>
                            </button>
                        ))}
                        {history.length === 0 && (
                            <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                                No mission runs yet.
                            </div>
                        )}
                    </div>
                </div>
            </div>

            <div className="grid-2">
                <div className="card">
                    <div className="card-header">MISSION DETAIL</div>
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
                    }}
                    >
                        {JSON.stringify(activeMission, null, 2)}
                    </pre>
                </div>

                <div className="card">
                    <div className="card-header">KIOSK STATUS</div>
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
                    }}
                    >
                        {JSON.stringify(kioskStatus, null, 2)}
                    </pre>
                </div>
            </div>

            <div className="card">
                <div className="card-header">SYNTHETIC DEPTH QUESTIONS</div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, minmax(0, 1fr))', gap: 8, marginBottom: 10 }}>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#9ca3af' }}>
                        run: <span style={{ color: '#e5e7eb' }}>{syntheticRun?.run_id?.slice(0, 10) || 'n/a'}</span>
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#9ca3af' }}>
                        focus: <span style={{ color: focusColor(syntheticRun?.loop_focus_mode) }}>{(syntheticRun?.loop_focus_mode || 'unknown').toUpperCase()}</span>
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#9ca3af' }}>
                        decision: <span style={{ color: '#10b981' }}>{(depthDecision?.decision?.decision || syntheticRun?.depth_decision_status || 'auto').toUpperCase()}</span>
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: '#9ca3af' }}>
                        questions: <span style={{ color: '#e5e7eb' }}>{syntheticRun?.depth_question_count || 0}</span>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
                    <button
                        type="button"
                        onClick={() => void refresh()}
                        style={buttonStyle('primary')}
                        disabled={busy}
                        title="Refresh synthetic depth status"
                    >
                        REFRESH DEPTH
                    </button>
                    <div style={{ alignSelf: 'center', fontFamily: 'var(--font-mono)', fontSize: 10, color: '#9ca3af' }}>
                        autonomous mode: depth missions auto-run when stable
                    </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 260, overflowY: 'auto' }}>
                    {(syntheticRun?.depth_questions || []).map((question, index) => (
                        <div
                            key={question.question_id}
                            style={{
                                display: 'flex',
                                gap: 10,
                                alignItems: 'flex-start',
                                padding: 8,
                                border: '1px solid var(--genesis-border)',
                                borderRadius: 8,
                                background: 'var(--genesis-bg)',
                            }}
                        >
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                                <div style={{ fontSize: 11, color: '#e5e7eb', fontFamily: 'var(--font-mono)' }}>
                                    {index + 1}. {question.question}
                                </div>
                                <div style={{ fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                                    why: {question.why}
                                </div>
                                <div style={{ fontSize: 10, color: '#60a5fa', fontFamily: 'var(--font-mono)' }}>
                                    build: {question.suggested_functionality}
                                </div>
                            </div>
                        </div>
                    ))}
                    {(syntheticRun?.depth_questions || []).length === 0 && (
                        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            No depth questions available yet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
