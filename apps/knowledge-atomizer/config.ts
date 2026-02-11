/**
 * Knowledge Atomizer Configuration
 * 
 * All configurable values in one place. Override via environment variables where supported.
 */

import type { ModelId } from './types';

// --- APP DEFAULTS ---
export const APP_CONFIG = {
    /** Application name */
    name: 'Knowledge Atomizer',
    /** Version */
    version: '1.0.0',
} as const;

// --- MODEL CONFIGURATION ---
export const MODEL_CONFIG = {
    /** Default model for general operations */
    defaultModel: 'gemini-2.5-flash' as ModelId,
    /** Model for synthesis operations (Pro tier) */
    synthesisModel: 'gemini-2.5-pro' as ModelId,
    /** Model for embeddings */
    embeddingModel: 'text-embedding-004',
    /** Default Ollama endpoint */
    ollamaEndpoint: 'http://localhost:11434',
} as const;

// --- FILE HANDLING ---
export const FILE_CONFIG = {
    /** Supported file extensions for upload */
    acceptedFileTypes: [
        '.txt', '.md', '.json', '.csv',
        '.js', '.ts', '.jsx', '.tsx',
        '.py', '.go', '.rs', '.sh',
        '.yaml', '.yml', '.toml',
        '.xml', '.html', '.css', '.sql',
        '.zip'
    ],
    /** Accept string for file input elements */
    get acceptString(): string {
        return this.acceptedFileTypes.join(',');
    },
    /** Max file size in bytes (10MB) */
    maxFileSize: 10 * 1024 * 1024,
} as const;

// --- TOKEN LIMITS ---
export const TOKEN_CONFIG = {
    /** Characters per token approximation */
    charsPerToken: 4,
    /** Max tokens for context window display */
    maxContextDisplay: 100000,
    /** Token limits by model */
    modelLimits: {
        'gemini-2.5-pro': 1000000,
        'gemini-2.5-flash': 1000000,
        'gemini-2.5-flash-lite': 1000000,
        'llama4-scout': 128000,
        'llama3.2': 128000,
        'mistral': 32000,
    } as Record<ModelId, number>,
} as const;

// --- UI CONFIGURATION ---
export const UI_CONFIG = {
    /** Max lines per function before ESLint warning (for reference) */
    maxFunctionLines: 200,
    /** Animation durations (ms) */
    animations: {
        fast: 150,
        normal: 300,
        slow: 500,
    },
    /** Debounce delays (ms) */
    debounce: {
        search: 300,
        save: 1000,
    },
} as const;

// --- CERTAINTY & STAKES COLORS ---
export const CERTAINTY_COLORS: Record<string, string> = {
    fact: 'bg-emerald-900/30 text-emerald-400 border-emerald-700',
    consensus: 'bg-blue-900/30 text-blue-400 border-blue-700',
    claim: 'bg-yellow-900/30 text-yellow-400 border-yellow-700',
    speculation: 'bg-orange-900/30 text-orange-400 border-orange-700',
    hypothesis: 'bg-purple-900/30 text-purple-400 border-purple-700',
};

export const STAKES_COLORS: Record<string, string> = {
    existential: 'bg-red-900/30 text-red-400',
    high: 'bg-orange-900/30 text-orange-400',
    medium: 'bg-yellow-900/30 text-yellow-400',
    low: 'bg-slate-800 text-slate-400',
    trivial: 'bg-slate-900 text-slate-500',
};

// --- API CONFIGURATION ---
export const API_CONFIG = {
    /** Request timeout in ms */
    timeout: 60000,
    /** Max retries on failure */
    maxRetries: 3,
    /** Retry delay in ms */
    retryDelay: 1000,
} as const;

// --- SYNTHESIS CONFIGURATION ---
export const SYNTHESIS_CONFIG = {
    /** Available synthesis types */
    types: ['Comprehensive', 'Summary', 'Analysis', 'Comparison'] as const,
    /** Default synthesis type */
    defaultType: 'Comprehensive' as const,
} as const;

// --- STUDIO CONFIGURATION ---
export const STUDIO_CONFIG = {
    /** Audio sample rate */
    audioSampleRate: 24000,
    /** Audio bit depth */
    audioBitDepth: 16,
    /** Audio channels */
    audioChannels: 1,
} as const;

// --- DEVELOPMENT ---
export const DEV_CONFIG = {
    /** Enable verbose logging */
    verbose: import.meta.env.DEV,
    /** Log prefix for console statements */
    logPrefix: '[Atomizer]',
} as const;
