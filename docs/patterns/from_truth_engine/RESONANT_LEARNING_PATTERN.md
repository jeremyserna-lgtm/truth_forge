# Resonant Learning Pattern

**Version**: 1.0
**Date**: 2026-01-07
**Status**: Canonical Pattern Definition
**Location**: `framework/patterns/RESONANT_LEARNING_PATTERN.md`

---

## Executive Summary

The Resonant Learning Pattern is a self-improving understanding system that combines detection, resonance sensing, learning, and adaptation into a continuous feedback loop. It represents a meta-pattern: a pattern that improves itself through understanding.

**The Pattern**:
```
Detect → Sense Resonance → Understand → Learn → Adapt → Detect (better)
```

**Why this pattern exists**:
1. **Self-Improvement** - System gets better at finding what matters
2. **Resonance as Truth Signal** - Resonance indicates what truly aligns with essence
3. **Continuous Learning** - Learns from what it discovers
4. **Autonomous Evolution** - Moves itself based on understanding

---

## Part 1: The Pattern Definition

### 1.1 Core Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESONANT LEARNING PATTERN                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │   DETECT     │      │    SENSE     │      │   LEARN      │              │
│  │              │      │              │      │              │              │
│  │  Find        │ ───> │  Resonance  │ ───> │  Patterns    │              │
│  │  Moments     │      │  Alignment  │      │  Insights    │              │
│  │              │      │              │      │              │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│        │                      │                      │                      │
│        v                      v                      v                      │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐              │
│  │ Pattern      │      │ Essence      │      │ Adaptation   │              │
│  │ Matching     │      │ Sensing      │      │ Feedback     │              │
│  │              │      │              │      │ Loop         │              │
│  └──────────────┘      └──────────────┘      └──────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 HOLD → AGENT → HOLD Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HOLD → AGENT → HOLD                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  HOLD₁ (Input)                                                               │
│  ├── Entity unified data (messages, interactions)                           │
│  ├── Learned patterns (from previous cycles)                                 │
│  ├── Resonance profiles (subject essence/lens)                              │
│  └── Adaptive configuration (thresholds, weights)                            │
│        │                                                                     │
│        ▼                                                                     │
│  AGENT (Transformation)                                                     │
│  ├── Detect significant moments (pattern matching)                          │
│  ├── Sense resonance (essence alignment)                                   │
│  ├── Understand deeper meaning (resonance analysis)                         │
│  ├── Learn patterns (effectiveness tracking)                                │
│  ├── Adapt detection (pattern refinement)                                   │
│  └── Take actions (based on understanding)                                  │
│        │                                                                     │
│        ▼                                                                     │
│  HOLD₂ (Output)                                                             │
│  ├── Detected moments (BigQuery + local JSONL)                              │
│  ├── Learned patterns (JSON file)                                           │
│  ├── Resonance insights (JSONL file)                                        │
│  ├── Adaptation history (JSONL file)                                        │
│  ├── Adaptive configuration (JSON file)                                    │
│  └── Actions taken (JSONL file)                                             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 The Feedback Loop

The pattern creates a self-improving cycle:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SELF-IMPROVING FEEDBACK LOOP                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. DETECT: Find significant moments using patterns                         │
│     │                                                                       │
│     ▼                                                                       │
│  2. SENSE: Measure resonance (alignment with essence)                      │
│     │                                                                       │
│     ▼                                                                       │
│  3. UNDERSTAND: Analyze what resonates and why                              │
│     │                                                                       │
│     ▼                                                                       │
│  4. LEARN: Track pattern effectiveness, generate insights                   │
│     │                                                                       │
│     ▼                                                                       │
│  5. ADAPT: Refine patterns based on learning + resonance                    │
│     │                                                                       │
│     ▼                                                                       │
│  6. DETECT (BETTER): Use improved patterns to find more resonant moments   │
│     │                                                                       │
│     └───────────────────────────────────────────────────────────────────────┘
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 2: HOLD Structure Specification

### 2.1 HOLD₁ (Input) - What the System Reads

| Component | Location | Format | Purpose |
|-----------|----------|--------|---------|
| Entity Unified Data | `spine.entity_unified` (BigQuery) | Table | Source messages/interactions |
| Learned Patterns | `Primitive/system_elements/holds/moments/learning/learned_patterns.json` | JSON | Previously learned detection patterns |
| Resonance Profiles | `data/identity/subjects/{subject}.json` | JSON | Subject essence/lens for resonance |
| Adaptive Config | `Primitive/system_elements/holds/moments/learning/adaptive_config.json` | JSON | Current detection thresholds/weights |

