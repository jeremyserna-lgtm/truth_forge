"""Document Service - LLM-first document retrieval.

Provides document indexing, semantic search, and retrieval optimized
for LLM consumption. Follows THE PATTERN: HOLD₁ → AGENT → HOLD₂.

MOLT LINEAGE:
- Source: New creation for LLM-aligned document management
- Version: 1.0.0
- Date: 2026-02-01
"""

from __future__ import annotations

import contextlib
import hashlib
import re
import time
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from truth_forge.services.base import BaseService
from truth_forge.services.document.models import (
    AtomExtractionResult,
    AtomQuery,
    AtomSearchResult,
    Document,
    DocumentAtom,
    DocumentDomain,
    DocumentIndex,
    DocumentQuery,
    DocumentResult,
    DocumentStatus,
    DocumentType,
    SearchResult,
)
from truth_forge.services.factory import get_service, register_service


# Directories to scan
SCAN_DIRECTORIES = ["docs", "framework", ".agent"]

# Directories to skip
SKIP_DIRECTORIES = {".git", ".venv", "node_modules", "__pycache__", ".obsidian", "archive"}


@register_service()
class DocumentService(BaseService):
    """LLM-first document retrieval service.

    Implements THE PATTERN:
    - HOLD₁: Raw markdown documents on disk
    - AGENT: Parsing, indexing, semantic search
    - HOLD₂: Structured Document objects with embeddings
    """

    service_name = "document"

    def __init__(self) -> None:
        """Initialize DocumentService."""
        super().__init__()
        self._index: DocumentIndex | None = None
        self._root: Path | None = None
        self._gateway: Any = None

        # Knowledge atom storage
        self._atoms: dict[str, DocumentAtom] = {}  # doc_id -> atom
        self._entity_index: dict[str, list[str]] = defaultdict(list)  # entity -> [doc_ids]
        self._theme_index: dict[str, list[str]] = defaultdict(list)  # theme -> [doc_ids]

        # Lazy-loaded KnowledgeService
        self._knowledge_service: Any = None

    def on_startup(self) -> None:
        """Initialize service on startup."""
        self._root = Path.cwd()
        # Lazy-load gateway for embeddings
        try:
            from truth_forge.gateway import get_gateway

            self._gateway = get_gateway()
        except ImportError:
            self._logger.warning("Gateway not available, embeddings disabled")

        # Build initial index
        self.rebuild_index()

    def on_shutdown(self) -> None:
        """Cleanup on shutdown."""
        self._logger.info(
            "document_service_shutdown",
            extra={"indexed_documents": len(self._index.documents) if self._index else 0},
        )

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def query(self, query: DocumentQuery | str) -> DocumentResult:
        """Query documents with natural language or structured filters.

        Args:
            query: Natural language question or DocumentQuery object.

        Returns:
            DocumentResult with matching documents and relevance scores.
        """
        start = time.time()

        # Convert string to query
        if isinstance(query, str):
            query = DocumentQuery(question=query)

        if self._index is None:
            self.rebuild_index()
        assert self._index is not None  # Guaranteed by rebuild_index()

        results: list[SearchResult] = []

        # First: Check `answers` field for direct question matches
        if query.question:
            question_matches = self._match_questions(query.question)
            results.extend(question_matches)

        # Second: Filter by structured criteria
        candidates = self._filter_candidates(query)

        # Third: Score by relevance
        for doc_id in candidates:
            if doc_id in [r.document.id for r in results]:
                continue  # Already matched by question

            doc = self._index.documents[doc_id]
            score, reason = self._score_document(doc, query)

            if score >= query.similarity_threshold:
                results.append(
                    SearchResult(
                        document=doc,
                        relevance_score=score,
                        match_reason=reason,
                        matched_questions=[],
                    )
                )

        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        # Limit results
        results = results[: query.max_results]

        return DocumentResult(
            results=results,
            query=query,
            total_documents=len(self._index.documents),
            search_time_ms=(time.time() - start) * 1000,
            embedding_used=False,  # TODO: Enable when embeddings ready
        )

    def get_document(self, doc_id: str) -> Document | None:
        """Get a document by ID.

        Args:
            doc_id: Document identifier.

        Returns:
            Document if found, None otherwise.
        """
        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        return self._index.documents.get(doc_id)

    def get_summary(self, doc_id: str) -> str | None:
        """Get just the summary for quick LLM triage.

        Args:
            doc_id: Document identifier.

        Returns:
            Summary string if available.
        """
        doc = self.get_document(doc_id)
        if doc:
            return doc.summary
        return None

    def list_by_domain(self, domain: str) -> list[Document]:
        """List all documents in a domain.

        Args:
            domain: Domain name.

        Returns:
            List of documents in that domain.
        """
        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        doc_ids = self._index.by_domain.get(domain, [])
        return [self._index.documents[doc_id] for doc_id in doc_ids]

    def list_by_type(self, doc_type: str) -> list[Document]:
        """List all documents of a type.

        Args:
            doc_type: Document type.

        Returns:
            List of documents of that type.
        """
        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        doc_ids = self._index.by_type.get(doc_type, [])
        return [self._index.documents[doc_id] for doc_id in doc_ids]

    def get_related(self, doc_id: str, depth: int = 1) -> list[Document]:
        """Get related documents up to specified depth.

        Args:
            doc_id: Starting document.
            depth: How many hops to follow.

        Returns:
            List of related documents.
        """
        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        doc = self._index.documents.get(doc_id)
        if not doc:
            return []

        visited: set[str] = {doc_id}
        current_level: list[str] = list(doc.related)
        result: list[Document] = []

        for _ in range(depth):
            next_level: list[str] = []
            for rel_id in current_level:
                if rel_id in visited:
                    continue
                visited.add(rel_id)

                rel_doc = self._index.documents.get(rel_id)
                if rel_doc:
                    result.append(rel_doc)
                    next_level.extend(rel_doc.related)

            current_level = next_level

        return result

    # =========================================================================
    # INDEXING
    # =========================================================================

    def rebuild_index(self) -> DocumentIndex:
        """Rebuild the document index from disk.

        Returns:
            Fresh DocumentIndex.
        """
        self._logger.info("document_index_rebuild_started")
        start = time.time()

        # Ensure root is set
        if self._root is None:
            self._root = Path.cwd()

        documents: dict[str, Document] = {}
        by_type: dict[str, list[str]] = defaultdict(list)
        by_domain: dict[str, list[str]] = defaultdict(list)
        by_status: dict[str, list[str]] = defaultdict(list)
        by_tag: dict[str, list[str]] = defaultdict(list)
        question_index: dict[str, list[str]] = defaultdict(list)

        # Scan all directories
        for scan_dir in SCAN_DIRECTORIES:
            dir_path = self._root / scan_dir
            if not dir_path.exists():
                continue

            for md_path in dir_path.rglob("*.md"):
                if any(skip in md_path.parts for skip in SKIP_DIRECTORIES):
                    continue

                try:
                    doc = self._parse_document(md_path)
                    documents[doc.id] = doc

                    # Build indices
                    by_type[doc.doc_type].append(doc.id)
                    by_domain[doc.domain].append(doc.id)
                    by_status[doc.status].append(doc.id)

                    for tag in doc.tags:
                        by_tag[tag].append(doc.id)

                    # Index questions for fast lookup
                    for question in doc.answers:
                        normalized = self._normalize_question(question)
                        question_index[normalized].append(doc.id)

                except Exception as e:
                    self._logger.error(
                        "document_parse_failed",
                        extra={"path": str(md_path), "error": str(e)},
                    )

        self._index = DocumentIndex(
            documents=documents,
            by_type=dict(by_type),
            by_domain=dict(by_domain),
            by_status=dict(by_status),
            by_tag=dict(by_tag),
            question_index=dict(question_index),
            generated_at=datetime.now(),
            document_count=len(documents),
            embedded_count=sum(1 for d in documents.values() if d.embedding is not None),
        )

        elapsed = (time.time() - start) * 1000
        self._logger.info(
            "document_index_rebuild_completed",
            extra={
                "document_count": len(documents),
                "duration_ms": elapsed,
            },
        )

        return self._index

    def _parse_document(self, path: Path) -> Document:
        """Parse a markdown document into Document model."""
        content = path.read_text(encoding="utf-8")

        frontmatter: dict[str, Any] = {}
        body = content

        # Extract frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                with contextlib.suppress(yaml.YAMLError):
                    frontmatter = yaml.safe_load(parts[1]) or {}
                body = parts[2].strip()

        # Compute content hash
        content_hash = hashlib.sha256(body.encode()).hexdigest()[:16]

        # Build Document
        doc_id = frontmatter.get("id", path.stem)
        assert self._root is not None  # Set by rebuild_index()

        return Document(
            id=doc_id,
            path=path.relative_to(self._root),
            title=frontmatter.get("title", path.stem.replace("_", " ").title()),
            doc_type=cast("DocumentType", self._parse_enum(frontmatter.get("type"), DocumentType)),
            status=cast(
                "DocumentStatus", self._parse_enum(frontmatter.get("status"), DocumentStatus)
            ),
            domain=cast(
                "DocumentDomain", self._parse_enum(frontmatter.get("domain"), DocumentDomain)
            ),
            summary=frontmatter.get("summary"),
            answers=frontmatter.get("answers", []),
            related=frontmatter.get("related", []),
            supersedes=frontmatter.get("supersedes", []),
            superseded_by=frontmatter.get("superseded_by"),
            blocks=frontmatter.get("blocks", []),
            implements=frontmatter.get("implements", []),
            tags=frontmatter.get("tags", []),
            aliases=frontmatter.get("aliases", []),
            confidence=frontmatter.get("confidence", 0.5),
            created=self._parse_date(frontmatter.get("created")),
            updated=self._parse_date(frontmatter.get("updated")),
            content=body,
            content_hash=content_hash,
            embedding_hash=frontmatter.get("embedding_hash"),
        )

    def _parse_enum(
        self,
        value: str | None,
        enum_type: type[DocumentType] | type[DocumentStatus] | type[DocumentDomain],
    ) -> DocumentType | DocumentStatus | DocumentDomain:
        """Parse string to enum, returning UNKNOWN if invalid."""

        # Helper to get unknown value for each enum type
        def get_unknown() -> DocumentType | DocumentStatus | DocumentDomain:
            if enum_type is DocumentType:
                return DocumentType.UNKNOWN
            if enum_type is DocumentStatus:
                return DocumentStatus.UNKNOWN
            return DocumentDomain.UNKNOWN

        if not value:
            return get_unknown()
        try:
            return enum_type(value)
        except ValueError:
            return get_unknown()

    def _parse_date(self, value: Any) -> date | None:
        """Parse date from various formats."""
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
        return None

    # =========================================================================
    # SEARCH INTERNALS
    # =========================================================================

    def _match_questions(self, user_question: str) -> list[SearchResult]:
        """Match user question against indexed answers."""
        assert self._index is not None  # Called only after index built
        results: list[SearchResult] = []
        normalized = self._normalize_question(user_question)

        # Direct match
        for indexed_q, doc_ids in self._index.question_index.items():
            similarity = self._question_similarity(normalized, indexed_q)
            if similarity > 0.6:
                for doc_id in doc_ids:
                    doc = self._index.documents[doc_id]
                    results.append(
                        SearchResult(
                            document=doc,
                            relevance_score=similarity,
                            match_reason=f"Answers: '{indexed_q}'",
                            matched_questions=[indexed_q],
                        )
                    )

        return results

    def _normalize_question(self, question: str) -> str:
        """Normalize question for matching."""
        # Lowercase, remove punctuation, collapse whitespace
        normalized = question.lower()
        normalized = re.sub(r"[^\w\s]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized

    def _question_similarity(self, q1: str, q2: str) -> float:
        """Simple word overlap similarity."""
        words1 = set(q1.split())
        words2 = set(q2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _filter_candidates(self, query: DocumentQuery) -> set[str]:
        """Filter documents by structured criteria."""
        assert self._index is not None  # Called only after index built
        candidates = set(self._index.documents.keys())

        # Filter by type
        if query.doc_type:
            type_docs = set(self._index.by_type.get(query.doc_type.value, []))
            candidates &= type_docs

        # Filter by domain
        if query.domain:
            domain_docs = set(self._index.by_domain.get(query.domain.value, []))
            candidates &= domain_docs

        # Filter by status
        if query.status:
            status_docs = set(self._index.by_status.get(query.status.value, []))
            candidates &= status_docs

        # Filter by tags (OR)
        if query.tags:
            tag_docs: set[str] = set()
            for tag in query.tags:
                tag_docs |= set(self._index.by_tag.get(tag, []))
            candidates &= tag_docs

        # Exclude deprecated unless requested
        if not query.include_deprecated:
            deprecated = set(self._index.by_status.get("deprecated", []))
            archived = set(self._index.by_status.get("archived", []))
            candidates -= deprecated
            candidates -= archived

        return candidates

    def _score_document(self, doc: Document, query: DocumentQuery) -> tuple[float, str]:
        """Score document relevance to query."""
        if not query.question:
            # No question, just filtering - return moderate score
            return 0.7, "Matched filters"

        score = 0.0
        reasons: list[str] = []

        question_lower = query.question.lower()

        # Title match
        if any(word in doc.title.lower() for word in question_lower.split()):
            score += 0.3
            reasons.append("title")

        # Summary match
        if doc.summary and any(word in doc.summary.lower() for word in question_lower.split()):
            score += 0.3
            reasons.append("summary")

        # Tag match
        for tag in doc.tags:
            if tag.lower() in question_lower:
                score += 0.2
                reasons.append(f"tag:{tag}")
                break

        # Domain match
        if doc.domain != DocumentDomain.UNKNOWN:
            domain_words = doc.domain.value.replace("-", " ").split()
            if any(word in question_lower for word in domain_words):
                score += 0.2
                reasons.append("domain")

        return min(score, 1.0), "Matched: " + ", ".join(reasons) if reasons else "Low confidence"

    # =========================================================================
    # HEALTH & STATS
    # =========================================================================

    def health_check(self) -> dict[str, Any]:
        """Return service health status."""
        return {
            "status": "healthy" if self._index else "degraded",
            "document_count": len(self._index.documents) if self._index else 0,
            "embedded_count": self._index.embedded_count if self._index else 0,
            "index_age_seconds": (
                (datetime.now() - self._index.generated_at).total_seconds() if self._index else None
            ),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get detailed index statistics."""
        if not self._index:
            return {}

        return {
            "total_documents": self._index.document_count,
            "embedded_documents": self._index.embedded_count,
            "by_type": {k: len(v) for k, v in self._index.by_type.items()},
            "by_domain": {k: len(v) for k, v in self._index.by_domain.items()},
            "by_status": {k: len(v) for k, v in self._index.by_status.items()},
            "indexed_questions": len(self._index.question_index),
            "atom_count": len(self._atoms),
            "unique_entities": len(self._entity_index),
            "unique_themes": len(self._theme_index),
            "generated_at": self._index.generated_at.isoformat(),
        }

    # =========================================================================
    # KNOWLEDGE ATOM INTEGRATION
    # =========================================================================

    def _get_knowledge_service(self) -> Any:
        """Lazy-load KnowledgeService to avoid circular imports."""
        if self._knowledge_service is None:
            try:
                self._knowledge_service = get_service("knowledge")
            except Exception as e:
                self._logger.warning(
                    "knowledge_service_unavailable",
                    extra={"error": str(e)},
                )
        return self._knowledge_service

    def extract_atoms(
        self,
        doc_ids: list[str] | None = None,
        force: bool = False,
        max_cost: float = 0.50,
    ) -> list[AtomExtractionResult]:
        """Extract knowledge atoms from documents via KnowledgeService.

        Args:
            doc_ids: Specific documents to extract. None = all documents.
            force: Re-extract even if atom exists and content unchanged.
            max_cost: Maximum cost to spend on extractions.

        Returns:
            List of extraction results (success/failure for each doc).
        """
        knowledge = self._get_knowledge_service()
        if knowledge is None:
            self._logger.error("cannot_extract_atoms_no_knowledge_service")
            return []

        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        # Select documents to process
        target_ids = doc_ids or list(self._index.documents.keys())
        results: list[AtomExtractionResult] = []
        total_cost = 0.0

        self._logger.info(
            "atom_extraction_started",
            extra={
                "target_count": len(target_ids),
                "max_cost": max_cost,
                "force": force,
            },
        )

        for doc_id in target_ids:
            # Cost governance
            if total_cost >= max_cost:
                self._logger.warning(
                    "atom_extraction_cost_limit",
                    extra={"total_cost": total_cost, "max_cost": max_cost},
                )
                break

            doc = self._index.documents.get(doc_id)
            if not doc:
                results.append(
                    AtomExtractionResult(
                        doc_id=doc_id,
                        success=False,
                        error="Document not found",
                    )
                )
                continue

            # Skip if unchanged and not forced
            existing = self._atoms.get(doc_id)
            if existing and not force:
                if existing.content_hash == doc.content_hash:
                    results.append(
                        AtomExtractionResult(
                            doc_id=doc_id,
                            success=True,
                            atom=existing,
                            cost=0.0,
                        )
                    )
                    continue

            # Extract via KnowledgeService
            try:
                extraction_result = self._extract_single_atom(doc, knowledge)
                results.append(extraction_result)
                total_cost += extraction_result.cost

                if extraction_result.success and extraction_result.atom:
                    self._store_atom(extraction_result.atom)

            except Exception as e:
                self._logger.error(
                    "atom_extraction_failed",
                    extra={"doc_id": doc_id, "error": str(e)},
                )
                results.append(
                    AtomExtractionResult(
                        doc_id=doc_id,
                        success=False,
                        error=str(e),
                    )
                )

        self._logger.info(
            "atom_extraction_completed",
            extra={
                "processed": len(results),
                "successful": sum(1 for r in results if r.success),
                "total_cost": total_cost,
            },
        )

        return results

    def _extract_single_atom(
        self,
        doc: Document,
        knowledge: Any,
    ) -> AtomExtractionResult:
        """Extract atom from a single document."""

        # Build content for extraction
        # Include summary and questions for richer context
        content_parts = []
        if doc.summary:
            content_parts.append(f"Summary: {doc.summary}")
        content_parts.append(doc.content[:8000])  # Limit content size

        content = "\n\n".join(content_parts)

        # Call KnowledgeService
        record = {"content": content, "source": f"document:{doc.id}"}
        processed = knowledge.process(record)

        if processed.get("knowledge_status") != "processed":
            return AtomExtractionResult(
                doc_id=doc.id,
                success=False,
                error=processed.get("knowledge_error", "Processing failed"),
                cost=processed.get("llm_cost", 0.0),
            )

        extraction = processed.get("extraction", {})

        atom = DocumentAtom(
            doc_id=doc.id,
            doc_path=str(doc.path),
            content_hash=doc.content_hash or "",
            summary=extraction.get("summary", ""),
            entities=extraction.get("entities", []),
            themes=extraction.get("themes", []),
            llm_model=processed.get("llm_model"),
            extraction_cost=processed.get("llm_cost", 0.0),
            extracted_at=datetime.now(),
        )
        atom.combined_text = atom.build_combined_text()

        return AtomExtractionResult(
            doc_id=doc.id,
            success=True,
            atom=atom,
            cost=processed.get("llm_cost", 0.0),
        )

    def _store_atom(self, atom: DocumentAtom) -> None:
        """Store atom and update indices."""
        # Remove old indices if replacing
        old_atom = self._atoms.get(atom.doc_id)
        if old_atom:
            for entity in old_atom.entities:
                normalized = entity.lower()
                if atom.doc_id in self._entity_index.get(normalized, []):
                    self._entity_index[normalized].remove(atom.doc_id)
            for theme in old_atom.themes:
                normalized = theme.lower()
                if atom.doc_id in self._theme_index.get(normalized, []):
                    self._theme_index[normalized].remove(atom.doc_id)

        # Store new atom
        self._atoms[atom.doc_id] = atom

        # Update indices
        for entity in atom.entities:
            self._entity_index[entity.lower()].append(atom.doc_id)
        for theme in atom.themes:
            self._theme_index[theme.lower()].append(atom.doc_id)

    def semantic_query(self, query: AtomQuery | str) -> list[AtomSearchResult]:
        """Query documents using semantic search across atoms.

        Args:
            query: Natural language query or AtomQuery object.

        Returns:
            List of matching documents with relevance scores.
        """
        if isinstance(query, str):
            query = AtomQuery(query=query)

        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        results: list[AtomSearchResult] = []
        query_lower = query.query.lower()
        query_words = set(query_lower.split())

        # Find candidate documents via entity/theme indices
        candidates: set[str] = set()

        # Direct entity matches
        for entity in query.entities:
            candidates.update(self._entity_index.get(entity.lower(), []))

        # Direct theme matches
        for theme in query.themes:
            candidates.update(self._theme_index.get(theme.lower(), []))

        # Query word matches against indices
        for word in query_words:
            # Check entities
            for entity_key, doc_ids in self._entity_index.items():
                if word in entity_key or entity_key in word:
                    candidates.update(doc_ids)
            # Check themes
            for theme_key, doc_ids in self._theme_index.items():
                if word in theme_key or theme_key in word:
                    candidates.update(doc_ids)

        # If no index matches, search all atoms
        if not candidates:
            candidates = set(self._atoms.keys())

        # Score and filter candidates
        for doc_id in candidates:
            atom = self._atoms.get(doc_id)
            if not atom:
                continue

            doc = self._index.documents.get(doc_id)
            if not doc:
                continue

            # Apply filters
            if query.domains and doc.domain not in [d.value for d in query.domains]:
                continue
            if query.doc_types and doc.doc_type not in [t.value for t in query.doc_types]:
                continue

            # Score relevance
            score, match_reason, matched_entities, matched_themes = self._score_atom(
                atom, query_lower, query_words
            )

            if score >= 0.3:
                results.append(
                    AtomSearchResult(
                        document=doc,
                        atom=atom,
                        relevance_score=score,
                        match_reason=match_reason,
                        matched_entities=matched_entities,
                        matched_themes=matched_themes,
                    )
                )

        # Sort by relevance
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        return results[: query.max_results]

    def _score_atom(
        self,
        atom: DocumentAtom,
        query_lower: str,
        query_words: set[str],
    ) -> tuple[float, str, list[str], list[str]]:
        """Score an atom against a query."""
        score = 0.0
        reasons: list[str] = []
        matched_entities: list[str] = []
        matched_themes: list[str] = []

        # Entity matches (high value)
        for entity in atom.entities:
            entity_lower = entity.lower()
            if entity_lower in query_lower or any(w in entity_lower for w in query_words):
                score += 0.25
                matched_entities.append(entity)
                reasons.append(f"entity:{entity}")

        # Theme matches (high value)
        for theme in atom.themes:
            theme_lower = theme.lower()
            if theme_lower in query_lower or any(w in theme_lower for w in query_words):
                score += 0.2
                matched_themes.append(theme)
                reasons.append(f"theme:{theme}")

        # Summary match (medium value)
        if atom.summary:
            summary_lower = atom.summary.lower()
            overlap = len(query_words & set(summary_lower.split()))
            if overlap > 0:
                score += 0.1 * min(overlap, 5)
                reasons.append("summary")

        # Cap score at 1.0
        score = min(score, 1.0)

        match_reason = ", ".join(reasons[:5]) if reasons else "weak_match"

        return score, match_reason, matched_entities, matched_themes

    def get_atom(self, doc_id: str) -> DocumentAtom | None:
        """Get the knowledge atom for a document.

        Args:
            doc_id: Document ID.

        Returns:
            DocumentAtom if extracted, None otherwise.
        """
        return self._atoms.get(doc_id)

    def get_entities(self) -> dict[str, int]:
        """Get all extracted entities with document counts.

        Returns:
            Dict of entity -> document count.
        """
        return {entity: len(doc_ids) for entity, doc_ids in self._entity_index.items()}

    def get_themes(self) -> dict[str, int]:
        """Get all extracted themes with document counts.

        Returns:
            Dict of theme -> document count.
        """
        return {theme: len(doc_ids) for theme, doc_ids in self._theme_index.items()}

    def find_by_entity(self, entity: str) -> list[Document]:
        """Find documents mentioning an entity.

        Args:
            entity: Entity name to search.

        Returns:
            List of documents containing the entity.
        """
        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        doc_ids = self._entity_index.get(entity.lower(), [])
        return [
            self._index.documents[doc_id] for doc_id in doc_ids if doc_id in self._index.documents
        ]

    def find_by_theme(self, theme: str) -> list[Document]:
        """Find documents related to a theme.

        Args:
            theme: Theme to search.

        Returns:
            List of documents with the theme.
        """
        if self._index is None:
            self.rebuild_index()
        assert self._index is not None

        doc_ids = self._theme_index.get(theme.lower(), [])
        return [
            self._index.documents[doc_id] for doc_id in doc_ids if doc_id in self._index.documents
        ]
