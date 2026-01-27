"""Tests for identity service module.

Tests the IdentityService class and helper functions.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from truth_forge.services.identity import (
    IdentityService,
    _generate_hash,
    _slugify,
    _format_sequence,
)


class TestHelperFunctions:
    """Tests for module-level helper functions."""

    def test_generate_hash_returns_hex_string(self) -> None:
        """Test _generate_hash returns hexadecimal string."""
        result = _generate_hash("test content")

        assert all(c in "0123456789abcdef" for c in result)

    def test_generate_hash_default_length(self) -> None:
        """Test _generate_hash default length is 16."""
        result = _generate_hash("test")

        assert len(result) == 16

    def test_generate_hash_custom_length(self) -> None:
        """Test _generate_hash respects custom length."""
        result = _generate_hash("test", length=8)

        assert len(result) == 8

    def test_generate_hash_deterministic(self) -> None:
        """Test _generate_hash returns same value for same input."""
        result1 = _generate_hash("same content")
        result2 = _generate_hash("same content")

        assert result1 == result2

    def test_generate_hash_different_for_different_input(self) -> None:
        """Test _generate_hash returns different values for different input."""
        result1 = _generate_hash("content A")
        result2 = _generate_hash("content B")

        assert result1 != result2

    def test_slugify_lowercase(self) -> None:
        """Test _slugify converts to lowercase."""
        result = _slugify("UPPERCASE")

        assert result == "uppercase"

    def test_slugify_replaces_special_chars(self) -> None:
        """Test _slugify replaces special characters with hyphens."""
        result = _slugify("Hello World!")

        assert result == "hello-world"

    def test_slugify_strips_hyphens(self) -> None:
        """Test _slugify strips leading/trailing hyphens."""
        result = _slugify("  @test@  ")

        assert result == "test"

    def test_slugify_handles_numbers(self) -> None:
        """Test _slugify preserves numbers."""
        result = _slugify("Test123")

        assert result == "test123"

    def test_format_sequence_default_width(self) -> None:
        """Test _format_sequence default width is 4."""
        result = _format_sequence(5)

        assert result == "0005"

    def test_format_sequence_custom_width(self) -> None:
        """Test _format_sequence respects custom width."""
        result = _format_sequence(5, width=6)

        assert result == "000005"

    def test_format_sequence_large_number(self) -> None:
        """Test _format_sequence handles large numbers."""
        result = _format_sequence(12345)

        assert result == "12345"


class TestIdentityService:
    """Tests for IdentityService class."""

    def test_service_name(self) -> None:
        """Test service name is set correctly."""
        assert IdentityService.service_name == "identity"

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_process_raises_not_implemented(self, mock_logger: MagicMock) -> None:
        """Test process raises NotImplementedError."""
        service = IdentityService.__new__(IdentityService)

        with pytest.raises(NotImplementedError) as exc_info:
            service.process({"id": "123"})

        assert "synchronous" in str(exc_info.value)

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_create_schema_returns_empty(self, mock_logger: MagicMock) -> None:
        """Test create_schema returns empty string."""
        service = IdentityService.__new__(IdentityService)

        schema = service.create_schema()

        assert schema == ""

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_script_id(self, mock_logger: MagicMock) -> None:
        """Test generate_script_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_script_id(
            script_name="test_script.py",
            script_path="/path/to/script",
            version="2.0",
        )

        assert result.startswith("script:test_script:2.0:")
        assert len(result.split(":")) == 4

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_script_id_deterministic(self, mock_logger: MagicMock) -> None:
        """Test generate_script_id is deterministic."""
        service = IdentityService.__new__(IdentityService)

        result1 = service.generate_script_id("script.py", "/path", "1.0")
        result2 = service.generate_script_id("script.py", "/path", "1.0")

        assert result1 == result2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_document_id(self, mock_logger: MagicMock) -> None:
        """Test generate_document_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_document_id("/path/to/doc.txt")

        assert result.startswith("doc:")
        assert len(result.split(":")) == 2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_document_id_with_metadata(self, mock_logger: MagicMock) -> None:
        """Test generate_document_id with metadata."""
        service = IdentityService.__new__(IdentityService)

        result1 = service.generate_document_id("/path", {"key": "value1"})
        result2 = service.generate_document_id("/path", {"key": "value2"})

        # Different metadata should produce different IDs
        assert result1 != result2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_message_id(self, mock_logger: MagicMock) -> None:
        """Test generate_message_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_message_id("conv-123", 5)

        assert result.startswith("msg:")
        assert ":0005" in result

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_conversation_id(self, mock_logger: MagicMock) -> None:
        """Test generate_conversation_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_conversation_id("email", "thread-123")

        assert result.startswith("conv:email:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_sentence_id(self, mock_logger: MagicMock) -> None:
        """Test generate_sentence_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_sentence_id("parent-123", 3)

        assert result.startswith("sent:")
        assert ":0003" in result

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_span_id(self, mock_logger: MagicMock) -> None:
        """Test generate_span_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_span_id("parent-123", 2)

        assert result.startswith("span:")
        assert ":0002" in result

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_word_id(self, mock_logger: MagicMock) -> None:
        """Test generate_word_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_word_id("parent-123", 10)

        assert result.startswith("word:")
        assert ":0010" in result

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_token_id(self, mock_logger: MagicMock) -> None:
        """Test generate_token_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_token_id("parent-123", 1)

        assert result.startswith("token:")
        # Token uses 12-char hash
        assert ":0001" in result

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_primitive_id_without_source(self, mock_logger: MagicMock) -> None:
        """Test generate_primitive_id without source_id."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_primitive_id(primitive_type="test")

        assert result.startswith("test:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_primitive_id_with_source(self, mock_logger: MagicMock) -> None:
        """Test generate_primitive_id with source_id."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_primitive_id(
            primitive_type="prim",
            source_id="source-123",
        )

        assert result.startswith("prim:")
        # With source, format is prim:hash:ulid
        parts = result.split(":")
        assert len(parts) >= 3

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_primitive_id_uses_ulid(self, mock_logger: MagicMock) -> None:
        """Test generate_primitive_id uses ULID when available."""
        service = IdentityService.__new__(IdentityService)
        result = service.generate_primitive_id()

        # Just verify it produces a valid ID
        assert result.startswith("prim:")
        # If ULID is available, it will have a specific format
        parts = result.split(":")
        assert len(parts) >= 2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_primitive_id_fallback(self, mock_logger: MagicMock) -> None:
        """Test generate_primitive_id falls back when ULID unavailable."""
        service = IdentityService.__new__(IdentityService)

        # Mock ImportError for ULID
        with patch.dict("sys.modules", {"ulid": None}):
            # Need to trigger actual ImportError
            import importlib

            original_import = __builtins__["__import__"]

            def mock_import(name: str, *args, **kwargs):  # type: ignore[no-untyped-def]
                if name == "ulid":
                    raise ImportError("No module named 'ulid'")
                return original_import(name, *args, **kwargs)

            with patch("builtins.__import__", side_effect=mock_import):
                result = service.generate_primitive_id()

        # Result should still be valid
        assert result.startswith("prim:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_run_id(self, mock_logger: MagicMock) -> None:
        """Test generate_run_id produces expected format."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_run_id()

        assert result.startswith("run:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_run_id_unique(self, mock_logger: MagicMock) -> None:
        """Test generate_run_id produces unique values."""
        service = IdentityService.__new__(IdentityService)

        result1 = service.generate_run_id()
        result2 = service.generate_run_id()

        assert result1 != result2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_atom_id_with_all_params(self, mock_logger: MagicMock) -> None:
        """Test generate_atom_id with all parameters."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_atom_id(
            source_id="src-123",
            source_name="test-source",
            content="test content",
        )

        assert result.startswith("atom:")
        assert len(result.split(":")) == 2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_atom_id_with_source_name_only(
        self, mock_logger: MagicMock
    ) -> None:
        """Test generate_atom_id with source_name only."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_atom_id(source_name="test-source")

        assert result.startswith("atom:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_atom_id_with_source_id_only(self, mock_logger: MagicMock) -> None:
        """Test generate_atom_id with source_id only."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_atom_id(source_id="src-123")

        assert result.startswith("atom:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_atom_id_with_content_only(self, mock_logger: MagicMock) -> None:
        """Test generate_atom_id with content only."""
        service = IdentityService.__new__(IdentityService)

        result = service.generate_atom_id(content="test content")

        assert result.startswith("atom:")

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_atom_id_no_params(self, mock_logger: MagicMock) -> None:
        """Test generate_atom_id with no parameters generates random ID."""
        service = IdentityService.__new__(IdentityService)

        result1 = service.generate_atom_id()
        result2 = service.generate_atom_id()

        # Should be different due to UUID
        assert result1 != result2

    @patch.object(IdentityService, "logger", new_callable=lambda: MagicMock())
    def test_generate_atom_id_deterministic_with_content(
        self, mock_logger: MagicMock
    ) -> None:
        """Test generate_atom_id is deterministic with same content."""
        service = IdentityService.__new__(IdentityService)

        result1 = service.generate_atom_id(content="same content")
        result2 = service.generate_atom_id(content="same content")

        assert result1 == result2

    def test_inherits_from_base_service(self) -> None:
        """Test IdentityService inherits from BaseService."""
        from truth_forge.services.base import BaseService

        assert issubclass(IdentityService, BaseService)
