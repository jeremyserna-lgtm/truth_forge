# Planning Checklists

**Verification checklists for different task types.**

---

## New Code Checklist (CREATION tasks)

Before claiming "done" on NEW code:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        NEW CODE CHECKLIST                                   │
│                                                                              │
│   □ TESTS WRITTEN (not just run)                                            │
│     □ Happy path test                                                       │
│     □ Empty/null input test                                                 │
│     □ Invalid input test                                                    │
│     □ Error path test (verify exceptions logged)                            │
│     □ Concurrent access test (if applicable)                                │
│                                                                              │
│   □ DATA SAFETY (for data-handling code)                                    │
│     □ Invalid data goes to DLQ (never discarded)                            │
│     □ DLQ write failure doesn't lose original data                          │
│     □ Idempotent operations (same input → same output)                      │
│     □ INSERT OR REPLACE (not INSERT which duplicates)                       │
│                                                                              │
│   □ ERROR HANDLING                                                          │
│     □ No bare `except: pass`                                                │
│     □ All exceptions logged with context                                    │
│     □ Error signals preserve original record                                │
│     □ Nested try/except if inner error handler can fail                     │
│                                                                              │
│   □ STATIC ANALYSIS                                                         │
│     □ mypy --strict passes                                                  │
│     □ ruff check passes                                                     │
│     □ No type: ignore without justification                                 │
│                                                                              │
│   ⚠️  FAILING ANY OF THESE = NOT DONE                                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Migration Checklist (MIGRATION tasks)

```
□ Source code identified and read
□ Target location prepared
□ Code copied/transformed
□ Imports updated
□ Existing tests located
□ Tests run and pass
□ Old location marked deprecated (if applicable)
```

---

## Plan Review Checklist

```
□ All tasks classified (Migration/Creation/Research/Configuration)
□ Gates defined with existence AND passing checks
□ DLQ defined for error capture
□ Idempotency verified for state-changing operations
□ New Code Checklist completed (for Creation tasks)
□ No time estimates (scope-based only)
□ Completion criteria explicit and verifiable
```

---

## The Planning Loop

```
STEP 1: IDENTIFY
  • Select next item from priority queue
  • Verify all dependencies are OPERATIONAL
  • List ALL source locations
  • CLASSIFY: Migration, Creation, Research, or Configuration

STEP 2: EXECUTE (varies by type)
  • Migration: Copy from source to target
  • Creation: Write new implementation
  • Research: Gather and document findings
  • Configuration: Apply and validate changes

STEP 3: WRITE TESTS (Creation/Configuration only)
  • WRITE tests BEFORE running them
  • Test happy path, edge cases, error handling

STEP 4: VERIFY (varies by type)
  • Migration: Tests pass, imports work
  • Creation: Tests EXIST AND pass
  • Research: Findings documented
  • Configuration: Validation passes

STEP 5: GATE CHECK
  • All required artifacts EXIST
  • All quality checks PASS
  • All deliverables VERIFIED
```

---

## UP

[planning/INDEX.md](INDEX.md)
