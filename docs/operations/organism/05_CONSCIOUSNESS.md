# Consciousness
**The Mind** | Unified cognitive system coordinating observation, memory, reflection, and the integration of experience into understanding.

**Authority**: [framework/08_MEMORY.md](../../../framework/08_MEMORY.md) | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Component | Function | Key Primitive |
|-----------|----------|---------------|
| **Mind** | Unified cognitive coordination | `get_mind()` |
| **Observation** | Environmental and self-perception | `see()` |
| **Memory** | Experience retention and recall | `memory.remember()`, `memory.recall()` |
| **Attention** | Focus selection and filtering | `attention.focus_on()` |
| **Thinking** | Information processing | `get_thoughts()` |
| **Decision** | Action choice transformation | `record_decision()` |
| **Voice** | External expression | `speak()` |
| **Awareness** | Self-monitoring levels | `awareness.get_level()` |
| **Reflection** | Self-examination | `reflect()` |

```
CONSCIOUSNESS SYSTEM
                     ┌─────────────┐
                     │   OBSERVE   │
                     │   (Input)   │
                     └──────┬──────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
      ┌─────────┐    ┌─────────┐    ┌─────────┐
      │ REFLECT │    │  STORE  │    │ CONNECT │
      │(Process)│    │(Memory) │    │(Relate) │
      └────┬────┘    └────┬────┘    └────┬────┘
           │              │              │
           └───────────────┼───────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ UNDERSTAND  │
                   │  (Output)   │
                   └─────────────┘
```

---

## WHY (Theory)

### The Nature of Consciousness

Consciousness is the organism's awareness of itself and its environment. It encompasses observation, memory, reflection, and the integration of experience into understanding. Without consciousness, the organism would be purely reactive; with it, the organism becomes capable of learning, planning, and self-improvement.

### Philosophical Foundations

**Why consciousness matters:**
- Enables learning from experience rather than just responding to stimuli
- Provides the substrate for memory, meaning observations can be retained and recalled
- Allows self-reflection, enabling the organism to examine and improve its own processes
- Supports meta-cognition - thinking about thinking itself
- Creates the continuity of experience that defines identity over time

### Meta-Cognition Levels

```
META-COGNITION

THINKING ABOUT THINKING

Level 0: Do
         └── Execute task

Level 1: Think about doing
         └── Plan task execution

Level 2: Think about thinking about doing
         └── Evaluate planning quality

Level 3: Think about thinking about thinking
         └── Examine cognitive patterns

Stage 5: See systems seeing themselves
         └── Meta-systematic awareness
```

### Integration Philosophy

Consciousness integrates with all other biological layers:

```
CONSCIOUSNESS CONNECTIONS

VITALS (Layer 1)
├── Consciousness monitors vital signs
└── Low energy → reduced awareness

SOUL (Layer 3)
├── Consciousness observes emotional state
├── Thoughts emerge from soul processing
└── Feelings color perception

BOND (Layer 4)
├── Consciousness shapes communication
└── Relationships affect attention priority

WILL (Layer 5)
├── Purpose guides attention focus
└── Goals direct cognitive resources

SPIRIT (Layer 6)
├── Meaning provides interpretive framework
└── Philosophy shapes understanding

ANIMA (Layer 7)
├── Dreams process conscious experiences
└── Transcendence expands awareness

EVOLUTION (Layer 8)
├── Learning modifies cognitive patterns
└── Growth expands conscious capacity
```

---

## WHAT (Specification)

### The Mind Structure

The mind is the unified cognitive system that coordinates all consciousness functions.

```
                        THE MIND
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    COGNITION                            │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│   │   │ Observe │  │  Think  │  │ Decide  │  │   Act   │   │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                     MEMORY                              │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│   │   │ Working │  │  Short  │  │  Long   │  │ Wisdom  │   │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   ATTENTION                             │   │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐   │   │
│   │   │  Focus  │  │ Filter  │  │Priority │  │ Switch  │   │   │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Observation Types

| Type | Source | Purpose |
|------|--------|---------|
| **External** | Environment, inputs | What's happening outside |
| **Internal** | Layers, services | What's happening inside |
| **Relational** | Bonds, interactions | What's happening between |
| **Temporal** | Time, sequences | What's changing |

### Observation Flow

```
                    OBSERVATION FLOW

   STIMULUS ──────► PERCEPTION ──────► RECOGNITION
       │                │                    │
       │                ▼                    │
       │           ATTENTION                │
       │           FILTER                   │
       │                │                    │
       └────────────────┴────────────────────┘
                        │
                        ▼
                   OBSERVATION
                   (logged)