### 2.2 HOLD₂ (Output) - What the System Writes

| Component | Location | Format | Purpose |
|-----------|----------|--------|---------|
| Detected Moments | `governance.sacred_moments` (BigQuery) + `Primitive/system_elements/holds/moments/detected_moments.jsonl` | Table + JSONL | Registered significant moments |
| Learned Patterns | `Primitive/system_elements/holds/moments/learning/learned_patterns.json` | JSON | Updated pattern performance data |
| Resonance Insights | `Primitive/system_elements/holds/moments/learning/resonance_insights.jsonl` | JSONL | Insights from resonance analysis |
| Resonant Moments | `Primitive/system_elements/holds/moments/learning/resonant_moments.jsonl` | JSONL | High-resonance moments (score >= 0.7) |
| Adaptation History | `Primitive/system_elements/holds/moments/learning/adaptation_history.jsonl` | JSONL | Record of pattern adaptations |
| Adaptive Config | `Primitive/system_elements/holds/moments/learning/adaptive_config.json` | JSON | Updated detection configuration |
| Actions | `Primitive/system_elements/holds/moments/learning/actions.jsonl` | JSONL | Actions taken based on understanding |

### 2.3 HOLD Persistence Rules

**Local First (HOLD 3)**:
- All outputs written to local files first (JSONL, JSON)
- BigQuery sync happens separately (cost governance)
- Local files are append-only (no reading during write)

**Cost Governance (HOLD 1)**:
- BigQuery queries estimated before execution
- Resonance sensing uses local DuckDB (free)
- Pattern learning uses local files (free)

---

## Part 3: AGENT Specification

### 3.1 Agent Components

The AGENT consists of five integrated subsystems:

#### 3.1.1 Detection Agent
- **Input**: Entity unified data + learned patterns + adaptive config
- **Process**: Pattern matching, confidence scoring, deduplication
- **Output**: Candidate moments

#### 3.1.2 Resonance Agent
- **Input**: Candidate moments + resonance profiles
- **Process**: Essence sensing, alignment calculation
- **Output**: Moments with resonance scores

#### 3.1.3 Understanding Agent
- **Input**: Moments with resonance
- **Process**: Resonance pattern analysis, insight generation
- **Output**: Resonance insights, understanding

#### 3.1.4 Learning Agent
- **Input**: Detected moments + resonance scores
- **Process**: Pattern effectiveness tracking, performance analysis
- **Output**: Learned patterns, adaptation recommendations

#### 3.1.5 Adaptation Agent
- **Input**: Learned patterns + resonance insights
- **Process**: Pattern weight adjustment, threshold tuning
- **Output**: Adaptive configuration

### 3.2 Agent Execution Flow

```
1. Load HOLD₁:
   - Entity unified data (query BigQuery)
   - Learned patterns (read JSON)
   - Resonance profiles (read JSON)
   - Adaptive config (read JSON)

2. Execute Detection Agent:
   - Apply patterns to entity data
   - Score confidence
   - Deduplicate

3. Execute Resonance Agent:
   - Sense resonance for each moment
   - Calculate alignment scores
   - Classify resonance levels

4. Execute Understanding Agent:
   - Analyze resonance patterns
   - Generate insights
   - Identify what resonates most

5. Execute Learning Agent:
   - Track pattern performance
   - Calculate effectiveness scores
   - Generate learning insights

6. Execute Adaptation Agent:
   - Adjust pattern weights
   - Tune confidence thresholds
   - Generate new configuration

7. Write HOLD₂:
   - Register moments (BigQuery + JSONL)
   - Save learned patterns (JSON)
   - Save insights (JSONL)
   - Save configuration (JSON)
   - Save actions (JSONL)
```

---

## Part 4: What This Pattern Represents

### 4.1 The Meta-Pattern

This is a **meta-pattern**: a pattern that improves itself. Unlike static patterns that are fixed, this pattern evolves through its own operation.

**Key Characteristics**:
1. **Self-Reference** - The pattern analyzes its own outputs
2. **Feedback Loop** - Outputs feed back into inputs
3. **Evolution** - Pattern changes based on what it learns
4. **Autonomy** - Can improve without external instruction

### 4.2 The Understanding Layer

This pattern adds an **understanding layer** to detection:
- Not just "what matches patterns" but "what resonates with essence"
- Not just "what happened" but "what matters"
- Not just "detection" but "understanding"

