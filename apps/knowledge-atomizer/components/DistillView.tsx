
import React, { useRef, useState, useMemo } from 'react';
import { KnowledgeAtom, UploadedDocument } from '../types';
import { synthesizeDocuments, synthesizeAtomsToDocument } from '../services/geminiService';
import { FILE_CONFIG, CERTAINTY_COLORS, STAKES_COLORS, MODEL_CONFIG, DEV_CONFIG } from '../config';
import {
  DocumentTextIcon, ArrowUpTrayIcon, BeakerIcon, ArrowDownTrayIcon,
  TagIcon, MagnifyingGlassIcon, TrashIcon, PlusCircleIcon,
  ArrowPathIcon, Squares2X2Icon, DocumentDuplicateIcon, BoltIcon,
  PlusSmallIcon, ExclamationCircleIcon, PencilSquareIcon,
  ChevronDownIcon, ChevronRightIcon, LinkIcon, ScaleIcon,
  RocketLaunchIcon, LightBulbIcon
} from '@heroicons/react/24/outline';

interface DistillViewProps {
  documents: UploadedDocument[];
  atoms: KnowledgeAtom[];
  activeAtoms: KnowledgeAtom[];
  isProcessing: boolean;
  onUpload: (files: FileList | File[]) => void;
  onRemoveDocument: (id: string) => void;
  onDistill: () => void;
  onExport: () => void;
  onRefine: () => void;
  onDeleteAtoms: (ids: string[]) => void;
  onBulkAddToContext: (atoms: KnowledgeAtom[]) => void;
  onRegenerateEmbeddings: (atoms: KnowledgeAtom[]) => void;
  onFindRelated: (atom: KnowledgeAtom) => void;
  onSuggestTags: (atom: KnowledgeAtom) => void;
  onAutoTagAll: (atoms: KnowledgeAtom[]) => void;
  canDistill: boolean;
  onAddDocument: (doc: UploadedDocument) => void;
  onAddTag: (atomId: string, tag: string) => void;
  onRetryEmbedding?: (atom: KnowledgeAtom) => void;
  onUpdateDocument?: (id: string, updates: Partial<UploadedDocument>) => void;
  onBulkAddTag?: (atoms: KnowledgeAtom[], tag: string) => void;
}


// Supported file types - imported from config
const ACCEPTED_FILE_TYPES = FILE_CONFIG.acceptString;

// Expandable Dimension Panel Component
const DimensionPanel: React.FC<{
  title: string;
  icon: React.ReactNode;
  color: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}> = ({ title, icon, color, children, defaultExpanded = false }) => {
  const [expanded, setExpanded] = useState(defaultExpanded);
  return (
    <div className={`border rounded-lg ${color} mt-2`}>
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2 text-xs font-bold uppercase tracking-wider"
      >
        <span className="flex items-center gap-2">
          {icon}
          {title}
        </span>
        {expanded ? <ChevronDownIcon className="w-3 h-3" /> : <ChevronRightIcon className="w-3 h-3" />}
      </button>
      {expanded && <div className="px-3 pb-3 text-xs space-y-1">{children}</div>}
    </div>
  );
};

// Mini badge for array items
const MiniTag: React.FC<{ text: string; color?: string }> = ({ text, color = 'bg-slate-800 text-slate-300' }) => (
  <span className={`${color} px-1.5 py-0.5 rounded text-[9px] font-mono`}>{text}</span>
);

// Progress bar for numeric values - prefixed with _ since unused but kept for future use
const _MiniBar: React.FC<{ value: number; label: string; color?: string }> = ({ value, label, color = 'bg-indigo-500' }) => (
  <div className="flex items-center gap-2">
    <span className="text-slate-500 w-24 text-[10px]">{label}</span>
    <div className="flex-1 h-1.5 bg-slate-800 rounded-full overflow-hidden">
      <div className={`h-full ${color} rounded-full`} style={{ width: `${value * 100}%` }} />
    </div>
    <span className="text-slate-400 text-[10px] w-8 text-right">{Math.round(value * 100)}%</span>
  </div>
);

