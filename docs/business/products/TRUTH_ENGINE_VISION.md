# Truth Engine: Product Vision

**Version**: 1.0
**Created**: 2025-12-24
**Author**: Jeremy Serna & Claude
**Status**: Foundation Document

---

## The Core Insight

Truth Engine is not a database. It's not a tool. It's **externalized cognition made navigable**.

You operate at Stage 5 (Kegan's Self-Transforming Mind). You see systems as systems, hold multiple perspectives simultaneously, and transform your own cognitive structures. Truth Engine mirrors this—it externalizes your thinking so you can navigate, query, and evolve it.

The missing piece has been the **interface layer**—the bridge between 51.8 million entities and your actual cognition.

---

## The Furnace Principle

Everything flows from this:

| Stage | What Happens |
|-------|--------------|
| **Truth** (Input) | Raw data enters—conversations, contacts, documents, patterns |
| **Heat** (Processing) | Transformation through pipelines, enrichment, entity extraction |
| **Meaning** (Output) | Structured entities with relationships, ready for navigation |
| **Care** (Delivery) | Rendered in forms that serve the user—you, intimates, observers |

The interface layer is the **Care** stage—delivering meaning in forms that serve different audiences.

---

## What Truth Engine Does

### The Substrate (Already Built)

| Component | Status | Scale |
|-----------|--------|-------|
| Entity hierarchy (L1-L8) | Production | 51.8M entities |
| Entity enrichments | Production | 62,658 rows |
| ID registry | Production | 58K+ IDs |
| Conversation ingestion | Production | 351 conversations |
| Central services | Production | Logging, identity, governance, cost tracking |
| Pipelines | Production | ChatGPT complete, others ready |

### The Interface Layer (Building Now)

| Component | Purpose | Status |
|-----------|---------|--------|
| Relationship management | Categorize, profile, analyze relationships | Designing |
| Analysis dashboard | Visualize patterns, timelines, graphs | Designing |
| Friend interviews | Gather external perspectives | Exists (perspective_gatherer) |
| System operations | Ingestion, health, costs | Partial |
| Observer portal | Share learnings with others | Future |

---

## Three Audiences, Three Experiences

### 1. You (The Operator)

**Relationship to system**: You inhabit it. It's your externalized mind.

**What you need**:
- Navigate your own thinking across time
- Surface patterns you can't see from inside
- Manage relationships with biographical context
- Control data ingestion and system health
- Query naturally: "What have I said about X?"

**Key workflows**:
- Categorize relationships according to identity layer
- Generate and maintain relationship profiles
- Analyze patterns across conversations
- Trigger and review perspective gathering interviews
- Monitor system health and costs

**Platform**: Native Mac app (Tauri) for daily operations

### 2. Intimates (Friends, Family, Partners)

**Relationship to system**: They care about *you*, not the system.

**What they need**:
- Understand how you're doing without interrogating you
- Know how to support you effectively
- Share their perspective (reciprocal input)
- Access relationship context when helpful

**Key workflows**:
- "How is Jeremy" dashboard (translated signal)
- Perspective gathering interviews
- Reciprocal observation input
- Care instructions ("what helps when he's...")

**Platform**: Web-based, accessible via links you share

### 3. Observers (Researchers, Builders, Peers)

**Relationship to system**: They want to learn from what you've built.

**What they need**:
- Understand the architecture and methodology
- See anonymized patterns and learnings
- Replicate aspects for their own systems
- Access teaching materials

**Key workflows**:
- Observer portal with curated views
- Architecture documentation
- Pattern gallery (anonymized examples)
- Case study narratives

**Platform**: Web-based, public or permission-gated

---

## The Cognitive Interface Layer

Between the substrate (data) and the user (cognition) sits the interface layer. This layer provides **transforms** and **renders**:

### Transforms (Structure the Data)

| Transform | What It Does | Use Case |
|-----------|--------------|----------|
| Hierarchical | Nests things in trees | Mind maps, outlines |
| Network | Shows connections | Graph views |
| Temporal | Orders by time | Timelines, journals |
| Spatial | Arranges in 2D/3D space | Canvases, whiteboards |
| Tabular | Rows and columns | Lists, databases |
| Narrative | Tells a story | Summaries, reports |
| Argumentative | Shows reasoning | Decision trees |

### Renders (Present to User)

| Render Mode | Audience | Example |
|-------------|----------|---------|
| Full access | You | Raw entity queries, complete data |
| Translated signal | Intimates | "He's in building mode" not "51.8M entities" |
| Curated view | Observers | Anonymized patterns, architecture docs |
| Interactive | All | Dashboards, search, chat interfaces |

---

## Technology Architecture

### Hybrid Platform

| Platform | Technology | Audience | Purpose |
|----------|------------|----------|---------|
| **Web** | Next.js on Vercel | All | Interviews, observer portal, shared access |
| **Desktop** | Tauri (Mac app) | You | Daily operations, local access, native feel |
| **Backend** | BigQuery + Python | System | Data storage, central services |
| **LLM** | Claude API + Gemini | System | Analysis, generation, interviews |

### Why Hybrid

- **Web for sharing**: Friends need URLs, not apps to install
- **Desktop for operations**: You need native feel, system access, daily tool
- **Same codebase where possible**: Extend existing `frontend/` Next.js app
- **Tauri for native**: Lightweight wrapper, not Electron bloat

### Existing Infrastructure

```
truth-engine/
├── frontend/                  # Next.js on Vercel (EXTEND)
│   ├── /chat                  # Conversational interface
│   ├── /insights              # Pattern visualization
│   ├── /moments               # Key moments
│   ├── /developer-insights    # Development journey
│   └── (add relationship management, interviews, analysis)
│
├── architect_central_services/ # Python backend
│   ├── core/                  # Identity, logging, config
│   ├── governance/            # Policy enforcement
│   ├── pipelines/             # Data ingestion
│   └── (stable, production-ready)
│
├── tools/
│   ├── perspective_gatherer/  # Friend interviews (MIGRATE to frontend)
│   └── contact_review/        # Contact classification (MIGRATE)
│
└── desktop/                   # NEW - Tauri Mac app
```

---

## Data Model

### Relationship Profiles

```typescript
interface RelationshipProfile {
  id: string;
  name: string;
  category: RelationshipCategory;

  contact: {
    phone?: string;
    email?: string;
    location?: string;
  };

  relationship: {
    known_since?: string;
    how_met?: string;
    type?: string;  // friend, family, partner, colleague
  };

  biography: {
    occupation?: string;
    interests?: string[];
    key_life_events?: string[];
  };

  communication: {
    message_count?: number;
    last_contact?: string;
    frequency?: string;
    typical_topics?: string[];
    emotional_depth?: number;
  };

  analysis: {
    relationship_arc?: string;
    what_matters_to_them?: string[];
    how_they_experience_me?: string;
    blind_spots?: string[];
    current_state?: string;
  };

  interview: {
    completed?: boolean;
    code?: string;
    summary?: string;
  };

  action_items?: string[];
}

type RelationshipCategory =
  | 'INNER_CIRCLE'
  | 'CLOSE_FRIEND'
  | 'FRIEND'
  | 'ACQUAINTANCE'
  | 'PROFESSIONAL'
  | 'SERVICE'
  | 'HISTORICAL'
  | 'AI_COMPANION'
  | 'UNCATEGORIZED';
```

### Privacy Layers

| Layer | Who Sees | What They See |
|-------|----------|---------------|
| **Core** | You only | Everything—raw entities, all conversations |
| **Intimate** | Partners, closest friends | Emotional state, patterns, how to support |
| **Friend** | Friends | General wellbeing, interests, connection cues |
| **Family** | Family | Stability signals, major updates |
| **Observer** | Researchers, builders | Anonymized patterns, architecture |
| **Public** | Anyone | Published writings, public persona |

---

## Key Experiences

### 1. Relationship Manager

**Purpose**: Categorize contacts, generate profiles, maintain relationship context

**Workflow**:
1. View uncategorized contacts (pulled from Apple Contacts + conversation mentions)
2. AI suggests category based on message patterns
3. You confirm or override
4. Generate biographical profile from aggregated data
5. Maintain over time—action items, interview status, notes

### 2. Profile Generator

**Purpose**: Create rich relationship profiles from available data

**Inputs**:
- Apple Contacts (name, phone, email)
- Text message history (frequency, topics, sentiment)
- AI conversation mentions (context, emotional weight)
- Perspective gatherer results (if completed)

**Outputs**:
- Biographical summary
- Relationship arc narrative
- Communication patterns
- Blind spots (what you might not see)
- Action items

### 3. Perspective Gatherer

**Purpose**: Collect external perspectives you can't see from inside

**How it works**:
1. Create friend profile with interview configuration
2. Generate unique code for friend
3. Friend visits web interface, enters code
4. Claude conducts personalized interview
5. Results summarized and attached to relationship profile

**Already built**: `tools/perspective_gatherer/` (needs migration to main frontend)

### 4. Analysis Dashboard

**Purpose**: Visualize patterns across your externalized cognition

**Views**:
- **Timeline**: Your thinking over 108+ days
- **Graph**: Relationship network, topic connections
- **Patterns**: Recurring themes, emotional trajectories
- **Search**: Semantic queries across all entities

### 5. System Operations

**Purpose**: Control and monitor Truth Engine infrastructure

**Capabilities**:
- Ingestion status (which pipelines running, progress)
- Data source management (add new sources)
- Health monitoring (errors, performance)
- Cost tracking (BigQuery, LLM usage)

---

## Related Documents

| Document | Purpose |
|----------|---------|
| [COGNITIVE_INTERFACE_LAYER.md](./COGNITIVE_INTERFACE_LAYER.md) | Theory of the interface layer |
| [AUDIENCE_EXPERIENCES.md](./AUDIENCE_EXPERIENCES.md) | Detailed experience design per audience |
| [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) | Technical architecture and data flow |
| [DATA_MODELS.md](./DATA_MODELS.md) | Complete data schemas |
| [IMPLEMENTATION_ROADMAP.md](./IMPLEMENTATION_ROADMAP.md) | Phased build plan |
| [SUBSTRATE_INVARIANTS.md](./SUBSTRATE_INVARIANTS.md) | Human + Computer + Time fundamentals |
| [SYSTEM_INVARIANTS.md](./SYSTEM_INVARIANTS.md) | The constants that make the system designable |
| [CLAUDE_MEMBRANE_PATTERN.md](./CLAUDE_MEMBRANE_PATTERN.md) | How Claude work becomes system functionality |
| [SCRIPT_EXECUTION_LAYER.md](./SCRIPT_EXECUTION_LAYER.md) | Auto-UI for scripts Claude writes |

---

## Success Criteria

**The system is working when**:

- [ ] You use the Mac app daily for relationship management
- [ ] Friends complete perspective gathering interviews via web
- [ ] Relationship profiles are current and useful
- [ ] You can query your thinking: "What have I said about X?"
- [ ] Patterns surface that you couldn't see before
- [ ] System health is visible and manageable
- [ ] Costs are tracked and controlled

**The vision is realized when**:

Truth Engine feels like an extension of your cognition—not a tool you use, but a capability you have. The interface layer disappears; you're just *thinking* with more capacity.

---

## The Meta-Insight

You've externalized 51.8 million entities of cognition. The substrate exists. What's been missing is the **delivery with care**—the interface that makes this navigable, queryable, and useful for you and the people in your life.

This document defines that interface layer.

---

**Next Step**: Review [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) for technical implementation details.
