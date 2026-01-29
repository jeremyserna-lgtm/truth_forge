
import React, { useRef, useState, useMemo } from 'react';
import { KnowledgeAtom, UploadedDocument } from '../types';
import { synthesizeDocuments, synthesizeAtomsToDocument } from '../services/geminiService';
import { 
    DocumentTextIcon, ArrowUpTrayIcon, BeakerIcon, ArrowDownTrayIcon, 
    TagIcon, AdjustmentsHorizontalIcon, ArchiveBoxIcon, EyeIcon, 
    MagnifyingGlassIcon, TrashIcon, PlusCircleIcon, CheckCircleIcon,
    ArrowPathIcon, LinkIcon, SparklesIcon, XMarkIcon, Squares2X2Icon,
    DocumentDuplicateIcon, BoltIcon, CubeTransparentIcon, PlusSmallIcon,
    FolderIcon, StopIcon, ExclamationCircleIcon, PencilSquareIcon, CheckIcon,
    Square3Stack3DIcon, ArrowsPointingOutIcon
} from '@heroicons/react/24/outline';

interface DistillViewProps {
  documents: UploadedDocument[];
  atoms: KnowledgeAtom[];
  activeAtoms: KnowledgeAtom[];
  isProcessing: boolean;
  onUpload: (files: FileList) => void;
  onRemoveDocument: (id: string) => void;
  onDistill: () => void;
  onExport: () => void;
  onRefine: () => void;
  onExpand: (config: { lens: string, structure: string, altitude: string }) => void;
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

const LENSES = ["Adam", "Economic", "Ethical", "Systemic", "Historical", "Futurist", "Cynical", "Scientific", "Psychological"];
const STRUCTURES = ["Atomic List", "Hierarchy", "Network Graph", "Narrative Flow", "Dialectic", "Rhizome"];
const ALTITUDES = ["Satellite (Abstract)", "Bird's Eye (Context)", "Street Level (Concrete)", "Subterranean (Root)", "Tectonic (Foundational)"];

const DistillView: React.FC<DistillViewProps> = ({
  documents,
  atoms,
  activeAtoms,
  isProcessing,
  onUpload,
  onRemoveDocument,
  onDistill,
  onExport,
  onRefine,
  onExpand,
  onDeleteAtoms,
  onBulkAddToContext,
  onRegenerateEmbeddings,
  onFindRelated,
  onSuggestTags,
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
  const [includeFrontMatter, setIncludeFrontMatter] = useState(false);
  
  // Dimensions State
  const [selectedLens, setSelectedLens] = useState(LENSES[0]);
  const [selectedStructure, setSelectedStructure] = useState(STRUCTURES[0]);
  const [selectedAltitude, setSelectedAltitude] = useState(ALTITUDES[2]);

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
  const [isBulkTagging, setIsBulkTagging] = useState(false);

  const activeAtomIds = useMemo(() => new Set(activeAtoms.map(a => a.id)), [activeAtoms]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
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
             // Use lens for synthesis
             const doc = await synthesizeAtomsToDocument(selected, selectedLens, 'gemini-3-pro-preview');
             onAddDocument(doc);
             alert("Synthesis complete! A new document has been created from your atoms.");
             setSelectedAtomIds(new Set());
          } catch(e) {
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
          const synthDoc = await synthesizeDocuments(selectedDocs, selectedLens, 'gemini-3-pro-preview', includeFrontMatter);
          onAddDocument(synthDoc);
          setSelectedDocIds(new Set());
          alert("Synthesis Complete! New document added.");
      } catch (e) {
          alert("Synthesis failed.");
      }
  };

  const handleExpand = () => {
      onExpand({
          lens: selectedLens,
          structure: selectedStructure,
          altitude: selectedAltitude
      });
  };

  const submitBulkTag = () => {
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
            title="Click to upload documents for analysis"
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
              multiple 
              accept=".txt,.md,.json,.csv,.js,.ts,.zip"
            />
            <ArrowUpTrayIcon className="w-8 h-8 text-slate-500 mb-2" />
            <h3 className="text-slate-200 font-bold text-sm">Upload Documents</h3>
            <p className="text-slate-500 text-xs mt-1">.zip, .txt, .md, .json</p>
          </div>

          <button
            onClick={onDistill}
            disabled={!canDistill || isProcessing}
            title="Break down all uploaded documents into atomic truths (single sentences)"
            className={`
              w-full py-3 rounded-xl font-bold text-sm shadow-lg flex items-center justify-center space-x-2
              transition-all transform hover:scale-[1.02] active:scale-[0.98]
              ${canDistill && !isProcessing
                ? 'bg-gradient-to-r from-primary-600 to-indigo-600 text-white hover:shadow-primary-500/25'
                : 'bg-slate-800 text-slate-500 cursor-not-allowed'}
            `}
          >
             {isProcessing ? <ArrowPathIcon className="w-5 h-5 animate-spin"/> : <BeakerIcon className="w-5 h-5" />}
             <span>{isProcessing ? 'Distilling...' : 'Distill to Atoms'}</span>
          </button>
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

               {/* 3-Dimensional Analysis Matrix */}
               <div className="flex flex-col md:flex-row gap-2 pt-2 border-t border-slate-800/50">
                   
                   {/* D1: Lens */}
                   <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700">
                        <EyeIcon className="w-4 h-4 text-slate-400 mx-2" />
                        <select 
                            value={selectedLens} 
                            onChange={(e) => setSelectedLens(e.target.value)}
                            className="bg-transparent text-white text-xs font-bold focus:outline-none w-24 md:w-28 cursor-pointer"
                            disabled={isProcessing}
                        >
                            {LENSES.map(d => <option key={d} value={d} className="bg-slate-900">{d}</option>)}
                        </select>
                   </div>

                   {/* D2: Structure */}
                   <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700">
                        <ArrowsPointingOutIcon className="w-4 h-4 text-slate-400 mx-2" />
                        <select 
                            value={selectedStructure} 
                            onChange={(e) => setSelectedStructure(e.target.value)}
                            className="bg-transparent text-white text-xs font-bold focus:outline-none w-24 md:w-28 cursor-pointer"
                            disabled={isProcessing}
                        >
                            {STRUCTURES.map(d => <option key={d} value={d} className="bg-slate-900">{d}</option>)}
                        </select>
                   </div>

                   {/* D3: Altitude */}
                   <div className="flex items-center bg-slate-800 rounded-lg p-1 border border-slate-700">
                        <Square3Stack3DIcon className="w-4 h-4 text-slate-400 mx-2" />
                        <select 
                            value={selectedAltitude} 
                            onChange={(e) => setSelectedAltitude(e.target.value)}
                            className="bg-transparent text-white text-xs font-bold focus:outline-none w-28 md:w-32 cursor-pointer"
                            disabled={isProcessing}
                        >
                            {ALTITUDES.map(d => <option key={d} value={d} className="bg-slate-900">{d}</option>)}
                        </select>
                   </div>

                   {/* Expand Action */}
                   {viewMode === 'atoms' && (
                       <button
                          onClick={handleExpand}
                          disabled={isProcessing || atoms.length === 0}
                          title="Generate new atoms using the selected 3-dimensional framework"
                          className="px-4 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold shadow-lg disabled:opacity-50 whitespace-nowrap flex items-center ml-auto md:ml-2"
                       >
                         {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin"/> : null}
                         <span>Expand View</span>
                       </button>
                   )}
                   
                   {/* Synthesize Action (Docs) */}
                   {viewMode === 'documents' && (
                       <button
                          onClick={handleSynthesizeDocs}
                          disabled={isProcessing || selectedDocIds.size < 2}
                          title="Merge selected documents into a new unified document using the selected Lens"
                          className="px-4 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-bold shadow-lg disabled:opacity-50 whitespace-nowrap flex items-center ml-auto"
                       >
                         {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin"/> : <BoltIcon className="w-3 h-3 mr-1" />}
                         Synthesize
                       </button>
                   )}
               </div>

               {/* Bulk Actions Row */}
               {viewMode === 'atoms' && atoms.length > 0 && (
                   <div className="flex items-center gap-2 pt-2 border-t border-slate-800/50 overflow-x-auto scrollbar-none">
                        <button onClick={onRefine} disabled={isProcessing} className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-purple-300 border border-purple-900/50 rounded-lg text-[10px] font-bold uppercase tracking-wider flex items-center whitespace-nowrap disabled:opacity-50">
                            {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin"/> : null}
                            Refine Significance
                        </button>
                        <button 
                            onClick={() => onAutoTagAll(atoms)} 
                            disabled={isProcessing} 
                            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-900/50 rounded-lg text-[10px] font-bold uppercase tracking-wider flex items-center whitespace-nowrap disabled:opacity-50"
                        >
                            {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin"/> : null}
                            Auto-Tag All
                        </button>

                        {selectedAtomIds.size > 0 && (
                            <button 
                                onClick={() => handleBulkAction('synthesize')} 
                                disabled={isProcessing} 
                                className="px-3 py-1 bg-emerald-900/40 hover:bg-emerald-800 text-emerald-400 border border-emerald-900/50 rounded-lg text-[10px] font-bold uppercase tracking-wider flex items-center whitespace-nowrap disabled:opacity-50"
                            >
                                {isProcessing ? <ArrowPathIcon className="w-3 h-3 mr-1 animate-spin"/> : <DocumentTextIcon className="w-3 h-3 mr-1"/>}
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
                                <button onClick={() => handleBulkAction('context')} className="p-1 hover:bg-slate-800 rounded text-yellow-400" title="Add to Context"><PlusCircleIcon className="w-4 h-4"/></button>
                                <button onClick={() => handleBulkAction('embed')} className="p-1 hover:bg-slate-800 rounded text-cyan-400" title="Force Embed"><BoltIcon className="w-4 h-4"/></button>
                                <button onClick={() => handleBulkAction('delete')} className="p-1 hover:bg-slate-800 rounded text-red-400" title="Delete Selected"><TrashIcon className="w-4 h-4"/></button>
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
                       filteredAtoms.map(atom => (
                           <div key={atom.id} className={`bg-slate-900 border ${activeAtomIds.has(atom.id) ? 'border-yellow-500/30 shadow-[0_0_10px_rgba(234,179,8,0.1)]' : 'border-slate-800'} rounded-xl p-4 transition-all hover:border-slate-600 group`}>
                               <div className="flex justify-between items-start mb-2">
                                   <div className="flex items-center space-x-2">
                                        <input 
                                            type="checkbox" 
                                            checked={selectedAtomIds.has(atom.id)} 
                                            onChange={() => toggleSelection(atom.id, 'atom')}
                                            className="rounded border-slate-700 bg-slate-800 text-indigo-600 focus:ring-indigo-500 w-3.5 h-3.5"
                                        />
                                        <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded ${atom.metadata?.significance === 'Fundamental' ? 'bg-rose-900/30 text-rose-400 border border-rose-900/50' : 'bg-slate-800 text-slate-400 border border-slate-700'}`}>
                                            {atom.metadata?.significance}
                                        </span>
                                        <span className="text-[9px] text-slate-500 uppercase font-mono">{atom.metadata?.theme}</span>
                                        {atom.embeddingStatus === 'failed' && <span className="text-red-500 text-[9px]" title="Embedding failed"><ExclamationCircleIcon className="w-3 h-3"/></span>}
                                        {atom.embeddingStatus === 'pending' && <span className="text-slate-600 text-[9px]" title="Embedding..."><ArrowPathIcon className="w-3 h-3 animate-spin"/></span>}
                                   </div>
                                   <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                       {onRetryEmbedding && atom.embeddingStatus === 'failed' && (
                                           <button onClick={() => onRetryEmbedding(atom)} title="Retry Embedding" className="p-1 text-slate-400 hover:text-cyan-400"><ArrowPathIcon className="w-4 h-4"/></button>
                                       )}
                                       <button onClick={() => onFindRelated(atom)} title="Find related atoms" className="p-1 text-slate-400 hover:text-cyan-400"><Squares2X2Icon className="w-4 h-4"/></button>
                                       <button onClick={() => onBulkAddToContext([atom])} title="Add to context" className="p-1 text-slate-400 hover:text-yellow-400"><PlusCircleIcon className="w-4 h-4"/></button>
                                   </div>
                               </div>
                               <p className="text-slate-300 text-sm mb-3 leading-relaxed font-light">{atom.content}</p>
                               <div className="flex flex-wrap gap-2 items-center">
                                   {atom.metadata?.tags?.map(t => (
                                       <span key={t} className="text-[10px] text-slate-500 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800 flex items-center">
                                           <TagIcon className="w-2.5 h-2.5 mr-1 opacity-50"/>
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
                                       <button onClick={() => setAddingTagToAtom(atom.id)} className="text-[10px] text-slate-600 hover:text-indigo-400 flex items-center transition-colors"><PlusSmallIcon className="w-3 h-3"/> Tag</button>
                                   )}
                               </div>
                           </div>
                       ))
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
                                                   <button onClick={() => setAddingTagToDoc(doc.id)} className="text-slate-600 hover:text-white"><PlusSmallIcon className="w-3 h-3"/></button>
                                                )}
                                           </div>
                                       </div>
                                   </div>
                               </div>
                               <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                   <button onClick={() => startRenaming(doc)} title="Rename" className="p-2 text-slate-500 hover:text-white"><PencilSquareIcon className="w-4 h-4"/></button>
                                   <button onClick={() => handleExportMd(doc)} title="Download Markdown" className="p-2 text-slate-500 hover:text-white"><ArrowDownTrayIcon className="w-4 h-4"/></button>
                                   <button onClick={() => onRemoveDocument(doc.id)} title="Delete Document" className="p-2 text-slate-500 hover:text-red-400"><TrashIcon className="w-4 h-4"/></button>
                               </div>
                           </div>
                       ))
                   )}
               )}
           </div>
        </div>
      </div>
    </div>
  );
};

export default DistillView;