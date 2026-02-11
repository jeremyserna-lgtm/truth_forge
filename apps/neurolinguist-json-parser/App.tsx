import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  FileJson,
  Upload,
  Play,
  Database,
  Activity,
  Layers,
  ChevronRight,
  ChevronDown,
  Cpu,
  ShieldCheck,
  FileText,
  Trash2,
  Download,
  Search,
  Sparkles,
  BarChart2,
  Maximize2,
  Minimize2,
  Info,
  Smile,
  Meh,
  Frown,
  Tag,
  X,
  User,
  Bot,
  Clock,
  Cloud,
  Wifi,
  WifiOff,
  Settings,
  RefreshCw,
  Moon,
  Sun,
  Zap,
  HardDrive,
  Plus,
  GitCompare,
  FileCode,
  Keyboard
} from 'lucide-react';
// @ts-ignore
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts';
import { OllamaService, ProcessingProgress, GpuInfo, ModelParameters, DEFAULT_MODEL_PARAMS, DEFAULT_ENTITY_TYPES } from './services/ollamaService';
import { embeddingCache } from './services/embeddingCache';
import {
  exportToSpineFormat,
  exportToSpineJSONL,
  exportEntitiesAsCSV,
  exportToNativeSpineJSONL,
  exportRelationshipsJSONL
} from './services/spineExport';
import { compareConversations, generateDiffReport, ConversationDiffResult } from './services/conversationDiff';
import { detectFormat, parseChat, convertToNeurolinguistFormat, getFormatDisplayName, ChatFormat } from './services/chatFormatParser';
import { validateConversation, formatValidationResult, ValidationResult } from './services/exportValidation';
import { exportToBigQuery, validateForBigQuery, checkBigQueryApiStatus, BigQueryExportResult } from './services/bigqueryExport';
import {
  calculateContextMetrics,
  estimateTokens,
  formatTokens,
  getUsageColor,
  ContextMetrics,
  MODEL_CONFIGS
} from './services/contextCalculator';
import { Conversation, Turn, Message, DenormalizedRow, ProcessingStatus, TopicSegment, Span, Sentence, DetailedProgress } from './types';
import { DEMO_JSON } from './constants';

const generateId = () => crypto.randomUUID();
const LS_KEY = 'neuroLinguist_data';
const LS_MODEL_KEY = 'neuroLinguist_model';
const LS_DARK_MODE = 'neuroLinguist_darkMode';
const LS_SAVED_CONVERSATIONS = 'neuroLinguist_savedConversations';

// --- Similarity Math ---
const dotProduct = (a: number[], b: number[]) => a.reduce((sum, val, i) => sum + val * b[i], 0);
const magnitude = (v: number[]) => Math.sqrt(v.reduce((sum, val) => sum + val * val, 0));
const cosineSimilarity = (a: number[] | undefined, b: number[] | undefined) => {
  if (!a || !b || a.length !== b.length) return 0;
  const magA = magnitude(a);
  const magB = magnitude(b);
  if (magA === 0 || magB === 0) return 0;
  return dotProduct(a, b) / (magA * magB);
};

// Format bytes to human readable
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

