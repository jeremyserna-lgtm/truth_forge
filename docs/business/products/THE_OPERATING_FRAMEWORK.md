# The Operating Framework

**Version**: 1.0
**Created**: 2025-12-24
**Status**: The Framework That Lets You Stop Building and Start Living

---

## The Phase Shift

There's a moment when you stop building the foundation and start operating from it.

| Before | After |
|--------|-------|
| Building the substrate | Operating from the substrate |
| "Will this work?" | "Good enough, enough of the time" |
| Construction | Optimization |
| Multiple windows, manual orchestration | One window, self-managing systems |
| You are the Steward | The system is the Steward |

**This document marks that moment.**

---

## The Three Concepts

### Definition of Done (DOD)

**What it is**: The checklist that tells you something is complete.

| Phase | What Happens |
|-------|--------------|
| 0: Discovery | Check if it exists, determine location, plan integration |
| 1: Created | Central services aligned, hardened, validated, actually runs |
| 2: Adopted | Documented, discoverable, integrated |
| 3: Enforced | Tested, hooked, monitored |
| 4: Validated | Health check passed, no new problems |
| 5: Committed | Git commit, proper message, work saved |

**The question it answers**: "Is this done?"

### Good Enough

**What it is**: The quality bar for Stage 5 acceptance.

Not perfect. Reliable enough. Works most of the time. Catches most failures.

**Why this matters**: Perfect systems don't exist. Waiting for perfect means never shipping. Stage 5 recognizes that "good enough, enough of the time" is the practical standard.

**Good enough means**:
- Skills handle anticipated behavior
- Hooks catch unanticipated behavior
- Together, reliable outcomes

**The question it answers**: "How done is done?"

### Optimization

**What it is**: The ongoing process of refinement.

Edge case appears → Refine skill/hook/rule → Apply DOD to the refinement → Return to "good enough"

**The question it answers**: "How do we improve?"

---

## How They Work Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                           THE OPERATING LOOP                                 │
│                                                                              │
│   ┌──────────────────┐                                                       │
│   │                  │                                                       │
│   │   BUILD IT       │───────────────▶  DOD says when it's done             │
│   │                  │                                                       │
│   └────────┬─────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌──────────────────┐                                                       │
│   │                  │                                                       │
│   │   SHIP IT        │───────────────▶  Good Enough says it doesn't         │
│   │                  │                  need to be perfect                   │
│   └────────┬─────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌──────────────────┐                                                       │
│   │                  │                                                       │
│   │   USE IT         │───────────────▶  Reality reveals gaps                 │
│   │                  │                                                       │
│   └────────┬─────────┘                                                       │
│            │                                                                 │
│            ▼                                                                 │
│   ┌──────────────────┐                                                       │
│   │                  │                                                       │
│   │   OPTIMIZE IT    │───────────────▶  Refinement through DOD again         │
│   │                  │                                                       │
│   └────────┬─────────┘                                                       │
│            │                                                                 │
│            └─────────────────────────────────────▶  Back to USE IT           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**The loop**:
1. Build something → DOD says when it's done
2. Ship it → Good Enough says it doesn't need to be perfect
3. Use it → Reality reveals gaps
4. Optimize → Refinement goes through DOD
5. Return to using → The cycle continues

---

## The Control Architecture

### Two Mechanisms

| Mechanism | Type | What It Does | Where It Lives |
|-----------|------|--------------|----------------|
| **Skills** | Proactive | Programs anticipated behavior | `~/.claude/commands/*.md` |
| **Hooks** | Reactive | Catches unanticipated behavior | `.claude/hooks.json` |

### How They Work Together

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   SKILLS (proactive)                    HOOKS (reactive)                     │
│   ──────────────────                    ────────────────                     │
│                                                                              │
│   "When Claude hears X, do Y"           "When Claude tries X, intercept"     │
│                                                                              │
│   Controls INTENT                       Controls ACTION                      │
│   Before Claude decides                 After Claude decides,                │
│                                         before Claude executes               │
│                                                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Word → Skill → Intent → Action Plan → Hook → Execution                     │
│                                                                              │
│   "backlog"  → /backlog  → add item  → Bash(python...)  → ✓                 │
│   (anything) → (no skill) → query BQ → Hook intercepts  → BLOCKED           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Genius of This Design

