"""Pytest fixtures for sync service tests.

Provides comprehensive mocks for:
- BigQuery client
- Supabase client
- Twenty CRM client
- Secret service
- Local database
"""

from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock, patch
import pytest
from datetime import datetime

# Mock BigQuery client
@pytest.fixture
def mock_bq_client() -> Mock:
    """Mock BigQuery client."""
    client = Mock()
    
    # Mock query execution
    query_result = Mock()
    query_result.result.return_value = []
    query_job = Mock()
    query_job.result.return_value = []
    client.query.return_value = query_job
    
    # Mock table operations
    table = Mock()
    table.schema = []
    client.get_table.return_value = table
    client.insert_rows_json.return_value = []
    
    return client


# Mock Supabase client
@pytest.fixture
def mock_supabase_client() -> Mock:
    """Mock Supabase client."""
    client = Mock()
    
    # Mock table operations
    table = Mock()
    table.select.return_value = table
    table.eq.return_value = table
    table.insert.return_value = table
    table.update.return_value = table
    table.upsert.return_value = table
    table.execute.return_value = Mock(data=[])
    
    client.table.return_value = table
    
    return client


# Mock Twenty CRM client
@pytest.fixture
def mock_twenty_crm_client() -> Mock:
    """Mock Twenty CRM API client."""
    client = Mock()
    
    # Mock contact operations
    client.get_contact.return_value = {
        "id": "crm_123",
        "name": {"firstName": "Test", "lastName": "User"},
        "customFields": {"contact_id": "bq_123"},
    }
    client.list_contacts.return_value = [
        {
            "id": "crm_123",
            "name": {"firstName": "Test", "lastName": "User"},
            "customFields": {"contact_id": "bq_123"},
        }
    ]
    client.create_contact.return_value = {
        "id": "crm_new_123",
        "name": {"firstName": "New", "lastName": "Contact"},
    }
    client.update_contact.return_value = {
        "id": "crm_123",
        "name": {"firstName": "Updated", "lastName": "User"},
    }
    client.upsert_contact.return_value = {
        "id": "crm_123",
        "name": {"firstName": "Test", "lastName": "User"},
    }
    
    # Mock company operations
    client.get_company.return_value = {"id": "company_123", "name": "Test Company"}
    client.list_companies.return_value = [{"id": "company_123", "name": "Test Company"}]
    client.create_company.return_value = {"id": "company_new_123", "name": "New Company"}
    
    # Mock custom fields
    client.list_custom_fields.return_value = []
    client.create_custom_field.return_value = {"id": "field_123", "name": "test_field"}
    
    return client


# Mock Secret Service
@pytest.fixture
def mock_secret_service() -> Mock:
    """Mock SecretService."""
    service = Mock()
    # Return a valid API key (not starting with "mock_") by default
    service.get_secret.return_value = "test_api_key_12345"
    service.get_secret_with_variants.return_value = "test_api_key_12345"
    return service


# Mock Local Database
@pytest.fixture
def mock_local_db() -> Mock:
    """Mock local database connection."""
    db = Mock()
    cursor = Mock()
    cursor.execute.return_value = None
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    cursor.rowcount = 0
    db.cursor.return_value = cursor
    db.commit.return_value = None
    return db


# Sample contact data
@pytest.fixture
def sample_contact() -> Dict[str, Any]:
    """Sample contact data from BigQuery."""
    return {
        "contact_id": "contact_mac_123",
        "apple_unique_id": "apple_123",
        "first_name": "John",
        "last_name": "Doe",
        "display_name": "John Doe",
        "canonical_name": "John Doe",
        "full_name": "John Doe",
        "organization": "Test Org",
        "job_title": "Engineer",
        "category_code": "B",
        "subcategory_code": "B1_BEST_FRIENDS",
        "is_business": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "llm_context": {},
        "communication_stats": {},
        "social_network": {},
        "ai_insights": {},
        "recommendations": {},
        "sync_metadata": {},
    }


# Sample CRM contact data
@pytest.fixture
def sample_crm_contact() -> Dict[str, Any]:
    """Sample contact data from Twenty CRM."""
    return {
        "id": "crm_123",
        "name": {"firstName": "John", "lastName": "Doe"},
        "emails": {"primaryEmail": "john@example.com", "additionalEmails": []},
        "phones": {
            "primaryPhoneNumber": "+15551234567",
            "primaryPhoneCountryCode": "US",
            "primaryPhoneCallingCode": "+1",
            "additionalPhones": [],
        },
        "customFields": {
            "contact_id": "contact_mac_123",
            "category_code": "B",
            "subcategory_code": "B1_BEST_FRIENDS",
        },
    }


# Sample business data
@pytest.fixture
def sample_business() -> Dict[str, Any]:
    """Sample business data."""
    return {
        "business_id": "business_123",
        "business_name": "Test Company",
        "industry": "Technology",
        "website": "https://example.com",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }


# Mock settings
@pytest.fixture
def mock_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock settings."""
    mock = Mock()
    mock.effective_gcp_project = "test-project"
    mock.twenty_base_url = "https://api.twenty.com"
    monkeypatch.setattr("truth_forge.core.settings.settings", mock)


# Mock requests for HTTP calls
@pytest.fixture
def mock_requests(monkeypatch: pytest.MonkeyPatch) -> Dict[str, Mock]:
    """Mock requests library.
    
    Returns a dict with 'get', 'post', 'patch', 'put', 'delete' mocks
    that can be configured in tests.
    """
    import requests as requests_module
    
    # Create individual mocks for each method
    get_mock = Mock()
    post_mock = Mock()
    patch_mock = Mock()
    put_mock = Mock()
    delete_mock = Mock()
    
    # Create default response
    default_response = Mock()
    default_response.status_code = 200
    default_response.json.return_value = {"data": {"createPerson": {"id": "crm_123"}}}
    default_response.raise_for_status.return_value = None
    default_response.text = "{}"
    
    # Set defaults
    get_mock.return_value = default_response
    post_mock.return_value = default_response
    patch_mock.return_value = default_response
    put_mock.return_value = default_response
    delete_mock.return_value = default_response
    
    # Create mock module
    class MockRequestsModule:
        def __init__(self) -> None:
            self.exceptions = requests_module.exceptions
            self.get = get_mock
            self.post = post_mock
            self.patch = patch_mock
            self.put = put_mock
            self.delete = delete_mock
    
    mock_module = MockRequestsModule()
    monkeypatch.setattr("truth_forge.services.sync.twenty_crm_client.requests", mock_module)
    
    return {
        "get": get_mock,
        "post": post_mock,
        "patch": patch_mock,
        "put": put_mock,
        "delete": delete_mock,
        "module": mock_module,
    }


# Mock BigQuerySyncService
@pytest.fixture
def mock_bq_sync() -> Mock:
    """Mock BigQuerySyncService for testing."""
    service = Mock()
    service.sync_contact_to_all.return_value = {"status": "synced"}
    return service
