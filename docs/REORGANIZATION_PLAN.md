# Docs Folder Reorganization Plan

**Date**: 2026-01-27  
**Status**: Planning  
**Purpose**: Reorganize docs/ to follow THE GRAMMAR and project standards

---

## Current Issues

### 1. Naming Violations
- `06_research/` - Numbered prefix violates folder naming (should be `snake_case`)
- `STUDY_GUIDE/` - PascalCase violates folder naming (should be `study_guide/`)
- `PrimitiveEngine/` - PascalCase (should be `primitive_engine/`)

### 2. Duplicate Folders
- `06_research/` and `research/` - Should be consolidated

### 3. Missing INDEX.md
- Root `docs/` has INDEX.md but may need updates
- Some subfolders missing INDEX.md files

### 4. Archive Organization
- Multiple archive locations: `archive/`, `_archive/`, `_deprecated_*`
- Should consolidate to single `archive/` structure

---

## Proposed Structure

```
docs/
├── INDEX.md                    # Root navigation hub
├── README.md                   # Docs overview
│
├── technical/                  # Technical documentation
│   ├── INDEX.md
│   ├── architecture/
│   ├── data_models/
│   ├── infrastructure/
│   ├── integrations/
│   ├── observability/
│   └── specs/
│
├── operations/                 # Operational documentation
│   ├── INDEX.md
│   ├── manuals/
│   ├── operational/
│   ├── organism/
│   ├── systems/
│   └── tools/
│
├── research/                   # Research documentation (consolidated)
│   ├── INDEX.md
│   ├── analysis/
│   ├── exercises/
│   ├── foundation/
│   ├── observations/
│   ├── source_materials/
│   ├── theoretical/
│   └── validation/
│
├── business/                   # Business documentation
│   ├── INDEX.md
│   ├── branding/
│   ├── communications/
│   ├── marketing/
│   ├── operations/
│   ├── products/
│   ├── sales/
│   └── strategy/
│
├── guides/                     # User guides
│   ├── INDEX.md
│   └── study_guide/            # Renamed from STUDY_GUIDE
│
├── personal/                   # Personal documentation
│   ├── INDEX.md
│   ├── communications/
│   ├── decisions/
│   ├── identity/
│   └── relationships/
│
└── archive/                    # Consolidated archive
    ├── INDEX.md
    └── [dated subfolders]/
```

---

## Actions Required

1. ✅ Merge `06_research/` into `research/`
2. ✅ Rename `STUDY_GUIDE/` to `study_guide/`
3. ✅ Rename `PrimitiveEngine/` to `primitive_engine/`
4. ✅ Consolidate archive folders
5. ✅ Create/update INDEX.md files
6. ✅ Verify all folder names follow `snake_case`

---

## THE GRAMMAR Compliance

| Current | Fixed | Reason |
|---------|-------|--------|
| `06_research/` | Merge to `research/` | No numbered prefixes |
| `STUDY_GUIDE/` | `study_guide/` | PascalCase → snake_case |
| `PrimitiveEngine/` | `primitive_engine/` | PascalCase → snake_case |

---

*Plan ready for execution.*
