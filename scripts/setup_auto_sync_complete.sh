#!/bin/bash
# Complete Setup for Automatic Sync Service
# This script:
# 1. Starts the sync service
# 2. Installs LaunchAgent (auto-start on login)
# 3. Installs monitor cron (restart if stops)
# 4. Verifies everything is working

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "============================================================"
echo "COMPLETE AUTO SYNC SETUP"
echo "============================================================"
echo ""

# Step 1: Start sync service
echo "Step 1: Starting sync service..."
"$SCRIPT_DIR/start_sync_service.sh"
if [ $? -ne 0 ]; then
    echo "❌ Failed to start sync service"
    exit 1
fi
echo ""

# Step 2: Install LaunchAgent
echo "Step 2: Installing LaunchAgent (auto-start on login)..."
"$SCRIPT_DIR/install_launch_agent.sh"
if [ $? -ne 0 ]; then
    echo "⚠️  Failed to install LaunchAgent (may need manual setup)"
fi
echo ""

# Step 3: Install monitor cron
echo "Step 3: Installing monitor cron (restart if stops)..."
"$SCRIPT_DIR/install_monitor_cron.sh"
if [ $? -ne 0 ]; then
    echo "⚠️  Failed to install monitor cron (may need manual setup)"
fi
echo ""

# Step 4: Verify
echo "Step 4: Verifying setup..."
echo ""

# Check if service is running
if [ -f "$PROJECT_ROOT/data/local/sync_service.pid" ]; then
    PID=$(cat "$PROJECT_ROOT/data/local/sync_service.pid")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "✅ Sync service is running (PID: $PID)"
    else
        echo "❌ Sync service PID file exists but process not running"
    fi
else
    echo "❌ Sync service PID file not found"
fi

# Check LaunchAgent
if launchctl list | grep -q "com.truthforge.sync"; then
    echo "✅ LaunchAgent is loaded"
else
    echo "⚠️  LaunchAgent not loaded (may need manual load)"
fi

# Check cron
if crontab -l 2>/dev/null | grep -q "monitor_sync_service.sh"; then
    echo "✅ Monitor cron job is installed"
else
    echo "⚠️  Monitor cron job not found (may need manual install)"
fi

echo ""
echo "============================================================"
echo "SETUP COMPLETE"
echo "============================================================"
echo ""
echo "The sync service will now:"
echo "  ✅ Run continuously"
echo "  ✅ Start automatically on login"
echo "  ✅ Restart automatically if it stops"
echo ""
echo "Monitor logs:"
echo "  tail -f $PROJECT_ROOT/auto_sync.log"
echo "  tail -f $PROJECT_ROOT/sync_monitor.log"
echo ""
