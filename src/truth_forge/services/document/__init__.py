"""Document Service - LLM-first document retrieval and management.

Provides semantic search, question matching, knowledge atom extraction,
and document retrieval optimized for LLM consumption.

MOLT LINEAGE:
- Source: New creation for LLM-aligned document management
- Version: 1.1.0
- Date: 2026-02-01

INTEGRATION:
- KnowledgeService: Extract entities/themes for semantic search
- Atom-based search: Query across extracted knowledge
"""

from truth_forge.services.document.models import (
    AtomExtractionResult,
    AtomQuery,
    AtomSearchResult,
    # Core models
    Document,
    # Atom integration
    DocumentAtom,
    DocumentDomain,
    DocumentIndex,
    DocumentQuery,
    DocumentResult,
    DocumentStatus,
    DocumentType,
    SearchResult,
)
from truth_forge.services.document.service import DocumentService


__all__ = [
    # Service
    "DocumentService",
    # Core models
    "Document",
    "DocumentQuery",
    "DocumentResult",
    "SearchResult",
    "DocumentIndex",
    # Enums
    "DocumentType",
    "DocumentStatus",
    "DocumentDomain",
    # Atom integration
    "DocumentAtom",
    "AtomQuery",
    "AtomSearchResult",
    "AtomExtractionResult",
]
