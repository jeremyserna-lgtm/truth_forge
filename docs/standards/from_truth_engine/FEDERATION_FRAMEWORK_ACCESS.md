---
title: "Federation Framework Access"
description: "How daughter organisms access THE FRAMEWORK and STANDARDS from Genesis"
version: "1.0.0"
status: "published"
last_updated: "2026-01-22"
author: "Genesis"
tags:
  - federation
  - framework
  - standards
  - governance
category: "Standards"
---

# Federation Framework Access

**The Essence** | THE FRAMEWORK and STANDARDS live in Genesis. Daughters access, not copy.

**Authority**: [07_STANDARDS.md](../07_STANDARDS.md) | **Status**: CANONICAL

---

## Overview

THE FRAMEWORK and STANDARDS are **single-source-of-truth** documents maintained in Truth Engine (Genesis). Daughter organisms (Credential Atlas, Primitive Engine, future organisms) **access** these centrally - they do NOT maintain local copies.

**Key Principles**:
- **Single Source**: Framework lives only in Truth Engine
- **No Duplication**: Daughters reference, not copy
- **Central Enforcement**: Standards enforced from Genesis
- **Version Control**: All organisms on same framework version
- **Evolution**: Framework evolves in Genesis, propagates to all

---

## The Architecture

```
TRUTH ENGINE (Genesis)
├── framework/                    # THE FRAMEWORK (canonical)
│   ├── 00_GENESIS.md            # Philosophical foundation
│   ├── 01_IDENTITY.md
│   ├── 02_PERCEPTION.md
│   ├── 03_METABOLISM.md
│   ├── 04_ARCHITECTURE.md
│   ├── 05_EXTENSION.md
│   ├── 06_LAW.md               # Inviolable laws
│   ├── 07_STANDARDS.md         # Standards authority
│   └── standards/              # ALL STANDARDS
│       ├── INDEX.md            # Standards registry
│       ├── API_DESIGN.md
│       ├── CONFIGURATION.md
│       ├── ... (26+ standards)
│       └── archive/
│
├── DAUGHTERS ACCESS VIA:
│   ├── Symlinks (preferred for local dev)
│   ├── Federation API (runtime)
│   └── Reference documents (documentation)

CREDENTIAL ATLAS (Daughter)
├── .federation/
│   └── FRAMEWORK_REF.md        # Points to Genesis
├── docs/
│   └── ... (CA-specific docs)
└── NO framework/ DIRECTORY     # Does not duplicate

PRIMITIVE ENGINE (Daughter)
├── .federation/
│   └── FRAMEWORK_REF.md        # Points to Genesis
└── NO framework/ DIRECTORY     # Does not duplicate
```

---

## Access Methods

### Method 1: Symlinks (Local Development)

For local development where organisms are on the same machine:

```bash
# In daughter organism root
ln -s /Users/jeremyserna/Truth_Engine/framework framework

# Or for just standards
ln -s /Users/jeremyserna/Truth_Engine/framework/standards framework_standards
```

**Pros**: Always current, no sync needed
**Cons**: Only works locally, not in deployed environments

### Method 2: Federation Reference Document

Every daughter has `.federation/FRAMEWORK_REF.md`:

```markdown
# Framework Reference

This organism follows THE FRAMEWORK maintained in Genesis (Truth Engine).

**Framework Location**: `/Users/jeremyserna/Truth_Engine/framework/`
**Standards Location**: `/Users/jeremyserna/Truth_Engine/framework/standards/`

## Quick Links

- [00_GENESIS.md](/Users/jeremyserna/Truth_Engine/framework/00_GENESIS.md)
- [06_LAW.md](/Users/jeremyserna/Truth_Engine/framework/06_LAW.md)
- [07_STANDARDS.md](/Users/jeremyserna/Truth_Engine/framework/07_STANDARDS.md)
- [Standards INDEX](/Users/jeremyserna/Truth_Engine/framework/standards/INDEX.md)

## Why No Local Copy

THE FRAMEWORK is single-source-of-truth. Maintaining copies creates:
- Version drift
- Conflicting standards
- Update burden
- Confusion about canonical source

Daughters ACCESS, not COPY.
```

### Method 3: Federation API (Runtime)

For deployed organisms, access via Federation API:

```python
from primitive.federation import get_framework_document, get_standard

# Get framework document
genesis_doc = get_framework_document("00_GENESIS.md")

# Get specific standard
api_standard = get_standard("API_DESIGN.md")

# Get all standards
standards = get_all_standards()
```

### Method 4: Copy on Deployment (Immutable)

For deployed organisms that need offline access:

```bash
# During deployment
cp -r /Truth_Engine/framework/ /deployed_organism/.framework_snapshot/

# Mark as immutable snapshot
echo "SNAPSHOT: 2026-01-22T15:00:00Z" > /deployed_organism/.framework_snapshot/VERSION
```

**Rules**:
- Snapshot is READ-ONLY
- Organism must update from Genesis on next deployment
- No local modifications allowed

---

## What Daughters CAN Have

### Daughter-Specific Documents

Daughters can have their own documentation that:
- **Extends** the framework for their domain
- **Applies** standards to their specific context
- **Documents** their unique capabilities

**Location**: `docs/` (not `framework/`)

### Example: Credential Atlas

```
credential_atlas/
├── .federation/
│   └── FRAMEWORK_REF.md          # Points to Genesis
├── docs/
│   ├── seeing/                   # CA-specific seeing docs
│   │   ├── HOW_WE_SEE_ORGANIZATIONS.md
│   │   ├── THE_SEEING_PROCESS.md
│   │   └── THE_UNIFIED_SEEING_FRAMEWORK.md
│   ├── assessments/              # CA-specific assessments
│   └── nursery/                  # CA-specific nursery docs
└── NO framework/ directory
```