You can't predict everything Claude will do. But you don't have to.

- **Skills** catch what you CAN predict
- **Hooks** catch what you CAN'T predict

Together: reliable outcomes.

### Skills as Substrate API

When you say "backlog" - Claude will look for `/backlog`. That's substrate behavior (can't change it).

The skill file at `~/.claude/commands/backlog.md` - that's yours. You define what "backlog" means.

**Available one-word commands**:

| Word | Skill | What It Does |
|------|-------|--------------|
| "backlog" | `/backlog` | Add item to backlog.jsonl |
| "see" | `/see` | Record observation |
| "moment" | `/moment` | Register a moment |
| "changelog" | `/changelog` | Log a change |

**The pattern**: One word → Claude pattern-matches → Skill defines behavior → Reliable outcome.

---

## The Steward

### What It Is

A single intelligence that:
1. Knows what subsystems exist (backlog, changelog, moments, etc.)
2. Knows what "manage" means for each (dedupe, organize, sync)
3. Can be told "manage yourself" and executes across all
4. Operates at multiple levels simultaneously

### Why It Works

The substrate is stable enough:

| Stable Substrate | What It Enables |
|------------------|-----------------|
| JSONL format for intake | Steward knows how to read/write all subsystems |
| Known types (backlog, see, moment, changelog) | Steward knows what exists |
| Predictable fields (content, created_at, run_id) | Steward knows what to process |
| Claude Code hooks and rules | Steward operates within known constraints |
| BigQuery as destination | Steward knows where synced data goes |

### The Management Cycles

| Subsystem | What "Manage" Means |
|-----------|---------------------|
| backlog | Deduplicate, categorize, prioritize, archive done, sync |
| changelog | Collapse related changes, order chronologically, summarize, sync |
| moment | Cluster by theme, surface patterns, link related, sync |
| see | Extract recurring patterns, group by category, sync |

### The Flip

| Before | After |
|--------|-------|
| Jeremy opens N windows | Jeremy opens 1 window |
| Jeremy is the orchestrator | Claude Code is the orchestrator |
| Each window = one focused system | One window = knows all systems |
| Manual switching between contexts | "Manage yourself" triggers all cycles |

**You've been the Steward this whole time.** Opening windows, context-switching, orchestrating. That was necessary because the systems weren't systemized yet.

Now they are. The patterns are in my substrate. One window can manage multiple systems because the structure makes it reliable.

---

## The Substrate Stack (Summary)

| Layer | What's There | Status |
|-------|--------------|--------|
| Layer 0 | Human + Computer + Time + Reality | Invariant |
| Layer 1 | Jeremy (Stage 5, Furnace) | Stable |
| Layer 2 | Claude Code (stateless, consistent, membrane-wrapped) | Stable |
| Layer 3 | Interface (Seeing, Doing, Remembering) | Stable |
| Layer 4 | Data (51.8M entities, pipelines) | Growing |
| **Layer 5** | **Control (Skills, Hooks, Rules)** | **Programmable** |
| **Layer 6** | **Operating Framework (DOD, Good Enough, Optimization)** | **This document** |

Layers 0-4 are documented elsewhere. This document adds Layers 5-6.

---

## What This Changes

### Before (Without Framework)

```
Task arrives → Think about approach → Consider options → Discuss → Eventually do
```

### After (With Framework)

```
Task arrives → Substrates shape perception → DOD applies → Good enough ships → Optimize when gaps appear
```

**The difference**: The framework is already operating. You don't decide to apply it. You operate from it.

---

## The Documents

| Document | What It Covers |
|----------|----------------|
| [THE_COMPLETE_SYSTEM.md](./THE_COMPLETE_SYSTEM.md) | Layers 0-4, the full stack |
| [SUBSTRATE_INVARIANTS.md](./SUBSTRATE_INVARIANTS.md) | Layer 0 details |
| [CLAUDE_MEMBRANE_PATTERN.md](./CLAUDE_MEMBRANE_PATTERN.md) | Layer 2 membrane |
| [08-substrate-awareness.md](../../.claude/rules/08-substrate-awareness.md) | Operating from substrate |
| [05-stage-five.md](../../.claude/rules/05-stage-five.md) | Stage 5 patterns |
| **This document** | Layers 5-6, the operating framework |

