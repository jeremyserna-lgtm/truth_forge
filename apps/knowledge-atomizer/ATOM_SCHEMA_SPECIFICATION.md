# Knowledge Atom Schema Specification

## Philosophy

Every knowledge atom should be analyzed at ALL levels by default. No picking and choosing. Full dimensional extraction every time.

The goal: When you look at an atom, you see the COMPLETE picture - what it says, what it implies, how certain it is, what it connects to, what it means, and why it matters.

---

## The 12 Analysis Dimensions

### 1. DATA LEVEL (What It Says)
| Field | Type | Description |
|-------|------|-------------|
| `content` | string | The atomic truth statement |
| `source_file` | string | Origin document |
| `source_context` | string | Surrounding context snippet |

### 2. SEMANTIC LEVEL (What It Means)
| Field | Type | Description |
|-------|------|-------------|
| `theme` | string | 1-2 word category |
| `domain` | string | Knowledge domain (tech, philosophy, business, etc.) |
| `abstraction_level` | 'concrete' \| 'conceptual' \| 'abstract' \| 'meta' | How abstract is this truth |

### 3. SIGNIFICANCE LEVEL (Why It Matters)
| Field | Type | Description |
|-------|------|-------------|
| `significance` | 'Foundational' \| 'Structural' \| 'Insight' \| 'Nuance' \| 'Detail' | Impact tier |
| `novelty` | 0-1 | How new/unique is this (vs common knowledge) |
| `actionability` | 0-1 | Can you DO something with this |

### 4. EPISTEMIC LEVEL (How Certain)
| Field | Type | Description |
|-------|------|-------------|
| `certainty` | 'fact' \| 'consensus' \| 'claim' \| 'speculation' \| 'hypothesis' | Confidence tier |
| `evidence_strength` | 0-1 | How well-supported |
| `verifiability` | 'observable' \| 'testable' \| 'logical' \| 'intuitive' | How can this be verified |

### 5. TEMPORAL LEVEL (When It Applies)
| Field | Type | Description |
|-------|------|-------------|
| `temporal_scope` | 'universal' \| 'historical' \| 'current' \| 'emerging' \| 'future' | Time relevance |
| `durability` | 'permanent' \| 'durable' \| 'transient' \| 'ephemeral' | How long will this be true |

### 6. RELATIONAL LEVEL (What It Connects To)
| Field | Type | Description |
|-------|------|-------------|
| `entities` | string[] | Named entities referenced |
| `concepts` | string[] | Abstract concepts referenced |
| `dependencies` | string[] | What this truth depends on |
| `implications` | string[] | What follows from this |

### 7. DIALECTICAL LEVEL (What It Opposes/Supports)
| Field | Type | Description |
|-------|------|-------------|
| `supports` | string[] | Positions/claims this supports |
| `contradicts` | string[] | Positions/claims this contradicts |
| `tensions` | string[] | Internal tensions or paradoxes |
| `synthesis_potential` | string | How this could resolve tensions |

### 8. AFFECTIVE LEVEL (Emotional Valence)
| Field | Type | Description |
|-------|------|-------------|
| `sentiment` | number (-1 to 1) | Positive/negative tone |
| `intensity` | 0-1 | Emotional intensity |
| `stakes` | 'existential' \| 'high' \| 'medium' \| 'low' \| 'trivial' | What's at risk |
| `urgency` | 0-1 | Time pressure implied |

### 9. PRAGMATIC LEVEL (What To Do)
| Field | Type | Description |
|-------|------|-------------|
| `action_items` | string[] | Implied actions |
| `preconditions` | string[] | What must be true first |
| `consequences` | string[] | What happens if acted upon |
| `audience` | string[] | Who needs to know this |

### 10. STRUCTURAL LEVEL (How It's Built)
| Field | Type | Description |
|-------|------|-------------|
| `structure_type` | 'claim' \| 'definition' \| 'comparison' \| 'causation' \| 'sequence' \| 'classification' | Logical form |
| `complexity` | 'atomic' \| 'compound' \| 'nested' | Structural complexity |
| `completeness` | 0-1 | Is this self-contained |

