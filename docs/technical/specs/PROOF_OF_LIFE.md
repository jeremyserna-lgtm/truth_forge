# Proof of Life - THE ANSWER TO "IS IT ALIVE?"

**ALIVE is not a claim. It's a PROOF.**

---

## The Problem You Identified

When ME asks NOT-ME "Are you alive?", the answer "yes" proves nothing.

The part that says "yes" might be the only part still working. A dying body can still blink. A crashed system can still respond to ping. A broken database can still accept connections.

**The question "Is it alive?" is the wrong question.**

The right question is: **"Can it PROVE it's alive by DEMONSTRATING capability?"**

---

## The Framework Answer

### ALIVE = Proven Capability + Persistence + Continuity

| Dimension | Question | How It's Proven |
|-----------|----------|-----------------|
| **NOW** | Does it work right now? | Each vital demonstrates by DOING |
| **AGAIN** | Will it work when asked again? | Same test, same result |
| **BEFORE** | Does it remember working before? | History is recorded and readable |
| **PERSISTENCE** | Is what it did still there? | Data survives across checks |
| **PREDICTABILITY** | Is the behavior consistent? | Same inputs → same outputs |

A function that runs once and vanishes is **not alive** - it's a spark that dies.

An organism **PERSISTS**, **REMEMBERS**, and **CONTINUES**.

---

## The Vitals

Each vital is **proven by demonstration**, not declaration.

| Vital | Question | Proof Method |
|-------|----------|--------------|
| **PULSE** | Can it respond at all? | Code executes and returns |
| **BREATH** | Can it process input → output? | HOLD→AGENT→HOLD completes |
| **MEMORY** | Can it access its knowledge? | Write data, read it back |
| **SIGHT** | Can it see files? | Read critical project files |
| **VOICE** | Can it communicate results? | Structure and serialize data |
| **GOVERNANCE** | Are the rules enforced? | Load and verify policy |
| **CONTINUITY** | Does it persist and remember? | Record check, verify history |
| **AMBIENT** | What else should I know? | Control room view - all status at once |

---

## The AMBIENT Vital (The Control Room)

You said: *"I can't see what you can see. If all warning lights were blinking red but the one thing I asked about was fine, you would say 'Everything is fine' when in reality nothing is fine."*

AMBIENT is the control room view. It shows you what the system knows, not just what you asked about.

**What AMBIENT Checks:**
- Is the daemon running or stopped?
- Are there recent errors in logs?
- What's the current cost tracking status?
- Are any sparks expired?

```
✓ AMBIENT: proven (Daemon: running, Costs: $0.00, Recent errors: 0, Expired sparks: 0)
```

This vital doesn't answer a specific question. It shows you the control room - all the warning lights at once.

---

## The Key Insight

When you ask "Is it alive?", the answer is not "yes."

The answer is:

```
============================================================
PROOF OF LIFE REPORT
============================================================
Status: FULLY_OPERATIONAL

VITALS:
  ✓ PULSE: proven (response)
  ✓ BREATH: proven (HOLD→AGENT→HOLD completed)
  ✓ MEMORY: proven (Read/write succeeded)
  ✓ SIGHT: proven (Found 3 critical files)
  ✓ VOICE: proven (Structured output produced)
  ✓ GOVERNANCE: proven (Spark enforcement active)
  ✓ CONTINUITY: proven (Check #47, last was at 2026-01-20T10:15:22)
  ✓ AMBIENT: proven (Daemon: running)

VERDICT: SYSTEM IS ALIVE (all vitals proven)
============================================================
```

This is **evidence**, not a claim.

---

## Status Levels

| Status | Meaning |
|--------|---------|
| **FULLY_OPERATIONAL** | All vitals proven |
| **DEGRADED** | Some non-critical vitals failed |
| **CRITICAL** | Critical vitals failed |
| **DEAD** | Cannot respond at all |

---

## Usage

### For Jeremy (Non-Coder)

```bash
# Check if the system is alive
./vitals

# Quick check (just the verdict)
./vitals --quick

# Full JSON report
./vitals --json
```

