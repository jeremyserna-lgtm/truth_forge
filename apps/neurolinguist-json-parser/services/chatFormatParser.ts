/**
 * Multi-Format Chat Parser
 * Supports importing conversations from Claude, ChatGPT, and Gemini exports
 */

export type ChatFormat = 'claude' | 'chatgpt' | 'gemini' | 'unknown';

export interface ParsedMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  model?: string;
}

export interface ParsedConversation {
  format: ChatFormat;
  title?: string;
  messages: ParsedMessage[];
  metadata: Record<string, unknown>;
}

/**
 * Detect the format of a chat export file
 */
export function detectFormat(content: string, filename: string): ChatFormat {
  const lowerFilename = filename.toLowerCase();

  // Check filename hints
  if (lowerFilename.includes('claude')) return 'claude';
  if (lowerFilename.includes('chatgpt') || lowerFilename.includes('openai')) return 'chatgpt';
  if (lowerFilename.includes('gemini') || lowerFilename.includes('bard')) return 'gemini';

  try {
    const data = JSON.parse(content);

    // Claude export format detection
    if (data.uuid && data.chat_messages && Array.isArray(data.chat_messages)) {
      return 'claude';
    }

    // Claude conversations.json array format
    if (Array.isArray(data) && data.length > 0 && data[0].uuid && data[0].chat_messages) {
      return 'claude';
    }

    // ChatGPT export format detection
    if (data.title && data.mapping && typeof data.mapping === 'object') {
      return 'chatgpt';
    }

    // ChatGPT conversations.json array format
    if (Array.isArray(data) && data.length > 0 && data[0].title && data[0].mapping) {
      return 'chatgpt';
    }

    // Gemini export format detection (typically has different structure)
    if (data.conversations && Array.isArray(data.conversations)) {
      return 'gemini';
    }

    // Check for Gemini's Takeout format
    if (Array.isArray(data) && data.length > 0 && data[0].textContent) {
      return 'gemini';
    }

  } catch {
    // Not valid JSON, might be text format
  }

  // Check for markdown/text patterns
  if (content.includes('## Human') || content.includes('## Assistant')) {
    return 'claude';
  }
  if (content.includes('**ChatGPT:**') || content.includes('**User:**')) {
    return 'chatgpt';
  }

  return 'unknown';
}

/**
 * Parse Claude export format
 */
function parseClaude(content: string): ParsedConversation[] {
  const data = JSON.parse(content);
  const conversations: ParsedConversation[] = [];

  // Handle single conversation or array
  const convArray = Array.isArray(data) ? data : [data];

  for (const conv of convArray) {
    if (!conv.chat_messages) continue;

    const messages: ParsedMessage[] = conv.chat_messages.map((msg: any) => ({
      role: msg.sender === 'human' ? 'user' : 'assistant',
      content: msg.text || '',
      timestamp: msg.created_at,
      model: msg.model,
    }));

    conversations.push({
      format: 'claude',
      title: conv.name || conv.title || `Conversation ${conv.uuid?.substring(0, 8)}`,
      messages,
      metadata: {
        uuid: conv.uuid,
        created_at: conv.created_at,
        updated_at: conv.updated_at,
        model: conv.model,
        project_uuid: conv.project_uuid,
      },
    });
  }

  return conversations;
}

/**
 * Parse ChatGPT export format
 */
function parseChatGPT(content: string): ParsedConversation[] {
  const data = JSON.parse(content);
  const conversations: ParsedConversation[] = [];

  // Handle single conversation or array
  const convArray = Array.isArray(data) ? data : [data];

  for (const conv of convArray) {
    if (!conv.mapping) continue;

    const messages: ParsedMessage[] = [];

    // ChatGPT uses a tree structure with mapping
    // We need to traverse it in order
    const nodeIds = Object.keys(conv.mapping);
    const nodes = conv.mapping;

    // Find root node and traverse
    const childMap: Record<string, string[]> = {};
    for (const nodeId of nodeIds) {
      const node = nodes[nodeId];
      if (node.parent) {
        if (!childMap[node.parent]) childMap[node.parent] = [];
        childMap[node.parent].push(nodeId);
      }
    }

    // Find root (node with no parent or parent not in mapping)
    const roots = nodeIds.filter(id => {
      const parent = nodes[id].parent;
      return !parent || !nodes[parent];
    });

    // BFS to get messages in order
    const queue = [...roots];
    while (queue.length > 0) {
      const nodeId = queue.shift()!;
      const node = nodes[nodeId];

      if (node.message && node.message.content) {
        const msgContent = node.message.content;
        const role = node.message.author?.role;

        if (role === 'user' || role === 'assistant') {
          let text = '';
          if (msgContent.parts && Array.isArray(msgContent.parts)) {
            text = msgContent.parts.filter((p: any) => typeof p === 'string').join('\n');
          } else if (typeof msgContent === 'string') {
            text = msgContent;
          }

          if (text.trim()) {
            messages.push({
              role: role as 'user' | 'assistant',
              content: text,
              timestamp: node.message.create_time
                ? new Date(node.message.create_time * 1000).toISOString()
                : undefined,
              model: node.message.metadata?.model_slug,
            });
          }
        }
      }

      // Add children to queue
      if (childMap[nodeId]) {
        queue.push(...childMap[nodeId]);
      }
    }

    if (messages.length > 0) {
      conversations.push({
        format: 'chatgpt',
        title: conv.title || 'ChatGPT Conversation',
        messages,
        metadata: {
          id: conv.id,
          create_time: conv.create_time,
          update_time: conv.update_time,
          model: conv.default_model_slug,
        },
      });
    }
  }

  return conversations;
}