export default function App() {
  const [jsonInput, setJsonInput] = useState<string>(DEMO_JSON);
  const [status, setStatus] = useState<ProcessingStatus>('idle');
  const [progress, setProgress] = useState<number>(0);
  const [log, setLog] = useState<string[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [activeTab, setActiveTab] = useState<'hierarchy' | 'table' | 'json' | 'compare'>('hierarchy');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Dark mode
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem(LS_DARK_MODE);
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  // Ollama connection state
  const [ollamaConnected, setOllamaConnected] = useState<boolean>(false);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>(() => {
    return localStorage.getItem(LS_MODEL_KEY) || 'llama3.2';
  });
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [detailedProgress, setDetailedProgress] = useState<DetailedProgress | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [gpuInfo, setGpuInfo] = useState<GpuInfo | null>(null);

  // Advanced settings
  const [nerModel, setNerModel] = useState<string>('');
  const [embeddingModel, setEmbeddingModel] = useState<string>('nomic-embed-text');
  const [modelParams, setModelParams] = useState<ModelParameters>(DEFAULT_MODEL_PARAMS);
  const [customEntityTypes, setCustomEntityTypes] = useState<string[]>([]);
  const [newEntityType, setNewEntityType] = useState<string>('');
  const [useCache, setUseCache] = useState<boolean>(true);
  const [ollamaHost, setOllamaHost] = useState<string>(() => {
    return localStorage.getItem('neurolinguist_ollama_host') || 'http://localhost:11434';
  });

  // Cache stats
  const [cacheStats, setCacheStats] = useState<{ totalEntries: number; totalSize: number } | null>(null);

  // Context window calculator
  const [contextMetrics, setContextMetrics] = useState<ContextMetrics | null>(null);
  const [showContextCalculator, setShowContextCalculator] = useState<boolean>(true);

  // Comparison
  const [savedConversations, setSavedConversations] = useState<Conversation[]>([]);
  const [compareConv, setCompareConv] = useState<Conversation | null>(null);
  const [diffResult, setDiffResult] = useState<ConversationDiffResult | null>(null);

  // Selection & Highlight State
  const [highlightedId, setHighlightedId] = useState<string | null>(null);
  const [selectedSpan, setSelectedSpan] = useState<{ span: Span, sentence: Sentence, message: Message, topic: TopicSegment } | null>(null);

  // Keyboard shortcut help
  const [showShortcuts, setShowShortcuts] = useState<boolean>(false);
  const [showExportPreview, setShowExportPreview] = useState<boolean>(false);
  const [exportPreviewData, setExportPreviewData] = useState<{
    format: string;
    content: string;
    filename: string;
    stats: { entities: number; relationships: number; levels: Record<number, number> };
    validation?: ValidationResult;
  } | null>(null);
  const [exportLoading, setExportLoading] = useState<boolean>(false);
  const [batchFiles, setBatchFiles] = useState<{ name: string; content: string; format: ChatFormat; status: 'pending' | 'processing' | 'done' | 'error' }[]>([]);
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [processedConversations, setProcessedConversations] = useState<Conversation[]>([]);
  const [bigQueryExporting, setBigQueryExporting] = useState<boolean>(false);
  const [bigQueryProgress, setBigQueryProgress] = useState<{
    stage: string;
    message: string;
    percentage: number;
  } | null>(null);
  const [bigQueryResult, setBigQueryResult] = useState<BigQueryExportResult | null>(null);
  const [showBigQueryModal, setShowBigQueryModal] = useState<boolean>(false);

  // Ollama service instance
  const ollamaService = useMemo(() => {
    const service = new OllamaService({
      model: selectedModel,
      nerModel: nerModel || undefined,
      embeddingModel,
      useCache,
      modelParams,
      customEntityTypes,
      baseUrl: ollamaHost
    });
    return service;
  }, [selectedModel, nerModel, embeddingModel, useCache, modelParams, customEntityTypes, ollamaHost]);

  // Apply dark mode
  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem(LS_DARK_MODE, JSON.stringify(darkMode));
  }, [darkMode]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+Enter to process
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !isProcessing && ollamaConnected) {
        e.preventDefault();
        handleProcess();
      }
      // Escape to cancel
      if (e.key === 'Escape' && isProcessing) {
        e.preventDefault();
        handleCancel();
      }
      // Ctrl+D for dark mode toggle
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        setDarkMode(d => !d);
      }
      // Ctrl+, for settings
      if ((e.ctrlKey || e.metaKey) && e.key === ',') {
        e.preventDefault();
        setShowSettings(s => !s);
      }
      // ? for shortcuts help
      if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
        const target = e.target as HTMLElement;
        if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA') {
          e.preventDefault();
          setShowShortcuts(s => !s);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isProcessing, ollamaConnected]);

  // Check Ollama connection on mount and periodically
  useEffect(() => {
    checkOllamaConnection();
    loadSavedConversations();
    loadCacheStats();

    const intervalId = setInterval(() => {
      if (!isProcessing) {
        checkOllamaConnection();
      }
    }, 30000);

    return () => clearInterval(intervalId);
  }, [isProcessing]);

  // Save selected model to localStorage
  useEffect(() => {
    localStorage.setItem(LS_MODEL_KEY, selectedModel);
    if (ollamaService) {
      ollamaService.setModel(selectedModel);
    }
  }, [selectedModel]);

  // Calculate context metrics when model or input changes
  useEffect(() => {
    const updateContextMetrics = async () => {
      const currentTokens = estimateTokens(jsonInput);
      const metrics = await calculateContextMetrics(selectedModel, currentTokens);
      setContextMetrics(metrics);
    };
    updateContextMetrics();
  }, [selectedModel, jsonInput]);

  const checkOllamaConnection = async () => {
    try {
      const service = new OllamaService({ baseUrl: ollamaHost });
      const { connected, models, gpu } = await service.checkConnection();
      setOllamaConnected(connected);
      setAvailableModels(models);
      setGpuInfo(gpu || null);
      if (connected) {
        addLog(`Connected to Ollama. ${models.length} models available.`);
      } else {
        addLog("Warning: Ollama not connected. Start Ollama to enable processing.");
      }
    } catch (e) {
      setOllamaConnected(false);
      addLog("Error checking Ollama connection.");
    }
  };

  const loadSavedConversations = () => {
    try {
      const saved = localStorage.getItem(LS_SAVED_CONVERSATIONS);
      if (saved) {
        setSavedConversations(JSON.parse(saved));
      }
    } catch (e) {
      console.error('Failed to load saved conversations');
    }
  };

  const loadCacheStats = async () => {
    try {
      const stats = await embeddingCache.getStats();
      setCacheStats(stats);
    } catch (e) {
      console.error('Failed to load cache stats');
    }
  };

  const handleCancel = () => {
    if (ollamaService) {
      ollamaService.cancel();
      setStatus('cancelling');
      addLog("Cancelling processing...");
    }
  };

  // Load from LocalStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(LS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && parsed.id) {
          setConversation(parsed);
          addLog("Loaded saved conversation from LocalStorage.");
        }
      }
    } catch (e) {
      console.error("Failed to load from local storage", e);
    }
  }, []);

  // Save to LocalStorage
  useEffect(() => {
    if (conversation) {
      try {
        localStorage.setItem(LS_KEY, JSON.stringify(conversation));
      } catch (e) {
        console.error("Failed to save to local storage (likely quota exceeded)", e);
      }
    }
  }, [conversation]);

  const addLog = (msg: string) => setLog(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const handleClearData = () => {
    if (confirm("Are you sure you want to clear all processed data?")) {
      setConversation(null);
      localStorage.removeItem(LS_KEY);
      setLog([]);
      setStatus('idle');
      setProgress(0);
      setHighlightedId(null);
      setSelectedSpan(null);
      setDiffResult(null);
    }
  };

  const handleClearCache = async () => {
    if (confirm("Clear all cached embeddings?")) {
      await embeddingCache.clear();
      await loadCacheStats();
      addLog("Embedding cache cleared.");
    }
  };

  const validateJSONInput = (content: string): { valid: boolean; error?: string; parsed?: any } => {
    try {
      const parsed = JSON.parse(content);
      let messagesArray = [];
      if (Array.isArray(parsed)) messagesArray = parsed;
      else if (parsed && Array.isArray(parsed.messages)) messagesArray = parsed.messages;
      else return { valid: false, error: "JSON must be an array of messages or an object with a 'messages' array." };

      if (messagesArray.length === 0) return { valid: false, error: "Messages array is empty." };

      const firstItem = messagesArray[0];
      if (!firstItem || typeof firstItem !== 'object' || !('role' in firstItem) || !('content' in firstItem)) {
        return { valid: false, error: "Messages must have 'role' and 'content' fields." };
      }
      return { valid: true, parsed: parsed };
    } catch (e) {
      return { valid: false, error: "Invalid JSON syntax." };
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;

      // Try to detect and convert from other formats
      const format = detectFormat(content, file.name);
      let processedContent = content;
      let formatNote = '';

      if (format !== 'unknown' && format !== 'claude') {
        try {
          const parsed = parseChat(content, file.name);
          if (parsed.length > 0) {
            // Convert first conversation to neurolinguist format
            processedContent = convertToNeurolinguistFormat(parsed[0]);
            formatNote = ` (converted from ${getFormatDisplayName(format)})`;
            addLog(`Detected ${getFormatDisplayName(format)} format. Converting...`);
          }
        } catch (convErr) {
          addLog(`Format conversion failed, trying direct import: ${convErr instanceof Error ? convErr.message : 'Unknown error'}`);
        }
      }

      const validation = validateJSONInput(processedContent);
      if (validation.valid) {
        setJsonInput(processedContent);
        addLog(`File uploaded: ${file.name}${formatNote} (${(file.size / 1024).toFixed(2)} KB). Structure valid.`);
        setStatus('idle');
      } else {
        addLog(`Error uploading ${file.name}: ${validation.error}`);
        setStatus('error');
        alert(`Validation Failed: ${validation.error}\n\nSupported formats: Claude, ChatGPT, Gemini JSON exports`);
      }
    };
    reader.onerror = () => {
      addLog(`Error reading file: ${file.name}`);
      setStatus('error');
    };
    reader.readAsText(file);
    event.target.value = '';
  };

  const handleBatchFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const newBatchFiles: typeof batchFiles = [];

    const readFile = (file: File): Promise<{ name: string; content: string; format: ChatFormat }> => {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          const format = detectFormat(content, file.name);
          resolve({ name: file.name, content, format });
        };
        reader.onerror = () => reject(new Error(`Failed to read ${file.name}`));
        reader.readAsText(file);
      });
    };

    Promise.all(Array.from(files).map(readFile))
      .then(results => {
        const batch = results.map(r => ({
          ...r,
          status: 'pending' as const,
        }));
        setBatchFiles(batch);
        setBatchMode(true);
        addLog(`Batch mode: ${batch.length} files loaded. Ready for processing.`);
      })
      .catch(err => {
        addLog(`Batch upload error: ${err.message}`);
      });

    event.target.value = '';
  };

  const handleBatchProcess = async () => {
    if (!ollamaConnected || batchFiles.length === 0) return;

    const results: Conversation[] = [];

    for (let i = 0; i < batchFiles.length; i++) {
      const file = batchFiles[i];
      setBatchFiles(prev => prev.map((f, idx) => idx === i ? { ...f, status: 'processing' } : f));
      addLog(`Processing ${i + 1}/${batchFiles.length}: ${file.name}...`);

      try {
        // Convert if needed
        let content = file.content;
        if (file.format !== 'unknown' && file.format !== 'claude') {
          const parsed = parseChat(file.content, file.name);
          if (parsed.length > 0) {
            content = convertToNeurolinguistFormat(parsed[0]);
          }
        }

        const validation = validateJSONInput(content);
        if (!validation.valid) {
          throw new Error(`Invalid JSON: ${validation.error}`);
        }

        setJsonInput(content);

        // Process the conversation
        const inputData = JSON.parse(content);
        const processedConv = await ollamaService.processConversation(inputData, (progress) => {
          setDetailedProgress(progress);
        });

        results.push(processedConv);
        setBatchFiles(prev => prev.map((f, idx) => idx === i ? { ...f, status: 'done' } : f));
        addLog(`Completed: ${file.name} (${processedConv.topicCount} topics)`);
      } catch (err) {
        setBatchFiles(prev => prev.map((f, idx) => idx === i ? { ...f, status: 'error' } : f));
        addLog(`Error processing ${file.name}: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
    }

    setProcessedConversations(results);
    if (results.length > 0) {
      setConversation(results[results.length - 1]); // Show last processed
    }
    addLog(`Batch complete: ${results.length}/${batchFiles.length} files processed successfully.`);
  };

  const handleBatchExport = async () => {
    if (processedConversations.length === 0) {
      addLog('No processed conversations to export.');
      return;
    }

    try {
      addLog(`Exporting ${processedConversations.length} conversations...`);
      const allEntities: string[] = [];

      for (const conv of processedConversations) {
        const content = await exportToNativeSpineJSONL(conv, {
          sourceFile: conv.sourceFile || 'batch_import',
          includeWords: true,
        });
        allEntities.push(content);
      }

      const combined = allEntities.join('\n');
      downloadContent(combined, `batch_export_${processedConversations.length}_conversations.jsonl`, 'application/x-ndjson');
      addLog(`Batch export complete: ${combined.split('\n').length} total entities.`);
    } catch (err) {
      addLog(`Batch export error: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  const clearBatchMode = () => {
    setBatchMode(false);
    setBatchFiles([]);
    setProcessedConversations([]);
    addLog('Batch mode cleared.');
  };

  const handleRegenerateSummary = async (topicId: string, turns: Turn[]) => {
    if (!ollamaConnected || !conversation) return;
    addLog(`Regenerating summary for topic ${topicId.substring(0, 8)}...`);
    try {
      const newSummary = await ollamaService.refineTopicSummary(turns);
      const updatedTopics = conversation.topics.map(t => {
        if (t.id === topicId) return { ...t, summary: newSummary };
        return t;
      });
      setConversation({ ...conversation, topics: updatedTopics });
      addLog(`Summary updated for topic ${topicId.substring(0, 8)}.`);
    } catch (e) {
      addLog(`Error regenerating summary: ${e}`);
    }
  };

  const handleProcess = async () => {
    if (!ollamaConnected) {
      alert("Ollama is not connected. Please start Ollama and refresh.");
      return;
    }
    const validation = validateJSONInput(jsonInput);
    if (!validation.valid) {
      addLog(`Cannot process: ${validation.error}`);
      setStatus('error');
      return;
    }

    setIsProcessing(true);
    setDetailedProgress(null);

    try {
      const parsedInput = validation.parsed;
      let messages: any[] = Array.isArray(parsedInput) ? parsedInput : parsedInput.messages;

      setStatus('analyzing_structure');
      setProgress(5);
      addLog(`Starting process with model: ${selectedModel}${nerModel ? ` (NER: ${nerModel})` : ''}`);
      addLog("Validated JSON structure.");

      const conversationId = generateId();
      const turns: Turn[] = [];
      let currentTurnMessages: Message[] = [];

      const l5Messages: Message[] = messages.map(m => ({
        id: generateId(),
        role: m.role || 'unknown',
        content: typeof m.content === 'string' ? m.content : JSON.stringify(m.content),
        sentences: [],
        parentId: '',
        sentenceCount: 0
      }));

      l5Messages.forEach((msg) => {
        if (msg.role === 'user' && currentTurnMessages.length > 0) {
          const turnId = generateId();
          currentTurnMessages.forEach(m => m.parentId = turnId);
          turns.push({
            id: turnId,
            messages: currentTurnMessages,
            parentId: '',
            messageCount: currentTurnMessages.length
          });
          currentTurnMessages = [];
        }
        currentTurnMessages.push(msg);
      });
      if (currentTurnMessages.length > 0) {
        const turnId = generateId();
        currentTurnMessages.forEach(m => m.parentId = turnId);
        turns.push({
          id: turnId,
          messages: currentTurnMessages,
          parentId: '',
          messageCount: currentTurnMessages.length
        });
      }

      addLog(`Identified ${turns.length} turns (Level 6).`);
      setProgress(10);

      const onTopicProgress = (progress: ProcessingProgress) => {
        setDetailedProgress(progress);
        setProgress(10 + Math.floor(progress.percentage * 0.1));
      };

      addLog(`Asking ${selectedModel} to segment turns into Topics (Level 7)...`);
      let topics = await ollamaService.segmentIntoTopics(turns, conversationId, onTopicProgress);
      addLog(`Created ${topics.length} Topic Segments.`);
      setProgress(20);

      setStatus('calculating_embeddings');
      addLog("Calculating topic embeddings for similarity analysis...");

      const onEmbeddingProgress = (progress: ProcessingProgress) => {
        setDetailedProgress(progress);
        setProgress(20 + Math.floor(progress.percentage * 0.1));
      };

      topics = await ollamaService.generateTopicEmbeddings(topics, onEmbeddingProgress);
      const embeddingsGenerated = topics.some(t => t.embedding && t.embedding.length > 0);
      const cacheStats = ollamaService.getCacheStats();
      addLog(embeddingsGenerated
        ? `Embeddings generated. Cache: ${cacheStats.hits} hits, ${cacheStats.misses} misses.`
        : "Embeddings skipped (nomic-embed-text not available).");
      setProgress(30);

      setStatus('parsing_sentences');
      const allMessages: Array<{ id: string; content: string; ref: Message }> = [];
      for (const topic of topics) {
        for (const turn of topic.turns) {
          for (const message of turn.messages) {
            allMessages.push({ id: message.id, content: message.content, ref: message });
          }
        }
      }

      addLog(`Processing ${allMessages.length} messages in parallel batches...`);

      const onMessageProgress = (current: number, total: number, label: string) => {
        setDetailedProgress({
          stage: 'messages',
          currentItem: current,
          totalItems: total,
          currentLabel: label,
          percentage: Math.round((current / total) * 100)
        });
        const currentProgress = 30 + Math.floor((current / total) * 70);
        setProgress(currentProgress);
        if (current % 5 === 0 || current === total) {
          addLog(`Parsed ${current}/${total} messages...`);
        }
      };

      const parsedResults = await ollamaService.parseMessagesBatch(
        allMessages.map(m => ({ id: m.id, content: m.content })),
        2,
        onMessageProgress
      );

      for (const msg of allMessages) {
        const sentences = parsedResults.get(msg.id) || [];
        msg.ref.sentences = sentences;
        msg.ref.sentenceCount = sentences.length;
      }

      const finalConversation: Conversation = {
        id: conversationId,
        title: "Processed Chat Log",
        topics: topics,
        topicCount: topics.length
      };

      setConversation(finalConversation);
      setStatus('complete');
      setDetailedProgress({
        stage: 'complete',
        currentItem: allMessages.length,
        totalItems: allMessages.length,
        currentLabel: 'Processing complete!',
        percentage: 100
      });
      addLog("Processing Complete. Hierarchy constructed successfully.");
      setActiveTab('hierarchy');
      await loadCacheStats();

    } catch (error: any) {
      console.error(error);
      if (error.message === 'Operation cancelled') {
        setStatus('idle');
        addLog("Processing cancelled by user.");
      } else {
        setStatus('error');
        addLog(`ERROR: ${error.message}`);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSaveConversation = () => {
    if (!conversation) return;
    const updated = [...savedConversations.filter(c => c.id !== conversation.id), conversation];
    setSavedConversations(updated);
    localStorage.setItem(LS_SAVED_CONVERSATIONS, JSON.stringify(updated));
    addLog(`Conversation saved for comparison.`);
  };

  const handleCompare = (conv: Conversation) => {
    if (!conversation) return;
    setCompareConv(conv);
    const diff = compareConversations(conv, conversation);
    setDiffResult(diff);
    setActiveTab('compare');
    addLog(`Comparing with saved conversation ${conv.id.substring(0, 8)}.`);
  };

  const handleExportSpine = (format: 'json' | 'jsonl' | 'csv') => {
    if (!conversation) return;

    let content: string;
    let filename: string;
    let mimeType: string;

    if (format === 'json') {
      content = JSON.stringify(exportToSpineFormat(conversation), null, 2);
      filename = `spine_export_${conversation.id.substring(0, 8)}.json`;
      mimeType = 'application/json';
    } else if (format === 'jsonl') {
      content = exportToSpineJSONL(conversation);
      filename = `spine_export_${conversation.id.substring(0, 8)}.jsonl`;
      mimeType = 'application/x-ndjson';
    } else {
      content = exportEntitiesAsCSV(conversation);
      filename = `spine_entities_${conversation.id.substring(0, 8)}.csv`;
      mimeType = 'text/csv';
    }

    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    addLog(`Exported to ${format.toUpperCase()} format.`);
  };

  const handleExportNativeSpine = async (includeRelationships: boolean = false, skipPreview: boolean = false) => {
    if (!conversation) return;

    try {
      setExportLoading(true);
      addLog('Validating conversation before export...');

      // Validate first
      const validation = validateConversation(conversation);
      if (!validation.valid) {
        addLog(`Validation failed: ${validation.stats.errors} errors found`);
        validation.issues.filter(i => i.level === 'error').forEach(issue => {
          addLog(`  ✗ ${issue.message}`);
        });
      } else {
        addLog(`Validation passed (${validation.stats.warnings} warnings)`);
      }

      addLog('Generating native spine export (BigQuery compatible)...');

      // Export entities
      const entitiesContent = await exportToNativeSpineJSONL(conversation, {
        sourceFile: conversation.sourceFile || 'imported',
        includeWords: true,
      });
      const entitiesFilename = `native_spine_${conversation.id.substring(0, 8)}.jsonl`;

      // Calculate stats
      const lines = entitiesContent.trim().split('\n');
      const levelCounts: Record<number, number> = {};
      lines.forEach(line => {
        try {
          const entity = JSON.parse(line);
          levelCounts[entity.level] = (levelCounts[entity.level] || 0) + 1;
        } catch { /* skip malformed */ }
      });

      // Get relationship count
      let relationshipCount = 0;
      if (includeRelationships) {
        const relContent = await exportRelationshipsJSONL(conversation);
        relationshipCount = relContent.trim().split('\n').length;
      }

      if (skipPreview) {
        // Direct download (skip if validation failed)
        if (!validation.valid) {
          addLog('Export cancelled due to validation errors. Fix issues first.');
          setExportLoading(false);
          return;
        }
        downloadContent(entitiesContent, entitiesFilename, 'application/x-ndjson');
        if (includeRelationships) {
          const relContent = await exportRelationshipsJSONL(conversation);
          downloadContent(relContent, `native_spine_relationships_${conversation.id.substring(0, 8)}.jsonl`, 'application/x-ndjson');
        }
        addLog(`Native spine export complete. Ready for BigQuery batch load.`);
      } else {
        // Show preview with validation
        setExportPreviewData({
          format: includeRelationships ? 'Native Spine (Entities + Relationships)' : 'Native Spine (Entities)',
          content: entitiesContent,
          filename: entitiesFilename,
          stats: {
            entities: lines.length,
            relationships: relationshipCount,
            levels: levelCounts,
          },
          validation,
        });
        setShowExportPreview(true);
      }
      setExportLoading(false);
    } catch (error) {
      setExportLoading(false);
      addLog(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  const downloadContent = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleConfirmExport = () => {
    if (!exportPreviewData) return;
    downloadContent(exportPreviewData.content, exportPreviewData.filename, 'application/x-ndjson');
    addLog(`Exported ${exportPreviewData.stats.entities} entities to ${exportPreviewData.filename}`);
    setShowExportPreview(false);
    setExportPreviewData(null);
  };

  const handleBigQueryExport = async () => {
    if (!conversation) return;

    setBigQueryExporting(true);
    setBigQueryResult(null);
    setShowBigQueryModal(true);

    try {
      addLog('Starting BigQuery export...');

      const result = await exportToBigQuery(conversation, {
        sourceFile: conversation.sourceFile || 'neurolinguist_parser',
        includeWords: true,
        onProgress: (progress) => {
          setBigQueryProgress(progress);
          addLog(`[BigQuery] ${progress.message}`);
        },
      });

      setBigQueryResult(result);

      if (result.success) {
        addLog(`BigQuery export complete: ${result.rows_written?.toLocaleString()} rows written to ${result.table}`);
        if (result.backup_table) {
          addLog(`Backup created: ${result.backup_table} (${result.backup_rows?.toLocaleString()} rows)`);
        }
      } else {
        addLog(`BigQuery export failed: ${result.error}`);
        if (result.validation_errors && result.validation_errors.length > 0) {
          result.validation_errors.slice(0, 5).forEach(err => {
            addLog(`  - ${err}`);
          });
        }
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setBigQueryResult({
        success: false,
        error: errorMessage,
      });
      addLog(`BigQuery export error: ${errorMessage}`);
    } finally {
      setBigQueryExporting(false);
      setBigQueryProgress(null);
    }
  };

  const addCustomEntity = () => {
    if (newEntityType.trim() && !customEntityTypes.includes(newEntityType.toUpperCase())) {
      setCustomEntityTypes([...customEntityTypes, newEntityType.toUpperCase()]);
      setNewEntityType('');
    }
  };

  const denormalizedData = useMemo(() => {
    if (!conversation) return [];
    const rows: DenormalizedRow[] = [];

    conversation.topics.forEach(topic => {
      topic.turns.forEach(turn => {
        turn.messages.forEach(msg => {
          msg.sentences.forEach(sentence => {
            const commonProps = {
              l8_id: conversation.id,
              l7_id: topic.id,
              l6_id: turn.id,
              l5_id: msg.id,
              l4_id: sentence.id,
              topic_count: conversation.topicCount,
              turn_count: topic.turnCount,
              message_count: turn.messageCount,
              sentence_count: msg.sentenceCount,
              word_count: sentence.wordCount,
              span_count: sentence.spanCount,
            };

            sentence.words.forEach(word => {
              rows.push({
                ...commonProps,
                l2_id: word.id,
                l3_id: undefined,
                level: 2,
                type: 'word',
                content: word.text,
                meta: 'Word'
              });
            });
            sentence.spans.forEach(span => {
              rows.push({
                ...commonProps,
                l3_id: span.id,
                l2_id: undefined,
                level: 3,
                type: 'span',
                content: span.text,
                meta: span.label
              });
            });
          });
        });
      });
    });
    return rows;
  }, [conversation]);

  const filteredData = useMemo(() => {
    if (!searchTerm) return denormalizedData;
    const lowerSearch = searchTerm.toLowerCase();
    return denormalizedData.filter(row =>
      row.content.toLowerCase().includes(lowerSearch) ||
      row.meta.toLowerCase().includes(lowerSearch) ||
      row.l8_id.includes(lowerSearch) ||
      row.l7_id.includes(lowerSearch)
    );
  }, [denormalizedData, searchTerm]);

  const handleExportCSV = () => {
    if (filteredData.length === 0) return;
    const headers = [
      "L8_ID", "L7_ID", "L6_ID", "L5_ID", "L4_ID", "Leaf_ID", "Level", "Type", "Content", "Meta",
      "Topic_Count", "Turn_Count", "Message_Count", "Sentence_Count", "Word_Count", "Span_Count"
    ];
    const csvContent = [
      headers.join(","),
      ...filteredData.map(row => [
        row.l8_id, row.l7_id, row.l6_id, row.l5_id, row.l4_id, row.l3_id || row.l2_id, row.level, row.type,
        `"${row.content.replace(/"/g, '""')}"`,
        `"${row.meta}"`,
        row.topic_count, row.turn_count, row.message_count, row.sentence_count, row.word_count, row.span_count
      ].join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `neurolinguist_export_${new Date().toISOString()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleSpanClick = (span: Span, sentence: Sentence, message: Message, topic: TopicSegment) => {
    setSelectedSpan({ span, sentence, message, topic });
    setHighlightedId(span.id);
  };

  // Theme classes
  const bgMain = darkMode ? 'bg-slate-900' : 'bg-slate-50';
  const bgCard = darkMode ? 'bg-slate-800' : 'bg-white';
  const bgCardAlt = darkMode ? 'bg-slate-700' : 'bg-slate-50';
  const textPrimary = darkMode ? 'text-slate-100' : 'text-slate-900';
  const textSecondary = darkMode ? 'text-slate-400' : 'text-slate-600';
  const borderColor = darkMode ? 'border-slate-700' : 'border-slate-200';

  return (
    <div className={`min-h-screen ${bgMain} flex flex-col font-sans relative ${textPrimary}`}>
      {/* Header */}
      <header className={`${darkMode ? 'bg-slate-950' : 'bg-slate-900'} text-white p-6 shadow-md border-b-4 border-emerald-500`}>
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500 rounded-lg">
              <Database className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">NeuroLinguist Parser</h1>
              <p className="text-slate-400 text-xs uppercase tracking-wider font-semibold">
                L8-L2 Hierarchical LLM Analysis • Local Mode
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm">
            {/* Context Window Calculator */}
            {contextMetrics && (
              <div
                className="flex items-center gap-2 px-3 py-1 bg-slate-800 border border-slate-600 rounded-full cursor-pointer hover:bg-slate-700 transition-colors"
                onClick={() => setShowContextCalculator(s => !s)}
                title={`Context: ${formatTokens(contextMetrics.currentTokens)} / ${formatTokens(contextMetrics.effectiveMaxTokens)} tokens`}
              >
                <Activity className="w-4 h-4 text-emerald-400" />
                <div className="flex items-center gap-1">
                  <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full transition-all duration-300"
                      style={{
                        width: `${Math.min(contextMetrics.usagePercent, 100)}%`,
                        backgroundColor: getUsageColor(contextMetrics.usagePercent)
                      }}
                    />
                  </div>
                  <span className="text-xs text-slate-300">
                    {formatTokens(contextMetrics.remainingTokens)} left
                  </span>
                </div>
              </div>
            )}
            {/* GPU Info */}
            {gpuInfo?.available && (
              <div className="flex items-center gap-2 px-3 py-1 bg-purple-900/50 border border-purple-700 text-purple-300 rounded-full">
                <HardDrive className="w-4 h-4" />
                <span>{formatBytes(gpuInfo.vramUsed || 0)} VRAM</span>
              </div>
            )}
            {/* Connection Status */}
            <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${ollamaConnected
              ? 'bg-emerald-900/50 border-emerald-700 text-emerald-300'
              : 'bg-red-900/50 border-red-700 text-red-300'
              }`}>
              {ollamaConnected ? <Wifi className="w-4 h-4" /> : <WifiOff className="w-4 h-4" />}
              <span>{ollamaConnected ? 'Connected' : 'Offline'}</span>
              <button onClick={checkOllamaConnection} className="ml-1 hover:text-white" title="Refresh connection">
                <RefreshCw className="w-3 h-3" />
              </button>
            </div>
            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(d => !d)}
              className="p-2 bg-slate-800 rounded-full border border-slate-700 hover:bg-slate-700 transition-colors"
              title="Toggle dark mode (Ctrl+D)"
            >
              {darkMode ? <Sun className="w-4 h-4 text-yellow-400" /> : <Moon className="w-4 h-4 text-slate-400" />}
            </button>
            {/* Keyboard Shortcuts */}
            <button
              onClick={() => setShowShortcuts(s => !s)}
              className="p-2 bg-slate-800 rounded-full border border-slate-700 hover:bg-slate-700 transition-colors"
              title="Keyboard shortcuts (?)"
            >
              <Keyboard className="w-4 h-4 text-slate-400" />
            </button>
            {/* Settings */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center gap-2 px-3 py-1 bg-slate-800 rounded-full border border-slate-700 hover:bg-slate-700 transition-colors"
              title="Settings (Ctrl+,)"
            >
              <Settings className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300">{selectedModel}</span>
            </button>
          </div>
        </div>
      </header>

      {/* Context Calculator Panel */}
      {showContextCalculator && contextMetrics && (
        <div className={`${darkMode ? 'bg-slate-800/95' : 'bg-slate-100'} border-b ${borderColor} px-6 py-4`}>
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-3">
              <h3 className={`${textPrimary} font-semibold flex items-center gap-2`}>
                <Activity className="w-5 h-5 text-emerald-500" />
                Context Window Calculator
              </h3>
              <button
                onClick={() => setShowContextCalculator(false)}
                className={`${textSecondary} hover:${textPrimary} p-1`}
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Max Available */}
              <div className={`${bgCard} p-4 rounded-lg border ${borderColor}`}>
                <div className={`${textSecondary} text-xs uppercase tracking-wider mb-1`}>Max Available</div>
                <div className={`${textPrimary} text-2xl font-bold`}>{formatTokens(contextMetrics.effectiveMaxTokens)}</div>
                <div className={`${textSecondary} text-xs`}>tokens</div>
              </div>

              {/* Currently Used */}
              <div className={`${bgCard} p-4 rounded-lg border ${borderColor}`}>
                <div className={`${textSecondary} text-xs uppercase tracking-wider mb-1`}>Current Input</div>
                <div className={`${textPrimary} text-2xl font-bold`}>{formatTokens(contextMetrics.currentTokens)}</div>
                <div className={`${textSecondary} text-xs`}>tokens ({contextMetrics.usagePercent.toFixed(1)}%)</div>
              </div>

              {/* Remaining */}
              <div className={`${bgCard} p-4 rounded-lg border ${borderColor}`}>
                <div className={`${textSecondary} text-xs uppercase tracking-wider mb-1`}>Remaining</div>
                <div className="text-2xl font-bold" style={{ color: getUsageColor(contextMetrics.usagePercent) }}>
                  {formatTokens(contextMetrics.remainingTokens)}
                </div>
                <div className={`${textSecondary} text-xs`}>tokens available</div>
              </div>

              {/* Memory */}
              <div className={`${bgCard} p-4 rounded-lg border ${borderColor}`}>
                <div className={`${textSecondary} text-xs uppercase tracking-wider mb-1`}>Memory</div>
                <div className={`${textPrimary} text-2xl font-bold`}>{contextMetrics.totalRamGB} GB</div>
                <div className={`${textSecondary} text-xs`}>{contextMetrics.modelSizeGB}GB model loaded</div>
              </div>
            </div>

            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between text-xs mb-1">
                <span className={textSecondary}>Context Usage</span>
                <span className={textSecondary}>{formatTokens(contextMetrics.currentTokens)} / {formatTokens(contextMetrics.effectiveMaxTokens)}</span>
              </div>
              <div className={`w-full h-3 ${darkMode ? 'bg-slate-700' : 'bg-slate-300'} rounded-full overflow-hidden`}>
                <div
                  className="h-full transition-all duration-500 rounded-full"
                  style={{
                    width: `${Math.min(contextMetrics.usagePercent, 100)}%`,
                    backgroundColor: getUsageColor(contextMetrics.usagePercent)
                  }}
                />
              </div>
              <div className="flex justify-between text-xs mt-1">
                <span className={textSecondary}>0</span>
                <span className={textSecondary}>Model: {contextMetrics.modelName}</span>
                <span className={textSecondary}>{formatTokens(contextMetrics.effectiveMaxTokens)}</span>
              </div>
            </div>

            {/* Info */}
            <div className={`mt-3 text-xs ${textSecondary} flex items-center gap-2`}>
              <Info className="w-3 h-3" />
              <span>
                KV cache: {(contextMetrics.kvCachePerTokenBytes / 1024).toFixed(0)}KB/token •
                Hardware limit: {formatTokens(contextMetrics.maxContextTokens)} •
                Model limit: {formatTokens(contextMetrics.theoreticalMaxTokens)}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4" onClick={() => setShowShortcuts(false)}>
          <div className={`${bgCard} rounded-xl shadow-2xl max-w-md w-full overflow-hidden ${borderColor} border`} onClick={e => e.stopPropagation()}>
            <div className="bg-emerald-500 p-4 flex justify-between items-center text-white">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Keyboard className="w-5 h-5" /> Keyboard Shortcuts
              </h3>
              <button onClick={() => setShowShortcuts(false)} className="hover:bg-emerald-600 p-1 rounded"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-3">
              {[
                ['Ctrl+Enter', 'Start processing'],
                ['Escape', 'Cancel processing'],
                ['Ctrl+D', 'Toggle dark mode'],
                ['Ctrl+,', 'Open settings'],
                ['?', 'Show shortcuts']
              ].map(([key, desc]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className={textSecondary}>{desc}</span>
                  <kbd className={`px-2 py-1 ${bgCardAlt} rounded text-xs font-mono ${borderColor} border`}>{key}</kbd>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Export Preview Modal */}
      {showExportPreview && exportPreviewData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4" onClick={() => setShowExportPreview(false)}>
          <div className={`${bgCard} rounded-xl shadow-2xl max-w-2xl w-full overflow-hidden ${borderColor} border`} onClick={e => e.stopPropagation()}>
            <div className="bg-emerald-500 p-4 flex justify-between items-center text-white">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Database className="w-5 h-5" /> Export Preview
              </h3>
              <button onClick={() => setShowExportPreview(false)} className="hover:bg-emerald-600 p-1 rounded"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className={`${bgCardAlt} p-4 rounded-lg`}>
                  <div className={`text-sm ${textSecondary}`}>Format</div>
                  <div className={`text-lg font-semibold ${textPrimary}`}>{exportPreviewData.format}</div>
                </div>
                <div className={`${bgCardAlt} p-4 rounded-lg`}>
                  <div className={`text-sm ${textSecondary}`}>Total Entities</div>
                  <div className={`text-lg font-semibold ${textPrimary}`}>{exportPreviewData.stats.entities.toLocaleString()}</div>
                </div>
              </div>

              <div className={`${bgCardAlt} p-4 rounded-lg`}>
                <div className={`text-sm ${textSecondary} mb-2`}>Entities by Level</div>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(exportPreviewData.stats.levels)
                    .sort(([a], [b]) => Number(b) - Number(a))
                    .map(([level, count]) => (
                      <div key={level} className={`flex justify-between ${textPrimary} text-sm`}>
                        <span>L{level}:</span>
                        <span className="font-mono">{count.toLocaleString()}</span>
                      </div>
                    ))}
                </div>
              </div>

              <div className={`${bgCardAlt} p-4 rounded-lg`}>
                <div className={`text-sm ${textSecondary} mb-2`}>Sample Output (first 5 lines)</div>
                <pre className={`text-xs font-mono ${textSecondary} overflow-x-auto max-h-32 overflow-y-auto`}>
                  {exportPreviewData.content.split('\n').slice(0, 5).map((line, i) => {
                    try {
                      return JSON.stringify(JSON.parse(line), null, 2).substring(0, 200) + '...\n';
                    } catch {
                      return line.substring(0, 200) + '...\n';
                    }
                  }).join('\n')}
                </pre>
              </div>

              <div className={`text-sm ${textSecondary}`}>
                File: <span className="font-mono">{exportPreviewData.filename}</span>
              </div>

              {/* Validation Results */}
              {exportPreviewData.validation && (
                <div className={`p-4 rounded-lg ${exportPreviewData.validation.valid ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'}`}>
                  <div className={`text-sm font-semibold mb-2 ${exportPreviewData.validation.valid ? 'text-emerald-700 dark:text-emerald-400' : 'text-red-700 dark:text-red-400'}`}>
                    {exportPreviewData.validation.valid ? '✓ Validation Passed' : '✗ Validation Failed'}
                    {exportPreviewData.validation.stats.warnings > 0 && ` (${exportPreviewData.validation.stats.warnings} warnings)`}
                  </div>
                  {exportPreviewData.validation.issues.length > 0 && (
                    <div className="space-y-1 max-h-24 overflow-y-auto">
                      {exportPreviewData.validation.issues.slice(0, 5).map((issue, idx) => (
                        <div key={idx} className={`text-xs ${issue.level === 'error' ? 'text-red-600 dark:text-red-400' : issue.level === 'warning' ? 'text-yellow-600 dark:text-yellow-400' : 'text-slate-600 dark:text-slate-400'}`}>
                          {issue.level === 'error' ? '✗' : issue.level === 'warning' ? '⚠' : 'ℹ'} {issue.message}
                        </div>
                      ))}
                      {exportPreviewData.validation.issues.length > 5 && (
                        <div className={`text-xs ${textSecondary}`}>...and {exportPreviewData.validation.issues.length - 5} more</div>
                      )}
                    </div>
                  )}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-200 dark:border-slate-700">
                <button
                  onClick={() => setShowExportPreview(false)}
                  className={`px-4 py-2 rounded-lg ${bgCardAlt} ${textPrimary} hover:opacity-80`}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmExport}
                  disabled={exportPreviewData.validation && !exportPreviewData.validation.valid}
                  className={`px-4 py-2 rounded-lg ${exportPreviewData.validation && !exportPreviewData.validation.valid ? 'bg-slate-400 cursor-not-allowed' : 'bg-emerald-500 hover:bg-emerald-600'} text-white flex items-center gap-2`}
                  title={exportPreviewData.validation && !exportPreviewData.validation.valid ? 'Fix validation errors before exporting' : ''}
                >
                  <Download className="w-4 h-4" /> {exportPreviewData.validation && !exportPreviewData.validation.valid ? 'Fix Errors First' : 'Download'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* BigQuery Export Modal */}
      {showBigQueryModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4" onClick={() => !bigQueryExporting && setShowBigQueryModal(false)}>
          <div className={`${bgCard} rounded-xl shadow-2xl max-w-md w-full overflow-hidden ${borderColor} border`} onClick={e => e.stopPropagation()}>
            <div className="bg-blue-500 p-4 flex justify-between items-center text-white">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Cloud className="w-5 h-5" /> BigQuery Export
              </h3>
              {!bigQueryExporting && (
                <button onClick={() => setShowBigQueryModal(false)} className="hover:bg-blue-600 p-1 rounded"><X className="w-5 h-5" /></button>
              )}
            </div>
            <div className="p-6 space-y-4">
              {/* Progress Indicator */}
              {bigQueryExporting && bigQueryProgress && (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Cpu className="w-5 h-5 text-blue-500 animate-spin" />
                    <span className={`${textPrimary} font-medium`}>{bigQueryProgress.stage}</span>
                  </div>
                  <div className={`text-sm ${textSecondary}`}>{bigQueryProgress.message}</div>
                  <div className={`w-full ${bgCardAlt} rounded-full h-2`}>
                    <div
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${bigQueryProgress.percentage}%` }}
                    />
                  </div>
                  <div className={`text-xs ${textSecondary} text-center`}>{bigQueryProgress.percentage}%</div>
                </div>
              )}

              {/* Result Display */}
              {bigQueryResult && !bigQueryExporting && (
                <div className={`p-4 rounded-lg ${bigQueryResult.success ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800' : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'}`}>
                  <div className={`font-semibold mb-2 ${bigQueryResult.success ? 'text-emerald-700 dark:text-emerald-400' : 'text-red-700 dark:text-red-400'}`}>
                    {bigQueryResult.success ? '✓ Export Successful' : '✗ Export Failed'}
                  </div>

                  {bigQueryResult.success ? (
                    <div className="space-y-2">
                      <div className={`text-sm ${textSecondary}`}>
                        <span className="font-medium">Rows written:</span> {bigQueryResult.rows_written?.toLocaleString()}
                      </div>
                      <div className={`text-sm ${textSecondary}`}>
                        <span className="font-medium">Table:</span> <span className="font-mono text-xs">{bigQueryResult.table}</span>
                      </div>
                      {bigQueryResult.backup_table && (
                        <div className={`text-sm ${textSecondary}`}>
                          <span className="font-medium">Backup:</span> <span className="font-mono text-xs">{bigQueryResult.backup_table}</span>
                          <span className="ml-2">({bigQueryResult.backup_rows?.toLocaleString()} rows)</span>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className={`text-sm ${textSecondary}`}>{bigQueryResult.error}</div>
                      {bigQueryResult.validation_errors && bigQueryResult.validation_errors.length > 0 && (
                        <div className="mt-2 space-y-1 max-h-24 overflow-y-auto">
                          {bigQueryResult.validation_errors.slice(0, 5).map((err, idx) => (
                            <div key={idx} className="text-xs text-red-600 dark:text-red-400">• {err}</div>
                          ))}
                          {bigQueryResult.total_errors && bigQueryResult.total_errors > 5 && (
                            <div className="text-xs text-slate-500">...and {bigQueryResult.total_errors - 5} more errors</div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Close Button */}
              {!bigQueryExporting && (
                <div className="flex justify-end pt-4 border-t border-slate-200 dark:border-slate-700">
                  <button
                    onClick={() => setShowBigQueryModal(false)}
                    className={`px-4 py-2 rounded-lg ${bgCardAlt} ${textPrimary} hover:opacity-80`}
                  >
                    Close
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Settings Panel */}
      {showSettings && (
        <div className={`${darkMode ? 'bg-slate-800' : 'bg-slate-100'} border-b ${borderColor} px-6 py-4`}>
          <div className="max-w-7xl mx-auto space-y-4">
            {/* Row 1: Models */}
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-3">
                <label className={`${textSecondary} text-sm font-medium`}>Main Model:</label>
                <select
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                  className={`${bgCard} ${textPrimary} px-3 py-1.5 rounded border ${borderColor} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                >
                  {availableModels.length > 0 ? (
                    availableModels.map(m => <option key={m} value={m}>{m}</option>)
                  ) : (
                    <>
                      <option value="llama3.2">llama3.2</option>
                      <option value="mistral">mistral</option>
                      <option value="phi3">phi3</option>
                    </>
                  )}
                </select>
              </div>
              <div className="flex items-center gap-3">
                <label className={`${textSecondary} text-sm font-medium`}>NER Model:</label>
                <select
                  value={nerModel}
                  onChange={(e) => setNerModel(e.target.value)}
                  className={`${bgCard} ${textPrimary} px-3 py-1.5 rounded border ${borderColor} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                >
                  <option value="">Same as main</option>
                  {availableModels.map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
              <div className="flex items-center gap-3">
                <label className={`${textSecondary} text-sm font-medium`}>Embedding:</label>
                <select
                  value={embeddingModel}
                  onChange={(e) => setEmbeddingModel(e.target.value)}
                  className={`${bgCard} ${textPrimary} px-3 py-1.5 rounded border ${borderColor} focus:outline-none focus:ring-2 focus:ring-emerald-500`}
                >
                  <option value="nomic-embed-text">nomic-embed-text</option>
                  {availableModels.filter(m => m.includes('embed')).map(m => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>
            </div>

            {/* Row 2: Parameters */}
            <div className="flex flex-wrap items-center gap-4">
              <div className="flex items-center gap-2">
                <label className={`${textSecondary} text-xs`}>Temp:</label>
                <input
                  type="number"
                  value={modelParams.temperature}
                  onChange={(e) => setModelParams({ ...modelParams, temperature: parseFloat(e.target.value) || 0.3 })}
                  min="0" max="2" step="0.1"
                  className={`w-16 ${bgCard} ${textPrimary} px-2 py-1 rounded border ${borderColor} text-sm`}
                />
              </div>
              <div className="flex items-center gap-2">
                <label className={`${textSecondary} text-xs`}>Top P:</label>
                <input
                  type="number"
                  value={modelParams.top_p}
                  onChange={(e) => setModelParams({ ...modelParams, top_p: parseFloat(e.target.value) || 0.9 })}
                  min="0" max="1" step="0.05"
                  className={`w-16 ${bgCard} ${textPrimary} px-2 py-1 rounded border ${borderColor} text-sm`}
                />
              </div>
              <div className="flex items-center gap-2">
                <label className={`${textSecondary} text-xs`}>Context:</label>
                <input
                  type="number"
                  value={modelParams.num_ctx}
                  onChange={(e) => setModelParams({ ...modelParams, num_ctx: parseInt(e.target.value) || 4096 })}
                  min="512" max="32768" step="512"
                  className={`w-20 ${bgCard} ${textPrimary} px-2 py-1 rounded border ${borderColor} text-sm`}
                />
              </div>
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-1 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={useCache}
                    onChange={(e) => setUseCache(e.target.checked)}
                    className="rounded text-emerald-500"
                  />
                  <span className={`${textSecondary} text-xs`}>Cache embeddings</span>
                </label>
              </div>
              {cacheStats && (
                <span className={`${textSecondary} text-xs`}>
                  Cache: {cacheStats.totalEntries} entries ({formatBytes(cacheStats.totalSize)})
                  <button onClick={handleClearCache} className="ml-2 text-red-400 hover:text-red-300 underline">clear</button>
                </span>
              )}
            </div>

            {/* Row 3: Custom Entity Types */}
            <div className="flex flex-wrap items-center gap-3">
              <label className={`${textSecondary} text-sm font-medium`}>Custom Entities:</label>
              {customEntityTypes.map(et => (
                <span key={et} className="flex items-center gap-1 px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
                  {et}
                  <button onClick={() => setCustomEntityTypes(customEntityTypes.filter(t => t !== et))} className="hover:text-purple-900">
                    <X className="w-3 h-3" />
                  </button>
                </span>
              ))}
              <div className="flex items-center gap-1">
                <input
                  type="text"
                  value={newEntityType}
                  onChange={(e) => setNewEntityType(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addCustomEntity()}
                  placeholder="Add entity type..."
                  className={`w-32 ${bgCard} ${textPrimary} px-2 py-1 rounded border ${borderColor} text-xs`}
                />
                <button onClick={addCustomEntity} className="p-1 bg-emerald-500 text-white rounded hover:bg-emerald-600">
                  <Plus className="w-3 h-3" />
                </button>
              </div>
            </div>

            {/* Row 4: Ollama Host */}
            <div className="flex items-center gap-3">
              <label className={`${textSecondary} text-sm font-medium`}>Ollama Host:</label>
              <input
                type="text"
                value={ollamaHost}
                onChange={(e) => {
                  setOllamaHost(e.target.value);
                  localStorage.setItem('neurolinguist_ollama_host', e.target.value);
                }}
                className={`w-64 ${bgCard} ${textPrimary} px-3 py-1.5 rounded border ${borderColor} text-sm`}
              />
              <button onClick={checkOllamaConnection} className="px-3 py-1.5 bg-emerald-600 text-white rounded hover:bg-emerald-700 text-sm">
                Test
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="flex-1 max-w-7xl mx-auto w-full p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Panel: Input & Controls */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className={`${bgCard} rounded-xl shadow-sm border ${borderColor} overflow-hidden`}>
            <div className={`p-4 ${bgCardAlt} border-b ${borderColor} flex justify-between items-center`}>
              <h2 className={`font-semibold ${textPrimary} flex items-center gap-2`}>
                <Activity className="w-4 h-4 text-blue-500" />
                System Status
              </h2>
              <div className="flex items-center gap-2">
                {conversation && (
                  <>
                    <button onClick={handleSaveConversation} className="p-1 hover:bg-emerald-100 text-emerald-500 rounded" title="Save for comparison">
                      <GitCompare className="w-4 h-4" />
                    </button>
                    <button onClick={handleClearData} className="p-1 hover:bg-red-100 text-slate-400 hover:text-red-500 rounded" title="Clear Data">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </>
                )}
                <span className={`px-2 py-0.5 rounded text-xs font-medium uppercase ${status === 'idle' ? 'bg-slate-200 text-slate-600' :
                  status === 'complete' ? 'bg-emerald-100 text-emerald-700' :
                    status === 'error' ? 'bg-red-100 text-red-700' :
                      'bg-blue-100 text-blue-700 animate-pulse'
                  }`}>
                  {status.replace('_', ' ')}
                </span>
              </div>
            </div>
            <div className="p-4">
              {status !== 'idle' && (
                <div className="mb-4">
                  <div className={`h-2 ${bgCardAlt} rounded-full overflow-hidden`}>
                    <div className="h-full bg-blue-500 transition-all duration-500 ease-out" style={{ width: `${progress}%` }} />
                  </div>
                  <div className="flex justify-between items-center mt-1">
                    <p className={`text-xs ${textSecondary}`}>
                      {detailedProgress ? (
                        <span>
                          <span className="font-medium capitalize">{detailedProgress.stage}</span>
                          {detailedProgress.totalItems > 1 && (
                            <span> ({detailedProgress.currentItem}/{detailedProgress.totalItems})</span>
                          )}
                        </span>
                      ) : (
                        <span>{status.replace('_', ' ')}</span>
                      )}
                    </p>
                    <p className={`text-xs ${textSecondary}`}>{progress}%</p>
                  </div>
                </div>
              )}
              <div className={`${darkMode ? 'bg-slate-950' : 'bg-slate-900'} rounded-lg p-3 h-48 overflow-y-auto custom-scrollbar font-mono text-xs text-green-400`}>
                {log.length === 0 ? <span className="text-slate-600">Waiting for input...</span> : log.map((l, i) => (
                  <div key={i} className="mb-1">{l}</div>
                ))}
              </div>
            </div>
          </div>

          <div className={`${bgCard} rounded-xl shadow-sm border ${borderColor} flex flex-col flex-1`}>
            <div className={`p-4 border-b ${borderColor} flex items-center justify-between`}>
              <h2 className={`font-semibold ${textPrimary} flex items-center gap-2`}>
                <FileJson className="w-4 h-4 text-orange-500" />
                Raw JSON Input
              </h2>
              <div className="flex gap-2">
                <label className={`flex items-center gap-2 px-3 py-1.5 ${bgCardAlt} hover:opacity-80 ${textSecondary} text-xs font-medium rounded-md cursor-pointer transition-colors border ${borderColor}`} title="Upload single file">
                  <Upload className="w-3.5 h-3.5" />
                  <span>Single</span>
                  <input type="file" accept=".json,application/json" className="hidden" onChange={handleFileUpload} />
                </label>
                <label className={`flex items-center gap-2 px-3 py-1.5 ${bgCardAlt} hover:opacity-80 ${textSecondary} text-xs font-medium rounded-md cursor-pointer transition-colors border ${borderColor}`} title="Upload multiple files for batch processing">
                  <Layers className="w-3.5 h-3.5" />
                  <span>Batch</span>
                  <input type="file" accept=".json,application/json" multiple className="hidden" onChange={handleBatchFileUpload} />
                </label>
              </div>
            </div>
            <div className="p-4 flex-1 flex flex-col gap-4">
              <textarea
                className={`w-full h-64 p-3 border ${borderColor} rounded-lg font-mono text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none resize-none ${bgCardAlt} ${textPrimary}`}
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                placeholder="Paste Claude, ChatGPT, or Gemini JSON export here..."
              />
              {isProcessing ? (
                <div className="flex gap-2">
                  <button
                    onClick={handleCancel}
                    className="flex-1 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors shadow-sm"
                  >
                    <X className="w-4 h-4" /> Cancel (Esc)
                  </button>
                  <div className="flex-[2] py-3 bg-slate-600 text-white font-medium rounded-lg flex items-center justify-center gap-2 cursor-not-allowed">
                    <Cpu className="w-4 h-4 animate-spin" /> Processing...
                  </div>
                </div>
              ) : (
                <button
                  onClick={handleProcess}
                  disabled={!ollamaConnected}
                  className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors shadow-sm"
                >
                  <Play className="w-4 h-4" /> Parse (Ctrl+Enter)
                </button>
              )}
              {!ollamaConnected && (
                <p className="text-xs text-red-500 text-center">
                  Ollama is not running. Start it with <code className={`${bgCardAlt} px-1 rounded`}>ollama serve</code>
                </p>
              )}
            </div>
          </div>

          {/* Batch Processing Panel */}
          {batchMode && (
            <div className={`${bgCard} rounded-xl shadow-sm border ${borderColor} p-4`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className={`font-semibold ${textPrimary} text-sm flex items-center gap-2`}>
                  <Layers className="w-4 h-4 text-blue-500" />
                  Batch Mode ({batchFiles.length} files)
                </h3>
                <button onClick={clearBatchMode} className="text-xs text-red-500 hover:text-red-700">
                  Clear
                </button>
              </div>
              <div className="space-y-2 max-h-40 overflow-y-auto mb-3">
                {batchFiles.map((file, idx) => (
                  <div key={idx} className={`flex items-center justify-between p-2 ${bgCardAlt} rounded border ${borderColor}`}>
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <span className={`text-xs ${file.status === 'done' ? 'text-emerald-500' : file.status === 'error' ? 'text-red-500' : file.status === 'processing' ? 'text-blue-500' : textSecondary}`}>
                        {file.status === 'processing' ? <Cpu className="w-3 h-3 animate-spin inline" /> : file.status === 'done' ? '✓' : file.status === 'error' ? '✗' : '○'}
                      </span>
                      <span className={`text-xs ${textSecondary} truncate`}>{file.name}</span>
                    </div>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${file.format === 'claude' ? 'bg-orange-100 text-orange-700 dark:bg-orange-900/30' : file.format === 'chatgpt' ? 'bg-green-100 text-green-700 dark:bg-green-900/30' : file.format === 'gemini' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30' : 'bg-slate-100 text-slate-700 dark:bg-slate-700'}`}>
                      {file.format}
                    </span>
                  </div>
                ))}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleBatchProcess}
                  disabled={!ollamaConnected || isProcessing}
                  className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-sm font-medium rounded flex items-center justify-center gap-2"
                >
                  <Play className="w-3.5 h-3.5" /> Process All
                </button>
                {processedConversations.length > 0 && (
                  <button
                    onClick={handleBatchExport}
                    className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded flex items-center justify-center gap-2"
                  >
                    <Download className="w-3.5 h-3.5" /> Export All
                  </button>
                )}
              </div>
              {processedConversations.length > 0 && (
                <p className={`text-xs ${textSecondary} mt-2`}>
                  {processedConversations.length} conversation(s) ready for export
                </p>
              )}
            </div>
          )}

          {/* Saved Conversations */}
          {savedConversations.length > 0 && (
            <div className={`${bgCard} rounded-xl shadow-sm border ${borderColor} p-4`}>
              <h3 className={`font-semibold ${textPrimary} text-sm mb-3 flex items-center gap-2`}>
                <GitCompare className="w-4 h-4 text-purple-500" />
                Saved for Comparison
              </h3>
              <div className="space-y-2">
                {savedConversations.map(conv => (
                  <div key={conv.id} className={`flex items-center justify-between p-2 ${bgCardAlt} rounded border ${borderColor}`}>
                    <span className={`text-xs ${textSecondary}`}>{conv.id.substring(0, 8)}... ({conv.topicCount} topics)</span>
                    <button
                      onClick={() => handleCompare(conv)}
                      disabled={!conversation || conversation.id === conv.id}
                      className="text-xs text-purple-600 hover:text-purple-700 disabled:opacity-50"
                    >
                      Compare
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Panel */}
        <div className="lg:col-span-8 flex flex-col gap-6 h-[calc(100vh-8rem)]">
          <div className="flex flex-col sm:flex-row justify-between items-end sm:items-center gap-4">
            <div className={`flex items-center gap-1 ${bgCardAlt} p-1 rounded-lg w-fit`}>
              <TabButton active={activeTab === 'hierarchy'} onClick={() => setActiveTab('hierarchy')} icon={Layers} label="Hierarchy" darkMode={darkMode} />
              <TabButton active={activeTab === 'table'} onClick={() => setActiveTab('table')} icon={Database} label="Data" darkMode={darkMode} />
              <TabButton active={activeTab === 'json'} onClick={() => setActiveTab('json')} icon={FileText} label="JSON" darkMode={darkMode} />
              {diffResult && <TabButton active={activeTab === 'compare'} onClick={() => setActiveTab('compare')} icon={GitCompare} label="Diff" darkMode={darkMode} />}
            </div>

            {conversation && (
              <div className="flex gap-2 w-full sm:w-auto">
                {activeTab === 'table' && (
                  <div className="relative flex-1 sm:w-64">
                    <Search className="absolute left-2.5 top-2 w-4 h-4 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search..."
                      className={`w-full pl-9 pr-3 py-1.5 text-sm border ${borderColor} rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500 ${bgCard} ${textPrimary}`}
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                )}
                <div className="relative group">
                  <button className={`flex items-center gap-2 px-3 py-1.5 ${darkMode ? 'bg-slate-700' : 'bg-slate-800'} text-white text-sm rounded-md hover:opacity-90 transition-colors`}>
                    <Download className="w-4 h-4" /> Export
                  </button>
                  <div className={`absolute right-0 mt-1 ${bgCard} border ${borderColor} rounded-md shadow-lg hidden group-hover:block z-10 min-w-[200px]`}>
                    <div className={`px-3 py-1.5 text-xs font-semibold ${textSecondary} border-b ${borderColor}`}>Legacy Formats</div>
                    <button onClick={handleExportCSV} className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-emerald-50 dark:hover:bg-emerald-900/20`}>CSV (Flat)</button>
                    <button onClick={() => handleExportSpine('json')} className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-emerald-50 dark:hover:bg-emerald-900/20`}>Spine JSON</button>
                    <button onClick={() => handleExportSpine('jsonl')} className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-emerald-50 dark:hover:bg-emerald-900/20`}>Spine JSONL</button>
                    <button onClick={() => handleExportSpine('csv')} className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-emerald-50 dark:hover:bg-emerald-900/20`}>Entities CSV</button>
                    <div className={`px-3 py-1.5 text-xs font-semibold ${textSecondary} border-t border-b ${borderColor} mt-1`}>BigQuery Native</div>
                    <button onClick={() => handleExportNativeSpine(false)} className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-emerald-50 dark:hover:bg-emerald-900/20`}>
                      <span className="flex items-center gap-2"><Database className="w-3 h-3" /> Entities JSONL</span>
                    </button>
                    <button onClick={() => handleExportNativeSpine(true)} className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-emerald-50 dark:hover:bg-emerald-900/20`}>
                      <span className="flex items-center gap-2"><Database className="w-3 h-3" /> Entities + Relations</span>
                    </button>
                    <div className={`px-3 py-1.5 text-xs font-semibold ${textSecondary} border-t border-b ${borderColor} mt-1`}>Direct Upload</div>
                    <button
                      onClick={handleBigQueryExport}
                      disabled={bigQueryExporting}
                      className={`w-full px-4 py-2 text-left text-sm ${textPrimary} hover:bg-blue-50 dark:hover:bg-blue-900/20 disabled:opacity-50`}
                    >
                      <span className="flex items-center gap-2">
                        <Cloud className="w-3 h-3 text-blue-500" />
                        {bigQueryExporting ? 'Exporting...' : 'Export to BigQuery'}
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className={`${bgCard} rounded-xl shadow-sm border ${borderColor} flex-1 overflow-hidden relative flex flex-col`}>
            {!conversation ? (
              <div className={`absolute inset-0 flex flex-col items-center justify-center ${textSecondary}`}>
                <Layers className="w-16 h-16 mb-4 opacity-20" />
                <p>No data processed yet.</p>
              </div>
            ) : (
              <>
                {activeTab === 'hierarchy' && (
                  <HierarchyView
                    conversation={conversation}
                    onRegenerateSummary={handleRegenerateSummary}
                    onSpanClick={handleSpanClick}
                    highlightedId={highlightedId}
                    darkMode={darkMode}
                  />
                )}
                {activeTab === 'table' && <TableView data={filteredData} totalCount={denormalizedData.length} highlightedId={highlightedId} darkMode={darkMode} />}
                {activeTab === 'json' && (
                  <div className="p-4 overflow-auto custom-scrollbar h-full">
                    <pre className={`text-xs font-mono ${textSecondary}`}>{JSON.stringify(conversation, null, 2)}</pre>
                  </div>
                )}
                {activeTab === 'compare' && diffResult && (
                  <DiffView diff={diffResult} darkMode={darkMode} />
                )}
              </>
            )}
          </div>
        </div>
      </main>

      {/* Span Detail Modal */}
      {selectedSpan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4" onClick={() => setSelectedSpan(null)}>
          <div className={`${bgCard} rounded-xl shadow-2xl max-w-lg w-full overflow-hidden border ${borderColor}`} onClick={e => e.stopPropagation()}>
            <div className="bg-emerald-500 p-4 flex justify-between items-center text-white">
              <h3 className="font-bold text-lg flex items-center gap-2">
                <Tag className="w-5 h-5" /> Span Detail
              </h3>
              <button onClick={() => setSelectedSpan(null)} className="hover:bg-emerald-600 p-1 rounded"><X className="w-5 h-5" /></button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className={`text-xs font-bold ${textSecondary} uppercase`}>Entity Text</label>
                <p className={`text-2xl font-bold ${textPrimary}`}>{selectedSpan.span.text}</p>
                <span className={`inline-block mt-1 px-2 py-0.5 rounded text-xs font-bold ${bgCardAlt} ${textSecondary} border ${borderColor}`}>
                  {selectedSpan.span.label}
                </span>
              </div>
              <div className={`p-3 ${bgCardAlt} rounded border ${borderColor}`}>
                <label className={`text-xs font-bold ${textSecondary} uppercase mb-1 block`}>Context (Sentence)</label>
                <p className={`text-sm ${textSecondary} italic`}>{selectedSpan.sentence.text}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={`text-xs font-bold ${textSecondary} uppercase`}>Turn / Role</label>
                  <p className={`text-sm font-medium capitalize flex items-center gap-1 ${textPrimary}`}>
                    {selectedSpan.message.role === 'user' ? <User className="w-3 h-3" /> : <Bot className="w-3 h-3" />}
                    {selectedSpan.message.role}
                  </p>
                </div>
                <div>
                  <label className={`text-xs font-bold ${textSecondary} uppercase`}>Topic</label>
                  <p className={`text-sm font-medium truncate ${textPrimary}`} title={selectedSpan.topic.title}>{selectedSpan.topic.title}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// --- Subcomponents ---

function TabButton({ active, onClick, icon: Icon, label, darkMode }: any) {
  return (
    <button onClick={onClick} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${active
      ? darkMode ? 'bg-slate-700 text-emerald-400 shadow-sm' : 'bg-white text-emerald-600 shadow-sm'
      : darkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-600/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-300/50'
      }`}>
      <Icon className="w-4 h-4" /> {label}
    </button>
  );
}

function TableView({ data, totalCount, highlightedId, darkMode }: { data: DenormalizedRow[], totalCount: number, highlightedId: string | null, darkMode: boolean }) {
  const rowRefs = useRef<{ [key: string]: HTMLTableRowElement | null }>({});
  const bgCardAlt = darkMode ? 'bg-slate-700' : 'bg-slate-50';
  const textPrimary = darkMode ? 'text-slate-100' : 'text-slate-900';
  const textSecondary = darkMode ? 'text-slate-400' : 'text-slate-600';
  const borderColor = darkMode ? 'border-slate-600' : 'border-slate-200';

  useEffect(() => {
    if (highlightedId && rowRefs.current[highlightedId]) {
      rowRefs.current[highlightedId]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [highlightedId]);

  return (
    <div className="flex flex-col h-full">
      <div className={`p-4 ${bgCardAlt} border-b ${borderColor} flex justify-between items-center`}>
        <h3 className={`font-semibold ${textPrimary}`}>Records: {data.length} <span className={`${textSecondary} font-normal`}>of {totalCount}</span></h3>
      </div>
      <div className="flex-1 overflow-auto custom-scrollbar">
        <table className="w-full text-left text-xs border-collapse">
          <thead className={`${bgCardAlt} ${textSecondary} sticky top-0 z-10 shadow-sm`}>
            <tr>
              <th className={`p-3 font-semibold border-b ${borderColor}`}>L8 ID</th>
              <th className={`p-3 font-semibold border-b ${borderColor}`}>L7 ID</th>
              <th className={`p-3 font-semibold border-b ${borderColor}`}>Leaf</th>
              <th className={`p-3 font-semibold border-b ${borderColor}`}>Type</th>
              <th className={`p-3 font-semibold border-b ${borderColor}`}>Content</th>
              <th className={`p-3 font-semibold border-b ${borderColor}`}>Counts</th>
            </tr>
          </thead>
          <tbody className={`divide-y ${darkMode ? 'divide-slate-700' : 'divide-slate-100'}`}>
            {data.map((row, i) => {
              const isHighlighted = (highlightedId && (row.l3_id === highlightedId || row.l2_id === highlightedId));
              return (
                <tr
                  key={i}
                  ref={el => { if (row.l3_id) rowRefs.current[row.l3_id] = el; }}
                  className={`${isHighlighted ? 'bg-yellow-50 dark:bg-yellow-900/20 ring-2 ring-inset ring-yellow-400' : darkMode ? 'hover:bg-slate-700/50' : 'hover:bg-slate-50'} transition-colors duration-500`}
                >
                  <td className={`p-3 ${textSecondary} font-mono`} title={row.l8_id}>{row.l8_id.substring(0, 6)}...</td>
                  <td className={`p-3 ${textSecondary} font-mono`} title={row.l7_id}>{row.l7_id.substring(0, 6)}...</td>
                  <td className="p-3 font-mono text-emerald-600">{row.l3_id ? row.l3_id.substring(0, 6) : row.l2_id?.substring(0, 6)}...</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${row.type === 'word' ? 'bg-slate-100 dark:bg-slate-600 text-slate-600 dark:text-slate-300' :
                      ['EMAIL', 'URL'].includes(row.meta) ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300' :
                        row.meta === 'CUSTOM_ENTITY' ? 'bg-purple-100 dark:bg-purple-900/50 text-purple-700 dark:text-purple-300' :
                          'bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300'
                      }`}>
                      {row.type === 'span' ? row.meta : row.type}
                    </span>
                  </td>
                  <td className={`p-3 font-medium ${textPrimary} max-w-xs truncate`} title={row.content}>{row.content}</td>
                  <td className={`p-3 ${textSecondary} italic text-[10px]`}>
                    T:{row.topic_count} Tn:{row.turn_count} M:{row.message_count}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DiffView({ diff, darkMode }: { diff: ConversationDiffResult, darkMode: boolean }) {
  const bgCardAlt = darkMode ? 'bg-slate-700' : 'bg-slate-50';
  const textPrimary = darkMode ? 'text-slate-100' : 'text-slate-900';
  const textSecondary = darkMode ? 'text-slate-400' : 'text-slate-600';
  const borderColor = darkMode ? 'border-slate-600' : 'border-slate-200';

  return (
    <div className="p-6 overflow-auto custom-scrollbar h-full">
      <h2 className={`text-xl font-bold ${textPrimary} mb-6`}>Conversation Comparison</h2>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className={`p-4 ${bgCardAlt} rounded-lg border ${borderColor}`}>
          <div className={`text-2xl font-bold ${diff.summary.topicCountDiff > 0 ? 'text-emerald-500' : diff.summary.topicCountDiff < 0 ? 'text-red-500' : textPrimary}`}>
            {diff.summary.topicCountDiff > 0 ? '+' : ''}{diff.summary.topicCountDiff}
          </div>
          <div className={`text-xs ${textSecondary}`}>Topic Change</div>
        </div>
        <div className={`p-4 ${bgCardAlt} rounded-lg border ${borderColor}`}>
          <div className={`text-2xl font-bold text-emerald-500`}>{diff.summary.newTopics}</div>
          <div className={`text-xs ${textSecondary}`}>New Topics</div>
        </div>
        <div className={`p-4 ${bgCardAlt} rounded-lg border ${borderColor}`}>
          <div className={`text-2xl font-bold text-red-500`}>{diff.summary.removedTopics}</div>
          <div className={`text-xs ${textSecondary}`}>Removed Topics</div>
        </div>
        <div className={`p-4 ${bgCardAlt} rounded-lg border ${borderColor}`}>
          <div className={`text-2xl font-bold text-blue-500`}>{diff.summary.similarTopics}</div>
          <div className={`text-xs ${textSecondary}`}>Similar Topics</div>
        </div>
      </div>

      {/* Keyword Evolution */}
      <div className={`mb-6 p-4 ${bgCardAlt} rounded-lg border ${borderColor}`}>
        <h3 className={`font-semibold ${textPrimary} mb-3`}>Keyword Evolution</h3>
        <div className="space-y-2">
          {diff.keywordEvolution.emerging.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="text-emerald-500 text-xs font-bold">EMERGING:</span>
              <div className="flex flex-wrap gap-1">
                {diff.keywordEvolution.emerging.map(k => (
                  <span key={k} className="px-2 py-0.5 bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 rounded text-xs">{k}</span>
                ))}
              </div>
            </div>
          )}
          {diff.keywordEvolution.declining.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="text-red-500 text-xs font-bold">DECLINING:</span>
              <div className="flex flex-wrap gap-1">
                {diff.keywordEvolution.declining.map(k => (
                  <span key={k} className="px-2 py-0.5 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded text-xs">{k}</span>
                ))}
              </div>
            </div>
          )}
          {diff.keywordEvolution.persistent.length > 0 && (
            <div className="flex items-start gap-2">
              <span className={`${textSecondary} text-xs font-bold`}>PERSISTENT:</span>
              <div className="flex flex-wrap gap-1">
                {diff.keywordEvolution.persistent.map(k => (
                  <span key={k} className={`px-2 py-0.5 ${darkMode ? 'bg-slate-600' : 'bg-slate-200'} ${textSecondary} rounded text-xs`}>{k}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sentiment Shift */}
      <div className={`mb-6 p-4 ${bgCardAlt} rounded-lg border ${borderColor}`}>
        <h3 className={`font-semibold ${textPrimary} mb-3`}>Sentiment Shift: <span className={`${diff.sentimentShift.shift === 'more_positive' ? 'text-emerald-500' : diff.sentimentShift.shift === 'more_negative' ? 'text-red-500' : textSecondary}`}>{diff.sentimentShift.shift.replace('_', ' ')}</span></h3>
        <div className="flex gap-8">
          <div>
            <div className={`text-xs ${textSecondary} mb-1`}>Before</div>
            <div className="flex gap-2">
              <span className="text-emerald-500">{diff.sentimentShift.conversation1.positive} pos</span>
              <span className={textSecondary}>{diff.sentimentShift.conversation1.neutral} neu</span>
              <span className="text-red-500">{diff.sentimentShift.conversation1.negative} neg</span>
            </div>
          </div>
          <div>
            <div className={`text-xs ${textSecondary} mb-1`}>After</div>
            <div className="flex gap-2">
              <span className="text-emerald-500">{diff.sentimentShift.conversation2.positive} pos</span>
              <span className={textSecondary}>{diff.sentimentShift.conversation2.neutral} neu</span>
              <span className="text-red-500">{diff.sentimentShift.conversation2.negative} neg</span>
            </div>
          </div>
        </div>
      </div>

      {/* Topic Lists */}
      {diff.topics.added.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-emerald-500 mb-2">+ New Topics</h3>
          {diff.topics.added.map(t => (
            <div key={t.id} className={`p-2 ${bgCardAlt} rounded border ${borderColor} mb-2`}>
              <div className={`font-medium ${textPrimary}`}>{t.title}</div>
              <div className={`text-xs ${textSecondary}`}>{t.summary}</div>
            </div>
          ))}
        </div>
      )}

      {diff.topics.removed.length > 0 && (
        <div className="mb-4">
          <h3 className="font-semibold text-red-500 mb-2">- Removed Topics</h3>
          {diff.topics.removed.map(t => (
            <div key={t.id} className={`p-2 ${bgCardAlt} rounded border ${borderColor} mb-2 opacity-60`}>
              <div className={`font-medium ${textPrimary}`}>{t.title}</div>
              <div className={`text-xs ${textSecondary}`}>{t.summary}</div>
            </div>
          ))}
        </div>
      )}

      {diff.topics.similar.length > 0 && (
        <div>
          <h3 className="font-semibold text-blue-500 mb-2">≈ Topic Evolution</h3>
          {diff.topics.similar.map(({ topic1, topic2, similarity, keywordOverlap }) => (
            <div key={topic1.id} className={`p-2 ${bgCardAlt} rounded border ${borderColor} mb-2`}>
              <div className="flex items-center gap-2">
                <span className={`${textSecondary} line-through`}>{topic1.title}</span>
                <span className={textSecondary}>→</span>
                <span className={`font-medium ${textPrimary}`}>{topic2.title}</span>
                <span className="text-blue-500 text-xs ml-auto">{(similarity * 100).toFixed(0)}% similar</span>
              </div>
              {keywordOverlap.length > 0 && (
                <div className={`text-xs ${textSecondary} mt-1`}>Shared: {keywordOverlap.join(', ')}</div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Simplified HierarchyView (keeping essential functionality)
function HierarchyView({
  conversation,
  onRegenerateSummary,
  onSpanClick,
  highlightedId,
  darkMode
}: {
  conversation: Conversation,
  onRegenerateSummary: (id: string, turns: Turn[]) => void,
  onSpanClick: (span: Span, sentence: Sentence, message: Message, topic: TopicSegment) => void,
  highlightedId: string | null,
  darkMode: boolean
}) {
  const [collapsedTopics, setCollapsedTopics] = useState<Set<string>>(new Set());
  const [collapsedTurns, setCollapsedTurns] = useState<Set<string>>(new Set());

  const bgCardAlt = darkMode ? 'bg-slate-700' : 'bg-slate-50';
  const textPrimary = darkMode ? 'text-slate-100' : 'text-slate-800';
  const textSecondary = darkMode ? 'text-slate-400' : 'text-slate-500';
  const borderColor = darkMode ? 'border-slate-600' : 'border-slate-200';

  const toggleTopic = (id: string) => {
    const next = new Set(collapsedTopics);
    next.has(id) ? next.delete(id) : next.add(id);
    setCollapsedTopics(next);
  };

  const toggleTurn = (id: string) => {
    const next = new Set(collapsedTurns);
    next.has(id) ? next.delete(id) : next.add(id);
    setCollapsedTurns(next);
  };

  const expandAll = () => { setCollapsedTopics(new Set()); setCollapsedTurns(new Set()); };
  const collapseAll = () => {
    setCollapsedTopics(new Set(conversation.topics.map(t => t.id)));
    setCollapsedTurns(new Set(conversation.topics.flatMap(t => t.turns.map(tn => tn.id))));
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden">
      <div className={`p-3 border-b ${borderColor} ${bgCardAlt} flex gap-3 items-center justify-end`}>
        <button onClick={expandAll} className={`flex items-center gap-1 px-2 py-1 ${darkMode ? 'bg-slate-600 border-slate-500' : 'bg-white border-slate-300'} border rounded text-xs ${textSecondary} hover:opacity-80 shadow-sm`}>
          <Maximize2 className="w-3 h-3" /> Expand
        </button>
        <button onClick={collapseAll} className={`flex items-center gap-1 px-2 py-1 ${darkMode ? 'bg-slate-600 border-slate-500' : 'bg-white border-slate-300'} border rounded text-xs ${textSecondary} hover:opacity-80 shadow-sm`}>
          <Minimize2 className="w-3 h-3" /> Collapse
        </button>
      </div>

      <div className="flex-1 overflow-auto custom-scrollbar p-6">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className={`border ${borderColor} rounded-lg p-4 ${darkMode ? 'bg-slate-800' : 'bg-white'} shadow-sm relative`}>
            <div className="absolute -left-3 top-4 w-1 h-8 bg-purple-500 rounded-full"></div>
            <h3 className={`text-lg font-bold ${textPrimary} flex items-center gap-2`}>
              <span>Conversation (L8)</span>
              <span className={`text-xs font-mono ${textSecondary} font-normal`}>{conversation.id.substring(0, 8)}</span>
            </h3>
            <span className="text-xs bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-300 px-2 py-0.5 rounded-full font-bold mt-1 inline-block">{conversation.topicCount} Topics</span>

            <div className={`space-y-4 pl-4 border-l-2 ${darkMode ? 'border-slate-600' : 'border-slate-100'} ml-2 mt-4`}>
              {conversation.topics.map(topic => {
                const isCollapsed = collapsedTopics.has(topic.id);

                return (
                  <div key={topic.id} className={`${bgCardAlt} rounded border ${borderColor} p-3 transition-all`}>
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-start gap-2 cursor-pointer group flex-1" onClick={() => toggleTopic(topic.id)}>
                        <button className="mt-1 p-0.5">
                          {isCollapsed ? <ChevronRight className={`w-4 h-4 ${textSecondary}`} /> : <ChevronDown className={`w-4 h-4 ${textSecondary}`} />}
                        </button>
                        <div className="flex-1">
                          <h4 className={`font-semibold ${textPrimary} text-sm flex items-center gap-2 group-hover:text-blue-500 transition-colors`}>
                            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                            Topic (L7): {topic.title}
                          </h4>
                          <div className="flex flex-wrap items-center gap-2 mt-1.5">
                            <SentimentIndicator sentiment={topic.sentiment} darkMode={darkMode} />
                            {topic.keywords && topic.keywords.slice(0, 3).map((k, idx) => (
                              <span key={idx} className={`text-[10px] ${darkMode ? 'bg-slate-600' : 'bg-white'} ${textSecondary} px-1.5 py-0.5 rounded border ${borderColor}`}>{k}</span>
                            ))}
                          </div>
                          <div className="flex items-center gap-2 mt-2">
                            <p className={`text-xs ${textSecondary}`}>{topic.summary}</p>
                            <button onClick={(e) => { e.stopPropagation(); onRegenerateSummary(topic.id, topic.turns); }} className="text-[10px] flex items-center gap-1 text-emerald-600 hover:text-emerald-700 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 px-1 py-0.5 rounded"><Sparkles className="w-3 h-3" /> Refine</button>
                          </div>
                        </div>
                      </div>
                      <span className="text-[10px] bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-300 px-1.5 rounded font-bold">{topic.turnCount} Turns</span>
                    </div>

                    {!isCollapsed && (
                      <div className={`space-y-3 pl-4 border-l-2 ${borderColor} ml-1 mt-3`}>
                        {topic.turns.map((turn, tIdx) => {
                          const isTurnCollapsed = collapsedTurns.has(turn.id);
                          const initiator = turn.messages[0]?.role || 'unknown';

                          return (
                            <div key={turn.id} className="relative">
                              <div className={`${darkMode ? 'bg-slate-600/30' : 'bg-white'} border ${borderColor} rounded p-2 text-xs`}>
                                <div className={`flex justify-between items-center ${textSecondary} font-mono text-[10px] mb-1 cursor-pointer hover:bg-white/10 rounded p-1`} onClick={() => toggleTurn(turn.id)}>
                                  <div className="flex items-center gap-2">
                                    <button className="p-0.5">{isTurnCollapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}</button>
                                    <span className={`font-bold ${initiator === 'user' ? 'text-blue-500' : 'text-emerald-500'}`}>Turn {tIdx + 1} ({initiator})</span>
                                  </div>
                                  <span className={`${darkMode ? 'bg-slate-500' : 'bg-slate-100'} ${textSecondary} px-1 rounded`}>Msgs: {turn.messageCount}</span>
                                </div>
                                {!isTurnCollapsed && (
                                  <div className="space-y-2 mt-2">
                                    {turn.messages.map(msg => (
                                      <div key={msg.id} className={`p-2 rounded border-l-2 ${msg.role === 'user' ? 'bg-blue-50/50 dark:bg-blue-900/20 border-blue-400' : 'bg-emerald-50/50 dark:bg-emerald-900/20 border-emerald-400'}`}>
                                        <div className="flex justify-between items-center mb-1">
                                          <span className={`font-bold text-[10px] uppercase ${textSecondary}`}>{msg.role} (L5)</span>
                                          <span className={`text-[9px] ${textSecondary}`}>Sentences: {msg.sentenceCount}</span>
                                        </div>
                                        <div className="mt-2 pl-2 space-y-1">
                                          {msg.sentences.slice(0, 3).map((sent, sIdx) => (
                                            <div key={sent.id} className={`${textSecondary} p-1 rounded group`}>
                                              <div className="flex gap-2">
                                                <span className="text-slate-400 select-none">{sIdx + 1}.</span>
                                                <span className="line-clamp-2">{sent.text}</span>
                                              </div>
                                              {sent.spans.length > 0 && (
                                                <div className="mt-1 pl-5 flex gap-1 flex-wrap">
                                                  {sent.spans.map(span => (
                                                    <button
                                                      key={span.id}
                                                      onClick={(e) => { e.stopPropagation(); onSpanClick(span, sent, msg, topic); }}
                                                      className={`px-1.5 py-0.5 rounded text-[10px] font-medium border cursor-pointer hover:shadow-sm transition-all ${span.label === 'CODE_SNIPPET' ? 'bg-slate-800 text-slate-200 border-slate-700' :
                                                        span.label === 'TECH_TERM' ? 'bg-indigo-100 dark:bg-indigo-900/50 text-indigo-700 dark:text-indigo-300 border-indigo-200 dark:border-indigo-700' :
                                                          'bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-700'
                                                        }`}>
                                                      {span.text} ({span.label})
                                                    </button>
                                                  ))}
                                                </div>
                                              )}
                                            </div>
                                          ))}
                                          {msg.sentences.length > 3 && (
                                            <div className={`text-[10px] ${textSecondary} pl-5`}>+ {msg.sentences.length - 3} more sentences</div>
                                          )}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const SentimentIndicator = ({ sentiment, darkMode }: { sentiment?: string, darkMode: boolean }) => {
  if (!sentiment) return null;
  const config = {
    positive: { icon: Smile, color: 'text-green-500', bg: darkMode ? 'bg-green-900/50' : 'bg-green-100' },
    neutral: { icon: Meh, color: darkMode ? 'text-slate-400' : 'text-slate-500', bg: darkMode ? 'bg-slate-600' : 'bg-slate-100' },
    negative: { icon: Frown, color: 'text-red-500', bg: darkMode ? 'bg-red-900/50' : 'bg-red-100' },
  }[sentiment] || { icon: Meh, color: 'text-slate-400', bg: 'bg-slate-50' };
  const Icon = config.icon;
  return (
    <div className={`flex items-center gap-1 px-1.5 py-0.5 rounded ${config.bg} border border-transparent`}>
      <Icon className={`w-3 h-3 ${config.color}`} />
      <span className={`text-[10px] uppercase font-bold ${config.color}`}>{sentiment}</span>
    </div>
  );
};
