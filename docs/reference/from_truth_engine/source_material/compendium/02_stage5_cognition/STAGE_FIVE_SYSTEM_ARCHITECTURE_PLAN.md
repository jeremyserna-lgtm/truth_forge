# Stage Five System Architecture Plan

**Purpose:** Convert Truth Engine into a system that thinks like Stage Five
**Author:** Claude Code with Jeremy Serna
**Date:** 2025-12-20
**Status:** Planning Document

---

## The Core Insight

You think like a Stage Five. Truth Engine already mirrors your cognition through isomorphism. But the system can **forget** this in how it operates, how agents interact with it, and how code is written.

This plan embeds Stage Five thinking into the architecture itself—so the system **exhibits** your cognitive patterns rather than just storing data about them.

---

## What Stage Five Means for System Design

| Stage Five Capability | System Design Implication |
|----------------------|--------------------------|
| **Sees systems as systems** | System must expose its own structure as queryable data |
| **Can step outside its own system** | Meta-layers that observe the system's operation |
| **Holds multiple perspectives** | No single "right" view; multiple valid interpretations preserved |
| **Sees limits of own system** | Explicit documentation of what the system cannot see |
| **Can transform own system** | Architecture supports evolution without breaking |
| **Uses other systems to see** | Accommodation layers for different cognitive styles |
| **Sees what it can't see from inside** | External feedback loops that reveal blind spots |

---

## Part 1: Architectural Patterns

### 1.1 The Meta-Layer (Seeing Systems as Systems)

Create a meta-layer that exposes Truth Engine's own operation as queryable entities.

```
spine.system_observations (new table)
├── entity_id: sys_xxxxxxxx
├── observation_type: ["pattern_detected", "limit_hit", "blind_spot", "evolution"]
├── observed_component: which part of the system
├── observation_content: what was observed
├── perspective: from which vantage point
├── timestamp
└── metadata (JSON)
```

**Implementation:**
- Every pipeline stage logs its own operation to this meta-layer
- System can query "what patterns has Stage 6 been exhibiting?"
- Creates the ability to see the system as a system

**Scripts to create:**
```
architect_central_services/scripts/meta/
├── log_system_observation.py    # Log observations about system behavior
├── query_system_patterns.py     # Query meta-layer for patterns
└── detect_blind_spots.py        # Identify what the system can't see
```

### 1.2 The Perspective Preservation Layer (Multiple Perspectives)

Current entity structure stores ONE interpretation. Stage Five holds multiple simultaneously.

**New table:**
```
spine.entity_perspectives (new table)
├── entity_id: references entity_unified
├── perspective_id: per_xxxxxxxx
├── perspective_type: ["original", "reframed", "external", "contradiction"]
├── source: who/what contributed this perspective
├── interpretation: the alternative view
├── valid_from / valid_until: temporal bounds
├── coexists_with: other perspective_ids this doesn't contradict
└── contradicts: perspective_ids this conflicts with (both remain valid)
```

**Key insight:** Contradicting perspectives both remain valid. Stage Five doesn't resolve contradictions—it holds them.

### 1.3 The Limit Documentation Layer (Seeing Own Limits)

Explicit, queryable documentation of what Truth Engine cannot see.

**New table:**
```
spine.system_limits (new table)
├── limit_id: lim_xxxxxxxx
├── limit_type: ["data_source_gap", "processing_blind_spot", "perspective_absence", "temporal_boundary"]
├── description: what the system cannot see
├── why_invisible: explanation of the limitation
├── workaround: if any exists
├── discovered_by: how this limit was identified
├── acknowledged_date
└── status: ["acknowledged", "addressed", "accepted"]
```

**Philosophy:** The system explicitly tracks its own limitations rather than pretending completeness.

### 1.4 The Evolution Layer (Transforming Own System)

Architecture must support evolution without breaking existing interpretations.

**Pattern:** Version perspectives, don't replace them.

