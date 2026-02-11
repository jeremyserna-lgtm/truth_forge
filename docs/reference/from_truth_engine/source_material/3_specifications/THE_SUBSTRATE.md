# Contract: THE_SUBSTRATE

**Type**: exist-now (foundational primitive)
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

There is a **substrate** - the root - from which all directories attach.

**Critical Distinction**: Some things ARE substrate. Others ATTACH to substrate.

```
THE SUBSTRATE (root: PrimitiveEngine/)
    │
    ├── Substrate Layers (ARE foundation - don't have primitive series)
    │   └── architect_central_services/src/.../
    │       ├── core/           ← IS substrate (identity, logging, config)
    │       ├── governance/     ← IS substrate (policies, intake)
    │       ├── cost/           ← IS substrate (cost protection)
    │       └── data_processing/ ← IS substrate (loaders, adapters)
    │
    ├── Pattern Contracts (primitives that define attachment)
    │   └── docs/primitive/contracts/
    │       └── *.md
    │
    └── Primitive Directories (ATTACH to substrate - have primitive series)
        ├── pipelines/text_messages/docs/primitive/
        ├── pipelines/chatgpt/docs/primitive/
        ├── identity/docs/primitive/
        └── {new_system}/docs/primitive/
```

---

## Substrate vs Primitive Directory

| Type | What It Is | Has Primitive Series? | Example |
|------|------------|----------------------|---------|
| **Substrate Layer** | Infrastructure others USE | **No** - IS the foundation | `core/`, `governance/` |
| **Primitive Directory** | System that USES substrate | **Yes** - describes itself | `pipelines/text_messages/` |

**Substrate layers don't describe themselves with primitive series. They ARE what others use.**

```python
# Substrate provides:
from architect_central_services import (
    get_logger,           # core/ substrate
    generate_message_id,  # core/identity_service substrate
    track_cost,          # cost/ substrate
    backlog,             # governance/intake substrate
)

# Primitive directories consume substrate, then describe themselves
# in their docs/primitive/ series
```

---

## Patterns ARE Primitives

**Patterns are exist-now too.** They exist in time. They have identity. They can be referenced.

| Pattern Contract | Pattern ID | What It IS |
|------------------|------------|------------|
| FILE_TO_ATOM_LINEAGE | `pat:file_to_atom` | The traceability chain |
| DOCUMENT_ROUTING | `pat:doc_routing` | Every doc has a home |
| DOCUMENT_METADATA | `pat:doc_metadata` | Doc classification |
| SYSTEM_FOLDER_PATTERN | `pat:sys_folder` | Every system same structure |
| PRIMITIVE_SERIES_TEMPLATE | `pat:prim_series` | Six questions answered |
| THE_SUBSTRATE | `pat:substrate` | The root everything attaches to |
| GENERATIVE_PRIMITIVE | `pat:gen_primitive` | Atoms → generated primitives |
| THE_PROGENITOR | `pat:progenitor` | Claude as membrane, reaches outside |
| THE_METABOLISM | `pat:metabolism` | Core digests, atoms to atoms |
| KNOWLEDGE_ATOM_SCHEMA | `pat:atom_schema` | Atoms tagged by growth type |

---

## Every Pattern Meets Truth Engine Standards

Every pattern contract MUST conform to:

### 1. The Three-Layer Test

| Layer | Question | Pattern Must Answer |
|-------|----------|---------------------|
| **Theory** | WHY does this pattern exist? | Origin, purpose, gap filled |
| **Specification** | WHAT exactly does it do? | Schema, flow, requirements |
| **Reference** | HOW do I use it? | Examples, templates, code |

### 2. Definition of Done (Patterns)

Every pattern contract must have:

- [ ] **Identity**: Pattern ID (`pat:{name}`)
- [ ] **Type declaration**: What kind of primitive is it
- [ ] **The Pattern section**: Clear description
- [ ] **Schema** (if applicable): Database tables
- [ ] **Code** (if applicable): Implementation patterns
- [ ] **Definition of Done**: Checklist for adopters
- [ ] **Related**: Links to related patterns

