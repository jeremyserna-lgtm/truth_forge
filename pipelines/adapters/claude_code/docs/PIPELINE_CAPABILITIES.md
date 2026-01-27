# Pipeline Capabilities - What You Can Do

**Based on Stage 0 discovery and pipeline implementation**

This document lists all the capabilities the pipeline now supports based on what Stage 0 found in your data.

**Spine / entity_unified alignment:** See `SPINE_LEVEL_DEFINITIONS.md` for canonical L5/L7/L8 definitions.  
**ID alignment & registration:** See `ENTITY_UNIFIED_ID_ALIGNMENT.md` for entity_unified ↔ Primitive.identity and `register_spine_entities.py`.

- **L8 = Conversations** — We construct L8 by grouping messages by `session_id`. One L8 per session.
- **L7 = Auto-compact boundaries** — We construct L7 from `subtype` = `compact_boundary` / `microcompact_boundary`. L7 = "which Claude" (identity boundary).
- **L6 = Turns** — A turn is a **full interaction round** (not 1:1). Contains full set of user messages + full set of assistant messages + full set of thinking blocks for that turn. Messages (L5) are children of turns (L6).
- **L5 = Message** — User message + assistant message + thinking block are **each a separate L5 entity**. Use `message_type` / `l5_type` to analyze thinking vs visible answers. Matches spine; usable in analysis.

---

## ✅ 1. Group Messages into Conversations (Session IDs) → L8

**What's there:**
- 72,442 messages with `sessionId` field
- Messages are clustered by `session_id` in BigQuery for fast queries

**What you can do:**
- Query all messages in a conversation: `WHERE session_id = '...'`
- Track conversation length, topics, and patterns over time
- Analyze conversation flow and structure
- Count messages per conversation

**Spine:** This is how we construct **L8 (Conversations)**. One L8 per unique `session_id`. Pipeline groups by `session_id` to create L8 entities for entity_unified.

**Fields available:**
- `session_id` (STRING, REQUIRED) - Groups messages into conversations
- Clustered in Stage 2 for fast queries

---

## ✅ 2. Reconstruct Exact Reply Chains (UUID/Parent UUID)

**What's there:**
- 70,861 messages with `parentUuid` field
- 70,861 messages with `uuid` field
- 274 messages with `logicalParentUuid` (cross-compaction linking)

**What you can do:**
- Build thread views showing who answered whom
- Measure conversation depth (how many replies deep)
- Detect broken threads (missing parent_uuid links)
- Reconstruct exact conversation flow
- Link messages across compaction boundaries using `logical_parent_uuid`

**Fields available:**
- `uuid` (STRING) - Unique message ID from source
- `parent_uuid` (STRING) - Links to parent message (direct reply chain)
- `logical_parent_uuid` (STRING) - Links ACROSS compaction boundaries

**Example query:**
```sql
-- Find all replies to a specific message
SELECT * FROM claude_code_stage_2
WHERE parent_uuid = 'some-uuid'
ORDER BY timestamp
```

---

## ✅ 2b. L7 = Auto-Compact Boundaries

**What's there:**
- Messages with `subtype` = `compact_boundary` or `microcompact_boundary`
- `compactMetadata` (e.g. trigger, preTokens), `logicalParentUuid` for cross-boundary linking

**What you can do:**
- Slice by "which Claude" (identity boundary): each auto-compact = new L7 segment within an L8 conversation
- Compare behavior across compaction segments (e.g. Claude₁ vs Claude₂ in same conversation)
- Use `topic_segment_id` / `compaction_segment_id` (L7 entity_id) in analysis

**Spine:** **L7 = auto-compact boundaries.** We construct L7 from `subtype IN ('compact_boundary', 'microcompact_boundary')`. One L7 per boundary; parent = L8. See `SPINE_LEVEL_DEFINITIONS.md`.

**Fields available:**
- `subtype` (STRING) - compact_boundary, microcompact_boundary
- `compact_metadata` (JSON) - e.g. trigger, preTokens
- `logical_parent_uuid` (STRING) - links across compaction boundaries

---

## ✅ 3. Analyze Thinking Blocks Separately from Visible Answers → L5

**What's there:**
- 10,802 thinking blocks (14.5% of messages)
- Thinking blocks extracted as separate records with `message_type = 'thinking'`
- Text blocks extracted as `message_type = 'assistant'`

**What you can do:**
- Study which conversations had more reasoning (correlate thinking blocks with quality/cost)
- Analyze reasoning quality separately from visible answers
- Search only visible text (exclude thinking blocks)
- Compare thinking vs. visible text length/patterns
- Use thinking blocks for quality and cost analysis

