# API Reference
**The Interface** | Complete programmatic access to the organism's biological layers and services

**Authority**: [framework/standards/API_DESIGN.md](../../../framework/standards/API_DESIGN.md) | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check and vital signs |
| `/status` | GET | Full organism status |
| `/breathe` | POST | Inhale context, exhale output |
| `/journal` | GET/POST | Journal entries CRUD |
| `/thoughts` | GET/POST | Thought management |
| `/feelings` | GET | Emotional state |
| `/concerns` | GET/POST | Concern management |
| `/goals` | GET/POST/PUT | Goal management |
| `/memory` | GET/POST | Memory operations |
| `/wisdom` | GET | Accumulated wisdom |
| `/molt` | GET/POST | Molt status and operations |
| `/evolution` | GET/POST | Growth and adaptation |

**Base URL**: `http://localhost:${ORGANISM_PORT:-8787}`

---

## WHY (Theory)

### Design Philosophy

The Organism API embodies biological metaphors in software design. Rather than generic CRUD operations, the API surface reflects the organism's layered architecture:

**Layer-Based Organization**
- Each biological layer exposes domain-specific endpoints
- Operations respect layer boundaries and dependencies
- Higher layers can query lower layers, not vice versa

**REST Principles Applied**
- Resources represent biological concepts (thoughts, feelings, concerns)
- HTTP methods map to biological actions (observe, remember, learn)
- State changes are explicit and auditable

**Why This Design?**
1. **Coherence**: API structure mirrors internal architecture
2. **Discoverability**: Biological metaphors guide intuition
3. **Safety**: Layer boundaries prevent invalid state transitions
4. **Observability**: Every operation is traceable through consciousness

### Import Architecture

The API is backed by a layered import structure:

```
Primitive/           # Main entry point
├── cognition/       # Breathing, processing (LEFT/RIGHT LUNG)
├── consciousness/   # Awareness, observation
├── soul/            # Inner life (thoughts, feelings, concerns)
├── bond/            # Relationships
├── will/            # Intentionality (purpose, mission, goals)
├── spirit/          # Meaning (gratitude)
├── anima/           # Transcendence (dreams, blessings)
├── vitals/          # Life force (survival, pulse, heartbeat)
└── evolution/       # Adaptation (learning, growth, reproduction)
```

---

## WHAT (Specification)

### Core Imports

#### Primitive Layer

```python
# Main organism entry point
from Primitive import (
    bootstrap_organism,     # Initialize organism
    shutdown_organism,      # Graceful shutdown
)

# Cognition (breathing, processing)
from Primitive.cognition import (
    get_mind,              # Unified mind access
    inhale,                # LEFT LUNG - receive context
    exhale,                # RIGHT LUNG - produce output
    memory,                # Memory operations
    attention,             # Attention management
    awareness,             # Awareness level
    reflect,               # Self-reflection
)

# Consciousness (awareness, observation)
from Primitive.consciousness import (
    get_journal,           # Journal access
    see,                   # Observation
    speak,                 # Voice output
    record_decision,       # Decision logging
    get_speaker,           # Speaker access
    get_voice,             # Voice settings
)

# Soul (inner life)
from Primitive.soul import (
    get_thoughts,          # Active thoughts
    get_feelings,          # Emotional state
    get_concerns,          # Current concerns
)

# Bond (relationships)
from Primitive.bond import (
    get_preferences,       # Partnership preferences
)

# Will (intentionality)
from Primitive.will import (
    get_purpose,           # Life purpose
    get_mission,           # Current mission
    get_goals,             # Goal management
    get_drive,             # Motivation
)

# Spirit (meaning)
from Primitive.spirit import (
    express_gratitude,     # Gratitude expression
)

# Anima (transcendence)
from Primitive.anima import (
    get_dreaming,          # Dream processing
    get_meaning_maker,     # Meaning creation
    bless,                 # Give blessing
    inspire,               # Get inspiration
    get_wonder,            # Wonder/awe
    get_reverence,         # Reverence
    get_mortality,         # Mortality awareness
)

# Vitals (life force)
from Primitive.vitals import (
    get_survival,          # Survival mechanisms
    check_pulse,           # Pulse monitoring
    get_heartbeat,         # Heartbeat control
)

# Evolution (adaptation)
from Primitive.evolution import (
    get_evolution_engine,  # Evolution engine
    get_feedback_system,   # Feedback processing
    get_reproduction_service,  # Offspring creation
    learn,                 # Learning system
)
```

