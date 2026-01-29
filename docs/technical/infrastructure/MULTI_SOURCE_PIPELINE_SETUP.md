# Multi-Source AI Conversations Pipeline

**Created**: 2026-01-28  
**Status**: ✅ **EXTERNAL TABLES CREATED**  
**Sources**: claude_code, chatgpt_web, claude_web, gemini_web, grok_web

---

## 🎯 Overview

This pipeline handles **5 different AI conversation sources**, all syncing to the same GCS bucket structure and loading into `entity_unified`.

---

## 📁 GCS Bucket Structure

```
gs://claude_code_pipeline_source/
└── data_pipelines/
    └── ai_conversations/
        ├── claude_code/      ← Local files from ~/.claude/projects
        ├── chatgpt_web/      ← Emailed files (manual upload)
        ├── claude_web/       ← Emailed files (manual upload)
        ├── gemini_web/       ← Manual upload
        └── grok_web/         ← Manual upload
```

---

## ✅ External Tables Created

All external tables are created and ready:

| Source | External Table | GCS Path |
|--------|---------------|----------|
| `claude_code` | `spine.claude_code_external` | `gs://.../ai_conversations/claude_code/*.jsonl` |
| `chatgpt_web` | `spine.chatgpt_web_external` | `gs://.../ai_conversations/chatgpt_web/*.jsonl` |
| `claude_web` | `spine.claude_web_external` | `gs://.../ai_conversations/claude_web/*.jsonl` |
| `gemini_web` | `spine.gemini_web_external` | `gs://.../ai_conversations/gemini_web/*.jsonl` |
| `grok_web` | `spine.grok_web_external` | `gs://.../ai_conversations/grok_web/*.jsonl` |

**Note**: Tables show "no data" errors until files are uploaded - that's normal!

---

## 🔄 Data Flow

### Claude Code (Local Files)

```
~/.claude/projects/*.jsonl
    ↓
Cron Job (1:00 AM UTC) ← sync_claude_code_to_gcs.sh
    ↓
gs://.../ai_conversations/claude_code/
    ↓
spine.claude_code_external
    ↓
BigQuery Scheduled Query
    ↓
spine.entity_unified
```

### Other Sources (Manual Upload)

```
Emailed/Manual Files
    ↓
Upload to GCS (manual or script)
    ↓
gs://.../ai_conversations/{source}/
    ↓
spine.{source}_external
    ↓
BigQuery Scheduled Query
    ↓
spine.entity_unified
```

---

## 📤 Uploading Files

### Claude Code (Automatic)

The cron job handles this automatically:
- **Schedule**: Daily at 1:00 AM UTC
- **Source**: `~/.claude/projects/`
- **Destination**: `gs://claude_code_pipeline_source/data_pipelines/ai_conversations/claude_code/`

### Other Sources (Manual)

Upload files manually to GCS:

```bash
# ChatGPT Web
gsutil cp your_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/chatgpt_web/

# Claude Web
gsutil cp your_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/claude_web/

# Gemini Web
gsutil cp your_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/gemini_web/

# Grok Web
gsutil cp your_file.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/grok_web/
```

Or upload multiple files:

```bash
# Upload all JSONL files from a directory
gsutil -m cp /path/to/files/*.jsonl gs://claude_code_pipeline_source/data_pipelines/ai_conversations/{source}/
```

---

## 🔍 Querying External Tables

### Check Each Source

```sql
-- Claude Code
SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.claude_code_external`

-- ChatGPT Web
SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.chatgpt_web_external`

-- Claude Web
SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.claude_web_external`

-- Gemini Web
SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.gemini_web_external`

-- Grok Web
SELECT COUNT(*) FROM `flash-clover-464719-g1.spine.grok_web_external`
```

### Query All Sources Together

```sql
-- Union all sources
SELECT 
  'claude_code' as source_pipeline,
  * 
FROM `flash-clover-464719-g1.spine.claude_code_external`

UNION ALL

SELECT 
  'chatgpt_web' as source_pipeline,
  * 
FROM `flash-clover-464719-g1.spine.chatgpt_web_external`

UNION ALL

SELECT 
  'claude_web' as source_pipeline,
  * 
FROM `flash-clover-464719-g1.spine.claude_web_external`

UNION ALL

SELECT 
  'gemini_web' as source_pipeline,
  * 
FROM `flash-clover-464719-g1.spine.gemini_web_external`

UNION ALL

SELECT 
  'grok_web' as source_pipeline,
  * 
FROM `flash-clover-464719-g1.spine.grok_web_external`
```

---

## 🚀 Creating Scheduled Queries

You'll need to create a scheduled query for each source (or one unified query). 

### Option 1: One Query Per Source

Create 5 separate scheduled queries, each processing one source.

### Option 2: Unified Query (Recommended)

Create one scheduled query that processes all sources:

```sql
-- Process all sources into entity_unified
INSERT INTO `flash-clover-464719-g1.spine.entity_unified` (...)
SELECT ... FROM `flash-clover-464719-g1.spine.claude_code_external` s
WHERE ...

UNION ALL

SELECT ... FROM `flash-clover-464719-g1.spine.chatgpt_web_external` s
WHERE ...

-- etc for all sources
```

---

## ✅ Current Status

- [x] External tables created for all 5 sources
- [x] Sync script updated for `~/.claude/projects/`
- [x] GCS bucket structure: `data_pipelines/ai_conversations/{source}/`
- [ ] Scheduled queries need to be created (one per source or unified)

---

## 📚 Next Steps

1. **Upload files** to each GCS path
2. **Verify external tables** show data
3. **Create scheduled queries** (one unified or per source)
4. **Monitor pipeline** runs

---

*All external tables are ready. Just upload files and create the scheduled queries!*
