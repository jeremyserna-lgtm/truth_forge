# Complete Automatic Sync Guide ✅

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: ✅ Complete - Ready to Run

---

## Overview

Complete automatic sync system that keeps **all layers** in sync:
- ✅ BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local DB
- ✅ Runs continuously
- ✅ **Never requires manual intervention**
- ✅ Handles all changes automatically

---

## Quick Start (3 Steps)

### Step 1: Initial Sync (One Time)

```bash
# Activate virtual environment
source .venv/bin/activate

# Sync all existing data to Twenty CRM
python scripts/sync_initial_data.py
```

This will:
- ✅ Fetch all contacts from BigQuery
- ✅ Sync each to Twenty CRM with all metadata
- ✅ Verify contacts appear in CRM
- ✅ Show summary

### Step 2: Start Auto Sync Service

```bash
# Run in foreground (for testing/monitoring)
python scripts/run_auto_sync.py

# Or run in background (production)
nohup python scripts/run_auto_sync.py > auto_sync.log 2>&1 &
```

### Step 3: Verify It's Working

```bash
# Check logs
tail -f auto_sync.log

# Check process
ps aux | grep run_auto_sync

# You should see sync cycles every 5 minutes
```

---

## How Automatic Sync Works

### Sync Cycle (Every 5 Minutes)

```
┌─────────────────────────────────────────────┐
│         AUTO SYNC CYCLE (5 min)            │
└─────────────────────────────────────────────┘
              │
              ├─→ [1] BigQuery → All Systems
              │   • Check contacts modified since last sync
              │   • Sync to Twenty CRM, Supabase, Local DB
              │   • All metadata fields included
              │
              ├─→ [2] Twenty CRM → BigQuery → All
              │   • Check contacts updated in CRM
              │   • Sync to BigQuery first (canonical)
              │   • Propagate to Supabase, Local DB
              │
              └─→ [3] Supabase → BigQuery → All
                  • Check contacts updated in Supabase
                  • Sync to BigQuery first
                  • Propagate to CRM, Local DB
```

### Result

**All layers stay in sync automatically!**

- Change in BigQuery → Syncs to CRM, Supabase, Local
- Change in CRM → Syncs to BigQuery → All systems
- Change in Supabase → Syncs to BigQuery → All systems

---

## Configuration

### Sync Interval

Default: 5 minutes (300 seconds)

```bash
# Every minute
python scripts/run_auto_sync.py --interval 60

# Every 10 minutes
python scripts/run_auto_sync.py --interval 600
```

### Batch Size

Default: 100 contacts per batch

```bash
# Smaller batches
python scripts/run_auto_sync.py --batch-size 50

# Larger batches
python scripts/run_auto_sync.py --batch-size 200
```

### Initial Sync

Run initial sync before starting auto sync:

```bash
python scripts/run_auto_sync.py --initial-sync
```

---

## Running as a Service

### Systemd (Linux)

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
ExecStart=/path/to/truth_forge/.venv/bin/python scripts/run_auto_sync.py
Restart=always
RestartSec=10
StandardOutput=append:/path/to/truth_forge/auto_sync.log
StandardError=append:/path/to/truth_forge/auto_sync.log

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

Deploy as a long-running service or scheduled Cloud Function.

---

## Monitoring

### Check Status

```python
from truth_forge.services.sync import AutoSyncService

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

### Health Indicators

✅ **Healthy**:
- Sync cycles completing regularly
- Contacts being synced
- Low error rate
- Last sync time recent

⚠️ **Issues**:
- No sync cycles
- High error rate
- Last sync time old
- Process not running

---

## What Gets Synced Automatically

### From BigQuery
- All contacts modified since last sync
- All metadata fields (30+ fields)
- Contact identifiers (email, phone)
- Relationships (embedded)

### From Twenty CRM
- All contacts updated in CRM
- All custom fields
- Changes propagate to all systems

### From Supabase
- All contacts updated in Supabase
- Changes propagate to all systems

---

## Troubleshooting

### Service Not Running

```bash
# Check if process is running
ps aux | grep run_auto_sync

# Check logs
tail -f auto_sync.log

# Restart if needed
python scripts/run_auto_sync.py
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
   - Verify contacts are being found

### High Error Rate

- Check error messages in logs
- Verify all systems are accessible
- Check API rate limits
- Verify data formats

---

## Status

**✅ Automatic Sync Complete**

- Service implemented
- Scripts ready
- Runs continuously
- Keeps all layers in sync
- **Never requires manual intervention**

**Start the service and it will handle everything automatically!**

---

**Last Updated**: 2026-01-27
