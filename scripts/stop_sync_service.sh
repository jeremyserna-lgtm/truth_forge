#!/bin/bash
# Stop Truth Forge Sync Service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PID_FILE="$PROJECT_ROOT/data/local/sync_service.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Sync service is not running (no PID file found)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "Sync service is not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 0
fi

echo "Stopping sync service (PID: $PID)..."
kill "$PID"

# Wait for process to stop
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Force kill if still running
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Force killing..."
    kill -9 "$PID"
fi

rm -f "$PID_FILE"
echo "✅ Sync service stopped"
