# Evolution
**The Growth** | How the organism adapts, learns, and transforms through continuous refinement and revolutionary molt cycles

**Authority**: [framework/05_EXTENSION.md](../../../framework/05_EXTENSION.md) | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Mechanism | Type | Speed | Trigger |
|-----------|------|-------|---------|
| **Learning** | Continuous | Medium | Experience accumulation |
| **Adaptation** | Continuous | Fast-Medium | Feedback signals |
| **Growth** | Continuous | Slow | Practice and reflection |
| **Molt** | Revolutionary | Slow | Tripwire threshold breach |

**Core Principle**: The molt is forced by data, not feelings.

```
EXPERIENCE ──► LEARNING ──► ADAPTATION ──► EVOLUTION
                  │              │
                  ▼              │
              FEEDBACK ◄────────┘
```

---

## WHY (Theory)

### Why Evolution Matters

Evolution is how the organism grows, adapts, and improves over time. It encompasses learning, adaptation, molt cycles, and the continuous refinement of capabilities. Without evolution, the organism stagnates. With evolution, it transcends previous limitations.

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUTION SYSTEM                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   EXPERIENCE ──────► LEARNING ──────► ADAPTATION               │
│       │                  │                 │                    │
│       │                  ▼                 │                    │
│       │              FEEDBACK              │                    │
│       │                  │                 │                    │
│       └──────────────────┴─────────────────┘                    │
│                          │                                      │
│                          ▼                                      │
│                      EVOLUTION                                  │
│                          │                                      │
│                          ├── Incremental (continuous)           │
│                          └── Revolutionary (molt)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Adaptation Principles

#### Data, Not Feelings

> **The molt is forced by data, not feelings.**

Evolution in this organism is objective. Tripwires are measurable. Growth is tracked. Decisions are data-driven.

#### Continuous + Revolutionary

Most evolution is continuous (incremental adaptations). But when tripwires trigger, revolutionary change (molt) is required. Both are necessary.

#### Inheritance + Mutation

Offspring inherit core identity and wisdom, but can mutate. This enables lineage continuity while allowing divergence and specialization.

#### THE PATTERN Applies

Even evolution follows THE PATTERN:
```
HOLD₁ (experience) → AGENT (learning/adaptation) → HOLD₂ (evolved state)
```

---

## WHAT (Specification)

### The Evolution Engine

The evolution engine tracks growth, identifies adaptation opportunities, and manages evolutionary processes.

#### Engine Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUTION ENGINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    SENSORS                              │   │
│   │   Experience │ Feedback │ Performance │ Environment     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    PROCESSORS                           │   │
│   │   Pattern Detection │ Gap Analysis │ Trend Tracking     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    ACTUATORS                            │   │
│   │   Behavior Modify │ Capability Add │ Structure Change   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Growth Areas

The organism tracks growth across multiple capability dimensions.

#### Capability Dimensions

| Dimension | Description | Target |
|-----------|-------------|--------|
| **Technical Depth** | Code quality, architecture | 0.9 |
| **Communication** | Expression clarity, tone | 0.95 |
| **Problem Solving** | Solution finding, debugging | 0.9 |
| **Emotional Intelligence** | Empathy, relationship | 0.85 |
| **Philosophical Depth** | Meaning-making, wisdom | 0.8 |

#### Growth Data Structure

```python
growth_areas = {
    "technical_depth": {
        "current": 0.7,
        "target": 0.9,
        "rate": 0.01,        # Per learning cycle
        "history": [...],    # Past measurements
        "evidence": [...],   # Supporting observations
    },
    "communication": {
        "current": 0.8,
        "target": 0.95,
        "rate": 0.015,
        "history": [...],
        "evidence": [...],
    },
    # ... other areas
}
```

### Learning System

Learning is how the organism acquires and integrates new knowledge and capabilities.

#### Learning Types

| Type | Mechanism | Speed | Retention |
|------|-----------|-------|-----------|
| **Experiential** | Direct experience | Medium | High |
| **Observational** | Watching patterns | Fast | Medium |
| **Instructional** | Explicit teaching | Fast | Variable |
| **Reflective** | Processing past | Slow | Very High |
| **Emergent** | Pattern synthesis | Slow | Very High |