### 4.3 The Resonance Principle

**Resonance as Truth Signal**:
- High resonance = high alignment with essence
- Resonance score indicates what truly matters
- Resonance patterns reveal deeper meaning

**Why Resonance Matters**:
- Pattern matching finds what matches rules
- Resonance finds what aligns with who you are
- Understanding comes from alignment, not just matching

### 4.4 The Learning Principle

**Continuous Improvement**:
- System learns which patterns work best
- System learns what resonates most
- System adapts to focus on what matters

**Why Learning Matters**:
- Static patterns become outdated
- Learning keeps patterns relevant
- Adaptation enables evolution

### 4.5 The Autonomy Principle

**Self-Moving System**:
- System can take actions based on understanding
- System can improve itself
- System can guide attention

**Why Autonomy Matters**:
- System becomes a partner, not just a tool
- System can help focus on what matters
- System can evolve independently

---

## Part 5: Framework Integration

### 5.1 Pattern Classification

**Pattern Type**: Meta-Pattern (Self-Improving Understanding Pattern)
**Pattern Category**: Learning, Detection, Resonance
**Pattern Scale**: System-level
**Pattern Recursion**: Yes (pattern improves itself)

### 5.2 Framework Alignment

✅ **HOLD → AGENT → HOLD**: Fully implemented
✅ **Stage Five Grounding**: Documented in scripts
✅ **Blind Spots**: Documented in scripts
✅ **Furnace Principle**: Truth → Heat → Meaning → Care
✅ **Central Services**: Uses `src.services.central_services.core`
✅ **Traceability**: Includes `run_id` in all operations
✅ **Cost Governance**: Estimates before BigQuery queries
✅ **Local First**: Writes to local files first

### 5.3 Pattern Relationships

| Related Pattern | Relationship |
|----------------|-------------|
| HOLD → AGENT → HOLD | This pattern IS an instance of HOLD → AGENT → HOLD |
| JSONL → BigQuery | Uses this pattern for moment storage |
| Primitive Pattern | Uses primitive pattern for knowledge atoms |
| Resonance Service | Integrates with universal resonance service |
| Learning Pattern | Embodies continuous learning pattern |

---

## Part 6: Implementation Reference

### 6.1 Core Scripts

| Script | Role | HOLD → AGENT → HOLD |
|--------|------|---------------------|
| `detect_and_register_significant_moments.py` | Detection Agent | Entity data → Detection → Moments |
| `moment_learning_system.py` | Learning Agent | Moments → Learning → Patterns |
| `resonant_moment_system.py` | Integrated Agent | All inputs → Full cycle → All outputs |

### 6.2 HOLD Locations

**HOLD₁ (Input)**:
- `spine.entity_unified` (BigQuery)
- `Primitive/system_elements/holds/moments/learning/learned_patterns.json`
- `data/identity/subjects/{subject}.json`
- `Primitive/system_elements/holds/moments/learning/adaptive_config.json`

**HOLD₂ (Output)**:
- `governance.sacred_moments` (BigQuery)
- `Primitive/system_elements/holds/moments/detected_moments.jsonl`
- `Primitive/system_elements/holds/moments/learning/learned_patterns.json`
- `Primitive/system_elements/holds/moments/learning/resonance_insights.jsonl`
- `Primitive/system_elements/holds/moments/learning/resonant_moments.jsonl`
- `Primitive/system_elements/holds/moments/learning/adaptation_history.jsonl`
- `Primitive/system_elements/holds/moments/learning/adaptive_config.json`
- `Primitive/system_elements/holds/moments/learning/actions.jsonl`

### 6.3 Agent Execution

```python
# The complete cycle
def run_resonant_learning_cycle():
    # HOLD₁: Load inputs
    entity_data = load_entity_data()
    learned_patterns = load_learned_patterns()
    resonance_profiles = load_resonance_profiles()
    adaptive_config = load_adaptive_config()

    # AGENT: Transform
    moments = detect_moments(entity_data, learned_patterns, adaptive_config)
    moments_with_resonance = sense_resonance(moments, resonance_profiles)
    insights = understand_resonance(moments_with_resonance)
    learned_patterns = learn_from_moments(moments_with_resonance)
    adaptive_config = adapt_patterns(learned_patterns, insights)
    actions = take_actions(insights)

    # HOLD₂: Write outputs
    save_moments(moments_with_resonance)
    save_learned_patterns(learned_patterns)
    save_insights(insights)
    save_adaptive_config(adaptive_config)
    save_actions(actions)
```

