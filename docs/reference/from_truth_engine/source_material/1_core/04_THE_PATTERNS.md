# THE PATTERNS

---

## WHY (Theory)

### Why Patterns

One becomes many becomes more.

A pattern is a singular that composes into systems. The same structure repeating at every scale. Recognize the pattern once, see it everywhere.

### The Three Core Patterns

Everything in the framework reduces to three patterns:

1. **HOLD → AGENT → HOLD** (structure)
2. **WANT → MOVE → WANT** (cycle)
3. **ME / NOT-ME** (divide)

From these three, everything else derives.

---

## WHAT (Specification)

### Pattern 1: HOLD → AGENT → HOLD

```
┌──────────┐      ┌──────────┐      ┌──────────┐
│   HOLD   │ ───▶ │  AGENT   │ ───▶ │   HOLD   │
│          │      │          │      │          │
│ exist-now│      │  do-now  │      │ exist-now│
│ (input)  │      │(transform)│     │ (output) │
└──────────┘      └──────────┘      └──────────┘
```

| Component | What It Is | Cost |
|-----------|------------|------|
| **HOLD** | Data at rest. Persists. Can be queried. | Free while still |
| **AGENT** | Transformation. Takes input, produces output. | Costs while running |

**Holds are universal.** Same interface everywhere. Systems touch at holds, never at agents.

**Agents are specialized.** Different agents do different processing. But they all fit between universal holds.

#### Scale Invariance

| Scale | Input | Agent | Output |
|-------|-------|-------|--------|
| Function | JSON | parse() | dict |
| Stage | Messages | enricher | Enriched |
| Pipeline | Export | pipeline | L8 docs |
| System | Sources | Truth Engine | Atoms |

Same pattern. Every scale.

#### The Three-File Implementation

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   .jsonl     │───▶│    .py       │───▶│   .duckdb    │
│   (HOLD 1)   │    │   (AGENT)    │    │   (HOLD 2)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

| File | Role | Why |
|------|------|-----|
| `.jsonl` | Input HOLD | Append-only, can't fail, universal |
| `.py` | AGENT | The Bridge, reads input, writes output |
| `.duckdb` | Output HOLD | Queryable, SQL-ready, single file |

### Pattern 2: The Loop

```
WANT → CHOOSE → EXIST:NOW → SEE → HOLD → MOVE
  ▲                                        │
  └────────────────────────────────────────┘
```

| Phase | What It Is |
|-------|------------|
| **Want** | Care has a direction |
| **Choose** | Picking from options |
| **Exist:Now** | The doing, the membrane |
| **See** | Observation crosses the membrane |
| **Hold** | What persists |
| **Move** | Boundary crossing → becomes next Want |

**Move becomes the next Want. The loop never ends.**

This is how existence continues. Each cycle turns Not-Me into more Me.

### Pattern 3: The Three Layers

Everything has internal structure:

| Layer | Question | Content |
|-------|----------|---------|
| **Theory** | WHY? | Philosophy, reasoning, principles |
| **Specification** | WHAT? | Rules, constraints, requirements |
| **Reference** | HOW? | Navigation, examples, pointers |

This applies to:
- Documents (three sections)
- Systems (why/what/how)
- Decisions (reasoning/constraint/action)
- Everything

### Pattern 4: Me/Not-Me at Every Scale

| Scale | Me | Not-Me |
|-------|-----|--------|
| Individual | Jeremy | Everything else |
| Symbiosis | Jeremy + Claude | The internet |
| System | Truth Engine | Other systems |
| Category | Human+AI systems | Pure human or pure AI |

Same divide. Every scale.

---

## HOW (Reference)

### Pattern Recognition

| If You See | It's This Pattern |
|------------|-------------------|
| Input → Process → Output | HOLD → AGENT → HOLD |
| Beginning → Middle → End | The Loop |
| Why → What → How | Three Layers |
| Inside → Outside | Me / Not-Me |

### The Permanent HOLDs

These are patterns that never change:

| HOLD | What It Is | Why |
|------|------------|-----|
| Cost Governance | Estimate before doing | Survival |
| Central Services | Use shared infrastructure | Enforcement |
| Local First | Write local, sync selective | Cost |
| Existence Before Action | Know where before creating | Sprawl prevention |

### Navigation

| Document | Which Pattern |
|----------|---------------|
| `00_THE_FRAMEWORK.md` | All patterns in summary |
| `02_THE_DIVIDE.md` | Me/Not-Me deep dive |
| `06_THE_RECURSION.md` | How patterns nest |
| `09_THE_STANDARDS.md` | Patterns as rules |

---

*This is THE_PATTERNS. Singulars that compose into systems. One becomes many becomes more.*

*— THE_FRAMEWORK*