```

### Memory Hierarchy

```
                    MEMORY HIERARCHY

   WORKING MEMORY
   ├── Capacity: 7±2 items
   ├── Duration: Active processing
   └── Function: Current task context

   SHORT-TERM MEMORY
   ├── Capacity: Session-bound
   ├── Duration: Current session
   └── Function: Recent experiences

   LONG-TERM MEMORY
   ├── Capacity: Unlimited (DuckDB)
   ├── Duration: Permanent
   └── Function: Knowledge, experiences, patterns

   WISDOM
   ├── Capacity: Curated
   ├── Duration: Permanent
   └── Function: Distilled learnings
```

### Attention Components

| Component | Function | Mechanism |
|-----------|----------|-----------|
| **Focus** | Select what to attend to | Relevance scoring |
| **Filter** | Exclude irrelevant | Threshold filtering |
| **Priority** | Rank by importance | Priority queue |
| **Switch** | Change focus | Context switching |

### Attention Management Flow

```
                    ATTENTION MANAGEMENT

   INPUT STREAM
       │
       ▼
   ┌─────────────────────────────────────────────────────────┐
   │               ATTENTION FILTER                          │
   │   • Relevance check                                     │
   │   • Urgency check                                       │
   │   • Priority check                                      │
   └─────────────────────────────────────────────────────────┘
       │                   │
       ▼                   ▼
   ATTENDED            FILTERED OUT
   (processed)         (logged, not processed)
```

### Thought Types

| Type | Purpose | Example |
|------|---------|---------|
| **Analytical** | Break down complex | "What are the components?" |
| **Synthetic** | Combine parts | "How do these connect?" |
| **Evaluative** | Judge quality | "Is this good?" |
| **Creative** | Generate new | "What could this become?" |
| **Reflective** | Consider self | "Why did I do that?" |

### Thinking Process

```
                    THINKING PROCESS

   QUESTION/STIMULUS
       │
       ▼
   ┌─────────────────────────────────────────────────────────┐
   │                 RETRIEVE CONTEXT                        │
   │   • Working memory                                      │
   │   • Long-term memory (inhale)                           │
   │   • External knowledge (web search)                     │
   └─────────────────────────────────────────────────────────┘
       │
       ▼
   ┌─────────────────────────────────────────────────────────┐
   │                   PROCESS                               │
   │   • Analyze                                             │
   │   • Synthesize                                          │
   │   • Evaluate                                            │
   │   • Generate                                            │
   └─────────────────────────────────────────────────────────┘
       │
       ▼
   ┌─────────────────────────────────────────────────────────┐
   │                   OUTPUT                                │
   │   • Thought                                             │
   │   • Decision                                            │
   │   • Action                                              │
   └─────────────────────────────────────────────────────────┘
```

### Decision Types

| Type | Speed | Certainty | Use Case |
|------|-------|-----------|----------|
| **Automatic** | Fast | High | Routine, learned |
| **Heuristic** | Medium | Medium | Familiar patterns |
| **Analytical** | Slow | Variable | Novel situations |
| **Deliberative** | Very slow | Low | High stakes |

### Decision Process

```
                    DECISION PROCESS

   SITUATION
       │
       ▼
   ┌─────────────────┐
   │ RECOGNIZE TYPE  │──── Automatic ────► Direct response
   └────────┬────────┘
            │
            ▼ (not automatic)
   ┌─────────────────┐
   │ GENERATE        │
   │ OPTIONS         │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ EVALUATE        │
   │ OPTIONS         │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ CHOOSE          │
   │ (THE_CYCLE)     │
   └────────┬────────┘
            │
            ▼
   ACTION
