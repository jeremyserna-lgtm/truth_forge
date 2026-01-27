# Automatic Sync Setup - No Manual Intervention Required ✅

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: ✅ Complete - Automatic Sync Ready

---

## Overview

The automatic sync service keeps **all layers** in sync automatically:
- ✅ BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local DB
- ✅ Runs continuously
- ✅ Requires no manual intervention
- ✅ Handles all changes automatically

---

## Quick Start

### Step 1: Initial Sync (One Time)

```bash
# Sync all existing data
python scripts/sync_initial_data.py
```

### Step 2: Start Auto Sync Service

```bash
# Run in foreground (for testing)
python scripts/run_auto_sync.py

# Or run in background
nohup python scripts/run_auto_sync.py > auto_sync.log 2>&1 &
```

### Step 3: Verify

The service will:
- ✅ Sync changes every 5 minutes (configurable)
- ✅ Keep all layers in sync automatically
- ✅ Log all activity
- ✅ Handle errors gracefully

---

## How It Works

### Sync Cycle (Every 5 Minutes)

1. **BigQuery → All Systems**
   - Checks for contacts modified since last sync
   - Syncs to Twenty CRM, Supabase, Local DB

2. **Twenty CRM → BigQuery → All**
   - Checks for contacts updated in CRM
   - Syncs to BigQuery first (canonical)
   - Then propagates to all systems

3. **Supabase → BigQuery → All**
   - Checks for contacts updated in Supabase
   - Syncs to BigQuery first
   - Then propagates to all systems

### Result

**All layers stay in sync automatically!**

---

## Configuration

### Sync Interval

Default: 5 minutes (300 seconds)

Change with `--interval`:
```bash
python scripts/run_auto_sync.py --interval 60  # Every minute
python scripts/run_auto_sync.py --interval 600  # Every 10 minutes
```

### Batch Size

Default: 100 contacts per batch

Change with `--batch-size`:
```bash
python scripts/run_auto_sync.py --batch-size 50
```

---

## Running as a Service

### Systemd Service (Linux)

Create `/etc/systemd/system/truth-forge-sync.service`:

```ini
[Unit]
Description=Truth Forge Auto Sync Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/truth_forge
Environment="PATH=/path/to/truth_forge/.venv/bin"
ExecStart=/path/to/truth_forge/.venv/bin/python scripts/run_auto_sync.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable truth-forge-sync
sudo systemctl start truth-forge-sync
sudo systemctl status truth-forge-sync
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

CMD ["python", "scripts/run_auto_sync.py"]
```

### Cloud Run / Cloud Functions

Deploy as a long-running service or scheduled function.

---

## Monitoring

### Check Status

```python
from truth_forge.services.sync.auto_sync_service import AutoSyncService

service = AutoSyncService()
stats = service.get_stats()
print(f"Running: {stats['running']}")
print(f"Total synced: {stats['total_synced']}")
print(f"Last sync: {stats['last_sync_time']}")
```

### View Logs

```bash
# If running in background
tail -f auto_sync.log

# Or if using systemd
journalctl -u truth-forge-sync -f
```

### Health Check

The service logs stats every cycle. Check for:
- ✅ Sync cycles completing
- ✅ Contacts being synced
- ⚠️ Errors (should be minimal)

---

## Webhook Support (Future)

For real-time sync, webhooks can be configured:

### Twenty CRM Webhooks
- Configure in Twenty CRM settings
- Point to webhook endpoint
- Triggers immediate sync on changes

### Supabase Webhooks
- Configure in Supabase dashboard
- Database webhooks for INSERT/UPDATE/DELETE
- Triggers immediate sync

---

## Troubleshooting

### Service Not Running

```bash
# Check if process is running
ps aux | grep run_auto_sync

# Check logs
tail -f auto_sync.log
```

### No Syncs Happening

1. **Check API Key**
   ```bash
   gcloud secrets versions access latest --secret=twenty-crm-api-key
   ```

2. **Check Connection**
   ```bash
   python scripts/test_twenty_crm_connection.py
   ```

3. **Check Logs**
   - Look for error messages
   - Check sync cycle completion

### High Error Rate

- Check error messages in logs
- Verify all systems are accessible
- Check API rate limits
- Verify data formats

---

## Status

**✅ Automatic Sync Ready**

- Service implemented
- Runs continuously
- Keeps all layers in sync
- No manual intervention required

**Start the service and it will keep everything in sync automatically!**

---

**Last Updated**: 2026-01-27
