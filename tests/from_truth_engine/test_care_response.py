"""Tests for CareResponse - The Never-Leave-the-Room Guarantee.

This implements Matthew's promise: "We will make sure you're okay."
These tests verify that the system NEVER returns None or silent failure.
Every response acknowledges presence, even in failure.

PRINCIPLE: "I couldn't do X, but I am still here. Here is Y."
"""
from __future__ import annotations

"""Tests for CareResponse - The Never-Leave-the-Room Guarantee.

This implements Matthew's promise: "We will make sure you're okay."
These tests verify that the system NEVER returns None or silent failure.
Every response acknowledges presence, even in failure.

PRINCIPLE: "I couldn't do X, but I am still here. Here is Y."
"""
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)


try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "tests.test_care_response.py"

import pytest
from datetime import datetime

from src.services.central_services.core.responses import (
    CareResponse,
    CareStatus,
    Care,
)

class TestCareResponseNeverNone:
    """Test the never-None guarantee of CareResponse."""

    def test_care_response_always_truthy(self):
        """CareResponse is always truthy - we never leave the room."""
        success = CareResponse.success({"data": "test"})
        partial = CareResponse.partial({"partial": "data"}, "Message", "Recovery")
        present = CareResponse.present("Couldn't complete", "Try again")

        # All must be truthy
        assert bool(success) is True
        assert bool(partial) is True
        assert bool(present) is True

        # None would be falsy - verify contrast
        assert bool(None) is False

    def test_success_never_none(self):
        """CareResponse.success() never returns None."""
        response = CareResponse.success(None, "Completed with no data")

        # Even with None data, the response itself is not None
        assert response is not None
        assert response.status == CareStatus.SUCCESS
        assert response.message == "Completed with no data"

    def test_partial_never_none(self):
        """CareResponse.partial() never returns None."""
        response = CareResponse.partial(
            data=None,
            message="Partial completion",
            recovery_path="Do X to complete"
        )

        assert response is not None
        assert response.status == CareStatus.PARTIAL
        assert response.recovery_path is not None

    def test_present_never_none(self):
        """CareResponse.present() never returns None - we stay even when we fail."""
        response = CareResponse.present(
            message="Could not complete the operation",
            recovery_path="Try simplifying the input"
        )

        assert response is not None
        assert response.status == CareStatus.PRESENT
        assert response.data is None  # No data, but we're still here
        assert response.recovery_path is not None  # Always tell them what to do next

class TestCareResponseStructure:
    """Test CareResponse has correct structure."""

    def test_success_structure(self):
        """Test CareResponse.success() has all required fields."""
        response = CareResponse.success(
            data={"key": "value"},
            message="Completed successfully",
            care_reasoning="Because we care"
        )

        assert response.status == CareStatus.SUCCESS
        assert response.message == "Completed successfully"
        assert response.data == {"key": "value"}
        assert response.care_reasoning == "Because we care"
        assert response.recovery_path is None  # Not needed for success
        assert isinstance(response.fidelity_log, list)
        assert isinstance(response.timestamp, datetime)

    def test_partial_structure(self):
        """Test CareResponse.partial() has all required fields."""
        response = CareResponse.partial(
            data={"partial": "result"},
            message="3 of 5 completed",
            recovery_path="Retry the remaining 2",
            fidelity_log=[{"struggle": "X failed", "recovery": "Skipped X"}],
            care_reasoning="We tried our best"
        )

        assert response.status == CareStatus.PARTIAL
        assert response.data == {"partial": "result"}
        assert response.recovery_path == "Retry the remaining 2"
        assert len(response.fidelity_log) == 1
        assert response.fidelity_log[0]["struggle"] == "X failed"

    def test_present_structure(self):
        """Test CareResponse.present() has all required fields - the counselor who stayed."""
        response = CareResponse.present(
            message="I couldn't analyze this input",
            recovery_path="Try with simpler text",
            care_reasoning="The input was too complex for current processing"
        )

        assert response.status == CareStatus.PRESENT
        assert response.data is None
        assert response.recovery_path == "Try with simpler text"
        assert response.care_reasoning is not None