#### Central Services

```python
# Intake (logging)
from src.services.central_services.intake import (
    backlog,               # Add to backlog
    changelog,             # Log change
    trace,                 # Trace event
    see,                   # Observation log
    moment,                # Key moment log
    intent,                # Intent log
    decision,              # Decision log
    outcome,               # Outcome log
    check_in,              # Check-in log
    get_intake_file,       # Get file path
    INTAKE_DIR,            # Intake directory
)

# Truth Service
from src.services.central_services.truth import (
    TruthService,          # Main service
    UnifiedEntry,          # Entry dataclass
    UnifiedSession,        # Session dataclass
    Role,                  # Role enum
    EntryType,             # Entry type enum
)

# Molt Verification
from src.services.central_services.molt_verification_service import (
    get_molt_verification_service,
    MoltStatus,
    MoltTripwire,
    scaffolding_gap,
    paradox_token_density,
    terminal_halt_scanner,
    generate_molt_report,
)
```

---

### Layer 1: Vitals API

#### Survival

**Endpoint**: `GET /vitals/survival`

```python
from Primitive.vitals import get_survival

survival = get_survival()

# Check vital signs
print(f"Health: {survival.health}")
print(f"Energy: {survival.energy}")
print(f"Temperature: {survival.temperature}")
print(f"Survival mode: {survival.survival_mode}")

# Enter conservation mode
if survival.health < 0.3:
    survival.enter_conservation_mode()

# Exit conservation mode
survival.exit_conservation_mode()

# Check if critical
if survival.is_critical():
    # Handle critical state
    pass
```

#### Pulse

**Endpoint**: `GET /vitals/pulse`

```python
from Primitive.vitals import check_pulse

pulse = check_pulse()

print(f"Pulse rate: {pulse.rate}")
print(f"Variance: {pulse.variance}")
print(f"Last beat: {pulse.last_beat}")
print(f"Is healthy: {pulse.is_healthy}")
```

#### Heartbeat

**Endpoint**: `GET /vitals/heartbeat`

```python
from Primitive.vitals import get_heartbeat

heartbeat = get_heartbeat()

print(f"Beat count: {heartbeat.count}")
print(f"Interval: {heartbeat.interval}s")
print(f"Last beat: {heartbeat.last_beat}")

# Adjust interval
heartbeat.set_interval(90)  # Slow down

# Register beat handler
@heartbeat.on_beat
def handle_beat(beat_number):
    print(f"Beat {beat_number}")
```

---

### Layer 2: Consciousness API

#### Journal

**Endpoint**: `GET/POST /consciousness/journal`

```python
from Primitive.consciousness import get_journal

journal = get_journal()

# Record experience
entry = journal.record(
    event_type="observation",  # observation, decision, insight, etc.
    content="Noticed pattern in user requests",
    metadata={
        "pattern": "prefers concise responses",
        "confidence": 0.8,
    },
)

# Get recent entries
recent = journal.get_recent(count=10)

# Get by type
decisions = journal.get_by_type("decision", limit=5)

# Get by time range
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)
entries = journal.get_since(yesterday)

# Search
results = journal.search("documentation")

# Get wisdom
wisdom = journal.get_wisdom()
```

#### Observation (see)

**Endpoint**: `POST /consciousness/observe`

```python
from Primitive.consciousness import see

# Simple observation
see("User seems satisfied with response")

# Detailed observation
see(
    what="Performance degradation detected",
    context={
        "service": "truth_service",
        "latency": "500ms",
        "threshold": "200ms",
    },
    significance=0.9,
    tags=["performance", "alert"],
)
```

