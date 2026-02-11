# LLM-UI technical specification for production systems

**Every major LLM interface — from ChatGPT to Claude to local Ollama setups — converges on a surprisingly small set of architectural patterns.** This specification distills them into implementable blueprints: the streaming protocols that deliver tokens to the browser, the state machines that classify and render content, the sandbox architectures that safely execute generated code, and the orchestration patterns that coordinate multi-agent workflows. The OpenAI Chat Completions API has become the de facto universal interface standard, adopted by every local and cloud provider, while MCP (Model Context Protocol) is emerging as the standard for tool extensibility. A developer building a custom LLM system can achieve production-quality results by implementing these concrete patterns.

---

## 1. Streaming protocols: SSE dominates, WebSockets serve real-time audio

All three major providers (OpenAI, Anthropic, Google) use **Server-Sent Events over POST requests** for text streaming. This means the browser `EventSource` API (GET-only) cannot be used — implementations must use `fetch()` with `ReadableStream`.

### Wire-level formats

**OpenAI Chat Completions** streams chunks separated by `\r\n\r\n`. Each chunk is `data: {JSON}\n\n` with a terminal `data: [DONE]\n\n`:

```typescript
interface ChatCompletionChunk {
  id: string;                    // "chatcmpl-A8dyC7f6..."
  object: "chat.completion.chunk";
  created: number;               // Unix timestamp
  model: string;
  choices: Array<{
    index: number;
    delta: {
      role?: "assistant";        // Only in first chunk
      content?: string;          // Token(s) per chunk
    };
    finish_reason: null | "stop" | "length" | "tool_calls";
  }>;
  usage: null | { prompt_tokens: number; completion_tokens: number; total_tokens: number };
}
```

The first chunk announces `role: "assistant"` with empty content. Subsequent chunks carry `delta.content` with one or more tokens. The stop chunk has an empty delta and `finish_reason: "stop"`. Usage data arrives in a final chunk (only if `stream_options.include_usage: true`) with an empty `choices` array.

**Anthropic** uses named SSE events with an `event:` line preceding each `data:` line, providing a typed event lifecycle:

```
event: message_start       → Message metadata, input token count
event: content_block_start → Begin text/tool_use/thinking block (index-based)
event: content_block_delta → Token data: text_delta, input_json_delta, or thinking_delta
event: content_block_stop  → Block complete
event: message_delta       → stop_reason ("end_turn"|"stop_sequence"|"max_tokens")
event: message_stop        → Stream complete
event: ping                → Keep-alive
```

The `content_block_delta` event carries typed deltas — `{"type": "text_delta", "text": "Hello"}` for text, or `{"type": "input_json_delta", "partial_json": "{\"location\": \"San Fra"}` for streaming tool arguments. Each block is tracked by `index`, allowing multiple content blocks (text + tool calls) to stream in sequence.

**Google Gemini** provides both SSE REST (`?alt=sse`) and WebSocket (for the Live API). The WebSocket endpoint at `wss://generativelanguage.googleapis.com/ws/...BidiGenerateContent` uses a setup message followed by bidirectional JSON messages with `clientContent`/`serverContent`/`toolCall`/`toolResponse` fields. WebSockets are used exclusively for real-time audio/video; text uses SSE.

### Client-side consumption pattern

```javascript
async function* streamLLM(url, body, headers) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify(body),
  });
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || '';
    for (const event of events) {
      for (const line of event.split(/\r?\n/)) {
        if (line.startsWith('data: ') && line.slice(6) !== '[DONE]') {
          yield JSON.parse(line.slice(6));
        }
      }
    }
  }
}
```

**Critical server configuration**: Set `X-Accel-Buffering: no` to prevent nginx from buffering the entire stream, and `Cache-Control: no-cache, no-transform` in response headers.

### Incremental markdown rendering

