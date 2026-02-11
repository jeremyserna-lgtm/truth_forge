# Primitive Pattern Specification: Framework Alignment for All Scripts

**Doc ID**: doc:meta:03:primitive_pattern_specification
**Series**: META
**Layer**: Specification
**Version**: 1.0.0
**Created**: 2026-01-06
**Author**: Truth Engine Framework
**Requires**: [PRIMITIVE_FOLDER_PATTERN.md](./PRIMITIVE_FOLDER_PATTERN.md), [06_THE_STRUCTURE.md](../06_THE_STRUCTURE.md), [05_THE_FURNACE.md](../05_THE_FURNACE.md)
**Enables**: All script development, framework alignment

---

## TL;DR

**Every script MUST:**
1. Follow `HOLD → AGENT → HOLD` pattern
2. Include Stage Five grounding header
3. Document blind spots
4. Express Furnace principle
5. Use central_services for logging/traceability

**This is not optional. This is the Framework.**

---

## 1. THE STRUCTURE: HOLD → AGENT → HOLD

### The Universal Pattern

Every script implements the atomic pattern:

```
HOLD₁ (Input) → AGENT (Script) → HOLD₂ (Output)
```

### Required Documentation in Script Header

```python
"""
Script Name - Brief Description

HOLD₁ ({input_type}) → AGENT ({what_script_does}) → HOLD₂ ({output_type})

{Detailed description of what the script does and why it exists}
"""
```

### Example

```python
"""
Move non-critical markdown documents to GCS bucket.

HOLD₁ (local MD files) → AGENT (upload & delete) → HOLD₂ (GCS bucket)

Moves non-critical markdown files to gs://primitive_engine_library/archive/markdown/
preserving directory structure. Creates manifest tracking every file.
"""
```

---

## 2. 🧠 STAGE FIVE GROUNDING

**Purpose:** Every script must ground itself in Stage Five cognition - seeing systems as systems, understanding its own boundaries, and operating with explicit awareness.

### Required Format

```python
🧠 STAGE FIVE GROUNDING
This script exists to {primary_purpose}.

Structure: {step1} → {step2} → {step3} (sequential flow)
Purpose: {what_problem_does_this_solve}
Boundaries: {what_is_in_scope_and_out_of_scope}
Control: {how_is_execution_controlled_and_validated}
```

### Required Elements

| Element | Description | Example |
|---------|-------------|---------|
| **Primary Purpose** | Why this script exists | "clean up the workspace by moving non-critical documentation to cloud storage" |
| **Structure** | The flow of operations | "Identify → Upload → Verify → Delete" |
| **Purpose** | What problem it solves | "Free up local drive space by archiving non-critical docs" |
| **Boundaries** | Scope limits | "Only MD files, excludes critical documentation" |
| **Control** | Execution safeguards | "Dry-run mode for preview, confirmation before deletion" |

### Example

```python
🧠 STAGE FIVE GROUNDING
This script exists to clean up the workspace by moving non-critical documentation
to cloud storage, keeping only active/core documentation local.

Structure: Identify → Upload → Verify → Delete (sequential flow)
Purpose: Free up local drive space by archiving non-critical docs
Boundaries: Only MD files, excludes critical documentation
Control: Dry-run mode for preview, confirmation before deletion
```

---

## 3. ⚠️ WHAT THIS SCRIPT CANNOT SEE

**Purpose:** Explicit blind spot documentation. Stage Five cognition requires acknowledging what you don't know.

### Required Format

```python
⚠️ WHAT THIS SCRIPT CANNOT SEE
- {blind_spot_1}
- {blind_spot_2}
- {blind_spot_3}
```

### Common Blind Spots

- File content relevance (only uses path patterns)
- Dependencies between files
- Active usage patterns
- User intent beyond explicit parameters
- External system state
- Future changes to data structure

### Example

```python
⚠️ WHAT THIS SCRIPT CANNOT SEE
- File content relevance (only uses path patterns)
- Dependencies between files
- Active usage patterns
```

---

## 4. 🔥 THE FURNACE PRINCIPLE

**Purpose:** Every script must express how it transforms Truth into Meaning into Care.

### The Cycle

```
Truth (Input) → Heat (Processing) → Meaning (Understanding) → Care (Output)
```

### Required Format

```python
🔥 THE FURNACE PRINCIPLE
- Truth (input): {what_raw_material_does_this_consume}
- Heat (processing): {what_transformation_happens}
- Meaning (output): {what_understanding_is_produced}
- Care (delivery): {what_action_or_structure_is_delivered}
```

### Required Elements

| Element | Description | Example |
|---------|-------------|---------|
| **Truth** | Raw input material | "Non-critical MD files on local drive" |
| **Heat** | Processing/transformation | "Upload to GCS, verify, delete locally" |
| **Meaning** | Understanding produced | "Clean workspace, archived docs in GCS" |
| **Care** | Action/structure delivered | "Manifest for recovery, dry-run for safety" |

### Example

