// Genesis Console — Knowledge Page (REAL — reads from persistent store)
import { useCallback, useEffect, useState } from 'react';
import { ATOM_TYPES } from '../constants';
import { AtomBadge } from '../components';
import { getJson } from '../api';

const ALL_TYPES = ['all', ...Object.keys(ATOM_TYPES)];

export default function KnowledgePage() {
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');
    const [selected, setSelected] = useState(null);
    const [allAtoms, setAllAtoms] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);

    const loadAtoms = useCallback(async () => {
        try {
            const data = await getJson('/api/atoms?limit=200');
            const mapped = (data.atoms || []).map(a => ({
                id: a.id,
                type: a.type,
                text: a.content,
                conf: a.confidence,
                ts: a._ts,
                entities: a.entities || [],
                themes: a.themes || [],
                source_intake_id: a.source_intake_id,
            }));
            setAllAtoms(mapped);
            setTotal(data.total || mapped.length);
        } catch {
            // Backend offline — keep whatever we had
        }
        setLoading(false);
    }, []);

    // Load atoms from backend on mount and every 10 seconds
    useEffect(() => {
        const initial = setTimeout(() => {
            void loadAtoms();
        }, 0);
        const interval = setInterval(loadAtoms, 10000);
        return () => {
            clearTimeout(initial);
            clearInterval(interval);
        };
    }, [loadAtoms]);

    const filtered = allAtoms.filter(a => {
        if (filter !== 'all' && a.type !== filter) return false;
        if (search && !a.text.toLowerCase().includes(search.toLowerCase())) return false;
        return true;
    });

    const typeCounts = {};
    allAtoms.forEach(a => { typeCounts[a.type] = (typeCounts[a.type] || 0) + 1; });

    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>KNOWLEDGE</h1>
                <p>Browse, filter, and explore extracted knowledge atoms. Every atom is an irreducible unit of meaning.</p>
            </div>

            {/* Stats Row */}
            <div className="grid-4">
                <div className="stat-card">
                    <span className="stat-label">TOTAL ATOMS</span>
                    <span className="stat-value" style={{ color: '#3b82f6' }}>{total}</span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">SIMPLE</span>
                    <span className="stat-value" style={{ color: '#10b981' }}>
                        {allAtoms.filter(a => ['fact', 'concept', 'relationship', 'directive', 'pattern'].includes(a.type)).length}
                    </span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">COMPOUND</span>
                    <span className="stat-value" style={{ color: '#ec4899' }}>
                        {allAtoms.filter(a => ['emergence', 'contradiction', 'amplification', 'meta_pattern', 'synthesis'].includes(a.type)).length}
                    </span>
                </div>
                <div className="stat-card">
                    <span className="stat-label">AVG CONFIDENCE</span>
                    <span className="stat-value" style={{ color: '#f59e0b' }}>
                        {allAtoms.length > 0 ? Math.round(allAtoms.reduce((s, a) => s + a.conf, 0) / allAtoms.length * 100) : 0}%
                    </span>
                </div>
            </div>

            {/* Search + Filters */}
            <div className="card">
                <input
                    type="text"
                    placeholder="Search atoms..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    title="Search atom text content"
                    style={{
                        width: '100%', padding: '10px 14px', marginBottom: 12,
                        background: 'var(--genesis-bg)', border: '1px solid var(--genesis-border)',
                        borderRadius: 'var(--radius-sm)', color: 'var(--genesis-text)',
                        fontFamily: 'var(--font-mono)', fontSize: 12, outline: 'none',
                    }}
                />
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                    {ALL_TYPES.map(t => {
                        const info = ATOM_TYPES[t];
                        const isActive = filter === t;
                        const count = t === 'all' ? allAtoms.length : (typeCounts[t] || 0);
                        return (
                            <button
                                key={t}
                                onClick={() => setFilter(t)}
                                title={`Filter atoms by ${info?.label || 'ALL'}`}
                                style={{
                                    padding: '4px 10px', borderRadius: 4, border: 'none', cursor: 'pointer',
                                    fontSize: 10, fontWeight: 600, fontFamily: 'var(--font-mono)', letterSpacing: 1,
                                    background: isActive ? (info?.color || '#3b82f6') + '33' : 'var(--genesis-border)',
                                    color: isActive ? (info?.color || '#3b82f6') : '#9ca3af',
                                    transition: 'all 0.15s ease',
                                }}
                            >
                                {(info?.label || 'ALL')} ({count})
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Atom List + Detail */}
            <div style={{ display: 'grid', gridTemplateColumns: selected !== null ? '1fr 1fr' : '1fr', gap: 'var(--gap-lg)' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    {loading && allAtoms.length === 0 && (
                        <div className="card" style={{ textAlign: 'center', padding: 40, color: '#4b5563' }}>
                            Loading atoms from storage...
                        </div>
                    )}
                    {!loading && allAtoms.length === 0 && (
                        <div className="card" style={{ textAlign: 'center', padding: 40, color: '#4b5563' }}>
                            <div style={{ fontSize: 32, marginBottom: 12, opacity: 0.2 }}>◇</div>
                            <div style={{ fontSize: 13, marginBottom: 4 }}>No atoms yet.</div>
                            <div style={{ fontSize: 11 }}>Drop files in the Pipeline to extract knowledge atoms.</div>
                        </div>
                    )}
                    {filtered.length === 0 && allAtoms.length > 0 && (
                        <div className="card" style={{ textAlign: 'center', padding: 40, color: '#4b5563' }}>
                            No atoms match your filter.
                        </div>
                    )}
                    {filtered.map((atom, i) => {
                        const info = ATOM_TYPES[atom.type] || {};
                        const isSelected = selected === i;
                        return (
                            <div
                                key={atom.id || i}
                                onClick={() => setSelected(isSelected ? null : i)}
                                className="animate-fade-in"
                                title={isSelected ? 'Collapse atom detail' : 'Open atom detail panel'}
                                style={{
                                    padding: '12px 16px', cursor: 'pointer',
                                    background: isSelected ? 'var(--genesis-surface-2)' : 'var(--genesis-surface)',
                                    borderRadius: 'var(--radius-md)',
                                    border: `1px solid ${isSelected ? (info.color || '#374151') + '55' : 'var(--genesis-border)'}`,
                                    borderLeft: `4px solid ${info.color || '#6b7280'}`,
                                    transition: 'all 0.15s ease',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                    <AtomBadge type={atom.type} />
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{
                                            width: 40, height: 4, background: 'var(--genesis-border)', borderRadius: 2, overflow: 'hidden',
                                        }}>
                                            <div style={{
                                                height: '100%', width: `${atom.conf * 100}%`, borderRadius: 2,
                                                background: atom.conf > 0.9 ? '#10b981' : atom.conf > 0.8 ? '#f59e0b' : '#ef4444',
                                            }} />
                                        </div>
                                        <span style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                                            {Math.round(atom.conf * 100)}%
                                        </span>
                                    </div>
                                </div>
                                <div style={{ fontSize: 12, color: '#d1d5db', lineHeight: 1.5 }}>{atom.text}</div>
                                {atom.entities?.length > 0 && (
                                    <div style={{ marginTop: 4, display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                                        {atom.entities.map(e => (
                                            <span key={e} style={{
                                                fontSize: 9, padding: '1px 5px', borderRadius: 3,
                                                background: 'rgba(59,130,246,0.1)', color: '#60a5fa',
                                                fontFamily: 'var(--font-mono)',
                                            }}>{e}</span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Detail Panel */}
                {selected !== null && filtered[selected] && (
                    <div className="card animate-slide-in-right" style={{ position: 'sticky', top: 20, alignSelf: 'start' }}>
                        <div className="card-header">ATOM DETAIL</div>
                        <div style={{ marginBottom: 16 }}>
                            <AtomBadge type={filtered[selected].type} />
                        </div>
                        <div style={{ fontSize: 14, color: '#e5e7eb', lineHeight: 1.6, marginBottom: 20 }}>
                            {filtered[selected].text}
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                            <div>
                                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 4 }}>CONFIDENCE</div>
                                <div style={{ fontSize: 18, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#10b981' }}>
                                    {Math.round(filtered[selected].conf * 100)}%
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 4 }}>TYPE CLASS</div>
                                <div style={{ fontSize: 12, fontWeight: 600, fontFamily: 'var(--font-mono)', color: '#d1d5db' }}>
                                    {['emergence', 'contradiction', 'amplification', 'meta_pattern', 'synthesis'].includes(filtered[selected].type) ? 'COMPOUND' : 'SIMPLE'}
                                </div>
                            </div>
                        </div>
                        {/* Entities */}
                        {filtered[selected].entities?.length > 0 && (
                            <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--genesis-border)' }}>
                                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 6 }}>ENTITIES</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                                    {filtered[selected].entities.map(e => (
                                        <span key={e} style={{
                                            fontSize: 10, padding: '2px 8px', borderRadius: 4,
                                            background: 'rgba(59,130,246,0.15)', color: '#60a5fa',
                                            fontFamily: 'var(--font-mono)',
                                        }}>{e}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {/* Themes */}
                        {filtered[selected].themes?.length > 0 && (
                            <div style={{ marginTop: 12 }}>
                                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 6 }}>THEMES</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                                    {filtered[selected].themes.map(t => (
                                        <span key={t} style={{
                                            fontSize: 10, padding: '2px 8px', borderRadius: 4,
                                            background: 'rgba(139,92,246,0.15)', color: '#a78bfa',
                                            fontFamily: 'var(--font-mono)',
                                        }}>{t}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                        <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid var(--genesis-border)' }}>
                            <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 6 }}>PROVENANCE</div>
                            <div style={{ fontSize: 10, color: '#9ca3af', fontFamily: 'var(--font-mono)', lineHeight: 1.6 }}>
                                Intake: {filtered[selected].source_intake_id?.slice(0, 8) || 'N/A'}<br />
                                Stored: {filtered[selected].ts ? new Date(filtered[selected].ts).toLocaleString() : 'N/A'}<br />
                                Pipeline: INTAKE → ATOMIZE → HOLD₂
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
