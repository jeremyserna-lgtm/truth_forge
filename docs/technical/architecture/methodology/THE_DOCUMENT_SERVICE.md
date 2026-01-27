# THE DOCUMENT SERVICE

**A Primitive for Documents**

**Author:** Jeremy Serna
**Date:** January 3, 2026
**Location:** Denver, Colorado
**Version:** 1.0

---

## The Problem

THE_PRIMITIVE takes raw content and produces atoms. But when you're working with documents (files, URLs, APIs), you need:
- Source tracking (which file, which URL)
- Metadata (filename, size, type)
- Document-level deduplication
- Traceability from atom back to source

THE_PRIMITIVE doesn't do this. It's content in, atoms out. Clean and simple.

---

## The Solution

A document service that IS a primitive for documents:

```
Documents → DOCUMENT SERVICE → Atoms (with document_id)
```

The document service:
1. **Collects** documents from various sources
2. **Stores** document records (metadata, source)
3. **Extracts** atoms directly (same as THE_PRIMITIVE)
4. **Links** atoms to their source document

It doesn't feed to THE_PRIMITIVE. It IS a primitive.

---

## The Pattern

Same as THE_PRIMITIVE: JSONL → AGENT → JSONL

```
HOLD₁: documents.jsonl (document records with content + metadata)
AGENT: Document Service (extract atoms)
HOLD₂: atoms.jsonl (with document_id for traceability)
```

The canonical flow:
```
Raw sources → collect() → documents.jsonl → devour() → atoms.jsonl
                              ↑                            ↓
                           HOLD₁                        HOLD₂
```

---

## The Schema

Each document in the JSONL:

```json
{
  "document_id": "doc:abc123",
  "source_path": "/path/to/file.py",
  "source_type": "file",
  "content": "... the full content ...",
  "content_hash": "sha256...",
  "collected_at": "2026-01-03T10:00:00Z",
  "metadata": {
    "filename": "file.py",
    "extension": ".py",
    "size_bytes": 1234,
    "language": "python"
  },
  "run_id": "run:xyz789"
}
```

---

## The Functions

### glob_documents()

Find documents by pattern:

```python
def glob_documents(pattern: str, base_path: str = ".") -> list[str]:
    """
    Find documents matching a glob pattern.

    Args:
        pattern: Glob pattern (e.g., "**/*.md", "docs/**/*.py")
        base_path: Where to start searching

    Returns:
        List of file paths

    Examples:
        glob_documents("**/*.md")           # All markdown files
        glob_documents("docs/**/*.md")      # Markdown in docs/
        glob_documents("*.py", "scripts/")  # Python in scripts/
    """
```

### collect_all()

Collect multiple documents at once:

```python
def collect_all(pattern: str, base_path: str = ".") -> dict:
    """
    Find and collect all documents matching pattern.
    Writes each to documents.jsonl (HOLD₁).

    Args:
        pattern: Glob pattern
        base_path: Where to start searching

    Returns:
        Stats dict with count collected
    """
```

### collect()

Grab a single document and store to JSONL:

```python
def collect(source: str, source_type: str = "file") -> dict:
    """
    Collect a document from a source.
    Writes to documents.jsonl (HOLD₁).

    Args:
        source: Path, URL, or identifier
        source_type: "file", "url", "api", etc.

    Returns:
        Document dict with content and metadata
    """
```

### devour()

Read from documents.jsonl, extract atoms, write to atoms.jsonl:

```python
def devour(document_id: str = None) -> dict:
    """
    Devour documents and produce atoms.
    Reads from documents.jsonl (HOLD₁).
    Writes to atoms.jsonl (HOLD₂).

    Args:
        document_id: Specific document, or None for all unprocessed

    Returns:
        Stats dict with atoms extracted
    """
```

### extract_atoms()

The membrane function (same as THE_PRIMITIVE):

```python
def extract_atoms(content: str) -> list[str]:
    """
    Extract knowledge atoms from content.
    "Pull the truth from this as sentences."

    Args:
        content: Document content

    Returns:
        List of truth sentences
    """
```

### exhale()

Write atoms to JSONL (same as THE_PRIMITIVE, but with document_id):

```python
def exhale(atoms: list[str], document_id: str) -> dict:
    """
    Write atoms to atoms.jsonl with document_id for traceability.

    Args:
        atoms: List of truth sentences
        document_id: Source document ID

    Returns:
        Stats dict
    """
```

---

## The Flow

### Collect Phase (Raw → JSONL)

```python
from document_service import collect

# Collect documents into documents.jsonl
collect("/path/to/file.py")
collect("/path/to/another.py")
collect("https://example.com/doc", source_type="url")

# Now documents.jsonl has all the documents with metadata
```

### Devour Phase (JSONL → Atoms)

```python
from document_service import devour

# Devour all unprocessed documents
stats = devour()
# Reads from documents.jsonl
# Extracts atoms from each document
# Writes to atoms.jsonl with document_id

# Or devour a specific document
stats = devour(document_id="doc:abc123")
```

### The Complete Flow

