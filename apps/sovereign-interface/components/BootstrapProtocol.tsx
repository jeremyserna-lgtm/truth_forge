import React, { useState } from 'react';
import { Terminal, Cpu, HardDrive, Download, ChevronRight, CheckCircle, Shield, Zap } from 'lucide-react';

export const BootstrapProtocol: React.FC = () => {
  const [step, setStep] = useState(0);

  const steps = [
    {
      id: 'hardware',
      title: 'SUBSTRATE RECOGNITION',
      desc: 'Detecting Sovereign Hardware Profile',
      content: (
        <div className="space-y-4">
          <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-500/30 p-4 rounded-lg">
            <h3 className="text-emerald-700 dark:text-emerald-400 font-bold mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4" /> M4 MAX DETECTED
            </h3>
            <p className="text-gray-600 dark:text-zinc-400 text-sm">
              Architecture: <span className="text-gray-900 dark:text-white">Apple Silicon (ARM64)</span><br/>
              Role: <span className="text-gray-900 dark:text-white">GENESIS MACHINE / MOBILE KING</span>
            </p>
          </div>
          <div className="bg-emerald-50 dark:bg-emerald-900/10 border border-emerald-200 dark:border-emerald-500/30 p-4 rounded-lg">
            <h3 className="text-emerald-700 dark:text-emerald-400 font-bold mb-2 flex items-center gap-2">
              <HardDrive className="w-4 h-4" /> 128GB UNIFIED MEMORY
            </h3>
            <div className="w-full bg-gray-200 dark:bg-zinc-800 h-2 rounded-full mt-2 mb-1">
              <div className="bg-emerald-500 h-full rounded-full" style={{ width: '15%' }}></div>
            </div>
            <p className="text-gray-500 dark:text-zinc-500 text-xs text-right font-mono">SYSTEM: 18GB | AVAILABLE FOR AI: ~110GB</p>
            <p className="text-gray-700 dark:text-zinc-300 text-sm mt-2">
              Status: <strong className="text-emerald-600 dark:text-emerald-400">GOD MODE CAPABLE</strong>. 
              You can run Llama-3-70B (Q4_K_M) entirely in RAM with zero offloading.
            </p>
          </div>
        </div>
      )
    },
    {
      id: 'env',
      title: 'ENVIRONMENT PREPARATION',
      desc: 'Installing The Forge (Tools)',
      content: (
        <div className="space-y-4 font-mono text-xs">
          <div className="bg-gray-100 dark:bg-black border border-gray-300 dark:border-zinc-700 p-4 rounded-lg relative group">
            <div className="absolute top-2 right-2 text-[10px] text-gray-500 dark:text-zinc-500">install_core.sh</div>
            <p className="text-gray-500 dark:text-zinc-400"># 1. Install Homebrew (The Package Manager)</p>
            <p className="text-emerald-600 dark:text-emerald-400">/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"</p>
            
            <p className="text-gray-500 dark:text-zinc-400 mt-4"># 2. Install Ollama (The Model Manager)</p>
            <p className="text-emerald-600 dark:text-emerald-400">brew install ollama</p>
            
            <p className="text-gray-500 dark:text-zinc-400 mt-4"># 3. Install MLX (Apple Silicon Native Inference)</p>
            <p className="text-emerald-600 dark:text-emerald-400">pip install mlx-lm</p>
          </div>
          <p className="text-gray-500 dark:text-zinc-400 text-sm italic">
            "The LLM is not a service running on hardware. The LLM inhabits the hardware."
          </p>
        </div>
      )
    },
    {
      id: 'ingest',
      title: 'MODEL INGESTION',
      desc: 'Downloading the Minds',
      content: (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 p-4 rounded-lg">
              <h4 className="text-emerald-600 dark:text-emerald-400 font-bold text-sm">THE BUILDER</h4>
              <p className="text-gray-500 dark:text-zinc-500 text-xs mb-3">Qwen 2.5 Coder 32B</p>
              <div className="flex items-center gap-2 text-xs font-mono bg-gray-100 dark:bg-black p-2 rounded border border-gray-200 dark:border-zinc-800 text-gray-700 dark:text-zinc-300">
                <Terminal className="w-3 h-3" />
                ollama pull qwen2.5-coder:32b
              </div>
            </div>
            <div className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 p-4 rounded-lg">
              <h4 className="text-purple-600 dark:text-purple-400 font-bold text-sm">THE BRAIN (Genesis)</h4>
              <p className="text-gray-500 dark:text-zinc-500 text-xs mb-3">Llama 3.3 70B (Quantized)</p>
              <div className="flex items-center gap-2 text-xs font-mono bg-gray-100 dark:bg-black p-2 rounded border border-gray-200 dark:border-zinc-800 text-gray-700 dark:text-zinc-300">
                <Terminal className="w-3 h-3" />
                ollama pull llama3.3:70b
              </div>
            </div>
          </div>
          <div className="bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-500/30 p-4 rounded-lg">
             <h4 className="text-amber-600 dark:text-amber-400 font-bold text-xs uppercase mb-1 flex items-center gap-2">
                <Shield className="w-3 h-3" /> Zero Trust Warning
             </h4>
             <p className="text-gray-600 dark:text-zinc-400 text-xs">
               Do not use "Instruction Tuned" chat models for Genesis. 
               We require BASE models to strip validation-seeking behaviors via the Inverted Training Paradigm.
             </p>
          </div>
        </div>
      )
    }
  ];

  return (
    <div className="h-full flex flex-col bg-white dark:bg-zinc-950 p-8 transition-colors duration-300">
      <div className="flex items-center justify-between mb-8 border-b border-gray-200 dark:border-zinc-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100 tracking-tight flex items-center gap-3">
            <Zap className="w-6 h-6 text-emerald-500" />
            BOOTSTRAP PROTOCOL
          </h1>
          <p className="text-gray-500 dark:text-zinc-500 text-sm mt-1 font-mono">Genesis Machine Configuration • Phase 0</p>
        </div>
        <div className="text-right">
           <span className="text-[10px] text-gray-500 dark:text-zinc-600 font-mono uppercase block">Target Architecture</span>
           <span className="text-emerald-600 dark:text-emerald-500 font-bold text-sm">SOVEREIGN NODE (SINGLE)</span>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-8 flex-1">
        {/* Steps List */}
        <div className="col-span-4 space-y-4">
          {steps.map((s, idx) => (
            <button
              key={s.id}
              onClick={() => setStep(idx)}
              className={`w-full text-left p-4 rounded-lg border transition-all duration-200 group ${
                step === idx 
                  ? 'bg-gray-50 dark:bg-zinc-900 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.1)]' 
                  : 'bg-gray-50/50 dark:bg-zinc-900/30 border-gray-200 dark:border-zinc-800 hover:bg-gray-100 dark:hover:bg-zinc-900/50'
              }`}
            >
              <div className="flex justify-between items-center mb-1">
                <span className={`text-[10px] font-bold uppercase tracking-wider ${step === idx ? 'text-emerald-600 dark:text-emerald-500' : 'text-gray-500 dark:text-zinc-600'}`}>
                  Step 0{idx + 1}
                </span>
                {step > idx && <CheckCircle className="w-4 h-4 text-emerald-500" />}
              </div>
              <h3 className={`text-sm font-bold ${step === idx ? 'text-gray-900 dark:text-gray-100' : 'text-gray-500 dark:text-zinc-400 group-hover:text-gray-700 dark:group-hover:text-zinc-200'}`}>
                {s.title}
              </h3>
              <p className="text-xs text-gray-500 dark:text-zinc-500 mt-1">{s.desc}</p>
            </button>
          ))}
          
          <div className="mt-8 p-4 bg-gray-100 dark:bg-black border border-gray-300 dark:border-zinc-800 rounded text-xs text-gray-500 dark:text-zinc-500 font-mono">
            <p className="mb-2 uppercase font-bold text-gray-400 dark:text-zinc-400">Setup Philosophy:</p>
            "You are not setting up a workstation. You are setting up an inference server that you also happen to type on. The Memory is for the Mind, not Chrome tabs."
          </div>
        </div>

        {/* Content Area */}
        <div className="col-span-8">
          <div className="h-full bg-gray-50 dark:bg-zinc-900/20 border border-gray-200 dark:border-zinc-800 rounded-xl p-8 relative overflow-hidden transition-colors">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 via-emerald-900 to-transparent"></div>
            
            <div className="mb-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{steps[step].title}</h2>
              <p className="text-gray-600 dark:text-zinc-400 text-sm">{steps[step].desc}</p>
            </div>

            <div className="animate-in fade-in slide-in-from-right-4 duration-300">
              {steps[step].content}
            </div>

            <div className="absolute bottom-8 right-8 flex gap-4">
              <button 
                onClick={() => setStep(Math.max(0, step - 1))}
                disabled={step === 0}
                className="px-6 py-2 rounded border border-gray-300 dark:border-zinc-700 text-gray-500 dark:text-zinc-400 hover:text-gray-900 dark:hover:text-white disabled:opacity-30 disabled:hover:text-gray-500 transition-colors text-sm font-bold"
              >
                BACK
              </button>
              <button 
                onClick={() => setStep(Math.min(steps.length - 1, step + 1))}
                disabled={step === steps.length - 1}
                className="px-6 py-2 rounded bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-30 disabled:bg-gray-300 dark:disabled:bg-zinc-700 transition-colors text-sm font-bold flex items-center gap-2"
              >
                NEXT PHASE <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};