# Task Classification

**Every task MUST be classified before planning.**

---

## Classification Types

| Type | Definition | Test Requirement | Example |
|------|------------|------------------|---------|
| **MIGRATION** | Existing code being moved/transformed | Run existing tests | Copy legacy service to new location |
| **CREATION** | New code being written | Write tests THEN run | Build new BaseService class |
| **RESEARCH** | Information gathering only | No code tests | Investigate API options |
| **CONFIGURATION** | Settings/config changes | Validation tests | Update pyproject.toml |

---

## Decision Tree

```python
def classify_task(task: Task) -> TaskType:
    if task.involves_writing_code():
        if task.has_existing_source():
            return TaskType.MIGRATION
        else:
            return TaskType.CREATION
    elif task.involves_code_artifacts():
        return TaskType.CONFIGURATION
    else:
        return TaskType.RESEARCH
```

---

## Why Classification Matters

| Type | Verification Approach |
|------|----------------------|
| MIGRATION | Tests already exist - run them |
| CREATION | Tests DON'T exist - must WRITE them first |
| RESEARCH | No tests needed - findings documented |
| CONFIGURATION | Validation needed - schema/format tests |

**The False Done Problem** occurs when CREATION tasks are verified like MIGRATION tasks:
- Running `pytest` with no tests passes
- This is a false positive
- Tests must EXIST before claiming done

---

## Classification in Plans

```markdown
## Task 1: Implement user authentication
**Classification**: CREATION
**Test Requirement**: Write unit tests for auth functions BEFORE running pytest

## Task 2: Move legacy auth code to new structure
**Classification**: MIGRATION
**Test Requirement**: Run existing tests after migration
```

---

## UP

[planning/INDEX.md](INDEX.md)