**Spine:** **L5 = user + assistant + thinking** (each a separate L5 entity). Thinking blocks are L5s with `message_type = 'thinking'`; assistant visible text is `message_type = 'assistant'`; user is `message_type = 'user'`. Same hierarchy as entity_unified; use `message_type` / `l5_type` in analysis to slice by type.

**Fields available:**
- `message_type` (STRING) - 'thinking' for thinking blocks, 'assistant' for visible text, 'user' for user
- `content` (STRING) - The actual thinking or text content
- `content_cleaned` (STRING) - Cleaned version for analysis

**Example query:**
```sql
-- Compare thinking vs visible text
SELECT 
  message_type,
  COUNT(*) as count,
  AVG(content_length) as avg_length
FROM claude_code_stage_2
WHERE role = 'assistant'
GROUP BY message_type
```

---

## ✅ 4. Analyze Tool Uses

**What's there:**
- 16,544 tool uses (22.1% of messages)
- Tool name, input, and output extracted

**What you can do:**
- See which tools are used most (e.g. read file, run code)
- Find where tools fail (check tool_output for errors)
- Optimize workflows (identify redundant tool calls)
- Measure tool usage patterns over time
- Correlate tool use with conversation outcomes

**Fields available:**
- `tool_name` (STRING) - Name of the tool used
- `tool_input` (STRING) - JSON input to the tool
- `tool_output` (STRING) - Output from the tool
- `message_type` (STRING) - 'tool_use' for tool calls

**Example query:**
```sql
-- Most used tools
SELECT 
  tool_name,
  COUNT(*) as usage_count
FROM claude_code_stage_2
WHERE tool_name IS NOT NULL
GROUP BY tool_name
ORDER BY usage_count DESC
```

---

## ✅ 5. Use File-History Snapshots (Which Files Were Open When)

**What's there:**
- 2,288 file-history snapshot messages
- Full snapshot data preserved in JSON format

**What you can do:**
- See which files were open when specific messages were sent
- Correlate file context with conversation topics
- Track file usage patterns over time
- Understand project context for each conversation

**Fields available:**
- `is_snapshot` (BOOLEAN) - True for file-history-snapshot messages
- `snapshot_data` (JSON) - Full snapshot data including `trackedFileBackups`

**Example query:**
```sql
-- Find snapshots with file context
SELECT 
  timestamp,
  session_id,
  JSON_EXTRACT_SCALAR(snapshot_data, '$.trackedFileBackups') as files
FROM claude_code_stage_2
WHERE is_snapshot = TRUE
ORDER BY timestamp
```

---

## ✅ 6. Project/Folder Analysis (Context Fields)

**What's there:**
- `cwd` (current working directory) - 70,861 messages
- `git_branch` - 70,861 messages
- `slug` (conversation slug) - 68,158 messages
- `version` (Claude Code version) - 70,861 messages

**What you can do:**
- Analyze behavior by project (slice by `cwd`)
- Track conversations by git branch
- Group by conversation slug (human-readable names)
- Study version-specific patterns

**Fields available:**
- `cwd` (STRING) - Current working directory
- `git_branch` (STRING) - Git branch of conversation
- `slug` (STRING) - Conversation slug (human-readable)
- `version` (STRING) - Claude Code version

---

## ✅ 7. All Other Capabilities

**Additional fields preserved:**
- `model` - Which model was used
- `cost_usd` - Cost per message
- `timestamp` / `timestamp_utc` - When messages were sent
- `content_date` - Date for partitioning
- `fingerprint` - For deduplication
- `is_duplicate` - Duplicate detection
- `subtype` - compact_boundary, microcompact_boundary (L7 detection)
- `compact_metadata` - Auto-compaction metadata
- `is_sidechain` - Sidechain messages

---

## Summary

**All capabilities identified by Stage 0 are now supported:**

1. ✅ **Group messages into conversations** - `session_id` preserved and clustered
2. ✅ **Reconstruct reply chains** - `uuid`, `parent_uuid`, `logical_parent_uuid` preserved
3. ✅ **Analyze thinking blocks separately** - `message_type = 'thinking'` extracted as separate records
4. ✅ **Analyze tool uses** - `tool_name`, `tool_input`, `tool_output` extracted
5. ✅ **Use file-history snapshots** - `snapshot_data` (JSON) and `is_snapshot` preserved
6. ✅ **Project/folder analysis** - `cwd`, `git_branch`, `slug`, `version` preserved

**All fields flow through Stage 1 → Stage 2 and are available for analysis.**
