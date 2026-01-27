# Twenty CRM API Reference

**Version**: 1.0.0
**Date**: 2026-01-27

---

## API Endpoints Used

### Base URL
- Default: `https://api.twenty.com`
- Configurable via `settings.twenty_base_url` or `TWENTY_BASE_URL` env var

### Authentication
- Method: Bearer Token
- Header: `Authorization: Bearer <api_key>`
- API key stored in Secret Manager: `twenty-crm-api-key`

---

## Endpoints

### Create Contact (Person)
- **Method**: `POST`
- **Endpoint**: `/api/people`
- **Headers**: 
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+15551234567",
  "customFields": {
    "contact_id": "12345",
    "category_code": "B",
    "first_name": "John",
    "last_name": "Doe",
    ...
  }
}
```

### Update Contact
- **Method**: `PATCH`
- **Endpoint**: `/api/people/{id}`
- **Body**: Same as create

### Get Contact
- **Method**: `GET`
- **Endpoint**: `/api/people/{id}`

### List Contacts
- **Method**: `GET`
- **Endpoint**: `/api/people`
- **Query Params**: `limit`, `updatedAfter`

### Create Company
- **Method**: `POST`
- **Endpoint**: `/api/companies`

### List Companies
- **Method**: `GET`
- **Endpoint**: `/api/companies`

### Create Custom Field
- **Method**: `POST`
- **Endpoint**: `/api/{object_type}-custom-fields`
- **Object Types**: `person`, `company`

### List Custom Fields
- **Method**: `GET`
- **Endpoint**: `/api/{object_type}-custom-fields`

---

## Data Format

### Contact (Person) Format
```json
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "+15551234567",
  "customFields": {
    "contact_id": "12345",
    "first_name": "John",
    "last_name": "Doe",
    "category_code": "B",
    "llm_context": "{\"relationship_arc\": \"...\"}",
    ...
  }
}
```

### Custom Fields
All metadata is stored in `customFields` object:
- Text fields: Direct values
- JSON fields: JSON strings
- Boolean fields: `true`/`false`
- Date fields: ISO format strings

---

## Error Handling

### Common Errors

**401 Unauthorized**
- API key invalid or missing
- Check Secret Manager

**404 Not Found**
- Endpoint doesn't exist
- Check API version/endpoint

**400 Bad Request**
- Invalid data format
- Missing required fields
- Check custom field names

**422 Unprocessable Entity**
- Validation error
- Check field types and values

---

## Testing

### Test API Connection
```python
from truth_forge.services.sync import TwentyCRMClient

with TwentyCRMClient() as client:
    contacts = client.list_contacts(limit=5)
    print(f"Found {len(contacts)} contacts")
```

### Test Create Contact
```python
from truth_forge.services.sync import TwentyCRMClient

with TwentyCRMClient() as client:
    contact = client.create_contact({
        "name": "Test Contact",
        "email": "test@example.com",
        "customFields": {
            "contact_id": "99999",
            "category_code": "X"
        }
    })
    print(f"Created: {contact.get('id')}")
```

---

## Troubleshooting

### No Data in CRM

1. **Check API Key**
   ```bash
   gcloud secrets versions access latest --secret=twenty-crm-api-key --project=flash-clover-464719-g1
   ```

2. **Test Connection**
   ```python
   python scripts/test_twenty_crm_connection.py
   ```

3. **Check Endpoint**
   - Verify `settings.twenty_base_url` is correct
   - Check if API version changed

4. **Check Custom Fields**
   - Run setup: `python scripts/setup_twenty_crm.py`
   - Verify fields exist

5. **Run Sync**
   ```bash
   python scripts/sync_to_twenty_crm_complete.py --limit 1
   ```

---

**Last Updated**: 2026-01-27