Streaming markdown creates a core challenge: partial syntax like `**bold` or ` ```python\ndef` shows raw characters until closing delimiters arrive. Three production-proven solutions exist:

- **streaming-markdown (smd)**: 3KB library that uses `appendChild()` internally (O(1) per chunk) instead of replacing `innerHTML` (O(n²)). Call `smd.parser_write(parser, chunk)` for each token.
- **Buffering FSM**: A finite state machine buffers on `*`, `[`, `` ` `` characters, flushing as raw text on unexpected characters or rendering as markdown when closing delimiters arrive. Shopify's Sidekick uses this pattern in production.
- **Streamdown**: Drop-in `react-markdown` replacement that auto-completes unterminated syntax during streaming.

For **code blocks**, buffer the entire block until the closing ` ``` ` is detected, then apply syntax highlighting. For **Mermaid diagrams**, validate with `mermaid.parse(content, { suppressErrors: true })` before rendering since partial diagrams are always invalid.

**Performance rule**: Batch DOM updates per animation frame using `requestAnimationFrame`, accumulating tokens between frames.

---

## 2. Content detection drives dynamic UI through typed message parts

The dominant pattern across all platforms is a **content-type discriminated union** rendered through a **parts-based message model**. The server produces typed parts, the transport streams them via SSE with type prefixes, and the client switches rendering components based on `part.type`.

### The Vercel AI SDK pattern (production standard)

```tsx
message.parts.map((part, i) => {
  switch (part.type) {
    case "text":          return <MarkdownRenderer content={part.text} />;
    case "tool-call":     return <ToolCallCard name={part.toolName} state={part.state} />;
    case "reasoning":     return <CollapsibleReasoning text={part.reasoning} />;
    case "source":        return <SourceCitation {...part} />;
    case "file":          return <FilePreview {...part} />;
  }
});
```

Tool calls follow a state machine: `INITIATED → INPUT_STREAMING → INPUT_AVAILABLE → EXECUTING → OUTPUT_AVAILABLE | OUTPUT_ERROR`. Each state maps to a distinct UI component — a spinner during execution, a structured card on success, an error banner on failure.

### Block matching with streaming classification

For content within text blocks (code fences, JSON, tables), the **llm-ui** library provides block-level pattern detection:

```
SSE Stream → useLLMOutput hook → Block Matching (regex + FSM) → Component Rendering
  ├─ findCompleteMatch(): closed ``` fences → CodeBlock component
  ├─ findPartialMatch(): open ``` fences → BufferedCodeBlock component
  ├─ lookBack(): process previously streamed context
  └─ fallback: everything else → Markdown component
```

The key insight: **the model's structured output protocol itself drives the UI component tree** — no separate "content detection" layer is needed when the API returns typed parts. For inline content within text streams, FSM-based parsers handle the detection incrementally.

### Google's A2UI protocol

Google's Agent-to-UI protocol (June 2025) takes this further: agents send JSON descriptions of component trees plus data models, and the client maps abstract descriptions to native widgets (React, Flutter, SwiftUI). The same payload renders across platforms while the client retains full control over styling and security.

---

## 3. NotebookLM's pipeline: RAG retrieval → template-driven generation → multi-modal output

NotebookLM is a **document-grounded RAG platform** built on Gemini 2.5 Flash. All content is loaded into the model's context window — not used for training.

### The ingestion pipeline

```
Upload (PDF/DOCX/Slides/URLs/YouTube/Audio)
  → Format-specific parsing (OCR for scanned documents)
  → Chunking into ~hundreds-of-token passages
  → Vector embedding via Gemini embedding model
  → Nearest-neighbor index storage
```

**Limits**: Up to 50 sources per notebook (300 for Enterprise), each under **200 MB or 500,000 words**. At query time, the user's input is embedded using the same model, cosine similarity retrieves top-k passages, and these are prepended to the generation prompt with artifact-specific templates.

### Audio Overview generation

The podcast pipeline runs in four stages: **(1)** RAG retrieval extracts key topics and relationships across all sources; **(2)** Gemini generates a two-speaker conversational script using a fixed multi-segment prompt template with alternating host/expert roles; **(3)** an optional second LLM pass improves naturalness; **(4)** Google's **SoundStorm** technology (parallel audio generation via Residual Vector Quantization on a Conformer architecture) produces the final MP3.

SoundStorm generates **30 seconds of audio in 0.5 seconds on TPU-v4** — 60x faster than real-time. The latest generation produces 2 minutes of dialogue in under 3 seconds. The system supports natural fillers, laughter, overlapping speech, and emotional expression across **24+ languages**.

### The Standalone Podcast API

```
POST /v1/projects/{PROJECT_ID}/locations/global/podcasts
{
  "podcastConfig": {
    "focus": "Discuss the key findings about X",
    "length": "SHORT" | "STANDARD",        // 4-5min or ~10min
    "languageCode": "en-US"
  },
  "contexts": [
    { "text": "..." },
    { "inlineData": { "mimeType": "image/png", "data": "base64..." }}
  ]
}
// Returns operation name; poll for completion, then:
GET /v1/{OPERATION_NAME}:download?alt=media → MP3
```

Input limit is **100,000 tokens** across all contexts. This API enables podcast generation without a NotebookLM notebook.

### Replicating the pipeline

The open-source `open-notebooklm` implementation demonstrates the pattern: extract text → define a Pydantic schema with `scratchpad` (brainstorming space) and `script` (list of speaker/text pairs) → generate via LLM in JSON mode → **two-pass refinement** (critical for quality) → per-line TTS concatenation. The scratchpad field is essential — it gives the LLM space to plan conversation structure before generating line-by-line dialogue. TTS options include MeloTTS, Bark/Suno, ElevenLabs, or Google Cloud TTS.

---

## 4. Tool calling formats differ by provider but share a call-ID correlation pattern

### Cross-platform tool definition comparison

| Aspect | OpenAI | Anthropic | Gemini |
|--------|--------|-----------|--------|
| Schema wrapper | `parameters` | `input_schema` | `parameters` |
| Call in response | `tool_calls[].function` | `content[].tool_use` | `parts[].functionCall` |
| Result role | `role: "tool"` | `role: "user"` with `tool_result` block | `role: "function"` with `functionResponse` |
| Correlation field | `tool_call_id` / `call_id` | `tool_use_id` ↔ `id` | By function name (no explicit ID) |
| Stop reason | `finish_reason: "tool_calls"` | `stop_reason: "tool_use"` | Implicit (functionCall present) |
| Parallel calls | `parallel_tool_calls: true` (default) | Default on; `disable_parallel_tool_use: true` to disable | Multiple `functionCall` parts |
| Strict mode | `strict: true` | `strict: true` (beta) | Schema always enforced |

**Anthropic's tool call** returns a content array mixing text and tool_use blocks — the model can explain what it's doing alongside the call:

```json
{"role": "assistant", "content": [
  {"type": "text", "text": "Let me check the weather for you."},
  {"type": "tool_use", "id": "toolu_01A09q", "name": "get_weather",
   "input": {"location": "San Francisco, CA"}}
], "stop_reason": "tool_use"}
```

Results are sent back as a user message with `tool_result` blocks (not a separate `tool` role like OpenAI). The `tool_use_id` must match the original `id`.

### Permission models

**Claude Desktop** requires explicit approval for every tool call by default. A popup appears: "Claude wants to use [tool_name] from [server_name]. Allow / Always Allow / Deny." The `claude_desktop_config.json` supports `autoapprove` lists for read-only tools and `autoblock` lists for dangerous ones.

**ChatGPT** uses automatic execution — built-in tools (search, DALL-E, Code Interpreter) run transparently with status indicators ("Searching...") but no user-blocking capability.

**Gemini API** delegates permission entirely to the developer — the model returns structured `functionCall` objects, and the developer's code decides whether to execute. Google recommends validating "significant consequence" calls with the user.

---

## 5. State management: stateless APIs with client-side context engineering

Every major LLM API is **stateless** — the client must replay the full conversation history with each request. The platforms differ dramatically in how they layer persistent context.

### ChatGPT's four-layer memory architecture

Reverse-engineered analysis reveals ChatGPT injects four layers into every prompt:

1. **Session metadata** (ephemeral): device, location, subscription tier, account age, average conversation depth, model usage distribution, screen size
2. **User memory** (persistent facts): stored via a dedicated `bio` tool when the model detects relevant facts (name, job, preferences) — **not RAG-based**, directly injected as text
3. **Recent conversation summaries**: ~15 recent chat titles with user message snippets (not full transcripts)
4. **Current session** (sliding window): token-count-based cap; older messages roll off

When context fills, current session messages are trimmed first; permanent facts and conversation summaries are preserved.

### Claude Projects: direct context injection

Claude Projects inject uploaded files **directly into the context window** — not via RAG retrieval. The layering order per API call:

```
[Anthropic base system prompt]
[Project custom instructions]
[Project knowledge files — full content]
[Conversation history]
[Current user message]
```

The API uses a top-level `system` parameter separate from the messages array. Claude's token counting endpoint (`POST /v1/messages/count_tokens`) enables proactive context management.

### Context window management implementation

```python
def build_context(system_prompt, conversation, retrieved_docs, tools,
                  model_limit=128000, reserve_output=4096):
    budget = model_limit - reserve_output
    must_have = [system_prompt, conversation[-1]]  # Always: system + current message
    used = sum(count_tokens(m) for m in must_have) + 20

    # Priority 2: Tool definitions
    # Priority 3: Retrieved documents (most relevant first, cap at 50% budget)
    # Priority 4: Conversation history (most recent first, fill remaining budget)
    for msg in reversed(conversation[:-1]):
        msg_tokens = count_tokens(msg) + 4
        if used + msg_tokens < budget:
            history.insert(0, msg)
            used += msg_tokens
        else: break
```

**Anthropic** offers a server-side **compaction API** (beta) that condenses earlier conversation parts while keeping recent messages verbatim. **OpenAI's Responses API** provides a `/responses/compact` endpoint that replaces older messages with encrypted compaction items preserving latent understanding. Both are emerging patterns for handling long conversations without simple truncation.

---

## 6. Multi-agent orchestration converges on four patterns

### The orchestrator-worker pattern (Anthropic's production system)

Anthropic's multi-agent research system uses a Lead Agent (Claude Opus) that analyzes queries, develops strategy, and spawns **3–5 subagents** (Claude Sonnet) in parallel. Each subagent gets an independent context window and performs iterative search. A CitationAgent post-processes findings. This achieves a **90.2% improvement** over single-agent Claude Opus on their internal research eval, with token usage explaining 80% of performance variance.

### Claude Code TeammateTool: file-based coordination

Claude Code's agent teams use a file-based architecture at `~/.claude/teams/{team-name}/`:

```json
// Task format
{
  "id": "1", "subject": "Review the landing page",
  "status": "pending",  // pending | in_progress | completed
  "owner": "agent-abc123",
  "blocks": ["2", "3"], "blockedBy": [],
  "heartbeat": "2026-01-23T10:30:00Z"
}
```

Teams support four orchestration patterns: **Leader** (one orchestrator, multiple specialists — workers self-assign from queue), **Swarm** (interchangeable parallel workers), **Pipeline** (sequential with `blockedBy` dependency chains), and **Watchdog** (worker + monitor that can trigger rollback). Agents communicate via file-based inboxes with typed messages.

### LangGraph: graph-based state machines

LangGraph models workflows as directed graphs where nodes are agents/functions and edges are control flow (deterministic or conditional). The `StateGraph` carries shared state with `add_messages` annotations. The supervisor pattern — `create_supervisor([agent_a, agent_b], model=model)` — handles delegation via handoff tools. Hierarchical teams nest supervisors, and LangGraph Studio provides a visual IDE with real-time execution streaming, state inspection, and "time travel" debugging.

### CrewAI: YAML-configured agent teams

CrewAI uses a `config/agents.yaml` + `config/tasks.yaml` pattern with `role`, `goal`, `backstory`, and `allow_delegation` per agent. Tasks specify `context` dependencies (other tasks whose output feeds in). The `Crew` object orchestrates execution as `Process.sequential` (chained) or `Process.hierarchical` (manager agent supervises and quality-checks). Flows add stateful, event-driven pipelines with conditional branching and parallelism.

---

## 7. Artifact rendering: sandboxed iframes with postMessage communication

### Claude's artifact system

Artifacts are embedded in the SSE stream using custom XML:

```xml
<antArtifact identifier="chart" type="application/vnd.ant.react" title="Sales Chart">
  // React component code
</antArtifact>
```

Supported types: `application/vnd.ant.react` (live React via React Runner), `text/html` (full iframe render), `image/svg+xml`, `application/vnd.ant.mermaid`, `application/vnd.ant.code` (syntax-highlighted), `text/markdown`. Trigger heuristics: content exceeds ~15 lines, is self-contained, and likely to be iterated on.

**Security architecture** (confirmed by Anthropic's security engineer): iframe sandboxes with **full-site process isolation** (separate origin from claude.ai), strict CSP allowing only `https://cdnjs.cloudflare.com`, no localStorage/sessionStorage, no external network requests (`connect-src 'none'`). Communication uses `postMessage` between parent and sandbox.

### The sandbox implementation pattern

```html
<!-- Parent embedding -->
<iframe id="sandbox" src="https://sandbox.example.com/runner.html"
  sandbox="allow-scripts" style="width: 100%; border: none;"></iframe>

<!-- Inside sandbox: security check + message handler -->
<script>
  if (window.self === window.top) window.location.href = 'https://parent.example.com';
  window.addEventListener('message', (event) => {
    if (event.origin !== 'https://parent.example.com') return;
    const { artifactType, content } = event.data;
    switch (artifactType) {
      case 'application/vnd.ant.react': renderReactComponent(content); break;
      case 'text/html': document.open(); document.write(content); document.close(); break;
      case 'image/svg+xml': document.body.innerHTML = content; break;
    }
  });
</script>
```

**Critical security rule**: Never combine `allow-scripts` + `allow-same-origin` on same-origin content — the iframe can remove its own sandbox attribute. Use a **different origin** for the sandbox iframe.

### ChatGPT Canvas and Google Build Mode

ChatGPT Canvas uses a side-panel document/code editor with `create_textdoc`, `update_textdoc`, and `comment_textdoc` operations. Python execution uses **Pyodide** (WebAssembly) in the browser. Google AI Studio's Build Mode generates full React/TypeScript applications with a three-panel IDE (chat + code editor + live preview), compiling and rendering in an iframe on Cloud Run. Both support version history navigation and diff views.

### Cursor's sketch-and-apply innovation

Cursor separates **what to change** from **how to integrate it**: a primary LLM generates a "sketch" (intended change), then a custom-trained "Apply" model intelligently integrates it into the existing codebase. This two-model architecture handles context nuances better than direct diff generation.

---

## 8. MCP: the JSON-RPC 2.0 protocol for universal tool connectivity

MCP (Model Context Protocol), now at **version 2025-11-25** with **97M+ monthly SDK downloads**, provides a standardized way for LLM applications to connect to external tools and data sources.

### Architecture and initialization

MCP follows a **Host → Client → Server** model: the Host (e.g., Claude Desktop) creates Clients, each maintaining a 1:1 connection with a Server. All communication uses JSON-RPC 2.0.

```json
// Client → Server: initialize
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
  "protocolVersion": "2025-11-25",
  "capabilities": { "roots": { "listChanged": true }, "sampling": {} },
  "clientInfo": { "name": "MyClient", "version": "1.0.0" }
}}

// Server → Client: response with capabilities
{"jsonrpc": "2.0", "id": 1, "result": {
  "protocolVersion": "2025-11-25",
  "capabilities": { "tools": {}, "resources": { "subscribe": true }, "prompts": {} },
  "serverInfo": { "name": "my-server", "version": "1.0.0" }
}}

// Client → Server: initialized notification (no id, no response)
{"jsonrpc": "2.0", "method": "initialized"}
```

### Three core primitives

**Tools** (model-controlled): defined with `name`, `description`, `inputSchema` (JSON Schema), and optional `outputSchema` and `annotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`). Called via `tools/call`, returning `content` arrays of `text`, `image`, `audio`, or `resource` items.