class TestFidelityLog:
    """Test the fidelity log - 'Here is where I struggled. Here is how I recovered.'"""

    def test_add_fidelity_entry(self):
        """Test adding fidelity entries to track struggles and recoveries."""
        response = CareResponse.success({"result": "data"})

        response.add_fidelity_entry(
            struggle="Database connection failed",
            recovery="Used cached data instead"
        )

        assert len(response.fidelity_log) == 1
        entry = response.fidelity_log[0]
        assert entry["struggle"] == "Database connection failed"
        assert entry["recovery"] == "Used cached data instead"
        assert "timestamp" in entry

    def test_multiple_fidelity_entries(self):
        """Test multiple fidelity entries chain correctly."""
        response = CareResponse.partial(
            data={"partial": "result"},
            message="Some worked, some didn't",
            recovery_path="Retry failed items"
        )

        response.add_fidelity_entry("First failure", "Recovered via X")
        response.add_fidelity_entry("Second failure", "Recovered via Y")
        response.add_fidelity_entry("Third failure", "Recovered via Z")

        assert len(response.fidelity_log) == 3
        assert response.fidelity_log[0]["struggle"] == "First failure"
        assert response.fidelity_log[2]["struggle"] == "Third failure"

    def test_fidelity_method_chaining(self):
        """Test add_fidelity_entry returns self for chaining."""
        response = (
            CareResponse.partial({}, "Message", "Recovery")
            .add_fidelity_entry("Struggle 1", "Recovery 1")
            .add_fidelity_entry("Struggle 2", "Recovery 2")
        )

        assert len(response.fidelity_log) == 2

class TestCareResponseMethods:
    """Test CareResponse utility methods."""

    def test_is_success(self):
        """Test is_success() method."""
        success = CareResponse.success({})
        partial = CareResponse.partial({}, "msg", "path")
        present = CareResponse.present("msg", "path")

        assert success.is_success() is True
        assert partial.is_success() is False
        assert present.is_success() is False

    def test_is_partial(self):
        """Test is_partial() method."""
        success = CareResponse.success({})
        partial = CareResponse.partial({}, "msg", "path")
        present = CareResponse.present("msg", "path")

        assert success.is_partial() is False
        assert partial.is_partial() is True
        assert present.is_partial() is False

    def test_is_present(self):
        """Test is_present() method."""
        success = CareResponse.success({})
        partial = CareResponse.partial({}, "msg", "path")
        present = CareResponse.present("msg", "path")

        assert success.is_present() is False
        assert partial.is_present() is False
        assert present.is_present() is True

    def test_has_data(self):
        """Test has_data() method."""
        with_data = CareResponse.success({"key": "value"})
        without_data = CareResponse.present("msg", "path")
        with_none_data = CareResponse.success(None)

        assert with_data.has_data() is True
        assert without_data.has_data() is False
        assert with_none_data.has_data() is False

    def test_to_dict(self):
        """Test serialization to dict."""
        response = CareResponse.success(
            data={"test": "data"},
            message="Test message",
            care_reasoning="Test reasoning"
        )

        result = response.to_dict()

        assert result["status"] == "success"
        assert result["message"] == "Test message"
        assert result["data"] == {"test": "data"}
        assert result["care_reasoning"] == "Test reasoning"
        assert "timestamp" in result

class TestCareAlias:
    """Test the Care convenience alias."""

    def test_care_is_care_response(self):
        """Care is an alias for CareResponse."""
        assert Care is CareResponse

    def test_care_usage(self):
        """Test using Care alias."""
        response = Care.success({"data": "test"})
        assert isinstance(response, CareResponse)
        assert response.is_success()

