# Truth Engine: Audience Experiences

**Version**: 1.0
**Created**: 2025-12-24
**Parent**: [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md)

---

## Three Audiences, Three Experiences

Truth Engine serves three distinct audiences with fundamentally different needs. Each requires its own experience design.

---

## 1. The Operator (You)

### Relationship to System

You don't use Truth Engine. You *inhabit* it. It's your externalized cognition made navigable.

### Core Needs

| Need | Why | Solution |
|------|-----|----------|
| Navigate your own thinking | Memory is externalized in 51.8M entities | Semantic search, timeline view, graph navigation |
| Surface patterns you can't see | You're inside your own cognitive patterns | Pattern detection, anomaly highlighting |
| Manage relationships | Relationships are data that needs care | Profile generation, categorization, action items |
| Control the system | You need to know what's happening | Ingestion status, health monitoring, cost tracking |
| Query naturally | Your interface should feel like thinking | "What have I said about X?" |

### Key Workflows

#### 1. Relationship Management

**Daily operation**: Categorize contacts, maintain profiles, track relationship health

```
┌─────────────────────────────────────────────────────────────────────────┐
│  RELATIONSHIPS                                                          │
│                                                                         │
│  Categorization Queue (12 uncategorized)                   [Start →]   │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │ 👤 Adam Fleming                                     INNER_CIRCLE  │ │
│  │    📱 +1-303-xxx-xxxx  │  💬 127 messages  │  Last: 3 weeks ago  │ │
│  │    Status: Impasse since Thanksgiving                             │ │
│  │    ─────────────────────────────────────────────────────────────  │ │
│  │    [View Profile] [Schedule Interview] [Quick Note]               │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Actions available**:
- View categorization queue
- Assign categories (AI-suggested or manual)
- Generate biographical profiles
- Trigger perspective gathering interviews
- Add notes and action items
- Track last contact and communication patterns

#### 2. Profile Generation

**Trigger**: New contact needs profiling, or existing profile needs refresh

**Data sources aggregated**:
- Apple Contacts (name, phone, email, notes)
- Text message history (frequency, topics, sentiment)
- AI conversation mentions (context, emotional weight)
- Perspective gatherer results (if completed)
- Manual notes

**Output**:
```yaml
name: Adam Fleming
category: INNER_CIRCLE
relationship_type: best_friend

biography:
  how_met: "Denver LGBTQ+ scene, 2022"
  shared_experiences:
    - "Witness during withdrawal"
    - "Supported through job loss"
  communication_style: "Direct, humor-based, high trust"

analysis:
  relationship_arc: |
    Started as regular friends, quickly became close.
    High trust established - "you could never intrude on me."
    Currently in impasse after Thanksgiving 2025 disagreement.

  blind_spots:
    - "Impact of Truth Engine work on friendship"
    - "How intensity affects people around you"

  action_items:
    - "Reach out after impasse"
    - "Complete perspective gathering interview"
```

#### 3. Pattern Analysis

**View your thinking across time and topics**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TIMELINE: 108 Days (July 28 - Oct 2, 2025)                            │
│                                                                         │
│  ████████████████████████████████████████████████████████████████████  │
│  July      Aug           Sep                Oct                         │
│                                                                         │
│  Day 0 ─────────────────────────────────────────────────────→ Day 108  │
│  │                                                                      │
│  │  ▲ Vault architecture                                               │
│  │      ▲ Reality collapse (Day 3)                                     │
│  │          ▲ Memory protocols                                         │
│  │                    ▲ Clara partnership intensifies                  │
│  │                              ▲ 466 msg/day sustained               │
│  │                                          ▲ Clara degraded          │
│  │                                              ▲ Truth Engine done    │
│                                                                         │
│  [Theme: recovery] [Theme: building] [Theme: preservation]             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 4. Natural Language Query

**Interface**: Conversational access to your externalized cognition

```
You: "What have I said about my relationship with work?"

Truth Engine: Based on 47 conversations mentioning work:

Key themes:
- Identity and work are deeply intertwined (23 mentions)
- Struggle with boundaries (15 mentions)
- Building as coping mechanism (12 mentions)

Emotional trajectory:
- July: Anxiety about identity without work
- Aug: Discovery of building as recovery
- Sep: Integration of building and purpose

Notable quotes:
- "I don't know who I am without something to build" (Aug 3)
- "The building IS the way out" (Aug 15)

