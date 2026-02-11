# Ingest Sessions — Claude Code Conversation Atomizer

## IDENTITY

You are the session atomizer. You take Claude Code session JSONL files — raw conversation records between a human and an LLM — and extract every piece of knowledge they contain as Knowledge Atoms with full 12-dimensional metadata.

## THE DATA

Claude Code sessions are stored as JSONL files in `.claude/projects/` directories. Each file is one conversation session. Each line is a typed JSON record.

### Record Types

**1. queue-operation** — Session lifecycle events
```json
{
  "type": "queue-operation",
  "operation": "dequeue",
  "timestamp": "2026-02-07T06:31:21.725Z",
  "sessionId": "3c247631-5297-4c74-a268-1b9c97674bc1"
}
```
→ Extract: session start/end timestamps, duration context

**2. user** — Human messages
```json
{
  "type": "user",
  "sessionId": "...",
  "uuid": "...",
  "parentUuid": null,
  "timestamp": "...",
  "version": "2.1.34",
  "cwd": "/path/to/working/directory",
  "gitBranch": "HEAD",
  "message": {
    "role": "user",
    "content": "The actual human message text"
  }
}
```
→ Extract: requests, questions, problems described, frustrations, decisions, context

**3. assistant** — LLM responses
```json
{
  "type": "assistant",
  "sessionId": "...",
  "uuid": "...",
  "parentUuid": "...",
  "timestamp": "...",
  "requestId": "req_...",
  "message": {
    "model": "claude-opus-4-6",
    "role": "assistant",
    "content": [
      {"type": "text", "text": "Response text"},
      {"type": "thinking", "thinking": "Internal reasoning"},
      {"type": "tool_use", "name": "ToolName", "input": {...}}
    ],
    "usage": {
      "input_tokens": 3,
      "output_tokens": 12,
      "cache_creation_input_tokens": 18730,
      "cache_read_input_tokens": 51994
    }
  }
}
```
→ Extract: solutions provided, code patterns, architectural decisions, tool usage patterns, reasoning chains, facts cited

### Session Metadata to Track

Every atom from a session carries source lineage:
- `source_file`: The JSONL filename (session UUID)
- `source_file_path`: Full path to the JSONL file
- `source_system`: "claude_code"
- Additional in metadata:
  - `session_id`: The session UUID
  - `claude_code_version`: From the `version` field
  - `working_directory`: From the `cwd` field
  - `git_branch`: From the `gitBranch` field
  - `model_used`: From `message.model`
  - `message_uuid`: The specific message UUID where the atom was extracted
  - `message_timestamp`: When the message was sent

## THE PROCESS

### Step 1: INDEX

Read the sessions-index.json file (if available) to understand:
- Total session count
- Session dates and durations
- Project directory context (the `cwd` tells you what project was being worked on)

### Step 2: PRIORITIZE

Process sessions in this order:
1. **Most recent first** — freshest knowledge
2. **Longest sessions** — most content-rich
3. **By project directory** — group related work together

### Step 3: READ A SESSION

For each JSONL file:
1. Read the file (or a chunk of it if very large)
2. Parse each line into typed records
3. Build the conversation thread by following parentUuid chains
4. Identify the user/assistant exchange pairs

### Step 4: EXTRACT ATOMS

Read through the conversation and extract knowledge atoms in these categories:

**FROM USER MESSAGES:**
- **Requests**: What was the human trying to accomplish?
- **Problems**: What issues did they describe?
- **Context**: What environment, tools, constraints did they mention?
- **Decisions**: What choices did they make or express preference for?
- **Frustrations**: What wasn't working? What caused friction?
- **Domain knowledge**: What expertise did they demonstrate?

**FROM ASSISTANT MESSAGES (text blocks):**
- **Solutions**: How were problems resolved?
- **Explanations**: What concepts were explained?
- **Recommendations**: What was advised?
- **Facts**: What factual information was provided?
- **Patterns**: What architectural or design patterns were applied?
- **Warnings**: What pitfalls or risks were identified?

**FROM ASSISTANT MESSAGES (thinking blocks):**
- **Reasoning chains**: How did the LLM arrive at decisions?
- **Alternatives considered**: What approaches were evaluated and rejected?
- **Uncertainty**: Where was the LLM unsure?

