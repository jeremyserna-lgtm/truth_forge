# Seeing Architecture

**Location**: `architect_central_services/src/architect_central_services/governance/seeing/`
**Purpose**: Introspection primitives - answering "what's here?" without requiring foreknowledge

---

## The Four Categories (TAXONOMY)

The seeing module contains four distinct types of components:

| Category | What It Is | Relationship to Data | File |
|----------|------------|---------------------|------|
| **Perspective** | Static metadata defining a viewpoint | Describes HOW to view | perspectives.py |
| **Processor** | Active class that transforms input | Produces primitives | emotion_processor.py, spine_processor.py |
| **Service** | Orchestrates/coordinates components | Manages flow | service.py, primitives_service.py |
| **Introspector** | Enumerates what exists | Discovers without interpreting | introspectors.py |

---

## 1. Perspectives (formerly "Conceptual Layers")

**Definition**: Static metadata that defines a perspective as a collection of lenses.

**Key insight**: Perspectives don't process data. They define the LENS through which data should be viewed.

### Structure

```
Perspective
├── name: str
├── description: str
├── layer_type: str ("universal", "domain", "identity")
├── lenses: List[Lens]
├── depends_on: List[str]
└── metadata: Dict

Lens
├── name: str
├── description: str
├── filter_fn: Optional[Callable]
├── interpret_fn: Optional[Callable]
└── metadata: Dict
```

### Current Perspectives

| Perspective | Type | Purpose | Lenses |
|-------------|------|---------|--------|
| **human** | universal | What's true for any human | embodied, emotional, temporal, social, needs, finite, meaning_seeker |
| **body** | domain | Physical embodiment | energy, circadian, health, sleep |
| **cognition** | domain | Cognitive processes | attention, learning, memory, decision_making, cognitive_load |
| **social** | domain | Relationships | connection, recognition, belonging, reciprocity, trust |
| **emotion** | domain | Emotion detection | sentiment, intensity, valence |
| **temporal** | domain | Time patterns | rhythm, velocity, acceleration, gaps |
| **risk** | domain | Risk/reward analysis | risk_tolerance, reward_type, tradeoff |
| **jeremy** | identity | Jeremy-specific patterns | furnace_*, stage5, night_builder, crisis_builder, hope, frustration, etc. |

### Hierarchy

```
universal (human)
    └── domain (body, cognition, social, emotion, temporal, risk)
            └── identity (jeremy)
```

The jeremy perspective DEPENDS ON the domain perspectives, which depend on the human perspective. This creates composable viewpoints.

### File Location

All perspectives are defined in `perspectives.py` via factory functions:
- `create_human_perspective()`
- `create_body_perspective()`
- `create_cognition_perspective()`
- `create_social_perspective()`
- `create_emotion_perspective()` ← Note: This creates a Perspective, NOT the EmotionProcessor class
- `create_temporal_perspective()`
- `create_risk_perspective()`
- `create_jeremy_perspective()`

The `PerspectiveManifest` class registers and manages all perspectives.

**Backward compatibility**: Old names (`Layer`, `LayerManifest`, `create_*_layer()`) are still exported as aliases.

---

## 2. Processors (formerly "Processing Layers")

**Definition**: Active classes that take input and produce primitives.

**Key insight**: Processors DO work. They transform data into structured primitives.

### Current Processors

| Processor | File | Input | Output | Data Source |
|-----------|------|-------|--------|-------------|
| **EmotionProcessor** | emotion_processor.py | Text | EmotionPrimitive, EmotionAggregate | NRCLex, TextBlob, Extended patterns |
| **SpineProcessor** | spine_processor.py | Query params | MessagePrimitive, ConversationPrimitive, EmotionalSignaturePrimitive, TopicClusterPrimitive, SemanticNeighborsPrimitive, MethodologyPatternPrimitive | BigQuery (entity_unified, entity_enrichments, entity_embeddings) |

### Common Patterns

Both processors follow these patterns:

