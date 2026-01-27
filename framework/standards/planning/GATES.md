# Gate Verification

**Gates MUST verify EXISTENCE before checking PASSING.**

---

## The Problem

```bash
# WRONG: Only checks passing
pytest tests/ -k "module" --cov-fail-under=90
# If no tests exist, this passes (false positive)

# CORRECT: Checks existence then passing
test_count=$(find tests/ -name "test_*.py" -exec grep -l "module" {} \; | wc -l)
if [ "$test_count" -eq 0 ]; then
    echo "FAIL: No tests exist for module"
    exit 1
fi
echo "✓ Tests exist: $test_count files"
pytest tests/ -k "module" --cov-fail-under=90
```

---

## Gate Definitions

| Artifact | Existence Check | Passing Check |
|----------|-----------------|---------------|
| Tests | Files exist with relevant content | Tests pass with coverage |
| Documentation | File exists, not empty | Content matches spec |
| Data | Records in destination | Records valid and complete |
| Errors | DLQ file exists (if errors occurred) | Errors captured with context |

---

## The Gate Check Box

```
╔══════════════════════════════════════════════════════════════════════╗
║                          🚦 GATE CHECK 🚦                             ║
║   □ Artifacts EXIST (not just steps completed)                        ║
║   □ Tests EXIST (for Creation tasks)                                  ║
║   □ Quality checks pass                                               ║
║   □ Data integrity verified (if applicable)                           ║
║   □ OPERATIONAL (actually works)                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## Verification Script

```bash
#!/bin/bash
# gate-verify.sh - Verify gate completion

set -e

echo "Verifying gate..."

# 1. Check artifact existence
for artifact in "${REQUIRED_ARTIFACTS[@]}"; do
    if [ ! -e "$artifact" ]; then
        echo "FAIL: Missing artifact: $artifact"
        exit 1
    fi
done
echo "✓ All artifacts exist"

# 2. Check test existence (for creation tasks)
test_count=$(find tests/ -name "test_*.py" | wc -l)
if [ "$test_count" -eq 0 ]; then
    echo "FAIL: No tests exist"
    exit 1
fi
echo "✓ Tests exist: $test_count files"

# 3. Run quality checks
.venv/bin/mypy src/ --strict
.venv/bin/ruff check src/
.venv/bin/pytest tests/ -v --cov --cov-fail-under=90

echo "✓ Gate verification complete"
```

---

## Gate Override

When a gate cannot be satisfied:

```markdown
# standard:override planning-gate-G3 - Legacy system incompatible, tracked in ISSUE-456
## Gate G3: Integration test with legacy system

**Override Reason**: Legacy system does not support test environment.

**Mitigations**:
1. Manual verification documented in `docs/legacy-verification.md`
2. Monitoring added for production verification
3. Rollback plan documented in `docs/rollback.md`

**Approval**: [Name], [Date]
```

---

## UP

[planning/INDEX.md](INDEX.md)
