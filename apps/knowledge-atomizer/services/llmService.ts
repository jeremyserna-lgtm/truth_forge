/**
 * Unified LLM Service
 *
 * Provides a single interface for all LLM operations across providers (Gemini, Ollama).
 * Handles provider selection, context window tracking, and graceful fallbacks.
 */

import {
  ModelConfig,
  ModelId,
  ModelProvider,
  ContextWindowState,
  ProviderStatus,
  KnowledgeAtom,
} from '../types';
import { MODELS as GEMINI_MODELS, estimateTokens as estimateGeminiTokens } from './geminiService';
import {
  OLLAMA_MODELS,
  checkOllamaStatus,
  getModelContextLimit,
  estimateOllamaTokens,
  ollamaChat,
  ollamaGenerate,
} from './ollamaService';

// ============================================================================
// MODEL REGISTRY - Single source of truth for all models
// ============================================================================

/**
 * All available models across all providers
 * This is the SINGLE source of truth for model configuration
 */
export const ALL_MODELS: ModelConfig[] = [
  // Gemini models with provider field added
  ...GEMINI_MODELS.map(m => ({ ...m, provider: 'gemini' as ModelProvider })),
  // Ollama models
  ...OLLAMA_MODELS,
];

/**
 * Get model config by ID
 */
export const getModelConfig = (modelId: ModelId): ModelConfig | undefined => {
  return ALL_MODELS.find(m => m.id === modelId);
};

/**
 * Get all models for a specific provider
 */
export const getModelsForProvider = (provider: ModelProvider): ModelConfig[] => {
  return ALL_MODELS.filter(m => m.provider === provider);
};

/**
 * Get provider for a model ID
 */
export const getProviderForModel = (modelId: ModelId): ModelProvider => {
  const model = getModelConfig(modelId);
  return model?.provider || 'gemini';
};

// ============================================================================
// TOKEN COUNTING - Unified token estimation
// ============================================================================

/**
 * Estimate tokens for text based on the target model's provider
 */
export const estimateTokens = (text: string, modelId?: ModelId): number => {
  if (!modelId) {
    // Default to more conservative estimate
    return Math.ceil(text.length / 3.5);
  }

  const provider = getProviderForModel(modelId);

  switch (provider) {
    case 'ollama':
      return estimateOllamaTokens(text);
    case 'gemini':
    default:
      return estimateGeminiTokens(text);
  }
};

/**
 * Serialize a KnowledgeAtom to its full string representation
 * This is what actually gets sent to the LLM, so we must count ALL of it
 */
export const serializeAtomForTokenCounting = (atom: KnowledgeAtom): string => {
  // Build the full serialized representation that matches what we send to the API
  const parts: string[] = [
    `Content: ${atom.content}`,
    `Source: ${atom.sourceFile}`,
  ];

  if (atom.metadata) {
    const m = atom.metadata;

    // Legacy fields
    if (m.theme) parts.push(`Theme: ${m.theme}`);
    if (m.significance) parts.push(`Significance: ${m.significance}`);
    if (m.tags?.length) parts.push(`Tags: ${m.tags.join(', ')}`);

    // Semantic dimension
    if (m.semantic) {
      parts.push(`Domain: ${m.semantic.domain}`);
      parts.push(`Abstraction: ${m.semantic.abstraction_level}`);
    }

    // Significance dimension
    if (m.significance_analysis) {
      parts.push(`Tier: ${m.significance_analysis.tier}`);
      parts.push(`Novelty: ${m.significance_analysis.novelty}`);
      parts.push(`Actionability: ${m.significance_analysis.actionability}`);
    }

    // Epistemic dimension
    if (m.epistemic) {
      parts.push(`Certainty: ${m.epistemic.certainty}`);
      parts.push(`Evidence Strength: ${m.epistemic.evidence_strength}`);
      parts.push(`Verifiability: ${m.epistemic.verifiability}`);
    }

    // Temporal dimension
    if (m.temporal) {
      parts.push(`Temporal Scope: ${m.temporal.scope}`);
      parts.push(`Durability: ${m.temporal.durability}`);
    }

    // Relational dimension
    if (m.relational) {
      if (m.relational.entities?.length) parts.push(`Entities: ${m.relational.entities.join(', ')}`);
      if (m.relational.concepts?.length) parts.push(`Concepts: ${m.relational.concepts.join(', ')}`);
      if (m.relational.dependencies?.length) parts.push(`Dependencies: ${m.relational.dependencies.join(', ')}`);
      if (m.relational.implications?.length) parts.push(`Implications: ${m.relational.implications.join(', ')}`);
    }

    // Dialectical dimension
    if (m.dialectical) {
      if (m.dialectical.supports?.length) parts.push(`Supports: ${m.dialectical.supports.join(', ')}`);
      if (m.dialectical.contradicts?.length) parts.push(`Contradicts: ${m.dialectical.contradicts.join(', ')}`);
      if (m.dialectical.tensions?.length) parts.push(`Tensions: ${m.dialectical.tensions.join(', ')}`);
      if (m.dialectical.synthesis_potential) parts.push(`Synthesis: ${m.dialectical.synthesis_potential}`);
    }

    // Affective dimension
    if (m.affective) {
      parts.push(`Sentiment: ${m.affective.sentiment}`);
      parts.push(`Intensity: ${m.affective.intensity}`);
      parts.push(`Stakes: ${m.affective.stakes}`);
      parts.push(`Urgency: ${m.affective.urgency}`);
    }

    // Pragmatic dimension
    if (m.pragmatic) {
      if (m.pragmatic.action_items?.length) parts.push(`Actions: ${m.pragmatic.action_items.join(', ')}`);
      if (m.pragmatic.preconditions?.length) parts.push(`Preconditions: ${m.pragmatic.preconditions.join(', ')}`);
      if (m.pragmatic.consequences?.length) parts.push(`Consequences: ${m.pragmatic.consequences.join(', ')}`);
      if (m.pragmatic.audience?.length) parts.push(`Audience: ${m.pragmatic.audience.join(', ')}`);
    }

    // Structural dimension
    if (m.structural) {
      parts.push(`Structure Type: ${m.structural.type}`);
      parts.push(`Complexity: ${m.structural.complexity}`);
      parts.push(`Completeness: ${m.structural.completeness}`);
    }

    // Ontological dimension
    if (m.ontological) {
      parts.push(`Entity Type: ${m.ontological.entity_type}`);
      if (m.ontological.categories?.length) parts.push(`Categories: ${m.ontological.categories.join(', ')}`);
      if (m.ontological.is_a?.length) parts.push(`Is-A: ${m.ontological.is_a.join(', ')}`);
      if (m.ontological.has_parts?.length) parts.push(`Has Parts: ${m.ontological.has_parts.join(', ')}`);
    }

    // Normative dimension
    if (m.normative) {
      parts.push(`Normative Type: ${m.normative.type}`);
      if (m.normative.values_invoked?.length) parts.push(`Values: ${m.normative.values_invoked.join(', ')}`);
      if (m.normative.should_statements?.length) parts.push(`Should: ${m.normative.should_statements.join(', ')}`);
    }
  }

  return parts.join('\n');
};

