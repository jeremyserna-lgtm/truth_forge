/**
 * Model & Provider Types
 * Configuration and status for LLM providers and context window management
 */

// ============================================================================
// PROVIDER AND MODEL TYPES
// ============================================================================

/**
 * LLM provider identifier
 */
export type ModelProvider = 'openai' | 'anthropic' | 'google' | 'local' | 'custom';

/**
 * Model identifier (provider:model_name)
 */
export type ModelId =
  | 'openai:gpt-4-turbo'
  | 'openai:gpt-4o'
  | 'anthropic:claude-opus-4'
  | 'anthropic:claude-3.5-sonnet'
  | 'google:gemini-pro'
  | 'local:llama2'
  | string;

/**
 * Configuration for a specific model
 */
export interface ModelConfig {
  id: ModelId;
  provider: ModelProvider;
  displayName: string;
  description?: string;
  contextWindowTokens: number;
  maxOutputTokens?: number;
  costPer1KInputTokens: number;
  costPer1KOutputTokens: number;
  temperature?: number;
  topP?: number;
  topK?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  capabilities: {
    chat: boolean;
    completion: boolean;
    embedding: boolean;
    vision: boolean;
    functionCalling: boolean;
    jsonMode?: boolean;
  };
  rateLimitPerMinute?: number;
  deprecated?: boolean;
  eol?: string; // End of life date
}

// ============================================================================
// CONTEXT WINDOW MANAGEMENT
// ============================================================================

/**
 * State of context window usage
 */
export interface ContextWindowState {
  model: ModelId;
  totalTokens: number;
  usedTokens: number;
  remainingTokens: number;
  percentUsed: number; // 0-100
  resetAt?: number;
}

/**
 * Provider-level status
 */
export interface ProviderStatus {
  provider: ModelProvider;
  available: boolean;
  lastChecked: number;
  responseTimeMs?: number;
  errorRate?: number; // 0-1
  rateLimitStatus?: {
    requestsThisMinute: number;
    limitPerMinute: number;
    resetAt: number;
  };
}

/**
 * Token usage tracking for cost calculation
 */
export interface TokenUsage {
  model: ModelId;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  estimatedCost: number;
  timestamp: number;
}

/**
 * Session-level token tracking
 */
export interface SessionTokenMetrics {
  sessionId: string;
  model: ModelId;
  startTime: number;
  usage: TokenUsage[];
  totalInputTokens: number;
  totalOutputTokens: number;
  totalCost: number;
  endTime?: number;
}

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Parse model ID to extract provider and model name
 */
export function parseModelId(modelId: ModelId): {
  provider: ModelProvider;
  modelName: string;
} {
  const [provider, ...rest] = modelId.split(':');
  return {
    provider: provider as ModelProvider,
    modelName: rest.join(':'),
  };
}

/**
 * Calculate estimated cost for token usage
 */
export function estimateCost(
  config: ModelConfig,
  inputTokens: number,
  outputTokens: number
): number {
  const inputCost = (inputTokens / 1000) * config.costPer1KInputTokens;
  const outputCost = (outputTokens / 1000) * config.costPer1KOutputTokens;
  return inputCost + outputCost;
}

/**
 * Get remaining context tokens
 */
export function getContextRemaining(
  config: ModelConfig,
  currentUsage: number
): number {
  return Math.max(0, config.contextWindowTokens - currentUsage);
}