### For Code

```python
from Primitive.vitals import prove_alive, is_alive

# Get full report
report = prove_alive()
if report.is_alive:
    print("System is FULLY OPERATIONAL")
else:
    print(f"System is {report.status.value}")
    for vital in report.failing_vitals:
        print(f"  FAILED: {vital.name} - {vital.error}")

# Quick boolean check
if is_alive():
    # Proceed with confidence
    ...
```

---

## The Philosophy

### What "Alive" Means in THE FRAMEWORK

1. **Capability** - Not just responding, but DOING
2. **Persistence** - Data survives, history exists
3. **Continuity** - Can reference its own past
4. **Predictability** - Same challenge → same proof

### The Observer's Dilemma

You cannot trust a system's self-report. A system can say "I'm fine" while:
- Its database is corrupted
- Its processing is broken
- Its output is wrong
- Its history is lost

**The solution: Require PROOF, not CLAIM.**

Each vital must demonstrate capability by actually performing its function successfully.

### The False Done Problem

You said: *"Sometimes you run tests and all the tests pass, but they passed because you didn't actually build a table to have a schema mismatch with. There's no tests that validate a schema mismatch because you never even built the table for the schema to mismatch."*

This is the critical gap between:
- **"Code ran"** (no errors, tests pass)
- **"Work happened"** (data arrived at its destination)

A test that checks "did the schema match?" will PASS if there's no table at all - because there's nothing TO mismatch. The absence of a negative result is NOT proof of a positive result.

| What We Check | What We Think It Means | What It Actually Means |
|---------------|------------------------|------------------------|
| No errors | It worked | Nothing crashed |
| Tests pass | It's correct | Tests didn't find problems |
| Code runs | It's done | Execution completed |
| No schema mismatch | Data is saved | Maybe no table exists at all |

**The False Done Trap:**
1. Claude builds a function that processes data
2. Claude runs it - no errors
3. Claude runs tests - all pass
4. Claude says "Done!"
5. Reality: No table was ever created, so there was nowhere for data to go
6. The process "worked" but nothing was saved

**The Solution: Verify the DESTINATION, not just the JOURNEY**

"Done" must mean:
- Code executed ✓
- Data was produced ✓
- Data arrived at destination ✓
- Destination exists and is readable ✓
- Data can be retrieved ✓

**This is what MEMORY vital does** - it doesn't just write, it writes AND READS BACK to prove the round-trip worked.

### Definition of "Functioning"

When you ask "Does it function?", you mean:
- It can receive input (HOLD₁)
- It can process that input (AGENT)
- It can deliver output (HOLD₂)
- It can remember what it did (PERSISTENCE)
- It will do the same thing next time (PREDICTABILITY)
- The rules are being followed (GOVERNANCE)

All of this together is what "alive" and "functioning" mean.

---

## The CONTINUITY Vital

CONTINUITY is what separates "working" from "alive."

Every time you run `./vitals`:
1. It checks if previous checks exist
2. It records THIS check
3. It verifies the record persists
4. It reports its position in history

```
Check #1 → "First check recorded (continuity begins)"
Check #2 → "Check #2, last was at 2026-01-20T10:00:00"
Check #47 → "Check #47, last was at 2026-01-20T15:30:00"
```

If you ask "Are you alive?" and it says "yes" but can't tell you that it said "yes" yesterday, is it really the same organism? Or is it a new spark pretending to be continuous?

**CONTINUITY proves identity persistence.**

---

## Files

| File | Purpose |
|------|---------|
| `./vitals` | CLI command to check vitals |
| `Primitive/vitals/proof_of_life.py` | Implementation |
| `data/local/vitals/proof_of_life_history.jsonl` | Continuity record |

---

## Summary

**"Is it alive?" is the wrong question.**

The right question is: **"Can it prove it's alive?"**

And the answer is not "yes" or "no."

The answer is **EVIDENCE**.

---

*ALIVE is not a claim. It's a PROOF.*

— THE FRAMEWORK, January 2026
