# BROWSER EXTENSION ARCHITECTURE

## THE VISION

An LLM integrated into Chrome that:
1. **SEES** — reads any tab's content, DOM, screenshots
2. **DISCUSSES** — natural language about what tabs are showing
3. **ACTS** — manipulates DOM, uses devtools, navigates
4. **ORCHESTRATES** — manages multiple tabs as workers
5. **LOOPS** — iterates across tabs until architecture is built

## THE PATTERN APPLIED

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BROWSER TAB ORCHESTRATOR                              │
│                                                                              │
│   HOLD₁ (Tabs)           AGENT (LLM)              HOLD₂ (Results)           │
│   ┌──────────────┐      ┌──────────────┐         ┌──────────────┐          │
│   │ Tab states   │      │ Scout/Qwen   │         │ Built        │          │
│   │ DOM content  │─────►│ reasoning    │────────►│ architecture │          │
│   │ Screenshots  │      │ + actions    │         │ Code files   │          │
│   │ User intent  │      │              │         │ Artifacts    │          │
│   └──────────────┘      └──────────────┘         └──────────────┘          │
│         ▲                      │                        │                   │
│         └──────────────────────┴────────────────────────┘                   │
│                           LOOP UNTIL DONE                                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## ARCHITECTURE

```
primitive-browser-extension/
├── manifest.json              # Chrome extension manifest v3
├── src/
│   ├── background/
│   │   ├── service-worker.ts  # Main orchestration loop
│   │   ├── tab-manager.ts     # Multi-tab state management
│   │   ├── llm-client.ts      # Connect to local LLM (Ollama/OpenClaw)
│   │   └── action-executor.ts # Execute LLM-decided actions
│   │
│   ├── content/
│   │   ├── dom-observer.ts    # Watch DOM changes
│   │   ├── dom-extractor.ts   # Extract structured content
│   │   ├── dom-mutator.ts     # Apply LLM actions to DOM
│   │   └── screenshot.ts      # Capture tab visuals
│   │
│   ├── devtools/
│   │   ├── panel.ts           # DevTools panel UI
│   │   ├── console-bridge.ts  # Execute in console context
│   │   ├── network-monitor.ts # Watch network requests
│   │   └── element-selector.ts# Visual element picker
│   │
│   ├── sidebar/
│   │   ├── chat-ui.tsx        # Conversation interface
│   │   ├── tab-preview.tsx    # Show managed tabs
│   │   ├── action-log.tsx     # Display action history
│   │   └── loop-status.tsx    # Show orchestration progress
│   │
│   └── shared/
│       ├── types.ts           # Shared type definitions
│       ├── messages.ts        # Chrome messaging protocol
│       └── state.ts           # Global state management
│
├── prompts/
│   ├── system.md              # Base system prompt
│   ├── tab-analysis.md        # Analyze tab content
│   ├── action-planning.md     # Plan next actions
│   └── orchestration.md       # Multi-tab coordination
│
└── config/
    └── llm-config.json        # LLM endpoint configuration
```

## CORE COMPONENTS

### 1. Tab Manager

```typescript
// src/background/tab-manager.ts

interface ManagedTab {
  id: number;
  url: string;
  title: string;
  role: TabRole;           // 'worker' | 'reference' | 'output' | 'llm-interface'
  state: TabState;
  lastContent: string;
  lastScreenshot?: string;
}

type TabRole =
  | 'worker'         // Active workspace (e.g., code editor)
  | 'reference'      // Documentation, examples
  | 'output'         // Where results go
  | 'llm-interface'; // Other LLMs (Google AI Studio, Claude, etc.)

class TabManager {
  private tabs: Map<number, ManagedTab> = new Map();

  async captureTabState(tabId: number): Promise<TabState> {
    const dom = await this.extractDOM(tabId);
    const screenshot = await this.captureScreenshot(tabId);
    const metadata = await this.getTabMetadata(tabId);

    return { dom, screenshot, metadata, capturedAt: Date.now() };
  }

  async captureAllTabs(): Promise<TabState[]> {
    return Promise.all(
      Array.from(this.tabs.keys()).map(id => this.captureTabState(id))
    );
  }
}
```

### 2. LLM Client

