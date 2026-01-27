# Twenty CRM Quick Start

**Version**: 1.0.0
**Date**: 2026-01-27

---

## Quick Setup

### 1. Store API Key

```bash
# Store in Secret Manager
echo -n "your-api-key" | gcloud secrets create twenty-crm-api-key \
  --data-file=- \
  --project=flash-clover-464719-g1
```

### 2. Run Setup

```bash
python scripts/setup_twenty_crm.py
```

### 3. Verify

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    result = service.verify_setup()
    print(result)
```

---

## Usage Examples

### Sync Contact from CRM

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    result = service.sync_contact_from_crm("crm-contact-id")
    print(result)
```

### Sync Contact to CRM

```python
from truth_forge.services.sync import BigQuerySyncService
from truth_forge.services.sync import TwentyCRMClient
from google.cloud import bigquery

bq_client = bigquery.Client()
crm_client = TwentyCRMClient()

sync = BigQuerySyncService(bq_client, None, None, crm_client)
result = sync.sync_contact_to_all("12345")
```

### Create Contact in CRM

```python
from truth_forge.services.sync import TwentyCRMClient

with TwentyCRMClient() as client:
    contact = client.create_contact({
        "name": "John Doe",
        "email": "john@example.com",
        "customFields": {
            "contact_id": "12345",
            "category_code": "B",
            "subcategory_code": "B1_BEST_FRIENDS"
        }
    })
```

---

## API Key Secret Names

The client tries these secret names (in order):
1. `twenty-crm-api-key`
2. `twenty_api_key`
3. `TWENTY_CRM_API_KEY`
4. `twenty-api-key`

Or environment variables:
- `TWENTY_CRM_API_KEY`
- `TWENTY_API_KEY`

---

## Custom Fields Reference

### Person Fields
- `contact_id` - Canonical ID
- `category_code` - A-H, X
- `subcategory_code` - Full code
- `relationship_category` - Category name
- `llm_context` - JSON string
- `communication_stats` - JSON string
- `social_network` - JSON string
- `ai_insights` - JSON string
- `recommendations` - JSON string
- `sync_metadata` - JSON string

### Company Fields
- `business_id` - Canonical ID
- `industry` - Industry name
- `business_type` - Legal type
- `llm_context` - JSON string
- `business_data` - JSON string
- `relationship_stats` - JSON string
- `sync_metadata` - JSON string

---

**Last Updated**: 2026-01-27
