# Claude Code Write Lifecycle

**What happens when Claude Code writes or edits a file**

This document traces every step from the moment Claude Code initiates a Write or Edit tool call to completion.

---

## The Four Scenarios

| Scenario | Tool | File Type | Hooks That Fire |
|----------|------|-----------|-----------------|
| 1. Write new MD | Write | .md | check_before_write.sh → claude-organize |
| 2. Edit existing MD | Edit | .md | check_before_write.sh → claude-organize |
| 3. Write new PY | Write | .py | check_before_write.sh → claude-organize |
| 4. Edit existing PY | Edit | .py | check_before_write.sh → claude-organize |

**Note:** Executing a Python script (Bash tool) has different hooks covered in a separate section.

---

## Scenario 1: Writing a New Markdown Document

### What Claude Code Sends

```json
{
  "tool": "Write",
  "file_path": "/Users/jeremyserna/PrimitiveEngine/docs/example.md",
  "content": "# Example Document\n\nThis is the full content of the new file..."
}
```

**Key characteristic:** The `Write` tool receives the **entire file content**. The file may or may not exist yet.

### Step-by-Step Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 1: WRITE NEW MARKDOWN DOCUMENT                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Step 1: Claude Code prepares Write tool call                              │
│          └─ file_path: "/path/to/new_doc.md"                               │
│          └─ content: "# Full document content..."                          │
│                                                                            │
│  Step 2: PreToolUse hooks fire (matcher: "Write|Edit|MultiEdit")           │
│          │                                                                 │
│          └─▶ check_before_write.sh                                         │
│              │                                                             │
│              └─▶ check_before_write.py                                     │
│                  │                                                         │
│                  ├─ Parse CLAUDE_TOOL_INPUT JSON                           │
│                  ├─ Extract file_path and content                          │
│                  ├─ Check extension (.md is tracked)                       │
│                  ├─ Check skip directories (not in venv, etc.)             │
│                  │                                                         │
│                  └─▶ registry_service.check_before_write()                 │
│                      │                                                     │
│                      ├─ Hash content (SHA256)                              │
│                      ├─ Query DuckDB: exact hash match?                    │
│                      │   └─ If match at DIFFERENT path → BLOCK (duplicate) │
│                      │   └─ If match at SAME path → ALLOW (same file)      │
│                      │                                                     │
│                      ├─ Query DuckDB VSS: semantic similarity?             │
│                      │   └─ Generate 1024-dim embedding (local BGE)        │
│                      │   └─ HNSW index search                              │
│                      │   └─ If similarity >= 85% → BLOCK (too similar)     │
│                      │                                                     │
│                      └─ No match → ALLOW (new content)                     │
│                                                                            │
│  Step 3: Decision                                                          │
│          └─ ALLOW (exit 0): Proceed to Step 4                              │
│          └─ BLOCK (exit 1): Stop here, show error to Claude Code           │
│                                                                            │
│  Step 4: Write executes                                                    │
│          └─ File is written to disk                                        │
│          └─ For NEW files: file is created                                 │
│          └─ For EXISTING files: file is overwritten                        │
│                                                                            │
│  Step 5: PostToolUse hooks fire (matcher: "Write|Edit|MultiEdit")          │
│          │                                                                 │
│          └─▶ claude-organize                                               │
│              └─ Node.js process                                            │
│              └─ Reads hook data from stdin                                 │
│              └─ Processes document metadata                                │
│              └─ Catalogs the written file                                  │
│                                                                            │
│  Step 6: Complete                                                          │
│          └─ Claude Code receives success confirmation                      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Environment Variables Available

| Variable | Value |
|----------|-------|
| `CLAUDE_TOOL_NAME` | `"Write"` |
| `CLAUDE_TOOL_INPUT` | `{"file_path": "...", "content": "..."}` |

### What Can Block This Write

1. **Exact duplicate at different path**: Same SHA256 hash exists in registry for a different file
2. **Too similar (>= 85%)**: Embedding similarity to existing registered content exceeds threshold
3. **Hook error**: If check_before_write.py crashes (though it fails open)

---

## Scenario 2: Editing an Existing Markdown Document

### What Claude Code Sends

```json
{
  "tool": "Edit",
  "file_path": "/Users/jeremyserna/PrimitiveEngine/docs/existing.md",
  "old_string": "This is the old text that exists in the file",
  "new_string": "This is the replacement text"
}
```

**Key characteristic:** The `Edit` tool uses **string replacement**. It finds `old_string` and replaces it with `new_string`. The hook receives the **new_string** as content to check, NOT the full file.