**Resources** (application-driven): identified by URIs (`file://`, `https://`, custom schemes). Listed via `resources/list`, read via `resources/read`. Support subscriptions for change notifications.

**Prompts** (user-controlled): structured templates with arguments, retrieved via `prompts/get`, returning pre-built message arrays for the LLM.

### Transport mechanisms

**stdio**: Client launches server as subprocess; JSON-RPC over stdin/stdout, newline-delimited. Shutdown via closing stdin → SIGTERM → SIGKILL.

**Streamable HTTP** (replaces deprecated HTTP+SSE): A single HTTP endpoint. Client POSTs JSON-RPC messages; server responds with `application/json` or opens an `text/event-stream` for streaming. Server assigns `Mcp-Session-Id` for session management. Client can GET the endpoint to open an SSE stream for server-initiated messages.

### Minimal Python MCP server

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"
```

Run with `uv run mcp dev server.py` (Inspector) or `mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)` for HTTP.

### Security model

MCP mandates **user consent for all tool invocations** — tool annotations are untrusted unless from verified servers. HTTP transport uses **OAuth 2.1** with Protected Resource Metadata (RFC 9728) for authorization server discovery. The spec explicitly requires human-in-the-loop approval capability for all tool operations.

---

## 9. Local LLM interfaces converge on the OpenAI-compatible API standard

The OpenAI Chat Completions API has become the **universal interface** for local LLM deployment. Every major framework implements it:

| Framework | Default Port | Tech Stack | Primary Use Case |
|-----------|-------------|------------|-----------------|
| Ollama | 11434 | Go + llama.cpp | Single-user, easy setup |
| LM Studio | 1234 | Electron + llama.cpp/MLX | Desktop GUI + API |
| vLLM | 8000 | Python + PagedAttention | Multi-user production serving |
| text-generation-webui | 5000 | Python + Gradio | Full-featured with extensions |
| Open WebUI | 3000 | SvelteKit + FastAPI | Multi-user web interface |

### Ollama's native API

Beyond the OpenAI-compatible `/v1/chat/completions`, Ollama provides a simpler native API with streaming as newline-delimited JSON (not SSE):

```json
// POST /api/chat with stream: true returns:
{"model":"llama3.2","created_at":"...","message":{"role":"assistant","content":"The"},"done":false}
{"model":"llama3.2","created_at":"...","message":{"role":"assistant","content":" sky"},"done":false}
{"model":"llama3.2","created_at":"...","message":{"role":"assistant","content":""},"done":true,
 "total_duration":5043500667,"eval_count":26,"eval_duration":4799921000}