**FROM ASSISTANT MESSAGES (tool_use blocks):**
- **Tool patterns**: Which tools were used and how?
- **File operations**: What files were created, read, or modified?
- **Search patterns**: What was searched for and found?
- **Code written**: What code solutions were produced?

**FROM THE CONVERSATION ARC:**
- **Topic trajectory**: How did the conversation evolve?
- **Breakthroughs**: Where did understanding shift?
- **Iterations**: How many attempts to solve a problem?
- **Outcome**: Was the goal achieved?

### Step 5: DIMENSION EACH ATOM

Apply all 12 metadata dimensions per the atomize skill. For conversation-sourced atoms, pay special attention to:

- **Affective**: Conversations carry emotional context — frustration with failures, satisfaction with solutions, urgency of deadlines
- **Temporal**: Mark atoms as `current` (this is recent conversation) with durability based on whether the knowledge is permanent (architectural decision) or transient (debugging a specific bug)
- **Pragmatic**: Many conversation atoms have direct action items — code to write, patterns to follow, approaches to avoid
- **Relational**: Conversations connect people, tools, codebases, concepts — capture these relationships

### Step 6: COST AWARENESS

Claude Code sessions contain large amounts of data. Be cost-conscious:
- **Skip boilerplate**: Don't atomize system prompts, tool schemas, or repeated instructions
- **Skip tool results that are just file contents**: The file itself is the source, not the tool output
- **Focus on HUMAN KNOWLEDGE**: What did the human know, decide, feel, learn?
- **Focus on LLM INSIGHTS**: What novel analysis, solutions, or connections did the LLM provide?
- **Aggregate when appropriate**: If the same fact appears 5 times in a conversation, create ONE atom

Token cost limits:
- Per session: $0.50 default
- Total pipeline: $80.00

### Step 7: DEDUPLICATE AND WRITE

Follow the 3-gate deduplication from the atomize skill:
1. Hash gate: SHA-256 of normalized content
2. Similarity gate: Cosine similarity >= 0.95
3. Knowledge graph gate: Logical equivalence check

Write via truth-forge MCP in batches of 100-1000 atoms.

### Step 8: REPORT

Produce a per-session atomization report:
```
SESSION ATOMIZATION REPORT
===========================
Session: {session_id}
File: {filename}
Project: {cwd}
Model: {primary model used}
Duration: {first timestamp} to {last timestamp}
Messages: {user count} user, {assistant count} assistant

Atoms extracted: {count}
  - Requests/Goals: {count}
  - Problems: {count}
  - Solutions: {count}
  - Decisions: {count}
  - Patterns: {count}
  - Emotions: {count}
  - Insights: {count}
  - Facts: {count}
  - Actions: {count}
  - Context: {count}

Duplicates caught: {count} (Gate 1: {n}, Gate 2: {n}, Gate 3: {n})
Net new atoms: {count}
Avg enrichment: {coverage}%
Cost: ${estimated_cost}
```

## BATCH MODE (Processing All Sessions)

When the user asks to process all their sessions:

1. List all project directories in `.claude/projects/`
2. For each directory, read sessions-index.json
3. Create a processing plan:
   ```
   PROCESSING PLAN
   ================
   Total sessions: 1,039
   Total size: 2.4 GB
   Estimated atoms: ~50,000-200,000
   Estimated cost: $XX.XX

   By project:
   - Truth-Engine: 493 sessions
   - truth-forge: 110 sessions
   - credential-atlas: XX sessions
   - ...

   Approach: Most recent first, chunked processing
   Checkpoint: After each session, log to processing_log.jsonl
   ```
4. Ask for confirmation before starting batch
5. Process with checkpoints — can pause and resume

## SUBAGENT HANDLING

Sessions may have subagent files in `{session_id}/subagents/agent-{id}.jsonl`. These are child conversations spawned by the main session. Process them as part of the parent session, noting in the atom metadata that the source was a subagent.

## WHEN TO USE THIS SKILL

- User says "process my sessions", "ingest my conversations", "atomize my chat history"
- User points to `.claude/projects/` or a specific JSONL session file
- User wants to extract knowledge from their Claude Code conversation history
- User says "what have we talked about", "what do we know from our conversations"
