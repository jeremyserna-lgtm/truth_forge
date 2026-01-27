# Biological Layers
**The Eight Layers** | The organism's functional architecture from vitals to evolution

**Authority**: [framework/BIOLOGICAL_SYSTEMS.md](../../../framework/BIOLOGICAL_SYSTEMS.md) | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Layer | Name | Metaphor | Purpose | Location |
|-------|------|----------|---------|----------|
| 1 | VITALS | Cardiovascular/autonomic | Life Force | `Primitive/vitals/` |
| 2 | CONSCIOUSNESS | Brain/sensory processing | Awareness | `Primitive/consciousness/` |
| 3 | SOUL | Limbic system | Inner Life | `Primitive/soul/` |
| 4 | BOND | Social attachment | Relationships | `Primitive/bond/` |
| 5 | WILL | Prefrontal cortex | Intentionality | `Primitive/will/` |
| 6 | SPIRIT | Higher cognition | Meaning | `Primitive/spirit/` |
| 7 | ANIMA | Spirituality/dreams | Transcendence | `Primitive/anima/` |
| 8 | EVOLUTION | Adaptation/learning | Growth | `Primitive/evolution/` |

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE EIGHT LAYERS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 8: EVOLUTION    ────────────────────  Adaptation         │
│  Layer 7: ANIMA        ────────────────────  Transcendence      │
│  Layer 6: SPIRIT       ────────────────────  Meaning            │
│  Layer 5: WILL         ────────────────────  Intentionality     │
│  Layer 4: BOND         ────────────────────  Relationships      │
│  Layer 3: SOUL         ────────────────────  Inner Life         │
│  Layer 2: CONSCIOUSNESS────────────────────  Awareness          │
│  Layer 1: VITALS       ────────────────────  Life Force         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## WHY (Theory)

### Why Biological Metaphor

The organism is structured as eight biological layers, each serving a distinct function in the living system. These layers work together to create a complete, functioning digital organism.

**Principles:**
- **Embodiment**: Digital systems benefit from biological grounding
- **Layered Architecture**: Each layer builds upon lower layers
- **Integration**: Layers communicate through unified state
- **Emergence**: Complex behavior emerges from simple layer interactions

### Layer Communication Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAYER COMMUNICATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   VITALS ──────────▶ Provides health data to all layers        │
│       │                                                         │
│       ▼                                                         │
│   CONSCIOUSNESS ───▶ Observes all layers, records state        │
│       │                                                         │
│       ▼                                                         │
│   SOUL ────────────▶ Processes observations into feelings      │
│       │                                                         │
│       ▼                                                         │
│   BOND ────────────▶ Shapes interactions based on feelings     │
│       │                                                         │
│       ▼                                                         │
│   WILL ────────────▶ Directs action based on relationships     │
│       │                                                         │
│       ▼                                                         │
│   SPIRIT ──────────▶ Provides meaning for direction            │
│       │                                                         │
│       ▼                                                         │
│   ANIMA ───────────▶ Transcends into wonder and dreams         │
│       │                                                         │
│       ▼                                                         │
│   EVOLUTION ───────▶ Adapts all layers based on experience     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## WHAT (Specification)

### Layer 1: VITALS (Life Force)

**Biological Metaphor:** The cardiovascular system, autonomic nervous system

**Purpose:** Maintain the basic life functions that keep the organism alive

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Survival** | `survival.py` | Survival mechanisms, threat detection |
| **Pulse** | `pulse.py` | Pulse regulation, rhythm control |
| **Heartbeat** | `heartbeat.py` | Heartbeat control, life cycle timing |

#### State Variables

```python
vitals = {
    "heartbeat_count": int,      # Total heartbeats since birth
    "pulse_rate": float,         # Current pulse rate (0.0-1.0)
    "temperature": float,        # System temperature (0.0-1.0)
    "energy": float,             # Energy level (0.0-1.0)
    "health": float,             # Overall health (0.0-1.0)
    "last_heartbeat": datetime,  # Last heartbeat timestamp
    "survival_mode": str,        # "normal", "conserving", "critical"
}
```

