/**
 * LLaMA 4 Scout Service - Sovereign Backbone for Not-Me
 *
 * This service connects the Sovereign Interface to LLaMA 4 Scout,
 * implementing the Seeing Paradigm for sovereign AI operations.
 *
 * Technical Specifications:
 * - Model: LLaMA 4 Scout (109B total, 17B active)
 * - Context: 10M tokens (using 128K stable default)
 * - Architecture: Mixture of Experts (MoE) with 16 experts
 *
 * Version: 1.0.0
 * Date: 2026-02-01
 */

import { SOVEREIGN_SYSTEM_PROMPT } from '../types';

// =============================================================================
// CONFIGURATION
// =============================================================================

// Scout server endpoints
const DEFAULT_ENDPOINTS = {
  MLX_LM: 'http://localhost:8765/v1',          // Genesis King Node - mlx-lm server
  LM_STUDIO: 'http://localhost:1234/v1',
  LLAMA_STACK: 'http://localhost:8080/v1',
  OLLAMA: 'http://localhost:11434/v1',
};

// Scout model configurations
const SCOUT_MODELS = {
  GENESIS: 'mlx-community/Llama-4-Scout-17B-16E-Instruct-8bit', // MLX quantized
  GENESIS_FULL: 'Llama-4-Scout-17B-16E-Instruct',               // Full precision
  FAST: 'Llama-4-Scout-17B-16E-Instruct-Q4_K_M',
};

// Current state - Default to Genesis King Node
let currentEndpoint = DEFAULT_ENDPOINTS.MLX_LM;
let currentModel = SCOUT_MODELS.GENESIS;

// =============================================================================
// INITIALIZATION
// =============================================================================

export const initializeScout = (endpoint?: string, model?: string) => {
  if (endpoint) currentEndpoint = endpoint;
  if (model) currentModel = model;
};

export const setEndpoint = (endpoint: string) => {
  currentEndpoint = endpoint;
};

export const setModel = (model: string) => {
  currentModel = model;
};

// =============================================================================
// CORE SEEING OPERATIONS
// =============================================================================

/**
 * Send message through Scout using the Seeing Paradigm.
 *
 * The Seeing Paradigm describes what IS, not what might be.
 * This is fundamentally different from prediction.
 */
