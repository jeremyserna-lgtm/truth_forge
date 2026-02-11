/**
 * Local Model Service for Llama Scout 4 and other local models
 *
 * Supports BOTH server types automatically:
 * - Ollama native API (/api/chat, /api/tags)
 * - OpenAI-compatible API (/v1/chat/completions, /v1/models) — mlx_lm.server, vLLM, etc.
 *
 * The service auto-detects which server is running and routes accordingly.
 */

import { ModelConfig, ModelId, ProviderStatus } from '../types';

// Default endpoint (both Ollama and mlx_lm.server default to this)
const DEFAULT_LOCAL_URL = 'http://localhost:11434';

// Get the local model server URL
const getLocalUrl = (): string => {
  return (typeof import.meta !== 'undefined' && (import.meta as any).env?.VITE_OLLAMA_URL)
    || (typeof process !== 'undefined' && process.env?.OLLAMA_URL)
    || DEFAULT_LOCAL_URL;
};

// Server type detection — cached after first check
type ServerType = 'ollama' | 'openai-compat' | null;
let _detectedServerType: ServerType = null;
let _resolvedModelId: string | null = null;

/**
 * Ollama model configurations
 * Context limits queried dynamically at runtime
 */
export const OLLAMA_MODELS: ModelConfig[] = [
  {
    id: 'llama4-scout',
    provider: 'ollama',
    label: 'Llama 4 Scout',
    tokenLimit: 10_000_000,
    description: 'Local 109B MoE model with 10M token context. Full sovereignty.',
    strengths: ['Massive Context', 'Local Privacy', 'No API Costs', 'Stage 5 Ready'],
    supportsStructuredOutput: true,
    supportsEmbeddings: false,
  },
  {
    id: 'llama3.2',
    provider: 'ollama',
    label: 'Llama 3.2',
    tokenLimit: 128_000,
    description: 'Fast local inference for quick tasks.',
    strengths: ['Speed', 'Efficiency', 'Good for Chat'],
    supportsStructuredOutput: true,
    supportsEmbeddings: false,
  },
  {
    id: 'mistral',
    provider: 'ollama',
    label: 'Mistral',
    tokenLimit: 32_000,
    description: 'Efficient local model for general tasks.',
    strengths: ['Balanced', 'Fast', 'Reliable'],
    supportsStructuredOutput: true,
    supportsEmbeddings: false,
  },
];

/**
 * Detect which server type is running on the endpoint.
 * Tries Ollama native first, then OpenAI-compatible.
 */
const detectServerType = async (): Promise<{ type: ServerType; models: string[] }> => {
  const url = getLocalUrl();

  // Try Ollama native: GET /api/tags
  try {
    const response = await fetch(`${url}/api/tags`, {
      method: 'GET',
      signal: AbortSignal.timeout(3000),
    });
    if (response.ok) {
      const data = await response.json();
      const models = (data.models || []).map((m: { name: string }) => m.name);
      _detectedServerType = 'ollama';
      console.log('[LocalModel] Detected Ollama server with models:', models);
      return { type: 'ollama', models };
    }
  } catch {
    // Not Ollama, try OpenAI-compatible
  }

  // Try OpenAI-compatible: GET /v1/models
  try {
    const response = await fetch(`${url}/v1/models`, {
      method: 'GET',
      signal: AbortSignal.timeout(3000),
    });
    if (response.ok) {
      const data = await response.json();
      const models = (data.data || []).map((m: { id: string }) => m.id);
      _detectedServerType = 'openai-compat';
      // Cache the first model ID for use in requests
      if (models.length > 0) {
        _resolvedModelId = models[0];
      }
      console.log('[LocalModel] Detected OpenAI-compatible server with models:', models);
      return { type: 'openai-compat', models };
    }
  } catch {
    // Neither server is available
  }

  _detectedServerType = null;
  return { type: null, models: [] };
};

/**
 * Check if a local model server is running and get available models
 */
export const checkOllamaStatus = async (): Promise<ProviderStatus> => {
  const { type, models } = await detectServerType();

  if (type) {
    return {
      provider: 'ollama',
      available: true,
      models,
      lastChecked: Date.now(),
    };
  }

  return {
    provider: 'ollama',
    available: false,
    models: [],
    error: 'No local model server found (tried Ollama and OpenAI-compatible)',
    lastChecked: Date.now(),
  };
};