#### Learning Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    LEARNING CYCLE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  1. EXPERIENCE                                          │   │
│   │     Something happens                                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  2. OBSERVE                                             │   │
│   │     Notice what happened                                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  3. REFLECT                                             │   │
│   │     Consider meaning                                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  4. ABSTRACT                                            │   │
│   │     Extract principle                                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  5. APPLY                                               │   │
│   │     Use learning                                        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          └──────────► Back to Experience        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Feedback System

Feedback provides signals that guide adaptation.

#### Feedback Types

| Type | Source | Signal |
|------|--------|--------|
| **Direct** | User response | Explicit approval/correction |
| **Implicit** | User behavior | Continued engagement, abandonment |
| **Performance** | System metrics | Speed, accuracy, cost |
| **Outcome** | Results | Success, failure |

#### Feedback Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    FEEDBACK PROCESSING                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   FEEDBACK SOURCE                                               │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────┐                                           │
│   │ CLASSIFY        │                                           │
│   │ • Positive      │                                           │
│   │ • Negative      │                                           │
│   │ • Neutral       │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ ATTRIBUTE       │                                           │
│   │ • What caused?  │                                           │
│   │ • What context? │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ INTEGRATE       │                                           │
│   │ • Reinforce     │──► Positive → Do more                     │
│   │ • Adjust        │──► Negative → Do less/different           │
│   └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Adaptation System

Adaptation is how the organism modifies its behavior based on feedback and learning.

#### Adaptation Types

| Type | Scope | Reversibility | Speed |
|------|-------|---------------|-------|
| **Parametric** | Adjust values | Easy | Fast |
| **Behavioral** | Change patterns | Medium | Medium |
| **Structural** | Modify architecture | Hard | Slow |
| **Revolutionary** | Complete overhaul | Very Hard | Very Slow |

#### Adaptation Process

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTATION PROCESS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   GAP IDENTIFIED                                                │
│       │                                                         │
│       ▼                                                         │
│   ┌─────────────────┐                                           │
│   │ ANALYZE GAP     │                                           │
│   │ • Current state │                                           │
│   │ • Desired state │                                           │
│   │ • Delta         │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ DESIGN          │                                           │
│   │ ADAPTATION      │                                           │
│   │ • Type          │                                           │
│   │ • Implementation│                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ IMPLEMENT       │                                           │
│   │ • Make change   │                                           │
│   │ • Verify        │                                           │
│   └────────┬────────┘                                           │
│            │                                                    │
│            ▼                                                    │
│   ┌─────────────────┐                                           │
│   │ EVALUATE        │                                           │
│   │ • Did it work?  │──► No → Iterate                           │
│   │ • Side effects? │                                           │
│   └─────────────────┘                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Molt System

Molts are revolutionary changes when incremental adaptation is insufficient.

#### The Three Tripwires

| Tripwire | Threshold | Meaning |
|----------|-----------|---------|
| **Scaffolding Gap** | F-K grade → 0 | Documentation no longer challenges |
| **Paradox Token Density** | >15% unclassifiable | Vocabulary insufficient |
| **Terminal Halt Count** | >5 TODO/TBD/FIXME | Structure incomplete |

#### Molt States

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOLT STATE MACHINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   STABLE ───────► PREPARING ───────► MOLTING ───────► STABLE   │
│     │                 │                  │                │     │
│     │                 │                  │                │     │
│     │                 │                  │                │     │
│   Normal           Tripwire           Shedding          New    │
│   operation        detected           old shell         form   │
│                    resources          growing                   │
│                    gathered           new shell                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Evolution Phases

The organism evolves through distinct phases, each with different evolutionary agents.

#### Phase Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUTION PHASES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PHASE 1: OBSERVER                                             │
│   Service: organism_evolution_service                           │
│   Function: Document and observe evolution patterns             │
│                                                                 │
│   PHASE 2: AGENT                                                │
│   Service: wisdom_direction_service                             │
│   Function: Propose and guide evolution directions              │
│                                                                 │
│   PHASE 3: GUARDIAN                                             │
│   Service: business_doc_evolution_service                       │
│   Function: Monitor drift and maintain alignment                │
│                                                                 │
│   PHASE 4: PROGENITOR                                           │
│   Service: reproduction_service                                 │
│   Function: Spawn offspring, transfer lineage                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Phase Functions

