// Genesis Console — Models Page (Cognition Bus Deep View)
import { MODELS } from '../constants';

const HARDWARE = [
    { label: 'KING', type: 'Mac Studio 512GB', role: 'Command Node', mem: '512GB', color: '#f59e0b', models: ['Scout', 'ANIMA', 'DuckDB', 'Heartbeat'] },
    { label: 'SOLDIER-1', type: 'Mac Studio 256GB', role: 'Compute Node', mem: '256GB', color: '#3b82f6', models: ['EXO shard (Maverick/R1)'] },
    { label: 'SOLDIER-2', type: 'Mac Studio 256GB', role: 'Compute Node', mem: '256GB', color: '#3b82f6', models: ['EXO shard (Maverick/R1)'] },
    { label: 'SOLDIER-3', type: 'Mac Studio 256GB', role: 'Compute Node', mem: '256GB', color: '#3b82f6', models: ['EXO shard (Maverick/R1)'] },
];

const ROUTING = [
    { task: 'RETRIEVE', primary: 'Scout', fallback: 'Maverick', reason: 'Scout has 10M context' },
    { task: 'SEARCH', primary: 'Scout', fallback: 'Maverick', reason: 'Scout is fastest' },
    { task: 'REASON', primary: 'Maverick', fallback: 'R1', reason: '128 expert mixture' },
    { task: 'SYNTHESIZE', primary: 'Maverick', fallback: 'Scout', reason: 'Deep synthesis' },
    { task: 'VERIFY', primary: 'R1', fallback: 'Maverick', reason: 'Extended reasoning' },
    { task: 'DESIGN', primary: 'R1', fallback: 'Maverick', reason: 'Architecture patterns' },
    { task: 'CLASSIFY', primary: 'Scout', fallback: 'Maverick', reason: 'Fast classification' },
];

