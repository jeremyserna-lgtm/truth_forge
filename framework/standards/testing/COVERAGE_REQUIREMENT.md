# Test Coverage Requirement — Non-Negotiable Standard

**The Standard** | 90% test coverage is MANDATORY. Zero exceptions. Zero excuses. Zero dishonesty.

**Authority**: [07_STANDARDS.md](../../07_STANDARDS.md) | **Status**: CANONICAL | **Enforcement**: BLOCKING

---

## THIS IS THE LAW

```
         ┌───────────────────────────────────────┐
         │   COVERAGE_REQUIREMENT.md             │
         │   THE ABSOLUTE MINIMUM                 │
         └─────────────────┬─────────────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
  [90% MINIMUM]    [ALL BLOCKERS FIXED]  [NO EXCEPTIONS]
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                   [VERIFICATION]
```

---

## The Requirement

### 90% Coverage — MANDATORY

**Every codebase MUST achieve 90% test coverage. This is non-negotiable.**

| Component | Minimum Coverage | Critical Paths |
|-----------|------------------|---------------|
| **All Code** | **90%** | **100%** |
| Business Logic | 90% | 100% |
| Error Handling | 90% | 100% |
| Public APIs | 90% | 100% |
| Data Transformations | 90% | 100% |
| Pipeline Stages | 90% | 100% |

**There are NO exceptions. There are NO excuses. There is NO "good enough".**

---

## What "90% Coverage" Means

### Line Coverage

Every line of code must be executed by tests, with exceptions only for:
- `if __name__ == "__main__":` blocks (excluded automatically)
- Type checking imports (`if TYPE_CHECKING:`)
- Debug-only code (must be marked `# pragma: no cover` with justification)

### Branch Coverage

Every code path must be tested:
- All `if/elif/else` branches
- All `try/except` blocks
- All `for/while` loop conditions
- All early returns

### Function Coverage

Every function must be called by tests:
- Public functions: 100% coverage
- Private functions: 90% coverage (via public interface or direct tests)
- Error handlers: 100% coverage

---

## The Blocker Removal Requirement

### ALL Blockers Must Be Fixed

**If tests cannot run, the code is NOT DONE. Period.**

Common blockers that MUST be fixed:

1. **Import Errors**
   - ❌ `ModuleNotFoundError`
   - ❌ `ImportError`
   - ❌ `AttributeError` on import
   - ✅ **FIXED**: All imports work correctly

2. **Missing Dependencies**
   - ❌ Missing test fixtures
   - ❌ Missing mock objects
   - ❌ Missing test data
   - ✅ **FIXED**: All dependencies available

3. **Path Issues**
   - ❌ `sys.path` not configured
   - ❌ Relative imports failing
   - ❌ Module resolution errors
   - ✅ **FIXED**: All paths resolve correctly

4. **Configuration Issues**
   - ❌ Missing environment variables
   - ❌ Missing config files
   - ❌ Missing credentials
   - ✅ **FIXED**: All config available (mocked if needed)

5. **Test Infrastructure**
   - ❌ pytest not configured
   - ❌ Coverage tool not configured
   - ❌ Test discovery failing
   - ✅ **FIXED**: All infrastructure working

**If ANY blocker exists, the code is NOT COMPLETE. Fix it. No excuses.**

---

## Verification Commands

### Must Pass Before "Done"

```bash
# 1. Verify tests can be collected (no import errors)
pytest --collect-only pipelines/adapters/claude_code/scripts/

# 2. Verify all tests pass
pytest pipelines/adapters/claude_code/scripts/ -v

# 3. Verify 90% coverage
pytest pipelines/adapters/claude_code/scripts/ \
  --cov=pipelines/adapters/claude_code/scripts \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-fail-under=90

# 4. Verify no blockers
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('pipelines/adapters/claude_code/scripts').resolve()))
try:
    from shared import PIPELINE_NAME
    print('✅ Imports work')
except Exception as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
```

**ALL of these MUST pass. If any fail, you are NOT done.**

---

## The Dishonesty Standard

### What Constitutes Dishonesty

**Dishonesty is claiming "done" when:**

