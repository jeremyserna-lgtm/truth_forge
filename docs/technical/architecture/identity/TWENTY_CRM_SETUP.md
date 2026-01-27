# Twenty CRM Setup & Integration

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: Implementation Complete
**Owner**: Jeremy Serna

---

## Executive Summary

Complete Twenty CRM integration with:
1. **API Client** - Uses API key from secrets manager
2. **Data Model Setup** - Custom fields for contacts, businesses, relationships
3. **Sync Service** - Full bidirectional sync with BigQuery
4. **Error Reporting** - All errors tracked transparently

---

## API Key Configuration

### Secret Manager

The API key is stored in Google Cloud Secret Manager. The client tries these secret names:
1. `twenty-crm-api-key`
2. `twenty_api_key`
3. `TWENTY_CRM_API_KEY`
4. `twenty-api-key`

### Environment Variable Fallback

If not found in secrets manager, falls back to:
- `TWENTY_CRM_API_KEY`
- `TWENTY_API_KEY`

### Base URL

Configured in `settings.twenty_base_url` (default: `https://api.twenty.com`)

---

## Setup Process

### Step 1: Store API Key in Secret Manager

```bash
# Set your project
export PROJECT_ID=flash-clover-464719-g1

# Create secret
echo -n "your-twenty-api-key-here" | gcloud secrets create twenty-crm-api-key \
  --data-file=- \
  --project=$PROJECT_ID

# Grant access (if needed)
gcloud secrets add-iam-policy-binding twenty-crm-api-key \
  --member="serviceAccount:your-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor" \
  --project=$PROJECT_ID
```

### Step 2: Run Setup Script

```bash
python scripts/setup_twenty_crm.py
```

This will:
- Create custom fields for persons (contacts)
- Create custom fields for companies (businesses)
- Verify all fields are set up correctly

### Step 3: Verify Setup

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    result = service.verify_setup()
    print(result)
```

---

## Custom Fields Created

### Person (Contact) Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `contact_id` | TEXT | Canonical contact ID from BigQuery |
| `category_code` | SELECT | Relationship category (A-H, X) |
| `subcategory_code` | TEXT | Full subcategory code |
| `relationship_category` | SELECT | Relationship category (family, friend, etc.) |
| `llm_context` | TEXT | Rich LLM context (JSON string) |
| `communication_stats` | TEXT | Communication statistics (JSON string) |
| `social_network` | TEXT | Social network context (JSON string) |
| `ai_insights` | TEXT | AI insights (JSON string) |
| `recommendations` | TEXT | Recommendations (JSON string) |
| `sync_metadata` | TEXT | Sync metadata (JSON string) |

### Company (Business) Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `business_id` | TEXT | Canonical business ID from BigQuery |
| `industry` | TEXT | Business industry |
| `business_type` | SELECT | Legal business type |
| `llm_context` | TEXT | Rich LLM context (JSON string) |
| `business_data` | TEXT | Business data (JSON string) |
| `relationship_stats` | TEXT | Relationship statistics (JSON string) |
| `sync_metadata` | TEXT | Sync metadata (JSON string) |

---

## Usage

### Initialize Service

```python
from truth_forge.services.sync import TwentyCRMService

# Service automatically gets API key from secrets manager
with TwentyCRMService() as service:
    # Setup (run once)
    service.setup_crm()
    
    # Verify setup
    result = service.verify_setup()
    
    # Sync contact from CRM
    result = service.sync_contact_from_crm("crm-contact-id")
    
    # Sync all from CRM
    result = service.sync_all_from_crm()
```

### Direct Client Usage

```python
from truth_forge.services.sync import TwentyCRMClient

# Client automatically gets API key from secrets manager
with TwentyCRMClient() as client:
    # Get contact
    contact = client.get_contact("contact-id")
    
    # Create contact
    new_contact = client.create_contact({
        "name": "John Doe",
        "email": "john@example.com",
        "customFields": {
            "contact_id": "12345",
            "category_code": "B",
            "subcategory_code": "B1_BEST_FRIENDS"
        }
    })
    
    # Upsert contact
    contact = client.upsert_contact({
        "name": "Jane Doe",
        "customFields": {
            "contact_id": "67890"
        }
    })
```

---

## Data Model Mapping

### Contact Mapping

**BigQuery → Twenty CRM**:
```python
{
    "name": contact["canonical_name"],
    "email": primary_email,  # From contact_identifiers
    "phone": primary_phone,  # From contact_identifiers
    "customFields": {
        "contact_id": str(contact["contact_id"]),
        "category_code": contact.get("category_code"),
        "subcategory_code": contact.get("subcategory_code"),
        "relationship_category": contact.get("relationship_category"),
        "llm_context": json.dumps(contact.get("llm_context", {})),
        "sync_metadata": json.dumps(contact.get("sync_metadata", {}))
    }
}
```

**Twenty CRM → BigQuery**:
```python
{
    "contact_id": int(crm_contact["customFields"]["contact_id"]),
    "canonical_name": crm_contact["name"],
    "category_code": crm_contact["customFields"].get("category_code"),
    # ... map all fields
}
```

### Business Mapping

**BigQuery → Twenty CRM**:
```python
{
    "name": business["business_name"],
    "domainName": business.get("website"),
    "customFields": {
        "business_id": str(business["business_id"]),
        "industry": business.get("industry"),
        "business_type": business.get("business_type"),
        "llm_context": json.dumps(business.get("llm_context", {}))
    }
}
```

---

## Sync Flow

### CRM → BigQuery → All

1. Change made in Twenty CRM
2. `CRMTwentySyncService.sync_from_crm_to_bigquery()` → updates BigQuery
3. `BigQuerySyncService.sync_contact_to_all()` → propagates to all systems

### BigQuery → CRM

1. Change made in BigQuery
2. `BigQuerySyncService._sync_to_crm_twenty()` → updates CRM
3. All custom fields preserved

---

## Error Handling

All errors are reported transparently via `ErrorReporter`:
- Sync failures logged
- Errors stored in `sync_errors` arrays
- Alerts sent to Jeremy
- Nothing hidden

---

## Testing

### Test API Connection

```python
from truth_forge.services.sync import TwentyCRMClient

with TwentyCRMClient() as client:
    contacts = client.list_contacts(limit=5)
    print(f"Found {len(contacts)} contacts")
```

### Test Setup

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    result = service.verify_setup()
    assert result["all_complete"], "Setup incomplete"
```

---

## Troubleshooting

### API Key Not Found

**Error**: `ValueError: Twenty CRM API key not found`

**Solution**:
1. Check secret exists: `gcloud secrets list --project=$PROJECT_ID`
2. Verify secret name matches one of the tried names
3. Check service account has `secretmanager.secretAccessor` role
4. Try environment variable fallback

### Custom Fields Not Created

**Error**: Field creation fails

**Solution**:
1. Check API key has write permissions
2. Verify field name doesn't conflict with existing fields
3. Check Twenty CRM API version compatibility

---

## Next Steps

1. [ ] Store API key in Secret Manager
2. [ ] Run `setup_twenty_crm.py` to create custom fields
3. [ ] Verify setup with `verify_setup()`
4. [ ] Test sync operations
5. [ ] Set up webhooks for real-time sync (optional)

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: Implementation Complete
