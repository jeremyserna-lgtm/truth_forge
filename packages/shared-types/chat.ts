/**
 * Unified Chat Types
 * Consistent message and conversation formats across all apps
 */

// ============================================================================
// MESSAGE TYPES
// ============================================================================

/**
 * Role of the message sender
 */
export type ChatRole = 'user' | 'model' | 'assistant' | 'system';

/**
 * Chat message - unified format supporting both KA and DS conventions
 */
export interface ChatMessage {
  /** Role of the sender */
  role: ChatRole;

  /** Content of the message - supports both 'content' (DS) and 'text' (KA) */
  content?: string;
  text?: string; // Alternative field name for compatibility

  /** Optional message timestamp */
  timestamp?: number;

  /** Optional metadata about the message */
  metadata?: {
    model?: string;
    tokens?: number;
    confidence?: number;
    sources?: string[];
    [key: string]: unknown;
  };
}

/**
 * Helper to get message text regardless of field name
 */
export function getChatMessageText(message: ChatMessage): string {
  return message.content || message.text || '';
}

// ============================================================================
// CONVERSATION TYPES
// ============================================================================

/**
 * Conversation session - maintains context across multiple exchanges
 */
export interface ConversationSession {
  /** Unique conversation ID */
  id: string;

  /** Multi-tenant support */
  tenantId?: string;

  /** Reference to related document */
  documentId?: string;

  /** Title or summary of the conversation */
  title?: string;

  /** Messages in chronological order */
  messages: ChatMessage[];

  /** Conversation metadata */
  metadata?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
    systemPrompt?: string;
    [key: string]: unknown;
  };

  /** Timestamps */
  createdAt: number;
  updatedAt: number;
  closedAt?: number;

  /** Status of the conversation */
  status: 'active' | 'archived' | 'deleted';
}

// ============================================================================
// REQUEST/RESPONSE TYPES
// ============================================================================

/**
 * Request to send a chat message
 */
export interface ChatRequest {
  /** Conversation ID (optional - create new if not provided) */
  conversationId?: string;

  /** User message */
  message: string;

  /** Multi-tenant context */
  tenantId?: string;

  /** Optional document context */
  documentId?: string;

  /** Model parameters */
  model?: string;
  temperature?: number;
  maxTokens?: number;
  systemPrompt?: string;

  /** Optional metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Response from chat processing
 */
export interface ChatResponse {
  /** Conversation ID */
  conversationId: string;

  /** Messages (original + new response) */
  messages: ChatMessage[];

  /** The assistant's response */
  response: {
    text: string;
    role: 'assistant' | 'model';
    model?: string;
    tokens?: number;
    confidence?: number;
  };

  /** Processing metadata */
  metadata?: {
    processingTime: number;
    tokensUsed: number;
    costEstimate?: number;
    [key: string]: unknown;
  };

  /** Status */
  status: 'success' | 'error' | 'partial';
  error?: string;
}

/**
 * Type guard for ChatMessage
 */
export function isChatMessage(obj: unknown): obj is ChatMessage {
  if (typeof obj !== 'object' || obj === null) return false;
  const msg = obj as Record<string, unknown>;
  const roles: ChatRole[] = ['user', 'model', 'assistant', 'system'];
  return roles.includes(msg.role as ChatRole) && (msg.content !== undefined || msg.text !== undefined);
}

/**
 * Type guard for ConversationSession
 */
export function isConversationSession(obj: unknown): obj is ConversationSession {
  if (typeof obj !== 'object' || obj === null) return false;
  const session = obj as Record<string, unknown>;
  return (
    typeof session.id === 'string' &&
    Array.isArray(session.messages) &&
    typeof session.createdAt === 'number' &&
    typeof session.status === 'string'
  );
}
