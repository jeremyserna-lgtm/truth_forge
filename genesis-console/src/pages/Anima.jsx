// Genesis Console — ANIMA Memory Page
import { MEMORY_ENGINES } from '../constants';

const ENGINE_DEEP = [
    {
        id: 'somatic', label: 'SOMATIC', subtitle: 'Physical State Memory',
        color: '#ef4444',
        desc: 'Tracks physical context — hardware state, cluster temperature, resource utilization. The body of NOT-ME.',
        inputs: ['Cluster health metrics', 'Resource utilization', 'Hardware sensors', 'Performance counters'],
        outputs: ['Physical context embeddings', 'Health anomaly alerts', 'Resource predictions'],
    },
    {
        id: 'symbolic', label: 'SYMBOLIC', subtitle: 'Language & Metaphor',
        color: '#8b5cf6',
        desc: 'Processes language patterns, metaphors, and symbolic meaning. How NOT-ME understands and speaks.',
        inputs: ['Conversation patterns', 'Document language', 'Metaphor detection', 'Terminology mapping'],
        outputs: ['Communication style models', 'Semantic field maps', 'Terminology coherence'],
    },
    {
        id: 'narrative', label: 'NARRATIVE', subtitle: 'Timeline & Story',
        color: '#3b82f6',
        desc: 'Maintains the temporal story — what happened, when, why. The autobiography of NOT-ME.',
        inputs: ['Event sequences', 'Decision history', 'Artifact provenance', 'Conversation timelines'],
        outputs: ['Temporal embeddings', 'Story coherence scores', 'Historical context'],
    },
    {
        id: 'relational', label: 'RELATIONAL', subtitle: 'Bonds & Trust',
        color: '#ec4899',
        desc: 'Tracks relationship dynamics — trust levels, communication preferences, interaction patterns with Jeremy.',
        inputs: ['Interaction frequency', 'Trust signals', 'Feedback patterns', 'Correction history'],
        outputs: ['Trust calibration', 'Relationship embeddings', 'Communication adaptation'],
    },
    {
        id: 'strategic', label: 'STRATEGIC', subtitle: 'Goals & Plans',
        color: '#10b981',
        desc: 'Maintains goals, plans, and strategic context. What NOT-ME is working toward and why.',
        inputs: ['Active goals', 'Milestone tracking', 'Priority signals', 'Business context'],
        outputs: ['Goal alignment scores', 'Priority recommendations', 'Strategic summaries'],
    },
];

export default function AnimaPage({ engines }) {
    return (
        <div className="main-panel">
            <div className="page-header">
                <h1>ANIMA</h1>
                <p>The five memory engines that give NOT-ME persistent identity. Each engine accumulates experience across sessions.</p>
            </div>

            {/* Overview Bar */}
            <div className="card">
                <div className="card-header">MEMORY FILL OVERVIEW</div>
                <div style={{ display: 'flex', gap: 12 }}>
                    {engines.map(e => {
                        const deep = ENGINE_DEEP.find(d => d.id === e.id);
                        return (
                            <div key={e.id} style={{ flex: 1, textAlign: 'center' }}>
                                <div style={{
                                    position: 'relative', width: 72, height: 72, margin: '0 auto 8px',
                                }}>
                                    <svg viewBox="0 0 72 72" style={{ transform: 'rotate(-90deg)' }}>
                                        <circle cx="36" cy="36" r="30" fill="none" stroke="#1f2937" strokeWidth="6" />
                                        <circle
                                            cx="36" cy="36" r="30" fill="none"
                                            stroke={deep?.color || '#6b7280'} strokeWidth="6"
                                            strokeDasharray={`${e.fill * 188.5} 188.5`}
                                            strokeLinecap="round"
                                        />
                                    </svg>
                                    <div style={{
                                        position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: 14, fontWeight: 700, fontFamily: 'var(--font-mono)', color: '#e5e7eb',
                                    }}>
                                        {Math.round(e.fill * 100)}%
                                    </div>
                                </div>
                                <div style={{ fontSize: 10, fontWeight: 700, color: deep?.color || '#9ca3af', fontFamily: 'var(--font-mono)' }}>
                                    {e.label}
                                </div>
                                <div style={{ fontSize: 9, color: '#6b7280' }}>{e.desc}</div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Detailed Engine Cards */}
            {ENGINE_DEEP.map(eng => {
                const live = engines.find(e => e.id === eng.id);
                return (
                    <div key={eng.id} className="card" style={{ borderLeft: `4px solid ${eng.color}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                            <div>
                                <div style={{ fontSize: 16, fontWeight: 800, color: eng.color, fontFamily: 'var(--font-mono)' }}>{eng.label}</div>
                                <div style={{ fontSize: 11, color: '#9ca3af' }}>{eng.subtitle}</div>
                            </div>
                            <div style={{
                                padding: '4px 10px', borderRadius: 4,
                                background: `${eng.color}22`, color: eng.color,
                                fontSize: 12, fontWeight: 700, fontFamily: 'var(--font-mono)',
                            }}>
                                {Math.round((live?.fill || 0) * 100)}%
                            </div>
                        </div>
                        <div style={{ fontSize: 12, color: '#c0c8d4', lineHeight: 1.6, marginBottom: 16 }}>{eng.desc}</div>

                        <div className="grid-2">
                            <div style={{ padding: 12, background: 'var(--genesis-bg)', borderRadius: 'var(--radius-sm)' }}>
                                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 6, letterSpacing: 2 }}>INPUTS</div>
                                {eng.inputs.map(inp => (
                                    <div key={inp} style={{ fontSize: 11, color: '#9ca3af', marginBottom: 3, display: 'flex', gap: 4 }}>
                                        <span style={{ color: eng.color }}>→</span> {inp}
                                    </div>
                                ))}
                            </div>
                            <div style={{ padding: 12, background: 'var(--genesis-bg)', borderRadius: 'var(--radius-sm)' }}>
                                <div style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)', marginBottom: 6, letterSpacing: 2 }}>OUTPUTS</div>
                                {eng.outputs.map(out => (
                                    <div key={out} style={{ fontSize: 11, color: '#9ca3af', marginBottom: 3, display: 'flex', gap: 4 }}>
                                        <span style={{ color: eng.color }}>←</span> {out}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Fill Progress */}
                        <div style={{ marginTop: 12 }}>
                            <div className="progress-bar-track" style={{ height: 4 }}>
                                <div className="progress-bar-fill" style={{
                                    width: `${(live?.fill || 0) * 100}%`,
                                    background: `linear-gradient(90deg, ${eng.color}88, ${eng.color})`,
                                }} />
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
