"""Tests for document service module."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

from truth_forge.services.document.models import (
    Document,
    DocumentDomain,
    DocumentQuery,
)
from truth_forge.services.document.service import DocumentService


# Create a concrete test class that implements the abstract method
class ConcreteDocumentService(DocumentService):
    """DocumentService with process method implemented for testing."""

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Implement abstract process method."""
        return {"processed": True}


class TestDocumentService:
    """Test DocumentService class."""

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_init(self, mock_base_init: Mock) -> None:
        """Test DocumentService initialization."""
        mock_base_init.return_value = None

        service = ConcreteDocumentService()
        service._logger = Mock()  # Mock logger
        service.process = Mock()  # Mock abstract method
        assert service.service_name == "document"
        assert service._index is None
        assert len(service._atoms) == 0

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_on_startup(self, mock_base_init: Mock) -> None:
        """Test service startup."""
        mock_base_init.return_value = None

        service = ConcreteDocumentService()
        service._logger = Mock()
        service.process = Mock()  # Mock abstract method

        with patch.object(service, "rebuild_index") as mock_rebuild:
            service.on_startup()
            mock_rebuild.assert_called_once()

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_get_document_not_found(self, mock_base_init: Mock) -> None:
        """Test get_document when document not found."""
        mock_base_init.return_value = None

        service = ConcreteDocumentService()
        service._logger = Mock()
        # Mock index with rebuild_index
        with patch.object(service, "rebuild_index"):
            mock_index = Mock()
            mock_index.documents = {}
            service._index = mock_index

            result = service.get_document("nonexistent")
            assert result is None

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_get_document_found(self, mock_base_init: Mock) -> None:
        """Test get_document when document found."""
        mock_base_init.return_value = None

        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test",
        )

        service = ConcreteDocumentService()
        service._logger = Mock()
        service.process = Mock()  # Mock abstract method
        with patch.object(service, "rebuild_index"):
            mock_index = Mock()
            mock_index.documents = {"doc-123": doc}
            service._index = mock_index

            result = service.get_document("doc-123")
            assert result == doc

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_get_summary(self, mock_base_init: Mock) -> None:
        """Test get_summary method."""
        mock_base_init.return_value = None

        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test",
            summary="Test summary",
        )

        service = ConcreteDocumentService()
        service._logger = Mock()
        service.process = Mock()  # Mock abstract method
        with patch.object(service, "rebuild_index"):
            mock_index = Mock()
            mock_index.documents = {"doc-123": doc}
            service._index = mock_index

            summary = service.get_summary("doc-123")
            assert summary == "Test summary"

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_query_string(self, mock_base_init: Mock) -> None:
        """Test query with string."""
        mock_base_init.return_value = None

        service = ConcreteDocumentService()
        service._logger = Mock()

        # Mock index
        with patch.object(service, "rebuild_index"):
            mock_index = Mock()
            mock_index.documents = {}
            mock_index.question_index = {}
            service._index = mock_index

            with patch.object(service, "_match_questions", return_value=[]):
                with patch.object(service, "_filter_candidates", return_value=[]):
                    with patch.object(service, "_score_document", return_value=(0.5, "test")):
                        result = service.query("Test question")
                        assert result.query.question == "Test question"

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_query_document_query(self, mock_base_init: Mock) -> None:
        """Test query with DocumentQuery object."""
        mock_base_init.return_value = None

        service = ConcreteDocumentService()
        service._logger = Mock()

        with patch.object(service, "rebuild_index"):
            mock_index = Mock()
            mock_index.documents = {}
            mock_index.question_index = {}
            service._index = mock_index

            query = DocumentQuery(question="Test")
            with patch.object(service, "_match_questions", return_value=[]):
                with patch.object(service, "_filter_candidates", return_value=[]):
                    with patch.object(service, "_score_document", return_value=(0.5, "test")):
                        result = service.query(query)
                        assert result.query == query

    @patch("truth_forge.services.document.service.BaseService.__init__")
    def test_list_by_domain(self, mock_base_init: Mock) -> None:
        """Test list_by_domain method."""
        mock_base_init.return_value = None

        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test",
            domain=DocumentDomain.FRAMEWORK,
        )

        service = ConcreteDocumentService()
        service._logger = Mock()
        service.process = Mock()  # Mock abstract method
        with patch.object(service, "rebuild_index"):
            mock_index = Mock()
            mock_index.by_domain = {"framework": ["doc-123"]}
            mock_index.documents = {"doc-123": doc}
            service._index = mock_index

            docs = service.list_by_domain("framework")
            assert len(docs) == 1
            assert docs[0].id == "doc-123"