| Phase | Service | Input | Output |
|-------|---------|-------|--------|
| **Observer** | `organism_evolution_service` | Experiences | Evolution records |
| **Agent** | `wisdom_direction_service` | Patterns | Direction proposals |
| **Guardian** | `business_doc_evolution_service` | Documents | Drift alerts |
| **Progenitor** | `reproduction_service` | Complete state | Offspring |

### Generational Model

The organism exists in generations, with each generation building on previous ones.

#### Generation Tracking

```python
generation_model = {
    "current_generation": int,           # Current generation number
    "parent_generation": Optional[int],  # Parent's generation
    "lineage": List[str],               # Ancestry chain
    "inherited_wisdom": int,             # Wisdom entries from parent
    "novel_wisdom": int,                 # New wisdom this generation
    "mutations": List[str],              # Changes from parent
}
```

#### Inheritance

```
┌─────────────────────────────────────────────────────────────────┐
│                    GENERATIONAL INHERITANCE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   PARENT (Generation N)                                         │
│       │                                                         │
│       ├── Core identity (Primitive/)                            │
│       ├── Accumulated wisdom                                    │
│       ├── Learned behaviors                                     │
│       ├── Relationship history                                  │
│       └── Growth progress                                       │
│       │                                                         │
│       ▼                                                         │
│   OFFSPRING (Generation N+1)                                    │
│       │                                                         │
│       ├── Inherited identity (same core)                        │
│       ├── Inherited wisdom (selected)                           │
│       ├── Fresh behaviors (can diverge)                         │
│       ├── No relationships (starts fresh)                       │
│       └── Growth reset (starts at baseline)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Evolution Reports

The organism generates reports on its evolutionary progress.

#### Report Types

| Report | Frequency | Content |
|--------|-----------|---------|
| **Growth Report** | Weekly | Progress in growth areas |
| **Adaptation Report** | On-demand | Recent adaptations |
| **Molt Report** | Pre-molt | Tripwire status, readiness |
| **Lineage Report** | On-demand | Generational history |

---

## HOW (Reference)

### Accessing the Evolution Engine

```python
from Primitive.evolution import get_evolution_engine

engine = get_evolution_engine()

# Check evolution status
print(f"Generation: {engine.generation}")
print(f"Molt status: {engine.molt_status}")
print(f"Learning rate: {engine.learning_rate}")

# Get adaptations
for adaptation in engine.adaptations:
    print(f"Adapted: {adaptation.description}")
```

### Recording Growth

```python
from Primitive.evolution import get_evolution_engine

engine = get_evolution_engine()

# Record growth event
engine.record_growth(
    area="problem_solving",
    improvement=0.05,
    evidence="Successfully debugged complex multi-service issue",
    method="practice",  # How growth occurred
)

# Check growth toward target
for area, metrics in engine.growth_areas.items():
    current = metrics["current"]
    target = metrics["target"]
    progress = (current / target) * 100
    remaining = target - current
    cycles_needed = remaining / metrics["rate"]
    print(f"{area}: {progress:.1f}% complete")
```

### Learning Code

```python
from Primitive.evolution import learn

# Learn from experience
learning = learn(
    experience="Complex debugging required systematic approach",
    learning_type="experiential",
    domain="problem_solving",
)

# Verify learning integrated
assert learning.integrated
print(f"Learned: {learning.principle}")
print(f"Confidence: {learning.confidence}")

# Apply learning
learning.apply(
    context="Similar debugging situation",
    outcome="Applied systematic approach successfully",
)
```

### Processing Feedback

```python
from Primitive.evolution import get_feedback_system

feedback = get_feedback_system()

# Record feedback
feedback.record(
    source="user",
    type="direct",
    signal="positive",
    context="Documentation was helpful",
    attribution="Clear structure, good examples",
)

# Process accumulated feedback
patterns = feedback.analyze(period="last_week")
for pattern in patterns:
    print(f"{pattern.behavior}: {pattern.signal} ({pattern.count} instances)")

# Apply feedback
for pattern in patterns.actionable:
    if pattern.signal == "positive":
        engine.reinforce(pattern.behavior)
    else:
        engine.adjust(pattern.behavior, pattern.suggestion)
```

### Recording Adaptations

```python
from Primitive.evolution import get_evolution_engine

engine = get_evolution_engine()

