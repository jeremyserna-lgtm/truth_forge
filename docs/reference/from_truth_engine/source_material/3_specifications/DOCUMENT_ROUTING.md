# Contract: DOCUMENT_ROUTING

**Type**: do-now (organizational pattern)
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Pattern

Every document type has a **home**. Documents route to their home on creation and can be **brought home** if they stray.

```
Document Created
    │
    ↓ classify
    │
Document Type Identified
    │
    ↓ route
    │
Home Directory (assigned by type)
    │
    ↓ register
    │
File Registry (knows where it lives)
```

---

## The Parallel Directory Bank

Each major system has a **parallel folder structure**. Documents about that system route to folders within it.

**Key insight: Every system has its own primitive series - its core documentation.**

```
architect_central_services/
├── pipelines/
│   ├── text_messages/
│   │   └── docs/
│   │       ├── primitive/      ← TEXT MESSAGE PRIMITIVE SERIES (core)
│   │       │   ├── 01_what.md
│   │       │   ├── 02_why.md
│   │       │   └── 03_how.md
│   │       ├── spec/           ← Specifications
│   │       ├── ref/            ← Reference
│   │       └── status/         ← Current state
│   ├── chatgpt/
│   │   └── docs/
│   │       ├── primitive/      ← CHATGPT PRIMITIVE SERIES (core)
│   │       └── ...
│   └── zoom/
│       └── docs/
│           ├── primitive/      ← ZOOM PRIMITIVE SERIES (core)
│           └── ...
│
├── src/.../
│   ├── knowledge_atom_service/
│   │   ├── primitive/          ← KNOWLEDGE ATOM PRIMITIVE SERIES (core)
│   │   └── *.md
│   └── truth/
│       ├── primitive/          ← TRUTH SERVICE PRIMITIVE SERIES (core)
│       └── *.md
│
└── identity/
    └── docs/
        ├── primitive/          ← IDENTITY PRIMITIVE SERIES (core)
        └── ...

docs/
├── primitive/                  ← SYSTEM-WIDE PRIMITIVE SERIES (foundation)
│   ├── contracts/              ← Contract definitions
│   └── *.md
├── consolidated/               ← Index files (pointers, not content)
├── series/                     ← AI-optimized series (from framework)
│   ├── primitive/              ← Global primitives
│   ├── arch/
│   ├── spec/
│   ├── ref/
│   ├── ops/
│   └── status/
├── specifications/             ← Formal specs HOME
├── architecture/               ← Architecture docs HOME
├── systems/                    ← System overviews HOME
├── policies/                   ← Policy docs HOME
└── data_dictionary/            ← Schema docs HOME
```

### The Primitive Series Pattern

Every system has these parallel folders:

| Folder | Purpose | Contents |
|--------|---------|----------|
| `primitive/` | Core truths | What it IS, Why it exists, How it works |
| `spec/` | Specifications | Schemas, contracts, APIs |
| `ref/` | Reference | Catalogs, indexes, lookups |
| `ops/` | Operations | How to use, runbooks |
| `status/` | Current state | Health, issues, progress |

**The primitive series is the foundation. Everything else builds on it.**

---

## Document Type → Home Mapping

| Document Type | Pattern | Home Directory |
|---------------|---------|----------------|
| **Pipeline docs** | `*_PIPELINE*.md`, `STAGE_*.md` | `pipelines/{source}/docs/` |
| **Service docs** | `*_SERVICE*.md` | Service folder or `architect_central_services/docs/` |
| **Contracts** | `*.md` defining patterns | `docs/primitive/contracts/` |
| **Specifications** | `*_SPEC.md`, `*_SPECIFICATION.md` | `docs/specifications/` |
| **Architecture** | `*_ARCHITECTURE.md`, system design | `docs/architecture/` |
| **System overviews** | `*_SYSTEM.md` | `docs/systems/` |
| **Policies** | `*_POLICY.md` | `docs/policies/` |
| **Data dictionary** | Schema documentation | `docs/data_dictionary/` |
| **Assessments** | `*_ASSESSMENT.md` | `docs/assessments/` or service folder |
| **Status/reports** | `*_STATUS.md`, `*_REPORT.md` | Near the thing they describe |
| **Index files** | `INDEX.md` | `docs/consolidated/` or in-place |

---

## The Router

