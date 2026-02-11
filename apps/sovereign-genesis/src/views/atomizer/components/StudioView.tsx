import React, { useState, useEffect, useRef } from 'react';
import { KnowledgeAtom, StudioArtifact, AudioLength, StudioFormat, DynamicStudioOption, UploadedDocument } from '../../../types';
import { generateStudioSuggestions, generateTextArtifact, generateAudioArtifact } from '../../../services/geminiService';
import { 
  MicrophoneIcon, DocumentTextIcon, SparklesIcon, PlayIcon, 
  ArrowDownTrayIcon, ClockIcon, SpeakerWaveIcon, BookOpenIcon,
  PencilSquareIcon, ChatBubbleLeftRightIcon, BeakerIcon, FolderArrowDownIcon
} from '@heroicons/react/24/solid';
import JSZip from 'jszip';

interface StudioViewProps {
  atoms: KnowledgeAtom[];
  isLoading: boolean;
  setLoading: (l: boolean) => void;
  onArtifactToAtoms: (artifact: StudioArtifact) => void;
  onArtifactToDocument: (artifact: StudioArtifact) => void;
}

const StudioView: React.FC<StudioViewProps> = ({ atoms, isLoading, setLoading, onArtifactToAtoms, onArtifactToDocument }) => {
  const [artifacts, setArtifacts] = useState<StudioArtifact[]>([]);
  const [selectedArtifact, setSelectedArtifact] = useState<StudioArtifact | null>(null);
  const [suggestions, setSuggestions] = useState<DynamicStudioOption[]>([]);
  
  // Audio Config
  const [audioMode, setAudioMode] = useState<StudioFormat>('Podcast');
  const [audioLength, setAudioLength] = useState<AudioLength>('Short');
  const audioRef = useRef<HTMLAudioElement>(null);

  const contextStr = atoms.map(a => a.content).join("\n");

  // Force audio reload when artifact changes
  useEffect(() => {
      if(audioRef.current && selectedArtifact?.audioUrl) {
          audioRef.current.load();
      }
  }, [selectedArtifact]);

  const handleSuggest = async () => {
    setLoading(true);
    try {
      const opts = await generateStudioSuggestions(contextStr);
      setSuggestions(opts);
    } catch(e) {
      alert("Failed to generate suggestions.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateText = async (type: StudioFormat, customAngle?: string) => {
    setLoading(true);
    try {
      const artifact = await generateTextArtifact(contextStr, type, customAngle);
      setArtifacts(prev => [artifact, ...prev]);
      setSelectedArtifact(artifact);
    } catch(e) {
      console.error(e);
      alert("Failed to generate text.");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAudio = async (type: StudioFormat) => {
    setLoading(true);
    try {
      const artifact = await generateAudioArtifact(contextStr, type, audioLength);
      setArtifacts(prev => [artifact, ...prev]);
      setSelectedArtifact(artifact);
    } catch(e) {
        console.error(e);
      alert("Failed to generate audio.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async (artifact: StudioArtifact) => {
      const zip = new JSZip();
      
      // 1. Transcript / Content
      zip.file(`${artifact.title.replace(/\s+/g, '_')}_transcript.md`, artifact.content);
      
      // 2. Audio (if exists)
      if (artifact.audioUrl) {
          const resp = await fetch(artifact.audioUrl);
          const blob = await resp.blob();
          zip.file(`${artifact.title.replace(/\s+/g, '_')}.wav`, blob);
      }
      
      // 3. Analysis (if exists)
      if (artifact.metaAnalysis) {
          zip.file('meta_analysis.json', JSON.stringify(artifact.metaAnalysis, null, 2));
      }
      
      const content = await zip.generateAsync({type:"blob"});
      const url = URL.createObjectURL(content);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${artifact.title.replace(/\s+/g, '_')}_package.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  };

  return (
    <div className="h-full flex flex-col p-6 max-w-7xl mx-auto w-full gap-8">
       {/* Header */}
       <div>
            <h1 className="text-3xl font-black text-white mb-2 flex items-center">
                <MicrophoneIcon className="w-8 h-8 mr-3 text-rose-500" />
                Creative Studio
            </h1>
            <p className="text-slate-400">Generate deep dives, podcasts, and critical analyses from your knowledge base.</p>
       </div>

       <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 h-full min-h-0">
          
          {/* LEFT: Controls */}
          <div className="lg:col-span-4 flex flex-col gap-6 overflow-y-auto scrollbar-thin pr-2">
              
              {/* Text Studio */}
              <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                  <h3 className="text-rose-400 font-bold uppercase tracking-wider mb-4 flex items-center">
                      <DocumentTextIcon className="w-5 h-5 mr-2" />
                      Text Studio
                  </h3>
                  <div className="grid grid-cols-2 gap-3 mb-4">
                      {['Deep Dive', 'Critique', 'Briefing Doc', 'Blog Post'].map((type) => (
                          <button 
                            key={type}
                            onClick={() => handleGenerateText(type as StudioFormat)}
                            disabled={isLoading}
                            title={`Generate a ${type}`}
                            className="bg-slate-800 hover:bg-slate-700 p-3 rounded-xl text-xs font-bold text-slate-300 border border-slate-700 transition-all hover:border-rose-500/50"
                          >
                              {type}
                          </button>
                      ))}
                  </div>
                  
                  {/* Dynamic Suggestions */}
                  <div className="border-t border-slate-800 pt-4">
                      <div className="flex justify-between items-center mb-3">
                        <span className="text-xs font-bold text-slate-500">AI SUGGESTIONS</span>
                        <button onClick={handleSuggest} disabled={isLoading} title="Get creative content ideas from the model" className="text-rose-400 text-xs hover:underline">
                            <SparklesIcon className="w-4 h-4 inline mr-1" />
                            Generate Ideas
                        </button>
                      </div>
                      <div className="space-y-2">
                          {suggestions.map((s, i) => (
                              <button 
                                key={i}
                                onClick={() => handleGenerateText('Custom', s.prompt_angle)}
                                disabled={isLoading}
                                title={s.description}
                                className="w-full text-left bg-slate-950 hover:bg-slate-800 p-3 rounded-lg border border-slate-800 transition-colors group"
                              >
                                  <div className="text-slate-200 text-sm font-bold group-hover:text-rose-400">{s.label}</div>
                                  <div className="text-slate-500 text-[10px] line-clamp-2">{s.description}</div>
                              </button>
                          ))}
                          {suggestions.length === 0 && (
                              <div className="text-center text-slate-600 text-xs py-4 italic">Click 'Generate Ideas' to get started.</div>
                          )}
                      </div>
                  </div>
              </div>

              {/* Voice Studio */}
              <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6">
                  <h3 className="text-cyan-400 font-bold uppercase tracking-wider mb-4 flex items-center">
                      <SpeakerWaveIcon className="w-5 h-5 mr-2" />
                      Voice Layer
                  </h3>
                  
                  <div className="space-y-4">
                      {/* Modes */}
                      <div className="grid grid-cols-2 gap-2">
                          {['Podcast', 'Debate', 'Spoken Critique', 'Brief'].map((m) => (
                              <button
                                key={m}
                                onClick={() => setAudioMode(m as StudioFormat)}
                                title={`Set mode to ${m}`}
                                className={`p-2 rounded-lg text-xs font-bold border transition-all ${audioMode === m ? 'bg-cyan-900/30 border-cyan-500 text-cyan-300' : 'bg-slate-800 border-slate-700 text-slate-400'}`}
                              >
                                  {m}
                              </button>
                          ))}
                      </div>

                      {/* Length */}
                      <div className="flex items-center space-x-2 bg-slate-950 p-2 rounded-lg">
                          <ClockIcon className="w-4 h-4 text-slate-500" />
                          {['Short', 'Medium', 'Long'].map((l) => (
                              <button
                                key={l}
                                onClick={() => setAudioLength(l as AudioLength)}
                                title={`Set length to ${l}`}
                                className={`flex-1 py-1 rounded text-[10px] font-bold uppercase ${audioLength === l ? 'bg-cyan-600 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                              >
                                  {l}
                              </button>
                          ))}
                      </div>

                      <button
                        onClick={() => handleGenerateAudio(audioMode)}
                        disabled={isLoading}
                        title="Generate audio based on selected mode and length"
                        className="w-full py-3 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl font-bold shadow-lg flex justify-center items-center disabled:opacity-50"
                      >
                          {isLoading ? (
                              <span className="animate-pulse">Synthesizing...</span>
                          ) : (
                              <>
                                <PlayIcon className="w-5 h-5 mr-2" />
                                Generate Audio
                              </>
                          )}
                      </button>
                  </div>
              </div>
          </div>

          {/* RIGHT: Content Viewer */}
          <div className="lg:col-span-8 flex flex-col bg-slate-900 rounded-2xl border border-slate-800 overflow-hidden">
              {selectedArtifact ? (
                  <div className="flex flex-col h-full">
                      {/* Artifact Header */}
                      <div className="p-6 border-b border-slate-800 bg-slate-900 flex justify-between items-start">
                          <div>
                              <div className="flex items-center space-x-3 mb-2">
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase border ${selectedArtifact.mode === 'Audio' ? 'bg-cyan-900/20 text-cyan-400 border-cyan-800' : 'bg-rose-900/20 text-rose-400 border-rose-800'}`}>
                                      {selectedArtifact.type}
                                  </span>
                                  <span className="text-slate-500 text-xs">
                                      {new Date(selectedArtifact.createdAt).toLocaleTimeString()}
                                  </span>
                              </div>
                              <h2 className="text-2xl font-bold text-white">{selectedArtifact.title}</h2>
                          </div>
                          
                          <div className="flex items-center space-x-2">
                              <button 
                                onClick={() => onArtifactToDocument(selectedArtifact)}
                                className="p-2 bg-slate-800 hover:bg-emerald-600 rounded-lg text-slate-300 hover:text-white transition-colors"
                                title="Save as Document in Data Tab"
                              >
                                  <FolderArrowDownIcon className="w-6 h-6" />
                              </button>
                              <button 
                                onClick={() => onArtifactToAtoms(selectedArtifact)}
                                className="p-2 bg-slate-800 hover:bg-indigo-600 rounded-lg text-slate-300 hover:text-white transition-colors"
                                title="Distill to Knowledge Atoms"
                              >
                                  <BeakerIcon className="w-6 h-6" />
                              </button>
                              <div className="w-px h-6 bg-slate-700 mx-2"></div>
                              <button 
                                onClick={() => handleDownload(selectedArtifact)}
                                className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 hover:text-white transition-colors"
                                title="Download Package (Content + Audio)"
                              >
                                  <ArrowDownTrayIcon className="w-6 h-6" />
                              </button>
                          </div>
                      </div>

                      {/* Artifact Content */}
                      <div className="flex-1 overflow-y-auto p-8 scrollbar-thin">
                          
                          {/* Audio Player if exists */}
                          {selectedArtifact.audioUrl && (
                              <div className="mb-8 p-6 bg-slate-950 rounded-2xl border border-slate-800 shadow-inner">
                                  <div className="flex items-center justify-between mb-4">
                                      <h4 className="text-cyan-400 font-bold uppercase text-xs tracking-widest">Audio Playback</h4>
                                      <span className="text-slate-500 text-xs font-mono">
                                          {audioLength} Duration
                                      </span>
                                  </div>
                                  <audio 
                                    ref={audioRef}
                                    controls 
                                    src={selectedArtifact.audioUrl} 
                                    className="w-full h-10 accent-cyan-500" 
                                  />
                              </div>
                          )}

                          {/* Meta Analysis if exists */}
                          {selectedArtifact.metaAnalysis && (
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                  <div className="bg-indigo-900/20 p-5 rounded-xl border border-indigo-500/30">
                                      <h5 className="text-indigo-300 font-bold uppercase text-xs mb-3">Key Points & Actions</h5>
                                      <ul className="space-y-2 text-sm text-slate-300 list-disc list-inside">
                                          {selectedArtifact.metaAnalysis.keyPoints.slice(0,3).map((p,i) => <li key={i}>{p}</li>)}
                                          {selectedArtifact.metaAnalysis.actionItems.slice(0,2).map((p,i) => <li key={i} className="text-indigo-200">{p}</li>)}
                                      </ul>
                                  </div>
                                  <div className="bg-emerald-900/20 p-5 rounded-xl border border-emerald-500/30">
                                      <h5 className="text-emerald-300 font-bold uppercase text-xs mb-3">Tone & Performance</h5>
                                      <div className="space-y-2 text-sm">
                                          <p><span className="text-slate-500">Tone:</span> <span className="text-slate-200">{selectedArtifact.metaAnalysis.tone}</span></p>
                                          <p><span className="text-slate-500">Grade:</span> <span className="text-emerald-400 font-bold">{selectedArtifact.metaAnalysis.performance}</span></p>
                                      </div>
                                  </div>
                              </div>
                          )}

                          {/* Markdown Content / Transcript */}
                          <div className="prose prose-invert prose-sm md:prose-base max-w-none">
                              <h3 className="text-slate-500 uppercase text-xs font-bold tracking-widest mb-4 border-b border-slate-800 pb-2">
                                  {selectedArtifact.mode === 'Audio' ? 'Transcript' : 'Generated Content'}
                              </h3>
                              <div className="whitespace-pre-wrap text-slate-300 font-light leading-relaxed">
                                  {selectedArtifact.content}
                              </div>
                          </div>
                      </div>
                  </div>
              ) : (
                  <div className="flex flex-col items-center justify-center h-full text-slate-600 opacity-50">
                      <BookOpenIcon className="w-24 h-24 mb-4" />
                      <p className="text-lg">Select or generate an artifact to view.</p>
                  </div>
              )}
          </div>
       </div>
    </div>
  );
};

export default StudioView;