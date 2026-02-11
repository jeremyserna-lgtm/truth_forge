# Contract: DOCUMENT_METADATA

**Type**: exist-now (document identity)
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

Every document has:
1. **Identity** - Unique ID, tied to file_registry
2. **Category** - What domain it belongs to
3. **Type** - File format
4. **Series** - Which series it's part of
5. **Related** - Documents it connects to

```
Document
    │
    ├── doc_id: doc:{category}:{series}:{number}:{slug}
    ├── category: Core | Pipeline | Service | Identity | Governance | ...
    ├── file_type: MD | SQL | PY | YAML | JSON
    ├── series: primitive | arch | spec | ref | ops | status
    ├── series_number: 01, 02, 03...
    └── related_docs: [doc_id, doc_id, ...]
```

---

## Categories

| Category | Code | Description | Home Directory |
|----------|------|-------------|----------------|
| **Core** | `core` | Foundation primitives | `docs/primitive/` |
| **Architecture** | `arch` | System design | `docs/architecture/` |
| **Pipeline** | `pipe` | Pipeline docs | `pipelines/{source}/docs/` |
| **Service** | `svc` | Service docs | Service folder or `architect_central_services/docs/` |
| **Identity** | `ident` | Identity layer | `architect_central_services/identity/docs/` |
| **Governance** | `gov` | Policies, standards | `docs/policies/`, `docs/standards/` |
| **Data** | `data` | Schema, data dictionary | `docs/data_dictionary/` |
| **Operations** | `ops` | Runbooks, how-to | `docs/guides/` |
| **Contract** | `contract` | Pattern contracts | `docs/primitive/contracts/` |

---

## File Types

| Type | Extension | Description |
|------|-----------|-------------|
| **MD** | `.md` | Markdown documentation |
| **SQL** | `.sql` | SQL schemas, queries |
| **PY** | `.py` | Python code |
| **YAML** | `.yaml`, `.yml` | Configuration |
| **JSON** | `.json` | Data, config |
| **TOML** | `.toml` | Configuration |

---

## Series (From DOCUMENT_SERIES_FRAMEWORK)

| Series | Question | When to Load |
|--------|----------|--------------|
| **PRIMITIVE** | "What is foundational?" | Once per project |
| **ARCH** | "How is it organized?" | When designing |
| **SPEC** | "What exactly does X do?" | When implementing |
| **REF** | "What exists?" | When searching |
| **OPS** | "How do I use X?" | When operating |
| **STATUS** | "What's happening now?" | When debugging |

---

## Document ID Format

```
doc:{category}:{series}:{number}:{slug}
```

**Examples:**
- `doc:core:primitive:01:exist_now`
- `doc:pipe:spec:05:chatgpt_stage_5`
- `doc:contract:spec:01:file_to_atom_lineage`
- `doc:svc:ref:03:knowledge_atom_service`

---

## Related Documents

Documents form chains:

```
primitive → primitive2 → primitive3
    │           │            │
    └───────────┴────────────┘
        related_docs array
```

### Relation Types

| Relation | Meaning | Direction |
|----------|---------|-----------|
| **requires** | Must read before this | Backward |
| **enables** | This unlocks next | Forward |
| **extends** | Adds to (primitive → primitive2) | Forward |
| **supersedes** | Replaces older version | Backward |
| **see_also** | Related but independent | Bidirectional |

---

## Schema: Document Registry Table

```sql
CREATE TABLE IF NOT EXISTS `jeremy-serna.knowledge.document_registry` (
    -- Identity (from FILE_TO_ATOM_LINEAGE)
    doc_id STRING NOT NULL,            -- doc:{category}:{series}:{number}:{slug}
    file_id STRING NOT NULL,           -- → file_registry.file_id

    -- Classification
    category STRING NOT NULL,          -- core, pipe, svc, etc.
    file_type STRING NOT NULL,         -- MD, SQL, PY, etc.

    -- Series
    series STRING,                     -- primitive, arch, spec, ref, ops, status
    series_number INT64,               -- Position in series (01, 02, etc.)

    -- Content
    title STRING NOT NULL,             -- Document title
    slug STRING NOT NULL,              -- URL-safe identifier
    description STRING,                -- TL;DR

    -- Relations
    related_docs ARRAY<STRUCT<
        doc_id STRING,
        relation_type STRING           -- requires, enables, extends, supersedes, see_also
    >>,

    -- Metadata
    author STRING,
    version STRING,                    -- Semantic version (1.0.0)
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP,
    atom_status STRING,                -- pending, extracted, n/a
    atom_count INT64,                  -- Number of atoms extracted

    -- Source
    file_path STRING NOT NULL,         -- Current location
    home_directory STRING NOT NULL     -- Canonical home
)
PARTITION BY DATE(created_at)
CLUSTER BY category, series, doc_id
OPTIONS (
    description = 'Registry of all documents with metadata, classification, and relations',
    labels = [
        ("contract", "document_metadata"),
        ("layer", "knowledge")
    ]
);
```

---

## Document Header (Required)

Every document MUST start with:

