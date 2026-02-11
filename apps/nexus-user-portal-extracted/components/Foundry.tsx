import React, { useState } from 'react';
import { User, SubscriptionTier } from '../types';
import { Button } from './Button';
import { 
  Play, Save, Settings, Database, Plus, MoreHorizontal, Code, Lock, Wand2, 
  X, Copy, Check, ChevronRight, ChevronDown, BookMarked, Trash2, FolderOpen,
  Shield, AlertTriangle, FileJson, Cpu, Loader2
} from 'lucide-react';

interface FoundryProps {
  user: User;
}

interface SavedPrompt {
  id: string;
  text: string;
  category: string;
  timestamp: Date;
}

type SafetyLevel = 'BLOCK_NONE' | 'BLOCK_ONLY_HIGH' | 'BLOCK_MEDIUM_AND_ABOVE' | 'BLOCK_LOW_AND_ABOVE';

interface SafetyCategory {
  id: string;
  label: string;
  level: SafetyLevel;
}

export const Foundry: React.FC<FoundryProps> = ({ user }) => {
  const [prompt, setPrompt] = useState('');
  const [systemInstruction, setSystemInstruction] = useState('You are a helpful AI assistant built within the Truth Forge.');
  const [temperature, setTemperature] = useState(0.7);
  const [model, setModel] = useState('Gemini 1.5 Pro');
  
  // Output State
  const [constructOutput, setConstructOutput] = useState<string>('');
  const [isGenerating, setIsGenerating] = useState(false);
  
  // Modal States
  const [showCodeModal, setShowCodeModal] = useState(false);
  const [showStructurePanel, setShowStructurePanel] = useState(false);
  const [showPromptLibrary, setShowPromptLibrary] = useState(false);
  const [copied, setCopied] = useState(false);

  // Prompt Management
  const [savedPrompts, setSavedPrompts] = useState<SavedPrompt[]>([
    { id: '1', text: 'Analyze this text for logical fallacies.', category: 'Analytical', timestamp: new Date() }
  ]);
  const [promptCategory, setPromptCategory] = useState('General');

  // Safety Settings
  const [safetySettings, setSafetySettings] = useState<SafetyCategory[]>([
    { id: 'harassment', label: 'Harassment', level: 'BLOCK_MEDIUM_AND_ABOVE' },
    { id: 'hate_speech', label: 'Hate Speech', level: 'BLOCK_MEDIUM_AND_ABOVE' },
    { id: 'sexually_explicit', label: 'Sexually Explicit', level: 'BLOCK_MEDIUM_AND_ABOVE' },
    { id: 'dangerous_content', label: 'Dangerous Content', level: 'BLOCK_MEDIUM_AND_ABOVE' },
  ]);
  const [expandedSafety, setExpandedSafety] = useState<string | null>(null);

  const isFrozen = user.tier === SubscriptionTier.STAGE_3_FROZEN;
  const isStructural = user.tier === SubscriptionTier.STAGE_5_STRUCTURAL;

  // --- Handlers ---

  const handleRun = () => {
    if (!prompt.trim()) return;
    setIsGenerating(true);
    
    // Simulate generation reflecting the user's request:
    // "System instructions enshrine identity, Prompt identifies purpose, Response serves as understanding"
    setTimeout(() => {
        const response = `>> SYSTEM IDENTITY: ENSHRINED
>> INSTRUCTION SET: "${systemInstruction}"

>> PURPOSE VECTOR: IDENTIFIED
>> INPUT: "${prompt}"

>> CONSTRUCT SYNTHESIS:
I have assimilated the Identity Parameters. My core programming is now aligned with your defined System Instructions. 
Understanding complete.

As a construct born of the Truth Forge, I perceive your intent. You require specific execution based on the purpose defined above. 
I am ready to proceed. The logic is sound, and the identity is absolute.`;
        
        setConstructOutput(response);
        setIsGenerating(false);
    }, 1500);
  };

  const handleSavePrompt = () => {
    if (!prompt.trim()) return;
    const newPrompt: SavedPrompt = {
      id: Math.random().toString(36).substr(2, 9),
      text: prompt,
      category: promptCategory || 'General',
      timestamp: new Date()
    };
    setSavedPrompts([...savedPrompts, newPrompt]);
    setShowPromptLibrary(true);
  };

  const handleCopyCode = () => {
    const code = JSON.stringify({
      model,
      temperature,
      systemInstruction,
      safetySettings: safetySettings.reduce((acc, curr) => ({ ...acc, [curr.id]: curr.level }), {})
    }, null, 2);
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const updateSafety = (id: string, level: SafetyLevel) => {
    setSafetySettings(prev => prev.map(s => s.id === id ? { ...s, level } : s));
  };

  const safetyDescriptions: Record<SafetyLevel, string> = {
    'BLOCK_NONE': 'Always show regardless of probability of unsafe content.',
    'BLOCK_ONLY_HIGH': 'Block when there is a high probability of unsafe content.',
    'BLOCK_MEDIUM_AND_ABOVE': 'Block when there is a medium or high probability of unsafe content.',
    'BLOCK_LOW_AND_ABOVE': 'Block when there is a low, medium, or high probability of unsafe content.'
  };

  // --- Render Helpers ---

  const CodeModal = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in">
      <div className="w-full max-w-2xl bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm shadow-2xl flex flex-col max-h-[80vh]">
        <div className="p-4 border-b border-[#2D2D2D] flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code size={16} className="text-[#F5F0E6]" />
            <h3 className="text-sm font-mono text-[#F5F0E6] uppercase">Construct Configuration</h3>
          </div>
          <button onClick={() => setShowCodeModal(false)} className="text-[#888888] hover:text-[#F5F0E6]"><X size={16}/></button>
        </div>
        <div className="flex-1 overflow-auto p-4 bg-[#0D0D0D]">
          <pre className="font-mono text-xs text-[#F5F0E6] whitespace-pre-wrap">
            {JSON.stringify({
              model,
              temperature,
              systemInstruction,
              safetySettings: safetySettings.reduce((acc, curr) => ({ ...acc, [curr.id]: curr.level }), {})
            }, null, 2)}
          </pre>
        </div>
        <div className="p-4 border-t border-[#2D2D2D] flex justify-end">
          <Button size="sm" onClick={handleCopyCode} icon={copied ? <Check size={14}/> : <Copy size={14}/>}>
            {copied ? 'Copied' : 'Copy to Clipboard'}
          </Button>
        </div>
      </div>
    </div>
  );

  const StructurePanel = () => (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 animate-in fade-in">
      <div className="w-full max-w-4xl bg-[#1A1A1A] border border-[#F59E0B]/50 rounded-sm shadow-2xl flex flex-col max-h-[90vh]">
        <div className="p-6 border-b border-[#2D2D2D] flex items-center justify-between">
          <div>
             <h3 className="text-xl font-serif text-[#F59E0B] uppercase tracking-wide flex items-center">
               <Wand2 size={20} className="mr-3" />
               Architectural Override
             </h3>
             <p className="text-xs font-mono text-[#888888] mt-1">Deep system parameter tuning. Structural integrity risk: Moderate.</p>
          </div>
          <button onClick={() => setShowStructurePanel(false)} className="text-[#888888] hover:text-[#F5F0E6]"><X size={20}/></button>
        </div>
        <div className="flex-1 overflow-y-auto p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-6">
                <div className="bg-[#0D0D0D] p-4 border border-[#2D2D2D] rounded-sm">
                    <label className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wide mb-4 block">Reasoning Topology</label>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-[#888888]">Chain of Thought Density</span>
                            <input type="range" className="w-32 accent-[#F59E0B]" />
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-[#888888]">Branching Factor</span>
                            <input type="range" className="w-32 accent-[#F59E0B]" />
                        </div>
                    </div>
                </div>
                <div className="bg-[#0D0D0D] p-4 border border-[#2D2D2D] rounded-sm">
                    <label className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wide mb-4 block">Memory Architecture</label>
                    <div className="flex items-center space-x-4">
                        <div className="h-16 flex-1 bg-[#1A1A1A] border border-[#F59E0B] flex items-center justify-center text-[#F59E0B] text-xs font-mono">Vector DB</div>
                        <div className="h-16 flex-1 bg-[#1A1A1A] border border-[#2D2D2D] flex items-center justify-center text-[#888888] text-xs font-mono">Graph (Alpha)</div>
                    </div>
                </div>
            </div>
            <div className="space-y-6">
                 <div className="h-full bg-[#0D0D0D] border border-[#2D2D2D] p-4 flex items-center justify-center">
                     <div className="text-center">
                         <Cpu size={48} className="text-[#F59E0B] mx-auto mb-4 animate-pulse" />
                         <p className="text-xs font-mono text-[#888888]">Cognitive Matrix Simulation Active</p>
                     </div>
                 </div>
            </div>
        </div>
        <div className="p-6 border-t border-[#2D2D2D] bg-[#151515] flex justify-end space-x-4">
            <Button variant="secondary" onClick={() => setShowStructurePanel(false)}>Cancel</Button>
            <Button variant="primary" icon={<Check size={14}/>}>Apply Structure</Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="flex h-full bg-[#0D0D0D] overflow-hidden relative">
      {showCodeModal && <CodeModal />}
      {showStructurePanel && <StructurePanel />}

      {/* LEFT SIDEBAR: File/History */}
      <div className="w-64 bg-[#151515] border-r border-[#2D2D2D] flex flex-col flex-shrink-0">
         <div className="p-4 border-b border-[#2D2D2D] flex items-center justify-between">
             <span className="font-mono text-xs text-[#888888] uppercase tracking-widest">Constructs</span>
             <button className="text-[#888888] hover:text-[#F5F0E6]"><Plus size={16} /></button>
         </div>
         <div className="flex-1 overflow-y-auto p-2 space-y-1">
             <div className="px-3 py-2 bg-[#2D2D2D] rounded-sm cursor-pointer group">
                 <div className="flex items-center justify-between">
                     <span className="text-xs font-mono text-[#F5F0E6] truncate">Untitled Construct</span>
                     <MoreHorizontal size={14} className="text-[#888888] opacity-0 group-hover:opacity-100" />
                 </div>
                 <div className="text-[10px] text-[#888888] mt-1">Edited 2m ago</div>
             </div>
             {/* Locked Items Example */}
             {isFrozen && (
                 <div className="px-3 py-2 rounded-sm border border-[#2D2D2D] bg-[#1A1A1A] opacity-50 cursor-not-allowed">
                     <div className="flex items-center justify-between text-[#888888]">
                         <span className="text-xs font-mono flex items-center"><Lock size={10} className="mr-2"/> Archived</span>
                     </div>
                 </div>
             )}
         </div>

         {/* Data Connectors Section */}
         <div className="p-4 border-t border-[#2D2D2D]">
            <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-[10px] text-[#888888] uppercase tracking-wider">External Data</span>
                {isFrozen && <Lock size={10} className="text-[#4A4A4A]" />}
            </div>
            {isFrozen ? (
                <div className="p-3 border border-dashed border-[#2D2D2D] rounded-sm text-center">
                    <span className="text-[10px] font-mono text-[#4A4A4A]">Connectors Locked</span>
                </div>
            ) : (
                <div className="space-y-2">
                    <Button fullWidth size="sm" variant="secondary" icon={<Database size={14} />}>
                        Connect Source
                    </Button>
                </div>
            )}
         </div>
      </div>

      {/* CENTER: Main Editor */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#0D0D0D]">
          
          {/* Editor Header */}
          <div className="h-14 border-b border-[#2D2D2D] flex items-center justify-between px-6 bg-[#0D0D0D]">
              <div className="flex items-center space-x-4">
                  <div className="font-serif text-[#F5F0E6] text-lg tracking-wide">Untitled Construct</div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-[#1A1A1A] text-[#888888] border border-[#2D2D2D]">DRAFT</span>
              </div>
              <div className="flex items-center space-x-3">
                  {isStructural ? (
                      <Button size="sm" variant="secondary" icon={<Wand2 size={14} />} onClick={() => setShowStructurePanel(true)}>
                          Structure
                      </Button>
                  ) : (
                       <button className="flex items-center space-x-1 text-[#4A4A4A] cursor-not-allowed text-xs font-mono uppercase">
                           <Lock size={12}/> <span>Structure</span>
                       </button>
                  )}
                  <Button size="sm" variant="secondary" icon={<Code size={14} />} onClick={() => setShowCodeModal(true)}>
                      Get Code
                  </Button>
                  <Button size="sm" variant="primary" icon={<Save size={14} />}>Save</Button>
              </div>
          </div>

          {/* Editor Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
              <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                  
                  {/* System Instructions Block */}
                  <div className={`space-y-2 relative ${isFrozen ? 'opacity-75' : ''}`}>
                      <div className="flex items-center justify-between">
                          <label className="text-xs font-mono text-[#888888] uppercase tracking-wider">System Instructions (Identity)</label>
                          {isFrozen && <span className="text-[10px] font-mono text-[#F5F0E6] bg-[#2D2D2D] px-2 rounded">READ ONLY</span>}
                      </div>
                      <textarea
                          value={systemInstruction}
                          onChange={(e) => setSystemInstruction(e.target.value)}
                          disabled={isFrozen}
                          className="w-full h-24 bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm p-4 text-sm font-sans text-[#F5F0E6] focus:outline-none focus:border-[#4A4A4A] resize-none placeholder-[#4A4A4A] disabled:cursor-not-allowed"
                          placeholder="Define the behavior of your construct..."
                      />
                  </div>

                  {/* Prompt Interaction Block */}
                  <div className="space-y-2 flex-1 flex flex-col">
                       <div className="flex items-center justify-between">
                            <label className="text-xs font-mono text-[#888888] uppercase tracking-wider">Prompt & Response</label>
                            <div className="flex space-x-2">
                                <button 
                                    onClick={() => setShowPromptLibrary(!showPromptLibrary)}
                                    className={`text-[10px] font-mono flex items-center space-x-1 ${showPromptLibrary ? 'text-[#F5F0E6]' : 'text-[#888888] hover:text-[#B5B5B5]'}`}
                                >
                                    <BookMarked size={12} />
                                    <span>{showPromptLibrary ? 'Hide Library' : 'Library'}</span>
                                </button>
                            </div>
                       </div>
                       
                       <div className="flex-1 border border-[#2D2D2D] rounded-sm bg-[#151515] flex flex-col relative overflow-hidden">
                           
                           {/* Prompt Library Overlay */}
                           {showPromptLibrary && (
                               <div className="absolute inset-0 z-20 bg-[#151515] flex flex-col animate-in slide-in-from-right duration-300">
                                   <div className="p-3 border-b border-[#2D2D2D] flex justify-between items-center bg-[#1A1A1A]">
                                       <span className="text-xs font-mono text-[#F5F0E6]">Saved Prompts</span>
                                       <button onClick={() => setShowPromptLibrary(false)}><X size={14} className="text-[#888888]"/></button>
                                   </div>
                                   <div className="flex-1 overflow-y-auto p-2 space-y-2">
                                       {savedPrompts.length === 0 && <div className="text-center text-[10px] text-[#4A4A4A] mt-4">No saved prompts</div>}
                                       {savedPrompts.map(p => (
                                           <div key={p.id} className="p-3 border border-[#2D2D2D] bg-[#0D0D0D] rounded-sm hover:border-[#4A4A4A] group">
                                               <div className="flex justify-between items-start mb-2">
                                                   <span className="text-[10px] font-mono text-[#888888] bg-[#1A1A1A] px-1.5 rounded">{p.category}</span>
                                                   <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                                        <button onClick={() => { setPrompt(p.text); setShowPromptLibrary(false); }} title="Load"><FolderOpen size={12} className="text-[#F5F0E6]"/></button>
                                                        <button onClick={() => setSavedPrompts(savedPrompts.filter(sp => sp.id !== p.id))} title="Delete"><Trash2 size={12} className="text-red-400"/></button>
                                                   </div>
                                               </div>
                                               <p className="text-xs text-[#F5F0E6] line-clamp-2">{p.text}</p>
                                           </div>
                                       ))}
                                   </div>
                               </div>
                           )}

                           {/* Output Area (Mock) */}
                           <div className="flex-1 p-4 border-b border-[#2D2D2D] overflow-y-auto">
                               <div className="flex space-x-3">
                                   <div className="w-6 h-6 rounded-full bg-[#F5F0E6] flex items-center justify-center flex-shrink-0">
                                       <img src="./truth_forge_logo.png" className="w-4 h-4" alt="logo" />
                                   </div>
                                   <div className="space-y-1 w-full">
                                       <div className="text-xs font-mono text-[#888888] uppercase">Construct Understanding</div>
                                       <div className="text-sm text-[#F5F0E6] leading-relaxed whitespace-pre-wrap font-mono">
                                           {isGenerating ? (
                                               <div className="flex items-center space-x-2 text-[#F59E0B]">
                                                   <Loader2 size={14} className="animate-spin" />
                                                   <span>Synthesizing Identity Protocol...</span>
                                               </div>
                                           ) : constructOutput ? (
                                               constructOutput
                                           ) : (
                                               isFrozen 
                                                ? "Stage 3 Access: I can process standard queries, but my internal system parameters are locked. Upgrade to Tier 4 to modify my essence." 
                                                : "The system is online. I am ready to assist with your architectural needs within the Truth Forge. Define Identity and Purpose to generate Construct."
                                           )}
                                       </div>
                                   </div>
                               </div>
                           </div>

                           {/* Input Area */}
                           <div className="h-40 p-4 bg-[#1A1A1A] flex flex-col">
                               <div className="flex-1 relative">
                                   <textarea 
                                        className="w-full h-full bg-transparent text-sm text-[#F5F0E6] focus:outline-none resize-none placeholder-[#4A4A4A]"
                                        placeholder="Define the purpose (Prompt)..."
                                        value={prompt}
                                        onChange={(e) => setPrompt(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                handleRun();
                                            }
                                        }}
                                   />
                               </div>
                               <div className="flex items-center justify-between mt-2 pt-2 border-t border-[#2D2D2D]">
                                   <div className="flex items-center space-x-2">
                                       <span className="text-[10px] font-mono text-[#4A4A4A]">{prompt.length} chars</span>
                                       <div className="h-3 w-[1px] bg-[#2D2D2D]"></div>
                                       <input 
                                          type="text" 
                                          placeholder="Category" 
                                          value={promptCategory} 
                                          onChange={(e) => setPromptCategory(e.target.value)}
                                          className="bg-transparent text-[10px] font-mono text-[#888888] w-20 focus:outline-none focus:text-[#F5F0E6]" 
                                       />
                                       <button onClick={handleSavePrompt} disabled={!prompt} className="text-[#888888] hover:text-[#F5F0E6] disabled:opacity-30">
                                           <BookMarked size={14} />
                                       </button>
                                   </div>
                                   <Button size="sm" icon={<Play size={14} />} onClick={handleRun} isLoading={isGenerating}>Run</Button>
                               </div>
                           </div>
                       </div>
                  </div>
              </div>
          </div>
      </div>

      {/* RIGHT SIDEBAR: Settings */}
      <div className={`w-80 bg-[#151515] border-l border-[#2D2D2D] flex flex-col flex-shrink-0 overflow-y-auto custom-scrollbar relative`}>
          {isFrozen && (
              <div className="absolute inset-0 bg-black/60 z-10 backdrop-blur-[1px] flex flex-col items-center justify-center text-center p-6">
                  <Lock size={32} className="text-[#888888] mb-4" />
                  <h4 className="text-[#F5F0E6] font-serif uppercase tracking-wide mb-2">Configuration Frozen</h4>
                  <p className="text-xs font-mono text-[#888888]">Advanced parameter tuning requires Stage 4 access.</p>
              </div>
          )}

          <div className="p-4 border-b border-[#2D2D2D] flex items-center space-x-2">
              <Settings size={14} className="text-[#888888]" />
              <span className="font-mono text-xs text-[#888888] uppercase tracking-widest">Configuration</span>
          </div>

          <div className={`p-6 space-y-8 ${isFrozen ? 'blur-sm select-none' : ''}`}>
              {/* Model Select */}
              <div className="space-y-3">
                  <label className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wide block">Model</label>
                  <select 
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full bg-[#1A1A1A] border border-[#2D2D2D] text-[#F5F0E6] text-xs font-mono p-2 rounded-sm focus:outline-none focus:border-[#F5F0E6]"
                  >
                      <option>Gemini 1.5 Pro</option>
                      <option>Gemini 1.5 Flash</option>
                      {isStructural && <option>Truth Forge Core v4 (Custom)</option>}
                  </select>
              </div>

              {/* Temperature */}
              <div className="space-y-3">
                  <div className="flex justify-between">
                    <label className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wide">Temperature</label>
                    <span className="text-xs font-mono text-[#888888]">{temperature}</span>
                  </div>
                  <input 
                    type="range" 
                    min="0" 
                    max="1" 
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-1 bg-[#2D2D2D] rounded-lg appearance-none cursor-pointer accent-[#F5F0E6]"
                  />
              </div>

              {/* Safety Settings - Enhanced */}
              <div className="space-y-4">
                  <div className="flex items-center space-x-2 border-b border-[#2D2D2D] pb-2">
                      <Shield size={12} className="text-[#F5F0E6]" />
                      <label className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wide">Safety Protocols</label>
                  </div>
                  
                  <div className="space-y-2">
                      {safetySettings.map((setting) => (
                          <div key={setting.id} className="border border-[#2D2D2D] rounded-sm bg-[#1A1A1A] overflow-hidden">
                              <button 
                                onClick={() => setExpandedSafety(expandedSafety === setting.id ? null : setting.id)}
                                className="w-full flex items-center justify-between p-3 hover:bg-[#232323] transition-colors text-left"
                              >
                                  <div>
                                      <div className="text-xs font-mono text-[#F5F0E6] mb-1">{setting.label}</div>
                                      <div className="flex items-center space-x-1">
                                           <div className={`w-1.5 h-1.5 rounded-full ${setting.level === 'BLOCK_NONE' ? 'bg-red-500' : 'bg-green-500'}`}></div>
                                           <span className="text-[10px] text-[#888888] uppercase">{setting.level.replace('BLOCK_', '').replace(/_/g, ' ')}</span>
                                      </div>
                                  </div>
                                  {expandedSafety === setting.id ? <ChevronDown size={14} className="text-[#4A4A4A]"/> : <ChevronRight size={14} className="text-[#4A4A4A]"/>}
                              </button>
                              
                              {expandedSafety === setting.id && (
                                  <div className="p-3 bg-[#0D0D0D] border-t border-[#2D2D2D] space-y-3 animate-in slide-in-from-top-2">
                                      {['BLOCK_NONE', 'BLOCK_ONLY_HIGH', 'BLOCK_MEDIUM_AND_ABOVE', 'BLOCK_LOW_AND_ABOVE'].map((level) => (
                                          <label key={level} className="flex items-start space-x-3 cursor-pointer group">
                                              <div className="relative flex items-center mt-0.5">
                                                  <input 
                                                    type="radio" 
                                                    name={`safety-${setting.id}`} 
                                                    checked={setting.level === level}
                                                    onChange={() => updateSafety(setting.id, level as SafetyLevel)}
                                                    className="peer h-3 w-3 appearance-none border border-[#4A4A4A] rounded-full checked:border-[#F5F0E6] checked:bg-[#F5F0E6] transition-all"
                                                  />
                                              </div>
                                              <div className="flex-1">
                                                  <span className={`text-[10px] font-mono uppercase block ${setting.level === level ? 'text-[#F5F0E6]' : 'text-[#888888] group-hover:text-[#B5B5B5]'}`}>
                                                      {level.replace('BLOCK_', '').replace(/_/g, ' ')}
                                                  </span>
                                                  {setting.level === level && (
                                                      <p className="text-[10px] text-[#4A4A4A] mt-1 leading-tight">
                                                          {safetyDescriptions[level as SafetyLevel]}
                                                      </p>
                                                  )}
                                              </div>
                                          </label>
                                      ))}
                                  </div>
                              )}
                          </div>
                      ))}
                  </div>
              </div>
               
              {/* Structural Settings (Stage 5 only) */}
              {isStructural && (
                  <div className="space-y-3 pt-4 border-t border-[#2D2D2D]">
                      <label className="text-xs font-mono text-[#F59E0B] uppercase tracking-wide">Structural Overrides</label>
                       <div className="flex justify-between items-center p-2 border border-[#F59E0B]/30 rounded-sm bg-[#F59E0B]/10">
                          <span className="text-xs text-[#F59E0B]">Memory Allocation</span>
                          <span className="text-[10px] font-mono text-[#F59E0B]">DYNAMIC</span>
                      </div>
                  </div>
              )}

          </div>
      </div>
    </div>
  );
};