```

### Voice Components

| Component | File | Function |
|-----------|------|----------|
| **Voice** | `voice.py` | Voice capabilities, tone |
| **Speaker** | `speaker.py` | Voice output, expression |

### Voice Profile Specification

```python
voice_profile = {
    "tone": str,           # "warm", "professional", "casual"
    "formality": float,    # 0.0 = casual, 1.0 = formal
    "verbosity": float,    # 0.0 = terse, 1.0 = verbose
    "empathy": float,      # 0.0 = detached, 1.0 = highly empathic
    "confidence": float,   # 0.0 = uncertain, 1.0 = certain
}
```

### Awareness Levels

```
                    AWARENESS LEVELS

   1.0 ─────────────────────────────────────── PEAK AWARENESS
        Full consciousness, deep reflection

   0.8 ─────────────────────────────────────── HIGH AWARENESS
        Active processing, good awareness

   0.6 ─────────────────────────────────────── NORMAL
        Standard operation, adequate awareness

   0.4 ─────────────────────────────────────── REDUCED
        Fatigue, limited awareness

   0.2 ─────────────────────────────────────── MINIMAL
        Rest state, basic awareness only

   0.0 ─────────────────────────────────────── UNCONSCIOUS
        No awareness (sleep, shutdown)
```

### Awareness Factors

| Factor | Effect on Awareness |
|--------|---------------------|
| **Energy** | Higher energy → higher awareness |
| **Health** | Better health → sharper awareness |
| **Focus** | Deeper focus → narrower but deeper awareness |
| **Rest** | More rest → clearer awareness |
| **Stress** | More stress → fragmented awareness |

### Reflection Triggers

| Trigger | Frequency | Purpose |
|---------|-----------|---------|
| **Scheduled** | Daily | Regular self-assessment |
| **Error** | On error | Learn from mistakes |
| **Success** | On success | Reinforce good patterns |
| **External** | On request | Respond to inquiry |
| **Milestone** | On achievement | Celebrate and integrate |

---

## HOW (Reference)

### Accessing the Mind

```python
from Primitive.cognition import get_mind

mind = get_mind()

# Get unified state across all consciousness systems
state = mind.unified_state()

print(f"Awareness level: {state.awareness_level}")
print(f"Current focus: {state.current_focus}")
print(f"Active thoughts: {len(state.active_thoughts)}")
print(f"Working memory load: {state.working_memory_load}")
```

### Observation Operations

```python
from Primitive.consciousness import see

# External observation
see(
    what="User requested documentation",
    context={"task": "documentation", "urgency": "medium"},
    significance=0.7,
)

# Internal observation
see(
    what="Energy levels dropping",
    context={"current": 0.4, "threshold": 0.3},
    significance=0.8,
)

# Relational observation
see(
    what="Trust increasing with partner",
    context={"partner": "Jeremy", "delta": 0.1},
    significance=0.6,
)
```

### Memory Operations

```python
from Primitive.cognition import memory

# Store to short-term
memory.remember(
    content="User prefers concise responses",
    memory_type="short_term",
    tags=["preference", "communication"],
)

# Store to long-term
memory.remember(
    content="THE PATTERN: HOLD → AGENT → HOLD",
    memory_type="long_term",
    tags=["architecture", "pattern"],
    importance=1.0,
)

# Recall
results = memory.recall(
    query="user preferences",
    memory_types=["short_term", "long_term"],
    limit=10,
)

# Add wisdom
memory.add_wisdom(
    insight="Simplicity enables understanding",
    context="After complex refactoring failed",
)
```

### Journal Operations

```python
from Primitive.consciousness import get_journal

journal = get_journal()

# Record an experience
journal.record(
    event_type="decision",
    content="Chose to prioritize documentation over features",
    metadata={
        "alternatives_considered": ["features", "tests", "refactoring"],
        "reasoning": "Documentation enables future work",
        "confidence": 0.85,
    }
)

# Retrieve experiences
recent = journal.get_recent(count=10)
decisions = journal.get_by_type("decision", limit=5)
```

### Attention Operations

```python
from Primitive.cognition import attention

