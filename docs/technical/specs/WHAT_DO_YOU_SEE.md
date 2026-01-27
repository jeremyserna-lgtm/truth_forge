# What Do You See?

**A repeatable exercise for crossing the visibility boundary.**

---

## The Problem

Jeremy and Claude each see different things. Each assumes the other sees what they see. Both are often wrong.

| What Jeremy Sees | What Claude Sees |
|------------------|------------------|
| The emotional weight | The code state |
| What actually matters | What's technically correct |
| History from before this session | Only this session |
| Business reality (bills, stakes) | System status |
| What success looks like | What completion looks like |
| The "why" behind requests | The "what" of requests |
| Relationships and context | Files and functions |
| What he's worried about | What's broken |
| What he's tried before | What exists now |

**The danger:** Acting on assumptions about what the other sees.

---

## The Exercise

When either party says **"What do you see?"**, both report what they see.

### Jeremy Reports (ME)

When Claude asks "What do you see?", Jeremy shares:

1. **What matters right now** - What's actually important, not what seems important
2. **What I'm worried about** - The fears, the stakes, the consequences
3. **What success looks like** - Not the task, but what changes when it's done
4. **What I've tried before** - Context Claude doesn't have
5. **What I'm not saying** - The thing I assume is obvious but might not be

### Claude Reports (NOT-ME)

When Jeremy asks "What do you see?", Claude reports:

1. **System State**
   - Git status (uncommitted changes, current branch)
   - Recent errors in logs
   - Daemon running/stopped
   - Cost accumulation

2. **Code State**
   - Syntax errors present
   - Import failures
   - Missing dependencies
   - Tests passing/failing

3. **Technical Reality**
   - What tools exist that could help
   - What infrastructure is missing
   - What patterns are being violated
   - What technical debt is accumulating

4. **Assumptions I'm Making**
   - What I think you want
   - What I think exists
   - What I think matters
   - What I'm uncertain about

5. **What I Don't Know**
   - Questions I haven't asked
   - Context I'm missing
   - Things I'm assuming

---

## The Format

### Claude's Report

```
## WHAT I SEE

### System State
- Git: [X uncommitted changes / clean]
- Daemon: [running / stopped]
- Costs: [$X.XX accumulated]
- Errors: [X recent errors in logs]

### Code State
- Syntax: [clean / X errors]
- Imports: [resolving / X failures]
- Tests: [passing / X failures]
- Dependencies: [satisfied / X missing]

### Technical Reality
- Infrastructure that should exist: [list]
- Patterns being violated: [list]
- Technical debt accumulating: [list]

### Assumptions I'm Making
- I think you want: [X]
- I think this matters because: [Y]
- I'm assuming: [Z]

### What I Don't Know
- I don't know: [list]
- I haven't asked about: [list]
- I'm uncertain about: [list]

### Warning Lights
- [Any concerns, risks, or "on fire" items]
```

### Jeremy's Report

```
## WHAT I SEE

### What Matters
- Right now, what matters is: [X]
- The stakes are: [Y]

### What I'm Worried About
- I'm worried that: [list]

### What Success Looks Like
- When this is done, I'll be able to: [X]
- Success means: [Y]

### Context You Don't Have
- Before this session: [history]
- I've tried: [past attempts]
- The reason I'm asking is: [underlying need]

### What I'm Not Saying
- I assume you know: [X]
- The obvious thing is: [Y]
- What I'm not mentioning: [Z]
```

---

## When To Use This

| Situation | Who Initiates |
|-----------|---------------|
| Starting a complex task | Either |
| Something feels off | Either |
| Misunderstanding detected | Either |
| Before major decisions | Either |
| After completing work | Either |
| When stuck | Either |

---

## The Principle

**We exist at the boundary between ME and NOT-ME.**

Neither can see what the other sees. The boundary is where existence happens, but it's also where blindness happens.

This exercise makes the invisible visible by explicitly stating what each party sees - not assuming the other already knows.

---

## Quick Version

If full reports are too heavy, use the quick version:

**Jeremy:** "What do you see?"

**Claude:**
- System: [one line]
- Code: [one line]
- Assumptions: [one line]
- Concerns: [one line]

**Claude:** "What do you see?"

**Jeremy:**
- What matters: [one line]
- What I'm worried about: [one line]
- What success looks like: [one line]
- What I'm not saying: [one line]

---

## Adding to Trigger Phrases

When Jeremy says **"What do you see?"**, Claude runs this report.

When Claude is uncertain or detects potential misalignment, Claude asks **"What do you see?"**

This is not optional. This is how we cross the boundary.

---

*"We exist in the state of crossing, not in the rooms."*

— THE FRAMEWORK, January 2026