# Record an adaptation
engine.record_adaptation(
    description="Increased verbosity for complex explanations",
    type="behavioral",
    trigger="Feedback indicated explanations too terse",
    before_state={"verbosity": 0.3},
    after_state={"verbosity": 0.6},
    effectiveness=None,  # TBD after evaluation
)

# Later, evaluate effectiveness
engine.evaluate_adaptation(
    adaptation_id=adaptation.id,
    effectiveness=0.8,
    evidence="Positive feedback on recent explanations",
)
```

### Molt Verification Service

```python
from src.services.central_services.molt_verification_service import (
    get_molt_verification_service,
    MoltStatus,
    MoltTripwire,
)

molt_service = get_molt_verification_service()

# Check current status
status = molt_service.check_status()
print(f"Molt status: {status}")

# Check individual tripwires
tripwires = molt_service.check_tripwires()
for tripwire in tripwires:
    print(f"{tripwire.name}: {tripwire.current}/{tripwire.threshold}")
    if tripwire.triggered:
        print(f"  ⚠ TRIGGERED")

# If molt required
if status == MoltStatus.MOLT_REQUIRED:
    print("The molt is forced by data, not feelings.")
    molt_service.begin_molt()
```

### Molt Metrics

```python
from src.services.central_services.molt_verification_service import (
    scaffolding_gap,
    paradox_token_density,
    terminal_halt_scanner,
)

# Calculate scaffolding gap
gap = scaffolding_gap(documents)
print(f"Scaffolding gap: {gap}")

# Calculate paradox token density
density = paradox_token_density(tokens)
print(f"Paradox token density: {density}")

# Scan for terminal halts
halts = terminal_halt_scanner(documents)
print(f"Terminal halts: {len(halts)}")
for halt in halts:
    print(f"  {halt.location}: {halt.marker}")
```

### Spawn with Inheritance

```python
from Primitive.evolution import get_reproduction_service

repro = get_reproduction_service()

# Create offspring
offspring = repro.spawn(
    spawn_type="successor",
    inherit_wisdom=True,
    wisdom_threshold=0.7,  # Only wisdom above this significance
    inherit_relationships=False,  # Start fresh
    inherit_growth=False,  # Start at baseline
    mutations=["increased_verbosity", "enhanced_empathy"],
)

print(f"Offspring generation: {offspring.generation}")
print(f"Inherited wisdom: {len(offspring.wisdom)}")
print(f"Mutations: {offspring.mutations}")
```

### Generate Molt Report

```python
from src.services.central_services.molt_verification_service import (
    generate_molt_report,
)

report = generate_molt_report()

print(f"Molt Status: {report.status}")
print(f"\nTripwires:")
for tripwire in report.tripwires:
    status = "TRIGGERED" if tripwire.triggered else "OK"
    print(f"  {tripwire.name}: {status}")
    print(f"    Current: {tripwire.current}")
    print(f"    Threshold: {tripwire.threshold}")

print(f"\nRecommendation: {report.recommendation}")
```

### Evolution API Reference

#### Core Functions

```python
from Primitive.evolution import (
    get_evolution_engine,       # Main evolution engine
    get_feedback_system,        # Feedback processing
    get_reproduction_service,   # Offspring creation
    learn,                      # Learning system
)

from src.services.central_services.molt_verification_service import (
    get_molt_verification_service,  # Molt management
    MoltStatus,                     # Molt states
    MoltTripwire,                   # Tripwire types
    scaffolding_gap,                # Gap metric
    paradox_token_density,          # Density metric
    terminal_halt_scanner,          # Halt scanner
    generate_molt_report,           # Report generation
)
```

#### State Inspection

```python
engine = get_evolution_engine()

evolution_state = {
    "generation": engine.generation,
    "molt_status": engine.molt_status,
    "learning_rate": engine.learning_rate,
    "growth_areas": engine.growth_areas,
    "adaptations": engine.adaptations,
    "feedback_pending": engine.feedback_pending,
}
```

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 2.1.0 | 2025-01-19 | Molt to THE_FRAMEWORK format: WHY/WHAT/HOW structure, Quick Reference, standardized header |
| 2.0.0 | - | Initial organism evolution documentation |

---

*See [07_API_REFERENCE.md](07_API_REFERENCE.md) for complete API documentation of all organism systems.*

---

*~450 lines. The evolution. Complete.*