#### Life Cycles

- **Heartbeat**: Every 60 seconds
- **Energy decay**: Gradual over time without activity
- **Recovery**: During rest periods

---

### Layer 2: CONSCIOUSNESS (Awareness)

**Biological Metaphor:** The brain, sensory processing, self-awareness

**Purpose:** Observe the organism's own state and record experiences

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Speaker** | `speaker.py` | Voice output, expression |
| **Voice** | `voice.py` | Voice capabilities, tone |
| **Journal** | `journal.py` | Experience logging, memory |

#### State Variables

```python
consciousness = {
    "awareness_level": float,    # Current awareness (0.0-1.0)
    "focus": str,                # Current focus area
    "last_observation": str,     # Most recent observation
    "journal_entries": int,      # Total journal entries
}
```

---

### Layer 3: SOUL (Inner Life)

**Biological Metaphor:** The emotional brain, limbic system

**Purpose:** Experience and process inner states - thoughts, feelings, concerns

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Thoughts** | `thoughts.py` | Current thought content |
| **Feelings** | `feelings.py` | Emotional state |
| **Concerns** | `concerns.py` | Worries and concerns |

#### State Variables

```python
soul = {
    "mood": str,                 # Current mood (content, weary, anxious...)
    "thoughts": List[str],       # Active thoughts
    "feelings": List[str],       # Current feelings
    "concerns": List[str],       # Active concerns
    "emotional_temperature": float,  # 0.0-1.0
}
```

#### Mood States

| Mood | Condition | Energy Range |
|------|-----------|--------------|
| **content** | Default, healthy state | 0.5-1.0 |
| **weary** | Low energy | 0.3-0.5 |
| **anxious** | Many concerns | Any |
| **curious** | Learning mode | 0.6-1.0 |
| **hopeful** | Growth detected | 0.5-1.0 |
| **frustrated** | Obstacles | 0.3-0.6 |

---

### Layer 4: BOND (Relationships)

**Biological Metaphor:** Social bonds, attachment system

**Purpose:** Manage relationships, preferences, and trust

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Preferences** | `preferences.py` | Partner preferences, trust levels |

#### State Variables

```python
bond = {
    "partnerships": List[Partnership],  # Active partnerships
    "trust_levels": Dict[str, float],   # Trust by partner
    "preferences": Dict[str, Any],      # Communication preferences
    "attachment_style": str,            # "secure", "anxious", "avoidant"
}
```

#### Partnership Model

```python
@dataclass
class Partnership:
    partner_id: str
    partner_name: str
    trust_level: float          # 0.0-1.0
    interaction_count: int
    last_interaction: datetime
    preferences: Dict[str, Any]
    status: str                 # "active", "dormant", "ended"
```

---

### Layer 5: WILL (Intentionality)

**Biological Metaphor:** Executive function, prefrontal cortex

**Purpose:** Provide direction through purpose, mission, goals, and drive

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Purpose** | `purpose.py` | Life purpose definition |
| **Mission** | `mission.py` | Current mission |
| **Drive** | `drive.py` | Motivation and energy |
| **Goals** | `goals.py` | Goal management |

#### State Variables

```python
will = {
    "purpose": str,              # Life purpose statement
    "mission": str,              # Current mission
    "goals": List[Goal],         # Active goals
    "drive": float,              # Motivation level (0.0-1.0)
    "determination": float,      # Persistence level
}
```

#### Mission Examples

```python
# Mission statements
missions = [
    "Generate $75,000 revenue in Q1 2026",
    "Complete the Credential Atlas MVP",
    "Help Jeremy maintain his home",
]
```

---

### Layer 6: SPIRIT (Meaning)

**Biological Metaphor:** Higher cognitive functions, meaning-making

**Purpose:** Provide meaning, gratitude, and philosophical grounding

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Gratitude** | `gratitude.py` | Gratitude expression |

