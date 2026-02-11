import React, { useRef, useState } from 'react';
import { SpinalNode, ModelConfig, StructureAnalysis } from '../../../types';
import {
    ArrowUpTrayIcon,
    ChartBarSquareIcon,
    ChevronRightIcon,
    ChevronDownIcon,
    FaceSmileIcon,
    ArrowPathIcon,
    ChatBubbleLeftRightIcon,
    ListBulletIcon,
    CursorArrowRaysIcon,
    CheckIcon
} from '@heroicons/react/24/solid';
import { analyzeJsonStructure, processStructuredImport } from '../../../services/importService';
import { generateSpinalEnrichment } from '../../../services/geminiService';

interface EnrichmentViewProps {
    modelConfig: ModelConfig;
    isLoading: boolean;
    onSetLoading: (l: boolean) => void;
}

const renderStats = (node: SpinalNode) => (
    <div className="flex space-x-4 mt-2 text-[10px] uppercase font-mono tracking-wide text-slate-500">
        {node.metadata.stats && (
            <>
                <span className={`flex items-center ${node.metadata.stats.sentiment > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    <FaceSmileIcon className="w-3 h-3 mr-1" />
                    Sent: {node.metadata.stats.sentiment.toFixed(2)}
                </span>
                <span className="text-blue-400">Read: {node.metadata.stats.readingLevel}</span>
                <span className="text-yellow-400">Emotions: {node.metadata.stats.emotions?.slice(0, 2).join(', ')}</span>
            </>
        )}
    </div>
);

// --- JSON EXPLORER COMPONENT ---

interface JsonTreeProps {
    data: any;
    path: string;
    level: number;
    onPick: (path: string, type: 'Array' | 'Object') => void;
    pickingMode: 'l8' | 'l5' | null;
    currentL8: string;
    currentL5: string;
}

const JsonTree: React.FC<JsonTreeProps> = ({ data, path, level, onPick, pickingMode, currentL8, currentL5 }) => {
    const [expanded, setExpanded] = useState(level < 1);

    // Safety check for circular or massive data
    if (level > 4) return <div className="ml-4 text-slate-600">...</div>;

    const isArray = Array.isArray(data);
    const isObject = typeof data === 'object' && data !== null && !isArray;

    const isSelectedL8 = path === currentL8;
    const isSelectedL5 = path === currentL5;

    const canPickL8 = pickingMode === 'l8' && isArray;
    // Can pick L5 if we are inside an object (likely a convo item) or it's an array of messages
    const canPickL5 = pickingMode === 'l5' && (isArray || isObject);

    const handlePick = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (canPickL8) onPick(path, 'Array');
        else if (canPickL5) onPick(path, isArray ? 'Array' : 'Object');
    };

    const renderLabel = () => {
        const parts = path.split('.');
        const label = parts[parts.length - 1] || 'root';

        let typeLabel = '';
        if (isArray) typeLabel = `Array(${data.length})`;
        else if (isObject) typeLabel = `Object{${Object.keys(data).length}}`;
        else typeLabel = String(data);

        return (
            <div
                className={`
                    flex items-center group py-1 px-2 rounded cursor-pointer transition-colors
                    ${(canPickL8 || canPickL5) ? 'hover:bg-indigo-900/30' : ''}
                    ${(isSelectedL8 || isSelectedL5) ? 'bg-indigo-900/50 border border-indigo-500/50' : ''}
                `}
                onClick={() => (isArray || isObject) && setExpanded(!expanded)}
                title="Expand/Collapse or Select Node"
            >
                {(isArray || isObject) && (
                    <span className="mr-1 text-slate-500">
                        {expanded ? <ChevronDownIcon className="w-3 h-3" /> : <ChevronRightIcon className="w-3 h-3" />}
                    </span>
                )}
                <span className="text-xs font-mono text-pink-300 mr-2">{label}</span>
                <span className="text-[10px] text-slate-500 mr-2">{typeLabel}</span>

                {/* Pick Action */}
                {(canPickL8 || canPickL5) && (
                    <button
                        onClick={handlePick}
                        title="Select this path for analysis"
                        className="opacity-0 group-hover:opacity-100 bg-indigo-600 hover:bg-indigo-500 text-white text-[9px] px-2 py-0.5 rounded ml-auto flex items-center"
                    >
                        <CursorArrowRaysIcon className="w-3 h-3 mr-1" />
                        Select
                    </button>
                )}
                {(isSelectedL8 || isSelectedL5) && (
                    <span className="ml-auto text-green-400">
                        <CheckIcon className="w-4 h-4" />
                    </span>
                )}
            </div>
        );
    };

    if (!isObject && !isArray) return <div className="ml-4 py-0.5 text-[10px] text-slate-600">{renderLabel()}</div>;

    return (
        <div className="ml-2 border-l border-slate-800/50 pl-2">
            {renderLabel()}
            {expanded && (
                <div>
                    {isArray ? (
                        <>
                            {/* Render schema of first item only to avoid massive lists */}
                            {data.length > 0 && (
                                <div className="ml-2">
                                    <div className="text-[9px] text-slate-600 uppercase mb-1">Item Schema (Index 0)</div>
                                    <JsonTree
                                        data={data[0]}
                                        path={`${path}[]`}
                                        level={level + 1}
                                        onPick={onPick}
                                        pickingMode={pickingMode}
                                        currentL8={currentL8}
                                        currentL5={currentL5}
                                    />
                                </div>
                            )}
                        </>
                    ) : (
                        Object.keys(data).slice(0, 15).map(key => (
                            <JsonTree
                                key={key}
                                data={data[key]}
                                path={`${path}.${key}`}
                                level={level + 1}
                                onPick={onPick}
                                pickingMode={pickingMode}
                                currentL8={currentL8}
                                currentL5={currentL5}
                            />
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

// --- MAIN COMPONENT ---

const EnrichmentView: React.FC<EnrichmentViewProps> = ({ modelConfig, isLoading, onSetLoading }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [rootNode, setRootNode] = useState<SpinalNode | null>(null);

    // Analysis State
    const [analysis, setAnalysis] = useState<StructureAnalysis | null>(null);
    const [l8Path, setL8Path] = useState<string>('root');
    const [l5Path, setL5Path] = useState<string>('');

    // UI State
    const [pickingMode, setPickingMode] = useState<'l8' | 'l5' | null>(null);

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.length) return;
        const file = e.target.files[0];
        onSetLoading(true);
        try {
            if (file.name.endsWith('.json')) {
                const result = await analyzeJsonStructure(file);
                setAnalysis(result);
                setL8Path('root'); // Reset
                setL5Path('');
            } else {
                // Text file fallback
                const text = await file.text();
                const node = await generateSpinalEnrichment("Text Document", [{ role: 'user', content: text }], modelConfig.id);
                setRootNode(node);
                setAnalysis(null);
            }
        } catch (err) {
            console.error(err);
            alert("Analysis failed. Ensure valid format.");
        } finally {
            onSetLoading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    };

    const handleGenerateSpine = async () => {
        if (!analysis) return;
        onSetLoading(true);
        try {
            const conversations = processStructuredImport(analysis, { l8Path, l5Path });

            if (conversations.length === 0) throw new Error("No conversations found with current mapping.");

            if (conversations.length === 1) {
                const node = await generateSpinalEnrichment(`Conversation 1`, conversations[0], modelConfig.id);
                setRootNode(node);
            } else {
                const longest = conversations.sort((a, b) => b.length - a.length)[0];
                const node = await generateSpinalEnrichment(`Dominant Conversation (${conversations.length} total)`, longest, modelConfig.id);
                setRootNode(node);
            }

            setAnalysis(null);
        } catch (e: any) {
            alert(`Generation failed: ${e.message}`);
        } finally {
            onSetLoading(false);
        }
    };

    // Tree Node Visualization Helper (For the result)
    const TreeNode: React.FC<{ node: SpinalNode, depth?: number }> = ({ node, depth = 0 }) => {
        const [expanded, setExpanded] = useState(depth < 2);
        return (
            <div className={`ml-${depth * 2} border-l border-slate-800 pl-4 py-2`}>
                <div className="bg-slate-900 p-3 rounded-lg hover:bg-slate-800 transition-colors cursor-pointer" onClick={() => setExpanded(!expanded)} title="Expand/Collapse">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                            {node.children && node.children.length > 0 && (
                                expanded ? <ChevronDownIcon className="w-4 h-4 text-slate-500" /> : <ChevronRightIcon className="w-4 h-4 text-slate-500" />
                            )}
                            <span className={`text-xs font-bold px-2 py-0.5 rounded ${node.level === 'L8' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-300'}`}>
                                {node.level}
                            </span>
                            <span className="text-sm font-medium text-slate-200 truncate max-w-md">
                                {node.level === 'L5' ? `"${node.content.substring(0, 50)}..."` : node.content}
                            </span>
                        </div>
                        <span className="text-[10px] text-slate-600 uppercase">{node.metadata.role}</span>
                    </div>
                    {renderStats(node)}
                </div>
                {expanded && node.children && (
                    <div className="mt-2">
                        {node.children.map((child, i) => <TreeNode key={i} node={child} depth={depth + 1} />)}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="h-full flex flex-col p-6 max-w-[1600px] mx-auto w-full overflow-y-auto scrollbar-thin">
            <div className="flex justify-between items-end mb-8">
                <div>
                    <h1 className="text-3xl font-black text-white mb-2 flex items-center">
                        <ChartBarSquareIcon className="w-8 h-8 mr-3 text-pink-500" />
                        Spinal Enrichment
                    </h1>
                    <p className="text-slate-400 max-w-2xl">
                        Map your data structure to generate deep NLP analytics.
                    </p>
                </div>

                <div className="flex space-x-3">
                    {rootNode && (
                        <button
                            onClick={() => { setRootNode(null); setAnalysis(null); }}
                            className="text-slate-400 hover:text-white text-xs font-bold underline"
                            title="Reset analysis view"
                        >
                            Start Over
                        </button>
                    )}
                    <button
                        onClick={() => !isLoading && fileInputRef.current?.click()}
                        disabled={isLoading}
                        title="Upload JSON export or Text file"
                        className={`
                            flex items-center space-x-2 px-6 py-3 rounded-xl transition-all shadow-lg font-bold border
                            ${isLoading
                                ? 'bg-slate-800 text-slate-500 border-slate-700 cursor-wait'
                                : 'bg-slate-800 hover:bg-slate-700 text-pink-400 border-pink-900/50 hover:border-pink-500'}
                        `}
                    >
                        {isLoading ? (
                            <ArrowPathIcon className="w-5 h-5 animate-spin" />
                        ) : (
                            <ArrowUpTrayIcon className="w-5 h-5" />
                        )}
                        <span>{isLoading ? 'Processing...' : 'Upload Data'}</span>
                    </button>
                </div>

                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleUpload}
                    className="hidden"
                    accept=".json,.txt"
                />
            </div>

            {/* MAPPING WIZARD */}
            {analysis && (
                <div className="bg-slate-900 rounded-2xl border border-slate-800 p-6 mb-6 shadow-2xl flex flex-col md:flex-row gap-6 h-[600px]">

                    {/* LEFT: JSON VIEWER */}
                    <div className="flex-1 flex flex-col min-w-0 border-r border-slate-800 pr-6">
                        <h3 className="text-slate-300 font-bold uppercase text-xs mb-4 flex items-center">
                            <ListBulletIcon className="w-4 h-4 mr-2" />
                            Structure Explorer
                        </h3>
                        <div className="bg-slate-950 rounded-xl border border-slate-800 flex-1 overflow-auto p-4 scrollbar-thin font-mono text-sm relative">
                            {pickingMode && (
                                <div className="absolute top-2 right-2 z-10 bg-indigo-600 text-white text-[10px] px-2 py-1 rounded shadow animate-pulse">
                                    Picking {pickingMode === 'l8' ? 'Conversation Root' : 'Message Sequence'}...
                                </div>
                            )}
                            <JsonTree
                                data={analysis.rawJson}
                                path="root"
                                level={0}
                                onPick={(p, _type) => {
                                    if (pickingMode === 'l8') setL8Path(p);
                                    if (pickingMode === 'l5') setL5Path(p);
                                    setPickingMode(null);
                                }}
                                pickingMode={pickingMode}
                                currentL8={l8Path}
                                currentL5={l5Path}
                            />
                        </div>
                    </div>

                    {/* RIGHT: CONFIG PANEL */}
                    <div className="w-full md:w-96 flex flex-col gap-6">
                        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
                            <div className="flex items-center justify-between mb-3">
                                <label className="block text-sm font-bold text-white flex items-center">
                                    <ChatBubbleLeftRightIcon className="w-4 h-4 mr-2 text-indigo-400" />
                                    Conversation Root
                                </label>
                                <button
                                    onClick={() => setPickingMode(pickingMode === 'l8' ? null : 'l8')}
                                    title="Select the array containing conversations"
                                    className={`text-[10px] px-2 py-1 rounded border transition-colors ${pickingMode === 'l8' ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'}`}
                                >
                                    {pickingMode === 'l8' ? 'Cancel Pick' : 'Pick from Tree'}
                                </button>
                            </div>
                            <p className="text-slate-500 text-xs mb-3">
                                Select the main <strong>Array</strong> that lists all conversations.
                            </p>
                            <div className="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs font-mono text-indigo-300 truncate">
                                {l8Path || 'Not Selected'}
                            </div>
                        </div>

                        <div className="bg-slate-950 p-5 rounded-xl border border-slate-800">
                            <div className="flex items-center justify-between mb-3">
                                <label className="block text-sm font-bold text-white flex items-center">
                                    <ListBulletIcon className="w-4 h-4 mr-2 text-pink-400" />
                                    Message Sequence
                                </label>
                                <button
                                    onClick={() => setPickingMode(pickingMode === 'l5' ? null : 'l5')}
                                    title="Select the list of messages within a conversation"
                                    className={`text-[10px] px-2 py-1 rounded border transition-colors ${pickingMode === 'l5' ? 'bg-pink-600 text-white border-pink-500' : 'bg-slate-800 text-slate-400 border-slate-700 hover:text-white'}`}
                                >
                                    {pickingMode === 'l5' ? 'Cancel Pick' : 'Pick from Tree'}
                                </button>
                            </div>
                            <p className="text-slate-500 text-xs mb-3">
                                Expand a conversation in the tree and select the <strong>field</strong> containing messages.
                            </p>
                            <div className="bg-slate-900 border border-slate-700 rounded px-3 py-2 text-xs font-mono text-pink-300 truncate">
                                {l5Path || 'Not Selected (Will attempt auto-detect)'}
                            </div>
                        </div>

                        <div className="mt-auto">
                            <button
                                onClick={handleGenerateSpine}
                                disabled={isLoading || l8Path === 'Not Selected'}
                                title="Run spinal analysis on configured structure"
                                className={`
                                    w-full relative overflow-hidden px-8 py-4 rounded-xl font-bold text-white shadow-xl flex items-center justify-center transition-all
                                    ${isLoading
                                        ? 'bg-slate-700 cursor-not-allowed opacity-80'
                                        : 'bg-gradient-to-r from-pink-600 to-indigo-600 hover:from-pink-500 hover:to-indigo-500 hover:scale-[1.02] active:scale-[0.98]'}
                                `}
                            >
                                <ArrowPathIcon className={`w-5 h-5 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                                <span>{isLoading ? 'Processing...' : 'Generate Analysis'}</span>
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* VISUALIZATION MODE */}
            <div className="flex-1 bg-slate-950 rounded-2xl border border-slate-800 overflow-y-auto p-6 scrollbar-thin shadow-inner min-h-[400px]">
                {!rootNode && !analysis && (
                    <div className="flex flex-col items-center justify-center h-full text-slate-600 opacity-50">
                        <ChartBarSquareIcon className="w-24 h-24 mb-6 text-slate-700" />
                        <h3 className="text-xl font-bold text-slate-500 mb-2">Ready for Spinal Analysis</h3>
                        <p className="max-w-md text-center">Upload a JSON conversation export (ChatGPT, Claude, etc.) to visualize the structural semantics.</p>
                    </div>
                )}
                {rootNode && (
                    <div className="animate-in fade-in zoom-in-95 duration-500">
                        <TreeNode node={rootNode} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default EnrichmentView;