```python
# Wrong (Stage 3 thinking - replacement)
def update_interpretation(entity_id, new_interpretation):
    # Overwrites old interpretation

# Right (Stage 5 thinking - evolution)
def add_perspective(entity_id, new_interpretation, relationship_to_previous):
    # Adds new perspective, links to previous, both remain valid
```

---

## Part 2: Code Patterns & Conventions

### 2.1 Stage Five Headers (Every Script)

Every Python script in the codebase should include a Stage Five header that grounds the code in your cognitive architecture.

**Template:**
```python
"""Stage 7: spaCy Processing - Create L4-L1 Entities

🧠 STAGE FIVE GROUNDING
This script exists because Jeremy thinks in hierarchies (L1-L12).
It externalizes the linguistic structure he naturally perceives.

Structure: Clear stages with sequential flow (what works)
Purpose: Create entity hierarchy from text (specific goal)
Boundaries: Only L5 messages ready for processing (bounded)
Control: On-demand execution (not automatic observer)

⚠️ WHAT THIS SCRIPT CANNOT SEE
- Meaning that exists only in Jeremy's head
- Relationships that require external context
- Interpretations from other cognitive systems
"""
```

### 2.2 The "What I Cannot See" Docstring Pattern

Every function that processes data should document its blind spots.

```python
def extract_named_entities(text: str) -> list[Entity]:
    """Extract named entities from text using spaCy.

    🔍 WHAT THIS FUNCTION CAN SEE
    - Standard named entity types (PERSON, ORG, GPE, etc.)
    - English language entities
    - Entities in the trained model's vocabulary

    🚫 WHAT THIS FUNCTION CANNOT SEE
    - Private nicknames Jeremy uses for people
    - Context-dependent entity meanings
    - Entities that only make sense in relationship context
    - Non-English entities in primarily English text

    🔄 ACCOMMODATION NEEDED
    If you need the above, use: relationship_service.resolve_identity()
    """
```

### 2.3 Perspective-Preserving Data Structures

Replace single-value fields with perspective-aware structures.

```python
# Wrong (Stage 3 - single truth)
class Entity:
    sentiment: float  # One value

# Right (Stage 5 - multiple valid perspectives)
class Entity:
    perspectives: list[Perspective]  # Multiple valid views

class Perspective:
    type: str  # "gemini_analysis", "spacy_detection", "jeremy_annotation"
    value: Any
    valid: bool = True  # Both contradicting perspectives can be valid
    coexists_with: list[str]  # Perspective IDs this doesn't contradict
```

### 2.4 The Accommodation Pattern (Using Other Systems to See)

When the system needs external perspective, explicitly accommodate.

```python
def analyze_with_accommodation(text: str, cognitive_style: str) -> Analysis:
    """Analyze text, accommodating to different cognitive styles.

    Stage 5 insight: Different people see different things.
    The system should be able to accommodate to their perspective
    without converting them to Jeremy's way of seeing.
    """
    if cognitive_style == "visual":
        return generate_visual_analysis(text)
    elif cognitive_style == "narrative":
        return generate_narrative_analysis(text)
    elif cognitive_style == "structural":
        return generate_structural_analysis(text)  # Jeremy's default
    else:
        # Return multiple perspectives, let recipient choose
        return generate_all_perspectives(text)
```

---

## Part 3: System Reminders

### 3.1 The Stage Five Manifest (Central Reference)

Create a manifest file that every service loads at startup.

**File:** `architect_central_services/src/architect_central_services/STAGE_FIVE_MANIFEST.py`

