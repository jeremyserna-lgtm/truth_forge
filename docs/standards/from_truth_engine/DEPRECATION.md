# Deprecation Standard

**The Standard** | How code AND documentation are phased out safely with clear timelines, migration paths, and tooling.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Quick Reference

| Artifact Type | Deprecation Location | Archive Location | Minimum Notice |
|---------------|---------------------|------------------|----------------|
| Code (functions, classes) | In-place with `@deprecated` | N/A (deleted after removal) | 2 minor versions OR 6 months |
| Standards Documents | In-place with header warning | `framework/standards/archive/` | 30 days |
| Framework Documents | In-place with header warning | `framework/archive/` | 30 days |
| Other Documentation | In-place with header warning | Nearest `archive/` folder | 30 days |

---

## 🚨 AGENT DIRECTIVE: Deprecation Enforcement

**ALL AGENTS MUST FOLLOW THIS POLICY.** When creating, modifying, or removing any artifact:

1. **NEVER delete without deprecation** — Mark deprecated first, archive later
2. **ALWAYS use centralized archive folders** — Never scatter deprecated docs
3. **ALWAYS update archive INDEX.md** — Every archived document must be registered
4. **ALWAYS include supersession reference** — What replaces this artifact?
5. **VERIFY before creating new documents** — Does a canonical version already exist?

---

## Part 1: Code Deprecation

### The Pattern

```python
from framework.standards.deprecation import deprecated

@deprecated(
    since="2.3.0",
    removal="3.0.0",
    reason="O(n²) complexity causes performance issues",
    replacement="process_items_v2"
)
def process_items(items: list) -> list:
    """Process items.

    .. deprecated:: 2.3.0
        Use :func:`process_items_v2` instead.
        Removal in version 3.0.0.
    """
    return [x * 2 for x in items]
```

### Code Deprecation Requirements

| Requirement | Rule |
|-------------|------|
| Decorator | Use `@deprecated` from `deprecation_utils.py` |
| Metadata | `since`, `removal`, `reason`, `replacement` (all required) |
| Docstring | Include `.. deprecated::` directive |
| Timeline | Minimum 2 minor versions OR 6 months |
| CHANGELOG | Entry under "Deprecated" when marking, "Removed" when deleting |

### Code Deprecation Lifecycle

```
ACTIVE → DEPRECATED → REMOVED
         │            │
         │            └── After removal version (code deleted)
         └── When replacement ready (decorator added)
```

### MUST (Required) — Code

1. **Use the `@deprecated` decorator** — All deprecated code uses the standard decorator.
2. **Provide all metadata**: `since`, `removal`, `reason`, `replacement`
3. **Update docstrings** — Add `.. deprecated::` directive.
4. **Respect minimum period** — 2 minor versions OR 6 months, whichever is longer.
5. **Update CHANGELOG** — "Deprecated" when marking, "Removed" when deleting.

### MUST NOT (Prohibited) — Code

1. **Remove without deprecation** — Never delete public APIs without prior deprecation.
2. **Deprecate in patches** — Only in minor or major versions.
3. **Shorten timeline silently** — Communicate explicitly if accelerated.

---

## Part 2: Document Deprecation

### Document Deprecation Lifecycle

```
ACTIVE → DEPRECATED → ARCHIVED → (optional) DELETED
         │            │           │
         │            │           └── After retention period (2-7 years)
         │            └── When superseded (moved to archive/)
         └── When replacement ready (warning header added)
```

### Document Deprecation Header

When a document is deprecated but not yet archived, add this header immediately after the title:

```markdown
# Document Title

> ⚠️ **DEPRECATED** — This document is superseded by [NEW_DOCUMENT.md](path/to/NEW_DOCUMENT.md).
>
> | Status | Deprecated |
> |--------|------------|
> | Superseded By | [NEW_DOCUMENT.md](path/to/NEW_DOCUMENT.md) |
> | Deprecated Date | YYYY-MM-DD |
> | Archive Date | YYYY-MM-DD (planned) |
> | Reason | Brief explanation |
>
> **Do not use this document for new work.** Refer to the superseding document.

(rest of document content)
```

