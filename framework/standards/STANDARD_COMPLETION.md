# Standard Completion

**The Standard** | Done is a state, not a destination. Every completion loops back to beginning.

**Authority**: THE FRAMEWORK | **Status**: ACTIVE
**Owner**: Framework | **Version**: 1.0 | **Effective**: 2026-01-26

---

## Quick Reference

| Concept | Definition |
|---------|------------|
| **Done** | A state where verification confirms the current iteration complete |
| **Complete** | The illusion - nothing is ever complete, only at a stable state |
| **The Loop** | Every completion returns to SEE, beginning the next iteration |
| **Definition of Done** | Checklist for current iteration, not final state |

---

## WHY (Theory)

### The Completion Paradox

**Done is real. Complete is illusion.**

```
LINEAR VIEW (Wrong):
  START ────────────────────────────────────────→ DONE (forever)

CYCLIC VIEW (Correct):
  START ──→ WORK ──→ DONE ──→ SEE ──→ START ──→ WORK ──→ DONE ──→ ...
              ↑                           ↑
              └───────────────────────────┘
                    THE LOOP
```

A system that claims "complete" has stopped evolving. A system that recognizes "done for now" continues to improve.

### The SEE:SEE:DO:DONE Cycle

Extending SEE:SEE:DO from 02_PERCEPTION:

```
SEE ────→ SEE:SEE ────→ DO ────→ SEE:DO ────→ DONE
 ↑                                              │
 │                                              │
 └──────────────── THE LOOP ────────────────────┘
```

| Phase | Question | State |
|-------|----------|-------|
| **SEE** | What do I perceive? | Beginning |
| **SEE:SEE** | Do I see that I see? | Recognition |
| **DO** | What action follows? | Execution |
| **SEE:DO** | Did I do what I intended? | Verification |
| **DONE** | Is this iteration complete? | Stable state |
| **→ SEE** | What do I now perceive? | New beginning |

**DONE is not the end of the cycle. DONE triggers new SEE.**

### The Three Completes

| Level | What "Done" Means | What Loops |
|-------|-------------------|------------|
| **Task** | This task verified complete | Next task begins |
| **Iteration** | This iteration verified complete | Next iteration begins |
| **System** | This system verified stable | Evolution continues |

### Alignment with THE FRAMEWORK

From 00_GENESIS:
> "The only permanent part of the system is the process of transformation itself."

Completion is transformation, not termination. Each "done" transforms into the next "beginning."

---

## WHAT (Specification)

### Definition of Done (MUST)

Every deliverable MUST have a Definition of Done that:

1. **Is a checklist** - Verifiable items, not aspirations
2. **Checks existence** - Things EXIST, not just "were attempted"
3. **Checks verification** - Things PASS, not just "ran"
4. **Does NOT claim finality** - "Done for this iteration" not "complete forever"

```markdown
## Definition of Done

### This Iteration

- [ ] All required sections exist
- [ ] All verification passes
- [ ] All references resolve
- [ ] Pattern coverage complete

### Next Iteration (Identified)

- [ ] [Known improvement 1]
- [ ] [Known improvement 2]
```

### The Loop Marker (MUST)

Every Definition of Done MUST acknowledge the loop:

```markdown
---

*This iteration is DONE. The loop continues.*

**Next SEE**: [What will be examined in the next iteration]
```

### Never Complete Acknowledgment (MUST)

Documents MUST NOT claim to be "complete" or "final."

```markdown
# ❌ WRONG
This is the complete specification for X.
This document is finalized.

# ✅ CORRECT
This is the current specification for X.
This document is at version 1.0.
```

### Iteration Tracking (SHOULD)

Documents SHOULD track iterations:

```markdown
## Iteration History

| Iteration | Date | Focus | Status |
|-----------|------|-------|--------|
| 1.0 | 2026-01-26 | Initial structure | DONE |
| 1.1 | TBD | Document splitting | IDENTIFIED |
```

---

## HOW (Reference)

### The Completion Checklist Template

```markdown
## Definition of Done (Iteration X.Y)

### Existence Checks
- [ ] Required artifact exists
- [ ] Required sections present
- [ ] Required links resolve

### Verification Checks
- [ ] Quality checks pass
- [ ] Pattern coverage verified
- [ ] Convergence validated

### Loop Acknowledgment
- [ ] Next iteration identified
- [ ] Known improvements documented
- [ ] "Never complete" acknowledged

---

*DONE for iteration X.Y. Loop continues to X.Z.*
```

### Applying to Documents

Every document cycle:

```
WRITE ──→ VERIFY ──→ DONE ──→ SEE (what's missing) ──→ WRITE ──→ ...
```

### Applying to Standards

Every standard cycle:

```
CREATE ──→ IMPLEMENT ──→ VERIFY ──→ DONE ──→ DISCOVER (gaps) ──→ UPDATE ──→ ...
```

### Applying to Code

Every code cycle:

```
WRITE ──→ TEST ──→ PASS ──→ DONE ──→ OBSERVE (production) ──→ IMPROVE ──→ ...
```

---

## The Completion Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                     THE COMPLETION LOOP                          │
│                                                                  │
│    ┌─────┐                                          ┌─────┐     │
│    │ SEE │ ◄────────────────────────────────────────│DONE │     │
│    └──┬──┘                                          └──▲──┘     │
│       │                                                │        │
│       ▼                                                │        │
│    ┌─────────┐                                    ┌────┴───┐    │
│    │ SEE:SEE │                                    │ SEE:DO │    │
│    └────┬────┘                                    └────▲───┘    │
│         │                                              │        │
│         ▼                                              │        │
│      ┌─────┐                                     ┌─────┘        │
│      │ DO  │ ────────────────────────────────────┘              │
│      └─────┘                                                    │
│                                                                  │
│   DONE is a gate, not a destination. Passing DONE returns to    │
│   SEE with new perception from having completed the cycle.      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns

### ❌ Finality Language

```markdown
# WRONG
This is the final version.
This specification is complete.
No further changes needed.

# CORRECT
This is version 1.0.
This iteration is done.
Next iteration will address X.
```

### ❌ Missing Next Iteration

```markdown
# WRONG
## Definition of Done
- [x] All items verified
(end of document)

# CORRECT
## Definition of Done
- [x] All items verified

## Next Iteration
- [ ] Split long documents
- [ ] Add examples
```

### ❌ Completion Without Loop

```markdown
# WRONG
Task complete. Moving on.

# CORRECT
Task done for this iteration.
Next SEE: Observe production behavior.
```

---

## Convergence

### Bottom-Up Validation

This standard requires meta-standards:
- [STANDARD_RECURSION](STANDARD_RECURSION.md) - SEE:SEE:DO cycle
- [STANDARD_LIFECYCLE](STANDARD_LIFECYCLE.md) - State management

### Top-Down Validation

This standard is shaped by theory:
- [00_GENESIS](../00_GENESIS.md) - Transformation is permanent
- [02_PERCEPTION](../02_PERCEPTION.md) - SEE:SEE:DO cycle

---

## Related Standards

| Standard | Relationship |
|----------|--------------|
| [STANDARD_RECURSION](STANDARD_RECURSION.md) | The SEE:SEE:DO foundation |
| [STANDARD_LIFECYCLE](STANDARD_LIFECYCLE.md) | State transitions |
| [planning/](planning/) | Task completion verification |

---

*Done is a state, not a destination. Every completion loops back to beginning.*
