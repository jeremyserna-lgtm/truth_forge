
import React, { useState, useEffect, useCallback } from 'react';
import { CpuChipIcon } from '@heroicons/react/24/outline';
import {
  AppView,
  UploadedDocument,
  KnowledgeAtom,
  ChatMessage,
  DynamicCommand,
  TokenUsage,
  AtomMetadata,
  ModelConfig,
  ContextWindowState,
  ProviderStatus,
  DebateTopic,
  DebateRound,
  StudioArtifact,
  ContextAnalysis
} from './types';
// Components for the linear workflow: INGEST → REFINE → STORE → USE
import DistillView from './components/DistillView';       // Step 1: INGEST
import EnrichmentView from './components/EnrichmentView'; // Step 2: REFINE
import ContextView from './components/ContextView';       // Step 3: STORE
import InteractView from './components/InteractView';     // USE: Interact
import StudioView from './components/StudioView';         // USE: Studio
import ArchitectView from './components/ArchitectView';   // USE: Architect
import TriadView from './components/TriadView';           // USE: Triad (Scout/Maverick/R1)
import TokenMeter from './components/TokenMeter';
import {
  distillToAtoms,
  chatWithContext,
  generateDynamicCommands,
  getDefaultCommands,
  refineAtomSignificance,
  extractTextFromZip,
  regenerateSpecificEmbeddings,
  calculateCosineSimilarity,
  MODELS,
  getModelAnalytics,
  generateDebateTopics,
  runDebateRound,
  suggestTags,
  embedSingleAtom,
  generateChatDocument,
  analyzeContextTrends,
  summarizeContext,
  identifyContextGaps
} from './services/geminiService';
import {
  ALL_MODELS,
  getModelsForProvider,
  estimateTokens,
  calculateContextUsage,
  checkAllProviders,
  getActualContextLimit,
} from './services/llmService';
import { loadAtoms, saveAtoms, mergeAtoms, loadActiveContext, saveActiveContext } from './services/storageService';
import {
  ArrowDownTrayIcon,      // Ingest - bring data in
  AdjustmentsHorizontalIcon, // Refine - adjust metadata
  ArchiveBoxIcon,         // Store - commit to memory
  ChatBubbleLeftRightIcon, // Interact - chat
  MicrophoneIcon,         // Studio - create content
  DocumentDuplicateIcon,  // Architect - generate plans
  Square3Stack3DIcon      // Triad - three models
} from '@heroicons/react/24/solid';