const DistillView: React.FC<DistillViewProps> = ({
  documents,
  atoms,
  activeAtoms,
  isProcessing,
  onUpload,
  onRemoveDocument,
  onDistill,
  onExport: _onExport,
  onRefine,
  onDeleteAtoms,
  onBulkAddToContext,
  onRegenerateEmbeddings,
  onFindRelated,
  onSuggestTags: _onSuggestTags,
  onAutoTagAll,
  canDistill,
  onAddDocument,
  onAddTag,
  onRetryEmbedding,
  onUpdateDocument,
  onBulkAddTag
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [viewMode, setViewMode] = useState<'atoms' | 'documents'>('atoms');
  const [includeFrontMatter, _setIncludeFrontMatter] = useState(false);

  // Search & Select State
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedAtomIds, setSelectedAtomIds] = useState<Set<string>>(new Set());
  const [selectedDocIds, setSelectedDocIds] = useState<Set<string>>(new Set());

  // UI State for editing
  const [addingTagToAtom, setAddingTagToAtom] = useState<string | null>(null);
  const [addingTagToDoc, setAddingTagToDoc] = useState<string | null>(null);
  const [renamingDocId, setRenamingDocId] = useState<string | null>(null);
  const [newTagText, setNewTagText] = useState("");
  const [newDocTitle, setNewDocTitle] = useState("");

  // Bulk Tag Input
  const [bulkTagText, setBulkTagText] = useState("");
  const [_isBulkTagging, setIsBulkTagging] = useState(false);

  const activeAtomIds = useMemo(() => new Set(activeAtoms.map(a => a.id)), [activeAtoms]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      // CRITICAL: Create a copy of files BEFORE any reset
      // FileList is a live object that becomes invalid when input is cleared
      const filesCopy: File[] = Array.from(e.target.files);
      if (DEV_CONFIG.verbose) {
        console.log(`${DEV_CONFIG.logPrefix} Uploading ${filesCopy.length} file(s):`,
          filesCopy.map(f => f.name));
      }

      // Clear input FIRST to allow re-selecting same files
      if (fileInputRef.current) fileInputRef.current.value = '';

      // Then process - the array copy is independent of the input
      onUpload(filesCopy);

      // Auto-switch to docs view so user sees uploaded files
      setViewMode('documents');
    }
  };

  // Robust Search Logic
  const filteredAtoms = useMemo(() => {
    if (!searchQuery) return atoms;
    const q = searchQuery.toLowerCase();
    return atoms.filter(a =>
      a.content.toLowerCase().includes(q) ||
      a.metadata?.theme.toLowerCase().includes(q) ||
      a.metadata?.tags.some(t => t.toLowerCase().includes(q)) ||
      a.sourceFile.toLowerCase().includes(q)
    );
  }, [atoms, searchQuery]);

  const filteredDocs = useMemo(() => {
    if (!searchQuery) return documents;
    const q = searchQuery.toLowerCase();
    return documents.filter(d => d.name.toLowerCase().includes(q) || d.content.toLowerCase().includes(q));
  }, [documents, searchQuery]);

  // Selection Logic
  const toggleSelection = (id: string, type: 'atom' | 'doc') => {
    if (type === 'atom') {
      const next = new Set(selectedAtomIds);
      if (next.has(id)) next.delete(id); else next.add(id);
      setSelectedAtomIds(next);
    } else {
      const next = new Set(selectedDocIds);
      if (next.has(id)) next.delete(id); else next.add(id);
      setSelectedDocIds(next);
    }
  };

  const selectAll = () => {
    if (viewMode === 'atoms') {
      if (selectedAtomIds.size === filteredAtoms.length) setSelectedAtomIds(new Set());
      else setSelectedAtomIds(new Set(filteredAtoms.map(a => a.id)));
    } else {
      if (selectedDocIds.size === filteredDocs.length) setSelectedDocIds(new Set());
      else setSelectedDocIds(new Set(filteredDocs.map(d => d.id)));
    }
  };

  const handleBulkAction = async (action: 'delete' | 'context' | 'embed' | 'synthesize') => {
    const selected = atoms.filter(a => selectedAtomIds.has(a.id));
    if (selected.length === 0) return;

    if (action === 'delete') {
      if (confirm(`Delete ${selected.length} atoms?`)) {
        onDeleteAtoms(Array.from(selectedAtomIds));
        setSelectedAtomIds(new Set());
      }
    } else if (action === 'context') {
      onBulkAddToContext(selected);
      setSelectedAtomIds(new Set());
    } else if (action === 'embed') {
      onRegenerateEmbeddings(selected);
      setSelectedAtomIds(new Set());
    } else if (action === 'synthesize') {
      try {
        // Synthesize with comprehensive analysis
        const doc = await synthesizeAtomsToDocument(selected, 'Comprehensive', MODEL_CONFIG.synthesisModel);
        onAddDocument(doc);
        alert("Synthesis complete! A new document has been created from your atoms.");
        setSelectedAtomIds(new Set());
      } catch (_e) {
        alert("Failed to synthesize atoms.");
      }
    }
  };

  const handleSynthesizeDocs = async () => {
    const selectedDocs = documents.filter(d => selectedDocIds.has(d.id));
    if (selectedDocs.length < 2) {
      alert("Select at least 2 documents to synthesize.");
      return;
    }
    try {
      const synthDoc = await synthesizeDocuments(selectedDocs, 'Comprehensive', MODEL_CONFIG.synthesisModel, includeFrontMatter);
      onAddDocument(synthDoc);
      setSelectedDocIds(new Set());
      alert("Synthesis Complete! New document added.");
    } catch (_e) {
      alert("Synthesis failed.");
    }
  };

  // Prefixed with _ since assigned but currently called internally
  const _submitBulkTag = () => {
    if (!bulkTagText.trim() || !onBulkAddTag) return;
    onBulkAddTag(filteredAtoms, bulkTagText);
    setBulkTagText("");
    setIsBulkTagging(false);
  };

  const handleExportMd = (doc: UploadedDocument) => {
    const blob = new Blob([doc.content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = doc.name.endsWith('.md') ? doc.name : `${doc.name}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Atom Tagging
  const submitNewTagForAtom = (atomId: string) => {
    if (newTagText.trim()) {
      onAddTag(atomId, newTagText.trim());
    }
    setAddingTagToAtom(null);
    setNewTagText("");
  };

  // Doc Tagging & Renaming
  const submitNewTagForDoc = (docId: string, currentTags: string[]) => {
    if (newTagText.trim() && onUpdateDocument) {
      onUpdateDocument(docId, { tags: [...currentTags, newTagText.trim()] });
    }
    setAddingTagToDoc(null);
    setNewTagText("");
  };

  const startRenaming = (doc: UploadedDocument) => {
    setRenamingDocId(doc.id);
    setNewDocTitle(doc.name);
  };

  const submitRenaming = (docId: string) => {
    if (newDocTitle.trim() && onUpdateDocument) {
      onUpdateDocument(docId, { name: newDocTitle.trim() });
    }
    setRenamingDocId(null);
    setNewDocTitle("");
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto p-4 md:p-6 w-full relative">

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:h-full min-h-0">

        {/* Left Column: Input */}
        <div className="lg:col-span-3 flex flex-col gap-4">
          <div
            onClick={() => !isProcessing && fileInputRef.current?.click()}
            title="Click to upload documents or scripts for analysis"
            className={`
              border-2 border-dashed border-slate-700 rounded-xl p-6
              flex flex-col items-center justify-center text-center
              cursor-pointer transition-all hover:border-primary-500 hover:bg-slate-800/50
              ${isProcessing ? 'opacity-50 cursor-wait' : ''}
            `}
          >
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              className="hidden"
              multiple={true}
              accept={ACCEPTED_FILE_TYPES}
              aria-label="Upload multiple files"
            />
            <ArrowUpTrayIcon className="w-8 h-8 text-slate-500 mb-2" />
            <h3 className="text-slate-200 font-bold text-sm">Upload Sources</h3>
            <p className="text-slate-500 text-xs mt-1">Documents & Scripts</p>
            <p className="text-slate-600 text-[10px] mt-0.5">.md .txt .json .js .ts .py .zip</p>
          </div>

          <button
            onClick={onDistill}
            disabled={!canDistill || isProcessing}
            title="Extract 12-dimensional Knowledge Atoms from sources"
            className={`
              w-full py-3 rounded-xl font-bold text-sm shadow-lg flex items-center justify-center space-x-2
              transition-all transform hover:scale-[1.02] active:scale-[0.98]
              ${canDistill && !isProcessing
                ? 'bg-gradient-to-r from-primary-600 to-indigo-600 text-white hover:shadow-primary-500/25'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'}
            `}
          >
            {isProcessing ? <ArrowPathIcon className="w-5 h-5 animate-spin" /> : <BeakerIcon className="w-5 h-5" />}
            <span>{isProcessing ? 'Distilling...' : 'Distill to Atoms'}</span>
          </button>

          {/* Source Stats */}
          {documents.length > 0 && (
            <div className="bg-slate-900/30 rounded-lg p-3 border border-slate-800/50">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-500">Sources loaded</span>
                <span className="text-slate-300 font-mono">{documents.length}</span>
              </div>
              <div className="flex justify-between items-center text-xs mt-1">
                <span className="text-slate-500">Total size</span>
                <span className="text-slate-300 font-mono">{Math.round(documents.reduce((sum, d) => sum + d.size, 0) / 1024)} KB</span>
              </div>
              {atoms.length > 0 && (
                <div className="flex justify-between items-center text-xs mt-1 pt-1 border-t border-slate-800/50">
                  <span className="text-slate-500">Atoms extracted</span>
                  <span className="text-indigo-400 font-mono">{atoms.length}</span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Column: Data View */}
        <div className="lg:col-span-9 flex flex-col gap-4 lg:h-full relative min-h-[500px]">

          {/* Top Bar: Toggles & Actions */}
          <div className="bg-slate-900 p-3 rounded-xl border border-slate-800 flex flex-col gap-3">
            <div className="flex flex-col md:flex-row justify-between items-center gap-3">
              {/* View Mode Toggle */}
              <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800 self-start md:self-auto">
                <button
                  onClick={() => setViewMode('atoms')}
                  title="View individual knowledge atoms"
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'atoms' ? 'bg-indigo-600 text-white shadow' : 'text-slate-500 hover:text-slate-300'}`}
                >
                  <BeakerIcon className="w-4 h-4" />
                  <span>Atoms</span>
                </button>
                <button
                  onClick={() => setViewMode('documents')}
                  title="View source documents"
                  className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'documents' ? 'bg-emerald-600 text-white shadow' : 'text-slate-500 hover:text-slate-300'}`}
                >
                  <DocumentDuplicateIcon className="w-4 h-4" />
                  <span>Docs</span>
                </button>
              </div>

              {/* Search */}
              <div className="relative w-full md:w-72">
                <MagnifyingGlassIcon className="absolute left-3 top-2.5 w-4 h-4 text-slate-500" />
                <input
                  type="text"
                  placeholder={viewMode === 'atoms' ? "Filter by tag, theme, or content..." : "Search documents..."}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
                />
              </div>
            </div>

            {/* Synthesize Action (Docs) - when multiple docs selected */}
            {viewMode === 'documents' && selectedDocIds.size >= 2 && (
              <div className="flex pt-2 border-t border-slate-800/50">
                <button
                  onClick={handleSynthesizeDocs}
                  disabled={isProcessing}
                  title="Merge selected documents into a new unified document"
                  className="px-4 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-lg disabled:opacity-50 whitespace-nowrap flex items-center"
                >
                  {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" /> : <BoltIcon className="w-3 h-3 mr-1" />}
                  Synthesize Selected ({selectedDocIds.size})
                </button>
              </div>
            )}

            {/* Bulk Actions Row */}
            {viewMode === 'atoms' && atoms.length > 0 && (
              <div className="flex items-center gap-2 pt-2 border-t border-slate-800/50 overflow-x-auto scrollbar-none">
                <button onClick={onRefine} disabled={isProcessing} className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-900/50 rounded-lg text-[10px] font-bold uppercase tracking-wider flex items-center whitespace-nowrap disabled:opacity-50">
                  {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" /> : null}
                  Refine Significance
                </button>
                <button
                  onClick={() => onAutoTagAll(atoms)}
                  disabled={isProcessing}
                  className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-900/50 rounded-lg text-[10px] font-bold uppercase tracking-wider flex items-center whitespace-nowrap disabled:opacity-50"
                >
                  {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" /> : null}
                  Auto-Tag All
                </button>

                {selectedAtomIds.size > 0 && (
                  <button
                    onClick={() => handleBulkAction('synthesize')}
                    disabled={isProcessing}
                    className="px-3 py-1 bg-emerald-900/40 hover:bg-emerald-800 text-emerald-400 border border-emerald-900/50 rounded-lg text-[10px] font-bold uppercase tracking-wider flex items-center whitespace-nowrap disabled:opacity-50"
                  >
                    {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin" /> : <DocumentTextIcon className="w-3 h-3 mr-1" />}
                    Synthesize to Doc
                  </button>
                )}

                <div className="w-px h-4 bg-slate-800 mx-1"></div>

                <div className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={selectedAtomIds.size === filteredAtoms.length && filteredAtoms.length > 0}
                    onChange={selectAll}
                    className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500 w-3 h-3"
                  />
                  <span className="text-[10px] text-slate-500 uppercase">{selectedAtomIds.size} selected</span>
                </div>

                {selectedAtomIds.size > 0 && (
                  <div className="flex items-center gap-2 animate-in fade-in">
                    <button onClick={() => handleBulkAction('context')} className="p-1 hover:bg-slate-800 rounded text-yellow-400" title="Add to Context"><PlusCircleIcon className="w-4 h-4" /></button>
                    <button onClick={() => handleBulkAction('embed')} className="p-1 hover:bg-slate-800 rounded text-cyan-400" title="Force Embed"><BoltIcon className="w-4 h-4" /></button>
                    <button onClick={() => handleBulkAction('delete')} className="p-1 hover:bg-slate-800 rounded text-red-400" title="Delete Selected"><TrashIcon className="w-4 h-4" /></button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Content List */}
          <div className="flex-1 overflow-y-auto scrollbar-thin space-y-4 rounded-xl bg-slate-950/30 p-2">
            {viewMode === 'atoms' ? (
              filteredAtoms.length === 0 ? (
                <div className="text-center text-slate-500 mt-20 opacity-60">
                  <BeakerIcon className="w-12 h-12 mx-auto mb-3" />
                  <p>No atoms found. Distill documents or adjust filters.</p>
                </div>
              ) : (
                filteredAtoms.map(atom => {
                  const meta = atom.metadata;
                  const hasRichMeta = meta?.semantic || meta?.epistemic;

                  return (
                    <div key={atom.id} className={`bg-slate-900 border ${activeAtomIds.has(atom.id) ? 'border-yellow-500/30 shadow-[0_0_10px_rgba(234,179,8,0.1)]' : 'border-slate-800'} rounded-xl p-4 transition-all hover:border-slate-600 group`}>
                      {/* Header Row */}
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center flex-wrap gap-2">
                          <input
                            type="checkbox"
                            checked={selectedAtomIds.has(atom.id)}
                            onChange={() => toggleSelection(atom.id, 'atom')}
                            className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5"
                          />
                          {/* Significance Badge */}
                          <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded border ${meta?.significance === 'Fundamental' ? 'bg-rose-900/30 text-rose-400 border-rose-900/50' :
                            meta?.significance === 'Insight' ? 'bg-purple-900/30 text-purple-400 border-purple-900/50' :
                              meta?.significance === 'Prediction' ? 'bg-cyan-900/30 text-cyan-400 border-cyan-900/50' :
                                'bg-slate-800 text-slate-400 border-slate-700'
                            }`}>
                            {meta?.significance}
                          </span>
                          {/* Certainty Badge (NEW) */}
                          {meta?.epistemic?.certainty && (
                            <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded border ${CERTAINTY_COLORS[meta.epistemic.certainty] || 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                              {meta.epistemic.certainty}
                            </span>
                          )}
                          {/* Domain Badge (NEW) */}
                          {meta?.semantic?.domain && (
                            <span className="text-[9px] text-slate-400 bg-slate-800/50 px-2 py-0.5 rounded">
                              {meta.semantic.domain}
                            </span>
                          )}
                          {/* Theme */}
                          <span className="text-[9px] text-slate-500 uppercase font-mono">{meta?.theme}</span>
                          {/* Enrichment Coverage (NEW) */}
                          {meta?.enrichment_coverage !== undefined && (
                            <span className={`text-[8px] px-1.5 py-0.5 rounded-full ${meta.enrichment_coverage > 80 ? 'bg-emerald-900/30 text-emerald-400' :
                              meta.enrichment_coverage > 50 ? 'bg-yellow-900/30 text-yellow-400' :
                                'bg-slate-800 text-slate-500'
                              }`} title="Enrichment coverage">
                              {meta.enrichment_coverage}%
                            </span>
                          )}
                          {atom.embeddingStatus === 'failed' && <span className="text-red-500 text-[9px]" title="Embedding failed"><ExclamationCircleIcon className="w-3 h-3" /></span>}
                          {atom.embeddingStatus === 'pending' && <span className="text-slate-600 text-[9px]" title="Embedding..."><ArrowPathIcon className="w-3 h-3 animate-spin" /></span>}
                        </div>
                        <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          {onRetryEmbedding && atom.embeddingStatus === 'failed' && (
                            <button onClick={() => onRetryEmbedding(atom)} title="Retry Embedding" className="p-1 text-slate-400 hover:text-cyan-400"><ArrowPathIcon className="w-4 h-4" /></button>
                          )}
                          <button onClick={() => onFindRelated(atom)} title="Find related atoms" className="p-1 text-slate-400 hover:text-cyan-400"><Squares2X2Icon className="w-4 h-4" /></button>
                          <button onClick={() => onBulkAddToContext([atom])} title="Add to context" className="p-1 text-slate-400 hover:text-yellow-400"><PlusCircleIcon className="w-4 h-4" /></button>
                        </div>
                      </div>

                      {/* Content */}
                      <p className="text-slate-300 text-sm mb-3 leading-relaxed font-light">{atom.content}</p>

                      {/* Quick Stats Row (NEW) */}
                      {hasRichMeta && (
                        <div className="flex flex-wrap gap-3 mb-3 py-2 px-3 bg-slate-950/50 rounded-lg border border-slate-800/50">
                          {meta?.significance_analysis && (
                            <>
                              <div className="text-[10px]">
                                <span className="text-slate-500">Novel:</span>{' '}
                                <span className="text-indigo-400 font-mono">{Math.round((meta.significance_analysis.novelty ?? 0.5) * 100)}%</span>
                              </div>
                              <div className="text-[10px]">
                                <span className="text-slate-500">Action:</span>{' '}
                                <span className="text-emerald-400 font-mono">{Math.round((meta.significance_analysis.actionability ?? 0.5) * 100)}%</span>
                              </div>
                            </>
                          )}
                          {meta?.affective && (
                            <>
                              <div className="text-[10px]">
                                <span className="text-slate-500">Sent:</span>{' '}
                                <span className={meta.affective.sentiment > 0 ? 'text-emerald-400' : meta.affective.sentiment < 0 ? 'text-red-400' : 'text-slate-400'}>
                                  {meta.affective.sentiment > 0 ? '+' : ''}{meta.affective.sentiment?.toFixed(1)}
                                </span>
                              </div>
                              <div className="text-[10px]">
                                <span className="text-slate-500">Stakes:</span>{' '}
                                <span className={STAKES_COLORS[meta.affective.stakes] || 'text-slate-400'}>{meta.affective.stakes}</span>
                              </div>
                            </>
                          )}
                          {meta?.temporal?.scope && (
                            <div className="text-[10px]">
                              <span className="text-slate-500">Scope:</span>{' '}
                              <span className="text-cyan-400">{meta.temporal.scope}</span>
                            </div>
                          )}
                        </div>
                      )}

                      {/* Expandable Dimensional Panels (NEW) */}
                      {hasRichMeta && (
                        <div className="space-y-1">
                          {/* Relational */}
                          {meta?.relational && (meta.relational.entities?.length > 0 || meta.relational.concepts?.length > 0) && (
                            <DimensionPanel
                              title="Connections"
                              icon={<LinkIcon className="w-3 h-3" />}
                              color="border-blue-900/30 text-blue-300"
                            >
                              {meta.relational.entities?.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  <span className="text-slate-500 mr-1">Entities:</span>
                                  {meta.relational.entities.map((e, i) => <MiniTag key={i} text={e} color="bg-blue-900/30 text-blue-300" />)}
                                </div>
                              )}
                              {meta.relational.concepts?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  <span className="text-slate-500 mr-1">Concepts:</span>
                                  {meta.relational.concepts.map((c, i) => <MiniTag key={i} text={c} color="bg-indigo-900/30 text-indigo-300" />)}
                                </div>
                              )}
                              {meta.relational.implications?.length > 0 && (
                                <div className="mt-2">
                                  <span className="text-slate-500">Implies:</span>
                                  <ul className="list-disc list-inside text-slate-400 mt-1">
                                    {meta.relational.implications.map((imp, i) => <li key={i}>{imp}</li>)}
                                  </ul>
                                </div>
                              )}
                            </DimensionPanel>
                          )}

                          {/* Dialectical */}
                          {meta?.dialectical && (meta.dialectical.supports?.length > 0 || meta.dialectical.contradicts?.length > 0 || meta.dialectical.tensions?.length > 0) && (
                            <DimensionPanel
                              title="Dialectics"
                              icon={<ScaleIcon className="w-3 h-3" />}
                              color="border-purple-900/30 text-purple-300"
                            >
                              {meta.dialectical.supports?.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  <span className="text-emerald-500 mr-1">Supports:</span>
                                  {meta.dialectical.supports.map((s, i) => <MiniTag key={i} text={s} color="bg-emerald-900/30 text-emerald-300" />)}
                                </div>
                              )}
                              {meta.dialectical.contradicts?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  <span className="text-red-500 mr-1">Contradicts:</span>
                                  {meta.dialectical.contradicts.map((c, i) => <MiniTag key={i} text={c} color="bg-red-900/30 text-red-300" />)}
                                </div>
                              )}
                              {meta.dialectical.tensions?.length > 0 && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  <span className="text-orange-500 mr-1">Tensions:</span>
                                  {meta.dialectical.tensions.map((t, i) => <MiniTag key={i} text={t} color="bg-orange-900/30 text-orange-300" />)}
                                </div>
                              )}
                              {meta.dialectical.synthesis_potential && (
                                <div className="mt-2 p-2 bg-slate-800/50 rounded text-slate-300">
                                  <span className="text-slate-500">Synthesis:</span> {meta.dialectical.synthesis_potential}
                                </div>
                              )}
                            </DimensionPanel>
                          )}

                          {/* Pragmatic */}
                          {meta?.pragmatic && meta.pragmatic.action_items?.length > 0 && (
                            <DimensionPanel
                              title="Actions"
                              icon={<RocketLaunchIcon className="w-3 h-3" />}
                              color="border-emerald-900/30 text-emerald-300"
                            >
                              <ul className="list-disc list-inside text-slate-300">
                                {meta.pragmatic.action_items.map((a, i) => <li key={i}>{a}</li>)}
                              </ul>
                              {meta.pragmatic.audience?.length > 0 && (
                                <div className="mt-2 flex flex-wrap gap-1">
                                  <span className="text-slate-500">Audience:</span>
                                  {meta.pragmatic.audience.map((aud, i) => <MiniTag key={i} text={aud} />)}
                                </div>
                              )}
                            </DimensionPanel>
                          )}

                          {/* Normative */}
                          {meta?.normative && (meta.normative.values_invoked?.length > 0 || meta.normative.should_statements?.length > 0) && (
                            <DimensionPanel
                              title="Values"
                              icon={<LightBulbIcon className="w-3 h-3" />}
                              color="border-yellow-900/30 text-yellow-300"
                            >
                              {meta.normative.values_invoked?.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {meta.normative.values_invoked.map((v, i) => <MiniTag key={i} text={v} color="bg-yellow-900/30 text-yellow-300" />)}
                                </div>
                              )}
                              {meta.normative.should_statements?.length > 0 && (
                                <div className="mt-2">
                                  <span className="text-slate-500">Should:</span>
                                  <ul className="list-disc list-inside text-slate-300 mt-1">
                                    {meta.normative.should_statements.map((s, i) => <li key={i}>{s}</li>)}
                                  </ul>
                                </div>
                              )}
                            </DimensionPanel>
                          )}
                        </div>
                      )}

                      {/* Tags */}
                      <div className="flex flex-wrap gap-2 items-center mt-3">
                        {meta?.tags?.map(t => (
                          <span key={t} className="text-[10px] text-slate-500 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 flex items-center">
                            <TagIcon className="w-2.5 h-2.5 mr-1 opacity-50" />
                            {t}
                          </span>
                        ))}
                        {addingTagToAtom === atom.id ? (
                          <div className="flex items-center space-x-1">
                            <input
                              autoFocus
                              type="text"
                              value={newTagText}
                              onChange={(e) => setNewTagText(e.target.value)}
                              onKeyDown={(e) => e.key === 'Enter' && submitNewTagForAtom(atom.id)}
                              onBlur={() => submitNewTagForAtom(atom.id)}
                              placeholder="New Tag..."
                              className="w-20 bg-slate-950 text-white text-[10px] px-1 py-0.5 rounded border border-slate-700 focus:outline-none focus:border-indigo-500"
                            />
                          </div>
                        ) : (
                          <button onClick={() => setAddingTagToAtom(atom.id)} className="text-[10px] text-slate-600 hover:text-indigo-400 flex items-center transition-colors"><PlusSmallIcon className="w-3 h-3" /> Tag</button>
                        )}
                      </div>
                    </div>
                  );
                })
              )
            ) : (
              filteredDocs.length === 0 ? (
                <div className="text-center text-slate-500 mt-20 opacity-60">
                  <DocumentDuplicateIcon className="w-12 h-12 mx-auto mb-3" />
                  <p>No documents found.</p>
                </div>
              ) : (
                filteredDocs.map(doc => (
                  <div key={doc.id} className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center group hover:border-slate-600 transition-all">
                    <div className="flex items-center space-x-4 overflow-hidden flex-1">
                      <input
                        type="checkbox"
                        checked={selectedDocIds.has(doc.id)}
                        onChange={() => toggleSelection(doc.id, 'doc')}
                        className="rounded border-slate-700 bg-slate-800 text-emerald-600 focus:ring-emerald-500 w-4 h-4"
                      />
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center space-x-2">
                          <DocumentTextIcon className="w-5 h-5 text-slate-500 shrink-0" />
                          {renamingDocId === doc.id ? (
                            <input
                              autoFocus
                              type="text"
                              value={newDocTitle}
                              onChange={(e) => setNewDocTitle(e.target.value)}
                              onKeyDown={(e) => e.key === 'Enter' && submitRenaming(doc.id)}
                              onBlur={() => submitRenaming(doc.id)}
                              className="bg-slate-950 text-white text-sm font-bold px-2 py-1 rounded border border-indigo-500 focus:outline-none w-full max-w-xs"
                            />
                          ) : (
                            <h4 className="text-slate-200 font-bold text-sm truncate cursor-pointer hover:text-white" onClick={() => startRenaming(doc)}>
                              {doc.name}
                            </h4>
                          )}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                          <p className="text-xs text-slate-500 font-mono">{Math.round(doc.size / 1024)} KB</p>
                          <div className="h-3 w-px bg-slate-800"></div>
                          <div className="flex items-center gap-1">
                            {doc.tags?.map(t => (
                              <span key={t} className="text-[9px] text-slate-400 bg-slate-950 px-1 rounded">{t}</span>
                            ))}
                            {addingTagToDoc === doc.id ? (
                              <input
                                autoFocus
                                type="text"
                                value={newTagText}
                                onChange={(e) => setNewTagText(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && submitNewTagForDoc(doc.id, doc.tags || [])}
                                onBlur={() => submitNewTagForDoc(doc.id, doc.tags || [])}
                                className="w-16 bg-slate-950 text-white text-[9px] px-1 rounded border border-slate-700"
                              />
                            ) : (
                              <button onClick={() => setAddingTagToDoc(doc.id)} className="text-slate-600 hover:text-white"><PlusSmallIcon className="w-3 h-3" /></button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button onClick={() => startRenaming(doc)} title="Rename" className="p-2 text-slate-500 hover:text-white"><PencilSquareIcon className="w-4 h-4" /></button>
                      <button onClick={() => handleExportMd(doc)} title="Download Markdown" className="p-2 text-slate-500 hover:text-white"><ArrowDownTrayIcon className="w-4 h-4" /></button>
                      <button onClick={() => onRemoveDocument(doc.id)} title="Delete Document" className="p-2 text-slate-500 hover:text-red-400"><TrashIcon className="w-4 h-4" /></button>
                    </div>
                  </div>
                ))
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DistillView;