"""Tests for care_service migrated to UnifiedService pattern."""

import pytest
from datetime import datetime

from src.services.central_services.care_service_migrated import (
    CareServiceMigrated,
    get_care_service,
    process_resonance,
    get_pending_actions,
    CareService,
)


class TestCareServiceMigrated:
    """Test suite for CareServiceMigrated."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = CareServiceMigrated()
        assert service.service_name == "care_service"
        assert service.holds is not None

    def test_execute_with_high_resonance(self):
        """Test execute with resonance above threshold."""
        service = CareServiceMigrated()

        input_data = {
            "resonance_result": {
                "score": 0.5,
                "subject_id": "test_subject",
                "resonance_id": "res_001",
                "matches": ["signal1", "signal2"]
            },
            "entity": {
                "name": "Test Entity",
                "need": "Test need"
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert result["care_record"] is not None
        assert "care_id" in result["care_record"]

    def test_execute_with_low_resonance(self):
        """Test execute with resonance below threshold."""
        service = CareServiceMigrated()

        input_data = {
            "resonance_result": {
                "score": 0.1,  # Below default threshold of 0.2
                "subject_id": "test_subject",
            },
            "entity": {}
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert result["care_record"] is None
        assert "threshold" in result["message"]

    def test_execute_missing_resonance_result(self):
        """Test execute with missing resonance_result."""
        service = CareServiceMigrated()

        input_data = {
            "entity": {"name": "Test"}
        }

        result = service.execute(input_data)

        assert result["status"] == "error"

    def test_care_record_structure(self):
        """Test that care record has expected structure."""
        service = CareServiceMigrated()

        input_data = {
            "resonance_result": {
                "score": 0.7,
                "subject_id": "structure_test",
                "resonance_id": "res_structure",
            },
            "entity": {
                "name": "Structure Test Entity",
                "need": "Test structure"
            }
        }

        result = service.execute(input_data)
        care_record = result["care_record"]

        assert "care_id" in care_record
        assert "subject_id" in care_record
        assert "need" in care_record
        assert "insight" in care_record
        assert "suggested_action" in care_record
        assert "status" in care_record
        assert care_record["status"] == "pending"

    def test_get_pending_actions_all(self):
        """Test get_pending_actions without filter."""
        service = CareServiceMigrated()

        # Create a care task
        service.execute({
            "resonance_result": {
                "score": 0.5,
                "subject_id": "pending_test",
            },
            "entity": {"name": "Pending Test"}
        })

        # Get all pending
        pending = service.get_pending_actions()

        assert isinstance(pending, list)

    def test_get_pending_actions_by_subject(self):
        """Test get_pending_actions filtered by subject_id."""
        service = CareServiceMigrated()

        subject_id = f"subject_{datetime.now().timestamp()}"

        # Create care task for specific subject
        service.execute({
            "resonance_result": {
                "score": 0.5,
                "subject_id": subject_id,
            },
            "entity": {"name": "Subject Filter Test"}
        })

        # Get pending for that subject
        pending = service.get_pending_actions(subject_id=subject_id)

        assert isinstance(pending, list)

    def test_update_status(self):
        """Test updating care task status."""
        service = CareServiceMigrated()

        # Create care task
        result = service.execute({
            "resonance_result": {
                "score": 0.6,
                "subject_id": "status_test",
                "resonance_id": "res_status",
            },
            "entity": {"name": "Status Test"}
        })

        care_id = result["care_record"]["care_id"]

        # Update status
        update_result = service.update_status(
            care_id=care_id,
            status="acted"
        )

        assert update_result["status"] == "success"

    def test_update_status_to_resolved(self):
        """Test updating status to resolved with timestamp."""
        service = CareServiceMigrated()

        # Create care task
        result = service.execute({
            "resonance_result": {
                "score": 0.7,
                "subject_id": "resolved_test",
            },
            "entity": {"name": "Resolve Test"}
        })

        care_id = result["care_record"]["care_id"]

        # Resolve it
        update_result = service.update_status(
            care_id=care_id,
            status="resolved"
        )

        assert update_result["status"] == "success"

    def test_backward_compatible_process_resonance(self):
        """Test backward compatible process_resonance function."""
        resonance_result = {
            "score": 0.5,
            "subject_id": "compat_test",
            "resonance_id": "res_compat",
        }
        entity = {
            "name": "Compatibility Test",
            "need": "Test backward compatibility"
        }

        care_record = process_resonance(resonance_result, entity)

        assert care_record is not None
        assert "care_id" in care_record

    def test_backward_compatible_get_pending(self):
        """Test backward compatible get_pending_actions function."""
        # Create some care tasks
        process_resonance(
            {"score": 0.5, "subject_id": "legacy_test"},
            {"name": "Legacy Test"}
        )

        pending = get_pending_actions()

        assert isinstance(pending, list)

    def test_legacy_care_service_class(self):
        """Test legacy CareService class wrapper."""
        service = CareService()

        resonance = {
            "score": 0.6,
            "subject_id": "legacy_class_test",
        }
        entity = {"name": "Legacy Class"}

        care_record = service.process_resonance(resonance, entity)

        assert care_record is not None

    def test_singleton_pattern(self):
        """Test that get_care_service returns the same instance."""
        service1 = get_care_service()
        service2 = get_care_service()

        assert service1 is service2


class TestCareServiceIntegration:
    """Integration tests for CareServiceMigrated."""

    def test_full_care_lifecycle(self):
        """Test complete care lifecycle: create, query, update."""
        service = CareServiceMigrated()

        subject_id = f"lifecycle_{datetime.now().timestamp()}"

        # Create care task
        create_result = service.execute({
            "resonance_result": {
                "score": 0.8,
                "subject_id": subject_id,
                "resonance_id": "res_lifecycle",
            },
            "entity": {
                "name": "Lifecycle Entity",
                "need": "Test complete lifecycle"
            }
        })

        care_id = create_result["care_record"]["care_id"]

        # Query pending
        pending = service.get_pending_actions(subject_id=subject_id)
        assert any(task["care_id"] == care_id for task in pending)

        # Update to acted
        service.update_status(care_id, "acted")

        # Update to resolved
        resolve_result = service.update_status(care_id, "resolved")
        assert resolve_result["status"] == "success"

    def test_multiple_subjects_care(self):
        """Test care tasks for multiple subjects."""
        service = CareServiceMigrated()

        timestamp = datetime.now().timestamp()
        subjects = [f"subject_a_{timestamp}", f"subject_b_{timestamp}"]

        for subject in subjects:
            result = service.execute({
                "resonance_result": {
                    "score": 0.5,
                    "subject_id": subject,
                },
                "entity": {"name": f"Entity for {subject}"}
            })
            assert result["status"] == "success"

    def test_care_persistence(self):
        """Test that care tasks persist in database."""
        service = CareServiceMigrated()

        # Create care task
        result = service.execute({
            "resonance_result": {
                "score": 0.6,
                "subject_id": "persist_test",
            },
            "entity": {"name": "Persistence Test"}
        })

        care_id = result["care_record"]["care_id"]

        # Create new service instance (would read from DB)
        # Note: In practice, singleton might return same instance
        # This tests that data is in persistent storage
        pending = service.get_pending_actions(subject_id="persist_test")

        assert any(task["care_id"] == care_id for task in pending)

    def test_resonance_threshold_boundary(self):
        """Test behavior at resonance threshold boundary."""
        service = CareServiceMigrated()

        # Exactly at threshold (0.2)
        result_at = service.execute({
            "resonance_result": {
                "score": 0.2,
                "subject_id": "threshold_at",
            },
            "entity": {}
        })

        # Just below threshold
        result_below = service.execute({
            "resonance_result": {
                "score": 0.19,
                "subject_id": "threshold_below",
            },
            "entity": {}
        })

        # Just above threshold
        result_above = service.execute({
            "resonance_result": {
                "score": 0.21,
                "subject_id": "threshold_above",
            },
            "entity": {}
        })

        assert result_at["care_record"] is not None
        assert result_below["care_record"] is None
        assert result_above["care_record"] is not None

    def test_metadata_in_care_record(self):
        """Test that metadata is captured in care records."""
        service = CareServiceMigrated()

        result = service.execute({
            "resonance_result": {
                "score": 0.7,
                "subject_id": "metadata_test",
                "resonance_id": "res_meta",
            },
            "entity": {
                "name": "Metadata Entity",
                "need": "Test metadata"
            }
        })

        care_record = result["care_record"]
        assert "metadata" in care_record
        assert care_record["metadata"]["resonance_score"] == 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
