#!/bin/bash
# Install cron job to monitor sync service
# This checks every minute and restarts if needed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MONITOR_SCRIPT="$PROJECT_ROOT/scripts/monitor_sync_service.sh"

# Get current crontab
CRON_TEMP=$(mktemp)
crontab -l > "$CRON_TEMP" 2>/dev/null || true

# Check if monitor already exists
if grep -q "monitor_sync_service.sh" "$CRON_TEMP"; then
    echo "Monitor cron job already exists"
    rm -f "$CRON_TEMP"
    exit 0
fi

# Add monitor cron job (runs every minute)
echo "# Truth Forge Sync Service Monitor - checks every minute" >> "$CRON_TEMP"
echo "* * * * * $MONITOR_SCRIPT >> $PROJECT_ROOT/sync_monitor.log 2>&1" >> "$CRON_TEMP"

# Install new crontab
crontab "$CRON_TEMP"
rm -f "$CRON_TEMP"

echo "✅ Monitor cron job installed"
echo ""
echo "The monitor will:"
echo "  ✅ Check sync service every minute"
echo "  ✅ Restart if it stops"
echo "  ✅ Log to: $PROJECT_ROOT/sync_monitor.log"
echo ""
echo "To view cron jobs:"
echo "  crontab -l"
echo ""
echo "To remove monitor:"
echo "  crontab -e  # Then remove the monitor line"
