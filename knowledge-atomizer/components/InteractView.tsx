import React, { useEffect, useRef, useState } from 'react';
import { ChatMessage, DynamicCommand, DebateTopic, DebateRound, ModelConfig } from '../types';
import { 
    SparklesIcon, ScaleIcon, ArrowPathIcon, ChartBarIcon, MagnifyingGlassIcon, 
    MicrophoneIcon, StopIcon, ChatBubbleLeftRightIcon, FireIcon, UserIcon, 
    SpeakerWaveIcon, DocumentTextIcon, BeakerIcon, XMarkIcon
} from '@heroicons/react/24/solid';

interface InteractViewProps {
  // Chat Props
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  onExportChat: (mode: 'document' | 'atom', theme: string) => void;
  isLoading: boolean;
  dynamicCommands: DynamicCommand[];
  staticCommands: { basic: DynamicCommand[]; meta: DynamicCommand[]; };
  
  // Debate Props
  debateTopics: DebateTopic[];
  activeDebateTopic: DebateTopic | null;
  debateHistory: DebateRound[];
  onSelectDebateTopic: (topic: DebateTopic) => void;
  onNextDebateRound: () => void;
  onGenerateDebateTopics: () => void;
  hasContext: boolean;
  activeModel: ModelConfig;
}

const InteractView: React.FC<InteractViewProps> = ({ 
  messages, 
  onSendMessage, 
  onExportChat,
  isLoading, 
  dynamicCommands,
  staticCommands,
  debateTopics,
  activeDebateTopic,
  debateHistory,
  onSelectDebateTopic,
  onNextDebateRound,
  onGenerateDebateTopics,
  hasContext,
  activeModel
}) => {
  const [mode, setMode] = useState<'chat' | 'debate'>('chat');
  const [exportMode, setExportMode] = useState<'none' | 'document' | 'atom'>('none');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = false;
        recognitionRef.current.interimResults = false;
        recognitionRef.current.lang = 'en-US';

        recognitionRef.current.onresult = (event: any) => {
            const transcript = event.results[0][0].transcript;
            setInputText(prev => prev + (prev ? " " : "") + transcript);
            setIsListening(false);
        };

        recognitionRef.current.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            setIsListening(false);
        };
        
        recognitionRef.current.onend = () => {
            setIsListening(false);
        };
    }
  }, []);

  const toggleListening = () => {
      if (isListening) {
          recognitionRef.current?.stop();
      } else {
          try {
              recognitionRef.current?.start();
              setIsListening(true);
          } catch(e) {
              console.error("Failed to start speech recognition", e);
          }
      }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, debateHistory, isLoading, mode]);

  const handleSend = () => {
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const handleCommandClick = (cmdLabel: string, cmdPrompt: string) => {
      if (exportMode !== 'none') {
          // Trigger export instead of send
          onExportChat(exportMode, cmdLabel); // Use the Label as the theme (e.g. "Summarize")
          setExportMode('none');
      } else {
          onSendMessage(cmdPrompt);
      }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // --- RENDERERS ---

  const renderChatMessage = (msg: ChatMessage, idx: number) => {
    const isModel = msg.role === 'model';
    return (
      <div key={idx} className={`flex ${isModel ? 'justify-start' : 'justify-end'} mb-6 animate-in fade-in slide-in-from-bottom-2`}>
        <div 
          className={`max-w-[85%] rounded-2xl p-4 shadow-lg ${
            isModel 
              ? 'bg-slate-800 border border-slate-700 text-slate-200' 
              : 'bg-primary-600 text-white'
          }`}
        >
          <div className="whitespace-pre-wrap leading-relaxed text-sm md:text-base font-light">
             {msg.text}
          </div>
        </div>
      </div>
    );
  };

  const renderDebateRound = (round: DebateRound) => (
      <div key={round.roundNumber} className="relative mb-8 animate-in fade-in slide-in-from-bottom-4">
        <div className="absolute left-1/2 -translate-x-1/2 -top-4 bg-slate-800 text-slate-400 text-[10px] px-3 py-1 rounded-full border border-slate-700 shadow-sm z-0">
            ROUND {round.roundNumber}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-8 pt-4">
            {/* Side A */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-800/50 border-l-4 border-blue-500 rounded-r-xl p-5 relative">
                <div className="absolute -top-3 left-4 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider shadow">Side A</div>
                <p className="text-slate-300 text-sm leading-relaxed font-light">
                    {round.turns.find(t => t.speaker === 'Side A')?.text}
                </p>
            </div>

            {/* Side B */}
            <div className="bg-gradient-to-bl from-slate-900 to-slate-800/50 border-r-4 border-red-500 rounded-l-xl p-5 relative md:text-right">
                <div className="absolute -top-3 right-4 bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider shadow">Side B</div>
                <p className="text-slate-300 text-sm leading-relaxed font-light">
                        {round.turns.find(t => t.speaker === 'Side B')?.text}
                </p>
            </div>
        </div>
        {/* User Injections in History if any (This logic assumes injected turns are part of rounds or interspersed, for now we keep it simple) */}
      </div>
  );

  return (
    <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm relative">
      
      {/* Mode Toggle Header */}
      <div className="flex justify-center p-4 bg-slate-950/80 border-b border-slate-800 z-10 backdrop-blur">
          <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800 shadow-lg">
              <button 
                onClick={() => setMode('chat')}
                title="Direct interaction mode"
                className={`flex items-center space-x-2 px-6 py-2 rounded-lg text-sm font-bold transition-all ${mode === 'chat' ? 'bg-primary-600 text-white shadow-md' : 'text-slate-500 hover:text-slate-300'}`}
              >
                  <ChatBubbleLeftRightIcon className="w-4 h-4" />
                  <span>Chat</span>
              </button>
              <button 
                onClick={() => setMode('debate')}
                title="Structured debate simulation mode"
                className={`flex items-center space-x-2 px-6 py-2 rounded-lg text-sm font-bold transition-all ${mode === 'debate' ? 'bg-orange-600 text-white shadow-md' : 'text-slate-500 hover:text-slate-300'}`}
              >
                  <FireIcon className="w-4 h-4" />
                  <span>Debate</span>
              </button>
          </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 scrollbar-thin">
        
        {/* CHAT MODE */}
        {mode === 'chat' && (
            <>
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60">
                        <SparklesIcon className="w-16 h-16 mb-4" />
                        <p>Knowledge Engine Ready. Interrogate the data.</p>
                    </div>
                )}
                {messages.map(renderChatMessage)}
            </>
        )}

        {/* DEBATE MODE */}
        {mode === 'debate' && (
            <>
                 {!activeDebateTopic ? (
                     <div className="flex flex-col items-center justify-center h-full max-w-4xl mx-auto">
                         <div className="text-center mb-8">
                             <h2 className="text-2xl font-bold text-white mb-2">Debate Arena</h2>
                             <p className="text-slate-400 text-sm">Select a topic to initiate a structured debate.</p>
                         </div>
                         {debateTopics.length === 0 ? (
                            <button 
                                onClick={onGenerateDebateTopics}
                                disabled={isLoading}
                                title="Analyze context and suggest debate topics"
                                className="bg-orange-600 hover:bg-orange-500 text-white px-8 py-4 rounded-full font-bold transition-all flex items-center"
                            >
                                <FireIcon className="w-5 h-5 mr-2" />
                                Generate Topics
                            </button>
                         ) : (
                             <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full px-4">
                                 {debateTopics.map(t => (
                                     <button 
                                        key={t.id}
                                        onClick={() => onSelectDebateTopic(t)}
                                        title="Click to start debate on this topic"
                                        className="bg-slate-800 hover:bg-slate-700 border border-slate-700 p-6 rounded-xl text-left transition-all"
                                     >
                                         <span className="text-orange-500 text-xs font-bold uppercase tracking-wider block mb-2">{t.label}</span>
                                         <span className="text-white font-medium">{t.question}</span>
                                     </button>
                                 ))}
                             </div>
                         )}
                     </div>
                 ) : (
                     <div className="max-w-5xl mx-auto w-full pb-20">
                         <div className="mb-8 text-center border-b border-slate-800 pb-4">
                             <span className="text-orange-500 text-[10px] font-bold uppercase tracking-widest">Active Debate</span>
                             <h2 className="text-xl font-bold text-white mt-1">{activeDebateTopic.question}</h2>
                             <button onClick={() => onSelectDebateTopic(null as any)} title="Close current debate" className="text-xs text-slate-500 hover:text-white mt-2 underline">End Debate</button>
                         </div>
                         
                         {debateHistory.map(renderDebateRound)}
                         
                         {/* Next Round Button */}
                         {!isLoading && (
                             <div className="flex justify-center mt-8">
                                 <button 
                                    onClick={onNextDebateRound}
                                    title="Generate the next round of arguments"
                                    className="bg-slate-100 hover:bg-white text-slate-900 px-6 py-2 rounded-full font-bold shadow-lg transition-transform hover:-translate-y-0.5 active:translate-y-0 text-sm flex items-center"
                                 >
                                     <span>Continue Debate</span>
                                     <ArrowPathIcon className="w-4 h-4 ml-2" />
                                 </button>
                             </div>
                         )}
                     </div>
                 )}
            </>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-center mt-4 mb-8">
            <div className="bg-slate-800 rounded-full px-4 py-2 border border-slate-700 flex items-center space-x-2">
               <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
               <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
               <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
               <span className="text-xs text-slate-400 font-mono ml-2">Processing...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Control Surface */}
      <div className="bg-slate-950 border-t border-slate-800 p-4 shadow-2xl z-20">
        
        {/* Export Mode Banner */}
        {exportMode !== 'none' && (
            <div className="absolute bottom-full left-0 right-0 bg-indigo-900/90 backdrop-blur-md border-t border-indigo-500 p-3 flex justify-between items-center animate-in slide-in-from-bottom-2">
                <div className="flex items-center text-white text-sm font-bold">
                    {exportMode === 'document' ? <DocumentTextIcon className="w-5 h-5 mr-2" /> : <BeakerIcon className="w-5 h-5 mr-2" />}
                    Select a Theme below to Generate {exportMode === 'document' ? 'Document' : 'Knowledge Atoms'}
                </div>
                <button onClick={() => setExportMode('none')} title="Cancel export" className="text-white hover:text-indigo-200">
                    <XMarkIcon className="w-5 h-5" />
                </button>
            </div>
        )}

        {/* Dynamic & Static Commands (Unified for both modes) */}
        <div className="mb-4 overflow-x-auto scrollbar-none pb-2">
          <div className="flex gap-2 min-w-max">
             {/* Suggested */}
             {dynamicCommands.map((cmd, i) => (
               <button
                 key={`dyn-${i}`}
                 onClick={() => handleCommandClick(cmd.label, cmd.prompt)}
                 disabled={isLoading}
                 title={cmd.description || cmd.prompt}
                 className={`
                    flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all
                    disabled:opacity-50
                    ${exportMode !== 'none' ? 'bg-indigo-800 border-indigo-500 text-white hover:bg-indigo-700' : 
                      i === 0 
                      ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30 border border-transparent hover:scale-105' 
                      : 'bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 hover:text-white'}
                 `}
               >
                  {i === 0 && <SparklesIcon className="w-3 h-3 text-yellow-300" />}
                  <span>{cmd.label}</span>
               </button>
             ))}
             
             {/* Divider */}
             <div className="w-px bg-slate-800 mx-2"></div>

             {/* Basic */}
             {staticCommands.basic.map((cmd, i) => (
                <button 
                    key={`basic-${i}`}
                    onClick={() => handleCommandClick(cmd.label, cmd.prompt)}
                    disabled={isLoading}
                    title={cmd.prompt}
                    className={`px-3 py-1.5 rounded text-xs border transition-colors whitespace-nowrap
                        ${exportMode !== 'none' ? 'bg-indigo-900/50 border-indigo-500 text-indigo-100 hover:bg-indigo-800' : 'bg-slate-900/50 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border-slate-800'}
                    `}
                >
                    {cmd.label}
                </button>
             ))}

             {/* Meta */}
             {staticCommands.meta.map((cmd, i) => (
                <button 
                    key={`meta-${i}`}
                    onClick={() => handleCommandClick(cmd.label, cmd.prompt)}
                    disabled={isLoading}
                    title={cmd.prompt}
                    className={`px-3 py-1.5 rounded text-xs border transition-colors flex items-center whitespace-nowrap
                        ${exportMode !== 'none' ? 'bg-pink-900/50 border-pink-500 text-pink-100 hover:bg-pink-800' : 'bg-slate-900/50 hover:bg-slate-800 text-cyan-300 border-cyan-900/30 hover:border-cyan-500/50'}
                    `}
                >
                    {i === 0 && <ScaleIcon className="w-3 h-3 mr-1" />}
                    {i === 1 && <ChartBarIcon className="w-3 h-3 mr-1" />}
                    {i === 2 && <MagnifyingGlassIcon className="w-3 h-3 mr-1" />}
                    <span>{cmd.label}</span>
                </button>
             ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="relative flex items-end gap-2">
          
          {/* Export Toggles */}
          <div className="flex flex-col gap-1 pb-1">
              <button 
                onClick={() => setExportMode(exportMode === 'document' ? 'none' : 'document')}
                className={`p-2 rounded-lg transition-colors ${exportMode === 'document' ? 'bg-white text-slate-900' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                title="Export Chat as Document"
              >
                  <DocumentTextIcon className="w-5 h-5" />
              </button>
              <button 
                onClick={() => setExportMode(exportMode === 'atom' ? 'none' : 'atom')}
                className={`p-2 rounded-lg transition-colors ${exportMode === 'atom' ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
                title="Distill Chat to Atoms"
              >
                  <BeakerIcon className="w-5 h-5" />
              </button>
          </div>

          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={mode === 'chat' ? "Interrogate the data..." : "Chime in or influence the debate..."}
            disabled={isLoading || exportMode !== 'none'}
            className="flex-1 bg-slate-900 text-slate-100 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 border border-slate-700 resize-none h-14 shadow-inner font-light placeholder-slate-600 disabled:opacity-50"
          />
          
          <button
             onClick={toggleListening}
             disabled={exportMode !== 'none'}
             className={`h-14 w-14 rounded-xl flex items-center justify-center transition-all ${isListening ? 'bg-red-600 animate-pulse text-white' : 'bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700'}`}
             title="Voice Input"
          >
              {isListening ? <StopIcon className="w-6 h-6" /> : <MicrophoneIcon className="w-6 h-6" />}
          </button>

          <button
            onClick={handleSend}
            disabled={isLoading || !inputText.trim() || exportMode !== 'none'}
            title="Send Message"
            className="h-14 w-14 bg-primary-600 hover:bg-primary-500 text-white rounded-xl disabled:opacity-50 disabled:bg-slate-700 transition-all flex items-center justify-center"
          >
            <ArrowPathIcon className={`w-6 h-6 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
        {mode === 'debate' && (
            <p className="text-[10px] text-slate-500 mt-2 text-center">
                <UserIcon className="w-3 h-3 inline mr-1" />
                Your input will be injected into the debate context, influencing the next round.
            </p>
        )}
      </div>
    </div>
  );
};

export default InteractView;