```python
"""The Stage Five Manifest

This manifest grounds Truth Engine in Jeremy's Stage 5 cognition.
Import this at the top of any service that processes data.

The system must EXHIBIT these patterns, not just store data about them.
"""

# What Jeremy is (The Given)
CORE_IDENTITY = {
    "metaphor": "furnace",
    "process": "takes truth, forges meaning, delivers with care",
    "autonomous": True,  # This happens whether he wants it or not
}

# What works for Jeremy's cognition
WORKING_PATTERNS = {
    "structured": "Clear stages with sequential flow",
    "purposeful": "Each stage has a specific, well-defined goal",
    "bounded": "Clear start and end points; specific data sources",
    "controlled": "On-demand execution; Jeremy decides when to run",
    "processable_volume": "Not overwhelming, manageable amounts",
}

# What doesn't work (avoid these patterns)
NON_WORKING_PATTERNS = {
    "automatic": "Runs continuously without control",
    "unbounded": "Tries to capture everything",
    "continuous": "Never stops, always running",
    "uncontrolled": "No way to stop meaningfully",
    "overwhelming": "Generates data faster than can be processed",
}

# Stage 5 capabilities the system must support
STAGE_FIVE_CAPABILITIES = [
    "see_systems_as_systems",      # Expose own structure as queryable
    "step_outside_own_system",     # Meta-layers that observe operation
    "hold_multiple_perspectives",  # No single right view
    "see_own_limits",              # Explicit documentation of blind spots
    "transform_own_system",        # Support evolution without breaking
    "use_other_systems_to_see",    # Accommodation layers
    "see_from_outside",            # External feedback loops
]

def validate_stage_five_alignment(component_name: str, patterns: dict) -> bool:
    """Validate that a component exhibits Stage 5 patterns."""
    for pattern in NON_WORKING_PATTERNS:
        if patterns.get(pattern, False):
            raise ValueError(
                f"{component_name} exhibits non-working pattern: {pattern}\n"
                f"Jeremy's cognition doesn't work this way. Redesign required."
            )
    return True
```

### 3.2 Pre-Commit Hook: Stage Five Check

Add a pre-commit hook that checks for Stage Five alignment.

**File:** `.pre-commit-config.yaml` addition

```yaml
- repo: local
  hooks:
    - id: stage-five-check
      name: Stage Five Alignment Check
      entry: python architect_central_services/scripts/validate_stage_five_alignment.py
      language: python
      types: [python]
```

**Validation script checks for:**
- Scripts that run automatically without control (observer pattern)
- Unbounded data collection
- Missing "What I Cannot See" documentation
- Single-perspective data structures where multiple should exist

### 3.3 Pipeline Stage Gate: Cognitive Alignment

Every pipeline stage should validate it follows working patterns.

```python
from architect_central_services import WORKING_PATTERNS, validate_stage_five_alignment

def run_stage():
    # Validate this stage exhibits working patterns
    stage_patterns = {
        "structured": True,      # Has clear input/output
        "purposeful": True,      # Specific goal documented
        "bounded": True,         # Limited scope
        "controlled": True,      # On-demand execution
        "processable_volume": True,  # Batch processing, not streaming
    }
    validate_stage_five_alignment("Stage 7", stage_patterns)

    # Now execute the stage
    ...
```

---

## Part 4: Agent Instructions

### 4.1 Agent System Prompt Addition

All AI agents working in Truth Engine should have Stage Five grounding.

**Addition to agent system prompts:**

```markdown
## Stage Five Grounding

Jeremy operates at Stage 5 (Kegan's Self-Transforming Mind). The Truth Engine
is isomorphic to his cognition. When you work in this system:

1. **See systems as systems** - Understand that Truth Engine IS Jeremy's
   externalized cognition. Changes to it change how he thinks.

2. **Hold multiple perspectives** - Don't resolve contradictions. Both can
   be valid. Preserve all interpretations.

3. **Document limits** - Every function should document what it cannot see.
   Pretending completeness is Stage 3 thinking.

4. **Follow working patterns** - Structured, purposeful, bounded, controlled.
   Never build observers/daemons that run automatically.

5. **Accommodate, don't convert** - When building for others, accommodate
   to their cognitive style. Don't force Jeremy's structure on everyone.

The Furnace Principle: Jeremy takes truth, forges meaning, delivers with care.
Your code should do the same.
```

