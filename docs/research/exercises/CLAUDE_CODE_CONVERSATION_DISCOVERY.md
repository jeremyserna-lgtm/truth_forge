# Claude Code Conversation Discovery

**Purpose**: Document how to find Claude Code conversation records for extraction or analysis.

**Created**: December 24, 2025

---

## Where Claude Code Stores Conversations

### Primary Location

```
~/.claude/projects/{workspace-path}/*.jsonl
```

The workspace path is derived from the absolute path with slashes replaced by dashes. For example:

| Workspace | Storage Path |
|-----------|--------------|
| `/Users/jeremyserna/PrimitiveEngine` | `~/.claude/projects/-Users-jeremyserna-Truth-Engine/` |
| `/Users/jeremyserna/Architect-Library` | `~/.claude/projects/-Users-jeremyserna-Architect-Library/` |

### File Types

| Pattern | Description |
|---------|-------------|
| `{uuid}.jsonl` | Main conversation sessions (e.g., `3018bf4e-565e-4c52-b5a6-aae9278bfea7.jsonl`) |
| `agent-{short-id}.jsonl` | Agent subprocesses spawned during conversations |
| `_archived_short_conversations/` | Archived short or inactive conversations |

---

## How I Found the Specific Conversation

### Step 1: Locate the Project Directory

```bash
ls -la ~/.claude/projects/
```

Identified: `-Users-jeremyserna-Truth-Engine` as the relevant project folder.

### Step 2: Find Files Modified Today

```bash
find ~/.claude/projects/-Users-jeremyserna-Truth-Engine -name "*.jsonl" -mtime 0 -type f
```

This returned all JSONL files modified in the last 24 hours.

### Step 3: Search for Specific Content

```bash
grep -l "Create the document this document describes" ~/.claude/projects/-Users-jeremyserna-Truth-Engine/*.jsonl
```

Found two matches. Checked modification times:

```bash
ls -la /path/to/file.jsonl
```

The file `3018bf4e-565e-4c52-b5a6-aae9278bfea7.jsonl` was modified at 20:06 on December 24, 2025.

---

## JSONL Structure

Each line in a `.jsonl` file is a JSON object with one of these types:

### Message Types

| Type | Description |
|------|-------------|
| `queue-operation` | Session queue management (start/end) |
| `file-history-snapshot` | File state tracking for undo |
| `user` | User messages (contains `message.content`) |
| `assistant` | Claude responses (contains `message.content`) |

### User Message Structure

```json
{
  "type": "user",
  "message": {
    "role": "user",
    "content": [
      {"type": "text", "text": "..."},
      {"type": "tool_result", "tool_use_id": "...", "content": "..."}
    ]
  },
  "uuid": "...",
  "timestamp": "2025-12-25T02:50:10.771Z",
  "sessionId": "3018bf4e-565e-4c52-b5a6-aae9278bfea7"
}
```

### Assistant Message Structure

```json
{
  "type": "assistant",
  "message": {
    "role": "assistant",
    "model": "claude-opus-4-5-20251101",
    "content": [
      {"type": "thinking", "thinking": "..."},
      {"type": "text", "text": "..."},
      {"type": "tool_use", "id": "...", "name": "Read", "input": {...}}
    ]
  },
  "uuid": "...",
  "timestamp": "...",
  "requestId": "req_..."
}
```

---

## Key Fields for Conversation Extraction

| Field | Location | Purpose |
|-------|----------|---------|
| User message text | `message.content[].text` (where type="text") | What the user said |
| LLM thinking | `message.content[].thinking` (where type="thinking") | Internal reasoning |
| LLM response | `message.content[].text` (where type="text") | What Claude said |
| Tool calls | `message.content[].name` and `.input` (where type="tool_use") | Actions taken |
| Tool results | `message.content[].content` (where type="tool_result") | Tool outputs |
| Timestamp | `timestamp` | When it happened |
| Session ID | `sessionId` | Groups related messages |
| Session slug | `slug` | Human-readable session name |

---

## Finding Conversations by Content

### Search for a phrase in all conversations:

```bash
grep -l "search phrase" ~/.claude/projects/-Users-jeremyserna-Truth-Engine/*.jsonl
```

### Search within a specific timeframe:

```bash
find ~/.claude/projects/-Users-jeremyserna-Truth-Engine -name "*.jsonl" -mtime 0 -exec grep -l "phrase" {} \;
```

### Get conversation metadata:

```bash
head -20 /path/to/conversation.jsonl | python3 -c "import json,sys; [print(json.loads(l).get('sessionId','')) for l in sys.stdin]" | head -1
```

---

## Python Script for Extraction

```python
import json

def extract_conversation(filepath):
    """Extract messages, thinking, and responses from a Claude Code conversation."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    conversation = []
    for line in lines:
        obj = json.loads(line)
        msg_type = obj.get('type', '')

        if msg_type == 'user':
            content = obj.get('message', {}).get('content', [])
            for item in content:
                if isinstance(item, dict) and item.get('type') == 'text':
                    text = item.get('text', '')
                    if not text.startswith('<ide_') and text.strip():
                        conversation.append({'role': 'user', 'content': text})

        elif msg_type == 'assistant':
            content = obj.get('message', {}).get('content', [])
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'thinking':
                        conversation.append({'role': 'thinking', 'content': item.get('thinking', '')})
                    elif item.get('type') == 'text':
                        text = item.get('text', '')
                        if text.strip():
                            conversation.append({'role': 'assistant', 'content': text})

    return conversation
```

---

## The Specific Conversation Found

| Field | Value |
|-------|-------|
| **Session ID** | `3018bf4e-565e-4c52-b5a6-aae9278bfea7` |
| **Session Slug** | `clever-frolicking-parasol` |
| **File Path** | `~/.claude/projects/-Users-jeremyserna-Truth-Engine/3018bf4e-565e-4c52-b5a6-aae9278bfea7.jsonl` |
| **File Size** | 383,413 bytes |
| **Last Modified** | December 24, 2025 at 20:06 |
| **Total Lines** | 55 |
| **Content** | Person Document creation + feedback reflection |

---

## Next Time: Quick Access

To find this conversation again:

```bash
# By session ID
cat ~/.claude/projects/-Users-jeremyserna-Truth-Engine/3018bf4e-565e-4c52-b5a6-aae9278bfea7.jsonl

# By searching for distinctive content
grep -l "Create the document this document describes" ~/.claude/projects/-Users-jeremyserna-Truth-Engine/*.jsonl

# By modification date range
find ~/.claude/projects/-Users-jeremyserna-Truth-Engine -name "*.jsonl" -newermt "2025-12-24" -not -newermt "2025-12-25"
```

---

## Related Files Created

| File | Purpose |
|------|---------|
| `docs/records/PERSON_DOCUMENT_CONVERSATION_2025-12-24.md` | Extracted conversation transcript |
| `docs/records/CLAUDE_CODE_CONVERSATION_DISCOVERY.md` | This discovery documentation |

---

*Created by Claude Code, December 24, 2025*