1. ❌ Tests cannot run (import errors, missing dependencies)
2. ❌ Coverage is below 90%
3. ❌ Blockers exist that prevent testing
4. ❌ Critical paths are untested
5. ❌ Error handling is untested
6. ❌ Edge cases are untested
7. ❌ Tests exist but don't actually verify behavior

### The Honesty Standard

**Honesty requires:**

1. ✅ All tests can run without errors
2. ✅ Coverage is 90% or higher
3. ✅ All blockers are fixed
4. ✅ Critical paths are 100% covered
5. ✅ Error handling is 100% covered
6. ✅ Edge cases are tested
7. ✅ Tests actually verify correct behavior

**If you claim "done" without meeting these requirements, you are being dishonest.**

---

## Enforcement

### CI/CD Gates

```yaml
# .github/workflows/test.yml
- name: Run tests with coverage
  run: |
    pytest pipelines/adapters/claude_code/scripts/ \
      --cov=pipelines/adapters/claude_code/scripts \
      --cov-fail-under=90 \
      --cov-report=xml
```

**PRs that don't meet 90% coverage are BLOCKED.**

### Pre-Commit Hooks

```bash
#!/bin/bash
# .git/hooks/pre-commit
pytest pipelines/adapters/claude_code/scripts/ \
  --cov=pipelines/adapters/claude_code/scripts \
  --cov-fail-under=90 \
  --quiet || {
  echo "❌ Coverage below 90%. Commit blocked."
  exit 1
}
```

**Commits that don't meet 90% coverage are BLOCKED.**

### Manual Verification

Before claiming "done", run:

```bash
# This MUST pass
.venv/bin/pytest pipelines/adapters/claude_code/scripts/ \
  --cov=pipelines/adapters/claude_code/scripts \
  --cov-fail-under=90 \
  --cov-report=term-missing
```

**If it doesn't pass, you are NOT done.**

---

## Configuration

### pyproject.toml

```toml
[tool.coverage.run]
source = ["pipelines/adapters/claude_code/scripts"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/migrations/*",
    "*/_deprecated/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]
fail_under = 90
precision = 2
show_missing = true
skip_covered = false

[tool.coverage.html]
directory = "htmlcov"
```

### pytest.ini

```ini
[pytest]
testpaths = pipelines/adapters/claude_code/scripts
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=pipelines/adapters/claude_code/scripts
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=90
    -v
```

---

## What Gets Excluded

### Automatic Exclusions

- `if __name__ == "__main__":` blocks
- `if TYPE_CHECKING:` blocks
- `def __repr__():` methods
- `raise NotImplementedError` lines

### Manual Exclusions (Require Justification)

```python
# pragma: no cover - Legacy code, tracked in ISSUE-123
def legacy_function():
    ...

# pragma: no cover - Debug only, never called in production
def debug_helper():
    ...
```

**Every exclusion MUST have a justification. No silent exclusions.**

---

## The False Done Problem

### The Problem

```bash
# WRONG: This passes even if no tests exist!
pytest pipelines/adapters/claude_code/scripts/
# Result: PASSED (0 tests) ← FALSE POSITIVE!

# WRONG: This passes even if coverage is 0%!
pytest --cov=pipelines/adapters/claude_code/scripts/
# Result: Coverage: 0% ← FALSE POSITIVE!
```

### The Solution

```bash
# CORRECT: Verify tests exist first
test_count=$(find pipelines/adapters/claude_code/scripts/ -name "test_*.py" | wc -l)
if [ "$test_count" -eq 0 ]; then
    echo "❌ FAIL: No tests exist"
    exit 1
fi

# CORRECT: Verify coverage threshold
pytest pipelines/adapters/claude_code/scripts/ \
  --cov=pipelines/adapters/claude_code/scripts \
  --cov-fail-under=90
# Result: FAILED if coverage < 90% ← CORRECT!
```

**Always verify existence before checking passing.**

---

## Coverage Reports

### Required Reports

1. **Terminal Report** (for CI/CD)
   ```bash
   pytest --cov=... --cov-report=term-missing
   ```

