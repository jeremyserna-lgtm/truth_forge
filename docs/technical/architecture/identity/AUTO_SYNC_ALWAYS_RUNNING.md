# Automatic Sync - Always Running ✅

**Date**: 2026-01-27
**Status**: ✅ Automatic Sync Available

---

## Current State

**The sync system CAN run automatically**, but you need to start it once. After that, it runs continuously without manual intervention.

---

## How Automatic Sync Works

### Auto Sync Service

The `AutoSyncService` runs continuously and:
- ✅ Syncs every 5 minutes automatically
- ✅ Checks for changes in BigQuery, CRM, Supabase
- ✅ Propagates changes to all systems
- ✅ Runs forever until stopped
- ✅ Requires no manual intervention

### Industry Standard Sync

The `IndustryStandardSyncService` combines:
- ✅ CDC change tracking
- ✅ Event-driven real-time sync
- ✅ Polling every 5 minutes
- ✅ All working together automatically

---

## Start Automatic Sync (One Time Setup)

### Option 1: Run in Background

```bash
# Start and leave running
nohup python scripts/run_industry_standard_sync.py > auto_sync.log 2>&1 &
```

This will:
- Start the sync service
- Run in background
- Keep running after you close terminal
- Log to `auto_sync.log`

### Option 2: Run as Systemd Service (Linux)

Create `/etc/systemd/system/truth-forge-sync.service`:

```ini
[Unit]
Description=Truth Forge Automatic Sync Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/truth_forge
Environment="PATH=/path/to/truth_forge/.venv/bin"
ExecStart=/path/to/truth_forge/.venv/bin/python scripts/run_industry_standard_sync.py
Restart=always
RestartSec=10
StandardOutput=append:/path/to/truth_forge/auto_sync.log
StandardError=append:/path/to/truth_forge/auto_sync.log

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable truth-forge-sync
sudo systemctl start truth-forge-sync
sudo systemctl status truth-forge-sync
```

### Option 3: Run as Daemon (macOS)

Create `~/Library/LaunchAgents/com.truthforge.sync.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.truthforge.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/truth_forge/.venv/bin/python</string>
        <string>/path/to/truth_forge/scripts/run_industry_standard_sync.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/truth_forge/auto_sync.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/truth_forge/auto_sync.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.truthforge.sync.plist
launchctl start com.truthforge.sync
```

---

## What Happens Automatically

Once started, the service:

### Every 5 Minutes:
1. ✅ Checks BigQuery for modified contacts
2. ✅ Syncs to Twenty CRM, Supabase, Local DB
3. ✅ Checks Twenty CRM for updated contacts
4. ✅ Syncs to BigQuery → All systems
5. ✅ Checks Supabase for updated contacts
6. ✅ Syncs to BigQuery → All systems

### Real-Time (Event-Driven):
- ✅ Changes detected → Immediate sync
- ✅ Events processed → Automatic propagation
- ✅ No delay for critical changes

### Result:
**All layers stay in sync automatically forever!**

---

## Verify It's Running

### Check Process

```bash
# Check if running
ps aux | grep run_industry_standard_sync

# Or check logs
tail -f auto_sync.log
```

### Check Status

```python
from truth_forge.services.sync import IndustryStandardSyncService

service = IndustryStandardSyncService()
stats = service.get_stats()
print(f"Running: {stats['running']}")
print(f"Last sync: {stats['last_sync_time']}")
```

---

## Monitoring

### View Logs

```bash
# Real-time logs
tail -f auto_sync.log

# Or if using systemd
journalctl -u truth-forge-sync -f
```

### Health Indicators

✅ **Healthy**:
- Process running
- Sync cycles completing
- Contacts being synced
- Low error rate

⚠️ **Issues**:
- Process not running
- No sync cycles
- High error rate
- Last sync time old

---

## Stop Automatic Sync

### If Running in Background

```bash
# Find process
ps aux | grep run_industry_standard_sync

# Kill process
kill <PID>
```

### If Running as Systemd Service

```bash
sudo systemctl stop truth-forge-sync
```

### If Running as LaunchAgent

```bash
launchctl stop com.truthforge.sync
launchctl unload ~/Library/LaunchAgents/com.truthforge.sync.plist
```

---

## Summary

**Yes, it stays synced automatically!**

- ✅ Start once → Runs forever
- ✅ Syncs every 5 minutes automatically
- ✅ Real-time sync for changes
- ✅ No manual intervention needed
- ✅ All layers stay in sync

**You only need to start it once, then it runs automatically forever!**

---

**Last Updated**: 2026-01-27