const App: React.FC = () => {
  const [view, setView] = useState<AppView>('ingest');
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  const [atoms, setAtoms] = useState<KnowledgeAtom[]>([]);
  const [activeContextAtoms, setActiveContextAtoms] = useState<KnowledgeAtom[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [dynamicCommands, setDynamicCommands] = useState<DynamicCommand[]>(getDefaultCommands());

  // Context Analytics State
  const [contextAnalysis, setContextAnalysis] = useState<ContextAnalysis>({ lastUpdated: 0 });

  // Debate State
  const [debateTopics, setDebateTopics] = useState<DebateTopic[]>([]);
  const [activeDebateTopic, setActiveDebateTopic] = useState<DebateTopic | null>(null);
  const [debateHistory, setDebateHistory] = useState<DebateRound[]>([]);

  // Provider & Model State
  const [providerStatus, setProviderStatus] = useState<ProviderStatus[]>([]);
  const [contextWindowState, setContextWindowState] = useState<ContextWindowState | null>(null);

  const [activeModel, setActiveModel] = useState<ModelConfig>(MODELS[1]); // Default to Flash (Index 1)
  const [isLoading, setIsLoading] = useState(false);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage>({ used: 0, limit: activeModel.tokenLimit });

  // Load from storage on mount
  useEffect(() => {
    const stored = loadAtoms();
    if (stored.length > 0) {
      setAtoms(stored);
    }
    const context = loadActiveContext();
    if (context.length > 0) {
      setActiveContextAtoms(context);
    } else if (stored.length > 0) {
      // Fallback: automatically set active context to first 20 stored atoms if empty
      setActiveContextAtoms(stored.slice(0, 20));
    }
  }, []);

  // Check provider availability on mount and periodically
  useEffect(() => {
    const checkProviders = async () => {
      const status = await checkAllProviders();
      setProviderStatus(status);

      // If current model's provider is unavailable, switch to an available one
      const currentProvider = activeModel.provider;
      const currentProviderStatus = status.find(s => s.provider === currentProvider);
      if (currentProviderStatus && !currentProviderStatus.available) {
        const availableProvider = status.find(s => s.available);
        if (availableProvider) {
          const fallbackModel = ALL_MODELS.find(m => m.provider === availableProvider.provider);
          if (fallbackModel) {
            setActiveModel(fallbackModel);
          }
        }
      }
    };

    checkProviders();
    // Re-check every 30 seconds
    const interval = setInterval(checkProviders, 30000);
    return () => clearInterval(interval);
  }, [activeModel.provider]);

  // Save to storage whenever atoms change
  useEffect(() => {
    if (atoms.length > 0) {
      saveAtoms(atoms);
    }
  }, [atoms]);

  // Save context persistence
  useEffect(() => {
    saveActiveContext(activeContextAtoms);
  }, [activeContextAtoms]);

  // Update limit when model changes
  useEffect(() => {
    setTokenUsage(prev => ({ ...prev, limit: activeModel.tokenLimit }));
  }, [activeModel]);

  // Update token count logic with detailed context window tracking
  useEffect(() => {
    const updateContextWindow = async () => {
      // Calculate detailed context usage
      const contextState = calculateContextUsage(activeModel.id, {
        documents: documents.map(d => d.content),
        atoms: activeContextAtoms,
        chatHistory: chatHistory.map(m => ({ role: m.role, text: m.text })),
      });

      // For Ollama models, query actual context limit at runtime
      if (activeModel.provider === 'ollama') {
        try {
          const actualLimit = await getActualContextLimit(activeModel.id);
          contextState.tokenLimit = actualLimit;
          contextState.percentUsed = (contextState.tokensUsed / actualLimit) * 100;
        } catch {
          // Keep default limit on error
        }
      }

      setContextWindowState(contextState);
      setTokenUsage({
        used: contextState.tokensUsed,
        limit: contextState.tokenLimit,
      });
    };

    updateContextWindow();
  }, [documents, activeContextAtoms, chatHistory, debateHistory, activeModel]);

  // Background Embedding Processor
  const processPendingEmbeddings = useCallback(async () => {
    // Find all atoms that are pending
    const pendingAtoms = atoms.filter(a => a.embeddingStatus === 'pending');
    if (pendingAtoms.length === 0) return;

    // Process in small batches to keep UI responsive and show incremental progress
    const BATCH_SIZE = 3;
    const batch = pendingAtoms.slice(0, BATCH_SIZE);

    await Promise.all(batch.map(async (atom) => {
      const processed = await embedSingleAtom(atom);
      // Update atom in state with result
      setAtoms(prev => prev.map(a => a.id === processed.id ? processed : a));
      // Update active context if present
      setActiveContextAtoms(prev => prev.map(a => a.id === processed.id ? processed : a));
    }));
  }, [atoms]);

  // Trigger processing whenever atoms change
  useEffect(() => {
    const hasPending = atoms.some(a => a.embeddingStatus === 'pending');
    if (hasPending) {
      processPendingEmbeddings();
    }
  }, [atoms, processPendingEmbeddings]);


  const handleUpload = async (files: FileList | File[]) => {
    // Convert to array if FileList (for consistent handling)
    const fileArray = Array.isArray(files) ? files : Array.from(files);
    console.log(`[App.handleUpload] Received ${fileArray.length} files from input:`,
      fileArray.map(f => f.name));

    const newDocs: UploadedDocument[] = [];
    let tempUsedTokens = tokenUsage.used;
    let acceptedCount = 0;
    let rejectedCount = 0;

    // Process all files in parallel for better performance
    const filePromises = fileArray.map(async (file, i) => {
      console.log(`[App.handleUpload] Processing file ${i + 1}/${files.length}: ${file.name}`);
      let fileContents: { name: string, content: string }[] = [];

      if (file.name.endsWith('.zip')) {
        try {
          const extracted = await extractTextFromZip(file);
          fileContents = extracted;
          console.log(`[App.handleUpload] Extracted ${extracted.length} files from zip: ${file.name}`);
        } catch (e) {
          console.error("Zip extract failed", e);
          return { error: true, name: file.name };
        }
      } else {
        const text = await file.text();
        fileContents = [{ name: file.name, content: text }];
        console.log(`[App.handleUpload] Read text file: ${file.name} (${text.length} chars)`);
      }

      return { error: false, contents: fileContents };
    });

    const results = await Promise.all(filePromises);
    console.log(`[App.handleUpload] Processed ${results.length} files, now adding to state`);

    for (const result of results) {
      if (result.error) {
        alert(`Failed to extract ${result.name}`);
        continue;
      }

      for (const item of result.contents || []) {
        const docTokens = estimateTokens(item.content);
        if (tempUsedTokens + docTokens <= activeModel.tokenLimit) {
          newDocs.push({
            id: `${item.name}-${Date.now()}-${Math.random()}`,
            name: item.name,
            content: item.content,
            size: item.content.length
          });
          tempUsedTokens += docTokens;
          acceptedCount++;
          console.log(`[App.handleUpload] Accepted: ${item.name} (${docTokens} tokens)`);
        } else {
          rejectedCount++;
          console.log(`[App.handleUpload] Rejected (token limit): ${item.name}`);
        }
      }
    }

    console.log(`[App.handleUpload] Final: ${newDocs.length} docs to add, ${acceptedCount} accepted, ${rejectedCount} rejected`);

    if (newDocs.length > 0) {
      setDocuments(prev => {
        console.log(`[App.handleUpload] Previous docs: ${prev.length}, adding ${newDocs.length}`);
        return [...prev, ...newDocs];
      });
    }

    if (rejectedCount > 0) {
      alert(`Context Warning: ${rejectedCount} document(s) were skipped.\n\nAdding them would exceed the ${activeModel.tokenLimit.toLocaleString()} token limit of ${activeModel.label}.\n\nAccepted: ${acceptedCount} docs.`);
    }
  };

  const handleRemoveDocument = (id: string) => {
    setDocuments(prev => prev.filter(d => d.id !== id));
  };

  const handleAddDocument = (doc: UploadedDocument) => {
    setDocuments(prev => [doc, ...prev]);
  };

  const handleUpdateDocument = (id: string, updates: Partial<UploadedDocument>) => {
    setDocuments(prev => prev.map(d => d.id === id ? { ...d, ...updates } : d));
  };

  const handleExport = () => {
    if (atoms.length === 0) return;
    const jsonlContent = atoms.map(atom => JSON.stringify({
      text: atom.content,
      metadata: { ...atom.metadata, source: atom.sourceFile, atom_id: atom.id }
    })).join('\n');
    const blob = new Blob([jsonlContent], { type: 'application/x-jsonlines' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `knowledge-atoms-export-${Date.now()}.jsonl`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleDistill = async () => {
    setIsLoading(true);
    try {
      let newAtoms: KnowledgeAtom[] = [];
      for (const doc of documents) {
        const docAtoms = await distillToAtoms(doc.name, doc.content, activeModel.id);
        newAtoms = [...newAtoms, ...docAtoms];
      }
      const merged = mergeAtoms(atoms, newAtoms);
      setAtoms(merged);
      setActiveContextAtoms(prev => mergeAtoms(prev, newAtoms)); // Auto-add new distillations to active context
    } catch (error) {
      console.error(error);
      alert("Error distilling documents.");
    } finally {
      setIsLoading(false);
    }
  };


  const handleRefine = async () => {
    if (activeContextAtoms.length === 0) return;
    setIsLoading(true);
    try {
      const updates = await refineAtomSignificance(activeContextAtoms, activeModel.id);
      const updateMap = new Map(updates.map(u => [u.id, u.significance]));

      // Update both global and active state
      const updater = (list: KnowledgeAtom[]) => list.map(a => {
        if (updateMap.has(a.id)) {
          return {
            ...a,
            metadata: {
              theme: a.metadata?.theme || 'General',
              tags: a.metadata?.tags || [],
              dimension: a.metadata?.dimension,
              significance: updateMap.get(a.id) as AtomMetadata['significance']
            }
          };
        }
        return a;
      });

      setAtoms(prev => updater(prev));
      setActiveContextAtoms(prev => updater(prev));
    } catch (error) {
      console.error("Refinement failed", error);
      alert("Failed to refine atom significance.");
    } finally {
      setIsLoading(false);
    }
  };

  const _handleNormalizeAtoms = (normalized: KnowledgeAtom[]) => {
    setAtoms(normalized);
    saveAtoms(normalized);
    alert("Normalization complete. Atoms reduced to Core Truths.");
  };

  const handleSuggestTags = async (atom: KnowledgeAtom) => {
    setIsLoading(true);
    try {
      const newTags = await suggestTags(atom.content, activeModel.id);
      if (newTags.length === 0) return;

      const updater = (list: KnowledgeAtom[]) => list.map(a => {
        if (a.id === atom.id) {
          const existingTags = new Set(a.metadata?.tags || []);
          newTags.forEach(t => existingTags.add(t));
          return {
            ...a,
            metadata: {
              ...a.metadata!,
              tags: Array.from(existingTags)
            }
          };
        }
        return a;
      });

      setAtoms(prev => updater(prev));
      setActiveContextAtoms(prev => updater(prev));
    } catch (_e) {
      alert("Failed to suggest tags.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddTag = (atomId: string, tag: string) => {
    const updater = (list: KnowledgeAtom[]) => list.map(a => {
      if (a.id === atomId) {
        const existingTags = new Set(a.metadata?.tags || []);
        existingTags.add(tag);
        return {
          ...a,
          metadata: {
            ...a.metadata!,
            tags: Array.from(existingTags)
          }
        };
      }
      return a;
    });
    setAtoms(prev => updater(prev));
    setActiveContextAtoms(prev => updater(prev));
  };

  // Bulk Manual Tagging
  const handleBulkAddTag = (targetAtoms: KnowledgeAtom[], tag: string) => {
    if (targetAtoms.length === 0 || !tag.trim()) return;
    const targetIds = new Set(targetAtoms.map(a => a.id));

    const updater = (list: KnowledgeAtom[]) => list.map(a => {
      if (targetIds.has(a.id)) {
        const existingTags = new Set(a.metadata?.tags || []);
        existingTags.add(tag.trim());
        return {
          ...a,
          metadata: {
            ...a.metadata!,
            tags: Array.from(existingTags)
          }
        };
      }
      return a;
    });

    setAtoms(prev => updater(prev));
    setActiveContextAtoms(prev => updater(prev));
  };

  // Improved Bulk Auto-tagging logic
  const handleAutoTagAll = async (targetAtoms: KnowledgeAtom[]) => {
    if (targetAtoms.length === 0) return;
    if (!confirm(`This will generate tags for ${targetAtoms.length} atoms. It may take some time. Continue?`)) return;

    setIsLoading(true);

    try {
      // Clone targets to avoid reference issues
      const pending = [...targetAtoms];
      // Process sequentially in chunks to allow React state updates to flush and avoid rate limits
      const CHUNK_SIZE = 4;
      const updates = new Map<string, string[]>();

      for (let i = 0; i < pending.length; i += CHUNK_SIZE) {
        const chunk = pending.slice(i, i + CHUNK_SIZE);

        await Promise.all(chunk.map(async (atom) => {
          try {
            // Use active model ID captured in closure or ref if needed, but here it's fine
            const newTags = await suggestTags(atom.content, activeModel.id);
            if (newTags.length > 0) {
              updates.set(atom.id, newTags);
            }
          } catch (e) { console.error("Single tag fail", e) }
        }));
      }

      // Apply all updates at once
      if (updates.size > 0) {
        const updater = (list: KnowledgeAtom[]) => list.map(a => {
          if (updates.has(a.id)) {
            const existing = new Set(a.metadata?.tags || []);
            updates.get(a.id)!.forEach(t => existing.add(t));
            return {
              ...a,
              metadata: { ...a.metadata!, tags: Array.from(existing) }
            };
          }
          return a;
        });

        setAtoms(prev => updater(prev));
        setActiveContextAtoms(prev => updater(prev));
        alert(`Successfully tagged ${updates.size} atoms.`);
      } else {
        alert("No new tags generated.");
      }

    } catch (e) {
      console.error("Bulk tag error", e);
      alert("Auto-tagging process encountered an error.");
    } finally {
      setIsLoading(false);
    }
  };

  // Studio Workflow Handlers
  const handleArtifactToAtoms = async (artifact: StudioArtifact) => {
    setIsLoading(true);
    try {
      const newAtoms = await distillToAtoms(artifact.title, artifact.content, activeModel.id);
      const merged = mergeAtoms(atoms, newAtoms);
      setAtoms(merged);
      setActiveContextAtoms(prev => mergeAtoms(prev, newAtoms));
      alert(`Successfully distilled ${newAtoms.length} atoms from "${artifact.title}". Switching to Data view.`);
      setView('data');
    } catch (_e) {
      alert("Failed to distill artifact.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleArtifactToDocument = (artifact: StudioArtifact) => {
    const newDoc: UploadedDocument = {
      id: `studio-doc-${Date.now()}`,
      name: `${artifact.title}.md`,
      content: artifact.content,
      size: artifact.content.length
    };
    setDocuments(prev => [newDoc, ...prev]);
    alert(`Saved "${artifact.title}" as a document. Switching to Data view.`);
    setView('data');
  };

  // Batch actions
  const handleDeleteAtoms = (ids: string[]) => {
    const idSet = new Set(ids);
    setAtoms(prev => prev.filter(a => !idSet.has(a.id)));
    setActiveContextAtoms(prev => prev.filter(a => !idSet.has(a.id)));
  };

  const handleBulkAddToContext = (selected: KnowledgeAtom[]) => {
    setActiveContextAtoms(prev => mergeAtoms(prev, selected));
  };

  const handleRegenerateEmbeddings = async (selected: KnowledgeAtom[]) => {
    setIsLoading(true);
    try {
      // Use regenerateSpecificEmbeddings instead of generic generateEmbeddings
      const refreshed = await regenerateSpecificEmbeddings(selected);

      // Force update the atoms map with the new embeddings
      const refreshedMap = new Map(refreshed.map(a => [a.id, a]));
      const updater = (list: KnowledgeAtom[]) => list.map(a => refreshedMap.get(a.id) || a);

      setAtoms(prev => updater(prev));
      setActiveContextAtoms(prev => updater(prev));
      alert(`Successfully generated embeddings for ${refreshed.length} atoms.`);
    } catch (e) {
      alert("Embedding regeneration failed.");
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFindRelated = (targetAtom: KnowledgeAtom) => {
    if (!targetAtom.embedding) {
      alert("This atom has no embedding. Please generate embeddings first.");
      return;
    }

    // Calculate similarity for all atoms
    const sorted = [...atoms].map(a => {
      if (!a.embedding) return { ...a, _sim: -1 };
      return { ...a, _sim: calculateCosineSimilarity(targetAtom.embedding!, a.embedding) };
    }).sort((a, b) => b._sim - a._sim);

    // Remove the temp _sim property (or keep it if you want to display score, but keeping it simple for now)
    const cleanSorted = sorted.map(a => {
      const { _sim, ...rest } = a;
      return rest as KnowledgeAtom;
    });

    setAtoms(cleanSorted);
  };

  const handleRetryEmbedding = async (atom: KnowledgeAtom) => {
    // Set to pending immediately
    const pendingAtom = { ...atom, embeddingStatus: 'pending' as const };
    setAtoms(prev => prev.map(a => a.id === atom.id ? pendingAtom : a));

    // Attempt embed
    const processed = await embedSingleAtom(pendingAtom);

    // Update result
    setAtoms(prev => prev.map(a => a.id === processed.id ? processed : a));
    setActiveContextAtoms(prev => prev.map(a => a.id === processed.id ? processed : a));
  };

  // --- CONTEXT ANALYTICS HANDLERS ---
  const handleAnalyzeTrends = async () => {
    if (activeContextAtoms.length === 0) return;
    setIsLoading(true);
    try {
      const report = await analyzeContextTrends(activeContextAtoms, activeModel.id);
      setContextAnalysis(prev => ({ ...prev, trends: report, lastUpdated: Date.now() }));
    } catch (_e) { alert("Analysis failed"); } finally { setIsLoading(false); }
  };

  const handleSummarizeContext = async () => {
    if (activeContextAtoms.length === 0) return;
    setIsLoading(true);
    try {
      const report = await summarizeContext(activeContextAtoms, activeModel.id);
      setContextAnalysis(prev => ({ ...prev, summary: report, lastUpdated: Date.now() }));
    } catch (_e) { alert("Analysis failed"); } finally { setIsLoading(false); }
  };

  const handleIdentifyGaps = async () => {
    if (activeContextAtoms.length === 0) return;
    setIsLoading(true);
    try {
      const report = await identifyContextGaps(activeContextAtoms, activeModel.id);
      setContextAnalysis(prev => ({ ...prev, gaps: report, lastUpdated: Date.now() }));
    } catch (_e) { alert("Analysis failed"); } finally { setIsLoading(false); }
  };

  // --- INTERACT LOGIC ---

  const handleSendMessage = async (text: string) => {
    const newUserMsg: ChatMessage = { role: 'user', text };
    setChatHistory(prev => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const atomContext = activeContextAtoms.map(a => {
        const meta = a.metadata ? `[${a.metadata.significance} | ${a.metadata.theme}]` : '';
        return `- ${meta} ${a.content} (Source: ${a.sourceFile})`;
      }).join("\n");
      const docContext = documents.map(d => `Document: ${d.name}\n${d.content}`).join("\n\n");
      const contextToUse = activeContextAtoms.length > 0 ? atomContext : docContext;

      if (!contextToUse) {
        throw new Error("No context available. Upload docs or add atoms to context.");
      }

      const response = await chatWithContext(
        chatHistory.map(m => ({ role: m.role, text: m.text })),
        contextToUse,
        text,
        activeModel.id
      );

      const newModelMsg: ChatMessage = { role: 'model', text: response.text };
      setChatHistory(prev => [...prev, newModelMsg]);

      generateDynamicCommands(text, response.text, contextToUse, activeModel.id)
        .then(cmds => setDynamicCommands(cmds))
        .catch(console.error);

    } catch (error: any) {
      setChatHistory(prev => [...prev, { role: 'model', text: `Error: ${error.message}`, isError: true }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatExport = async (mode: 'document' | 'atom', theme: string) => {
    if (chatHistory.length === 0) return;
    setIsLoading(true);
    try {
      if (mode === 'document') {
        const docContent = await generateChatDocument(chatHistory, theme, activeModel.id);
        const blob = new Blob([docContent], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `${theme.replace(/\s+/g, '_')}_Chat_Export.md`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        const transcript = chatHistory.map(m => `${m.role.toUpperCase()}: ${m.text}`).join('\n');
        const newAtoms = await distillToAtoms(`Chat Export: ${theme}`, transcript, activeModel.id);

        if (newAtoms.length > 0) {
          const merged = mergeAtoms(atoms, newAtoms);
          setAtoms(merged);
          setActiveContextAtoms(prev => mergeAtoms(prev, newAtoms));
          alert(`${newAtoms.length} Knowledge Atoms distilled from chat and added to library.`);
        }
      }
    } catch (e) {
      console.error("Export failed", e);
      alert("Export failed.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateDebateTopics = async () => {
    if ((activeContextAtoms.length === 0 && documents.length === 0) || isLoading) return;
    setIsLoading(true);
    try {
      const context = activeContextAtoms.length > 0
        ? JSON.stringify(activeContextAtoms.map(({ content, metadata }) => ({
          content,
          theme: metadata?.theme,
          significance: metadata?.significance
        })))
        : documents.map(d => d.content).join("\n");

      const topics = await generateDebateTopics(context, activeModel.id);
      setDebateTopics(topics);
    } catch (e) {
      console.error("Debate generation failed", e);
      alert("Failed to generate topics");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDebateRound = async () => {
    if (!activeDebateTopic || isLoading) return;
    setIsLoading(true);
    try {
      const context = activeContextAtoms.length > 0
        ? JSON.stringify(activeContextAtoms.map(({ content, metadata }) => ({
          content,
          theme: metadata?.theme,
          significance: metadata?.significance
        })))
        : documents.map(d => d.content).join("\n");

      const round = await runDebateRound(activeDebateTopic, debateHistory, context, activeModel.id);
      setDebateHistory(prev => [...prev, round]);
    } catch (e) {
      console.error("Debate round failed", e);
      alert("Failed to generate debate round");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen bg-slate-950 text-slate-100 font-sans flex flex-col overflow-hidden">

      {/* Top Navigation Bar */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur flex items-center justify-between px-6 shrink-0 z-50">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
            <span className="font-bold text-white text-lg">K</span>
          </div>
          <span className="font-bold text-lg tracking-wide hidden lg:block">Knowledge<span className="font-light text-slate-400">Atomizer</span></span>
        </div>

        {/* Model Selector - Grouped by Provider */}
        <div className="flex items-center space-x-2 bg-slate-900 rounded-lg p-1 border border-slate-800">
          <CpuChipIcon className={`w-4 h-4 ml-2 ${activeModel.provider === 'ollama' ? 'text-emerald-400' : 'text-indigo-400'}`} />
          <select
            value={activeModel.id}
            onChange={(e) => {
              const model = ALL_MODELS.find(m => m.id === e.target.value);
              if (model) setActiveModel(model);
            }}
            className="bg-transparent text-sm text-slate-300 font-medium py-1 pr-2 focus:outline-none cursor-pointer"
          >
            {/* Gemini Models */}
            <optgroup label="☁️ Gemini (Cloud)">
              {getModelsForProvider('gemini').map(model => (
                <option key={model.id} value={model.id} className="bg-slate-900">
                  {model.label}
                </option>
              ))}
            </optgroup>
            {/* Ollama Models - with availability indicator */}
            <optgroup label={`🦙 Ollama (Local) ${providerStatus.find(p => p.provider === 'ollama')?.available ? '✓' : '✗'}`}>
              {getModelsForProvider('ollama').map(model => {
                const ollamaStatus = providerStatus.find(p => p.provider === 'ollama');
                // Match llama4-scout -> llama4:scout or llama3.2 -> llama3.2:latest
                const modelBase = model.id.toLowerCase().replace('-', ':').split(':')[0];
                const isAvailable = ollamaStatus?.available && ollamaStatus?.models.some(m => {
                  const ollamaBase = m.toLowerCase().split(':')[0];
                  return ollamaBase === modelBase || m.toLowerCase().includes(modelBase);
                });
                return (
                  <option
                    key={model.id}
                    value={model.id}
                    className="bg-slate-900"
                    disabled={!ollamaStatus?.available}
                  >
                    {model.label} {isAvailable ? '' : '(not pulled)'}
                  </option>
                );
              })}
            </optgroup>
          </select>
        </div>

        {/* View Switcher - Linear Workflow: INGEST → REFINE → STORE → USE */}
        <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-800 overflow-x-auto scrollbar-none">
          {/* Step 1: INGEST - Upload docs, distill to atoms */}
          <button
            onClick={() => setView('ingest')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'ingest' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <ArrowDownTrayIcon className="w-4 h-4" />
            <span className="hidden md:inline">1. Ingest</span>
          </button>

          {/* Step 2: REFINE - Work with atom metadata, tags, lenses */}
          <button
            onClick={() => setView('refine')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'refine' ? 'bg-pink-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <AdjustmentsHorizontalIcon className="w-4 h-4" />
            <span className="hidden md:inline">2. Refine</span>
          </button>

          {/* Step 3: STORE - Commit atoms to context + long-term memory */}
          <button
            onClick={() => setView('store')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'store' ? 'bg-yellow-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <ArchiveBoxIcon className="w-4 h-4" />
            <span className="hidden md:inline">3. Store</span>
          </button>

          {/* Divider */}
          <div className="w-px bg-slate-700 mx-1"></div>

          {/* USE PHASE - Interact with stored atoms */}
          <button
            onClick={() => setView('interact')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'interact' ? 'bg-primary-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <ChatBubbleLeftRightIcon className="w-4 h-4" />
            <span className="hidden md:inline">Interact</span>
          </button>
          <button
            onClick={() => setView('studio')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'studio' ? 'bg-rose-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <MicrophoneIcon className="w-4 h-4" />
            <span className="hidden md:inline">Studio</span>
          </button>
          <button
            onClick={() => setView('architect')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'architect' ? 'bg-violet-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <DocumentDuplicateIcon className="w-4 h-4" />
            <span className="hidden md:inline">Architect</span>
          </button>
          <button
            onClick={() => setView('triad')}
            className={`flex items-center space-x-2 px-3 md:px-4 py-1.5 rounded-md text-sm font-medium transition-all whitespace-nowrap ${view === 'triad' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}`}
          >
            <Square3Stack3DIcon className="w-4 h-4" />
            <span className="hidden md:inline">Triad</span>
          </button>
        </div>

        {/* Stats - Context Window Meter */}
        <div className="flex items-center w-32 md:w-48">
          <TokenMeter
            current={tokenUsage.used}
            max={tokenUsage.limit}
            contextState={contextWindowState}
            modelLabel={activeModel.label}
            provider={activeModel.provider}
          />
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative">
        {/* Step 1: INGEST - Upload documents and distill to atoms */}
        {view === 'ingest' && (
          <DistillView
            documents={documents}
            atoms={atoms}
            activeAtoms={activeContextAtoms}
            isProcessing={isLoading}
            onUpload={handleUpload}
            onRemoveDocument={handleRemoveDocument}
            onDistill={handleDistill}
            onExport={handleExport}
            onRefine={handleRefine}
            onDeleteAtoms={handleDeleteAtoms}
            onBulkAddToContext={handleBulkAddToContext}
            onRegenerateEmbeddings={handleRegenerateEmbeddings}
            onFindRelated={handleFindRelated}
            onSuggestTags={handleSuggestTags}
            onAutoTagAll={handleAutoTagAll}
            canDistill={documents.length > 0}
            onAddDocument={handleAddDocument}
            onAddTag={handleAddTag}
            onRetryEmbedding={handleRetryEmbedding}
            onUpdateDocument={handleUpdateDocument}
            onBulkAddTag={handleBulkAddTag}
          />
        )}
        {/* Step 3: STORE - Commit atoms to context + long-term memory */}
        {view === 'store' && (
          <ContextView
            storedAtoms={atoms}
            activeAtoms={activeContextAtoms}
            onAddToContext={(a) => setActiveContextAtoms(prev => [...prev, a])}
            onRemoveFromContext={(id) => setActiveContextAtoms(prev => prev.filter(x => x.id !== id))}
            onRegenerateEmbeddings={handleRegenerateEmbeddings}
            onAnalyzeTrends={handleAnalyzeTrends}
            onSummarizeContext={handleSummarizeContext}
            onIdentifyGaps={handleIdentifyGaps}
            contextAnalysis={contextAnalysis}
            isProcessing={isLoading}
          />
        )}
        {/* Step 2: REFINE - Work with atom metadata, lenses, tags */}
        {view === 'refine' && (
          <EnrichmentView
            modelConfig={activeModel}
            isLoading={isLoading}
            onSetLoading={setIsLoading}
          />
        )}
        {/* USE PHASE: Studio - Create content from atoms */}
        {view === 'studio' && (
          <StudioView
            atoms={activeContextAtoms.length > 0 ? activeContextAtoms : atoms}
            isLoading={isLoading}
            setLoading={setIsLoading}
            onArtifactToAtoms={handleArtifactToAtoms}
            onArtifactToDocument={handleArtifactToDocument}
          />
        )}
        {/* USE PHASE: Interact - Chat with your atoms */}
        {view === 'interact' && (
          <InteractView
            messages={chatHistory}
            onSendMessage={(text) => {
              handleSendMessage(text);
            }}
            onExportChat={handleChatExport}
            isLoading={isLoading}
            dynamicCommands={dynamicCommands}
            staticCommands={getModelAnalytics(activeModel.id)}
            debateTopics={debateTopics}
            activeDebateTopic={activeDebateTopic}
            debateHistory={debateHistory}
            onSelectDebateTopic={(t) => { setActiveDebateTopic(t); setDebateHistory([]); }}
            onGenerateDebateTopics={handleGenerateDebateTopics}
            onNextDebateRound={handleDebateRound}
            hasContext={documents.length > 0 || activeContextAtoms.length > 0}
            activeModel={activeModel}
          />
        )}
        {/* USE PHASE: Architect - Generate implementation plans */}
        {view === 'architect' && (
          <ArchitectView
            atoms={activeContextAtoms.length > 0 ? activeContextAtoms : atoms}
            documents={documents}
            activeModel={activeModel}
            isLoading={isLoading}
            setLoading={setIsLoading}
          />
        )}
        {/* USE PHASE: Triad - Scout/Maverick/R1 tensor generation */}
        {view === 'triad' && (
          <TriadView
            atoms={atoms}
            activeModel={activeModel}
            isLoading={isLoading}
            setLoading={setIsLoading}
            onAtomGenerated={(atom) => {
              const newAtoms = mergeAtoms(atoms, [atom]);
              setAtoms(newAtoms);
              setActiveContextAtoms(prev => mergeAtoms(prev, [atom]));
            }}
            documents={documents}
            onUploadDocuments={handleUpload}
            onRemoveDocument={handleRemoveDocument}
          />
        )}
      </main>

    </div>
  );
};

export default App;