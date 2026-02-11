import React, { useEffect } from 'react';
import { DebateTopic, DebateRound, ModelConfig } from '../types';
import { UserGroupIcon, FireIcon, PlayIcon, PlusIcon } from '@heroicons/react/24/solid';

interface DebateViewProps {
    topics: DebateTopic[];
    activeTopic: DebateTopic | null;
    history: DebateRound[];
    isLoading: boolean;
    onSelectTopic: (topic: DebateTopic) => void;
    onNextRound: () => void;
    onGenerateTopics: () => void;
    hasContext: boolean;
    activeModel: ModelConfig;
}

const DebateView: React.FC<DebateViewProps> = ({
    topics,
    activeTopic,
    history,
    isLoading,
    onSelectTopic,
    onNextRound,
    onGenerateTopics,
    hasContext,
    activeModel
}) => {
    const scrollRef = React.useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history, isLoading]);

    if (!hasContext) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 p-8 text-center">
                <UserGroupIcon className="w-20 h-20 mb-4 opacity-50" />
                <h2 className="text-2xl font-bold text-slate-300 mb-2">No Context Available</h2>
                <p>Upload and distill documents to generate debate topics.</p>
            </div>
        );
    }

    if (!activeTopic) {
        return (
            <div className="flex flex-col h-full p-8 max-w-5xl mx-auto w-full">
                <div className="text-center mb-10">
                    <h2 className="text-3xl md:text-4xl font-black text-white mb-4 flex items-center justify-center">
                        <FireIcon className="w-8 h-8 mr-3 text-orange-500" />
                        Debate Arena
                    </h2>
                    <p className="text-slate-400 text-lg">Select a controversial topic derived from your data to initiate a structured debate.</p>
                </div>

                {topics.length === 0 ? (
                    <div className="flex-1 flex flex-col items-center justify-center">
                        <button
                            onClick={onGenerateTopics}
                            disabled={isLoading}
                            title="Analyze context and generate debate topics"
                            className="group relative inline-flex items-center justify-center px-8 py-4 font-bold text-white transition-all duration-200 bg-orange-600 font-lg rounded-full hover:bg-orange-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-600 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <span className="animate-pulse">Analyzing Context...</span>
                            ) : (
                                <>
                                    <PlusIcon className="w-6 h-6 mr-2" />
                                    Generate Debate Topics
                                </>
                            )}
                        </button>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {topics.map((topic) => (
                            <button
                                key={topic.id}
                                onClick={() => onSelectTopic(topic)}
                                title="Click to start this debate"
                                className="flex flex-col text-left bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-orange-500/50 p-6 rounded-2xl transition-all group shadow-lg"
                            >
                                <span className="text-xs font-bold text-orange-500 uppercase tracking-widest mb-2">{topic.label}</span>
                                <span className="text-lg md:text-xl font-medium text-slate-200 group-hover:text-white leading-snug">{topic.question}</span>
                            </button>
                        ))}
                        <button
                            onClick={onGenerateTopics}
                            title="Discard current topics and generate new ones"
                            className="flex flex-col items-center justify-center bg-slate-900/50 hover:bg-slate-900 border-2 border-dashed border-slate-800 hover:border-slate-600 p-6 rounded-2xl transition-all text-slate-500 hover:text-slate-300"
                        >
                            <PlusIcon className="w-8 h-8 mb-2" />
                            <span>Regenerate Topics</span>
                        </button>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-slate-950">
            {/* Debate Header */}
            <div className="p-4 border-b border-slate-800 bg-slate-900 shadow-md flex justify-between items-center z-10">
                <div>
                    <div className="flex items-center space-x-2 mb-1">
                        <span className="bg-orange-900/30 text-orange-400 text-[10px] font-bold px-2 py-0.5 rounded border border-orange-900/50 uppercase">Active Debate</span>
                        <h3 className="text-slate-200 font-bold truncate max-w-md">{activeTopic.label}</h3>
                    </div>
                    <p className="text-xs text-slate-500 italic max-w-2xl truncate">"{activeTopic.question}"</p>
                </div>
                <button
                    onClick={() => onSelectTopic(null as any)} // Reset
                    title="Stop debate and return to topic selection"
                    className="text-xs text-slate-400 hover:text-white underline decoration-slate-700 hover:decoration-white underline-offset-4"
                >
                    End Debate
                </button>
            </div>

            {/* Debate Flow */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 scrollbar-thin bg-slate-950" ref={scrollRef}>
                {history.length === 0 && !isLoading && (
                    <div className="text-center py-20 opacity-50">
                        <p>Press "Begin Debate" to start the arguments.</p>
                    </div>
                )}

                {history.map((round) => (
                    <div key={round.roundNumber} className="relative">
                        <div className="absolute left-1/2 -translate-x-1/2 -top-4 bg-slate-800 text-slate-400 text-[10px] px-3 py-1 rounded-full border border-slate-700 shadow-sm z-0">
                            ROUND {round.roundNumber}
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
                            {/* Side A */}
                            <div className="bg-gradient-to-br from-slate-900 to-slate-800/50 border-l-4 border-blue-500 rounded-r-xl p-6 relative">
                                <div className="absolute -top-3 left-4 bg-blue-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider shadow">Side A (Pro)</div>
                                <p className="text-slate-300 text-sm md:text-base leading-relaxed font-light">
                                    {round.turns.find(t => t.speaker === 'Side A')?.text}
                                </p>
                            </div>

                            {/* Side B */}
                            <div className="bg-gradient-to-bl from-slate-900 to-slate-800/50 border-r-4 border-red-500 rounded-l-xl p-6 relative md:text-right">
                                <div className="absolute -top-3 right-4 bg-red-600 text-white text-[10px] font-bold px-2 py-1 rounded uppercase tracking-wider shadow">Side B (Con)</div>
                                <p className="text-slate-300 text-sm md:text-base leading-relaxed font-light">
                                    {round.turns.find(t => t.speaker === 'Side B')?.text}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-center py-8">
                        <div className="flex items-center space-x-3 text-orange-500">
                            <FireIcon className="w-6 h-6 animate-pulse" />
                            <span className="font-mono text-sm animate-pulse">Constructing Arguments ({activeModel.label})...</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Controls */}
            <div className="p-6 border-t border-slate-800 bg-slate-900/50 backdrop-blur-md flex justify-center">
                <button
                    onClick={onNextRound}
                    disabled={isLoading}
                    title={history.length === 0 ? "Start the debate" : "Generate the next round of arguments"}
                    className="flex items-center space-x-3 bg-slate-100 hover:bg-white text-slate-900 px-8 py-3 rounded-xl font-bold shadow-lg shadow-white/10 hover:shadow-white/20 transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <PlayIcon className="w-5 h-5" />
                    <span>{history.length === 0 ? "Begin Debate" : "Next Round"}</span>
                </button>
            </div>
        </div>
    );
};

export default DebateView;