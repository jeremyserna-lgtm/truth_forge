// Genesis Console — Pipeline Page (Intake + Process)
import { useState, useCallback } from 'react';
import {
    DropZone, PipelineVisualization, CognitionBus,
    KnowledgeStream, AnimaMemory, SystemLog, SovereigntyStatus,
} from '../components';
import { SOVEREIGNTY_ITEMS } from '../constants';

export default function PipelinePage({
    ollamaStatus, pipeline, addLog, engines, log, nudgeMemory,
}) {
    const [files, setFiles] = useState([]);
    const runModeNote = !ollamaStatus.connected
        ? 'Ollama is offline. Pipeline will run in fallback atomizer mode.'
        : (ollamaStatus.models?.length || 0) === 0
            ? 'No local Ollama models loaded. Pipeline will run in fallback atomizer mode.'
            : '';

    const removeFile = useCallback((index) => {
        setFiles(prev => prev.filter((_, i) => i !== index));
    }, []);

    const handleRun = () => {
        if (files.length === 0) return;
        if (runModeNote) {
            addLog(`Pipeline fallback mode: ${runModeNote}`, 'warn');
        }
        addLog(`Intake: ${files.length} file(s) classified and wrapped`);
        files.forEach(f => addLog(`  → ${f.name} (${(f.size / 1024).toFixed(1)}KB)`));
        pipeline.runPipeline(files);
        nudgeMemory();
    };

    return (
        <div className="main-panel">
            {/* Page Header */}
            <div className="page-header">
                <h1>PIPELINE</h1>
                <p>Drop any file to begin the cascade. INTAKE → ATOMIZE → COMPOUND → SYNTHESIZE → FORGE → PODCAST.</p>
            </div>

            {/* Intake Zone */}
            <div className="card">
                <div className="card-header">UNIVERSAL INTAKE</div>
                <DropZone files={files} onFilesChange={setFiles} onRemoveFile={removeFile} />
                <div style={{ marginTop: 12 }}>
                    <button
                        className="btn-primary"
                        disabled={files.length === 0 || pipeline.processing}
                        onClick={handleRun}
                        title="Run the current intake batch through the atomization pipeline"
                    >
                        {pipeline.processing ? 'PROCESSING...' : 'RUN PIPELINE'}
                    </button>
                    {pipeline.processing && (
                        <button
                            onClick={pipeline.cancelPipeline}
                            title="Stop the current pipeline run"
                            style={{
                                width: '100%', marginTop: 8, padding: '10px 0',
                                background: 'rgba(239,68,68,0.1)', color: '#ef4444',
                                border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)',
                                fontSize: 11, fontFamily: 'var(--font-mono)', cursor: 'pointer',
                                letterSpacing: 2,
                            }}
                        >
                            CANCEL
                        </button>
                    )}
                    <div style={{ marginTop: 10, fontSize: 11, fontFamily: 'var(--font-mono)', color: runModeNote ? '#f59e0b' : '#6b7280' }}>
                        {pipeline.error || runModeNote || 'Ready. Drop files, then run pipeline.'}
                    </div>
                </div>
            </div>

            {/* Pipeline Visualization */}
            <PipelineVisualization
                currentStage={pipeline.currentStage}
                completedStages={pipeline.completedStages}
            />

            {/* Cognition Bus */}
            <CognitionBus
                activeModels={pipeline.activeModels}
                ollamaModels={ollamaStatus.models}
            />

            {/* Knowledge Stream + Sidebar */}
            <div className="grid-2">
                <KnowledgeStream atoms={pipeline.atoms} />
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--gap-lg)' }}>
                    <AnimaMemory engines={engines} />
                    <SovereigntyStatus items={SOVEREIGNTY_ITEMS} />
                    <SystemLog log={log} />
                </div>
            </div>
        </div>
    );
}
