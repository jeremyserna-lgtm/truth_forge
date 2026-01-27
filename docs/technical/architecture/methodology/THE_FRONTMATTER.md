# THE FRONTMATTER

**Version**: 1.0
**Status**: Living Document

---

## Document Structure

- **Theory**: Why frontmatter, why system-issued
- **Specification**: Schema and services
- **Reference**: How to use

---

# THEORY

## The Problem

Without provenance:
- Which version is canonical?
- Did this pass review?
- When was it created?
- Where did it come from?

## The Solution

**Frontmatter = Provenance**

Every document gets metadata that proves:
- It passed review (QA)
- It has a unique identity (ID)
- Its knowledge was extracted (KA)
- Its location is tracked

**Key insight: Claude writes content. System stamps metadata.**

If a document has a valid ID, it's official. Claude can't fake it because Claude doesn't issue IDs—the system does.

---

# SPECIFICATION

## Schema

```yaml
---
# Identity (ID Service)
id: doc:a1b2c3d4                        # Content hash ID, proof of provenance
issued: 2026-01-02T15:30:00Z            # When ID was issued

# QA (QA Service)
qa:
  run_id: QA-000042                     # Which QA run
  date: 2026-01-02T16:00:00Z            # When reviewed
  status: passed                        # passed | failed | pending | skipped

# Knowledge Atoms (KA Service)
ka:
  run_id: KA-000015                     # Which KA run
  date: 2026-01-02T16:05:00Z            # When extracted
  status: extracted                     # extracted | pending | failed | skipped
  atom_count: 12                        # How many atoms
  atom_ids: [AT-001, AT-002, ...]       # Which atoms

# Location (Location Service)
source_location: /original/path.md      # Where it was created
current_location: gs://bucket/path.md   # Where it is now

# Content Metadata (Content Services)
summary: "One sentence description"     # Auto-extracted
keywords: [keyword1, keyword2]          # 3-5 lowercase
category: technical/architecture        # Category path
doc_type: specification                 # Type classification
dates_referenced: [2025-12-01]          # ISO dates found in content

# Changelog (All Services)
changelog:
  - event: created
    date: 2026-01-02T15:30:00Z
    by: frontmatter_coordinator
  - event: qa_reviewed
    date: 2026-01-02T16:00:00Z
    by: qa_service
    details:
      run_id: QA-000042
      status: passed
---
```

## Services

Each service owns its section:

| Service | Section | Responsibility |
|---------|---------|----------------|
| ID Service | `id`, `issued` | Issue unique IDs |
| QA Service | `qa` | Review status |
| KA Service | `ka` | Atom extraction status |
| Location Service | `source_location`, `current_location` | Track file location |
| Content Service | `summary`, `keywords`, `category`, `doc_type`, `dates_referenced` | Content analysis |
| Changelog | `changelog` | All services append events |

**Coordinator** manages the whole, services write their sections.

## ID Format

```
CANONICAL FORMAT: doc:{content_hash} (12-character content hash)
                  doc:a1b2c3d4e5f6

Uses generate_document_id() from id_generator.py.
Deterministic: same content = same ID.

OLD FORMATS (detected and migrated):
            JIRA-style: PROJ-1234
            Issue: #123
            Date-seq: 20240101-001
            UUID: a1b2c3d4-...
            TE-NNNNNN (deprecated sequential format)
```

If document has old format ID → migrate to new format, log the mapping.

## Document Types

| Type | Use |
|------|-----|
| `specification` | Requirements, contracts |
| `notes` | Personal notes, journals |
| `reference` | API docs, lookups |
| `guide` | How-to, tutorials |
| `analysis` | Reports, findings |
| `narrative` | Stories, explanations |
| `script` | Code files |
| `config` | Configuration files |
| `other` | Everything else |

## Categories

```
technical/
├── architecture
├── code
├── api
├── documentation
├── infrastructure

business/
├── strategy
├── operations
├── revenue

operations/
├── config
├── monitoring
├── deployment

personal/
├── notes
├── journal

other/
└── uncategorized
```