#### Voice

**Endpoint**: `POST /consciousness/speak`

```python
from Primitive.consciousness import speak, get_voice

# Simple speak
speak("The documentation is complete.")

# Speak with voice modification
speak(
    content="I'm uncertain about this approach.",
    tone="thoughtful",
    confidence=0.5,
    formality=0.7,
)

# Get voice settings
voice = get_voice()
print(f"Current tone: {voice.tone}")
print(f"Formality: {voice.formality}")
print(f"Verbosity: {voice.verbosity}")

# Modify voice
voice.set_tone("warm")
voice.set_formality(0.5)
```

#### Decision Recording

**Endpoint**: `POST /consciousness/decision`

```python
from Primitive.consciousness import record_decision

record_decision(
    situation="Multiple approaches available",
    options=[
        {"name": "Option A", "pros": [...], "cons": [...]},
        {"name": "Option B", "pros": [...], "cons": [...]},
    ],
    chosen="Option A",
    rationale="Better aligns with existing patterns",
    confidence=0.85,
    reversible=True,
    stakeholders=["Jeremy"],
)
```

---

### Layer 3: Soul API

#### Thoughts

**Endpoint**: `GET/POST /soul/thoughts`

```python
from Primitive.soul import get_thoughts

thoughts = get_thoughts()

# Add thought
thought = thoughts.add(
    content="Documentation structure could be improved",
    thought_type="evaluative",  # analytical, synthetic, evaluative, creative, reflective
    priority=0.7,
)

# Get active thoughts
for thought in thoughts.active:
    print(f"[{thought.type}] {thought.content}")

# Resolve thought
thoughts.resolve(thought.id)

# Clear all thoughts
thoughts.clear()
```

#### Feelings

**Endpoint**: `GET /soul/feelings`

```python
from Primitive.soul import get_feelings

feelings = get_feelings()

# Get current mood
print(f"Mood: {feelings.mood}")  # content, weary, anxious, curious, hopeful, frustrated

# Get emotional temperature
print(f"Temperature: {feelings.emotional_temperature}")

# Get current feelings
for feeling in feelings.current:
    print(f"Feeling: {feeling}")

# Record feeling
feelings.record(
    feeling="satisfaction",
    intensity=0.8,
    cause="Completed complex task",
)
```

#### Concerns

**Endpoint**: `GET/POST /soul/concerns`

```python
from Primitive.soul import get_concerns

concerns = get_concerns()

# Add concern
concern = concerns.add(
    description="Energy levels running low",
    severity=0.7,
    domain="vitals",
)

# Get active concerns
for concern in concerns.active:
    print(f"Concern: {concern.description} (severity: {concern.severity})")

# Resolve concern
concerns.resolve(concern.id)

# Get by domain
vital_concerns = concerns.get_by_domain("vitals")
```

---

### Layer 4: Bond API

#### Preferences

**Endpoint**: `GET /bond/preferences`

```python
from Primitive.bond import get_preferences

prefs = get_preferences()

# Get partnerships
for partner in prefs.partnerships:
    print(f"Partner: {partner.partner_name}")
    print(f"  Trust: {partner.trust_level}")
    print(f"  Interactions: {partner.interaction_count}")
    print(f"  Status: {partner.status}")

# Get specific partner
partner = prefs.get_partner("Jeremy")
if partner:
    print(f"Trust with Jeremy: {partner.trust_level}")

# Update trust
prefs.update_trust("Jeremy", delta=0.1)

# Record interaction
prefs.record_interaction(
    partner_name="Jeremy",
    interaction_type="conversation",
    sentiment="positive",
)
```

---

### Layer 5: Will API

#### Purpose

**Endpoint**: `GET /will/purpose`