### Step-by-Step Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 2: EDIT EXISTING MARKDOWN DOCUMENT                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Step 1: Claude Code prepares Edit tool call                               │
│          └─ file_path: "/path/to/existing.md"                              │
│          └─ old_string: "text to find"                                     │
│          └─ new_string: "replacement text"                                 │
│                                                                            │
│  Step 2: PreToolUse hooks fire (matcher: "Write|Edit|MultiEdit")           │
│          │                                                                 │
│          └─▶ check_before_write.sh                                         │
│              │                                                             │
│              └─▶ check_before_write.py                                     │
│                  │                                                         │
│                  ├─ Parse CLAUDE_TOOL_INPUT JSON                           │
│                  ├─ Extract file_path                                      │
│                  ├─ Extract content from:                                  │
│                  │   └─ "content" key (Write tool)                         │
│                  │   └─ "file_text" key (alternative)                      │
│                  │   └─ NOTE: Edit tool has old_string/new_string          │
│                  │          The hook may not find content to check!        │
│                  │                                                         │
│                  └─ If no content found → ALLOW (can't check)              │
│                                                                            │
│  Step 3: Decision                                                          │
│          └─ For Edit: Usually ALLOW (content not in expected keys)         │
│                                                                            │
│  Step 4: Edit executes                                                     │
│          └─ Find old_string in file                                        │
│          └─ Replace with new_string                                        │
│          └─ If old_string not found → Error                                │
│          └─ If old_string not unique → Error                               │
│                                                                            │
│  Step 5: PostToolUse hooks fire                                            │
│          └─▶ claude-organize                                               │
│                                                                            │
│  Step 6: Complete                                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Critical Difference from Write

The Edit tool's input structure is different:
```json
// Write tool input
{"file_path": "...", "content": "full file content"}

// Edit tool input
{"file_path": "...", "old_string": "...", "new_string": "..."}
```

The current `check_before_write.py` looks for `content` or `file_text` keys:
```python
content = tool_input.get("content") or tool_input.get("file_text")
if not filepath or not content:
    return "ALLOW"  # Can't check, so allow
```

**Result:** Edit operations typically pass through without registry check because the content isn't in the expected keys.

---

## Scenario 3: Writing a New Python Script

### What Claude Code Sends

```json
{
  "tool": "Write",
  "file_path": "/Users/jeremyserna/PrimitiveEngine/scripts/new_script.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Script docstring.\"\"\"\n\nfrom architect_central_services import get_logger\n\nlogger = get_logger(__name__)\n\ndef main():\n    pass\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

### Step-by-Step Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 3: WRITE NEW PYTHON SCRIPT                                        │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Step 1: Claude Code prepares Write tool call                              │
│          └─ file_path: "/path/to/new_script.py"                            │
│          └─ content: "#!/usr/bin/env python3\n..."                         │
│                                                                            │
│  Step 2: PreToolUse hooks fire                                             │
│          │                                                                 │
│          └─▶ check_before_write.sh                                         │
│              │                                                             │
│              └─▶ check_before_write.py                                     │
│                  │                                                         │
│                  ├─ Parse CLAUDE_TOOL_INPUT JSON                           │
│                  ├─ Extract file_path and content                          │
│                  ├─ Check extension (.py is tracked)                       │
│                  ├─ Check skip directories                                 │
│                  │                                                         │
│                  └─▶ registry_service.check_before_write()                 │
│                      │                                                     │
│                      ├─ Hash content (SHA256)                              │
│                      ├─ Query DuckDB: exact hash match?                    │
│                      ├─ Query DuckDB VSS: semantic similarity?             │
│                      │   └─ 1024-dim local embedding                       │
│                      │   └─ Compare against registered Python files        │
│                      │                                                     │
│                      └─ Decision: ALLOW or BLOCK                           │
│                                                                            │
│  Step 3: Decision                                                          │
│          └─ ALLOW or BLOCK                                                 │
│                                                                            │
│  Step 4: Write executes                                                    │
│          └─ Python file is written to disk                                 │
│                                                                            │
│  Step 5: PostToolUse hooks fire                                            │
│          │                                                                 │
│          └─▶ claude-organize                                               │
│              └─ Catalogs the new Python file                               │
│                                                                            │
│  Step 6: Complete                                                          │
│                                                                            │
│  ════════════════════════════════════════════════════════════════════════  │
│  NOTE: At this point the script EXISTS but has NOT BEEN EXECUTED.          │
│  Execution triggers DIFFERENT hooks (smart_validate.sh, etc.)              │
│  ════════════════════════════════════════════════════════════════════════  │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Python-Specific Considerations

When writing Python scripts, the registry check also considers:
- Code pattern similarity (not just text similarity)
- Whether similar utility scripts already exist
- The 85% semantic similarity threshold applies to code too

---

## Scenario 4: Editing an Existing Python Script

### What Claude Code Sends

```json
{
  "tool": "Edit",
  "file_path": "/Users/jeremyserna/PrimitiveEngine/scripts/existing_script.py",
  "old_string": "def old_function():\n    pass",
  "new_string": "def new_function():\n    logger.info(\"Hello\")\n    return True"
}
```

### Step-by-Step Flow

```
┌────────────────────────────────────────────────────────────────────────────┐
│ SCENARIO 4: EDIT EXISTING PYTHON SCRIPT                                    │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Step 1: Claude Code prepares Edit tool call                               │
│          └─ file_path: "/path/to/existing_script.py"                       │
│          └─ old_string: "def old_function():..."                           │
│          └─ new_string: "def new_function():..."                           │
│                                                                            │
│  Step 2: PreToolUse hooks fire                                             │
│          │                                                                 │
│          └─▶ check_before_write.sh                                         │
│              │                                                             │
│              └─▶ check_before_write.py                                     │
│                  │                                                         │
│                  ├─ Parse CLAUDE_TOOL_INPUT JSON                           │
│                  ├─ Look for "content" or "file_text"                      │
│                  ├─ NOT FOUND (Edit uses old_string/new_string)            │
│                  │                                                         │
│                  └─ Return "ALLOW" (can't check partial content)           │
│                                                                            │
│  Step 3: Edit executes                                                     │
│          └─ Find old_string in file                                        │
│          └─ Replace with new_string                                        │
│          └─ Save file                                                      │
│                                                                            │
│  Step 4: PostToolUse hooks fire                                            │
│          │                                                                 │
│          └─▶ claude-organize                                               │
│                                                                            │
│  Step 5: Complete                                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

### Key Insight: Edit Tool Bypasses Registry Check

Because the Edit tool uses `old_string`/`new_string` instead of `content`, the registry service does not currently check Edit operations. This is a **known gap**.

**Why this might be intentional:**
- Edits are usually small, targeted changes
- Checking partial replacements against full-document embeddings doesn't make sense
- The full file already exists and was presumably checked when written

**Potential risk:**
- Could theoretically replace entire file content via Edit without duplicate check
- But Edit requires `old_string` to exist, so it can't create from scratch

---

## Separate Flow: Executing a Python Script

This is NOT a Write/Edit operation. It uses the Bash tool.

```
┌────────────────────────────────────────────────────────────────────────────┐
│ EXECUTING A PYTHON SCRIPT (Bash tool)                                      │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Step 1: Claude Code prepares Bash tool call                               │
│          └─ command: "python3 /path/to/script.py"                          │
│                                                                            │
│  Step 2: PreToolUse hooks fire (matcher: "Bash")                           │
│          │                                                                 │
│          └─▶ smart_validate.sh                                             │
│              │                                                             │
│              ├─ Only fires for python*.py commands                         │
│              ├─ Skip if path contains /tests/ or /hooks/                   │
│              ├─ Check cache: /tmp/claude_validation_cache/{md5_hash}       │
│              │   └─ If cached PASS → exit 0 immediately                    │
│              │                                                             │
│              ├─ TRIAGE (grep, no Claude):                                  │
│              │   └─ Scan for: bigquery, delete, drop, loops, shell         │
│              │   └─ No risky patterns? → PASS, cache, exit 0               │
│              │                                                             │
│              ├─ CLASSIFICATION (claude -p, ~200 tokens):                   │
│              │   └─ "Does this use get_bigquery_client()?"                 │
│              │   └─ "Any loops over queries without limits?"               │
│              │   └─ Returns: SAFE or UNSAFE                                │
│              │   └─ If SAFE → PASS, cache, exit 0                          │
│              │                                                             │
│              └─ FULL VALIDATION (claude -p, ~500 tokens):                  │
│                  └─ Check COST PROTECTION                                  │
│                  └─ Check LOOP SAFETY                                      │
│                  └─ Check DELETE SAFETY                                    │
│                  └─ Check LOGGING (get_logger not print)                   │
│                  └─ Check IDENTITY (generate_*_id not UUID)                │
│                  └─ Returns: PASS or FAIL                                  │
│                  └─ Cache result, exit 0 (warning if FAIL)                 │
│                                                                            │
│  Step 3: Script executes                                                   │
│          └─ Python process runs                                            │
│          └─ Output captured                                                │
│          └─ Exit code recorded                                             │
│                                                                            │
│  Step 4: PostToolUse hooks fire (matcher: "Bash")                          │
│          │                                                                 │
│          └─▶ post_script_framework.sh                                      │
│              │                                                             │
│              ├─ Check CLAUDE_TOOL_EXIT_CODE                                │
│              │                                                             │
│              ├─ IF FAILED (exit != 0):                                     │
│              │   └─ Invoke claude -p to diagnose                           │
│              │   └─ TRUTH: What went wrong?                                │
│              │   └─ CARE: How to fix?                                      │
│              │   └─ MEANING: What should it do?                            │
│              │   └─ May edit the file to fix                               │
│              │                                                             │
│              └─ IF SUCCEEDED:                                              │
│                  └─ Find newly created .py files (< 1 min old)             │
│                  └─ For each without docstring:                            │
│                      └─ generate_frontmatter.py → get entity ID            │
│                      └─ claude -p → fill in TRUTH/CARE/MEANING             │
│                                                                            │
│  Step 5: Complete                                                          │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Hook Files Reference

### PreToolUse Hooks

| Hook | Matcher | File | What It Does |
|------|---------|------|--------------|
| check_before_write.sh | Write\|Edit\|MultiEdit | `.claude/hooks/check_before_write.sh` | Registry similarity check |
| smart_validate.sh | Bash | `.claude/hooks/smart_validate.sh` | Python script validation |

### PostToolUse Hooks

| Hook | Matcher | File | What It Does |
|------|---------|------|--------------|
| claude-organize | Write\|Edit\|MultiEdit | `/opt/homebrew/bin/claude-organize` | Document organization |
| post_script_framework.sh | Bash | `.claude/hooks/post_script_framework.sh` | Script failure diagnosis, frontmatter |

---

## The Registry Service

**Location:** `~/.primitive_engine/registry/document_registry.duckdb`

### Tables

```sql
-- Document records
CREATE TABLE registry_records (
    document_id VARCHAR PRIMARY KEY,    -- e.g., "doc_abc123"
    content_hash VARCHAR NOT NULL,      -- SHA256 of normalized content
    filepath VARCHAR NOT NULL,          -- Canonical absolute path
    approved_at TIMESTAMP NOT NULL,
    approved_by VARCHAR NOT NULL,       -- e.g., "stamp_document"
    has_embedding BOOLEAN DEFAULT FALSE,
    synced_to_cloud BOOLEAN DEFAULT FALSE
);

-- Embeddings for similarity search
CREATE TABLE registry_embeddings (
    content_hash VARCHAR PRIMARY KEY,
    embedding FLOAT[1024] NOT NULL,     -- LOCAL embeddings only!
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_embedding_hnsw ON registry_embeddings USING HNSW (embedding);
```

### Two Embedding Systems (Never Mix)

| System | Service | Dimensions | Storage | Cost |
|--------|---------|------------|---------|------|
| **LOCAL** | `local_embedding_service` | 1024 | DuckDB VSS | FREE |
| **CLOUD** | `embedding_service` | 3072 | BigQuery | $0.075/M tokens |

The registry service **REJECTS** 3072-dim embeddings:
```python
if len(embedding) == 3072:
    raise ValueError("Cannot store cloud embeddings in local registry")
```

---

## Environment Variables

| Variable | When Available | Content |
|----------|----------------|---------|
| `CLAUDE_TOOL_NAME` | PreToolUse, PostToolUse | Tool name: "Write", "Edit", "Bash" |
| `CLAUDE_TOOL_INPUT` | PreToolUse, PostToolUse | JSON of tool parameters |
| `CLAUDE_TOOL_OUTPUT` | PostToolUse only | Tool output (stdout) |
| `CLAUDE_TOOL_EXIT_CODE` | PostToolUse only | Exit code (Bash only) |

---

## Summary Matrix

| Action | PreToolUse | Registry Check? | Tool | PostToolUse |
|--------|------------|-----------------|------|-------------|
| Write MD | check_before_write.sh | YES (full content) | Write | claude-organize |
| Edit MD | check_before_write.sh | NO (content not found) | Edit | claude-organize |
| Write PY | check_before_write.sh | YES (full content) | Write | claude-organize |
| Edit PY | check_before_write.sh | NO (content not found) | Edit | claude-organize |
| Run PY | smart_validate.sh | N/A (validation, not registry) | Bash | post_script_framework.sh |

---

## Known Gaps

1. **Edit operations bypass registry check**: The Edit tool uses `old_string`/`new_string`, not `content`, so the registry can't check the new content for duplicates.

2. **Partial content problem**: Even if Edit passed the new_string, checking a 3-line replacement against full-document embeddings doesn't make semantic sense.

3. **No post-edit registration**: After an Edit, the modified file isn't automatically re-registered with its new hash/embedding.

---

*Document generated: 2026-01-02*
*Primitive: exist-now (documentation)*