```markdown
# Document Title

**Doc ID**: doc:{category}:{series}:{number}:{slug}
**Category**: {Core | Pipeline | Service | Identity | Governance | Data | Operations | Contract}
**File Type**: MD
**Series**: {PRIMITIVE | ARCH | SPEC | REF | OPS | STATUS}
**Version**: {X.Y.Z}
**Created**: {YYYY-MM-DD}
**Author**: {name}

**Requires**: [prerequisite](path)
**Enables**: [dependent](path)
**Extends**: [previous in chain](path)

---

## TL;DR

- Point 1
- Point 2
- Point 3

---
```

---

## Pipeline Document Example

```markdown
# Text Messages Stage 4 - Identity Resolution

**Doc ID**: doc:pipe:spec:04:text_messages_stage_4
**Category**: Pipeline
**File Type**: MD
**Series**: SPEC
**Version**: 1.0.0
**Created**: 2025-12-30
**Author**: Jeremy Serna & Claude Code

**Requires**: [Stage 3](./STAGE_3.md)
**Enables**: [Stage 5](./STAGE_5.md)
**Extends**: [SMS Pipeline Overview](./ARCHITECTURE.md)

---

## TL;DR

- Stage 4 resolves message senders to known identities
- Uses identity layer contacts_master for matching
- Output: messages with resolved `sender_id`

---
```

---

## Related Document Chains

### Primitive Chain (Core)
```
01_exist_now.md
    └── extends → 02_reality_layers.md
                      └── extends → 03_furnace_principle.md
                                        └── extends → 04_standards.md
```

### Pipeline Chain (Per Source)
```
STAGE_0_ASSESSMENT.md
    └── enables → STAGE_1_EXTRACTION.md
                      └── enables → STAGE_2_CLEANING.md
                                        └── enables → ...
```

### Contract Chain
```
FILE_TO_ATOM_LINEAGE.md
    └── see_also → DOCUMENT_ROUTING.md
                      └── see_also → DOCUMENT_METADATA.md (this)
```

---

## The Registration Flow

```python
from architect_central_services import generate_file_id

def register_document(
    file_path: str,
    title: str,
    category: str,
    series: str = None,
    series_number: int = None,
    related_docs: list = None
) -> str:
    """Register a document with full metadata."""

    # 1. Register file (from FILE_TO_ATOM_LINEAGE)
    file_id = register_file(file_path)

    # 2. Generate doc_id
    slug = slugify(title)
    number_str = f"{series_number:02d}" if series_number else "00"
    doc_id = f"doc:{category}:{series or 'none'}:{number_str}:{slug}"

    # 3. Determine home directory (from DOCUMENT_ROUTING)
    home = get_document_home(file_path, category)

    # 4. Insert into document_registry
    insert_document_registry(
        doc_id=doc_id,
        file_id=file_id,
        category=category,
        file_type=Path(file_path).suffix[1:].upper(),
        series=series,
        series_number=series_number,
        title=title,
        slug=slug,
        related_docs=related_docs or [],
        file_path=str(file_path),
        home_directory=home,
        created_at=datetime.utcnow()
    )

    return doc_id
```

---

## Queries Enabled

### "All docs in a series"
```sql
SELECT * FROM knowledge.document_registry
WHERE series = 'primitive'
ORDER BY series_number;
```

### "Related documents chain"
```sql
WITH RECURSIVE chain AS (
    SELECT doc_id, title, related_docs, 0 as depth
    FROM knowledge.document_registry
    WHERE doc_id = @start_doc_id

    UNION ALL

    SELECT d.doc_id, d.title, d.related_docs, c.depth + 1
    FROM chain c, UNNEST(c.related_docs) AS rel
    JOIN knowledge.document_registry d ON d.doc_id = rel.doc_id
    WHERE rel.relation_type IN ('enables', 'extends')
    AND c.depth < 10
)
SELECT * FROM chain ORDER BY depth;
```

### "Docs by category"
```sql
SELECT category, COUNT(*) as doc_count
FROM knowledge.document_registry
GROUP BY category
ORDER BY doc_count DESC;
```

---

## Definition of Done

### Phase 1: Created
- [x] Contract defined
- [ ] `document_registry` table created
- [ ] `register_document()` function implemented
- [ ] Doc ID generator added

### Phase 2: Adopted
- [ ] New docs registered on creation
- [ ] Existing key docs registered
- [ ] Header format enforced

### Phase 3: Enforced
- [ ] Pre-commit hook: docs must have required header
- [ ] Claude Code rule: register on creation
- [ ] Conformance checker for doc headers

---

## Related

- [FILE_TO_ATOM_LINEAGE.md](FILE_TO_ATOM_LINEAGE.md) - File → Content → Atoms
- [DOCUMENT_ROUTING.md](DOCUMENT_ROUTING.md) - Every doc has a home
- [DOCUMENT_SERIES_FRAMEWORK.md](../../standards/DOCUMENT_SERIES_FRAMEWORK.md) - Series structure

---

**Every document has identity. Category. Series. Relations. Register them all.**
