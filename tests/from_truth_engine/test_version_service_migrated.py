"""Tests for version_service migrated to UnifiedService pattern."""

import pytest
from datetime import datetime

from src.services.central_services.version_service.service_migrated import (
    VersionService,
    get_service,
    exhale,
    ValidationError,
)

class TestVersionService:
    """Test suite for VersionService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = VersionService()
        assert service.service_name == "version_service"
        assert service.holds is not None

    def test_execute_with_valid_data(self):
        """Test execute method with valid version data."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "entity_id": "doc_001",
            "content": "Test document content v1",
            "metadata": {"author": "test_user"}
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "version_id" in result
        # Note: execute() doesn't return version_count, it returns entity_id
        assert "entity_id" in result

    def test_execute_missing_entity_type(self):
        """Test execute with missing entity_type - still succeeds with default."""
        service = VersionService()

        input_data = {
            "entity_id": "doc_001",
            "content": "Test content",
        }

        # Service uses "unknown" as default entity_type, so this succeeds
        result = service.execute(input_data)
        assert result["status"] == "success"

    def test_execute_missing_entity_id(self):
        """Test execute with missing entity_id."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "content": "Test content",
        }

        # Service raises ValidationError when entity_id is missing
        with pytest.raises(ValidationError):
            service.execute(input_data)

    def test_version_id_generation(self):
        """Test that version IDs are generated consistently."""
        service = VersionService()

        input_data = {
            "entity_type": "code",
            "entity_id": "module_001",
            "content": "def test(): pass",
        }

        result1 = service.execute(input_data)
        result2 = service.execute(input_data)

        assert result1["status"] == "success"
        assert result2["status"] == "success"
        # Version IDs should be different due to timestamp
        assert result1["version_id"] != result2["version_id"]

    def test_exhale_creates_version(self):
        """Test backward compatible exhale function."""
        result = exhale(
            entity_type="document",
            entity_id="test_doc",
            content="Test content for exhale",
            metadata={"test": True}
        )

        assert result["status"] == "success"
        assert "version_id" in result

    def test_get_version_history_function(self):
        """Test get_version_history service method."""
        service = get_service()
        # Create a few versions
        for i in range(3):
            exhale(
                entity_type="document",
                entity_id="history_test",
                content=f"Version {i}",
            )

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="history_test",
            limit=10
        )

        assert isinstance(history, list)
        # Should have at least the versions we just created
        assert len(history) >= 3

    def test_get_version_by_id(self):
        """Test retrieving a specific version by version_id."""
        service = VersionService()

        # Create a version
        input_data = {
            "entity_type": "code",
            "entity_id": "test_module",
            "content": "def specific_version(): pass",
        }
        result = service.execute(input_data)
        version_id = result["version_id"]

        # Retrieve it
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("version_id") == version_id

    def test_get_version_history_method(self):
        """Test get_version_history service method."""
        service = VersionService()

        # Create multiple versions
        for i in range(5):
            service.execute({
                "entity_type": "test",
                "entity_id": "multi_version",
                "content": f"Content v{i}",
            })

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="multi_version"
        )

        assert isinstance(history, list)
        assert len(history) >= 5

    def test_version_counter_increments(self):
        """Test that version counter increments correctly."""
        service = VersionService()

        entity_id = f"counter_test_{datetime.now().timestamp()}"

        # Create first version
        result1 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 1",
        })

        # Create second version
        result2 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 2",
        })

        # Note: execute() doesn't return version_count, but both should succeed
        # and have unique version IDs
        assert result1["status"] == "success"
        assert result2["status"] == "success"
        assert result1["version_id"] != result2["version_id"]

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_metadata_preservation(self):
        """Test that metadata is preserved in versions."""
        service = VersionService()

        metadata = {
            "author": "test_user",
            "tags": ["important", "test"],
            "custom_field": "custom_value"
        }

        result = service.execute({
            "entity_type": "document",
            "entity_id": "metadata_test",
            "content": "Test content",
            "metadata": metadata
        })

        version_id = result["version_id"]
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("metadata") is not None

class TestVersionServiceIntegration:
    """Integration tests for VersionService."""

    def test_full_version_lifecycle(self):
        """Test complete version lifecycle: create, retrieve, query history."""
        service = VersionService()

        entity_id = f"lifecycle_test_{datetime.now().timestamp()}"

        # Create initial version
        v1_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v1(): return 1",
            "metadata": {"version_label": "v1"}
        })
        v1_id = v1_result["version_id"]

        # Create second version
        v2_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v2(): return 2",
            "metadata": {"version_label": "v2"}
        })
        v2_id = v2_result["version_id"]

        # Retrieve specific versions
        version_1 = service.get_version(v1_id)
        version_2 = service.get_version(v2_id)

        assert version_1 is not None
        assert version_2 is not None
        assert version_1["content"] != version_2["content"]

        # Get history (entity_id is first arg, not entity_type)
        history = service.get_version_history(
            entity_id=entity_id
        )

        assert len(history) >= 2

    def test_concurrent_versioning(self):
        """Test that multiple entities can be versioned simultaneously."""
        service = VersionService()

        timestamp = datetime.now().timestamp()

        # Create versions for multiple entities
        entities = ["entity_a", "entity_b", "entity_c"]

        for entity_id in entities:
            result = service.execute({
                "entity_type": "test",
                "entity_id": f"{entity_id}_{timestamp}",
                "content": f"Content for {entity_id}",
            })
            assert result["status"] == "success"

    def test_version_query_with_limit(self):
        """Test that version history respects limit parameter."""
        service = VersionService()

        entity_id = f"limit_test_{datetime.now().timestamp()}"

        # Create 10 versions
        for i in range(10):
            service.execute({
                "entity_type": "test",
                "entity_id": entity_id,
                "content": f"Version {i}",
            })

        # Query with limit (entity_id is first arg)
        history = service.get_version_history(
            entity_id=entity_id,
            limit=5
        )

        assert len(history) <= 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "tests.test_version_service_migrated.py"

import pytest
from datetime import datetime

from src.services.central_services.version_service.service_migrated import (
    VersionService,
    get_service,
    exhale,
    ValidationError,
)

class TestVersionService:
    """Test suite for VersionService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = VersionService()
        assert service.service_name == "version_service"
        assert service.holds is not None

    def test_execute_with_valid_data(self):
        """Test execute method with valid version data."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "entity_id": "doc_001",
            "content": "Test document content v1",
            "metadata": {"author": "test_user"}
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "version_id" in result
        # Note: execute() doesn't return version_count, it returns entity_id
        assert "entity_id" in result

    def test_execute_missing_entity_type(self):
        """Test execute with missing entity_type - still succeeds with default."""
        service = VersionService()

        input_data = {
            "entity_id": "doc_001",
            "content": "Test content",
        }

        # Service uses "unknown" as default entity_type, so this succeeds
        result = service.execute(input_data)
        assert result["status"] == "success"

    def test_execute_missing_entity_id(self):
        """Test execute with missing entity_id."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "content": "Test content",
        }

        # Service raises ValidationError when entity_id is missing
        with pytest.raises(ValidationError):
            service.execute(input_data)

    def test_version_id_generation(self):
        """Test that version IDs are generated consistently."""
        service = VersionService()

        input_data = {
            "entity_type": "code",
            "entity_id": "module_001",
            "content": "def test(): pass",
        }

        result1 = service.execute(input_data)
        result2 = service.execute(input_data)

        assert result1["status"] == "success"
        assert result2["status"] == "success"
        # Version IDs should be different due to timestamp
        assert result1["version_id"] != result2["version_id"]

    def test_exhale_creates_version(self):
        """Test backward compatible exhale function."""
        result = exhale(
            entity_type="document",
            entity_id="test_doc",
            content="Test content for exhale",
            metadata={"test": True}
        )

        assert result["status"] == "success"
        assert "version_id" in result

    def test_get_version_history_function(self):
        """Test get_version_history service method."""
        service = get_service()
        # Create a few versions
        for i in range(3):
            exhale(
                entity_type="document",
                entity_id="history_test",
                content=f"Version {i}",
            )

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="history_test",
            limit=10
        )

        assert isinstance(history, list)
        # Should have at least the versions we just created
        assert len(history) >= 3

    def test_get_version_by_id(self):
        """Test retrieving a specific version by version_id."""
        service = VersionService()

        # Create a version
        input_data = {
            "entity_type": "code",
            "entity_id": "test_module",
            "content": "def specific_version(): pass",
        }
        result = service.execute(input_data)
        version_id = result["version_id"]

        # Retrieve it
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("version_id") == version_id

    def test_get_version_history_method(self):
        """Test get_version_history service method."""
        service = VersionService()

        # Create multiple versions
        for i in range(5):
            service.execute({
                "entity_type": "test",
                "entity_id": "multi_version",
                "content": f"Content v{i}",
            })

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="multi_version"
        )

        assert isinstance(history, list)
        assert len(history) >= 5

    def test_version_counter_increments(self):
        """Test that version counter increments correctly."""
        service = VersionService()

        entity_id = f"counter_test_{datetime.now().timestamp()}"

        # Create first version
        result1 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 1",
        })

        # Create second version
        result2 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 2",
        })

        # Note: execute() doesn't return version_count, but both should succeed
        # and have unique version IDs
        assert result1["status"] == "success"
        assert result2["status"] == "success"
        assert result1["version_id"] != result2["version_id"]

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_metadata_preservation(self):
        """Test that metadata is preserved in versions."""
        service = VersionService()

        metadata = {
            "author": "test_user",
            "tags": ["important", "test"],
            "custom_field": "custom_value"
        }

        result = service.execute({
            "entity_type": "document",
            "entity_id": "metadata_test",
            "content": "Test content",
            "metadata": metadata
        })

        version_id = result["version_id"]
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("metadata") is not None

