import {
  TopicSegment, Turn, Sentence, Span, Word
} from '../types';
import { embeddingCache } from './embeddingCache';

const generateId = () => crypto.randomUUID();

// Get Ollama host from environment or localStorage or default
const getOllamaHost = (): string => {
  // Check localStorage first (user override)
  const stored = localStorage.getItem('neurolinguist_ollama_host');
  if (stored) return stored;

  // Check for env var (set at build time)
  // @ts-ignore
  if (typeof import.meta !== 'undefined' && import.meta.env?.VITE_OLLAMA_HOST) {
    // @ts-ignore
    return import.meta.env.VITE_OLLAMA_HOST;
  }

  return 'http://localhost:11434';
};

export interface ModelParameters {
  temperature: number;
  top_p: number;
  top_k: number;
  num_ctx: number;
  num_predict: number;
  repeat_penalty: number;
}

export interface OllamaConfig {
  baseUrl: string;
  model: string;
  embeddingModel: string;
  nerModel: string; // Separate model for NER (can be faster/smaller)
  maxRetries: number;
  retryDelayMs: number;
  timeoutMs: number;
  useCache: boolean;
  modelParams: ModelParameters;
  customEntityTypes: string[];
}

export interface ProcessingProgress {
  stage: 'topics' | 'embeddings' | 'messages' | 'complete';
  currentItem: number;
  totalItems: number;
  currentLabel: string;
  percentage: number;
}

export interface GpuInfo {
  available: boolean;
  name?: string;
  vramTotal?: number;
  vramUsed?: number;
}

export type ProgressCallback = (progress: ProcessingProgress) => void;

const DEFAULT_MODEL_PARAMS: ModelParameters = {
  temperature: 0.3,
  top_p: 0.9,
  top_k: 40,
  num_ctx: 4096,
  num_predict: 4096,
  repeat_penalty: 1.1
};

const DEFAULT_CONFIG: OllamaConfig = {
  baseUrl: getOllamaHost(),
  model: 'llama3.2',
  embeddingModel: 'nomic-embed-text',
  nerModel: '', // Empty = use main model
  maxRetries: 3,
  retryDelayMs: 1000,
  timeoutMs: 120000,
  useCache: true,
  modelParams: DEFAULT_MODEL_PARAMS,
  customEntityTypes: []
};

// Default entity types
const DEFAULT_ENTITY_TYPES = [
  'CODE_SNIPPET',
  'TECH_TERM',
  'DATE',
  'LOCATION',
  'PERSON',
  'EMAIL',
  'URL',
  'PHONE_NUMBER',
  'CUSTOM_ENTITY',
  'VERB_PHRASE'
];

export class OllamaService {
  private config: OllamaConfig;
  private abortController: AbortController | null = null;
  private cacheStats = { hits: 0, misses: 0 };

