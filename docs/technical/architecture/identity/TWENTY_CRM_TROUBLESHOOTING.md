# Twenty CRM Troubleshooting Guide

**Version**: 1.0.0
**Date**: 2026-01-27

---

## Problem: No Records in Twenty CRM

If you don't see any records in Twenty CRM, follow these steps:

---

## Step 1: Test Connection

```bash
python scripts/test_twenty_crm_connection.py
```

This will:
- ✅ Test API connection
- ✅ Check if custom fields are set up
- ✅ List existing contacts
- ✅ Test syncing one contact

---

## Step 2: Verify Setup

### Check Custom Fields

```bash
python scripts/setup_twenty_crm.py
```

This creates all custom fields. If fields already exist, it will skip them.

### Verify Setup

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    result = service.verify_setup()
    print(result)
```

---

## Step 3: Sync Data

### Option A: Sync All Contacts

```bash
# Dry run first (see what would be synced)
python scripts/sync_all_to_twenty_crm.py --dry-run

# Then sync for real
python scripts/sync_all_to_twenty_crm.py

# Or sync with limit for testing
python scripts/sync_all_to_twenty_crm.py --limit 10
```

### Option B: Sync Specific Contact

```bash
python scripts/push_data_through_all_layers.py --contact-id 12345 --verify
```

### Option C: Sync from Python

```python
from truth_forge.services.sync import BigQuerySyncService, TwentyCRMClient
from google.cloud import bigquery
from truth_forge.core.settings import settings

bq_client = bigquery.Client(project=settings.effective_gcp_project)
crm_client = TwentyCRMClient()

# You'll need supabase and local_db clients too
bq_sync = BigQuerySyncService(bq_client, None, None, crm_client)

# Sync one contact
result = bq_sync.sync_contact_to_all("12345")
print(result)
```

---

## Common Issues

### Issue 1: API Key Not Found

**Error**: `ValueError: Twenty CRM API key not found`

**Solution**:
```bash
# Check if secret exists
gcloud secrets list --project=flash-clover-464719-g1 | grep twenty

# Create secret if missing
echo -n "your-api-key" | gcloud secrets create twenty-crm-api-key \
  --data-file=- --project=flash-clover-464719-g1

# Grant access to service account
gcloud secrets add-iam-policy-binding twenty-crm-api-key \
  --member="serviceAccount:your-service-account@flash-clover-464719-g1.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=flash-clover-464719-g1
```

### Issue 2: Custom Fields Not Created

**Error**: Fields missing in CRM

**Solution**:
```bash
# Run setup
python scripts/setup_twenty_crm.py

# Verify
python scripts/verify_twenty_crm_implementation.py
```

### Issue 3: No Contacts in BigQuery

**Error**: No contacts to sync

**Solution**:
```python
from google.cloud import bigquery
from truth_forge.core.settings import settings

bq_client = bigquery.Client(project=settings.effective_gcp_project)
query = "SELECT COUNT(*) as count FROM `identity.contacts_master` WHERE is_me = FALSE"
result = list(bq_client.query(query).result())
print(f"Contacts in BigQuery: {result[0].count}")
```

### Issue 4: Sync Fails Silently

**Error**: No error but no records appear

**Solution**:
```bash
# Run diagnostic
python scripts/test_twenty_crm_connection.py

# Check sync results
python scripts/sync_all_to_twenty_crm.py --limit 1
```

---

## Verification Checklist

- [ ] API key stored in Secret Manager
- [ ] API key accessible (test connection)
- [ ] Custom fields created (run setup)
- [ ] Contacts exist in BigQuery
- [ ] Sync script runs without errors
- [ ] Records appear in Twenty CRM

---

## Quick Start (First Time)

```bash
# 1. Store API key
echo -n "your-api-key" | gcloud secrets create twenty-crm-api-key \
  --data-file=- --project=flash-clover-464719-g1

# 2. Run setup
python scripts/setup_twenty_crm.py

# 3. Test connection
python scripts/test_twenty_crm_connection.py

# 4. Sync data
python scripts/sync_all_to_twenty_crm.py --limit 10

# 5. Verify in CRM
# Check Twenty CRM UI - you should see contacts
```

---

## Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from truth_forge.services.sync import TwentyCRMClient

with TwentyCRMClient() as client:
    contacts = client.list_contacts(limit=5)
    print(f"Found {len(contacts)} contacts")
```

---

## Still Not Working?

1. **Check API Key**: Verify it's valid in Twenty CRM
2. **Check Base URL**: Verify `settings.twenty_base_url` is correct
3. **Check Permissions**: API key needs read/write permissions
4. **Check Logs**: Look for error messages in sync output
5. **Test Manually**: Try creating a contact directly in CRM UI

---

**Last Updated**: 2026-01-27