```python
from pathlib import Path
from typing import Optional

# Document type patterns → home directories
DOCUMENT_HOMES = {
    # Pipeline docs
    r"text_message.*": "architect_central_services/pipelines/text_messages/docs/",
    r"chatgpt.*": "architect_central_services/pipelines/chatgpt/docs/",
    r"zoom.*": "architect_central_services/pipelines/zoom/docs/",
    r"STAGE_\d+.*": None,  # Infer from content

    # Core docs
    r".*_CONTRACT\.md$": "docs/primitive/contracts/",
    r".*_SPEC\.md$": "docs/specifications/",
    r".*_SPECIFICATION\.md$": "docs/specifications/",
    r".*_ARCHITECTURE\.md$": "docs/architecture/",
    r".*_SYSTEM\.md$": "docs/systems/",
    r".*_POLICY\.md$": "docs/policies/",

    # Service docs
    r"KNOWLEDGE_ATOM.*": "architect_central_services/docs/",
    r".*_SERVICE.*": "architect_central_services/docs/",
}


def get_document_home(filename: str, content: Optional[str] = None) -> str:
    """Determine the home directory for a document.

    Parameters:
    -----------
        filename: Name of the document file
        content: Optional content for deeper classification

    Returns:
    -------
        Path to home directory
    """
    import re

    for pattern, home in DOCUMENT_HOMES.items():
        if re.match(pattern, filename, re.IGNORECASE):
            if home:
                return home
            # Need to infer from content
            break

    # Content-based routing for ambiguous cases
    if content:
        if "text_message" in content.lower() or "sms" in content.lower():
            return "architect_central_services/pipelines/text_messages/docs/"
        if "chatgpt" in content.lower():
            return "architect_central_services/pipelines/chatgpt/docs/"
        if "knowledge atom" in content.lower():
            return "architect_central_services/docs/"

    # Default: holding area
    return "_holding/docs_unclassified/"


def bring_home(file_path: Path) -> Path:
    """Move a document to its home directory.

    Parameters:
    -----------
        file_path: Current location of the document

    Returns:
    -------
        New path after moving to home
    """
    content = file_path.read_text()
    home_dir = get_document_home(file_path.name, content)
    home_path = Path(home_dir) / file_path.name

    # Don't move if already home
    if file_path.parent == Path(home_dir):
        return file_path

    # Move to home
    home_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.rename(home_path)

    return home_path
```

---

## The Sweep Pattern

Periodically, sweep for strays and bring them home:

```python
def sweep_strays(root: Path = Path(".")) -> list[tuple[Path, Path]]:
    """Find documents outside their home and offer to move them.

    Returns list of (current_path, home_path) tuples.
    """
    strays = []

    for md_file in root.rglob("*.md"):
        # Skip already-organized locations
        if any(skip in str(md_file) for skip in [
            "_deprecated", "_holding", ".git", "node_modules", "venv"
        ]):
            continue

        home = get_document_home(md_file.name)
        if not str(md_file).startswith(home):
            strays.append((md_file, Path(home) / md_file.name))

    return strays
```

---

## Integration with FILE_TO_ATOM_LINEAGE

When a document is created:

1. **Route** → Determine home directory
2. **Create** → Write to home directory (not root!)
3. **Register** → Add to `file_registry` with home path
4. **Extract** → Process to atoms with correct `source_file_path`

When a document moves:

1. **Update** → `file_registry.file_path` changes
2. **Preserve** → `file_hash` stays the same (content didn't change)
3. **Lineage** → Atoms still trace back correctly

---

## Anti-Patterns

```python
# WRONG - Create at root, move later
with open("NEW_DOC.md", "w") as f:
    f.write(content)
# ... later ...
shutil.move("NEW_DOC.md", "docs/somewhere/")

# CORRECT - Create at home
home = get_document_home("NEW_DOC.md", content)
with open(f"{home}/NEW_DOC.md", "w") as f:
    f.write(content)
```

---

## Definition of Done

### Phase 1: Created
- [x] Contract defined
- [ ] Router function implemented
- [ ] Bring-home function implemented
- [ ] Sweep function implemented

### Phase 2: Adopted
- [ ] All new documents routed on creation
- [ ] Existing strays identified
- [ ] Major strays brought home

### Phase 3: Enforced
- [ ] Pre-commit hook: new docs must be in home
- [ ] Claude Code rule: create at home, not root
- [ ] Weekly sweep scheduled

---

## Related

- [FILE_TO_ATOM_LINEAGE.md](FILE_TO_ATOM_LINEAGE.md) - Traceability pattern
- [DEPRECATION_POLICY.md](../../policies/DEPRECATION_POLICY.md) - When docs archive
- [06-file-organization.md](../../../.claude/rules/06-file-organization.md) - File org rule
- [sweep_root_to_holding.py](../../../scripts/sweep_root_to_holding.py) - Current sweep script

---

**Every document has a home. Create at home. Bring strays home.**