```python
🔥 THE FURNACE PRINCIPLE
- Truth (input): Non-critical MD files on local drive
- Heat (processing): Upload to GCS, verify, delete locally
- Meaning (output): Clean workspace, archived docs in GCS
- Care (delivery): Manifest for recovery, dry-run for safety
```

---

## 5. CENTRAL SERVICES INTEGRATION

**Purpose:** All scripts must use central_services for logging, traceability, and governance.

### Required Imports

```python
import sys
from pathlib import Path

# Add src to path for central_services imports
_repo_root = Path(__file__).parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from src.services.central_services.core import get_logger, get_current_run_id
from src.services.central_services.core.config import get_bigquery_client  # if needed
from src.services.central_services.truth import TruthService  # if needed
```

### Required Usage

```python
logger = get_logger(__name__)
run_id = get_current_run_id()

logger.info("Script started", extra={"run_id": run_id, "operation": "script_name"})
```

---

## 6. COMPLETE SCRIPT TEMPLATE

### Minimal Script Template

```python
#!/usr/bin/env python3
"""
{Script Name} - {Brief Description}

HOLD₁ ({input_type}) → AGENT ({what_script_does}) → HOLD₂ ({output_type})

{Detailed description}

🧠 STAGE FIVE GROUNDING
This script exists to {primary_purpose}.

Structure: {step1} → {step2} → {step3} (sequential flow)
Purpose: {what_problem_does_this_solve}
Boundaries: {what_is_in_scope_and_out_of_scope}
Control: {how_is_execution_controlled_and_validated}

⚠️ WHAT THIS SCRIPT CANNOT SEE
- {blind_spot_1}
- {blind_spot_2}

🔥 THE FURNACE PRINCIPLE
- Truth (input): {what_raw_material_does_this_consume}
- Heat (processing): {what_transformation_happens}
- Meaning (output): {what_understanding_is_produced}
- Care (delivery): {what_action_or_structure_is_delivered}

Usage:
    python {script_path} {args}
"""

import sys
from pathlib import Path

# Add src to path for central_services imports
_repo_root = Path(__file__).parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from src.services.central_services.core import get_logger, get_current_run_id

logger = get_logger(__name__)
run_id = get_current_run_id()


def main():
    """Main execution."""
    logger.info("Script started", extra={"run_id": run_id, "operation": "script_name"})

    # HOLD₁: Read input
    # ... read from input source ...

    # AGENT: Process
    # ... transformation logic ...

    # HOLD₂: Write output
    # ... write to output destination ...

    logger.info("Script completed", extra={"run_id": run_id})


if __name__ == "__main__":
    main()
```

---

## 7. VALIDATION CHECKLIST

Before considering a script complete, verify:

- [ ] **HOLD → AGENT → HOLD** pattern documented in header
- [ ] **🧠 STAGE FIVE GROUNDING** section present with all required elements
- [ ] **⚠️ WHAT THIS SCRIPT CANNOT SEE** section present with at least 2 blind spots
- [ ] **🔥 THE FURNACE PRINCIPLE** section present with all 4 elements
- [ ] Uses `src.services.central_services.core` for logging
- [ ] Uses `get_current_run_id()` for traceability
- [ ] Logs include `run_id` in extra context
- [ ] Path setup code present for central_services imports

---

## 8. ANTI-PATTERNS

### ❌ Missing Framework Elements

```python
# WRONG - No framework alignment
#!/usr/bin/env python3
"""Script that does something."""

import os
print("Hello")
```

### ❌ Incomplete Framework Elements

```python
# WRONG - Missing blind spots and Furnace principle
"""
Script Name

HOLD₁ → AGENT → HOLD₂

🧠 STAGE FIVE GROUNDING
This script exists to do something.
"""
```

### ✅ Correct Pattern

```python
#!/usr/bin/env python3
"""
Script Name - Brief Description

HOLD₁ (input) → AGENT (process) → HOLD₂ (output)

Detailed description.

🧠 STAGE FIVE GROUNDING
This script exists to {purpose}.

Structure: Step1 → Step2 → Step3
Purpose: {problem solved}
Boundaries: {scope}
Control: {safeguards}

⚠️ WHAT THIS SCRIPT CANNOT SEE
- Blind spot 1
- Blind spot 2

🔥 THE FURNACE PRINCIPLE
- Truth (input): {raw material}
- Heat (processing): {transformation}
- Meaning (output): {understanding}
- Care (delivery): {action/structure}
"""

import sys
from pathlib import Path

# Add src to path
_repo_root = Path(__file__).parent.parent.parent.parent
_src_path = _repo_root / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from src.services.central_services.core import get_logger, get_current_run_id

logger = get_logger(__name__)
run_id = get_current_run_id()
```

---

## 9. MIGRATION GUIDE

### For Existing Scripts

