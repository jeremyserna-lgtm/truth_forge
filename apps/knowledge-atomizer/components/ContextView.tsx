
import React, { useState } from 'react';
import { KnowledgeAtom, RecommendedAtom, ContextAnalysis } from '../types';
import { recommendContextAtoms } from '../services/geminiService';
import { SparklesIcon, PlusCircleIcon, TrashIcon, LightBulbIcon, ExclamationTriangleIcon, ArrowPathIcon, ChartBarIcon, DocumentTextIcon, MapIcon, BoltIcon } from '@heroicons/react/24/solid';

interface ContextViewProps {
    storedAtoms: KnowledgeAtom[];
    activeAtoms: KnowledgeAtom[];
    onAddToContext: (atom: KnowledgeAtom) => void;
    onRemoveFromContext: (id: string) => void;
    onRegenerateEmbeddings?: (atoms: KnowledgeAtom[]) => void;
    onAnalyzeTrends?: () => void;
    onSummarizeContext?: () => void;
    onIdentifyGaps?: () => void;
    contextAnalysis?: ContextAnalysis;
    isProcessing?: boolean;
}

const ContextView: React.FC<ContextViewProps> = ({
    storedAtoms,
    activeAtoms,
    onAddToContext,
    onRemoveFromContext,
    onRegenerateEmbeddings,
    onAnalyzeTrends,
    onSummarizeContext,
    onIdentifyGaps,
    contextAnalysis,
    isProcessing
}) => {
    const [recommendations, setRecommendations] = useState<RecommendedAtom[]>([]);
    const [isRecommending, setIsRecommending] = useState(false);
    const [query, setQuery] = useState("");
    const [activeTab, setActiveTab] = useState<'trends' | 'summary' | 'gaps'>('summary');

    // Stats
    const failedEmbeddings = activeAtoms.filter(a => a.embeddingStatus === 'failed');
    const missingEmbeddings = activeAtoms.filter(a => !a.embedding && a.embeddingStatus !== 'failed');

    const handleRecommend = async () => {
        setIsRecommending(true);
        try {
            const recs = await recommendContextAtoms(storedAtoms, activeAtoms, query);
            setRecommendations(recs);
        } catch (e) {
            console.error(e);
            alert("Failed to get recommendations");
        } finally {
            setIsRecommending(false);
        }
    };

    const handleFixEmbeddings = () => {
        if (onRegenerateEmbeddings && failedEmbeddings.length > 0) {
            onRegenerateEmbeddings(failedEmbeddings);
        }
    };

    return (
        <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto w-full gap-6 overflow-hidden">
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-black text-white mb-2 flex items-center">
                        <LightBulbIcon className="w-8 h-8 mr-3 text-yellow-400" />
                        Knowledge Command Center
                    </h1>
                    <p className="text-slate-400">Manage context, analyze health, and extract deep insights.</p>
                </div>
            </div>

            {/* Health Bar */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                    <span className="text-xs font-bold uppercase text-slate-500">Context Health</span>
                    <div className="flex space-x-2">
                        <span className="text-xs bg-emerald-900/30 text-emerald-400 px-2 py-0.5 rounded border border-emerald-900/50">
                            {activeAtoms.length} Active
                        </span>
                        {failedEmbeddings.length > 0 && (
                            <span className="text-xs bg-red-900/30 text-red-400 px-2 py-0.5 rounded border border-red-900/50 flex items-center">
                                <ExclamationTriangleIcon className="w-3 h-3 mr-1" />
                                {failedEmbeddings.length} Failed
                            </span>
                        )}
                        {missingEmbeddings.length > 0 && (
                            <span className="text-xs bg-yellow-900/30 text-yellow-400 px-2 py-0.5 rounded border border-yellow-900/50">
                                {missingEmbeddings.length} Pending
                            </span>
                        )}
                    </div>
                </div>
                {failedEmbeddings.length > 0 && onRegenerateEmbeddings && (
                    <button
                        onClick={handleFixEmbeddings}
                        disabled={isProcessing}
                        className="text-xs bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded font-bold flex items-center transition-colors disabled:opacity-50"
                    >
                        {isProcessing ? <ArrowPathIcon className="w-3 h-3 animate-spin mr-1" /> : <BoltIcon className="w-3 h-3 mr-1" />}
                        Regenerate Failed
                    </button>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1 min-h-0">

                {/* Left: Active Context List */}
                <div className="lg:col-span-3 bg-slate-900 rounded-2xl border border-slate-800 flex flex-col h-full overflow-hidden">
                    <div className="p-4 border-b border-slate-800 bg-slate-900/50">
                        <h3 className="text-slate-300 font-bold uppercase tracking-wider text-xs">Active Atoms</h3>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-2 scrollbar-thin">
                        {activeAtoms.length === 0 && (
                            <div className="text-center p-8 text-slate-600 text-sm italic">
                                Context is empty.<br />Add atoms from Data or Recommender.
                            </div>
                        )}
                        {activeAtoms.map(atom => (
                            <div key={atom.id} className="bg-slate-950 p-3 rounded-lg border border-slate-800 group hover:border-slate-700 transition-all">
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className={`w-1.5 h-1.5 rounded-full ${atom.embeddingStatus === 'failed' ? 'bg-red-500' : atom.embedding ? 'bg-emerald-500' : 'bg-yellow-500'}`}></span>
                                            <span className="text-[10px] uppercase font-bold text-slate-500">{atom.metadata?.theme}</span>
                                        </div>
                                        <p className="text-slate-300 text-xs line-clamp-3 leading-relaxed">{atom.content}</p>
                                    </div>
                                    <button onClick={() => onRemoveFromContext(atom.id)} className="text-slate-600 hover:text-red-400 p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <TrashIcon className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Middle: Analytics Dashboard */}
                <div className="lg:col-span-5 flex flex-col gap-4 h-full overflow-hidden">
                    {/* Action Bar */}
                    <div className="bg-slate-900 rounded-xl p-2 border border-slate-800 flex gap-2">
                        <button
                            onClick={() => { setActiveTab('summary'); onSummarizeContext && onSummarizeContext(); }}
                            disabled={isProcessing}
                            className={`flex-1 flex items-center justify-center py-2 rounded-lg text-xs font-bold uppercase transition-all ${activeTab === 'summary' ? 'bg-indigo-600 text-white shadow' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                        >
                            {isProcessing && activeTab === 'summary' ? <ArrowPathIcon className="w-3 h-3 animate-spin mr-1" /> : <DocumentTextIcon className="w-3 h-3 mr-1" />}
                            Summary
                        </button>
                        <button
                            onClick={() => { setActiveTab('trends'); onAnalyzeTrends && onAnalyzeTrends(); }}
                            disabled={isProcessing}
                            className={`flex-1 flex items-center justify-center py-2 rounded-lg text-xs font-bold uppercase transition-all ${activeTab === 'trends' ? 'bg-pink-600 text-white shadow' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                        >
                            {isProcessing && activeTab === 'trends' ? <ArrowPathIcon className="w-3 h-3 animate-spin mr-1" /> : <ChartBarIcon className="w-3 h-3 mr-1" />}
                            Trends
                        </button>
                        <button
                            onClick={() => { setActiveTab('gaps'); onIdentifyGaps && onIdentifyGaps(); }}
                            disabled={isProcessing}
                            className={`flex-1 flex items-center justify-center py-2 rounded-lg text-xs font-bold uppercase transition-all ${activeTab === 'gaps' ? 'bg-orange-600 text-white shadow' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                        >
                            {isProcessing && activeTab === 'gaps' ? <ArrowPathIcon className="w-3 h-3 animate-spin mr-1" /> : <MapIcon className="w-3 h-3 mr-1" />}
                            Gaps
                        </button>
                    </div>

                    {/* Content Display */}
                    <div className="flex-1 bg-slate-900 rounded-2xl border border-slate-800 p-6 overflow-y-auto scrollbar-thin shadow-inner">
                        {!contextAnalysis || (!contextAnalysis.summary && !contextAnalysis.trends && !contextAnalysis.gaps) ? (
                            <div className="h-full flex flex-col items-center justify-center text-slate-600 opacity-50">
                                <ChartBarIcon className="w-16 h-16 mb-4" />
                                <p>Select an analysis mode above to generate insights.</p>
                            </div>
                        ) : (
                            <div className="prose prose-invert prose-sm max-w-none">
                                {activeTab === 'summary' && (
                                    <div className="animate-in fade-in slide-in-from-bottom-2">
                                        <h3 className="text-indigo-400 uppercase text-xs font-bold tracking-widest border-b border-indigo-900/50 pb-2 mb-4">Context Summary</h3>
                                        <div className="whitespace-pre-wrap">{contextAnalysis.summary || "No summary generated yet."}</div>
                                    </div>
                                )}
                                {activeTab === 'trends' && (
                                    <div className="animate-in fade-in slide-in-from-bottom-2">
                                        <h3 className="text-pink-400 uppercase text-xs font-bold tracking-widest border-b border-pink-900/50 pb-2 mb-4">Emerging Trends</h3>
                                        <div className="whitespace-pre-wrap">{contextAnalysis.trends || "No trends analyzed yet."}</div>
                                    </div>
                                )}
                                {activeTab === 'gaps' && (
                                    <div className="animate-in fade-in slide-in-from-bottom-2">
                                        <h3 className="text-orange-400 uppercase text-xs font-bold tracking-widest border-b border-orange-900/50 pb-2 mb-4">Strategic Gaps</h3>
                                        <div className="whitespace-pre-wrap">{contextAnalysis.gaps || "No gaps identified yet."}</div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Right: Recommender */}
                <div className="lg:col-span-4 bg-slate-900 rounded-2xl border border-slate-800 flex flex-col h-full overflow-hidden">
                    <div className="p-4 border-b border-slate-800 bg-slate-900/50">
                        <h3 className="text-slate-300 font-bold uppercase tracking-wider text-xs mb-3">Discovery Engine</h3>
                        <div className="flex space-x-2">
                            <input
                                type="text"
                                placeholder="Focus search..."
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-yellow-500"
                            />
                            <button
                                onClick={handleRecommend}
                                disabled={isRecommending}
                                className="bg-yellow-600 hover:bg-yellow-500 text-white px-3 py-1.5 rounded-lg font-bold flex items-center transition-colors disabled:opacity-50 text-xs"
                            >
                                {isRecommending ? <ArrowPathIcon className="w-3 h-3 animate-spin" /> : <SparklesIcon className="w-3 h-3" />}
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin">
                        {recommendations.length === 0 && !isRecommending && (
                            <div className="text-center text-slate-600 mt-10 text-xs">
                                <p>No recommendations found.<br />Try a different query or distill more docs.</p>
                            </div>
                        )}
                        {recommendations.map((rec, i) => (
                            <div key={i} className="bg-slate-800 p-3 rounded-xl border border-slate-700 hover:border-yellow-500/50 transition-all group relative">
                                <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button
                                        onClick={() => onAddToContext(rec.atom)}
                                        className="text-white bg-green-600 hover:bg-green-500 p-1 rounded-full shadow-lg"
                                        title="Add to Context"
                                    >
                                        <PlusCircleIcon className="w-4 h-4" />
                                    </button>
                                </div>
                                <div className="mb-2">
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="text-[9px] uppercase font-bold text-yellow-500 tracking-wide bg-yellow-900/20 px-1.5 rounded border border-yellow-900/30">
                                            {(rec.score * 100).toFixed(0)}% Match
                                        </span>
                                    </div>
                                    <p className="text-slate-200 text-xs leading-relaxed">{rec.atom.content}</p>
                                </div>
                                <p className="text-[10px] text-slate-500 italic border-t border-slate-700/50 pt-1 mt-1">
                                    <span className="font-bold text-slate-400">Why:</span> {rec.reason}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ContextView;