# Execute Sync - Complete Instructions ✅

**Version**: 1.0.0
**Date**: 2026-01-27

---

## 🚀 Execute These Commands Now

### Step 1: Initial Sync (Sync All Existing Data)

```bash
# Activate virtual environment
source .venv/bin/activate

# Sync all contacts from BigQuery to Twenty CRM
python scripts/sync_initial_data.py
```

**What this does**:
- ✅ Fetches all contacts from `identity.contacts_master` in BigQuery
- ✅ Syncs each contact to Twenty CRM with ALL metadata
- ✅ Verifies contacts appear in CRM
- ✅ Shows progress and summary

**Expected time**: ~1-2 minutes per 100 contacts

---

### Step 2: Start Automatic Sync Service

```bash
# Run in foreground (see live output)
python scripts/run_auto_sync.py

# Or run in background (production)
nohup python scripts/run_auto_sync.py > auto_sync.log 2>&1 &
```

**What this does**:
- ✅ Starts continuous sync service
- ✅ Syncs changes every 5 minutes automatically
- ✅ Keeps all layers in sync forever
- ✅ **Never requires manual intervention**

---

## What Happens Automatically

Once the service is running:

### Every 5 Minutes:

1. **BigQuery → All Systems**
   - Checks for contacts modified since last sync
   - Syncs to Twenty CRM, Supabase, Local DB
   - All metadata fields included

2. **Twenty CRM → BigQuery → All**
   - Checks for contacts updated in CRM
   - Syncs to BigQuery first (canonical)
   - Propagates to Supabase, Local DB

3. **Supabase → BigQuery → All**
   - Checks for contacts updated in Supabase
   - Syncs to BigQuery first
   - Propagates to CRM, Local DB

### Result

**All layers stay in sync automatically forever!**

- Change in BigQuery → Automatically syncs to CRM, Supabase, Local
- Change in CRM → Automatically syncs to BigQuery → All systems
- Change in Supabase → Automatically syncs to BigQuery → All systems

---

## Verify It's Working

### Check Logs

```bash
# View live logs
tail -f auto_sync.log

# You should see sync cycles every 5 minutes:
# ============================================================
# SYNC CYCLE - 2026-01-27T10:00:00
# ============================================================
# [1/3] Syncing from BigQuery to all systems...
#   Found 5 contacts to sync from BigQuery
#   ✅ Synced 5/5 contacts from BigQuery
# ...
```

### Check Twenty CRM

1. Open Twenty CRM UI
2. Go to People/Contacts
3. You should see all your contacts
4. Check custom fields are populated
5. Make a change in CRM → It will sync to BigQuery automatically!

### Check Process

```bash
# Verify service is running
ps aux | grep run_auto_sync

# Should show process running
```

---

## Configuration

### Change Sync Interval

```bash
# Every minute (for testing)
python scripts/run_auto_sync.py --interval 60

# Every 10 minutes
python scripts/run_auto_sync.py --interval 600
```

### Change Batch Size

```bash
# Smaller batches
python scripts/run_auto_sync.py --batch-size 50

# Larger batches
python scripts/run_auto_sync.py --batch-size 200
```

---

## Running as a Service

### Systemd (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/truth-forge-sync.service
```

```ini
[Unit]
Description=Truth Forge Auto Sync Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/truth_forge
ExecStart=/path/to/truth_forge/.venv/bin/python scripts/run_auto_sync.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable truth-forge-sync
sudo systemctl start truth-forge-sync
sudo systemctl status truth-forge-sync
```

---

## Status

**✅ Ready to Execute**

Run the commands above and your data will:
- ✅ Sync to Twenty CRM immediately
- ✅ Stay in sync automatically forever
- ✅ Never require manual intervention

**Execute now and your data will be synced automatically!**

---

**Last Updated**: 2026-01-27