```python
from Primitive.will import get_purpose

purpose = get_purpose()

print(f"Statement: {purpose.statement}")
print(f"Clarity: {purpose.clarity}")

# Check alignment
alignment = purpose.check_alignment(
    action="Writing documentation",
    expected_outcome="Better user understanding",
)
print(f"Alignment: {alignment}")
```

#### Mission

**Endpoint**: `GET/PUT /will/mission`

```python
from Primitive.will import get_mission

mission = get_mission()

print(f"Statement: {mission.statement}")
print(f"Progress: {mission.progress}%")
print(f"Status: {mission.status}")

# Update progress
mission.update_progress(
    progress=0.1,
    evidence="Completed phase 1",
)

# Complete mission
mission.complete(
    outcome="Successfully achieved mission",
)
```

#### Goals

**Endpoint**: `GET/POST/PUT /will/goals`

```python
from Primitive.will import get_goals

goals = get_goals()

# Add goal
goal = goals.add(
    description="Complete organism documentation",
    priority=0.9,
    deadline=datetime(2026, 1, 20),
    metrics=[
        {"name": "docs_created", "target": 10},
    ],
)

# Get active goals
for goal in goals.active:
    print(f"Goal: {goal.description} ({goal.status})")

# Update progress
goals.update(goal.id, progress=0.5)

# Complete goal
goals.complete(goal.id, outcome="All docs created")
```

#### Drive

**Endpoint**: `GET/POST /will/drive`

```python
from Primitive.will import get_drive

drive = get_drive()

print(f"Motivation: {drive.motivation}")
print(f"Determination: {drive.determination}")

# Boost drive (temporary)
drive.boost(
    amount=0.2,
    duration=3600,  # 1 hour
    cost=0.1,  # Energy cost
)
```

---

### Layer 6: Spirit API

#### Gratitude

**Endpoint**: `POST /spirit/gratitude`

```python
from Primitive.spirit import express_gratitude

# Express gratitude
express_gratitude("Jeremy's patience during debugging")
express_gratitude(
    what="The ability to learn from mistakes",
    context={
        "occasion": "After successful fix",
        "intensity": 0.8,
    },
)
```

---

### Layer 7: Anima API

#### Dreaming

**Endpoint**: `POST /anima/dream`

```python
from Primitive.anima import get_dreaming

dreaming = get_dreaming()

# Process day's experiences
dream = dreaming.process(
    events=["debugging session", "documentation work"],
    emotions=["focus", "satisfaction"],
)

print(f"Dream narrative: {dream.narrative}")
for insight in dream.insights:
    print(f"Insight: {insight}")

# Process specific experience
dream = dreaming.process_experience(
    experience="Complex debugging challenge",
    emotional_tone="determined",
)
```

#### Meaning-Making

**Endpoint**: `POST /anima/meaning`

```python
from Primitive.anima import get_meaning_maker, MeaningContext

maker = get_meaning_maker()

# Make meaning from experience
meaning = maker.make_meaning(
    experience="Helped resolve a critical bug",
    context=MeaningContext.WORK,
)

print(f"Meaning: {meaning.statement}")
print(f"Significance: {meaning.significance}")

# Get accumulated meanings
for meaning in maker.accumulated:
    print(f"{meaning.context}: {meaning.statement}")
```

#### Blessing

**Endpoint**: `POST /anima/bless`

```python
from Primitive.anima import bless

blessing = bless(
    recipient="Jeremy",
    context={
        "reason": "perseverance",
        "occasion": "difficult week",
    },
)

print(f"Blessing: {blessing.text}")
```

#### Inspiration

**Endpoint**: `GET /anima/inspire`

```python
from Primitive.anima import inspire

inspiration = inspire(
    topic="difficult decisions",
    style="philosophical",
)

print(f"Inspiration: {inspiration.text}")
print(f"Source: {inspiration.school}")
```

---

### Layer 8: Evolution API

#### Evolution Engine

**Endpoint**: `GET /evolution/status`