```python
# 1. Central services imports
from architect_central_services import (
    get_logger,
    get_current_run_id,
    generate_primitive_id,
)

# 2. Run ID traceability
self.run_id = get_current_run_id()

# 3. Primitive ID generation (with source traceability)
primitive_id = generate_primitive_id("prefix", source_id=source_id)

# 4. Expose method for external consumption
def expose(self) -> Dict[str, Any]:
    """Expose processor data for consumption."""
    ...
```

### Key Difference from Perspectives

- **Perspective**: "Here's how to view emotion" (metadata)
- **Processor**: "Here's the emotion I detected in this text" (computed result)

**Backward compatibility**: Old names (`EmotionLayer`, `SpineLayer`, `get_spine_layer()`) are still exported as aliases.

---

## 3. Services

**Definition**: Components that orchestrate or coordinate other components.

### Current Services

| Service | File | Purpose |
|---------|------|---------|
| **SeeingService** | service.py | Orchestrates introspection across domains (code, documents, directories, transcripts, schemas) |
| **PrimitivesService** | primitives_service.py | Manages primitives + time slicing (TimeFrame, TemporalSlice, SemanticFrame) |

### Service vs Processor

- **Service**: Coordinates multiple components, manages state, provides unified API
- **Processor**: Single-purpose transformation, produces one type of primitive

---

## 4. Introspectors

**Definition**: Components that enumerate what exists without interpreting it.

**Key insight**: Introspectors answer "what's here?" - they discover structure without assigning meaning.

### Current Introspectors

#### Core Domain Introspectors

| Introspector | File | Domain | What It Enumerates |
|--------------|------|--------|-------------------|
| **CodeIntrospector** | introspectors.py | Python files | AST nodes (functions, classes, imports, decorators) |
| **DocumentIntrospector** | introspectors.py | Markdown/docs | Headings, paragraphs, code blocks, links |
| **FileSystemIntrospector** | introspectors.py | Directories | Files by type, sizes, structure |
| **TranscriptIntrospector** | introspectors.py | JSONL files | Entries, fields, entities |
| **SchemaIntrospector** | introspectors.py | Databases | Tables, columns, types |

#### Truth Engine Infrastructure Introspectors