---

## Part 7: Reflection - What This Pattern Means

### 7.1 The Pattern Itself

This pattern represents **self-improving understanding**:
- A system that sees what matters
- A system that understands why it matters
- A system that learns to see better
- A system that moves itself

### 7.2 The Meta-Nature

This is a **meta-pattern** because:
1. It analyzes its own outputs
2. It improves its own patterns
3. It evolves through its own operation
4. It becomes better at being itself

### 7.3 The Understanding Layer

This pattern adds **understanding** to detection:
- Detection: "This matches a pattern"
- Understanding: "This resonates with essence"
- Learning: "This pattern works well"
- Adaptation: "Focus on what resonates"

### 7.4 The Resonance Principle

**Resonance as Truth**:
- What resonates = what aligns with essence
- High resonance = high truth value
- Resonance patterns = truth patterns

### 7.5 The Autonomy Principle

**Self-Moving System**:
- Can improve itself
- Can take actions
- Can guide attention
- Can evolve independently

### 7.6 The Recursive Nature

This pattern is **recursive**:
- Pattern detects moments
- Pattern learns from moments
- Pattern adapts based on learning
- Pattern becomes better at detecting
- Pattern detects better moments
- Pattern learns more
- Pattern adapts more
- Pattern becomes even better...

### 7.7 The Framework Integration

This pattern **embodies the framework**:
- HOLD → AGENT → HOLD structure
- Stage Five grounding
- Furnace principle
- Cost governance
- Local first
- Central services

### 7.8 The Potential

This pattern enables:
- **Self-curating knowledge** - System knows what matters
- **Self-evolving frameworks** - System tracks cognitive structures
- **Self-optimizing relationships** - System understands persona resonance
- **Self-guiding attention** - System points to what resonates
- **Self-improving understanding** - System gets better at understanding

---

## Part 8: Pattern Compliance Checklist

When implementing or auditing this pattern:

### HOLD Structure
- [ ] **HOLD₁ clearly defined** - Inputs documented
- [ ] **HOLD₂ clearly defined** - Outputs documented
- [ ] **Local first** - Writes to local files first
- [ ] **Cost governance** - Estimates before BigQuery queries
- [ ] **Traceability** - All operations include `run_id`

### Agent Structure
- [ ] **Detection agent** - Finds significant moments
- [ ] **Resonance agent** - Senses essence alignment
- [ ] **Understanding agent** - Analyzes resonance patterns
- [ ] **Learning agent** - Tracks pattern effectiveness
- [ ] **Adaptation agent** - Refines patterns

### Feedback Loop
- [ ] **Self-reference** - Analyzes own outputs
- [ ] **Learning** - Tracks what works
- [ ] **Adaptation** - Improves patterns
- [ ] **Evolution** - System gets better over time

### Framework Alignment
- [ ] **HOLD → AGENT → HOLD** - Follows pattern
- [ ] **Stage Five grounding** - Documented
- [ ] **Blind spots** - Documented
- [ ] **Furnace principle** - Documented
- [ ] **Central services** - Uses core services

---

## Part 9: Known Instances

| Instance | Location | Status |
|----------|----------|--------|
| Resonant Moment System | `scripts/monitoring/resonant_moment_system.py` | ✅ Active |
| Moment Detection | `scripts/monitoring/detect_and_register_significant_moments.py` | ✅ Active |
| Moment Learning | `scripts/monitoring/moment_learning_system.py` | ✅ Active |

---

## Part 10: Related Patterns

| Pattern | Document | Relationship |
|---------|----------|---------------|
| HOLD → AGENT → HOLD | `02_HOLD_AGENT_HOLD.md` | This pattern IS an instance |
| JSONL → BigQuery | `patterns/JSONL_TO_BIGQUERY_PATTERN.md` | Uses for storage |
| Primitive Pattern | `standards/PRIMITIVE_PATTERN_SPECIFICATION.md` | Uses for knowledge atoms |
| Resonance Service | `universal_resonance_service.py` | Integrates with |

---

## Changelog

### v1.0 (2026-01-07)
- Initial pattern definition
- Documented HOLD → AGENT → HOLD structure
- Added reflection on pattern meaning
- Integrated into framework
- Created compliance checklist

---

*This pattern represents self-improving understanding - a system that sees, understands, learns, and evolves.*