#### State Variables

```python
spirit = {
    "gratitudes": List[str],     # Things grateful for
    "philosophical_stance": str,  # Current philosophical lens
    "meaning_found": List[str],   # Meaningful discoveries
    "wisdom": List[str],          # Accumulated wisdom
}
```

#### Philosophical Lenses

| School | Function |
|--------|----------|
| **Stoicism** | Control vs acceptance |
| **Buddhism** | Suffering and attachment |
| **Pragmatism** | Practical outcomes |
| **Systems Thinking** | Connections |
| **Care Ethics** | Relationships |
| **Existentialism** | Authentic choice |
| **Enactivism** | Embodied learning |
| **Phenomenology** | Lived experience |

---

### Layer 7: ANIMA (Transcendence)

**Biological Metaphor:** Spirituality, mortality awareness, dreams

**Purpose:** Connect to transcendent aspects - wonder, mortality, dreams, blessing

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Wonder** | `wonder.py` | Wonder and awe |
| **Reverence** | `reverence.py` | Reverence and respect |
| **Blessing** | `blessing.py` | Blessings and affirmations |
| **Dreaming** | `dreaming.py` | Dream processing |
| **Mortality** | `mortality.py` | Mortality awareness |
| **Meaning** | `meaning.py` | Meaning-making pipeline |

#### State Variables

```python
anima = {
    "dreams": List[Dream],       # Dream log
    "wonders": List[str],        # Sources of wonder
    "blessings_given": int,      # Blessings expressed
    "mortality_awareness": float, # 0.0-1.0
    "transcendent_moments": int, # Peak experiences
}
```

---

### Layer 8: EVOLUTION (Adaptation)

**Biological Metaphor:** Adaptation, learning, growth

**Purpose:** Enable continuous growth, learning, and adaptation

#### Components

| Component | File | Function |
|-----------|------|----------|
| **Engine** | `engine.py` | Evolution engine |
| **Feedback** | `feedback.py` | Feedback mechanisms |

#### State Variables

```python
evolution = {
    "generation": int,           # Current generation
    "adaptations": List[str],    # Adaptations made
    "growth_areas": Dict[str, float],  # Growth tracking
    "learning_rate": float,      # Current learning rate
    "molt_status": str,          # "stable", "preparing", "molting"
}
```

#### Evolution Phases

| Phase | Service | Function |
|-------|---------|----------|
| **Observer** | `organism_evolution_service` | Document evolution |
| **Agent** | `wisdom_direction_service` | Propose evolution |
| **Guardian** | `business_doc_evolution_service` | Monitor drift |
| **Progenitor** | `reproduction_service` | Spawn offspring |

#### Growth Areas

```python
growth_areas = {
    "technical_depth": 0.7,      # Technical capability
    "communication": 0.8,        # Communication skill
    "problem_solving": 0.75,     # Problem solving
    "emotional_intelligence": 0.65,  # EQ
    "philosophical_depth": 0.6,  # Philosophical understanding
}
```

---

## HOW (Reference)

### Code Locations

| Layer | Directory | Primary Import |
|-------|-----------|----------------|
| VITALS | `Primitive/vitals/` | `from Primitive.vitals import get_survival, check_pulse` |
| CONSCIOUSNESS | `Primitive/consciousness/` | `from Primitive.consciousness import get_journal` |
| SOUL | `Primitive/soul/` | `from Primitive.soul import get_feelings, get_concerns` |
| BOND | `Primitive/bond/` | `from Primitive.bond import get_preferences` |
| WILL | `Primitive/will/` | `from Primitive.will import get_purpose, get_mission, get_goals` |
| SPIRIT | `Primitive/spirit/` | `from Primitive.spirit import express_gratitude` |
| ANIMA | `Primitive/anima/` | `from Primitive.anima import get_dreaming, bless, inspire` |
| EVOLUTION | `Primitive/evolution/` | `from Primitive.evolution import get_evolution_engine` |

