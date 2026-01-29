#!/bin/bash
# Sync AI Conversation JSONL files from local to GCS bucket
# This script syncs ~/.claude/projects/*.jsonl to gs://claude_code_pipeline_source/data_pipelines/ai_conversations/claude_code/

set -e  # Exit on error

# Configuration
LOCAL_SOURCE_DIR="${HOME}/.claude/projects"
GCS_BUCKET="gs://claude_code_pipeline_source/data_pipelines/ai_conversations"
LOG_FILE="${HOME}/.claude-code-sync.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "${GREEN}Starting AI Conversations sync to GCS...${NC}"

# Check if local directory exists
if [ ! -d "$LOCAL_SOURCE_DIR" ]; then
    log "${YELLOW}Warning: Local source directory does not exist: $LOCAL_SOURCE_DIR${NC}"
    log "Creating directory..."
    mkdir -p "$LOCAL_SOURCE_DIR"
    log "${GREEN}Directory created. Add JSONL files to this directory.${NC}"
    exit 0
fi

# Check if gsutil is installed
if ! command -v gsutil &> /dev/null; then
    log "${RED}Error: gsutil is not installed.${NC}"
    log "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
if ! gsutil ls "$GCS_BUCKET" &> /dev/null; then
    log "${RED}Error: Cannot access GCS bucket. Authenticate with: gcloud auth login${NC}"
    exit 1
fi

# Count files before sync
LOCAL_COUNT=$(find "$LOCAL_SOURCE_DIR" -name "*.jsonl" -type f | wc -l | tr -d ' ')

if [ "$LOCAL_COUNT" -eq 0 ]; then
    log "${YELLOW}No JSONL files found in $LOCAL_SOURCE_DIR${NC}"
    log "Add JSONL files to this directory and run the sync again."
    exit 0
fi

log "Found $LOCAL_COUNT JSONL file(s) to sync"

# Sync files to GCS (rsync only uploads new/changed files - automatic deduplication)
# Sync to claude_code subdirectory
log "Syncing Claude Code files to $GCS_BUCKET/claude_code/..."
log "Note: rsync automatically skips files that already exist (deduplication)"
gsutil -m rsync -r -x ".*" "$LOCAL_SOURCE_DIR" "$GCS_BUCKET/claude_code/" 2>&1 | tee -a "$LOG_FILE"

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    log "${GREEN}Sync completed successfully!${NC}"
    
    # Count files in GCS
    GCS_COUNT=$(gsutil ls "$GCS_BUCKET/claude_code/**/*.jsonl" 2>/dev/null | wc -l | tr -d ' ')
    log "Files in GCS bucket: $GCS_COUNT"
    
    log "${GREEN}BigQuery pipeline will automatically process new files.${NC}"
else
    log "${RED}Sync failed. Check the log file: $LOG_FILE${NC}"
    exit 1
fi
