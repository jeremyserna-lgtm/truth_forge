import React, { useState, useRef, useEffect } from 'react';
import { User, SubscriptionTier, SourceCategory, ChatMode, KnowledgeAtom } from '../types';
import { Button } from './Button';
import { 
  Upload, FileText, X, Mic, Image as ImageIcon, Video, Building2, 
  MessageSquare, Zap, Send, Atom, Database, 
  Activity, Layers, Clock, Share2, Loader2, Sparkles, Brain,
  List, HelpCircle, Lightbulb, Play, ArrowRight, CheckCircle2,
  HardDrive, AlertTriangle, ArrowDownToLine, RefreshCw, Trash2
} from 'lucide-react';

interface DataSynthesisProps {
  user: User;
}

// Unified View Type covering all top-level tabs
type MainView = 'DOCUMENTS' | 'IMAGES' | 'VIDEOS' | 'AUDIO' | 'ARCHITECTURE' | 'CHAT' | 'SYNTHESIZE';
type SynthesisTab = 'SUMMARY' | 'KEY_POINTS' | 'TAKEAWAYS' | 'QUESTIONS';

interface FileItem {
  id: string;
  name: string;
  type: string;
  category: SourceCategory;
  status: 'processing' | 'processed' | 'error';
  size: number;
  tokens: number;
  uploadDate: Date;
}

// Extended Atom Interface for local state
interface ExtendedAtom extends KnowledgeAtom {
  activeTab: 'attributes' | 'lineage' | 'resonance';
  sourceIds?: string[]; // IDs of files or atoms this derived from
  originType?: SourceCategory | 'SYSTEM';
}

interface SynthesisResult {
  category: SourceCategory;
  summary: string;
  keyPoints: string[];
  takeaways: string;
  questions: string[];
  epiphany: string;
  sourceCount: number;
}

const MAX_CONTEXT_TOKENS = 1000000;