```python
from document_service import collect, devour

# Phase 1: Collect into HOLD₁
for path in file_paths:
    collect(path)

# Phase 2: Devour from HOLD₁ to HOLD₂
stats = devour()
```

---

## The Difference

| Aspect | THE_PRIMITIVE | DOCUMENT SERVICE |
|--------|---------------|------------------|
| **Input** | Raw content string | documents.jsonl |
| **HOLD₁** | (none - direct input) | documents.jsonl |
| **Tracking** | source_name only | document_id + metadata |
| **Output** | atoms.jsonl | atoms.jsonl (with document_id) |
| **Purpose** | Devour content | Devour documents |

Both produce atoms. The document service adds:
- Document-level storage
- Metadata tracking
- Source traceability

---

## File Structure

```
.primitive_engine/
├── atoms/                    # THE_PRIMITIVE writes here
│   └── *.jsonl
├── documents/                # DOCUMENT SERVICE writes here
│   └── documents.jsonl       # All collected documents
├── atoms.duckdb              # Canonical atom store
└── documents.duckdb          # Canonical document store
```

---

## Building It

### Step 1: Create the Service

Create `THE_DOCUMENT_SERVICE.py` in `.primitive_engine/`:

```python
"""
THE DOCUMENT SERVICE
===============================================================================

Collect documents. Extract atoms. JSONL → AGENT → JSONL.

===============================================================================
"""

from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

# Where things go
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / ".primitive_engine" / "documents"
ATOMS_DIR = PROJECT_ROOT / ".primitive_engine" / "atoms"
DOCS_DIR.mkdir(parents=True, exist_ok=True)
ATOMS_DIR.mkdir(parents=True, exist_ok=True)
DOCS_JSONL = DOCS_DIR / "documents.jsonl"
```

### Step 2: Implement glob_documents()

```python
from pathlib import Path

def glob_documents(pattern: str, base_path: str = ".") -> list[str]:
    """Find documents matching a glob pattern."""
    base = Path(base_path)
    return [str(p) for p in base.glob(pattern) if p.is_file()]
```

### Step 3: Implement collect()

```python
def collect(source: str, source_type: str = "file") -> dict:
    """Collect a document and write to documents.jsonl."""

    if source_type == "file":
        path = Path(source)
        content = path.read_text()
        metadata = {
            "filename": path.name,
            "extension": path.suffix,
            "size_bytes": path.stat().st_size,
        }
    else:
        raise ValueError(f"Unknown source_type: {source_type}")

    content_hash = hashlib.sha256(content.encode()).hexdigest()

    document = {
        "document_id": f"doc:{content_hash[:16]}",
        "source_path": str(source),
        "source_type": source_type,
        "content": content,
        "content_hash": content_hash,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata,
        "processed": False,  # Not yet devoured
    }

    # Write to HOLD₁
    with open(DOCS_JSONL, "a") as f:
        f.write(json.dumps(document) + "\n")

    return document
```

### Step 4: Implement collect_all()

```python
def collect_all(pattern: str, base_path: str = ".") -> dict:
    """Find and collect all documents matching pattern."""
    files = glob_documents(pattern, base_path)
    stats = {"collected": 0, "skipped": 0}

    for file_path in files:
        try:
            collect(file_path)
            stats["collected"] += 1
        except Exception as e:
            print(f"Skipped {file_path}: {e}")
            stats["skipped"] += 1

    return stats
```

### Step 3: Implement devour()

```python
def devour(document_id: str = None) -> dict:
    """Read from documents.jsonl, extract atoms, write to atoms.jsonl."""

    from architect_central_services.core.shared.claude_code_client import call_prompt

    stats = {"documents": 0, "atoms": 0}

    # Read all documents from HOLD₁
    with open(DOCS_JSONL, "r") as f:
        documents = [json.loads(line) for line in f if line.strip()]

    for doc in documents:
        # Skip if already processed or doesn't match filter
        if doc.get("processed"):
            continue
        if document_id and doc["document_id"] != document_id:
            continue

        # Extract atoms
        result = call_prompt("extract_knowledge_atoms", content=doc["content"], as_json=True)
        atoms = result.get("atoms", [])

        # Write atoms to HOLD₂ (with document_id)
        for atom_text in atoms:
            atom = {
                "atom_id": f"atom:{doc['document_id']}:{hashlib.sha256(atom_text.encode()).hexdigest()[:16]}",
                "content": atom_text,
                "document_id": doc["document_id"],  # Traceability
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            atoms_path = ATOMS_DIR / f"{doc['document_id'].replace(':', '_')}.jsonl"
            with open(atoms_path, "a") as f:
                f.write(json.dumps(atom) + "\n")
            stats["atoms"] += 1

        stats["documents"] += 1

    return stats
```

---

## The Result

After running:

```python
collect("my_script.py")   # Phase 1: collect
devour()                   # Phase 2: extract
```

You get:

1. **documents.jsonl** - Document record with content + metadata
2. **atoms.jsonl** - Atoms with document_id = "doc:abc123"
3. **atoms.duckdb** - Atoms queryable by document_id

