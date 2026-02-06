"""Tests for document models module."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from truth_forge.services.document.models import (
    AtomExtractionResult,
    AtomQuery,
    Document,
    DocumentAtom,
    DocumentDomain,
    DocumentIndex,
    DocumentQuery,
    DocumentResult,
    DocumentStatus,
    DocumentType,
    EmbeddingRequest,
    EmbeddingResult,
    SearchResult,
)


class TestEnums:
    """Test enum classes."""

    def test_document_type(self) -> None:
        """Test DocumentType enum."""
        assert DocumentType.FRAMEWORK.value == "framework"
        assert DocumentType.SPECIFICATION.value == "specification"

    def test_document_status(self) -> None:
        """Test DocumentStatus enum."""
        assert DocumentStatus.DRAFT.value == "draft"
        assert DocumentStatus.CANONICAL.value == "canonical"

    def test_document_domain(self) -> None:
        """Test DocumentDomain enum."""
        assert DocumentDomain.FRAMEWORK.value == "framework"
        assert DocumentDomain.NOT_ME.value == "not-me"


class TestDocument:
    """Test Document model."""

    def test_creation(self) -> None:
        """Test creating Document."""
        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test Document",
        )
        assert doc.id == "doc-123"
        assert doc.title == "Test Document"
        assert doc.doc_type == DocumentType.UNKNOWN

    def test_with_classification(self) -> None:
        """Test Document with classification."""
        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test",
            doc_type=DocumentType.FRAMEWORK,
            status=DocumentStatus.CANONICAL,
            domain=DocumentDomain.FRAMEWORK,
        )
        assert doc.doc_type == DocumentType.FRAMEWORK
        assert doc.status == DocumentStatus.CANONICAL

    def test_with_content(self) -> None:
        """Test Document with content."""
        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test",
            content="Document content here",
        )
        assert doc.content == "Document content here"


class TestDocumentQuery:
    """Test DocumentQuery model."""

    def test_defaults(self) -> None:
        """Test default query values."""
        query = DocumentQuery()
        assert query.max_results == 10
        assert query.use_embeddings is True
        assert query.include_deprecated is False

    def test_with_question(self) -> None:
        """Test query with natural language question."""
        query = DocumentQuery(question="How does X work?")
        assert query.question == "How does X work?"

    def test_with_filters(self) -> None:
        """Test query with structured filters."""
        query = DocumentQuery(
            doc_type=DocumentType.FRAMEWORK,
            domain=DocumentDomain.FRAMEWORK,
            tags=["test"],
        )
        assert query.doc_type == DocumentType.FRAMEWORK
        assert "test" in query.tags


class TestSearchResult:
    """Test SearchResult model."""

    def test_creation(self) -> None:
        """Test creating SearchResult."""
        doc = Document(
            id="doc-123",
            path=Path("test.md"),
            title="Test",
        )
        result = SearchResult(
            document=doc,
            relevance_score=0.9,
            match_reason="Matched question",
        )
        assert result.document == doc
        assert result.relevance_score == 0.9


class TestDocumentResult:
    """Test DocumentResult model."""

    def test_creation(self) -> None:
        """Test creating DocumentResult."""
        query = DocumentQuery()
        result = DocumentResult(
            results=[],
            query=query,
            total_documents=100,
            search_time_ms=50.0,
            embedding_used=False,
        )
        assert result.total_documents == 100
        assert result.search_time_ms == 50.0


class TestDocumentAtom:
    """Test DocumentAtom model."""

    def test_creation(self) -> None:
        """Test creating DocumentAtom."""
        atom = DocumentAtom(
            doc_id="doc-123",
            doc_path="test.md",
            content_hash="abc123",
            summary="Test summary",
            entities=["entity1", "entity2"],
            themes=["theme1"],
        )
        assert atom.doc_id == "doc-123"
        assert len(atom.entities) == 2

    def test_build_combined_text(self) -> None:
        """Test build_combined_text method."""
        atom = DocumentAtom(
            doc_id="test",
            doc_path="test.md",
            content_hash="hash",
            summary="Summary",
            entities=["Entity1"],
            themes=["Theme1"],
        )
        combined = atom.build_combined_text()
        assert "Summary" in combined
        assert "Entity1" in combined
        assert "Theme1" in combined


class TestAtomQuery:
    """Test AtomQuery model."""

    def test_creation(self) -> None:
        """Test creating AtomQuery."""
        query = AtomQuery(query="Test query")
        assert query.query == "Test query"
        assert query.max_results == 10


class TestDocumentIndex:
    """Test DocumentIndex model."""

    def test_creation(self) -> None:
        """Test creating DocumentIndex."""
        index = DocumentIndex(
            documents={},
            by_type={},
            by_domain={},
            by_status={},
            by_tag={},
            question_index={},
            generated_at=datetime.now(),
            document_count=0,
            embedded_count=0,
        )
        assert index.document_count == 0
        assert index.embedded_count == 0


class TestEmbeddingRequest:
    """Test EmbeddingRequest model."""

    def test_creation(self) -> None:
        """Test creating EmbeddingRequest."""
        request = EmbeddingRequest(
            doc_id="doc-123",
            content="Test content",
        )
        assert request.doc_id == "doc-123"
        assert request.include_summary is True


class TestEmbeddingResult:
    """Test EmbeddingResult model."""

    def test_creation(self) -> None:
        """Test creating EmbeddingResult."""
        result = EmbeddingResult(
            doc_id="doc-123",
            embedding=[0.1, 0.2, 0.3],
            content_hash="hash",
            model="test-model",
            dimensions=3,
        )
        assert result.doc_id == "doc-123"
        assert len(result.embedding) == 3
        assert result.dimensions == 3


class TestAtomExtractionResult:
    """Test AtomExtractionResult model."""

    def test_success(self) -> None:
        """Test successful extraction result."""
        atom = DocumentAtom(
            doc_id="test",
            doc_path="test.md",
            content_hash="hash",
            summary="Summary",
        )
        result = AtomExtractionResult(
            doc_id="test",
            success=True,
            atom=atom,
        )
        assert result.success is True
        assert result.atom == atom

    def test_failure(self) -> None:
        """Test failed extraction result."""
        result = AtomExtractionResult(
            doc_id="test",
            success=False,
            error="Extraction failed",
        )
        assert result.success is False
        assert result.error == "Extraction failed"