### 3. Hybrid Durability

Pattern contracts exist in:
- **Local**: `docs/primitive/contracts/*.md` (git)
- **Cloud**: `governance.pattern_contracts` (BigQuery, for querying)

---

## The Attachment Model

Systems attach to the substrate by:

1. **Creating their primitive series** (`{system}/docs/primitive/`)
2. **Following the folder pattern** (SYSTEM_FOLDER_PATTERN)
3. **Implementing pattern contracts** (as applicable)
4. **Registering in file_registry** (FILE_TO_ATOM_LINEAGE)

```
Substrate (root)
    │
    ├── Pattern defines → How systems attach
    │
    ├── System attaches → Following the pattern
    │
    └── Pattern IS a primitive → Attached to same substrate
```

---

## The Recursion

**Patterns are primitives. Primitives follow patterns. The loop closes.**

```
Patterns exist (as primitives)
    ↓
Patterns define structure (for other primitives)
    ↓
New primitives follow patterns (including new patterns)
    ↓
New patterns become primitives
    ↓
Loop continues
```

---

## Root Structure

The substrate's core directories:

```
PrimitiveEngine/                           ← THE SUBSTRATE (root)
│
├── docs/
│   ├── primitive/
│   │   ├── THE_ROOT.md                ← The root's existence (philosophical)
│   │   ├── THE_PRIMITIVE.md           ← What primitives are
│   │   ├── TRUTH_ENGINE_STANDARDS.md  ← The constitution
│   │   ├── contracts/                  ← Pattern contracts
│   │   │   ├── templates/             ← Templates for primitive series
│   │   │   ├── THE_SUBSTRATE.md       ← This file
│   │   │   └── *.md                   ← Other pattern contracts
│   │   └── *.md                        ← Other root-level primitives
│   │
│   └── consolidated/                   ← Index files
│
├── architect_central_services/
│   │
│   ├── src/.../                        ← SUBSTRATE LAYERS (no primitive series)
│   │   ├── core/                      ← IS substrate
│   │   ├── governance/                ← IS substrate
│   │   ├── cost/                      ← IS substrate
│   │   └── data_processing/           ← IS substrate
│   │
│   ├── pipelines/                      ← PRIMITIVE DIRECTORIES (have series)
│   │   ├── text_messages/docs/primitive/
│   │   ├── chatgpt/docs/primitive/
│   │   └── zoom/docs/primitive/
│   │
│   ├── identity/docs/primitive/        ← PRIMITIVE DIRECTORY
│   │
│   └── src/.../                        ← PRIMITIVE DIRECTORIES (have series)
│       ├── knowledge_atom_service/docs/primitive/
│       └── truth/docs/primitive/
│
└── ...                                 ← More systems attach
```

---

## Conformance

Every attached system must meet Truth Engine standards by having:

| Requirement | Check |
|-------------|-------|
| Primitive series | `{system}/docs/primitive/` exists |
| INDEX.md | Entry point exists |
| Six files | 01_WHAT through 06_WHO |
| Pattern conformance | Follows SYSTEM_FOLDER_PATTERN |
| Registration | Files in file_registry |

---

## Related

- [THE_SEED.md](../../1_core/01_THE_SEED.md) - The bedrock
- [THE_STANDARDS.md](../../1_core/09_THE_STANDARDS.md) - The constitution
- [SYSTEM_FOLDER_PATTERN.md](SYSTEM_FOLDER_PATTERN.md) - How systems structure
- [PRIMITIVE_SERIES_TEMPLATE.md](PRIMITIVE_SERIES_TEMPLATE.md) - The six questions

---

**The substrate is the root. Patterns attach. Patterns ARE primitives. Everything conforms to Truth Engine standards.**