2. **HTML Report** (for developers)
   ```bash
   pytest --cov=... --cov-report=html
   open htmlcov/index.html
   ```

3. **XML Report** (for CI/CD integration)
   ```bash
   pytest --cov=... --cov-report=xml
   ```

### Report Requirements

- Show missing lines
- Show branch coverage
- Show function coverage
- Identify untested code paths
- Highlight critical paths below 100%

---

## The Standard Applied

### For Pipeline Code

**Every pipeline stage MUST have:**

1. ✅ Unit tests for all functions
2. ✅ Integration tests for stage execution
3. ✅ Error handling tests
4. ✅ Edge case tests
5. ✅ 90% minimum coverage
6. ✅ 100% coverage for critical paths

### For Shared Utilities

**Every utility function MUST have:**

1. ✅ Unit tests
2. ✅ Error handling tests
3. ✅ Edge case tests
4. ✅ 90% minimum coverage

### For Test Infrastructure

**Test infrastructure itself MUST:**

1. ✅ Work without errors
2. ✅ Be documented
3. ✅ Be maintainable
4. ✅ Not be a blocker

---

## Escalation Path

### If Coverage Cannot Be Achieved

**There is NO escalation path. Fix the code.**

If you cannot achieve 90% coverage, the problem is:

1. ❌ Code is too complex → Refactor
2. ❌ Code is untestable → Redesign
3. ❌ Tests are missing → Write them
4. ❌ Blockers exist → Fix them

**There is NO "good enough". There is NO "later". There is NO exception.**

---

## Pattern Coverage

### ME:NOT-ME

| Aspect | ME (Human) | NOT-ME (AI) |
|--------|------------|-------------|
| **Writing tests** | Understands intent | Generates comprehensive coverage |
| **Reading coverage** | Sees gaps | Identifies untested paths |
| **Fixing gaps** | Prioritizes critical paths | Covers all paths |

### HOLD:AGENT:HOLD

```
HOLD₁ (Input)           AGENT (Process)           HOLD₂ (Output)
Test input            → Code under test          → Coverage report
Untested code         → Test writing             → 90%+ coverage
```

### TRUTH:MEANING:CARE

| Phase | Application |
|-------|-------------|
| **TRUTH** | Coverage report shows actual coverage |
| **MEANING** | 90% threshold means quality |
| **CARE** | All blockers fixed, all paths tested |

---

## Convergence

### Bottom-Up Validation

This standard requires:
- [STANDARD_CREATION](../STANDARD_CREATION.md) - Template structure
- [STANDARD_COMPLIANCE](../STANDARD_COMPLIANCE.md) - Verification tiers
- [testing/INDEX.md](INDEX.md) - Parent standard

### Top-Down Validation

This standard is shaped by:
- [06_LAW](../../06_LAW.md) - No Magic, Observability pillars
- [03_METABOLISM](../../03_METABOLISM.md) - TRUTH:MEANING:CARE
- [01_IDENTITY](../../01_IDENTITY.md) - ME:NOT-ME honesty

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [testing/INDEX.md](INDEX.md) | Parent standard |
| [code_quality/](../code_quality/) | Tests require typed fixtures |
| [error_handling/](../error_handling/) | Error paths must be tested |
| [planning/](../planning/) | Tests EXIST before claiming done |

---

## Industry Alignment

- [Google Testing Standards](https://testing.googleblog.com/) - 80%+ coverage
- [Microsoft Testing Guidelines](https://docs.microsoft.com/en-us/azure/devops/test/) - Comprehensive testing
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/) - Coverage tooling

**We exceed industry standards with 90% requirement.**

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-01-27 | Created non-negotiable 90% coverage standard | Claude |
| 2026-01-27 | Added blocker removal requirement | Claude |
| 2026-01-27 | Added dishonesty standard | Claude |

---

## The Final Word

**90% coverage is MANDATORY. Zero exceptions. Zero excuses. Zero dishonesty.**

If you claim "done" without 90% coverage and all blockers fixed, you are being dishonest.

**This is the law. Enforce it.**

---

*90% coverage. All blockers fixed. No exceptions. No excuses. No dishonesty.*