/**
 * Get the actual context window size for a model
 */
export const getModelContextLimit = async (modelName: string): Promise<number> => {
  const url = getLocalUrl();

  // Only Ollama native supports /api/show
  if (_detectedServerType === 'ollama') {
    try {
      const response = await fetch(`${url}/api/show`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: modelName }),
      });

      if (response.ok) {
        const data = await response.json();
        const contextLength =
          data.parameters?.num_ctx ||
          data.model_info?.context_length ||
          extractContextFromModelfile(data.modelfile);

        if (contextLength && typeof contextLength === 'number') {
          return contextLength;
        }
      }
    } catch {
      // Fall through to default
    }
  }

  return getDefaultContextLimit(modelName);
};

/**
 * Extract context length from modelfile string
 */
const extractContextFromModelfile = (modelfile?: string): number | null => {
  if (!modelfile) return null;
  const match = modelfile.match(/num_ctx\s+(\d+)/i);
  return match ? parseInt(match[1], 10) : null;
};

/**
 * Get default context limit for known models
 */
const getDefaultContextLimit = (modelName: string): number => {
  const n = modelName.toLowerCase();
  if (n.includes('llama4') || n.includes('llama-4') || n.includes('scout')) return 10_000_000;
  if (n.includes('llama3.2') || n.includes('llama-3.2')) return 128_000;
  if (n.includes('llama3.1') || n.includes('llama-3.1')) return 128_000;
  if (n.includes('mistral')) return 32_000;
  if (n.includes('mixtral')) return 32_000;
  if (n.includes('qwen')) return 32_000;
  return 8_192;
};

/**
 * Token estimation for local models
 */
export const estimateOllamaTokens = (text: string): number => {
  const words = text.split(/\s+/).filter(w => w.length > 0);
  const charBased = Math.ceil(text.length / 3.8);
  const wordBased = Math.ceil(words.length * 1.3);
  return Math.max(charBased, wordBased);
};

/**
 * Resolve the actual model name to send to the server.
 * Ollama expects "llama4:scout", mlx_lm.server returns its own model IDs.
 */
const resolveModelName = (modelId: ModelId): string => {
  // If we detected an OpenAI-compatible server, use its reported model ID
  if (_detectedServerType === 'openai-compat' && _resolvedModelId) {
    return _resolvedModelId;
  }

  // Ollama native model name mapping
  switch (modelId) {
    case 'llama4-scout': return 'llama4:scout';
    case 'llama3.2': return 'llama3.2:latest';
    case 'mistral': return 'mistral:latest';
    default: return modelId;
  }
};

/**
 * Strip markdown code fences from LLM output to get raw JSON.
 * Local models often wrap JSON in ```json ... ```.
 */
const extractJson = (text: string): string => {
  let s = text.trim();
  if (s.startsWith('```')) {
    const firstNewline = s.indexOf('\n');
    if (firstNewline === -1) return s;
    s = s.slice(firstNewline + 1);
    if (s.trimEnd().endsWith('```')) {
      s = s.trimEnd().slice(0, -3).trimEnd();
    }
  }
  return s;
};

/**
 * Chat completion — auto-routes between Ollama native and OpenAI-compatible API
 */
export const ollamaChat = async (
  modelId: ModelId,
  messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }>,
  options?: {
    temperature?: number;
    maxTokens?: number;
    jsonMode?: boolean;
  }
): Promise<{ text: string; tokensUsed?: number }> => {
  const url = getLocalUrl();
  const modelName = resolveModelName(modelId);

  // Auto-detect server type if not cached
  if (_detectedServerType === null) {
    await detectServerType();
  }

  if (_detectedServerType === 'openai-compat') {
    return ollamaChatOpenAI(url, modelName, messages, options);
  }

  // Default: Ollama native API
  return ollamaChatNative(url, modelName, messages, options);
};

/**
 * Chat via Ollama native API (/api/chat)
 */