### Document Archive Locations

| Document Type | Archive Location |
|---------------|------------------|
| Standards (`framework/standards/*.md`) | `framework/standards/archive/` |
| Framework docs (`framework/*.md`) | `framework/archive/` |
| Service docs (`src/services/*/docs/`) | `src/services/*/docs/archive/` |
| Root-level docs (`/*.md`) | `docs/archive/` or nearest `archive/` |

### MUST (Required) — Documents

1. **Add deprecation header** — Before archiving, document must have warning header for 30 days minimum.
2. **Use centralized archive folders** — Never create ad-hoc archive locations.
3. **Update archive INDEX.md** — Every archived document must be registered.
4. **Include supersession chain** — Document what replaces this and why.
5. **Preserve for reference** — Archives are read-only historical references.

### MUST NOT (Prohibited) — Documents

1. **Delete without archiving** — Documents are archived, not deleted.
2. **Archive without deprecation notice** — Must have 30-day warning period.
3. **Create duplicate documents** — Check for existing canonical versions first.
4. **Reference archived documents as authoritative** — Always use canonical versions.

---

## Part 3: Archive Policy

### Archive Folder Structure

Every major directory with documentation should have an `archive/` subfolder:

```
framework/
├── standards/
│   ├── archive/           # Archived standards
│   │   ├── INDEX.md       # Required: registry of archived docs
│   │   └── *.md           # Archived documents
│   └── *.md               # Active standards
├── archive/               # Archived framework docs
│   ├── INDEX.md
│   └── *.md
└── *.md                   # Active framework docs
```

### Archive INDEX.md Template

Every `archive/` folder MUST contain an `INDEX.md` with this structure:

```markdown
# Archive Index

**Superseded documents.** Historical reference only. Do not use for new work.

---

## Archived Documents

| Document | Superseded By | Date Archived | Retention Until |
|----------|---------------|---------------|-----------------|
| OLD_DOC.md | [NEW_DOC.md](../NEW_DOC.md) | YYYY-MM-DD | YYYY-MM-DD |

---

## Archive Policy

- **Purpose**: Historical reference, audit trail, migration support
- **Status**: NOT AUTHORITATIVE — Always use canonical versions
- **Retention**: Minimum 2 years, maximum 7 years (unless legal hold)
- **Deletion**: Requires explicit approval and audit trail entry

---

## Do Not Reference These Documents

These documents are NOT authoritative. Always use the canonical document that superseded them.
```

### Retention Policy

| Document Type | Minimum Retention | Maximum Retention | Deletion Authority |
|---------------|-------------------|-------------------|-------------------|
| Standards | 2 years | 7 years | Framework owner |
| Framework docs | 2 years | 7 years | Framework owner |
| Compliance docs | 7 years | Indefinite | Legal/Compliance |
| API docs | 2 years | 5 years | API owner |
| General docs | 1 year | 3 years | Document owner |

### Retention Exceptions

- **Legal hold**: Documents under legal hold are NEVER deleted
- **Compliance**: SOC2, HIPAA, PCI documents follow regulatory requirements
- **Audit trail**: Deletion must be recorded in archive INDEX.md

---

## Part 4: Agent Enforcement

### Pre-Creation Checklist

Before creating ANY new document, agents MUST:

```markdown
## Document Creation Checklist

- [ ] Searched for existing canonical document on this topic
- [ ] Verified no duplicate in `framework/standards/`
- [ ] Verified no duplicate in `framework/` (numbered docs)
- [ ] If updating existing topic, will deprecate old document
- [ ] New document follows DOCUMENT_FORMAT standard
- [ ] New document has authority header referencing governing doc
```

### Pre-Deletion/Archive Checklist

Before archiving ANY document, agents MUST:

```markdown
## Archive Checklist

- [ ] Document has had deprecation header for 30+ days (or emergency exception documented)
- [ ] Superseding document exists and is canonical
- [ ] Archive INDEX.md will be updated
- [ ] All references to old document identified
- [ ] Migration path documented in superseding document
```

### Agent Instructions Block

**Copy this block into agent instruction files (.cursorrules, CLAUDE.md, etc.):**

