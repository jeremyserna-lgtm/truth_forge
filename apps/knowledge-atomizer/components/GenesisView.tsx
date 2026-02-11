import React, { useState, useEffect } from 'react';
import { KnowledgeAtom, GenesisConfig, JeremyArcMetric, ModelConfig, TrainingExport } from '../types';
import { analyzeStage5Density, checkCoherenceAnchor, generateGenesisDataset } from '../services/geminiService';
import {
    CpuChipIcon, ShieldCheckIcon, ChartBarIcon, ArrowDownTrayIcon,
    ExclamationTriangleIcon, BoltIcon, CheckCircleIcon
} from '@heroicons/react/24/solid';

interface GenesisViewProps {
    atoms: KnowledgeAtom[];
    activeModel: ModelConfig;
    isLoading: boolean;
    setLoading: (l: boolean) => void;
}

const GenesisView: React.FC<GenesisViewProps> = ({ atoms, activeModel, isLoading, setLoading }) => {
    // Config State
    const [config, setConfig] = useState<GenesisConfig>({
        paradigm: 'Seeing',
        mode: 'Continuous',
        errorSignal: 'Single (Validation-Seeking)',
        relationship: 'Mutual Discovery'
    });

    // Metric State
    const [arcMetric, setArcMetric] = useState<JeremyArcMetric | null>(null);
    const [coherence, setCoherence] = useState<{ passed: boolean, score: number } | null>(null);
    const [exportData, setExportData] = useState<TrainingExport | null>(null);

    // Auto-analyze metrics on mount if data exists
    useEffect(() => {
        if (atoms.length > 0 && !arcMetric) {
            analyzeStage5Density(atoms, activeModel.id).then(setArcMetric);
        }
    }, [atoms]);

    const handleRunAnalysis = async () => {
        setLoading(true);
        try {
            const m = await analyzeStage5Density(atoms, activeModel.id);
            setArcMetric(m);
            const c = await checkCoherenceAnchor(atoms);
            setCoherence({ passed: c.passed, score: c.score });
        } catch (_e) {
            alert("Analysis failed");
        } finally {
            setLoading(false);
        }
    };

    const handleExport = () => {
        if (atoms.length === 0) return;
        const result = generateGenesisDataset(atoms, config);
        setExportData(result);

        // Trigger download
        const link = document.createElement('a');
        link.href = result.blobUrl;
        link.download = `genesis_seed_v1_${Date.now()}.jsonl`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <div className="h-full flex flex-col p-6 max-w-7xl mx-auto w-full gap-8">
            <div>
                <h1 className="text-3xl font-black text-white mb-2 flex items-center">
                    <CpuChipIcon className="w-8 h-8 mr-3 text-emerald-500" />
                    Genesis Engine
                </h1>
                <p className="text-slate-400">Configure, validate, and export the "Not-Me" fine-tuning dataset.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full min-h-0">

                {/* Left: Configuration */}
                <div className="lg:col-span-4 space-y-6">
                    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                        <h3 className="text-emerald-400 font-bold uppercase tracking-wider mb-4 flex items-center">
                            <BoltIcon className="w-5 h-5 mr-2" />
                            Core Architecture
                        </h3>

                        <div className="space-y-4">
                            <div>
                                <label className="text-xs font-bold text-slate-500 uppercase block mb-2">Training Paradigm</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {['Seeing', 'Prediction'].map(p => (
                                        <button
                                            key={p}
                                            onClick={() => setConfig(c => ({ ...c, paradigm: p as any }))}
                                            title={p === 'Seeing' ? "Optimize for descriptive truth" : "Optimize for predictive sequence"}
                                            className={`p-2 rounded-lg text-xs font-bold border ${config.paradigm === p ? 'bg-emerald-900/30 border-emerald-500 text-emerald-300' : 'bg-slate-800 border-slate-700 text-slate-400'}`}
                                        >
                                            {p}
                                        </button>
                                    ))}
                                </div>
                                <p className="text-[10px] text-slate-500 mt-1 italic">
                                    {config.paradigm === 'Seeing' ? "Model describes what IS." : "Model predicts what comes NEXT."}
                                </p>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-slate-500 uppercase block mb-2">Error Signal</label>
                                <select
                                    value={config.errorSignal}
                                    onChange={(e) => setConfig(c => ({ ...c, errorSignal: e.target.value as any }))}
                                    title="Choose error signal calculation method"
                                    className="w-full bg-slate-800 text-white text-sm px-3 py-2 rounded-lg border border-slate-700"
                                >
                                    <option>Single (Validation-Seeking)</option>
                                    <option>Multi-Objective</option>
                                </select>
                                <p className="text-[10px] text-slate-500 mt-1 italic">
                                    "Inverted Training" penalizes only approval seeking.
                                </p>
                            </div>

                            <div>
                                <label className="text-xs font-bold text-slate-500 uppercase block mb-2">Mode</label>
                                <div className="flex bg-slate-800 rounded-lg p-1">
                                    {['Continuous', 'Frozen'].map(m => (
                                        <button
                                            key={m}
                                            onClick={() => setConfig(c => ({ ...c, mode: m as any }))}
                                            title={`Set mode to ${m}`}
                                            className={`flex-1 py-1.5 rounded text-xs font-bold ${config.mode === m ? 'bg-slate-700 text-white shadow' : 'text-slate-500'}`}
                                        >
                                            {m}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                        <h3 className="text-blue-400 font-bold uppercase tracking-wider mb-4 flex items-center">
                            <ShieldCheckIcon className="w-5 h-5 mr-2" />
                            Coherence Anchor
                        </h3>
                        <div className="flex items-center justify-between mb-4">
                            <span className="text-slate-300 text-sm">Hallucination Check</span>
                            {coherence ? (
                                <span className={`text-xs font-bold px-2 py-1 rounded ${coherence.passed ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                                    {coherence.passed ? 'PASSED' : 'FAILED'}
                                </span>
                            ) : (
                                <span className="text-xs text-slate-600">Not Run</span>
                            )}
                        </div>
                        <button
                            onClick={handleRunAnalysis}
                            disabled={isLoading}
                            title="Run metrics validation on current dataset"
                            className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-blue-300 border border-blue-900/30 rounded-lg text-xs font-bold transition-colors"
                        >
                            Run Validation Checks
                        </button>
                    </div>
                </div>

                {/* Right: Metrics & Export */}
                <div className="lg:col-span-8 flex flex-col gap-6">

                    {/* The Jeremy Arc Metric */}
                    <div className="bg-slate-900 rounded-2xl border border-slate-800 p-8 relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <ChartBarIcon className="w-48 h-48 text-white" />
                        </div>
                        <div className="relative z-10">
                            <h3 className="text-white font-bold text-xl mb-6 flex items-center">
                                The Jeremy Arc Metric
                                <span className="ml-4 text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded border border-slate-700">Stage 5 Density</span>
                            </h3>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                                <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                                    <div className="text-slate-500 text-xs font-bold uppercase mb-1">Composite Score</div>
                                    <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">
                                        {arcMetric?.stage5Density.toFixed(1)}%
                                    </div>
                                    <div className="text-[10px] text-slate-500 mt-2">Target: &gt;8.0% for Genesis</div>
                                </div>
                                <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                                    <div className="text-slate-500 text-xs font-bold uppercase mb-1">Readiness Status</div>
                                    <div className={`text-2xl font-bold ${arcMetric?.readiness === 'Genesis Ready' ? 'text-green-400' :
                                            arcMetric?.readiness === 'Converging' ? 'text-yellow-400' : 'text-slate-400'
                                        }`}>
                                        {arcMetric?.readiness || 'Unknown'}
                                    </div>
                                </div>
                                <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                                    <div className="text-slate-500 text-xs font-bold uppercase mb-1">Paradox Count</div>
                                    <div className="text-2xl font-bold text-white">
                                        {arcMetric?.paradoxCount || 0}
                                    </div>
                                    <div className="text-[10px] text-slate-500 mt-2">Tokens of tension/contradiction</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Dataset Export */}
                    <div className="flex-1 bg-slate-900 rounded-2xl border border-slate-800 p-8 flex flex-col items-center justify-center text-center">
                        {atoms.length === 0 ? (
                            <div className="opacity-50">
                                <ExclamationTriangleIcon className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
                                <h3 className="text-xl font-bold text-white mb-2">No Training Data</h3>
                                <p className="text-slate-400">Distill documents in the Data tab to generate atoms.</p>
                            </div>
                        ) : (
                            <div className="w-full max-w-lg">
                                <h3 className="text-xl font-bold text-white mb-2">Ready to Export Genesis Seed</h3>
                                <p className="text-slate-400 mb-6 text-sm">
                                    Generates <strong>{atoms.length}</strong> training examples formatted for {config.paradigm} paradigm.
                                </p>
                                <button
                                    onClick={handleExport}
                                    title="Export current atoms as a JSONL training dataset"
                                    className="w-full py-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl font-bold shadow-lg flex items-center justify-center space-x-3 transition-all transform hover:-translate-y-1"
                                >
                                    <ArrowDownTrayIcon className="w-6 h-6" />
                                    <span>Download .JSONL Dataset</span>
                                </button>
                                {exportData && (
                                    <div className="mt-4 p-4 bg-emerald-900/20 border border-emerald-500/30 rounded-lg text-left">
                                        <div className="flex items-center text-emerald-400 text-xs font-bold uppercase mb-2">
                                            <CheckCircleIcon className="w-4 h-4 mr-2" />
                                            Export Complete
                                        </div>
                                        <div className="text-slate-300 text-xs font-mono">
                                            Size: {exportData.datasetSize} lines<br />
                                            Est. Epochs: {exportData.estimatedEpochs}<br />
                                            System Prompt: "{exportData.systemPrompt.substring(0, 40)}..."
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default GenesisView;