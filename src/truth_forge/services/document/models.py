"""Document Service Models.

Pydantic models for document management and retrieval.

MOLT LINEAGE:
- Source: New creation for LLM-aligned document management
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class DocumentType(str, Enum):
    """Document type taxonomy."""

    FRAMEWORK = "framework"
    STANDARD = "standard"
    SPECIFICATION = "specification"
    PLAN = "plan"
    ADR = "adr"
    GUIDE = "guide"
    REFERENCE = "reference"
    INDEX = "index"
    LOG = "log"
    PERSONAL = "personal"
    UNKNOWN = "unknown"


class DocumentStatus(str, Enum):
    """Document lifecycle status."""

    DRAFT = "draft"
    REVIEW = "review"
    CANONICAL = "canonical"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    UNKNOWN = "unknown"


class DocumentDomain(str, Enum):
    """Business domain taxonomy."""

    FRAMEWORK = "framework"
    NOT_ME = "not-me"
    PRIMITIVE_ENGINE = "primitive-engine"
    CREDENTIAL_ATLAS = "credential-atlas"
    INFRASTRUCTURE = "infrastructure"
    BUSINESS = "business"
    PERSONAL = "personal"
    OPERATIONS = "operations"
    UNKNOWN = "unknown"


class Document(BaseModel):
    """Parsed document with frontmatter and content."""

    # Identity
    id: str = Field(description="Unique document identifier")
    path: Path = Field(description="File path relative to root")
    title: str = Field(description="Human-readable title")

    # Classification
    doc_type: DocumentType = Field(default=DocumentType.UNKNOWN)
    status: DocumentStatus = Field(default=DocumentStatus.UNKNOWN)
    domain: DocumentDomain = Field(default=DocumentDomain.UNKNOWN)

    # LLM Alignment
    summary: str | None = Field(default=None, description="2-3 sentence TL;DR")
    answers: list[str] = Field(default_factory=list, description="Questions this answers")

    # Relationships
    related: list[str] = Field(default_factory=list)
    supersedes: list[str] = Field(default_factory=list)
    superseded_by: str | None = Field(default=None)
    blocks: list[str] = Field(default_factory=list)
    implements: list[str] = Field(default_factory=list)

    # Discovery
    tags: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)

    # Quality
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    created: date | None = Field(default=None)
    updated: date | None = Field(default=None)

    # Content
    content: str = Field(default="", description="Document body without frontmatter")
    content_hash: str | None = Field(default=None, description="Hash for change detection")

    # Embedding
    embedding: list[float] | None = Field(default=None, exclude=True)
    embedding_hash: str | None = Field(default=None)

    model_config = ConfigDict(use_enum_values=True)


class DocumentQuery(BaseModel):
    """Query for document retrieval."""

    # Natural language query
    question: str | None = Field(default=None, description="Natural language question")

    # Structured filters
    doc_type: DocumentType | None = Field(default=None)
    status: DocumentStatus | None = Field(default=None)
    domain: DocumentDomain | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)

    # Search behavior
    include_deprecated: bool = Field(default=False)
    include_content: bool = Field(default=True)
    max_results: int = Field(default=10, ge=1, le=100)

    # Semantic search
    use_embeddings: bool = Field(default=True)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Single search result with relevance scoring."""

    document: Document
    relevance_score: float = Field(ge=0.0, le=1.0)
    match_reason: str = Field(description="Why this matched")
    matched_questions: list[str] = Field(default_factory=list)


class DocumentResult(BaseModel):
    """Document retrieval result."""

    results: list[SearchResult]
    query: DocumentQuery
    total_documents: int
    search_time_ms: float
    embedding_used: bool


class DocumentIndex(BaseModel):
    """Full document index for persistence."""

    documents: dict[str, Document]
    by_type: dict[str, list[str]]
    by_domain: dict[str, list[str]]
    by_status: dict[str, list[str]]
    by_tag: dict[str, list[str]]
    question_index: dict[str, list[str]]  # question -> [doc_ids]
    generated_at: datetime
    document_count: int
    embedded_count: int


class EmbeddingRequest(BaseModel):
    """Request to embed document content."""

    doc_id: str
    content: str
    include_summary: bool = True
    include_questions: bool = True


class EmbeddingResult(BaseModel):
    """Result of embedding generation."""

    doc_id: str
    embedding: list[float]
    content_hash: str
    model: str
    dimensions: int


# =============================================================================
# KNOWLEDGE ATOM INTEGRATION
# =============================================================================


class DocumentAtom(BaseModel):
    """Knowledge atom extracted from a document.

    Bridges DocumentService and KnowledgeService:
    - Document owns the source (markdown file with frontmatter)
    - KnowledgeService extracts structured knowledge (entities, themes)
    - DocumentAtom links them for semantic search

    FLOW:
    Document (HOLD₁) → KnowledgeService (AGENT) → DocumentAtom (HOLD₂)
    """

    # Source linkage
    doc_id: str = Field(description="Source document ID")
    doc_path: str = Field(description="Source document path")
    content_hash: str = Field(description="Hash of content when extracted")

    # Extracted knowledge (from KnowledgeService)
    summary: str = Field(description="LLM-generated summary")
    entities: list[str] = Field(default_factory=list, description="People, places, orgs")
    themes: list[str] = Field(default_factory=list, description="Key topics/themes")

    # Extraction metadata
    llm_model: str | None = Field(default=None, description="Model used for extraction")
    extraction_cost: float = Field(default=0.0, description="Cost of extraction")
    extracted_at: datetime | None = Field(default=None)

    # Search optimization
    combined_text: str = Field(
        default="",
        description="Summary + entities + themes combined for search",
    )

    def build_combined_text(self) -> str:
        """Build combined text for semantic search."""
        parts = [self.summary]
        if self.entities:
            parts.append(f"Entities: {', '.join(self.entities)}")
        if self.themes:
            parts.append(f"Themes: {', '.join(self.themes)}")
        return " ".join(parts)


class AtomQuery(BaseModel):
    """Query for semantic search across atoms."""

    # Natural language query
    query: str = Field(description="Semantic query")

    # Filters
    domains: list[DocumentDomain] = Field(default_factory=list)
    doc_types: list[DocumentType] = Field(default_factory=list)
    entities: list[str] = Field(default_factory=list, description="Filter by entity")
    themes: list[str] = Field(default_factory=list, description="Filter by theme")

    # Search behavior
    max_results: int = Field(default=10, ge=1, le=50)
    include_content: bool = Field(default=True)


class AtomSearchResult(BaseModel):
    """Result of atom-based semantic search."""

    document: Document
    atom: DocumentAtom
    relevance_score: float = Field(ge=0.0, le=1.0)
    match_reason: str
    matched_entities: list[str] = Field(default_factory=list)
    matched_themes: list[str] = Field(default_factory=list)


class AtomExtractionResult(BaseModel):
    """Result of atom extraction for a document."""

    doc_id: str
    success: bool
    atom: DocumentAtom | None = None
    error: str | None = None
    cost: float = 0.0