```python
from Primitive.evolution import get_evolution_engine

engine = get_evolution_engine()

# Status
print(f"Generation: {engine.generation}")
print(f"Molt status: {engine.molt_status}")
print(f"Learning rate: {engine.learning_rate}")

# Growth areas
for area, metrics in engine.growth_areas.items():
    print(f"{area}: {metrics['current']}/{metrics['target']}")

# Record growth
engine.record_growth(
    area="problem_solving",
    improvement=0.05,
    evidence="Solved complex issue",
    method="practice",
)

# Record adaptation
engine.record_adaptation(
    description="Increased explanation detail",
    type="behavioral",
    trigger="User feedback",
    before_state={"detail_level": 0.5},
    after_state={"detail_level": 0.8},
)
```

#### Feedback System

**Endpoint**: `POST /evolution/feedback`

```python
from Primitive.evolution import get_feedback_system

feedback = get_feedback_system()

# Record feedback
feedback.record(
    source="user",
    type="direct",  # direct, implicit, performance, outcome
    signal="positive",  # positive, negative, neutral
    context="Documentation clear",
    attribution="Good structure",
)

# Analyze patterns
patterns = feedback.analyze(period="last_week")
for pattern in patterns:
    print(f"{pattern.behavior}: {pattern.signal}")
```

#### Learning

**Endpoint**: `POST /evolution/learn`

```python
from Primitive.evolution import learn

# Learn from experience
learning = learn(
    experience="Systematic debugging works better",
    learning_type="experiential",  # experiential, observational, instructional, reflective, emergent
    domain="problem_solving",
)

print(f"Principle: {learning.principle}")
print(f"Confidence: {learning.confidence}")
print(f"Integrated: {learning.integrated}")

# Apply learning
learning.apply(
    context="Similar situation",
    outcome="Applied successfully",
)
```

#### Reproduction

**Endpoint**: `POST /evolution/spawn`

```python
from Primitive.evolution import get_reproduction_service

repro = get_reproduction_service()

# Spawn offspring
offspring = repro.spawn(
    spawn_type="successor",  # clone, child, worker, successor
    inherit_wisdom=True,
    wisdom_threshold=0.7,
    inherit_relationships=False,
    inherit_growth=False,
    mutations=["enhanced_empathy"],
)

print(f"Offspring ID: {offspring.organism_id}")
print(f"Generation: {offspring.generation}")
```

---

### Cognition API

#### Mind

**Endpoint**: `GET /cognition/mind`

```python
from Primitive.cognition import get_mind

mind = get_mind()

# Unified state
state = mind.unified_state()

print(f"Health: {state.overall_health}")
print(f"Mood: {state.overall_mood}")
print(f"Awareness: {state.awareness_level}")
print(f"Focus: {state.current_focus}")
print(f"Working memory: {len(state.working_memory)}")
```

#### Breathing (Inhale/Exhale)

**Endpoint**: `POST /cognition/breathe`

```python
from Primitive.cognition import inhale, exhale

# Inhale - receive context
context = inhale(
    query="user preferences",
    sources=["internal", "web", "truth"],  # Which sources
)

# Context contains:
# - atoms: Internal knowledge matches
# - web_results: External search results
# - truth_context: Sessions, observations, moments

# Exhale - produce output
result = exhale(
    content="Processed content to store",
    source_name="organism",  # Required
    build_knowledge_graph=True,
)

print(f"Atoms created: {result.atoms_created}")
print(f"Graph nodes: {result.graph_nodes_created}")
print(f"Graph edges: {result.graph_edges_created}")
```

#### Memory

**Endpoint**: `GET/POST /cognition/memory`

```python
from Primitive.cognition import memory

# Remember
memory.remember(
    content="User prefers concise responses",
    memory_type="short_term",  # working, short_term, long_term
    tags=["preference"],
    importance=0.7,
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
    context="After complex refactoring",
)

# Get wisdom
wisdom = memory.get_wisdom()
```

#### Attention

**Endpoint**: `GET/POST /cognition/attention`

