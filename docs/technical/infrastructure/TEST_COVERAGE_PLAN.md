# Test Coverage Plan: 95% Target

**Date**: 2026-01-28  
**Current Status**: Claude Code pipeline has extensive tests  
**Target**: 95% coverage across codebase  
**Standard**: 90% minimum (per framework standards), targeting 95%

---

## Current Test Status

### Test Count
- **Total test files**: 108 Python test files
- **Tests collected**: 1,092+ tests
- **Claude Code pipeline**: Extensive test coverage already

### Coverage Status
- **Standard**: 90% minimum (per `framework/standards/testing/COVERAGE.md`)
- **Target**: 95% (user requirement)
- **Current**: Needs measurement

---

## New Code Requiring Tests

### 1. Dataflow Pipeline (`pipelines/adapters/claude_code/dataflow_pipeline.py`)

**Status**: ✅ **Tests Created** (`tests/unit/pipelines/test_dataflow_pipeline.py`)

**Test Coverage**:
- ✅ Multi-source support (all 8 sources)
- ✅ Extract function for each source
- ✅ THE GATE identity generation
- ✅ Gemini Flash Lite spelling correction
- ✅ spaCy sentence segmentation
- ✅ Message entity creation (L5)
- ✅ Conversation entity creation (L8)
- ✅ entity_unified row builder (34 columns)
- ✅ Error handling
- ✅ Integration flow

**Estimated Coverage**: ~85-90% (needs verification)

**Remaining Gaps**:
- Full Beam pipeline execution (requires Beam test framework)
- BigQuery write operations (mocked)
- Error recovery paths

---

## Test Coverage Strategy

### Priority 1: Dataflow Pipeline (NEW CODE)

**File**: `pipelines/adapters/claude_code/dataflow_pipeline.py`  
**Tests**: `tests/unit/pipelines/test_dataflow_pipeline.py`  
**Status**: ✅ Created

**To Verify**:
```bash
.venv/bin/pytest tests/unit/pipelines/test_dataflow_pipeline.py \
  --cov=pipelines/adapters/claude_code/dataflow_pipeline \
  --cov-report=term-missing
```

**Target**: 90%+ coverage

---

### Priority 2: Existing Pipeline Code

**Claude Code Pipeline** (already well-tested):
- Stage scripts (0-16): Extensive tests exist
- Shared modules: 62-92% coverage
- Utility scripts: Need expansion

**Action**: Run coverage report to identify gaps

---

### Priority 3: Core Services

**Files needing tests**:
- `src/truth_forge/services/sync/*.py` - Sync services
- `src/truth_forge/gateway/*.py` - Gateway providers
- `src/truth_forge/core/*.py` - Core utilities

**Action**: Check existing test coverage, add missing tests

---

## Running Coverage Reports

### Full Codebase Coverage

```bash
# Run coverage for entire codebase
.venv/bin/pytest \
  --cov=src \
  --cov=pipelines \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=90

# View HTML report
open htmlcov/index.html
```

### Dataflow Pipeline Coverage

```bash
# Test Dataflow pipeline specifically
.venv/bin/pytest tests/unit/pipelines/test_dataflow_pipeline.py \
  --cov=pipelines/adapters/claude_code/dataflow_pipeline \
  --cov-report=term-missing \
  --cov-fail-under=90
```

### Claude Code Pipeline Coverage

```bash
# Test Claude Code pipeline
.venv/bin/pytest pipelines/adapters/claude_code/scripts/tests/ \
  --cov=pipelines/adapters/claude_code/scripts \
  --cov-report=term-missing \
  --cov-fail-under=90
```

---

## Coverage Targets by Module

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| **Dataflow Pipeline** | ~0% (new) | 95% | 🔴 HIGH |
| **Claude Code Stages** | 5-15% | 95% | 🟡 MEDIUM |
| **Shared Modules** | 62-92% | 95% | 🟢 LOW |
| **Core Services** | Unknown | 95% | 🟡 MEDIUM |
| **Gateway Providers** | Unknown | 95% | 🟡 MEDIUM |

---

## Test Requirements

### For Dataflow Pipeline

**Must Test**:
1. ✅ All 8 sources supported
2. ✅ Extract function for each source
3. ✅ THE GATE identity generation (deterministic)
4. ✅ Gemini Flash Lite spelling correction
   - User messages cleaned
   - Assistant messages passthrough
   - Error handling
5. ✅ spaCy sentence segmentation
6. ✅ L5 message entity creation
7. ✅ L4 sentence entity creation
8. ✅ L8 conversation entity creation
9. ✅ entity_unified row structure (34 columns)
10. ✅ Error handling and edge cases

**Already Covered**: ✅ All above (test file created)

**Needs Verification**: Run coverage report

---

## Next Steps

1. **Run Coverage Report**:
   ```bash
   .venv/bin/pytest tests/unit/pipelines/test_dataflow_pipeline.py \
     --cov=pipelines/adapters/claude_code/dataflow_pipeline \
     --cov-report=term-missing
   ```

2. **Identify Gaps**: Review coverage report for missing lines

3. **Add Missing Tests**: Fill coverage gaps

4. **Verify 95% Target**: Ensure Dataflow pipeline reaches 95%

5. **Expand Other Modules**: Work through remaining modules to reach 95% overall

---

## Test Execution

### Run All Tests

```bash
.venv/bin/pytest tests/ -v
```

### Run with Coverage

```bash
.venv/bin/pytest tests/ \
  --cov=src \
  --cov=pipelines \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=90
```

### Run Specific Test Suite

```bash
# Dataflow pipeline tests
.venv/bin/pytest tests/unit/pipelines/test_dataflow_pipeline.py -v

# Claude Code pipeline tests
.venv/bin/pytest pipelines/adapters/claude_code/scripts/tests/ -v
```

---

**Last Updated**: 2026-01-28  
**Status**: ✅ Dataflow pipeline tests created - needs coverage verification
