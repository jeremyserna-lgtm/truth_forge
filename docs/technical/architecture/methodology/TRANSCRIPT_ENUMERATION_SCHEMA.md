# Transcript Enumeration Schema

**What this is**: The complete data dictionary for Claude Code transcripts, discovered by enumeration (not pre-knowledge).

**Source**: 951 transcripts, 82,723 entries
**Discovery date**: 2025-12-25

---

## The Hierarchy

```
6 Entry Types (what kind of thing is this?)
    └── 23 Tool Types (what action was taken?)
            └── 2,730 Key Paths (what data exists?)
```

**The pattern**: Start broad, zoom in to get what you need.

---

## Level 1: Entry Types (6)

Everything in a transcript is one of these:

| Entry Type | What It Is | When You Care |
|------------|------------|---------------|
| `user` | Human input | What was asked |
| `assistant` | Claude's response | **What was done** (tool calls live here) |
| `system` | System messages | Context, reminders |
| `summary` | Compact summaries | Condensed context |
| `file-history-snapshot` | File state tracking | Undo/backup tracking |
| `queue-operation` | Queue management | Session mechanics |

**To get "what Claude did"** → filter for `type = assistant`

---

## Level 2: Tool Types (23)

When `type = assistant`, look at `message.content[].type = tool_use`:

### Document Operations
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `Write` | Create a file | `.file_path`, `.content` |
| `Edit` | Modify a file | `.file_path`, `.old_string`, `.new_string` |
| `Read` | Access a file | `.file_path`, `.limit`, `.offset` |

### Discovery Operations
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `Glob` | Find files by pattern | `.pattern`, `.path` |
| `Grep` | Search file contents | `.pattern`, `.path`, `.glob`, `.output_mode` |
| `WebSearch` | Search the web | `.query` |
| `WebFetch` | Fetch a URL | `.url`, `.prompt` |

### Execution Operations
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `Bash` | Run shell command | `.command`, `.description`, `.timeout` |
| `KillShell` | Stop a shell | `.shell_id` |

### Agent Operations
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `Task` | Launch sub-agent | `.prompt`, `.description`, `.subagent_type` |
| `TaskOutput` | Get agent result | `.task_id`, `.block` |
| `Skill` | Invoke a skill | `.skill` |

### Planning Operations
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `EnterPlanMode` | Start planning | (none) |
| `ExitPlanMode` | Finish planning | `.plan` |
| `TodoWrite` | Track tasks | `.todos[]` (`.content`, `.status`, `.activeForm`) |

### Interaction Operations
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `AskUserQuestion` | Ask for input | `.questions` |

### Browser Operations (MCP)
| Tool | What It Does | Key Parameters |
|------|--------------|----------------|
| `mcp__playwright__browser_navigate` | Go to URL | `.url` |
| `mcp__playwright__browser_click` | Click element | `.element`, `.ref` |
| `mcp__playwright__browser_snapshot` | Capture state | (none) |
| `mcp__playwright__browser_take_screenshot` | Screenshot | `.filename`, `.fullPage` |

---

## Level 3: Key Paths (2,730)

The full detail - every nested field that exists.

### Document Lifecycle Paths
```
# Creation
message.content[].name = "Write"
message.content[].input.file_path    → where
message.content[].input.content      → what

# Modification
message.content[].name = "Edit"
message.content[].input.file_path    → where
message.content[].input.old_string   → before
message.content[].input.new_string   → after

# Access
message.content[].name = "Read"
message.content[].input.file_path    → where

# Move/Delete (in Bash)
message.content[].name = "Bash"
message.content[].input.command      → "mv /old/path /new/path" or "rm /path"
```

### Temporal Paths
```
timestamp                            → when this entry was recorded
message.usage.input_tokens           → cost tracking
message.usage.output_tokens          → cost tracking
sessionId                            → which session
uuid                                 → unique entry ID
parentUuid                           → conversation threading
```

### Context Paths
```
cwd                                  → working directory
gitBranch                            → current branch
version                              → Claude Code version
slug                                 → session name
```

---

## How To Use This

### "I want all documents ever created"
```
Filter: type = assistant
        message.content[].type = tool_use
        message.content[].name = Write
Extract: message.content[].input.file_path
         message.content[].input.content
         timestamp
```

### "I want the lifecycle of a specific document"
```
Filter: type = assistant
        message.content[].input.file_path = "/path/to/file.md"
        message.content[].name IN (Write, Edit, Read)
Sort:   timestamp
Result: Creation → Edits → Reads (in order)
```

### "I want all Bash commands that moved files"
```
Filter: type = assistant
        message.content[].name = Bash
        message.content[].input.command CONTAINS "mv "
Extract: message.content[].input.command
         timestamp
Parse:   source_path, dest_path from command
```

### "I want to know what was read before each Write"
```
Group by: sessionId
Sort by:  timestamp
Pattern:  Read → Read → Read → Write
Extract:  The Reads that preceded each Write
```

---

## The Principle

**Enumeration discovers structure. Queries extract meaning.**

1. Run the enumerator → get the schema
2. Know what exists → know what to query
3. Query for what you need → get the data

The transcript records everything. The enumeration tells you what's there. You decide what matters.

---

## Counts Summary

| Level | Count | Description |
|-------|-------|-------------|
| Entry Types | 6 | Base patterns (user, assistant, system, summary, file-history-snapshot, queue-operation) |
| Tool Types | 23 | Actions Claude can take |
| Key Paths | 2,730 | Every possible nested field |
| Transcripts | 951 | Files in the directory |
| Entries | 82,723 | Total records enumerated |

---

## Future: Document Identity

To track documents across moves/renames, need:
1. **At creation**: Embed `document_id` in frontmatter (PostToolUse hook on Write)
2. **At move**: Track `mv` commands in Bash to maintain path → document_id mapping
3. **At query**: Resolve current path via the alias graph

The enumeration schema doesn't solve identity - it just tells you what data exists. Identity requires embedding the ID in the document itself.