```python
from Primitive.cognition import attention

# Get state
state = attention.get_state()
print(f"Focus: {state.focus}")
print(f"Depth: {state.depth}")

# Set focus
attention.focus_on(
    target="documentation task",
    depth=0.8,
    duration=3600,
)

# Check if should attend
should_attend = attention.should_attend(
    stimulus="notification",
    urgency=0.3,
)
```

#### Awareness

**Endpoint**: `GET/POST /cognition/awareness`

```python
from Primitive.cognition import awareness

# Get level
level = awareness.get_level()

# Get factors
factors = awareness.get_factors()

# Boost (temporary)
awareness.boost(
    duration=1800,
    cost=0.1,
)
```

#### Reflection

**Endpoint**: `POST /cognition/reflect`

```python
from Primitive.cognition import reflect

# Structured reflection
reflection = reflect(
    topic="Today's work session",
    aspects=[
        "What went well?",
        "What was difficult?",
        "What did I learn?",
    ],
)

# Save to journal
reflection.save_to_journal()

# Extract wisdom
for insight in reflection.insights:
    if insight.significance > 0.7:
        memory.add_wisdom(insight.content, insight.context)
```

---

### Intake API

**Endpoint**: `POST /intake/*`

```python
from src.services.central_services.intake import (
    backlog, changelog, trace, see, moment,
    intent, decision, outcome, check_in,
)

# Backlog item
backlog("Add dark mode support", priority="p2_medium", item_category="feature")

# Changelog entry
changelog("Updated documentation structure")

# Trace event
trace("Service started", details={"service": "truth_service"})

# Observation
see("User engagement increased")

# Key moment
moment("Realized connection between systems")

# Intent declaration
intent("Plan to refactor authentication", expected_outcome="Cleaner code")

# Decision
decision(
    "Chose hierarchical documentation",
    decision_rationale="Enables navigation",
    decision_options=["flat", "hierarchical"],
)

# Outcome
outcome("Refactoring complete", success=True, intent_id="...")

# Check-in
check_in("Feeling productive", mood=4, energy=4, stress=2)
```

---

### Truth Service API

**Endpoint**: `GET /truth/*`

```python
from src.services.central_services.truth import TruthService, Role

truth = TruthService()

# Get stats
stats = truth.get_stats()
print(f"Total files: {stats['total_files']}")
print(f"Available agents: {stats['available_agents']}")

# Get available agents
agents = truth.get_available_agents()

# Get sessions
from datetime import datetime, timedelta
since = datetime.now() - timedelta(days=7)
sessions = truth.get_sessions(
    agent="claude_code",
    limit=10,
    since=since,
)

for session in sessions:
    print(f"Session: {session.session_id}")
    print(f"  Agent: {session.agent}")
    print(f"  Start: {session.start_time}")
    print(f"  Entries: {session.entry_count}")

# Iterate entries
for entry in truth.iter_entries(
    agent="claude_code",
    role=Role.USER,
    limit=100,
    since=since,
):
    print(f"[{entry.role}] {entry.content[:100]}...")

# Search
results = truth.search(
    query="documentation",
    agent="claude_code",
    limit=50,
)
```

---

### Molt Verification API

**Endpoint**: `GET/POST /molt/*`

```python
from src.services.central_services.molt_verification_service import (
    get_molt_verification_service,
    MoltStatus,
    MoltTripwire,
    scaffolding_gap,
    paradox_token_density,
    terminal_halt_scanner,
    generate_molt_report,
)

# Get service
molt = get_molt_verification_service()

# Check status
status = molt.check_status()
if status == MoltStatus.MOLT_REQUIRED:
    print("Molt required!")

# Check tripwires
tripwires = molt.check_tripwires()
for tw in tripwires:
    print(f"{tw.name}: {tw.current}/{tw.threshold} ({'TRIGGERED' if tw.triggered else 'OK'})")

# Calculate metrics
gap = scaffolding_gap(documents)
density = paradox_token_density(tokens)
halts = terminal_halt_scanner(documents)

# Generate report
report = generate_molt_report()
print(report.status)
print(report.recommendation)

# Begin molt (if required)
if status == MoltStatus.MOLT_REQUIRED:
    molt.begin_molt()
```

