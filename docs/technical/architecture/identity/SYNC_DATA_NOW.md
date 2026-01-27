# Sync Data to Twenty CRM - Complete Guide

**Problem**: No data showing in Twenty CRM

**Solution**: Run the sync script to push data from BigQuery to Twenty CRM

---

## Quick Start

### Step 1: Verify Setup

```bash
# Activate virtual environment
source .venv/bin/activate

# Run setup (creates custom fields)
python scripts/setup_twenty_crm.py
```

### Step 2: Sync Data

```bash
# Sync all contacts (recommended)
python scripts/sync_to_twenty_crm_complete.py

# Or sync with limit for testing
python scripts/sync_to_twenty_crm_complete.py --limit 10

# Or sync specific contact
python scripts/sync_to_twenty_crm_complete.py --contact-id 12345
```

---

## What the Script Does

1. **Verifies Setup** - Checks custom fields are created
2. **Tests Connection** - Verifies API key works
3. **Fetches Contacts** - Gets contacts from `identity.contacts_master` in BigQuery
4. **Syncs Each Contact** - Pushes to Twenty CRM with all metadata
5. **Verifies Results** - Confirms contacts appear in CRM

---

## Expected Output

```
============================================================
TWENTY CRM COMPLETE SYNC
============================================================
Initializing Twenty CRM service...
============================================================
VERIFYING SETUP
============================================================
✅ Setup complete!
   Person fields: 35
   Company fields: 7

============================================================
TESTING CONNECTION
============================================================
✅ Connection works! Found 0 existing contacts

============================================================
GETTING CONTACTS FROM BIGQUERY
============================================================
Found 150 contacts in BigQuery

============================================================
SYNCING 150 CONTACTS TO TWENTY CRM
============================================================

[1/150] Syncing contact 12345...
Syncing contact to CRM: John Doe (ID: 12345)
✅ Successfully synced contact John Doe to CRM (CRM ID: abc-123)
  ✅ Synced to CRM! CRM ID: abc-123
  ✅ Verified in CRM: John Doe

...

============================================================
SYNC SUMMARY
============================================================
Total contacts: 150
✅ Successfully synced: 150
❌ Failed: 0

============================================================
VERIFYING IN TWENTY CRM
============================================================
Total contacts in CRM: 150

First 5 contacts in CRM:
  1. John Doe (CRM ID: abc-123, Contact ID: 12345)
  2. Jane Smith (CRM ID: def-456, Contact ID: 12346)
  ...

✅ Data is now in Twenty CRM!
   Check the Twenty CRM UI to see your contacts.
```

---

## Troubleshooting

### No Contacts Found in BigQuery

```python
from google.cloud import bigquery
from truth_forge.core.settings import settings

bq_client = bigquery.Client(project=settings.effective_gcp_project)
query = "SELECT COUNT(*) as count FROM `identity.contacts_master` WHERE is_me = FALSE"
result = list(bq_client.query(query).result())
print(f"Contacts in BigQuery: {result[0].count}")
```

### API Key Issues

```bash
# Check if secret exists
gcloud secrets list --project=flash-clover-464719-g1 | grep twenty

# Verify API key is accessible
python -c "
from truth_forge.services.secret.service import SecretService
service = SecretService()
key = service.get_secret('twenty-crm-api-key')
print(f'API key found: {key[:10]}...' if key else 'API key not found')
"
```

### Sync Errors

Check the error messages in the output. Common issues:
- API key invalid → Check Secret Manager
- Custom fields not created → Run setup script
- Network issues → Check connectivity
- API endpoint wrong → Check `settings.twenty_base_url`

---

## Manual Sync (Python)

```python
from truth_forge.services.sync import TwentyCRMService
from google.cloud import bigquery
from truth_forge.core.settings import settings

bq_client = bigquery.Client(project=settings.effective_gcp_project)

with TwentyCRMService() as service:
    # Get contact IDs
    query = """
    SELECT contact_id
    FROM `identity.contacts_master`
    WHERE is_me = FALSE
    LIMIT 10
    """
    results = list(bq_client.query(query).result())
    contact_ids = [str(row.contact_id) for row in results]
    
    # Sync each contact
    for contact_id in contact_ids:
        print(f"Syncing {contact_id}...")
        result = service.bq_sync.sync_contact_to_all(contact_id)
        
        crm_result = result.get("crm_twenty", {})
        if crm_result.get("status") == "synced":
            print(f"  ✅ Synced! CRM ID: {crm_result.get('crm_id')}")
        else:
            print(f"  ❌ Failed: {crm_result.get('error')}")
```

---

## Verify in Twenty CRM

After syncing:

1. Open Twenty CRM UI
2. Go to People/Contacts section
3. You should see all synced contacts
4. Check custom fields are populated
5. Verify metadata is visible

---

## Next Steps

Once data is synced:

1. **Verify Data** - Check contacts appear in CRM
2. **Test Updates** - Update a contact in CRM, verify sync back
3. **Monitor** - Watch for sync errors
4. **Schedule** - Set up automated sync if needed

---

**Last Updated**: 2026-01-27
