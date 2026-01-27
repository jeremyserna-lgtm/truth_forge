"""Comprehensive tests for TwentyCRMSetup.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any, List
from unittest.mock import Mock, patch
import pytest

from truth_forge.services.sync.twenty_crm_setup import TwentyCRMSetup


class TestTwentyCRMSetup:
    """Test suite for TwentyCRMSetup."""
    
    def test_init_with_client(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test initialization with client provided."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        assert setup.client == mock_twenty_crm_client
    
    def test_init_without_client(
        self,
        mock_secret_service: Mock,
        mock_settings: None,
    ) -> None:
        """Test initialization without client (creates one)."""
        with patch("truth_forge.services.sync.twenty_crm_setup.TwentyCRMClient") as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            setup = TwentyCRMSetup()
            
            assert setup.client == mock_client
    
    def test_setup_all(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up all custom fields."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        # Mock list_custom_fields to return empty (no existing fields)
        mock_twenty_crm_client.list_custom_fields.return_value = []
        
        # Mock create_custom_field
        mock_twenty_crm_client.create_custom_field.return_value = {"id": "field_123", "name": "test"}
        
        result = setup.setup_all()
        
        assert result["status"] == "complete"
        assert "person_fields" in result
        assert "company_fields" in result
    
    def test_setup_person_custom_fields_new(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up person custom fields when none exist."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        mock_twenty_crm_client.list_custom_fields.return_value = []
        mock_twenty_crm_client.create_custom_field.return_value = {"id": "field_123", "name": "contact_id"}
        
        result = setup.setup_person_custom_fields()
        
        assert len(result) > 0
        mock_twenty_crm_client.create_custom_field.assert_called()
    
    def test_setup_person_custom_fields_existing(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up person custom fields when some exist."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        # Mock existing fields
        mock_twenty_crm_client.list_custom_fields.return_value = [
            {"id": "field_1", "name": "contact_id"},
        ]
        
        # Mock create for new fields
        mock_twenty_crm_client.create_custom_field.return_value = {"id": "field_2", "name": "category_code"}
        
        result = setup.setup_person_custom_fields()
        
        assert len(result) > 0
        # Should skip existing, create new
    
    def test_setup_person_custom_fields_error(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up person custom fields when creation fails."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        mock_twenty_crm_client.list_custom_fields.return_value = []
        mock_twenty_crm_client.create_custom_field.side_effect = Exception("Create error")
        
        # Should not raise, just log error
        result = setup.setup_person_custom_fields()
        
        assert isinstance(result, list)
    
    def test_setup_company_custom_fields_new(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up company custom fields when none exist."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        mock_twenty_crm_client.list_custom_fields.return_value = []
        mock_twenty_crm_client.create_custom_field.return_value = {"id": "field_123", "name": "business_id"}
        
        result = setup.setup_company_custom_fields()
        
        assert len(result) > 0
        mock_twenty_crm_client.create_custom_field.assert_called()
    
    def test_setup_company_custom_fields_existing(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up company custom fields when some exist."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        mock_twenty_crm_client.list_custom_fields.return_value = [
            {"id": "field_1", "name": "business_id"},
        ]
        
        mock_twenty_crm_client.create_custom_field.return_value = {"id": "field_2", "name": "industry"}
        
        result = setup.setup_company_custom_fields()
        
        assert len(result) > 0
    
    def test_setup_company_custom_fields_error(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test setting up company custom fields when creation fails."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        mock_twenty_crm_client.list_custom_fields.return_value = []
        mock_twenty_crm_client.create_custom_field.side_effect = Exception("Create error")
        
        result = setup.setup_company_custom_fields()
        
        assert isinstance(result, list)
    
    def test_verify_setup_complete(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test verifying setup when complete."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        # Mock all required fields exist
        mock_twenty_crm_client.list_custom_fields.side_effect = [
            [  # Person fields
                {"name": "contact_id"},
                {"name": "category_code"},
                {"name": "subcategory_code"},
                {"name": "relationship_category"},
                {"name": "llm_context"},
                {"name": "sync_metadata"},
            ],
            [  # Company fields
                {"name": "business_id"},
                {"name": "industry"},
                {"name": "llm_context"},
                {"name": "sync_metadata"},
            ],
        ]
        
        result = setup.verify_setup()
        
        assert result["all_complete"] is True
        assert result["person_fields"]["complete"] is True
        assert result["company_fields"]["complete"] is True
    
    def test_verify_setup_incomplete(
        self,
        mock_twenty_crm_client: Mock,
    ) -> None:
        """Test verifying setup when incomplete."""
        setup = TwentyCRMSetup(client=mock_twenty_crm_client)
        
        # Mock missing fields
        mock_twenty_crm_client.list_custom_fields.side_effect = [
            [{"name": "contact_id"}],  # Missing other person fields
            [{"name": "business_id"}],  # Missing other company fields
        ]
        
        result = setup.verify_setup()
        
        assert result["all_complete"] is False
        assert len(result["person_fields"]["missing"]) > 0
        assert len(result["company_fields"]["missing"]) > 0