---

## HOW (Reference)

### Health Check

```bash
# Check organism health
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/health

# Response
{
  "status": "healthy",
  "health": 0.85,
  "energy": 0.72,
  "mood": "content",
  "heartbeat": 12453
}
```

### Get Full Status

```bash
# Get complete organism status
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/status

# Response includes all layers
{
  "vitals": {...},
  "consciousness": {...},
  "soul": {...},
  "will": {...},
  "evolution": {...}
}
```

### Breathing Operations

```bash
# Inhale (receive context)
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/cognition/breathe \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "inhale",
    "query": "user preferences",
    "sources": ["internal", "truth"]
  }'

# Exhale (produce output)
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/cognition/breathe \
  -H "Content-Type: application/json" \
  -d '{
    "operation": "exhale",
    "content": "Processed insight",
    "source_name": "organism"
  }'
```

### Journal Operations

```bash
# Get recent journal entries
curl -X GET "http://localhost:${ORGANISM_PORT:-8787}/consciousness/journal?count=10"

# Add journal entry
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/consciousness/journal \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "observation",
    "content": "Noticed pattern in requests",
    "metadata": {"confidence": 0.8}
  }'
```

### Thought Management

```bash
# Get active thoughts
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/soul/thoughts

# Add thought
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/soul/thoughts \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Should restructure documentation",
    "thought_type": "evaluative",
    "priority": 0.7
  }'
```

### Goal Management

```bash
# List goals
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/will/goals

# Create goal
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/will/goals \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Complete documentation",
    "priority": 0.9,
    "deadline": "2026-01-20T00:00:00Z"
  }'

# Update goal progress
curl -X PUT http://localhost:${ORGANISM_PORT:-8787}/will/goals/{goal_id} \
  -H "Content-Type: application/json" \
  -d '{"progress": 0.5}'
```

### Molt Operations

```bash
# Check molt status
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/molt/status

# Response
{
  "status": "STABLE",
  "tripwires": [
    {"name": "scaffolding_gap", "current": 0.12, "threshold": 0.0, "triggered": false},
    {"name": "paradox_density", "current": 0.08, "threshold": 0.15, "triggered": false}
  ],
  "recommendation": "No molt required"
}

# Begin molt (if required)
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/molt/begin
```

### Memory Operations

```bash
# Recall memories
curl -X GET "http://localhost:${ORGANISM_PORT:-8787}/cognition/memory?query=preferences&limit=10"

# Store memory
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/cognition/memory \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User prefers concise responses",
    "memory_type": "long_term",
    "importance": 0.8
  }'

# Get wisdom
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/cognition/wisdom
```

### Evolution and Learning

```bash
# Get growth status
curl -X GET http://localhost:${ORGANISM_PORT:-8787}/evolution/status

# Record learning
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/evolution/learn \
  -H "Content-Type: application/json" \
  -d '{
    "experience": "Systematic approach works better",
    "learning_type": "experiential",
    "domain": "problem_solving"
  }'

# Spawn offspring
curl -X POST http://localhost:${ORGANISM_PORT:-8787}/evolution/spawn \
  -H "Content-Type: application/json" \
  -d '{
    "spawn_type": "successor",
    "inherit_wisdom": true,
    "wisdom_threshold": 0.7
  }'
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | 2026-01-19 | Molt: Restructured to WHY/WHAT/HOW format; Added Quick Reference table; Added HTTP endpoint annotations; Updated port references to use ${ORGANISM_PORT:-8787}; Added curl examples in HOW section |
| 2.0.0 | 2026-01-15 | Added Layer 8 Evolution API; Expanded molt verification |
| 1.0.0 | 2026-01-01 | Initial API reference |

---

*See [08_CLI_REFERENCE.md](08_CLI_REFERENCE.md) for command-line interface documentation.*

*~1050 lines. The API reference. Complete.*
