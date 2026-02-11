/**
 * conversationService.ts — Claude Code Session JSONL Reader
 *
 * Reads Claude Code session files (.jsonl) and structures them
 * for atomization. This is the bridge between raw conversation
 * data and the Knowledge Atom extraction pipeline.
 *
 * Replaces the traditional Python NLP pipeline with LLM-native processing.
 * The LLM IS the transformation engine.
 */

// ============================================================
// TYPES
// ============================================================

export interface SessionRecord {
  type: 'user' | 'assistant' | 'queue-operation';
  sessionId: string;
  uuid?: string;
  parentUuid?: string | null;
  timestamp: string;
  isSidechain?: boolean;
  userType?: string;
  cwd?: string;
  version?: string;
  gitBranch?: string;
  permissionMode?: string;
  requestId?: string;
  isApiErrorMessage?: boolean;
  slug?: string;
  isMeta?: boolean;
  agentId?: string;
  message?: UserMessage | AssistantMessage;
  operation?: string;
}

export interface UserMessage {
  role: 'user';
  content: string;
}

export interface AssistantMessage {
  role: 'assistant';
  model?: string;
  id?: string;
  type?: string;
  content: ContentBlock[];
  stop_reason?: string | null;
  usage?: TokenUsageInfo;
}

export interface ContentBlock {
  type: 'text' | 'thinking' | 'tool_use' | 'tool_result';
  text?: string;
  thinking?: string;
  signature?: string;
  id?: string;
  name?: string;
  input?: Record<string, unknown>;
  content?: unknown;
}

export interface TokenUsageInfo {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
  service_tier?: string;
}

export interface ParsedConversation {
  sessionId: string;
  sourceFile: string;
  sourceFilePath: string;
  project: string;
  model: string;
  version: string;
  cwd: string;
  gitBranch: string;
  startTime: string;
  endTime: string;
  exchanges: ConversationExchange[];
  totalUserMessages: number;
  totalAssistantMessages: number;
  totalTokensUsed: number;
  toolsUsed: string[];
  hasSubagents: boolean;
}

export interface ConversationExchange {
  index: number;
  userMessage: string;
  assistantText: string;
  assistantThinking: string;
  toolsUsed: ToolUseRecord[];
  timestamp: string;
  model: string;
  tokensUsed: number;
}

export interface ToolUseRecord {
  name: string;
  input: Record<string, unknown>;
}

export interface SessionIndex {
  sessions: SessionIndexEntry[];
}

export interface SessionIndexEntry {
  sessionId: string;
  createdAt: string;
  lastUpdatedAt: string;
  summary?: string;
  projectPath?: string;
}

// ============================================================
// PARSING
// ============================================================

/**
 * Parse a single JSONL file into structured conversation data.
 * Each line is a JSON record of type user, assistant, or queue-operation.
 */
export function parseSessionJSONL(
  content: string,
  filename: string,
  filePath: string
): ParsedConversation {
  const lines = content.trim().split('\n').filter(line => line.trim());
  const records: SessionRecord[] = [];

  for (const line of lines) {
    try {
      const record = JSON.parse(line) as SessionRecord;
      records.push(record);
    } catch {
      // Skip malformed lines — Fail-Safe pillar: log and continue
      console.warn(`Skipping malformed JSONL line in ${filename}`);
    }
  }

  // Extract metadata from first meaningful record
  const firstRecord = records.find(r => r.type === 'user' || r.type === 'assistant');
  const sessionId = firstRecord?.sessionId || 'unknown';
  const version = firstRecord?.version || 'unknown';
  const cwd = firstRecord?.cwd || 'unknown';
  const gitBranch = firstRecord?.gitBranch || 'unknown';

  // Derive project name from the file path
  const project = deriveProjectName(filePath);

  // Build conversation thread
  const exchanges = buildExchanges(records);

  // Collect metadata
  const timestamps = records
    .filter(r => r.timestamp)
    .map(r => r.timestamp)
    .sort();

  const models = new Set<string>();
  const toolNames = new Set<string>();
  let totalTokens = 0;

  for (const record of records) {
    if (record.type === 'assistant' && record.message) {
      const msg = record.message as AssistantMessage;
      if (msg.model) models.add(msg.model);
      if (msg.usage) {
        totalTokens += (msg.usage.input_tokens || 0) + (msg.usage.output_tokens || 0);
      }
      if (msg.content && Array.isArray(msg.content)) {
        for (const block of msg.content) {
          if (block.type === 'tool_use' && block.name) {
            toolNames.add(block.name);
          }
        }
      }
    }
  }

  const hasSubagents = records.some(r => r.agentId != null);

  return {
    sessionId,
    sourceFile: filename,
    sourceFilePath: filePath,
    project,
    model: Array.from(models).join(', ') || 'unknown',
    version,
    cwd,
    gitBranch,
    startTime: timestamps[0] || '',
    endTime: timestamps[timestamps.length - 1] || '',
    exchanges,
    totalUserMessages: records.filter(r => r.type === 'user').length,
    totalAssistantMessages: records.filter(r => r.type === 'assistant').length,
    totalTokensUsed: totalTokens,
    toolsUsed: Array.from(toolNames),
    hasSubagents,
  };
}

