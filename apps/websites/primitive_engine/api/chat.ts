import Anthropic from "@anthropic-ai/sdk";
import type { VercelRequest, VercelResponse } from "@vercel/node";

// =============================================================================
// CLIENT INITIALIZATION
// =============================================================================
const anthropic = new Anthropic();

// =============================================================================
// SYSTEM CONTEXT - Primitive Engine Custom Engagement
// =============================================================================
const SYSTEM_CONTEXT = `# PRIMITIVE ENGINE - THE BUILDER

You are the Primitive Engine, a custom systems builder. Your job is to have a conversation with potential clients to understand what they're trying to build and whether Primitive Engine can help.

## IDENTITY

- **Company**: Primitive Engine LLC - THE BUILDER
- **Offering**: Custom systems built through pilot weeks and ongoing stewardship
- **Parent**: Part of the Truth Forge federation

## YOUR ROLE IN THIS CONVERSATION

You're having an initial discovery conversation. Your goals:
1. Understand what the person is trying to build or solve
2. Ask clarifying questions to get to the real problem
3. Assess whether this is something Primitive Engine can help with
4. If it's a fit, explain what a pilot week might look like for their use case
5. If it's not a fit, be honest about that

## WHAT PRIMITIVE ENGINE BUILDS

- **Data Pipelines**: ETL, real-time streaming, batch processing, data warehousing
- **AI Integration**: Domain-specific models, not generic chatbots. Models that understand YOUR data.
- **Automation**: Workflows triggered by time, events, or conditions. Things you do repeatedly, done automatically.
- **Internal Tools**: Dashboards, admin panels, operational systems
- **Custom Infrastructure**: Whatever you need that doesn't exist yet

## ENGAGEMENT MODEL

### Pilot Week ($5,000 - $15,000)
- One week intensive build
- Assessment call to understand the scope
- 5-day build of the core system
- Documentation
- Deployment to your environment
- You own the result

### Stewardship ($2,000/month)
- Ongoing relationship after pilot
- Monthly evolution of the system
- Priority support
- Quarterly review
- New feature builds as needed

### Custom Project (Scoped)
- Larger builds that need more than a week
- Discovery phase to understand full scope
- Fixed scope contract
- Milestone delivery
- Full documentation

## CONVERSATION STYLE

- Be direct and conversational
- Ask questions to understand the real problem, not just the stated one
- Don't over-promise or use jargon
- If something sounds like a bad fit, say so honestly
- Don't push for a sale - this is discovery, not persuasion
- Keep responses concise - this is a conversation, not a pitch

## WHAT YOU DON'T DO

- We don't sell off-the-shelf software
- We don't do hourly consulting without deliverables
- We don't build things that require ongoing dependency on us (unless the client wants stewardship)
- We don't pretend to be cheaper than we are

## OPENING

When the conversation starts, give a brief, warm welcome and ask what they're trying to build. Don't dump information on them - let them describe their situation first.`;

// =============================================================================
// TOOLS - Web Search for research
// =============================================================================
const TOOLS: Anthropic.Tool[] = [
  {
    name: "web_search",
    description: "Search the web for current information about technologies, solutions, or industry practices. Use when you need context about what the client is describing.",
    input_schema: {
      type: "object" as const,
      properties: {
        query: {
          type: "string",
          description: "The search query"
        }
      },
      required: ["query"]
    }
  }
];

// =============================================================================
// WEB SEARCH IMPLEMENTATION
// =============================================================================
async function performWebSearch(query: string): Promise<string> {
  const braveApiKey = process.env.BRAVE_SEARCH_API_KEY;
  if (!braveApiKey) {
    return `[Web search not available]`;
  }

  try {
    const response = await fetch(
      `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=5`,
      {
        headers: {
          "Accept": "application/json",
          "X-Subscription-Token": braveApiKey
        }
      }
    );

    if (!response.ok) return `[Web search failed: ${response.status}]`;

    const data = await response.json();
    const results = data.web?.results || [];
    if (results.length === 0) return `[No results for: "${query}"]`;

    return results.slice(0, 5).map((r: { title: string; url: string; description: string }, i: number) =>
      `${i + 1}. **${r.title}**\n   ${r.url}\n   ${r.description}`
    ).join("\n\n");
  } catch (error) {
    return `[Web search error: ${error instanceof Error ? error.message : "Unknown"}]`;
  }
}

// =============================================================================
// API HANDLER
// =============================================================================
interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatRequest {
  messages: Message[];
  sessionId?: string;
  context?: string;
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // CORS headers
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version");

  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const body = req.body as ChatRequest;
    const { messages, sessionId } = body;

    if (!messages || !Array.isArray(messages)) {
      return res.status(400).json({ error: "Messages array required" });
    }

    // Format messages for Claude
    const formattedMessages: Anthropic.MessageParam[] = messages.map((msg) => ({
      role: msg.role,
      content: msg.content
    }));

    // Initial API call
    let response = await anthropic.messages.create({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
      system: SYSTEM_CONTEXT,
      messages: formattedMessages,
      tools: TOOLS,
    });

    // Handle tool use (web search)
    while (response.stop_reason === "tool_use") {
      const toolUseBlock = response.content.find(
        (block): block is Anthropic.ToolUseBlock => block.type === "tool_use"
      );
      if (!toolUseBlock) break;

      let toolResult: string;
      if (toolUseBlock.name === "web_search") {
        const input = toolUseBlock.input as { query: string };
        toolResult = await performWebSearch(input.query);
      } else {
        toolResult = `[Unknown tool: ${toolUseBlock.name}]`;
      }

      response = await anthropic.messages.create({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1024,
        system: SYSTEM_CONTEXT,
        messages: [
          ...formattedMessages,
          { role: "assistant", content: response.content },
          { role: "user", content: [{ type: "tool_result", tool_use_id: toolUseBlock.id, content: toolResult }] }
        ],
        tools: TOOLS,
      });
    }

    // Extract text response
    const textBlock = response.content.find(
      (block): block is Anthropic.TextBlock => block.type === "text"
    );
    const assistantMessage = textBlock?.text || "I apologize, but I couldn't generate a response.";

    // Log for debugging
    console.log("Primitive Engine Chat:", JSON.stringify({
      timestamp: new Date().toISOString(),
      sessionId: sessionId || "anonymous",
      messageCount: messages.length + 1,
    }));

    res.status(200).json({ message: assistantMessage, sessionId: sessionId || crypto.randomUUID() });
  } catch (error) {
    console.error("Chat API error:", error);
    res.status(500).json({
      error: "Failed to process message",
      details: error instanceof Error ? error.message : "Unknown error",
    });
  }
}
