# Contract: GENERATIVE_PRIMITIVE

**Type**: do-now (generation pattern)
**Pattern ID**: `pat:gen_primitive`
**Status**: Contract defined
**Created**: 2025-12-30

---

## The Vision

**Primitives can be generated from knowledge atoms.**

When sufficient knowledge exists about a system, the primitive series, directory structure, and scripts can be generated automatically.

```
Knowledge Atoms (sufficient)
    │
    ↓ Pattern recognition
    │
Imagined Primitive
    │
    ↓ Pattern application
    │
Generated Structure
    ├── {system}/
    │   ├── README.md
    │   ├── docs/primitive/
    │   │   ├── INDEX.md
    │   │   ├── 01_WHAT.md
    │   │   ├── 02_WHY.md
    │   │   ├── 03_HOW.md
    │   │   ├── 04_WHERE.md
    │   │   ├── 05_WHEN.md
    │   │   └── 06_WHO.md
    │   ├── scripts/
    │   └── sql/
    │
    ↓ Registration
    │
Primitive exists in Truth Engine
```

---

## The Principle

**Patterns + Sufficient Knowledge = Generation**

| Component | Source | Pattern Applied |
|-----------|--------|-----------------|
| Directory | WHERE atoms | SYSTEM_FOLDER_PATTERN |
| README | WHAT atoms | Standard README template |
| Primitive series | All 6 question atoms | PRIMITIVE_SERIES_TEMPLATE |
| Scripts | HOW atoms | Script patterns |
| SQL | WHERE/HOW atoms | BigQuery patterns |

---

## Knowledge Sufficiency

A primitive can be generated when these atoms exist:

| Question | Required Atoms | Minimum |
|----------|---------------|---------|
| WHAT | Definition, boundaries, type | 3+ |
| WHY | Origin, gap, value | 3+ |
| HOW | Flow, components, dependencies | 5+ |
| WHERE | Code path, data path, doc path | 3+ |
| WHEN | Use cases, anti-patterns | 3+ |
| WHO | Users, maintainers, stakeholders | 2+ |

**Total minimum**: ~19 atoms about a system → generatable primitive

---

## The Generation Flow

### Phase 1: Knowledge Accumulation

```python
# Atoms accumulate from various sources
atoms = [
    Atom(content="Text messages pipeline extracts from chat.db",
         question="WHAT"),
    Atom(content="Jeremy's text history is locked in Apple format",
         question="WHY"),
    Atom(content="Stage 0 assesses, Stage 1 extracts raw",
         question="HOW"),
    # ... more atoms
]
```

### Phase 2: Sufficiency Check

```python
def is_generatable(atoms: List[Atom]) -> bool:
    """Check if enough atoms exist for each question."""
    questions = ["WHAT", "WHY", "HOW", "WHERE", "WHEN", "WHO"]
    for q in questions:
        if count_atoms(atoms, question=q) < MINIMUM[q]:
            return False
    return True
```

### Phase 3: Pattern Application

```python
def generate_primitive(atoms: List[Atom], system_name: str) -> Path:
    """Generate full primitive structure from atoms."""

    # Create directory structure
    root = create_directory(system_name, pattern=SYSTEM_FOLDER_PATTERN)

    # Generate README
    what_atoms = filter_atoms(atoms, question="WHAT")
    generate_readme(root, what_atoms)

    # Generate primitive series
    for question in ["WHAT", "WHY", "HOW", "WHERE", "WHEN", "WHO"]:
        question_atoms = filter_atoms(atoms, question=question)
        generate_doc(root / f"docs/primitive/0{N}_{question}.md",
                     question_atoms,
                     template=PRIMITIVE_SERIES_TEMPLATE)

    # Generate scripts (if HOW atoms are code-specific)
    if has_implementation_atoms(atoms):
        generate_scripts(root / "scripts/", atoms)

    return root
```

### Phase 4: Registration

```python
def register_generated_primitive(root: Path) -> str:
    """Register generated files in file_registry."""
    files = list(root.glob("**/*"))
    for f in files:
        register_file(f)  # FILE_TO_ATOM_LINEAGE
    return generate_primitive_id(root.name)
```

---

## Atom-to-Document Mapping

| Atom Tag | Document Section |
|----------|------------------|
| `atom:what:definition` | 01_WHAT.md → Definition |
| `atom:what:boundary` | 01_WHAT.md → Boundaries |
| `atom:why:origin` | 02_WHY.md → Origin Story |
| `atom:why:gap` | 02_WHY.md → Gap It Fills |
| `atom:how:flow` | 03_HOW.md → The Flow |
| `atom:how:component` | 03_HOW.md → Key Components |
| `atom:where:code` | 04_WHERE.md → Code Locations |
| `atom:where:data` | 04_WHERE.md → Data Locations |
| `atom:when:usecase` | 05_WHEN.md → Use Cases |
| `atom:when:antipattern` | 05_WHEN.md → Anti-Patterns |
| `atom:who:user` | 06_WHO.md → Users |
| `atom:who:maintainer` | 06_WHO.md → Maintainers |

---

## The Recursive Application

**This contract can generate itself.**

If sufficient atoms exist about GENERATIVE_PRIMITIVE:
- WHAT: It generates primitives from atoms
- WHY: Patterns + knowledge = automation
- HOW: Accumulate → Check → Apply → Register
- WHERE: `docs/primitive/contracts/GENERATIVE_PRIMITIVE.md`
- WHEN: When atoms are sufficient
- WHO: Claude (generator), Jeremy (validator)

→ The primitive series for GENERATIVE_PRIMITIVE can be generated.

---

## The Loop

```
Manual primitive creation
    │
    ↓ Extract knowledge atoms
    │
Atoms in knowledge_atoms table
    │
    ↓ Imagine new primitive
    │
Sufficient atoms?
    ├── No → Continue accumulating
    └── Yes → Generate primitive
            │
            ↓ New primitive exists
            │
            ↓ Extract atoms from new primitive
            │
            └── Loop continues
```

**The system learns to build itself.**

---

## Definition of Done

### Phase 1: Conceptual
- [x] Pattern contract defined
- [x] Atom-to-document mapping specified
- [ ] Sufficiency criteria validated

### Phase 2: Implementation
- [ ] `is_generatable()` function implemented
- [ ] `generate_primitive()` function implemented
- [ ] Integration with knowledge_atoms table

### Phase 3: Validation
- [ ] Successfully generate one primitive from atoms
- [ ] Generated primitive passes DOD
- [ ] Atoms extracted from generated primitive

---

## Related

- [PRIMITIVE_SERIES_TEMPLATE.md](PRIMITIVE_SERIES_TEMPLATE.md) - The pattern applied
- [SYSTEM_FOLDER_PATTERN.md](SYSTEM_FOLDER_PATTERN.md) - Directory structure
- [FILE_TO_ATOM_LINEAGE.md](FILE_TO_ATOM_LINEAGE.md) - Traceability
- [THE_SUBSTRATE.md](THE_SUBSTRATE.md) - Where primitives attach

---

**Sufficient knowledge + Universal patterns = Automatic generation. The system builds itself.**
