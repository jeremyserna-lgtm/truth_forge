// Genesis Console — Dashboard Page (Mission Control Overview)
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MODELS, SOVEREIGNTY_ITEMS, ATOM_TYPES } from '../constants';
import { Heartbeat, AnimaMemory, SovereigntyStatus, OllamaStatusBadge, AtomBadge } from '../components';
import { getJson } from '../api';

const TRIAD_COLORS = {
    CORE: '#3b82f6',
    SUPPORTIVE: '#f59e0b',
    META: '#8b5cf6',
};

const SOVEREIGN_COLORS = {
    TRUTH_FORGE: '#10b981',
    PRIMITIVE_ENGINE: '#f97316',
    CREDENTIAL_ATLAS: '#06b6d4',
};

const SOVEREIGN_INFO = {
    TRUTH_FORGE: { label: 'TRUTH FORGE', role: 'The Brain', stance: 'I hold the soul.', icon: '🧠' },
    PRIMITIVE_ENGINE: { label: 'PRIMITIVE ENGINE', role: 'The Hands', stance: 'I build the bridge.', icon: '🔨' },
    CREDENTIAL_ATLAS: { label: 'CREDENTIAL ATLAS', role: 'The Eyes', stance: 'I verify existence.', icon: '👁' },
};

export default function DashboardPage({ ollamaStatus, uptime, engines, totalAtoms, cascadeCycle, saturation, log, pipelineAtoms }) {
    const navigate = useNavigate();
    const recentLog = (log || []).slice(-5).reverse();
    const [recentAtoms, setRecentAtoms] = useState(pipelineAtoms || []);
    const [triad, setTriad] = useState(null);

    useEffect(() => {
        void getJson('/api/atoms?limit=6').then((data) => {
            const mapped = (data.atoms || []).map(a => ({
                type: a.type, text: a.content, conf: a.confidence, id: a.id,
            }));
            if (mapped.length > 0) setRecentAtoms(mapped);
        }).catch(() => { });

        void getJson('/api/triad').then(setTriad).catch(() => { });
    }, []);

    const triadHealth = triad?.health || {};

    return (
        <div className="main-panel">
            {/* Hero Banner */}
            <div style={{
                background: 'linear-gradient(135deg, #0f172a 0%, #1a1030 60%, #0a0f1a 100%)',
                borderRadius: 'var(--radius-xl)',
                padding: '32px 36px',
                border: '1px solid var(--genesis-border)',
                position: 'relative',
                overflow: 'hidden',
            }}>
                {/* Subtle grid pattern */}
                <div style={{
                    position: 'absolute', inset: 0,
                    backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(139,92,246,0.06) 1px, transparent 0)',
                    backgroundSize: '30px 30px',
                }} />

                <div style={{ position: 'relative', zIndex: 1, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <h1 style={{
                            fontSize: 28, fontWeight: 900, fontFamily: 'var(--font-mono)',
                            letterSpacing: 4, color: '#e5e7eb', margin: 0,
                        }}>
                            GENESIS
                        </h1>
                        <p style={{ fontSize: 11, color: '#6b7280', fontFamily: 'var(--font-mono)', letterSpacing: 2, marginTop: 4 }}>
                            THREE ONTOLOGICAL ROLES · SOVEREIGN INTELLIGENCE
                        </p>
                        <div style={{ display: 'flex', gap: 16, marginTop: 20, alignItems: 'center' }}>
                            <Heartbeat active={true} />
                            <OllamaStatusBadge connected={ollamaStatus.connected} modelCount={ollamaStatus.models.length} />
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginTop: 14, flexWrap: 'wrap' }}>
                            <button
                                type="button"
                                onClick={() => navigate('/pipeline')}
                                title="Open pipeline to process files into atoms"
                                style={{
                                    padding: '7px 10px',
                                    borderRadius: 8,
                                    border: '1px solid rgba(59,130,246,0.35)',
                                    background: 'rgba(59,130,246,0.12)',
                                    color: '#60a5fa',
                                    fontSize: 10,
                                    fontFamily: 'var(--font-mono)',
                                    letterSpacing: 1,
                                    cursor: 'pointer',
                                }}
                            >
                                OPEN PIPELINE
                            </button>
                            <button
                                type="button"
                                onClick={() => navigate('/chat?route=/dashboard')}
                                title="Ask assistant to explain this dashboard"
                                style={{
                                    padding: '7px 10px',
                                    borderRadius: 8,
                                    border: '1px solid var(--genesis-border-light)',
                                    background: 'rgba(17,24,39,0.92)',
                                    color: '#d1d5db',
                                    fontSize: 10,
                                    fontFamily: 'var(--font-mono)',
                                    letterSpacing: 1,
                                    cursor: 'pointer',
                                }}
                            >
                                ASK ASSISTANT
                            </button>
                        </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 36, fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#10b981' }}>
                            $0.00
                        </div>
                        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)', letterSpacing: 1 }}>
                            TODAY'S CLOUD COST
                        </div>
                        <div style={{ fontSize: 11, color: '#4b5563', fontFamily: 'var(--font-mono)', marginTop: 8 }}>
                            UPTIME {uptime}
                        </div>
                    </div>
                </div>
            </div>

            {/* Architectural Triad — Structure (Anatomy) */}
            <div style={{ marginBottom: 4 }}>
                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', letterSpacing: 2, marginBottom: 8, paddingLeft: 4 }}>
                    PILLAR 1 — STRUCTURE (Anatomy) · "Is this robust?"
                </div>
                <div className="grid-3" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
                    {['CORE', 'SUPPORTIVE', 'META'].map(layer => {
                        const pillar = triad?.pillars?.[layer];
                        const color = TRIAD_COLORS[layer];
                        const svcCount = pillar?.service_count || 0;
                        return (
                            <div key={layer} className="stat-card" style={{ borderTop: `2px solid ${color}` }}>
                                <span className="stat-label" style={{ color }}>{layer}</span>
                                <span className="stat-value" style={{ color, fontSize: 20 }}>{svcCount}</span>
                                <span className="stat-sub">{pillar?.definition || '...'}</span>
                                <div style={{ marginTop: 6, fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                                    {(pillar?.services || []).map(s => s.name).join(' · ') || 'loading...'}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Federation of Sovereigns — Agency (Who Acts) */}
            <div style={{ marginBottom: 4 }}>
                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', letterSpacing: 2, marginBottom: 8, paddingLeft: 4 }}>
                    PILLAR 3 — AGENCY (Who Acts) · "Who is acting?"
                </div>
                <div className="grid-3" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
                    {Object.entries(SOVEREIGN_INFO).map(([key, sov]) => {
                        const count = triad?.federation?.[key.toLowerCase()] || 0;
                        const color = SOVEREIGN_COLORS[key];
                        return (
                            <div key={key} className="stat-card" style={{ borderTop: `2px solid ${color}` }}>
                                <span className="stat-label" style={{ color, display: 'flex', alignItems: 'center', gap: 6 }}>
                                    <span style={{ fontSize: 14 }}>{sov.icon}</span> {sov.label}
                                </span>
                                <span className="stat-value" style={{ color, fontSize: 18 }}>{count}</span>
                                <span className="stat-sub" style={{ fontStyle: 'italic' }}>"{sov.stance}"</span>
                                <div style={{ marginTop: 4, fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                                    {sov.role}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid-4">
                <div className="stat-card">
                    <span className="stat-label">TOTAL ATOMS</span>
                    <span className="stat-value" style={{ color: '#3b82f6' }}>{totalAtoms || 0}</span>
                    <span className="stat-sub">knowledge units extracted</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">ONTOLOGY</span>
                    <span className="stat-value" style={{ color: triadHealth.balance_score >= 70 ? '#10b981' : '#f59e0b' }}>
                        {triadHealth.balance_score || 0}%
                    </span>
                    <span className="stat-sub">{triadHealth.total_services || 0} services × 3 dimensions</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">SATURATION</span>
                    <span className="stat-value" style={{ color: '#f59e0b' }}>{Math.round((saturation || 0) * 100)}%</span>
                    <span className="stat-sub">information density</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">CLUSTER</span>
                    <span className="stat-value" style={{ color: '#10b981' }}>1.28TB</span>
                    <span className="stat-sub">unified memory</span>
                </div>
            </div>

            {/* Models + ANIMA Row */}
            <div className="grid-2">
                {/* Models Overview */}
                <div className="card">
                    <div className="card-header">COGNITION TRIAD</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {MODELS.map(m => (
                            <div key={m.id} style={{
                                display: 'flex', alignItems: 'center', gap: 12,
                                padding: '10px 14px',
                                background: 'var(--genesis-bg)',
                                borderRadius: 'var(--radius-md)',
                                border: '1px solid var(--genesis-border)',
                            }}>
                                <div style={{
                                    width: 38, height: 38, borderRadius: 'var(--radius-sm)',
                                    background: `linear-gradient(135deg, ${m.color}33, ${m.color}11)`,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    border: `1px solid ${m.color}44`,
                                }}>
                                    <span style={{ fontSize: 14, fontWeight: 800, color: m.color, fontFamily: 'var(--font-mono)' }}>
                                        {m.name.charAt(0)}
                                    </span>
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <span style={{ fontSize: 13, fontWeight: 700, color: m.color, fontFamily: 'var(--font-mono)' }}>
                                            {m.name}
                                        </span>
                                        <span style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>{m.mem}</span>
                                    </div>
                                    <div style={{ fontSize: 10, color: '#9ca3af', marginTop: 2 }}>{m.role} — {m.desc}</div>
                                </div>
                                <div className={`status-dot ${ollamaStatus.models.some(om =>
                                    om.name.toLowerCase().includes(m.id) ||
                                    om.name.toLowerCase().includes(m.name.toLowerCase())
                                ) ? 'online' : 'offline'
                                    }`} />
                            </div>
                        ))}
                    </div>
                </div>

                {/* ANIMA + Sovereignty */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--gap-lg)' }}>
                    <AnimaMemory engines={engines} />
                    <SovereigntyStatus items={SOVEREIGNTY_ITEMS} />
                </div>
            </div>

            {/* Recent Atoms + Recent Log Row */}
            <div className="grid-2">
                {/* Recent Atoms Preview */}
                <div className="card" style={{ maxHeight: 300 }}>
                    <div className="card-header">
                        <span>RECENT ATOMS</span>
                        <span className="badge">{recentAtoms.length}</span>
                    </div>
                    <div style={{ overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 220 }}>
                        {recentAtoms.length === 0 ? (
                            <div style={{ padding: 20, textAlign: 'center', color: '#4b5563', fontSize: 11 }}>
                                No atoms yet. Drop files in Pipeline.
                            </div>
                        ) : (
                            recentAtoms.slice(0, 6).map((atom, i) => (
                                <div key={atom.id || i} style={{
                                    padding: '8px 10px',
                                    background: 'var(--genesis-bg)',
                                    borderRadius: 6,
                                    borderLeft: `3px solid ${(ATOM_TYPES[atom.type] || {}).color || '#6b7280'}`,
                                }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
                                        <AtomBadge type={atom.type} />
                                        <span style={{ fontSize: 9, color: '#4b5563', fontFamily: 'var(--font-mono)' }}>
                                            {Math.round(atom.conf * 100)}%
                                        </span>
                                    </div>
                                    <div style={{ fontSize: 11, color: '#c0c8d4', lineHeight: 1.4 }}>{atom.text}</div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Recent System Log */}
                <div className="card" style={{ maxHeight: 300 }}>
                    <div className="card-header">SYSTEM LOG</div>
                    <div style={{ overflow: 'auto', maxHeight: 220 }}>
                        {recentLog.length === 0 ? (
                            <div style={{ color: '#4b5563', fontFamily: 'var(--font-mono)', fontSize: 10, padding: 16 }}>
                                Genesis Console operational. Awaiting first intake.
                            </div>
                        ) : (
                            recentLog.map(entry => (
                                <div key={entry.id} className="log-entry">
                                    <span className="timestamp">{entry.ts}</span>
                                    <span style={{
                                        color: entry.level === 'success' ? '#10b981' : entry.level === 'warn' ? '#f59e0b' : '#9ca3af',
                                    }}>{entry.msg}</span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