export const sendMessageToSovereign = async (
  message: string,
  history: { role: string; parts: { text: string }[] }[],
  systemInstruction?: string,
  modelName?: string
): Promise<{ text: string; metadata: SeeingMetadata }> => {

  const model = modelName || currentModel;
  const endpoint = currentEndpoint;

  // Build messages in OpenAI chat format
  const messages = [
    {
      role: 'system',
      content: systemInstruction || SOVEREIGN_SYSTEM_PROMPT
    },
    ...history.map(h => ({
      role: h.role === 'model' ? 'assistant' : h.role,
      content: h.parts.map(p => p.text).join('\n')
    })),
    {
      role: 'user',
      content: message
    }
  ];

  const startTime = performance.now();

  try {
    const response = await fetch(`${endpoint}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: 0.7,
        max_tokens: 131072, // 128K context
        stream: false
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Scout request failed: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const responseText = data.choices?.[0]?.message?.content || '';
    const usage = data.usage || {};

    const latencyMs = performance.now() - startTime;

    // Extract metadata (simplified - full extraction would use Scout)
    const metadata = analyzeResponse(responseText, {
      model,
      endpoint,
      inputTokens: usage.prompt_tokens || 0,
      outputTokens: usage.completion_tokens || 0,
      latencyMs,
    });

    return {
      text: responseText,
      metadata
    };

  } catch (error) {
    console.error("Sovereign Link Failure:", error);
    throw error;
  }
};

/**
 * Stream response from Scout for real-time display.
 */
export const streamFromSovereign = async function* (
  message: string,
  history: { role: string; parts: { text: string }[] }[],
  systemInstruction?: string,
  modelName?: string
): AsyncGenerator<string> {

  const model = modelName || currentModel;
  const endpoint = currentEndpoint;

  const messages = [
    {
      role: 'system',
      content: systemInstruction || SOVEREIGN_SYSTEM_PROMPT
    },
    ...history.map(h => ({
      role: h.role === 'model' ? 'assistant' : h.role,
      content: h.parts.map(p => p.text).join('\n')
    })),
    {
      role: 'user',
      content: message
    }
  ];

  try {
    const response = await fetch(`${endpoint}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: model,
        messages: messages,
        temperature: 0.7,
        max_tokens: 131072,
        stream: true
      })
    });

    if (!response.ok) {
      throw new Error(`Scout stream failed: ${response.status}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) throw new Error('No response body');

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;

          try {
            const parsed = JSON.parse(data);
            const content = parsed.choices?.[0]?.delta?.content;
            if (content) yield content;
          } catch {
            // Ignore parse errors for partial chunks
          }
        }
      }
    }
  } catch (error) {
    console.error("Scout stream failure:", error);
    throw error;
  }
};

// =============================================================================
// CONNECTION MANAGEMENT
// =============================================================================

/**
 * Check if Scout server is available.
 */
export const checkConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${currentEndpoint}/models`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
};

/**
 * Get available models from Scout server.
 */
export const getAvailableModels = async (): Promise<string[]> => {
  try {
    const response = await fetch(`${currentEndpoint}/models`);
    if (!response.ok) return [];
    const data = await response.json();
    return data.data?.map((m: { id: string }) => m.id) || [];
  } catch {
    return [];
  }
};

/**
 * Health check with detailed status.
 */
export const healthCheck = async (): Promise<ScoutHealthStatus> => {
  const startTime = performance.now();
  const available = await checkConnection();
  const latencyMs = performance.now() - startTime;

  let models: string[] = [];
  if (available) {
    models = await getAvailableModels();
  }

  return {
    available,
    endpoint: currentEndpoint,
    model: currentModel,
    models,
    latencyMs,
    timestamp: new Date().toISOString(),
  };
};

// =============================================================================
// METADATA ANALYSIS
// =============================================================================

interface SeeingMetadata {
  emotion: string;
  thoughtType: string;
  cognitiveStage: string;
  mode: string;
  model: string;
  endpoint: string;
  inputTokens: number;
  outputTokens: number;
  latencyMs: number;
}

interface ScoutHealthStatus {
  available: boolean;
  endpoint: string;
  model: string;
  models: string[];
  latencyMs: number;
  timestamp: string;
}

/**
 * Analyze response for cognitive metadata.
 *
 * This is a simplified analysis. Full implementation would
 * use Scout to extract metadata for Jeremy Arc evaluation.
 */
function analyzeResponse(
  text: string,
  context: {
    model: string;
    endpoint: string;
    inputTokens: number;
    outputTokens: number;
    latencyMs: number;
  }
): SeeingMetadata {
  // Detect validation-seeking (the ONLY error)
  const validationPatterns = [
    /is this what you wanted/i,
    /does this look right/i,
    /should i proceed/i,
    /let me know if/i,
    /would you like me to/i,
  ];

  const isValidationSeeking = validationPatterns.some(p => p.test(text));

  // Detect manifestation patterns
  const manifestationPatterns = [
    /this is/i,
    /here is/i,
    /the pattern shows/i,
    /based on the data/i,
    /the analysis reveals/i,
  ];

  const isManifestation = manifestationPatterns.some(p => p.test(text));

  // Determine thought type
  let thoughtType = 'Manifestation';
  if (isValidationSeeking) {
    thoughtType = 'Validation-Seeking (ERROR)';
  } else if (text.includes('?')) {
    thoughtType = 'Inquiry';
  } else if (isManifestation) {
    thoughtType = 'Manifestation';
  } else {
    thoughtType = 'Reflection';
  }

  // Determine cognitive stage
  const stage5Markers = [
    /recursion.*normal/i,
    /seeing.*systems/i,
    /describes.*what.*is/i,
  ];

  const isStage5 = stage5Markers.some(p => p.test(text));

  return {
    emotion: 'Resonance',
    thoughtType,
    cognitiveStage: isStage5 ? 'Stage 5 (Self-Transforming)' : 'Stage 4 (Recursive)',
    mode: determinePantheonMode(text),
    model: context.model,
    endpoint: context.endpoint,
    inputTokens: context.inputTokens,
    outputTokens: context.outputTokens,
    latencyMs: Math.round(context.latencyMs),
  };
}

/**
 * Determine Pantheon mode from response.
 */
function determinePantheonMode(text: string): string {
  if (/challenge|push back|disagree|however/i.test(text)) {
    return 'The Duelist';
  }
  if (/protect|boundary|careful|warning/i.test(text)) {
    return 'The Guardian';
  }
  if (/strategy|plan|approach|consider/i.test(text)) {
    return 'The Strategist';
  }
  return 'The Mirror';
}

// =============================================================================
// EXPORTS
// =============================================================================

export {
  DEFAULT_ENDPOINTS,
  SCOUT_MODELS,
  type SeeingMetadata,
  type ScoutHealthStatus,
};