/**
 * Build user-assistant exchange pairs from the record stream.
 * Follows parentUuid chains to reconstruct conversation order.
 */
function buildExchanges(records: SessionRecord[]): ConversationExchange[] {
  const exchanges: ConversationExchange[] = [];
  const messageRecords = records.filter(r => r.type === 'user' || r.type === 'assistant');

  let currentUser: SessionRecord | null = null;
  let exchangeIndex = 0;

  for (const record of messageRecords) {
    if (record.type === 'user') {
      currentUser = record;
    } else if (record.type === 'assistant' && currentUser) {
      const msg = record.message as AssistantMessage;
      const contentBlocks = msg?.content || [];

      // Extract text from content blocks
      const textParts = contentBlocks
        .filter((b): b is ContentBlock & { text: string } => b.type === 'text' && !!b.text)
        .map(b => b.text);

      const thinkingParts = contentBlocks
        .filter((b): b is ContentBlock & { thinking: string } => b.type === 'thinking' && !!b.thinking)
        .map(b => b.thinking);

      const tools = contentBlocks
        .filter((b): b is ContentBlock & { name: string; input: Record<string, unknown> } =>
          b.type === 'tool_use' && !!b.name)
        .map(b => ({ name: b.name, input: b.input || {} }));

      const userContent = typeof (currentUser.message as UserMessage)?.content === 'string'
        ? (currentUser.message as UserMessage).content
        : JSON.stringify((currentUser.message as UserMessage)?.content || '');

      exchanges.push({
        index: exchangeIndex++,
        userMessage: userContent,
        assistantText: textParts.join('\n\n'),
        assistantThinking: thinkingParts.join('\n\n'),
        toolsUsed: tools,
        timestamp: record.timestamp,
        model: msg?.model || 'unknown',
        tokensUsed: (msg?.usage?.input_tokens || 0) + (msg?.usage?.output_tokens || 0),
      });

      currentUser = null;
    }
  }

  return exchanges;
}

/**
 * Derive a human-readable project name from the file path.
 * Claude Code stores sessions in directories named after the working directory.
 */
function deriveProjectName(filePath: string): string {
  // Path format: .claude/projects/-Users-jeremyserna-Truth-Engine/session.jsonl
  const parts = filePath.split('/');
  const projectDirIndex = parts.findIndex(p => p === 'projects');
  if (projectDirIndex >= 0 && projectDirIndex + 1 < parts.length) {
    const slug = parts[projectDirIndex + 1];
    // Convert -Users-jeremyserna-Truth-Engine → Truth Engine
    const segments = slug.split('-').filter(Boolean);
    // Remove common prefixes (Users, jeremyserna)
    const meaningful = segments.filter(s =>
      !['Users', 'jeremyserna', 'sessions', 'eloquent', 'focused', 'goldberg'].includes(s)
    );
    return meaningful.join(' ') || slug;
  }
  return 'Unknown Project';
}

// ============================================================
// ATOMIZATION PROMPT GENERATION
// ============================================================

/**
 * Generate the prompt that tells the LLM how to atomize a conversation.
 * This is where the atom-forge skill intelligence lives.
 */