  constructor(config?: Partial<OllamaConfig>) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
      modelParams: { ...DEFAULT_MODEL_PARAMS, ...config?.modelParams }
    };
  }

  // Cancel any in-progress operations
  cancel(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
    }
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Retry wrapper with exponential backoff
  private async withRetry<T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= this.config.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error: any) {
        lastError = error;

        if (error.name === 'AbortError') {
          throw new Error('Operation cancelled');
        }

        if (attempt < this.config.maxRetries) {
          const delay = this.config.retryDelayMs * Math.pow(2, attempt - 1);
          console.warn(`${operationName} failed (attempt ${attempt}/${this.config.maxRetries}), retrying in ${delay}ms...`, error.message);
          await this.sleep(delay);
        }
      }
    }

    throw new Error(`${operationName} failed after ${this.config.maxRetries} attempts: ${lastError?.message}`);
  }

  // Streaming completion with progress
  private async generateCompletionStreaming(
    prompt: string,
    jsonMode: boolean = false,
    onChunk?: (chunk: string) => void,
    modelOverride?: string
  ): Promise<string> {
    this.abortController = new AbortController();
    const timeoutId = setTimeout(() => this.abortController?.abort(), this.config.timeoutMs);

    try {
      const response = await fetch(`${this.config.baseUrl}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: this.abortController.signal,
        body: JSON.stringify({
          model: modelOverride || this.config.model,
          prompt: prompt,
          stream: true,
          format: jsonMode ? 'json' : undefined,
          options: this.config.modelParams
        })
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      const decoder = new TextDecoder();
      let fullResponse = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.response) {
              fullResponse += data.response;
              onChunk?.(data.response);
            }
          } catch {
            // Ignore parse errors for incomplete chunks
          }
        }
      }

      return fullResponse;
    } finally {
      clearTimeout(timeoutId);
      this.abortController = null;
    }
  }

  // Non-streaming completion
  private async generateCompletion(
    prompt: string,
    jsonMode: boolean = false,
    modelOverride?: string
  ): Promise<string> {
    return this.withRetry(async () => {
      this.abortController = new AbortController();
      const timeoutId = setTimeout(() => this.abortController?.abort(), this.config.timeoutMs);

      try {
        const response = await fetch(`${this.config.baseUrl}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          signal: this.abortController.signal,
          body: JSON.stringify({
            model: modelOverride || this.config.model,
            prompt: prompt,
            stream: false,
            format: jsonMode ? 'json' : undefined,
            options: this.config.modelParams
          })
        });

        if (!response.ok) {
          throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        return data.response;
      } finally {
        clearTimeout(timeoutId);
        this.abortController = null;
      }
    }, 'generateCompletion');
  }

  // Generate embedding with cache support
  private async generateEmbedding(text: string): Promise<number[]> {
    // Check cache first
    if (this.config.useCache) {
      const cached = await embeddingCache.get(text, this.config.embeddingModel);
      if (cached) {
        this.cacheStats.hits++;
        return cached;
      }
      this.cacheStats.misses++;
    }

    try {
      const embedding = await this.withRetry(async () => {
        this.abortController = new AbortController();
        const timeoutId = setTimeout(() => this.abortController?.abort(), 30000);

        try {
          const response = await fetch(`${this.config.baseUrl}/api/embeddings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            signal: this.abortController.signal,
            body: JSON.stringify({
              model: this.config.embeddingModel,
              prompt: text
            })
          });

          if (!response.ok) {
            throw new Error(`Embedding API error: ${response.status}`);
          }

          const data = await response.json();
          return data.embedding || [];
        } finally {
          clearTimeout(timeoutId);
          this.abortController = null;
        }
      }, 'generateEmbedding');

      // Cache the result
      if (this.config.useCache && embedding.length > 0) {
        await embeddingCache.set(text, this.config.embeddingModel, embedding);
      }

      return embedding;
    } catch (e) {
      console.warn('Embedding service unavailable:', e);
      return [];
    }
  }

  // Batch processing for embeddings (parallel)
  async generateEmbeddingsBatch(texts: string[], concurrency: number = 3): Promise<number[][]> {
    const results: number[][] = new Array(texts.length).fill([]);
    const queue = texts.map((text, index) => ({ text, index }));

    const workers = Array(Math.min(concurrency, texts.length)).fill(null).map(async () => {
      while (queue.length > 0) {
        const item = queue.shift();
        if (!item) break;

        try {
          results[item.index] = await this.generateEmbedding(item.text);
        } catch (e) {
          console.warn(`Embedding failed for item ${item.index}:`, e);
          results[item.index] = [];
        }
      }
    });

    await Promise.all(workers);
    return results;
  }

  // Chunk large conversations into manageable pieces
  chunkConversation(turns: Turn[], maxTurnsPerChunk: number = 20): Turn[][] {
    const chunks: Turn[][] = [];
    for (let i = 0; i < turns.length; i += maxTurnsPerChunk) {
      chunks.push(turns.slice(i, i + maxTurnsPerChunk));
    }
    return chunks;
  }

  // 1. Structure Analysis: Groups turns into topics (with chunking for large conversations)
  async segmentIntoTopics(
    turns: Turn[],
    conversationId: string,
    onProgress?: ProgressCallback
  ): Promise<TopicSegment[]> {
    onProgress?.({
      stage: 'topics',
      currentItem: 0,
      totalItems: 1,
      currentLabel: 'Analyzing conversation structure...',
      percentage: 0
    });

    // If few turns, just make one topic
    if (turns.length <= 2) {
      const topicId = generateId();
      turns.forEach(t => t.parentId = topicId);
      return [{
        id: topicId,
        title: "General Discussion",
        summary: "Short conversation",
        turns: turns,
        parentId: conversationId,
        turnCount: turns.length,
        sentiment: 'neutral',
        keywords: ['discussion', 'general']
      }];
    }

    // For very large conversations, chunk and process
    if (turns.length > 50) {
      onProgress?.({
        stage: 'topics',
        currentItem: 0,
        totalItems: 1,
        currentLabel: `Large conversation (${turns.length} turns), chunking...`,
        percentage: 5
      });

      const chunks = this.chunkConversation(turns, 25);
      const allTopics: TopicSegment[] = [];
      let globalTurnOffset = 0;

      for (let chunkIdx = 0; chunkIdx < chunks.length; chunkIdx++) {
        const chunk = chunks[chunkIdx];
        const chunkTopics = await this.segmentSingleChunk(chunk, conversationId, globalTurnOffset);
        allTopics.push(...chunkTopics);
        globalTurnOffset += chunk.length;

        onProgress?.({
          stage: 'topics',
          currentItem: chunkIdx + 1,
          totalItems: chunks.length,
          currentLabel: `Processed chunk ${chunkIdx + 1}/${chunks.length}`,
          percentage: Math.round(((chunkIdx + 1) / chunks.length) * 100)
        });
      }

      return allTopics;
    }

    return this.segmentSingleChunk(turns, conversationId, 0, onProgress);
  }

  private async segmentSingleChunk(
    turns: Turn[],
    conversationId: string,
    turnOffset: number = 0,
    onProgress?: ProgressCallback
  ): Promise<TopicSegment[]> {
    const turnsText = turns.map((t, i) =>
      `Turn ${i + turnOffset}: ${t.messages.map(m => `${m.role}: ${m.content.substring(0, 150)}...`).join(' | ')}`
    ).join('\n');

    const prompt = `You are analyzing a conversation for topic segmentation.

Analyze these ${turns.length} turns and group them into logical Topic Segments.

Return ONLY valid JSON array with this exact structure:
[
  {
    "title": "descriptive title",
    "summary": "concise 1-2 sentence summary",
    "start_index": 0,
    "end_index": 2,
    "sentiment": "positive" | "neutral" | "negative",
    "keywords": ["keyword1", "keyword2", "keyword3"]
  }
]

Rules:
- start_index and end_index are inclusive turn indices (0-based, relative to this chunk)
- Ensure all turns are covered (no gaps, no overlaps)
- Each topic should have 3-5 keywords
- Keep summaries under 50 words

CONVERSATION TURNS:
${turnsText}

JSON RESPONSE:`;

    try {
      let responseText = '';

      responseText = await this.generateCompletionStreaming(prompt, true, (chunk) => {
        onProgress?.({
          stage: 'topics',
          currentItem: 0,
          totalItems: 1,
          currentLabel: `Segmenting topics... (${responseText.length} chars)`,
          percentage: Math.min(90, responseText.length / 50)
        });
      });

      let segmentData;
      try {
        segmentData = JSON.parse(responseText);
      } catch {
        const match = responseText.match(/\[[\s\S]*\]/);
        if (match) {
          segmentData = JSON.parse(match[0]);
        } else {
          throw new Error('No valid JSON found in response');
        }
      }

      if (!Array.isArray(segmentData) || segmentData.length === 0) {
        throw new Error('Invalid response structure');
      }

      const topics: TopicSegment[] = [];

      segmentData.forEach((seg: any) => {
        const topicId = generateId();
        const startIdx = Math.max(0, seg.start_index || 0);
        const endIdx = Math.min(turns.length - 1, seg.end_index || turns.length - 1);
        const topicTurns = turns.slice(startIdx, endIdx + 1);

        topicTurns.forEach(t => t.parentId = topicId);

        topics.push({
          id: topicId,
          title: seg.title || 'Untitled Topic',
          summary: seg.summary || 'No summary available',
          turns: topicTurns,
          parentId: conversationId,
          turnCount: topicTurns.length,
          sentiment: (seg.sentiment || 'neutral') as 'positive' | 'neutral' | 'negative',
          keywords: Array.isArray(seg.keywords) ? seg.keywords : ['conversation']
        });
      });

      onProgress?.({
        stage: 'topics',
        currentItem: 1,
        totalItems: 1,
        currentLabel: `Created ${topics.length} topic segments`,
        percentage: 100
      });

      if (topics.length === 0) throw new Error("No topics parsed");
      return topics;

    } catch (e: any) {
      if (e.message === 'Operation cancelled') throw e;

      console.warn("Topic segmentation failed, falling back to single topic", e);
      const topicId = generateId();
      turns.forEach(t => t.parentId = topicId);
      return [{
        id: topicId,
        title: "Full Conversation",
        summary: "Entire conversation log",
        turns: turns,
        parentId: conversationId,
        turnCount: turns.length,
        sentiment: 'neutral',
        keywords: ['conversation']
      }];
    }
  }

  // Generate topic embeddings with cache
  async generateTopicEmbeddings(
    topics: TopicSegment[],
    onProgress?: ProgressCallback
  ): Promise<TopicSegment[]> {
    if (topics.length === 0) return topics;

    onProgress?.({
      stage: 'embeddings',
      currentItem: 0,
      totalItems: topics.length,
      currentLabel: 'Generating topic embeddings...',
      percentage: 0
    });

    const texts = topics.map(topic =>
      `${topic.title}: ${topic.summary} ${topic.keywords?.join(' ') || ''}`
    );

    const embeddings = await this.generateEmbeddingsBatch(texts, 3);

    const results = topics.map((topic, i) => {
      onProgress?.({
        stage: 'embeddings',
        currentItem: i + 1,
        totalItems: topics.length,
        currentLabel: `Embedded: ${topic.title.substring(0, 30)}...`,
        percentage: Math.round(((i + 1) / topics.length) * 100)
      });

      return {
        ...topic,
        embedding: embeddings[i].length > 0 ? embeddings[i] : undefined
      };
    });

    return results;
  }

  // Regenerate Topic Summary
  async refineTopicSummary(turns: Turn[]): Promise<string> {
    const context = turns.map(t =>
      t.messages.map(m => `${m.role}: ${m.content}`).join('\n')
    ).join('\n---\n');

    const prompt = `Provide a concise, high-quality summary (maximum 2 sentences) for this conversation segment. Focus on the main topic and key outcome.

CONVERSATION:
${context}

SUMMARY:`;

    try {
      const response = await this.generateCompletion(prompt, false);
      return response.trim() || "Summary unavailable.";
    } catch (error: any) {
      if (error.message === 'Operation cancelled') throw error;
      console.error("Summary generation failed", error);
      return "Error generating summary.";
    }
  }

  // Get all entity types (default + custom)
  private getAllEntityTypes(): string[] {
    return [...DEFAULT_ENTITY_TYPES, ...this.config.customEntityTypes];
  }

  // Parse message content with custom entity support
  async parseMessageContent(
    messageId: string,
    text: string,
    onProgress?: (chunk: string) => void
  ): Promise<Sentence[]> {
    if (!text || text.trim().length === 0) return [];

    const entityTypes = this.getAllEntityTypes();
    const nerModel = this.config.nerModel || this.config.model;

    const prompt = `Analyze this text and return ONLY valid JSON.

Extract:
1. Sentences (treat code blocks as single atomic units)
2. Words/tokens for each sentence
3. Named entities/spans with labels

Span types to identify:
${entityTypes.map(t => `- ${t}`).join('\n')}

Return this exact JSON structure:
[
  {
    "text": "The full sentence text.",
    "words": ["The", "full", "sentence", "text"],
    "spans": [
      {"text": "entity text", "label": "SPAN_TYPE"}
    ]
  }
]

TEXT TO PARSE:
${text}

JSON RESPONSE:`;

    try {
      const responseText = await this.generateCompletionStreaming(prompt, true, onProgress, nerModel);

      let parsedData;
      try {
        parsedData = JSON.parse(responseText);
      } catch {
        const match = responseText.match(/\[[\s\S]*\]/);
        if (match) {
          parsedData = JSON.parse(match[0]);
        } else {
          throw new Error('No valid JSON found');
        }
      }

      if (!Array.isArray(parsedData)) {
        throw new Error('Response is not an array');
      }

      return parsedData.map((s: any) => {
        const sentenceId = generateId();

        const words: Word[] = (s.words || s.text?.split(/\s+/) || []).map((w: string) => ({
          id: generateId(),
          text: typeof w === 'string' ? w : String(w),
          parentId: sentenceId,
          type: 'word' as const
        }));

        const spans: Span[] = (s.spans || []).map((sp: any) => ({
          id: generateId(),
          text: sp.text || '',
          label: sp.label || 'UNKNOWN',
          parentId: sentenceId,
          type: 'span' as const
        }));

        return {
          id: sentenceId,
          text: s.text || '',
          words: words,
          spans: spans,
          parentId: messageId,
          wordCount: words.length,
          spanCount: spans.length
        };
      });

    } catch (error: any) {
      if (error.message === 'Operation cancelled') throw error;

      console.error("Error parsing message content:", error);
      const sentenceId = generateId();
      const words = text.split(/\s+/).map(w => ({
        id: generateId(),
        text: w,
        parentId: sentenceId,
        type: 'word' as const
      }));
      return [{
        id: sentenceId,
        text: text,
        words: words,
        spans: [],
        parentId: messageId,
        wordCount: words.length,
        spanCount: 0
      }];
    }
  }

  // Batch process messages
  async parseMessagesBatch(
    messages: Array<{ id: string; content: string }>,
    concurrency: number = 2,
    onProgress?: (current: number, total: number, label: string) => void
  ): Promise<Map<string, Sentence[]>> {
    const results = new Map<string, Sentence[]>();
    const queue = [...messages];
    let completed = 0;

    const workers = Array(Math.min(concurrency, messages.length)).fill(null).map(async () => {
      while (queue.length > 0) {
        const item = queue.shift();
        if (!item) break;

        try {
          const sentences = await this.parseMessageContent(item.id, item.content);
          results.set(item.id, sentences);
        } catch (e: any) {
          if (e.message === 'Operation cancelled') throw e;
          console.warn(`Failed to parse message ${item.id}:`, e);
          results.set(item.id, []);
        }

        completed++;
        onProgress?.(completed, messages.length, `Message ${completed}/${messages.length}`);
      }
    });

    await Promise.all(workers);
    return results;
  }

  // Health check with GPU info
  async checkConnection(): Promise<{ connected: boolean; models: string[]; gpu?: GpuInfo }> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.config.baseUrl}/api/tags`, {
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        return { connected: false, models: [] };
      }

      const data = await response.json();
      const models = data.models?.map((m: any) => m.name) || [];

      // Try to get GPU info
      let gpu: GpuInfo | undefined;
      try {
        const gpuResponse = await fetch(`${this.config.baseUrl}/api/ps`, {
          signal: AbortSignal.timeout(3000)
        });
        if (gpuResponse.ok) {
          const gpuData = await gpuResponse.json();
          if (gpuData.models && gpuData.models.length > 0) {
            const runningModel = gpuData.models[0];
            gpu = {
              available: true,
              name: runningModel.name,
              vramTotal: runningModel.size,
              vramUsed: runningModel.size_vram
            };
          }
        }
      } catch {
        // GPU info is optional
      }

      return { connected: true, models, gpu };
    } catch {
      return { connected: false, models: [] };
    }
  }

  // Get cache statistics
  getCacheStats(): { hits: number; misses: number; hitRate: number } {
    const total = this.cacheStats.hits + this.cacheStats.misses;
    return {
      ...this.cacheStats,
      hitRate: total > 0 ? this.cacheStats.hits / total : 0
    };
  }

  // Clear cache statistics
  resetCacheStats(): void {
    this.cacheStats = { hits: 0, misses: 0 };
  }

  getConfig(): OllamaConfig {
    return { ...this.config };
  }

  setModel(model: string): void {
    this.config.model = model;
  }

  setNerModel(model: string): void {
    this.config.nerModel = model;
  }

  setEmbeddingModel(model: string): void {
    this.config.embeddingModel = model;
  }

  setModelParams(params: Partial<ModelParameters>): void {
    this.config.modelParams = { ...this.config.modelParams, ...params };
  }

  setCustomEntityTypes(types: string[]): void {
    this.config.customEntityTypes = types;
  }

  addCustomEntityType(type: string): void {
    if (!this.config.customEntityTypes.includes(type)) {
      this.config.customEntityTypes.push(type);
    }
  }

  setUseCache(useCache: boolean): void {
    this.config.useCache = useCache;
  }

  setBaseUrl(url: string): void {
    this.config.baseUrl = url;
    localStorage.setItem('neurolinguist_ollama_host', url);
  }
}

export { DEFAULT_ENTITY_TYPES, DEFAULT_MODEL_PARAMS };
