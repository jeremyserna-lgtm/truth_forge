// Genesis Console — Watcher Page (Passive Atomization Monitor)
import { useState, useEffect, useCallback } from 'react';
import { Eye, EyeOff, RefreshCw, Play, Square, FileText, Zap } from 'lucide-react';

export default function WatcherPage() {
    const [status, setStatus] = useState(null);
    const [index, setIndex] = useState({ total: 0, entries: [] });
    const [loading, setLoading] = useState(true);

    const fetchStatus = useCallback(async () => {
        try {
            const res = await fetch('/api/watcher/status');
            if (res.ok) setStatus(await res.json());
        } catch { /* offline */ }
    }, []);

    const fetchIndex = useCallback(async () => {
        try {
            const res = await fetch('/api/watcher/index?limit=50');
            if (res.ok) setIndex(await res.json());
        } catch { /* offline */ }
        setLoading(false);
    }, []);

    useEffect(() => {
        fetchStatus();
        fetchIndex();
        const interval = setInterval(() => {
            fetchStatus();
            fetchIndex();
        }, 5000);
        return () => clearInterval(interval);
    }, [fetchStatus, fetchIndex]);

    const startWatcher = async () => {
        await fetch('/api/watcher/start', { method: 'POST' });
        await fetchStatus();
    };

    const stopWatcher = async () => {
        await fetch('/api/watcher/stop', { method: 'POST' });
        await fetchStatus();
    };

    const triggerSweep = async () => {
        await fetch('/api/watcher/sweep', { method: 'POST' });
        await fetchStatus();
    };

    const formatTime = (ms) => {
        if (!ms) return '—';
        const s = Math.floor(ms / 1000);
        const m = Math.floor(s / 60);
        const h = Math.floor(m / 60);
        if (h > 0) return `${h}h ${m % 60}m`;
        if (m > 0) return `${m}m ${s % 60}s`;
        return `${s}s`;
    };

    const formatDate = (ts) => {
        if (!ts) return '—';
        return new Date(ts).toLocaleString('en-US', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false,
        });
    };

    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>PASSIVE ATOMIZATION</h1>
                <p>
                    Autonomous file watcher monitoring the entire truth_forge/ directory.
                    Every file change produces knowledge atoms without direction.
                </p>
            </div>

            {/* Status Banner */}
            <div style={{
                background: status?.active
                    ? 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(59,130,246,0.05) 100%)'
                    : 'linear-gradient(135deg, rgba(107,114,128,0.08) 0%, rgba(107,114,128,0.05) 100%)',
                borderRadius: 'var(--radius-xl)',
                padding: '24px 32px',
                border: `1px solid ${status?.active ? 'rgba(16,185,129,0.2)' : 'rgba(107,114,128,0.2)'}`,
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{
                        width: 48, height: 48, borderRadius: 12,
                        background: status?.active ? 'rgba(16,185,129,0.15)' : 'rgba(107,114,128,0.15)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                    }}>
                        {status?.active
                            ? <Eye size={24} color="#10b981" style={{ animation: 'breathe 2s ease-in-out infinite' }} />
                            : <EyeOff size={24} color="#6b7280" />}
                    </div>
                    <div>
                        <div style={{
                            fontSize: 18, fontWeight: 800, fontFamily: 'var(--font-mono)',
                            color: status?.active ? '#10b981' : '#6b7280', letterSpacing: 2,
                        }}>
                            {status?.active ? 'WATCHING' : 'IDLE'}
                        </div>
                        <div style={{ fontSize: 11, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            {status?.root || '—'}
                        </div>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: 8 }}>
                    {status?.active ? (
                        <button onClick={stopWatcher} style={{
                            padding: '8px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                            background: 'rgba(239,68,68,0.1)', color: '#ef4444',
                            fontSize: 11, fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: 1,
                            display: 'flex', alignItems: 'center', gap: 6,
                        }}>
                            <Square size={12} /> STOP
                        </button>
                    ) : (
                        <button onClick={startWatcher} style={{
                            padding: '8px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                            background: 'rgba(16,185,129,0.1)', color: '#10b981',
                            fontSize: 11, fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: 1,
                            display: 'flex', alignItems: 'center', gap: 6,
                        }}>
                            <Play size={12} /> START
                        </button>
                    )}
                    <button onClick={triggerSweep} style={{
                        padding: '8px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
                        background: 'rgba(139,92,246,0.1)', color: '#8b5cf6',
                        fontSize: 11, fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: 1,
                        display: 'flex', alignItems: 'center', gap: 6,
                    }}>
                        <RefreshCw size={12} /> FULL SWEEP
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid-4" style={{ marginTop: 'var(--gap-lg)' }}>
                <div className="stat-card">
                    <span className="stat-label">FILES PROCESSED</span>
                    <span className="stat-value" style={{ color: '#3b82f6' }}>
                        {status?.processed || 0}
                    </span>
                    <span className="stat-sub">since watcher started</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">ATOMS EXTRACTED</span>
                    <span className="stat-value" style={{ color: '#10b981' }}>
                        {status?.totalAtoms || 0}
                    </span>
                    <span className="stat-sub">from passive watching</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">QUEUE DEPTH</span>
                    <span className="stat-value" style={{ color: '#f59e0b' }}>
                        {status?.queueSize || 0}
                    </span>
                    <span className="stat-sub">files pending</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">INDEX SIZE</span>
                    <span className="stat-value" style={{ color: '#8b5cf6' }}>
                        {status?.indexSize || 0}
                    </span>
                    <span className="stat-sub">files tracked</span>
                </div>
            </div>

            {/* Current Processing + Errors */}
            <div className="grid-2" style={{ marginTop: 'var(--gap-lg)' }}>
                <div className="card">
                    <div className="card-header">CURRENT ACTIVITY</div>
                    {status?.currentFile ? (
                        <div style={{
                            padding: '12px 16px', borderRadius: 8,
                            background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.15)',
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                                <Zap size={12} color="#3b82f6" style={{ animation: 'breathe 1s ease-in-out infinite' }} />
                                <span style={{ fontSize: 10, color: '#3b82f6', fontFamily: 'var(--font-mono)', letterSpacing: 1 }}>
                                    ATOMIZING
                                </span>
                            </div>
                            <div style={{ fontSize: 12, color: '#d1d5db', fontFamily: 'var(--font-mono)', wordBreak: 'break-all' }}>
                                {status.currentFile}
                            </div>
                        </div>
                    ) : (
                        <div style={{ padding: 20, textAlign: 'center', color: '#4b5563', fontSize: 11 }}>
                            {status?.active ? 'Waiting for file changes...' : 'Watcher is not active'}
                        </div>
                    )}
                    <div style={{ marginTop: 12, display: 'flex', gap: 16 }}>
                        <div style={{ fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            Uptime: {formatTime(status?.uptime || 0)}
                        </div>
                        <div style={{ fontSize: 10, color: status?.errors > 0 ? '#ef4444' : '#6b7280', fontFamily: 'var(--font-mono)' }}>
                            Errors: {status?.errors || 0}
                        </div>
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">HOW IT WORKS</div>
                    <div style={{ fontSize: 11, color: '#9ca3af', lineHeight: 1.8, fontFamily: 'var(--font-mono)' }}>
                        <div style={{ marginBottom: 8 }}>
                            <span style={{ color: '#10b981' }}>①</span> Watcher monitors <span style={{ color: '#e5e7eb' }}>truth_forge/</span> for file changes
                        </div>
                        <div style={{ marginBottom: 8 }}>
                            <span style={{ color: '#3b82f6' }}>②</span> Changed files are queued by priority <span style={{ color: '#e5e7eb' }}>(P0→P4)</span>
                        </div>
                        <div style={{ marginBottom: 8 }}>
                            <span style={{ color: '#8b5cf6' }}>③</span> SHA-256 dedup skips unchanged files
                        </div>
                        <div style={{ marginBottom: 8 }}>
                            <span style={{ color: '#f59e0b' }}>④</span> Scout extracts atoms via <span style={{ color: '#e5e7eb' }}>HOLD₁ → AGENT → HOLD₂</span>
                        </div>
                        <div>
                            <span style={{ color: '#ec4899' }}>⑤</span> Atoms stored to <span style={{ color: '#e5e7eb' }}>data/atoms.jsonl</span> — permanent
                        </div>
                    </div>
                </div>
            </div>

            {/* Recently Processed Files */}
            <div className="card" style={{ marginTop: 'var(--gap-lg)' }}>
                <div className="card-header">
                    <span>RECENTLY PROCESSED</span>
                    <span className="badge">{index.total} total</span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 400, overflow: 'auto' }}>
                    {loading && index.entries.length === 0 && (
                        <div style={{ padding: 20, textAlign: 'center', color: '#4b5563', fontSize: 11 }}>
                            Loading index...
                        </div>
                    )}
                    {!loading && index.entries.length === 0 && (
                        <div style={{ padding: 20, textAlign: 'center', color: '#4b5563', fontSize: 11 }}>
                            <div style={{ fontSize: 28, marginBottom: 8, opacity: 0.15 }}>◇</div>
                            No files processed yet. Start the watcher or ensure Ollama is running.
                        </div>
                    )}
                    {index.entries.map((entry, i) => (
                        <div key={entry.filepath || i} style={{
                            display: 'flex', alignItems: 'center', gap: 12,
                            padding: '8px 12px', borderRadius: 6,
                            background: i % 2 === 0 ? 'var(--genesis-bg)' : 'transparent',
                        }}>
                            <FileText size={14} color="#6b7280" style={{ flexShrink: 0 }} />
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{
                                    fontSize: 11, color: '#d1d5db', fontFamily: 'var(--font-mono)',
                                    whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                                }}>
                                    {entry.filepath?.replace(/.*truth_forge\//, '')}
                                </div>
                            </div>
                            <div style={{
                                fontSize: 9, fontWeight: 700, fontFamily: 'var(--font-mono)',
                                color: '#10b981', background: 'rgba(16,185,129,0.1)',
                                padding: '2px 6px', borderRadius: 3,
                            }}>
                                {entry.atom_count || 0} atoms
                            </div>
                            <div style={{
                                fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)',
                                whiteSpace: 'nowrap',
                            }}>
                                {formatDate(entry.last_processed)}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