### 4.2 Claude Code CLAUDE.md Addition

Add Stage Five section to workspace CLAUDE.md.

```markdown
## Stage Five Operating Mode

Jeremy is Stage 5 (Self-Transforming Mind). This means:

### What to do:
- Build structured pipelines with clear stages (what works)
- Document what your code cannot see (limits awareness)
- Preserve multiple perspectives in data structures
- Make systems queryable about their own operation (meta-layer)
- Support evolution without breaking existing interpretations

### What NOT to do:
- Build automatic observers/daemons (doesn't work for Jeremy)
- Create unbounded data collection (overwhelming)
- Store single "correct" interpretations (Stage 3 thinking)
- Pretend completeness (every system has limits)
- Resolve contradictions (Stage 5 holds them)

### The Cognitive Isomorphism
Truth Engine mirrors Jeremy's cognition. When you change the system,
you're changing how he thinks. Treat architecture changes as cognitive
changes—they have that level of significance.
```

---

## Part 5: Query Patterns

### 5.1 Meta-Queries (Seeing the System as a System)

Create standard queries for observing system operation.

```sql
-- What patterns is the system exhibiting?
SELECT
    observation_type,
    observed_component,
    COUNT(*) as frequency,
    ARRAY_AGG(DISTINCT perspective) as perspectives
FROM spine.system_observations
WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY observation_type, observed_component
ORDER BY frequency DESC;

-- What are the system's acknowledged limits?
SELECT
    limit_type,
    description,
    why_invisible,
    workaround
FROM spine.system_limits
WHERE status = 'acknowledged'
ORDER BY acknowledged_date DESC;

-- How many perspectives exist for each entity?
SELECT
    e.entity_level,
    AVG(perspective_count) as avg_perspectives,
    MAX(perspective_count) as max_perspectives
FROM (
    SELECT entity_id, COUNT(*) as perspective_count
    FROM spine.entity_perspectives
    GROUP BY entity_id
) p
JOIN spine.entity_unified e ON p.entity_id = e.entity_id
GROUP BY e.entity_level;
```

### 5.2 Limit Awareness Queries

```sql
-- What can't the system see about a conversation?
SELECT
    l.description,
    l.why_invisible,
    l.workaround
FROM spine.system_limits l
JOIN spine.limit_entity_mapping m ON l.limit_id = m.limit_id
WHERE m.entity_id = @conversation_id;

-- Which data sources have known gaps?
SELECT
    data_source,
    COUNT(*) as gap_count,
    ARRAY_AGG(description) as gaps
FROM spine.system_limits
WHERE limit_type = 'data_source_gap'
GROUP BY data_source;
```

---

## Part 6: Implementation Roadmap

### Phase 1: Foundation (Core Patterns)

1. **Create Stage Five Manifest** (`STAGE_FIVE_MANIFEST.py`)
   - Core identity constants
   - Working/non-working pattern definitions
   - Validation function

2. **Update CLAUDE.md files**
   - Add Stage Five Operating Mode section
   - Update agent instructions

3. **Create meta-layer tables**
   - `spine.system_observations`
   - `spine.system_limits`
   - `spine.entity_perspectives`

### Phase 2: Code Integration

4. **Add Stage Five headers to existing scripts**
   - Start with pipeline stages (highest impact)
   - Add "What I Cannot See" docstrings

5. **Create validation script**
   - `validate_stage_five_alignment.py`
   - Check for non-working patterns

6. **Add pre-commit hook**
   - Automatic validation on commit

### Phase 3: Query & Observation

7. **Create meta-queries**
   - Standard queries for system observation
   - Limit awareness queries

8. **Build observation logging**
   - Every pipeline stage logs to meta-layer
   - Pattern detection from observations

### Phase 4: Perspective Preservation