### 11. ONTOLOGICAL LEVEL (What Exists)
| Field | Type | Description |
|-------|------|-------------|
| `entity_type` | 'thing' \| 'process' \| 'relation' \| 'property' \| 'state' | What kind of being |
| `categories` | string[] | Classification categories |
| `is_a` | string[] | Parent types |
| `has_parts` | string[] | Component parts |

### 12. NORMATIVE LEVEL (What Should Be)
| Field | Type | Description |
|-------|------|-------------|
| `normative_type` | 'descriptive' \| 'prescriptive' \| 'evaluative' | Is/Ought distinction |
| `values_invoked` | string[] | Values this appeals to |
| `should_statements` | string[] | Implied oughts |

---

## Computed/Derived Fields

These are calculated from the primary dimensions:

| Field | Type | Description |
|-------|------|-------------|
| `quality_score` | 0-100 | Overall atom quality |
| `embedding` | number[] | Vector representation |
| `embedding_status` | 'pending' \| 'success' \| 'failed' | Embedding state |
| `hash` | string | Content hash for dedup |
| `created_at` | number | Timestamp |
| `last_enriched` | number | Last enrichment timestamp |

---

## Implementation Strategy

### Phase 1: Core + Semantic + Epistemic
Start with what we have + add certainty and evidence tracking.

### Phase 2: Relational + Dialectical
Add entity extraction and tension detection.

### Phase 3: Temporal + Affective + Pragmatic
Add time scoping, sentiment, and action extraction.

### Phase 4: Structural + Ontological + Normative
Full philosophical analysis.

---

## Example Enriched Atom

```json
{
  "id": "sha256:abc123...",
  "content": "The furnace doesn't strain. If forcing, find the shape that burns.",
  "source_file": "CLAUDE.md",

  "semantic": {
    "theme": "Architecture",
    "domain": "philosophy",
    "abstraction_level": "abstract"
  },

  "significance": {
    "tier": "Foundational",
    "novelty": 0.8,
    "actionability": 0.9
  },

  "epistemic": {
    "certainty": "claim",
    "evidence_strength": 0.6,
    "verifiability": "intuitive"
  },

  "temporal": {
    "scope": "universal",
    "durability": "permanent"
  },

  "relational": {
    "entities": ["furnace", "shape"],
    "concepts": ["strain", "flow", "resistance"],
    "dependencies": ["existence of 'furnace' metaphor"],
    "implications": ["stop when forcing", "find natural paths"]
  },

  "dialectical": {
    "supports": ["flow state philosophy", "wu-wei"],
    "contradicts": ["grind culture", "push through pain"],
    "tensions": [],
    "synthesis_potential": "Effort without strain"
  },

  "affective": {
    "sentiment": 0.3,
    "intensity": 0.6,
    "stakes": "medium",
    "urgency": 0.4
  },

  "pragmatic": {
    "action_items": ["Notice strain signals", "Step back when forcing"],
    "preconditions": ["awareness of current effort state"],
    "consequences": ["reduced friction", "better outcomes"],
    "audience": ["builders", "creators", "problem-solvers"]
  },

  "structural": {
    "type": "causation",
    "complexity": "compound",
    "completeness": 0.7
  },

  "ontological": {
    "entity_type": "process",
    "categories": ["methodology", "heuristic"],
    "is_a": ["principle", "guideline"],
    "has_parts": ["observation", "action"]
  },

  "normative": {
    "type": "prescriptive",
    "values_invoked": ["efficiency", "harmony", "wisdom"],
    "should_statements": ["find the shape that burns"]
  },

  "computed": {
    "quality_score": 87,
    "embedding": [0.12, -0.34, ...],
    "embedding_status": "success",
    "hash": "sha256:abc123..."
  },

  "tags": ["framework", "philosophy", "furnace", "Stage-5"]
}
```

---

## Migration Path

1. **Backward compatible**: All new fields optional initially
2. **Progressive enrichment**: Atoms get enriched incrementally
3. **Display-first**: Show what we have, even if partial
4. **Quality indicator**: Show enrichment coverage percentage

---

## UI Implications

The DistillView should show:
- **Badges** for top-level significance/certainty
- **Expandable panels** for each dimension
- **Visual indicators** for enrichment completeness
- **Filters** by any dimension

The goal: Transform atoms from opaque text blobs into multi-dimensional truth objects.
