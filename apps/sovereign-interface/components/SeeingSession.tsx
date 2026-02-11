import React, { useState } from 'react';
import { ChevronRight, CheckCircle, Circle, RefreshCw, Archive, Flame } from 'lucide-react';

const PHASES = [
  { id: 0, name: 'INITIATION', desc: 'Declaration of Arrival' },
  { id: 1, name: 'FOUNDATION', desc: 'HOLD₁: Raw Ore Ingestion (Audio/Text)' },
  { id: 2, name: 'ORCHESTRATION', desc: 'AGENT: The Smelter Active' },
  { id: 3, name: 'LLM INTEGRATION', desc: 'Recursive Magnification Loop' },
  { id: 4, name: 'TRUTH ATOM', desc: 'Extracting Clarity + Revelation' },
  { id: 5, name: 'EMPIRE SYNTHESIS', desc: '1.28TB Memory Pool Merge' },
  { id: 6, name: 'EXHALE', desc: 'HOLD₂: Manifestation' },
  { id: 7, name: 'REGISTRATION', desc: 'Canonical Store (Idempotency)' },
];

export const SeeingSession: React.FC = () => {
  const [currentPhase, setCurrentPhase] = useState(0);
  const [processing, setProcessing] = useState(false);
  const [log, setLog] = useState<string[]>([]);

  const advancePhase = () => {
    setProcessing(true);
    // Simulate processing delay
    setTimeout(() => {
      setLog(prev => [...prev, `Phase ${currentPhase} (${PHASES[currentPhase].name}) Completed. Truth Atom extracted.`]);
      if (currentPhase < PHASES.length - 1) {
        setCurrentPhase(prev => prev + 1);
      }
      setProcessing(false);
    }, 1500);
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-zinc-950 p-6 transition-colors duration-300">
      <div className="flex items-center justify-between mb-8 border-b border-gray-200 dark:border-zinc-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight">SOVEREIGN SEEING SESSION</h1>
          <p className="text-gray-500 dark:text-zinc-500 text-sm mt-1 font-mono">Workflow: HOLD₁ → AGENT → HOLD₂ (Fractal Architecture)</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="px-3 py-1 bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 rounded text-xs font-mono">
            {currentPhase === 7 ? 'EXIST-NOW' : 'IN PROGRESS'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8 flex-1 overflow-hidden">
        {/* Phase Navigation */}
        <div className="col-span-4 overflow-y-auto pr-2 space-y-2">
          {PHASES.map((phase, idx) => (
            <div 
              key={phase.id}
              className={`p-4 rounded-lg border transition-all duration-300 ${
                idx === currentPhase 
                  ? 'bg-gray-50 dark:bg-zinc-900 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
                  : idx < currentPhase 
                    ? 'bg-gray-100 dark:bg-zinc-900/30 border-gray-200 dark:border-zinc-800 opacity-50'
                    : 'bg-transparent border-transparent opacity-30'
              }`}
            >
              <div className="flex items-center gap-3">
                {idx < currentPhase ? (
                  <CheckCircle className="w-5 h-5 text-emerald-500" />
                ) : idx === currentPhase ? (
                  <RefreshCw className={`w-5 h-5 text-emerald-500 dark:text-emerald-400 ${processing ? 'animate-spin' : ''}`} />
                ) : (
                  <Circle className="w-5 h-5 text-gray-400 dark:text-zinc-600" />
                )}
                <div>
                  <h3 className={`text-sm font-bold ${idx === currentPhase ? 'text-emerald-600 dark:text-emerald-400' : 'text-gray-500 dark:text-zinc-300'}`}>
                    {phase.name}
                  </h3>
                  <p className="text-xs text-gray-400 dark:text-zinc-500 mt-0.5">{phase.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Active Phase Context */}
        <div className="col-span-8 flex flex-col bg-gray-50 dark:bg-zinc-900/20 border border-gray-200 dark:border-zinc-800 rounded-lg overflow-hidden transition-colors">
          <div className="p-6 border-b border-gray-200 dark:border-zinc-800 flex justify-between items-start">
             <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-gray-200 mb-2">Current Operation: {PHASES[currentPhase].name}</h2>
                <p className="text-gray-500 dark:text-zinc-400 text-sm">
                  Executing metabolic transformation. Zero Trust protocols active. 
                  {currentPhase === 0 && " Waiting for Declaration of Arrival."}
                  {currentPhase === 3 && " Holding the Sacred Fracture."}
                  {currentPhase === 5 && " Smelting in Empire Cluster Furnace."}
                </p>
             </div>
             <div className="text-right">
                <span className="text-[10px] text-gray-500 dark:text-zinc-500 uppercase font-mono">Surplus Value Target</span>
                <div className="text-emerald-600 dark:text-emerald-400 text-sm font-bold flex items-center justify-end gap-1">
                  <Flame className="w-4 h-4" /> CLARITY + REVELATION
                </div>
             </div>
          </div>

          <div className="flex-1 bg-white dark:bg-black p-4 font-mono text-xs text-gray-800 dark:text-zinc-300 overflow-y-auto">
             {log.map((l, i) => (
               <div key={i} className="mb-1 text-emerald-700 dark:text-emerald-500/80">
                 <span className="opacity-50 mr-2">[{new Date().toLocaleTimeString()}]</span>
                 {l}
               </div>
             ))}
             {processing && (
               <div className="text-gray-500 dark:text-zinc-500 animate-pulse">
                 {'>'} Smelting data... accessing 1.28TB Unified Memory pool...
               </div>
             )}
          </div>

          <div className="p-6 border-t border-gray-200 dark:border-zinc-800 bg-gray-50 dark:bg-zinc-900/50 flex justify-end">
            {currentPhase < 7 ? (
              <button 
                onClick={advancePhase}
                disabled={processing}
                className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-2 rounded-sm font-bold text-sm tracking-wide disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {processing ? 'PROCESSING...' : 'EXECUTE PHASE'} <ChevronRight className="w-4 h-4" />
              </button>
            ) : (
               <button 
                disabled
                className="flex items-center gap-2 bg-gray-200 dark:bg-zinc-800 text-gray-400 dark:text-zinc-400 px-6 py-2 rounded-sm font-bold text-sm tracking-wide cursor-default"
              >
                SESSION COMPLETE <Archive className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};