Now you can trace any atom back to its source document.

---

## Why Two Primitives

THE_PRIMITIVE: content → atoms
- Takes raw content
- No source tracking
- Simple, clean

DOCUMENT SERVICE: documents → atoms
- Takes from documents.jsonl
- Full source tracking
- Document-level deduplication

Use THE_PRIMITIVE when you have content.
Use DOCUMENT SERVICE when you have documents.

---

## Alternative: Modify THE_PRIMITIVE

Instead of a separate service, you could modify THE_PRIMITIVE to handle documents directly. Here's what would change:

### Current Primitive

```python
def devour(content: str, source_name: str) -> dict:
    """Takes content string and a name."""
    atoms = extract_atoms(content)
    return exhale(atoms, source_name)
```

- Input: raw content string
- Tracking: source_name only (e.g., "primitive", "my_script")
- No knowledge of where content came from

### Modified Primitive

```python
def devour(source: str | Path, source_type: str = "file") -> dict:
    """Takes a source (path, URL) and collects it."""

    # 1. Collect the document
    document = collect(source, source_type)

    # 2. Store document record (new)
    store_document(document)

    # 3. Extract atoms
    atoms = extract_atoms(document["content"])

    # 4. Exhale with document_id as source (traceability)
    return exhale(atoms, source_name=document["document_id"])
```

### Schema Changes

**Current atom schema:**
```python
{
    "atom_id": "atom:source_name:hash",
    "content": "...",
    "content_hash": "...",
    "source_name": "primitive",  # Just a name
    "created_at": "...",
    "run_id": "..."
}
```

**New atom schema:**
```python
{
    "atom_id": "atom:doc_abc123:hash",
    "content": "...",
    "content_hash": "...",
    "source_name": "doc_abc123",      # Links to document
    "document_id": "doc:abc123",       # NEW: explicit link
    "created_at": "...",
    "run_id": "..."
}
```

**New document schema (additional table):**
```python
{
    "document_id": "doc:abc123",
    "source_path": "/path/to/file.py",
    "source_type": "file",
    "content_hash": "sha256...",
    "collected_at": "2026-01-03T10:00:00Z",
    "metadata": {
        "filename": "file.py",
        "extension": ".py",
        "size_bytes": 1234
    },
    "run_id": "..."
}
```

### New Functions to Add

```python
def collect(source: str, source_type: str = "file") -> dict:
    """Collect a document from a source."""
    # Read content
    # Generate document_id from content hash
    # Gather metadata
    # Return document dict

def store_document(document: dict) -> dict:
    """Store document record to documents.jsonl and documents table."""
    # Append to documents.jsonl
    # Insert into documents table in DuckDB

def sync_documents_to_duckdb() -> dict:
    """Sync documents from JSONL to DuckDB."""
    # Same pattern as sync_to_duckdb() for atoms
```

### DuckDB Changes

Add a `documents` table:

```sql
CREATE TABLE IF NOT EXISTS documents (
    document_id VARCHAR PRIMARY KEY,
    source_path VARCHAR,
    source_type VARCHAR,
    content_hash VARCHAR,
    collected_at VARCHAR,
    metadata JSON,
    run_id VARCHAR
)
```

Add `document_id` column to atoms:

```sql
ALTER TABLE atoms ADD COLUMN document_id VARCHAR
```

### CLI Changes

**Current:**
```bash
python3 THE_PRIMITIVE.py                    # Devours itself
python3 THE_PRIMITIVE.py file.py            # Devours one file
```

**After modification:**
```bash
python3 THE_PRIMITIVE.py                    # Devours itself (unchanged)
python3 THE_PRIMITIVE.py file.py            # Collects + devours file
python3 THE_PRIMITIVE.py --content "text"   # Raw content mode (backwards compat)
```

### Summary of Changes

| Component | Current | After Modification |
|-----------|---------|-------------------|
| **Input** | `content: str` | `source: str \| Path` |
| **First step** | Extract atoms | Collect document |
| **Document storage** | None | documents.jsonl + DuckDB |
| **Atom source** | `source_name` (arbitrary) | `document_id` (traceable) |
| **New functions** | - | `collect()`, `store_document()` |
| **New table** | - | `documents` |
| **New column** | - | `atoms.document_id` |

### The Tradeoff

**Separate service:**
- THE_PRIMITIVE stays clean (content in, atoms out)
- Document service handles all the complexity
- Two scripts to maintain

**Modified primitive:**
- One script does everything
- More complex, but self-contained
- Document handling is built into the extraction flow

---

## Next Steps

1. Create `.primitive_engine/THE_DOCUMENT_SERVICE.py`
2. Implement collect() for file sources
3. Implement devour() to extract atoms
4. Add document-level deduplication
5. Add sync_to_duckdb() for documents
6. Add sync_to_duckdb() for atoms (reuse from THE_PRIMITIVE)

---

*Collect documents. Extract atoms. Traceability preserved.*

— THE_FRAMEWORK

---

**END OF DOCUMENT**