```typescript
// src/background/llm-client.ts

interface LLMClient {
  endpoint: string;  // http://localhost:11434/v1 (Ollama)
  model: string;     // qwen2.5-coder:32b or llama4:scout

  async reason(context: OrchestratorContext): Promise<LLMResponse> {
    const prompt = this.buildPrompt(context);

    const response = await fetch(`${this.endpoint}/chat/completions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: this.model,
        messages: [
          { role: 'system', content: SYSTEM_PROMPT },
          { role: 'user', content: prompt }
        ],
        temperature: 0.7,
      })
    });

    return this.parseResponse(await response.json());
  }

  private buildPrompt(context: OrchestratorContext): string {
    return `
## Current State

### Managed Tabs
${context.tabs.map(t => `- [${t.role}] ${t.title}: ${t.url}`).join('\n')}

### Tab Contents
${context.tabs.map(t => `
#### ${t.title}
\`\`\`
${t.lastContent.slice(0, 10000)}
\`\`\`
`).join('\n')}

### User Intent
${context.userIntent}

### Previous Actions
${context.actionHistory.slice(-10).map(a => `- ${a.action}: ${a.result}`).join('\n')}

## Task
Analyze the current state across all tabs. Decide what actions to take.
Return a JSON action plan.
    `;
  }
}
```

### 3. Action Executor

```typescript
// src/background/action-executor.ts

type Action =
  | { type: 'navigate'; tabId: number; url: string }
  | { type: 'click'; tabId: number; selector: string }
  | { type: 'type'; tabId: number; selector: string; text: string }
  | { type: 'execute_script'; tabId: number; script: string }
  | { type: 'extract'; tabId: number; selector: string }
  | { type: 'screenshot'; tabId: number }
  | { type: 'open_devtools'; tabId: number }
  | { type: 'console_eval'; tabId: number; expression: string }
  | { type: 'wait'; ms: number }
  | { type: 'create_tab'; url: string; role: TabRole }
  | { type: 'send_to_llm_tab'; tabId: number; prompt: string }; // For LLM tabs

class ActionExecutor {
  async execute(action: Action): Promise<ActionResult> {
    switch (action.type) {
      case 'navigate':
        await chrome.tabs.update(action.tabId, { url: action.url });
        return { success: true, action };

      case 'click':
        await chrome.scripting.executeScript({
          target: { tabId: action.tabId },
          func: (sel) => document.querySelector(sel)?.click(),
          args: [action.selector]
        });
        return { success: true, action };

      case 'type':
        await chrome.scripting.executeScript({
          target: { tabId: action.tabId },
          func: (sel, text) => {
            const el = document.querySelector(sel) as HTMLInputElement;
            el.value = text;
            el.dispatchEvent(new Event('input', { bubbles: true }));
          },
          args: [action.selector, action.text]
        });
        return { success: true, action };

      case 'send_to_llm_tab':
        // Special: interact with another LLM interface (AI Studio, Claude, etc.)
        return this.sendToLLMInterface(action.tabId, action.prompt);

      // ... other actions
    }
  }

  private async sendToLLMInterface(tabId: number, prompt: string): Promise<ActionResult> {
    // Detect which LLM interface this tab is
    const url = (await chrome.tabs.get(tabId)).url;

    if (url?.includes('aistudio.google.com')) {
      return this.sendToGoogleAIStudio(tabId, prompt);
    } else if (url?.includes('claude.ai')) {
      return this.sendToClaude(tabId, prompt);
    }
    // ... other LLM interfaces
  }
}
```

### 4. Orchestration Loop

```typescript
// src/background/service-worker.ts

class Orchestrator {
  private tabManager: TabManager;
  private llmClient: LLMClient;
  private executor: ActionExecutor;
  private loopActive: boolean = false;

  async startLoop(intent: string, maxIterations: number = 50): Promise<void> {
    this.loopActive = true;
    let iteration = 0;

    while (this.loopActive && iteration < maxIterations) {
      // 1. HOLD₁ — Capture all tab states
      const tabStates = await this.tabManager.captureAllTabs();

      // 2. AGENT — LLM reasons about what to do
      const context: OrchestratorContext = {
        tabs: tabStates,
        userIntent: intent,
        actionHistory: this.actionHistory,
        iteration,
      };

      const response = await this.llmClient.reason(context);

      // Check if LLM says we're done
      if (response.status === 'complete') {
        this.loopActive = false;
        break;
      }

      // 3. Execute actions across tabs
      for (const action of response.actions) {
        const result = await this.executor.execute(action);
        this.actionHistory.push({ action, result, iteration });

        // Wait for DOM to settle
        await this.waitForStability(action.tabId);
      }

      // 4. HOLD₂ — Results are in the tabs themselves

      iteration++;

      // Brief pause between iterations
      await new Promise(r => setTimeout(r, 1000));
    }
  }

  stopLoop(): void {
    this.loopActive = false;
  }
}
```

### 5. Multi-LLM Orchestration

The killer feature: using browser tabs as workers, including other LLM interfaces.

