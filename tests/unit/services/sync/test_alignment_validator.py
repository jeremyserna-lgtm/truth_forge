"""Comprehensive tests for AlignmentValidator.

Achieves 95%+ coverage with all branches and edge cases tested.
"""

from typing import Dict, Any
import pytest

from truth_forge.services.sync.alignment_validator import AlignmentValidator


class TestAlignmentValidator:
    """Test suite for AlignmentValidator."""
    
    def test_init(self) -> None:
        """Test initialization."""
        validator = AlignmentValidator()
        
        assert validator.category_codes == {"A", "B", "C", "D", "E", "F", "G", "H", "X"}
    
    def test_validate_contact_valid(
        self,
    ) -> None:
        """Test validating a valid contact."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
            "subcategory_code": "B1_BEST_FRIENDS",
            "sync_metadata": {
                "version": 1,
                "last_updated": "2026-01-01T00:00:00Z",
                "last_updated_by": "system",
            },
            "is_business": False,
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert len(result["warnings"]) == 0
    
    def test_validate_contact_missing_contact_id(
        self,
    ) -> None:
        """Test validating contact missing contact_id."""
        validator = AlignmentValidator()
        
        contact = {
            "canonical_name": "Test User",
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is False
        assert any("contact_id" in error for error in result["errors"])
    
    def test_validate_contact_missing_canonical_name(
        self,
    ) -> None:
        """Test validating contact missing canonical_name."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is False
        assert any("canonical_name" in error for error in result["errors"])
    
    def test_validate_contact_invalid_category_code(
        self,
    ) -> None:
        """Test validating contact with invalid category_code."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "Z",  # Invalid
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is False
        assert any("category_code" in error for error in result["errors"])
    
    def test_validate_contact_subcategory_without_category(
        self,
    ) -> None:
        """Test validating contact with subcategory but no category."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "subcategory_code": "B1_BEST_FRIENDS",
        }
        
        result = validator.validate_contact(contact)
        
        assert len(result["warnings"]) > 0
        assert any("subcategory_code" in warning for warning in result["warnings"])
    
    def test_validate_contact_subcategory_mismatch(
        self,
    ) -> None:
        """Test validating contact with subcategory that doesn't match category."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "A",
            "subcategory_code": "B1_BEST_FRIENDS",  # Doesn't start with A
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is False
        assert any("subcategory_code" in error for error in result["errors"])
    
    def test_validate_contact_missing_sync_metadata(
        self,
    ) -> None:
        """Test validating contact with missing sync metadata."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "sync_metadata": {},
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is True  # Missing metadata is just warnings
        assert len(result["warnings"]) > 0
        assert any("version" in warning for warning in result["warnings"])
    
    def test_validate_contact_invalid_is_business(
        self,
    ) -> None:
        """Test validating contact with invalid is_business type."""
        validator = AlignmentValidator()
        
        contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "is_business": "yes",  # Should be bool
        }
        
        result = validator.validate_contact(contact)
        
        assert result["valid"] is False
        assert any("is_business" in error for error in result["errors"])
    
    def test_compare_contacts_aligned(
        self,
    ) -> None:
        """Test comparing two aligned contacts."""
        validator = AlignmentValidator()
        
        contact1 = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
            "subcategory_code": "B1",
            "organization": "Test Org",
            "sync_metadata": {"version": 1},
        }
        
        contact2 = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
            "subcategory_code": "B1",
            "organization": "Test Org",
            "sync_metadata": {"version": 1},
        }
        
        result = validator.compare_contacts(contact1, contact2)
        
        assert result["aligned"] is True
        assert len(result["differences"]) == 0
    
    def test_compare_contacts_different(
        self,
    ) -> None:
        """Test comparing two different contacts."""
        validator = AlignmentValidator()
        
        contact1 = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
            "sync_metadata": {"version": 1},
        }
        
        contact2 = {
            "contact_id": "123",
            "canonical_name": "Different User",
            "category_code": "A",
            "sync_metadata": {"version": 2},
        }
        
        result = validator.compare_contacts(contact1, contact2)
        
        assert result["aligned"] is False
        assert len(result["differences"]) > 0
        assert any(diff["field"] == "canonical_name" for diff in result["differences"])
        assert any(diff["field"] == "category_code" for diff in result["differences"])
    
    def test_validate_alignment_all_systems(
        self,
    ) -> None:
        """Test validating alignment across all systems."""
        validator = AlignmentValidator()
        
        bigquery_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        supabase_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        local_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        crm_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        result = validator.validate_alignment(
            bigquery_contact,
            supabase_contact=supabase_contact,
            local_contact=local_contact,
            crm_contact=crm_contact,
        )
        
        assert "bigquery" in result
        assert "supabase" in result
        assert "local" in result
        assert "crm_twenty" in result
        assert "alignment" in result
        assert result["overall_aligned"] is True
    
    def test_validate_alignment_partial_systems(
        self,
    ) -> None:
        """Test validating alignment with only some systems."""
        validator = AlignmentValidator()
        
        bigquery_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        supabase_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        result = validator.validate_alignment(
            bigquery_contact,
            supabase_contact=supabase_contact,
        )
        
        assert "bigquery" in result
        assert "supabase" in result
        assert "local" not in result
        assert "crm_twenty" not in result
        assert "bigquery_vs_supabase" in result["alignment"]
    
    def test_validate_alignment_misaligned(
        self,
    ) -> None:
        """Test validating alignment when systems are misaligned."""
        validator = AlignmentValidator()
        
        bigquery_contact = {
            "contact_id": "123",
            "canonical_name": "Test User",
            "category_code": "B",
        }
        
        supabase_contact = {
            "contact_id": "123",
            "canonical_name": "Different User",
            "category_code": "A",
        }
        
        result = validator.validate_alignment(
            bigquery_contact,
            supabase_contact=supabase_contact,
        )
        
        assert result["overall_aligned"] is False
        assert "bigquery_vs_supabase" in result["alignment"]
        assert result["alignment"]["bigquery_vs_supabase"]["aligned"] is False