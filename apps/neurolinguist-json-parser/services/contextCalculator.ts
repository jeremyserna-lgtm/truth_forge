/**
 * Context Window Calculator
 *
 * Calculates maximum available context window based on:
 * - System RAM
 * - Model size
 * - KV cache requirements per token
 *
 * Formula: Max tokens = (Available RAM - Model Size) / KV cache per token
 */

export interface ModelConfig {
  name: string;
  sizeGB: number;
  hiddenSize: number;
  numLayers: number;
  numKvHeads: number;
  headDim: number;
  theoreticalMaxContext: number;
}

export interface ContextMetrics {
  // System
  totalRamGB: number;
  availableRamGB: number;
  usedRamGB: number;

  // Model
  modelSizeGB: number;
  modelName: string;

  // Context calculations
  kvCachePerTokenBytes: number;
  maxContextTokens: number;
  theoreticalMaxTokens: number;
  effectiveMaxTokens: number;

  // Current usage
  currentTokens: number;
  remainingTokens: number;
  usagePercent: number;
}

// Known model configurations
export const MODEL_CONFIGS: Record<string, ModelConfig> = {
  'llama4:scout': {
    name: 'Llama 4 Scout',
    sizeGB: 67,
    hiddenSize: 5120,
    numLayers: 48,
    numKvHeads: 8,
    headDim: 128,
    theoreticalMaxContext: 10_000_000,
  },
  'llama4-scout-8bit': {
    name: 'Llama 4 Scout 8-bit',
    sizeGB: 108,
    hiddenSize: 5120,
    numLayers: 48,
    numKvHeads: 8,
    headDim: 128,
    theoreticalMaxContext: 10_000_000,
  },
  'llama3.2:latest': {
    name: 'Llama 3.2',
    sizeGB: 2,
    hiddenSize: 2048,
    numLayers: 16,
    numKvHeads: 8,
    headDim: 64,
    theoreticalMaxContext: 128_000,
  },
  'qwen2.5-coder:32b': {
    name: 'Qwen 2.5 Coder 32B',
    sizeGB: 19,
    hiddenSize: 5120,
    numLayers: 64,
    numKvHeads: 8,
    headDim: 128,
    theoreticalMaxContext: 131_072,
  },
  // Default fallback for unknown models
  'default': {
    name: 'Unknown Model',
    sizeGB: 8,
    hiddenSize: 4096,
    numLayers: 32,
    numKvHeads: 8,
    headDim: 128,
    theoreticalMaxContext: 128_000,
  },
};

/**
 * Calculate KV cache bytes per token
 */
export function calculateKvCachePerToken(config: ModelConfig): number {
  // KV cache per token = 2 (K+V) * numLayers * numKvHeads * headDim * 2 (fp16 bytes)
  return 2 * config.numLayers * config.numKvHeads * config.headDim * 2;
}

/**
 * Get system RAM (returns 720GB as default for Jeremy's setup,
 * or attempts to detect via navigator if available)
 */
export async function getSystemRamGB(): Promise<number> {
  // Check localStorage for override
  const override = localStorage.getItem('neurolinguist_system_ram_gb');
  if (override) {
    return parseFloat(override);
  }

  // Try to detect (limited in browser)
  // @ts-ignore - deviceMemory is not in all browsers
  if (navigator.deviceMemory) {
    // deviceMemory returns a rough value, multiply by some factor for Apple Silicon
    // This is imprecise - better to let user set it
    // @ts-ignore
    const detected = navigator.deviceMemory;
    // For Apple Silicon unified memory, this is very underestimated
    // Return a more reasonable default
    return 720; // Jeremy's known config
  }

  // Default to Jeremy's setup
  return 720;
}

/**
 * Calculate context metrics for a given model
 */
export async function calculateContextMetrics(
  modelName: string,
  currentTokens: number = 0
): Promise<ContextMetrics> {
  const totalRamGB = await getSystemRamGB();

  // Get model config (use default if unknown)
  const config = MODEL_CONFIGS[modelName] || MODEL_CONFIGS['default'];

  const kvCachePerTokenBytes = calculateKvCachePerToken(config);
  const modelSizeBytes = config.sizeGB * 1024 * 1024 * 1024;
  const availableBytes = (totalRamGB * 1024 * 1024 * 1024) - modelSizeBytes;

  // Calculate max context based on available memory
  const maxContextTokens = Math.floor(availableBytes / kvCachePerTokenBytes);

  // Effective max is the minimum of hardware limit and model's theoretical max
  const effectiveMaxTokens = Math.min(maxContextTokens, config.theoreticalMaxContext);

  const remainingTokens = effectiveMaxTokens - currentTokens;
  const usagePercent = (currentTokens / effectiveMaxTokens) * 100;

  return {
    totalRamGB,
    availableRamGB: totalRamGB - config.sizeGB,
    usedRamGB: config.sizeGB + (currentTokens * kvCachePerTokenBytes / (1024 * 1024 * 1024)),

    modelSizeGB: config.sizeGB,
    modelName: config.name,

    kvCachePerTokenBytes,
    maxContextTokens,
    theoreticalMaxTokens: config.theoreticalMaxContext,
    effectiveMaxTokens,

    currentTokens,
    remainingTokens,
    usagePercent: Math.min(usagePercent, 100),
  };
}

/**
 * Estimate token count from text (rough approximation)
 * ~4 characters per token for English
 */
export function estimateTokens(text: string): number {
  return Math.ceil(text.length / 4);
}

/**
 * Format token count for display
 */
export function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) {
    return `${(tokens / 1_000_000).toFixed(2)}M`;
  } else if (tokens >= 1_000) {
    return `${(tokens / 1_000).toFixed(1)}K`;
  }
  return tokens.toString();
}

/**
 * Get color based on usage percentage
 */
export function getUsageColor(percent: number): string {
  if (percent < 50) return '#22c55e'; // green
  if (percent < 75) return '#eab308'; // yellow
  if (percent < 90) return '#f97316'; // orange
  return '#ef4444'; // red
}
