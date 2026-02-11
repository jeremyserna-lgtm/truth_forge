// Genesis Console — Shared UI Components
import { useState, useEffect, useRef, useCallback } from 'react';
import { ATOM_TYPES, getFileInfo, PIPELINE_STAGES, MODELS } from './constants';

// ═══════════════════════════════════════
// HEARTBEAT — The system's pulse
// ═══════════════════════════════════════
export function Heartbeat({ active, label = true }) {
    const [pulse, setPulse] = useState(false);

    useEffect(() => {
        if (!active) return;
        const interval = setInterval(() => {
            setPulse(true);
            setTimeout(() => setPulse(false), 600);
        }, 2000);
        return () => clearInterval(interval);
    }, [active]);

    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
                width: 14, height: 14, borderRadius: '50%',
                background: active ? (pulse ? '#10b981' : '#065f46') : '#374151',
                boxShadow: active && pulse ? '0 0 12px #10b981, 0 0 24px rgba(16,185,129,0.3)' : 'none',
                transition: 'all 0.3s ease',
            }} />
            {label && (
                <span style={{
                    fontSize: 11,
                    color: active ? '#10b981' : '#6b7280',
                    fontFamily: 'var(--font-mono)',
                    letterSpacing: 2,
                }}>
                    {active ? 'HEARTBEAT ACTIVE' : 'HEARTBEAT IDLE'}
                </span>
            )}
        </div>
    );
}

// ═══════════════════════════════════════
// PIPELINE STAGE — Visual pipeline node
// ═══════════════════════════════════════
export function PipelineStage({ stage, isComplete, isCurrent }) {
    return (
        <div className={`pipeline-stage ${!isComplete && !isCurrent ? 'dimmed' : ''}`}>
            <div
                className={`pipeline-node ${isCurrent ? 'active' : ''} ${isComplete ? 'complete' : ''}`}
                style={{ '--stage-color': stage.color }}
            >
                {isCurrent && (
                    <div style={{
                        position: 'absolute', inset: 0,
                        background: `linear-gradient(180deg, transparent 0%, ${stage.color}22 50%, transparent 100%)`,
                        animation: 'scan 1.5s ease-in-out infinite',
                    }} />
                )}
                <span style={{
                    fontSize: 11, fontWeight: 700,
                    color: isComplete || isCurrent ? '#fff' : '#6b7280',
                    fontFamily: 'var(--font-mono)',
                    position: 'relative', zIndex: 1,
                }}>
                    {isComplete ? '✓' : stage.label.charAt(0)}
                </span>
            </div>
            <span style={{
                fontSize: 10, fontWeight: 600,
                color: isCurrent ? stage.color : isComplete ? '#d1d5db' : '#6b7280',
                fontFamily: 'var(--font-mono)',
            }}>
                {stage.label}
            </span>
            <span style={{ fontSize: 9, color: '#6b7280' }}>{stage.desc}</span>
        </div>
    );
}

