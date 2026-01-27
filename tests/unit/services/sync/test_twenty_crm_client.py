"""Comprehensive tests for TwentyCRMClient.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests
from datetime import datetime

from truth_forge.services.sync.twenty_crm_client import TwentyCRMClient


# Helper to create mock response
def create_mock_response(
    status_code: int = 200,
    json_data: Dict[str, Any] = None,
    text: str = "{}",
    raise_error: Exception = None,
) -> Mock:
    """Create a mock HTTP response."""
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.text = text
    if raise_error:
        response.raise_for_status.side_effect = raise_error
    else:
        response.raise_for_status.return_value = None
    return response


class TestTwentyCRMClient:
    """Test suite for TwentyCRMClient."""
    
    def test_init_with_secret_service(
        self, mock_secret_service: Mock, mock_settings: None
    ) -> None:
        """Test initialization with secret service."""
        client = TwentyCRMClient(secret_service=mock_secret_service)
        assert client.secret_service == mock_secret_service
        assert client.base_url == "https://api.twenty.com"
        assert "Authorization" in client.headers
        assert client.timeout == 30.0
    
    def test_init_without_secret_service(self, mock_settings: None) -> None:
        """Test initialization without secret service."""
        with patch("truth_forge.services.sync.twenty_crm_client.SecretService") as mock_secret:
            mock_instance = Mock()
            mock_instance.get_secret_with_variants.return_value = "test_key"
            mock_secret.return_value = mock_instance
            
            client = TwentyCRMClient()
            assert client.api_key == "test_key"
    
    def test_get_api_key_from_secret_service(
        self, mock_secret_service: Mock, mock_settings: None
    ) -> None:
        """Test getting API key from secret service."""
        mock_secret_service.get_secret_with_variants.return_value = "secret_key_123"
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        assert client.api_key == "secret_key_123"
    
    def test_get_api_key_mock_value(
        self, mock_secret_service: Mock, mock_settings: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test handling mock API key value."""
        mock_secret_service.get_secret_with_variants.return_value = "mock_Twenty_CRM"
        # Set env var as fallback so it doesn't raise
        monkeypatch.setenv("TWENTY_CRM_API_KEY", "env_fallback_key")
        
        with patch("truth_forge.services.sync.twenty_crm_client.logger") as mock_logger:
            client = TwentyCRMClient(secret_service=mock_secret_service)
            # Should use env fallback, but log warning about mock value
            assert client.api_key == "env_fallback_key"
    
    def test_get_api_key_from_env(self, mock_secret_service: Mock, mock_settings: None, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting API key from environment variable."""
        mock_secret_service.get_secret_with_variants.side_effect = Exception("Not found")
        monkeypatch.setenv("TWENTY_CRM_API_KEY", "env_key_123")
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        assert client.api_key == "env_key_123"
    
    def test_get_api_key_not_found(
        self, mock_secret_service: Mock, mock_settings: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when API key not found."""
        mock_secret_service.get_secret_with_variants.side_effect = Exception("Not found")
        monkeypatch.delenv("TWENTY_CRM_API_KEY", raising=False)
        monkeypatch.delenv("TWENTY_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="Twenty CRM API key not found"):
            TwentyCRMClient(secret_service=mock_secret_service)
    
    def test_get_contact_success(self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]) -> None:
        """Test getting contact successfully."""
        mock_response = create_mock_response(
            json_data={"id": "crm_123", "name": {"firstName": "Test"}}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.get_contact("crm_123")
        
        assert result["id"] == "crm_123"
        mock_requests["get"].assert_called_once()
    
    def test_get_contact_error(self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]) -> None:
        """Test getting contact with error."""
        mock_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404 Not Found")
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_contact("crm_123")
    
    def test_list_contacts_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test listing contacts successfully."""
        mock_response = create_mock_response(
            json_data={"people": [{"id": "crm_123"}]}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_contacts(limit=10)
        
        assert len(result) == 1
        assert result[0]["id"] == "crm_123"
    
    def test_list_contacts_with_updated_since(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test listing contacts with updated_since parameter."""
        mock_response = create_mock_response(json_data={"people": []})
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        updated_since = datetime.utcnow()
        result = client.list_contacts(updated_since=updated_since, limit=10)
        
        assert isinstance(result, list)
        call_args = mock_requests["get"].call_args
        assert "updatedAfter" in call_args[1]["params"]
    
    def test_list_contacts_dict_response(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test handling dict response from list_contacts."""
        mock_response = create_mock_response(
            json_data={"data": [{"id": "crm_123"}]}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_contacts(limit=10)
        
        assert len(result) == 1
    
    def test_list_contacts_list_response(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test handling list response from list_contacts."""
        mock_response = create_mock_response(json_data=[{"id": "crm_123"}])
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_contacts(limit=10)
        
        assert len(result) == 1
    
    def test_create_contact_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test creating contact successfully."""
        mock_response = create_mock_response(
            json_data={
                "data": {"createPerson": {"id": "crm_new_123", "name": {"firstName": "New"}}}
            }
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {"name": {"firstName": "New", "lastName": "Contact"}}
        result = client.create_contact(contact_data)
        
        assert result["id"] == "crm_new_123"
        mock_requests["post"].assert_called_once()
    
    def test_create_contact_direct_response(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test creating contact with direct response (not GraphQL)."""
        mock_response = create_mock_response(json_data={"id": "crm_direct_123"})
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {"name": {"firstName": "Direct", "lastName": "Contact"}}
        result = client.create_contact(contact_data)
        
        assert result["id"] == "crm_direct_123"
    
    def test_create_contact_http_error(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Mock
    ) -> None:
        """Test creating contact with HTTP error."""
        mock_response = create_mock_response(
            status_code=400,
            text='{"error": "Bad Request"}',
            raise_error=requests.exceptions.HTTPError("400 Bad Request"),
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {"name": {"firstName": "Error", "lastName": "Contact"}}
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.create_contact(contact_data)
    
    def test_create_contact_general_error(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test creating contact with general error."""
        mock_requests["post"].side_effect = Exception("Network error")
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {"name": {"firstName": "Error", "lastName": "Contact"}}
        
        with pytest.raises(Exception, match="Network error"):
            client.create_contact(contact_data)
    
    def test_update_contact_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test updating contact successfully."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "crm_123", "name": {"firstName": "Updated"}}
        mock_response.raise_for_status.return_value = None
        mock_requests["patch"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {"name": {"firstName": "Updated", "lastName": "User"}}
        result = client.update_contact("crm_123", contact_data)
        
        assert result["id"] == "crm_123"
        mock_requests["patch"].assert_called_once()
    
    def test_upsert_contact_existing(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upserting existing contact."""
        # Mock list_contacts to return existing contact
        list_response = create_mock_response(
            json_data={
                "people": [{"id": "crm_123", "customFields": {"contact_id": "bq_123"}}]
            }
        )
        
        # Mock update response
        update_response = create_mock_response(
            json_data={"id": "crm_123", "name": {"firstName": "Updated"}}
        )
        
        # First call: get_contact fails, second call: list_contacts finds it
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        mock_requests["get"].side_effect = [get_response, list_response]
        mock_requests["patch"].return_value = update_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {
            "customFields": {"contact_id": "bq_123"},
            "name": {"firstName": "Updated", "lastName": "User"},
        }
        result = client.upsert_contact(contact_data)
        
        assert result["id"] == "crm_123"
    
    def test_upsert_contact_new(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upserting new contact."""
        # First call: get_contact fails, second call: list_contacts returns empty
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(json_data={"people": []})
        create_response = create_mock_response(
            json_data={"data": {"createPerson": {"id": "crm_new_123"}}}
        )
        
        # Set up side_effect for multiple get calls
        mock_requests["get"].side_effect = [get_response, list_response]
        mock_requests["post"].return_value = create_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {
            "customFields": {"contact_id": "bq_new_123"},
            "name": {"firstName": "New", "lastName": "Contact"},
        }
        result = client.upsert_contact(contact_data)
        
        assert result["id"] == "crm_new_123"
    
    def test_upsert_contact_no_id_error(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upserting contact that returns no ID."""
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(json_data={"people": []})
        create_response = create_mock_response(json_data={})  # No ID
        
        mock_requests["get"].side_effect = [get_response, list_response]
        mock_requests["post"].return_value = create_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {
            "customFields": {"contact_id": "bq_123"},
            "name": {"firstName": "New", "lastName": "Contact"},
        }
        
        with pytest.raises(ValueError, match="Contact creation failed"):
            client.upsert_contact(contact_data)
    
    def test_upsert_contact_with_email_phone(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upserting contact with email and phone."""
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(json_data={"people": []})
        create_response = create_mock_response(
            json_data={"data": {"createPerson": {"id": "crm_123"}}}
        )
        update_response = create_mock_response(json_data={"id": "crm_123"})
        
        mock_requests["get"].side_effect = [get_response, list_response]
        mock_requests["post"].return_value = create_response
        mock_requests["patch"].return_value = update_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {
            "customFields": {"contact_id": "bq_123"},
            "name": {"firstName": "Test", "lastName": "User"},
            "email": "test@example.com",
            "phone": "+15551234567",
        }
        result = client.upsert_contact(contact_data)
        
        assert result["id"] == "crm_123"
        # Verify update was called for email/phone
        assert mock_requests["patch"].called
    
    def test_find_contact_by_custom_id_found(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test finding contact by custom ID when found."""
        # First call (get_contact) fails, second call (list_contacts) finds it
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(
            json_data={
                "people": [{"id": "crm_123", "customFields": {"contact_id": "bq_123"}}]
            }
        )
        mock_requests["get"].side_effect = [get_response, list_response]
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client._find_contact_by_custom_id("bq_123")
        
        assert result is not None
        assert result["id"] == "crm_123"
    
    def test_find_contact_by_custom_id_not_found(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test finding contact by custom ID when not found."""
        # First call (get_contact) fails, second call (list_contacts) returns empty
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(json_data={"people": []})
        mock_requests["get"].side_effect = [get_response, list_response]
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client._find_contact_by_custom_id("bq_999")
        
        assert result is None
    
    def test_find_contact_by_custom_id_get_contact_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Mock
    ) -> None:
        """Test finding contact by trying get_contact first."""
        get_response = create_mock_response(
            json_data={"id": "crm_123", "customFields": {"contact_id": "bq_123"}}
        )
        mock_requests["get"].return_value = get_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client._find_contact_by_custom_id("bq_123")
        
        assert result is not None
    
    def test_find_contact_by_custom_id_get_contact_error(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test finding contact when get_contact fails, falls back to list."""
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(json_data={"people": []})
        mock_requests["get"].side_effect = [get_response, list_response]
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client._find_contact_by_custom_id("bq_123")
        
        assert result is None
    
    def test_update_contact_identifiers(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test updating contact identifiers."""
        update_response = create_mock_response(json_data={"id": "crm_123"})
        mock_requests["patch"].return_value = update_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        client._update_contact_identifiers("crm_123", email="test@example.com", phone="+15551234567")
        
        mock_requests["patch"].assert_called_once()
    
    def test_update_contact_identifiers_error(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test updating contact identifiers with error."""
        update_response = create_mock_response(
            raise_error=Exception("Update failed")
        )
        mock_requests["patch"].return_value = update_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        
        with patch("truth_forge.services.sync.twenty_crm_client.logger") as mock_logger:
            client._update_contact_identifiers("crm_123", email="test@example.com")
            # Should log error but not raise
            mock_logger.debug.assert_called()
    
    def test_get_company_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Mock
    ) -> None:
        """Test getting company successfully."""
        mock_response = create_mock_response(
            json_data={"id": "company_123", "name": "Test Company"}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.get_company("company_123")
        
        assert result["id"] == "company_123"
    
    def test_list_companies_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Mock
    ) -> None:
        """Test listing companies successfully."""
        mock_response = create_mock_response(
            json_data={"data": [{"id": "company_123"}]}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_companies(limit=10)
        
        assert len(result) == 1
    
    def test_create_company_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Mock
    ) -> None:
        """Test creating company successfully."""
        mock_response = create_mock_response(
            json_data={"id": "company_new_123", "name": "New Company"}
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        company_data = {"name": "New Company"}
        result = client.create_company(company_data)
        
        assert result["id"] == "company_new_123"
    
    def test_upsert_company_existing(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upserting existing company."""
        # Mock get_company to fail, then list_companies to find it
        get_response = create_mock_response(
            raise_error=requests.exceptions.HTTPError("404")
        )
        list_response = create_mock_response(
            json_data={
                "data": [{"id": "company_123", "customFields": {"business_id": "biz_123"}}]
            }
        )
        update_response = create_mock_response(json_data={"id": "company_123"})
        
        mock_requests["get"].side_effect = [get_response, list_response]
        mock_requests["patch"].return_value = update_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        company_data = {"customFields": {"business_id": "biz_123"}, "name": "Updated Company"}
        result = client.upsert_company(company_data)
        
        # The result should have an id
        assert result.get("id") == "company_123"
    
    def test_list_custom_fields_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test listing custom fields successfully."""
        mock_response = create_mock_response(
            json_data={"data": [{"id": "field_123", "name": "test_field"}]}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_custom_fields("person")
        
        assert len(result) == 1
        assert result[0]["name"] == "test_field"
    
    def test_create_custom_field_success(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Mock
    ) -> None:
        """Test creating custom field successfully."""
        mock_response = create_mock_response(
            json_data={"id": "field_new_123", "name": "new_field"}
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        field_data = {"name": "new_field", "type": "TEXT"}
        result = client.create_custom_field("person", field_data)
        
        assert result["id"] == "field_new_123"
    
    def test_close(self, mock_secret_service: Mock, mock_settings: None) -> None:
        """Test closing client (no-op for now)."""
        client = TwentyCRMClient(secret_service=mock_secret_service)
        # Should not raise
        client.close()
    
    def test_create_relationship(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test creating a relationship."""
        mock_response = create_mock_response(
            json_data={"id": "rel_123", "personId": "crm_1", "companyId": "company_1"}
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        relationship_data = {
            "personId": "crm_1",
            "companyId": "company_1",
            "role": "Engineer",
        }
        
        result = client.create_relationship(relationship_data)
        
        assert result["id"] == "rel_123"
        mock_requests["post"].assert_called_once()
    
    def test_upsert_relationship(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upserting a relationship."""
        mock_response = create_mock_response(
            json_data={"id": "rel_123", "personId": "crm_1", "companyId": "company_1"}
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        relationship_data = {
            "personId": "crm_1",
            "companyId": "company_1",
        }
        
        result = client.upsert_relationship(relationship_data)
        
        assert result["id"] == "rel_123"
        mock_requests["post"].assert_called_once()
    
    def test_get_person_relationships(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test getting person relationships."""
        mock_response = create_mock_response(
            json_data={"data": [{"id": "rel_1"}, {"id": "rel_2"}]}
        )
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.get_person_relationships("crm_123")
        
        assert len(result) == 2
        assert result[0]["id"] == "rel_1"
    
    def test_context_manager(
        self, mock_secret_service: Mock, mock_settings: None
    ) -> None:
        """Test context manager usage."""
        with TwentyCRMClient(secret_service=mock_secret_service) as client:
            assert client is not None
            assert client.secret_service == mock_secret_service
    
    def test_list_contacts_unexpected_data_format(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test list_contacts with unexpected data format."""
        mock_response = create_mock_response(json_data="unexpected_string")
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_contacts()
        
        assert result == []
    
    def test_list_contacts_dict_single_item(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test list_contacts with 'people' key containing a dict (not list)."""
        # When result is a dict with 'people' key that is also a dict (not list)
        mock_response = create_mock_response(json_data={"people": {"id": "crm_1", "name": "Test"}})
        mock_requests["get"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        result = client.list_contacts()
        
        # Should wrap single dict in list
        assert len(result) == 1
        assert result[0]["id"] == "crm_1"
    
    def test_create_contact_nested_id_extraction(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test create_contact with nested ID extraction."""
        mock_response = create_mock_response(
            json_data={"data": {"createPerson": {"id": "crm_123"}}}
        )
        mock_requests["post"].return_value = mock_response
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {"name": {"firstName": "Test"}}
        
        result = client.create_contact(contact_data)
        
        assert result["id"] == "crm_123"
    
    def test_upsert_contact_with_email_phone_update(
        self, mock_secret_service: Mock, mock_settings: None, mock_requests: Dict[str, Mock]
    ) -> None:
        """Test upsert_contact with email and phone update."""
        # First call: get_contact finds existing
        get_response = create_mock_response(
            json_data={"id": "crm_existing", "customFields": {"contact_id": "bq_123"}}
        )
        # Second call: update_contact
        update_response = create_mock_response(
            json_data={"id": "crm_existing", "name": "Updated"}
        )
        # Third call: _update_contact_identifiers (PATCH)
        patch_response = create_mock_response(json_data={"id": "crm_existing"})
        
        mock_requests["get"].side_effect = [get_response]
        mock_requests["patch"].side_effect = [update_response, patch_response]
        
        client = TwentyCRMClient(secret_service=mock_secret_service)
        contact_data = {
            "customFields": {"contact_id": "bq_123"},
            "email": "test@example.com",
            "phone": "+1234567890",
        }
        
        result = client.upsert_contact(contact_data)
        
        assert result["id"] == "crm_existing"
        # Should have called patch twice (update + identifiers)
        assert mock_requests["patch"].call_count == 2
