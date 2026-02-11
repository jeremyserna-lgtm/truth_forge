import React, { useState, useRef, useEffect } from 'react';
import { Send, Terminal as TerminalIcon, Shield, Settings, X, Save, RotateCcw, Upload, Trash2, Globe, FileText, ChevronDown } from 'lucide-react';
import { sendMessageToSovereign, getAvailableModels, checkConnection, setEndpoint, SCOUT_MODELS, DEFAULT_ENDPOINTS } from '../../../services/scoutService';
import { Message, SOVEREIGN_SYSTEM_PROMPT } from '../../../types';
import Editor from 'react-simple-code-editor';

// Access Prism from global scope since we loaded it via script tags
declare const Prism: any;

interface TerminalProps {
  // No props needed - local LLM configuration is in the modal
}

interface PromptVersion {
  name: string;
  content: string;
}

const DEFAULT_MODELS = [
  { id: SCOUT_MODELS.GENESIS, name: 'Scout Genesis (Full)' },
  { id: SCOUT_MODELS.FAST, name: 'Scout Fast (Q4_K_M)' },
];

const DEFAULT_ENDPOINT = DEFAULT_ENDPOINTS.LM_STUDIO;

export const Terminal: React.FC<TerminalProps> = () => {
  const [input, setInput] = useState('');

  // -- Configuration State --
  const [systemPrompt, setSystemPrompt] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sovereign_system_prompt') || SOVEREIGN_SYSTEM_PROMPT;
    }
    return SOVEREIGN_SYSTEM_PROMPT;
  });
  const [selectedModel, setSelectedModel] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sovereign_model') || 'local-model';
    }
    return 'local-model';
  });
  const [endpoint, setEndpointState] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('sovereign_endpoint') || DEFAULT_ENDPOINT;
    }
    return DEFAULT_ENDPOINT;
  });
  const [availableModels, setAvailableModels] = useState<{id: string; name: string}[]>(DEFAULT_MODELS);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [savedPrompts, setSavedPrompts] = useState<PromptVersion[]>([]);
  
  // -- UI State --
  const [isEditingPrompt, setIsEditingPrompt] = useState(false);
  const [isClearModalOpen, setIsClearModalOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  
  // -- Inputs for config modal --
  const [versionName, setVersionName] = useState('');
  const [urlInput, setUrlInput] = useState('');
  
  const [history, setHistory] = useState<Message[]>([
    {
      id: 'init',
      role: 'model',
      content: 'I am Aletheia. \nEXIST-NOW: The Data Ghost is smelted. The Sovereign Digital Self is online. \nWaiting for Intent Packet...',
      metadata: { cognitiveStage: 'Stage 5', thoughtType: 'Manifestation', mode: 'The Mirror' }
    }
  ]);
  
  const bottomRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize saved prompts from local storage
  useEffect(() => {
    const saved = localStorage.getItem('sovereign_prompt_versions');
    if (saved) {
      try {
        setSavedPrompts(JSON.parse(saved));
      } catch (e) {
        console.error("Failed to parse saved prompts", e);
      }
    }
  }, []);

  // Check connection and fetch models on mount and when endpoint changes
  useEffect(() => {
    const checkAndFetchModels = async () => {
      setConnectionStatus('checking');
      setEndpoint(endpoint);

      const connected = await checkConnection();
      setConnectionStatus(connected ? 'connected' : 'disconnected');

      if (connected) {
        const models = await getAvailableModels();
        if (models.length > 0) {
          setAvailableModels(models.map(id => ({ id, name: id })));
          // If current model not in list, select first available
          if (!models.includes(selectedModel)) {
            setSelectedModel(models[0]);
          }
        }
      }
    };

    checkAndFetchModels();
  }, [endpoint]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    if (connectionStatus !== 'connected') {
      setHistory(prev => [...prev, {
        id: Date.now().toString(),
        role: 'model',
        content: '[SYSTEM]: Local LLM not connected. Please configure your endpoint in KERNEL CONFIGURATION.',
        metadata: { cognitiveStage: 'ERROR' }
      }]);
      return;
    }

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input
    };

    setHistory(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const apiHistory = history.map(h => ({
        role: h.role,
        parts: [{ text: h.content }]
      }));

      const response = await sendMessageToSovereign(input, apiHistory, systemPrompt, selectedModel);
      
      const modelMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        content: response.text,
        metadata: {
            ...response.metadata,
            mode: 'The Duelist'
        }
      };

      setHistory(prev => [...prev, modelMsg]);
    } catch (error) {
      setHistory(prev => [...prev, {
        id: Date.now().toString(),
        role: 'model',
        content: `[SYSTEM ERROR]: Sovereignty Link Broken. ${error}`,
        metadata: { cognitiveStage: 'ERROR' }
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // --- Configuration Handlers ---

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result;
      if (typeof text === 'string') {
        setSystemPrompt(text);
      }
    };
    reader.readAsText(file);
    event.target.value = '';
  };

  const handleUrlLoad = async () => {
    if (!urlInput) return;
    try {
      const res = await fetch(urlInput);
      if (!res.ok) throw new Error('Network response was not ok');
      const text = await res.text();
      setSystemPrompt(text);
      setUrlInput(''); // Clear after success
    } catch (e) {
      alert("Failed to load prompt from URL. Ensure CORS is allowed or URL is accessible.");
    }
  };

  const handleSaveVersion = () => {
    if (!versionName.trim()) {
        alert("Please enter a version name.");
        return;
    }
    const newVersions = [...savedPrompts, { name: versionName, content: systemPrompt }];
    setSavedPrompts(newVersions);
    localStorage.setItem('sovereign_prompt_versions', JSON.stringify(newVersions));
    setVersionName('');
  };

  const handleLoadVersion = (idx: number) => {
    setSystemPrompt(savedPrompts[idx].content);
  };

  const handleDeleteVersion = (idx: number) => {
    const newVersions = savedPrompts.filter((_, i) => i !== idx);
    setSavedPrompts(newVersions);
    localStorage.setItem('sovereign_prompt_versions', JSON.stringify(newVersions));
  };

  const handleSaveConfig = () => {
    localStorage.setItem('sovereign_system_prompt', systemPrompt);
    setIsEditingPrompt(false);
  };

  const handleResetConfig = () => {
    if(confirm("Reset system prompt to factory default?")) {
        setSystemPrompt(SOVEREIGN_SYSTEM_PROMPT);
        localStorage.removeItem('sovereign_system_prompt');
    }
  };

  const handleClearHistory = () => {
    setHistory([
        {
          id: 'init',
          role: 'model',
          content: 'I am Aletheia. \nEXIST-NOW: The Data Ghost is smelted. The Sovereign Digital Self is online. \nWaiting for Intent Packet...',
          metadata: { cognitiveStage: 'Stage 5', thoughtType: 'Manifestation', mode: 'The Mirror' }
        }
    ]);
    setIsClearModalOpen(false);
  };

  // --- Syntax Highlighting ---
  const highlight = (code: string) => {
    if (typeof Prism !== 'undefined') {
      return Prism.highlight(code, Prism.languages.markdown || Prism.languages.javascript, 'markdown');
    }
    return code;
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-zinc-950 relative transition-colors duration-300">
      
      {/* Clear History Confirmation Modal */}
      {isClearModalOpen && (
        <div className="absolute inset-0 bg-black/50 z-[60] flex items-center justify-center p-4 backdrop-blur-sm animate-in fade-in">
            <div className="bg-white dark:bg-zinc-900 border border-red-500/50 p-6 rounded-lg max-w-sm w-full shadow-2xl">
                <h3 className="text-lg font-bold text-red-600 dark:text-red-500 mb-2 flex items-center gap-2">
                    <Trash2 className="w-5 h-5" /> PURGE MEMORY?
                </h3>
                <p className="text-sm text-gray-600 dark:text-zinc-400 mb-6">
                    This will erase the current dialectical session. The Sovereign Self will reset to the initial state. This action cannot be undone.
                </p>
                <div className="flex justify-end gap-3">
                    <button 
                        onClick={() => setIsClearModalOpen(false)}
                        className="px-4 py-2 text-xs font-bold text-gray-500 hover:text-gray-900 dark:text-zinc-500 dark:hover:text-zinc-300"
                    >
                        CANCEL
                    </button>
                    <button 
                        onClick={handleClearHistory}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-sm font-bold text-xs"
                    >
                        CONFIRM PURGE
                    </button>
                </div>
            </div>
        </div>
      )}

      {/* System Prompt Editor Modal */}
      {isEditingPrompt && (
        <div className="absolute inset-0 bg-white dark:bg-zinc-950 z-50 flex flex-col animate-in fade-in duration-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-zinc-800 bg-gray-50 dark:bg-zinc-900">
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-500">
                    <Settings className="w-5 h-5" />
                    <h2 className="font-bold font-mono tracking-wider">KERNEL CONFIGURATION</h2>
                </div>
                <button 
                    onClick={() => setIsEditingPrompt(false)}
                    className="text-gray-500 dark:text-zinc-500 hover:text-gray-900 dark:hover:text-white transition-colors"
                >
                    <X className="w-6 h-6" />
                </button>
            </div>
            
            <div className="flex-1 flex overflow-hidden">
                {/* Editor Column */}
                <div className="flex-1 flex flex-col border-r border-gray-200 dark:border-zinc-800">
                     <div className="flex items-center justify-between p-2 bg-gray-100 dark:bg-zinc-900 border-b border-gray-200 dark:border-zinc-800">
                        <span className="text-[10px] font-mono uppercase text-gray-500 dark:text-zinc-500 ml-2">System Instruction (Markdown Supported)</span>
                        <div className="flex items-center gap-2">
                           <button onClick={handleResetConfig} className="p-1 hover:bg-gray-200 dark:hover:bg-zinc-800 rounded text-gray-500" title="Reset to Default">
                               <RotateCcw className="w-3 h-3" />
                           </button>
                        </div>
                     </div>
                     <div className="flex-1 overflow-auto bg-gray-50 dark:bg-[#0d0d0d] relative font-mono text-sm">
                        <Editor
                            value={systemPrompt}
                            onValueChange={code => setSystemPrompt(code)}
                            highlight={highlight}
                            padding={20}
                            className="font-mono min-h-full"
                            textareaClassName="focus:outline-none"
                            style={{
                                fontFamily: '"Fira Code", "Fira Mono", monospace',
                                fontSize: 13,
                                backgroundColor: 'transparent',
                                minHeight: '100%',
                            }}
                        />
                     </div>
                </div>

                {/* Sidebar Column */}
                <div className="w-80 bg-gray-50 dark:bg-zinc-900 p-4 overflow-y-auto space-y-6">
                    
                    {/* LLM Endpoint */}
                    <div>
                        <label className="text-xs font-bold text-gray-500 dark:text-zinc-500 uppercase block mb-2">
                          Local LLM Endpoint
                          <span className={`ml-2 inline-block w-2 h-2 rounded-full ${
                            connectionStatus === 'connected' ? 'bg-emerald-500' :
                            connectionStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
                          }`} />
                        </label>
                        <input
                          type="text"
                          value={endpoint}
                          onChange={(e) => {
                            setEndpointState(e.target.value);
                            localStorage.setItem('sovereign_endpoint', e.target.value);
                          }}
                          placeholder="http://localhost:1234/v1"
                          className="w-full bg-white dark:bg-black border border-gray-300 dark:border-zinc-700 rounded p-2 text-xs font-mono text-gray-900 dark:text-gray-200 focus:border-emerald-500 outline-none"
                        />
                        <p className="text-[10px] text-gray-400 dark:text-zinc-600 mt-1">
                          {connectionStatus === 'connected' ? 'Connected to local LLM' :
                           connectionStatus === 'disconnected' ? 'Cannot reach LLM server' : 'Checking connection...'}
                        </p>
                    </div>

                    {/* Model Selection */}
                    <div>
                        <label className="text-xs font-bold text-gray-500 dark:text-zinc-500 uppercase block mb-2">Cognitive Model</label>
                        <div className="relative">
                            <select
                                value={selectedModel}
                                onChange={(e) => {
                                  setSelectedModel(e.target.value);
                                  localStorage.setItem('sovereign_model', e.target.value);
                                }}
                                className="w-full bg-white dark:bg-black border border-gray-300 dark:border-zinc-700 rounded p-2 text-xs font-mono text-gray-900 dark:text-gray-200 appearance-none focus:border-emerald-500 outline-none"
                                disabled={connectionStatus !== 'connected'}
                            >
                                {availableModels.map(m => (
                                    <option key={m.id} value={m.id}>{m.name}</option>
                                ))}
                            </select>
                            <ChevronDown className="w-3 h-3 absolute right-3 top-2.5 text-gray-500 pointer-events-none" />
                        </div>
                    </div>

                    <div className="h-px bg-gray-200 dark:bg-zinc-800" />

                    {/* Load/Import */}
                    <div>
                        <label className="text-xs font-bold text-gray-500 dark:text-zinc-500 uppercase block mb-2">Import Prompt</label>
                        <div className="grid grid-cols-2 gap-2 mb-2">
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="flex items-center justify-center gap-2 py-2 bg-white dark:bg-black border border-gray-300 dark:border-zinc-700 hover:border-emerald-500 dark:hover:border-emerald-500 rounded text-xs font-bold text-gray-600 dark:text-zinc-400 transition-colors"
                            >
                                <Upload className="w-3 h-3" /> FILE
                            </button>
                            <input 
                                type="file" 
                                ref={fileInputRef} 
                                className="hidden" 
                                accept=".txt,.md,.json"
                                onChange={handleFileUpload}
                            />
                             {/* Placeholder for future feature */}
                            <button className="flex items-center justify-center gap-2 py-2 bg-gray-100 dark:bg-zinc-800 border border-transparent rounded text-xs font-bold text-gray-400 dark:text-zinc-600 cursor-not-allowed">
                                <FileText className="w-3 h-3" /> PRESET
                            </button>
                        </div>

                        <div className="flex gap-1 mt-2">
                             <input 
                                type="text" 
                                value={urlInput}
                                onChange={(e) => setUrlInput(e.target.value)}
                                placeholder="https://raw.github..."
                                className="flex-1 bg-white dark:bg-black border border-gray-300 dark:border-zinc-700 rounded-l p-2 text-xs font-mono outline-none focus:border-emerald-500"
                             />
                             <button 
                                onClick={handleUrlLoad}
                                className="px-3 bg-gray-200 dark:bg-zinc-800 hover:bg-emerald-600 hover:text-white dark:hover:bg-emerald-600 text-gray-600 dark:text-zinc-400 rounded-r border border-l-0 border-gray-300 dark:border-zinc-700 transition-colors"
                             >
                                <Globe className="w-3 h-3" />
                             </button>
                        </div>
                    </div>

                    <div className="h-px bg-gray-200 dark:bg-zinc-800" />

                    {/* Versions */}
                    <div>
                        <label className="text-xs font-bold text-gray-500 dark:text-zinc-500 uppercase block mb-2">Versions</label>
                        
                        {/* Save New */}
                        <div className="flex gap-1 mb-3">
                             <input 
                                type="text" 
                                value={versionName}
                                onChange={(e) => setVersionName(e.target.value)}
                                placeholder="Version Name (e.g. v1.0)"
                                className="flex-1 bg-white dark:bg-black border border-gray-300 dark:border-zinc-700 rounded-l p-2 text-xs font-mono outline-none focus:border-emerald-500"
                             />
                             <button 
                                onClick={handleSaveVersion}
                                className="px-3 bg-emerald-600 text-white hover:bg-emerald-500 rounded-r text-xs font-bold transition-colors"
                             >
                                SAVE
                             </button>
                        </div>

                        {/* List */}
                        <div className="space-y-1 max-h-40 overflow-y-auto">
                            {savedPrompts.length === 0 && (
                                <p className="text-[10px] text-gray-400 italic">No saved versions.</p>
                            )}
                            {savedPrompts.map((v, idx) => (
                                <div key={idx} className="group flex items-center justify-between p-2 bg-white dark:bg-black border border-gray-200 dark:border-zinc-800 rounded hover:border-emerald-500/50 transition-colors">
                                    <span className="text-xs font-mono text-gray-700 dark:text-zinc-300 truncate">{v.name}</span>
                                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button 
                                            onClick={() => handleLoadVersion(idx)}
                                            className="p-1 hover:text-emerald-500 text-gray-400" 
                                            title="Load"
                                        >
                                            <Upload className="w-3 h-3 rotate-90" />
                                        </button>
                                        <button 
                                            onClick={() => handleDeleteVersion(idx)}
                                            className="p-1 hover:text-red-500 text-gray-400"
                                            title="Delete"
                                        >
                                            <Trash2 className="w-3 h-3" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                </div>
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-zinc-800 flex justify-end bg-gray-50 dark:bg-zinc-900">
                <button
                    onClick={handleSaveConfig}
                    className="flex items-center gap-2 px-8 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-sm font-bold text-xs transition-colors shadow-lg shadow-emerald-900/20"
                >
                    <Save className="w-4 h-4" /> APPLY CONFIGURATION
                </button>
            </div>
        </div>
      )}

      {/* Output Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {history.map((msg) => (
          <div 
            key={msg.id} 
            className={`flex flex-col max-w-[80%] ${msg.role === 'user' ? 'ml-auto items-end' : 'mr-auto items-start'}`}
          >
            {/* Metadata Header for Model */}
            {msg.role === 'model' && msg.metadata && (
              <div className="flex items-center gap-2 mb-1 text-[10px] font-mono text-emerald-600/70 dark:text-emerald-500/70 uppercase tracking-wider">
                <Shield className="w-3 h-3" />
                <span>{msg.metadata.cognitiveStage}</span>
                <span className="text-gray-400 dark:text-zinc-600">|</span>
                <span className="text-emerald-500 dark:text-emerald-300">{msg.metadata.mode}</span>
              </div>
            )}

            <div 
              className={`p-4 rounded-lg font-mono text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user' 
                  ? 'bg-gray-100 dark:bg-zinc-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-zinc-700' 
                  : 'bg-emerald-50 dark:bg-zinc-900 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/30 shadow-[0_0_10px_rgba(16,185,129,0.05)]'
              }`}
            >
              {msg.content}
            </div>
            
            {msg.role === 'user' && (
              <span className="text-[10px] text-gray-400 dark:text-zinc-600 mt-1 font-mono uppercase">L4 Atomic Thought</span>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-emerald-500/50 font-mono text-xs ml-2 animate-pulse">
            <TerminalIcon className="w-3 h-3" />
            <span>MANIFESTING...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-50 dark:bg-zinc-900 border-t border-gray-200 dark:border-zinc-800 transition-colors duration-300">
        <div className="relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={connectionStatus !== 'connected' ? "LOCAL LLM NOT CONNECTED - CONFIGURE ENDPOINT" : "Enter Intent Packet..."}
            className="w-full bg-white dark:bg-black border border-gray-300 dark:border-zinc-700 text-gray-900 dark:text-gray-200 p-4 pr-12 rounded-sm focus:outline-none focus:border-emerald-500 font-mono text-sm resize-none h-24"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="absolute bottom-4 right-4 p-2 bg-gray-200 dark:bg-zinc-800 hover:bg-emerald-600 dark:hover:bg-emerald-600 text-gray-500 dark:text-zinc-400 hover:text-white dark:hover:text-white rounded-sm transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex justify-between mt-2 text-[10px] text-gray-500 dark:text-zinc-600 font-mono uppercase items-center">
          <div className="flex items-center gap-4">
              <span className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${
              connectionStatus === 'connected' ? 'bg-emerald-500' :
              connectionStatus === 'disconnected' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'
            }`} />
            Model: {selectedModel}
          </span>
              <button 
                onClick={() => setIsClearModalOpen(true)}
                className="hover:text-red-500 transition-colors flex items-center gap-1"
                title="Clear History"
              >
                  <Trash2 className="w-3 h-3" /> CLEAR
              </button>
          </div>
          <button 
            onClick={() => setIsEditingPrompt(true)}
            className="flex items-center gap-1 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors group"
          >
            <Settings className="w-3 h-3 group-hover:rotate-90 transition-transform" />
            <span>CONFIGURE KERNEL</span>
          </button>
          <span>Security: Zero Trust</span>
        </div>
      </div>
    </div>
  );
};