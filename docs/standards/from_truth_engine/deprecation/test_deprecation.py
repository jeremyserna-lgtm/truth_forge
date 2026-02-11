"""Test suite for deprecation utilities.

Run: pytest framework/standards/deprecation/test_deprecation.py -v
"""
from __future__ import annotations

"""Test suite for deprecation utilities.

Run: pytest framework/standards/deprecation/test_deprecation.py -v
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
script_id = "framework.standards.deprecation.test_deprecation.py"

import warnings

import pytest

from framework.standards.deprecation import (
    deprecated,
    get_deprecation_info,
    is_deprecated,
    pending_deprecation,
    warn_deprecated_parameter,
)

# =============================================================================
# Example deprecated code for testing
# =============================================================================

@deprecated(
    since="2.3.0",
    removal="3.0.0",
    reason="Replaced by process_items_v2 for better performance",
    replacement="process_items_v2",
)
def process_items(items: list) -> list:
    """Process items by doubling each value.

    .. deprecated:: 2.3.0
        Use :func:`process_items_v2` instead for O(n) performance.
        This function will be removed in version 3.0.0.
    """
    return [x * 2 for x in items]

def process_items_v2(items: list) -> list:
    """Process items efficiently."""
    return [x * 2 for x in items]

@deprecated(
    since="2.3.0",
    removal="3.0.0",
    reason="Use AsyncDataLoader for better concurrency",
    replacement="AsyncDataLoader",
)
class DataLoader:
    """Legacy synchronous data loader.

    .. deprecated:: 2.3.0
        Use :class:`AsyncDataLoader` instead for async support.
    """

    def __init__(self, source: str):
        self.source = source

    def load(self) -> dict:
        return {"source": self.source, "data": []}

@pending_deprecation(
    since="2.2.0",
    deprecation_version="2.3.0",
    reason="Moving to configuration-based validation",
    replacement="validate_with_config",
)
def validate_data(data: dict) -> bool:
    """Validate data structure."""
    return isinstance(data, dict)

def fetch_data(
    url: str,
    timeout: int = 30,
    verify_ssl: bool | None = None,
) -> dict:
    """Fetch data from a URL."""
    if verify_ssl is not None:
        warn_deprecated_parameter(
            param="verify_ssl",
            since="2.3.0",
            removal="3.0.0",
            replacement="ssl_context",
        )
    return {"url": url, "timeout": timeout}

# =============================================================================
# Tests
# =============================================================================

class TestDeprecatedDecorator:
    """Tests for the @deprecated decorator."""

    def test_deprecated_function_emits_warning(self):
        """Deprecated function should emit DeprecationWarning."""
        with pytest.warns(DeprecationWarning, match="process_items is deprecated"):
            process_items([1, 2, 3])

    def test_deprecated_function_still_works(self):
        """Deprecated function should still return correct results."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            result = process_items([1, 2, 3])
            assert result == [2, 4, 6]

    def test_deprecated_function_warning_message(self):
        """Warning message should contain all metadata."""
        with pytest.warns(DeprecationWarning) as record:
            process_items([1])

        warning_msg = str(record[0].message)
        assert "2.3.0" in warning_msg
        assert "3.0.0" in warning_msg
        assert "process_items_v2" in warning_msg

    def test_deprecated_class_emits_warning(self):
        """Deprecated class should emit warning on instantiation."""
        with pytest.warns(DeprecationWarning, match="DataLoader is deprecated"):
            DataLoader("test")

    def test_deprecated_class_still_works(self):
        """Deprecated class should still function correctly."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            loader = DataLoader("test_source")
            assert loader.source == "test_source"
            assert loader.load() == {"source": "test_source", "data": []}

class TestPendingDeprecation:
    """Tests for the @pending_deprecation decorator."""

    def test_pending_deprecation_emits_warning(self):
        """Pending deprecation should emit PendingDeprecationWarning."""
        with pytest.warns(PendingDeprecationWarning, match="will be deprecated"):
            validate_data({})

    def test_pending_deprecation_still_works(self):
        """Function with pending deprecation should still work."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", PendingDeprecationWarning)
            assert validate_data({"key": "value"}) is True
            assert validate_data([]) is False

class TestDeprecatedParameter:
    """Tests for deprecated parameters."""

    def test_deprecated_parameter_emits_warning(self):
        """Using deprecated parameter should emit warning."""
        with pytest.warns(DeprecationWarning, match="verify_ssl"):
            fetch_data("https://example.com", verify_ssl=True)

    def test_no_warning_without_deprecated_param(self):
        """No warning when deprecated parameter not used."""
        with warnings.catch_warnings():
            warnings.simplefilter("error", DeprecationWarning)
            result = fetch_data("https://example.com")
            assert result["url"] == "https://example.com"

class TestDeprecationMetadata:
    """Tests for deprecation info helpers."""

    def test_get_deprecation_info(self):
        """Should retrieve deprecation metadata."""
        info = get_deprecation_info(process_items)
        assert info is not None
        assert info["since"] == "2.3.0"
        assert info["removal"] == "3.0.0"
        assert info["replacement"] == "process_items_v2"

    def test_get_deprecation_info_class(self):
        """Should retrieve class deprecation metadata."""
        info = get_deprecation_info(DataLoader)
        assert info is not None
        assert info["since"] == "2.3.0"

    def test_get_deprecation_info_not_deprecated(self):
        """Should return None for non-deprecated code."""
        info = get_deprecation_info(process_items_v2)
        assert info is None

    def test_is_deprecated(self):
        """Should correctly identify deprecated code."""
        assert is_deprecated(process_items) is True
        assert is_deprecated(DataLoader) is True
        assert is_deprecated(process_items_v2) is False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