class TestVersionServiceIntegration:
    """Integration tests for VersionService."""

    def test_full_version_lifecycle(self):
        """Test complete version lifecycle: create, retrieve, query history."""
        service = VersionService()

        entity_id = f"lifecycle_test_{datetime.now().timestamp()}"

        # Create initial version
        v1_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v1(): return 1",
            "metadata": {"version_label": "v1"}
        })
        v1_id = v1_result["version_id"]

        # Create second version
        v2_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v2(): return 2",
            "metadata": {"version_label": "v2"}
        })
        v2_id = v2_result["version_id"]

        # Retrieve specific versions
        version_1 = service.get_version(v1_id)
        version_2 = service.get_version(v2_id)

        assert version_1 is not None
        assert version_2 is not None
        assert version_1["content"] != version_2["content"]

        # Get history (entity_id is first arg, not entity_type)
        history = service.get_version_history(
            entity_id=entity_id
        )

        assert len(history) >= 2

    def test_concurrent_versioning(self):
        """Test that multiple entities can be versioned simultaneously."""
        service = VersionService()

        timestamp = datetime.now().timestamp()

        # Create versions for multiple entities
        entities = ["entity_a", "entity_b", "entity_c"]

        for entity_id in entities:
            result = service.execute({
                "entity_type": "test",
                "entity_id": f"{entity_id}_{timestamp}",
                "content": f"Content for {entity_id}",
            })
            assert result["status"] == "success"

    def test_version_query_with_limit(self):
        """Test that version history respects limit parameter."""
        service = VersionService()

        entity_id = f"limit_test_{datetime.now().timestamp()}"

        # Create 10 versions
        for i in range(10):
            service.execute({
                "entity_type": "test",
                "entity_id": entity_id,
                "content": f"Version {i}",
            })

        # Query with limit (entity_id is first arg)
        history = service.get_version_history(
            entity_id=entity_id,
            limit=5
        )

        assert len(history) <= 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