class TestCareServiceNeverNone:
    """Test that CareService implements the never-None guarantee."""

    def test_care_service_low_resonance_returns_care_response(self):
        """CareService returns CareResponse even for low resonance."""
        from src.services.central_services.care_service import CareService

        service = CareService()
        result = service.process_resonance(
            resonance_result={"score": 0.1, "subject_id": "test"},
            entity={}
        )

        # Must return CareResponse, not None
        assert result is not None
        assert isinstance(result, CareResponse)
        assert result.status == CareStatus.PRESENT
        assert "still here" in result.message.lower()

    def test_care_service_high_resonance_returns_care_response(self):
        """CareService returns CareResponse for high resonance."""
        from src.services.central_services.care_service import CareService

        service = CareService()
        result = service.process_resonance(
            resonance_result={
                "score": 0.5,
                "subject_id": "test",
                "resonance_id": "res_test"
            },
            entity={"name": "Test"}
        )

        # Must return CareResponse, not None
        assert result is not None
        assert isinstance(result, CareResponse)
        assert result.status == CareStatus.SUCCESS
        assert result.has_data()

class TestExhaleFidelityLog:
    """Test that exhale() returns fidelity_log."""

    def test_exhale_returns_fidelity_log(self):
        """exhale() should return stats dict with fidelity_log."""
        try:
            from src.services.central_services.primitive_pattern.pattern import exhale

            result = exhale(
                content="Test content for fidelity check",
                source_name="test_fidelity",
                build_knowledge_graph=False  # Skip KG to simplify test
            )

            # Must have fidelity_log in result
            assert "fidelity_log" in result
            assert isinstance(result["fidelity_log"], list)

            # Must have status in result
            assert "status" in result
            assert result["status"] in ["success", "partial", "present"]
        except ImportError:
            pytest.skip("primitive_pattern not available")

    def test_exhale_fidelity_log_on_failure(self):
        """exhale() logs struggles when things fail."""
        try:
            from src.services.central_services.primitive_pattern.pattern import exhale

            # Empty content should still return, not crash
            result = exhale(
                content="",  # Empty content
                source_name="test_empty",
                build_knowledge_graph=False
            )

            assert result is not None
            assert "fidelity_log" in result
        except ImportError:
            pytest.skip("primitive_pattern not available")

class TestSocialSentinelNeverNone:
    """Test that SocialSentinelService implements the never-None guarantee."""

    def test_observe_returns_value(self):
        """observe() never returns None."""
        try:
            from src.services.central_services.social_sentinel_service import (
                get_social_sentinel_service
            )

            service = get_social_sentinel_service()
            result = service.observe(
                person_id="test_person",
                observation_type="stage",
                data={"confidence": 0.8, "stage": 4}
            )

            assert result is not None
            assert isinstance(result, CareResponse)
        except ImportError:
            pytest.skip("social_sentinel_service not available")

    def test_check_constellation_returns_value(self):
        """check_constellation() never returns None."""
        try:
            from src.services.central_services.social_sentinel_service import (
                get_social_sentinel_service
            )

            service = get_social_sentinel_service()
            result = service.check_constellation()

            # Returns CareResponse, not a list - the guardian never leaves the room
            assert result is not None
            assert isinstance(result, CareResponse)
            assert result.has_data()
        except ImportError:
            pytest.skip("social_sentinel_service not available")

    def test_resolve_intervention_returns_care_response(self):
        """resolve_intervention() returns CareResponse."""
        try:
            from src.services.central_services.social_sentinel_service import (
                SocialSentinelService,
                InterventionTrigger
            )
            from src.services.central_services.social_sentinel_service.service import (
                InterventionTrigger
            )

            service = SocialSentinelService()

            # Create a mock intervention
            intervention = InterventionTrigger(
                person_id="test_resolve",
                person_name="Test Person",
                trigger_type="regression",
                message="Test message",
                severity="warning",
                recommended_action="Test action",
                evidence=[]
            )

            result = service.resolve_intervention(
                intervention=intervention,
                resolution="Reached out successfully",
                action_taken="Called and spoke with them"
            )

            assert result is not None
            assert isinstance(result, CareResponse)
            assert result.is_success()
        except ImportError:
            pytest.skip("social_sentinel_service not available")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