/**
 * Calculate detailed context window usage
 * Now properly counts FULL serialized atoms, not just content
 */
export const calculateContextUsage = (
  modelId: ModelId,
  components: {
    systemPrompt?: string;
    documents?: string[];
    atoms?: KnowledgeAtom[];
    chatHistory?: Array<{ role: string; text: string }>;
    currentMessage?: string;
  }
): ContextWindowState => {
  const model = getModelConfig(modelId);
  const tokenLimit = model?.tokenLimit || 128_000;

  const breakdown = {
    systemPrompt: components.systemPrompt ? estimateTokens(components.systemPrompt, modelId) : 0,
    documents: components.documents
      ? components.documents.reduce((sum, doc) => sum + estimateTokens(doc, modelId), 0)
      : 0,
    // FIXED: Count FULL serialized atom, not just content
    atoms: components.atoms
      ? components.atoms.reduce((sum, atom) => sum + estimateTokens(serializeAtomForTokenCounting(atom), modelId), 0)
      : 0,
    chatHistory: components.chatHistory
      ? components.chatHistory.reduce((sum, msg) => sum + estimateTokens(msg.text, modelId), 0)
      : 0,
    currentMessage: components.currentMessage
      ? estimateTokens(components.currentMessage, modelId)
      : 0,
  };

  const tokensUsed =
    breakdown.systemPrompt +
    breakdown.documents +
    breakdown.atoms +
    breakdown.chatHistory +
    breakdown.currentMessage;

  return {
    tokensUsed,
    tokenLimit,
    percentUsed: (tokensUsed / tokenLimit) * 100,
    modelId,
    breakdown,
  };
};

// ============================================================================
// PROVIDER STATUS - Health checking
// ============================================================================

/**
 * Check status of all providers
 */
export const checkAllProviders = async (): Promise<ProviderStatus[]> => {
  const results: ProviderStatus[] = [];

  // Gemini is always "available" if API key exists
  const hasGeminiKey = typeof process !== 'undefined' &&
    (process.env?.API_KEY || process.env?.GEMINI_API_KEY);

  results.push({
    provider: 'gemini',
    available: !!hasGeminiKey,
    models: hasGeminiKey ? GEMINI_MODELS.map(m => m.id) : [],
    error: hasGeminiKey ? undefined : 'API key not configured',
    lastChecked: Date.now(),
  });

  // Check Ollama
  const ollamaStatus = await checkOllamaStatus();
  results.push(ollamaStatus);

  return results;
};

/**
 * Check if a specific model is available
 */