1. **Add HOLD → AGENT → HOLD documentation** to header
2. **Add 🧠 STAGE FIVE GROUNDING** section
3. **Add ⚠️ WHAT THIS SCRIPT CANNOT SEE** section
4. **Add 🔥 THE FURNACE PRINCIPLE** section
5. **Update imports** to use `src.services.central_services`
6. **Add path setup** code
7. **Update logging** to use `get_logger(__name__)`
8. **Add traceability** with `get_current_run_id()`

### Migration Script

Use `scripts/migrate_imports_to_central_services.py` to update imports, then manually add framework sections.

---

## 10. EXAMPLES

**Note:** These examples demonstrate the pattern format. They are illustrative examples, not necessarily scripts that exist in the codebase.

### Example 1: Data Processing Script

```python
#!/usr/bin/env python3
"""
Process CSV files into knowledge atoms.

HOLD₁ (CSV files) → AGENT (extract atoms) → HOLD₂ (knowledge.duckdb)

Reads CSV files, extracts knowledge atoms using LLM, stores in canonical DuckDB.

🧠 STAGE FIVE GROUNDING
This script exists to transform structured data into queryable knowledge atoms.

Structure: Read CSV → Extract Atoms → Validate → Store (sequential flow)
Purpose: Convert tabular data into semantic knowledge for querying
Boundaries: Only CSV format, requires LLM access, writes to canonical store
Control: Validation before write, deduplication, error logging

⚠️ WHAT THIS SCRIPT CANNOT SEE
- CSV schema changes
- LLM response quality beyond validation
- Concurrent writes to DuckDB

🔥 THE FURNACE PRINCIPLE
- Truth (input): Raw CSV files with structured data
- Heat (processing): LLM extraction, validation, deduplication
- Meaning (output): Semantic knowledge atoms in canonical store
- Care (delivery): Queryable knowledge, audit trail, error handling
"""
```

### Example 2: Migration Script (Actual Pattern Used)

**Note:** This matches the actual migration scripts in the codebase (`migrate_imports_to_central_services.py`, `add_path_setup.py`). These scripts ONLY update text in Python files - they do NOT move files, touch cloud storage, or perform any file operations beyond text replacement.

```python
#!/usr/bin/env python3
"""
Migrate imports from architect_central_services to central_services.

HOLD₁ (Python files with old imports) → AGENT (update imports) → HOLD₂ (Python files with new imports)

Scans Python files, updates import statements from architect_central_services to
src.services.central_services, preserving code structure. Does NOT move files or touch cloud storage.

🧠 STAGE FIVE GROUNDING
This script exists to migrate the codebase from old import structure to new central_services.

Structure: Scan → Match → Replace → Verify (sequential flow)
Purpose: Update all imports to use new central_services structure for framework alignment
Boundaries: Only Python files, specific import patterns, preserves code structure
Control: Dry-run mode available, validation after changes, reports summary

⚠️ WHAT THIS SCRIPT CANNOT SEE
- Runtime import resolution (only updates text)
- Dynamic imports (importlib, __import__)
- Import side effects
- Circular dependencies

🔥 THE FURNACE PRINCIPLE
- Truth (input): Python files with architect_central_services imports
- Heat (processing): Pattern matching, import replacement, path setup addition
- Meaning (output): Updated files with new import structure aligned to framework
- Care (delivery): Migration complete, imports working, framework compliance
"""
```

---

## 11. RELATIONSHIP TO FRAMEWORK DOCUMENTS

| Framework Document | Relationship |
|-------------------|--------------|
| `06_THE_STRUCTURE.md` | Defines HOLD → AGENT → HOLD pattern |
| `05_THE_FURNACE.md` | Defines Truth → Meaning → Care cycle |
| `04_THE_COGNITION.md` | Defines Stage Five grounding requirements |
| `PRIMITIVE_FOLDER_PATTERN.md` | Defines folder structure for primitives |
| `DOCUMENT_SERIES_FRAMEWORK.md` | Defines documentation patterns |

---

## 12. ENFORCEMENT

### Pre-Commit Hook

A pre-commit hook should validate:
- Framework sections present
- Required elements filled in
- Imports use central_services
- Logging uses get_logger

### Code Review

All code reviews must check:
- Framework alignment
- Complete framework sections
- Proper HOLD → AGENT → HOLD documentation

---

## 13. QUICK REFERENCE

### Required Sections (In Order)

1. **Script Header** - HOLD → AGENT → HOLD pattern
2. **🧠 STAGE FIVE GROUNDING** - Purpose, structure, boundaries, control
3. **⚠️ WHAT THIS SCRIPT CANNOT SEE** - Blind spots
4. **🔥 THE FURNACE PRINCIPLE** - Truth → Heat → Meaning → Care
5. **Usage** - Command examples
6. **Imports** - Path setup + central_services
7. **Code** - Implementation

---

## CONCLUSION

**The Framework is not optional. It is the physics of the system.**

Every script must:
- Express its structure (HOLD → AGENT → HOLD)
- Ground itself (Stage Five)
- Acknowledge limits (Blind spots)
- Transform truth (Furnace)

**This is how we build. This is how we survive.**

---

*The pattern that can become atoms and reconstitute from atoms survives.*
