# Twenty CRM Complete Metadata Implementation

**Version**: 1.0.0
**Date**: 2026-01-27
**Status**: ✅ Implementation Complete
**Owner**: Jeremy Serna

---

## Executive Summary

Complete implementation of **all contact metadata** into Twenty CRM for comprehensive relationship management across all contact layers.

**What's Implemented**:
1. ✅ **All Contact Metadata Fields** - Name components, organization, notes, birthday, identifiers
2. ✅ **Rich LLM Context** - Full LLM context, communication stats, social network, AI insights, recommendations
3. ✅ **Contact Identifiers** - Email and phone sync from BigQuery
4. ✅ **Bidirectional Sync** - Complete metadata flows both ways
5. ✅ **Relationship Tracking** - People-to-people and people-to-business relationships

---

## Custom Fields Created

### Person (Contact) Fields - Complete Metadata

#### Primary Identifiers
- `contact_id` - Canonical contact ID from BigQuery
- `apple_unique_id` - Apple Contacts ZUNIQUEID
- `apple_identity_unique_id` - Apple Contacts ZIDENTITYUNIQUEID

#### Name Components
- `first_name` - First name
- `last_name` - Last name
- `middle_name` - Middle name
- `nickname` - Nickname
- `name_suffix` - Name suffix (Jr., Sr., III, etc.)
- `title` - Title (Mr., Mrs., Dr., etc.)
- `full_name` - Full name
- `name_normalized` - Normalized name for searching

#### Organization
- `organization` - Organization name
- `job_title` - Job title
- `department` - Department

#### Relationship Categorization
- `category_code` - Relationship category (A-H, X)
- `subcategory_code` - Full subcategory code
- `relationship_category` - Relationship category (family, friend, romantic, etc.)

#### Metadata
- `notes` - Contact notes
- `birthday` - Birthday (DATE field)
- `is_business` - True if business contact (BOOLEAN)
- `is_me` - True if this is Jeremy (BOOLEAN)

#### Rich LLM Data (JSON strings)
- `llm_context` - Rich LLM context data
- `communication_stats` - Communication statistics
- `social_network` - Social network context
- `ai_insights` - AI-generated insights
- `recommendations` - AI recommendations

#### Sync Metadata
- `sync_metadata` - Sync metadata (JSON string)

---

## Data Flow

### BigQuery → Twenty CRM

**Transformation** (`_transform_bq_to_crm_twenty`):
1. Fetches contact from `identity.contacts_master`
2. Fetches identifiers (email, phone) from `identity.contact_identifiers`
3. Maps ALL fields to Twenty CRM format:
   - Core fields → `name`, `email`, `phone`
   - All metadata → `customFields`
   - JSON fields → JSON strings in customFields

**Example**:
```python
{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+15551234567",
    "customFields": {
        "contact_id": "12345",
        "first_name": "John",
        "last_name": "Doe",
        "category_code": "B",
        "subcategory_code": "B1_BEST_FRIENDS",
        "llm_context": '{"relationship_arc": "...", ...}',
        "communication_stats": '{"total_messages": 100, ...}',
        # ... all other fields
    }
}
```

### Twenty CRM → BigQuery

**Transformation** (`_transform_crm_to_canonical`):
1. Fetches contact from Twenty CRM
2. Parses JSON fields from `customFields`
3. Maps ALL fields back to canonical format
4. Updates sync metadata

**Example**:
```python
{
    "contact_id": 12345,
    "canonical_name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "category_code": "B",
    "llm_context": {"relationship_arc": "...", ...},
    "communication_stats": {"total_messages": 100, ...},
    # ... all other fields
}
```

---

## Contact Identifiers Sync

### Email & Phone

**From BigQuery**:
- Fetches primary email and phone from `identity.contact_identifiers`
- Sets in Twenty CRM `email` and `phone` fields
- Also stored in customFields for reference

**To BigQuery**:
- Email and phone from Twenty CRM are synced back
- Stored in `identity.contact_identifiers` table

**Implementation**:
- `_fetch_contact_identifiers()` - Fetches from BigQuery
- `_update_contact_identifiers()` - Updates in Twenty CRM
- Automatic sync during upsert operations

---

## Relationships

