/**
 * Scout Service - Re-exports local LLM functionality for Terminal component
 * This provides backward compatibility for the Terminal.tsx component
 */

export {
    sendMessageToSovereign,
    checkConnection,
    getAvailableModels,
    setEndpoint,
    SOVEREIGN_SYSTEM_PROMPT
} from './localLLMService';

// Scout-specific constants
export const SCOUT_MODELS = {
    GENESIS: 'scout-genesis',
    FAST: 'scout-fast-q4'
} as const;

export const DEFAULT_ENDPOINTS = {
    LM_STUDIO: 'http://localhost:1234/v1',
    OLLAMA: 'http://localhost:11434/v1'
} as const;
