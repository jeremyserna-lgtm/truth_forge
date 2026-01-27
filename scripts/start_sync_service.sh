#!/bin/bash
# Start Truth Forge Sync Service
# This script starts the sync service and ensures it stays running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
LOG_FILE="$PROJECT_ROOT/auto_sync.log"
PID_FILE="$PROJECT_ROOT/data/local/sync_service.pid"

# Create PID directory if it doesn't exist
mkdir -p "$(dirname "$PID_FILE")"

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Sync service already running (PID: $OLD_PID)"
        exit 0
    else
        echo "Removing stale PID file"
        rm -f "$PID_FILE"
    fi
fi

# Activate virtual environment
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

source "$VENV_PATH/bin/activate"

# Set GCP project ID if not set (use project from secret path: 81233637196)
if [ -z "$GCP_PROJECT_ID" ] && [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    export GCP_PROJECT_ID="81233637196"
    export GOOGLE_CLOUD_PROJECT="81233637196"
    echo "Set GCP_PROJECT_ID to 81233637196"
fi

# Start the service
echo "Starting Truth Forge Sync Service..."
cd "$PROJECT_ROOT"
nohup python scripts/run_industry_standard_sync.py > "$LOG_FILE" 2>&1 &
NEW_PID=$!

# Save PID
echo "$NEW_PID" > "$PID_FILE"

echo "✅ Sync service started (PID: $NEW_PID)"
echo "   Logs: $LOG_FILE"
echo "   PID file: $PID_FILE"

# Wait a moment to check if it started successfully
sleep 2
if ps -p "$NEW_PID" > /dev/null 2>&1; then
    echo "✅ Service is running"
    exit 0
else
    echo "❌ Service failed to start. Check logs: $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