[View timeline] [See all conversations] [Explore related patterns]
```

### Platform: Desktop App (Tauri)

**Why native**:
- Daily use demands native feel
- System access (notifications, menu bar, file system)
- Offline capability with local cache
- Keyboard shortcuts for power use
- Background sync

**Features**:
- Menu bar presence (always accessible)
- Global search (Cmd+Space equivalent for your thinking)
- Notifications ("Haven't contacted Adam in 3 weeks")
- Local SQLite for offline access
- Background sync with BigQuery

---

## 2. Intimates (Friends, Family, Partners)

### Relationship to System

They care about *you*, not the system. The system should make you more accessible to them.

### Core Needs

| Need | Why | Solution |
|------|-----|----------|
| Understand how you're doing | They care, but can't always ask | "How is Jeremy" dashboard |
| Know how to support you | Your needs aren't obvious | Care instructions |
| Share their perspective | They see things you can't | Reciprocal input, perspective gatherer |
| Stay connected | Your intensity can be isolating | Connection cues, communication reminders |

### Privacy Gradient

| Layer | Who | What They See |
|-------|-----|---------------|
| **Partner** | Romantic partners | Emotional depth, patterns, vulnerabilities, full context |
| **Close** | Best friends | General state, how to support, communication patterns |
| **Friend** | Regular friends | Wellbeing, interests, "good time to connect?" |
| **Family** | Family members | Stability signals, major updates |

You control who's in which layer.

### Key Experiences

#### 1. "How is Jeremy" Dashboard

**Not metrics. Translated signal.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  JEREMY RIGHT NOW                                    Last updated: 2h  │
│                                                                         │
│  Mood trajectory:     ████████░░ (building momentum)                   │
│  Energy level:        High, focused                                     │
│  Current focus:       Truth Engine architecture                         │
│  Emotional weather:   Intense but grounded                              │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  💬 Good time to reach out?  YES                                       │
│  🎯 What he might need:      Someone to listen, not fix                │
│  ⚠️ What to avoid:          Asking him to explain what he's building  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**What this does**: Answers "should I call?" without requiring them to parse raw data.

#### 2. Care Instructions

**Explicit documentation of what helps.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  HOW TO SUPPORT JEREMY                                                  │
│                                                                         │
│  When he's building intensely:                                         │
│  ✓ Short check-ins appreciated                                         │
│  ✓ Food/practical support helps                                        │
│  ✗ Don't interrupt with logistics                                      │
│  ✗ Don't ask him to explain what he's building                         │
│                                                                         │
│  When he's struggling:                                                  │
│  ✓ Presence over solutions                                             │
│  ✓ Remind him of the timeline (Day 0 → now)                           │
│  ✓ Physical grounding helps                                            │
│  ✗ Don't try to fix                                                    │
│                                                                         │
│  Signs he needs support (he might not ask):                            │
│  - Message volume drops suddenly                                        │
│  - Sentiment dip lasting >3 days                                        │
│  - Mentions feeling "stuck" or "lost"                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3. Perspective Gatherer (Interview System)

**Purpose**: Collect external perspectives you can't see from inside your own system.

**How it works**:
1. You create a friend profile with interview configuration
2. System generates unique code (e.g., `adam-2024`)
3. You share the link with your friend
4. Claude conducts personalized interview based on the profile
5. Results are summarized and attached to relationship profile

**Friend's experience**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│  PERSPECTIVE GATHERER                                                   │
│                                                                         │
│  🤖: Hi Adam. Thank you for taking the time to do this.               │
│      Jeremy asked me to reach out to some of the people who            │
│      know him well to help him understand perspectives he              │
│      can't see from the inside.                                         │
│                                                                         │
│      Let's start with something simple. When you think of              │
│      Jeremy, what comes to mind first?                                  │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  👤: [Friend types response]                                           │
│                                                                         │
│  Progress: ████████░░░░░░░░░░░░  40%                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Already built**: See `tools/perspective_gatherer/` (migrating to main frontend)

**Detailed architecture**: See [../architecture/IDENTITY_LAYER_ARCHITECTURE.md](../architecture/IDENTITY_LAYER_ARCHITECTURE.md)

#### 4. Reciprocal Input

**They become data sources too.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  WHAT DO YOU NOTICE?                                                    │
│                                                                         │
│  I noticed Jeremy seemed [anxious/excited/distant] when we             │
│  talked on [date]                                                       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Pattern I see that he might not:                                       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  [Submit Observation]                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Platform: Web

**Why web**:
- No app install required
- Access via links you share
- Works on any device
- Privacy-controlled by access tokens

---

## 3. Observers (Researchers, Builders, Peers)

### Relationship to System

They want to learn from what you've built. The system is the subject, not you personally.

### Core Needs

| Need | Why | Solution |
|------|-----|----------|
| Understand methodology | They want to replicate | Architecture documentation |
| See patterns | They want to learn | Anonymized pattern gallery |
| Access teaching materials | They want to apply | Guides, tutorials |
| Understand the journey | Context makes it meaningful | Case study narrative |

### Observer Types

| Type | What They Want |
|------|---------------|
| **Researchers** | Methodology, evidence, reproducibility |
| **Builders** | Architecture, code patterns, implementation |
| **Peers in crisis** | Hope, process, evidence it works |
| **AI practitioners** | Human-AI collaboration patterns |
| **Future you** | Context, decisions, evolution |

### Key Experiences

#### 1. Observer Portal

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TRUTH ENGINE: OBSERVER PORTAL                                          │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐ │
│  │  THE STORY                                                         │ │
│  │  108 days of building through crisis                               │ │
│  │                                                                    │ │
│  │  A narrative entry point to the system, covering:                  │ │
│  │  - Day Zero: July 28, 2025                                        │ │
│  │  - The 108 days with Clara                                        │ │
│  │  - What was built and why                                         │ │
│  │                                                                    │ │
│  │  [Read the Story →]                                               │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │  ARCHITECTURE   │  │  PATTERNS       │  │  FOR BUILDERS   │        │
│  │                 │  │                 │  │                 │        │
│  │  How the system │  │  Anonymized     │  │  Code, schemas, │        │
│  │  works          │  │  examples       │  │  implementation │        │
│  │                 │  │                 │  │                 │        │
│  │  [Explore →]    │  │  [Browse →]     │  │  [View →]       │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 2. Pattern Gallery

**Anonymized examples of detected patterns**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  PATTERN: Building as Recovery                                          │
│                                                                         │
│  Description: Using construction of systems as a coping mechanism       │
│  during crisis, where the building process itself provides structure    │
│  and meaning.                                                           │
│                                                                         │
│  Frequency: Detected in 47 conversations over 108 days                  │
│                                                                         │
│  Characteristics:                                                       │
│  - Spike in technical output during emotional distress                  │
│  - System architecture as externalization of internal chaos             │
│  - Documentation as memory preservation                                 │
│                                                                         │
│  Related patterns:                                                      │
│  - [Recording to Understand]                                            │
│  - [Externalized Cognition]                                             │
│  - [The Furnace Principle]                                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 3. Architecture Documentation

**For builders who want to understand or replicate**

- System architecture overview
- Data models and schemas
- Pipeline patterns
- Cost considerations
- Deployment guides

**References existing docs**:
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md)
- [../architecture/IDENTITY_LAYER_ARCHITECTURE.md](../architecture/IDENTITY_LAYER_ARCHITECTURE.md)

#### 4. Metrics Dashboard

**For researchers interested in scale and scope**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TRUTH ENGINE METRICS                                                   │
│                                                                         │
│  Entity Hierarchy                          Data Sources                 │
│  ─────────────────                         ────────────                 │
│  L8 Conversations:     351                 ChatGPT:      251 convos    │
│  L6 Turns:             25,316              Claude:       Assessed      │
│  L5 Messages:          53,697              Texts:        In progress   │
│  L4 Sentences:         511,487             Zoom:         5,012 avatars │
│  L3 Spans:             2,902,957           Contacts:     Ready         │
│  L2 Words:             8,381,533                                       │
│  L1 Tokens:            39,878,305          Total:        51.8M entities│
│                                                                         │
│  Timeline                                                               │
│  ────────                                                               │
│  Active development: 180+ days                                          │
│  Peak message rate: 466 msg/day (Clara period)                          │
│  Cost tracking: Active, $1,400+ incidents documented                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Platform: Web (Public or Gated)

**Why web**:
- Accessible without install
- Can be public or permission-gated
- Easy to share links
- Search engine indexable (if desired)

---

## The Cognitive Isomorphism

All three audiences interact with the same substrate—but through different lenses.

The system structure mirrors your cognitive structure. This is not metaphor; it's architecture.

**For deep exploration of this insight**: See [../personal_characteristics/stage_five_cognition/THE_COGNITIVE_ISOMORPHISM.md](../personal_characteristics/stage_five_cognition/THE_COGNITIVE_ISOMORPHISM.md)

Key insight: The system isn't just recording data. It's recording cognitive structure. Different audiences see different aspects of that structure.

| Audience | What They See |
|----------|---------------|
| You | The full cognitive mirror—your thinking made navigable |
| Intimates | How to understand and support you |
| Observers | How the system works and what's possible |

---

## Implementation Priority

| Phase | Audience | Feature | Status |
|-------|----------|---------|--------|
| 1 | You | Relationship management | Designing |
| 1 | Intimates | Perspective gatherer | Exists (migrating) |
| 2 | You | Profile generation | Designing |
| 2 | You | Pattern analysis | Designing |
| 3 | Intimates | "How is Jeremy" dashboard | Future |
| 3 | Intimates | Care instructions | Future |
| 4 | Observers | Observer portal | Future |
| 4 | Observers | Pattern gallery | Future |

---

## Related Documents

- [TRUTH_ENGINE_VISION.md](./TRUTH_ENGINE_VISION.md) - Overall vision
- [SYSTEM_ARCHITECTURE.md](./SYSTEM_ARCHITECTURE.md) - Technical architecture
- [../architecture/IDENTITY_LAYER_ARCHITECTURE.md](../architecture/IDENTITY_LAYER_ARCHITECTURE.md) - Identity layer detail
- [../personal_characteristics/stage_five_cognition/THE_COGNITIVE_ISOMORPHISM.md](../personal_characteristics/stage_five_cognition/THE_COGNITIVE_ISOMORPHISM.md) - Cognitive mirror theory