```markdown
## 📦 DEPRECATION & ARCHIVE POLICY — MANDATORY

**Before creating documents:**
1. Search `framework/standards/` for existing canonical version
2. Search `framework/` for existing numbered framework doc
3. If topic exists, UPDATE existing doc — do not create duplicate

**Before removing/replacing documents:**
1. Add deprecation header to old document
2. Wait 30 days (or document emergency exception)
3. Move to nearest `archive/` folder
4. Update `archive/INDEX.md` with entry
5. Update references to point to new canonical doc

**Archive locations:**
- Standards: `framework/standards/archive/`
- Framework: `framework/archive/`
- Services: `src/services/*/docs/archive/`

**NEVER:**
- Delete documents without archiving
- Create duplicates of existing topics
- Reference archived docs as authoritative
- Archive without updating INDEX.md
```

---

## Part 5: Semantic Versioning Integration

### Code Deprecation

| Version Change | Deprecation Action |
|----------------|-------------------|
| Patch (x.y.Z) | Never introduce deprecations |
| Minor (x.Y.0) | Add new deprecations, maintain deprecated code |
| Major (X.0.0) | Remove deprecated code |

### Document Deprecation

| Change Type | Action |
|-------------|--------|
| Minor update | Edit in place, no deprecation |
| Major rewrite | Deprecate old, create new canonical |
| Consolidation | Deprecate fragments, create unified doc |
| Obsolescence | Deprecate and archive, no replacement needed |

---

## Enforcement

### Automated (pylint + deprecation_checker)

| Check | Severity |
|-------|----------|
| Missing decorator metadata | error |
| Missing docstring notice | warning |
| Invalid version format | error |
| Version ordering (removal > since) | error |

### Documentation Enforcement

| Check | Mechanism |
|-------|-----------|
| Duplicate detection | Agent pre-creation checklist |
| Archive INDEX current | PR review checklist |
| Deprecation headers present | Agent enforcement |
| Retention policy compliance | Quarterly audit |

### Configuration

```ini
# pylintrc
[MASTER]
load-plugins=framework.standards.deprecation.deprecation_checker
```

---

## Escape Hatch

### Code — Security Emergency

```python
@deprecated(
    since="2.3.0",
    removal="2.4.0",  # Shortened
    reason="SECURITY: CVE-XXXX-YYYY",
    replacement="secure_function"
)
# standard:override deprecation-min-timeline - Security vulnerability CVE-XXXX-YYYY
def vulnerable_function():
    ...
```

### Documents — Emergency Archive

```markdown
> ⚠️ **EMERGENCY ARCHIVE** — Archived without standard 30-day notice.
>
> | Status | Archived |
> |--------|----------|
> | Exception Reason | [Security/Compliance/Critical Error] |
> | Approved By | [Name] |
> | Date | YYYY-MM-DD |
> | Standard Override | `standard:override deprecation-notice-period` |
```

---

## Tooling

Location: `framework/standards/deprecation/`

| File | Purpose |
|------|---------|
| `deprecation_utils.py` | `@deprecated` decorator and helpers |
| `deprecation_checker.py` | Pylint plugin for enforcement |
| `test_deprecation.py` | Test suite |

---

## CHANGELOG Format

```markdown
## [2.3.0] - 2025-01-15

### Deprecated
- `process_items()` - Use `process_items_v2()`. Removal in 3.0.0. (#123)
- `OLD_STANDARD.md` - Superseded by `NEW_STANDARD.md`. Archived. (#124)

## [3.0.0] - 2025-07-01

### Removed
- `process_items()` - Deprecated since 2.3.0. (#123)
```

---

## Related Standards

- [DOCUMENT_FORMAT.md](DOCUMENT_FORMAT.md) — Document structure
- [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) — Archive folder locations
- [VERSION_CONTROL.md](VERSION_CONTROL.md) — Commit messages for deprecations

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2025-01-18 | Added document deprecation policy, archive policy, agent enforcement | Claude |
| 2025-01-18 | Initial code deprecation standard | Claude |

---

*~350 lines. Deprecation and archive standard. Complete.*
