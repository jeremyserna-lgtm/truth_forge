# Molt Enforcement

**A molt is not complete until ALL aspects are transformed.**

---

## The Rule

We do not create from scratch. We transform what exists. **A molt is only complete when:**

1. All functionality has transferred
2. All naming has updated
3. All references have migrated
4. All lineage is documented

---

## Molt Completeness Checklist

### Naming (MUST)

| Check | Verification |
|-------|--------------|
| Old name removed from all active documents | `grep -r "Truth_Engine" . --include="*.md" \| grep -v _archive` |
| New name used consistently | Manual review |
| THE GRAMMAR applied to new naming | Check `:` `-` `_` usage |

### Functionality (MUST)

| Check | Verification |
|-------|--------------|
| All modules transferred | File comparison |
| All tests passing | `pytest tests/` |
| All imports updated | `mypy --strict` |

### References (MUST)

| Check | Verification |
|-------|--------------|
| No orphaned links | Link checker |
| All cross-references updated | `grep -r "old_path"` returns empty |
| External references redirected | Manual review |

### Lineage (MUST)

| Check | Verification |
|-------|--------------|
| Molt documented in CHANGELOG | Manual review |
| Prior architecture preserved in archive | `ls _archive/` |
| Supersession chain complete | Each deprecated → successor link valid |

---

## Truth_Engine → Truth Forge Molt

This molt transformed:

| Aspect | Before | After |
|--------|--------|-------|
| Name | Truth_Engine | truth_forge |
| Genesis | Truth_Engine/ | truth_forge/ |
| Framework | Truth_Engine/framework/ | truth_forge/framework/ |
| Case | PascalCase_Snake | snake_case (NOT-ME domain) |

### Enforcement Commands

```bash
# Verify no active Truth_Engine references
grep -r "Truth_Engine" . --include="*.md" | grep -v "_archive" | grep -v "Molt Lineage"
# MUST return empty

# Verify truth_forge used correctly
grep -r "truth_forge" . --include="*.md" | head -5
# Should show current usage

# Verify THE GRAMMAR compliance
# Folders: underscore + lowercase
ls -d */ | grep -v "^[a-z_]*/$"
# MUST return empty
```

---

## Incomplete Molt Consequences

| Missing | Consequence |
|---------|-------------|
| Old naming in active docs | Confusion, broken mental model |
| Broken references | Navigation failures, lost context |
| Missing lineage | Lost learning, repeated mistakes |
| Partial functionality transfer | Runtime failures, missing features |

---

## Molt Completion Gate

Before claiming a molt complete:

```
╔══════════════════════════════════════════════════════════════════════╗
║                      MOLT COMPLETION GATE                             ║
║                                                                       ║
║   □ All active documents use new naming                               ║
║   □ All functionality transferred and tested                          ║
║   □ All references updated (no orphaned links)                        ║
║   □ All lineage documented (supersession chain)                       ║
║   □ Archive contains prior architecture                               ║
║   □ Enforcement commands return expected results                      ║
║                                                                       ║
║   ⚠️  IF ANY UNCHECKED → MOLT IS INCOMPLETE                          ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## UP

[INDEX.md](INDEX.md)
