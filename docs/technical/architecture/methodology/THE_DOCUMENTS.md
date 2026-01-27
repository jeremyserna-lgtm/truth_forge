# THE DOCUMENTS

**How documents become knowledge and leave.**

**Author:** Jeremy Serna & Claude
**Date:** January 2, 2026
**Location:** Denver, Colorado
**Version:** 2.0

---

## The Simple Truth

```
Documents → Knowledge Atoms → Archive to GCS
           (what matters)    (clear the drive)
```

**Documents are transient. Knowledge atoms are permanent.**

We don't need the documents. We need what's IN them. Extract the truth, archive the source, keep the drive clean.

---

## What We Keep Locally

| Keep | Why |
|------|-----|
| **Framework docs** | THE_* series - the soul, must be accessible |
| **Knowledge atoms** | The extracted truth (in DuckDB + BigQuery) |

**Everything else goes to GCS after processing.**

---

## The Flow

```
Document exists (anywhere)
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  BREATHE (ExtractionService)                          │
│  - THE_PROMPT: "Pull the truth from this as sentences"│
│  - Creates knowledge atoms                            │
│  - Atoms stored in DuckDB (local) + BigQuery (cloud)  │
└───────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────┐
│  ARCHIVE (Upload to GCS)                              │
│  - Upload document to library bucket                  │
│  - Record: source_path, document_hash, atoms_produced │
│  - Delete local copy                                  │
└───────────────────────────────────────────────────────┘
        │
        ▼
    Drive is clean. Knowledge is preserved.
```

---

## Why This Works

| Question | Answer |
|----------|--------|
| "Where's the document?" | Archived in GCS, but who cares - atoms have the knowledge |
| "Can I search it?" | Search atoms, not documents. Atoms are queryable. |
| "What if I need it back?" | It's in GCS. Download if needed. |
| "What about duplicates?" | Atoms are deduplicated. Documents don't matter. |
| "What about organization?" | Atoms are organized by content, not files. |

**Knowledge atoms can be re-extracted into each other.** The system is self-healing.

---

## Framework Position

```
THE_PHILOSOPHY (soul)
    │
    │  drives
    ▼
THE_PRIMITIVES (logical)
    │
    │  describes
    ▼
THE_BREATHING (process)
    │
    │  includes
    ▼
THE_DOCUMENTS (this document) ← Documents are a source for BREATHING
    │
    │  runs on
    ▼
THE_FOUNDATION (physical)
```

---

## The GCS Library Bucket

All processed documents go to:

```
gs://truth-engine-library/
├── documents/
│   └── YYYY-MM/
│       └── {hash}_{original_filename}.md
│
└── manifest.jsonl  # Record of what's archived
```

**Manifest entry:**
```json
{
  "document_hash": "sha256:...",
  "original_path": "/path/to/doc.md",
  "archived_path": "gs://truth-engine-library/documents/2026-01/...",
  "archived_at": "2026-01-02T15:30:00Z",
  "atoms_produced": 23,
  "extractor_run_id": "run:md:abc123"
}
```

---

## What Stays Local

### Framework Documents (docs/the_framework/)

These are the soul. They stay local for Claude Code access:

```
docs/the_framework/
├── THE_FRAMEWORK.md
├── THE_PHILOSOPHY.md
├── THE_PRIMITIVES.md
├── THE_BREATHING.md
├── THE_DOCUMENTS.md      ← This file
└── THE_FOUNDATION.md
```

### Why Framework Stays

1. **Claude Code needs them** - Referenced constantly
2. **They ARE the system** - The soul can't be archived
3. **They're small** - Not cluttering the drive
4. **They evolve** - Active documents, not archived history

---

## The Clean Sweep

### Phase 1: Extract All Documents

```bash
# Find all markdown files
find . -name "*.md" -type f

# For each document:
# 1. Extract to knowledge atoms
# 2. Record what was extracted
```

### Phase 2: Archive to GCS

```bash
# For each processed document:
# 1. Upload to gs://truth-engine-library/
# 2. Add to manifest.jsonl
# 3. Delete local copy (except framework)
```

### Phase 3: Verify and Clean

```bash
# Verify atoms exist
# Verify archive is complete
# Remove empty directories
# Drive is clean
```

---

## Traceability

Even after archiving, we can trace:

```
Knowledge Atom
    → extractor_run.run_id
    → manifest.jsonl entry
    → original document in GCS
```

The atom knows its origin. The manifest knows where the source lives.

---

## Code Locations

| Component | Location | Status |
|-----------|----------|--------|
| ExtractionService | `knowledge_service/extraction_service.py` | ✅ Exists |
| Archive script | `scripts/archive_documents_to_gcs.py` | 📋 Backlog |
| Clean sweep script | `scripts/clean_sweep_documents.py` | 📋 Backlog |

---

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| No frontmatter needed | Skip it | Atoms have the knowledge, documents are archived |
| Archive to GCS | Yes | Clear the drive, keep the source somewhere |
| Framework stays local | Yes | The soul must be accessible |
| Atoms are the truth | Yes | Documents are just the source |
| Re-extraction is fine | Yes | Atoms can be re-extracted, system is self-healing |

---

*"Documents are transient. Knowledge is permanent. Extract the truth, archive the source, keep the drive clean."*

— Jeremy Serna, January 2, 2026

---

**END OF DOCUMENT**