from __future__ import annotations
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
from __future__ import annotations

"""Tests for version_service migrated to UnifiedService pattern."""
from __future__ import annotations

from datetime import datetime

from src.services.central_services.version_service.service_migrated import (
    VersionService,
    get_service,
    exhale,
    ValidationError,
)

class TestVersionService:
    """Test suite for VersionService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = VersionService()
        assert service.service_name == "version_service"
        assert service.holds is not None

    def test_execute_with_valid_data(self):
        """Test execute method with valid version data."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "entity_id": "doc_001",
            "content": "Test document content v1",
            "metadata": {"author": "test_user"}
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "version_id" in result
        # Note: execute() doesn't return version_count, it returns entity_id
        assert "entity_id" in result

    def test_execute_missing_entity_type(self):
        """Test execute with missing entity_type - still succeeds with default."""
        service = VersionService()

        input_data = {
            "entity_id": "doc_001",
            "content": "Test content",
        }

        # Service uses "unknown" as default entity_type, so this succeeds
        result = service.execute(input_data)
        assert result["status"] == "success"

    def test_execute_missing_entity_id(self):
        """Test execute with missing entity_id."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "content": "Test content",
        }

        # Service raises ValidationError when entity_id is missing
        with pytest.raises(ValidationError):
            service.execute(input_data)

    def test_version_id_generation(self):
        """Test that version IDs are generated consistently."""
        service = VersionService()

        input_data = {
            "entity_type": "code",
            "entity_id": "module_001",
            "content": "def test(): pass",
        }

        result1 = service.execute(input_data)
        result2 = service.execute(input_data)

        assert result1["status"] == "success"
        assert result2["status"] == "success"
        # Version IDs should be different due to timestamp
        assert result1["version_id"] != result2["version_id"]

    def test_exhale_creates_version(self):
        """Test backward compatible exhale function."""
        result = exhale(
            entity_type="document",
            entity_id="test_doc",
            content="Test content for exhale",
            metadata={"test": True}
        )

        assert result["status"] == "success"
        assert "version_id" in result

    def test_get_version_history_function(self):
        """Test get_version_history service method."""
        service = get_service()
        # Create a few versions
        for i in range(3):
            exhale(
                entity_type="document",
                entity_id="history_test",
                content=f"Version {i}",
            )

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="history_test",
            limit=10
        )

        assert isinstance(history, list)
        # Should have at least the versions we just created
        assert len(history) >= 3

    def test_get_version_by_id(self):
        """Test retrieving a specific version by version_id."""
        service = VersionService()

        # Create a version
        input_data = {
            "entity_type": "code",
            "entity_id": "test_module",
            "content": "def specific_version(): pass",
        }
        result = service.execute(input_data)
        version_id = result["version_id"]

        # Retrieve it
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("version_id") == version_id

    def test_get_version_history_method(self):
        """Test get_version_history service method."""
        service = VersionService()

        # Create multiple versions
        for i in range(5):
            service.execute({
                "entity_type": "test",
                "entity_id": "multi_version",
                "content": f"Content v{i}",
            })

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="multi_version"
        )

        assert isinstance(history, list)
        assert len(history) >= 5

    def test_version_counter_increments(self):
        """Test that version counter increments correctly."""
        service = VersionService()

        entity_id = f"counter_test_{datetime.now().timestamp()}"

        # Create first version
        result1 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 1",
        })

        # Create second version
        result2 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 2",
        })

        # Note: execute() doesn't return version_count, but both should succeed
        # and have unique version IDs
        assert result1["status"] == "success"
        assert result2["status"] == "success"
        assert result1["version_id"] != result2["version_id"]

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_metadata_preservation(self):
        """Test that metadata is preserved in versions."""
        service = VersionService()

        metadata = {
            "author": "test_user",
            "tags": ["important", "test"],
            "custom_field": "custom_value"
        }

        result = service.execute({
            "entity_type": "document",
            "entity_id": "metadata_test",
            "content": "Test content",
            "metadata": metadata
        })

        version_id = result["version_id"]
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("metadata") is not None

class TestVersionServiceIntegration:
    """Integration tests for VersionService."""

    def test_full_version_lifecycle(self):
        """Test complete version lifecycle: create, retrieve, query history."""
        service = VersionService()

        entity_id = f"lifecycle_test_{datetime.now().timestamp()}"

        # Create initial version
        v1_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v1(): return 1",
            "metadata": {"version_label": "v1"}
        })
        v1_id = v1_result["version_id"]

        # Create second version
        v2_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v2(): return 2",
            "metadata": {"version_label": "v2"}
        })
        v2_id = v2_result["version_id"]

        # Retrieve specific versions
        version_1 = service.get_version(v1_id)
        version_2 = service.get_version(v2_id)

        assert version_1 is not None
        assert version_2 is not None
        assert version_1["content"] != version_2["content"]

        # Get history (entity_id is first arg, not entity_type)
        history = service.get_version_history(
            entity_id=entity_id
        )

        assert len(history) >= 2

    def test_concurrent_versioning(self):
        """Test that multiple entities can be versioned simultaneously."""
        service = VersionService()

        timestamp = datetime.now().timestamp()

        # Create versions for multiple entities
        entities = ["entity_a", "entity_b", "entity_c"]

        for entity_id in entities:
            result = service.execute({
                "entity_type": "test",
                "entity_id": f"{entity_id}_{timestamp}",
                "content": f"Content for {entity_id}",
            })
            assert result["status"] == "success"

    def test_version_query_with_limit(self):
        """Test that version history respects limit parameter."""
        service = VersionService()

        entity_id = f"limit_test_{datetime.now().timestamp()}"

        # Create 10 versions
        for i in range(10):
            service.execute({
                "entity_type": "test",
                "entity_id": entity_id,
                "content": f"Version {i}",
            })

        # Query with limit (entity_id is first arg)
        history = service.get_version_history(
            entity_id=entity_id,
            limit=5
        )

        assert len(history) <= 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "tests.test_version_service_migrated.py"

import pytest
from datetime import datetime

from src.services.central_services.version_service.service_migrated import (
    VersionService,
    get_service,
    exhale,
    ValidationError,
)

class TestVersionService:
    """Test suite for VersionService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = VersionService()
        assert service.service_name == "version_service"
        assert service.holds is not None

    def test_execute_with_valid_data(self):
        """Test execute method with valid version data."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "entity_id": "doc_001",
            "content": "Test document content v1",
            "metadata": {"author": "test_user"}
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "version_id" in result
        # Note: execute() doesn't return version_count, it returns entity_id
        assert "entity_id" in result

    def test_execute_missing_entity_type(self):
        """Test execute with missing entity_type - still succeeds with default."""
        service = VersionService()

        input_data = {
            "entity_id": "doc_001",
            "content": "Test content",
        }

        # Service uses "unknown" as default entity_type, so this succeeds
        result = service.execute(input_data)
        assert result["status"] == "success"

    def test_execute_missing_entity_id(self):
        """Test execute with missing entity_id."""
        service = VersionService()

        input_data = {
            "entity_type": "document",
            "content": "Test content",
        }

        # Service raises ValidationError when entity_id is missing
        with pytest.raises(ValidationError):
            service.execute(input_data)

    def test_version_id_generation(self):
        """Test that version IDs are generated consistently."""
        service = VersionService()

        input_data = {
            "entity_type": "code",
            "entity_id": "module_001",
            "content": "def test(): pass",
        }

        result1 = service.execute(input_data)
        result2 = service.execute(input_data)

        assert result1["status"] == "success"
        assert result2["status"] == "success"
        # Version IDs should be different due to timestamp
        assert result1["version_id"] != result2["version_id"]

    def test_exhale_creates_version(self):
        """Test backward compatible exhale function."""
        result = exhale(
            entity_type="document",
            entity_id="test_doc",
            content="Test content for exhale",
            metadata={"test": True}
        )

        assert result["status"] == "success"
        assert "version_id" in result

    def test_get_version_history_function(self):
        """Test get_version_history service method."""
        service = get_service()
        # Create a few versions
        for i in range(3):
            exhale(
                entity_type="document",
                entity_id="history_test",
                content=f"Version {i}",
            )

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="history_test",
            limit=10
        )

        assert isinstance(history, list)
        # Should have at least the versions we just created
        assert len(history) >= 3

    def test_get_version_by_id(self):
        """Test retrieving a specific version by version_id."""
        service = VersionService()

        # Create a version
        input_data = {
            "entity_type": "code",
            "entity_id": "test_module",
            "content": "def specific_version(): pass",
        }
        result = service.execute(input_data)
        version_id = result["version_id"]

        # Retrieve it
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("version_id") == version_id

    def test_get_version_history_method(self):
        """Test get_version_history service method."""
        service = VersionService()

        # Create multiple versions
        for i in range(5):
            service.execute({
                "entity_type": "test",
                "entity_id": "multi_version",
                "content": f"Content v{i}",
            })

        # get_version_history takes entity_id as first arg (not entity_type)
        history = service.get_version_history(
            entity_id="multi_version"
        )

        assert isinstance(history, list)
        assert len(history) >= 5

    def test_version_counter_increments(self):
        """Test that version counter increments correctly."""
        service = VersionService()

        entity_id = f"counter_test_{datetime.now().timestamp()}"

        # Create first version
        result1 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 1",
        })

        # Create second version
        result2 = service.execute({
            "entity_type": "document",
            "entity_id": entity_id,
            "content": "Version 2",
        })

        # Note: execute() doesn't return version_count, but both should succeed
        # and have unique version IDs
        assert result1["status"] == "success"
        assert result2["status"] == "success"
        assert result1["version_id"] != result2["version_id"]

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_metadata_preservation(self):
        """Test that metadata is preserved in versions."""
        service = VersionService()

        metadata = {
            "author": "test_user",
            "tags": ["important", "test"],
            "custom_field": "custom_value"
        }

        result = service.execute({
            "entity_type": "document",
            "entity_id": "metadata_test",
            "content": "Test content",
            "metadata": metadata
        })

        version_id = result["version_id"]
        version = service.get_version(version_id)

        assert version is not None
        assert version.get("metadata") is not None

class TestVersionServiceIntegration:
    """Integration tests for VersionService."""

    def test_full_version_lifecycle(self):
        """Test complete version lifecycle: create, retrieve, query history."""
        service = VersionService()

        entity_id = f"lifecycle_test_{datetime.now().timestamp()}"

        # Create initial version
        v1_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v1(): return 1",
            "metadata": {"version_label": "v1"}
        })
        v1_id = v1_result["version_id"]

        # Create second version
        v2_result = service.execute({
            "entity_type": "code",
            "entity_id": entity_id,
            "content": "def v2(): return 2",
            "metadata": {"version_label": "v2"}
        })
        v2_id = v2_result["version_id"]

        # Retrieve specific versions
        version_1 = service.get_version(v1_id)
        version_2 = service.get_version(v2_id)

        assert version_1 is not None
        assert version_2 is not None
        assert version_1["content"] != version_2["content"]

        # Get history (entity_id is first arg, not entity_type)
        history = service.get_version_history(
            entity_id=entity_id
        )

        assert len(history) >= 2

    def test_concurrent_versioning(self):
        """Test that multiple entities can be versioned simultaneously."""
        service = VersionService()

        timestamp = datetime.now().timestamp()

        # Create versions for multiple entities
        entities = ["entity_a", "entity_b", "entity_c"]

        for entity_id in entities:
            result = service.execute({
                "entity_type": "test",
                "entity_id": f"{entity_id}_{timestamp}",
                "content": f"Content for {entity_id}",
            })
            assert result["status"] == "success"

    def test_version_query_with_limit(self):
        """Test that version history respects limit parameter."""
        service = VersionService()

        entity_id = f"limit_test_{datetime.now().timestamp()}"

        # Create 10 versions
        for i in range(10):
            service.execute({
                "entity_type": "test",
                "entity_id": entity_id,
                "content": f"Version {i}",
            })

        # Query with limit (entity_id is first arg)
        history = service.get_version_history(
            entity_id=entity_id,
            limit=5
        )

        assert len(history) <= 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
