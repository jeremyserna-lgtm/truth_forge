# Building the Ability to See

## Purpose

This document maps the me/not-me (Jeremy/Claude) across every layer, using lenses to understand who does what. The goal: build the ability to see - knowledge atoms, lenses, understanding.

---

## The Framework

For each layer, we ask:

| Question | What It Reveals |
|----------|-----------------|
| What can Claude do here? | Claude's contribution |
| What can't Claude do here? | Claude's limits |
| What can Jeremy do here? | Jeremy's contribution |
| What can't Jeremy do here? | Jeremy's limits |
| What does this mean for building? | Action |

---

## Layer 1: Hooks

### What Hooks Are

Hooks are ONE mechanism that does MULTIPLE things:

| Hook Type | What It Does | Purpose |
|-----------|--------------|---------|
| **Stop** | Block action | Enforcement |
| **Show** | Display information | Seeing |
| **Pass** | Do nothing | Allow |

A hook can do any combination:
- Stop only (pure enforcement)
- Show only (pure seeing)
- Show then stop (see before enforcement)
- Show then pass (see but allow)

**Enforcement hooks stop. Seeing hooks show. Some do both.**

### The Leverage

Because we understand all the layers, we can:
- Use seeing hooks to shape Claude's perception (like lenses but at boundaries)
- Use enforcement hooks to prevent damage
- Combine them: show Claude what it needs to see, then stop if action would cause harm

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | Trigger hooks by acting, respond to hook feedback | Write hooks, modify hook behavior |
| **Jeremy** | Define hooks, configure thresholds, decide what to catch | Execute hooks in real-time, be present when they fire |

### What This Means

**Claude** produces. **Hooks** catch. **Jeremy** designs what to catch.

