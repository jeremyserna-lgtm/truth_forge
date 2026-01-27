# What Molt IS

**Layer**: Theory (ME) - defines what a molt primitive IS

---

## The Primitive

**Molt** is the mechanism by which organisms shed old architecture to grow into new forms.

```
Prior Architecture → Discovery → Transformation → New Architecture
```

We do not create from scratch. We transform what exists.

---

## Why Molt Exists

### The Problem

Content moves. Architecture evolves. Without molt:
- Old locations become dead ends
- Lineage is lost
- Reversibility is impossible
- Growth creates orphans

### The Solution

Molt provides:
- **Archive**: Original preserved, dated, accessible
- **Stub**: Redirect in original location
- **Audit Trail**: Who → Where → When
- **Reversibility**: Archive enables restoration

---

## Molt as DNA

Molt is a **DNA capability**—it is inherited by every organism.

| Attribute | Value |
|-----------|-------|
| **Inheritance** | Automatic (all organisms) |
| **Location** | `src/{organism}/molt/` |
| **Standard** | `framework/standards/molt/` |
| **Tracking** | Framework-level |

Non-DNA capabilities are organism-specific. Molt is universal.

---

## The Molt Anatomy

### Input (HOLD₁)

- Source directory with content
- Destination directory (where content moved)
- Archive directory (where originals go)

### Process (AGENT)

1. Discover files in source
2. Check if migrated to destination
3. Archive original to dated folder
4. Create redirect stub in source
5. Update audit trail

### Output (HOLD₂)

- Archive folder with originals
- Stub files in source (7-line redirects)
- Updated audit index

---

## The Stub Contract

Every stub MUST contain:

```markdown
# [Title]

> **MOVED**: This document has been molted to [destination].
>
> **New Location**: [relative path to new location]
>
> **Archive**: [relative path to archive]
>
> **Molted On**: [YYYY-MM-DD]
```

This is the minimum viable stub. Extensions are allowed.

---

## Shrinkage Guarantee

**Source MUST shrink after molt.**

| Metric | Before | After |
|--------|--------|-------|
| Source size | Original content | ~7 lines per file |
| Archive size | Empty | Original content |
| Total content | X | X (preserved) |

If source did not shrink, molt did not happen.

---

## UP

[INDEX.md](INDEX.md) - Molt Standard hub
