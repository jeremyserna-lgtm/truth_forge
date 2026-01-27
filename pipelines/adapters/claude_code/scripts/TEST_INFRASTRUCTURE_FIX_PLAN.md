# Test Infrastructure Fix Plan — 90% Coverage Requirement

**Date**: 2026-01-27  
**Status**: 🔄 **IN PROGRESS**  
**Requirement**: 90% test coverage, all blockers fixed, zero exceptions

---

## Current Status

### ✅ Completed
1. Created `COVERAGE_REQUIREMENT.md` standard (90% mandatory)
2. Updated `COVERAGE.md` to reflect 90% requirement
3. Updated `testing/INDEX.md` to reference new standard
4. Fixed import errors in `test_id_generation.py`
5. Fixed import errors in `test_pipeline_stages.py`
6. Fixed logging imports in `shared/__init__.py`, `shared/constants.py`, `shared/config.py`, `shared/utilities.py`

### 🔄 In Progress
1. Fixing missing `get_pipeline_hold2_path` function
2. Creating comprehensive test suite
3. Achieving 90% coverage

### ❌ Remaining Blockers

#### Blocker 1: Missing `get_pipeline_hold2_path` Function
**Location**: `test_pipeline_stages.py` line 57  
**Error**: `ImportError: cannot import name 'get_pipeline_hold2_path' from 'shared'`  
**Fix Required**: 
- Add `get_pipeline_hold2_path()` to `shared/utilities.py`
- Export from `shared/__init__.py`

#### Blocker 2: Test Coverage Currently 0%
**Status**: Tests cannot run due to import errors  
**Fix Required**: 
- Fix all import errors
- Create comprehensive test suite
- Achieve 90% coverage

---

## Fix Implementation

### Step 1: Add Missing Function to shared/utilities.py

```python
def get_pipeline_hold2_path(stage: int, pipeline_name: str) -> Path:
    """Get path to pipeline HOLD₂ for a specific stage.
    
    Args:
        stage: Stage number (0-16)
        pipeline_name: Pipeline name (e.g., 'claude_code')
    
    Returns:
        Path to pipeline HOLD₂ JSONL file
    """
    pipeline_dir = Path(__file__).parent.parent.parent
    staging_dir = pipeline_dir / "staging" / "knowledge_atoms" / f"stage_{stage}"
    staging_dir.mkdir(parents=True, exist_ok=True)
    return staging_dir / "hold2.jsonl"
```

### Step 2: Export from shared/__init__.py

Add to exports:
```python
from .utilities import (
    ...,
    get_pipeline_hold2_path,
)
```

### Step 3: Create Comprehensive Test Suite

Need tests for:
- All 17 stage scripts
- All shared utilities
- All error handling paths
- All edge cases
- All data transformations

### Step 4: Verify 90% Coverage

```bash
pytest pipelines/adapters/claude_code/scripts/ \
  --cov=pipelines/adapters/claude_code/scripts \
  --cov-fail-under=90 \
  --cov-report=term-missing
```

---

## Standard Enshrined

✅ **Created**: `framework/standards/testing/COVERAGE_REQUIREMENT.md`

**Key Requirements**:
- 90% coverage is MANDATORY
- All blockers must be fixed
- Zero exceptions
- Zero excuses
- Zero dishonesty

**Enforcement**:
- CI/CD gates
- Pre-commit hooks
- Manual verification required

---

*This plan addresses every layer. No exceptions. No excuses. No dishonesty.*