export const DataSynthesis: React.FC<DataSynthesisProps> = ({ user }) => {
  // Navigation
  const [activeView, setActiveView] = useState<MainView>('DOCUMENTS');
  
  // Synthesis Output State
  const [synthesisTab, setSynthesisTab] = useState<SynthesisTab>('SUMMARY');
  const [lastSynthesis, setLastSynthesis] = useState<SynthesisResult | null>(null);
  const [isProcessingSynthesis, setIsProcessingSynthesis] = useState(false);

  // Chat State
  const [chatMode, setChatMode] = useState<ChatMode>(ChatMode.ENGAGE);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState<{role: 'user' | 'system', content: string}[]>([
      { role: 'system', content: 'Truth Forge Construct initialized. Select a dimension to begin interaction.'}
  ]);
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  // Synthesis Production State
  const [productionType, setProductionType] = useState<'DOC' | 'IMG' | 'VID' | 'AUDIO' | null>(null);
  const [productionSubType, setProductionSubType] = useState<string | null>(null);
  const [generatedArtifact, setGeneratedArtifact] = useState<string | null>(null);

  // File Data
  const [files, setFiles] = useState<FileItem[]>([]);
  
  // Interaction Token Overhead (simulates conversation history growing)
  const [interactionTokens, setInteractionTokens] = useState(0);
  const [isConsolidating, setIsConsolidating] = useState(false);
  const [consolidatedCount, setConsolidatedCount] = useState(0);

  // Atom Data with expansion state
  const [atoms, setAtoms] = useState<ExtendedAtom[]>([
      { id: 'k1', label: 'Self-Sovereignty', description: 'Core axiom regarding user ownership of data.', depth: 1, resonance: 95, type: 'axiom', activeTab: 'attributes', originType: 'SYSTEM' },
      { id: 'k2', label: 'Fluid Tiering', description: 'Dynamic access control based on user resonance.', depth: 3, resonance: 80, type: 'concept', activeTab: 'attributes', originType: 'SYSTEM' },
  ]);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const isFrozen = user.tier === SubscriptionTier.STAGE_3_FROZEN;

  // Reset view state when switching tabs
  useEffect(() => {
    // If we switch views, we might want to clear the 'last synthesis' view to show the new queue
    // But we keep the data in atoms.
    if (lastSynthesis && lastSynthesis.category !== getCurrentCategory(activeView)) {
        setLastSynthesis(null);
    }
  }, [activeView]);

  // --- Calculations ---
  const fileTokens = files.reduce((acc, f) => acc + f.tokens, 0);
  const totalTokens = fileTokens + interactionTokens;
  const usagePercentage = Math.min((totalTokens / MAX_CONTEXT_TOKENS) * 100, 100);
  const isContextFull = totalTokens >= MAX_CONTEXT_TOKENS;

  // --- Helpers ---

  const getFilesForView = (view: MainView) => {
    switch(view) {
      case 'DOCUMENTS': return files.filter(f => f.category === SourceCategory.DOCUMENTS);
      case 'IMAGES': return files.filter(f => f.category === SourceCategory.IMAGES);
      case 'VIDEOS': return files.filter(f => f.category === SourceCategory.VIDEOS);
      case 'AUDIO': return files.filter(f => f.category === SourceCategory.AUDIO);
      default: return [];
    }
  };

  const getCurrentCategory = (view: MainView): SourceCategory => {
      if (view === 'IMAGES') return SourceCategory.IMAGES;
      if (view === 'VIDEOS') return SourceCategory.VIDEOS;
      if (view === 'AUDIO') return SourceCategory.AUDIO;
      return SourceCategory.DOCUMENTS;
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (isContextFull) return;

    if (e.target.files && e.target.files.length > 0) {
      setLastSynthesis(null); // Reset synthesis view on new upload
      const newFiles: FileItem[] = Array.from(e.target.files).map((file: File) => ({
        id: Math.random().toString(36).substr(2, 9),
        name: file.name,
        type: file.type,
        category: getCurrentCategory(activeView),
        status: 'processing',
        size: file.size,
        tokens: 0,
        uploadDate: new Date()
      }));

      setFiles(prev => [...newFiles, ...prev]);

      // Simulate Processing Logic
      newFiles.forEach(file => {
          setTimeout(() => {
              setFiles(prev => prev.map(f => {
                  if (f.id === file.id) {
                      const simulatedTokens = Math.floor(Math.random() * 100000) + 50000;
                      return {
                          ...f,
                          status: 'processed',
                          tokens: simulatedTokens
                      };
                  }
                  return f;
              }));
          }, 1000 + Math.random() * 1000); 
      });
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleRemoveFile = (id: string) => {
      setFiles(prev => prev.filter(f => f.id !== id));
  };
  
  const handleClearQueue = () => {
      const category = getCurrentCategory(activeView);
      setFiles(prev => prev.filter(f => f.category !== category));
      setLastSynthesis(null);
  };

  const handleConsolidateContext = () => {
      setIsConsolidating(true);
      // Create archival atoms so data isn't "lost"
      const archivedAtoms: ExtendedAtom[] = files.map(f => ({
          id: `arch-${f.id}`,
          label: f.name,
          description: `Archived ${f.category} source.`,
          depth: 1,
          resonance: 5,
          type: 'axiom',
          activeTab: 'attributes',
          originType: f.category,
          sourceIds: []
      }));

      setTimeout(() => {
          setConsolidatedCount(prev => prev + files.length);
          setAtoms(prev => [...prev, ...archivedAtoms]);
          setFiles([]); // Clear context globally
          setInteractionTokens(0);
          setLastSynthesis(null);
          setIsConsolidating(false);
      }, 2000);
  };

  const getDynamicEpiphany = (category: string) => {
    const epiphanies = [
        `Synthesizing this ${category.toLowerCase()} group revealed a gap in previous logic: The user creates the structure, but the structure must also be able to modify the user's permissions.`,
        `Analysis of the ${category.toLowerCase()} vectors suggests a latent desire for 'Unsupervised Creation'. The current constraints are generating friction.`,
        `A recursive pattern was found in the ${category.toLowerCase()} metadata: The concept of 'Identity' is being redefined as a fluid resource rather than a static ID.`,
        `The ${category.toLowerCase()} input contradicts earlier axioms of 'Fixed Storage'. Data is behaving more like a stream than a deposit.`
    ];
    return epiphanies[Math.floor(Math.random() * epiphanies.length)];
  };

  const handleTriggerSynthesis = () => {
      const activeFiles = getFilesForView(activeView);
      if (activeFiles.length === 0 || isContextFull) return;
      
      setIsProcessingSynthesis(true);
      setInteractionTokens(prev => prev + 50000); 

      // 1. Prepare Mock Data based on View
      const category = getCurrentCategory(activeView);
      const sourceNames = activeFiles.map(f => f.name).join(', ');
      
      const mockResult: SynthesisResult = {
          category,
          sourceCount: activeFiles.length,
          summary: `The aggregated ${category.toLowerCase()} context from ${activeFiles.length} sources (${sourceNames}) suggests a unified focus on recursive architecture. The data indicates a shift from static storage to dynamic state management.`,
          keyPoints: [
              "Self-Sovereignty: User data is axiomatically owned.",
              "Recursive Logic: System outputs feed back into inputs.",
              "Fluid Tiering: Access levels adapt to resonance."
          ],
          takeaways: "The primary takeaway is that the architecture must support 'Living Documents'. Static files are merely snapshots of a continuous truth.",
          questions: [
              "How do we reconcile conflict between legacy documents?",
              `What is the entropy decay rate for the uploaded ${category.toLowerCase()}?`,
              "Should the Manifesto override conflicting financial data?"
          ],
          epiphany: getDynamicEpiphany(category)
      };

      setTimeout(() => {
          // 2. Convert Files to Source Atoms
          const sourceAtoms: ExtendedAtom[] = activeFiles.map(f => ({
              id: `src-${f.id}`,
              label: f.name,
              description: `Ingested ${f.category} source. Size: ${f.size}b.`,
              depth: 1,
              resonance: 10,
              type: 'axiom',
              activeTab: 'attributes',
              originType: f.category
          }));

          // 3. Convert Synthesis Artifacts to Derivative Atoms
          const derivativeAtoms: ExtendedAtom[] = [
              // Summary Atom
              {
                  id: `syn-sum-${Date.now()}`,
                  label: `${category} Synthesis Summary`,
                  description: mockResult.summary.substring(0, 100) + "...",
                  depth: 3,
                  resonance: 85,
                  type: 'derivative',
                  activeTab: 'attributes',
                  originType: category,
                  sourceIds: activeFiles.map(f => f.id)
              },
              // Takeaway Atom
              {
                  id: `syn-take-${Date.now()}`,
                  label: "Core Takeaway",
                  description: mockResult.takeaways,
                  depth: 4,
                  resonance: 90,
                  type: 'derivative',
                  activeTab: 'attributes',
                  originType: category,
                  sourceIds: activeFiles.map(f => f.id)
              },
              // Epiphany Atom (Concept)
              {
                  id: `syn-epi-${Date.now()}`,
                  label: "System Epiphany: Fluid Tiering",
                  description: mockResult.epiphany,
                  depth: 8,
                  resonance: 100,
                  type: 'concept',
                  activeTab: 'attributes',
                  originType: 'SYSTEM',
                  sourceIds: activeFiles.map(f => f.id)
              }
          ];

          // 4. Update State: Add atoms, Clear processed files, Set result
          setAtoms(prev => [...derivativeAtoms, ...sourceAtoms, ...prev]);
          setFiles(prev => prev.filter(f => f.category !== category)); // Clear queue for this category
          setLastSynthesis(mockResult);
          setIsProcessingSynthesis(false);
      }, 2000);
  };

  const handleChatSubmit = () => {
    if (!chatInput.trim() || isContextFull) return;
    
    // Chat consumes tokens
    const inputTokens = Math.floor(chatInput.length / 4);
    const outputTokens = 1500; 
    setInteractionTokens(prev => prev + inputTokens + outputTokens);

    setChatHistory(prev => [...prev, { role: 'user', content: chatInput }]);
    setChatInput('');
    setIsSynthesizing(true);
    setTimeout(() => {
        setChatHistory(prev => [...prev, { role: 'system', content: `[${chatMode} Mode]: Processed input. Updating internal vectors.` }]);
        setIsSynthesizing(false);
    }, 1000);
  };

  const handleProduction = () => {
    if (isContextFull) return;
    setIsSynthesizing(true);
    setInteractionTokens(prev => prev + 25000); 

    setTimeout(() => {
      setGeneratedArtifact(`Generated ${productionSubType} (${productionType})... \n\nContent initialized successfully.`);
      setIsSynthesizing(false);
    }, 2000);
  };

  const handleResetSynthesis = () => {
      setLastSynthesis(null);
  };

  // --- Render Sections ---

  const renderVisualizer = () => {
    const activeFiles = getFilesForView(activeView);
    const hasFiles = activeFiles.length > 0;
    
    if (isConsolidating) {
        return (
            <div className="flex-1 p-8 flex flex-col items-center justify-center bg-[#0D0D0D] relative overflow-hidden">
                <div className="relative z-10 flex flex-col items-center animate-pulse">
                    <Database size={64} className="text-[#F59E0B] mb-6" />
                    <h2 className="text-2xl font-serif text-[#F5F0E6] uppercase tracking-wide mb-2">Consolidating Memory</h2>
                    <p className="text-sm font-mono text-[#888888]">Transferring context vectors to persistent storage...</p>
                </div>
                <div className="absolute inset-0 bg-gradient-to-t from-[#F59E0B]/5 to-transparent"></div>
            </div>
        );
    }

    return (
      <div className="flex-1 p-8 flex flex-col relative bg-[#0D0D0D]">
         <div className="absolute inset-0 opacity-5" style={{ backgroundImage: 'radial-gradient(#4A4A4A 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
         
         <div className="relative z-10 flex-1 flex flex-col">
             <header className="mb-6 flex justify-between items-start">
                 <div>
                    <h2 className="text-2xl font-serif text-[#F5F0E6] uppercase tracking-wide">
                        {activeView} AGGREGATION
                    </h2>
                    <p className="text-xs font-mono text-[#888888] mt-1">
                        Visualizing semantic density and asset distribution.
                    </p>
                 </div>
                 {isContextFull && (
                     <div className="flex items-center space-x-2 bg-red-900/20 border border-red-500/50 px-3 py-2 rounded-sm animate-pulse">
                         <AlertTriangle size={16} className="text-red-400" />
                         <span className="text-xs font-mono text-red-400 uppercase tracking-wide">Context Window Full</span>
                     </div>
                 )}
             </header>

             {/* Main Content Area */}
             <div className="flex-1 flex flex-col items-center justify-center transition-all duration-500">
                 
                 {/* STATE 1: VIEWING SYNTHESIS RESULT (Files Cleared) */}
                 {lastSynthesis ? (
                    <div className="w-full h-full flex flex-col space-y-6 animate-in fade-in zoom-in-95 duration-500">
                        <div className="flex justify-between items-center bg-[#1A1A1A] p-2 border border-[#2D2D2D] rounded-sm">
                            <span className="text-xs font-mono text-[#F59E0B] flex items-center">
                                <CheckCircle2 size={12} className="mr-2"/>
                                Context Synthesized & Queued to Atoms
                            </span>
                            <Button size="sm" variant="secondary" onClick={handleResetSynthesis} icon={<RefreshCw size={12}/>}>
                                New Batch
                            </Button>
                        </div>
                        
                        {/* 1. Synthesis Output Tabs */}
                        <div className="bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm overflow-hidden flex flex-col flex-1">
                            <div className="flex border-b border-[#2D2D2D]">
                                {[
                                    { id: 'SUMMARY', icon: <FileText size={14}/>, label: 'Summary' },
                                    { id: 'KEY_POINTS', icon: <List size={14}/>, label: 'Key Points' },
                                    { id: 'TAKEAWAYS', icon: <Lightbulb size={14}/>, label: 'Takeaways' },
                                    { id: 'QUESTIONS', icon: <HelpCircle size={14}/>, label: 'Future Questions' },
                                ].map((tab) => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setSynthesisTab(tab.id as SynthesisTab)}
                                        className={`
                                            flex-1 py-3 flex items-center justify-center space-x-2 text-xs font-mono uppercase tracking-wider transition-colors
                                            ${synthesisTab === tab.id 
                                                ? 'bg-[#2D2D2D] text-[#F5F0E6] border-b-2 border-[#F59E0B]' 
                                                : 'text-[#888888] hover:bg-[#232323] hover:text-[#B5B5B5]'}
                                        `}
                                    >
                                        {tab.icon}
                                        <span>{tab.label}</span>
                                    </button>
                                ))}
                            </div>
                            <div className="p-6 flex-1 overflow-y-auto custom-scrollbar bg-[#0D0D0D]/50">
                                <div className="text-sm font-sans text-[#F5F0E6] leading-relaxed">
                                    {synthesisTab === 'SUMMARY' && lastSynthesis.summary}
                                    {synthesisTab === 'KEY_POINTS' && (
                                        <ul className="list-disc list-inside space-y-2 text-[#F5F0E6]">
                                            {lastSynthesis.keyPoints.map((pt, i) => <li key={i}>{pt}</li>)}
                                        </ul>
                                    )}
                                    {synthesisTab === 'TAKEAWAYS' && lastSynthesis.takeaways}
                                    {synthesisTab === 'QUESTIONS' && (
                                        <div className="space-y-2">
                                            {lastSynthesis.questions.map((q, i) => <p key={i} className="text-[#F5F0E6]">{i+1}. {q}</p>)}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* 2. Metrics */}
                        <div className="grid grid-cols-3 gap-4 h-32">
                            <div className="bg-[#151515] border border-[#2D2D2D] rounded-sm p-4 flex flex-col items-center justify-center">
                                <div className="text-3xl font-serif text-[#F5F0E6]">{lastSynthesis.sourceCount + 3}</div>
                                <div className="text-[10px] font-mono text-[#888888] uppercase mt-1">New Atoms Created</div>
                            </div>
                            
                            <div className="bg-[#151515] border border-[#2D2D2D] rounded-sm p-4 flex flex-col items-center justify-center">
                                <div className="text-3xl font-serif text-[#F5F0E6]">{lastSynthesis.sourceCount}</div>
                                <div className="text-[10px] font-mono text-[#888888] uppercase mt-1">Sources Processed</div>
                            </div>

                            <div className="bg-[#151515] border border-[#F59E0B]/30 rounded-sm p-4 flex flex-col items-center justify-center relative overflow-hidden">
                                <div className="absolute inset-0 bg-[#F59E0B]/5 animate-pulse"></div>
                                <div className="text-lg font-serif text-[#F59E0B] text-center leading-tight relative z-10">
                                    "Recursive Sovereignty"
                                </div>
                                <div className="text-[10px] font-mono text-[#888888] uppercase mt-2 relative z-10">Core Truth Identified</div>
                            </div>
                        </div>

                        {/* 3. System Epiphany */}
                        <div className="bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm p-5 flex items-start space-x-4">
                            <div className="p-2 bg-[#0D0D0D] border border-[#2D2D2D] rounded-full mt-1">
                                <Sparkles size={16} className="text-[#F59E0B]" />
                            </div>
                            <div>
                                <h4 className="text-xs font-mono text-[#F59E0B] uppercase tracking-wide mb-1">System Epiphany</h4>
                                <p className="text-xs text-[#888888] italic">
                                    "{lastSynthesis.epiphany}"
                                </p>
                            </div>
                        </div>
                    </div>
                 ) : !hasFiles ? (
                     // STATE 2: EMPTY STATE
                     <div className="text-center opacity-50 border border-[#2D2D2D] bg-[#1A1A1A]/50 p-12 rounded-sm w-full h-full flex flex-col items-center justify-center">
                         <div className="w-16 h-16 rounded-full border border-dashed border-[#4A4A4A] flex items-center justify-center mx-auto mb-4">
                             <Upload size={24} className="text-[#4A4A4A]"/>
                         </div>
                         <p className="text-sm font-mono text-[#888888] uppercase tracking-wider">No signals detected</p>
                         <p className="text-xs text-[#4A4A4A] mt-2">Upload {activeView.toLowerCase()} to queue context</p>
                     </div>
                 ) : (
                     // STATE 3: QUEUE READY
                     <div className="w-full h-full border border-[#2D2D2D] bg-[#1A1A1A]/50 rounded-sm p-12 flex flex-col items-center justify-center space-y-6">
                         <div className="text-center space-y-2">
                             <Layers size={48} className="text-[#F5F0E6] mx-auto mb-4" />
                             <h3 className="text-xl font-serif text-[#F5F0E6] uppercase">Context Queued</h3>
                             <p className="text-sm font-mono text-[#888888] max-w-md mx-auto">
                                 {activeFiles.length} signals ready for ingestion. System is standing by to integrate these sources into a unified understanding.
                             </p>
                         </div>
                         <Button 
                            size="lg" 
                            onClick={handleTriggerSynthesis} 
                            isLoading={isProcessingSynthesis}
                            disabled={isContextFull}
                            icon={<Zap size={16}/>}
                         >
                             {isContextFull ? 'Context Full - Consolidate First' : 'Synthesize Context'}
                         </Button>
                     </div>
                 )}
             </div>
         </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-[#0D0D0D] overflow-hidden">
      
      {/* --- TOP HORIZONTAL NAVIGATION --- */}
      <div className="h-14 bg-[#0D0D0D] border-b border-[#2D2D2D] flex items-center px-4 space-x-1">
          {[
              { id: 'DOCUMENTS', icon: <FileText size={14}/>, label: 'Documents' },
              { id: 'IMAGES', icon: <ImageIcon size={14}/>, label: 'Images' },
              { id: 'VIDEOS', icon: <Video size={14}/>, label: 'Videos' },
              { id: 'AUDIO', icon: <Mic size={14}/>, label: 'Audio' },
          ].map((tab) => (
              <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id as MainView)}
                  className={`
                      h-full px-4 flex items-center space-x-2 border-b-2 text-xs font-mono uppercase tracking-wider transition-colors
                      ${activeView === tab.id 
                          ? 'border-[#F5F0E6] text-[#F5F0E6] bg-[#1A1A1A]' 
                          : 'border-transparent text-[#888888] hover:text-[#B5B5B5] hover:bg-[#151515]'}
                  `}
              >
                  {tab.icon}
                  <span>{tab.label}</span>
              </button>
          ))}
          
          <div className="h-6 w-[1px] bg-[#2D2D2D] mx-2"></div>

          {[
              { id: 'ARCHITECTURE', icon: <Building2 size={14}/>, label: 'Architecture' },
              { id: 'CHAT', icon: <MessageSquare size={14}/>, label: 'Chat' },
              { id: 'SYNTHESIZE', icon: <Zap size={14}/>, label: 'Synthesize' },
          ].map((tab) => (
              <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id as MainView)}
                  className={`
                      h-full px-4 flex items-center space-x-2 border-b-2 text-xs font-mono uppercase tracking-wider transition-colors
                      ${activeView === tab.id 
                          ? 'border-[#F59E0B] text-[#F59E0B] bg-[#1A1A1A]' 
                          : 'border-transparent text-[#888888] hover:text-[#B5B5B5] hover:bg-[#151515]'}
                  `}
              >
                  {tab.icon}
                  <span>{tab.label}</span>
              </button>
          ))}
      </div>

      {/* --- MAIN CONTENT --- */}
      <div className="flex-1 flex overflow-hidden relative bg-[#0D0D0D]">

          {/* 1. SOURCE TABS (DOC/IMG/VID/AUDIO) */}
          {['DOCUMENTS', 'IMAGES', 'VIDEOS', 'AUDIO'].includes(activeView) && (
              <>
                {/* Left Queue & Context Meter */}
                <div className="w-72 bg-[#151515] border-r border-[#2D2D2D] flex flex-col flex-shrink-0">
                    <div className="p-4 border-b border-[#2D2D2D] flex justify-between items-center">
                         <span className="font-mono text-xs text-[#888888] uppercase tracking-widest">{activeView} Queue</span>
                         <div className="flex items-center space-x-2">
                             <span className="text-[10px] font-mono text-[#4A4A4A]">{getFilesForView(activeView).length} items</span>
                             {getFilesForView(activeView).length > 0 && (
                                 <button onClick={handleClearQueue} className="text-[#4A4A4A] hover:text-red-400" title="Clear All">
                                     <Trash2 size={12} />
                                 </button>
                             )}
                         </div>
                    </div>
                    
                    {/* File List */}
                    <div className="flex-1 overflow-y-auto p-3 space-y-2">
                         {getFilesForView(activeView).length === 0 && (
                             <div className="text-center py-8 opacity-50">
                                 <p className="text-[10px] font-mono text-[#4A4A4A]">Queue Empty</p>
                             </div>
                         )}
                         {getFilesForView(activeView).map((file) => (
                            <div key={file.id} className="p-3 bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm flex items-center justify-between group animate-in slide-in-from-left-2 duration-300">
                                <div className="flex items-center space-x-3 overflow-hidden">
                                    <div className={file.status === 'processing' ? 'animate-pulse text-[#F59E0B]' : 'text-[#888888]'}>
                                        {activeView === 'IMAGES' ? <ImageIcon size={14} /> : 
                                         activeView === 'VIDEOS' ? <Video size={14} /> :
                                         activeView === 'AUDIO' ? <Mic size={14} /> : <FileText size={14} />}
                                    </div>
                                    <div className="min-w-0">
                                        <div className="text-xs font-mono text-[#F5F0E6] truncate">{file.name}</div>
                                        {file.status === 'processing' ? (
                                            <div className="text-[8px] text-[#F59E0B] font-mono uppercase">Reading...</div>
                                        ) : (
                                            <div className="text-[8px] text-[#4A4A4A] font-mono">~{file.tokens.toLocaleString()} tokens</div>
                                        )}
                                    </div>
                                </div>
                                <button 
                                    onClick={() => handleRemoveFile(file.id)}
                                    className="text-[#4A4A4A] hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <X size={14} />
                                </button>
                            </div>
                         ))}
                    </div>

                    {/* CONTEXT METER / UPLOAD SECTION */}
                    <div className="p-4 border-t border-[#2D2D2D] bg-[#1A1A1A]">
                        {/* Meter */}
                        <div className="mb-4">
                            <div className="flex justify-between items-end mb-1">
                                <span className={`text-[10px] font-mono uppercase tracking-wider ${isContextFull ? 'text-red-400' : 'text-[#888888]'}`}>
                                    Context Window
                                </span>
                                <span className={`text-[10px] font-mono ${isContextFull ? 'text-red-400 font-bold' : 'text-[#F5F0E6]'}`}>
                                    {Math.round(totalTokens / 1000)}k / 1M
                                </span>
                            </div>
                            <div className="h-1.5 w-full bg-[#0D0D0D] rounded-full overflow-hidden border border-[#2D2D2D]">
                                <div 
                                    className={`h-full transition-all duration-500 ease-out ${isContextFull ? 'bg-red-500' : usagePercentage > 80 ? 'bg-orange-500' : 'bg-[#F5F0E6]'}`}
                                    style={{ width: `${usagePercentage}%` }}
                                ></div>
                            </div>
                        </div>

                        {/* Actions */}
                        {isContextFull ? (
                            <Button 
                                fullWidth 
                                variant="primary" 
                                className="bg-red-900/20 text-red-200 border border-red-900 hover:bg-red-900/40"
                                onClick={handleConsolidateContext}
                                icon={<ArrowDownToLine size={14}/>}
                                isLoading={isConsolidating}
                            >
                                Consolidate to Memory
                            </Button>
                        ) : (
                            <div className="space-y-2">
                                <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileSelect} multiple />
                                <Button fullWidth size="sm" variant="secondary" icon={<Upload size={14} />} onClick={() => fileInputRef.current?.click()} disabled={isFrozen}>
                                    Upload {activeView === 'DOCUMENTS' ? 'File' : activeView === 'IMAGES' ? 'Image' : 'Media'}
                                </Button>
                                {files.length > 0 && (
                                    <Button fullWidth size="sm" className="bg-[#1A1A1A] border border-[#2D2D2D] text-[#888888] hover:text-[#F5F0E6]" icon={<ArrowDownToLine size={14}/>} onClick={handleConsolidateContext} isLoading={isConsolidating}>
                                        Offload to Memory
                                    </Button>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* Middle Visualizer */}
                {renderVisualizer()}
              </>
          )}

          {/* 2. ARCHITECTURE (Long Term Memory) */}
          {activeView === 'ARCHITECTURE' && (
              <div className="flex-1 p-12 overflow-y-auto custom-scrollbar flex flex-col items-center">
                  <header className="mb-12 text-center max-w-2xl">
                      <div className="inline-flex items-center justify-center p-3 rounded-full bg-[#1A1A1A] border border-[#2D2D2D] mb-4">
                          <Database size={24} className="text-[#F59E0B]" />
                      </div>
                      <h2 className="text-3xl font-serif text-[#F5F0E6] uppercase tracking-wide">
                          Long-Term Memory
                      </h2>
                      <p className="text-sm font-mono text-[#888888] mt-4 leading-relaxed">
                          This layer consolidates out-of-context data streams into persistent structural knowledge. 
                          These elements are not immediately active in the input stream but are constantly considered by the construct for pattern matching and deep retrieval.
                      </p>
                  </header>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
                      {/* Summary Block 1 */}
                      <div className="bg-[#1A1A1A] border border-[#2D2D2D] p-6 rounded-sm">
                          <div className="flex items-center justify-between mb-4">
                              <span className="text-xs font-mono text-[#F59E0B] uppercase tracking-widest">Condensed History</span>
                              <Clock size={14} className="text-[#4A4A4A]"/>
                          </div>
                          <div className="space-y-3">
                              <div className="text-sm text-[#F5F0E6] leading-relaxed line-clamp-3">
                                  "User interaction patterns suggest a preference for recursive logic frameworks. Previous sessions regarding 'Self-Sovereignty' have been crystallized into core axioms."
                              </div>
                              <div className="h-1 w-full bg-[#2D2D2D] mt-2"><div className="h-full w-2/3 bg-[#F59E0B]"></div></div>
                              <div className="text-[10px] font-mono text-[#888888] text-right">Consolidated 2h ago</div>
                          </div>
                      </div>

                      {/* Summary Block 2 */}
                      <div className="bg-[#1A1A1A] border border-[#2D2D2D] p-6 rounded-sm">
                          <div className="flex items-center justify-between mb-4">
                              <span className="text-xs font-mono text-[#F59E0B] uppercase tracking-widest">Dormant Vectors</span>
                              <Layers size={14} className="text-[#4A4A4A]"/>
                          </div>
                          <div className="flex flex-wrap gap-2">
                              {['Semantic drift', 'Legacy Auth', 'Tier 2 Protocols', 'Unresolved Queries'].map(tag => (
                                  <span key={tag} className="px-2 py-1 bg-[#0D0D0D] border border-[#2D2D2D] text-[10px] font-mono text-[#888888]">{tag}</span>
                              ))}
                              {consolidatedCount > 0 && (
                                  <span className="px-2 py-1 bg-[#F59E0B]/20 border border-[#F59E0B]/50 text-[10px] font-mono text-[#F59E0B]">
                                      +{consolidatedCount} Recent Batches
                                  </span>
                              )}
                          </div>
                      </div>

                      {/* Deep Storage Visual */}
                      <div className="col-span-1 md:col-span-2 bg-[#0D0D0D] border border-[#2D2D2D] p-8 flex items-center justify-center relative overflow-hidden">
                          <div className="absolute inset-0 flex items-center justify-center opacity-20 pointer-events-none">
                              <Atom size={200} className="text-[#F59E0B] animate-spin-slow" />
                          </div>
                          <div className="relative z-10 text-center">
                              <div className="text-4xl font-mono text-[#F5F0E6]">4.2 PB</div>
                              <div className="text-xs font-mono text-[#888888] uppercase mt-2">Total Knowledge Capacity</div>
                              {consolidatedCount > 0 && <div className="text-xs text-[#4A4A4A] mt-1">Recently consolidated {consolidatedCount} items</div>}
                          </div>
                      </div>
                  </div>
              </div>
          )}

          {/* 3. CHAT (Bottom-aligned Dimensions) */}
          {activeView === 'CHAT' && (
              <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full border-x border-[#2D2D2D] bg-[#0D0D0D]">
                  {/* Chat Output */}
                  <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
                      {chatHistory.map((msg, idx) => (
                          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                              <div className={`
                                  max-w-[80%] p-4 rounded-sm border text-sm font-mono leading-relaxed
                                  ${msg.role === 'user' 
                                      ? 'bg-[#1A1A1A] border-[#2D2D2D] text-[#F5F0E6]' 
                                      : 'bg-transparent border-[#4A4A4A] text-[#888888]'}
                              `}>
                                  {msg.content}
                              </div>
                          </div>
                      ))}
                      {isSynthesizing && (
                          <div className="flex justify-start">
                              <div className="flex items-center space-x-2 text-[#888888] text-xs font-mono uppercase p-4">
                                  <span className="w-2 h-2 bg-[#F59E0B] rounded-full animate-pulse"></span>
                                  <span>System Thinking...</span>
                              </div>
                          </div>
                      )}
                      
                      {isContextFull && (
                           <div className="flex justify-center my-4">
                              <div className="bg-red-900/20 border border-red-900/50 text-red-300 px-4 py-2 rounded-sm text-xs font-mono uppercase flex items-center">
                                  <AlertTriangle size={12} className="mr-2" />
                                  Context Full. Consolidate to continue.
                              </div>
                           </div>
                      )}
                  </div>

                  {/* Chat Input Area with Dimensions */}
                  <div className="p-6 border-t border-[#2D2D2D] bg-[#151515]">
                      
                      {/* Dimensions Control */}
                      <div className="flex items-center justify-center mb-4">
                          <div className="bg-[#0D0D0D] p-1 rounded-full border border-[#2D2D2D] flex space-x-1">
                              {[ChatMode.ENGAGE, ChatMode.ORGANIZE, ChatMode.ASK].map((mode) => (
                                  <button
                                      key={mode}
                                      onClick={() => setChatMode(mode)}
                                      className={`
                                          px-4 py-1 rounded-full text-[10px] font-mono uppercase tracking-wider transition-all
                                          ${chatMode === mode 
                                              ? 'bg-[#F59E0B] text-[#0D0D0D] shadow-sm' 
                                              : 'text-[#888888] hover:text-[#F5F0E6]'}
                                      `}
                                  >
                                      {mode}
                                  </button>
                              ))}
                          </div>
                      </div>

                      <div className="relative">
                          <input
                              type="text"
                              value={chatInput}
                              onChange={(e) => setChatInput(e.target.value)}
                              onKeyDown={(e) => e.key === 'Enter' && handleChatSubmit()}
                              placeholder={isContextFull ? "Context limit reached..." : `Command the construct (${chatMode} dimension)...`}
                              disabled={isContextFull}
                              className={`
                                w-full bg-[#1A1A1A] border rounded-full py-4 pl-6 pr-14 text-sm font-mono focus:outline-none transition-colors
                                ${isContextFull 
                                    ? 'border-red-900 text-red-900 placeholder-red-900/50 cursor-not-allowed' 
                                    : 'border-[#2D2D2D] text-[#F5F0E6] focus:border-[#F59E0B]'}
                              `}
                          />
                          <button 
                              onClick={handleChatSubmit}
                              disabled={isContextFull}
                              className={`
                                absolute right-2 top-2 bottom-2 w-10 h-10 rounded-full flex items-center justify-center transition-all
                                ${isContextFull 
                                    ? 'bg-[#2D2D2D] text-[#4A4A4A] cursor-not-allowed' 
                                    : 'bg-[#2D2D2D] hover:bg-[#F59E0B] hover:text-[#0D0D0D] text-[#F5F0E6]'}
                              `}
                          >
                              <Send size={16} />
                          </button>
                      </div>
                  </div>
              </div>
          )}

          {/* 4. SYNTHESIZE (Granular Atoms + Production) */}
          {activeView === 'SYNTHESIZE' && (
              <div className="flex-1 flex overflow-hidden bg-[#0D0D0D]">
                   {/* Left Panel: Granular Knowledge Atoms */}
                   <div className="w-96 bg-[#151515] border-r border-[#2D2D2D] flex flex-col">
                       <div className="p-4 border-b border-[#2D2D2D]">
                           <h3 className="text-xs font-mono text-[#888888] uppercase tracking-widest">Knowledge Atoms</h3>
                           <p className="text-[10px] text-[#4A4A4A] mt-1">Distilled Truths available for synthesis</p>
                       </div>
                       <div className="flex-1 overflow-y-auto p-4 space-y-4">
                           {atoms.map(atom => (
                               <div key={atom.id} className="bg-[#1A1A1A] border border-[#2D2D2D] rounded-sm group overflow-hidden transition-all duration-300">
                                   {/* Header */}
                                   <div className="p-3 bg-[#1A1A1A] border-b border-[#2D2D2D] flex justify-between items-start cursor-pointer hover:bg-[#232323]">
                                       <div>
                                            <div className="flex items-center space-x-2 mb-1">
                                                <span className={`w-2 h-2 rounded-full ${atom.type === 'axiom' ? 'bg-[#F59E0B]' : atom.type === 'derivative' ? 'bg-purple-500' : 'bg-blue-500'}`}></span>
                                                <span className="text-xs font-mono text-[#F5F0E6] font-bold">{atom.label}</span>
                                            </div>
                                            <div className="text-[10px] text-[#888888]">{atom.description}</div>
                                       </div>
                                       <span className="text-[10px] font-mono text-[#4A4A4A]">Res:{atom.resonance}%</span>
                                   </div>
                                   
                                   {/* Tabs */}
                                   <div className="flex border-b border-[#2D2D2D] bg-[#0D0D0D]">
                                       <button onClick={() => setAtoms(prev => prev.map(a => a.id === atom.id ? {...a, activeTab: 'attributes'} : a))} className={`flex-1 py-1.5 text-[10px] font-mono uppercase ${atom.activeTab === 'attributes' ? 'text-[#F5F0E6] bg-[#232323]' : 'text-[#4A4A4A] hover:text-[#888888]'}`}>Attributes</button>
                                       <button onClick={() => setAtoms(prev => prev.map(a => a.id === atom.id ? {...a, activeTab: 'lineage'} : a))} className={`flex-1 py-1.5 text-[10px] font-mono uppercase ${atom.activeTab === 'lineage' ? 'text-[#F5F0E6] bg-[#232323]' : 'text-[#4A4A4A] hover:text-[#888888]'}`}>Lineage</button>
                                       <button onClick={() => setAtoms(prev => prev.map(a => a.id === atom.id ? {...a, activeTab: 'resonance'} : a))} className={`flex-1 py-1.5 text-[10px] font-mono uppercase ${atom.activeTab === 'resonance' ? 'text-[#F5F0E6] bg-[#232323]' : 'text-[#4A4A4A] hover:text-[#888888]'}`}>Resonance</button>
                                   </div>

                                   {/* Content */}
                                   <div className="p-3 bg-[#0D0D0D]">
                                       {atom.activeTab === 'attributes' && (
                                           <div className="space-y-1">
                                               <div className="flex justify-between text-[10px] font-mono text-[#888888]"><span>Depth</span> <span className="text-[#F5F0E6]">{atom.depth}</span></div>
                                               <div className="flex justify-between text-[10px] font-mono text-[#888888]"><span>Origin</span> <span className="text-[#F5F0E6]">{atom.originType}</span></div>
                                           </div>
                                       )}
                                       {atom.activeTab === 'lineage' && (
                                           <div className="text-[10px] font-mono text-[#888888]">
                                              {atom.sourceIds ? (
                                                  <>Derived from {atom.sourceIds.length} source(s).</>
                                              ) : (
                                                  <>Foundational Axiom (No antecedent)</>
                                              )}
                                           </div>
                                       )}
                                       {atom.activeTab === 'resonance' && (
                                           <div className="text-[10px] font-mono text-[#888888]">
                                               Highly active in <span className="text-[#F59E0B]">Architecture Sector 4</span>.
                                           </div>
                                       )}
                                   </div>
                               </div>
                           ))}
                       </div>
                   </div>

                   {/* Main Panel: Production Studio */}
                   <div className="flex-1 flex flex-col p-8 relative">
                       <div className="mb-8">
                           <h2 className="text-2xl font-serif text-[#F5F0E6] uppercase tracking-wide flex items-center">
                               <Zap className="mr-3 text-[#F59E0B]" size={24}/>
                               Production Studio
                           </h2>
                           <p className="text-sm font-mono text-[#888888] mt-2">
                               Recursion loop: Select output format and iteration type.
                           </p>
                           {isContextFull && <p className="text-xs text-red-400 mt-2 font-mono">WARNING: Context limit reached. Production may be truncated.</p>}
                       </div>

                       {/* 1. Format Selection */}
                       <div className="grid grid-cols-4 gap-4 mb-6">
                           {[
                               { id: 'DOC', label: 'Document', icon: <FileText size={20}/> },
                               { id: 'IMG', label: 'Image', icon: <ImageIcon size={20}/> },
                               { id: 'VID', label: 'Video', icon: <Video size={20}/> },
                               { id: 'AUDIO', label: 'Audio', icon: <Mic size={20}/> },
                           ].map((type) => (
                               <button 
                                   key={type.id}
                                   onClick={() => { setProductionType(type.id as any); setProductionSubType(null); }}
                                   disabled={isContextFull}
                                   className={`
                                       flex flex-col items-center justify-center p-4 border rounded-sm transition-all
                                       ${productionType === type.id 
                                           ? 'bg-[#F5F0E6] text-[#0D0D0D] border-[#F5F0E6]' 
                                           : isContextFull 
                                                ? 'bg-[#1A1A1A] border-[#2D2D2D] text-[#4A4A4A] cursor-not-allowed'
                                                : 'bg-[#1A1A1A] border-[#2D2D2D] text-[#888888] hover:border-[#F5F0E6] hover:text-[#F5F0E6]'}
                                   `}
                               >
                                   {type.icon}
                                   <span className="text-[10px] font-mono uppercase tracking-wider mt-2">{type.label}</span>
                               </button>
                           ))}
                       </div>

                       {/* 2. Sub-Type Selection & Preview */}
                       {productionType && (
                           <div className="bg-[#151515] border border-[#2D2D2D] rounded-sm p-6 flex flex-col flex-1 animate-in fade-in slide-in-from-bottom-4">
                               <div className="mb-6">
                                   <h4 className="text-xs font-mono text-[#F5F0E6] uppercase tracking-wide mb-3">Select Iteration Type</h4>
                                   <div className="flex space-x-3">
                                       {(productionType === 'DOC' ? ['Deep Dive', 'Report', 'Brief'] : 
                                         productionType === 'IMG' ? ['Wireframe', 'Render', 'Schematic'] :
                                         productionType === 'VID' ? ['Explainer', 'Montage', 'Loop'] :
                                         ['Monologue', 'Podcast', 'Ambient']).map((sub) => (
                                           <button
                                               key={sub}
                                               onClick={() => setProductionSubType(sub)}
                                               className={`
                                                   px-4 py-2 border rounded-sm text-xs font-mono uppercase transition-all
                                                   ${productionSubType === sub 
                                                       ? 'bg-[#F59E0B] text-[#0D0D0D] border-[#F59E0B]' 
                                                       : 'bg-[#0D0D0D] text-[#888888] border-[#2D2D2D] hover:border-[#4A4A4A]'}
                                               `}
                                           >
                                               {sub}
                                           </button>
                                       ))}
                                   </div>
                               </div>

                               {/* 3. Shape Preview & Init */}
                               {productionSubType && (
                                   <div className="flex-1 flex flex-col">
                                       <div className="flex-1 bg-[#0D0D0D] border border-[#2D2D2D] rounded-sm mb-4 flex items-center justify-center p-8 relative overflow-hidden">
                                           {/* Visual Abstract Shape based on choice */}
                                           <div className={`
                                               transition-all duration-1000
                                               ${productionType === 'DOC' ? 'w-32 h-40 border-2 border-[#F59E0B]' : 
                                                 productionType === 'IMG' ? 'w-40 h-40 rounded-full border-2 border-[#F59E0B]' :
                                                 productionType === 'VID' ? 'w-60 h-32 border-2 border-[#F59E0B]' : 'w-40 h-10 border-2 border-[#F59E0B] rounded-full'}
                                           `}>
                                                <div className="absolute inset-0 bg-[#F59E0B]/5 animate-pulse"></div>
                                           </div>
                                           <span className="absolute text-[10px] font-mono text-[#F59E0B] uppercase tracking-widest bg-[#0D0D0D] px-2">
                                               {productionSubType} Template
                                           </span>
                                       </div>
                                       
                                       <Button fullWidth onClick={handleProduction} isLoading={isSynthesizing} icon={<Share2 size={14}/>}>
                                           Initialize {productionSubType}
                                       </Button>
                                   </div>
                               )}
                               
                               {generatedArtifact && (
                                   <div className="mt-4 p-4 bg-[#1A1A1A] border border-green-900/50 rounded-sm text-green-400 text-xs font-mono">
                                       {generatedArtifact}
                                   </div>
                               )}
                           </div>
                       )}
                   </div>
              </div>
          )}

      </div>
    </div>
  );
};