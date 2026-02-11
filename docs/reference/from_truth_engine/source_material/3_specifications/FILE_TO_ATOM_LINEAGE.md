# Contract: FILE_TO_ATOM_LINEAGE

**Type**: exist-now (traceability chain)
**Status**: Gap identified, contract defined
**Created**: 2025-12-30

---

## The Pattern

Every knowledge atom traces back to a source file through content:

```
File (GCS cold storage)
    │
    ├── file_id (identity)
    ├── file_hash (SHA256 of content)
    ├── file_path (original location)
    └── archived_at (when moved to cold)
    │
    ↓ extraction
    │
Content (document_runs)
    │
    ├── run_id (identity)
    ├── source_file_id (→ file_registry)
    ├── source_file_hash (verify integrity)
    └── extracted_at
    │
    ↓ atomization
    │
Knowledge Atoms (knowledge_atoms)
    │
    ├── atom_id (identity)
    ├── run_id (→ document_runs)
    ├── content_hash (SHA256 of atom content)
    └── created_at
```

---

## Required Tables

### 1. knowledge.file_registry

```sql
CREATE TABLE knowledge.file_registry (
    file_id STRING NOT NULL,           -- fil_xxxxxxxx
    file_path STRING NOT NULL,         -- Original path before archival
    file_name STRING NOT NULL,         -- Filename only
    file_hash STRING NOT NULL,         -- SHA256 of file content
    file_size_bytes INT64,             -- Size at registration
    source_system STRING,              -- Where it came from
    archived_path STRING,              -- GCS path after archival (nullable until archived)
    archived_at TIMESTAMP,             -- When moved to cold storage
    registered_at TIMESTAMP NOT NULL,  -- When first seen
    metadata JSON                      -- Flexible metadata
)
PARTITION BY DATE(registered_at)
CLUSTER BY file_hash, source_system;
```

### 2. knowledge.atom_lineage (Bridge Table)

```sql
CREATE TABLE knowledge.atom_lineage (
    lineage_id STRING NOT NULL,        -- lin_xxxxxxxx
    file_id STRING NOT NULL,           -- → file_registry
    file_hash STRING NOT NULL,         -- Denormalized for query
    run_id STRING NOT NULL,            -- → document_runs
    atom_id STRING NOT NULL,           -- → knowledge_atoms
    atom_content_hash STRING,          -- Denormalized for dedup
    created_at TIMESTAMP NOT NULL
)
PARTITION BY DATE(created_at)
CLUSTER BY file_id, atom_id;
```

### 3. Schema Extensions

**document_runs** - Add fields:
```sql
ALTER TABLE knowledge.document_runs
ADD COLUMN source_file_id STRING,      -- → file_registry.file_id
ADD COLUMN source_file_hash STRING,    -- SHA256 at extraction time
ADD COLUMN source_file_path STRING;    -- Original path
```

**knowledge_atoms** - Populate existing field:
```sql
-- content_hash field exists but is never populated
-- Extraction pipeline MUST compute and store SHA256
UPDATE knowledge.knowledge_atoms
SET content_hash = SHA256(content)
WHERE content_hash IS NULL;
```

---

## The Flow

### On File Discovery (Collector)

```python
from architect_central_services import generate_file_id
import hashlib

def register_file(file_path: Path) -> str:
    content = file_path.read_bytes()
    file_hash = hashlib.sha256(content).hexdigest()

    file_id = generate_file_id()

    # Insert into file_registry
    insert_file_registry(
        file_id=file_id,
        file_path=str(file_path),
        file_name=file_path.name,
        file_hash=file_hash,
        file_size_bytes=len(content),
        source_system="collector_name",
        registered_at=datetime.utcnow()
    )

    return file_id
```

### On Content Extraction (Pipeline)

```python
def extract_content(file_id: str, run_id: str) -> None:
    file_record = get_file_registry(file_id)

    # Update document_runs with file reference
    update_document_run(
        run_id=run_id,
        source_file_id=file_id,
        source_file_hash=file_record.file_hash,
        source_file_path=file_record.file_path
    )
```

