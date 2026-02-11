"""Tests for search_service migrated to UnifiedService pattern."""

import pytest
from datetime import datetime

from src.services.central_services.search_service.service_migrated import (
    SearchService,
    get_service,
    search,
    ValidationError,
)

class TestSearchService:
    """Test suite for SearchService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = SearchService()
        assert service.service_name == "search_service"
        assert service.holds is not None

    def test_execute_with_valid_search(self):
        """Test execute method with valid search query."""
        service = SearchService()

        input_data = {
            "query": "test search query",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result

    def test_execute_missing_query(self):
        """Test execute with missing query."""
        service = SearchService()

        input_data = {
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_execute_various_search_types(self):
        """Test execute with different search types."""
        service = SearchService()

        search_types = ["keyword", "semantic", "regex", "sql"]

        for search_type in search_types:
            input_data = {
                "query": "test query",
                "search_type": search_type,
                "sources": ["documents"],
            }

            result = service.execute(input_data)
            assert result["status"] == "success"
            assert result["search_type"] == search_type

    def test_search_with_metadata(self):
        """Test search with additional metadata."""
        service = SearchService()

        input_data = {
            "query": "metadata test",
            "search_type": "keyword",
            "sources": ["documents"],
            "metadata": {
                "user_id": "test_user",
                "context": "testing"
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result

    def test_backward_compatible_search(self):
        """Test backward compatible search function."""
        result = search(
            query="backward compatible test",
            search_type="keyword",
            sources=["documents"]
        )

        assert result["status"] == "success"
        assert "results" in result

    def test_get_search_history_function(self):
        """Test get_search_history service method."""
        service = get_service()
        # Perform a few searches
        for i in range(3):
            search(
                query=f"history test {i}",
                search_type="keyword",
                sources=["documents"]
            )

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=10)

        assert isinstance(history, list)
        assert len(history) >= 3

    def test_get_search_by_id(self):
        """Test retrieving a specific search by search_id."""
        service = SearchService()

        # Perform a search
        result = service.execute({
            "query": "specific search test",
            "search_type": "keyword",
            "sources": ["documents"],
        })
        search_id = result["search_id"]

        # Retrieve it
        search_record = service.get_search(search_id)

        assert search_record is not None
        assert search_record.get("search_id") == search_id

    def test_search_history_ordering(self):
        """Test that search history is ordered by timestamp."""
        service = SearchService()

        # Perform multiple searches
        for i in range(5):
            service.execute({
                "query": f"order test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=5)

        # Check that timestamps are in descending order (most recent first)
        if len(history) >= 2:
            timestamps = [record.get("timestamp") for record in history]
            # Should be sorted in descending order
            assert all(
                timestamps[i] >= timestamps[i + 1]
                for i in range(len(timestamps) - 1)
                if timestamps[i] and timestamps[i + 1]
            )

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_search_with_filters(self):
        """Test search with additional filters."""
        service = SearchService()

        input_data = {
            "query": "filter test",
            "search_type": "keyword",
            "sources": ["documents", "atoms"],
            "filters": {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"

    def test_empty_query_handling(self):
        """Test handling of empty query string."""
        service = SearchService()

        input_data = {
            "query": "",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        # Should either succeed with empty results or error
        assert "status" in result

class TestSearchServiceIntegration:
    """Integration tests for SearchService."""

    def test_full_search_lifecycle(self):
        """Test complete search lifecycle: perform, retrieve, query history."""
        service = SearchService()

        # Perform search
        search_result = service.execute({
            "query": "lifecycle test query",
            "search_type": "semantic",
            "sources": ["documents", "atoms"],
            "metadata": {"test": "lifecycle"}
        })

        search_id = search_result["search_id"]

        # Retrieve specific search
        search_record = service.get_search(search_id)
        assert search_record is not None
        assert search_record["query"] == "lifecycle test query"

        # Get history (query as first arg, limit as second)
        history = service.get_search_history(query=None, limit=10)
        assert any(
            record.get("search_id") == search_id
            for record in history
        )

    def test_multiple_search_types_integration(self):
        """Test that different search types can coexist."""
        service = SearchService()

        search_configs = [
            {"query": "keyword test", "search_type": "keyword"},
            {"query": "semantic test", "search_type": "semantic"},
            {"query": "test.*pattern", "search_type": "regex"},
        ]

        search_ids = []
        for config in search_configs:
            config["sources"] = ["documents"]
            result = service.execute(config)
            assert result["status"] == "success"
            search_ids.append(result["search_id"])

        # Verify all searches are in history
        history = service.get_search_history(query=None, limit=20)
        history_ids = [record.get("search_id") for record in history]

        for search_id in search_ids:
            assert search_id in history_ids

    def test_search_results_structure(self):
        """Test that search results have expected structure."""
        service = SearchService()

        result = service.execute({
            "query": "structure test",
            "search_type": "keyword",
            "sources": ["documents"],
        })

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_concurrent_searches(self):
        """Test that multiple searches can be performed without conflicts."""
        service = SearchService()

        # Perform multiple searches rapidly
        results = []
        for i in range(10):
            result = service.execute({
                "query": f"concurrent test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })
            results.append(result)

        # All should succeed
        assert all(r["status"] == "success" for r in results)

        # All should have unique search IDs
        search_ids = [r["search_id"] for r in results]
        assert len(search_ids) == len(set(search_ids))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "tests.test_search_service_migrated.py"

import pytest
from datetime import datetime

from src.services.central_services.search_service.service_migrated import (
    SearchService,
    get_service,
    search,
    ValidationError,
)

class TestSearchService:
    """Test suite for SearchService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = SearchService()
        assert service.service_name == "search_service"
        assert service.holds is not None

    def test_execute_with_valid_search(self):
        """Test execute method with valid search query."""
        service = SearchService()

        input_data = {
            "query": "test search query",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result

    def test_execute_missing_query(self):
        """Test execute with missing query."""
        service = SearchService()

        input_data = {
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_execute_various_search_types(self):
        """Test execute with different search types."""
        service = SearchService()

        search_types = ["keyword", "semantic", "regex", "sql"]

        for search_type in search_types:
            input_data = {
                "query": "test query",
                "search_type": search_type,
                "sources": ["documents"],
            }

            result = service.execute(input_data)
            assert result["status"] == "success"
            assert result["search_type"] == search_type

    def test_search_with_metadata(self):
        """Test search with additional metadata."""
        service = SearchService()

        input_data = {
            "query": "metadata test",
            "search_type": "keyword",
            "sources": ["documents"],
            "metadata": {
                "user_id": "test_user",
                "context": "testing"
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result

    def test_backward_compatible_search(self):
        """Test backward compatible search function."""
        result = search(
            query="backward compatible test",
            search_type="keyword",
            sources=["documents"]
        )

        assert result["status"] == "success"
        assert "results" in result

    def test_get_search_history_function(self):
        """Test get_search_history service method."""
        service = get_service()
        # Perform a few searches
        for i in range(3):
            search(
                query=f"history test {i}",
                search_type="keyword",
                sources=["documents"]
            )

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=10)

        assert isinstance(history, list)
        assert len(history) >= 3

    def test_get_search_by_id(self):
        """Test retrieving a specific search by search_id."""
        service = SearchService()

        # Perform a search
        result = service.execute({
            "query": "specific search test",
            "search_type": "keyword",
            "sources": ["documents"],
        })
        search_id = result["search_id"]

        # Retrieve it
        search_record = service.get_search(search_id)

        assert search_record is not None
        assert search_record.get("search_id") == search_id

    def test_search_history_ordering(self):
        """Test that search history is ordered by timestamp."""
        service = SearchService()

        # Perform multiple searches
        for i in range(5):
            service.execute({
                "query": f"order test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=5)

        # Check that timestamps are in descending order (most recent first)
        if len(history) >= 2:
            timestamps = [record.get("timestamp") for record in history]
            # Should be sorted in descending order
            assert all(
                timestamps[i] >= timestamps[i + 1]
                for i in range(len(timestamps) - 1)
                if timestamps[i] and timestamps[i + 1]
            )

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_search_with_filters(self):
        """Test search with additional filters."""
        service = SearchService()

        input_data = {
            "query": "filter test",
            "search_type": "keyword",
            "sources": ["documents", "atoms"],
            "filters": {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"

    def test_empty_query_handling(self):
        """Test handling of empty query string."""
        service = SearchService()

        input_data = {
            "query": "",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        # Should either succeed with empty results or error
        assert "status" in result

class TestSearchServiceIntegration:
    """Integration tests for SearchService."""

    def test_full_search_lifecycle(self):
        """Test complete search lifecycle: perform, retrieve, query history."""
        service = SearchService()

        # Perform search
        search_result = service.execute({
            "query": "lifecycle test query",
            "search_type": "semantic",
            "sources": ["documents", "atoms"],
            "metadata": {"test": "lifecycle"}
        })

        search_id = search_result["search_id"]

        # Retrieve specific search
        search_record = service.get_search(search_id)
        assert search_record is not None
        assert search_record["query"] == "lifecycle test query"

        # Get history (query as first arg, limit as second)
        history = service.get_search_history(query=None, limit=10)
        assert any(
            record.get("search_id") == search_id
            for record in history
        )

    def test_multiple_search_types_integration(self):
        """Test that different search types can coexist."""
        service = SearchService()

        search_configs = [
            {"query": "keyword test", "search_type": "keyword"},
            {"query": "semantic test", "search_type": "semantic"},
            {"query": "test.*pattern", "search_type": "regex"},
        ]

        search_ids = []
        for config in search_configs:
            config["sources"] = ["documents"]
            result = service.execute(config)
            assert result["status"] == "success"
            search_ids.append(result["search_id"])

        # Verify all searches are in history
        history = service.get_search_history(query=None, limit=20)
        history_ids = [record.get("search_id") for record in history]

        for search_id in search_ids:
            assert search_id in history_ids

    def test_search_results_structure(self):
        """Test that search results have expected structure."""
        service = SearchService()

        result = service.execute({
            "query": "structure test",
            "search_type": "keyword",
            "sources": ["documents"],
        })

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_concurrent_searches(self):
        """Test that multiple searches can be performed without conflicts."""
        service = SearchService()

        # Perform multiple searches rapidly
        results = []
        for i in range(10):
            result = service.execute({
                "query": f"concurrent test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })
            results.append(result)

        # All should succeed
        assert all(r["status"] == "success" for r in results)

        # All should have unique search IDs
        search_ids = [r["search_id"] for r in results]
        assert len(search_ids) == len(set(search_ids))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
from __future__ import annotations
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
from __future__ import annotations

"""Tests for search_service migrated to UnifiedService pattern."""
from __future__ import annotations

from datetime import datetime

from src.services.central_services.search_service.service_migrated import (
    SearchService,
    get_service,
    search,
    ValidationError,
)

class TestSearchService:
    """Test suite for SearchService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = SearchService()
        assert service.service_name == "search_service"
        assert service.holds is not None

    def test_execute_with_valid_search(self):
        """Test execute method with valid search query."""
        service = SearchService()

        input_data = {
            "query": "test search query",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result

    def test_execute_missing_query(self):
        """Test execute with missing query."""
        service = SearchService()

        input_data = {
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_execute_various_search_types(self):
        """Test execute with different search types."""
        service = SearchService()

        search_types = ["keyword", "semantic", "regex", "sql"]

        for search_type in search_types:
            input_data = {
                "query": "test query",
                "search_type": search_type,
                "sources": ["documents"],
            }

            result = service.execute(input_data)
            assert result["status"] == "success"
            assert result["search_type"] == search_type

    def test_search_with_metadata(self):
        """Test search with additional metadata."""
        service = SearchService()

        input_data = {
            "query": "metadata test",
            "search_type": "keyword",
            "sources": ["documents"],
            "metadata": {
                "user_id": "test_user",
                "context": "testing"
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result

    def test_backward_compatible_search(self):
        """Test backward compatible search function."""
        result = search(
            query="backward compatible test",
            search_type="keyword",
            sources=["documents"]
        )

        assert result["status"] == "success"
        assert "results" in result

    def test_get_search_history_function(self):
        """Test get_search_history service method."""
        service = get_service()
        # Perform a few searches
        for i in range(3):
            search(
                query=f"history test {i}",
                search_type="keyword",
                sources=["documents"]
            )

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=10)

        assert isinstance(history, list)
        assert len(history) >= 3

    def test_get_search_by_id(self):
        """Test retrieving a specific search by search_id."""
        service = SearchService()

        # Perform a search
        result = service.execute({
            "query": "specific search test",
            "search_type": "keyword",
            "sources": ["documents"],
        })
        search_id = result["search_id"]

        # Retrieve it
        search_record = service.get_search(search_id)

        assert search_record is not None
        assert search_record.get("search_id") == search_id

    def test_search_history_ordering(self):
        """Test that search history is ordered by timestamp."""
        service = SearchService()

        # Perform multiple searches
        for i in range(5):
            service.execute({
                "query": f"order test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=5)

        # Check that timestamps are in descending order (most recent first)
        if len(history) >= 2:
            timestamps = [record.get("timestamp") for record in history]
            # Should be sorted in descending order
            assert all(
                timestamps[i] >= timestamps[i + 1]
                for i in range(len(timestamps) - 1)
                if timestamps[i] and timestamps[i + 1]
            )

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_search_with_filters(self):
        """Test search with additional filters."""
        service = SearchService()

        input_data = {
            "query": "filter test",
            "search_type": "keyword",
            "sources": ["documents", "atoms"],
            "filters": {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"

    def test_empty_query_handling(self):
        """Test handling of empty query string."""
        service = SearchService()

        input_data = {
            "query": "",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        # Should either succeed with empty results or error
        assert "status" in result

class TestSearchServiceIntegration:
    """Integration tests for SearchService."""

    def test_full_search_lifecycle(self):
        """Test complete search lifecycle: perform, retrieve, query history."""
        service = SearchService()

        # Perform search
        search_result = service.execute({
            "query": "lifecycle test query",
            "search_type": "semantic",
            "sources": ["documents", "atoms"],
            "metadata": {"test": "lifecycle"}
        })

        search_id = search_result["search_id"]

        # Retrieve specific search
        search_record = service.get_search(search_id)
        assert search_record is not None
        assert search_record["query"] == "lifecycle test query"

        # Get history (query as first arg, limit as second)
        history = service.get_search_history(query=None, limit=10)
        assert any(
            record.get("search_id") == search_id
            for record in history
        )

    def test_multiple_search_types_integration(self):
        """Test that different search types can coexist."""
        service = SearchService()

        search_configs = [
            {"query": "keyword test", "search_type": "keyword"},
            {"query": "semantic test", "search_type": "semantic"},
            {"query": "test.*pattern", "search_type": "regex"},
        ]

        search_ids = []
        for config in search_configs:
            config["sources"] = ["documents"]
            result = service.execute(config)
            assert result["status"] == "success"
            search_ids.append(result["search_id"])

        # Verify all searches are in history
        history = service.get_search_history(query=None, limit=20)
        history_ids = [record.get("search_id") for record in history]

        for search_id in search_ids:
            assert search_id in history_ids

    def test_search_results_structure(self):
        """Test that search results have expected structure."""
        service = SearchService()

        result = service.execute({
            "query": "structure test",
            "search_type": "keyword",
            "sources": ["documents"],
        })

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_concurrent_searches(self):
        """Test that multiple searches can be performed without conflicts."""
        service = SearchService()

        # Perform multiple searches rapidly
        results = []
        for i in range(10):
            result = service.execute({
                "query": f"concurrent test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })
            results.append(result)

        # All should succeed
        assert all(r["status"] == "success" for r in results)

        # All should have unique search IDs
        search_ids = [r["search_id"] for r in results]
        assert len(search_ids) == len(set(search_ids))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
script_id = "tests.test_search_service_migrated.py"

import pytest
from datetime import datetime

from src.services.central_services.search_service.service_migrated import (
    SearchService,
    get_service,
    search,
    ValidationError,
)

class TestSearchService:
    """Test suite for SearchService."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = SearchService()
        assert service.service_name == "search_service"
        assert service.holds is not None

    def test_execute_with_valid_search(self):
        """Test execute method with valid search query."""
        service = SearchService()

        input_data = {
            "query": "test search query",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result

    def test_execute_missing_query(self):
        """Test execute with missing query."""
        service = SearchService()

        input_data = {
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        assert result["status"] == "error"
        assert len(result["errors"]) > 0

    def test_execute_various_search_types(self):
        """Test execute with different search types."""
        service = SearchService()

        search_types = ["keyword", "semantic", "regex", "sql"]

        for search_type in search_types:
            input_data = {
                "query": "test query",
                "search_type": search_type,
                "sources": ["documents"],
            }

            result = service.execute(input_data)
            assert result["status"] == "success"
            assert result["search_type"] == search_type

    def test_search_with_metadata(self):
        """Test search with additional metadata."""
        service = SearchService()

        input_data = {
            "query": "metadata test",
            "search_type": "keyword",
            "sources": ["documents"],
            "metadata": {
                "user_id": "test_user",
                "context": "testing"
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"
        assert "search_id" in result

    def test_backward_compatible_search(self):
        """Test backward compatible search function."""
        result = search(
            query="backward compatible test",
            search_type="keyword",
            sources=["documents"]
        )

        assert result["status"] == "success"
        assert "results" in result

    def test_get_search_history_function(self):
        """Test get_search_history service method."""
        service = get_service()
        # Perform a few searches
        for i in range(3):
            search(
                query=f"history test {i}",
                search_type="keyword",
                sources=["documents"]
            )

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=10)

        assert isinstance(history, list)
        assert len(history) >= 3

    def test_get_search_by_id(self):
        """Test retrieving a specific search by search_id."""
        service = SearchService()

        # Perform a search
        result = service.execute({
            "query": "specific search test",
            "search_type": "keyword",
            "sources": ["documents"],
        })
        search_id = result["search_id"]

        # Retrieve it
        search_record = service.get_search(search_id)

        assert search_record is not None
        assert search_record.get("search_id") == search_id

    def test_search_history_ordering(self):
        """Test that search history is ordered by timestamp."""
        service = SearchService()

        # Perform multiple searches
        for i in range(5):
            service.execute({
                "query": f"order test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })

        # get_search_history takes query as first arg, limit as second
        history = service.get_search_history(query=None, limit=5)

        # Check that timestamps are in descending order (most recent first)
        if len(history) >= 2:
            timestamps = [record.get("timestamp") for record in history]
            # Should be sorted in descending order
            assert all(
                timestamps[i] >= timestamps[i + 1]
                for i in range(len(timestamps) - 1)
                if timestamps[i] and timestamps[i + 1]
            )

    def test_singleton_pattern(self):
        """Test that get_service returns the same instance."""
        service1 = get_service()
        service2 = get_service()

        assert service1 is service2

    def test_search_with_filters(self):
        """Test search with additional filters."""
        service = SearchService()

        input_data = {
            "query": "filter test",
            "search_type": "keyword",
            "sources": ["documents", "atoms"],
            "filters": {
                "date_from": "2024-01-01",
                "date_to": "2024-12-31",
            }
        }

        result = service.execute(input_data)

        assert result["status"] == "success"

    def test_empty_query_handling(self):
        """Test handling of empty query string."""
        service = SearchService()

        input_data = {
            "query": "",
            "search_type": "keyword",
            "sources": ["documents"],
        }

        result = service.execute(input_data)

        # Should either succeed with empty results or error
        assert "status" in result

class TestSearchServiceIntegration:
    """Integration tests for SearchService."""

    def test_full_search_lifecycle(self):
        """Test complete search lifecycle: perform, retrieve, query history."""
        service = SearchService()

        # Perform search
        search_result = service.execute({
            "query": "lifecycle test query",
            "search_type": "semantic",
            "sources": ["documents", "atoms"],
            "metadata": {"test": "lifecycle"}
        })

        search_id = search_result["search_id"]

        # Retrieve specific search
        search_record = service.get_search(search_id)
        assert search_record is not None
        assert search_record["query"] == "lifecycle test query"

        # Get history (query as first arg, limit as second)
        history = service.get_search_history(query=None, limit=10)
        assert any(
            record.get("search_id") == search_id
            for record in history
        )

    def test_multiple_search_types_integration(self):
        """Test that different search types can coexist."""
        service = SearchService()

        search_configs = [
            {"query": "keyword test", "search_type": "keyword"},
            {"query": "semantic test", "search_type": "semantic"},
            {"query": "test.*pattern", "search_type": "regex"},
        ]

        search_ids = []
        for config in search_configs:
            config["sources"] = ["documents"]
            result = service.execute(config)
            assert result["status"] == "success"
            search_ids.append(result["search_id"])

        # Verify all searches are in history
        history = service.get_search_history(query=None, limit=20)
        history_ids = [record.get("search_id") for record in history]

        for search_id in search_ids:
            assert search_id in history_ids

    def test_search_results_structure(self):
        """Test that search results have expected structure."""
        service = SearchService()

        result = service.execute({
            "query": "structure test",
            "search_type": "keyword",
            "sources": ["documents"],
        })

        assert result["status"] == "success"
        assert "search_id" in result
        assert "results" in result
        assert isinstance(result["results"], list)

    def test_concurrent_searches(self):
        """Test that multiple searches can be performed without conflicts."""
        service = SearchService()

        # Perform multiple searches rapidly
        results = []
        for i in range(10):
            result = service.execute({
                "query": f"concurrent test {i}",
                "search_type": "keyword",
                "sources": ["documents"],
            })
            results.append(result)

        # All should succeed
        assert all(r["status"] == "success" for r in results)

        # All should have unique search IDs
        search_ids = [r["search_id"] for r in results]
        assert len(search_ids) == len(set(search_ids))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
try:
    from truth_forge.core import get_logger as _get_logger
except Exception:
    from src.services.central_services.core import get_logger as _get_logger
_LOGGER = _get_logger(__name__)