```

Model configuration uses the **Modelfile** format with Go template syntax for chat templates, supporting `PARAMETER` directives for all generation parameters, `SYSTEM` for system prompts, `ADAPTER` for LoRA, and `MESSAGE` for few-shot examples.

### GGUF quantization: Q4_K_M is the recommended default

GGUF files are self-contained binaries with header, typed metadata (architecture, tokenizer, context length), and quantized tensor data aligned to 32-byte boundaries for SIMD.

**K-Quant quality hierarchy** (higher = better quality, more RAM):

| Quantization | Bits/Weight | 7B Model Size | Quality Impact |
|-------------|-------------|---------------|----------------|
| Q8_0 | 8.0 | ~7.0 GB | Near-lossless |
| Q6_K | 6.0 | ~5.5 GB | Almost lossless |
| **Q4_K_M** | **4.9** | **~3.8 GB** | **Balanced — recommended default** |
| Q3_K_M | 3.0 | ~3.1 GB | Significant quality loss |
| Q2_K | 2.7 | ~2.7 GB | Not recommended |

**Memory rule of thumb**: Model in Q4_K_M ≈ 0.5× parameter count in GB. Quantized models run **1.5–2x faster** than FP16 with 90–95% quality retention at Q4_K_M.

### What's harder locally

Local frameworks support tool calling, multimodal input, and structured output, but with **less reliability** than frontier cloud models. vLLM's PagedAttention provides up to **24x higher throughput** than HuggingFace Transformers for multi-user serving, but single-user latency depends entirely on local hardware. The gap between local and cloud model quality is narrowing rapidly, but frontier models still lead on complex reasoning, reliable tool use, and long-context tasks.

### Universal frontend connection pattern

```javascript
async function* streamChat(baseUrl, model, messages, params = {}) {
  const response = await fetch(`${baseUrl}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, messages, stream: true, ...params })
  });
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop();
    for (const line of lines) {
      if (line.startsWith('data: ') && line !== 'data: [DONE]')
        yield JSON.parse(line.slice(6));
    }
  }
}
// Works with Ollama, LM Studio, vLLM, OpenAI, or any compatible server
```

---

## Conclusion: the implementable architecture

A developer building a custom LLM system should target these specific patterns. **For streaming**, implement SSE over POST with `fetch()` + `ReadableStream`, using a buffering FSM or streaming-markdown library for incremental rendering. **For the API layer**, implement the OpenAI Chat Completions format — it's the universal standard that works with every local and cloud provider. **For tool extensibility**, build an MCP client using the TypeScript or Python SDK, which provides a standardized way to discover and invoke tools across any MCP server. **For rich output rendering**, use a sandboxed iframe on a separate origin with `allow-scripts` only, communicating via `postMessage`, with React Runner for dynamic component compilation. **For state management**, implement priority-based context window management that preserves system prompts and recent messages while compressing or dropping older history. **For multi-agent orchestration**, the orchestrator-worker pattern with independent context windows per agent delivers the strongest results, with LangGraph's StateGraph providing the most flexible programmatic framework.

The entire stack — from streaming tokens to sandboxed execution — can be built on these well-tested patterns. The convergence around the OpenAI API standard, SSE transport, JSON-RPC (for MCP), and iframe sandboxing means a single implementation can target local Ollama, cloud providers, and custom model servers with minimal adaptation.