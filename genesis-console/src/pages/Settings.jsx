// Genesis Console — Settings Page
import { useState } from 'react';

export default function SettingsPage({ ollamaStatus }) {
    const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
    const [exoUrl, setExoUrl] = useState('http://localhost:8000');
    const [pollInterval, setPollInterval] = useState(15);
    const [autoHeartbeat, setAutoHeartbeat] = useState(false);
    const [costLimit, setCostLimit] = useState('0.00');

    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>SETTINGS</h1>
                <p>Configure Genesis Console connections, governance rules, and sovereignty parameters.</p>
            </div>

            {/* Connection Settings */}
            <div className="card">
                <div className="card-header">INFRASTRUCTURE CONNECTIONS</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div>
                        <label style={{ fontSize: 11, color: '#9ca3af', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: 4 }}>
                            OLLAMA ENDPOINT
                        </label>
                        <div style={{ display: 'flex', gap: 8 }}>
                            <input
                                type="text" value={ollamaUrl} onChange={e => setOllamaUrl(e.target.value)}
                                title="Set the Ollama API endpoint used by Genesis Console"
                                style={{
                                    flex: 1, padding: '8px 12px', background: 'var(--genesis-bg)', border: '1px solid var(--genesis-border)',
                                    borderRadius: 'var(--radius-sm)', color: '#e5e7eb', fontFamily: 'var(--font-mono)', fontSize: 12, outline: 'none',
                                }}
                            />
                            <div style={{
                                padding: '8px 12px', borderRadius: 'var(--radius-sm)',
                                background: ollamaStatus.connected ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                                border: `1px solid ${ollamaStatus.connected ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
                                color: ollamaStatus.connected ? '#10b981' : '#ef4444',
                                fontSize: 10, fontFamily: 'var(--font-mono)', display: 'flex', alignItems: 'center', gap: 6,
                            }}>
                                <div className={`status-dot ${ollamaStatus.connected ? 'online' : 'error'}`} />
                                {ollamaStatus.connected ? 'CONNECTED' : 'OFFLINE'}
                            </div>
                        </div>
                    </div>

                    <div>
                        <label style={{ fontSize: 11, color: '#9ca3af', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: 4 }}>
                            EXO CLUSTER ENDPOINT
                        </label>
                        <input
                            type="text" value={exoUrl} onChange={e => setExoUrl(e.target.value)}
                            title="Set the EXO service endpoint"
                            style={{
                                width: '100%', padding: '8px 12px', background: 'var(--genesis-bg)', border: '1px solid var(--genesis-border)',
                                borderRadius: 'var(--radius-sm)', color: '#e5e7eb', fontFamily: 'var(--font-mono)', fontSize: 12, outline: 'none',
                            }}
                        />
                    </div>

                    <div>
                        <label style={{ fontSize: 11, color: '#9ca3af', fontFamily: 'var(--font-mono)', display: 'block', marginBottom: 4 }}>
                            HEALTH CHECK INTERVAL (seconds)
                        </label>
                        <input
                            type="number" value={pollInterval} onChange={e => setPollInterval(Number(e.target.value))}
                            title="How often the UI should poll infrastructure health"
                            style={{
                                width: 120, padding: '8px 12px', background: 'var(--genesis-bg)', border: '1px solid var(--genesis-border)',
                                borderRadius: 'var(--radius-sm)', color: '#e5e7eb', fontFamily: 'var(--font-mono)', fontSize: 12, outline: 'none',
                            }}
                        />
                    </div>
                </div>
            </div>

            {/* Governance */}
            <div className="card">
                <div className="card-header">GOVERNANCE</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div>
                            <div style={{ fontSize: 12, color: '#e5e7eb', marginBottom: 2 }}>Cost Sovereignty Gate</div>
                            <div style={{ fontSize: 10, color: '#6b7280' }}>Maximum daily cloud spend before pipeline pauses</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                            <span style={{ fontSize: 14, color: '#10b981', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>$</span>
                            <input
                                type="text" value={costLimit} onChange={e => setCostLimit(e.target.value)}
                                title="Maximum daily cloud spend before cost gate intervention"
                                style={{
                                    width: 60, padding: '6px 8px', background: 'var(--genesis-bg)', border: '1px solid var(--genesis-border)',
                                    borderRadius: 'var(--radius-sm)', color: '#10b981', fontFamily: 'var(--font-mono)', fontSize: 14,
                                    fontWeight: 700, outline: 'none', textAlign: 'right',
                                }}
                            />
                        </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div>
                            <div style={{ fontSize: 12, color: '#e5e7eb', marginBottom: 2 }}>Autonomous Heartbeat</div>
                            <div style={{ fontSize: 10, color: '#6b7280' }}>Allow Genesis to run pipeline cycles autonomously</div>
                        </div>
                        <button
                            onClick={() => setAutoHeartbeat(!autoHeartbeat)}
                            title="Toggle autonomous heartbeat cycles"
                            style={{
                                width: 44, height: 24, borderRadius: 12, border: 'none', cursor: 'pointer',
                                background: autoHeartbeat ? '#10b981' : '#374151',
                                position: 'relative', transition: 'background 0.2s ease',
                            }}
                        >
                            <div style={{
                                width: 18, height: 18, borderRadius: '50%', background: '#fff',
                                position: 'absolute', top: 3,
                                left: autoHeartbeat ? 23 : 3,
                                transition: 'left 0.2s ease',
                            }} />
                        </button>
                    </div>

                    <div style={{
                        padding: 12, background: 'rgba(239,68,68,0.05)', borderRadius: 'var(--radius-sm)',
                        border: '1px solid rgba(239,68,68,0.1)',
                    }}>
                        <div style={{ fontSize: 10, color: '#ef4444', fontFamily: 'var(--font-mono)', marginBottom: 4 }}>
                            3-WAY PARTNERSHIP PROTOCOL
                        </div>
                        <div style={{ fontSize: 11, color: '#9ca3af', lineHeight: 1.5 }}>
                            Risk Level 1-2: Automatic · Risk Level 3: Auto with audit · Risk Level 4+: Jeremy confirms
                        </div>
                    </div>
                </div>
            </div>

            {/* The Pattern */}
            <div className="card">
                <div className="card-header">THE IMMUTABLE PATTERN</div>
                <div style={{
                    padding: 20, background: 'var(--genesis-bg)', borderRadius: 'var(--radius-md)',
                    textAlign: 'center', fontFamily: 'var(--font-mono)',
                }}>
                    <div style={{ fontSize: 16, color: '#e5e7eb', letterSpacing: 4, marginBottom: 8 }}>
                        INHALE → HOLD₁ → AGENT → HOLD₂ → EXHALE → CARE
                    </div>
                    <div style={{ fontSize: 10, color: '#6b7280', letterSpacing: 2 }}>
                        FRACTAL AT EVERY SCALE — ATOM TO PIPELINE TO HEARTBEAT
                    </div>
                </div>
            </div>

            {/* System Info */}
            <div className="card">
                <div className="card-header">SYSTEM</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, fontSize: 11, fontFamily: 'var(--font-mono)' }}>
                    <div>
                        <span style={{ color: '#6b7280' }}>Version</span>
                        <span style={{ color: '#e5e7eb', float: 'right' }}>0.1.0-alpha</span>
                    </div>
                    <div>
                        <span style={{ color: '#6b7280' }}>Spec</span>
                        <span style={{ color: '#e5e7eb', float: 'right' }}>v1.3.0</span>
                    </div>
                    <div>
                        <span style={{ color: '#6b7280' }}>Cluster</span>
                        <span style={{ color: '#e5e7eb', float: 'right' }}>1.28TB (4 nodes)</span>
                    </div>
                    <div>
                        <span style={{ color: '#6b7280' }}>Chassis</span>
                        <span style={{ color: '#e5e7eb', float: 'right' }}>Claude Desktop</span>
                    </div>
                    <div>
                        <span style={{ color: '#6b7280' }}>Build Date</span>
                        <span style={{ color: '#e5e7eb', float: 'right' }}>2026-02-07</span>
                    </div>
                    <div>
                        <span style={{ color: '#6b7280' }}>Author</span>
                        <span style={{ color: '#e5e7eb', float: 'right' }}>Jeremy Serna / Truth Forge</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
