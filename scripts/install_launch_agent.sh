#!/bin/bash
# Install LaunchAgent for automatic sync service
# This makes the service start automatically on login

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
PYTHON_PATH="$VENV_PATH/bin/python"
SYNC_SCRIPT="$PROJECT_ROOT/scripts/run_industry_standard_sync.py"
LOG_FILE="$PROJECT_ROOT/auto_sync.log"
PLIST_FILE="$HOME/Library/LaunchAgents/com.truthforge.sync.plist"

# Verify paths exist
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Python not found at $PYTHON_PATH"
    exit 1
fi

if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "Error: Sync script not found at $SYNC_SCRIPT"
    exit 1
fi

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create plist file
cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.truthforge.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SYNC_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_FILE</string>
    <key>StandardErrorPath</key>
    <string>$LOG_FILE</string>
    <key>WorkingDirectory</key>
    <string>$PROJECT_ROOT</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$VENV_PATH/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>GCP_PROJECT_ID</key>
        <string>81233637196</string>
        <key>GOOGLE_CLOUD_PROJECT</key>
        <string>81233637196</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ LaunchAgent created: $PLIST_FILE"

# Load the LaunchAgent
launchctl load "$PLIST_FILE" 2>/dev/null || launchctl load -w "$PLIST_FILE"

if [ $? -eq 0 ]; then
    echo "✅ LaunchAgent loaded successfully"
    echo ""
    echo "The sync service will now:"
    echo "  ✅ Start automatically on login"
    echo "  ✅ Restart automatically if it stops"
    echo "  ✅ Run continuously in the background"
    echo ""
    echo "To check status:"
    echo "  launchctl list | grep truthforge"
    echo ""
    echo "To unload (stop auto-start):"
    echo "  launchctl unload $PLIST_FILE"
else
    echo "⚠️  Failed to load LaunchAgent. You may need to:"
    echo "  launchctl load -w $PLIST_FILE"
fi