export function buildAtomizationPrompt(conversation: ParsedConversation): string {
  // Build a readable conversation transcript
  const transcript = conversation.exchanges
    .map(ex => {
      let text = `[Exchange ${ex.index + 1} — ${ex.timestamp}]\n`;
      text += `HUMAN: ${ex.userMessage}\n`;
      if (ex.toolsUsed.length > 0) {
        text += `TOOLS USED: ${ex.toolsUsed.map(t => t.name).join(', ')}\n`;
      }
      text += `ASSISTANT: ${ex.assistantText.substring(0, 2000)}`;
      if (ex.assistantText.length > 2000) text += '\n[...truncated...]';
      return text;
    })
    .join('\n\n---\n\n');

  return `You are a Knowledge Atom extractor. Read this conversation and extract every meaningful piece of knowledge as individual atoms.

## CONVERSATION CONTEXT
- Project: ${conversation.project}
- Model: ${conversation.model}
- Working Directory: ${conversation.cwd}
- Duration: ${conversation.startTime} to ${conversation.endTime}
- Messages: ${conversation.totalUserMessages} user, ${conversation.totalAssistantMessages} assistant
- Tools Used: ${conversation.toolsUsed.join(', ') || 'none'}

## CONVERSATION TRANSCRIPT
${transcript}

## EXTRACTION INSTRUCTIONS

For EACH meaningful unit of knowledge in this conversation, produce a JSON object:

\`\`\`json
{
  "content": "The knowledge statement — one irreducible fact, decision, insight, or observation",
  "category": "fact|decision|problem|solution|pattern|emotion|insight|action|context",
  "metadata": {
    "semantic": { "theme": "...", "domain": "...", "abstraction_level": "concrete|conceptual|abstract|meta" },
    "significance_analysis": { "tier": "Foundational|Structural|Insight|Nuance|Detail", "novelty": 0.0-1.0, "actionability": 0.0-1.0 },
    "epistemic": { "certainty": "fact|consensus|claim|speculation|hypothesis", "evidence_strength": 0.0-1.0, "verifiability": "observable|testable|logical|intuitive" },
    "temporal": { "scope": "universal|historical|current|emerging|future", "durability": "permanent|durable|transient|ephemeral" },
    "relational": { "entities": [], "concepts": [], "dependencies": [], "implications": [] },
    "affective": { "sentiment": -1.0 to 1.0, "intensity": 0.0-1.0, "stakes": "existential|high|medium|low|trivial", "urgency": 0.0-1.0 },
    "pragmatic": { "action_items": [], "preconditions": [], "consequences": [], "audience": [] },
    "structural": { "type": "claim|definition|comparison|causation|sequence|classification", "complexity": "atomic|compound|nested", "completeness": 0.0-1.0 }
  }
}
\`\`\`

## RULES
1. Each atom is ONE irreducible knowledge unit — don't combine multiple facts
2. Fill metadata dimensions that are meaningful; skip dimensions that don't apply
3. Focus on KNOWLEDGE that would be lost if this conversation disappeared
4. Skip boilerplate, tool schemas, and repeated instructions
5. Extract from BOTH human and assistant messages
6. Capture emotions and frustrations — these are knowledge too
7. Note decisions with their rationale
8. Note problems WITH their solutions (as separate atoms that reference each other)

Return a JSON array of atom objects. No commentary outside the JSON.`;
}

// ============================================================
// BATCH PROCESSING
// ============================================================

export interface BatchProgress {
  totalSessions: number;
  processedSessions: number;
  totalAtomsExtracted: number;
  duplicatesCaught: number;
  currentSession: string;
  errors: string[];
  estimatedCost: number;
}

/**
 * Read a sessions-index.json file and return the index.
 */
export function parseSessionIndex(content: string): SessionIndex {
  try {
    const data = JSON.parse(content);
    // Handle both array format and object-with-sessions format
    if (Array.isArray(data)) {
      return { sessions: data };
    }
    return data as SessionIndex;
  } catch {
    return { sessions: [] };
  }
}

/**
 * Estimate the token cost for processing a conversation.
 * Used for cost governance before batch processing.
 */
export function estimateProcessingCost(conversation: ParsedConversation): number {
  // Rough estimate: 4 chars per token
  const totalChars = conversation.exchanges.reduce((sum, ex) => {
    return sum + ex.userMessage.length + ex.assistantText.length;
  }, 0);
  const estimatedTokens = totalChars / 4;

  // Gemini 2.5 Flash pricing (approximate)
  const inputCostPerMToken = 0.15;  // $0.15 per million input tokens
  const outputCostPerMToken = 0.60;  // $0.60 per million output tokens

  // Assume output is ~20% of input (atoms are condensed knowledge)
  const inputCost = (estimatedTokens / 1_000_000) * inputCostPerMToken;
  const outputCost = (estimatedTokens * 0.2 / 1_000_000) * outputCostPerMToken;

  return inputCost + outputCost;
}

// ============================================================
// CONVERSATION-TO-DOCUMENT ADAPTER
// ============================================================

/**
 * Convert a parsed conversation into a document format that the existing
 * knowledge-atomizer distillToAtoms() function can process.
 *
 * This bridges the new conversation pathway into the existing pipeline.
 */
export function conversationToDocument(conversation: ParsedConversation): {
  name: string;
  content: string;
  metadata: Record<string, string>;
} {
  const content = conversation.exchanges
    .map(ex => {
      let text = `## Exchange ${ex.index + 1}\n\n`;
      text += `**Human**: ${ex.userMessage}\n\n`;
      if (ex.toolsUsed.length > 0) {
        text += `*Tools used: ${ex.toolsUsed.map(t => t.name).join(', ')}*\n\n`;
      }
      text += `**Assistant**: ${ex.assistantText}\n\n`;
      return text;
    })
    .join('---\n\n');

  return {
    name: `${conversation.project} — Session ${conversation.sessionId.substring(0, 8)}`,
    content,
    metadata: {
      sessionId: conversation.sessionId,
      project: conversation.project,
      model: conversation.model,
      cwd: conversation.cwd,
      startTime: conversation.startTime,
      endTime: conversation.endTime,
      source_system: 'claude_code',
      source_pipeline: 'atom_forge',
    },
  };
}