/**
 * Parse Gemini export format
 */
function parseGemini(content: string): ParsedConversation[] {
  const data = JSON.parse(content);
  const conversations: ParsedConversation[] = [];

  // Handle Google Takeout format
  if (Array.isArray(data)) {
    // Takeout exports each turn as separate object
    const messages: ParsedMessage[] = [];

    for (const item of data) {
      if (item.textContent) {
        // Determine role from context (Gemini doesn't always clearly mark this)
        const isUser = item.role === 'user' || item.isUserInput === true;
        messages.push({
          role: isUser ? 'user' : 'assistant',
          content: item.textContent,
          timestamp: item.createTime || item.timestamp,
        });
      }
    }

    if (messages.length > 0) {
      conversations.push({
        format: 'gemini',
        title: 'Gemini Conversation',
        messages,
        metadata: {},
      });
    }
  }

  // Handle conversations wrapper format
  if (data.conversations && Array.isArray(data.conversations)) {
    for (const conv of data.conversations) {
      const messages: ParsedMessage[] = [];

      if (conv.messages && Array.isArray(conv.messages)) {
        for (const msg of conv.messages) {
          messages.push({
            role: msg.role === 'model' ? 'assistant' : (msg.role || 'user'),
            content: msg.content || msg.text || '',
            timestamp: msg.timestamp,
          });
        }
      }

      if (messages.length > 0) {
        conversations.push({
          format: 'gemini',
          title: conv.title || 'Gemini Conversation',
          messages,
          metadata: {
            id: conv.id,
            created: conv.created,
          },
        });
      }
    }
  }

  return conversations;
}

/**
 * Parse chat export from any supported format
 */
export function parseChat(content: string, filename: string): ParsedConversation[] {
  const format = detectFormat(content, filename);

  switch (format) {
    case 'claude':
      return parseClaude(content);
    case 'chatgpt':
      return parseChatGPT(content);
    case 'gemini':
      return parseGemini(content);
    default:
      throw new Error(`Unable to detect chat format. Supported formats: Claude, ChatGPT, Gemini`);
  }
}

/**
 * Convert parsed conversation to the format expected by the Neurolinguist parser
 * Returns a JSON string that can be used as input
 */
export function convertToNeurolinguistFormat(parsed: ParsedConversation): string {
  // Build the format that Neurolinguist expects
  const messages = parsed.messages.map((msg, index) => ({
    id: `msg-${index}`,
    role: msg.role,
    content: msg.content,
    timestamp: msg.timestamp,
  }));

  return JSON.stringify({
    uuid: crypto.randomUUID(),
    name: parsed.title || 'Imported Conversation',
    chat_messages: parsed.messages.map((msg, index) => ({
      uuid: crypto.randomUUID(),
      sender: msg.role === 'user' ? 'human' : 'assistant',
      text: msg.content,
      created_at: msg.timestamp || new Date().toISOString(),
      model: msg.model,
    })),
    created_at: parsed.metadata.created_at || parsed.metadata.create_time || new Date().toISOString(),
    updated_at: parsed.metadata.updated_at || parsed.metadata.update_time || new Date().toISOString(),
    source_format: parsed.format,
  }, null, 2);
}

/**
 * Get format display name
 */
export function getFormatDisplayName(format: ChatFormat): string {
  switch (format) {
    case 'claude': return 'Claude';
    case 'chatgpt': return 'ChatGPT';
    case 'gemini': return 'Gemini';
    default: return 'Unknown';
  }
}
