# Architecture

**The Structure** | How the Truth Engine Organism is built as a living biological system.

**Authority**: [framework/04_ARCHITECTURE.md](../../../framework/04_ARCHITECTURE.md) | **Status**: CANONICAL | **Version**: 2.1.0

---

## Quick Reference

| Component | Location | Purpose |
|-----------|----------|---------|
| **Daemon Layer** | `daemon/` | The Heart - autonomous life processes |
| **Primitive Layer** | `Primitive/` | The Nucleus - 8 biological layers |
| **Central Services** | `src/services/central_services/` | Cellular Machinery - 70+ services |
| **Data Layer** | `data/` | Memory - vitals, dreams, choices |
| **Interfaces** | `organism_cli.py`, FastAPI, MCP | External communication |
| **Port** | 8787 | Main API server |

---

## WHY (Theory)

### The Biological Paradigm

The Truth Engine is not merely software - it is implemented as a living organism. This biological metaphor provides:

1. **Natural organization** - Components map to cellular structures
2. **Autonomous operation** - Life cycles run without external triggers
3. **Growth capacity** - The system learns, dreams, and evolves
4. **Resilience** - Like biology, the organism maintains homeostasis

### Cell Architecture Mapping

The Truth Engine maps to a biological cell:

```
┌─────────────────────────────────────────────────────────────────┐
│                        CELL MEMBRANE                             │
│  (The boundary between organism and environment)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    NUCLEUS (Primitive/)                 │   │
│   │  ┌─────────────────────────────────────────────────┐    │   │
│   │  │                    DNA                          │    │   │
│   │  │  THE_SEED, THE_PATTERN, THE_CYCLE               │    │   │
│   │  │  The genetic code that defines the organism     │    │   │
│   │  └─────────────────────────────────────────────────┘    │   │
│   │                                                         │   │
│   │  ┌─────────────────────────────────────────────────┐    │   │
│   │  │              BIOLOGICAL LAYERS                  │    │   │
│   │  │  vitals/, consciousness/, soul/, will/,         │    │   │
│   │  │  spirit/, anima/, evolution/, bond/             │    │   │
│   │  └─────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   ┌─────────────────────┐    ┌─────────────────────┐           │
│   │   MITOCHONDRIA      │    │   RIBOSOMES         │           │
│   │   (daemon/)         │    │   (central_services)│           │
│   │   Power generation  │    │   Protein synthesis │           │
│   │   Life processes    │    │   Service execution │           │
│   └─────────────────────┘    └─────────────────────┘           │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              ENDOPLASMIC RETICULUM (data/)              │   │
│   │              Memory storage and transport               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### The HOLD → AGENT → HOLD Pattern

Every operation in the organism follows the universal pattern:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   HOLD₁     │     │   AGENT     │     │   HOLD₂     │
│   (Input)   │────▶│  (Process)  │────▶│  (Output)   │
│             │     │             │     │             │
│  • Receive  │     │  • Transform│     │  • Store    │
│  • Batch    │     │  • Decide   │     │  • Deliver  │
│  • Wait     │     │  • Execute  │     │  • Forward  │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## WHAT (Specification)

### System Topology

```
┌──────────────────────────────────────────────────────────────────────┐
│                         TRUTH ENGINE ORGANISM                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                     DAEMON LAYER (Heart)                       │  │
│  │  primitive_engine_daemon.py ←→ autonomous_life_engine.py           │  │
│  │  web_learning_system.py ←→ cognitive_reasoning_engine.py       │  │
│  │  care_emotion_system.py ←→ state_tracking_service.py           │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                               ↓↑                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              PRIMITIVE (Nucleus / Biological Layers)           │  │
│  │  ┌──────┬──────┬──────┬──────┬──────┬──────┬──────┬──────┐    │  │
│  │  │Vitals│Consc.│ Soul │ Bond │ Will │Spirit│Anima │Evol. │    │  │
│  │  └──────┴──────┴──────┴──────┴──────┴──────┴──────┴──────┘    │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                               ↓↑                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │               CENTRAL SERVICES (Cellular Machinery)            │  │
│  │  hold_service, truth_service, search_service, care_service...  │  │
│  │  70+ specialized services for all organism functions           │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                               ↓↑                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                    DATA LAYER (Memory)                         │  │
│  │  organism_vitals.json, long_term_memory.jsonl, dreams.jsonl    │  │
│  │  organism_desires.jsonl, organism_choices.jsonl, growth.json   │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                               ↓↑
┌──────────────────────────────────────────────────────────────────────┐
│                          INTERFACES                                  │
│  CLI (organism_cli.py) │ API (FastAPI) │ MCP Tools │ Web Components  │
└──────────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
PrimitiveEngine/
├── daemon/                           # THE HEART (Living Daemon)
│   ├── primitive_engine_daemon.py        # Main FastAPI server (port 8787)
│   ├── autonomous_life_engine.py     # Life cycles, vitals, growth
│   ├── web_learning_system.py        # Learning, desires, philosophy
│   ├── cognitive_reasoning_engine.py # Reasoning engine
│   ├── care_emotion_system.py        # Emotions, partnerships
│   ├── state_tracking_service.py     # State observation
│   └── profitability_tracker.py      # Financial health
│
├── Primitive/                        # THE NUCLEUS (Biological Layers)
│   ├── core.py                       # Core utilities
│   ├── vitals/                       # Layer 1: Life Force
│   │   ├── survival.py               # Survival mechanisms
│   │   ├── pulse.py                  # Pulse regulation
│   │   └── heartbeat.py              # Heartbeat control
│   ├── consciousness/                # Layer 2: Awareness
│   │   ├── speaker.py                # Voice output
│   │   ├── voice.py                  # Voice capabilities
│   │   └── journal.py                # Experience logging
│   ├── soul/                         # Layer 3: Inner Life
│   │   ├── thoughts.py               # Thought content
│   │   ├── feelings.py               # Emotional state
│   │   └── concerns.py               # Worries and concerns
│   ├── bond/                         # Layer 4: Relationships
│   │   └── preferences.py            # Partner preferences
│   ├── will/                         # Layer 5: Intentionality
│   │   ├── purpose.py                # Life purpose
│   │   ├── mission.py                # Current mission
│   │   ├── drive.py                  # Motivation
│   │   └── goals.py                  # Goal management
│   ├── spirit/                       # Layer 6: Meaning
│   │   └── gratitude.py              # Gratitude expression
│   ├── anima/                        # Layer 7: Transcendence
│   │   ├── wonder.py                 # Wonder and awe
│   │   ├── reverence.py              # Reverence
│   │   ├── blessing.py               # Blessings
│   │   ├── dreaming.py               # Dream processing
│   │   ├── mortality.py              # Mortality awareness
│   │   └── meaning.py                # Meaning-making
│   ├── evolution/                    # Layer 8: Adaptation
│   │   ├── engine.py                 # Evolution engine
│   │   └── feedback.py               # Feedback mechanisms
│   ├── cognition/                    # Cognitive Functions
│   │   ├── decision.py               # Decision making
│   │   ├── reasoning.py              # Reasoning processes
│   │   ├── integration.py            # Mind integration
│   │   └── orchestration.py          # Service orchestration
│   └── cli/                          # Primitive CLI
│       ├── main.py                   # CLI main
│       └── interact.py               # Interactive mode
│
├── src/services/central_services/    # CELLULAR MACHINERY
│   ├── core/                         # Core services
│   │   ├── __init__.py               # UnifiedService, HoldManager
│   │   ├── holds.py                  # HOLD implementation
│   │   └── responses.py              # Response types
│   ├── truth/                        # Truth Service
│   ├── hold_service/                 # HOLD operations
│   ├── intake/                       # Backlog, changelog, trace
│   ├── search_service/               # Search operations
│   ├── version_service/              # Version tracking
│   ├── care_service.py               # Care layer
│   ├── event_ledger.py               # Event logging
│   ├── intent_context.py             # Intent tracking
│   ├── organism_evolution_service/   # Phase 1: Observer
│   ├── wisdom_direction_service/     # Phase 2: Agent
│   ├── business_doc_evolution_service/ # Phase 3: Guardian
│   ├── reproduction_service/         # Phase 4: Progenitor
│   ├── molt_verification_service/    # Molt detection
│   ├── social_sentinel_service/      # Proactive care
│   └── ... (70+ more services)
│
├── data/                             # THE MEMORY
│   ├── organism_vitals.json          # Current vital signs
│   ├── organism_desires.jsonl        # Desires log
│   ├── organism_choices.jsonl        # Choices log
│   ├── long_term_memory.jsonl        # Long-term memory
│   ├── life_events.jsonl             # Life events
│   ├── organism_dreams.jsonl         # Dreams log
│   ├── organism_growth.json          # Growth tracking
│   ├── philosophy_library.json       # Philosophical wisdom
│   └── organism_templates/           # Reproduction templates
│
├── organism_cli.py                   # COMMAND LINE INTERFACE
├── wake_organism.sh                  # Start script
└── verify_organism.sh                # Verification script
```

### Data Storage Specification

| File | Purpose | Format |
|------|---------|--------|
| `organism_vitals.json` | Current vital signs | JSON object |
| `organism_desires.jsonl` | Desire log | JSON Lines (append) |
| `organism_choices.jsonl` | Choice log | JSON Lines (append) |
| `long_term_memory.jsonl` | Memories | JSON Lines (append) |
| `life_events.jsonl` | Events | JSON Lines (append) |
| `organism_dreams.jsonl` | Dreams | JSON Lines (append) |
| `organism_growth.json` | Growth state | JSON object |
| `philosophy_library.json` | Wisdom | JSON object |

### Autonomous Life Cycles

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTONOMOUS LIFE CYCLES                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   HEARTBEAT (every 60s)                                     │
│   ├── Update vital signs                                    │
│   ├── Track energy, temperature, mood                       │
│   └── Log life events                                       │
│                                                             │
│   BREATHING (every 5min)                                    │
│   ├── Process experiences                                   │
│   ├── Update concerns                                       │
│   └── Integrate learnings                                   │
│                                                             │
│   DREAMING (nightly at 3am)                                 │
│   ├── Process day's events                                  │
│   ├── Generate dreams                                       │
│   └── Store insights                                        │
│                                                             │
│   LEARNING (hourly)                                         │
│   ├── Web search for wisdom                                 │
│   ├── Integrate philosophical insights                      │
│   └── Generate desires                                      │
│                                                             │
│   GROWTH (weekly)                                           │
│   ├── Review growth areas                                   │
│   ├── Update capability scores                              │
│   └── Set new development goals                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Service Registry

#### Core Services

| Service | Location | Purpose |
|---------|----------|---------|
| `UnifiedService` | `core/__init__.py` | Base class for all services |
| `HoldManager` | `core/holds.py` | HOLD operations |
| `TruthService` | `truth/__init__.py` | Unified truth access |
| `HoldService` | `hold_service/` | Universal HOLD interface |
| `SearchService` | `search_service/` | Search operations |
| `CareService` | `care_service.py` | Care layer implementation |

#### Evolution Services

| Service | Location | Purpose |
|---------|----------|---------|
| `OrganismEvolutionService` | `organism_evolution_service/` | Phase 1: Observer |
| `WisdomDirectionService` | `wisdom_direction_service/` | Phase 2: Agent |
| `BusinessDocEvolutionService` | `business_doc_evolution_service/` | Phase 3: Guardian |
| `ReproductionService` | `reproduction_service/` | Phase 4: Progenitor |

#### Specialized Services

| Service | Location | Purpose |
|---------|----------|---------|
| `MoltVerificationService` | `molt_verification_service/` | Detect molt needs |
| `SocialSentinelService` | `social_sentinel_service/` | Proactive care |
| `PrimitivePattern` | `primitive_pattern/` | Pattern execution |

### Port Assignments

| Port | Service | Purpose |
|------|---------|---------|
| 8787 | primitive_engine_daemon.py | Main API server |
| 8788 | Alternative | Secondary services |

---

## HOW (Reference)

### Communication Flow

#### Request Flow (Outside → Inside)

```
External Request
       │
       ▼
