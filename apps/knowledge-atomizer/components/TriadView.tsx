/**
 * TriadView - Real-time visualization of Scout/Maverick/R1 knowledge atom generation
 *
 * Shows:
 * - Three models working in parallel via shared tensor space
 * - Each model's perspective as it generates
 * - EXO distributed inference routing
 * - Convergence/divergence analysis
 * - MemoryCortex communication (tensor-level)
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  KnowledgeAtom,
  ModelConfig,
  ChatMessage,
} from '../types';
import {
  CpuChipIcon,
  BoltIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  EyeIcon,
  BeakerIcon,
  Square3Stack3DIcon,
} from '@heroicons/react/24/solid';

interface ModelPerspective {
  model_name: string;
  model_id: string;
  response_content: string;
  input_tokens: number;
  output_tokens: number;
  latency_ms: number;
  timestamp: string;
  distributed?: boolean; // Whether EXO was used
}

interface GenerationStatus {
  stage: 'idle' | 'enriching' | 'scout' | 'maverick' | 'r1' | 'analyzing' | 'complete';
  currentModel?: string;
  progress: number; // 0-100
}

interface TriadAtom extends KnowledgeAtom {
  perspectives?: ModelPerspective[];
  convergence_score?: number;
  divergence_note?: string;
  generation_metadata?: {
    enriched_input: string;
    processing_time_ms: number;
    memory_graphs: string[];
  };
}

interface TriadViewProps {
  atoms: KnowledgeAtom[];
  activeModel: ModelConfig;
  isLoading: boolean;
  setLoading: (loading: boolean) => void;
  onAtomGenerated: (atom: TriadAtom) => void;
  documents: UploadedDocument[];
  onUploadDocuments: (files: FileList) => void;
  onRemoveDocument: (id: string) => void;
}

interface UploadedDocument {
  id: string;
  name: string;
  content: string;
  size: number;
}

const TriadView: React.FC<TriadViewProps> = ({
  atoms,
  activeModel,
  isLoading,
  setLoading,
  onAtomGenerated,
  documents,
  onUploadDocuments,
  onRemoveDocument,
}) => {
  const [userInput, setUserInput] = useState('');
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>({
    stage: 'idle',
    progress: 0,
  });
  const [currentAtom, setCurrentAtom] = useState<TriadAtom | null>(null);
  const [generationHistory, setGenerationHistory] = useState<TriadAtom[]>([]);
  const [exoStatus, setExoStatus] = useState<{
    available: boolean;
    soldier_count: number;
  }>({ available: false, soldier_count: 0 });

  // Live perspective streaming
  const [scoutPerspective, setScoutPerspective] = useState<ModelPerspective | null>(null);
  const [maverickPerspective, setMaverickPerspective] = useState<ModelPerspective | null>(null);
  const [r1Perspective, setR1Perspective] = useState<ModelPerspective | null>(null);

  // Auto-scroll to latest
  const historyEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    historyEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [generationHistory]);

  // Check EXO status on mount
  useEffect(() => {
    const checkEXO = async () => {
      try {
        const response = await fetch('http://localhost:8000/v1/models');
        setExoStatus({
          available: response.ok,
          soldier_count: 3, // Genesis cluster: 3 soldiers
        });
      } catch {
        setExoStatus({ available: false, soldier_count: 0 });
      }
    };
    checkEXO();
    // Re-check every 30s
    const interval = setInterval(checkEXO, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleGenerate = async () => {
    if (!userInput.trim()) return;
    if (isLoading) return;

    setLoading(true);
    setGenerationStatus({ stage: 'enriching', progress: 10 });
    setScoutPerspective(null);
    setMaverickPerspective(null);
    setR1Perspective(null);

    try {
      // Call backend KnowledgeAtomFactory API
      // Include documents in Scout's context (10M token window)
      const response = await fetch('/api/knowledge-atom/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: userInput,
          use_exo: true,
          commit_to_memory: true,
          documents: documents.map(d => ({
            name: d.name,
            content: d.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      const atom: TriadAtom = await response.json();

      // Simulate progressive updates for visualization
      // In production, use Server-Sent Events or WebSockets for real-time streaming

      setGenerationStatus({ stage: 'scout', currentModel: 'Scout', progress: 30 });
      await new Promise(r => setTimeout(r, 500));
      const scoutPersp = atom.perspectives?.find(p => p.model_id.includes('scout'));
      if (scoutPersp) setScoutPerspective(scoutPersp);

      setGenerationStatus({ stage: 'maverick', currentModel: 'Maverick', progress: 60 });
      await new Promise(r => setTimeout(r, 500));
      const maverickPersp = atom.perspectives?.find(p => p.model_id.includes('maverick'));
      if (maverickPersp) setMaverickPerspective(maverickPersp);

      setGenerationStatus({ stage: 'r1', currentModel: 'R1', progress: 80 });
      await new Promise(r => setTimeout(r, 500));
      const r1Persp = atom.perspectives?.find(p => p.model_id.includes('r1') || p.model_id.includes('deepseek'));
      if (r1Persp) setR1Perspective(r1Persp);

      setGenerationStatus({ stage: 'analyzing', progress: 90 });
      await new Promise(r => setTimeout(r, 300));

      setGenerationStatus({ stage: 'complete', progress: 100 });
      setCurrentAtom(atom);
      setGenerationHistory(prev => [...prev, atom]);
      onAtomGenerated(atom);

      // Reset input
      setUserInput('');

      // Return to idle after 2s
      setTimeout(() => {
        setGenerationStatus({ stage: 'idle', progress: 0 });
      }, 2000);

    } catch (error: any) {
      alert(`Generation failed: ${error.message}`);
      setGenerationStatus({ stage: 'idle', progress: 0 });
    } finally {
      setLoading(false);
    }
  };

  const getStageColor = (stage: GenerationStatus['stage']) => {
    switch (stage) {
      case 'enriching': return 'text-blue-400';
      case 'scout': return 'text-green-400';
      case 'maverick': return 'text-purple-400';
      case 'r1': return 'text-orange-400';
      case 'analyzing': return 'text-yellow-400';
      case 'complete': return 'text-emerald-400';
      default: return 'text-slate-400';
    }
  };

  const getStageIcon = (stage: GenerationStatus['stage']) => {
    switch (stage) {
      case 'scout': return <EyeIcon className="w-5 h-5" />;
      case 'maverick': return <BeakerIcon className="w-5 h-5" />;
      case 'r1': return <CpuChipIcon className="w-5 h-5" />;
      case 'analyzing': return <ChartBarIcon className="w-5 h-5" />;
      case 'complete': return <CheckCircleIcon className="w-5 h-5" />;
      default: return <Square3Stack3DIcon className="w-5 h-5" />;
    }
  };

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUploadDocuments(e.target.files);
    }
  };

  const totalTokensEstimate = documents.reduce((acc, doc) => {
    // Rough estimate: 1 token ≈ 4 characters
    return acc + Math.ceil(doc.content.length / 4);
  }, 0);

  return (
    <div className="h-full flex flex-col bg-slate-950 overflow-hidden">
      {/* Header */}
      <div className="shrink-0 border-b border-slate-800 bg-slate-900/50 backdrop-blur p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-black text-white flex items-center">
              <Square3Stack3DIcon className="w-8 h-8 mr-3 text-indigo-500" />
              Triad Generation
            </h1>
            <p className="text-slate-400 mt-1">
              Scout, Maverick, and R1 communicating via tensor space
            </p>
          </div>

          {/* EXO Status */}
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
            exoStatus.available
              ? 'bg-emerald-900/20 border-emerald-500/30 text-emerald-400'
              : 'bg-red-900/20 border-red-500/30 text-red-400'
          }`}>
            <BoltIcon className="w-4 h-4" />
            <span className="text-xs font-bold">
              EXO {exoStatus.available ? 'ONLINE' : 'OFFLINE'}
            </span>
            {exoStatus.available && (
              <span className="text-[10px] text-emerald-500/70">
                ({exoStatus.soldier_count} soldiers)
              </span>
            )}
          </div>
        </div>

        {/* Document Context Bar */}
        <div className="flex items-center justify-between bg-slate-900/80 rounded-lg p-3 border border-slate-800">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <EyeIcon className="w-4 h-4 text-green-400" />
              <span className="text-sm font-bold text-green-400">Scout Context</span>
            </div>
            <div className="text-xs text-slate-400">
              {documents.length} documents • ~{(totalTokensEstimate / 1000).toFixed(1)}K tokens
              <span className="text-slate-600 ml-2">
                (10M limit)
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".txt,.md,.py,.ts,.tsx,.js,.jsx,.json,.yaml,.yml,.rs,.go,.java,.cpp,.c,.h,.hpp"
              onChange={handleFileSelect}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-3 py-1.5 bg-green-900/30 hover:bg-green-900/50 text-green-400 rounded-lg text-xs font-bold border border-green-500/30 transition-colors"
            >
              + Upload Codebase
            </button>
            {documents.length > 0 && (
              <button
                onClick={() => {
                  if (confirm(`Remove all ${documents.length} documents?`)) {
                    documents.forEach(d => onRemoveDocument(d.id));
                  }
                }}
                className="px-3 py-1.5 bg-red-900/30 hover:bg-red-900/50 text-red-400 rounded-lg text-xs font-bold border border-red-500/30 transition-colors"
              >
                Clear All
              </button>
            )}
          </div>
        </div>

        {/* Document List (if any) */}
        {documents.length > 0 && (
          <div className="mt-3 max-h-24 overflow-y-auto bg-slate-900/50 rounded-lg p-2 border border-slate-800">
            <div className="flex flex-wrap gap-2">
              {documents.map(doc => (
                <div
                  key={doc.id}
                  className="flex items-center space-x-2 bg-slate-800/50 rounded px-2 py-1 text-xs"
                >
                  <span className="text-slate-300">{doc.name}</span>
                  <span className="text-slate-600">
                    ({(doc.content.length / 1024).toFixed(1)}KB)
                  </span>
                  <button
                    onClick={() => onRemoveDocument(doc.id)}
                    className="text-red-400 hover:text-red-300 ml-1"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 p-6 overflow-hidden">

        {/* Left: Input & Generation Status */}
        <div className="flex flex-col gap-6 overflow-hidden">

          {/* Input */}
          <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
            <h3 className="text-white font-bold mb-4">Generate Knowledge Atom</h3>
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Enter text to generate multi-perspective knowledge atom..."
              disabled={isLoading}
              className="w-full h-32 bg-slate-950 text-white rounded-lg p-4 border border-slate-700 focus:border-indigo-500 focus:outline-none resize-none"
            />
            <button
              onClick={handleGenerate}
              disabled={isLoading || !userInput.trim()}
              className={`w-full mt-4 py-3 rounded-lg font-bold transition-all ${
                isLoading || !userInput.trim()
                  ? 'bg-slate-800 text-slate-600 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg'
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                  Generating...
                </span>
              ) : (
                'Generate Atom'
              )}
            </button>
          </div>

          {/* Generation Status */}
          {generationStatus.stage !== 'idle' && (
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
              <h3 className="text-white font-bold mb-4 flex items-center">
                {getStageIcon(generationStatus.stage)}
                <span className="ml-2">
                  {generationStatus.stage === 'enriching' && 'Enriching input via MemoryCortex...'}
                  {generationStatus.stage === 'scout' && 'Scout observing (10M context)...'}
                  {generationStatus.stage === 'maverick' && 'Maverick reasoning (128 experts)...'}
                  {generationStatus.stage === 'r1' && 'R1 architecting (671B parameters)...'}
                  {generationStatus.stage === 'analyzing' && 'Analyzing convergence/divergence...'}
                  {generationStatus.stage === 'complete' && 'Complete!'}
                </span>
              </h3>

              {/* Progress Bar */}
              <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500`}
                  style={{ width: `${generationStatus.progress}%` }}
                />
              </div>

              {generationStatus.currentModel && (
                <p className={`mt-2 text-sm ${getStageColor(generationStatus.stage)}`}>
                  {generationStatus.currentModel} active
                  {generationStatus.stage === 'maverick' || generationStatus.stage === 'r1'
                    ? ' (EXO distributed)'
                    : ' (single-node)'}
                </p>
              )}
            </div>
          )}

          {/* Model Perspectives (Live) */}
          <div className="flex-1 bg-slate-900 rounded-2xl border border-slate-800 p-6 overflow-y-auto">
            <h3 className="text-white font-bold mb-4">Model Perspectives</h3>

            <div className="space-y-4">
              {/* Scout */}
              <div className={`p-4 rounded-lg border ${
                scoutPerspective
                  ? 'bg-green-900/20 border-green-500/30'
                  : 'bg-slate-800/50 border-slate-700'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-green-400">Scout (Seeing)</span>
                  {scoutPerspective && (
                    <span className="text-xs text-green-500/70">
                      {scoutPerspective.latency_ms.toFixed(0)}ms
                    </span>
                  )}
                </div>
                {scoutPerspective ? (
                  <p className="text-sm text-slate-300">
                    {scoutPerspective.response_content.slice(0, 200)}...
                  </p>
                ) : (
                  <p className="text-xs text-slate-600 italic">Waiting...</p>
                )}
              </div>

              {/* Maverick */}
              <div className={`p-4 rounded-lg border ${
                maverickPerspective
                  ? 'bg-purple-900/20 border-purple-500/30'
                  : 'bg-slate-800/50 border-slate-700'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-purple-400">Maverick (Deep Reasoning)</span>
                  {maverickPerspective && (
                    <span className="text-xs text-purple-500/70">
                      {maverickPerspective.latency_ms.toFixed(0)}ms
                      {maverickPerspective.distributed && ' • EXO'}
                    </span>
                  )}
                </div>
                {maverickPerspective ? (
                  <p className="text-sm text-slate-300">
                    {maverickPerspective.response_content.slice(0, 200)}...
                  </p>
                ) : (
                  <p className="text-xs text-slate-600 italic">Waiting...</p>
                )}
              </div>

              {/* R1 */}
              <div className={`p-4 rounded-lg border ${
                r1Perspective
                  ? 'bg-orange-900/20 border-orange-500/30'
                  : 'bg-slate-800/50 border-slate-700'
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-orange-400">R1 (The Architect)</span>
                  {r1Perspective && (
                    <span className="text-xs text-orange-500/70">
                      {r1Perspective.latency_ms.toFixed(0)}ms
                      {r1Perspective.distributed && ' • EXO'}
                    </span>
                  )}
                </div>
                {r1Perspective ? (
                  <p className="text-sm text-slate-300">
                    {r1Perspective.response_content.slice(0, 200)}...
                  </p>
                ) : (
                  <p className="text-xs text-slate-600 italic">Waiting...</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right: Generation History & Analysis */}
        <div className="flex flex-col gap-6 overflow-hidden">

          {/* Current Atom Analysis */}
          {currentAtom && (
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
              <h3 className="text-white font-bold mb-4">Analysis</h3>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="bg-slate-950/50 p-3 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Perspectives</div>
                  <div className="text-2xl font-bold text-white">
                    {currentAtom.perspectives?.length || 0}
                  </div>
                </div>
                <div className="bg-slate-950/50 p-3 rounded-lg">
                  <div className="text-xs text-slate-500 mb-1">Convergence</div>
                  <div className={`text-2xl font-bold ${
                    currentAtom.convergence_score
                      ? currentAtom.convergence_score > 0.7
                        ? 'text-green-400'
                        : 'text-yellow-400'
                      : 'text-slate-600'
                  }`}>
                    {currentAtom.convergence_score
                      ? `${(currentAtom.convergence_score * 100).toFixed(0)}%`
                      : 'N/A'}
                  </div>
                </div>
              </div>

              {currentAtom.divergence_note && (
                <div className="p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg">
                  <div className="text-xs text-yellow-400 font-bold mb-1">DIVERGENCE DETECTED</div>
                  <p className="text-xs text-slate-300">{currentAtom.divergence_note}</p>
                </div>
              )}

              {currentAtom.generation_metadata && (
                <div className="mt-4 text-xs text-slate-500">
                  <div>Processing time: {currentAtom.generation_metadata.processing_time_ms}ms</div>
                  <div>Memory graphs: {currentAtom.generation_metadata.memory_graphs.join(', ')}</div>
                </div>
              )}
            </div>
          )}

          {/* Generation History */}
          <div className="flex-1 bg-slate-900 rounded-2xl border border-slate-800 p-6 overflow-y-auto">
            <h3 className="text-white font-bold mb-4">Generation History</h3>

            {generationHistory.length === 0 ? (
              <p className="text-slate-600 text-sm italic text-center mt-8">
                No atoms generated yet. Enter text above to begin.
              </p>
            ) : (
              <div className="space-y-3">
                {generationHistory.map((atom, idx) => (
                  <div
                    key={atom.id || idx}
                    className="p-4 bg-slate-950/50 rounded-lg border border-slate-800 hover:border-slate-700 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-xs text-slate-500">
                        {new Date(atom.createdAt).toLocaleTimeString()}
                      </span>
                      <div className="flex items-center space-x-2">
                        {atom.convergence_score && atom.convergence_score > 0.7 ? (
                          <CheckCircleIcon className="w-4 h-4 text-green-400" />
                        ) : (
                          <XCircleIcon className="w-4 h-4 text-yellow-400" />
                        )}
                        <span className="text-xs text-slate-400">
                          {atom.perspectives?.length || 0} perspectives
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-300 line-clamp-2">
                      {atom.content}
                    </p>
                  </div>
                ))}
                <div ref={historyEndRef} />
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default TriadView;