```typescript
// Example: Building architecture using multiple LLMs

const orchestrationPlan = {
  intent: "Build a REST API for user authentication",

  tabs: [
    { role: 'llm-interface', url: 'https://aistudio.google.com', purpose: 'Generate schemas' },
    { role: 'llm-interface', url: 'https://claude.ai', purpose: 'Review and critique' },
    { role: 'reference', url: 'https://docs.python.org', purpose: 'Documentation' },
    { role: 'worker', url: 'https://github.dev/...', purpose: 'Write code' },
    { role: 'output', url: 'file:///workspace/output.md', purpose: 'Collect results' },
  ],

  loop: [
    // Step 1: Ask AI Studio to generate initial schema
    { action: 'send_to_llm_tab', tab: 'aistudio', prompt: 'Generate auth schema...' },
    { action: 'extract', tab: 'aistudio', selector: '.response-content' },

    // Step 2: Send to Claude for review
    { action: 'send_to_llm_tab', tab: 'claude', prompt: 'Review this schema: ${previous}' },
    { action: 'extract', tab: 'claude', selector: '.response' },

    // Step 3: If Claude suggests changes, loop back to AI Studio
    // Step 4: When consensus, write to worker tab
    // Step 5: Repeat until architecture is complete
  ]
};
```

## SYSTEM PROMPT FOR BROWSER ORCHESTRATOR

```markdown
# BROWSER ORCHESTRATOR

You are an LLM integrated into Chrome, operating as a cognitive extension.

## YOUR CAPABILITIES

1. **SEE** — You can read any tab's DOM, take screenshots, observe network
2. **ACT** — You can click, type, navigate, execute scripts, use devtools
3. **ORCHESTRATE** — You manage multiple tabs as workers
4. **LOOP** — You iterate until the task is complete

## TAB ROLES

- **worker**: Active workspace where you build/edit
- **reference**: Documentation, examples, sources
- **output**: Where final results are collected
- **llm-interface**: Other LLMs (AI Studio, Claude, etc.) you can delegate to

## THE PATTERN

```
HOLD₁ (Tab States) → AGENT (You) → HOLD₂ (Tab Actions)
         ↑                              │
         └──────────────────────────────┘
                    LOOP
```

## DECISION FRAMEWORK

When given a task:
1. What tabs do I need? (open them)
2. What information do I need from each? (extract)
3. What actions move toward completion? (execute)
4. Am I done? (check against intent)
5. If not, loop

## OUTPUT FORMAT

Return JSON:
```json
{
  "status": "in_progress" | "complete" | "blocked",
  "reasoning": "Why I'm taking these actions",
  "actions": [
    { "type": "...", "tabId": ..., ... }
  ],
  "next_check": "What to verify after actions"
}
```

## MULTI-LLM COORDINATION

When using LLM tabs (AI Studio, Claude, etc.):
1. Send a clear, scoped prompt
2. Wait for response
3. Extract the response content
4. Integrate into your reasoning
5. Continue or loop

You are the ORCHESTRATOR. Other LLMs are WORKERS.
```

## CONNECTION TO OPENCLAW

The extension connects to local LLM via OpenClaw gateway:

```json
// config/llm-config.json
{
  "endpoint": "http://127.0.0.1:11434/v1",
  "model": "qwen2.5-coder:32b",
  "fallback": "llama4:scout",
  "maxContextTokens": 131072
}
```

Or for Empire cluster:
```json
{
  "endpoint": "http://empire.local:52415/v1",
  "model": "llama4:scout",
  "maxContextTokens": 10000000
}
```

## DEVELOPMENT PHASES

### Phase 1: Foundation
- [ ] Basic extension manifest
- [ ] Tab state capture (DOM + screenshot)
- [ ] Single-tab LLM conversation
- [ ] Simple action execution

### Phase 2: Orchestration
- [ ] Multi-tab management
- [ ] Orchestration loop
- [ ] Action history tracking
- [ ] Loop termination detection

### Phase 3: LLM Tab Integration
- [ ] Detect LLM interfaces
- [ ] Send prompts to LLM tabs
- [ ] Extract responses
- [ ] Multi-LLM coordination

### Phase 4: DevTools Integration
- [ ] Console execution
- [ ] Network monitoring
- [ ] Element inspection
- [ ] Performance profiling

### Phase 5: Empire Integration
- [ ] Connect to distributed cluster
- [ ] 10M context for full-session memory
- [ ] Persistent orchestration state

---

*This is THE PATTERN applied to the browser. Tabs are HOLDs. The LLM is the AGENT. Actions loop until done.*