---

## Enforcement Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│   CLAUDE: "Write file X"                                                 │
│        │                                                                 │
│        ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ PRE-TOOL-USE                                                     │   │
│   │                                                                  │   │
│   │   NEW file?                                                      │   │
│   │     → Check registry for similarity                             │   │
│   │     → >85% similar? BLOCK (use existing)                        │   │
│   │     → New? ALLOW                                                │   │
│   │                                                                  │   │
│   │   EDIT file?                                                     │   │
│   │     → Has new-format ID? ALLOW                                  │   │
│   │     → Has old-format ID? ALLOW (will migrate)                   │   │
│   │     → No ID? ALLOW (will stamp)                                 │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│        │                                                                 │
│        ▼                                                                 │
│   WRITE OCCURS (file created/modified)                                   │
│        │                                                                 │
│        ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ POST-WRITE                                                       │   │
│   │                                                                  │   │
│   │   Already has new-format ID? → Done                             │   │
│   │                                                                  │   │
│   │   Validate content                                              │   │
│   │     → FAILS? Delete file, BLOCK                                 │   │
│   │     → PASSES? Continue                                          │   │
│   │                                                                  │   │
│   │   Stamp frontmatter:                                            │   │
│   │     1. Issue ID (ID Service)                                    │   │
│   │     2. Set QA status (QA Service)                               │   │
│   │     3. Extract content metadata (Content Service)               │   │
│   │     4. Set source location (Location Service)                   │   │
│   │     5. Add changelog entry                                      │   │
│   │     6. Write frontmatter to file                                │   │
│   │     7. Register in script registry                              │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│        │                                                                 │
│        ▼                                                                 │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │ PRE-COMMIT                                                       │   │
│   │                                                                  │   │
│   │   Has frontmatter? → No? BLOCK                                  │   │
│   │   Has new-format ID? → No? BLOCK                                │   │
│   │   QA status passed? → No? BLOCK                                 │   │
│   │   All yes? → ALLOW COMMIT                                       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│        │                                                                 │
│        ▼                                                                 │
│   COMMIT (document is official)                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# REFERENCE

## Files

| File | Purpose |
|------|---------|
| `services/frontmatter_schema.py` | Schema definition |
| `services/id_service.py` | Issues unique IDs |
| `services/frontmatter_coordinator.py` | Manages all services |
| `services/document_enforcement.py` | Enforcement hooks |

## Storage

```
~/.primitive_engine/
├── id_service/
│   ├── counter.json          # Next ID to issue
│   └── issued.jsonl          # All issued IDs
├── qa_counter.json           # QA run counter
└── enforcement_log.jsonl     # All enforcement events
```

## CLI Usage

```bash
# Check frontmatter
python frontmatter_coordinator.py check /path/to/doc.md

# Stamp document (dry run)
python frontmatter_coordinator.py stamp /path/to/doc.md

# Stamp document (write)
python frontmatter_coordinator.py stamp /path/to/doc.md --write

# Full enforcement flow
python document_enforcement.py process /path/to/doc.md
```

## Integration

The sprawl reducer uses frontmatter:

```python
# After document passes QA during sprawl reduction
coordinator = get_frontmatter_coordinator()
stamped = coordinator.stamp_document(filepath, qa_run_id)
Path(filepath).write_text(stamped)

# After KA extraction
updated = coordinator.update_ka_status(filepath, ka_run_id, atom_count)
Path(filepath).write_text(updated)

# After archive to GCS
updated = coordinator.update_location(filepath, gcs_path, reason="archived")
Path(filepath).write_text(updated)
```

---

## The Principle

**ID = Proof of Provenance**

- No ID → Not official
- Old ID → Needs migration
- New ID → Passed review, tracked, official

**Claude writes content. System stamps metadata.**

---

*This document follows THE_FRAMEWORK structure: Theory, Specification, Reference.*
*— THE_FRONTMATTER*