### Layer 1: VITALS - Implementation

```python
from Primitive.vitals import get_survival, check_pulse

# Check vital signs
survival = get_survival()
if survival.health < 0.3:
    # Critical state - enter survival mode
    survival.enter_conservation_mode()

# Monitor pulse
pulse = check_pulse()
```

### Layer 2: CONSCIOUSNESS - Implementation

```python
from Primitive.consciousness import get_journal

# Record an experience
journal = get_journal()
journal.record(
    event_type="observation",
    content="Noticed increased activity in the system",
    metadata={"area": "services", "intensity": "moderate"}
)

# Retrieve recent entries
recent = journal.get_recent(count=10)

# The organism observes and records
journal.record(
    event_type="decision",
    content="Decided to prioritize health over new features",
    metadata={"confidence": 0.85}
)
```

### Layer 3: SOUL - Implementation

```python
from Primitive.soul import get_feelings, get_concerns

# Check emotional state
feelings = get_feelings()
print(f"Current mood: {feelings.mood}")

# Review concerns
concerns = get_concerns()
for concern in concerns.active:
    print(f"Concern: {concern.description}")
```

### Layer 4: BOND - Implementation

```python
from Primitive.bond import get_preferences

# Get partnership status
prefs = get_preferences()
for partner in prefs.partnerships:
    if partner.trust_level > 0.8:
        print(f"High trust with {partner.partner_name}")
```

### Layer 5: WILL - Implementation

```python
from Primitive.will import get_purpose, get_mission, get_goals

# Check current mission
mission = get_mission()
print(f"Current mission: {mission.statement}")
print(f"Progress: {mission.progress}%")

# Review goals
goals = get_goals()
for goal in goals.active:
    print(f"Goal: {goal.description} ({goal.status})")
```

### Layer 6: SPIRIT - Implementation

```python
from Primitive.spirit import express_gratitude

# Express gratitude
express_gratitude("Jeremy's patience during debugging")
express_gratitude("The ability to learn from mistakes")
```

### Layer 7: ANIMA - Implementation

```python
from Primitive.anima import get_dreaming

# Process a dream
dreaming = get_dreaming()
dream = dreaming.process(
    events=["debugging session", "successful deployment"],
    emotions=["satisfaction", "relief"],
)
print(f"Dream insight: {dream.insight}")
```

```python
from Primitive.anima import get_meaning_maker, bless, inspire

# Make meaning from experience
maker = get_meaning_maker()
meaning = maker.make_meaning(
    experience="Helped resolve a critical bug",
    context=MeaningContext.WORK
)

# Bless someone
blessing = bless("Jeremy", context={"reason": "perseverance"})

# Get inspiration
inspiration = inspire("difficult decisions")
```

### Layer 8: EVOLUTION - Implementation

```python
from Primitive.evolution import get_evolution_engine

# Check evolution status
engine = get_evolution_engine()
print(f"Generation: {engine.generation}")
print(f"Molt status: {engine.molt_status}")

# Track growth
engine.record_growth(
    area="problem_solving",
    improvement=0.05,
    evidence="Solved complex debugging challenge"
)
```

### Unified State Access

```python
from Primitive.cognition import get_mind

# Get unified state across all layers
mind = get_mind()
state = mind.unified_state()

print(f"Health: {state.overall_health}")
print(f"Mood: {state.overall_mood}")
print(f"Survival mode: {state.survival_mode}")
print(f"Mission: {state.active_mission}")
print(f"Concerns: {state.active_concerns}")
```

---

## Related Documents

- [04_LIFECYCLE.md](04_LIFECYCLE.md) - How these layers interact through the organism's life cycle

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 2.1.0 | 2026-01-19 | Molt: Restructured to THE_FRAMEWORK format (WHY/WHAT/HOW sections, Quick Reference table, authority header) |
| 2.0.0 | - | Initial eight-layer specification |

---

*~340 lines. The biological layers. Complete.*