### People-to-People Relationships

**Tracking**:
- Relationships stored in `identity.people_relationships` (BigQuery)
- Can be referenced via customFields in Twenty CRM
- Full relationship context available in LLM prompts

**Implementation**:
- `PeopleRelationshipSyncService` handles sync
- Relationship data included in `social_network` customField
- Common connections tracked in `social_network` JSON

### People-to-Business Relationships

**Tracking**:
- Relationships stored in `identity.people_business_relationships` (BigQuery)
- Linked via Twenty CRM company relationships
- Full relationship context available

**Implementation**:
- `RelationshipSyncService` handles sync
- Companies linked to people via Twenty CRM relationships API
- Relationship data in `business_data` customField

---

## Usage Examples

### Sync Contact with All Metadata

```python
from truth_forge.services.sync import BigQuerySyncService, TwentyCRMClient

crm_client = TwentyCRMClient()
bq_sync = BigQuerySyncService(bq_client, supabase, local_db, crm_client)

# Syncs ALL metadata to Twenty CRM
result = bq_sync.sync_contact_to_all("12345")
```

### Update Contact in CRM

```python
from truth_forge.services.sync import TwentyCRMClient

with TwentyCRMClient() as client:
    contact = client.update_contact("crm-id", {
        "name": "John Doe",
        "email": "john@example.com",
        "customFields": {
            "contact_id": "12345",
            "notes": "Updated notes",
            "llm_context": '{"relationship_arc": "Updated arc"}',
        }
    })
```

### Sync from CRM to All Systems

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    # Syncs from CRM to BigQuery, then to all systems
    result = service.sync_contact_from_crm("crm-contact-id")
```

---

## Field Mapping Reference

| BigQuery Field | Twenty CRM Field | Type |
|----------------|------------------|------|
| `contact_id` | `customFields.contact_id` | TEXT |
| `canonical_name` | `name` | TEXT |
| `first_name` | `customFields.first_name` | TEXT |
| `last_name` | `customFields.last_name` | TEXT |
| `email` (from identifiers) | `email` | TEXT |
| `phone` (from identifiers) | `phone` | TEXT |
| `category_code` | `customFields.category_code` | SELECT |
| `subcategory_code` | `customFields.subcategory_code` | TEXT |
| `llm_context` | `customFields.llm_context` | TEXT (JSON) |
| `communication_stats` | `customFields.communication_stats` | TEXT (JSON) |
| `social_network` | `customFields.social_network` | TEXT (JSON) |
| `notes` | `customFields.notes` | TEXT |
| `birthday` | `customFields.birthday` | DATE |

---

## Setup

### 1. Run Setup Script

```bash
python scripts/setup_twenty_crm.py
```

This creates all custom fields listed above.

### 2. Verify Setup

```python
from truth_forge.services.sync import TwentyCRMService

with TwentyCRMService() as service:
    result = service.verify_setup()
    print(result)
```

### 3. Sync Existing Contacts

```python
from truth_forge.services.sync import BigQuerySyncService

# Sync all contacts to Twenty CRM
bq_sync = BigQuerySyncService(bq_client, supabase, local_db, crm_client)
for contact_id in contact_ids:
    bq_sync.sync_contact_to_all(contact_id)
```

---

## Benefits

### Complete Relationship Management
- All contact details visible in one place
- Rich context for every relationship
- Full history and evolution tracking

### LLM Integration
- All LLM context available in CRM
- Dynamic prompting with full context
- AI insights and recommendations visible

### Multi-Source Sync
- Changes in CRM propagate everywhere
- Changes in BigQuery sync to CRM
- Complete alignment across all systems

### Transparency
- All errors reported
- Nothing hidden
- Complete audit trail

---

## Next Steps

1. ✅ **Custom Fields Created** - All metadata fields available
2. ✅ **Transformation Complete** - Full bidirectional mapping
3. ✅ **Identifiers Sync** - Email and phone synced
4. ✅ **Relationships Tracked** - People and business relationships
5. **Test Sync** - Verify all metadata flows correctly
6. **Monitor** - Watch for sync errors and issues

---

**Last Updated**: 2026-01-27
**Version**: 1.0.0
**Status**: ✅ Implementation Complete - Ready for Use