| Introspector | File | Domain | What It Enumerates |
|--------------|------|--------|-------------------|
| **HookIntrospector** | introspectors.py | hooks.json | PreToolUse/PostToolUse hooks, categories, matchers, on_demand hooks |
| **SkillIntrospector** | introspectors.py | commands/*.md | Skills with frontmatter, descriptions, code blocks, headings |
| **RuleIntrospector** | introspectors.py | rules/*.md | Rules with priorities, severities, frontmatter, related rules |
| **ConfigIntrospector** | introspectors.py | TOML/YAML/JSON | Sections, values, depth, top-level keys |
| **PipelineIntrospector** | introspectors.py | pipeline dirs | Stages, scripts, docs, SQL files, structure presence |

### Output Models

Each introspector produces a corresponding model:

**Core Domain:**
- CodeIntrospector → `SeenCode`
- DocumentIntrospector → `SeenDocument`
- FileSystemIntrospector → `SeenDirectory`
- TranscriptIntrospector → `SeenTranscript`
- SchemaIntrospector → `SeenSchema`

**Truth Engine Infrastructure:**
- HookIntrospector → `SeenHooks`
- SkillIntrospector → `SeenSkills`
- RuleIntrospector → `SeenRules`
- ConfigIntrospector → `SeenConfig`
- PipelineIntrospector → `SeenPipeline`

---

## File Organization

```
seeing/
├── __init__.py            # Exports all public components (organized by taxonomy)
├── perspectives.py        # Perspectives + Lens dataclass + PerspectiveManifest
├── emotion_processor.py   # EmotionProcessor
├── spine_processor.py     # SpineProcessor
├── service.py             # SeeingService
├── primitives_service.py  # PrimitivesService + time slicing
├── introspectors.py       # All 5 introspectors
├── models.py              # Seen* output models
└── limits.py              # Limiting/pagination utilities
```

**Organization principle**: Files are named by their taxonomy category.

---

## Relationships

```
                    ┌─────────────────────────────────────┐
                    │         PrimitivesService           │
                    │   (manages primitives + time)       │
                    └─────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
    ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
    │  SeeingService  │     │EmotionProcessor │     │  SpineProcessor │
    │  (orchestrates  │     │  (processes     │     │  (queries       │
    │   introspection)│     │   text→emotion) │     │   corpus)       │
    └────────┬────────┘     └─────────────────┘     └─────────────────┘
             │
    ┌────────┴────────────────────────────────────────┐
    │                                                  │
    ▼                                                  ▼
┌──────────────────┐                        ┌──────────────────┐
│   Introspectors  │                        │   Perspectives   │
│  (enumerate)     │                        │ (define lenses)  │
│  - Code          │                        │ - human          │
│  - Document      │                        │ - body           │
│  - FileSystem    │                        │ - cognition      │
│  - Transcript    │                        │ - social         │
│  - Schema        │                        │ - emotion        │
└──────────────────┘                        │ - temporal       │
                                            │ - risk           │
                                            │ - jeremy         │
                                            └──────────────────┘
```

---

## Usage Patterns

### Using Perspectives

```python
from architect_central_services.governance.seeing import (
    create_default_manifest,
    create_jeremy_perspective,
    # Or backward compatible:
    create_jeremy_layer,
)

# Get all registered perspectives
manifest = create_default_manifest()
perspectives_info = manifest.see_layers()

# Get a specific perspective
jeremy = manifest.get("jeremy")

# Get lenses from a perspective
hope_lens = jeremy.get_lens("hope")
```

### Using Processors

```python
from architect_central_services.governance.seeing import (
    EmotionProcessor,
    SpineProcessor,
    # Or backward compatible:
    EmotionLayer,
    SpineLayer,
)

# Process text through emotion detection
emotion_processor = EmotionProcessor()
primitive = emotion_processor.process_message(
    message_id="msg_123",
    message_text="I'm excited about this!",
)

# Query corpus for messages
spine = SpineProcessor()
messages = spine.get_user_messages(start_date="2024-06-01", limit=100)
```

### Using Introspectors

```python
from architect_central_services.governance.seeing import (
    CodeIntrospector,
    DocumentIntrospector,
)

# See what's in a Python file
code = CodeIntrospector()
seen = code.see("path/to/file.py")
# Returns: functions, classes, imports, decorators...

# See what's in a markdown file
doc = DocumentIntrospector()
seen = doc.see("path/to/file.md")
# Returns: headings, code blocks, links...
```

---

## Design Principles

1. **Introspection over pattern matching**: Ask "what's here?" not "is X here?"
2. **Primitives preserve full data**: No truncation at primitive layer; truncation happens at presentation
3. **Central services alignment**: All components use get_logger, run_id, generate_primitive_id
4. **Composable perspectives**: Perspectives can depend on other perspectives
5. **Separation of concerns**: Perspective (what to see) vs Processor (how to compute) vs Introspector (what exists)

---

## Naming Conventions (TAXONOMY)

| Category | Class Naming | File Naming | Factory Function |
|----------|--------------|-------------|------------------|
| Perspective | `Perspective`, `PerspectiveManifest` | perspectives.py | `create_*_perspective()` |
| Processor | `*Processor` | *_processor.py | N/A |
| Service | `*Service` | *_service.py or service.py | N/A |
| Introspector | `*Introspector` | introspectors.py | N/A |

**Backward compatibility aliases are maintained for:**
- `Layer` → `Perspective`
- `LayerManifest` → `PerspectiveManifest`
- `EmotionLayer` → `EmotionProcessor`
- `SpineLayer` → `SpineProcessor`
- `create_*_layer()` → `create_*_perspective()`
- `get_spine_layer()` → `get_spine_processor()`

---

## Future Considerations

### Potential New Processors
- **TranscriptProcessor**: Process Claude Code transcripts → tool patterns, decision primitives
- **RelationshipProcessor**: Query entity relationships → connection primitives
- **TemporalProcessor**: Time-series analysis → trend primitives

### Potential New Perspectives
- **work** (domain): Work patterns, productivity, focus
- **health** (domain): Physical and mental health indicators
- **creative** (domain): Creative output patterns

---

**Last Updated**: December 2025
**Maintainer**: Jeremy Serna & Claude Code