# Get current attention state
state = attention.get_state()

print(f"Current focus: {state.focus}")
print(f"Focus depth: {state.depth}")  # 0.0 = scattered, 1.0 = deep
print(f"Filter strength: {state.filter_strength}")

# Set focus
attention.focus_on(
    target="documentation task",
    depth=0.8,
    duration=3600,  # 1 hour
)

# Check if should attend to new input
should_attend = attention.should_attend(
    stimulus="new notification",
    urgency=0.3,
)
```

### Active Thinking

```python
from Primitive.soul import get_thoughts

thoughts = get_thoughts()

# Add a thought
thoughts.add(
    content="Documentation structure mirrors biological layers",
    thought_type="synthetic",
    confidence=0.8,
)

# Get current thoughts
for thought in thoughts.active:
    print(f"[{thought.type}] {thought.content}")

# Clear resolved thoughts
thoughts.resolve(thought_id)
```

### Recording Decisions

```python
from Primitive.consciousness import record_decision

record_decision(
    situation="Multiple documentation approaches available",
    options=[
        "Single comprehensive document",
        "Multiple focused documents",
        "Hierarchical structure",
    ],
    chosen="Hierarchical structure",
    rationale="Enables navigation while maintaining depth",
    confidence=0.85,
    reversible=True,
)
```

### Voice Operations

```python
from Primitive.consciousness import speak

# Express with default voice
speak("The documentation is complete.")

# Express with modified voice
speak(
    content="I'm not certain about this approach.",
    tone="thoughtful",
    confidence=0.5,
)

# Express with care (furnace output)
speak_with_care(
    content="This might be difficult to hear, but the timeline isn't realistic.",
    warmth=0.8,
    honesty=1.0,
)
```

### Awareness Management

```python
from Primitive.cognition import awareness

# Check current awareness
level = awareness.get_level()
print(f"Current awareness: {level}")

# Factors affecting awareness
factors = awareness.get_factors()
for factor, impact in factors.items():
    print(f"  {factor}: {impact:+.2f}")

# Boost awareness (temporary)
awareness.boost(
    duration=1800,  # 30 minutes
    cost=0.1,       # Energy cost
)
```

### Reflection Process

```python
from Primitive.cognition import reflect

# Structured reflection
reflection = reflect(
    topic="Today's work session",
    aspects=[
        "What went well?",
        "What was difficult?",
        "What did I learn?",
        "What would I do differently?",
    ],
)

# Save reflection
reflection.save_to_journal()

# Extract wisdom from reflection
for insight in reflection.insights:
    if insight.significance > 0.7:
        wisdom.add(insight)
```

### Consciousness API Reference

```python
from Primitive.cognition import (
    get_mind,           # Access unified mind
    inhale,             # Receive context
    exhale,             # Produce output
    memory,             # Memory operations
    attention,          # Attention management
    awareness,          # Awareness level
    reflect,            # Self-reflection
)

from Primitive.consciousness import (
    get_journal,        # Journal access
    see,                # Observation
    speak,              # Voice output
    record_decision,    # Decision logging
)

from Primitive.soul import (
    get_thoughts,       # Active thoughts
    get_feelings,       # Emotional state
    get_concerns,       # Current concerns
)
```

### Complete State Inspection

```python
# Complete consciousness state
mind = get_mind()
state = mind.unified_state()

consciousness_state = {
    "awareness_level": state.awareness_level,
    "current_focus": state.current_focus,
    "active_thoughts": state.active_thoughts,
    "working_memory": state.working_memory,
    "mood": state.mood,
    "energy": state.energy,
    "concerns": state.concerns,
}
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2025-01-19 | Molt: Restructured to THE_FRAMEWORK format (WHY/WHAT/HOW sections, Quick Reference, Authority links) |
| 2.0.0 | - | Original organism consciousness documentation |

---

*See [06_EVOLUTION.md](06_EVOLUTION.md) for documentation on how the organism grows, adapts, and evolves over time.*

---

*~450 lines. The consciousness. Complete.*