export const isModelAvailable = async (modelId: ModelId): Promise<boolean> => {
  const model = getModelConfig(modelId);
  if (!model) return false;

  if (model.provider === 'gemini') {
    return !!(typeof process !== 'undefined' &&
      (process.env?.API_KEY || process.env?.GEMINI_API_KEY));
  }

  if (model.provider === 'ollama') {
    const status = await checkOllamaStatus();
    if (!status.available) return false;

    // Check if specific model is pulled
    // Handle llama4-scout -> llama4:scout mapping
    const normalizedModelId = modelId.toLowerCase().replace('-', ':');
    return status.models.some(m => {
      const normalizedOllamaModel = m.toLowerCase();
      return (
        normalizedOllamaModel === normalizedModelId ||
        normalizedOllamaModel.startsWith(normalizedModelId.split(':')[0]) ||
        normalizedModelId.includes(normalizedOllamaModel.split(':')[0])
      );
    });
  }

  return false;
};

// ============================================================================
// DYNAMIC CONTEXT LIMIT - Query actual limits at runtime
// ============================================================================

/**
 * Get the actual context limit for a model (queries Ollama for real limits)
 */
export const getActualContextLimit = async (modelId: ModelId): Promise<number> => {
  const model = getModelConfig(modelId);
  if (!model) return 8_192;

  if (model.provider === 'gemini') {
    // Gemini limits are static/known
    return model.tokenLimit;
  }

  if (model.provider === 'ollama') {
    // Query Ollama for the actual context limit
    try {
      return await getModelContextLimit(modelId);
    } catch {
      return model.tokenLimit;  // Fall back to configured limit
    }
  }

  return model.tokenLimit;
};

// ============================================================================
// UNIFIED CHAT INTERFACE
// ============================================================================

export interface ChatOptions {
  temperature?: number;
  maxTokens?: number;
  jsonMode?: boolean;
  systemPrompt?: string;
}

export interface ChatResponse {
  text: string;
  tokensUsed?: number;
  provider: ModelProvider;
  modelId: ModelId;
}

/**
 * Unified chat interface that routes to the correct provider
 */
export const chat = async (
  modelId: ModelId,
  messages: Array<{ role: 'user' | 'model' | 'system'; content: string }>,
  options?: ChatOptions
): Promise<ChatResponse> => {
  const provider = getProviderForModel(modelId);

  if (provider === 'ollama') {
    // Convert 'model' role to 'assistant' for Ollama
    const ollamaMessages = messages.map(m => ({
      role: m.role === 'model' ? 'assistant' as const : m.role,
      content: m.content,
    }));

    const result = await ollamaChat(modelId, ollamaMessages, options);

    return {
      text: result.text,
      tokensUsed: result.tokensUsed,
      provider: 'ollama',
      modelId,
    };
  }

  // For Gemini, we need to use the existing geminiService
  // This will be called through the existing chatWithContext function
  throw new Error('Use chatWithContext from geminiService for Gemini models');
};

/**
 * Unified generate interface (non-chat completion)
 */
export const generate = async (
  modelId: ModelId,
  prompt: string,
  options?: ChatOptions
): Promise<ChatResponse> => {
  const provider = getProviderForModel(modelId);

  if (provider === 'ollama') {
    const result = await ollamaGenerate(modelId, prompt, options);

    return {
      text: result.text,
      tokensUsed: result.tokensUsed,
      provider: 'ollama',
      modelId,
    };
  }

  // For Gemini, this would go through the existing service
  throw new Error('Use geminiService directly for Gemini generation');
};

// ============================================================================
// CONTEXT WINDOW UTILITIES
// ============================================================================

/**
 * Format context window state for display
 */
export const formatContextUsage = (state: ContextWindowState): string => {
  const usedK = Math.round(state.tokensUsed / 1000);
  const limitK = Math.round(state.tokenLimit / 1000);
  const limitM = state.tokenLimit >= 1_000_000 ? `${(state.tokenLimit / 1_000_000).toFixed(1)}M` : `${limitK}K`;

  return `${usedK}K / ${limitM} (${state.percentUsed.toFixed(1)}%)`;
};

/**
 * Get context window health status
 */
export const getContextHealth = (state: ContextWindowState): 'healthy' | 'warning' | 'critical' => {
  if (state.percentUsed >= 90) return 'critical';
  if (state.percentUsed >= 70) return 'warning';
  return 'healthy';
};

/**
 * Calculate how many more tokens can be added
 */
export const getRemainingTokens = (state: ContextWindowState): number => {
  return Math.max(0, state.tokenLimit - state.tokensUsed);
};

/**
 * Check if content fits within remaining context
 */
export const contentFitsInContext = (
  content: string,
  state: ContextWindowState,
  modelId?: ModelId
): boolean => {
  const contentTokens = estimateTokens(content, modelId || state.modelId);
  return contentTokens <= getRemainingTokens(state);
};