// ═══════════════════════════════════════
// PIPELINE VISUALIZATION — Full pipeline bar
// ═══════════════════════════════════════
export function PipelineVisualization({ currentStage, completedStages }) {
    return (
        <div className="card">
            <div className="card-header">PIPELINE</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 4 }}>
                {PIPELINE_STAGES.map((stage, i) => (
                    <div key={stage.id} style={{ display: 'flex', alignItems: 'center' }}>
                        <PipelineStage
                            stage={stage}
                            isComplete={completedStages.has(i)}
                            isCurrent={currentStage === i}
                        />
                        {i < PIPELINE_STAGES.length - 1 && (
                            <div
                                className={`pipeline-connector ${completedStages.has(i) ? 'complete' : ''}`}
                                style={{ '--stage-color': stage.color }}
                            />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════
// MODEL CARD — Shows model status
// ═══════════════════════════════════════
export function ModelCard({ model, isActive, ollamaModels = [] }) {
    const [glow, setGlow] = useState(false);

    // Check if this model is actually loaded in Ollama
    const isLoaded = ollamaModels.some(m =>
        m.name.toLowerCase().includes(model.id) ||
        m.name.toLowerCase().includes(model.name.toLowerCase())
    );

    useEffect(() => {
        if (!isActive) return;
        const interval = setInterval(() => {
            setGlow(true);
            setTimeout(() => setGlow(false), 800);
        }, 1500 + Math.random() * 1000);
        return () => clearInterval(interval);
    }, [isActive]);

    return (
        <div
            className={`model-card ${isActive ? 'active' : ''} ${isActive && glow ? 'glowing' : ''}`}
            style={{ '--model-color': model.color }}
        >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                <div>
                    <div style={{ fontSize: 14, fontWeight: 700, color: model.color, fontFamily: 'var(--font-mono)' }}>
                        {model.name}
                    </div>
                    <div style={{ fontSize: 10, color: '#9ca3af', marginTop: 2 }}>{model.sub}</div>
                </div>
                <div className={`status-dot ${isActive ? 'online' : isLoaded ? 'online' : 'offline'}`} />
            </div>
            <div style={{ fontSize: 11, color: '#d1d5db', fontStyle: 'italic', marginBottom: 6 }}>{model.role}</div>
            <div style={{ fontSize: 10, color: '#6b7280' }}>{model.desc}</div>
            <div style={{
                fontSize: 9, color: '#4b5563', marginTop: 8, fontFamily: 'var(--font-mono)',
                display: 'flex', justifyContent: 'space-between',
            }}>
                <span>{model.mem} allocated</span>
                {isLoaded && <span style={{ color: '#10b981' }}>LOADED</span>}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════
// COGNITION BUS — All three models
// ═══════════════════════════════════════
export function CognitionBus({ activeModels, ollamaModels }) {
    return (
        <div>
            <div style={{
                fontSize: 10, color: '#6b7280', fontFamily: 'var(--font-mono)',
                marginBottom: 8, letterSpacing: 2, paddingLeft: 4,
            }}>
                COGNITION BUS
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
                {MODELS.map(m => (
                    <ModelCard
                        key={m.id}
                        model={m}
                        isActive={activeModels.has(m.id)}
                        ollamaModels={ollamaModels}
                    />
                ))}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════
// ATOM BADGE — Type indicator pill
// ═══════════════════════════════════════
export function AtomBadge({ type }) {
    const info = ATOM_TYPES[type] || { color: '#6b7280', label: type?.toUpperCase() || 'UNKNOWN' };
    return (
        <span className="atom-badge" style={{
            background: info.color + '22',
            color: info.color,
        }}>
            {info.label}
        </span>
    );
}

// ═══════════════════════════════════════
// KNOWLEDGE STREAM — Live atom feed
// ═══════════════════════════════════════
export function KnowledgeStream({ atoms }) {
    const streamRef = useRef(null);

    useEffect(() => {
        if (streamRef.current) streamRef.current.scrollTop = 0;
    }, [atoms]);

    return (
        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 300 }}>
            <div className="card-header">
                <span>KNOWLEDGE STREAM</span>
                <span className="badge">{atoms.length} atoms</span>
            </div>
            <div ref={streamRef} style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column', gap: 6 }}>
                {atoms.length === 0 ? (
                    <div style={{
                        flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: 8,
                    }}>
                        <div style={{ fontSize: 32, opacity: 0.15 }}>◇</div>
                        <div style={{ fontSize: 11, color: '#4b5563' }}>Waiting for atoms...</div>
                    </div>
                ) : (
                    atoms.map(atom => (
                        <div key={atom.id} className="animate-fade-in" style={{
                            padding: '10px 12px',
                            background: '#0a0f1a',
                            borderRadius: 8,
                            borderLeft: `3px solid ${(ATOM_TYPES[atom.type] || {}).color || '#6b7280'}`,
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                                <AtomBadge type={atom.type} />
                                <span style={{ fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                                    {Math.round(atom.conf * 100)}% · {atom.ts}
                                </span>
                            </div>
                            <div style={{ fontSize: 12, color: '#d1d5db', lineHeight: 1.5 }}>{atom.text}</div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════
// ANIMA MEMORY — Five engine bars
// ═══════════════════════════════════════
export function AnimaMemory({ engines }) {
    return (
        <div className="card">
            <div className="card-header">ANIMA MEMORY</div>
            {engines.map(e => (
                <div key={e.id} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <div style={{
                        width: 70, fontSize: 9, color: '#9ca3af',
                        fontFamily: 'var(--font-mono)', textAlign: 'right',
                    }}>
                        {e.label}
                    </div>
                    <div className="progress-bar-track">
                        <div className="progress-bar-fill" style={{ width: `${e.fill * 100}%` }} />
                    </div>
                    <div style={{ width: 30, fontSize: 9, color: '#6b7280', fontFamily: 'var(--font-mono)' }}>
                        {Math.round(e.fill * 100)}%
                    </div>
                </div>
            ))}
        </div>
    );
}

// ═══════════════════════════════════════
// SYSTEM LOG — Event log panel
// ═══════════════════════════════════════
export function SystemLog({ log }) {
    const logRef = useRef(null);

    useEffect(() => {
        if (logRef.current) {
            logRef.current.scrollTop = logRef.current.scrollHeight;
        }
    }, [log]);

    const getLevelColor = (level) => {
        switch (level) {
            case 'success': return '#10b981';
            case 'warn': return '#f59e0b';
            case 'error': return '#ef4444';
            default: return '#9ca3af';
        }
    };

    return (
        <div className="card" style={{ maxHeight: 220 }}>
            <div className="card-header">SYSTEM LOG</div>
            <div ref={logRef} style={{ maxHeight: 160, overflow: 'auto' }}>
                {log.length === 0 ? (
                    <div style={{ color: '#4b5563', fontFamily: 'var(--font-mono)', fontSize: 10 }}>Ready.</div>
                ) : (
                    log.slice().reverse().map(entry => (
                        <div key={entry.id} className="log-entry">
                            <span className="timestamp">{entry.ts}</span>
                            <span style={{ color: getLevelColor(entry.level) }}>{entry.msg}</span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════
// SOVEREIGNTY STATUS — Grid of system facts
// ═══════════════════════════════════════
export function SovereigntyStatus({ items }) {
    return (
        <div className="card">
            <div className="card-header">SOVEREIGNTY</div>
            <div className="sovereignty-grid">
                {items.map(item => (
                    <div key={item.label} className="sovereignty-item">
                        <div className="label">{item.label}</div>
                        <div className={`value ${item.status ? 'ok' : ''}`}>
                            {item.value}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

// ═══════════════════════════════════════
// FILE CHIP — Ingested file display
// ═══════════════════════════════════════
export function FileChip({ file, onRemove }) {
    const info = getFileInfo(file.name);
    return (
        <div className="file-chip" style={{ border: `1px solid ${info.color}33` }}>
            <span style={{ fontSize: 18, color: info.color }}>{info.icon}</span>
            <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                    fontSize: 12, color: '#e5e7eb', fontFamily: 'var(--font-mono)',
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                }}>
                    {file.name}
                </div>
                <div style={{ fontSize: 9, color: info.color, fontFamily: 'var(--font-mono)' }}>
                    {info.type} · {(file.size / 1024).toFixed(1)}KB
                </div>
            </div>
            <button className="remove-btn" onClick={onRemove} title={`Remove ${file.name}`}>✕</button>
        </div>
    );
}

// ═══════════════════════════════════════
// DROP ZONE — Universal file intake
// ═══════════════════════════════════════
export function DropZone({ files, onFilesChange, onRemoveFile }) {
    const [dragOver, setDragOver] = useState(false);
    const fileInputRef = useRef(null);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        const dropped = Array.from(e.dataTransfer.files);
        onFilesChange(prev => [...prev, ...dropped]);
    }, [onFilesChange]);

    const handleFileSelect = useCallback((e) => {
        const selected = Array.from(e.target.files || []);
        onFilesChange(prev => [...prev, ...selected]);
    }, [onFilesChange]);

    return (
        <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`drop-zone ${dragOver ? 'drag-over' : ''} ${files.length > 0 ? 'has-files' : ''}`}
            title="Drop files here or click to browse local files"
        >
            <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                style={{ display: 'none' }}
                title="Select one or more files to process"
            />
            {files.length === 0 ? (
                <>
                    <div style={{ fontSize: 28, marginBottom: 8, opacity: 0.5 }}>↓</div>
                    <div style={{ fontSize: 13, color: '#9ca3af', fontWeight: 500 }}>Drop anything here</div>
                    <div style={{ fontSize: 10, color: '#6b7280', marginTop: 4 }}>
                        Code · Data · Documents · Audio · Images · Video — any file type
                    </div>
                </>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6, width: '100%' }}
                    onClick={(e) => e.stopPropagation()}>
                    {files.map((f, i) => (
                        <FileChip key={`${f.name}-${i}`} file={f} onRemove={() => onRemoveFile(i)} />
                    ))}
                    <div
                        onClick={() => fileInputRef.current?.click()}
                        style={{ fontSize: 10, color: '#6b7280', marginTop: 4, textAlign: 'center', cursor: 'pointer' }}
                        title="Add more files to the current intake batch">
                        + Drop more or click to add
                    </div>
                </div>
            )}
        </div>
    );
}

// ═══════════════════════════════════════
// OLLAMA STATUS INDICATOR
// ═══════════════════════════════════════
export function OllamaStatusBadge({ connected, modelCount }) {
    return (
        <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 10px',
            background: connected ? 'rgba(16,185,129,0.1)' : 'rgba(107,114,128,0.1)',
            borderRadius: 6,
            border: `1px solid ${connected ? 'rgba(16,185,129,0.2)' : 'rgba(107,114,128,0.2)'}`,
        }}>
            <div className={`status-dot ${connected ? 'online' : 'offline'}`} />
            <span style={{
                fontSize: 10, fontFamily: 'var(--font-mono)', letterSpacing: 1,
                color: connected ? '#10b981' : '#6b7280',
            }}>
                {connected ? `OLLAMA · ${modelCount} model${modelCount !== 1 ? 's' : ''}` : 'OLLAMA OFFLINE'}
            </span>
        </div>
    );
}
