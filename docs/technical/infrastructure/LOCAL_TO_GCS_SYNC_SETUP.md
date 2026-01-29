# Local to GCS Sync Setup

**Created**: 2026-01-28  
**Purpose**: Automatically sync local Claude Code JSONL files to GCS bucket for BigQuery pipeline

---

## 🎯 Overview

Your local files at `~/.claude-code/sessions/*.jsonl` need to be synced to `gs://claude_code_pipeline_source/` so BigQuery can process them.

**Two options:**
1. **Automated cron job** (Recommended - runs automatically)
2. **Manual sync script** (Run when needed)

---

## ✅ Option 1: Automated Cron Job (Recommended)

### Step 1: Make Script Executable

```bash
chmod +x scripts/sync_claude_code_to_gcs.sh
```

### Step 2: Test the Script

```bash
# Run manually to test
./scripts/sync_claude_code_to_gcs.sh
```

**Expected output:**
```
[2026-01-28 10:00:00] Starting Claude Code sync to GCS...
[2026-01-28 10:00:00] Found 5 JSONL file(s) to sync
[2026-01-28 10:00:00] Syncing to gs://claude_code_pipeline_source/...
[2026-01-28 10:00:01] Sync completed successfully!
[2026-01-28 10:00:01] Files in GCS bucket: 5
```

### Step 3: Set Up Cron Job

Add to your crontab to run every hour:

```bash
# Edit crontab
crontab -e

# Add this line (runs every hour at minute 0):
0 * * * * /Users/jeremyserna/truth_forge/scripts/sync_claude_code_to_gcs.sh

# Or run every 15 minutes:
*/15 * * * * /Users/jeremyserna/truth_forge/scripts/sync_claude_code_to_gcs.sh

# Or run daily at 1:00 AM (before BigQuery pipeline at 2:00 AM):
0 1 * * * /Users/jeremyserna/truth_forge/scripts/sync_claude_code_to_gcs.sh
```

**Save and exit.** The cron job is now active.

### Step 4: Verify Cron Job

```bash
# List your cron jobs
crontab -l

# Check cron logs (macOS)
tail -f /var/log/system.log | grep CRON

# Or check the script's log file
tail -f ~/.claude-code-sync.log
```

---

## ✅ Option 2: Manual Sync (When Needed)

### Run the Script Manually

```bash
# From project root
./scripts/sync_claude_code_to_gcs.sh

# Or with full path
/Users/jeremyserna/truth_forge/scripts/sync_claude_code_to_gcs.sh
```

### Or Use gsutil Directly

```bash
# Sync all JSONL files
gsutil -m rsync -r ~/.claude-code/sessions gs://claude_code_pipeline_source/

# Upload a specific file
gsutil cp ~/.claude-code/sessions/my_file.jsonl gs://claude_code_pipeline_source/

# Upload all JSONL files from directory
gsutil -m cp ~/.claude-code/sessions/*.jsonl gs://claude_code_pipeline_source/
```

---

## 🔧 Prerequisites

### 1. Install Google Cloud SDK

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Authenticate

```bash
# Login to Google Cloud
gcloud auth login

# Set default project
gcloud config set project flash-clover-464719-g1

# Verify access to bucket
gsutil ls gs://claude_code_pipeline_source/
```

---

## 📊 Complete Pipeline Flow

```
Local Files (~/.claude-code/sessions/*.jsonl)
    ↓
Cron Job (sync_claude_code_to_gcs.sh) ← Runs automatically
    ↓
GCS Bucket (claude_code_pipeline_source)
    ↓
External Table (claude_code_external) ← Already created
    ↓
Scheduled Query (Transformation) ← You create this
    ↓
entity_unified (Production)
```

---

## 🕐 Recommended Schedule

**Timeline:**
- **1:00 AM UTC**: Cron job syncs local → GCS
- **2:00 AM UTC**: BigQuery scheduled query processes GCS → entity_unified

**Cron schedule:**
```bash
0 1 * * * /Users/jeremyserna/truth_forge/scripts/sync_claude_code_to_gcs.sh
```

This ensures files are synced before BigQuery processes them.

---

## 🔍 Monitoring

### Check Sync Status

```bash
# View sync log
tail -f ~/.claude-code-sync.log

# Check files in GCS
gsutil ls gs://claude_code_pipeline_source/

# Count files
gsutil ls gs://claude_code_pipeline_source/**/*.jsonl | wc -l
```

### Check Local Files

```bash
# Count local JSONL files
find ~/.claude-code/sessions -name "*.jsonl" -type f | wc -l

# List local files
ls -lh ~/.claude-code/sessions/*.jsonl
```

---

## 🆘 Troubleshooting

### "gsutil: command not found"

**Fix**: Install Google Cloud SDK
```bash
brew install google-cloud-sdk
```

### "Access Denied" when syncing

**Fix**: Authenticate and set project
```bash
gcloud auth login
gcloud config set project flash-clover-464719-g1
```

### Cron job not running

**Check**:
1. Is cron service running? (macOS: System Preferences → Security → Full Disk Access)
2. Check cron logs: `tail -f /var/log/system.log | grep CRON`
3. Check script log: `tail -f ~/.claude-code-sync.log`
4. Verify script path in crontab is absolute (not relative)

### Files not syncing

**Check**:
1. Are files actually in `~/.claude-code/sessions/`?
2. Do files have `.jsonl` extension?
3. Check sync log for errors: `cat ~/.claude-code-sync.log`

---

## ✅ Success Criteria

You'll know it's working when:

- [ ] Script runs without errors
- [ ] Files appear in GCS bucket: `gsutil ls gs://claude_code_pipeline_source/`
- [ ] External table shows data: Query `spine.claude_code_external` in BigQuery
- [ ] Cron job runs automatically (check logs)

---

## 📚 Related Documentation

- **GCS Pipeline**: `BIGQUERY_GCS_PIPELINE_COMPLETE.md`
- **BigQuery Setup**: `BIGQUERY_CLAUDE_CODE_GCS_PIPELINE.md`
- **Sync Script**: `scripts/sync_claude_code_to_gcs.sh`

---

*Once this is set up, your local files will automatically sync to GCS, and BigQuery will process them automatically.*