---

## What Daughters CANNOT Have

### Duplicate Framework

**NEVER**:
```
daughter_organism/
├── framework/                    # NO - DUPLICATE
│   ├── 00_GENESIS.md            # WRONG
│   └── standards/               # WRONG
```

### Local Standards Overrides

**NEVER**:
```
daughter_organism/
├── standards/                    # NO - Standards live in Genesis
│   └── API_DESIGN_LOCAL.md      # WRONG
```

### Modified Framework Copies

**NEVER**:
```
daughter_organism/
├── framework/
│   └── 00_GENESIS.md            # Modified copy - FORBIDDEN
```

---

## Enforcement

### Pre-Commit Hook

```python
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: no-framework-copies
      name: No Framework Copies
      entry: python -c "
import os
import sys
if os.path.exists('framework/') and 'Truth_Engine' not in os.getcwd():
    print('ERROR: Daughter organisms cannot have framework/ directory')
    print('THE FRAMEWORK lives in Truth Engine only')
    sys.exit(1)
"
      language: python
      always_run: true
```

### Validation Script

```python
# validate_federation_access.py
def validate_daughter_organism(path):
    errors = []

    # Check no framework/ directory
    if os.path.exists(os.path.join(path, 'framework')):
        if 'Truth_Engine' not in path:
            errors.append("framework/ directory exists - must be removed")

    # Check .federation/FRAMEWORK_REF.md exists
    ref_path = os.path.join(path, '.federation', 'FRAMEWORK_REF.md')
    if not os.path.exists(ref_path):
        errors.append(".federation/FRAMEWORK_REF.md missing")

    return errors
```

---

## Migration Guide

### For Existing Daughters

1. **Remove duplicate framework/**
   ```bash
   rm -rf daughter_organism/framework/
   ```

2. **Create .federation/ directory**
   ```bash
   mkdir -p daughter_organism/.federation/
   ```

3. **Create FRAMEWORK_REF.md**
   ```bash
   # See template below
   ```

4. **Update any local references**
   - Change `../framework/` to `Truth_Engine/framework/`
   - Update imports to use federation access

5. **Verify no broken links**
   ```bash
   grep -r "framework/" daughter_organism/docs/
   # Fix any references to local framework/
   ```

---

## FRAMEWORK_REF.md Template

```markdown
# Framework Reference - {ORGANISM_NAME}

**This organism follows THE FRAMEWORK maintained in Genesis (Truth Engine).**

---

## Framework Location

| Resource | Path |
|----------|------|
| THE FRAMEWORK | `/Users/jeremyserna/Truth_Engine/framework/` |
| Standards | `/Users/jeremyserna/Truth_Engine/framework/standards/` |
| Standards Index | `/Users/jeremyserna/Truth_Engine/framework/standards/INDEX.md` |

---

## Core Documents

| Document | Purpose |
|----------|---------|
| [00_GENESIS.md](../Truth_Engine/framework/00_GENESIS.md) | Philosophical foundation |
| [06_LAW.md](../Truth_Engine/framework/06_LAW.md) | Inviolable laws |
| [07_STANDARDS.md](../Truth_Engine/framework/07_STANDARDS.md) | Standards authority |

---

## Why This Reference Exists

THE FRAMEWORK is single-source-of-truth, maintained only in Truth Engine.

**This organism does NOT maintain local copies because:**
- Version drift creates confusion
- Conflicting standards break the federation
- Central updates must propagate automatically
- Genesis is the authority

---

## How to Access Framework

### Local Development
```bash
# Symlink if needed
ln -s /Users/jeremyserna/Truth_Engine/framework framework_link
```

### In Code
```python
from primitive.federation import get_standard
standard = get_standard("API_DESIGN.md")
```

---

## Daughter-Specific Documentation

This organism's specific documentation lives in `docs/`, not `framework/`.

Daughter documentation can:
- Extend framework concepts for this domain
- Apply standards to specific contexts
- Document unique capabilities

Daughter documentation CANNOT:
- Override framework definitions
- Create local standards
- Duplicate Genesis content

---

*{ORGANISM_NAME} is a daughter of Truth Engine. THE FRAMEWORK flows from Genesis.*
```

---

## Version Control

### Framework Versioning

THE FRAMEWORK is versioned in Genesis:

```yaml
# Truth_Engine/framework/VERSION.yaml
framework_version: "2.0.0"
standards_version: "1.0.0"
last_updated: "2026-01-22"
breaking_changes_since: "2.0.0"
```

### Daughter Compatibility

Daughters declare framework compatibility:

```yaml
# daughter_organism/.federation/compatibility.yaml
requires_framework_version: ">=2.0.0"
requires_standards_version: ">=1.0.0"
last_verified: "2026-01-22"
```

---

## Related Documents

- [FEDERATION_DOCUMENT_STANDARD.md](FEDERATION_DOCUMENT_STANDARD.md) - Document format
- [FEDERATION_FOLDER_STRUCTURE.md](FEDERATION_FOLDER_STRUCTURE.md) - Folder organization
- [07_STANDARDS.md](../07_STANDARDS.md) - Standards authority

---

## The Principle

> **One framework. One source. Many organisms. No copies.**

THE FRAMEWORK is the philosophical and technical foundation of the federation. It lives in Genesis. Daughters access it. They do not duplicate it. This ensures coherence across all organisms.

---

*~350 lines. Federation framework access standard. Complete.*