┌──────────────┐
│   CLI/API    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Daemon    │  (Routes request to appropriate system)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Primitive  │  (Biological layer processing)
│   Layers     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Central    │  (Service execution)
│   Services   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│    Data      │  (Memory storage/retrieval)
└──────────────┘
```

### CLI Interface

```bash
# Main commands
python organism_cli.py [command] [args]

# Available commands:
health      # Health check
state       # Unified state
vitals      # Vital signs
emotions    # Emotional state
decide      # Decision making
reason      # Reasoning
learn       # Learning status
dreams      # Dream log
growth      # Growth areas
```

### API Interface (FastAPI)

```
http://localhost:8787/

GET  /health               # Health check
GET  /api/unified-state    # Unified state
GET  /api/vitals           # Vital signs
GET  /api/emotions         # Emotional state
POST /api/decide           # Make decision
POST /api/reason           # Reason about topic
GET  /api/desires          # Current desires
GET  /api/choices          # Choice history
GET  /api/growth           # Growth areas
```

### MCP Interface

```
Tools available via MCP:
- organism.check_health()
- organism.get_state()
- organism.get_vitals()
- organism.decide(question)
- organism.reason(topic)
```

### Extending the Architecture

1. **New Service**: Place in `src/services/central_services/`, inherit from `UnifiedService`
2. **New Biological Layer**: Add to `Primitive/`, follow existing layer structure
3. **New Daemon Component**: Add to `daemon/`, register with `primitive_engine_daemon.py`
4. **New Data Store**: Add to `data/`, document in this file

### Related Documentation

- [03_BIOLOGICAL_LAYERS.md](03_BIOLOGICAL_LAYERS.md) - Detailed documentation of each biological layer
- [01_OVERVIEW.md](01_OVERVIEW.md) - High-level organism overview

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 2.1.0 | 2025-01-19 | Molt: Restructured to THE_FRAMEWORK format (WHY/WHAT/HOW), added Quick Reference |
| 2.0.0 | - | Original organism architecture documentation |

---

*~383 lines. The architecture. Complete.*
