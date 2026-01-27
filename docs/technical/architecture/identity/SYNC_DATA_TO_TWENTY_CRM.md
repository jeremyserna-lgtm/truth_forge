# How to Sync Data to Twenty CRM

**Problem**: No records showing in Twenty CRM

**Solution**: You need to sync data from BigQuery to Twenty CRM

---

## Quick Steps

### Step 1: Verify Setup

First, make sure custom fields are created:

```bash
# Activate virtual environment
source .venv/bin/activate  # or your venv path

# Run setup (creates custom fields)
python scripts/setup_twenty_crm.py
```

### Step 2: Sync Data

Sync contacts from BigQuery to Twenty CRM:

```bash
# Sync all contacts
python scripts/sync_all_to_twenty_crm.py

# Or sync with limit for testing
python scripts/sync_all_to_twenty_crm.py --limit 10

# Or dry run first to see what would be synced
python scripts/sync_all_to_twenty_crm.py --dry-run
```

### Step 3: Verify in CRM

Check Twenty CRM UI - you should now see contacts!

---

## Alternative: Sync from Python

If scripts don't work, sync directly from Python:

```python
from truth_forge.services.sync import TwentyCRMService
from google.cloud import bigquery
from truth_forge.core.settings import settings

# Initialize
bq_client = bigquery.Client(project=settings.effective_gcp_project)

with TwentyCRMService() as service:
    # Get one contact ID from BigQuery
    query = """
    SELECT contact_id
    FROM `identity.contacts_master`
    WHERE is_me = FALSE
    LIMIT 1
    """
    result = list(bq_client.query(query).result())
    
    if result:
        contact_id = str(result[0].contact_id)
        print(f"Syncing contact {contact_id}...")
        
        # Sync to all systems (including CRM)
        sync_result = service.bq_sync.sync_contact_to_all(contact_id)
        print(f"Result: {sync_result}")
        
        # Check CRM sync
        crm_result = sync_result.get("crm_twenty", {})
        if crm_result.get("status") == "synced":
            print(f"✅ Synced to CRM! CRM ID: {crm_result.get('crm_id')}")
        else:
            print(f"❌ CRM sync failed: {crm_result.get('error')}")
    else:
        print("No contacts found in BigQuery")
```

---

## Troubleshooting

### Issue: API Key Not Found

```bash
# Check if secret exists
gcloud secrets list --project=flash-clover-464719-g1 | grep twenty

# Create if missing
echo -n "your-api-key" | gcloud secrets create twenty-crm-api-key \
  --data-file=- --project=flash-clover-464719-g1
```

### Issue: No Contacts in BigQuery

```python
from google.cloud import bigquery
from truth_forge.core.settings import settings

bq_client = bigquery.Client(project=settings.effective_gcp_project)
query = "SELECT COUNT(*) as count FROM `identity.contacts_master` WHERE is_me = FALSE"
result = list(bq_client.query(query).result())
print(f"Contacts in BigQuery: {result[0].count}")
```

### Issue: Sync Fails

Check the error message. Common issues:
- API key invalid
- Custom fields not created (run setup)
- Network/connection issues
- BigQuery permissions

---

## Manual Sync (One Contact)

```python
from truth_forge.services.sync import BigQuerySyncService, TwentyCRMClient
from google.cloud import bigquery
from truth_forge.core.settings import settings

# Initialize clients
bq_client = bigquery.Client(project=settings.effective_gcp_project)
crm_client = TwentyCRMClient()

# Create sync service
bq_sync = BigQuerySyncService(bq_client, None, None, crm_client)

# Sync one contact (replace with actual contact_id)
contact_id = "12345"  # Your contact ID
result = bq_sync.sync_contact_to_all(contact_id)

print(f"Sync result: {result}")
print(f"CRM status: {result.get('crm_twenty', {}).get('status')}")
```

---

## Verify Records Appeared

After syncing, check Twenty CRM:

1. Open Twenty CRM UI
2. Go to People/Contacts
3. You should see synced contacts
4. Check custom fields are populated

---

## Next Steps

Once data is synced:

1. **Verify Setup**: All custom fields should be visible
2. **Check Data**: Verify contact metadata is correct
3. **Test Updates**: Update a contact in CRM, verify it syncs back
4. **Monitor**: Watch for sync errors

---

**Last Updated**: 2026-01-27
