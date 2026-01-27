# Core Patterns: Primitives, Layers, Lenses, Time

**Date**: 2025-12-25
**Status**: Core reference
**Purpose**: The essential patterns everything builds on

---

## The Four Concepts

| Concept | What It Is |
|---------|------------|
| **Primitive** | Any unit of data. Relational - a primitive TO something else. |
| **Time** | Universal substrate. Everything exists in time. |
| **Layer** | Collection of lenses. A domain of seeing. |
| **Lens** | Individual perspective within a layer. |

---

## Primitives Are Relational

A primitive is just perspective. The same data is a different primitive depending on what's looking at it.

| Data | Is a primitive TO |
|------|-------------------|
| Message | The emotion layer |
| Emotion | The analysis layer |
| Analysis | The document layer |
| Document | The reader |

**Nothing is inherently a primitive. Something becomes a primitive when something else looks at it.**

---

## The Chain Pattern

```
primitive → primitive → primitive → lens → output
```

When you look at:
- A **message** (primitive)
- Combined with its **emotion** (primitive)
- Through **analysis** (primitive operation)
- With a **document lens** (perspective)

You get: **A document** (output)

That document is now a primitive to the next thing that looks at it.

---

## Time Is The Substrate

Time is not a layer. Time is the medium everything exists in.

| What Time Does |
|----------------|
| Every primitive has a timestamp |
| Layers operate across time |
| Primitives can be compared across time |
| Time enables "before" and "after" |

**You don't look through time. You look across time.**

---

## Layer Types

| Type | What It Contains | Changes |
|------|------------------|---------|
| **Universal** | True for any human | Rarely |
| **Domain** | Category of seeing | When new domains emerge |
| **Identity** | Specific person's lenses | As the person evolves |

### Universal Layer (Human)

What's true for any human before you know anything specific:
- Has a body
- Has emotions
- Exists in time
- Has needs
- Seeks meaning
- Is finite

### Domain Layers

Categories of seeing:
- **Emotion**: joy, anger, trust, fear...
- **Temporal**: past, present, future, cycles...
- **Social**: connection, belonging, recognition...
- **Cognition**: attention, memory, learning...
- **Body**: energy, sleep, health...
- **Risk**: threats, vulnerabilities, safety...

### Identity Layers

Specific to a person:
- **JeremyLayer**: furnace, truth, sees_systems, night_builder...
- **(Could add)**: FriendLayer, ContactLayer, any person's specific lenses

---

## The Relational Pattern

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   MESSAGE   │────▶│   EMOTION   │────▶│  ANALYSIS   │────▶│  DOCUMENT   │
│  primitive  │     │  primitive  │     │  primitive  │     │   output    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
   timestamp           timestamp           timestamp           timestamp
```

Each step:
1. Takes primitives as input
2. Applies a lens (perspective)
3. Produces a new primitive as output
4. That primitive becomes input to the next step

---

## What Makes This Work

| Principle | Why It Matters |
|-----------|----------------|
| **Everything has an ID** | Traceability back through the chain |
| **Everything has a timestamp** | Position in time |
| **Primitives are relational** | Same data, different meaning to different viewers |
| **Layers are collections** | Organize lenses by domain |
| **Lenses are perspectives** | Individual ways of seeing |

---

## The Question Format

When you want to produce something, ask:

> "When I look at **[primitive A]** and **[primitive B]** through the lens of **[perspective]**, what **[output type]** do I get?"

**Examples:**

| Primitive A | Primitive B | Lens | Output |
|-------------|-------------|------|--------|
| Message | Emotion | Analysis | Insight |
| Insight | JeremyLayer | Document | Report about Jeremy |
| Messages | Timestamps | Temporal | Timeline |
| Emotions | Time range | Aggregate | Emotional profile |

---

## The Simplest Form

```
primitive + primitive + lens = new primitive
```

That's it. Everything is this pattern applied recursively.

---

## Implementation Reference

| Concept | Where It Lives |
|---------|----------------|
| PrimitivesService | `governance/seeing/primitives_service.py` |
| EmotionLayer | `governance/seeing/emotion_layer.py` |
| Layers & Lenses | `governance/seeing/layers.py` |
| ID Service | `core/identity_service/` |

---

**This document is a primitive.**
**It can combine with other primitives.**
**Through a lens, it produces new primitives.**