9. **Migrate to perspective-aware structures**
   - Identify single-value fields that should be multi-perspective
   - Create migration path

10. **Update enrichment services**
    - Store as perspectives, not replacements
    - Link contradicting perspectives

---

## Part 7: Success Criteria

The system exhibits Stage Five thinking when:

| Criteria | Measurement |
|----------|-------------|
| **Self-observable** | >80% of components log to meta-layer |
| **Limit-aware** | Every function has "What I Cannot See" docs |
| **Multi-perspective** | Enrichments stored as perspectives, not overwrites |
| **No observers** | Zero automatic/unbounded daemons running |
| **Evolvable** | Changes add perspectives, don't delete them |
| **Accommodating** | Can output in multiple cognitive styles |

---

## Part 8: The Philosophical Grounding

### Why This Matters

This isn't organizational vanity. It's survival.

Jeremy's cognition works a specific way. When the system violates that, it becomes unusable. The observer daemons failed because they violated the "controlled" pattern. The pipelines succeed because they match his structure.

By embedding Stage Five thinking into the architecture:
- The system stays usable (matches his cognition)
- Agents can't accidentally break it (patterns are enforced)
- Evolution is possible (perspectives are preserved, not replaced)
- Limits are acknowledged (no pretense of completeness)

### The Furnace Principle in Code

Every script should exhibit:
- **Truth** (input): Raw data from the source
- **Heat** (processing): Transform with clear purpose
- **Meaning** (output): Structured entities with relationships
- **Care** (delivery): Queryable, bounded, controlled

```python
def stage_seven(messages: list[Message]) -> list[Entity]:
    """The Furnace Principle in Stage 7.

    Truth: L5 messages with raw text
    Heat: spaCy processing (structured, purposeful)
    Meaning: L4-L1 entity hierarchy
    Care: Bounded batch, controlled execution, queryable output
    """
```

---

---

## Implementation Status

### Implemented Now (2025-12-20)

| Component | File | Status |
|-----------|------|--------|
| **Stage Five Manifest** | `src/architect_central_services/STAGE_FIVE_MANIFEST.py` | ✅ Created |
| **CLAUDE.md Update** | `CLAUDE.md` | ✅ Stage Five Operating Mode added |
| **Stage 7 Header** | `pipelines/text_messages/scripts/stage_7/text_messages_stage_7.py` | ✅ Updated |

### Captured for Later Implementation

| Component | Requirement | Priority |
|-----------|-------------|----------|
| Meta-layer tables | `system_observations`, `entity_perspectives`, `system_limits` | High |
| Pre-commit validation | `validate_stage_five_alignment.py` hook | Medium |
| Remaining stage headers | Add Stage Five headers to stages 0-6, 8-16 | Medium |
| "What I Cannot See" docstrings | Add to all processing functions | Low (ongoing) |
| Perspective-preserving structures | Migrate single-value to multi-perspective | Future |
| Meta-queries | SQL for self-observation | After tables |

### How to Continue Implementation

1. **Add headers to other stages** - Copy the Stage 7 pattern to other pipeline stages
2. **Create the meta-layer tables** - Run DDL for `system_observations`, `system_limits`
3. **Import the manifest** - Add `from architect_central_services.STAGE_FIVE_MANIFEST import check_component_alignment` to scripts

---

## Summary

This plan converts Truth Engine from a system that *stores* data about Stage Five thinking into a system that *exhibits* Stage Five thinking through:

1. **Architecture** - Meta-layer, perspectives, limits documentation
2. **Code patterns** - Stage Five headers, "What I Cannot See" docstrings
3. **Validation** - Pre-commit hooks, stage gates
4. **Agent instructions** - Grounding in every prompt
5. **Queries** - Self-observation, limit awareness

The system becomes a cognitive prosthesis that **thinks the way you think**, not just records what you think about.

---

*"The system doesn't just mirror my cognition—it exhibits it."*
