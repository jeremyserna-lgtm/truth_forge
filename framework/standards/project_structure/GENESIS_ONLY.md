# Genesis-Only Additions

**What genesis (truth_forge) has that daughters do NOT have.**

---

## The Rule

**Daughters reference genesis via federation. They do NOT duplicate framework/.**

---

## Genesis Structure

Genesis (truth_forge) contains the canonical framework:

```
truth_forge/
├── [all universal folders]
│
└── framework/                # ONLY IN GENESIS
    ├── 00_GENESIS.md         # Theory - axiomatic truths
    ├── 01_IDENTITY.md        # Theory - ME:NOT-ME
    ├── 02_PERCEPTION.md      # Theory - SEE:SEE:DO
    ├── 03_METABOLISM.md      # Theory - TRUTH:MEANING:CARE
    ├── 04_ARCHITECTURE.md    # Theory - HOLD:AGENT:HOLD
    ├── 05_EXTENSION.md       # Theory - The Molt
    ├── 06_LAW.md             # Theory - Inviolable rules
    ├── 07_STANDARDS.md       # Theory - Standards as law
    │
    ├── standards/            # Canonical standards
    │   ├── INDEX.md          # Standards registry
    │   ├── STANDARD_*.md     # Meta-standards
    │   ├── code_quality/
    │   ├── error_handling/
    │   ├── security/
    │   └── ...
    │
    ├── decisions/            # Architecture Decision Records
    │   ├── INDEX.md
    │   └── 0001-*.md
    │
    └── archive/              # Deprecated framework docs
```

---

## Federation

Daughters access genesis via `.seed/`:

```python
# .seed/sync.py
from pathlib import Path

GENESIS_PATH = Path.home() / "truth_forge"
FRAMEWORK_PATH = GENESIS_PATH / "framework"

def get_standard(name: str) -> Path:
    """Get path to canonical standard in genesis."""
    return FRAMEWORK_PATH / "standards" / name / "INDEX.md"
```

---

## What Daughters Have

```
primitive_engine/             # Daughter organism
├── .seed/                    # Federation identity
│   ├── identity.json         # WHO: "primitive_engine"
│   └── sync.py               # Links to genesis
│
├── [universal structure]     # Same as all organisms
│
└── NO framework/             # NEVER duplicate
```

---

## NEVER

```
✗ Put framework/ in daughter organisms
✗ Duplicate standards locally
✗ Create local copies of theory documents
```

## ALWAYS

```
✓ Reference genesis framework via federation
✓ Keep daughters lightweight
✓ Single source of truth in genesis
```

---

## UP

[INDEX.md](INDEX.md)
