# Run Sync Now - Complete Instructions ✅

**Version**: 1.0.0
**Date**: 2026-01-27

---

## Execute These Commands

### 1. Initial Sync (One Time)

```bash
# Activate virtual environment
source .venv/bin/activate

# Sync all existing data
python scripts/sync_initial_data.py
```

**Expected Output**:
```
============================================================
INITIAL SYNC - SYNCING ALL DATA TO TWENTY CRM
============================================================
Fetching contacts from BigQuery...
Found 150 contacts to sync

Progress: 10/150 (synced: 10, errors: 0)
Progress: 20/150 (synced: 20, errors: 0)
...

============================================================
INITIAL SYNC COMPLETE
============================================================
Total contacts: 150
✅ Successfully synced: 150
❌ Errors: 0

Verifying in Twenty CRM...
✅ Total contacts in CRM: 150
```

### 2. Start Auto Sync Service

```bash
# Run in foreground (see output)
python scripts/run_auto_sync.py

# Or run in background
nohup python scripts/run_auto_sync.py > auto_sync.log 2>&1 &
```

**Expected Output**:
```
============================================================
AUTOMATIC SYNC SERVICE
============================================================
Sync interval: 300 seconds
Batch size: 100

This service will:
  - Keep BigQuery ↔ Twenty CRM ↔ Supabase ↔ Local in sync
  - Run automatically every 300 seconds
  - Require no manual intervention
  - Log all activity to auto_sync.log

============================================================
STARTING AUTO SYNC SERVICE
============================================================
✅ Auto sync service started
   Service will keep all layers in sync automatically
   Press Ctrl+C to stop

============================================================
AUTO SYNC SERVICE RUNNING
============================================================
Press Ctrl+C to stop

============================================================
SYNC CYCLE - 2026-01-27T10:00:00
============================================================

[1/3] Syncing from BigQuery to all systems...
  Found 5 contacts to sync from BigQuery
  ✅ Synced 5/5 contacts from BigQuery

[2/3] Syncing from Twenty CRM to BigQuery...
  Found 2 contacts to sync from CRM
  ✅ Synced 2/2 contacts from CRM

[3/3] Syncing from Supabase to BigQuery...
  No changes in Supabase

============================================================
SYNC CYCLE COMPLETE
============================================================
Duration: 12.34s
Synced: 7 records
Total synced (all time): 7
Total errors: 0
Next sync in: 300s
```

---

## Verify Data in Twenty CRM

After initial sync:

1. Open Twenty CRM UI
2. Go to People/Contacts
3. You should see all your contacts
4. Check custom fields are populated
5. Verify metadata is visible

---

## Monitor Auto Sync

```bash
# View logs in real-time
tail -f auto_sync.log

# Check process
ps aux | grep run_auto_sync

# Check stats
python -c "
from truth_forge.services.sync import AutoSyncService
service = AutoSyncService()
print(service.get_stats())
"
```

---

## That's It!

Once started:
- ✅ Service runs continuously
- ✅ Syncs every 5 minutes
- ✅ Keeps all layers in sync
- ✅ **Never requires manual intervention**

**Your data will stay in sync automatically forever!**

---

**Last Updated**: 2026-01-27
