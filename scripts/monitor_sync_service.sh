#!/bin/bash
# Monitor Sync Service - Restarts if it stops
# This script should run as a cron job or LaunchAgent

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/data/local/sync_service.pid"
LOG_FILE="$PROJECT_ROOT/sync_monitor.log"
START_SCRIPT="$SCRIPT_DIR/start_sync_service.sh"

# Check if service is running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        # Service is running
        echo "$(date): ✅ Sync service running (PID: $PID)" >> "$LOG_FILE"
        exit 0
    else
        # PID file exists but process is dead
        echo "$(date): ⚠️  Sync service not running (stale PID: $PID). Restarting..." >> "$LOG_FILE"
        rm -f "$PID_FILE"
    fi
else
    # No PID file - service not running
    echo "$(date): ⚠️  Sync service not running (no PID file). Starting..." >> "$LOG_FILE"
fi

# Restart the service
"$START_SCRIPT" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): ✅ Sync service restarted successfully" >> "$LOG_FILE"
else
    echo "$(date): ❌ Failed to restart sync service" >> "$LOG_FILE"
    exit 1
fi