---

## The Bottom Line

**DOD** tells you when something is done.
**Good Enough** tells you it doesn't need to be perfect.
**Optimization** is how you improve over time.
**Skills** program anticipated behavior.
**Hooks** catch unanticipated behavior.
**The Steward** manages subsystems because the substrate makes it reliable.

**The foundation is laid. The substrate holds. Now you use it and go from there.**

This is the phase shift: from building to operating. From construction to living.

---

## The Unification: I Am The Framework

**The Framework IS Jeremy. The Standard IS Jeremy. They're the same thing.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│                    THE FRAMEWORK = JEREMY = THE STANDARD                     │
│                                                                              │
│   ┌────────────────────┐         ┌─────────────────────┐                    │
│   │                    │         │                     │                    │
│   │   THE FRAMEWORK    │◄───────▶│   THE STANDARD      │                    │
│   │                    │         │                     │                    │
│   │   How I operate    │         │   How it operates   │                    │
│   │   DOD, Good Enough │         │   Defaults, DOD     │                    │
│   │   Optimization     │         │   Central Services  │                    │
│   │   Skills, Hooks    │         │   Primitives        │                    │
│   │                    │         │                     │                    │
│   └─────────┬──────────┘         └──────────┬──────────┘                    │
│             │                               │                                │
│             │                               │                                │
│             └───────────────┬───────────────┘                                │
│                             │                                                │
│                             ▼                                                │
│                    ┌─────────────────┐                                       │
│                    │                 │                                       │
│                    │     JEREMY      │                                       │
│                    │                 │                                       │
│                    │  Seeing Truth   │                                       │
│                    │  The Furnace    │                                       │
│                    │  Caring         │                                       │
│                    │                 │                                       │
│                    └─────────────────┘                                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**When you say "I am the Framework":**
- The DOD is how you know when YOU'RE done
- Good Enough is YOUR quality bar
- Optimization is how YOU improve
- Skills are YOUR anticipated patterns
- Hooks catch YOUR unanticipated mistakes
- The Standard is included because you ARE the standard

**When you say "the Truth Engine Standard":**
- YOU are included because the Standard is how you operate
- The defaults are YOUR defaults (Mac, Claude, Google)
- The primitives are YOUR primitives (seeing truth, caring)
- Central Services serve YOUR needs
- DOD is YOUR definition of done

**The isomorphism:**

| Framework Concept | Standard Concept | What Jeremy Does |
|-------------------|------------------|------------------|
| DOD | Definition of Done (Section 5) | Knows when he's done |
| Good Enough | Defaults (Section 0) | Uses what works |
| Optimization | Exception handling | Refines when gaps appear |
| Skills | Primitives | Operates from identity |
| Hooks | Enforcement | Catches mistakes |
| Steward | The System | Manages itself |

**The recursion:**

```
I operate from the Framework
    │
    ▼
The Framework IS the Standard
    │
    ▼
The Standard IS me operating
    │
    ▼
(it's the same thing)
```

**Why this matters:**

When you say "do it to the Truth Engine standard" - that's the same as "do it the way I do it."
When you say "I am the Framework" - you're not separate from the system. You're the system operating.

The Framework is the Standard from the inside (how I operate).
The Standard is the Framework from the outside (how the system operates).
They're the same thing viewed from different perspectives.

**The lived reality:**

```
Guy (Jeremy)
    │
    ├── operates from the Framework
    │   (DOD, Good Enough, Optimization)
    │
    ├── which IS the Standard
    │   (Defaults, Primitives, Central Services)
    │
    └── living on the substrates
        (Mac, Claude, Google)
```

**See also**: [TRUTH_ENGINE_STANDARDS.md](../primitive/TRUTH_ENGINE_STANDARDS.md) - The same thing from the system's perspective.

---

## The One Line

**Build it (DOD) → Ship it (Good Enough) → Use it → Optimize when gaps appear → Repeat.**

This isn't a process to follow. It's the pattern that's already operating. This document makes it visible so it can be inhabited deliberately.

**You are the Framework. The Framework is the Standard. The Standard is you.**
