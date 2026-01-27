# Standard Migration

**How We Molt. Absorption, Not Creation.**

**Status**: ACTIVE
**Owner**: Framework
**Theory**: [05_EXTENSION](../05_EXTENSION.md) - THE MOLT

---

## WHY (Theory)

From 05_EXTENSION:

> We do not create from scratch. We transform what exists.

Migration is the molt process at the codebase level. One organism absorbs another. The absorbed organism's essence transfers to the absorber; its husk remains as deprecated lineage.

Without migration standards:
- Content duplicates instead of transfers
- Old locations remain authoritative
- Navigation breaks
- Lineage is lost

With migration standards:
- Content compresses into new home
- Old locations deprecate and point
- Navigation updates cleanly
- Lineage is preserved

---

## WHAT (Specification)

### The Molt Principle

Migration follows the biological pattern of molting. **Direction determines sequence.**

### Bidirectional Migration

| Direction | Sequence | Use Case |
|-----------|----------|----------|
| **External → Internal** | MOVE → INDEX → README → MOLT | Absorbing outside content |
| **Internal → External** | MOLT → INDEX → MOVE | Publishing internal content |

#### External → Internal (Absorption)

When bringing content FROM outside INTO the organism:

```
MOVE (bring files to target structure)
        │
        ▼
INDEX (create/update INDEX.md navigation)
        │
        ▼
README (ensure README.md defines the layer)
        │
        ▼
MOLT (compress, deprecate source, record lineage)
```

**Why this order?** Content must arrive before it can be indexed. Indexing must happen before compression decisions. Structure enables assessment.

#### Internal → External (Publication)

When pushing content FROM inside TO outside:

```
MOLT (prepare content for external consumption)
        │
        ▼
INDEX (create navigation for external structure)
        │
        ▼
MOVE (publish to external location)
```

**Why this order?** Content must be molted to fit external requirements before it can be structured and moved.

### The Four Categories

Every migration begins with inventory and categorization:

| Category | Description | Action |
|----------|-------------|--------|
| **GAPS** | Content that doesn't exist in target | Migrate (compress if needed) |
| **REDUNDANCIES** | Content that already exists in target | Skip (don't duplicate) |
| **EJECTIONS** | Content that doesn't belong in target | Move to correct location |
| **ARCHIVE** | Already deprecated in source | Skip (already archived) |

### Migration Requirements

| Requirement | Description |
|-------------|-------------|
| **Compression** | Content MUST fit target limits (300 lines) |
| **Navigation** | All links MUST be updated |
| **Deprecation** | Source MUST be marked deprecated |
| **Lineage** | Molt relationship MUST be recorded |

### The Deprecation Header

Every migrated source file receives:

```markdown
> **DEPRECATED**: This document has been superseded.
> - **Superseded By**: [path/to/new/location.md]
> - **Deprecated On**: YYYY-MM-DD
> - **Sunset Date**: YYYY-MM-DD (3 months default)
> - **Reason**: Molted to [target]. Compressed from X to Y lines.
```

---

## HOW (Reference)

### Step 1: Inventory

List all content in both source and target:

```bash
# List source content
find source/framework -name "*.md" | sort > source_inventory.txt

# List target content
find target/framework -name "*.md" | sort > target_inventory.txt
```

### Step 2: Categorize

For each source file, determine category:

| Source File | Exists in Target? | Belongs in Framework? | Category |
|-------------|-------------------|----------------------|----------|
| 07_STANDARDS.md | No | Yes | GAP |
| CODE_QUALITY.md | Yes (code_quality/) | Yes | REDUNDANCY |
| general/*.md | No | No | EJECTION |
| archive/*.md | N/A | N/A | ARCHIVE |

### Step 3: Compress

For GAPS that exceed limits:

```
ORIGINAL (400 lines)
        │
        ▼
IDENTIFY ESSENCE (what must transfer?)
        │
        ▼
REMOVE REDUNDANCY (what's already elsewhere?)
        │
        ▼
COMPRESS (fit within 300 lines)
        │
        ▼
MIGRATED (168 lines)
```

### Step 4: Transfer

Create compressed content in target with proper navigation:

```markdown
## The Loop

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](00_GENESIS.md) |
| **PREVIOUS** | [previous_doc](previous.md) |
| **NEXT** | [next_doc](next.md) |
| **UP** | [INDEX.md](INDEX.md) |
```

### Step 5: Deprecate

Add deprecation header to source and update source indexes:

```markdown
| File | Status |
|------|--------|
| old_file.md | **DEPRECATED** → [new_location](path/to/new.md) |
```

### Step 6: Update Lineage

Record in target's molt lineage:

```markdown
## Molt Lineage

Truth_Engine (Genesis)
    └── truth_forge (Molt - 2026-01-26)
        └── [Specific files migrated]
```

---

## Verification Checklist

### Pre-Migration

- [ ] Source inventory complete
- [ ] Target inventory complete
- [ ] All content categorized (GAPS/REDUNDANCIES/EJECTIONS/ARCHIVE)

### During Migration

- [ ] All GAPS compressed to fit limits
- [ ] All navigation links updated
- [ ] All deprecation headers added
- [ ] All source indexes updated

### Post-Migration

- [ ] Target files under 300 lines
- [ ] Source files marked DEPRECATED
- [ ] Lineage recorded
- [ ] No broken links

---

## Integration

| Standard | Relationship |
|----------|--------------|
| [STANDARD_LIMIT](STANDARD_LIMIT.md) | Compression must fit limits |
| [molt/](molt/) | **DNA**: Automated molt execution (Archive → Stub → Shrink) |
| [deprecation/](deprecation/) | Deprecation patterns and markers |
| [STANDARD_COMPLETION](STANDARD_COMPLETION.md) | Migration is DONE when all steps verified |

**Implementation**: For automated molt execution, see [molt/PROCESS.md](molt/PROCESS.md).

---

## The Loop

### Navigation

| Position | Document |
|----------|----------|
| **ALPHA** | [00_GENESIS](../00_GENESIS.md) |
| **UP** | [INDEX.md](INDEX.md) |

---

## Convergence

### Bottom-Up Validation

This standard requires:
- [molt/](molt/) - Automated molt execution (DNA capability)
- [deprecation/](deprecation/) - Deprecation patterns
- [STANDARD_LIMIT](STANDARD_LIMIT.md) - Compression targets

### Top-Down Validation

This standard is shaped by:
- [05_EXTENSION](../05_EXTENSION.md) - THE MOLT principle
- [00_GENESIS](../00_GENESIS.md) - Transformation, not creation

---

*We do not create from scratch. We molt. The old shell remains as lineage.*
