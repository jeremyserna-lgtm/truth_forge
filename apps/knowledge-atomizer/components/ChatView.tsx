import React, { useEffect, useRef, useState } from 'react';
import { ChatMessage, DynamicCommand } from '../types';
import { SparklesIcon, ScaleIcon, ArrowPathIcon, ChartBarIcon, MagnifyingGlassIcon } from '@heroicons/react/24/solid';

interface ChatViewProps {
  messages: ChatMessage[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  dynamicCommands: DynamicCommand[];
  staticCommands: {
    basic: DynamicCommand[];
    meta: DynamicCommand[];
  };
}

const ChatView: React.FC<ChatViewProps> = ({
  messages,
  onSendMessage,
  isLoading,
  dynamicCommands,
  staticCommands
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [inputText, setInputText] = useState('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = () => {
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText);
    setInputText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const renderMessage = (msg: ChatMessage, idx: number) => {
    const isModel = msg.role === 'model';
    return (
      <div key={idx} className={`flex ${isModel ? 'justify-start' : 'justify-end'} mb-6`}>
        <div
          className={`max-w-[85%] rounded-2xl p-4 shadow-lg ${isModel
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

  return (
    <div className="flex flex-col h-full bg-slate-900/50 backdrop-blur-sm">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60">
            <SparklesIcon className="w-16 h-16 mb-4" />
            <p>Knowledge Engine Ready. Select a command or type to begin.</p>
          </div>
        )}
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="flex justify-start mb-6">
            <div className="bg-slate-800 rounded-2xl p-4 border border-slate-700">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Control Surface */}
      <div className="bg-slate-950 border-t border-slate-800 p-4 shadow-2xl z-20">

        {/* Suggested Queries (Dynamic) */}
        <div className="mb-4">
          <p className="text-[10px] text-slate-500 font-bold uppercase mb-2 tracking-wider">Suggested Queries</p>
          <div className="flex flex-wrap gap-2">
            {dynamicCommands.map((cmd, i) => (
              <button
                key={`dyn-${i}`}
                onClick={() => onSendMessage(cmd.prompt)}
                disabled={isLoading}
                className={`
                    flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${i === 0
                    ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-lg shadow-indigo-500/30 border border-transparent hover:scale-105'
                    : 'bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 hover:text-white'}
                 `}
              >
                {i === 0 && <SparklesIcon className="w-3 h-3 text-yellow-300" />}
                <span>{cmd.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Static Tools Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4 pt-2 border-t border-slate-900">
          <div className="flex flex-wrap gap-2 items-center">
            <span className="text-[10px] text-slate-600 font-bold uppercase mr-1">Basic</span>
            {staticCommands.basic.map((cmd, i) => (
              <button
                key={`basic-${i}`}
                onClick={() => onSendMessage(cmd.prompt)}
                disabled={isLoading}
                className="px-3 py-1.5 bg-slate-900/50 hover:bg-slate-800 text-slate-400 hover:text-slate-200 rounded text-xs border border-slate-800 transition-colors"
              >
                {cmd.label}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-2 items-center lg:justify-end">
            <span className="text-[10px] text-slate-600 font-bold uppercase mr-1">Meta</span>
            {staticCommands.meta.map((cmd, i) => (
              <button
                key={`meta-${i}`}
                onClick={() => onSendMessage(cmd.prompt)}
                disabled={isLoading}
                className="px-3 py-1.5 bg-slate-900/50 hover:bg-slate-800 text-cyan-300 rounded text-xs border border-cyan-900/30 hover:border-cyan-500/50 transition-colors flex items-center"
              >
                {i === 0 && <ScaleIcon className="w-3 h-3 mr-1" />}
                {i === 1 && <ChartBarIcon className="w-3 h-3 mr-1" />}
                {i === 2 && <MagnifyingGlassIcon className="w-3 h-3 mr-1" />}
                <span className={i > 2 ? 'ml-0' : ''}>{cmd.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Input Area */}
        <div className="relative">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Interrogate the data..."
            disabled={isLoading}
            className="w-full bg-slate-900 text-slate-100 rounded-xl pl-4 pr-14 py-4 focus:outline-none focus:ring-2 focus:ring-primary-500 border border-slate-700 resize-none h-16 shadow-inner font-light placeholder-slate-600"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !inputText.trim()}
            className="absolute right-3 top-3 p-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg disabled:opacity-50 disabled:bg-slate-700 transition-all"
          >
            <ArrowPathIcon className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatView;