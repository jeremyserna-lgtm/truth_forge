# Source Adapters Reference

## Overview

Atom-Forge is universal — it atomizes any input. Source adapters provide specialized reading patterns that help the LLM understand different data formats efficiently.

## Adapter: Claude Code Sessions

**Location**: `.claude/projects/{project-slug}/*.jsonl`
**Format**: JSONL (one JSON record per line)
**Record types**: user, assistant, queue-operation

### File Structure
```
.claude/projects/
├── -Users-jeremyserna-Truth-Engine/         # 493+ sessions
│   ├── sessions-index.json                  # Session metadata index
│   ├── {session-uuid}.jsonl                 # Main conversation
│   ├── {session-uuid}/
│   │   └── subagents/
│   │       └── agent-{id}.jsonl             # Subagent conversations
│   └── ...
├── -Users-jeremyserna-truth-forge/          # 110+ sessions
├── -Users-jeremyserna-credential-atlas/     # Credential Atlas sessions
├── -Users-jeremyserna-Architect-Library/    # Architect Library sessions
└── ...
```

### Key Fields for Atomization
- `message.content` — The actual text to atomize (string for user, array for assistant)
- `message.model` — Which LLM was used
- `message.usage` — Token consumption data
- `cwd` — Working directory (tells you what project)
- `timestamp` — When the message was sent
- `sessionId` — Links all records in a conversation
- `parentUuid` → `uuid` chain — Reconstructs conversation order

### Content Block Types (Assistant Messages)
- `text` — Natural language response → primary atomization target
- `thinking` — Internal reasoning → extract reasoning patterns, alternatives considered
- `tool_use` — Tool invocations → extract tool usage patterns, file operations

### What to Skip
- System prompts and tool schemas (boilerplate)
- Raw file contents read by tools (the file is the source, not the echo)
- Repeated instructions across messages
- Cache statistics and token counts (operational, not knowledge)

## Adapter: Generic LLM Conversations

**Format**: JSON or JSONL with role/content pairs
**Detection**: Look for `role` and `content` fields

### Common Formats
```json
// OpenAI-style
{"role": "user", "content": "..."}
{"role": "assistant", "content": "..."}

// Gemini-style
{"role": "user", "parts": [{"text": "..."}]}
{"role": "model", "parts": [{"text": "..."}]}
```

### Mapping
Map any format to: `{speaker, text, timestamp, metadata}`

## Adapter: Text Documents

**Format**: .txt, .md, .html
**Approach**: Read as continuous text, extract knowledge through comprehension

### Strategy
1. Read the document
2. Identify sections and topics
3. Extract claims, definitions, facts, recommendations
4. Each paragraph may yield 0-5 atoms depending on density

## Adapter: Structured Data

**Format**: .csv, .json with tabular data
**Approach**: LLM interprets column semantics, extracts knowledge from patterns

### Strategy
1. Read headers/schema
2. Sample rows to understand data shape
3. Extract knowledge about what the data represents
4. Aggregate patterns (not individual rows — those are data, not knowledge)

## Adapter: Text Messages

**Source**: Text message exports
**Pipeline**: `source_pipeline = "text_messages"`
**Approach**: Treat as conversation, extract with affective dimension emphasis

## Adding New Adapters

Any new data source follows the pattern:
1. Understand the format (how is the data structured?)
2. Identify the knowledge-carrying fields (where is the meaning?)
3. Map to the atomization process (comprehend → extract → dimension)
4. Set source tracking (source_file, source_system, source_pipeline)

The LLM handles the actual intelligence — the adapter just tells it how to read the format.