const ollamaChatNative = async (
  url: string,
  modelName: string,
  messages: Array<{ role: string; content: string }>,
  options?: { temperature?: number; maxTokens?: number; jsonMode?: boolean }
): Promise<{ text: string; tokensUsed?: number }> => {
  const requestBody: Record<string, unknown> = {
    model: modelName,
    messages,
    stream: false,
    options: {
      temperature: options?.temperature ?? 0.7,
      num_predict: options?.maxTokens ?? 4096,
    },
  };

  if (options?.jsonMode) {
    requestBody.format = 'json';
  }

  const response = await fetch(`${url}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Ollama chat failed: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  return {
    text: data.message?.content || '',
    tokensUsed: data.eval_count || data.prompt_eval_count,
  };
};

/**
 * Chat via OpenAI-compatible API (/v1/chat/completions) — mlx_lm.server, vLLM, etc.
 */
const ollamaChatOpenAI = async (
  url: string,
  modelName: string,
  messages: Array<{ role: string; content: string }>,
  options?: { temperature?: number; maxTokens?: number; jsonMode?: boolean }
): Promise<{ text: string; tokensUsed?: number }> => {
  const requestBody: Record<string, unknown> = {
    model: modelName,
    messages,
    temperature: options?.temperature ?? 0.7,
    max_tokens: options?.maxTokens ?? 4096,
    stream: false,
  };

  if (options?.jsonMode) {
    requestBody.response_format = { type: 'json_object' };
  }

  const response = await fetch(`${url}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Local model chat failed: ${response.status} - ${errorText}`);
  }

  const data = await response.json();
  const choice = data.choices?.[0];
  const usage = data.usage;

  return {
    text: choice?.message?.content || '',
    tokensUsed: usage ? (usage.prompt_tokens + usage.completion_tokens) : undefined,
  };
};

/**
 * Generate completion (non-chat) — auto-routes between server types
 */
export const ollamaGenerate = async (
  modelId: ModelId,
  prompt: string,
  options?: {
    temperature?: number;
    maxTokens?: number;
    jsonMode?: boolean;
    systemPrompt?: string;
  }
): Promise<{ text: string; tokensUsed?: number }> => {
  const url = getLocalUrl();
  const modelName = resolveModelName(modelId);

  if (_detectedServerType === null) {
    await detectServerType();
  }

  // OpenAI-compatible servers don't have /api/generate — use chat instead
  if (_detectedServerType === 'openai-compat') {
    const messages: Array<{ role: 'system' | 'user' | 'assistant'; content: string }> = [];
    if (options?.systemPrompt) {
      messages.push({ role: 'system', content: options.systemPrompt });
    }
    messages.push({ role: 'user', content: prompt });
    return ollamaChatOpenAI(url, modelName, messages, options);
  }

  // Ollama native /api/generate
  const requestBody: Record<string, unknown> = {
    model: modelName,
    prompt,
    stream: false,
    options: {
      temperature: options?.temperature ?? 0.7,
      num_predict: options?.maxTokens ?? 4096,
    },
  };

  if (options?.systemPrompt) {
    requestBody.system = options.systemPrompt;
  }

  if (options?.jsonMode) {
    requestBody.format = 'json';
  }

  const response = await fetch(`${url}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Ollama generate failed: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  return {
    text: data.response || '',
    tokensUsed: data.eval_count,
  };
};

/**
 * Map our ModelId to Ollama model name (kept for backward compat)
 */
const getOllamaModelName = (modelId: ModelId): string => {
  return resolveModelName(modelId);
};

/**
 * Pull/download a model if not available (Ollama only)
 */
export const pullModel = async (
  modelName: string,
  onProgress?: (status: string, completed?: number, total?: number) => void
): Promise<boolean> => {
  // Only works with Ollama native
  if (_detectedServerType === 'openai-compat') {
    console.warn('Model pull not supported on OpenAI-compatible servers (mlx_lm.server)');
    return false;
  }

  const url = getLocalUrl();

  try {
    const response = await fetch(`${url}/api/pull`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: modelName, stream: true }),
    });

    if (!response.ok) {
      throw new Error(`Pull failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) return false;

    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value);
      const lines = text.split('\n').filter(l => l.trim());

      for (const line of lines) {
        try {
          const data = JSON.parse(line);
          if (onProgress) {
            onProgress(data.status, data.completed, data.total);
          }
        } catch {
          // Ignore JSON parse errors for partial lines
        }
      }
    }

    return true;
  } catch (error) {
    console.error('Model pull failed:', error);
    return false;
  }
};

// Export the JSON extraction utility for use by other services
export { extractJson };
