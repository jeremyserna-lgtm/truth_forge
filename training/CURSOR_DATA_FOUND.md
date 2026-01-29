# FOUND: Cursor Chat Data Location

**Source Document**: `/Users/jeremyserna/Desktop/Truth_Engine/.../CURSOR_CHAT_STORAGE_COMPLETE.md`  
**Discovery**: All Cursor conversations stored in `chatSessions` directory

---

## Cursor Data Storage

### Primary Location
**Path**: `~/Library/Application Support/Cursor/User/workspaceStorage/{workspace_id}/chatSessions/*.json`

**What's stored**:
- ✅ Cursor Agents (native)
- ✅ GitHub Copilot (extension)
- ✅ Claude Code (extension) ← THIS IS WHAT WE NEED
- ✅ All other extension agents

**Format**: JSON files (UUID-named)

### How to Distinguish Agents

```python
# From the JSON structure:
{
  "sessionId": "uuid",
  "requests": [
    {
      "agent": {
        "extensionDisplayName": "Claude Code"  # Extension agents
        # OR missing/empty = Cursor Agents (native)
      },
      "responderUsername": "Claude" | "Cursor Agent"
    }
  ]
}
```

---

## Next Steps to Extract Cursor Data

### 1. Find All chatSessions Directories
```bash
find ~/Library/Application\ Support/Cursor/User/workspaceStorage \
  -name "chatSessions" -type d
```

### 2. Extract Claude Code Conversations
Look for JSON files where:
- `agent.extensionDisplayName` = "Claude Code"
- OR `responderUsername` contains "Claude"

### 3. Process into Pipeline
Once extracted:
- Convert to JSONL format
- Upload to GCS bucket
- Run through entity_unified pipeline

---

## The Complete Data Picture (Updated)

### Source 1: ChatGPT/Clara ✅ READY
- 53,697 messages in entity_unified
- 100% enriched

### Source 2: Claude Code (Primary) ⚠️ IN STAGING
- 226,972 messages in `claude_code_stage_3`
- Timeline: Oct 2025 → Jan 2026
- **This is the main profound data**

### Source 3: Cursor Chats (NEW DISCOVERY!) 📁 FOUND
- Stored in `~/Library/Application Support/Cursor/User/workspaceStorage/*/chatSessions/*.json`
- Contains Claude Code extension conversations
- Timeline: October 2024 transition period
- **Fills the gap when you tried Cursor before settling on Claude**

---

## Critical Question

**Do the 227K messages in `claude_code_stage_3` come FROM Cursor chatSessions?**

**Hypothesis**: YES - the stage_3 data was likely extracted from these Cursor chatSessions directories

**To verify**:
1. Check dates in Cursor chatSessions vs claude_code_stage_3
2. Compare message counts
3. Look at content samples

**If TRUE**: The data is already being processed, just needs completion

**If FALSE**: We have TWO separate Claude Code sources to process

---

## Action Plan

### Step 1: Inventory Cursor chatSessions (NOW)
```bash
# Count JSON files
find ~/Library/Application\ Support/Cursor/User/workspaceStorage \
  -path "*/chatSessions/*.json" | wc -l

# Check total size
du -sh ~/Library/Application\ Support/Cursor/User/workspaceStorage/*/chatSessions/
```

### Step 2: Sample Claude Code Conversations
```bash
# Find a Claude Code conversation
# Parse JSON to verify format
# Check dates to compare with stage_3 data
```

### Step 3: Determine Relationship
- Are Cursor chatSessions the SOURCE of claude_code_stage_3?
- Or are they separate data sources?

### Step 4: Extract & Process
**If same source**: Continue processing stage_3  
**If different**: Extract Cursor chats separately

---

## Timeline Impact

### If Cursor = stage_3 Source (Likely)
- No additional extraction needed
- Continue pipeline from stage_3
- 1-2 days to entity_unified

### If Cursor = Separate Source
- Need extraction script
- Process Cursor chats separately
- Add to pipeline
- 2-3 days to entity_unified

---

**Bottom Line**: Found the Cursor data storage location! Now checking if it's already been processed into claude_code_stage_3, or if it's a separate source we need to add to the pipeline.

Investigating now...