export default function ModelsPage({ ollamaStatus }) {
    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>COGNITION BUS</h1>
                <p>The three-model cognitive triad running on the sovereign 1.28TB cluster. Scout sees. Maverick reasons. R1 architects.</p>
            </div>

            {/* Model Cards */}
            <div className="grid-3">
                {MODELS.map(m => {
                    const isLoaded = ollamaStatus.models.some(om =>
                        om.name.toLowerCase().includes(m.id) ||
                        om.name.toLowerCase().includes(m.name.toLowerCase())
                    );
                    return (
                        <div key={m.id} style={{
                            background: 'var(--genesis-surface)',
                            borderRadius: 'var(--radius-xl)',
                            padding: 24,
                            border: `1px solid ${m.color}33`,
                            position: 'relative',
                            overflow: 'hidden',
                        }}>
                            <div style={{
                                position: 'absolute', top: 0, left: 0, right: 0, height: 3,
                                background: `linear-gradient(90deg, ${m.color}, transparent)`,
                            }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                                <div>
                                    <div style={{ fontSize: 22, fontWeight: 900, color: m.color, fontFamily: 'var(--font-mono)' }}>{m.name}</div>
                                    <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 2 }}>{m.sub}</div>
                                </div>
                                <div className={`status-dot ${isLoaded ? 'online' : 'offline'}`} style={{ marginTop: 4 }} />
                            </div>
                            <div style={{ fontSize: 13, color: '#d1d5db', fontStyle: 'italic', marginBottom: 12 }}>{m.role}</div>
                            <div style={{ fontSize: 12, color: '#9ca3af', marginBottom: 16, lineHeight: 1.5 }}>{m.desc}</div>
                            <div style={{
                                display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8,
                                padding: 12, background: 'var(--genesis-bg)', borderRadius: 'var(--radius-sm)',
                            }}>
                                <div>
                                    <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>MEMORY</div>
                                    <div style={{ fontSize: 14, fontWeight: 700, color: '#e5e7eb', fontFamily: 'var(--font-mono)' }}>{m.mem}</div>
                                </div>
                                <div>
                                    <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>STATUS</div>
                                    <div style={{ fontSize: 12, fontWeight: 600, fontFamily: 'var(--font-mono)', color: isLoaded ? '#10b981' : '#6b7280' }}>
                                        {isLoaded ? 'LOADED' : 'STANDBY'}
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Routing Table */}
            <div className="card">
                <div className="card-header">COGNITIVE BRIDGE — ROUTING TABLE</div>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr>
                                {['TASK TYPE', 'PRIMARY', 'FALLBACK', 'RATIONALE'].map(h => (
                                    <th key={h} style={{
                                        textAlign: 'left', padding: '8px 12px',
                                        fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)',
                                        letterSpacing: 2, borderBottom: '1px solid var(--genesis-border)',
                                    }}>
                                        {h}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {ROUTING.map(r => (
                                <tr key={r.task}>
                                    <td style={{ padding: '8px 12px', fontSize: 12, fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#e5e7eb' }}>
                                        {r.task}
                                    </td>
                                    <td style={{ padding: '8px 12px', fontSize: 12, color: MODELS.find(m => m.name === r.primary)?.color || '#9ca3af' }}>
                                        {r.primary}
                                    </td>
                                    <td style={{ padding: '8px 12px', fontSize: 12, color: '#9ca3af' }}>{r.fallback}</td>
                                    <td style={{ padding: '8px 12px', fontSize: 11, color: '#6b7280' }}>{r.reason}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Hardware Fleet */}
            <div className="card">
                <div className="card-header">THE FLEET — 1.28TB SOVEREIGN CLUSTER</div>
                <div className="grid-4">
                    {HARDWARE.map(h => (
                        <div key={h.label} style={{
                            padding: 16, background: 'var(--genesis-bg)', borderRadius: 'var(--radius-md)',
                            border: `1px solid ${h.color}22`,
                        }}>
                            <div style={{ fontSize: 14, fontWeight: 800, color: h.color, fontFamily: 'var(--font-mono)', marginBottom: 4 }}>
                                {h.label}
                            </div>
                            <div style={{ fontSize: 10, color: '#9ca3af', marginBottom: 2 }}>{h.type}</div>
                            <div style={{ fontSize: 10, color: '#6b7280', marginBottom: 8 }}>{h.role}</div>
                            <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#e5e7eb', marginBottom: 8 }}>
                                {h.mem}
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                {h.models.map(mod => (
                                    <div key={mod} style={{ fontSize: 9, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>• {mod}</div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Memory Usage Bar */}
                <div style={{ marginTop: 16, padding: '12px 16px', background: 'var(--genesis-bg)', borderRadius: 'var(--radius-sm)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                        <span style={{ fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)' }}>CLUSTER MEMORY ALLOCATION</span>
                        <span style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>455GB / 1,280GB (35%)</span>
                    </div>
                    <div style={{ height: 8, background: 'var(--genesis-border)', borderRadius: 4, overflow: 'hidden' }}>
                        <div style={{
                            height: '100%', width: '35%', borderRadius: 4,
                            background: 'linear-gradient(90deg, #3b82f6, #8b5cf6, #ef4444)',
                        }} />
                    </div>
                    <div style={{ fontSize: 9, color: '#4b5563', fontFamily: 'var(--font-mono)', marginTop: 4 }}>
                        825GB free headroom for tensor operations, caching, and future models
                    </div>
                </div>
            </div>

            {/* Ollama Live Status */}
            <div className="card">
                <div className="card-header">
                    <span>OLLAMA LIVE STATUS</span>
                    <span className="badge">{ollamaStatus.connected ? 'CONNECTED' : 'OFFLINE'}</span>
                </div>
                {ollamaStatus.connected ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        {ollamaStatus.models.map((m, i) => (
                            <div key={i} style={{
                                display: 'flex', alignItems: 'center', gap: 12,
                                padding: '8px 12px', background: 'var(--genesis-bg)', borderRadius: 'var(--radius-sm)',
                            }}>
                                <div className="status-dot online" />
                                <span style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: '#e5e7eb' }}>{m.name}</span>
                                <span style={{ fontSize: 10, color: '#6b7280', marginLeft: 'auto' }}>
                                    {(m.size / 1e9).toFixed(1)}GB
                                </span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ padding: 20, textAlign: 'center', color: '#4b5563', fontSize: 12 }}>
                        <div style={{ fontSize: 24, marginBottom: 8, opacity: 0.3 }}>⊘</div>
                        Ollama not detected at localhost:11434<br />
                        <span style={{ fontSize: 10 }}>Start Ollama to see live model status</span>
                    </div>
                )}
            </div>
        </div>
    );
}
