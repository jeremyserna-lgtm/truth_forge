# Deprecation States

**The lifecycle states for deprecated components.**

---

## The Rule

Deprecation is not deletion—it is transformation tracking.

---

## State Definitions

| State | Meaning | Action Required |
|-------|---------|-----------------|
| **ACTIVE** | Current, in use | None |
| **DEPRECATED** | Superseded, marked for archive | Add deprecation header, move to archive immediately |
| **ARCHIVED** | Historical reference only | Moved to archive location and GCS bucket, removed from source |

---

## State Transitions

```
ACTIVE ──→ DEPRECATED ──→ ARCHIVED
              │              │
              └── Immediate ─┘
```

**Note**: Deprecated documents are archived immediately. The DEPRECATED state is transient—documents are moved to archive and uploaded to GCS bucket `gs://truth-engine-archive/` immediately. Files are removed from source location with no redirect stubs.

---

## Deprecation Header

Every deprecated document MUST begin with:

```markdown
> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [path/to/new/document.md]
> - **Deprecated On**: [YYYY-MM-DD]
> - **Archived On**: [YYYY-MM-DD]
> - **Reason**: [Brief explanation]
>
> This document has been moved to archive. See archive location below.
```

**Note**: Deprecated documents are immediately moved to archive and uploaded to GCS bucket `gs://truth-engine-archive/`. The original location is left empty (file removed, no redirect stub).

---

## Code Deprecation

For code files:

```python
# DEPRECATED: This module has been superseded.
# Superseded By: src/new_module.py
# Deprecated On: 2026-01-26
# Reason: Molted to truth_forge architecture

import warnings
warnings.warn(
    "This module is deprecated. Use new_module instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

## Deprecation vs Deletion

| Action | When | Reversible | Learning Preserved |
|--------|------|------------|-------------------|
| **Deprecation** | Component superseded | Yes | Yes |
| **Sunset** | Deprecated long enough | Difficult | Yes (archived) |
| **Deletion** | Never (avoid) | No | No |

**Deprecation honors lineage.** The old contains accumulated learning.

---

## UP

[INDEX.md](INDEX.md)
