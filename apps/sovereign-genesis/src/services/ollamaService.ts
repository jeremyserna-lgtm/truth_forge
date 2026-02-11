/**
 * Ollama Service for Llama Scout 4 and other local models
 *
 * This service provides a unified interface to Ollama-hosted models,
 * including real-time context window measurement.
 */

import { ModelConfig, ModelId, ProviderStatus } from '../types';

// Default Ollama endpoint
const DEFAULT_OLLAMA_URL = 'http://localhost:11434';

// Get the Ollama base URL from env or use default
const getOllamaUrl = (): string => {
  return (typeof process !== 'undefined' && process.env?.OLLAMA_URL) || DEFAULT_OLLAMA_URL;
};

/**
 * Ollama model configurations
 * Context limits queried dynamically at runtime
 */
export const OLLAMA_MODELS: ModelConfig[] = [
  {
    id: 'llama4-scout',
    provider: 'ollama',
    label: 'Llama 4 Scout',
    tokenLimit: 10_000_000,  // 10M context - queried dynamically
    description: 'Local 109B MoE model with 10M token context. Full sovereignty.',
    strengths: ['Massive Context', 'Local Privacy', 'No API Costs', 'Stage 5 Ready'],
    supportsStructuredOutput: true,
    supportsEmbeddings: false,  // Use separate embedding model
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
 * Check if Ollama is running and get available models
 */
export const checkOllamaStatus = async (): Promise<ProviderStatus> => {
  const url = getOllamaUrl();

  try {
    const response = await fetch(`${url}/api/tags`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    if (!response.ok) {
      return {
        provider: 'ollama',
        available: false,
        models: [],
        error: `Ollama returned ${response.status}`,
        lastChecked: Date.now(),
      };
    }

    const data = await response.json();
    const models = (data.models || []).map((m: { name: string }) => m.name);

    return {
      provider: 'ollama',
      available: true,
      models,
      lastChecked: Date.now(),
    };
  } catch (error) {
    return {
      provider: 'ollama',
      available: false,
      models: [],
      error: error instanceof Error ? error.message : 'Connection failed',
      lastChecked: Date.now(),
    };
  }
};

/**
 * Get the actual context window size for a model from Ollama
 * This queries the model's metadata to get the true context limit
 */
export const getModelContextLimit = async (modelName: string): Promise<number> => {
  const url = getOllamaUrl();

  try {
    const response = await fetch(`${url}/api/show`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: modelName }),
    });

    if (!response.ok) {
      console.warn(`Could not get model info for ${modelName}`);
      return getDefaultContextLimit(modelName);
    }

    const data = await response.json();

    // Ollama returns context length in parameters or modelfile
    // Try multiple locations where context_length might be
    const contextLength =
      data.parameters?.num_ctx ||
      data.model_info?.context_length ||
      data.details?.parameter_size?.includes('ctx') ||
      extractContextFromModelfile(data.modelfile);

    if (contextLength && typeof contextLength === 'number') {
      return contextLength;
    }

    return getDefaultContextLimit(modelName);
  } catch (error) {
    console.warn(`Error getting context limit for ${modelName}:`, error);
    return getDefaultContextLimit(modelName);
  }
};

/**
 * Extract context length from modelfile string
 */
const extractContextFromModelfile = (modelfile?: string): number | null => {
  if (!modelfile) return null;

  // Look for num_ctx parameter
  const match = modelfile.match(/num_ctx\s+(\d+)/i);
  if (match) {
    return parseInt(match[1], 10);
  }

  return null;
};

/**
 * Get default context limit for known models
 */
const getDefaultContextLimit = (modelName: string): number => {
  const normalizedName = modelName.toLowerCase();

  if (normalizedName.includes('llama4') || normalizedName.includes('llama-4')) {
    return 10_000_000;  // Llama 4 Scout: 10M
  }
  if (normalizedName.includes('llama3.2') || normalizedName.includes('llama-3.2')) {
    return 128_000;
  }
  if (normalizedName.includes('llama3.1') || normalizedName.includes('llama-3.1')) {
    return 128_000;
  }
  if (normalizedName.includes('mistral')) {
    return 32_000;
  }
  if (normalizedName.includes('mixtral')) {
    return 32_000;
  }
  if (normalizedName.includes('qwen')) {
    return 32_000;
  }

  // Default fallback
  return 8_192;
};

/**
 * Token estimation for Ollama models
 * More accurate than simple char/4 for Llama tokenizers
 */
export const estimateOllamaTokens = (text: string): number => {
  // Llama tokenizers average ~3.5-4 chars per token for English
  // But handle whitespace and special chars differently
  const words = text.split(/\s+/).filter(w => w.length > 0);
  const _avgCharsPerWord = text.length / Math.max(words.length, 1);

  // Llama tokenizers: roughly 1 token per 4 chars, but words often get own token
  // Use weighted average
  const charBasedEstimate = Math.ceil(text.length / 3.8);
  const wordBasedEstimate = Math.ceil(words.length * 1.3);

  // Return the higher estimate for safety
  return Math.max(charBasedEstimate, wordBasedEstimate);
};

/**
 * Chat completion with Ollama
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
  const url = getOllamaUrl();
  const modelName = getOllamaModelName(modelId);

  const requestBody: Record<string, unknown> = {
    model: modelName,
    messages,
    stream: false,
    options: {
      temperature: options?.temperature ?? 0.7,
      num_predict: options?.maxTokens ?? 4096,
    },
  };

  // Enable JSON mode if requested
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
 * Generate completion (non-chat) with Ollama
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
  const url = getOllamaUrl();
  const modelName = getOllamaModelName(modelId);

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
 * Map our ModelId to Ollama model name
 */
const getOllamaModelName = (modelId: ModelId): string => {
  switch (modelId) {
    case 'llama4-scout':
      return 'llama4:scout';  // Matches actual Ollama tag
    case 'llama3.2':
      return 'llama3.2:latest';
    case 'mistral':
      return 'mistral:latest';
    default:
      return modelId;
  }
};

/**
 * Pull/download a model if not available
 */
export const pullModel = async (
  modelName: string,
  onProgress?: (status: string, completed?: number, total?: number) => void
): Promise<boolean> => {
  const url = getOllamaUrl();

  try {
    const response = await fetch(`${url}/api/pull`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: modelName, stream: true }),
    });

    if (!response.ok) {
      throw new Error(`Pull failed: ${response.status}`);
    }

    // Stream the response for progress updates
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