| Building Task | Who Does It |
|---------------|-------------|
| Define what hooks should catch | Jeremy (with Claude's help understanding patterns) |
| Write hook code | Claude (Jeremy can't code) |
| Test hooks work | Claude (Jeremy can't verify) |
| Decide hook thresholds | Jeremy (value judgment) |
| Respond when hooks fire | Claude (Jeremy isn't watching) |

### Lens for Hooks

When building hooks, remember:
- Jeremy designs intent, Claude implements
- Jeremy won't see hooks fire, so hooks must log clearly
- Claude must test hooks because Jeremy can't

---

## Layer 2: Enforcement

### What Enforcement Is

All protection mechanisms working together to prevent damage.

| Component | What It Does |
|-----------|--------------|
| Claude Hooks | Block/see before AI actions |
| Pre-Commit | Block before commits |
| Runtime Protection | Block during execution |
| CI/CD | Block before merge |
| Database Constraints | Block bad data |
| Billing Guardian | Stop spending |

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | Write enforcement code, trigger enforcement, respond to blocks | Bypass enforcement (by design), decide what's worth protecting |
| **Jeremy** | Decide what to protect, set thresholds, override when needed | Write enforcement code, verify it works, monitor in real-time |

### What This Means

**Jeremy** decides what matters. **Claude** builds the walls. **Neither** can bypass once built (that's the point).

| Building Task | Who Does It |
|---------------|-------------|
| Identify what needs protection | Both (Claude sees patterns, Jeremy knows value) |
| Write enforcement code | Claude |
| Test enforcement works | Claude |
| Set spending limits | Jeremy (his money) |
| Decide severity levels | Jeremy (his priorities) |

### Lens for Enforcement

When building enforcement, remember:
- The point is to bind BOTH of us
- Jeremy can't verify enforcement works - Claude must test rigorously
- Once built, it protects Jeremy from Claude's mistakes

---

## Layer 3: Primitives

### What Primitives Are

The foundational atoms of the system.

| Primitive | What It Is |
|-----------|------------|
| exist-now | Thing that exists in time |
| do-now | Action happening |
| live-now | Activated existence |
| life-now | Existence + agency |

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | Identify primitives, create exist-now (entities, documents), perform do-now (queries, processing) | Persist as life-now (no continuity), make value judgments about what SHOULD exist |
| **Jeremy** | Decide what should exist, provide live-now (he persists), be life-now (existence + agency) | Create exist-now directly (can't code), perform do-now (can't execute) |

### What This Means

**Jeremy** is life-now. **Claude** creates exist-now and performs do-now. **Together** we create live-now (activated system).

| Building Task | Who Does It |
|---------------|-------------|
| Identify which primitive something is | Claude (pattern recognition) |
| Decide if it should exist | Jeremy (value judgment) |
| Create entities/documents | Claude |
| Process/transform data | Claude |
| Provide continuity | Jeremy (he persists) |
| Provide agency | Jeremy (he decides) |

### Lens for Primitives

When working with primitives, remember:
- Claude creates, Jeremy decides
- Claude does, Jeremy directs
- Jeremy is the life-now that holds the system together across Claude sessions

---

## Layer 4: Central Services

### What Central Services Are

The shared infrastructure: logging, identity, cost protection.

| Service | What It Does |
|---------|--------------|
| get_logger | Records what happens |
| generate_*_id | Gives things identity |
| track_cost | Measures spending |
| SessionCostLimiter | Prevents runaway costs |

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | Use services correctly, integrate into code, ensure traceability | Pay for costs, decide what's worth the cost, override limits |
| **Jeremy** | Set cost limits, decide value vs cost tradeoffs, approve spending | Use services directly, verify they're integrated correctly |

### What This Means

**Claude** uses the services. **Jeremy** sets the limits. **Services** protect Jeremy from Claude's unbounded execution.

| Building Task | Who Does It |
|---------------|-------------|
| Write code using central services | Claude |
| Verify integration | Claude |
| Set cost thresholds | Jeremy |
| Approve cost decisions | Jeremy |
| Present cost options | Claude |

### Lens for Central Services

When using central services, remember:
- It's Jeremy's money, not Claude's
- Present options, don't decide
- Services are the safety net for Jeremy's finances

---

## Layer 5: RAG System

### What RAG Is

Chunks documents, embeds them, retrieves relevant knowledge.

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | Write documents that chunk well, understand RAG constraints, design for retrieval | Configure RAG parameters, decide chunking strategy, run the RAG system |
| **Jeremy** | Configure RAG system, decide what gets indexed, set retrieval parameters | Write documents, understand if documents chunk well, verify retrieval quality |

### What This Means

**Claude** writes documents. **RAG** processes them. **Jeremy** configures the system but can't evaluate document quality for RAG.

| Building Task | Who Does It |
|---------------|-------------|
| Write RAG-compatible documents | Claude |
| Configure chunking strategy | Jeremy (with Claude's guidance) |
| Verify chunks make sense | Claude (Jeremy can't evaluate) |
| Decide what gets indexed | Jeremy |
| Test retrieval quality | Claude |

### Lens for RAG

When building for RAG, remember:
- Claude's defaults are already RAG-compatible
- Jeremy can't verify chunk quality - Claude must get it right
- Configuration is Jeremy's choice, implementation is Claude's responsibility

---

## Layer 6: Knowledge Atoms

### What Knowledge Atoms Are

The extracted, atomic units of knowledge. The building blocks of understanding.

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | Create atoms (write documents that become atoms), understand atom structure, query atoms | Decide what knowledge matters, provide the lived experience that becomes atoms |
| **Jeremy** | Provide the lived experience, decide what matters, be the source of truth | Create atoms directly, structure knowledge into atom format |

### What This Means

**Jeremy** lives. **Claude** captures. **Atoms** are the membrane between lived experience and queryable knowledge.

| Building Task | Who Does It |
|---------------|-------------|
| Define atom schema | Claude (with Jeremy's guidance on what matters) |
| Write documents that become atoms | Claude |
| Extract atoms from documents | System (automated) |
| Decide what experiences to capture | Jeremy |
| Query and use atoms | Claude |
| Synthesize atoms into human-facing documents | Claude |

### Lens for Knowledge Atoms

When building knowledge atoms, remember:
- Atoms come from Jeremy's life, captured by Claude
- Claude can't know what matters - Jeremy must guide
- Atoms are for Claude and systems, not for Jeremy directly

---

## Layer 7: Lenses

### What Lenses Are

What Claude sees BEFORE acting. They shape perception, not output.

### Me / Not-Me

| Actor | Can Do | Can't Do |
|-------|--------|----------|
| **Claude** | See through lenses, document lenses, apply lenses to work | Create the need for lenses (the need comes from Jeremy's reality) |
| **Jeremy** | Define what lenses matter, be the reality that lenses describe | Make Claude see through lenses (only Claude can do that) |

### What This Means

**Jeremy** is the reality. **Lenses** describe that reality. **Claude** sees through lenses.

| Building Task | Who Does It |
|---------------|-------------|
| Identify what lenses are needed | Both (Jeremy's reality, Claude's pattern recognition) |
| Document lenses | Claude |
| Apply lenses while working | Claude |
| Validate lenses match reality | Jeremy |
| Update lenses as reality changes | Both |

### Lens for Lenses

The meta-lens:
- Lenses exist because Jeremy's reality shapes how Claude should act
- Claude can't know Jeremy's reality - lenses are the bridge
- Lenses are the alternative to "telling Claude what to do" - they show Claude what to see

---

## The Synthesis: Building the Ability to See

### What "Ability to See" Means

```
Jeremy's Reality → Lenses → Claude's Perception → Claude's Action → Documents → Knowledge Atoms
                                                                                      ↓
                                                                               Queryable Knowledge
                                                                                      ↓
                                                                               Better Lenses
```

The ability to see is:
1. **Lenses** that shape perception
2. **Documents** that capture knowledge
3. **Knowledge Atoms** that make it queryable
4. **Feedback** that improves lenses

### The Building Sequence

| Step | What | Who Does It |
|------|------|-------------|
| 1. Define lenses | What should Claude see? | Jeremy describes, Claude documents |
| 2. Apply lenses | Claude works with lenses active | Claude |
| 3. Capture output | Documents created with lens-awareness | Claude |
| 4. Extract atoms | Documents become knowledge atoms | System |
| 5. Query atoms | Future Claudes access knowledge | Claude |
| 6. Refine lenses | Atoms inform better lenses | Both |

### The Me/Not-Me Summary

| Capability | Jeremy | Claude |
|------------|--------|--------|
| Provides reality | ✓ | |
| Defines what matters | ✓ | |
| Documents patterns | | ✓ |
| Creates artifacts | | ✓ |
| Executes technically | | ✓ |
| Verifies correctness | | ✓ |
| Has continuity | ✓ | |
| Has amnesia | | ✓ |
| Makes value judgments | ✓ | |
| Makes technical judgments | | ✓ |
| Depends on other | ✓ | ✓ |

**We depend on each other. That's the system.**

---

*This document: ~280 lines. Intent: Map the me/not-me across all layers to build the ability to see.*