### On Atom Creation (Knowledge Atom Service)

```python
def create_atom(content: str, run_id: str) -> str:
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    atom_id = generate_knowledge_atom_id()

    # Create atom with content_hash populated
    insert_knowledge_atom(
        atom_id=atom_id,
        content=content,
        content_hash=content_hash,  # MUST populate
        run_id=run_id
    )

    # Create lineage record
    run_record = get_document_run(run_id)
    insert_atom_lineage(
        lineage_id=generate_lineage_id(),
        file_id=run_record.source_file_id,
        file_hash=run_record.source_file_hash,
        run_id=run_id,
        atom_id=atom_id,
        atom_content_hash=content_hash
    )

    return atom_id
```

### On Deprecation (Archive)

```python
def deprecate_file(file_id: str, reason: str) -> None:
    file_record = get_file_registry(file_id)

    # Move to GCS cold storage
    gcs_path = archive_to_gcs(
        local_path=file_record.file_path,
        bucket="truth-engine-archive"
    )

    # Update registry (file moves, knowledge stays)
    update_file_registry(
        file_id=file_id,
        archived_path=gcs_path,
        archived_at=datetime.utcnow()
    )

    # Content and atoms remain in DB - fully queryable
    # Only the raw file moves to cold storage
```

---

## Queries Enabled

### "All atoms from this file"

```sql
SELECT a.*
FROM knowledge.atom_lineage l
JOIN knowledge.knowledge_atoms a ON l.atom_id = a.atom_id
WHERE l.file_id = @file_id;
```

### "What file produced this atom?"

```sql
SELECT f.*
FROM knowledge.atom_lineage l
JOIN knowledge.file_registry f ON l.file_id = f.file_id
WHERE l.atom_id = @atom_id;
```

### "Duplicate content across files"

```sql
SELECT file_hash, COUNT(DISTINCT file_id) as file_count
FROM knowledge.file_registry
GROUP BY file_hash
HAVING file_count > 1;
```

### "Atoms with duplicate content"

```sql
SELECT atom_content_hash, COUNT(*) as atom_count
FROM knowledge.atom_lineage
GROUP BY atom_content_hash
HAVING atom_count > 1;
```

---

## Definition of Done

### Phase 1: Created
- [ ] `knowledge.file_registry` table created
- [ ] `knowledge.atom_lineage` table created
- [ ] `document_runs` schema extended
- [ ] ID generators: `generate_file_id()`, `generate_lineage_id()`

### Phase 2: Adopted
- [ ] Collectors register files on discovery
- [ ] Pipelines link document_runs to files
- [ ] Knowledge Atom Service populates content_hash
- [ ] Lineage records created on atom creation

### Phase 3: Enforced
- [ ] Pre-commit hook: atoms must have content_hash
- [ ] Pipeline validation: document_runs must have source_file_id
- [ ] Deprecation flow archives to GCS, updates registry

### Phase 4: Validated
- [ ] Can query "atoms from file" < 1s
- [ ] Can query "file for atom" < 1s
- [ ] Duplicate detection works

---

## Current Gaps (2025-12-30)

| Component | Status | Gap |
|-----------|--------|-----|
| `file_registry` | MISSING | Table not created |
| `atom_lineage` | MISSING | Table not created |
| `document_runs.source_file_*` | MISSING | Fields not added |
| `knowledge_atoms.content_hash` | EXISTS BUT EMPTY | Never populated |
| Deprecation → GCS | PARTIAL | Policy exists, archival not automated |

---

## Related

- [DEPRECATION_POLICY.md](../../policies/DEPRECATION_POLICY.md) - When files archive
- [KNOWLEDGE_ATOM_SYSTEM_SPEC.md](../../specifications/KNOWLEDGE_ATOM_SYSTEM_SPEC.md) - Atom structure
- [THE_BRIDGE.md](../../../architect_central_services/src/architect_central_services/truth/THE_BRIDGE.md) - Truth to atoms
- [HYBRID_DURABILITY rule](../../../.claude/rules/14-hybrid-durability.md) - Local + cloud pattern

---

**The file moves. The knowledge stays. The link holds.**
