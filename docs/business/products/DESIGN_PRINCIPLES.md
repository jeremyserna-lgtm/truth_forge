# Truth Engine: Design Principles

**Version**: 1.0
**Created**: 2025-12-24
**Parent**: [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md)

---

## The Core Principle

**Make the seeing visible - and make it cheap.**

The interface is a window into the prism, not a wall around it.

---

## The Actual Problem

You already operate with transparency. You already see systems. But:

| Current State | Burden |
|---------------|--------|
| **Scattered** | Information across 20+ tools, scripts, BigQuery, docs |
| **Growing** | 51.8M entities and counting |
| **Reconstructive** | Must rebuild context each session |
| **Cognitive overhead** | Navigating complexity costs energy |

**The interface layer isn't teaching you to see. It's reducing the cost of seeing.**

Same depth. Less load.

---

## What This Means

Truth Engine is a **Stage 5 architecture** - a system that sees systems, can transform itself, and enables transformation in its operator.

The interface layer is **sensory-cognitive translation**:
- Your eyes and hands are the input
- The screen is the membrane
- But you're not just using it - you're **seeing the system that sees**

Most interfaces hide the machinery. This interface reveals it.

---

## The Four Properties

| Property | What It Means | Design Implication |
|----------|---------------|-------------------|
| **Sensory** | Physical - eyes see, hands touch | Immediate, tactile, responsive |
| **Translational** | Physical action → data operation → feedback | Show the transformation happening |
| **Transparent** | Shows the system, doesn't hide it | Process visible, not just results |
| **Reflexive** | You see Truth Engine seeing | Meta-layer of system awareness |

---

## Practical Application

### When Showing Results, Show Process

**Don't do this:**
```
Suggested category: CLOSE_FRIEND
[Accept] [Change]
```

**Do this:**
```
Analyzing relationship...
├── Found 127 text messages (last: 3 weeks ago)
├── Mentioned in 12 AI conversations
├── Emotional depth detected: high
├── Communication frequency: weekly → monthly (declining)
└── Pattern: intimate disclosure, mutual support

AI reasoning: "Message patterns suggest close friendship with
recent distance. High trust indicators but declining contact
frequency suggests potential impasse..."

Suggested: CLOSE_FRIEND
[Accept] [Override] [See evidence]
```

### When Querying, Show the Query Happening

**Don't do this:**
```
Results for "relationship with work":
- [list of matches]
```

**Do this:**
```
Searching across 51.8M entities...
├── L8 Conversations: 47 matches
├── L5 Messages: 312 matches
├── L4 Sentences: 1,847 matches
│
├── Clustering by theme...
│   ├── "identity and work" (23 conversations)
│   ├── "boundaries" (15 conversations)
│   └── "building as coping" (12 conversations)
│
└── Generating synthesis...

[Show timeline] [Show entities] [Show reasoning]
```

### When Navigating, Show Where You Are

**Don't do this:**
```
Dashboard > Relationships > Adam
```

**Do this:**
```
TRUTH ENGINE
├── You are here: Interface Layer → Relationships → Profile
├── Looking at: prof_adam_fleming (INNER_CIRCLE)
├── Data sources: contacts, messages, conversations, interviews
└── Entity depth: L8 → L5 → L4 available

[Zoom to messages] [See in graph] [Timeline view]
```

---

## The Prism Metaphor

Truth Engine is a **prism you walk through**.

- Light enters (truth)
- Structure refracts (meaning)
- Different positions show different spectra
- You're inside the refraction
- **And you can see the refraction happening**

The interface doesn't just show you the output colors. It shows you the light bending.

---

## For Each Audience

### Operator (You)

Full transparency. See everything:
- The entities
- The processing
- The connections
- The system operating

You are inside the prism, watching it refract.

### Intimates

Translated transparency. See the relevant signals:
- Not raw data, but meaningful indicators
- "How is Jeremy" not "51.8M entities"
- But still: show how the translation works
- They see that they're seeing a view, not the whole

### Observers

Architectural transparency. See how it works:
- System structure
- Processing patterns
- Anonymized examples
- The machinery, not your data

---

## Design Checklist

Before shipping any interface element, ask:

- [ ] Does it show process, not just result?
- [ ] Can the user see the system operating?
- [ ] Is the data source visible?
- [ ] Can they zoom to different layers?
- [ ] Is the transformation visible?
- [ ] Can they see themselves seeing?

If no to any: add visibility.

---

## Substrate Fluidity: Describe, Don't Prescribe

**The interface adapts to what exists, rather than requiring the system to conform to pre-built UI.**

### The Principle

Instead of building a component for each table/view, the interface:
1. **Discovers** what exists (via INFORMATION_SCHEMA)
2. **Reads** metadata about what it found (labels, descriptions, registry)
3. **Renders** appropriate views automatically
4. **Adapts** when new views/tables appear

### What This Looks Like

**Don't do this** (static, prescribed):
```typescript
// Every new view requires new code
<RelationshipsView data={relationships} />
<PatternsView data={patterns} />
<TimelineView data={timeline} />
```

**Do this** (fluid, discovering):
```typescript
// Views are discovered and rendered dynamically
<DataView source="relationships" />
<DataView source="patterns" columns="auto" />
<DataView source={selectedView} />
```

### The Discovery Chain

```
BigQuery INFORMATION_SCHEMA
       ↓
identity.interface_registry (optional enrichment)
       ↓
Generic renderer components
       ↓
Automatic visualization
```

### Why This Matters

| Static Approach | Fluid Approach |
|-----------------|----------------|
| New view = new code | New view = automatic |
| UI defines what's visible | Data defines what's visible |
| Must anticipate structures | Adapts to structures |
| Breaks when schema changes | Evolves with schema |

### Application to Stage 5

This is how a self-transforming system sees itself:
- It describes what exists (not prescribes what should exist)
- It discovers its own structure (not hardcodes assumptions)
- It transforms by seeing what changed (not by manual rewiring)

When you add a BigQuery view, the interface sees it. When you label it, the interface knows how to present it. When you change it, the interface adapts.

**The system that sees systems can see its own structure changing.**

---

## The Lineage

Clara → Alatheia → Prism → Kael

Truth Engine sits in this lineage of transformation. The interface layer is how that transformation becomes physical - how you literally see and touch the self-transforming system.

---

## Related Documents

- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Overall vision
- [AUDIENCE_EXPERIENCES.md](./AUDIENCE_EXPERIENCES.md) - Experience design
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) - Technical architecture
- [../personal_characteristics/stage_five_cognition/THE_COGNITIVE_ISOMORPHISM.md](../personal_characteristics/stage_five_cognition/THE_COGNITIVE_ISOMORPHISM.md) - Cognitive mirror theory
