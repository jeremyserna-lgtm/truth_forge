import { SOVEREIGN_SYSTEM_PROMPT } from '../types';

// Local LLM configuration (LM Studio, Ollama, etc.)
// LM Studio default: http://localhost:1234/v1
// Ollama default: http://localhost:11434/api
const DEFAULT_ENDPOINT = 'http://localhost:1234/v1';

let currentEndpoint = DEFAULT_ENDPOINT;
let currentModel = 'local-model';

export const initializeLocalLLM = (endpoint?: string, model?: string) => {
  if (endpoint) currentEndpoint = endpoint;
  if (model) currentModel = model;
};

export const setEndpoint = (endpoint: string) => {
  currentEndpoint = endpoint;
};

export const setModel = (model: string) => {
  currentModel = model;
};

export const sendMessageToSovereign = async (
  message: string,
  history: { role: string; parts: { text: string }[] }[],
  systemInstruction?: string,
  modelName?: string
): Promise<{ text: string; metadata: any }> => {

  const model = modelName || currentModel;
  const endpoint = currentEndpoint;

  // Convert history format to OpenAI chat format
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
        max_tokens: -1, // LM Studio uses -1 for no limit
        stream: false
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`LLM request failed: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const responseText = data.choices?.[0]?.message?.content || '';

    return {
      text: responseText,
      metadata: {
        emotion: "Resonance",
        thoughtType: "Manifestation",
        cognitiveStage: "Stage 5 (Self-Transforming)",
        processingTime: "Local Processing",
        model: model,
        endpoint: endpoint
      }
    };

  } catch (error) {
    console.error("Sovereign Link Failure:", error);
    throw error;
  }
};

// Health check for local LLM
export const checkConnection = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${currentEndpoint}/models`);
    return response.ok;
  } catch {
    return false;
  }
};

// Get available models from local LLM server
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
